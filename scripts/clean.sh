#!/bin/bash

# usage: source ./scripts/clean.sh

tmux kill-server
rm -rf ./install/ ./build/ ./log/
unset AMENT_PREFIX_PATH
