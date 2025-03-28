# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from enum import IntEnum, auto, unique


@unique
class BatchStatus(IntEnum):
    NotStarted = 0
    Running = auto()

    # NOTE: DO NOT REORDER THESE ENUMS. The order is important for the is_terminated method
    #       and other logic in the code to work properly
    Completed = auto()
    Canceled = auto()
    Failed = auto()

    @staticmethod
    def is_terminated(status: "BatchStatus") -> bool:
        return status >= BatchStatus.Completed

    @staticmethod
    def is_failed(status: "BatchStatus") -> bool:
        return status == BatchStatus.Failed or status == BatchStatus.Canceled
