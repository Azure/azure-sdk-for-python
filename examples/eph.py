# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------

import logging
import asyncio
import sys
from eventprocessorhost.abstract_event_processor import AbstractEventProcessor
from eventprocessorhost.azure_storage_checkpoint_manager import AzureStorageCheckpointLeaseManager
from eventprocessorhost.eh_config import EventHubConfig
from eventprocessorhost.eph import EventProcessorHost

class EventProcessor(AbstractEventProcessor):
    """
    Example Implmentation of AbstractEventProcessor
    """
    def __init__(self, params=None):
        """
        Init Event processor
        """
        self._msg_counter = 0
    async def open_async(self, context):
        """
        Called by processor host to initialize the event processor.
        """
        logging.info("Connection established %s", context.partition_id)

    async def close_async(self, context, reason):
        """
        Called by processor host to indicate that the event processor is being stopped.
        (Params) Context:Information about the partition
        """
        logging.info("Connection closed (reason %s, id %s, offset %s, sq_number %s)", reason,
                     context.partition_id, context.offset, context.sequence_number)

    async def process_events_async(self, context, messages):
        """
        Called by the processor host when a batch of events has arrived.
        This is where the real work of the event processor is done.
        (Params) Context: Information about the partition, Messages: The events to be processed.
        """
        logging.info("Events processed %s %s", context.partition_id, messages)
        await context.checkpoint_async()

    async def process_error_async(self, context, error):
        """
        Called when the underlying client experiences an error while receiving.
        EventProcessorHost will take care of recovering from the error and
        continuing to pump messages,so no action is required from
        (Params) Context: Information about the partition, Error: The error that occured.
        """
        logging.error("Event Processor Error %s ", repr(error))


try:
    # Configure Logging
    logging.basicConfig(filename='eph.log', level=logging.INFO,
                        format='%(asctime)s:%(msecs)03d, \'%(message)s\' ',
                        datefmt='%Y-%m-%d:%H:%M:%S')
    logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

    # Storage Account Credentials
    STORAGE_ACCOUNT_NAME = "mystorageaccount"
    STORAGE_KEY = "sas encoded storage key"
    LEASE_CONTAINER_NAME = "leases"

    # Eventhub config and storage manager 
    EH_CONFIG = EventHubConfig('<mynamespace>', '<myeventhub>','<URL-encoded-SAS-policy>', 
                               '<URL-encoded-SAS-key>', consumer_group="$default")
    STORAGE_MANAGER = AzureStorageCheckpointLeaseManager(STORAGE_ACCOUNT_NAME, STORAGE_KEY,
                                                         LEASE_CONTAINER_NAME)
    #Event loop and host
    LOOP = asyncio.get_event_loop()
    HOST = EventProcessorHost(EventProcessor, EH_CONFIG, STORAGE_MANAGER,
                              ep_params=["param1","param2"], loop=LOOP)

    LOOP.run_until_complete(HOST.open_async())
    LOOP.run_until_complete(HOST.close_async())

finally:
    LOOP.stop()
