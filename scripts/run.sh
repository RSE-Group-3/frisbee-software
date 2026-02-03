#!/bin/bash
source install/setup.bash

echo "Select Mode:"
echo "1) Simulation (Gazebo)"
echo "2) Real Robot (Physical Hardware)"
echo "3) Mapping Only (SLAM)"
read -p "Enter choice [1-3]: " choice

case $choice in
  1)
    ros2 launch frisbee_bot sim_launch.py
    ;;
  2)
    ros2 launch frisbee_bot hardware_launch.py
    ;;
  3)
    ros2 launch frisbee_bot slam_launch.py
    ;;
  *)
    echo "Invalid choice"
    ;;
esac