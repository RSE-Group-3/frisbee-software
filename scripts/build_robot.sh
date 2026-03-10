#!/bin/bash

rm -rf build/ install/ log/

colcon build --packages-select fb_hardware_if --symlink-install
colcon build --packages-select fb_utils --symlink-install
source install/setup.bash

ros2 pkg list | grep fb_