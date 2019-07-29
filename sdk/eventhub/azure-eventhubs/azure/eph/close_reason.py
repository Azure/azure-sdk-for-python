from enum import Enum


class CloseReason(Enum):
    SHUTDOWN = 0
    LEASE_LOST = 1
    EXCEPTION = 2

