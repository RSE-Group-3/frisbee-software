FROM ros:humble
ARG GID=1000
ARG UID=1000

RUN apt update && apt install -y \
    python3-pip \
    tmux \
    nano \
    psmisc \
    && rm -rf /var/lib/apt/lists/*

# TODO: cannot find
# RUN apt update && apt install -y \
#     ros-humble-foxglove-bridge \
#     && rm -rf /var/lib/apt/lists/*

# vision
RUN apt update && apt install -y \
    ros-humble-usb-cam ros-humble-image-tools \
    python3-opencv \
    ros-humble-cv-bridge \
    ros-humble-image-transport \
    ros-humble-image-transport-plugins \
    && rm -rf /var/lib/apt/lists/*

# mobility
RUN apt update && apt install -y \
    ros-humble-topic-tools \
    ros-humble-teleop-twist-keyboard \
    ros-humble-navigation2 \
    ros-humble-nav2-bringup \
    && rm -rf /var/lib/apt/lists/*
     
# sim
RUN apt update && apt install -y \
    ros-humble-gazebo-ros-pkgs \
    ros-humble-ros2-control ros-humble-ros2-controllers \
    ros-humble-xacro \
    ros-humble-gazebo-ros2-control \
    ros-humble-ros2-control \
    ros-humble-controller-manager \
    && rm -rf /var/lib/apt/lists/*


RUN groupadd -g $GID appgroup && useradd -m -u $UID -g appgroup -s /bin/bash appuser
USER appuser

# ros workspace
WORKDIR /ros2_ws
COPY . /ros2_ws
RUN . /opt/ros/humble/setup.sh

RUN echo 'source /opt/ros/humble/setup.sh' >> /home/appuser/.bashrc
RUN echo 'PS1="\[\e[1;32m\]\u@\h:\w\$ \[\e[0m\]"' >> /home/appuser/.bashrc

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

# # Set up tmux 256-color configuration
# RUN echo 'set -g default-terminal "screen-256color"' >> /home/appuser/.tmux.conf \
#  && echo 'set -g terminal-overrides "*:colors=256"' >> /home/appuser/.tmux.conf

CMD ["bash", "-i"]