#!/bin/bash

conda activate frisbee_env

rm -rf build/ install/ log/
unset AMENT_PREFIX_PATH

colcon build --symlink-install
source install/setup.bash

ros2 pkg list | grep fb_