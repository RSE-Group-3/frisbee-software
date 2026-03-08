#!/bin/bash

rm -rf build/ install/ log/
unset AMENT_PREFIX_PATH

tmux kill-server