#!/bin/bash

SESSION="arduino_bridge"

# Kill existing session if it exists
tmux has-session -t $SESSION 2>/dev/null
if [ $? -eq 0 ]; then
    tmux kill-session -t $SESSION
fi

tmux new-session -d -s $SESSION

# tmux split-window -h -t $SESSION

tmux send-keys -t $SESSION:0.0 "ros2 launch fb_drivers arduino_bridge.launch.py" C-m

