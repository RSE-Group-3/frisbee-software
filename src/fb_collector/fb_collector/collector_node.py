import rclpy
from rclpy.node import Node
from std_msgs.msg import String

import time

class CollectorNode(Node):
    def __init__(self):
        super().__init__('collector_control_node')
        
        pass

    def collector_cmd_callback(self, msg):
        command = msg.data
        self.get_logger().info(f"Received Command: {command}")
        
        if command == "prepare_intake":
            self.run_intake_sequence()
            
        elif command == "emergency_halt":
            self.stop_all_motors()

    def run_intake_sequence(self):
        # Need to fill the hardware logic here
        self.get_logger().info("HARDWARE: Spinning Intake Motors at 80% Power...")
        time.sleep(5.0) 

        self.get_logger().info("HARDWARE: Intake Complete!")
        
        status_msg = String()
        status_msg.data = "collector_success"
        self.event_pub.publish(status_msg)

    def stop_all_motors(self):
        self.get_logger().warn("HARDWARE: EMERGENCY STOP - Stop Collection")
        # Need to fill the hardware logic here

def main(args=None):
    rclpy.init(args=args)
    node = CollectorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()