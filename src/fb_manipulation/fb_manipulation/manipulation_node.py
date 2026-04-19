import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from fb_interfaces.action import ExecuteCommand
from rclpy.action import ActionServer
from rclpy.task import Future

TIMEOUT = 10 # s


class ManipulationNode(Node):
    def __init__(self):
        super().__init__('manipulation_node')

        self.collector_serial_cmd_pub = self.create_publisher(String, 'arduino/collector/cmd', 10)
        self.serial_status_sub = self.create_subscription(
            String, 'arduino/collector/status', self.collector_serial_callback, 10
        )
        self.launcher_serial_cmd_pub = self.create_publisher(String, 'arduino/launcher/cmd', 10)
        self.serial_status_sub = self.create_subscription(
            String, 'arduino/launcher/status', self.launcher_serial_callback, 10
        )

        self.action = ActionServer(
            self,
            ExecuteCommand,
            'manipulation/execute',
            self.execute_callback
        )

        self.get_logger().info("Manipulation node online.")

        self.current_sequence = []
        self.current_index = 0
        self.timer = None
        self.command_in_progress = None
        self.goal_handle = None
        self._done_future = None


    def _parse_action_goal(self, msg: str):
        task_tokens = msg.strip().split()
        task, args = task_tokens[0], task_tokens[1:]

        match task:
            case 'stop':
                sequence = [
                    'STOP',  # stop all motors if not already stopped
                ]
            case 'reset_mech':
                sequence = [
                    'COLLECTOR: open',
                    'COLLECTOR: high',
                ]
            case 'launch':
                try:
                    assert len(args) == 1 and args[0].isdigit()
                    sequence = [
                        f'LAUNCHER: launch {args[0]}'
                    ]
                except:
                    self.get_logger().error(f"Bad launch arguments, expected 'launch <int>', got '{msg}'")
                    sequence = [
                        f'LAUNCHER: launch 1200'
                    ]
            case 'collect': 
                sequence = [
                    'COLLECTOR: low',
                    'COLLECTOR: close',
                    'COLLECTOR: high_tilt',
                    'COLLECTOR: open',
                    'COLLECTOR: high',
                ]
            case _:
                task, sequence = None, None

        return task, sequence


    async def execute_callback(self, goal_handle):
        request = goal_handle.request
        result = ExecuteCommand.Result()

        try:
            msg = request.command
            task, sequence = self._parse_action_goal(msg)

            if sequence is None:
                result.success = False
                result.message = f"Manipulation error parsing command {msg}"
                goal_handle.abort()
                return result

            if self.command_in_progress and task != 'stop':
                result.success = False
                result.message = f"Manipulation task {self.command_in_progress} in progress"
                goal_handle.abort()
                return result

            self.get_logger().warn(f"Starting command sequence: {task}")

            self.current_sequence = sequence
            self.current_index = 0
            self.command_in_progress = task
            self.goal_handle = goal_handle

            feedback = ExecuteCommand.Feedback()
            feedback.status = f'Manipulation started "{task}"'
            goal_handle.publish_feedback(feedback)

            self._done_future = Future()

            self._send_next_command()

            result = await self._done_future
            return result

        except Exception as e:
            result.success = False
            result.message = f'Manipulation error parsing command "{request.command}": {e}'
            goal_handle.abort()
            return result


    def _send_next_command(self):
        if not self.current_sequence or self.current_index >= len(self.current_sequence):
            self.get_logger().warn(f"COMPLETE: {self.current_sequence}")

            result = ExecuteCommand.Result()
            result.success = True
            result.message = f"Manipulation COMPLETE: {self.current_sequence}"

            self.goal_handle.succeed()
            self.command_in_progress = None

            if self._done_future and not self._done_future.done():
                self._done_future.set_result(result)
            return

        cmd = self.current_sequence[self.current_index]
        self.get_logger().info(f"Sending command: '{cmd}'")

        feedback = ExecuteCommand.Feedback()
        feedback.status = f"Manipulation executing: {cmd}"
        self.goal_handle.publish_feedback(feedback)

        if cmd.startswith('STOP'):
            self.collector_serial_cmd_pub.publish(String(data=cmd))
            self.launcher_serial_cmd_pub.publish(String(data=cmd))
        elif cmd.startswith('LAUNCHER'):
            self.launcher_serial_cmd_pub.publish(String(data=cmd))
        elif cmd.startswith('COLLECTOR'):
            self.collector_serial_cmd_pub.publish(String(data=cmd))

        if self.timer:
            self.timer.cancel()
        self.timer = self.create_timer(TIMEOUT, self._command_timeout)

    def serial_callback(self, msg: String):
        self.get_logger().info(f"Status received '{msg.data}'")

        if not self.command_in_progress:
            return

        if self.timer:
            self.timer.cancel()
            self.timer = None

        serial_msg = msg.data
        ack_status = serial_msg.split()[0]

        if ack_status == 'OK:':
            self.get_logger().info(f"Received status: '{msg.data}'")

            # guard against stale state
            if not self.current_sequence:
                return

            self.current_index += 1
            self._send_next_command()

        elif ack_status == 'FAIL:':
            self.get_logger().error(f"Execution failed: {msg.data}")

            result = ExecuteCommand.Result()
            result.success = False
            result.message = f"Manipulation execution failed: {msg.data}"

            self.goal_handle.abort()
            self.command_in_progress = None

            if self._done_future and not self._done_future.done():
                self._done_future.set_result(result)

    def collector_serial_callback(self, msg: String):
        self.serial_callback(msg)

    def launcher_serial_callback(self, msg: String):
        self.serial_callback(msg)


    def _command_timeout(self):
        if not self.current_sequence or self.current_index >= len(self.current_sequence):
            return

        cmd = self.current_sequence[self.current_index]

        if self.timer:
            self.timer.cancel()
            self.timer = None

        self.get_logger().warn(f"Timeout on command {cmd}")

        result = ExecuteCommand.Result()
        result.success = False
        result.message = f"Manipulation timeout on command {cmd}"

        self.goal_handle.abort()
        self.command_in_progress = None

        if self._done_future and not self._done_future.done():
            self._done_future.set_result(result)


def main(args=None):
    rclpy.init(args=args)
    node = ManipulationNode()
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