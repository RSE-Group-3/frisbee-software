#!/bin/bash

if [ -z "$1" ]; then
  echo "Usage: $0 <sketch_name>"
  exit 1
fi

SKETCH_NAME=$1
SKETCH_PATH="./arduino/${SKETCH_NAME}/${SKETCH_NAME}.ino"

echo "Using sketch: $SKETCH_PATH"

arduino-cli board list

arduino-cli compile \
    --fqbn arduino:samd:nano_33_iot \
    "$SKETCH_PATH"

arduino-cli upload \
  -p /dev/ttyACM0 \
  --fqbn arduino:samd:nano_33_iot \
  "$SKETCH_PATH"