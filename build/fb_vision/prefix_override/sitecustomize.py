import sys
if sys.prefix == '/home/mmliu/miniconda3/envs/frisbee_env':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/mmliu/Documents/cmu/16450-Capstone/frisbee-software/install/fb_vision'
