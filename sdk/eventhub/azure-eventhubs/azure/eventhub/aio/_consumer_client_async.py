# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import logging
from typing import Any, Union, TYPE_CHECKING
from .._common import EventPosition,\
    EventHubSharedKeyCredential, EventHubSASTokenCredential
from ._eventprocessor.event_processor import EventProcessor
from ._client_async import EventHubClient
if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential  # type: ignore

log = logging.getLogger(__name__)


class EventHubConsumerClient(EventHubClient):
    """Represents an AMQP connection to an EventHub.

    """

    def __init__(self, host, event_hub_path, credential, **kwargs):
        # type:(str, str, Union[EventHubSharedKeyCredential, EventHubSASTokenCredential, TokenCredential], Any) -> None
        """



        :param prefetch: The message prefetch count of the consumer. Default is 300.
        :type prefetch: int
        """

        super(EventHubConsumerClient, self).__init__(host=host, event_hub_path=event_hub_path, credential=credential, **kwargs)
        self._partition_manager = kwargs.get("partition_manager")
        self._event_processors = dict()
        self._closed = False

    async def receive(
            self, event_handler, consumer_group, *, partition_id=None,
            owner_level=None, prefetch=None, track_last_enqueued_event_properties=False,
            initial_event_position=None, load_balancing_interval=10,
            error_handler=None, partition_initialize_handler=None, partition_close_handler=None,
    ):
        """Receive events from partition(s) optionally with load balancing and checkpointing.

        :param event_handler: A function
        :param consumer_group:
        :param partition_id:
        :param owner_level:
        :param prefetch:
        :param track_last_enqueued_event_properties:
        :param initial_event_position:
        :param load_balancing_interval:
        :param error_handler:
        :param partition_initialize_handler:
        :param partition_close_handler:
        :return:
        """
        async with self._lock:
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
            await event_processor.start()
        finally:
            async with self._lock:
                await event_processor.stop()
                if partition_id and partition_id in self._event_processors:
                    del self._event_processors[partition_id]
                elif 'all' in self._event_processors:
                    del self._event_processors['all']

    async def get_last_enqueued_event_properties(self, partition_id: str):
        """The latest enqueued event information of a partition.
        This property will be updated each time an event is received when
        the client is created with `track_last_enqueued_event_properties` being `True`.
        The dict includes following information of the partition:

            - `sequence_number`
            - `offset`
            - `enqueued_time`
            - `retrieval_time`

        :rtype: dict or None
        :raises: ValueError
        """
        if partition_id in self._event_processors or 'all' in self._event_processors:
            return self._event_processors[partition_id].get_last_enqueued_event_properties(partition_id)
        else:
            raise ValueError("You're not receiving events from partition {}".format(partition_id))

    async def close(self):
        # type: () -> None
        """Stop retrieving events from event hubs and close the underlying AMQP connection and links.

        """
        async with self._lock:
            for _ in range(len(self._event_processors)):
                _, ep = self._event_processors.popitem()
                await ep.stop()
            await super().close()
