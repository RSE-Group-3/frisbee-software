
BUILD="true"
[[ "$1" == "--skip_build" ]] && BUILD="false"
[[ $# -gt 1 ]] && { echo "Too many arguments"; print_help; exit 1; }

if [ "$BUILD" = "true" ]; then
  cd ./docker/frisbee_laptop
  echo "Building docker file..."
  docker build -t frisbee_laptop .
  cd ../..
fi


docker run --rm -it \
--net=host \
--ipc=host \
--privileged \
-v /dev:/dev \
-v $(pwd):/ros2_ws \
frisbee_laptop