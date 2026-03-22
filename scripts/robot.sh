#!/bin/bash

SIM=false

for arg in "$@"; do
    case $arg in
        --sim)
        SIM=true
        shift
        ;;
        *)
        ;;
    esac
done

if [ "$SIM" = true ]; then
    echo -e "\nLaunching robot tmux sessions (simulation)...\n"
else
    echo -e "\n:aunching robot tmux sessions (hardware)...\n"
fi


colcon build --packages-select fb_bringup --symlink-install
colcon build --packages-select fb_gazebo --symlink-install
colcon build --packages-select fb_mobility --symlink-install
colcon build --packages-select fb_manipulation --symlink-install

source install/setup.bash

ros2 pkg list | grep fb_

tmux kill-server

######

# ./fb_bringup/scripts/cameras_robot.sh # UNUSED

if [ "$SIM" = true ]; then
    ./src/fb_gazebo/scripts/gazebo.sh
    ./src/fb_mobility/scripts/teleop.sh

    ./src/fb_manipulation/scripts/manipulation_sim.sh

    sleep 1
    tmux attach-session -t manipulation_sim
else
    ./src/fb_bringup/scripts/arduino_bridge.sh

    ./src/fb_mobility/scripts/diff_drive.sh
    ./src/fb_mobility/scripts/teleop.sh

    ./src/fb_manipulation/scripts/manipulation.sh

    sleep 1
    tmux attach-session -t manipulation
fi

