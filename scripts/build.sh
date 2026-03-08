#!/bin/bash

rm -rf build/ install/ log/
unset AMENT_PREFIX_PATH

colcon build --packages-select fb_collector --symlink-install
colcon build --packages-select fb_launcher --symlink-install
colcon build --packages-select fb_mobility --symlink-install
colcon build --packages-select fb_planning --symlink-install
colcon build --packages-select fb_vision --symlink-install

source install/setup.bash

ros2 pkg list | grep fb_