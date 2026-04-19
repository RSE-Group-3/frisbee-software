from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    pkg_name = "fb_manipulation"

    manipulation_node = Node(
        package=pkg_name,
        executable="manipulation_node",
        arguments=[],
        output="screen"
    )

    fake_arduino = Node(
        package=pkg_name,
        executable="fake_arduino",
        arguments=[],
        output="screen"
    )

    return LaunchDescription([
        manipulation_node,
        fake_arduino,
    ])