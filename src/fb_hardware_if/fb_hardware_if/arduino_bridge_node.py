import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import serial
from serial.serialutil import SerialException

class ArduinoBridge(Node):
    def __init__(self):
        super().__init__('arduino_bridge')

        self.serial_port = '/dev/ttyACM0'
        self.baudrate = 115200
        self.ser = None
        self.arduino_connected = False

        self.status_pub = self.create_publisher(String, 'arduino/status', 10)
        self.cmd_sub = self.create_subscription(String, 'arduino/cmd', self.cmd_callback, 10)

        # Timer to read serial periodically (20 Hz)
        self.create_timer(0.05, self.read_serial)
        # Timer to attempt reconnect if Arduino disconnected
        self.create_timer(5.0, self.check_connection)

        self.connect_arduino()

    def connect_arduino(self):
        """Try to open serial port safely."""
        if self.ser is None:
            try:
                self.ser = serial.Serial(self.serial_port, self.baudrate, timeout=0.1)
                self.arduino_connected = True
                self.get_logger().info(f"ARDUINO: Arduino connected on {self.serial_port}")
            except SerialException:
                self.arduino_connected = False
                self.ser = None
                self.get_logger().warn(f"ARDUINO: Arduino not found on {self.serial_port}. Will retry...")

    def check_connection(self):
        """Reconnect if Arduino is offline."""
        if not self.arduino_connected:
            self.connect_arduino()

    def cmd_callback(self, msg: String):
        """Send command to Arduino safely."""
        if not self.arduino_connected:
            self.get_logger().warn("ARDUINO: Cannot send command: Arduino offline")
            return

        cmd = msg.data.strip() # assume valid command
        try:
            self.ser.write((cmd + '\n').encode('utf-8'))
        except SerialException:
            self.get_logger().warn("ARDUINO: Failed to write to Arduino")
            self.arduino_connected = False
            self.ser = None

    def read_serial(self):
        """Read and publish Arduino status."""
        if not self.arduino_connected:
            return

        try:
            while self.ser.in_waiting:
                line = self.ser.readline().decode('utf-8').strip()
                if line:
                    msg = String()
                    msg.data = line
                    self.status_pub.publish(msg)
        except SerialException:
            self.get_logger().warn("ARDUINO: Lost connection")
            self.arduino_connected = False
            self.ser = None

def main():
    rclpy.init()
    node = ArduinoBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node.ser:
            node.ser.close()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()