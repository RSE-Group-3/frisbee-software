import rclpy
from rclpy.node import Node

from std_msgs.msg import String
from fb_utils.fb_msgs import LauncherIFCmd, LauncherIFCmdMsg, LauncherIFAckMsg

import json
import threading
from enum import IntEnum
    

class LauncherIFNode(Node):
    def __init__(self):
        super().__init__('launcher_control_node')

        self.cmd_sub = self.create_subscription(
            String, # LauncherIFCmdMsg
            'launcher/cmd', 
            self.planner_callback, 
            10)
        self.ack_pub = self.create_publisher(
            String, # LauncherIFAckMsg
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


        self.declare_parameter('mode', 'automatic')
        self.mode = self.get_parameter('mode').value

        self.get_logger().info("LAUNCHER: Launcher interface node online.")

        threading.Thread(target=self.input_loop, daemon=True).start()

        # detault startup behavior
        self.current_cmd = None
        
    
    def input_loop(self):
        while rclpy.ok():
            if self.mode == 'automatic':
                user_input = input('\033[92m' + 'AUTOMATIC MODE: Using central planner. Enter "m" to switch to manual user commands, or Ctrl-C to ESTOP: ' + '\033[0m')
                if user_input == 'm':
                    self.get_logger().info("LAUNCHER: Operating in MANUAL mode (user inputs).")
                    self.mode = 'manual'
                else:
                    self.get_logger().info("LAUNCHER: User input not recognized.")

            elif self.mode == 'manual':
                user_input = input('\033[92m' + 'MANUAL MODE: Enter manual input. Enter "a" to switch to using central planner, or Ctrl-C to ESTOP: ' + '\033[0m')
                if user_input == 'a':
                    self.get_logger().info("LAUNCHER: Operating in AUTOMATIC mode (central planner).")
                    self.mode = 'automatic'
                else:
                    serial_cmd_msg = self.launcher.process_user_input(user_input)
                    if not serial_cmd_msg:
                        print('User input failed to parse.')
                    else:
                        self.serial_cmd_pub.publish(serial_cmd_msg)
            else:
                assert False


    def planner_callback(self, cmd_msg: String):
        '''
        recieved cmd from planner
        '''
        cmd_msg = LauncherIFCmdMsg(**json.loads(cmd_msg)) # convert to dataclass
        
        if self.current_cmd is None:
            self.logger.info("LAUNCHER: Launcher is ready, executing command")
            serial_str = ''

            match cmd_msg.cmd:
                case LauncherIFCmd.RESET:
                    serial_str = self.execute_reset()
                case LauncherIFCmd.LAUNCH:
                    serial_str = self.execute_launch()
                
            arduino_msg = String(data=serial_str)
            self.arduino_cmd_pub.publish(arduino_msg)

        else:
            self.logger.info("LAUNCHER: Launcher is not ready to receive new commands, ignoring command")
            ack_msg = LauncherIFAckMsg(cmd=cmd_msg.cmd, success=False, err_msg='Launcher is not ready to receive new commands, ignoring command')

            ack_msg = String(data=json.dump(ack_msg)) # convert to ros msg
            self.status_pub.publish(ack_msg)

    
    def arduino_callback(self, status_msg: String):
        '''
        received LAUNCHER status message from arduino
        '''
        if not status_msg.data.startswith("LAUNCHER_MOTOR:"): return

        status_msg = status_msg.data.strip()

        ack_msg = LauncherIFAckMsg()
        
        # parse arduino status=
        if status_msg == "LAUNCHER_MOTOR: reset success" and self.current_cmd == LauncherIFCmd.RESET:
            self.logger.info("LAUNCHER: reset success")
        elif status_msg == "LAUNCHER_MOTOR: launch success" and self.current_cmd == LauncherIFCmd.LAUNCH:
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