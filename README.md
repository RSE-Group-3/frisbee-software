# frisbee-software


### running in docker

sudo usermod -aG docker $USER

Robot:
./docker/robot.sh # build and run docker image
./scripts/robot.sh # build and launch all nodes

Laptop:
./docker/laptop.sh # build and run docker image
./scripts/laptop.sh # build and launch all nodes


### devices

on laptop:
* /dev/video2: front camera
* /dev/video4: back camera

on pi:
<!-- * /dev/video0: front camera 
* /dev/video2: back camera -->
* /dev/ttyUSB0: arduino
