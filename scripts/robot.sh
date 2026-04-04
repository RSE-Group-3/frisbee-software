#!/bin/bash

# defaults for PRL after sunset
EXPOSURE=60
BRIGHTNESS=0
SKIP_BUILD=false

for arg in "$@"; do
    case $arg in
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

if [ "$SKIP_BUILD" = false ]; then
    colcon build --packages-select fb_bringup --symlink-install
else
    echo -e "\nSkipping build...\n"
fi

source install/setup.bash

ros2 pkg list | grep fb_

tmux kill-server

######

./src/fb_bringup/scripts/launch_cameras.sh --topic /camera/collector --device /dev/video0 --exposure $EXPOSURE --brightness $BRIGHTNESS
# ./src/fb_bringup/scripts/launch_cameras.sh --topic /camera/launcher --device /dev/video2 --exposure $EXPOSURE --brightness $BRIGHTNESS
./src/fb_bringup/scripts/arduino_bridge.sh

tmux attach-session -t arduino_bridge