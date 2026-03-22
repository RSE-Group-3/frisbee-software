#!/bin/bash

colcon build --packages-select fb_planning --symlink-install
colcon build --packages-select fb_vision --symlink-install
colcon build --packages-select fb_utils --symlink-install

colcon build --packages-select fb_drivers --symlink-install

source install/setup.bash

ros2 pkg list | grep fb_

###

tmux kill-server

./scripts/sessions_laptop/foxglove_bridge.sh

./scripts/sessions_laptop/central_planner.sh
./scripts/sessions_laptop/path_planner.sh

./scripts/sessions_laptop/vision.sh

sleep 1
tmux attach