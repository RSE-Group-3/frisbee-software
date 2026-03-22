from enum import IntEnum

class RobotStates(IntEnum):
    IDLE = 0
    PREDICTING = 1
    SEARCHING = 2
    APPROACHING = 3
    COLLECTING = 4
    RETURNING = 5
    LAUNCHING = 6

    RESETTING_MECHANICAL = 7
    RESETTING_POSITION = 8
    RESETTING_TRACKER = 9

    SAFESTOP = 10

def task_to_state(task: str):
    if task in _TASK_TO_STATE:
        return _TASK_TO_STATE[task]
    else:
        return None

_TASK_TO_STATE = {
    'predict': RobotStates.PREDICTING,
    'search': RobotStates.SEARCHING,
    'approach': RobotStates.APPROACHING,
    'collect': RobotStates.COLLECTING,
    'return': RobotStates.RETURNING,
    'launch': RobotStates.LAUNCHING,

    'reset_mech': RobotStates.RESETTING_MECHANICAL,
    'reset_pos': RobotStates.RESETTING_POSITION,
    'reset_track': RobotStates.RESETTING_TRACKER,

    'stop': RobotStates.SAFESTOP,
}

def valid_tasks():
    return _TASK_TO_STATE.keys()

def is_valid_task_list(task_list):
    if 'stop' in task_list: # safestop must be the only task
        return len(task_list) == 1
    
    for task in task_list:
        if task not in valid_tasks():
            return False
    return True

__all__ = [
    "RobotState",
    "task_to_state",
    "valid_tasks"
    "is_valid_task_list"
]