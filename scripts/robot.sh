#!/bin/bash

colcon build --packages-select fb_bringup --symlink-install

source install/setup.bash

ros2 pkg list | grep fb_

tmux kill-server

######

./src/fb_bringup/scripts/cameras_robot.sh
./src/fb_bringup/scripts/arduino_bridge.sh


