#!/bin/bash

# example usage: ./scripts/run_robot.sh --mode launcher --build --no_hardware

MODE="all"
BUILD="false"
HARDWARE="true"

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode)
      MODE="$2"
      shift 2
      ;;
    --build)
      BUILD="true"
      shift 1
      ;;
    --no_hardware)
      HARDWARE="false"
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


conda activate frisbee_env

if [ "$BUILD" = "true" ]; then
  echo "Building workspace..."
  source ./scripts/build.sh
fi

tmux kill-server


run_launcher_manual() {
  ./scripts/robot/upload_ino.sh
  ./scripts/robot/launcher_interface.sh --manual
}

run_collector_manual() {
  ./scripts/robot/upload_ino.sh
  ./scripts/robot/collector_interface.sh --manual
}

run_launcher() {
  ./scripts/robot/upload_ino.sh
  ./scripts/robot/launcher_interface.sh
}

run_collector() {
  ./scripts/robot/upload_ino.sh
  ./scripts/robot/collector_interface.sh
}

run_mobility() {
  # Add command to run mobility mode here
  echo "Mobility mode not implemented yet"
}

run_hardware_utils() {
  ./scripts/robot/arduino_bridge.sh
}

run_vision() {
  if [ "$HARDWARE" = "true" ]; then
    ./scripts/launch_robot_cams.sh \
      --device_front /dev/video0 \
      --device_back /dev/video2 \
      --exposure 200
  fi
}

case "$MODE" in
  "all")
    echo "Running everything..."
    run_hardware_utils &
    run_launcher &
    run_collector &
    run_mobility &
    run_vision
    ;;
  "vision")
    echo "Running vision-only mode..."
    run_vision
    ;;
  "launcher")
    echo "Running launcher-only mode..."
    run_hardware_utils &
    run_launcher_manual
    ;;
  "collector")
    echo "Running collector-only mode..."
    run_hardware_utils &
    run_collector_manual
    ;;
  "mobility")
    echo "Running mobility-only mode..."
    run_hardware_utils &
    run_mobility_manual
    ;;
  *)
    echo "Unknown mode: $MODE"
    echo ""
    print_help
    exit 1
    ;;
esac


sleep 1
tmux attach