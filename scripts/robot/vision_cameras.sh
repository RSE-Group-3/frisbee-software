#!/bin/bash

DEVICE_FRONT="/dev/video0"
CAMERA_FRONT="front_robot_cam"
DEVICE_BACK="/dev/video2"
CAMERA_BACK="back_robot_cam"
EXPOSURE="200" # min=1 max=5000 step=1 default=157 value=50



SESSION="robot_cameras"

# Kill existing session if it exists
tmux has-session -t $SESSION 2>/dev/null
if [ $? -eq 0 ]; then
    tmux kill-session -t $SESSION
fi

tmux new-session -d -s $SESSION

tmux split-window -h -t $SESSION
tmux split-window -v -t $SESSION:0.0
tmux split-window -v -t $SESSION:0.2



wait_for_node() {
  NODE=$1
  TIMEOUT=$2
  START=$(date +%s)

  while true; do
    if ros2 node list | grep -q "$NODE"; then
      return 0
    fi

    NOW=$(date +%s)
    if [ $((NOW - START)) -ge $TIMEOUT ]; then
      return 1
    fi

    sleep 0.2
  done
}

# front camera
tmux send-keys -t $SESSION:0.0 "conda activate frisbee-env" C-m
tmux send-keys -t $SESSION:0.0 "source /opt/ros/humble/setup.bash" C-m
tmux send-keys -t $SESSION:0.0 "ros2 run usb_cam usb_cam_node_exe \
  --ros-args --remap __ns:=/$CAMERA_FRONT \
  -p video_device:=$DEVICE_FRONT \
  -p pixel_format:='mjpeg2rgb'" C-m
echo "Launching $CAMERA_FRONT..."

# back camera
tmux send-keys -t $SESSION:0.2 "conda activate frisbee-env" C-m
tmux send-keys -t $SESSION:0.2 "source /opt/ros/humble/setup.bash" C-m
tmux send-keys -t $SESSION:0.2 "ros2 run usb_cam usb_cam_node_exe \
  --ros-args --remap __ns:=/$CAMERA_BACK \
  --remap __node:=back_camera_node \
  -p video_device:=$DEVICE_BACK \
  -p pixel_format:='mjpeg2rgb'" C-m
echo "Launching $CAMERA_BACK..."

(
if ! wait_for_node "/$CAMERA_FRONT" 5; then
  echo "Warning: $CAMERA_FRONT did not come up within timeout, skipping parameter setting"
else
  echo "$CAMERA_FRONT is up, setting parameters..."
  sleep 0.5
  tmux send-keys -t $SESSION:0.1 "v4l2-ctl -d $DEVICE_FRONT --set-ctrl=brightness=0" C-m
  tmux send-keys -t $SESSION:0.1 "v4l2-ctl -d $DEVICE_FRONT --set-ctrl=auto_exposure=1" C-m
  tmux send-keys -t $SESSION:0.1 "v4l2-ctl -d $DEVICE_FRONT --set-ctrl=exposure_time_absolute=$EXPOSURE" C-m
fi
) &


(
if ! wait_for_node "/$CAMERA_BACK" 5; then
  echo "Warning: $CAMERA_BACK did not come up within timeout, skipping parameter setting"
else
  echo "$CAMERA_BACK is up, setting parameters..."
  sleep 0.5
  tmux send-keys -t $SESSION:0.3 "v4l2-ctl -d $DEVICE_BACK --set-ctrl=brightness=0" C-m
  tmux send-keys -t $SESSION:0.3 "v4l2-ctl -d $DEVICE_BACK --set-ctrl=auto_exposure=1" C-m
  tmux send-keys -t $SESSION:0.3 "v4l2-ctl -d $DEVICE_BACK --set-ctrl=exposure_time_absolute=$EXPOSURE" C-m
fi
) &

wait