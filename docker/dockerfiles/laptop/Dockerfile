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

CMD ["bash", "-i"]