#!/bin/bash

while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --camera_set)
        CAMERA_SET="$2"
        shift 2
        ;;
        --brightness)
        BRIGHTNESS="$2"
        shift 2
        ;;
        --exposure)
        EXPOSURE="$2"
        shift 2
        ;;
        *)
        echo "Unknown option: $1"
        exit 1
        ;;
    esac
done

SESSION="cameras_robot"

# Kill existing session if it exists
tmux has-session -t $SESSION 2>/dev/null
if [ $? -eq 0 ]; then
    tmux kill-session -t $SESSION
fi

tmux new-session -d -s $SESSION

tmux split-window -h -t $SESSION

tmux send-keys -t $SESSION:0.0 "ros2 launch fb_bringup cameras.launch.py --show-args" C-m
tmux send-keys -t $SESSION:0.0 "ros2 launch fb_bringup cameras.launch.py camera_set:=$CAMERA_SET brightness:=$BRIGHTNESS exposure:=$EXPOSURE" C-m
# TODO: launch 2 cameras?

tmux send-keys -t $SESSION:0.1 "v4l2-ctl -l --device=/dev/video2" C-m