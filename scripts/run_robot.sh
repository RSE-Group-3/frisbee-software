#!/bin/bash

# example usage: ./scripts/run_robot.sh --build

BUILD="false"
[[ "$1" == "--build" ]] && BUILD="true"
[[ $# -gt 1 ]] && { echo "Too many arguments"; print_help; exit 1; }

if [ "$BUILD" = "true" ]; then
  echo "Building workspace..."
  source ./scripts/build_robot.sh
fi

tmux kill-server

./scripts/robot/launch_cameras.sh
./scripts/robot/arduino_bridge.sh

./scripts/robot/mobility_if.sh
./scripts/robot/collector_if.sh
./scripts/robot/launcher_if.sh

sleep 1
tmux attach