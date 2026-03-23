import rclpy
from rclpy.node import Node

from std_msgs.msg import String

TIMEOUT = 10 # s

class ManipulationNode(Node):
    def __init__(self):
        super().__init__('manipulation_node')

        self.manip_cmd_sub = self.create_subscription(String, 'manipulation/cmd', self.planner_callback, 10)
        self.manip_status_pub = self.create_publisher(String, 'manipulation/status', 10)
        self.serial_cmd_pub = self.create_publisher(String, 'arduino/cmd', 10)
        self.serial_status_sub = self.create_subscription(String, 'arduino/status', self.serial_callback, 10)

        self.get_logger().info("Manipulation interface node online.")

        self.current_sequence = []
        self.current_index = 0
        self.timer = None
        self.command_in_progress = None


    def parse_planner_task(self, msg: str):
        '''
        03/23/2026 TODO: change commands sent to serial

        wheel commands in fb_mobility/diff_drive.py
            WHEELS vl_vr {left_vel} {right_vel}
        '''

        task_msg = msg.strip().split()
        task, args = task_msg[0], task_msg[1:]

        match task:
            case 'start': 
                sequence = [ # also acts as collector reset
                    'START', # start motors if not already started
                    'COLLECTOR open',
                    'COLLECTOR high',
                ]
            case 'stop':
                sequence = [
                    'STOP', # stop motors if not already stopped
                ]
            case 'launcher.launch':
                if len(args) == 1:
                    sequence = [
                        f'LAUNCHER launch {args[0]}'
                    ]
                else:
                    self.get_logger().error(f"Bad launcher.launch arguments")
                    sequence = [
                        f'LAUNCHER launch 5'
                    ]
            # case 'collector.reset': # not used
            #     sequence = [
            #         'COLLECTOR open',
            #         'COLLECTOR high',
            #     ]
            case 'collector.collect': 
                sequence = [
                    'COLLECTOR low',
                    'COLLECTOR close',
                    'COLLECTOR high_tilt',
                    'COLLECTOR open',
                    'COLLECTOR high',
                ]
            case _:
                task, sequence = None, None

        return task, sequence

    def parse_serial_ack(self, msg: str):
        '''
        03/23/2026 TODO: change this based on arduino serial output
        '''
        # assume all acks are either 'OK: info...' or 'FAIL: info...'
        serial_msg = msg.strip()
        ack_status = serial_msg.split()[0]
        if ack_status == "OK:":
            return True, serial_msg
        elif ack_status == "FAIL:":
            return False, serial_msg
        

    def planner_callback(self, msg: String):
        task, sequence = self.parse_planner_task(msg.data)

        if sequence is None:
            self.get_logger().error(f"Unknown manipulation task: {task}")
            self.manip_status_pub.publish(String(data=f"{task}; fail; unknown manipulation task {task}"))
            return

        if self.command_in_progress and task != 'stop': # stop interrupts commands
            self.get_logger().error(f"Task {self.command_in_progress} already in progress, ignoring task {task}")
            return

        self.get_logger().warn(f"Starting command sequence: {task}")
        self.current_sequence = sequence
        self.current_index = 0
        self.command_in_progress = task
        self._send_next_command()

    def _send_next_command(self):
        if self.current_index >= len(self.current_sequence):
            self.manip_status_pub.publish(String(data=f"{self.command_in_progress}; ok;"))
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

        success, info = self.parse_serial_ack(msg.data)

        if self.timer:
            self.timer.cancel()

        if success:
            self.get_logger().info(f"Received status: '{msg.data}'")
            self.current_index += 1
            self._send_next_command()
        else:
            self.get_logger().error(f"Received status: '{msg.data}'")
            self.manip_status_pub.publish(String(data=f"{self.command_in_progress}; fail; {info}"))
            self.command_in_progress = None

    def _command_timeout(self):
        cmd = {self.current_sequence[self.current_index]}
        self.get_logger().warn(f"Timeout on command {cmd}")
        self.manip_status_pub.publish(String(data=f"{self.command_in_progress}; fail; timeout on command {cmd}"))
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