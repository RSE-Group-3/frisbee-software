import future

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from fb_interfaces.srv import PlannerCommand

TIMEOUT = 10 # s

class ManipulationNode(Node):
    def __init__(self):
        super().__init__('manipulation_node')

        self.serial_cmd_pub = self.create_publisher(String, 'arduino/cmd', 10)
        self.serial_status_sub = self.create_subscription(String, 'arduino/status', self.serial_callback, 10)

        self.srv = self.create_service(PlannerCommand, 'manipulation/execute', self.execute_callback)

        self.get_logger().info("Manipulation service node online.")

        self.current_sequence = []
        self.current_index = 0
        self.timer = None
        self.command_in_progress = None
        self.service_response = None

    def parse_planner_task(self, msg: str):
        '''
        wheel commands in fb_mobility/diff_drive.py
            WHEELS speed {left_vel} {right_vel}
        '''
        task_msg = msg.strip().split()
        task, args = task_msg[0], task_msg[1:]

        match task:
            case 'reset': 
                sequence = [
                    'COLLECTOR: open',
                    'COLLECTOR: high',
                ]
            case 'stop':
                sequence = [
                    'STOP',  # stop all motors if not already stopped
                ]
            case 'launcher.launch':
                try:
                    assert len(args) == 1 and args[0].isdigit()
                    sequence = [
                        f'LAUNCHER: launch {args[0]}'
                    ]
                except:
                    self.get_logger().error(f"Bad launch arguments, expected 'launcher.launch <int>', got '{msg}'")
                    sequence = [
                        f'LAUNCHER: launch 1200'
                    ]
            case 'collector.collect': 
                sequence = [
                    'COLLECTOR: low',
                    'COLLECTOR: close',
                    'COLLECTOR: high_tilt',
                    'COLLECTOR: open',
                    'COLLECTOR: high',
                ]
            case _:
                task, sequence = None, None

        return task, sequence

    def execute_callback(self, request, response):
        try:
            task, sequence = self.parse_planner_task(request.command)
            if sequence is None:
                response.success = False
                response.message = f"Unknown manipulation task {task}"
                return response
            if self.command_in_progress and task != 'stop': # allow 'stop' command to interrupt any current command
                response.success = False
                response.message = f"Task {self.command_in_progress} in progress, cannot execute {task}"
                return response

            self.get_logger().warn(f"Starting command sequence: {task}")
            self.current_sequence = sequence
            self.current_index = 0
            self.command_in_progress = task
            self.service_response = response
            self._send_next_command()

            future = self.client.call_async(request)
            future.add_done_callback(self.response_callback)
        
        except:
            response.success = False
            response.message = f"Error parsing command {request.command}"
            return response

    def _send_next_command(self):
        if self.current_index >= len(self.current_sequence):
            self.get_logger().warn(f"COMPLETE: Successfully executed {self.chain}")
            self.service_response.message = f"COMPLETE: Successfully executed {self.chain}"
            self.service_response.success = True
            self.command_in_progress = None
            return

        cmd = self.current_sequence[self.current_index]
        self.get_logger().info(f"Sending command: '{cmd}'")
        self.serial_cmd_pub.publish(String(data=cmd))

        self.timer = self.create_timer(TIMEOUT, self._command_timeout)

    def serial_callback(self, msg: String):
        self.get_logger().info(f"Status received '{msg.data}'")
        if not self.command_in_progress:
            self.get_logger().info(f"No command in progress, ignoring status: '{msg.data}'")
            return

        if self.timer:
            self.timer.cancel()

        serial_msg = msg.data
        ack_status = serial_msg.split()[0]
        if ack_status == 'OK:':
            self.get_logger().info(f"Received status: '{msg.data}'")
            self.current_index += 1
            self._send_next_command()
        elif ack_status == 'FAIL:':
            self.get_logger().error(f"Received status: '{msg.data}'")
            self.get_logger().error(f"COMPLETE: Execution failed: {msg.data}")
            self.service_response.message = f"COMPLETE: Execution failed: {msg.data}"
            self.service_response.success = False
            self.command_in_progress = None

    def _command_timeout(self):
        cmd = self.current_sequence[self.current_index]
        if self.timer:
            self.timer.cancel()

        self.service_response.success = False
        self.get_logger().warn(f"COMPLETE: Timeout on command {cmd}")
        self.service_response.message = f"COMPLETE: Timeout on command {cmd}"
        self.command_in_progress = None
        return


def main(args=None):
    rclpy.init(args=args)
    node = ManipulationNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.serial_cmd_pub.publish(String(data="STOP"))
        node.get_logger().warn("STOP triggered by Ctrl-C")
    finally:
        node.destroy_node()
        rclpy.shutdown()