# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import logging
import threading

from typing import Any, Union, TYPE_CHECKING, Iterable, List
from uamqp import constants  # type:ignore
from .client import EventHubClient
from .producer import EventHubProducer
from .common import EventData, \
    EventHubSharedKeyCredential, EventHubSASTokenCredential, EventDataBatch

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential  # type: ignore

log = logging.getLogger(__name__)


class EventHubProducerClient(EventHubClient):
    """
    The EventHubProducerClient class defines a high level interface for
    sending events to the Azure Event Hubs service.

    Example:
        .. literalinclude:: ../examples/test_examples_eventhub.py
            :start-after: [START create_eventhub_producer_client_sync]
            :end-before: [END create_eventhub_producer_client_sync]
            :language: python
            :dedent: 4
            :caption: Create a new instance of the EventHubProducerClient.

    """

    def __init__(self, host, event_hub_path, credential, **kwargs):
        # type:(str, str, Union[EventHubSharedKeyCredential, EventHubSASTokenCredential, TokenCredential], Any) -> None
        super(EventHubProducerClient, self).__init__(
            host=host, event_hub_path=event_hub_path, credential=credential, **kwargs)
        self._producers = []  # type: List[EventHubProducer]
        self._client_lock = threading.Lock()
        self._producers_locks = []  # type: List[threading.Lock]
        self._max_message_size_on_link = 0

    def _init_locks_for_producers(self):
        if not self._producers:
            with self._client_lock:
                if not self._producers:
                    num_of_producers = len(self.get_partition_ids()) + 1
                    self._producers = [None] * num_of_producers
                    for _ in range(num_of_producers):
                        self._producers_locks.append(threading.Lock())

    def send(self, event_data, **kwargs):
        # type: (Union[EventData, EventDataBatch, Iterable[EventData]], Any) -> None
        """
        Sends an event data and blocks until acknowledgement is received or operation times out.

        :param event_data:
        :param partition_key:
        :param partition_id:
        :param timeout:
        :return:

        Example:
            .. literalinclude:: ../examples/test_examples_eventhub.py
                :start-after: [START eventhub_producer_client_send_sync]
                :end-before: [END eventhub_producer_client_send_sync]
                :language: python
                :dedent: 4
                :caption: Sends an event data and blocks until acknowledgement is received or operation times out.

        """
        partition_id = kwargs.pop("partition_id", None)

        self._init_locks_for_producers()

        producer_index = int(partition_id) if partition_id is not None else -1
        if self._producers[producer_index] is None or\
                self._producers[producer_index]._closed:  # pylint:disable=protected-access
            with self._producers_locks[producer_index]:
                if self._producers[producer_index] is None:
                    self._producers[producer_index] = self._create_producer(partition_id=partition_id)
        with self._producers_locks[producer_index]:
            self._producers[producer_index].send(event_data, **kwargs)

    def create_batch(self, max_size=None):
        # type:(int) -> EventDataBatch
        """
        Create an EventDataBatch object with max size being max_size.
        The max_size should be no greater than the max allowed message size defined by the service side.

        :param max_size: The maximum size of bytes data that an EventDataBatch object can hold.
        :type max_size: int
        :return: an EventDataBatch instance
        :rtype: ~azure.eventhub.EventDataBatch

        Example:
            .. literalinclude:: ../examples/test_examples_eventhub.py
                :start-after: [START eventhub_producer_client_create_batch_sync]
                :end-before: [END eventhub_producer_client_create_batch_sync]
                :language: python
                :dedent: 4
                :caption: Create EventDataBatch object within limited size

        """
        # pylint: disable=protected-access
        if not self._max_message_size_on_link:
            self._init_locks_for_producers()
            with self._producers_locks[-1]:
                if self._producers[-1] is None:
                    self._producers[-1] = self._create_producer(partition_id=None)
                    self._producers[-1]._open_with_retry()  # pylint: disable=protected-access
            with self._client_lock:
                self._max_message_size_on_link =\
                    self._producers[-1]._handler.message_handler._link.peer_max_message_size \
                    or constants.MAX_MESSAGE_LENGTH_BYTES

        if max_size and max_size > self._max_message_size_on_link:
            raise ValueError('Max message size: {} is too large, acceptable max batch size is: {} bytes.'
                             .format(max_size, self._max_message_size_on_link))

        return EventDataBatch(max_size=(max_size or self._max_message_size_on_link))

    def close(self):
        # type: () -> None
        """
        Close down the handler. If the handler has already closed,
        this will be a no op.

        Example:
            .. literalinclude:: ../examples/test_examples_eventhub.py
                :start-after: [START eventhub_producer_client_close_sync]
                :end-before: [END eventhub_producer_client_close_sync]
                :language: python
                :dedent: 4
                :caption: Close down the handler.

        """
        if self._producers:
            for p in self._producers:
                if p:
                    p.close()
        self._conn_manager.close_connection()
