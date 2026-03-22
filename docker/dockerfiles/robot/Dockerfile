FROM ros:humble
ARG GID=1000
ARG UID=1000

RUN apt update && apt install -y \
    python3-pip \
    tmux \
    nano \
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

# Set up tmux 256-color configuration
RUN echo 'set -g default-terminal "screen-256color"' >> /home/appuser/.tmux.conf \
 && echo 'set -g terminal-overrides "*:colors=256"' >> /home/appuser/.tmux.conf

CMD ["bash", "-i"]