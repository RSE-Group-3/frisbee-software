import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Twist
from sensor_msgs.msg import CompressedImage, Image
from fb_interfaces.action import ExecuteCommand
from rclpy.action import ActionServer
from rclpy.task import Future
from cv_bridge import CvBridge
import cv2
import numpy as np

TIMEOUT = 600 # s

# X CENTER
CENTER = 183/320 
CENTER_DEADZONE_LOWER = 0.01 # normalized based on image width (0 to 1)
CENTER_DEADZONE_UPPER = 0.1 # normalized based on image width (0 to 1)

# Y CENTER
FRISBEE_TOP_GOAL = 191/240
FRISBEE_TOP_CLOSE = 150/240
FRISBEE_TOP_GOAL_ERROR = 5/240

LOOP_TIME = 0.1 # s
ERROR_SCALE = 10 # scale normalized error to get actual move time
ERROR_SCALE_INCREMENT = 4 # add to error scale when turning in the same direction
MIN_MOVE_TIME = 0.1 # s
MAX_MOVE_TIME_UPPER = 1.0 # s
MAX_MOVE_TIME_LOWER = 0.3 # s
PAUSE_TIME = 3.0 # s to let vision catch up
VERIFY_TIME = 1.0

LINEAR_X = 0.3
ANGULAR_Z = 0.5

