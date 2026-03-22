from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction, RegisterEventHandler
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch.event_handlers import OnProcessStart
from ament_index_python.packages import get_package_share_directory
import subprocess
import os

def generate_launch_description():
    pkg_name = "fb_bringup"

    all_camera_sets = {
        'test': {'front_cam': '/dev/video0'},
        'laptop1': {'front_cam': '/dev/video2'},
        'laptop2': {'front_cam': '/dev/video2', 'back_cam': '/dev/video4'},
        'robot1': {'front_cam': '/dev/video0'},
        'robot2': {'front_cam': '/dev/video0', 'back_cam': '/dev/video2'},
    }

    camera_set_arg = DeclareLaunchArgument('camera_set', description='''
        'test': {'front_cam': '/dev/video0'},
        'laptop1': {'front_cam': '/dev/video2'},
        'laptop2': {'front_cam': '/dev/video2', 'back_cam': '/dev/video4'},
        'robot1': {'front_cam': '/dev/video0'},
        'robot2': {'front_cam': '/dev/video0', 'back_cam': '/dev/video2'},
        ''')
    brightness_arg = DeclareLaunchArgument('brightness', description='brightness 0x00980900 (int)    : min=-64 max=64 step=1')
    exposure_arg = DeclareLaunchArgument('exposure', description='exposure_time_absolute 0x009a0902 (int)    : min=1 max=5000 step=1')

    camera_set = LaunchConfiguration('camera_set')
    brightness = LaunchConfiguration('brightness')
    exposure = LaunchConfiguration('exposure')

    usb_cam_params_file = os.path.join(get_package_share_directory(pkg_name), 'config', 'usb_cam_params.yaml')

    ld = LaunchDescription([camera_set_arg, brightness_arg, exposure_arg])

    # Function to set up camera nodes
    def setup_nodes(context, *args, **kwargs):
        cam_set_name = camera_set.perform(context)
        if cam_set_name not in all_camera_sets:
            raise RuntimeError(f"Invalid camera_set '{cam_set_name}'. Valid options: {list(all_camera_sets.keys())}")

        nodes = []
        for cam_name, device in all_camera_sets[cam_set_name].items():
            # Launch USB camera node
            cam_node = Node(
                package='usb_cam',
                executable='usb_cam_node_exe',
                namespace=cam_name,
                name='usb_cam_node',
                parameters=[usb_cam_params_file, {'video_device': device}],
                respawn=True,
                respawn_delay=10.0
            )
            nodes.append(cam_node)

            # Set camera v4l2 parameters after node starts
            def make_set_params(device=device):
                def set_params(context):
                    subprocess.run(["v4l2-ctl", "-d", device, "--set-ctrl=auto_exposure=1"])
                    subprocess.run(["v4l2-ctl", "-d", device, f"--set-ctrl=exposure_time_absolute={exposure.perform(context)}"])
                    subprocess.run(["v4l2-ctl", "-d", device, f"--set-ctrl=brightness={brightness.perform(context)}"])
                return set_params

            nodes.append(
                RegisterEventHandler(
                    OnProcessStart(
                        target_action=cam_node,
                        on_start=[OpaqueFunction(function=make_set_params())]
                    )
                )
            )

        return nodes

    ld.add_action(OpaqueFunction(function=setup_nodes))
    return ld