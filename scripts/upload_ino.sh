#!/bin/bash
arduino-cli board list

# arduino-cli compile \
#     --fqbn arduino:avr:nano \
#     ./arduino/launcher_motor/launcher_motor.ino

# arduino-cli lib install Servo
# arduino-cli lib install AccelStepper
# arduino-cli core install arduino:samd # avr not needed?

arduino-cli compile \
    --fqbn arduino:samd:nano_33_iot \
    ./arduino/launcher_motor/launcher_motor.ino

arduino-cli upload \
  -p /dev/ttyACM0 \
  --fqbn arduino:samd:nano_33_iot \
  ./arduino/launcher_motor/launcher_motor.ino
