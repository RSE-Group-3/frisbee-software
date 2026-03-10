#!/bin/bash

tmux kill-server

./scripts/sessions_laptop/foxglove_bridge.sh

./scripts/sessions_laptop/central_planner.sh
./scripts/sessions_laptop/path_planner.sh

./scripts/sessions_laptop/vision_models.sh
./scripts/sessions_laptop/launch_cameras.sh

sleep 1
tmux attach