# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import logging
from typing import Any, Union, TYPE_CHECKING
from ._common import EventPosition,\
    EventHubSharedKeyCredential, EventHubSASTokenCredential
from ._eventprocessor.event_processor import EventProcessor
from ._client import EventHubClient
if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential  # type: ignore

log = logging.getLogger(__name__)


class EventHubConsumerClient(EventHubClient):
    """Represents an AMQP connection to an EventHub.

    """

    def __init__(self, host, event_hub_path, credential, **kwargs):
        # type:(str, str, Union[EventHubSharedKeyCredential, EventHubSASTokenCredential, TokenCredential], Any) -> None
        super(EventHubConsumerClient, self).__init__(host=host, event_hub_path=event_hub_path, credential=credential, **kwargs)
        self._partition_manager = kwargs.get("partition_manager")
        self._event_processors = dict()
        self._closed = False

    def receive(
            self, event_handler, consumer_group, *, partition_id=None,
            owner_level=None, prefetch=None, track_last_enqueued_event_properties=False,
            initial_event_position=None, load_balancing_interval=10,
            error_handler=None, partition_initialize_handler=None, partition_close_handler=None,
    ):
        """Receive events from partition(s) optionally with load balancing and checkpointing.

        """
        with self._lock:
            if 'all' in self._event_processors:
                raise ValueError("This consumer client is already receiving events from all partitions. "
                                 "Shouldn't receive from any other partitions again")
            elif partition_id is None and self._event_processors:
                raise ValueError("This consumer client is already receiving events. "
                                 "Shouldn't receive from all partitions again")
            elif partition_id in self._event_processors:
                raise ValueError("This consumer is already receiving events from partition {}. "
                                 "Shouldn't receive from it again.".format(partition_id))

            event_processor = EventProcessor(
                self, consumer_group, event_handler,
                partition_id=partition_id,
                partition_manager=self._partition_manager,
                error_handler=error_handler,
                partition_initialize_handler=partition_initialize_handler,
                partition_close_handler=partition_close_handler,
                initial_event_position=initial_event_position or EventPosition("-1"),
                polling_interval=load_balancing_interval,
                owner_level=owner_level,
                prefetch=prefetch,
                track_last_enqueued_event_properties=track_last_enqueued_event_properties,
            )
            if partition_id:
                self._event_processors[partition_id] = event_processor
            else:
                self._event_processors["all"] = event_processor
        try:
            event_processor.start()
        finally:
            with self._lock:
                if event_processor._running:
                    event_processor.stop()
                if partition_id and partition_id in self._event_processors:
                    del self._event_processors[partition_id]
                elif 'all' in self._event_processors:
                    del self._event_processors['all']

    def get_last_enqueued_event_properties(self, partition_id: str):
        if partition_id in self._event_processors or 'all' in self._event_processors:
            return self._event_processors[partition_id].get_last_enqueued_event_properties(partition_id)
        else:
            raise ValueError("You're not receiving events from partition {}".format(partition_id))

    def update_checkpoint(self, event):
        self._partition_manager.update_checkpoint(event)

    def close(self):
        # type: () -> None
        """Stop retrieving events from event hubs and close the underlying AMQP connection.

        """
        with self._lock:
            for _ in range(len(self._event_processors)):
                _, ep = self._event_processors.popitem()
                ep.stop()
            super().close()
