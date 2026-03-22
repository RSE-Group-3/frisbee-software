#!/bin/bash

MODE="auto"
[[ "$1" == "--manual" ]] && MODE="manual"
[[ $# -gt 1 ]] && { echo "Too many arguments"; print_help; exit 1; }


SESSION="diff_drive"

# Kill existing session if it exists
tmux has-session -t $SESSION 2>/dev/null
if [ $? -eq 0 ]; then
    tmux kill-session -t $SESSION
fi

tmux new-session -d -s $SESSION

tmux send-keys -t $SESSION:0.0 "ros2 run fb_mobility diff_drive" C-m 
