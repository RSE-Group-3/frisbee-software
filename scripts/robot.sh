#!/bin/bash

colcon build --packages-select fb_bringup --symlink-install

source install/setup.bash

ros2 pkg list | grep fb_

tmux kill-server

######

./src/fb_bringup/scripts/launch_cameras.sh --camera_set laptop1 --exposure 1000 --brightness 50
# ./src/fb_bringup/scripts/arduino_bridge.sh

# tmux attach-session -t arduino_bridge