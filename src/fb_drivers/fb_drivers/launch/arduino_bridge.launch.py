from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    pkg_name = "fb_drivers"

    manipulation_node = Node(
        package=pkg_name,
        executable="arduino_bridge",
        arguments=["--dev", "/dev/ttyACM0"],
        output="screen"
    )

    return LaunchDescription([
        manipulation_node,
    ])