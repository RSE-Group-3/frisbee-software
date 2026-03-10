from dataclasses import dataclass
from enum import IntEnum

class LauncherCmd(IntEnum):
    RESET = 0
    LAUNCH = 1
class LauncherAck(IntEnum):
    STOPPED = -1
    RESET_SUCCESS = 0
    LAUNCH_SUCCESS = 1

class CollectorCmd(IntEnum):
    RESET = 0
    COLLECT = 1
class CollectorAck(IntEnum):
    STOPPED = -1
    RESET_SUCCESS = 0
    COLLECT_SUCCESS = 1
