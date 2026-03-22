#!/bin/bash

SESSION="manipulation"

# Kill existing session if it exists
tmux has-session -t $SESSION 2>/dev/null
if [ $? -eq 0 ]; then
    tmux kill-session -t $SESSION
fi

tmux new-session -d -s $SESSION

tmux split-window -h -t $SESSION
tmux split-window -v -t $SESSION

tmux send-keys -t $SESSION:0.0 "ros2 launch fb_manipulation manipulation.launch.py" C-m

tmux send-keys -t $SESSION:0.1 "ros2 topic echo /arduino/cmd" C-m

tmux send-keys -t $SESSION:0.2 "ros2 topic echo /arduino/status" C-m