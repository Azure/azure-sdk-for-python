# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------

import uuid
import asyncio
from azure.eventprocessorhost.partition_manager import PartitionManager


class EventProcessorHost:
    """
    Represents a host for processing Event Hubs event data at scale.
    Takes in event hub a event processor class definition a eh_config object
    As well as a storage manager and an optional event_processor params (ep_params)
    """

    def __init__(self, event_processor, eh_config, storage_manager, ep_params=None, eph_options=None, loop=None):
        """
        Initialize EventProcessorHost.
        :param event_processor: The event processing handler.
        :type event_processor: ~azure.eventprocessorhost.AbstractEventProcessor
        :param eh_config: The EPH connection configuration.
        :type eh_config: ~azure.eventprocessorhost.EventHubConfig
        :param storage_manager: The Azure storage manager for persisting lease and
         checkpoint information.
        :type storage_manager: ~azure.eventprocessorhost.AzureStorageCheckpointLeaseManager
        :param ep_params: Optional arbitrary parameters to be passed into the event_processor
         on initialization.
        :type ep_params: list
        :param eph_options: EPH configuration options.
        :type eph_options: ~azure.eventprocessorhost.EPHOptions
        :param loop: An eventloop. If not provided the default asyncio event loop will be used.
        """
        self.event_processor = event_processor
        self.event_processor_params = ep_params
        self.eh_config = eh_config
        self.guid = str(uuid.uuid4())
        self.host_name = "host" + str(self.guid)
        self.loop = loop or asyncio.get_event_loop()
        self.eph_options = eph_options or EPHOptions()
        self.partition_manager = PartitionManager(self)
        self.storage_manager = storage_manager
        if self.storage_manager:
            self.storage_manager.initialize(self)

    async def open_async(self):
        """
        Starts the host
        """
        if not self.loop:
            self.loop = asyncio.get_event_loop()
        await self.partition_manager.start_async()

    async def close_async(self):
        """
        Stops the host
        """
        await self.partition_manager.stop_async()
        
class EPHOptions:
    """
    Class that contains default and overidable EPH option
    """

    def __init__(self):
        self.max_batch_size = 10
        self.prefetch_count = 300
        self.receive_timeout = 60
        self.release_pump_on_timeout = False
        self.initial_offset_provider = "-1"
        self.debug_trace = False
