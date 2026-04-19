import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Twist
from fb_interfaces.action import ExecuteCommand
from rclpy.action import ActionServer
from rclpy.task import Future

TIMEOUT = 600 # s

CENTER_DEADZONE = 0.1 # normalized based on image width (0 to 1)
TURN_STEP = 5.0 # deg
FORWARD_TIME = 0.15 # s
PAUSE_TIME = 1.0 # s to let vision catch up

class PathPlanner(Node):
    def __init__(self):
        super().__init__('path_planner_node')

        self.frisbee_center_sub = self.create_subscription(String, '/vision/ground_segmentation/center', self.frisbee_center_callback, 10)
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        self.action = ActionServer(
            self,
            ExecuteCommand,
            'navigation/execute',
            self.execute_callback
        )

        self.get_logger().info("Path planner node online.")

        self.command_in_progress = None
        self.timer = None
        self.goal_handle = None
        self._done_future = None

        self.frisbee_center = None
        self.state = "ALIGN"
        self.state_start_time = self.get_clock().now()
        
        self.main_loop_timer = self.create_timer(0.1, self.main_loop)
        

    def frisbee_center_callback(self, msg):
        try:
            self.frisbee_center = tuple(map(int, msg.data.strip().split()))
            self.frisbee_center = (self.frisbee_center[0]/320, self.frisbee_center[1]/240)
        except:
            self.get_logger().error(f"Could not parse frisbee center message ({msg.data})")

    def approach(self):
        if self.frisbee_center is None:
            self.get_logger().warn("Waiting for frisbee center...")
            return

        now = self.get_clock().now()

        # normalized x: 0 (left) → 1 (right), center = 0.5
        error_x = self.frisbee_center[0] - 0.5

        twist = Twist()

        if self.state == "ALIGN":

            if abs(error_x) < CENTER_DEADZONE:
                self.get_logger().info("Aligned. Switching to APPROACH")
                self.state = "APPROACH"
                self.state_start_time = now
                return

            # small discrete turn
            direction = -1.0 if error_x > 0 else 1.0

            twist.angular.z = direction * 0.5  # low angular speed
            self.cmd_vel_pub.publish(twist)

            self.state = "WAIT_AFTER_TURN"
            self.state_start_time = now

        elif self.state == "WAIT_AFTER_TURN":
            # stop motion
            self.cmd_vel_pub.publish(Twist())

            if (now - self.state_start_time).nanoseconds > int(PAUSE_TIME * 1e9):
                self.state = "ALIGN"

        elif self.state == "APPROACH":
            # if too off-center, go back to align
            if abs(error_x) > CENTER_DEADZONE:
                self.get_logger().info("Drift detected. Re-aligning")
                self.state = "ALIGN"
                return

            # forward burst
            twist.linear.x = 0.3
            self.cmd_vel_pub.publish(twist)

            self.state = "WAIT_AFTER_FORWARD"
            self.state_start_time = now

        elif self.state == "WAIT_AFTER_FORWARD":
            # stop
            self.cmd_vel_pub.publish(Twist())

            if (now - self.state_start_time).nanoseconds > int(PAUSE_TIME * 1e9):
                self.state = "APPROACH"

        if self.frisbee_center[1] > 0.8:
            self.get_logger().info("APPROACH COMPLETE")

            result = ExecuteCommand.Result()
            result.success = True
            result.message = "Nav approach complete"
            self.state = "ALIGN"
            self._reset_and_return_future(result)

    def main_loop(self):
        if self.command_in_progress == 'approach':
            self.approach()    
    
        elif self.command_in_progress == 'stop':
            msg = Twist()
            msg.linear.x = 1.0
            msg.angular.z = 1.0
            self.cmd_vel_pub.publish(msg)

            self.get_logger().warn(f"Stopped wheel motors")

            result = ExecuteCommand.Result()
            result.success = True
            result.message = f"Nav stopped wheel motors"
            self._reset_and_return_future(result)
            return result
        
        elif self.command_in_progress is not None:
            self.get_logger().error(f"Unexpected command")


    def _parse_action_goal(self, msg: str):
        task_tokens = msg.strip().split()
        task, args = task_tokens[0], task_tokens[1:]

        return task


    async def execute_callback(self, goal_handle):
        request = goal_handle.request
        result = ExecuteCommand.Result()

        try:
            msg = request.command
            task = self._parse_action_goal(msg)

            if self.command_in_progress is not None and task != 'stop':
                result.success = False
                result.message = f"Nav task {self.command_in_progress} in progress"
                goal_handle.abort()
                return result

            self.get_logger().warn(f"Starting command sequence: {task}")

            feedback = ExecuteCommand.Feedback()
            feedback.status = f'Nav started "{task}"'
            goal_handle.publish_feedback(feedback)

            self.command_in_progress = task
            self.goal_handle = goal_handle

            if self.timer:
                self.timer.cancel()
            self.timer = self.create_timer(TIMEOUT, self._command_timeout)
            
            self._done_future = Future()

            result = await self._done_future
            return result

        except Exception as e:
            result.success = False
            result.message = f'Nav error parsing command "{request.command}": {e}'
            goal_handle.abort()
            return result


    def _command_timeout(self):
        if not self.current_sequence or self.current_index >= len(self.current_sequence):
            return

        cmd = self.current_sequence[self.current_index]

        self.get_logger().warn(f"Timeout on command {cmd}")

        result = ExecuteCommand.Result()
        result.success = False
        result.message = f"Nav timeout on command {cmd}"

        self._reset_and_return_future(result)

    def _reset_and_return_future(self, result):
        if self.timer:
            self.timer.cancel()
            self.timer = None
        self.goal_handle.abort()
        self.command_in_progress = None

        if self._done_future and not self._done_future.done():
            self._done_future.set_result(result)


def main(args=None):
    rclpy.init(args=args)
    node = PathPlanner()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.serial_cmd_pub.publish(String(data="STOP"))
        node.get_logger().warn("STOP triggered by Ctrl-C")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()


# tune: "center" trapezoid range, and "far" y<100 range

# if frisbee close and not in center, back up slowly until frisbee is far (doesn't need to be super precise)

# turn based on error until frisbee is near center (vision feedback)

# approach in straight line with imu fine tuning 
