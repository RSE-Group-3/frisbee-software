import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Float64MultiArray
from geometry_msgs.msg import Twist

WHEEL_RADIUS = 0.09
WHEEL_SEPARATION = 0.908

class DiffDriveSerial(Node):
    def __init__(self):
        super().__init__('diffdrive_serial')

        self.vel_sub = self.create_subscription(Twist, '/cmd_vel', self.cb, 10)
        self.serial_pub = self.create_publisher(String, 'arduino/cmd', 10)
        self.left_gazebo_pub = self.create_publisher(Float64MultiArray, 'left_wheel_velocity_controller/commands', 10)
        self.right_gazebo_pub = self.create_publisher(Float64MultiArray, 'right_wheel_velocity_controller/commands', 10)
    
    def cb(self, msg):
        v = msg.linear.x
        w = msg.angular.z

        v_l = (v - (w * WHEEL_SEPARATION / 2.0)) / WHEEL_RADIUS
        v_r = (v + (w * WHEEL_SEPARATION / 2.0)) / WHEEL_RADIUS

        cmd = f"WHEELS speed {v_l:.3f} {v_r:.3f}\n"
        
        self.serial_pub.publish(String(data=cmd))
        
        left_data = Float64MultiArray(data=[v_l])
        right_data = Float64MultiArray(data=[v_r])

        self.left_gazebo_pub.publish(left_data)
        self.right_gazebo_pub.publish(right_data)

        self.get_logger().info(f"Left velocity: {v_l}, Right velocity: {v_r}")

def main():
    rclpy.init()
    node = DiffDriveSerial()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()