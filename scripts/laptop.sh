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
colcon build --packages-select fb_manipulation --symlink-install


source install/setup.bash

ros2 pkg list | grep fb_

######

# ./src/fb_bringup/scripts/launch_cameras.sh test 1000 50

./src/fb_planning/scripts/central_planner.sh

if [ "$SIM" = true ]; then
    ./src/fb_manipulation/scripts/manipulation_sim.sh

    ./src/fb_gazebo/scripts/gazebo.sh
    ./src/fb_mobility/scripts/teleop.sh
else
    ./src/fb_manipulation/scripts/manipulation.sh

    ./src/fb_mobility/scripts/diff_drive.sh
    ./src/fb_mobility/scripts/teleop.sh

fi

./src/fb_planning/scripts/path_planner.sh

./src/fb_vision/scripts/vision.sh

sleep 1
tmux attach-session -t central_planner