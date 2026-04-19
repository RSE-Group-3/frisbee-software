import rclpy
from rclpy.node import Node

from std_msgs.msg import String

import time

class FakeArduino(Node):
    def __init__(self):
        super().__init__('fake_arduino')

        self.collector_cmd_sub = self.create_subscription(
            String, 'arduino/collector/cmd', self.collector_serial_callback, 10)
        self.collector_status_pub = self.create_publisher(
            String, 'arduino/collector/status', 10)
        
        self.launcher_cmd_sub = self.create_subscription(
            String, 'arduino/launcher/cmd', self.launcher_serial_callback, 10)
        self.launcher_status_pub = self.create_publisher(
            String, 'arduino/launcher/status', 10)

        self.get_logger().info("Fake Arduino node online.")

    def collector_serial_callback(self, cmd_msg: String):
        time.sleep(1)
        if cmd_msg.data.startswith("WHEELS"): return
        self.collector_status_pub.publish(String(data=f'OK: fake success for "{cmd_msg.data}"'))

    def launcher_serial_callback(self, cmd_msg: String):
        time.sleep(1)
        if cmd_msg.data.startswith("WHEELS"): return
        self.launcher_status_pub.publish(String(data=f'OK: fake success for "{cmd_msg.data}"'))
        

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