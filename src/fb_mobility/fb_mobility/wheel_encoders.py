import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Float64MultiArray
from sensor_msgs.msg import JointState

RPM_TO_RAD_S = 2 * 3.141592653589793 / 60.0

class WheelEncoders(Node):
    def __init__(self):
        super().__init__('diffdrive_serial')

        self.serial_sub = self.create_subscription(String, 'arduino/launcher/status', self.callback, 10)
        
        self.joint_pub = self.create_publisher(JointState, 'joint_states', 10)
        self.current_vel_pub = self.create_publisher(Float64MultiArray, 'wheels/current_velocity_rpm', 10)
        self.target_vel_pub = self.create_publisher(Float64MultiArray, 'wheels/target_velocity_rpm', 10)
        self.vel_err_pub = self.create_publisher(Float64MultiArray, 'wheels/velocity_error_rpm', 10)
        self.pwm_pub = self.create_publisher(Float64MultiArray, 'wheels/pwm', 10)

        self.get_logger().info(f"Started Wheel Encoders node")
    
    def callback(self, msg: String):
        # String(data=f'WHEELS_ENC|CL:0.00 TL:0.00 PL:0.00|CR:0.00 TR:0.00 PR:0.00')
        data = msg.data
        
        def parse_section(section):
            values = {}
            for item in section.split():
                key, val = item.split(':')
                values[key] = float(val)
            return values
        
        try:
            if not data.startswith('WHEELS_ENC'): return
            _, left_part, right_part = data.split('|')
            left = parse_section(left_part)
            right = parse_section(right_part)
            
        except ValueError:
            self.get_logger().warn(f"Bad data: {data}")
            return


        left_vel_rads = left['CL'] * RPM_TO_RAD_S
        right_vel_rads = right['CR'] * RPM_TO_RAD_S

        joint_msg = JointState()
        joint_msg.header.stamp = self.get_clock().now().to_msg()
        joint_msg.name = ['left_wheel', 'right_wheel']
        joint_msg.velocity = [left_vel_rads, right_vel_rads]

        self.joint_pub.publish(joint_msg)

        current_vel_msg = Float64MultiArray()
        current_vel_msg.data = [left['CL'], right['CR']]
        target_vel_msg = Float64MultiArray()
        target_vel_msg.data = [left['TL'], right['TR']]
        vel_err_msg = Float64MultiArray()
        vel_err_msg.data = [left['TL'] - left['CL'], right['TR'] - right['CR']]
        pwm_msg = Float64MultiArray()
        pwm_msg.data = [left['PL'], right['PR']]
        self.current_vel_pub.publish(current_vel_msg)
        self.target_vel_pub.publish(target_vel_msg)
        self.vel_err_pub.publish(vel_err_msg)
        self.pwm_pub.publish(pwm_msg)

def main():
    rclpy.init()
    node = WheelEncoders()
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