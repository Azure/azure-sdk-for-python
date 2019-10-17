# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import logging
import asyncio
from typing import Any, Union, TYPE_CHECKING
from azure.eventhub.common import EventPosition,\
    EventHubSharedKeyCredential, EventHubSASTokenCredential

from .eventprocessor.event_processor import EventProcessor

from .client_async import EventHubClient

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential  # type: ignore

log = logging.getLogger(__name__)


class EventHubConsumerClient(EventHubClient):

    def __init__(self, host, event_hub_path, credential, **kwargs):
        # type:(str, str, Union[EventHubSharedKeyCredential, EventHubSASTokenCredential, TokenCredential], Any) -> None
        super(EventHubConsumerClient, self).__init__(host=host, event_hub_path=event_hub_path, credential=credential, **kwargs)
        self._partition_manager = kwargs.get("partition_manager")
        self._event_processors = []

    async def receive(
            self, event_handler, consumer_group, *, partition_id=None,
            error_handler=None, partition_initialize_handler=None, partition_close_handler=None,
            initial_event_position=None, polling_interval=None):
        """Receive events from partition(s) optionally with load balancing and checkpointing.

        """
        event_processor = EventProcessor(
            self, consumer_group, event_handler,
            partition_id=partition_id,
            partition_manager=self._partition_manager,
            error_handler=error_handler,
            partition_initialize_handler=partition_initialize_handler,
            partition_close_handler=partition_close_handler,
            initial_event_position=initial_event_position or EventPosition("-1"),
            polling_interval=polling_interval or 10
        )
        self._event_processors.append(event_processor)
        await event_processor.start()

    async def update_checkpoint(self, event):
        self._partition_manager.update_checkpoint(event)

    async def close(self):
        # type: () -> None
        """Stop retrieving events from event hubs and close the underlying AMQP connection.

        """
        for ep in self._event_processors:
            await ep.stop()
        await super().close()
