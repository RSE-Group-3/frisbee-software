#!/bin/bash

DEVICE_FRONT="/dev/video0"
CAMERA_FRONT="front_robot_cam"

DEVICE_BACK="/dev/video2"
CAMERA_BACK="back_robot_cam"

EXPOSURE="200" # min=1 max=5000 step=1 default=157 value=50



SESSION="launch_cameras"

# Kill existing session if it exists
tmux has-session -t $SESSION 2>/dev/null
if [ $? -eq 0 ]; then
    tmux kill-session -t $SESSION
fi

tmux new-session -d -s $SESSION

tmux split-window -h -t $SESSION
tmux split-window -v -t $SESSION:0.0

# front camera
tmux send-keys -t $SESSION:0.0 "source /opt/ros/humble/setup.bash" C-m
tmux send-keys -t $SESSION:0.0 "ros2 run usb_cam usb_cam_node_exe \
  --ros-args --remap __ns:=/$CAMERA_FRONT \
  -p video_device:=$DEVICE_FRONT \
  -p pixel_format:='mjpeg2rgb'" C-m

# back camera
tmux send-keys -t $SESSION:0.1 "conda activate frisbee-env" C-m
tmux send-keys -t $SESSION:0.1 "source /opt/ros/humble/setup.bash" C-m
tmux send-keys -t $SESSION:0.1 "ros2 run usb_cam usb_cam_node_exe \
  --ros-args --remap __ns:=/$CAMERA_BACK \
  -p video_device:=$DEVICE_BACK \
  -p pixel_format:='mjpeg2rgb'" C-m
