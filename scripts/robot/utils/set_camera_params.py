import subprocess
import sys

def main():
    devices = sys.argv[1:]
    
    while True:
        exposure = input('\nSet exposure:')

        for device in devices:
            subprocess.call(f'v4l2-ctl -d {device} --set-ctrl=brightness=0')
            subprocess.call(f'v4l2-ctl -d {device} --set-ctrl=auto_exposure=1')
            subprocess.call(f'v4l2-ctl -d {device} --set-ctrl=exposure_time_absolute={exposure}')


if __name__ == '__main__':
    main()