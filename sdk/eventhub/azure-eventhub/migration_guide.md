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

V5 has both sync and async APIs. Sync API is under package azure.eventhub whereas async API is under package azure.eventhub.aio.
They have the same class names under the two packages. For instance, class `EventHubConsumerClient` with sync API under package `azure.eventhub` has its 
async counterpart under package `auzre.eventhub.aio`.

The code samples in this migration guide use async APIs.

### Client constructors

| In v1                                          | Equivalent in v5                                                 | Sample |
|------------------------------------------------|------------------------------------------------------------------|--------|
| `EventHubClient()`    | `EventHubProducerClient()` or `EventHubConsumerClient()` | [using credential](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventhub/azure-eventhub/samples/sync_samples/client_secret_auth.py) |
| `EventHubClient.from_connection_string()` | `EventHubProducerClient.from_connection_string` or `EventHubConsumerClient.from_connection_string` |[receive events](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventhub/azure-eventhub/samples/async_samples/recv_async.py),  [send events](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventhub/azure-eventhub/samples/async_samples/send_async.py) |
| `EventProcessorHost()`| `EventHubConsumerClient(..., checkpoint_store)`| [receive events using checkpoint store](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventhub/azure-eventhub/samples/async_samples/recv_with_checkpoint_store_async.py) |

### Receiving events 

| In v1                                          | Equivalent in v5                                                 | Sample |
|------------------------------------------------|------------------------------------------------------------------|--------|
| `EventHubClient.add_receiver()` and `Receiver.receive()`                       | `EventHubConsumerClient.receive()`                               | [receive events](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventhub/azure-eventhub/samples/async_samples/recv_async.py) |

### Sending events

| In v1                                          | Equivalent in v5                                                 | Sample |
|------------------------------------------------|------------------------------------------------------------------|--------|
| `EventHubClient.add_sender()` and `Sender.send()`                          | `EventHubProducerClient.send_batch()`                               | [send events](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventhub/azure-eventhub/samples/async_samples/send_async.py) |

### Minor renames

TODO: add some minor renames

## Migration samples

* [Receiving events](#migrating-code-from-eventhubclient-and-receiverasync-to-eventhubconsumerclient-for-receiving-events)
* [Receiving events with checkpointing](#migrating-code-from-eventhubclient-and-senderasync-to-eventhubproducerclient-for-sending-events)
* [Sending events](#migrating-code-from-eventprocessorhost-to-eventhubconsumerclient-for-receiving-events)

### Migrating code from `EventHubClient` and `ReceiverAsync` to `EventHubConsumerClient` for receiving events

In V1, `ReceiverAsync.receive()` returns a list of EventData.

In V5, EventHubConsumerClient.receive() calls user callback on_event to process events.

For example, this code which receives from a partition in V1:

```python
client = EventHubClientAsync.from_connection_string(connection_str)
receiver = client.add_async_receiver(consumer_group="$default", partition="0", offset=Offset('@latest'))
try:
    await client.run_async()
    logger = logging.getLogger("azure.eventhub")
    received = await receiver.receive(timeout=5)
    for event_data in received:
        logger.info("Message received:{}".format(event_data.body_as_str()))
except:
    raise
finally:
    await client.stop_async()
```

Becomes this in V5:

```python
async def on_event(partition_context, event):
    print("Received event from partition: {}".format(partition_context.partition_id))
    print(event)

client = EventHubConsumerClient.from_connection_string(
    conn_str=CONNECTION_STR,
    consumer_group="$default",
    eventhub_name=EVENTHUB_NAME
)

async with client:
    await client.receive(on_event=on_event, partition_id="0", starting_position="@latest")
```

### Migrating code from `EventHubClient` and `SenderAsync` to `EventHubProducerClient` for sending events

In V1, you create an `EventHubClient`, then create a `SenderAsync`, and call `SenderAsync.send` to send an event that may have
a list/generator of messages.

In V5, this has been consolidated into a one method - `EventHubProducerClient.send_batch`.
Batching merges information from multiple events into a single send, reducing
the amount of network communication needed vs sending events one at a time.
This method deterministically tells you whether the batch of events are sent to the event hub.

So in V1:
```python
client = EventHubClientAsync.from_connection_string(connection_str)
sender = client.add_async_sender(partition="0")
try:
    await client.run_async()
    event_data = EventData(b"A single event")
    await sender.send(event_data)
except:
    raise
finally:
    await client.stop_async()
```

In V5:
```python
producer = EventHubProducerClient.from_connection_string(conn_str=EVENT_HUB_CONNECTION_STR, eventhub_name=EVENTHUB_NAME)
async with producer:
    event_data_batch = await producer.create_batch(max_size_in_bytes=10000, partition_id="0")
    while True:
        try:
            event_data_batch.add(EventData('Message inside EventBatchData'))
        except ValueError:
            break
    await producer.send_batch(event_data_batch)
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

async def main():
    checkpoint_store = BlobCheckpointStore.from_connection_string(STORAGE_CONNECTION_STR, "container_name_to_store_checkpoint")
    client = EventHubConsumerClient.from_connection_string(
        CONNECTION_STR,
        consumer_group="$Default",
        checkpoint_store=checkpoint_store,
    )
    async with client:
        await client.receive(on_event)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
```
