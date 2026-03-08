import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from sensor_msgs.msg import Image

import cv2
from cv_bridge import CvBridge

class AirTrackerNode(Node):
    def __init__(self):
        super().__init__('air_tracker_node')
        
        self.front_image_sub = self.create_subscription(
            Image,
            'front_robot_cam/image_raw',
            self.image_callback,
            10
        )
            
        self.results_pub = self.create_publisher(String, 'vision/air_results', 10)
        
        self.get_logger().info("Air Tracker Node Initialized")


    def image_callback(self, msg):
        self.get_logger().info("Received image data for processing")
        
        # Convert ROS Image message to OpenCV format
        bridge = CvBridge()
        try:
            cv_image = bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as e:
            self.get_logger().error(f"Error converting image: {e}")
            return
        
        results = 'dummy air tracker result'
        
        result_msg = String()
        result_msg.data = results
        self.results_pub.publish(result_msg)


def main(args=None):
    rclpy.init(args=args)
    node = AirTrackerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()