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

tmux split-window -v -t $SESSION
tmux split-window -h -t $SESSION:0.0
tmux split-window -h -t $SESSION:0.2

tmux send-keys -t $SESSION:0.0 "ros2 launch fb_drivers cameras.launch.py --show-args" C-m
tmux send-keys -t $SESSION:0.0 "ros2 launch fb_drivers cameras.launch.py camera_set:=laptop1 brightness:=50 exposure:=1000" C-m

tmux send-keys -t $SESSION:0.1 "v4l2-ctl -l --device=/dev/video2" C-m

tmux send-keys -t $SESSION:0.2 "ros2 run fb_vision ground_tracker_node" C-m # TODO launch file
tmux send-keys -t $SESSION:0.3 "ros2 run fb_vision air_tracker_node" C-m