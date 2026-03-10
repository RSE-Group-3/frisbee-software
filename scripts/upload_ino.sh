#!/bin/bash

arduino-cli compile --fqbn arduino:avr:nano ../frisbee-arduino/Motor_testing/DC_motor/DC_motor.ino 

arduino-cli upload --port /dev/ttyAMA0 --fqbn arduino:avr:nano ../frisbee-arduino/Motor_testing/DC_motor/DC_motor.ino 