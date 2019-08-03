# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------

from typing import List
from abc import ABC, abstractmethod
from enum import Enum
from .checkpoint_manager import CheckpointManager

from azure.eventhub import EventData


class CloseReason(Enum):
    SHUTDOWN = 0  # user call EventProcessor.stop()
    OWNERSHIP_LOST = 1  # lose the ownership of a partition.
    EVENTHUB_EXCEPTION = 2  # Exception happens during receiving events


class PartitionProcessor(ABC):
    def __init__(self, checkpoint_manager: CheckpointManager):
        self._checkpoint_manager = checkpoint_manager

    async def close(self, reason):
        """Called when EventProcessor stops processing this PartitionProcessor.

        There are different reasons to trigger the PartitionProcessor to close.
        Refer to enum class CloseReason

        """
        pass

    @abstractmethod
    async def process_events(self, events: List[EventData]):
        """Called when a batch of events have been received.

        """
        pass

    async def process_error(self, error):
        """Called when an error happens

        """
        pass
