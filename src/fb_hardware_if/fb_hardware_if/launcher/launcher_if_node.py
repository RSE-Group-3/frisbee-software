import rclpy
from rclpy.node import Node

from std_msgs.msg import String, Int32
from fb_utils.fb_msgs import LauncherCmd, LauncherAck

import threading
import time

class LauncherIFNode(Node):
    def __init__(self):
        super().__init__('launcher_control_node')

        self.cmd_sub = self.create_subscription(
            Int32, 'launcher/cmd', self.planner_callback, 10)
        self.ack_pub = self.create_publisher(
            Int32, 'launcher/ack', 10)
        
        self.arduino_cmd_pub = self.create_publisher(
            String, 'arduino/cmd', 10)
        self.arduino_status_sub = self.create_subscription(
            String, 'arduino/ack', self.arduino_callback, 10)

        self.get_logger().info("Launcher interface node online.")

        self._ack_event = threading.Event()
        self._last_ack = ""
        self._busy_lock = threading.Lock()

        self.declare_parameter("hardware", True)
        self.use_hardware = self.get_parameter("hardware").get_parameter_value().bool_value
        self.get_logger().warn(f"use_hardware={self.use_hardware}")
                

    def execute_sequence(self, sequence):
        if not self.use_hardware:
            self.get_logger().info(f"skipping hardware")
            time.sleep(1.0)
            return 0
        else:
            self.get_logger().info(f"executing cmd")
            with self._busy_lock:
                for cmd in sequence:
                    if self.send_cmd_and_wait(cmd):
                        self.get_logger().error(f"command failed: {cmd}, aborting sequence")
                        return -1
                return 0

    def send_cmd_and_wait(self, cmd, timeout=10.0):
        self._ack_event.clear()
        self.arduino_cmd_pub.publish(String(data=cmd))

        if self._ack_event.wait(timeout):
            if self._last_ack.startswith(cmd):
                return 0
            else:
                self.get_logger().warn(f"unexpected ACK: {self._last_ack}")
                return -1
        else:
            self.get_logger().warn(f"timeout waiting for ACK: {cmd}")
            return -1

    def planner_callback(self, cmd_msg: String):
        '''
        recieved cmd from planner
        '''
        if cmd_msg.data == LauncherCmd.RESET:
            self.execute_reset()
        elif cmd_msg.data == LauncherCmd.LAUNCH:
            self.execute_launch()
        else:
            self.get_logger().warn(f"Unknown planner command: {cmd_msg.data}")

    def arduino_callback(self, status_msg: String):
        """
        received arduino status message
        """
        if not status_msg.data.startswith("LAUNCHER"):
            return

        try:
            line = status_msg.data.strip().split()
            if len(line) < 2:
                self.get_logger().warn(f"ignoring bad message '{status_msg.data}'")
                return
            self._last_ack = " ".join(line[:2])  # or adjust to your ACK format
            self._ack_event.set()
        except Exception as e:
            self.get_logger().warn(f"error parsing ACK: {e}")

    def estop(self):
        """
        triggered by Ctrl-C
        """
        self.arduino_cmd_pub.publish(String(data="STOP"))
        self.get_logger().warn("node terminated by Ctrl-C, estop triggered")

    ##################################################################################

    def execute_reset(self):
        sequence = [
        ]

        if self.execute_sequence(sequence):
            self.ack_pub.publish(Int32(data=LauncherAck.ERROR))
            self.get_logger().info("LAUNCHER: ERROR")
        else:
            self.ack_pub.publish(Int32(data=LauncherAck.RESET_SUCCESS))
            self.get_logger().info("LAUNCHER: RESET_SUCCESS")

    def execute_launch(self):
        sequence = [
            'LAUNCHER: launch 40',
        ]

        if self.execute_sequence(sequence):
            self.get_logger().info("LAUNCHER: ERROR")
            self.ack_pub.publish(Int32(data=LauncherAck.ERROR))
        else:
            self.ack_pub.publish(Int32(data=LauncherAck.LAUNCH_SUCCESS))
            self.get_logger().info("LAUNCHER: LAUNCH_SUCCESS")


def main(args=None):
    rclpy.init(args=args)
    node = LauncherIFNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.estop()
    finally:
        node.destroy_node()
        rclpy.shutdown()