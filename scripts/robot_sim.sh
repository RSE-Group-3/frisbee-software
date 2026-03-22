#!/bin/bash
colcon build --packages-select fb_manipulation --symlink-install
colcon build --packages-select fb_mobility --symlink-install
colcon build --packages-select fb_utils --symlink-install

colcon build --packages-select fb_gazebo --symlink-install

source install/setup.bash

ros2 pkg list | grep fb_

###

tmux kill-server

./scripts/sessions_robot/mobility_sim.sh
./scripts/sessions_robot/manipulation_sim.sh

sleep 1
tmux attach