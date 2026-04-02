#!/bin/bash

colcon build --packages-select fb_bringup --symlink-install

source install/setup.bash

ros2 pkg list | grep fb_

tmux kill-server

######

# ./src/fb_bringup/scripts/launch_cameras.sh robot2 1000 50 # TODO
./src/fb_bringup/scripts/arduino_bridge.sh

tmux attach-session -t arduino_bridge