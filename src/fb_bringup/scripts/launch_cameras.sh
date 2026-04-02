#!/bin/bash

while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --topic)
        TOPIC="$2"
        shift 2
        ;;
        --device)
        DEVICE="$2"
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

SESSION="camera_"$(basename $TOPIC)

# Kill existing session if it exists
tmux has-session -t $SESSION 2>/dev/null
if [ $? -eq 0 ]; then
    tmux kill-session -t $SESSION
fi

tmux new-session -d -s $SESSION

tmux split-window -v -t $SESSION

tmux send-keys -t $SESSION:0.0 "ros2 launch fb_bringup cameras.launch.py --show-args" C-m
tmux send-keys -t $SESSION:0.0 "ros2 launch fb_bringup cameras.launch.py topic:=$TOPIC device:=$DEVICE brightness:=$BRIGHTNESS exposure:=$EXPOSURE" C-m

tmux send-keys -t $SESSION:0.1 "v4l2-ctl -l --device=$DEVICE # list controls"