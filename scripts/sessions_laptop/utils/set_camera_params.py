import subprocess
import sys

def main():
    devices = sys.argv[1:]
    print()
    print('Devices:', devices)
    print('Example input:')
    print('    b 50 # brightness')
    print('    e 1000 # exposure_time_absolute')

    while True:
        print()
        args = input('Set ctrl: ').strip().split()
        if len(args) != 2:
            print('invalid input.')
            continue

        ctrl, value = args
        if ctrl == 'b':
            for device in devices:
                subprocess.run([f"v4l2-ctl", "-d", device, "--set-ctrl=brightness={value}"])
            print(f'done. brightness={value}')
        elif ctrl == 'e':
            for device in devices:
                subprocess.run(["v4l2-ctl", "-d", device, "--set-ctrl=auto_exposure=1"])
                subprocess.run(["v4l2-ctl", "-d", device, f"--set-ctrl=exposure_time_absolute={value}"])
            print(f'done. exposure_time_absolute={value}')
        else:
            print('invalid input.')
            continue


if __name__ == '__main__':
    main()