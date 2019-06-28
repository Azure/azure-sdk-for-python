# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------

from abc import ABC, abstractmethod


class AbstractEventProcessor(ABC):
    """
    Abstract that must be extended by event processor classes.
    """
    def __init__(self, params=None):
        pass

    @abstractmethod
    async def open_async(self, context):
        """
        Called by processor host to initialize the event processor.

        :param context: Information about the partition
        :type context: ~azure.eventprocessorhost.partition_context.PartitionContext
        """

    @abstractmethod
    async def close_async(self, context, reason):
        """
        Called by processor host to indicate that the event processor is being stopped.

        :param context: Information about the partition
        :type context: ~azure.eventprocessorhost.partition_context.PartitionContext
        :param reason: The reason for closing.
        :type reason: str
        """

    @abstractmethod
    async def process_events_async(self, context, messages):
        """
        Called by the processor host when a batch of events has arrived.
        This is where the real work of the event processor is done.

        :param context: Information about the partition
        :type context: ~azure.eventprocessorhost.partition_context.PartitionContext
        :param messages: The events to be processed.
        :type messages: list[~azure.eventhub.common.EventData]
        """

    @abstractmethod
    async def process_error_async(self, context, error):
        """
        Called when the underlying client experiences an error while receiving.
        EventProcessorHost will take care of recovering from the error and
        continuing to pump messages.

        :param context: Information about the partition
        :type context: ~azure.eventprocessorhost.partition_context.PartitionContext
        :param error: The error that occured.
        """
