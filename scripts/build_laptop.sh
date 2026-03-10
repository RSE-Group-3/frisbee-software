#!/bin/bash

rm -rf build/ install/ log/

colcon build --packages-select fb_planning --symlink-install
colcon build --packages-select fb_vision --symlink-install
colcon build --packages-select fb_utils --symlink-install
source install/setup.bash

ros2 pkg list | grep fb_