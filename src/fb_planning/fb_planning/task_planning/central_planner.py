import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from std_srvs.srv import Trigger

import time

from ..utils.planner_utils import RobotStates
from ..utils import planner_utils

class CentralPlanner(Node):
    def __init__(self):
        super().__init__('central_planner')

        self.vision_cmd_pub = self.create_publisher(String, 'vision/cmd', 10)
        self.nav_cmd_pub = self.create_publisher(String, 'nav/cmd', 10)
        self.manip_cmd_pub = self.create_publisher(String, 'manipulation/cmd', 10)

        self.vision_status_sub = self.create_subscription(String, 'vision/status', self.vision_status_callback, 10)
        self.nav_status_sub = self.create_subscription(String, 'nav/status', self.nav_status_callback, 10)
        self.manip_status_sub = self.create_subscription(String, 'manipulation/status', self.manip_status_callback, 10)
        self.command_sub = self.create_subscription(String, 'command_sequence', self.command_sequence_callback, 10)

        self.state = RobotStates.IDLE
        self.chain = []
        self.task_idx = 0
        self.done = False

        self.create_timer(0.1, self.planner_loop)
        self.get_logger().info("CentralPlanner initialized.")

        self.debug = False # simulate task execution

    #####################################################
    
    def command_sequence_callback(self, msg):
        task_list = [cmd.strip() for cmd in msg.data.split(',')]
        assert planner_utils.is_valid_task_list(task_list)

        if 'stop' in task_list:
            self.safestop()
        elif self.state == RobotStates.IDLE:
            self.chain = task_list
            self.task_idx = 0
            self.get_logger().warn(f"Starting command sequence: {self.chain}")
            self.start_next_command()
        else:
            self.get_logger().error(f"Robot is busy, ignoring command sequence: {self.chain}")

    def safestop(self):
        self.get_logger().warn("Safestop, stopping command sequence.")
        self.get_logger().info(f"Exiting state: {self.state.name}.")
        self.state = RobotStates.IDLE
        self.chain = []
        self.task_idx = 0
        # TODO: other safestop logic

    def start_next_command(self):
        if self.task_idx >= len(self.chain):
            self.get_logger().info("Command sequence complete.")
            self.state = RobotStates.IDLE
            self.chain = []
            self.task_idx = 0
            return
        
        task = self.chain[self.task_idx]
        self.get_logger().info(f"Executing task: {task}")
        self.state = planner_utils.task_to_state(task)

        if self.debug:
            self.get_logger().info(f"sleeping..."); time.sleep(1); self.get_logger().info(f"done.")
            self.done = True
        else:
            if task == 'predict':
                self.get_logger().error(f"UNIMPLEMENTED")
                self.get_logger().info(f"sleeping..."); time.sleep(1); self.get_logger().info(f"done.")
                self.done = True

            elif task in ['search', 'approach', 'return']:
                self.get_logger().error(f"UNIMPLEMENTED")
                self.get_logger().info(f"sleeping..."); time.sleep(1); self.get_logger().info(f"done.")
                self.done = True
                
                # self.nav_cmd_pub.publish(String(data=task))

            elif task == 'collect':
                self.manip_cmd_pub.publish(String(data='collector.collect'))

            elif task == 'launch':
                self.manip_cmd_pub.publish(String(data='launcher.launch'))

        self.task_idx += 1

    #####################################################
    
    def parse_subsystem_status(self, msg: String):
        try:
            msg_data = msg.data.strip().split(";")
            return msg_data[0].strip(), msg_data[1].strip(), ';'.join(msg_data[2:])
        except:
            self.get_logger().fatal(f"Bad subsystem status message: {msg.data}")

    def vision_status_callback(self, msg: String):
        cmd, status, info = self.parse_subsystem_status(msg)
        if status: 
            self.done = True

    def nav_status_callback(self, msg: String):
        cmd, status, info = self.parse_subsystem_status(msg)
        if status: 
            self.done = True

    def manip_status_callback(self, msg: String):
        cmd, status, info = self.parse_subsystem_status(msg)
        if status: 
            self.done = True

    #####################################################
    
    def planner_loop(self):
        if self.done:
            self.done = False
            self.start_next_command()

def main(args=None):
    rclpy.init(args=args)
    node = CentralPlanner()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()