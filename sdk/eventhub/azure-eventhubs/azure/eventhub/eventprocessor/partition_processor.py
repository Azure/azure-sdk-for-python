# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------

from typing import List
from abc import ABC, abstractmethod
from .checkpoint_manager import CheckpointManager

from azure.eventhub import EventData


class PartitionProcessor(ABC):
    def __init__(self, eventhub_name, consumer_group_name, partition_id, checkpoint_manager: CheckpointManager):
        self._partition_id = partition_id
        self._eventhub_name = eventhub_name
        self._consumer_group_name = consumer_group_name
        self._checkpoint_manager = checkpoint_manager

    async def close(self, reason):
        """Called when EventProcessor stops processing this PartitionProcessor.

        There are four different reasons to trigger the PartitionProcessor to close.
        Refer to enum class CloseReason of close_reason.py

        """
        pass

    @abstractmethod
    async def process_events(self, events: List[EventData]):
        """Called when a batch of events have been received.

        """
        pass
