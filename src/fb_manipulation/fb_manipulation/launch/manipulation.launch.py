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

    return LaunchDescription([
        manipulation_node,
    ])