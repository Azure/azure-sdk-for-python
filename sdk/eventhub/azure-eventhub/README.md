# Azure Event Hubs client library for Python

Azure Event Hubs is a highly scalable publish-subscribe service that can ingest millions of events per second and stream
them to multiple consumers. This lets you process and analyze the massive amounts of data produced by your connected
devices and applications. Once Event Hubs has collected the data, you can retrieve, transform, and store it by using
any real-time analytics provider or with batching/storage adapters. If you would like to know more about Azure Event Hubs,
you may wish to review: [What is Event Hubs](https://docs.microsoft.com/azure/event-hubs/event-hubs-about)?

The Azure Event Hubs client library allows for publishing and consuming of Azure Event Hubs events and may be used to:

- Emit telemetry about your application for business intelligence and diagnostic purposes.
- Publish facts about the state of your application which interested parties may observe and use as a trigger for taking action.
- Observe interesting operations and interactions happening within your business or other ecosystem, allowing loosely coupled systems to interact without the need to bind them together.
- Receive events from one or more publishers, transform them to better meet the needs of your ecosystem, then publish the transformed events to a new stream for consumers to observe.

[Source code](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventhub/azure-eventhub/) | [Package (PyPi)](https://pypi.org/project/azure-eventhub/) | [API reference documentation][api_reference] | [Product documentation](https://docs.microsoft.com/azure/event-hubs/) | [Samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/eventhub/azure-eventhub/samples)

## _Disclaimer_

_Azure SDK Python packages support for Python 2.7 has ended 01 January 2022. For more information and questions, please refer to https://github.com/Azure/azure-sdk-for-python/issues/20691_

## Getting started

### Prerequisites

- Python 3.6 or later.
- **Microsoft Azure Subscription:**  To use Azure services, including Azure Event Hubs, you'll need a subscription.
If you do not have an existing Azure account, you may sign up for a free trial or use your MSDN subscriber benefits when you [create an account](https://account.windowsazure.com/Home/Index).

- **Event Hubs namespace with an Event Hub:** To interact with Azure Event Hubs, you'll also need to have a namespace and Event Hub  available.
If you are not familiar with creating Azure resources, you may wish to follow the step-by-step guide
for [creating an Event Hub using the Azure portal](https://docs.microsoft.com/azure/event-hubs/event-hubs-create).
There, you can also find detailed instructions for using the Azure CLI, Azure PowerShell, or Azure Resource Manager (ARM) templates to create an Event Hub.

### Install the package

Install the Azure Event Hubs client library for Python with pip:

```
$ pip install azure-eventhub
```

### Authenticate the client

Interaction with Event Hubs starts with an instance of EventHubConsumerClient or EventHubProducerClient class. You need either the host name, SAS/AAD credential and event hub name or a connection string to instantiate the client object.

**[Create client from connection string:](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventhub/azure-eventhub/samples/sync_samples/connection_string_authentication.py)**

For the Event Hubs client library to interact with an Event Hub, the easiest means is to use a connection string, which is created automatically when creating an Event Hubs namespace.
If you aren't familiar with shared access policies in Azure, you may wish to follow the step-by-step guide to [get an Event Hubs connection string](https://docs.microsoft.com/azure/event-hubs/event-hubs-get-connection-string).

- The `from_connection_string` method takes the connection string of the form
`Endpoint=sb://<yournamespace>.servicebus.windows.net/;SharedAccessKeyName=<yoursharedaccesskeyname>;SharedAccessKey=<yoursharedaccesskey>` and
entity name to your Event Hub instance. You can get the connection string from the [Azure portal](https://docs.microsoft.com/azure/event-hubs/event-hubs-get-connection-string#get-connection-string-from-the-portal).

**[Create client using the azure-identity library:](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventhub/azure-eventhub/samples/sync_samples/client_identity_authentication.py)**

Alternately, one can use a Credential object to authenticate via AAD with the azure-identity package.

- This constructor demonstrated in the sample linked above takes the host name and entity name of your Event Hub instance and credential that implements the
[TokenCredential](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/azure/core/credentials.py)
protocol. There are implementations of the `TokenCredential` protocol available in the
[azure-identity package](https://pypi.org/project/azure-identity/). The host name is of the format `<yournamespace.servicebus.windows.net>`.
- To use the credential types provided by `azure-identity`, please install the package:
```pip install azure-identity```
- Additionally, to use the async API,  you must first install an async transport, such as [`aiohttp`](https://pypi.org/project/aiohttp/):
```pip install aiohttp```
- When using Azure Active Directory, your principal must be assigned a role which allows access to Event Hubs, such as the
Azure Event Hubs Data Owner role. For more information about using Azure Active Directory authorization with Event Hubs,
please refer to [the associated documentation](https://docs.microsoft.com/azure/event-hubs/authorize-access-azure-active-directory).

## Key concepts

- An **EventHubProducerClient** is a source of telemetry data, diagnostics information, usage logs, or other log data,
as part of an embedded device solution, a mobile device application, a game title running on a console or other device,
some client or server based business solution, or a web site.

- An **EventHubConsumerClient** picks up such information from the Event Hub and processes it. Processing may involve aggregation,
complex computation, and filtering. Processing may also involve distribution or storage of the information in a raw or transformed fashion.
Event Hub consumers are often robust and high-scale platform infrastructure parts with built-in analytics capabilities,
like Azure Stream Analytics, Apache Spark, or Apache Storm.

- A **partition** is an ordered sequence of events that is held in an Event Hub. Azure Event Hubs provides message streaming
through a partitioned consumer pattern in which each consumer only reads a specific subset, or partition, of the message stream.
As newer events arrive, they are added to the end of this sequence. The number of partitions is specified at the time an Event Hub is created and cannot be changed.

- A **consumer group** is a view of an entire Event Hub. Consumer groups enable multiple consuming applications to each
have a separate view of the event stream, and to read the stream independently at their own pace and from their own position.
There can be at most 5 concurrent readers on a partition per consumer group; however it is recommended that there is only
one active consumer for a given partition and consumer group pairing. Each active reader receives all of the events from
its partition; if there are multiple readers on the same partition, then they will receive duplicate events.

For more concepts and deeper discussion, see: [Event Hubs Features](https://docs.microsoft.com/azure/event-hubs/event-hubs-features).
Also, the concepts for AMQP are well documented in [OASIS Advanced Messaging Queuing Protocol (AMQP) Version 1.0](https://docs.oasis-open.org/amqp/core/v1.0/os/amqp-core-overview-v1.0-os.html).

## Examples

The following sections provide several code snippets covering some of the most common Event Hubs tasks, including:

- [Inspect an Event Hub](#inspect-an-event-hub)
- [Publish events to an Event Hub](#publish-events-to-an-event-hub)
- [Consume events from an Event Hub](#consume-events-from-an-event-hub)
- [Consume events from an Event Hub in batches](#consume-events-from-an-event-hub-in-batches)
- [Publish events to an Event Hub asynchronously](#publish-events-to-an-event-hub-asynchronously)
- [Consume events from an Event Hub asynchronously](#consume-events-from-an-event-hub-asynchronously)
- [Consume events from an Event Hub in batches asynchronously](#consume-events-from-an-event-hub-in-batches-asynchronously)
- [Consume events and save checkpoints using a checkpoint store](#consume-events-and-save-checkpoints-using-a-checkpoint-store)
- [Use EventHubConsumerClient to work with IoT Hub](#use-eventhubconsumerclient-to-work-with-iot-hub)

### Inspect an Event Hub

Get the partition ids of an Event Hub.

```python
from azure.eventhub import EventHubConsumerClient

connection_str = '<< CONNECTION STRING FOR THE EVENT HUBS NAMESPACE >>'
consumer_group = '<< CONSUMER GROUP >>'
eventhub_name = '<< NAME OF THE EVENT HUB >>'
client = EventHubConsumerClient.from_connection_string(connection_str, consumer_group, eventhub_name=eventhub_name)
partition_ids = client.get_partition_ids()
```

### Publish events to an Event Hub

Use the `create_batch` method on `EventHubProducerClient` to create an `EventDataBatch` object which can then be sent using the `send_batch` method.
Events may be added to the `EventDataBatch` using the `add` method until the maximum batch size limit in bytes has been reached.
```python
from azure.eventhub import EventHubProducerClient, EventData

connection_str = '<< CONNECTION STRING FOR THE EVENT HUBS NAMESPACE >>'
eventhub_name = '<< NAME OF THE EVENT HUB >>'
client = EventHubProducerClient.from_connection_string(connection_str, eventhub_name=eventhub_name)

event_data_batch = client.create_batch()
can_add = True
while can_add:
    try:
        event_data_batch.add(EventData('Message inside EventBatchData'))
    except ValueError:
        can_add = False  # EventDataBatch object reaches max_size.

with client:
    client.send_batch(event_data_batch)
```

### Consume events from an Event Hub

There are multiple ways to consume events from an EventHub.  To simply trigger a callback when an event is received,
the `EventHubConsumerClient.receive` method will be of use as follows:

```python
import logging
from azure.eventhub import EventHubConsumerClient

connection_str = '<< CONNECTION STRING FOR THE EVENT HUBS NAMESPACE >>'
consumer_group = '<< CONSUMER GROUP >>'
eventhub_name = '<< NAME OF THE EVENT HUB >>'
client = EventHubConsumerClient.from_connection_string(connection_str, consumer_group, eventhub_name=eventhub_name)

logger = logging.getLogger("azure.eventhub")
logging.basicConfig(level=logging.INFO)

def on_event(partition_context, event):
    logger.info("Received event from partition {}".format(partition_context.partition_id))
    partition_context.update_checkpoint(event)

with client:
    client.receive(
        on_event=on_event,
        starting_position="-1",  # "-1" is from the beginning of the partition.
    )
    # receive events from specified partition:
    # client.receive(on_event=on_event, partition_id='0')
```

### Consume events from an Event Hub in batches

Whereas the above sample triggers the callback for each message as it is received, the following sample
triggers the callback on a batch of events, attempting to receive a number at a time.

```python
import logging
from azure.eventhub import EventHubConsumerClient

connection_str = '<< CONNECTION STRING FOR THE EVENT HUBS NAMESPACE >>'
consumer_group = '<< CONSUMER GROUP >>'
eventhub_name = '<< NAME OF THE EVENT HUB >>'
client = EventHubConsumerClient.from_connection_string(connection_str, consumer_group, eventhub_name=eventhub_name)

logger = logging.getLogger("azure.eventhub")
logging.basicConfig(level=logging.INFO)

def on_event_batch(partition_context, events):
    logger.info("Received event from partition {}".format(partition_context.partition_id))
    partition_context.update_checkpoint()

with client:
    client.receive_batch(
        on_event_batch=on_event_batch,
        starting_position="-1",  # "-1" is from the beginning of the partition.
    )
    # receive events from specified partition:
    # client.receive_batch(on_event_batch=on_event_batch, partition_id='0')
```

### Publish events to an Event Hub asynchronously

Use the `create_batch` method on `EventHubProducer` to create an `EventDataBatch` object which can then be sent using the `send_batch` method.
Events may be added to the `EventDataBatch` using the `add` method until the maximum batch size limit in bytes has been reached.
```python
import asyncio
from azure.eventhub.aio import EventHubProducerClient  # The package name suffixed with ".aio" for async
from azure.eventhub import EventData

connection_str = '<< CONNECTION STRING FOR THE EVENT HUBS NAMESPACE >>'
consumer_group = '<< CONSUMER GROUP >>'
eventhub_name = '<< NAME OF THE EVENT HUB >>'

async def create_batch(client):
    event_data_batch = await client.create_batch()
    can_add = True
    while can_add:
        try:
            event_data_batch.add(EventData('Message inside EventBatchData'))
        except ValueError:
            can_add = False  # EventDataBatch object reaches max_size.
    return event_data_batch

async def send():
    client = EventHubProducerClient.from_connection_string(connection_str, eventhub_name=eventhub_name)
    batch_data = await create_batch(client)
    async with client:
        await client.send_batch(batch_data)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(send())
```

### Consume events from an Event Hub asynchronously

This SDK supports both synchronous and asyncio based code.  To receive as demonstrated in the samples above, but within
aio, one would need the following:

```python
import logging
import asyncio
from azure.eventhub.aio import EventHubConsumerClient

connection_str = '<< CONNECTION STRING FOR THE EVENT HUBS NAMESPACE >>'
consumer_group = '<< CONSUMER GROUP >>'
eventhub_name = '<< NAME OF THE EVENT HUB >>'

logger = logging.getLogger("azure.eventhub")
logging.basicConfig(level=logging.INFO)

async def on_event(partition_context, event):
    logger.info("Received event from partition {}".format(partition_context.partition_id))
    await partition_context.update_checkpoint(event)

async def receive():
    client = EventHubConsumerClient.from_connection_string(connection_str, consumer_group, eventhub_name=eventhub_name)
    async with client:
        await client.receive(
            on_event=on_event,
            starting_position="-1",  # "-1" is from the beginning of the partition.
        )
        # receive events from specified partition:
        # await client.receive(on_event=on_event, partition_id='0')

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(receive())
```

### Consume events from an Event Hub in batches asynchronously

All synchronous functions are supported in aio as well.  As demonstrated above for synchronous batch receipt, one can accomplish
the same within asyncio as follows:

```python
import logging
import asyncio
from azure.eventhub.aio import EventHubConsumerClient

connection_str = '<< CONNECTION STRING FOR THE EVENT HUBS NAMESPACE >>'
consumer_group = '<< CONSUMER GROUP >>'
eventhub_name = '<< NAME OF THE EVENT HUB >>'

logger = logging.getLogger("azure.eventhub")
logging.basicConfig(level=logging.INFO)

async def on_event_batch(partition_context, events):
    logger.info("Received event from partition {}".format(partition_context.partition_id))
    await partition_context.update_checkpoint()

async def receive_batch():
    client = EventHubConsumerClient.from_connection_string(connection_str, consumer_group, eventhub_name=eventhub_name)
    async with client:
        await client.receive_batch(
            on_event_batch=on_event_batch,
            starting_position="-1",  # "-1" is from the beginning of the partition.
        )
        # receive events from specified partition:
        # await client.receive_batch(on_event_batch=on_event_batch, partition_id='0')

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(receive_batch())
```

### Consume events and save checkpoints using a checkpoint store

`EventHubConsumerClient` is a high level construct which allows you to receive events from multiple partitions at once
and load balance with other consumers using the same Event Hub and consumer group.

This also allows the user to track progress when events are processed using checkpoints.

A checkpoint is meant to represent the last successfully processed event by the user from a particular partition of
a consumer group in an Event Hub instance. The `EventHubConsumerClient` uses an instance of `CheckpointStore` to update checkpoints
and to store the relevant information required by the load balancing algorithm.

Search pypi with the prefix `azure-eventhub-checkpointstore` to
find packages that support this and use the `CheckpointStore` implementation from one such package. Please note that both sync and async libraries are provided.

In the below example, we create an instance of `EventHubConsumerClient` and use a `BlobCheckpointStore`. You need
to [create an Azure Storage account](https://docs.microsoft.com/azure/storage/common/storage-quickstart-create-account?tabs=azure-portal)
and a [Blob Container](https://docs.microsoft.com/azure/storage/blobs/storage-quickstart-blobs-portal#create-a-container) to run the code.

[Azure Blob Storage Checkpoint Store Async](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventhub/azure-eventhub-checkpointstoreblob-aio)
and [Azure Blob Storage Checkpoint Store Sync](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventhub/azure-eventhub-checkpointstoreblob)
are one of the `CheckpointStore` implementations we provide that applies Azure Blob Storage as the persistent store.


```python
import asyncio

from azure.eventhub.aio import EventHubConsumerClient
from azure.eventhub.extensions.checkpointstoreblobaio import BlobCheckpointStore

connection_str = '<< CONNECTION STRING FOR THE EVENT HUBS NAMESPACE >>'
consumer_group = '<< CONSUMER GROUP >>'
eventhub_name = '<< NAME OF THE EVENT HUB >>'
storage_connection_str = '<< CONNECTION STRING FOR THE STORAGE >>'
container_name = '<<NAME OF THE BLOB CONTAINER>>'

async def on_event(partition_context, event):
    # do something
    await partition_context.update_checkpoint(event)  # Or update_checkpoint every N events for better performance.

async def receive(client):
    await client.receive(
        on_event=on_event,
        starting_position="-1",  # "-1" is from the beginning of the partition.
    )

async def main():
    checkpoint_store = BlobCheckpointStore.from_connection_string(storage_connection_str, container_name)
    client = EventHubConsumerClient.from_connection_string(
        connection_str,
        consumer_group,
        eventhub_name=eventhub_name,
        checkpoint_store=checkpoint_store,  # For load balancing and checkpoint. Leave None for no load balancing
    )
    async with client:
        await receive(client)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
```

### Use EventHubConsumerClient to work with IoT Hub

You can use `EventHubConsumerClient` to work with IoT Hub as well. This is useful for receiving telemetry data of IoT Hub from the
linked EventHub. The associated connection string will not have send claims, hence sending events is not possible.

Please notice that the connection string needs to be for an [Event Hub-compatible endpoint](https://docs.microsoft.com/azure/iot-hub/iot-hub-devguide-messages-read-builtin),
e.g. "Endpoint=sb://my-iothub-namespace-[uid].servicebus.windows.net/;SharedAccessKeyName=my-SA-name;SharedAccessKey=my-SA-key;EntityPath=my-iot-hub-name"

There are two ways to get the Event Hubs compatible endpoint:
- Manually get the "Built-in endpoints" of the IoT Hub in Azure Portal and receive from it.
```python
from azure.eventhub import EventHubConsumerClient

connection_str = 'Endpoint=sb://my-iothub-namespace-[uid].servicebus.windows.net/;SharedAccessKeyName=my-SA-name;SharedAccessKey=my-SA-key;EntityPath=my-iot-hub-name'
consumer_group = '<< CONSUMER GROUP >>'
client = EventHubConsumerClient.from_connection_string(connection_str, consumer_group)

partition_ids = client.get_partition_ids()
```
- Programmatically retrieve the built-in Event Hubs compatible endpoint.
Refer to [IoT Hub Connection String Sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventhub/azure-eventhub/samples/async_samples/iot_hub_connection_string_receive_async.py).

## Troubleshooting

### General

The Event Hubs APIs generate the following exceptions in azure.eventhub.exceptions

- **AuthenticationError:** Failed to authenticate because of wrong address, SAS policy/key pair, SAS token or azure identity.
- **ConnectError:** Failed to connect to the EventHubs. The AuthenticationError is a type of ConnectError.
- **ConnectionLostError:** Lose connection after a connection has been built.
- **EventDataError:** The EventData to be sent fails data validation. For instance, this error is raised if you try to send an EventData that is already sent.
- **EventDataSendError:** The Eventhubs service responds with an error when an EventData is sent.
- **OperationTimeoutError:** EventHubConsumer.send() times out.
- **EventHubError:** All other Eventhubs related errors. It is also the root error class of all the errors described above.

### Logging

- Enable `azure.eventhub` logger to collect traces from the library.
- Enable `uamqp` logger to collect traces from the underlying uAMQP library.
- Enable AMQP frame level trace by setting `logging_enable=True` when creating the client.
- There may be cases where you consider the `uamqp` logging to be too verbose. To suppress unnecessary logging, add the following snippet to the top of your code:
```python
import logging

# The logging levels below may need to be adjusted based on the logging that you want to suppress.
uamqp_logger = logging.getLogger('uamqp')
uamqp_logger.setLevel(logging.ERROR)

# or even further fine-grained control, suppressing the warnings in uamqp.connection module
uamqp_connection_logger = logging.getLogger('uamqp.connection')
uamqp_connection_logger.setLevel(logging.ERROR)
```

## Next steps

### More sample code

Please take a look at the [samples](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventhub/azure-eventhub/samples) directory for detailed examples of how to use this library to send and receive events to/from Event Hubs.

### Documentation

Reference documentation is available [here](https://azuresdkdocs.blob.core.windows.net/$web/python/azure-eventhub/latest/azure.eventhub.html).

### Schema Registry and Avro Encoder

The EventHubs SDK integrates nicely with the [Schema Registry][schemaregistry_service] service and [Avro][avro].
For more information, please refer to [Schema Registry SDK][schemaregistry_repo] and [Schema Registry Avro Encoder SDK][schemaregistry_avroencoder_repo].

### Building uAMQP wheel from source

`azure-eventhub` depends on the [uAMQP](https://pypi.org/project/uamqp/) for the AMQP protocol implementation.
uAMQP wheels are provided for most major operating systems and will be installed automatically when installing `azure-eventhub`.

If you're running on a platform for which uAMQP wheels are not provided, please follow
 the [uAMQP Installation](https://github.com/Azure/azure-uamqp-python#installation) guidance to install from source.

### Provide Feedback

If you encounter any bugs or have suggestions, please file an issue in the [Issues](https://github.com/Azure/azure-sdk-for-python/issues) section of the project.

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the
PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

[avro]: https://avro.apache.org/
[api_reference]: https://docs.microsoft.com/python/api/overview/azure/eventhub-readme
[schemaregistry_service]: https://aka.ms/schemaregistry
[schemaregistry_repo]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/schemaregistry/azure-schemaregistry
[schemaregistry_avroencoder_repo]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/schemaregistry/azure-schemaregistry-avroencoder

![Impressions](https://azure-sdk-impressions.azurewebsites.net/api/impressions/azure-sdk-for-python/sdk/eventhub/azure-eventhub/README.png)
