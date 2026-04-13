import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Float64MultiArray
from geometry_msgs.msg import Twist

WHEEL_RADIUS = 0.09
WHEEL_SEPARATION = 0.908

MOVING_PWM = 170
MOVING_TURN_PWM = 200

class SimpleDriveSerial(Node):
    def __init__(self):
        super().__init__('simpledrive_serial')

        self.vel_sub = self.create_subscription(Twist, '/cmd_vel', self.cb, 10)
        self.serial_pub = self.create_publisher(String, 'arduino/cmd', 10)
    
    def cb(self, msg):
        v = msg.linear.x
        w = msg.angular.z
        self.get_logger().info(f"v: {v}, w: {w}")


        if v > 0:
            if w < 0:
                v_l, v_r = MOVING_TURN_PWM, 0
                self.get_logger().info(f"forward right, v_l: {v_l}, v_r: {v_r}")
            elif w == 0:
                v_l, v_r = MOVING_PWM, MOVING_PWM
                self.get_logger().info(f"forward, v_l: {v_l}, v_r: {v_r}")
            else:
                v_l, v_r = 0, MOVING_TURN_PWM
                self.get_logger().info(f"forward left, v_l: {v_l}, v_r: {v_r}")
        elif v == 0:
            v_l, v_r = 0, 0
            self.get_logger().info(f"STOP, v_l: {v_l}, v_r: {v_r}")
        elif v < 0:
            if w < 0:
                v_l, v_r = 0, -MOVING_TURN_PWM
                self.get_logger().info(f"backward left, v_l: {v_l}, v_r: {v_r}")
            elif w == 0:
                v_l, v_r = -MOVING_PWM, -MOVING_PWM
                self.get_logger().info(f"backward, v_l: {v_l}, v_r: {v_r}")
            else:
                v_l, v_r = -MOVING_TURN_PWM, 0
                self.get_logger().info(f"backward right, v_l: {v_l}, v_r: {v_r}")
        
        cmd = f"WHEELS speed {v_l} {v_r}\n"
        if v_l == 0 and v_r == 0:
            cmd = f"STOP\n"
        
        
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