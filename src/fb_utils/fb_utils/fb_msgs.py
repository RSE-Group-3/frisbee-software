from dataclasses import dataclass
from enum import IntEnum

class LauncherIFCmd(IntEnum):
    RESET = 0
    LAUNCH = 1
@dataclass
class LauncherIFCmdMsg:  # published by CentralPlanner
    cmd: LauncherIFCmd
@dataclass  
class LauncherIFAckMsg:  # published by LauncherIFNode
    cmd: LauncherIFCmd
    success: bool
    err_msg: str

class CollectorIFCmd(IntEnum):
    HOME = 0
    OPEN = 1
    CLOSE = 2
    COLLECT = 3
    LOAD = 4
@dataclass
class CollectorIFCmdMsg:  # published by CentralPlanner
    cmd: CollectorIFCmd
@dataclass  
class CollectorIFAckMsg:  # published by CollectorIFNode
    cmd: CollectorIFCmd
    success: bool
    err_msg: str