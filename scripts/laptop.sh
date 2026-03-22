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
    echo -e "\nLaunching laptop tmux sessions (simulation)...\n"
else
    echo -e "\n:aunching laptop tmux sessions (hardware)...\n"
fi

colcon build --packages-select fb_bringup --symlink-install
colcon build --packages-select fb_planning --symlink-install
colcon build --packages-select fb_vision --symlink-install

source install/setup.bash

ros2 pkg list | grep fb_

######

./src/fb_bringup/scripts/foxglove_bridge.sh
# ./src/fb_bringup/scripts/cameras_laptop.sh

./src/fb_planning/scripts/central_planner.sh
./src/fb_planning/scripts/path_planner.sh

./src/fb_vision/scripts/vision.sh


if [ "$SIM" = true ]; then
    ./src/fb_gazebo/scripts/gazebo.sh
    ./src/fb_mobility/scripts/teleop.sh

    ./src/fb_manipulation/scripts/manipulation_sim.sh

    sleep 1
    tmux attach-session -t manipulation_sim
else
    ./src/fb_mobility/scripts/diff_drive.sh
    ./src/fb_mobility/scripts/teleop.sh

    ./src/fb_manipulation/scripts/manipulation.sh

    sleep 1
    tmux attach-session -t manipulation
fi

sleep 1
tmux attach-session -t central_planner