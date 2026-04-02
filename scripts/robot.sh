#!/bin/bash

colcon build --packages-select fb_bringup --symlink-install

source install/setup.bash

ros2 pkg list | grep fb_

tmux kill-server

######

EXPOSURE=100
BRIGHTNESS=20

./src/fb_bringup/scripts/launch_cameras.sh --topic /camera/collector --device /dev/video0 --exposure $EXPOSURE --brightness $BRIGHTNESS
# ./src/fb_bringup/scripts/launch_cameras.sh --topic /camera/launcher --device /dev/video2 --exposure $EXPOSURE --brightness $BRIGHTNESS
./src/fb_bringup/scripts/arduino_bridge.sh

tmux attach-session -t arduino_bridge