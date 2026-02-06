from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='frisbee_launcher',
            executable='launcher_node',
            name='launcher_node',
            output='screen'
        ),
        Node(
            package='frisbee_collector',
            executable='collector_node',
            name='collector_node',
            output='screen'
        ),
        Node(
            package='frisbee_mobility',
            executable='mobility_node',
            name='mobility_node',
            output='screen'
        ),
        Node(
            package='frisbee_vision',
            executable='camera_node',
            name='camera_node',
            output='screen'
        )
    ])