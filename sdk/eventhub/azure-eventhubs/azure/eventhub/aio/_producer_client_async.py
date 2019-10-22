# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import asyncio
import logging

from typing import Any, Union, TYPE_CHECKING, Iterable, List
from ._client_async import EventHubClient
from ._producer_async import EventHubProducer
from .._common import EventData, \
    EventHubSharedKeyCredential, EventHubSASTokenCredential, EventDataBatch

from uamqp import constants

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential  # type: ignore

log = logging.getLogger(__name__)


class EventHubProducerClient(EventHubClient):
    """
    The EventHubProducerClient class defines a high level interface for asynchronously
    sending events to the Azure Event Hubs service.

    Example:
        .. literalinclude:: ../examples/async_examples/test_examples_eventhub_async.py
            :start-after: [START create_eventhub_client_async]
            :end-before: [END create_eventhub_client_async]
            :language: python
            :dedent: 4
            :caption: Create a new instance of the Event Hub client async.

    """

    def __init__(self, host, event_hub_path, credential, **kwargs):
        # type:(str, str, Union[EventHubSharedKeyCredential, EventHubSASTokenCredential, TokenCredential], Any) -> None
        super(EventHubProducerClient, self).__init__(host=host, event_hub_path=event_hub_path, credential=credential, **kwargs)
        self._producers = None  # type: List[EventHubProducer]
        self._producers_lock = asyncio.Lock()  # sync the creation of self._producers
        self._producers_locks = None  # sync the creation of

    async def send(self, event_data: Union[EventData, EventDataBatch, Iterable[EventData]],
            *, partition_key: Union[str, bytes] = None, partition_id: str = None, timeout: float = None):

        if self._producers is None:
            async with self._producers_lock:
                if self._producers is None:
                    num_of_producers = len(await self.get_partition_ids()) + 1
                    self._producers = [None] * num_of_producers
                    self._producers_locks = [asyncio.Lock()] * num_of_producers

        producer_index = int(partition_id) if partition_id is not None else -1
        if self._producers[producer_index] is None or self._producers[producer_index]._closed:
            async with self._producers_locks[producer_index]:
                if self._producers[producer_index] is None:
                    self._producers[producer_index] = self._create_producer(partition_id=partition_id)

        await self._producers[producer_index].send(event_data, partition_key=partition_key, timeout=timeout)

    async def create_batch(self, max_size=None, partition_key=None):
        # type:(int, str) -> EventDataBatch
        if not self._max_message_size_on_link:
            async with self._producers_locks[-1]:
                if self._producers[-1] is None:
                    self._producers[-1] = self._create_producer(partition_id=None)
                    await self._producers[-1]._open_with_retry()  # pylint: disable=protected-access
            async with self._producers_locks:
                self._max_message_size_on_link = self._producers[-1].message_handler._link.peer_max_message_size \
                                                 or constants.MAX_MESSAGE_LENGTH_BYTES  # pylint: disable=protected-access

        if max_size and max_size > self._max_message_size_on_link:
            raise ValueError('Max message size: {} is too large, acceptable max batch size is: {} bytes.'
                             .format(max_size, self._max_message_size_on_link))

        return EventDataBatch(max_size=(max_size or self._max_message_size_on_link), partition_key=partition_key)

    async def close(self):
        # type: () -> None
        for p in self._producers:
            if p:
                await p.close()
        await self._conn_manager.close_connection()
