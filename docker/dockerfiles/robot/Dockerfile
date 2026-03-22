FROM ros:humble
ARG GID=1000
ARG UID=1000

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

# sim
RUN apt update && apt install -y \
    ros-humble-gazebo-ros-pkgs \
    ros-humble-ros2-control ros-humble-ros2-controllers \
    ros-humble-xacro \
    ros-humble-gazebo-ros2-control \
    ros-humble-ros2-control \
    ros-humble-controller-manager \
    ros-humble-teleop-twist-keyboard \
    ros-humble-navigation2 \
    ros-humble-nav2-bringup \
    ros-humble-topic-tools \
    psmisc \
    && rm -rf /var/lib/apt/lists/*


# Install Arduino CLI
RUN curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh \
    && mv bin/arduino-cli /usr/local/bin/
# Install Arduino cores and libraries
RUN arduino-cli core update-index \
    && arduino-cli core install arduino:avr \
    && arduino-cli lib install Servo

RUN pip install pyserial



RUN groupadd -g $GID appgroup && useradd -m -u $UID -g appgroup -s /bin/bash appuser
USER appuser

# ros workspace
WORKDIR /ros2_ws
COPY . /ros2_ws
RUN . /opt/ros/humble/setup.sh

RUN cat <<'EOF' >> /home/appuser/.bashrc
# green prompt
PS1="\[\e[1;32m\]\u@\h:\w\$ \[\e[0m\]"
# ros source
source /opt/ros/humble/setup.sh
SETUP="/ros2_ws/install/setup.bash"
if [ -f "$SETUP" ]; then
    source "$SETUP"
fi
EOF

CMD ["bash", "-i"]