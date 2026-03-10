FROM ros:humble

RUN apt update && apt install -y \
    python3-pip \
    tmux \
    && rm -rf /var/lib/apt/lists/*
    
RUN apt update && apt install -y \
    ros-humble-foxglove-bridge \
    ros-humble-usb-cam ros-humble-image-tools \
    python3-opencv \
    ros-humble-cv-bridge \
    ros-humble-image-transport \
    ros-humble-image-transport-plugins \
    && rm -rf /var/lib/apt/lists/*

# Create workspace
WORKDIR /ros2_ws

# Copy your project
COPY . /ros2_ws

# Build workspace
RUN . /opt/ros/humble/setup.sh

CMD ["bash"]