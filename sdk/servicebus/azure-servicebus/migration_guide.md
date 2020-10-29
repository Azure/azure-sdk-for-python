# Guide to migrate from azure-servicebus v0.50 to v7

This document is intended for users that are familiar with v0.50 of the Python SDK for Service Bus library (`azure-servicebus 0.50.x`) and wish 
to migrate their application to v7 of the same library.

For users new to the Python SDK for Service Bus, please see the [readme file for the azure-servicebus](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus/README.md).

## General changes
Version 7 of the azure-servicebus package is the result of our efforts to create a client library that is user-friendly and idiomatic to the Python ecosystem.
Alongside an API redesign driven by the new [Azure SDK Design Guidelines for Python](https://azure.github.io/azure-sdk/python_introduction.html#design-principles), 
the latest version improves on several areas from v0.50.

Note: The large version gap is in order to normalize service bus SDK versions across our languages, as they consolidate on structure as well.

### Specific clients for sending and receiving
In v7 we've simplified the API surface, making two distinct clients, rather than one for each of queue, topic, and subscription:
* `ServiceBusSender` for sending messages. [Sync API](https://azuresdkdocs.blob.core.windows.net/$web/python/azure-servicebus/latest/azure.servicebus.html#azure.servicebus.ServiceBusSender)
and [Async API](https://azuresdkdocs.blob.core.windows.net/$web/python/azure-servicebus/latest/azure.servicebus.aio.html#azure.servicebus.aio.ServiceBusSender)
* `ServiceBusReceiver` for receiving messages. [Sync API](https://azuresdkdocs.blob.core.windows.net/$web/python/azure-servicebus/latest/azure.servicebus.html#azure.servicebus.ServiceBusReceiver)
and [Async API](https://azuresdkdocs.blob.core.windows.net/$web/python/azure-servicebus/latest/azure.servicebus.aio.html#azure.servicebus.aio.ServiceBusReceiver)
* `ServiceBusSessionReceiver` for receiving messages from a session. [Sync API](https://azuresdkdocs.blob.core.windows.net/$web/python/azure-servicebus/latest/azure.servicebus.html#azure.servicebus.ServiceBusSessionReceiver)
and [Async API](https://azuresdkdocs.blob.core.windows.net/$web/python/azure-servicebus/latest/azure.servicebus.aio.html#azure.servicebus.aio.ServiceBusSessionReceiver)

As a user this will be largely transparent to you, as initialization will still occur primarily via the top level ServiceBusClient,
the primary difference will be that rather than creating a queue_client, for instance, and then a sender off of that, you would simply
create a servicebus queue sender off of your ServiceBusClient instance via the "get_queue_sender" method.

It should also be noted that many of the helper methods that previously existed on the intermediary client (e.g. QueueClient and `peek()`) now
exist on the receiver (in the case of `peek()`) or sender itself.  This is to better consolidate functionality and align messaging link lifetime
semantics with the sender or receiver lifetime.

### Client constructors

| In v0.50 | Equivalent in v7 | Sample |
|---|---|---|
| `ServiceBusClient.from_connection_string()`    | `ServiceBusClient.from_connection_string()` | [using credential](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus/samples/sync_samples/sample_code_servicebus.py ) |
| `QueueClient.from_connection_string()`    | `ServiceBusClient.from_connection_string().get_queue_<sender/receiver>()` | [client initialization](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus/samples/sync_samples/send_queue.py ) |
| `QueueClient.from_connection_string(idle_timeout=None)` | `QueueClient.from_connection_string(max_wait_time=None)` | [providing a timeout](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus/samples/sync_samples/session_pool_receive.py) |

### Receiving messages

| In v0.50 | Equivalent in v7 | Sample |
|---|---|---|
| `QueueClient.from_connection_string().get_receiver().fetch_next()  and ServiceBusClient.from_connection_string().get_queue().get_receiver().fetch_next()`| `ServiceBusClient.from_connection_string().get_queue_receiver().receive_messages()`| [Get a receiver and receive a single batch of messages](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus/samples/sync_samples/receive_queue.py) |
| `QueueClient.from_connection_string().get_receiver().peek()  and ServiceBusClient.from_connection_string().get_queue().get_receiver().peek()`| `ServiceBusClient.from_connection_string().get_queue_receiver().peek_messages()`| [Get a receiver and receive a single batch of messages](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/servicebus/azure-servicebus/samples/sync_samples/receive_peek.py) |
| `QueueClient.from_connection_string().get_deadletter_receiver()  and ServiceBusClient.from_connection_string().get_queue().get_deadletter_receiver()`| `ServiceBusClient.from_connection_string().get_queue_receiver(sub_queue=SubQueue.DeadLetter)`| [Get a deadletter receiver](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/servicebus/azure-servicebus/samples/sync_samples/receive_deadlettered_messages.py) |

### Sending messages

| In v0.50 | Equivalent in v7 | Sample |
|---|---|---|
| `QueueClient.from_connection_string().send()  and ServiceBusClient.from_connection_string().get_queue().get_sender().send()`| `ServiceBusClient.from_connection_string().get_queue_sender().send_messages()`| [Get a sender and send a message](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus/samples/sync_samples/send_queue.py) |
| `queue_client.send(BatchMessage(["data 1", "data 2", ...]))`| `batch = queue_sender.create_message_batch()  batch.add_message(ServiceBusMessage("data 1"))  queue_sender.send_messages(batch)`| [Create and send a batch of messages](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus/samples/sync_samples/send_queue.py) |

### Scheduling messages and cancelling scheduled messages 

| In v0.50 | Equivalent in v7 | Sample |
|---|---|---|
| `queue_client.get_sender().schedule(schedule_time_utc, message1, message2)` | `sb_client.get_queue_sender().schedule_messages([message1, message2], schedule_time_utc)` | [Schedule messages](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus/samples/sync_samples/schedule_messages_and_cancellation.py) |
| `queue_client.get_sender().cancel_scheduled_messages(sequence_number1, sequence_number2)`| `sb_client.get_queue_sender().cancel_scheduled_messages([sequence_number1, sequence_number2])` | [Cancel scheduled messages](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus/samples/sync_samples/schedule_messages_and_cancellation.py)|

### Working with sessions

| In v0.50 | Equivalent in v7 | Sample |
|---|---|---|
| `queue_client.send(message, session='foo')  and queue_client.get_sender(session='foo').send(message)`| `sb_client.get_queue_sender().send_messages(Message('body', session_id='foo'))`| [Send a message to a session](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus/samples/sync_samples/session_send_receive.py) |
| `AutoLockRenew().register(queue_client.get_receiver(session='foo'))`| `receiver=sb_client.get_queue_receiver(session_id='foo')` <br> `AutoLockRenewer().register(receiver, receiver.session)`| [Access a session and ensure its lock is auto-renewed](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/servicebus/azure-servicebus/samples/sync_samples/auto_lock_renew.py) |
| `receiver.get_session_state()` | `receiver.session.get_state()` | [Perform session specific operations on a receiver](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/servicebus/azure-servicebus/samples/sync_samples/session_send_receive.py)

### Working with UTC time
| In v0.50 | Equivalent in v7 | Note |
|---|---|---|
| `session.locked_until < datetime.now()`| `session.locked_until_utc < datetime.utcnow()`| All datetimes are now UTC and named as such|
| `message.scheduled_enqueue_time < datetime.now()`| `message.scheduled_enqueue_time_utc < datetime.utcnow()`| UTC Datetime normalization applies across all objects and datetime fields|

### Managing queues
| In v0.50 | Equivalent in v7 | Sample |
|---|---|---|
| `azure.servicebus.control_client.ServiceBusService().create_queue(queue_name)` | `azure.servicebus.management.ServiceBusAdministrationClient().create_queue(queue_name)` | [Create a queue](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/servicebus/azure-servicebus/samples/sync_samples/mgmt_queue.py) |
| `azure.servicebus.ServiceBusClient().list_queues()` | `azure.servicebus.management.ServiceBusAdministrationClient().list_queues()` | [List queues](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/servicebus/azure-servicebus/samples/sync_samples/mgmt_queue.py) |

### Working with AutoLockRenewer
| In v0.50 | Equivalent in v7 | Sample |
|---|---|---|
| `azure.servicebus.AutoLockRenew().shutdown()` | `azure.servicebus.AutoLockRenewer().close()` | [Close an auto-lock-renewer](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus/samples/sync_samples/auto_lock_renew.py) |


## Migration samples

* [Receiving messages](#migrating-code-from-queueclient-and-receiver-to-servicebusreceiver-for-receiving-messages)
* [Sending messages](#migrating-code-from-queueclient-and-sender-to-servicebussender-for-sending-messages)

### Migrating code from `QueueClient` and `Receiver` to `ServiceBusReceiver` for receiving messages

In v0.50, `QueueClient` would be created directly or from the `ServiceBusClient.get_queue` method,
after which user would call `get_receiver` to obtain a receiver, calling `fetch_next` to receive a single 
batch of messages, or iterate over the receiver to receive continuously.

In v7, users should initialize the client via `ServiceBusClient.get_queue_receiver`.  Single-batch-receive
has been renamed to `receive_messages`, iterating over the receiver for continual message consumption has not changed.
It should also be noted that if a session receiver is desired, to use the `get_<queue/subscription>_receiver`
function and pass the `session_id` parameter.

For example, this code which keeps receiving from a partition in v0.50:

```python
client = ServiceBusClient.from_connection_string(CONNECTION_STR)
queue_client = client.get_queue(queue)

with queue_client.get_receiver(idle_timeout=1, mode=ReceiveSettleMode.PeekLock, prefetch=10) as receiver:

    # Receive list of messages as a batch
    batch = receiver.fetch_next(max_batch_size=10)
    for message in batch:
        print("Message: {}".format(message))
        message.complete()

    # Receive messages as a continuous generator
    for message in receiver:
        print("Message: {}".format(message))
        message.complete()
```

Becomes this in v7:
```python
with ServiceBusClient.from_connection_string(conn_str=CONNECTION_STR, receive_mode=ReceiveMode.PeekLock) as client:

    with client.get_queue_receiver(queue_name=QUEUE_NAME) as receiver:
        batch = receiver.receive_messages(max_message_count=10, max_wait_time=5)
        for message in batch:
            print("Message: {}".format(message))
            receiver.complete_message(message)

        for message in receiver:
            print("Message: {}".format(message))
            receiver.complete_message(message)
```


### Migrating code from `QueueClient` and `Sender` to `ServiceBusSender` for sending messages

In v0.50, `QueueClient` would be created directly or from the `ServiceBusClient.get_queue` method,
after which user would call `get_sender` to obtain a sender, calling `send` to send a single or batch
of messages.  Send could also be called directly off of the `QueueClient`

In v7, users should initialize the client via `ServiceBusClient.get_queue_sender`.  Sending itself has not
changed, but currently does not support sending a list of messages in one call.  If this is desired, first
insert those messages into a batch.

So in v0.50:
```python
client = ServiceBusClient.from_connection_string(CONNECTION_STR)

queue_client = client.get_queue(queue)
with queue_client.get_sender() as sender:
    # Send one at a time.
    for i in range(100):
        message = Message("Sample message no. {}".format(i))
        sender.send(message)

    # Send as a batch.
    messages_to_batch = [Message("Batch message no. {}".format(i)) for i in range(10)]
    batch = BatchMessage(messages_to_batch)
    sender.send(batch)
```

In v7:
```python
with ServiceBusClient.from_connection_string(conn_str=CONNECTION_STR) as client:

    with client.get_queue_sender(queue_name=QUEUE_NAME) as sender:
        # Sending one at a time.
        for i in range(100):
            message = ServiceBusMessage("Sample message no. {}".format(i))
            sender.send_messages(message)

        # Send as a batch
        batch = new ServiceBusMessageBatch()
        for i in range(10):
            batch.add_message(ServiceBusMessage("Batch message no. {}".format(i)))
        sender.send_messages(batch)
```
