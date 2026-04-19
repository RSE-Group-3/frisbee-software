import time

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from std_msgs.msg import String
from fb_interfaces.action import ExecuteCommand

from fb_planning.utils.planner_utils import RobotStates
from fb_planning.utils import planner_utils


class CentralPlanner(Node):
    def __init__(self):
        super().__init__('central_planner')

        # clients
        self.manip_client = ActionClient(self, ExecuteCommand, 'manipulation/execute')
        self.nav_client = ActionClient(self, ExecuteCommand, 'navigation/execute')
        # self.vision_client = ActionClient(self, ExecuteCommand, 'vision/execute')

        # subscriptions
        self.user_sub = self.create_subscription(String, 'user_input', self.user_input_callback, 10)

        self.state = RobotStates.IDLE
        self.chain = []
        self.task_idx = 0
        self.done = False

        self.create_timer(0.1, self.planner_loop)

        self.get_logger().info("CentralPlanner initialized.")

    ########################################################

    def user_input_callback(self, msg: String):
        try:
            task_str = msg.data.strip()
            self.get_logger().info(f'Received user input: "{task_str}"')
            task_list = [cmd.strip() for cmd in task_str.split(',')]

            assert planner_utils.is_valid_task_list(task_list)

            if 'stop' in task_list:
                self.get_logger().warn(f"User requested stop. Stopping task sequence: {self.chain}")
                self.chain = ['stop']
                self.task_idx = 0
                self.start_next_command()
            elif self.state == RobotStates.IDLE:
                self.chain = task_list
                self.task_idx = 0
                self.get_logger().warn(f"Starting task sequence: {self.chain}")
                self.start_next_command()
            else:
                self.get_logger().error(f"Robot busy. Ignoring user input: {task_list}")

        except Exception as e:
            self.get_logger().error(f"Error processing user input: {msg.data} | {e}")

    # =====================================================
    # TASK EXECUTION
    # =====================================================

    def start_next_command(self):
        if self.task_idx >= len(self.chain):
            self.get_logger().info("Sequence complete.")
            self._reset()
            return

        task = self.chain[self.task_idx].split()[0]
        task_with_args = self.chain[self.task_idx]
        self.get_logger().info(f"Executing: {task}")

        self.state = planner_utils.task_to_state(task)

        if task == 'stop':
            # TODO: other stop logic
            self._send_manip_goal(task_with_args)
            self._send_nav_goal(task_with_args)
            self.done = True
        elif task in ['predict', 'reset_track']:
            self._handle_unimplemented(task)
        elif task in ['search', 'approach', 'return', 'reset_pos']:
            self._send_nav_goal(task_with_args)
        elif task in ['collect', 'launch', 'reset_mech']:
            self._send_manip_goal(task_with_args)
        else:
            self.get_logger().error(f"Unknown task: {task}")
            self.done = True

        self.task_idx += 1

    def _handle_unimplemented(self, task):
        self.get_logger().warn(f"{task} UNIMPLEMENTED")
        time.sleep(1)
        self.done = True

    def _send_nav_goal(self, task):
        goal_msg = ExecuteCommand.Goal()
        goal_msg.command = task

        self.nav_client.wait_for_server()

        future = self.nav_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )
        future.add_done_callback(self.goal_response_callback)

    def _send_manip_goal(self, task):
        goal_msg = ExecuteCommand.Goal()
        goal_msg.command = task

        self.manip_client.wait_for_server()

        future = self.manip_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )
        future.add_done_callback(self.goal_response_callback)

    def _reset(self):
        self.state = RobotStates.IDLE
        self.chain = []
        self.task_idx = 0

    ########################################################

    def goal_response_callback(self, future):
        goal_handle = future.result()

        if not goal_handle.accepted:
            self.get_logger().error("Goal rejected.")
            self.done = True
            return

        self.get_logger().info("Goal accepted.")

        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.result_callback)

    def result_callback(self, future):
        result = future.result().result
        if result.success:
            self.get_logger().info(f"Result: {result.success}, {result.message}")
        else:
            self.get_logger().error(f"Result: {result.success}, {result.message}")
        self.done = True

    def feedback_callback(self, feedback_msg):
        status = feedback_msg.feedback.status
        self.get_logger().info(f"Feedback: {status}")

    ########################################################

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