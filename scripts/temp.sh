#!/bin/bash
colcon build --packages-select fb_utils --symlink-install
colcon build --packages-select fb_gazebo --symlink-install

source install/setup.bash

ros2 pkg list | grep fb_

###

tmux kill-server

# ./scripts/sessions_robot/arduino_bridge.sh

sleep 1
tmux attach