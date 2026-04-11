import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Float64MultiArray
from geometry_msgs.msg import Twist

WHEEL_RADIUS = 0.09
WHEEL_SEPARATION = 0.908

PWM = 100
FORWARD_CMD = f"WHEELS speed {PWM} {PWM}\n"
FORWARD_CMD = f"WHEELS speed {120} {-120}\n" # TURN
BACKWARD_CMD = f"WHEELS speed -{PWM} -{PWM}\n"
STOP_CMD = "STOP"

class SimpleDriveSerial(Node):
    def __init__(self):
        super().__init__('simpledrive_serial')

        self.vel_sub = self.create_subscription(Twist, '/cmd_vel', self.cb, 10)
        self.serial_pub = self.create_publisher(String, 'arduino/cmd', 10)
    
    def cb(self, msg):
        v = msg.linear.x
        w = msg.angular.z

        if v > 0:
            cmd = FORWARD_CMD
            self.get_logger().info(f"moving forward...")
        elif v == 0:
            cmd = STOP_CMD
            self.get_logger().info(f"STOP")
        else:
            cmd = BACKWARD_CMD
            self.get_logger().info(f"moving backward...")
        
        self.serial_pub.publish(String(data=cmd))


def main():
    rclpy.init()
    node = SimpleDriveSerial()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()