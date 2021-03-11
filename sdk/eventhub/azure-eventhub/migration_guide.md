# Guide for migrating azure-eventhub to v5 from v1

This guide is intended to assist in the migration to `azure-eventhub` v5 from v1. It will focus on side-by-side comparisons for similar operations between the two packages.

Familiarity with the `azure-eventhub` v1 package is assumed. For those new to the Event Hubs client library for Python, please refer to the [README for `azure-eventhub`](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventhub/azure-eventhub/README.md) rather than this guide.

## Table of contents

* [Migration benefits](#migration-benefits)
    - [Cross Service SDK improvements](#cross-service-sdk-improvements)
    - [New features](#new-features)
* [Important changes](#important-changes)
    - [Client hierarchy](#client-hierarchy)
    - [Client constructors](#client-constructors)
    - [Sending events](#sending-events)
    - [Receiving events](#receiving-events)
    - [Migrating code from EventProcessorHost to EventHubConsumerClient for receiving events](#migrating-code-from-eventprocessorhost-to-eventhubconsumerclient-for-receiving-events)
* [Additional samples](#additional-samples)

## Migration benefits

A natural question to ask when considering whether or not to adopt a new version or library is what the benefits of doing so would be. As Azure has matured and been embraced by a more diverse group of developers, we have been focused on learning the patterns and practices to best support developer productivity and to understand the gaps that the Python client libraries have.

There were several areas of consistent feedback expressed across the Azure client library ecosystem. One of the most important is that the client libraries for different Azure services have not had a consistent approach to organization, naming, and API structure. Additionally, many developers have felt that the learning curve was difficult, and the APIs did not offer a good, approachable, and consistent onboarding story for those learning Azure or exploring a specific Azure service.

To try and improve the development experience across Azure services, a set of uniform [design guidelines](https://azure.github.io/azure-sdk/general_introduction.html) was created for all languages to drive a consistent experience with established API patterns for all services. A set of [Python-specific guidelines](https://azure.github.io/azure-sdk/python/guidelines/index.html) was also introduced to ensure that Python clients have a natural and idiomatic feel with respect to the Python ecosystem. Further details are available in the guidelines for those interested.

### Cross Service SDK improvements

The modern Event Hubs client library also provides the ability to share in some of the cross-service improvements made to the Azure development experience, such as:
- using the new [`azure-identity`](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/identity/azure-identity/README.md) library to share a single authentication approach between clients
- a unified logging and diagnostics pipeline offering a common view of the activities across each of the client libraries

### New features

We have a variety of new features in version 5 of the Event Hubs library.

- Ability to create a batch of messages with the `EventHubProducer.create_batch()` and `EventDataBatch.add()` APIs. This will help you manage events to be sent in the most optimal way.
- Ability to configure the retry policy used by operations on the clients.
- Authentication with AAD credentials using [`azure-identity`](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/identity/azure-identity/README.md).

Refer to the [changelog](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventhub/azure-eventhub/CHANGELOG.md) for more new features, changes and bug fixes.

## Important changes

### Client hierarchy

In the interest of simplifying the API surface, we've made two distinct clients: the `EventHubProducerClient` for sending events and the `EventHubConsumerClient` for receiving events. This is in contrast to the single `EventHubClient` that was used to create senders and receivers.
We've also merged the functionality from `EventProcessorHost` into `EventHubConsumerClient`.

#### Approachability
By having a single entry point for sending, the `EventHubProducerClient` helps with the discoverability of the API
as you can explore all available features for sending events through methods from a single client, as opposed to searching
through documentation or exploring namespace for the types that you can instantiate.

Similarly, by having a single entry point for receiving of any type (from single partition, all partitions, or with load balancing and checkpointing features) within Event Hubs, the `EventHubConsumerClient` helps with the discoverability of the API as you can explore all available features for receiving events through methods from a single client, as opposed to searching
through documentation or exploring namespace for the types that you can instantiate.

#### Consistency
We now have methods with similar names, signature and location for sending and receiving.
This provides consistency and predictability on the various features of the library.

### Client constructors

While we continue to support connection strings when constructing a client, below are the differences in the two versions:
- In v5, we now support the use of Azure Active Directory for authentication.
The new [`azure-identity`](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/identity/azure-identity/README.md) library allows us
to share a single authentication solution between clients of different Azure services.
- The option to construct a client using an address of the form `amqps://<SAS-policy-name>:<SAS-key>@<fully-qualified-namespace>/<eventhub-name>` is no longer supported in v5. This address is not readily available in the Azure portal or in any tooling and so was subject to human error. We instead recommend using the connection string if you want to use a SAS policy.

In v1:
```python
# Authenticate with address
eventhub_client = EventHubClient(address)

# Authenticate with connection string
eventhub_client = EventHubClient.from_connection_string(conn_str)

# Authenticate the EventProcessorHost and StorageCheckpointLeaseManager
eh_config = EventHubConfig(eh_namespace, eventhub_name, user, key, consumer_group="$default")
storage_manager = AzureStorageCheckpointLeaseManager(storage_account_name, storage_key, lease_container_name)
host = EventProcessorHost(EventProcessor, eventhub_config, storage_manager)
```
In v5:
```python
# Address is no longer used for authentication.

# Authenticate with connection string
producer_client = EventHubProducerClient.from_connection_string(conn_str)
consumer_client = EventHubConsumerClient.from_connection_string(conn_str)
checkpoint_store = BlobCheckpointStore.from_connection_string(storage_conn_str, container_name)
consumer_client_with_checkpoint_store = EventHubConsumerClient.from_connection_string(conn_str, consumer_group='$Default', checkpoint_store=checkpoint_store)

# Authenticate with Active Directory
from azure.identity import EnvironmentCredential
producer_client = EventHubProducerClient(fully_qualified_namespace, eventhub_name, credential=EnvironmentCredential())
consumer_client = EventHubConsumerClient(fully_qualified_namespace, eventhub_name, consumer_group='$Default', credential=EnvironmentCredential())
checkpoint_store = BlobCheckpointStore(blob_account_url, container_name, credential=EnvironmentCredential())
consumer_client_with_checkpoint_store = EventHubConsumerClient(fully_qualified_namespace, eventhub_name, consumer_group='$Default', credential=EnvironmentCredential(), checkpoint_store=checkpoint_store)
```
### Sending events

- The `run` and `stop` methods were previously used since the single `EventHubClient` controlled the lifecycle for all senders and receivers. In v5, the `run` and `stop` methods are deprecated since the `EventHubProducerClient` controls its own lifecycle.
- The `add_sender` method is no longer used to create sender clients. Instead, the `EventHubProducerClient` is used for sending events.
- The `send` method that allowed sending single events in each call is removed in favor of the `send_batch` to encourage sending events in batches for better throughput.
- The new `send_batch` method takes a list of `EventData` objects that is batched into a single message by the client before sending.
- The above approach fails if the list of events increase the size limit of the message. To safely send within size limits, use the `EventDataBatch` object to which you can add `EventData` objects until the size limit is reached after which you can send it using the same `send_batch` method.

In v1:
```python
client = EventHubClient(address)
sender = client.add_sender()
client.run()
sender.send(EventData('Single message'))
client.stop()
```

In v5:
```python
producer_client = EventHubProducerClient.from_connection_string(conn_str, eventhub_name)

# Send list of EventData. This can fail if the list exceeds size limit.
event_data_batch = [EventData('Single message')]
producer.send_batch(event_data_batch)

# Send EventDataBatch. Multiple messages will safely be sent by using `create_batch` to create a batch object.
# `add` will throw a ValueError if added size results in the batch exceeding the maximum batch size.
event_data_batch = producer.create_batch()
event_data_batch.add(EventData('Single message'))
producer.send_batch(event_data_batch)
```

### Receiving events

- The `run` and `stop` methods were previously used since the single `EventHubClient` controlled the lifecycle for all senders and receivers. In v5, the `run` and `stop` methods are deprecated since the `EventHubConsumerClient` controls its own lifecycle.
- The `add_receiver` method is no longer used to create receiver clients. Instead, the `EventHubConsumerClient` is used for receiving events.
- In v1, the `receive` method returned a list of `EventData`. You would call this method repeatedly every time you want receive a set of events. In v5, the new `receive` method takes user callback to process events and any resulting errors. This way, you call the method once and it continues to process incoming events until you stop it.
- Additionally, we have a method `receive_batch` which behaves the same as `receive`, but calls the user callback with a batch of events instead of single events.
- The same methods can be used whether you want to receive from a single partition or from all partitions.

In v1:
```python
client = EventHubClient(address)
receiver = client.add_receiver(consumer_group, partition)
client.run()
batch = receiver.receive()
client.stop()
```

In v5:
```python
# Receive
def on_event(partition_context, event):
    print("Received event from partition: {}.".format(partition_context.partition_id))

consumer_client = EventHubConsumerClient.from_connection_string(conn_str, consumer_group, eventhub_name=eh_name)
with consumer_client:
    consumer_client.receive(on_event=on_even, partition_id=partition_id)

# Receive batch
def on_event_batch(partition_context, event_batch):
    print("Partition {}, Received count: {}".format(partition_context.partition_id, len(event_batch)))

consumer_client = EventHubConsumerClient.from_connection_string(conn_str, consumer_group, eventhub_name=eh_name)
with consumer_client:
    consumer_client.receive_batch(on_event_batch=on_event_batch, partition_id=partition_id)
```
### Migrating code from `EventProcessorHost` to `EventHubConsumerClient` for receiving events

In V1, `EventProcessorHost` allowed you to balance the load between multiple instances of
your program when receiving events.

In V5, `EventHubConsumerClient` allows you to do the same with the `receive()` method if you
pass a `CheckpointStore` to the constructor.

> **Note:** V1 checkpoints are not compatible with V5 checkpoints.
If pointed at the same blob, consumption will begin at the first message.
V1 checkpoint json in the respective blobs can be manually converted (per-partition) if needed.
In V1 checkpoints (sequence_number and offset) are stored in the format of json along with ownership information
as the content of the blob, while in V5, checkpoints are kept in the metadata of a blob and the metadata is composed of name-value pairs.
Please check [update_checkpoint](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventhub/azure-eventhub-checkpointstoreblob/azure/eventhub/extensions/checkpointstoreblob/_blobstoragecs.py#L231-L250) in V5 for implementation detail.

So in v1:
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

And in v5:
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

## Additional samples

More examples can be found at [Samples for azure-eventhub](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/eventhub/azure-eventhub/samples)