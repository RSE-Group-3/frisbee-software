#!/bin/bash

MODE="auto"
[[ "$1" == "--manual" ]] && MODE="manual"
[[ $# -gt 1 ]] && { echo "Too many arguments"; print_help; exit 1; }


SESSION="mobility"

# Kill existing session if it exists
tmux has-session -t $SESSION 2>/dev/null
if [ $? -eq 0 ]; then
    tmux kill-session -t $SESSION
fi

tmux new-session -d -s $SESSION

tmux split-window -v -t $SESSION
tmux split-window -v -t $SESSION

tmux send-keys -t $SESSION:0.0 "killall gzserver gzclient gazebo" C-m
tmux send-keys -t $SESSION:0.0 "ros2 run fb_mobility diff_drive" C-m # diff drive node

tmux send-keys -t $SESSION:0.1 "ros2 run teleop_twist_keyboard teleop_twist_keyboard" C-m

tmux send-keys -t $SESSION:0.2 "ros2 topic echo /cmd_vel"