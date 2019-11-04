# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import logging
from typing import Any, Union, TYPE_CHECKING, Callable, Dict, List, Tuple
from azure.eventhub import EventPosition, EventData, EventHubSharedKeyCredential, EventHubSASTokenCredential
from .eventprocessor.event_processor import EventProcessor, CloseReason
from .eventprocessor.partition_context import PartitionContext
from .client_async import EventHubClient
if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential  # type: ignore

log = logging.getLogger(__name__)


class EventHubConsumerClient(EventHubClient):
    """ The EventHubProducerClient class defines a high level interface for
    receiving events from the Azure Event Hubs service.

    The main goal of `EventHubConsumerClient` is to receive events from all partitions of an EventHub with
    load balancing and checkpointing.

    When multiple `EventHubConsumerClient` works with one process, multiple processes, or multiple computer machines
    and if they use the same repository as the load balancing and checkpointing store, they will balance automatically.
    To enable the load balancing and / or checkpointing, partition_manager must be set when creating the
    `EventHubConsumerClient`.

    An `EventHubConsumerClient` can also receive from a specific partition when you call its method `receive()`
    and specify the partition_id.
    Load balancing won't work in single-partition mode. But users can still save checkpoint if the partition_manager
    is set.

    :param str host: The hostname of the Event Hub.
    :param str event_hub_path: The path of the specific Event Hub to connect the client to.
    :param credential: The credential object used for authentication which implements particular interface
     of getting tokens.
    :type credential: ~azure.eventhub.EventHubSharedKeyCredential,~azure.eventhub.EventHubSASTokenCredential,
     Credential objects in azure-identity and objects that implement `get_token(self, *scopes)` method
    :keyword bool logging_enable: Whether to output network trace logs to the logger. Default is `False`.
    :keyword float auth_timeout: The time in seconds to wait for a token to be authorized by the service.
     The default value is 60 seconds. If set to 0, no timeout will be enforced from the client.
    :keyword str user_agent: The user agent that needs to be appended to the built in user agent string.
    :keyword int retry_total: The total number of attempts to redo the failed operation when an error happened. Default
     value is 3.
    :keyword transport_type: The type of transport protocol that will be used for communicating with
     the Event Hubs service. Default is ~azure.eventhub.TransportType.Amqp.
    :paramtype transport_type: ~azure.eventhub.TransportType
    :keyword dict http_proxy: HTTP proxy settings. This must be a dictionary with the following
     keys: 'proxy_hostname' (str value) and 'proxy_port' (int value).
     Additionally the following keys may also be present: 'username', 'password'.
    :keyword partition_manager: stores the load balancing data and checkpoint data when receiving events
     if partition_manager is specified. If it's None, this EventHubConsumerClient instance will receive
     events without load balancing and checkpoint.
    :paramtype partition_manager: Implementation classes of ~azure.eventhub.aio.PartitionManager
    :keyword float load_balancing_interval: When load balancing kicks in, this is the interval in seconds
     between two load balancing. Default is 10.

    .. admonition:: Example:

        .. literalinclude:: ../samples/async_samples/sample_code_eventhub_async.py
            :start-after: [START create_eventhub_consumer_client_async]
            :end-before: [END create_eventhub_consumer_client_async]
            :language: python
            :dedent: 4
            :caption: Create a new instance of the EventHubConsumerClient.
    """

    def __init__(self, host, event_hub_path, credential, **kwargs) -> None:
        # type:(str, str, Union[EventHubSharedKeyCredential, EventHubSASTokenCredential, TokenCredential], Any) -> None
        self._partition_manager = kwargs.pop("partition_manager") if "partition_manager" in kwargs else None
        self._load_balancing_interval = kwargs.pop("load_balancing_interval") \
            if "load_balancing_interval" in kwargs else 10
        super(EventHubConsumerClient, self).__init__(
            host=host, event_hub_path=event_hub_path, credential=credential,
            network_tracing=kwargs.get("logging_enable"), **kwargs)
        self._event_processors = dict()  # type: Dict[Tuple[str, str], EventProcessor]
        self._closed = False

    async def receive(
            self, on_events: Callable[[PartitionContext, List[EventData]], None], consumer_group: str,
            *,
            partition_id: str = None,
            owner_level: int = None,
            prefetch: int = 300,
            track_last_enqueued_event_properties: bool = False,
            initial_event_position: Union[EventPosition, Dict[str, EventPosition]] = None,
            on_error: Callable[[PartitionContext, Exception], None] = None,
            on_partition_initialize: Callable[[PartitionContext], None] = None,
            on_partition_close: Callable[[PartitionContext, CloseReason], None] = None
    ) -> None:
        """Receive events from partition(s) optionally with load balancing and checkpointing.

        :param on_events: The callback function for handling received events. The callback takes two
         parameters: partition_context` which contains partition information and `events` which are the received events.
         Please define the callback like `on_event(partition_context, events)`.
         For detailed partition context information, please refer to ~azure.eventhub.PartitionContext.
        :type on_events: Callable[PartitionContext, List[EventData]]
        :param consumer_group: Receive events from the event hub for this consumer group
        :param partition_id: Receive from this partition only if it's not None. Receive from all partition otherwise.
        :param owner_level: The priority of the exclusive consumer. An exclusive
         consumer will be created if owner_level is set. Higher owner_level has higher exclusive priority.
        :param prefetch: The number of events to prefetch from the service
         for processing. Default is 300.
        :param track_last_enqueued_event_properties: Indicates whether or not the consumer should request information
         on the last enqueued event on its associated partition, and track that information as events are received.
         When information about the partition's last enqueued event is being tracked, each event received from the
         Event Hubs service will carry metadata about the partition. This results in a small amount of additional
         network bandwidth consumption that is generally a favorable trade-off when considered against periodically
         making requests for partition properties using the Event Hub client.
         It is set to `False` by default.
        :param initial_event_position: Start receiving from this initial_event_position
         if there isn't checkpoint data for a partition. Use the checkpoint data if there it's available. This can be a
         a dict with partition id as the key and position as the value for individual partitions, or a single
         EventPosition instance for all partitions.
        :type initial_event_position: ~azure.eventhub.EventPosition, dict[str,~azure.eventhub.EventPosition]
        :keyword on_error: The callback function which would be called when there is an error met during the receiving
         time. The callback takes two parameters: `partition_context` which contains partition information
         and `error` being the exception. Please define the callback like `on_error(partition_context, error)`.
        :paramtype on_error: Callable[[PartitionContext, Exception]]
        :keyword on_partition_initialize: The callback function which will be called after a consumer for certain
         partition finishes initialization. The callback takes two parameter: `partition_context` which contains
         the partition information. Please define the callback like`on_partition_initialize(partition_context)`.
        :paramtype on_partition_initialize: Callable[[PartitionContext]]
        :keyword on_partition_close: The callback function which will be called after a consumer for certain
         partition is closed. The callback takes two parameters: `partition_context` which contains partition
         information and `reason` for the close. Please define the callback like `on_error(partition_context, reason)`.
         Please refer to `azure.eventhub.CloseReason` for different closing reason.
        :paramtype on_partition_close: Callable[[PartitionContext, CloseReason]]
        :rtype: None

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_code_eventhub_async.py
                :start-after: [START eventhub_consumer_client_receive_async]
                :end-before: [END eventhub_consumer_client_receive_async]
                :language: python
                :dedent: 4
                :caption: Receive events from the EventHub.
        """
        async with self._lock:
            error = None
            if (consumer_group, '-1') in self._event_processors:
                error = ValueError("This consumer client is already receiving events from all partitions for"
                                   " consumer group {}. ".format(consumer_group))
            elif partition_id is None and any(x[0] == consumer_group for x in self._event_processors):
                error = ValueError("This consumer client is already receiving events for consumer group {}. "
                                   .format(consumer_group))
            elif (consumer_group, partition_id) in self._event_processors:
                error = ValueError("This consumer is already receiving events from partition {} for consumer group {}. "
                                   .format(partition_id, consumer_group))
            if error:
                log.warning(error)
                raise error

            event_processor = EventProcessor(
                self, consumer_group, on_events,
                partition_id=partition_id,
                partition_manager=self._partition_manager,
                error_handler=on_error,
                partition_initialize_handler=on_partition_initialize,
                partition_close_handler=on_partition_close,
                initial_event_position=initial_event_position or EventPosition("-1"),
                polling_interval=self._load_balancing_interval,
                owner_level=owner_level,
                prefetch=prefetch,
                track_last_enqueued_event_properties=track_last_enqueued_event_properties,
            )
            if partition_id:
                self._event_processors[(consumer_group, partition_id)] = event_processor
            else:
                self._event_processors[(consumer_group, "-1")] = event_processor
        try:
            await event_processor.start()
        finally:
            await event_processor.stop()
            async with self._lock:
                if partition_id and (consumer_group, partition_id) in self._event_processors:
                    del self._event_processors[(consumer_group, partition_id)]
                elif partition_id is None and (consumer_group, '-1') in self._event_processors:
                    del self._event_processors[(consumer_group, "-1")]

    async def close(self):
        # type: () -> None
        """Stop retrieving events from event hubs and close the underlying AMQP connection and links.

        :rtype: None

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_code_eventhub_async.py
                :start-after: [START eventhub_consumer_client_close_async]
                :end-before: [END eventhub_consumer_client_close_async]
                :language: python
                :dedent: 4
                :caption: Close down the client.

        """
        async with self._lock:
            for _ in range(len(self._event_processors)):
                _, ep = self._event_processors.popitem()
                await ep.stop()
            await super().close()
