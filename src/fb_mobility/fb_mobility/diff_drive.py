import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Float64MultiArray
from geometry_msgs.msg import Twist
import numpy as np

# WHEEL_RADIUS = 0.09
# WHEEL_SEPARATION = 0.908
# LOWER_LIMIT = 150
# UPPER_LIMIT = 150
# PWM_SCALE = 100

MOVING = 1
MOVING_OTHER = 0
TURN = 1
TURN_OTHER = -1

class DiffDriveSerial(Node):
    def __init__(self):
        super().__init__('diffdrive_serial')

        self.vel_sub = self.create_subscription(Twist, '/cmd_vel', self.callback, 10)
        self.serial_pub = self.create_publisher(String, 'arduino/launcher/cmd', 10) # using same arduino
        self.left_gazebo_pub = self.create_publisher(Float64MultiArray, 'left_wheel_velocity_controller/commands', 10) # for gazebo only
        self.right_gazebo_pub = self.create_publisher(Float64MultiArray, 'right_wheel_velocity_controller/commands', 10)

        self.get_logger().info(f"Started Diff Drive node")
    
    # def callback(self, msg):
    #     v = msg.linear.x
    #     w = msg.angular.z

    #     v_l = (v - (w * WHEEL_SEPARATION / 2.0)) / WHEEL_RADIUS
    #     v_r = (v + (w * WHEEL_SEPARATION / 2.0)) / WHEEL_RADIUS

    #     pwm_l = v_l * PWM_SCALE
    #     if pwm_l:
    #         pwm_l = pwm_l/abs(pwm_l) * np.clip(abs(pwm_l), LOWER_LIMIT, UPPER_LIMIT)
    #     pwm_r = v_r * PWM_SCALE
    #     if pwm_r:
    #         pwm_r = pwm_r/abs(pwm_r) * np.clip(abs(pwm_r), LOWER_LIMIT, UPPER_LIMIT)

    #     self.get_logger().info(f"===")
    #     self.get_logger().info(f"Left velocity: {v_l}, Right velocity: {v_r}")
    #     self.get_logger().info(f"Left PWM: {pwm_l}, Right PWM: {pwm_r}")

    #     cmd = f"WHEELS speed {pwm_l:.3f} {pwm_r:.3f}\n"
        
    #     self.serial_pub.publish(String(data=cmd))
    #     left_data = Float64MultiArray(data=[v_l])
    #     right_data = Float64MultiArray(data=[v_r])
    #     self.left_gazebo_pub.publish(left_data)
    #     self.right_gazebo_pub.publish(right_data)

    def callback(self, msg):
        v = msg.linear.x
        w = msg.angular.z
        self.get_logger().info(f"v: {v}, w: {w}")

        if v > 0:
            if w < 0:
                v_l, v_r = MOVING, MOVING_OTHER
            elif w == 0:
                v_l, v_r = MOVING, MOVING
            else:
                v_l, v_r = MOVING_OTHER, MOVING
        elif v == 0:
            if w < 0:
                v_l, v_r = TURN, TURN_OTHER
            elif w == 0:
                v_l, v_r = 0, 0
            else:
                v_l, v_r = TURN_OTHER, TURN
        
        elif v < 0:
            if w < 0:
                v_l, v_r = -MOVING_OTHER, -MOVING
            elif w == 0:
                v_l, v_r = -MOVING, -MOVING
            else:
                v_l, v_r = -MOVING, -MOVING_OTHER

        self.get_logger().info(f"===")
        self.get_logger().info(f"Left velocity: {v_l}, Right velocity: {v_r}")
        # self.get_logger().info(f"Left PWM: {v_l}, Right PWM: {v_r}")
        
        cmd = f"WHEELS speed {v_l} {v_r}\n"
        if v_l == 0 and v_r == 0:
            cmd = f"STOP\n"
        
        self.serial_pub.publish(String(data=cmd))
        left_data = Float64MultiArray(data=[v_l])
        right_data = Float64MultiArray(data=[v_r])
        self.left_gazebo_pub.publish(left_data)
        self.right_gazebo_pub.publish(right_data)


def main():
    rclpy.init()
    node = DiffDriveSerial()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if rclpy.ok():
            node.destroy_node()
            rclpy.shutdown()

if __name__ == '__main__':
    main()