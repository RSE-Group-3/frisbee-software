#!/bin/bash

SESSION="foxglove_bridge"

# Kill existing session if it exists
tmux has-session -t $SESSION 2>/dev/null
if [ $? -eq 0 ]; then
    tmux kill-session -t $SESSION
fi

tmux new-session -d -s $SESSION

tmux send-keys -t $SESSION:0.0 "source /opt/ros/humble/setup.bash" C-m
tmux send-keys -t $SESSION:0.0 "ros2 launch foxglove_bridge foxglove_bridge_launch.xml port:=8765" C-m

# Attach to session
# tmux attach -t $SESSION