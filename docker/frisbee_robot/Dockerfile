FROM ros:humble

RUN apt update && apt install -y \
    python3-pip \
    tmux \
    && rm -rf /var/lib/apt/lists/*

RUN apt update && apt install -y \
    python3-pip \
    tmux \
    && rm -rf /var/lib/apt/lists/*


# Install Arduino CLI
RUN curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh \
    && mv bin/arduino-cli /usr/local/bin/
# Install Arduino cores and libraries
RUN arduino-cli core update-index \
    && arduino-cli core install arduino:avr \
    && arduino-cli lib install Servo


RUN pip install pyserial


# Create workspace
WORKDIR /ros2_ws

# Copy your project
COPY . /ros2_ws

# Build workspace
RUN . /opt/ros/humble/setup.sh

CMD ["bash"]