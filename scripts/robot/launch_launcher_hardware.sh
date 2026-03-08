#!/bin/bash

SESSION="launcher_hardware"

# Kill existing session if it exists
tmux has-session -t $SESSION 2>/dev/null
if [ $? -eq 0 ]; then
    tmux kill-session -t $SESSION
fi

tmux new-session -d -s $SESSION

tmux split-window -h -t $SESSION

tmux send-keys -t $SESSION:0.0 "conda activate frisbee-env" C-m
tmux send-keys -t $SESSION:0.0 "source install/setup.bash" C-m
tmux send-keys -t $SESSION:0.0 "launch motor placeholder" # launch motors

tmux send-keys -t $SESSION:0.0 "conda activate frisbee-env" C-m
tmux send-keys -t $SESSION:0.1 "source install/setup.bash" C-m
tmux send-keys -t $SESSION:0.1 "launch motor placeholder" # launch motors



SESSION="launcher_control"

# Kill existing session if it exists
tmux has-session -t $SESSION 2>/dev/null
if [ $? -eq 0 ]; then
    tmux kill-session -t $SESSION
fi

tmux new-session -d -s $SESSION

tmux split-window -h -t $SESSION

tmux send-keys -t $SESSION:0.0 "conda activate frisbee-env" C-m
tmux send-keys -t $SESSION:0.0 "source install/setup.bash" C-m
tmux send-keys -t $SESSION:0.0 "ros2 run fb_launcher launcher_node" C-m

