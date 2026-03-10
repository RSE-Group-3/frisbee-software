#!/bin/bash

# example usage: ./scripts/run_robot.sh --build

BUILD="false"
[[ "$1" == "--build" ]] && BUILD="true"
[[ $# -gt 1 ]] && { echo "Too many arguments"; print_help; exit 1; }

if [ "$BUILD" = "true" ]; then
  echo "Building workspace..."
  source ./scripts/build_laptop.sh
fi

tmux kill-server

./scripts/laptop/foxglove_bridge.sh
./scripts/laptop/central_planner.sh
./scripts/laptop/vision_models.sh

sleep 1
tmux attach