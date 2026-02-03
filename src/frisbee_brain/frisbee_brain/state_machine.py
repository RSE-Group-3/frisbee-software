import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class FrisbeeStateMachine(Node):
    def __init__(self):
        super().__init__('state_machine')
        self.state = "MODE_STARTUP"
        self.state_pub = self.create_publisher(String, 'robot/current_state', 10)
        self.create_subscription(String, 'robot/events', self.event_callback, 10)
        self.timer = self.create_timer(0.1, self.publish_state)
        self.get_logger().info("State Machine Initialized in MODE_STARTUP")
        print(self.state)

    def event_callback(self, msg):
        event = msg.data
        new_state = self.state
        
        # --- State Transition Logic ---
        if self.state == "MODE_STARTUP":
            if event == "safety_checks_passed": new_state = "MODE_LISTENING"
            elif event == "safety_check_failed": new_state = "MODE_SHUTDOWN"

        elif self.state == "MODE_LISTENING":
            if event == "user_cmd_collect": new_state = "MODE_SEARCHING"
            elif event == "user_cmd_launch": new_state = "MODE_LAUNCHING"

        elif self.state == "MODE_SEARCHING":
            if event == "path_planner_found_frisbee": new_state = "MODE_COLLECTING"
            elif event == "mapper_no_more_frisbees": new_state = "MODE_RETURNING"

        elif self.state == "MODE_COLLECTING":
            if event == "collector_success": new_state = "MODE_SEARCHING"

        elif self.state == "MODE_RETURNING":
            if event == "pathplanner_returned_home": new_state = "MODE_LISTENING"

        elif self.state == "MODE_LAUNCHING":
            if event == "launcher_success": new_state = "MODE_LISTENING"

        # --- Global Logic ---
        if "request_shutdown" in event:
            new_state = "MODE_SHUTDOWN"
        elif "request_safestop" in event:
            new_state = "MODE_SAFESTOP"
        elif self.state == "MODE_SAFESTOP" and event == "user_okay":
            new_state = "MODE_LISTENING" # Return to a ready state

        if new_state != self.state:
            self.get_logger().info(f"Transition: {self.state} -> {new_state}")
            self.state = new_state

    def publish_state(self):
        self.state_pub.publish(String(data=self.state))

def main(args=None):
    rclpy.init(args=args)
    node = FrisbeeStateMachine()
    rclpy.spin(node)
    rclpy.shutdown()