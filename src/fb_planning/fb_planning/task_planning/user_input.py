#!/usr/bin/env python3

import subprocess

VALID_TASKS = ['launch', 'collect']

def run_command(tasks):
    cmd = ["ros2", "topic", "pub", "/command_sequence", "std_msgs/String", f"data: '{tasks}'", "--once"]
    try:
        print(f"Running: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        print("Command finished successfully.\n")
    except subprocess.CalledProcessError as e:
        print(f"Command failed with return code {e.returncode}\n")
    except KeyboardInterrupt:
        print("\nExecution interrupted by user.\n")
        raise

def main():
    print("tasks:")

    try:
        while True:
            user_input = input("\nEnter task sequence (q to exit): ").strip()
            if user_input.lower() == "q":
                print("Exiting.")
                break
            
            else:
                task_list = user_input.split(',')
                for task in task_list:
                    if task not in VALID_TASKS:
                        print(f"Invalid task: {task}. Please use: {', '.join(VALID_TASKS)}")
                        break
                else:
                    run_command(user_input)


    except KeyboardInterrupt:
        print("\nExecution interrupted by user. Goodbye!")

if __name__ == "__main__":
    main()