#!/bin/bash

# Name of the environment
ENV_NAME="frisbee_env"

# Check if conda command exists
if ! command -v conda &> /dev/null; then
    echo "Conda not found! Please install Anaconda or Miniconda first."
    exit 1
fi

# Create the environment with Python 3.10
echo "Creating Conda environment '$ENV_NAME' with Python 3.10..."
conda create -y -n "$ENV_NAME" python=3.10 pip

# Activate the environment
echo "Activating environment..."
# Use 'conda activate' in interactive shell
eval "$(conda shell.bash hook)"
conda activate "$ENV_NAME"

# Install common ROS 2 Python dependencies
echo "Installing ROS 2 Python dependencies..."
pip install setuptools colcon-common-extensions empy lark-parser

# Other dependencies:
echo "Installing other dependencies..."
conda install -y -n "$ENV_NAME" opencv numpy matplotlib

# Done
echo "Conda environment '$ENV_NAME' setup complete!"
echo "Activate it with: conda activate $ENV_NAME"
