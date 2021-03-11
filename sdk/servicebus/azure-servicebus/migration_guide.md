# Guide for migrating azure-servicebus to v7 from v0.50

This guide is intended to assist in the migration to `azure-servicebus` v7 from v0.50.
It will focus on side-by-side comparisons for similar operations between the two packages.

Familiarity with the `azure-servicebus` v0.50 package is assumed.
For those new to the Service Bus client library for Python, please refer to the [README for `azure-servicebus`](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/servicebus/azure-servicebus/README.md) rather than this guide.

## Table of contents

* [Migration benefits](#migration-benefits)
    - [Cross Service SDK improvements](#cross-service-sdk-improvements)
    - [New Features](#new-features)
* [Important changes](#important-changes)
    - [Client hierarchy](#client-hierarchy)
    - [Client constructors](#client-constructors)
    - [Creating sender and receivers](#creating-sender-and-receivers)
    - [Sending messages](#sending-messages)
    - [Receiving messages](#receiving-messages)
    - [Settling messages](#settling-messages)
    - [Scheduling messages and cancelling scheduled messages](#scheduling-messages-and-cancelling-scheduled-messages)
    - [Working with sessions](#working-with-sessions)
    - [Lock renewal](#lock-renewal)
    - [Message format changes](#message-format-changes)
    - [Working with Administration Client](#working-with-administration-client)
    - [Migration samples](#migration-samples)
* [Additional samples](#additional-samples)

## Migration benefits

A natural question to ask when considering whether or not to adopt a new version or library is what
the benefits of doing so would be. As Azure has matured and been embraced by a more diverse group of developers,
we have been focused on learning the patterns and practices to best support developer productivity and
to understand the gaps that the Python client libraries have.

There were several areas of consistent feedback expressed across the Azure client library ecosystem.
One of the most important is that the client libraries for different Azure services have not had a
consistent approach to organization, naming, and API structure. Additionally, many developers have felt
that the learning curve was difficult, and the APIs did not offer a good, approachable,
and consistent onboarding story for those learning Azure or exploring a specific Azure service.

To try and improve the development experience across Azure services,
a set of uniform [design guidelines](https://azure.github.io/azure-sdk/general_introduction.html) was created
for all languages to drive a consistent experience with established API patterns for all services.
A set of [Python-specific guidelines](https://azure.github.io/azure-sdk/python/guidelines/index.html) was also introduced to ensure
that Python clients have a natural and idiomatic feel with respect to the Python ecosystem.
Further details are available in the guidelines for those interested.

### Cross Service SDK improvements

The modern Service Bus client library also provides the ability to share in some of the cross-service improvements made to the Azure development experience, such as
- using the new [`azure-identity`](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/identity/azure-identity/README.md) library
to share a single authentication approach between clients
- a unified logging and diagnostics pipeline offering a common view of the activities across each of the client libraries

### New Features

We have a variety of new features in the version 7 of the Service Bus library.

- Ability to create a batch of messages with the smarter `ServiceBusSender.create_message_batch()` and `ServiceBusMessageBatch.add_message()` APIs. This will help you manage the messages to be sent in the most optimal way.
- Ability to configure the retry policy used by the operations on the client.
- Ability to connect to the service through http proxy.
- Authentication with AAD credentials using [`azure-identity`](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/identity/azure-identity/README.md).
- Refer to the [CHANGELOG.md](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/servicebus/azure-servicebus/CHANGELOG.md) for more new features, changes and bug fixes.

## Important changes

### Client hierarchy

In the interest of simplifying the API surface we've made a single top level client called `ServiceBusClient`,
rather than one for each of queue, topic, and subscription.
This acts as the single entry point in contrast with multiple entry points from before.
You can create senders and receivers from this client to the queue/topic/subscription/session of your
choice and start sending/receiving messages.

#### Approachability
By having a single entry point, the `ServiceBusClient` helps with the discoverability of the API
as you can explore all available features through methods from a single client, as opposed to searching
through documentation or exploring namespace for the types that you can instantiate.
Whether sending or receiving, using sessions or not, you will start your applications by constructing the same client.

#### Consistency
We now have methods with similar names, signature and location to create senders and receivers.
This provides consistency and predictability on the various features of the library.

### Client constructors

- Constructing the client using the connection string remains the same in both versions.
```python
# Authenticate with connection string in V0.50 and V7
servicebus_client = ServiceBusClient.from_connection_string(conn_str)
```
- Additionally, you can now use Azure Active Directory for authentication via the [`azure-identity`](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/identity/azure-identity/README.md) library in V7.
```python
# Authenticate with Azure Active Directory in V7
from azure.identity import DefaultAzureCredential
servicebus_client = ServiceBusClient(fully_qualified_namespace, credential=DefaultAzureCredential())
```
- The option to construct the client using SAS key name and value is not available in the new version, but will be added in the near future.

### Creating sender and receivers

- `QueueClient`, `TopicClient` and `SubscriptionClient` have been replaced with methods to create receivers and senders directly from `ServiceBusClient`.
- The method to create a receiver takes an optional parameter `sub_queue` which can be used to create a receiver for dead-letter sub queue. This replaces the dedicated method `get_deadletter_receiver` from the older version.

In V0.50:

```python
client = ServiceBusClient.from_connection_string(connstr)

# for queues
queue_client = client.get_queue(queue_name)
queue_sender = queue_client.get_sender()
queue_receiver = queue_client.get_receiver()
queue_dead_letter_receiver = queue_client.get_deadletter_receiver()

# for topics
topic_client = client.get_topic(topic_name)
topic_sender = topic_client.get_sender()

# for subscription
subscription_client = client.get_subscription(topic_name, subscription_name)
subscription_receiver = subscription_client.get_receiver()
subscription_dead_letter_receiver = subscription_client.get_deadletter_receiver()
```

In V7:
```Python
with ServiceBusClient.from_connection_string(connstr) as client:

    # for queues
    queue_sender = client.get_queue_sender(queue_name)
    queue_receiver = client.get_queue_receiver(queue_name)
    queue_dead_letter_receiver = client.get_queue_receiver(queue_name, sub_queue=ServiceBusSubQueue.DEAD_LETTER)

    # for topics
    topic_sender = client.get_topic_sender(topic_name)

    # for subscription
    subscription_receiver = client.get_subscription_receiver(topic_name, subscription_name)
    subscription_dead_letter_receiver = client.get_subscription_receiver(topic_name, subscription_name, sub_queue=ServiceBusSubQueue.DEAD_LETTER)
```

### Sending messages

- The `send` method is renamed to `send_messages` following the pattern of using the `messages` suffix in methods that deal with messages.
- You can now pass an array of messages directly in method used to send messages rather than first creating a `BatchMessage`
- Sending multiple messages in a single go always had the potential to fail if batch size exceeded the size limit. To help with this, we have a new class `ServiceBusMessageBatch` which helps in creating a batch that will never increase the size limit.

In V0.50:
```python
with sender:
    # send a single message
    sender.send(Message("Hello world!"))

    # send multiple messages. This can fail if the batch exceeded size limit
    sender.send(BatchMessage(["data 1", "data 2", ...]))
```

In V7:
```python
with sender:

    # send a single message
    sender.send_messages(ServiceBusMessage("Hello world!"))

    # send multiple messages. This can fail if the batch exceeded size limit
    sender.send_messages([ServiceBusMessage("data1"), [ServiceBusMessage("data2"), [ServiceBusMessage("data3")])

    # safely send multiple messages by using a batch object
    message_batch = sender.create_message_batch()
    # add_message will throw MessageSizeExceededError if added size results in the batch exceeding the maximum batch size
    message_batch.add_message(ServiceBusMessage("data"))
    sender.send_messages(message_batch)
```

### Receiving messages

- `fetch_next` method is named to `receive_messages` on `ServiceBusReceiver` to be consistent in usage of the `messages` suffix in other methods on the receiver and the sender.
- `peek` method is renamed to `peek_messages` as the same reason mentioned above.

In V0.50:

```python
with receiver:
    received_messages = receiver.fetch_next(max_batch_size=10, timeout=10)
    peeked_messages = receiver.peek(count=1, start_from=None)
```

In V7:
```python
with receiver:
    received_messages = receiver.receive_messages(max_message_count=10, max_wait_time=10)
    peeked_messages = receiver.peek_messages(max_message_count=1, sequence_number=None)
```

### Settling messages

- Previously, the methods to settle messages (`complete()`, `abandon()`, `defer()` and `dead_letter()`) were on the messages themselves.
These have been moved to the receiver in the new version, take the message as input and have the `message` suffix in their name.
- The idea is to have the message represents just the data and not have the responsibility of any operation on the service side.
Additionally, since a message cannot be settled if the receiver that was used to receive it is not alive, tying these operations
to the receiver drives the message home better.

In V0.50:
```python

with receiver:
    received_message.complete()
    # or
    # received_message.abandon()
    # received_message.defer()
    # received_message.dead_letter()
```

In V7:
```python
with receiver:
    receiver.complete_message(received_message)
    # or
    # receiver.abandon_message(received_message)
    # receiver.defer_message(received_message)
    # receiver.dead_letter_message(received_message)
```

### Scheduling messages and cancelling scheduled messages

- `schedule_messages` and `cancel_scheduled_messages` now takes an array of messages/sequence numbers instead of argument list.

In V0.50:
```python
with sender:
    sender.schedule(schedule_time=schedule_time_utc, message1, message2)
    sender.cancel_scheduled_messages(sequence_number1, sequence_number2)
```

In V7:
```python
with sender:
    sender.schedule_messages(messages=[message1, message2], schedule_time_utc=schedule_time_utc)
    sender.cancel_scheduled_messages([sequence_number1, sequence_number2])
```

### Working with sessions

- To send messages to a sessionful entity, previously the `QueueClient.send` method or `Sender.get_sender` method take `session` parameter.
While in the new version, `session_id` is property on the `ServiceBusMessage`.
- Previously `SessionReceiver` class is used for receiving messages from sessionful entities and performing session-related operations.
In the new version, `SessionReceiver` has been collapsed into `ServiceBusReceiver` to improve modularity and reduce public API surface.
- `ServiceBusSession` class is introduced to perform session-related operations and it can be approached by property `ServiceBusReceiver.session`. For non-sessionful receivers, `ServiceBusReceiver.session` is `None`.

In V0.50:
```python
# Send
queue_client.send(message, session='foo')

sender = queue_client.get_sender(session='foo')
with sender:
    sender.send(message)

# Session-related operation
with session_receiver:
    session_receiver.get_session_state()
    session_receiver.set_session_state("start")
    session_receiver.renew_lock()
```

In V7:
```python
# Send
with sender:
    sender.send_messages(ServiceBusMessage('body', session_id='foo'))

# Session-related operation
with session_receiver:
    session_receiver.session.get_state()
    session_receiver.session.set_state("start")
    session_receiver.session.renew_lock()
```

### Lock renewal

#### Message lock renewal

- `renew_lock` method was moved from `Message` to `ServiceBusReceiver` and renamed to `renew_message_lock` for the same reason as settlement methods movement.

In V0.50:
```python
with receiver:
    received_message.renew_lock()
```

In V7:
```python
with receiver:
    receiver.renew_message_lock(received_message)
```

#### Session lock renewal

- `renew_lock` method was moved to the class `ServiceBusSession` which can be approached by property `ServiceBusReceiver.session` within a sessionful receiver.

In V0.50:
```python
with session_receiver:
    session_receiver.renew_lock()
```

In V7:
```python
with session_receiver:
    session_receiver.session.renew_lock()
```

#### Working with AutoLockRenewer

- `AutoLockRenew` class is renamed to `AutoLockRenewer` and `register` method now takes both the receiver and the object to be auto-lock-renewed.

In V0.50:
```python
from azure.servicebus import AutoLockRenew
auto_lock_renew = AutoLockRenew()

with receiver:
    auto_lock_renew.register(received_message)

with session_receiver:
    auto_lock_renew.register(session_receiver)

auto_lock_renew.shutdown()
```

In V7:
```python
from azure.servicebus import AutoLockRenewer
auto_lock_renewer = AutoLockRenewer()

with receiver:
    auto_lock_renewer.register(receiver, received_message)

with session_receiver:
    auto_lock_renewer.register(session_receiver, session_receiver.session)

auto_lock_renewer.close()
```

### Message format changes

In V0.50 of this library, we had the below to represent a Service Bus message:
- `Message` is the class representing the message you send to and receive from the service.
- `PeekMessage` is the return type of the messages received via the `peek` method.
- `DeferredMessage` is the return type of the messages received via the `receive_deferred_messages` method.

In V7 of this library, we simplified this as below:
- `ServiceBusMessage` is now the class representing the message when you need to send it with the below changes to better align with the [AMQP spec](https://www.amqp.org/sites/amqp.org/files/amqp.pdf):
  - `label` has been renamed to `subject`
  - `user_properties` has been renamed to `application_properties`
  - `annotations` has been placed under `raw_amqp_message` instance variable.
- `ServiceBusReceivedMessage` is now the class representing the message when you get it from the service, regardless of whether you used the `peek_messages`/`receive_deferred_messages` operation or received it using the receiver.
  - Properties `settled` and `expired` are no longer available.
- Refer to the [CHANGELOG.md](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/servicebus/azure-servicebus/CHANGELOG.md) for more changes on the message properties.

### Working with Administration Client

In v0.50, you could create/get/update/delete/list Service Bus queues/topics/subscriptions/rules using the `control_client`.
In v7, this is replaced by the `ServiceBusAdministrationClient`.
The following code snippets show how to manage queues, similar methods are provided on the `ServiceBusAdministrationClient` to manage topics, subscriptions and rules.

In V0.50:
```python
from azure.servicebus.control_client import ServiceBusService
service_bus_service = ServiceBusService()
queue = service_bus_service.get_queue(queue_name)
service_bus_service.create_queue(queue_name)
service_bus_service.delete_queue(queue_name)
queues = service_bus_service.list_queues()
```

In V7:
```python
from azure.servicebus.management import ServiceBusAdministrationClient
service_bus_administration_client = ServiceBusAdministrationClient()
queue = service_bus_administration_client.get_queue(queue_name)
service_bus_administration_client.create_queue(queue_name)
service_bus_administration_client.delete_queue(queue_name)
queues = service_bus_administration_client.list_queues()
```

### Migration samples

* [Receiving messages](#migrating-code-from-queueclient-and-receiver-to-servicebusreceiver-for-receiving-messages)
* [Sending messages](#migrating-code-from-queueclient-and-sender-to-servicebussender-for-sending-messages)

#### Migrating code from `QueueClient` and `Receiver` to `ServiceBusReceiver` for receiving messages

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
with ServiceBusClient.from_connection_string(conn_str=CONNECTION_STR, receive_mode=ServiceBusReceiveMode.PEEK_LOCK) as client:

    with client.get_queue_receiver(queue_name=QUEUE_NAME) as receiver:
        batch = receiver.receive_messages(max_message_count=10, max_wait_time=5)
        for message in batch:
            print("Message: {}".format(message))
            receiver.complete_message(message)

        for message in receiver:
            print("Message: {}".format(message))
            receiver.complete_message(message)
```

#### Migrating code from `QueueClient` and `Sender` to `ServiceBusSender` for sending messages

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

## Additional samples

More examples can be found at [Samples for azure-servicebus](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus/samples)
