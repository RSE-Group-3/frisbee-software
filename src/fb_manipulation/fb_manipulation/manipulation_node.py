import rclpy
from rclpy.node import Node

from std_msgs.msg import String

SEQUENCES = {
                'launcher.launch': [
                    'LAUNCHER launch 40',
                ],
                'collector.reset': [
                    'COLLECTOR open',
                    'COLLECTOR high',
                ],
                'collector.collect': [
                    'COLLECTOR low',
                    'COLLECTOR close',
                    'COLLECTOR high',
                    'COLLECTOR high_tilt',
                    'COLLECTOR open',
                    'COLLECTOR high',
                ],
            }

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

    def planner_callback(self, msg: String):
        task = msg.data
        if task not in SEQUENCES:
            self.get_logger().error(f"Unknown manipulation task: {task}")
            self.manip_status_pub.publish(String(data=f"{task}; fail; unknown manipulation task {task}"))
            return

        if self.command_in_progress:
            self.get_logger().error(f"Task {self.command_in_progress} already in progress, ignoring {task}")
            return

        self.get_logger().warn(f"Starting command sequence: {task}")
        self.current_sequence = SEQUENCES[task]
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

        # assume all acks are either 'OK: info...' or 'FAIL: info...'
        serial_status = msg.data.strip()
        ack_status = serial_status.split()[0]
        if ack_status == "OK:":
            self.get_logger().info(f"Received status: '{serial_status}'")
            self.current_index += 1
            if self.timer:
                self.timer.cancel()
            self._send_next_command()
        elif ack_status == "FAIL:":
            self.get_logger().warn(f"Received status: '{serial_status}'")
            if self.timer:
                self.timer.cancel()
            self.manip_status_pub.publish(String(data=f"{self.command_in_progress}; fail; {serial_status}"))
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