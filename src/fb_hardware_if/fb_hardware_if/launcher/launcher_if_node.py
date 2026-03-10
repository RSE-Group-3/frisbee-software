import rclpy
from rclpy.node import Node

from std_msgs.msg import String
from fb_utils.fb_msgs import LauncherCmd, LauncherCmdMsg, LauncherAckMsg

import json
import threading
from enum import IntEnum
    

class LauncherIFNode(Node):
    def __init__(self):
        super().__init__('launcher_control_node')

        self.cmd_sub = self.create_subscription(
            String, # LauncherCmdMsg
            'launcher/cmd', 
            self.planner_callback, 
            10)
        self.ack_pub = self.create_publisher(
            String, # LauncherAckMsg
            'launcher/ack',
            10)
        
        self.arduino_cmd_pub = self.create_publisher(
            String, 
            'arduino/cmd', 
            10)
        self.arduino_status_sub = self.create_subscription(
            String, 
            'arduino/status', 
            self.arduino_callback, 
            10)

        self.get_logger().info("LAUNCHER: Launcher interface node online.")

        self.current_cmd = None


    def planner_callback(self, cmd_msg: String):
        '''
        recieved cmd from planner
        '''
        cmd_msg = LauncherCmdMsg(**json.loads(cmd_msg)) # convert to dataclass
        
        if self.current_cmd is None:
            self.logger.info("LAUNCHER: Launcher is ready, executing command")
            serial_str = ''

            match cmd_msg.cmd:
                case LauncherCmd.RESET:
                    serial_str = self.execute_reset()
                case LauncherCmd.LAUNCH:
                    serial_str = self.execute_launch()
                
            arduino_msg = String(data=serial_str)
            self.arduino_cmd_pub.publish(arduino_msg)

        else:
            self.logger.info("LAUNCHER: Launcher is not ready to receive new commands, ignoring command")
            ack_msg = LauncherAckMsg(cmd=cmd_msg.cmd, success=False, err_msg='Launcher is not ready to receive new commands, ignoring command')

            ack_msg = String(data=json.dump(ack_msg)) # convert to ros msg
            self.status_pub.publish(ack_msg)

    
    def arduino_callback(self, status_msg: String):
        '''
        received LAUNCHER status message from arduino
        '''
        if not status_msg.data.startswith("LAUNCHER_MOTOR:"): return

        status_msg = status_msg.data.strip()

        ack_msg = LauncherAckMsg()
        
        # parse arduino status
        if status_msg == "LAUNCHER_MOTOR: reset success" and self.current_cmd == LauncherCmd.RESET:
            self.logger.info("LAUNCHER: reset success")
        elif status_msg == "LAUNCHER_MOTOR: launch success" and self.current_cmd == LauncherCmd.LAUNCH:
            self.logger.info("LAUNCHER: launch success")
        else:
            self.logger.info(f"LAUNCHER: warning! ignoring bad message '{status_msg}'")
            return
            
        ack_msg.cmd = self.current_cmd
        ack_msg.success = True

        ack_msg = String(data=json.dump(ack_msg)) # convert to ros msg
        self.ack_pub.publish(ack_msg)

        self.current_cmd = None # ready for next command
        

    def estop(self):
        '''
        triggered by Ctrl-C
        '''
        serial_str = String(data="ESTOP")
        self.arduino_cmd_pub.publish(serial_str)

        self.logger.info("LAUNCHER: Node terminated by Ctrl-C, estop triggered")


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