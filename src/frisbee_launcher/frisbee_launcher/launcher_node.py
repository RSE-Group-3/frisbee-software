import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class LauncherNode(Node):
    def __init__(self):
        super().__init__('launcher_node')
        
        self.cmd_sub = self.create_subscription(
            String,
            'launcher/interface/cmd',
            self.launcher_callback,
            10)
            
        self.event_pub = self.create_publisher(String, 'robot/events', 10)
        
        self.get_logger().info("Launcher Subsystem Hardware Interface Online")

    def launcher_callback(self, msg):
        command = msg.data
        
        if command == "initiate_launch_sequence":
            self.get_logger().info("🚀 Command Received: Spinning up flywheels...")
            self.execute_launch()
        elif command == "emergency_halt":
            self.stop_motors()

    def execute_launch(self):
        # Need to fill the hardware logic here
        import time
        
        self.get_logger().info("Flywheels reaching target RPM...")
        time.sleep(1.5)
        
        self.get_logger().info("ACTUATING PUSHER: Launching frisbee!")
        time.sleep(0.5)

        self.get_logger().info("Launch Complete!")
        
        feedback = String()
        feedback.data = "launcher_success"
        self.event_pub.publish(feedback)

    def stop_motors(self):
        self.get_logger().warn("EMERGENCY STOP: Stop launcher")
        # Need to fill the hardware logic here

def main(args=None):
    rclpy.init(args=args)
    node = LauncherNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()