from dataclasses import dataclass
from enum import IntEnum

class LauncherCmd(IntEnum):
    RESET = 0
    LAUNCH = 1
@dataclass
class LauncherCmdMsg:  # published by CentralPlanner
    cmd: LauncherCmd
@dataclass  
class LauncherAckMsg:  # published by LauncherNode
    cmd: LauncherCmd
    success: bool
    err_msg: str

class CollectorCmd(IntEnum):
    HOME = 0
    OPEN = 1
    CLOSE = 2
    COLLECT = 3
    LOAD = 4
@dataclass
class CollectorCmdMsg:  # published by CentralPlanner
    cmd: CollectorCmd
@dataclass  
class CollectorAckMsg:  # published by CollectorNode
    cmd: CollectorCmd
    success: bool
    err_msg: str