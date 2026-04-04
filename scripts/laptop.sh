#!/bin/bash

SIM=false
CAMERA=false

# defaults for PRL after sunset
EXPOSURE=60
BRIGHTNESS=0
SKIP_BUILD=false

for arg in "$@"; do
    case $arg in
        --sim)
        SIM=true
        shift
        ;;
        --camera)
        CAMERA=true
        shift
        ;;
        --exposure)
        EXPOSURE="$2"
        shift
        shift
        ;;
        --brightness)
        BRIGHTNESS="$2"
        shift
        shift
        ;;
        --skip)
        SKIP_BUILD=true
        shift
        ;;
        --h)
        echo "Usage: $0 [--exposure <value>] [--brightness <value>]"
        exit 0
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

if [ "$SKIP_BUILD" = false ]; then
    colcon build --packages-select fb_interfaces --symlink-install
    colcon build --packages-select fb_bringup --symlink-install
    colcon build --packages-select fb_planning --symlink-install
    colcon build --packages-select fb_vision --symlink-install
    colcon build --packages-select fb_manipulation --symlink-install
    colcon build --packages-select fb_gazebo --symlink-install
    colcon build --packages-select fb_mobility --symlink-install
else
    echo -e "\nSkipping build...\n"
fi

source install/setup.bash

ros2 pkg list | grep fb_

tmux kill-server

######

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

if [ "$CAMERA" = true ]; then
    ./src/fb_bringup/scripts/launch_cameras.sh --topic /camera/collector --device /dev/video2 --exposure $EXPOSURE --brightness $BRIGHTNESS
    # TODO: other cameras if needed
fi

sleep 1
tmux attach-session -t central_planner