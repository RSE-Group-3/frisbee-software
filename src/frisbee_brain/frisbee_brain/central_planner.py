import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool
from geometry_msgs.msg import PoseStamped

class CentralPlanner(Node):
    def __init__(self):
        super().__init__('central_planner')
        
        self.current_state = "MODE_STARTUP"
        
        self.launcher_cmd = self.create_publisher(String, 'launcher/interface/cmd', 10)
        self.collector_cmd = self.create_publisher(String, 'collector/interface/cmd', 10)
        self.path_goal_pub = self.create_publisher(PoseStamped, 'path_planner/goal', 10)
        
        self.create_subscription(String, 'robot/current_state', self.state_cb, 10)
        self.create_subscription(PoseStamped, 'perception/frisbee_pose', self.frisbee_cb, 10)
        
        self.create_timer(0.1, self.planner_loop)

    def state_cb(self, msg):
        self.current_state = msg.data

    def frisbee_cb(self, msg):
        if self.current_state in ["MODE_SEARCHING", "MODE_COLLECTING"]:
            self.path_goal_pub.publish(msg)

    def planner_loop(self):
        if self.current_state == "MODE_COLLECTING":
            # Command Collector Interface to prepare for intake
            self.collector_cmd.publish(String(data="prepare_intake"))
            
        elif self.current_state == "MODE_LAUNCHING":
            # Command Launcher Interface to execute throw
            self.launcher_cmd.publish(String(data="initiate_launch_sequence"))
            
        elif self.current_state == "MODE_RETURNING":
            # Send home coordinates to Mobility Subsystem
            home_pose = PoseStamped() # Assume origin for this example
            self.path_goal_pub.publish(home_pose)
            
        elif self.current_state == "MODE_SAFESTOP":
            # Stop all actuators across subsystems
            self.launcher_cmd.publish(String(data="emergency_halt"))
            self.collector_cmd.publish(String(data="emergency_halt"))

def main(args=None):
    rclpy.init(args=args)
    node = CentralPlanner()
    rclpy.spin(node)
    rclpy.shutdown()