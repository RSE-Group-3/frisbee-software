import rclpy
from rclpy.node import Node

from std_msgs.msg import String

import time

LOOP_TIME = 0.1

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

        self.wheel_enc_timer = self.create_timer(LOOP_TIME, self.wheel_enc_loop)

        self.left_target_vel = 0
        self.right_target_vel = 0

    def wheel_enc_loop(self):
        self.launcher_status_pub.publish(String(data=f'WHEELS_ENC|CL:0.00 TL:{self.left_target_vel} PL:0.00|CR:0.00 TR:{self.right_target_vel} PR:0.00'))

    def collector_serial_callback(self, cmd_msg: String):
        time.sleep(1)
        self.collector_status_pub.publish(String(data=f'OK: fake success for "{cmd_msg.data}"'))

    def launcher_serial_callback(self, cmd_msg: String):
        if cmd_msg.data.startswith('WHEELS'):
            cmd_msg_parts = cmd_msg.data.strip().split()
            self.left_target_vel = float(cmd_msg_parts[2])
            self.right_target_vel = float(cmd_msg_parts[3])

        time.sleep(1)
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