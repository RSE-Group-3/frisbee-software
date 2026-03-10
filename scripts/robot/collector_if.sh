#!/bin/bash

SESSION="collector_if"

# Kill existing session if it exists
tmux has-session -t $SESSION 2>/dev/null
if [ $? -eq 0 ]; then
    tmux kill-session -t $SESSION
fi

tmux new-session -d -s $SESSION

# tmux split-window -h -t $SESSION

tmux send-keys -t $SESSION:0.0 "source install/setup.bash" C-m
tmux send-keys -t $SESSION:0.0 "ros2 run fb_hardware_if collector_if_node" C-m
