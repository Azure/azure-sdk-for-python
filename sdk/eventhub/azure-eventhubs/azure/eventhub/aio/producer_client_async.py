# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import asyncio
import logging

from typing import Any, Union, TYPE_CHECKING, Iterable, List
from .client_async import EventHubClient
from .producer_async import EventHubProducer
from azure.eventhub.common import EventData, \
    EventHubSharedKeyCredential, EventHubSASTokenCredential, EventDataBatch

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential  # type: ignore

log = logging.getLogger(__name__)


class EventHubProducerClient(EventHubClient):
    """
    The EventHubClient class defines a high level interface for asynchronously
    sending events to and receiving events from the Azure Event Hubs service.

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
                    self._producers_locks = [asyncio.Lock] * num_of_producers

        producer_index = int(partition_id) if partition_id is not None else -1
        if self._producers[producer_index] is None or self._producers[producer_index]._closed:
            async with self._producers_locks[producer_index]:
                if self._producers[producer_index] is None:
                    self._producers[producer_index] = self._create_producer(partition_id=partition_id)

        await self._producers[producer_index].send(event_data, partition_key=partition_key, timeout=timeout)

    async def close(self):
        # type: () -> None
        for p in self._producers:
            if p:
                await p.close()
        await self._conn_manager.close_connection()
