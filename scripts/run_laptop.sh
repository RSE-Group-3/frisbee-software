#!/bin/bash

BUILD="false"
[[ "$1" == "--build" ]] && BUILD="true"
[[ $# -gt 1 ]] && { echo "Too many arguments"; print_help; exit 1; }

if [ "$BUILD" = "true" ]; then
  echo "Building workspace..."
  source ./scripts/build_laptop.sh
fi

tmux kill-server

./scripts/sessions_laptop/foxglove_bridge.sh

./scripts/sessions_laptop/central_planner.sh
./scripts/sessions_laptop/path_planner.sh

./scripts/sessions_laptop/vision_models.sh
./scripts/sessions_laptop/launch_cameras.sh

sleep 1
tmux attach