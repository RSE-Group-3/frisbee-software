#!/bin/bash

DEVICE_FRONT="/dev/video0"
DEVICE_BACK="/dev/video2"
EXPOSURE="200" # min=1 max=5000 step=1 default=157 value=50


print_help() {
  echo ""
  echo "Available video devices:"
  v4l2-ctl --list-devices	
  echo ""
  echo "Usage: $0 [OPTIONS]"
  echo ""
  echo "Options:"
  echo "  --device_front <path>       Front video device (default: /dev/video0)"
  echo "  --device_back <path>        Back video device (default: /dev/video2)"
  echo "  --exposure <value>    Set manual exposure_time_absolute (default: 200)"
  echo "  -h, --help            Show help message"
  echo ""
  echo "Examples:"
  echo "  $0 --device_front /dev/video0 --device_back /dev/video2 --exposure 100"
}

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --device_front)
      DEVICE_FRONT="$2"
      shift 2
      ;;
    --device_back)
      DEVICE_BACK="$2"
      shift 2
      ;;
    --exposure)
      EXPOSURE="$2"
      shift 2
      ;;
    -h|--help)
      print_help
      exit 0
      ;;
    *)
      echo "Unknown argument: $1"
      echo ""
      print_help
      exit 1
      ;;
  esac
done


./scripts/launch_single_cam.sh \
  --camera front_robot_cam \
  --device $DEVICE_FRONT \
  --exposure $EXPOSURE \
  --brightness 0

./scripts/launch_single_cam.sh \
  --camera back_robot_cam \
  --device $DEVICE_BACK \
  --exposure $EXPOSURE \
  --brightness 0