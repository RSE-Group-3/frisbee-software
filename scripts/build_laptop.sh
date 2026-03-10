#!/bin/bash

set -e

rm -rf build/ install/ log/

packages=("fb_planning" "fb_vision" "fb_utils")

if [ $# -eq 1 ]; then
    if [[ " ${packages[*]} " == *" $1 "* ]]; then
        colcon build --packages-select "$1" --symlink-install
    else
        echo "Package $1 not in build list: ${packages[*]}"
        exit 1
    fi
else
    for pkg in "${packages[@]}"; do
        colcon build --packages-select "$pkg" --symlink-install
    done
fi


source install/setup.bash

ros2 pkg list | grep fb_