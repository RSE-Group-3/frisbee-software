import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from std_srvs.srv import Trigger
from enum import IntEnum

class PlannerMode(IntEnum):
    IDLE = 0
    LISTENING = 1
    SEARCHING = 2
    APPROACHING = 3
    COLLECTING = 4
    RETURNING = 5
    LAUNCHING = 6

VALID_TASKS = {
    'listen': PlannerMode.LISTENING,
    'search': PlannerMode.SEARCHING,
    'approach': PlannerMode.APPROACHING,
    'collect': PlannerMode.COLLECTING,
    'return': PlannerMode.RETURNING,
    'launch': PlannerMode.LAUNCHING
}

class CentralPlanner(Node):
    def __init__(self):
        super().__init__('central_planner')

        self.nav_cmd_pub = self.create_publisher(String, 'nav/cmd', 10)
        self.manip_cmd_pub = self.create_publisher(String, 'manipulation/cmd', 10)

        self.nav_status_sub = self.create_subscription(String, 'nav/status', self.nav_status_callback, 10)
        self.manip_status_sub = self.create_subscription(String, 'manipulation/status', self.manip_status_callback, 10)
        self.command_sub = self.create_subscription(String, 'command_sequence', self.command_sequence_callback, 10)

        self.mode = PlannerMode.IDLE
        self.chain = []
        self.command_index = 0

        self.listening_done = False
        self.search_done = False
        self.approach_done = False
        self.collect_done = False
        self.return_done = False
        self.launch_done = False

        self.create_timer(0.1, self.planner_loop)
        self.get_logger().info("CentralPlanner initialized.")

    #####################################################
    
    def command_sequence_callback(self, msg):
        cmd_list = [cmd.strip() for cmd in msg.data.split(',')]
        if len(cmd_list) == 1 and cmd_list[0] == 'demo':
            cmd_list = ['listen', 'search', 'approach', 'collect', 'return', 'launch']
        else:
            for cmd in cmd_list:
                if cmd not in VALID_TASKS:
                    self.get_logger().error(f"Invalid command in sequence: {cmd}")
                    return
        self.chain = cmd_list
        self.command_index = 0
        self.get_logger().info(f"Starting command sequence: {','.join(self.chain)}")
        self.start_next_command()

    def start_next_command(self):
        if self.command_index >= len(self.chain):
            self.get_logger().info("Command sequence complete.")
            self.mode = PlannerMode.IDLE
            self.chain = []
            self.command_index = 0
            return

        cmd = self.chain[self.command_index]
        self.mode = VALID_TASKS[cmd]

        if cmd == 'listen':
            assert False # unimplemented
        elif cmd in ['search', 'approach', 'return']:
            self.nav_cmd_pub.publish(String(data=cmd))
        elif cmd == 'collect':
            self.manip_cmd_pub.publish(String(data='collector.collect'))
        elif cmd == 'launch':
            self.manip_cmd_pub.publish(String(data='launcher.launch'))

        self.get_logger().info(f"Executing task: {cmd.upper()}")
        self.command_index += 1

    #####################################################
    
    def nav_status_callback(self, msg):
        if msg.data == 'search_done':
            self.search_done = True
        elif msg.data == 'approach_done':
            self.approach_done = True
        elif msg.data == 'return_done':
            self.return_done = True

    def manip_status_callback(self, msg):
        if msg.data == 'collect_done':
            self.collect_done = True
        elif msg.data == 'launch_done':
            self.launch_done = True

    #####################################################
    
    def planner_loop(self):
        if self.mode == PlannerMode.LISTENING and self.listening_done:
            self.listening_done = False
            self.start_next_command()
        elif self.mode == PlannerMode.SEARCHING and self.search_done:
            self.search_done = False
            self.start_next_command()
        elif self.mode == PlannerMode.APPROACHING and self.approach_done:
            self.approach_done = False
            self.start_next_command()
        elif self.mode == PlannerMode.COLLECTING and self.collect_done:
            self.collect_done = False
            self.start_next_command()
        elif self.mode == PlannerMode.RETURNING and self.return_done:
            self.return_done = False
            self.start_next_command()
        elif self.mode == PlannerMode.LAUNCHING and self.launch_done:
            self.launch_done = False
            self.start_next_command()

def main(args=None):
    rclpy.init(args=args)
    node = CentralPlanner()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()