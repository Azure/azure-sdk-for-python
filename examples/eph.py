# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------

import logging
import asyncio
import sys
import os

from azure.eventprocessorhost import (
    AbstractEventProcessor,
    AzureStorageCheckpointLeaseManager,
    EventHubConfig,
    EventProcessorHost,
    EPHOptions)

import examples
logger = examples.get_logger(logging.DEBUG)

class ExEventProcessorHost(EventProcessorHost):
    async def open_async(self):
        _loop = asyncio.get_event_loop()
        _loop.create_task(self.kill_me())
        await super().open_async()

    async def kill_me(self):
        await asyncio.sleep(30)
        self.loop.create_task(self.close_async())


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
        (Params) Context:Information about the partition
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
        (Params) Context: Information about the partition, Messages: The events to be processed.
        """
        logger.info("Events processed {}".format(context.sequence_number))
        await context.checkpoint_async()

    async def process_error_async(self, context, error):
        """
        Called when the underlying client experiences an error while receiving.
        EventProcessorHost will take care of recovering from the error and
        continuing to pump messages,so no action is required from
        (Params) Context: Information about the partition, Error: The error that occured.
        """
        logger.error("Event Processor Error {}".format(repr(error)))


try:
    LOOP = asyncio.get_event_loop()

    # Storage Account Credentials
    STORAGE_ACCOUNT_NAME = os.environ.get('AZURE_STORAGE_ACCOUNT')
    STORAGE_KEY = os.environ.get('AZURE_STORAGE_ACCESS_KEY')
    LEASE_CONTAINER_NAME = "leases"

    NAMESPACE = os.environ.get('EVENT_HUB_NAMESPACE')
    EVENTHUB = os.environ.get('EVENT_HUB_NAME')
    USER = os.environ.get('EVENT_HUB_SAS_POLICY')
    KEY = os.environ.get('EVENT_HUB_SAS_KEY')

    # Eventhub config and storage manager 
    EH_CONFIG = EventHubConfig(NAMESPACE, EVENTHUB, USER, KEY, consumer_group="$default")
    EH_OPTIONS = EPHOptions()
    EH_OPTIONS.release_pump_on_timeout = True
    EH_OPTIONS.debug_trace = False
    STORAGE_MANAGER = AzureStorageCheckpointLeaseManager(STORAGE_ACCOUNT_NAME, STORAGE_KEY,
                                                         LEASE_CONTAINER_NAME)
    #Event loop and host
    HOST = EventProcessorHost(
        EventProcessor,
        EH_CONFIG,
        STORAGE_MANAGER,
        ep_params=["param1","param2"],
        eph_options=EH_OPTIONS,
        loop=LOOP)

    # HOST = exEventProcessorHost(EventProcessor, EH_CONFIG, STORAGE_MANAGER,
    #                             ep_params=["param1", "param2"], loop=LOOP)

    host = EventProcessorHost(EventProcessor, EH_CONFIG, STORAGE_MANAGER,
                              ep_params=["param1", "param2"], loop=loop)
    loop.create_task(host.open_async())
    while any([True if not task.done() else False for task in asyncio.Task.all_tasks()]):
        loop.run_until_complete(asyncio.sleep(1))
    loop.run_until_complete(host.close_async())

finally:
    loop.stop()
