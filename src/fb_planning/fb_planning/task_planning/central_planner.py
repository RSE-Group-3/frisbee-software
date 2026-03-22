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
        print('=========================================')
        cmd = input('TESTS\n' +
                    '\n' +
                    '0 listen\n' +
                    '1 search\n' +
                    '2 approach\n' +
                    '3 collect\n' +
                    '4 launch\n' +
                    '\n' +
                    '01 listen,search\n' +
                    '12 search,approach\n' +
                    '23 approach,collect\n' +
                    '34 collect,launch\n' +
                    '\n' +
                    'm manual_serial\n' +
                    '\n' +
                    '01234 demo \n' +
                    '\n' +
                    't teleop \n' +
                    'r rotate \n' +
                    '\n' +
                    'Enter test: '
                    )
        print('=========================================')
        
        match cmd:
            case '0': 
                self.test_listen(auto_start=False)
            case '1': 
                self.test_search(auto_start=False)
            case '2': 
                self.test_approach(auto_start=False)
            case '3': 
                self.test_collect(auto_start=False)
            case '4': 
                self.test_launch(auto_start=False)

            case '01': 
                self.test_listen(auto_start=False)
                self.test_search(auto_start=False)
            case '12': 
                self.test_search(auto_start=False)
                self.test_approach(auto_start=False)
            case '23': 
                self.test_approach(auto_start=False)
                self.test_collect(auto_start=False)
            case '34': 
                self.test_collect(auto_start=False)
                self.test_launch(auto_start=False)

            case 'm': 
                self.test_manual_serial()
                
            case '01234': 
                print('unimplemented')
            case _: 
                print('Invalid test name.')
        
            
    def test_listen(self, auto_start=True):
        if not auto_start: 
            input('TEST 0 listen. \Enter to begin listening:')
        return True
    
    def test_search(self, auto_start=True):
        if not auto_start: 
            input('TEST 1 search. \nEnter an angle to begin searching (default 0):')
        return True
    
    def test_approach(self, auto_start=True):
        if not auto_start: 
            input('TEST 2 approach. \nEnter to begin approaching:')
        return True
    
    def test_collect(self, auto_start=True):
        if not auto_start: 
            input('TEST 3 collect. \nMake sure frisbee is aligned with collector. \nPress start to reset collector and collect:')
        return True
    
    def test_launch(self, auto_start=True):
        if not auto_start: 
            input('TEST 4 launch. \nPress enter to launch:')
        self.launcher_cmd_pub.publish(Int32(data=1))
        return True


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