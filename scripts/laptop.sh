#!/bin/bash

colcon build --packages-select fb_bringup --symlink-install
colcon build --packages-select fb_planning --symlink-install
colcon build --packages-select fb_vision --symlink-install

source install/setup.bash

ros2 pkg list | grep fb_

######

./src/fb_bringup/scripts/foxglove_bridge.sh
./src/fb_bringup/scripts/cameras_laptop.sh

./src/fb_planning/scripts/central_planner.sh
./src/fb_planning/scripts/path_planner.sh

./src/fb_vision/scripts/vision.sh

sleep 1
tmux attach-session -t central_planner