class PathPlanner(Node):
    def __init__(self):
        super().__init__('path_planner_node')

        self.frisbee_center_sub = self.create_subscription(String, '/vision/ground_segmentation/center', self.frisbee_center_callback, 10)
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        self.image_sub = self.create_subscription(
            CompressedImage,
            'camera/collector/image_raw/compressed',
            self.image_callback,
            1
        )
        self.vis_pub = self.create_publisher(CompressedImage, '/path_planner/approach/visualization', 10)
        self.path_timer_pub = self.create_publisher(String, '/path_planner/approach/timers', 10)

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

        self.frisbee_center = (0.5, 0)
        self.frisbee_top = 0
        self.state = "ALIGN"
        self.state_start_time = self.get_clock().now()
        
        self.main_loop_timer = self.create_timer(LOOP_TIME, self.main_loop)

        self.last_rot_dir = 0
        self.rot_streak = 0
        self.rot_updated = False

    def visualize(self, image):
        h, w = image.shape[:2]

        vis = image.copy()

        # cv2.line(vis, (center_x, 0), (center_x, h), (255, 0, 0), 1)
        dz_left_bound = int(w * (CENTER - CENTER_DEADZONE_LOWER))
        dz_right_bound = int(w * (CENTER + CENTER_DEADZONE_LOWER))
        cv2.line(vis, (dz_left_bound, 0), (dz_left_bound, h), (255, 0, 0), 1)
        cv2.line(vis, (dz_right_bound, 0), (dz_right_bound, h), (255, 0, 0), 1)

        dz_left_bound = int(w * (CENTER - CENTER_DEADZONE_UPPER))
        dz_right_bound = int(w * (CENTER + CENTER_DEADZONE_UPPER))
        cv2.line(vis, (dz_left_bound, 0), (dz_left_bound, h), (255, 150, 0), 1)
        cv2.line(vis, (dz_right_bound, 0), (dz_right_bound, h), (255, 150, 0), 1)

        top_close = int(h * (FRISBEE_TOP_CLOSE))
        cv2.line(vis, (0, top_close), (w, top_close), (255, 150, 0), 1)

        top_goal_upper_bound = int(h * (FRISBEE_TOP_GOAL - FRISBEE_TOP_GOAL_ERROR))
        top_goal_lower_bound = int(h * (FRISBEE_TOP_GOAL + FRISBEE_TOP_GOAL_ERROR))
        cv2.line(vis, (0, top_goal_upper_bound), (w, top_goal_upper_bound), (255, 0, 0), 1)
        cv2.line(vis, (0, top_goal_lower_bound), (w, top_goal_lower_bound), (255, 0, 0), 1)

        cv2.drawMarker(
            vis,
            (int(self.frisbee_center[0] * w), int(self.frisbee_center[1] * h)),
            (0, 255, 0),
            markerType=cv2.MARKER_CROSS,
            markerSize=20,
            thickness=2
        )

        cv2.drawMarker(
            vis,
            (int(self.frisbee_center[0] * w), int(self.frisbee_top * h)),
            (0, 0, 255),
            markerType=cv2.MARKER_TILTED_CROSS,
            markerSize=20,
            thickness=2
        )

        return vis
        

    def image_callback(self, msg):
        # self.get_logger().info("Received image data for processing")
        
        bridge = CvBridge()
        try:
            cv_image = bridge.compressed_imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as e:
            self.get_logger().error(f"Error converting image: {e}")
            return
        
        vis = self.visualize(cv_image)

        vis_msg = bridge.cv2_to_compressed_imgmsg(vis)
        self.vis_pub.publish(vis_msg)


    def frisbee_center_callback(self, msg):
        try:
            frisbee_center_and_top = tuple(map(int, msg.data.strip().split()))
            if frisbee_center_and_top[0] != -1:
                self.frisbee_center = (frisbee_center_and_top[0]/320, frisbee_center_and_top[1]/240)
                self.frisbee_top = frisbee_center_and_top[2]/240
        except:
            self.get_logger().error(f"Could not parse frisbee center message ({msg.data})")


    def approach(self):
        if self.frisbee_center is None:
            self.get_logger().warn("Waiting for frisbee center...")
            return

        now = self.get_clock().now()

        error_x = self.frisbee_center[0] - CENTER
        error_y = self.frisbee_top - FRISBEE_TOP_GOAL

        twist = Twist()

        if self.state == "VERIFYING":
            if (now - self.state_start_time).nanoseconds > int(VERIFY_TIME * 1e9):
                if abs(error_x) < CENTER_DEADZONE_LOWER and abs(error_y) < FRISBEE_TOP_GOAL_ERROR:
                    self.get_logger().info("APPROACH COMPLETE")
                    result = ExecuteCommand.Result()
                    result.success = True
                    result.message = "Nav approach complete"
                    self._reset_and_return_future(result)
                    return
                else:
                    self.state = "ALIGN"
                    self.state_start_time = now
                    self.get_logger().info("reset start_time, aligning")
                    return
            
        # set based on y
        if self.frisbee_top < FRISBEE_TOP_CLOSE:
            center_deadzone = CENTER_DEADZONE_UPPER
            max_move_time = MAX_MOVE_TIME_UPPER
        else:
            center_deadzone = CENTER_DEADZONE_LOWER
            max_move_time = MAX_MOVE_TIME_LOWER

        elapsed = (now - self.state_start_time).nanoseconds / 1e9
        rot_interval = np.clip(abs(error_x) * ERROR_SCALE, MIN_MOVE_TIME, max_move_time)
        lin_interval = np.clip(abs(error_y) * ERROR_SCALE, MIN_MOVE_TIME, max_move_time)

        if self.state == "ALIGN":
            if abs(error_x) < center_deadzone and abs(error_y) < FRISBEE_TOP_GOAL_ERROR:
                
                self.get_logger().info("verifying")
                self.state = "VERIFYING"
                self.state_start_time = now
                self.get_logger().info("reset start_time, verifying")
                return

            elif abs(error_x) >= center_deadzone:
                direction = -1.0 if error_x > 0 else 1.0
                twist.angular.z = direction * ANGULAR_Z
                self.cmd_vel_pub.publish(twist)

                if not self.rot_updated:
                    if direction == self.last_rot_dir:
                        self.rot_streak += 1
                    else:
                        self.rot_streak = 1
                        self.last_rot_dir = direction
                self.rot_updated = True

                effective_error_scale = ERROR_SCALE + max(0, self.rot_streak - 3) * ERROR_SCALE_INCREMENT

                rot_interval = np.clip(
                    abs(error_x) * effective_error_scale,
                    MIN_MOVE_TIME,
                    max_move_time
                )

                self.get_logger().info(f"rotating | elapsed: {elapsed:.3f}s / interval: {rot_interval:.3f}s | scale: {effective_error_scale:.2f}")

                if elapsed > rot_interval:
                    self.state = "WAIT"
                    self.state_start_time = now
                    self.get_logger().info("reset start_time, waiting")
                else:
                    self.state = "ALIGN"

            elif self.frisbee_top <= FRISBEE_TOP_GOAL - FRISBEE_TOP_GOAL_ERROR:
                self.rot_streak = 0 # reset
                self.last_rot_dir = 0

                twist.linear.x = LINEAR_X
                self.cmd_vel_pub.publish(twist)

                self.get_logger().info(f"forward | elapsed: {elapsed:.3f}s / interval: {lin_interval:.3f}s | scale: {ERROR_SCALE:.2f}")
                if elapsed > lin_interval:
                    self.state = "WAIT"
                    self.state_start_time = now
                    self.get_logger().info("reset start_time, waiting")
                else:
                    self.state = "ALIGN"

            elif self.frisbee_top >= FRISBEE_TOP_GOAL + FRISBEE_TOP_GOAL_ERROR:
                self.rot_streak = 0 # reset
                self.last_rot_dir = 0
                
                twist.linear.x = -LINEAR_X
                self.cmd_vel_pub.publish(twist)

                self.get_logger().info(f"backward | elapsed: {elapsed:.3f}s / interval: {lin_interval:.3f}s | scale: {ERROR_SCALE:.2f}")
                if elapsed > lin_interval:
                    self.state = "WAIT"
                    self.state_start_time = now
                    self.get_logger().info("reset start_time, waiting")
                else:
                    self.state = "ALIGN"

            else:
                self.get_logger().error("stuck in ALIGN")

            self.path_timer_pub.publish(String(data=f"rotation interval: {MIN_MOVE_TIME} < {rot_interval} < {max_move_time}\nlinear interval: {MIN_MOVE_TIME} < {lin_interval} < {max_move_time}"))
            
                
        elif self.state == "WAIT":
            self.rot_updated = False
            
            self.cmd_vel_pub.publish(Twist())
            if (now - self.state_start_time).nanoseconds > int(PAUSE_TIME * 1e9):
                self.state_start_time = now
                self.get_logger().info("reset start_time, aligning")
                self.state = "ALIGN"


    def wiggle(self):
        twist = Twist()
        duration = 0.2

        actions = [
            ("forward", (LINEAR_X, 0.0)),
            ("stop", (0.0, 0.0)),
            ("backward", (-LINEAR_X, 0.0)),
            ("stop", (0.0, 0.0)),
            ("left", (0.0, ANGULAR_Z)),
            ("stop", (0.0, 0.0)),
            ("right", (0.0, -ANGULAR_Z)),
            ("stop", (0.0, 0.0)),
        ]

        for name, (lx, az) in actions:
            self.get_logger().info(f"wiggle: {name}")

            twist.linear.x = lx
            twist.angular.z = az

            start = self.get_clock().now()

            while (self.get_clock().now() - start).nanoseconds < int(duration * 1e9):
                self.cmd_vel_pub.publish(twist)

            self.cmd_vel_pub.publish(Twist())

        result = ExecuteCommand.Result()
        result.success = True
        result.message = "Nav wiggle complete"
        self._reset_and_return_future(result)

    def main_loop(self):
        if self.command_in_progress == 'wiggle':
            self.wiggle()    
    
        elif self.command_in_progress == 'approach':
            self.approach()    
    
        elif self.command_in_progress == 'stop':
            self.cmd_vel_pub.publish(Twist())

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

        return task, args


    async def execute_callback(self, goal_handle):
        request = goal_handle.request
        result = ExecuteCommand.Result()

        try:
            msg = request.command
            task, args = self._parse_action_goal(msg)
            
            # temporary for extra commands
            if len(args):
                assert len(args) == 1
                task = args[0]

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
        node.cmd_vel_pub.publish(Twist()) # stop wheels
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

