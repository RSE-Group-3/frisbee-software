import subprocess
import sys

def main():
    devices = sys.argv[1:]
    print()
    print('Devices:', devices)
    
    while True:
        exposure = input('Set exposure: ')

        for device in devices:
            subprocess.run(["v4l2-ctl", "-d", device, "--set-ctrl=brightness=0"])
            subprocess.run(["v4l2-ctl", "-d", device, "--set-ctrl=auto_exposure=1"])
            subprocess.run(["v4l2-ctl", "-d", device, f"--set-ctrl=exposure_time_absolute={exposure}"])


if __name__ == '__main__':
    main()