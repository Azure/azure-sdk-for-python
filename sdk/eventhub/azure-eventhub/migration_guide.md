# Migration Guide (EventHubs v1 to v5)

This document is intended for users that are familiar with V1 of the Python SDK for Event Hubs library (`azure-eventhub 1.x.x`) and wish 
to migrate their application to V5 of the same library.

For users new to the Python SDK for Event Hubs, please see the [readme file for the azure-eventhub](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventhub/azure-eventhub/README.md).

## General changes

In the interest of simplifying the API surface we've made two distinct
clients, rather than having a single `EventHubClient`. 
* `EventHubProducerClient` for sending messages. [Sync API](https://azuresdkdocs.blob.core.windows.net/$web/python/azure-eventhub/5.0.0b6/azure.eventhub.html#azure.eventhub.EventHubProducerClient)
and [Async API](https://azuresdkdocs.blob.core.windows.net/$web/python/azure-eventhub/5.0.0b6/azure.eventhub.aio.html#azure.eventhub.aio.EventHubProducerClient)
* `EventHubConsumerClient` for receiving messages. [Sync API](https://azuresdkdocs.blob.core.windows.net/$web/python/azure-eventhub/5.0.0b6/azure.eventhub.html#azure.eventhub.EventHubConsumerClient)
and [Async API](https://azuresdkdocs.blob.core.windows.net/$web/python/azure-eventhub/5.0.0b6/azure.eventhub.aio.html#azure.eventhub.aio.EventHubConsumerClient)

We've also merged the functionality from `EventProcessorHost` into 
`EventHubConsumerClient`, allowing `EventHubConsumerClient` to be the single
point of entry for receiving of any type (from single partition, all partitions, or with load balancing and checkpointing features) within Event Hubs.


### Client constructors

| In v1                                          | Equivalent in v5                                                 | Sample |
|------------------------------------------------|------------------------------------------------------------------|--------|
| `EventHubClient()`    | `EventHubProducerClient()` or `EventHubConsumerClient()` | [using credential](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventhub/azure-eventhub/samples/sync_samples/client_secret_auth.py) |
| `EventHubClient.from_connection_string()` | `EventHubProducerClient.from_connection_string` or `EventHubConsumerClient.from_connection_string` |[receive events](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventhub/azure-eventhub/samples/async_samples/recv_async.py),  [send events](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventhub/azure-eventhub/samples/async_samples/send_async.py) |
| `EventProcessorHost()`| `EventHubConsumerClient(..., checkpoint_store)`| [receive events using checkpoint store](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventhub/azure-eventhub/samples/async_samples/recv_with_checkpoint_store_async.py) |

### Receiving events 

| In v1                                          | Equivalent in v5                                                 | Sample |
|------------------------------------------------|------------------------------------------------------------------|--------|
| `EventHubClient.add_receiver()` and `Receiver.receive()`                       | `EventHubConsumerClient.receive()`                               | [receiveEvents](https://github.com/Azure/azure-sdk-for-js/blob/master/sdk/eventhub/event-hubs/samples/receiveEvents.ts) |

### Sending events

| In v1                                          | Equivalent in v5                                                 | Sample |
|------------------------------------------------|------------------------------------------------------------------|--------|
| `EventHubClient.add_sender()` and `Sender.send()`                          | `EventHubProducerClient.send_batch()`                               | [sendEvents](https://github.com/Azure/azure-sdk-for-js/blob/master/sdk/eventhub/event-hubs/samples/sendEvents.ts) |

### Minor renames

TODO: add some minor renames

## Migration samples

* [Receiving events](#migrating-code-from-eventhubclient-and-receiver-to-eventhubconsumerclient-for-receiving-events)
* [Receiving events with checkpointing](#migrating-code-from-eventprocessorhost-to-eventhubconsumerclient-for-receiving-events)
* [Sending events](#migrating-code-from-eventhubclient-to-eventhubproducerclient-for-sending-events)

### Migrating code from `EventHubClient` and `ReceiverAsync` to `EventHubConsumerClient` for receiving events

In V1, `ReceiverAsync.receive()` returns a list of EventData.

In V5, EventHubConsumerClient.receive() calls user callback on_event to process events.

For example, this code which receives from a partition in V1:

```python

```

Becomes this in V5:

```python
import asyncio
import os
from azure.eventhub.aio import EventHubConsumerClient

CONNECTION_STR = os.environ["EVENT_HUB_CONN_STR"]
EVENTHUB_NAME = os.environ['EVENT_HUB_NAME']


async def on_event(partition_context, event):
    print("Received event from partition: {}".format(partition_context.partition_id))
    print(event)

async def main():
    client = EventHubConsumerClient.from_connection_string(
        conn_str=CONNECTION_STR,
        consumer_group="$default",
        eventhub_name=EVENTHUB_NAME
    )
    async with client:
        await client.receive(on_event=on_event)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
```

### Migrating code from `EventHubClient` and `SenderAsync` to `EventHubProducerClient` for sending events

In V1, you create an `EventHubClient`, then create a `SenderAsync`, and call `SenderAsync.send` to send an event that may have
a list/generator of messages.

In V5, this has been consolidated into a one method - `EventHubProducerClient.send_batch`.
Batching merges information from multiple events into a single send, reducing
the amount of network communication needed vs sending events one at a time.
This method deterministically tells you whether the batch of events are sent to the event hub.

So in V2:
```python

```

In V5:
```python
import asyncio
import os

from azure.eventhub.aio import EventHubProducerClient
from azure.eventhub import EventData

EVENT_HUB_CONNECTION_STR = os.environ['EVENT_HUB_CONN_STR']
EVENTHUB_NAME = os.environ['EVENT_HUB_NAME']


async def run(producer):
    async with producer:
        event_data_batch = await producer.create_batch(max_size_in_bytes=10000)
        while True:
            try:
                event_data_batch.add(EventData('Message inside EventBatchData'))
            except ValueError:
                break
        await producer.send_batch(event_data_batch)
producer = EventHubProducerClient.from_connection_string(conn_str=EVENT_HUB_CONNECTION_STR, eventhub_name=EVENTHUB_NAME)
loop = asyncio.get_event_loop()
loop.run_until_complete(run)
```

### Migrating code from `EventProcessorHost` to `EventHubConsumerClient` for receiving events

In V1, `EventProcessorHost` allowed you to balance the load between multiple instances of 
your program when receiving events.

In V5, `EventHubConsumerClient` allows you to do the same with the `receive()` method if you
pass a `CheckpointStore` to the constructor.

So in V1:
```python

```

And in V5:
```python
import asyncio
import os
from azure.eventhub.aio import EventHubConsumerClient
from azure.eventhub.extensions.checkpointstoreblobaio import BlobCheckpointStore

CONNECTION_STR = os.environ["EVENT_HUB_CONN_STR"]
STORAGE_CONNECTION_STR = os.environ["AZURE_STORAGE_CONN_STR"]


async def on_event(partition_context, event):
    # put your code here
    print("Received event from partition: {}".format(partition_context.partition_id))
    await partition_context.update_checkpoint(event)


async def receive(client):
    try:
        await client.receive(on_event=on_event)
    except KeyboardInterrupt:
        await client.close()


async def main():
    checkpoint_store = BlobCheckpointStore.from_connection_string(STORAGE_CONNECTION_STR, "container_name_to_store_checkpoint")
    client = EventHubConsumerClient.from_connection_string(
        CONNECTION_STR,
        consumer_group="$Default",
        checkpoint_store=checkpoint_store,
    )
    async with client:
        await receive(client)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
```
