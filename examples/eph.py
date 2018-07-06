# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------

import logging
import asyncio
import sys
import os
import signal
import functools

from azure.eventprocessorhost import (
    AbstractEventProcessor,
    AzureStorageCheckpointLeaseManager,
    EventHubConfig,
    EventProcessorHost,
    EPHOptions)

import examples
logger = examples.get_logger(logging.INFO)


class EventProcessor(AbstractEventProcessor):
    """
    Example Implmentation of AbstractEventProcessor
    """

    def __init__(self, params=None):
        """
        Init Event processor
        """
        super().__init__(params)
        self._msg_counter = 0

    async def open_async(self, context):
        """
        Called by processor host to initialize the event processor.
        """
        logger.info("Connection established {}".format(context.partition_id))

    async def close_async(self, context, reason):
        """
        Called by processor host to indicate that the event processor is being stopped.
        :param context: Information about the partition
        :type context: ~azure.eventprocessorhost.PartitionContext
        """
        logger.info("Connection closed (reason {}, id {}, offset {}, sq_number {})".format(
            reason,
            context.partition_id,
            context.offset,
            context.sequence_number))

    async def process_events_async(self, context, messages):
        """
        Called by the processor host when a batch of events has arrived.
        This is where the real work of the event processor is done.
        :param context: Information about the partition
        :type context: ~azure.eventprocessorhost.PartitionContext
        :param messages: The events to be processed.
        :type messages: list[~azure.eventhub.common.EventData]
        """
        logger.info("Events processed {}".format(context.sequence_number))
        await context.checkpoint_async()

    async def process_error_async(self, context, error):
        """
        Called when the underlying client experiences an error while receiving.
        EventProcessorHost will take care of recovering from the error and
        continuing to pump messages,so no action is required from
        :param context: Information about the partition
        :type context: ~azure.eventprocessorhost.PartitionContext
        :param error: The error that occured.
        """
        logger.error("Event Processor Error {!r}".format(error))


async def wait_and_close(host):
    """
    Run EventProcessorHost for 2 minutes then shutdown.
    """
    await asyncio.sleep(60)
    await host.close_async()


try:
    loop = asyncio.get_event_loop()

    # Storage Account Credentials
    STORAGE_ACCOUNT_NAME = os.environ.get('AZURE_STORAGE_ACCOUNT')
    STORAGE_KEY = os.environ.get('AZURE_STORAGE_ACCESS_KEY')
    LEASE_CONTAINER_NAME = "leases"

    NAMESPACE = os.environ.get('EVENT_HUB_NAMESPACE')
    EVENTHUB = os.environ.get('EVENT_HUB_NAME')
    USER = os.environ.get('EVENT_HUB_SAS_POLICY')
    KEY = os.environ.get('EVENT_HUB_SAS_KEY')

    # Eventhub config and storage manager 
    eh_config = EventHubConfig(NAMESPACE, EVENTHUB, USER, KEY, consumer_group="$default")
    eh_options = EPHOptions()
    eh_options.release_pump_on_timeout = True
    eh_options.debug_trace = False
    storage_manager = AzureStorageCheckpointLeaseManager(
        STORAGE_ACCOUNT_NAME, STORAGE_KEY, LEASE_CONTAINER_NAME)

    # Event loop and host
    host = EventProcessorHost(
        EventProcessor,
        eh_config,
        storage_manager,
        ep_params=["param1","param2"],
        eph_options=eh_options,
        loop=loop)

    tasks = asyncio.gather(
        host.open_async(),
        wait_and_close(host))
    loop.run_until_complete(tasks)

except KeyboardInterrupt:
    # Canceling pending tasks and stopping the loop
    for task in asyncio.Task.all_tasks():
        task.cancel()
    loop.run_forever()
    tasks.exception()

finally:
    loop.stop()
