#!/usr/bin/env python3

import subprocess
from fb_planning.utils.planner_utils import RobotStates
from fb_planning.utils import planner_utils

# terminal colors
GREEN = "\033[32m"
RESET = "\033[0m"

def run_command(tasks):
    # ros2 service call /user_input fb_interfaces/srv/PlannerCommand '{"command": "launch"}'
    cmd = ["ros2", "topic", "pub", "-1", "/user_input", "std_msgs/msg/String", f'{{"data": "{tasks}"}}']
    try:
        print()
        print(f"Running: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        print("Command sent.\n")
    except subprocess.CalledProcessError as e:
        print(f"Command failed with return code {e.returncode}\n")
    except KeyboardInterrupt:
        print("\nExecution interrupted by user.\n")
        raise

def print_help():
    print(f'''
VALID_TASKS = {planner_utils.valid_tasks()}

Usage:
    collect               # single task
    collect,return,launch # task sequence

    reset_mech            # reset collector
    reset_position        # zero robot position
    reset_tracker         # discard previous tracking data
          
    reset                 # reset_mech,reset_pos,reset_track
    demo                  # predict,search,approach,collect,return,launch

    stop                  # interrupt task execution
''')
    
def main():
    print_help()

    try:
        while True:
            user_input = input(f"\n{GREEN}Enter task sequence: {RESET}").strip()

            # shortcuts
            if user_input == 'h' or user_input == 'help':
                print_help()
                continue
            elif user_input == 'reset':
                user_input = 'reset_mech,reset_pos,reset_track'
            elif user_input == 'demo':
                user_input = 'predict,search,approach,collect,return,launch'
                
            task_list = user_input.split(',')
            
            if not planner_utils.is_valid_task_list(task_list):
                print(f"Invalid task list: {task_list}. Please use: {', '.join(planner_utils.valid_tasks())}")
            else:
                run_command(user_input)


    except KeyboardInterrupt:
        print("Exiting.")

if __name__ == "__main__":
    main()