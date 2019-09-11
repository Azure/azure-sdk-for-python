# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------

from typing import List
from abc import ABC, abstractmethod
from enum import Enum
from azure.eventhub import EventData
from .partition_context import PartitionContext


class CloseReason(Enum):
    SHUTDOWN = 0  # user call EventProcessor.stop()
    OWNERSHIP_LOST = 1  # lose the ownership of a partition.
    EVENTHUB_EXCEPTION = 2  # Exception happens during receiving events
    PROCESS_EVENTS_ERROR = 3  # Exception happens during process_events


class PartitionProcessor(ABC):
    """
    PartitionProcessor processes events received from the Azure Event Hubs service. A single instance of a class
    implementing this abstract class will be created for every partition the associated
    ~azure.eventhub.aio.eventprocessor.EventProcessor owns.

    """

    async def initialize(self, partition_context: PartitionContext):
        """This method will be called when `EventProcessor` creates a `PartitionProcessor`.

        :param partition_context: The context information of this partition.
        :type partition_context: ~azure.eventhub.aio.eventprocessor.PartitionContext
        """

        # Please put the code for initialization of PartitionProcessor here.

    async def close(self, reason, partition_context: PartitionContext):
        """Called when EventProcessor stops processing this PartitionProcessor.

        There are different reasons to trigger the PartitionProcessor to close.
        Refer to enum class ~azure.eventhub.eventprocessor.CloseReason

        :param reason: Reason for closing the PartitionProcessor.
        :type reason: ~azure.eventhub.eventprocessor.CloseReason
        :param partition_context: The context information of this partition.
         Use its method update_checkpoint to save checkpoint to the data store.
        :type partition_context: ~azure.eventhub.aio.eventprocessor.PartitionContext

        """

        # Please put the code for closing PartitionProcessor here.

    @abstractmethod
    async def process_events(self, events: List[EventData], partition_context: PartitionContext):
        """Called when a batch of events have been received.

        :param events: Received events.
        :type events: list[~azure.eventhub.common.EventData]
        :param partition_context: The context information of this partition.
         Use its method update_checkpoint to save checkpoint to the data store.
        :type partition_context: ~azure.eventhub.aio.eventprocessor.PartitionContext

        """

        # Please put the code for processing events here.

    async def process_error(self, error, partition_context: PartitionContext):
        """Called when an error happens when receiving or processing events

        :param error: The error that happens.
        :type error: Exception
        :param partition_context: The context information of this partition.
         Use its method update_checkpoint to save checkpoint to the data store.
        :type partition_context: ~azure.eventhub.aio.eventprocessor.PartitionContext

        """

        # Please put the code for processing error here.
