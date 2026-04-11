import rclpy
from rclpy.node import Node

from std_msgs.msg import String

import time

class FakeArduino(Node):
    def __init__(self):
        super().__init__('fake_arduino')

        self.cmd_sub = self.create_subscription(
            String, 'arduino/cmd', self.serial_callback, 10)
        self.status_pub = self.create_publisher(
            String, 'arduino/status', 10)

        self.get_logger().info("Fake Arduino node online.")

    def serial_callback(self, cmd_msg: String):
        """
        received collector or launcher command from manipulation node
        """
        time.sleep(1)
        if cmd_msg.data.startswith("WHEELS"): return
        self.status_pub.publish(String(data=f'OK: fake success for "{cmd_msg.data}"'))
        # self.status_pub.publish(String(data=f'FAIL: fake fail for "{subcmd_msg.data}"'))
        

def main(args=None):
    rclpy.init(args=args)
    node = FakeArduino()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.estop()
    finally:
        node.destroy_node()
        rclpy.shutdown()