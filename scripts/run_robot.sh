#!/bin/bash

# example usage: ./scripts/run_robot.sh --mode launcher --build --no_hardware

MODE="all"
BUILD="false"
HARDWARE="true"


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