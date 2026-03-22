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

        self.cmd_sub = self.create_subscription(String, 'manipulation/cmd', self.planner_callback, 10)
        self.status_pub = self.create_publisher(String, 'manipulation/status', 10)
        self.serial_pub = self.create_publisher(String, 'arduino/cmd', 10)
        self.serial_sub = self.create_subscription(String, 'arduino/status', self.serial_callback, 10)

        self.get_logger().info("Manipulation interface node online.")

        self.current_sequence = []
        self.current_index = 0
        self.timer = None
        self.command_in_progress = None

    def planner_callback(self, msg: String):
        cmd = msg.data
        if cmd not in SEQUENCES:
            self.get_logger().error(f"Unknown planner command: {cmd}")
            self.status_pub.publish(String(data=f"{cmd} fail"))
            return

        if self.command_in_progress:
            self.get_logger().warn(f"Command {self.command_in_progress} already in progress, ignoring {cmd}")
            return

        self.get_logger().info(f"Starting command sequence: {cmd}")
        self.current_sequence = SEQUENCES[cmd]
        self.current_index = 0
        self.command_in_progress = cmd
        self._send_next_subcommand()

    def _send_next_subcommand(self):
        if self.current_index >= len(self.current_sequence):
            self.status_pub.publish(String(data=f"{self.command_in_progress} ok"))
            self.get_logger().info(f"COMPLETE: {self.command_in_progress}")
            self.command_in_progress = None
            return

        subcmd = self.current_sequence[self.current_index]
        self.get_logger().info(f"Sending subcommand: '{subcmd}'")
        self.serial_pub.publish(String(data=subcmd))

        self.timer = self.create_timer(TIMEOUT, self._subcommand_timeout)

    def serial_callback(self, msg: String):
        if not self.command_in_progress:
            return

        # assume ack is either 'OK: ...' or 'FAIL: ...'
        status = msg.data.strip()
        ack_status = status.split()[0]
        if ack_status == "OK:":
            self.get_logger().info(f"Received status: '{status}'")
            self.current_index += 1
            if self.timer:
                self.timer.cancel()
            self._send_next_subcommand()
        elif ack_status == "FAIL:":
            self.get_logger().warn(f"Received status: '{status}'")
            if self.timer:
                self.timer.cancel()
            self.status_pub.publish(String(data=f"{self.command_in_progress} fail"))
            self.command_in_progress = None

    def _subcommand_timeout(self):
        self.get_logger().warn(f"Timeout on subcommand {self.current_sequence[self.current_index]}")
        self.status_pub.publish(String(data=f"{self.command_in_progress} fail"))
        self.command_in_progress = None
        if self.timer:
            self.timer.cancel()


def main(args=None):
    rclpy.init(args=args)
    node = ManipulationNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.serial_pub.publish(String(data="STOP"))
        node.get_logger().warn("STOP triggered by Ctrl-C")
    finally:
        node.destroy_node()
        rclpy.shutdown()