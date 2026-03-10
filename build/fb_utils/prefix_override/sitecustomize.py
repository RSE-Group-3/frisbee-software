import sys
if sys.prefix == '/home/frisbee/miniconda3/envs/frisbee_env':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/frisbee/ros2_ws/src/frisbee-software/install/fb_utils'
