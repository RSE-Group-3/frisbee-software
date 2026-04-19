#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Imu
import board
import busio
import adafruit_bno055


class BNO055IMUPublisher(Node):
    def __init__(self):
        super().__init__('bno055_imu_publisher')

        self.publisher_ = self.create_publisher(Imu, '/imu/data', 10)
        self.timer = self.create_timer(0.05, self.timer_callback)  # 20 Hz

        # Initialize I2C and sensor
        i2c = busio.I2C(board.SCL, board.SDA)
        self.sensor = adafruit_bno055.BNO055_I2C(i2c)

        self.get_logger().info("BNO055 IMU Publisher started")

    def timer_callback(self):
        imu_msg = Imu()

        # Orientation (quaternion not directly provided -> use Euler if needed)
        quat = self.sensor.quaternion  # (x, y, z, w)

        if quat is not None:
            imu_msg.orientation.x = quat[0]
            imu_msg.orientation.y = quat[1]
            imu_msg.orientation.z = quat[2]
            imu_msg.orientation.w = quat[3]

        # Angular velocity (rad/s)
        gyro = self.sensor.gyro
        if gyro is not None:
            imu_msg.angular_velocity.x = gyro[0]
            imu_msg.angular_velocity.y = gyro[1]
            imu_msg.angular_velocity.z = gyro[2]

        # Linear acceleration (m/s^2)
        accel = self.sensor.acceleration
        if accel is not None:
            imu_msg.linear_acceleration.x = accel[0]
            imu_msg.linear_acceleration.y = accel[1]
            imu_msg.linear_acceleration.z = accel[2]

        # Frame
        imu_msg.header.stamp = self.get_clock().now().to_msg()
        imu_msg.header.frame_id = "imu_link"

        self.publisher_.publish(imu_msg)


def main(args=None):
    rclpy.init(args=args)
    node = BNO055IMUPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()