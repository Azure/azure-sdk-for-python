# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import logging
import threading

from typing import Any, Union, TYPE_CHECKING, Iterable, List
from ._client import EventHubClient
from ._producer import EventHubProducer
from ._common import EventData, \
    EventHubSharedKeyCredential, EventHubSASTokenCredential, EventDataBatch

from uamqp import constants

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
        self._producers = None  # type: List[EventHubProducer]
        self._producers_lock = threading.Lock()
        self._producers_locks = None
        self._max_message_size_on_link = constants.MAX_MESSAGE_LENGTH_BYTES

    def send(self, event_data: Union[EventData, EventDataBatch, Iterable[EventData]],
            *, partition_key: Union[str, bytes] = None, partition_id: str = None, timeout: float = None):
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

        if self._producers is None:
            with self._producers_lock:
                if self._producers is None:
                    num_of_producers = len(self.get_partition_ids()) + 1
                    self._producers = [None] * num_of_producers
                    self._producers_locks = [threading.Lock()] * num_of_producers

        producer_index = int(partition_id) if partition_id is not None else -1
        if self._producers[producer_index] is None or self._producers[producer_index]._closed:  # pylint:disable=protected-access
            with self._producers_locks[producer_index]:
                if self._producers[producer_index] is None:
                    self._producers[producer_index] = self._create_producer(partition_id=partition_id)

        self._producers[producer_index].send(event_data, partition_key=partition_key, timeout=timeout)

    def create_batch(self, max_size=None, partition_key=None):
        """
        Create an EventDataBatch object with max size being max_size.
        The max_size should be no greater than the max allowed message size defined by the service side.

        :param max_size: The maximum size of bytes data that an EventDataBatch object can hold.
        :type max_size: int
        :param partition_key: With the given partition_key, event data will land to
         a particular partition of the Event Hub decided by the service.
        :type partition_key: str
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
        # type:(int, str) -> EventDataBatch
        if not self._max_message_size_on_link:
            with self._producers_locks[-1]:
                if self._producers[-1] is None:
                    self._producers[-1] = self._create_producer(partition_id=None)
                    self._producers[-1]._open_with_retry()  # pylint: disable=protected-access
            with self._producers_locks:
                self._max_message_size_on_link = self._producers[-1].message_handler._link.peer_max_message_size \
                                                 or constants.MAX_MESSAGE_LENGTH_BYTES  # pylint: disable=protected-access

        if max_size and max_size > self._max_message_size_on_link:
            raise ValueError('Max message size: {} is too large, acceptable max batch size is: {} bytes.'
                             .format(max_size, self._max_message_size_on_link))

        return EventDataBatch(max_size=(max_size or self._max_message_size_on_link), partition_key=partition_key)

    def close(self):
        # type:() -> None
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
        # type: () -> None
        for p in self._producers:
            if p:
                p.close()
        self._conn_manager.close_connection()
