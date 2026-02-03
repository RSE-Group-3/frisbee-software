from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='frisbee_brain',
            executable='state_machine',
            name='state_machine_node',
            output='screen',
            emulate_tty=True,
            parameters=[{'use_sim_time': False}]
        ),
        
        Node(
            package='frisbee_brain',
            executable='central_planner',
            name='central_planner_node',
            output='screen',
            emulate_tty=True,
            parameters=[{'use_sim_time': False}]
        ),

        Node(
            package='frisbee_launcher',
            executable='launcher_node',
            name='launcher'
        ),

        Node(
            package='frisbee_collector',
            executable='collector_node',
            name='collector'
        )
    ])