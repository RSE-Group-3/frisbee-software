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

    topic_arg = DeclareLaunchArgument('topic', description='topic (e.g. /camera/collector)')
    device_arg = DeclareLaunchArgument('device', description='video device (e.g. /dev/video0)')
    brightness_arg = DeclareLaunchArgument('brightness', description='brightness 0x00980900 (int)    : min=-64 max=64 step=1')
    exposure_arg = DeclareLaunchArgument('exposure', description='exposure_time_absolute 0x009a0902 (int)    : min=1 max=5000 step=1')

    topic = LaunchConfiguration('topic')
    device = LaunchConfiguration('device')
    brightness = LaunchConfiguration('brightness')
    exposure = LaunchConfiguration('exposure')

    usb_cam_params_file = os.path.join(get_package_share_directory(pkg_name), 'config', 'usb_cam_params.yaml')

    ld = LaunchDescription([topic_arg, device_arg, brightness_arg, exposure_arg])

    # Function to set up camera nodes
    def setup_nodes(context, *args, **kwargs):
        device_name = device.perform(context).strip()
        
        nodes = []

        # Launch USB camera node
        cam_node = Node(
            package='usb_cam',
            executable='usb_cam_node_exe',
            namespace=topic,
            name='usb_cam_node',
            parameters=[{
                    'video_device': device_name,
                    'framerate': 5.0,
                    'image_width': 320, #1280,
                    'image_height': 240, #720,
                    'pixel_format': 'mjpeg2rgb'
                }],
            respawn=True,
            respawn_delay=10.0
        )

        # to see valid image sizes: v4l2-ctl --list-formats-ext -d /dev/video0
        # to see v4l2 parameters: v4l2-ctl -d /dev/video0 --list-ctrls

        nodes.append(cam_node)

        # Set camera v4l2 parameters after node starts
        def make_set_params(device=device_name):
            def set_params(context):
                subprocess.run(["v4l2-ctl", "-d", device_name, "--set-ctrl=auto_exposure=1"])
                subprocess.run(["v4l2-ctl", "-d", device_name, f"--set-ctrl=exposure_time_absolute={exposure.perform(context)}"])
                subprocess.run(["v4l2-ctl", "-d", device_name, f"--set-ctrl=brightness={brightness.perform(context)}"])
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