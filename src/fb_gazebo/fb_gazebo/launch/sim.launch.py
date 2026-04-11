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

    controller_config = PathJoinSubstitution([
        FindPackageShare("fb_gazebo"),
        "config",
        "controller.yaml"
    ])

    # Robot description
    robot_description = Command([
        "xacro",
        " ",
        PathJoinSubstitution([
            FindPackageShare(pkg_name),
            "urdf",
            "robot.urdf.xacro"
        ]),
        " ",
        "controller_config:=",
        controller_config
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
        ),
        launch_arguments={
            'world': os.path.join(
                get_package_share_directory('fb_gazebo'),
                'worlds',
                'frisbee_world.world'
            ),
            'gui': 'false',
        }.items()
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

    left_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["left_wheel_velocity_controller", "-c", "/controller_manager"],
        output="screen"
    )

    right_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["right_wheel_velocity_controller", "-c", "/controller_manager"],
        output="screen"
    )

    spawn_joint_state_handler = RegisterEventHandler(
        OnProcessStart(
            target_action=spawn_robot,
            on_start=[joint_state_broadcaster_spawner]
        )
    )

    spawn_left_handler = RegisterEventHandler(
        OnProcessStart(
            target_action=joint_state_broadcaster_spawner,
            on_start=[left_controller_spawner]
        )
    )

    spawn_right_handler = RegisterEventHandler(
        OnProcessStart(
            target_action=left_controller_spawner,
            on_start=[right_controller_spawner]
        )
    )

    return LaunchDescription([
        gazebo,
        rsp_node, 
        spawn_robot,
        spawn_joint_state_handler,
        spawn_left_handler,
        spawn_right_handler,
        # joint_state_broadcaster_spawner,
        # left_controller_spawner,
        # right_controller_spawner,
    ])