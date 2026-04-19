from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    pkg_name = "fb_bringup"

    # arduino_bridge_node = Node(
    #     package=pkg_name,
    #     executable="arduino_bridge",
    #     arguments=["--device", "/dev/ttyACM0", "--topic", "arduino"],
    #     output="screen"
    # )

    collector_arduino_bridge_node = Node(
        package=pkg_name,
        executable="arduino_bridge",
        arguments=["--device", "/dev/ttyACM0", "--topic", "arduino/collector"],
        output="screen"
    )

    launcher_arduino_bridge_node = Node(
        package=pkg_name,
        executable="arduino_bridge",
        arguments=["--device", "/dev/ttyACM0", "--topic", "arduino/launcher"],
        output="screen"
    )

    return LaunchDescription([
        collector_arduino_bridge_node,
        launcher_arduino_bridge_node,
    ])