#!/bin/bash

tmux kill-server

./scripts/sessions_robot/launch_cameras.sh
./scripts/sessions_robot/arduino_bridge.sh

./scripts/sessions_robot/mobility_if.sh
./scripts/sessions_robot/collector_if.sh
./scripts/sessions_robot/launcher_if.sh

sleep 1
tmux attach