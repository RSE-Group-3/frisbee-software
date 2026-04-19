FROM ros:humble
ARG GID=1000
ARG UID=1000

RUN apt update && apt install -y \
    python3-pip \
    tmux \
    nano \
    psmisc \
    curl \
    # vision
    ros-humble-usb-cam \
    # ros-humble-image-tools \
    # ros-humble-cv-bridge \
    ros-humble-image-transport \
    ros-humble-image-transport-plugins \
    && rm -rf /var/lib/apt/lists/*

# system-wide arduino
RUN curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh \
    && mv bin/arduino-cli /usr/local/bin/

RUN groupadd -g $GID appgroup \
    && useradd -m -u $UID -g appgroup -s /bin/bash appuser \
    && usermod -aG dialout appuser \
    && usermod -aG video appuser

USER appuser

# ensure Arduino CLI uses a consistent user-owned directory
ENV ARDUINO_DATA_DIR=/home/appuser/.arduino15
ENV ARDUINO_CONFIG_DIR=/home/appuser/.arduino15

# RUN mkdir -p /home/appuser/.arduino15 \
    # && arduino-cli core update-index \
    # && arduino-cli core install arduino:samd \
    # && arduino-cli lib install Servo \
    # && arduino-cli lib install AccelStepper

RUN pip install pyserial

# ros workspace
WORKDIR /ros2_ws
COPY . /ros2_ws

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

# Set up tmux 256-color configuration
RUN echo 'set -g default-terminal "screen-256color"' >> /home/appuser/.tmux.conf \
 && echo 'set -g terminal-overrides "*:colors=256"' >> /home/appuser/.tmux.conf

CMD ["bash", "-i"]