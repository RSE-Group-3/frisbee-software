import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool, Int32
from geometry_msgs.msg import PoseStamped
from fb_utils.fb_msgs import LauncherCmd, LauncherAck, CollectorCmd, CollectorAck

from enum import IntEnum

class PlannerMode(IntEnum):
    STARTUP = 0
    LISTENING = 1
    SEARCHING = 2
    COLLECTING = 3
    RETURNING = 4
    LAUNCHING = 5
    SAFESTOP = 6

class CentralPlanner(Node):
    def __init__(self):
        super().__init__('central_planner')
        
        self.arduino_cmd_pub = self.create_publisher(Int32, 'arduino/cmd', 10)
        self.arduino_ack_sub = self.create_subscription(Int32, 'arduino/ack', self.arduino_callback, 10)

        self.launcher_cmd_pub = self.create_publisher(Int32, 'launcher/cmd', 10)
        self.launcher_ack_sub = self.create_subscription(Int32, 'launcher/status', self.launcher_callback, 10)
        self.collector_cmd_pub = self.create_publisher(Int32, 'collector/cmd', 10)
        self.collector_ack_sub = self.create_subscription(Int32, 'collector/status', self.collector_callback, 10)
        
        self.create_timer(0.1, self.planner_loop)

        self.state = PlannerMode.STARTUP

    def planner_loop(self):
        cmd = int(input("0 to reset, 1 to launch: "))
        assert cmd == 0 or cmd == 1
        self.launcher_cmd_pub.publish(Int32(data=cmd))
            

    def launcher_callback(self, msg):
        pass
        
    def collector_callback(self, msg):
        pass
    
    def arduino_callback(self, msg):
        pass

def main(args=None):
    rclpy.init(args=args)
    node = CentralPlanner()
    rclpy.spin(node)
    rclpy.shutdown()