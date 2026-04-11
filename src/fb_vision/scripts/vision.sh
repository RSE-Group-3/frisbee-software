#!/bin/bash

SESSION="vision"

# Kill existing session if it exists
tmux has-session -t $SESSION 2>/dev/null
if [ $? -eq 0 ]; then
    tmux kill-session -t $SESSION
fi

tmux new-session -d -s $SESSION

tmux split-window -v -t $SESSION

tmux send-keys -t $SESSION:0.0 "ros2 run fb_vision ground_tracker_node" C-m
tmux send-keys -t $SESSION:0.1 "ros2 run fb_vision ground_tracker_node_old" C-m
# tmux send-keys -t $SESSION:0.1 "ros2 run fb_vision air_tracker_node" C-m