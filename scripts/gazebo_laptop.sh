#!/bin/bash
set -e

cd ../frisbee-software-sim

SKIP_BUILD=false

for arg in "$@"; do
    case $arg in
        --skip)
        SKIP_BUILD=true
        shift
        ;;
        --h)
        echo "Usage: $0 --skip"
        exit 0
        ;;
        *)
        ;;
    esac
done


if [ "$SKIP_BUILD" = false ]; then
    colcon build --packages-select fb_gazebo --symlink-install
else
    echo -e "\nSkipping build...\n"
fi

source install/setup.bash

ros2 pkg list | grep fb_

tmux kill-server

######

./src/fb_gazebo/scripts/gazebo.sh

sleep 1
tmux attach-session -t gazebo