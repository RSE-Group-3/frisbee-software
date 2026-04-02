import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from example_interfaces.srv import Trigger  # simple service

TIMEOUT = 10 # s

class ManipulationNode(Node):
    def __init__(self):
        super().__init__('manipulation_node')

        self.serial_cmd_pub = self.create_publisher(String, 'arduino/cmd', 10)
        self.serial_status_sub = self.create_subscription(String, 'arduino/status', self.serial_callback, 10)

        # Service to replace planner subscription
        self.srv = self.create_service(Trigger, 'manipulation/execute', self.execute_callback)

        self.get_logger().info("Manipulation service node online.")

        self.current_sequence = []
        self.current_index = 0
        self.timer = None
        self.command_in_progress = None
        self.service_response = None  # store pending service response

    def parse_planner_task(self, msg: str):
        '''
        03/23/2026 TODO: change commands sent to serial

        wheel commands in fb_mobility/diff_drive.py
            WHEELS vl_vr {left_vel} {right_vel}
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
                if len(args) == 1:
                    sequence = [
                        f'LAUNCHER: launch {args[0]}'
                    ]
                else:
                    self.get_logger().error(f"Bad launch arguments")
                    sequence = [
                        f'LAUNCHER: launch 1100'
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
        # replace planner_callback with service callback
        task, sequence = self.parse_planner_task(request.message)

        if sequence is None:
            response.success = False
            response.message = f"{task}; fail; unknown manipulation task {task}"
            return response

        if self.command_in_progress and task != 'stop':
            self.get_logger().error(f"Task {self.command_in_progress} already in progress, ignoring task {task}")
            response.success = False
            response.message = f"Task {self.command_in_progress} in progress, cannot execute {task}"
            return response

        self.get_logger().warn(f"Starting command sequence: {task}")
        self.current_sequence = sequence
        self.current_index = 0
        self.command_in_progress = task
        self.service_response = response
        self._send_next_command()

        return response  # service will return immediately; response updated in serial_callback

    def _send_next_command(self):
        if self.current_index >= len(self.current_sequence):
            if self.service_response:
                self.service_response.success = True
                self.service_response.message = f"{self.command_in_progress}; ok;"
            self.get_logger().warn(f"COMPLETE: {self.command_in_progress}")
            self.command_in_progress = None
            return

        cmd = self.current_sequence[self.current_index]
        self.get_logger().info(f"Sending command: '{cmd}'")
        self.serial_cmd_pub.publish(String(data=cmd))

        self.timer = self.create_timer(TIMEOUT, self._command_timeout)

    def serial_callback(self, msg: String):
        if not self.command_in_progress:
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
            self.manip_status_pub.publish(String(data=f"{self.command_in_progress}; fail; {serial_msg}"))
            if self.service_response:
                self.service_response.success = False
                self.service_response.message = f"{self.command_in_progress}; fail; {serial_msg}"
            self.command_in_progress = None

    def _command_timeout(self):
        cmd = self.current_sequence[self.current_index]
        self.get_logger().warn(f"Timeout on command {cmd}")
        self.manip_status_pub.publish(String(data=f"{self.command_in_progress}; fail; timeout on command {cmd}"))
        if self.service_response:
            self.service_response.success = False
            self.service_response.message = f"{self.command_in_progress}; fail; timeout on command {cmd}"
        self.command_in_progress = None
        if self.timer:
            self.timer.cancel()


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