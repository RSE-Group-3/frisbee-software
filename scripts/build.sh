#!/bin/bash
# Navigate to the workspace root
cd ~/frisbee_ws/

# Optional: Remove old build folders to prevent cache issues
# rm -rf build/ install/ log/

# Build the specific packages for the robot
colcon build --symlink-install

# Source the local workspace
source install/setup.bash

echo "Build finished and workspace sourced."