#!/bin/bash
sudo apt-get update
sudo apt-get install -y python3-pip ros-humble-nav2-bringup ros-humble-turtlebot3-vcs

pip3 install opencv-python numpy ultralytics

echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
source ~/.bashrc

echo "Setup Complete. You are ready to build."