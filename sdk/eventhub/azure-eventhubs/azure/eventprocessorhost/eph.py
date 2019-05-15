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
    Takes in an event hub, a event processor class definition, a config object,
    as well as a storage manager and optional event processor params (ep_params).
    """

    def __init__(self, event_processor, eh_config, storage_manager, ep_params=None, eph_options=None, loop=None):
        """
        Initialize EventProcessorHost.

        :param event_processor: The event processing handler.
        :type event_processor: ~azure.eventprocessorhost.abstract_event_processor.AbstractEventProcessor
        :param eh_config: The EPH connection configuration.
        :type eh_config: ~azure.eventprocessorhost.eh_config.EventHubConfig
        :param storage_manager: The Azure storage manager for persisting lease and
         checkpoint information.
        :type storage_manager:
         ~azure.eventprocessorhost.azure_storage_checkpoint_manager.AzureStorageCheckpointLeaseManager
        :param ep_params: Optional arbitrary parameters to be passed into the event_processor
         on initialization.
        :type ep_params: list
        :param eph_options: EPH configuration options.
        :type eph_options: ~azure.eventprocessorhost.eph.EPHOptions
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
        Starts the host.
        """
        if not self.loop:
            self.loop = asyncio.get_event_loop()
        await self.partition_manager.start_async()

    async def close_async(self):
        """
        Stops the host.
        """
        await self.partition_manager.stop_async()


class EPHOptions:
    """
    Class that contains default and overidable EPH option.

    :ivar max_batch_size: The maximum number of events retrieved for processing
     at a time. This value must be less than or equal to the prefetch count. The actual
     number of events returned for processing may be any number up to the maximum.
     The default value is 10.
    :vartype max_batch_size: int
    :ivar prefetch_count: The number of events to fetch from the service in advance of
     processing. The default value is 300.
    :vartype prefetch_count: int
    :ivar receive_timeout: The length of time a single partition receiver will wait in
     order to receive a batch of events. Default is 60 seconds.
    :vartype receive_timeout: int
    :ivar release_pump_on_timeout: Whether to shutdown an individual partition receiver if
     no events were received in the specified timeout. Shutting down the pump will release
     the lease to allow it to be picked up by another host. Default is False.
    :vartype release_pump_on_timeout: bool
    :ivar initial_offset_provider: The initial event offset to receive from if no persisted
     offset is found. Default is "-1" (i.e. from the first event available).
    :vartype initial_offset_provider: str
    :ivar debug_trace: Whether to emit the network traffic in the logs. In order to view
     these events the logger must be configured to track "uamqp". Default is False.
    :vartype debug_trace: bool
    :ivar http_proxy: HTTP proxy configuration. This should be a dictionary with
     the following keys present: 'proxy_hostname' and 'proxy_port'. Additional optional
     keys are 'username' and 'password'.
    :vartype http_proxy: dict
    :ivar keep_alive_interval: The time in seconds between asynchronously pinging a receiver
     connection to keep it alive during inactivity. Default is None - i.e. no connection pinging.
    :vartype keep_alive_interval: int
    :ivar auto_reconnect_on_error: Whether to automatically attempt to reconnect a receiver
     connection if it is detach from the service with a retryable error. Default is True.
    :vartype auto_reconnect_on_error: bool
    """

    def __init__(self):
        self.max_batch_size = 10
        self.prefetch_count = 300
        self.receive_timeout = 60
        self.release_pump_on_timeout = False
        self.initial_offset_provider = "-1"
        self.debug_trace = False
        self.http_proxy = None
        self.keep_alive_interval = None
        self.auto_reconnect_on_error = True
