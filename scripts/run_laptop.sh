#!/bin/bash

MODE="all"
BUILD="false"

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
    *)
      echo "Unknown argument: $1"
      echo ""
      print_help
      exit 1
      ;;
  esac
done



if [ "$BUILD" = "true" ]; then
  echo "Building workspace..."
  source ./scripts/build.sh
fi

tmux kill-server
./scripts/laptop/launch_foxglove.sh



run_launcher() {
  # Add command to run launcher mode here
  echo "Launcher mode not implemented yet"
}

run_collector() {
  # Add command to run collector mode here
  echo "Collector mode not implemented yet"
}

run_mobility() {
  # Add command to run mobility mode here
  echo "Mobility mode not implemented yet"
}

run_vision() {
  ./scripts/launch_vision_models.sh
}

case "$MODE" in
  "all")
    echo "Running everything..."
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
    run_launcher
    ;;
  "collector")
    echo "Running collector-only mode..."
    run_collector
    ;;
  "mobility")
    echo "Running mobility-only mode..."
    run_mobility
    ;;
  *)
    echo "Unknown mode: $MODE"
    echo ""
    print_help
    exit 1
    ;;
esac