#!/bin/bash

DEVICE_FRONT="/dev/video2"
CAMERA_FRONT="front_cam"
DEVICE_BACK="/dev/video4"
CAMERA_BACK="back_cam"


# CAMERAS=("$CAMERA_FRONT" "$CAMERA_BACK")
# DEVICES=("$DEVICE_FRONT" "$DEVICE_BACK")

CAMERAS=("$CAMERA_FRONT")
DEVICES=("$DEVICE_FRONT")



SESSION="vision"

# Kill existing session if it exists
tmux has-session -t $SESSION 2>/dev/null
if [ $? -eq 0 ]; then
    tmux kill-session -t $SESSION
fi

tmux new-session -d -s $SESSION

tmux split-window -h -t $SESSION

tmux send-keys -t $SESSION:0.0 "ros2 run fb_vision ground_tracker_node" C-m # TODO launch file
tmux send-keys -t $SESSION:0.1 "ros2 run fb_vision air_tracker_node" C-m