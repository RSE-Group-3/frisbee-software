#!/bin/bash

CAMERA=""
DEVICE=""
EXPOSURE=""
BRIGHTNESS=""

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --camera)
      CAMERA="$2"
      shift 2
      ;;
    --device)
      DEVICE="$2"
      shift 2
      ;;
    --exposure)
      EXPOSURE="$2"
      shift 2
      ;;
    --brightness)
      BRIGHTNESS="$2"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1"
      echo ""
      print_help
      exit 1
      ;;
  esac
done

if [[ -z "$CAMERA" || -z "$DEVICE" || -z "$EXPOSURE" || -z "$BRIGHTNESS" ]]; then
    echo "Error: all arguments --camera, --device, --exposure, --brightness are required"
    echo ""
    print_help
    exit 1
fi


SESSION=$CAMERA

# Kill existing session if it exists
tmux has-session -t $SESSION 2>/dev/null
if [ $? -eq 0 ]; then
    tmux kill-session -t $SESSION
fi

tmux new-session -d -s $SESSION

# tmux split-window -h -t $SESSION

tmux send-keys -t $SESSION:0.0 "conda activate frisbee-env" C-m
tmux send-keys -t $SESSION:0.0 "source /opt/ros/humble/setup.bash" C-m
tmux send-keys -t $SESSION:0.0 "ros2 run usb_cam usb_cam_node_exe \
  --ros-args --remap __ns:=/$CAMERA \
  -p video_device:=$DEVICE \
  -p pixel_format:='mjpeg2rgb'" C-m

echo "Launched $CAMERA with device $DEVICE, waiting for node to come up..."

# Attach to session
# tmux attach -t $SESSION

until ros2 node list | grep -q "/$CAMERA"; do
  sleep 0.1
done
echo "$CAMERA is up, setting parameters..."

# Set camera parameters
sleep 0.5
v4l2-ctl -d $DEVICE --set-ctrl=brightness=$BRIGHTNESS
sleep 0.5
v4l2-ctl -d $DEVICE --set-ctrl=auto_exposure=1
sleep 0.5
v4l2-ctl -d $DEVICE --set-ctrl=exposure_time_absolute=$EXPOSURE
echo "done."