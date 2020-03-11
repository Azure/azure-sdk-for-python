# Guide to migrate from azure-eventhub v1 to v5

This document is intended for users that are familiar with V1 of the Python SDK for Event Hubs library (`azure-eventhub 1.x.x`) and wish 
to migrate their application to V5 of the same library.

For users new to the Python SDK for Event Hubs, please see the [readme file for the azure-eventhub](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventhub/azure-eventhub/README.md).

## General changes
Version 5 of the azure-eventhub package is the result of our efforts to create a client library that is user-friendly and idiomatic to the Python ecosystem.
Alongside an API redesign driven by the new [Azure SDK Design Guidelines for Python](https://azure.github.io/azure-sdk/python_introduction.html#design-principles), 
the latest version improves on several areas from V1.

### Specific clients for sending and receiving
In V5 we've simplified the API surface, making two distinct clients, rather than having a single `EventHubClient`:
* `EventHubProducerClient` for sending messages. [Sync API](https://azuresdkdocs.blob.core.windows.net/$web/python/azure-eventhub/5.0.0/azure.eventhub.html#azure.eventhub.EventHubProducerClient)
and [Async API](https://azuresdkdocs.blob.core.windows.net/$web/python/azure-eventhub/5.0.0/azure.eventhub.aio.html#azure.eventhub.aio.EventHubProducerClient)
* `EventHubConsumerClient` for receiving messages. [Sync API](https://azuresdkdocs.blob.core.windows.net/$web/python/azure-eventhub/5.0.0/azure.eventhub.html#azure.eventhub.EventHubConsumerClient)
and [Async API](https://azuresdkdocs.blob.core.windows.net/$web/python/azure-eventhub/5.0.0/azure.eventhub.aio.html#azure.eventhub.aio.EventHubConsumerClient)

We've also merged the functionality from `EventProcessorHost` into 
`EventHubConsumerClient`, allowing `EventHubConsumerClient` to be the single
point of entry for receiving of any type (from single partition, all partitions, or with load balancing and checkpointing features) within Event Hubs.

V5 has both sync and async APIs. Sync API is under package `azure.eventhub` whereas async API is under package `azure.eventhub.aio`.
They have the same class names under the two packages. For instance, class `EventHubConsumerClient` with sync API under package `azure.eventhub` has its 
async counterpart under package `auzre.eventhub.aio`.
The code samples in this migration guide use async APIs.

### Client constructors

| In v1 | Equivalent in v5 | Sample |
|---|---|---|
| `EventHubClientAsync()`    | `EventHubProducerClient()` or `EventHubConsumerClient()` | [using credential](./samples/async_samples/client_identity_authentication_async.py ) |
| `EventHubClientAsync.from_connection_string()` | `EventHubProducerClient.from_connection_string` or `EventHubConsumerClient.from_connection_string` |[client creation](./samples/async_samples/client_creation_async.py) |
| `EventProcessorHost()`| `EventHubConsumerClient(..., checkpoint_store)`| [receive events using checkpoint store](./samples/async_samples/recv_with_checkpoint_store_async.py) |

In V5, the SDK provides `BlobCheckpointStore` in extension packages azure-eventhub-checkpointstoreblob (for sync) and azure-eventhub-checkpointstoreblob-aio (for async).
You can define your own `CheckpointStore` class to persist checkpoint data.

### Receiving events 

| In v1 | Equivalent in v5 | Sample |
|---|---|---|
| `EventHubClientAsync.add_async_receiver()` and `AsyncReceiver.receive()`| `EventHubConsumerClient.receive()`| [receive events](./samples/async_samples/recv_async.py) |

### Sending events
The process of building event batches is more transparent with `send_batch` of V5.

| In v1 | Equivalent in v5 | Sample |
|---|---|---|
| `EventHubClientAsync.add_async_sender()` and `AsyncSender.send()`| `EventHubProducerClient.send_batch()`| [send events](./samples/async_samples/send_async.py) |

## Migration samples

* [Receiving events](#migrating-code-from-eventhubclient-and-asyncreceiver-to-eventhubconsumerclient-for-receiving-events)
* [Receiving events with checkpointing](#migrating-code-from-eventhubclient-and-asyncsender-to-eventhubproducerclient-for-sending-events)
* [Sending events](#migrating-code-from-eventprocessorhost-to-eventhubconsumerclient-for-receiving-events)

### Migrating code from `EventHubClient` and `AsyncReceiver` to `EventHubConsumerClient` for receiving events

In V1, `AsyncReceiver.receive()` returns a list of EventData.

In V5, EventHubConsumerClient.receive() calls user callback on_event to process events.

For example, this code which keeps receiving from a partition in V1:

```python
client = EventHubClientAsync.from_connection_string(connection_str, eventhub=EVENTHUB_NAME)
receiver = client.add_async_receiver(consumer_group="$Default", partition="0", offset=Offset('@latest'))
try:
    await client.run_async()
    logger = logging.getLogger("azure.eventhub")
    while True:
        received = await receiver.receive(timeout=5)
        for event_data in received:
            logger.info("Message received:{}".format(event_data.body_as_str()))
finally:
    await client.stop_async()
```

Becomes this in V5:

```python
logger = logging.getLogger("azure.eventhub")
async def on_event(partition_context, event):
    logger.info("Message received:{}".format(event.body_as_str()))
    await partition_context.update_checkpoint(event)

client = EventHubConsumerClient.from_connection_string(
    conn_str=CONNECTION_STR, consumer_group="$Default", eventhub_name=EVENTHUB_NAME
)
async with client:
    await client.receive(on_event=on_event, partition_id="0", starting_position="@latest")
```

### Migrating code from `EventHubClient` and `AsyncSender` to `EventHubProducerClient` for sending events

In V1, you create an `EventHubClient`, then create a `AsyncSender`, and call `AsyncSender.send` to send an event that may have
a list/generator of messages.

In V5, this has been consolidated into a one method - `EventHubProducerClient.send_batch`.
Batching merges information from multiple events into a single send, reducing
the amount of network communication needed vs sending events one at a time.
This method deterministically tells you whether the batch of events are sent to the event hub.

So in V1:
```python
client = EventHubClientAsync.from_connection_string(connection_str, eventhub=EVENTHUB_NAME)
sender = client.add_async_sender(partition="0")
try:
    await client.run_async()
    event_data = EventData(b"A single event")
    await sender.send(event_data)
finally:
    await client.stop_async()
```

In V5:
```python
producer = EventHubProducerClient.from_connection_string(conn_str=EVENT_HUB_CONNECTION_STR, eventhub_name=EVENTHUB_NAME)
async with producer:
    event_data_batch = await producer.create_batch(partition_id="0")
    event_data_batch.add(EventData(b"A single event"))
    await producer.send_batch(event_data_batch)
```

### Migrating code from `EventProcessorHost` to `EventHubConsumerClient` for receiving events

In V1, `EventProcessorHost` allowed you to balance the load between multiple instances of 
your program when receiving events.

In V5, `EventHubConsumerClient` allows you to do the same with the `receive()` method if you
pass a `CheckpointStore` to the constructor.

So in V1:
```python
import logging
import asyncio
import os

from azure.eventprocessorhost import (
    AbstractEventProcessor,
    AzureStorageCheckpointLeaseManager,
    EventHubConfig,
    EventProcessorHost,
    EPHOptions)

logger = logging.getLogger("azure.eventhub")


class EventProcessor(AbstractEventProcessor):
    def __init__(self, params=None):
        super().__init__(params)
        self._msg_counter = 0

    async def open_async(self, context):
        logger.info("Connection established {}".format(context.partition_id))

    async def close_async(self, context, reason):
        logger.info("Connection closed (reason {}, id {})".format(
            reason,
            context.partition_id))

    async def process_events_async(self, context, messages):
        self._msg_counter += len(messages)
        logger.info("Partition id {}, Events processed {}".format(context.partition_id, self._msg_counter))
        await context.checkpoint_async()

    async def process_error_async(self, context, error):
        logger.error("Event Processor Error {!r}".format(error))

# Storage Account Credentials
STORAGE_ACCOUNT_NAME = os.environ.get('AZURE_STORAGE_ACCOUNT')
STORAGE_KEY = os.environ.get('AZURE_STORAGE_ACCESS_KEY')
LEASE_CONTAINER_NAME = "leases"

NAMESPACE = os.environ.get('EVENT_HUB_NAMESPACE')
EVENTHUB = os.environ.get('EVENT_HUB_NAME')
USER = os.environ.get('EVENT_HUB_SAS_POLICY')
KEY = os.environ.get('EVENT_HUB_SAS_KEY')

# Eventhub config and storage manager
eh_config = EventHubConfig(NAMESPACE, EVENTHUB, USER, KEY, consumer_group="$Default")
eh_options = EPHOptions()
eh_options.debug_trace = False
storage_manager = AzureStorageCheckpointLeaseManager(
    STORAGE_ACCOUNT_NAME, STORAGE_KEY, LEASE_CONTAINER_NAME)

# Event loop and host
loop = asyncio.get_event_loop()
host = EventProcessorHost(
    EventProcessor,
    eh_config,
    storage_manager,
    ep_params=["param1","param2"],
    eph_options=eh_options,
    loop=loop)
try:
    loop.run_until_complete(host.open_async())
finally:
    await host.close_async()
    loop.stop()

```

And in V5:
```python
import asyncio
import os
import logging
from collections import defaultdict
from azure.eventhub.aio import EventHubConsumerClient
from azure.eventhub.extensions.checkpointstoreblobaio import BlobCheckpointStore

logging.basicConfig(level=logging.INFO)
CONNECTION_STR = os.environ["EVENT_HUB_CONN_STR"]
STORAGE_CONNECTION_STR = os.environ["AZURE_STORAGE_CONN_STR"]
BLOB_CONTAINER_NAME = "your-blob-container-name"
logger = logging.getLogger("azure.eventhub")

events_processed = defaultdict(int)
async def on_event(partition_context, event):
    partition_id = partition_context.partition_id
    events_processed[partition_id] += 1
    logger.info("Partition id {}, Events processed {}".format(partition_id, events_processed[partition_id]))
    await partition_context.update_checkpoint(event)

async def on_partition_initialize(context):
    logger.info("Partition {} initialized".format(context.partition_id))

async def on_partition_close(context, reason):
    logger.info("Partition {} has closed, reason {})".format(context.partition_id, reason))

async def on_error(context, error):
    if context:
        logger.error("Partition {} has a partition related error {!r}.".format(context.partition_id, error))
    else:
        logger.error("Receiving event has a non-partition error {!r}".format(error))

async def main():
    checkpoint_store = BlobCheckpointStore.from_connection_string(STORAGE_CONNECTION_STR, BLOB_CONTAINER_NAME)
    client = EventHubConsumerClient.from_connection_string(
        CONNECTION_STR,
        consumer_group="$Default",
        checkpoint_store=checkpoint_store,
    )
    async with client:
        await client.receive(
            on_event,
            on_error=on_error,  # optional
            on_partition_initialize=on_partition_initialize,  # optional
            on_partition_close=on_partition_close,  # optional
            starting_position="-1",  # "-1" is from the beginning of the partition.
        )

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
```
