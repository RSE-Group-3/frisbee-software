#!/bin/bash

MODE='automatic'

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --manual)
      MODE="manual"
      shift 1
      ;;
    *)
      echo "Unknown argument: $1"
      echo ""
      print_help
      exit 1
      ;;
  esac
done


SESSION="launcher_if"

# Kill existing session if it exists
tmux has-session -t $SESSION 2>/dev/null
if [ $? -eq 0 ]; then
    tmux kill-session -t $SESSION
fi

tmux new-session -d -s $SESSION

# tmux split-window -h -t $SESSION

tmux send-keys -t $SESSION:0.0 "conda activate frisbee_env" C-m
tmux send-keys -t $SESSION:0.0 "source install/setup.bash" C-m
tmux send-keys -t $SESSION:0.0 "ros2 run fb_launcher launcher_if_node \
                                --ros-args -p mode:=$MODE" C-m
