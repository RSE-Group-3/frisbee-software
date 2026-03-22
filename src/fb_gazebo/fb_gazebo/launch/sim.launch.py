from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, RegisterEventHandler, LogInfo
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import Command, PathJoinSubstitution
from launch.event_handlers import OnProcessStart
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    pkg_name = "fb_gazebo"

    # Robot description
    robot_description = Command([
        "xacro",
        " ",
        PathJoinSubstitution([
            FindPackageShare(pkg_name),
            "urdf",
            "robot.urdf.xacro"
        ])
    ])

    # Robot state publisher
    rsp_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{"robot_description": robot_description,
                     "use_sim_time": True}],
        output="screen"
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('gazebo_ros'),
                'launch',
                'gazebo.launch.py'
            )
        )
    )

    # Node to spawn the robot in Gazebo
    spawn_robot = Node(
        package="gazebo_ros",
        executable="spawn_entity.py",
        arguments=[
            "-topic", "robot_description",
            "-entity", "fb_robot",
            "-x", "0",
            "-y", "0",
            "-z", "1.0" 
        ],
        output="screen"
    )

    # Controller spawners
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster", "-c", "/controller_manager"],
        output="screen"
    )

    diff_drive_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["diff_drive_controller", "-c", "/controller_manager"],
        output="screen"
    )

    spawn_joint_state_handler = RegisterEventHandler(
        OnProcessStart(
            target_action=spawn_robot,
            on_start=[joint_state_broadcaster_spawner]
        )
    )

    spawn_diff_drive_handler = RegisterEventHandler(
        OnProcessStart(
            target_action=joint_state_broadcaster_spawner,
            on_start=[diff_drive_controller_spawner]
        )
    )

    relay_node = Node(
        package="topic_tools",
        executable="relay",
        name="cmd_vel_relay",
        arguments=["/cmd_vel", "/diff_drive_controller/cmd_vel_unstamped"],
        output="screen"
    )

    spawn_relay_handler = RegisterEventHandler(
        OnProcessStart(
            target_action=diff_drive_controller_spawner,
            on_start=[relay_node]
        )
    )

    return LaunchDescription([
        gazebo,
        rsp_node, 
        spawn_robot,
        spawn_joint_state_handler,
        spawn_diff_drive_handler,
        spawn_relay_handler
    ])