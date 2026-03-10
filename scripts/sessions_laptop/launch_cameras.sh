#!/bin/bash

DEVICE_FRONT="/dev/video2"
CAMERA_FRONT="front_cam"
DEVICE_BACK="/dev/video4"
CAMERA_BACK="back_cam"


# CAMERAS=("$CAMERA_FRONT" "$CAMERA_BACK")
# DEVICES=("$DEVICE_FRONT" "$DEVICE_BACK")

CAMERAS=("$CAMERA_FRONT")
DEVICES=("$DEVICE_FRONT")



SESSION="launch_cameras"

# Kill existing session if it exists
tmux has-session -t $SESSION 2>/dev/null
if [ $? -eq 0 ]; then
    tmux kill-session -t $SESSION
fi

tmux new-session -d -s $SESSION

tmux split-window -h -t $SESSION
tmux split-window -v -t $SESSION:0.0


for i in "${!CAMERAS[@]}"; do
  tmux send-keys -t $SESSION:0.$i "ros2 run usb_cam usb_cam_node_exe \
    --ros-args --remap __ns:=/${CAMERAS[$i]} \
    -p video_device:=${DEVICES[$i]} \
    -p framerate:=15.0 \
    -p image_width:=1280 \
    -p image_height:=720 \
    -p pixel_format:='mjpeg2rgb'" C-m
done


tmux send-keys -t $SESSION:0.2 "python3 ./scripts/sessions_laptop/utils/set_camera_params.py $DEVICE_FRONT $DEVICE_BACK" C-m