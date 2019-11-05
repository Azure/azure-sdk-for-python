# Azure Event Hubs client library for Python

Azure Event Hubs is a highly scalable publish-subscribe service that can ingest millions of events per second and stream
them to multiple consumers. This lets you process and analyze the massive amounts of data produced by your connected
devices and applications. Once Event Hubs has collected the data, you can retrieve, transform, and store it by using
any real-time analytics provider or with batching/storage adapters. If you would like to know more about Azure Event Hubs,
you may wish to review: [What is Event Hubs](https://docs.microsoft.com/en-us/azure/event-hubs/event-hubs-about)?

The Azure Event Hubs client library allows for publishing and consuming of Azure Event Hubs events and may be used to:

- Emit telemetry about your application for business intelligence and diagnostic purposes.
- Publish facts about the state of your application which interested parties may observe and use as a trigger for taking action.
- Observe interesting operations and interactions happening within your business or other ecosystem, allowing loosely coupled systems to interact without the need to bind them together.
- Receive events from one or more publishers, transform them to better meet the needs of your ecosystem, then publish the transformed events to a new stream for consumers to observe.

[Source code](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/eventhub/azure-eventhubs) | [Package (PyPi)](https://pypi.org/project/azure-eventhub/5.0.0b5) | [API reference documentation](https://azuresdkdocs.blob.core.windows.net/$web/python/azure-eventhub/5.0.0b5/azure.eventhub.html) | [Product documentation](https://docs.microsoft.com/en-us/azure/event-hubs/)

## Getting started

### Install the package

Install the Azure Event Hubs client library for Python with pip:

```
$ pip install --pre azure-eventhub
```

**Prerequisites**

- Python 2.7, 3.5 or later.
- **Microsoft Azure Subscription:**  To use Azure services, including Azure Event Hubs, you'll need a subscription.
If you do not have an existing Azure account, you may sign up for a free trial or use your MSDN subscriber benefits when you [create an account](https://account.windowsazure.com/Home/Index).

- **Event Hubs namespace with an Event Hub:** To interact with Azure Event Hubs, you'll also need to have a namespace and Event Hub  available.
If you are not familiar with creating Azure resources, you may wish to follow the step-by-step guide
for [creating an Event Hub using the Azure portal](https://docs.microsoft.com/en-us/azure/event-hubs/event-hubs-create).
There, you can also find detailed instructions for using the Azure CLI, Azure PowerShell, or Azure Resource Manager (ARM) templates to create an Event Hub.

### Authenticate the client

Interaction with Event Hubs starts with an instance of the EventHubClient class. You need the host name, SAS/AAD credential and event hub name to instantiate the client object.

#### Obtain a connection string

For the Event Hubs client library to interact with an Event Hub, it will need to understand how to connect and authorize with it.
The easiest means for doing so is to use a connection string, which is created automatically when creating an Event Hubs namespace.
If you aren't familiar with shared access policies in Azure, you may wish to follow the step-by-step guide to [get an Event Hubs connection string](https://docs.microsoft.com/en-us/azure/event-hubs/event-hubs-get-connection-string).

#### Create client

There are several ways to instantiate the EventHubClient object and the following code snippets demonstrate two ways:

**Create client from connection string:**

```python
from azure.eventhub import EventHubConsumerClient

connection_str = '<< CONNECTION STRING FOR THE EVENT HUBS NAMESPACE >>'
event_hub_path = '<< NAME OF THE EVENT HUB >>'
consumer_client = EventHubConsumerClient.from_connection_string(connection_str, event_hub_path)

```

- The `from_connection_string` method takes the connection string of the form
`Endpoint=sb://<yournamespace>.servicebus.windows.net/;SharedAccessKeyName=<yoursharedaccesskeyname>;SharedAccessKey=<yoursharedaccesskey>` and
entity name to your Event Hub instance. You can get the connection string from the [Azure portal](https://docs.microsoft.com/en-us/azure/event-hubs/event-hubs-get-connection-string#get-connection-string-from-the-portal).

**Create client using the azure-identity library:**

```python
from azure.eventhub import EventHubConsumerClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()

host = '<< HOSTNAME OF THE EVENT HUB >>'
event_hub_path = '<< NAME OF THE EVENT HUB >>'
consumer_client = EventHubConsumerClient(host, event_hub_path, credential)

```

- This constructor takes the host name and entity name of your Event Hub instance and credential that implements the
TokenCredential interface. There are implementations of the TokenCredential interface available in the
[azure-identity package](https://pypi.org/project/azure-identity/). The host name is of the format `<yournamespace.servicebus.windows.net>`.

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
As newer events arrive, they are added to the end of this sequence. The number of partitions is specified at the time anEvent Hub is created and cannot be changed.

- A **consumer group** is a view of an entire Event Hub. Consumer groups enable multiple consuming applications to each
have a separate view of the event stream, and to read the stream independently at their own pace and from their own position.
There can be at most 5 concurrent readers on a partition per consumer group; however it is recommended that there is only
one active consumer for a given partition and consumer group pairing. Each active reader receives all of the events from
its partition; if there are multiple readers on the same partition, then they will receive duplicate events.

For more concepts and deeper discussion, see: [Event Hubs Features](https://docs.microsoft.com/en-us/azure/event-hubs/event-hubs-features).
Also, the concepts for AMQP are well documented in [OASIS Advanced Messaging Queuing Protocol (AMQP) Version 1.0](http://docs.oasis-open.org/amqp/core/v1.0/os/amqp-core-overview-v1.0-os.html).

## Examples

The following sections provide several code snippets covering some of the most common Event Hubs tasks, including:

- [Inspect an Event Hub](#inspect-an-event-hub)
- [Publish events to an Event Hub](#publish-events-to-an-event-hub)
- [Consume events from an Event Hub](#consume-events-from-an-event-hub)
- [Async publish events to an Event Hub](#async-publish-events-to-an-event-hub)
- [Async consume events from an Event Hub](#async-consume-events-from-an-event-hub)
- [Consume events using a partition manager](#consume-events-using-a-partition-manager)
- [Use EventHubConsumerClient to work with IoT Hub](#use-eventhubconsumerclient-to-work-with-iot-hub)

### Inspect an Event Hub

Get the partition ids of an Event Hub.

```python
from azure.eventhub import EventHubConsumerClient

connection_str = '<< CONNECTION STRING FOR THE EVENT HUBS NAMESPACE >>'
event_hub_path = '<< NAME OF THE EVENT HUB >>'
client = EventHubConsumerClient.from_connection_string(connection_str, event_hub_path)
partition_ids = client.get_partition_ids()
```

### Publish events to an Event Hub

Publish events to an Event Hub.

#### Send a single event or an array of events

```python
from azure.eventhub import EventHubProducerClient, EventData

connection_str = '<< CONNECTION STRING FOR THE EVENT HUBS NAMESPACE >>'
event_hub_path = '<< NAME OF THE EVENT HUB >>'
client = EventHubProducerClient.from_connection_string(connection_str, event_hub_path)

try:
    event_list = []
    for i in range(10):
        event_list.append(EventData(b"A single event"))
    with client:
        client.send(event_list)
except:
    raise
finally:
    pass
```

#### Send a batch of events

Use the `create_batch` method on `EventHubProducerClient` to create an `EventDataBatch` object which can then be sent using the `send` method.
Events may be added to the `EventDataBatch` using the `try_add` method until the maximum batch size limit in bytes has been reached.
```python
from azure.eventhub import EventHubProducerClient, EventData

try:
    connection_str = '<< CONNECTION STRING FOR THE EVENT HUBS NAMESPACE >>'
    event_hub_path = '<< NAME OF THE EVENT HUB >>'
    client = EventHubProducerClient.from_connection_string(connection_str, event_hub_path)

    event_data_batch = client.create_batch(max_size=10000)
    can_add = True
    while can_add:
        try:
            event_data_batch.try_add(EventData('Message inside EventBatchData'))
        except ValueError:
            can_add = False  # EventDataBatch object reaches max_size.

    with client:
        client.send(event_data_batch)
except:
	raise
finally:
    pass
```

### Consume events from an Event Hub

Consume events from an Event Hub.

```python
import logging
from azure.eventhub import EventHubConsumerClient

connection_str = '<< CONNECTION STRING FOR THE EVENT HUBS NAMESPACE >>'
event_hub_path = '<< NAME OF THE EVENT HUB >>'
client = EventHubConsumerClient.from_connection_string(connection_str, event_hub_path)

logger = logging.getLogger("azure.eventhub")

def on_events(partition_context, events):
    logger.info("Received {} events from partition {}".format(len(events), partition_context.partition_id))

try:
    with client:
        client.receive(on_events=on_events, consumer_group="$Default")
        # receive events from specified partition:
        # client.receive(on_events=on_events, consumer_group="$Default", partition_id='0')
except:
    raise
finally:
    pass
```

### Async publish events to an Event Hub

Publish events to an Event Hub asynchronously.

#### Send a single event or an array of events
```python
from azure.eventhub.aio import EventHubProducerClient
from azure.eventhub import EventData

connection_str = '<< CONNECTION STRING FOR THE EVENT HUBS NAMESPACE >>'
event_hub_path = '<< NAME OF THE EVENT HUB >>'
client = EventHubProducerClient.from_connection_string(connection_str, event_hub_path)

try:
 	event_list = []
 	for i in range(10):
 		event_list.append(EventData(b"A single event"))

	async with client:
		await client.send(event_list)  # Send a list of events
		await client.send(EventData(b"A single event"))  # Send a single event
except:
	raise
finally:
    pass
```

#### Send a batch of events

Use the `create_batch` method on `EventHubProcuer` to create an `EventDataBatch` object which can then be sent using the `send` method.
Events may be added to the `EventDataBatch` using the `try_add` method until the maximum batch size limit in bytes has been reached.
```python
from azure.eventhub.aio import EventHubProducerClient
from azure.eventhub import EventData

try:
    connection_str = '<< CONNECTION STRING FOR THE EVENT HUBS NAMESPACE >>'
    event_hub_path = '<< NAME OF THE EVENT HUB >>'
    client = EventHubProducerClient.from_connection_string(connection_str, event_hub_path)

    event_data_batch = await client.create_batch(max_size=10000)
    can_add = True
    while can_add:
        try:
            event_data_batch.try_add(EventData('Message inside EventBatchData'))
        except ValueError:
            can_add = False  # EventDataBatch object reaches max_size.

    async with client:
        await client.send(event_data_batch)
except:
	raise
finally:
    pass
```

### Async consume events from an Event Hub

Consume events asynchronously from an EventHub.

```python
import logging
from azure.eventhub.aio import EventHubConsumerClient

connection_str = '<< CONNECTION STRING FOR THE EVENT HUBS NAMESPACE >>'
event_hub_path = '<< NAME OF THE EVENT HUB >>'
client = EventHubConsumerClient.from_connection_string(connection_str, event_hub_path)

logger = logging.getLogger("azure.eventhub")

async def on_events(partition_context, events):
    logger.info("Received {} events from partition {}".format(len(events), partition_context.partition_id))

try:
    async with client:
        received = await client.receive(on_events=on_events, consumer_group='$Default')
        # receive events from specified partition:
        # received = await client.receive(on_events=on_events, consumer_group='$Default', partition_id='0')
except:
    raise
finally:
    pass
```

### Consume events using a partition manager

`EventHubConsumerClient` is a high level construct which allows you to receive events from multiple partitions at once 
and load balance with other consumers using the same Event Hub and consumer group.

This also allows the user to track progress when events are processed using checkpoints.

A checkpoint is meant to represent the last successfully processed event by the user from a particular partition of
a consumer group in an Event Hub instance.The `EventHubConsumerClient` uses an instance of PartitionManager to update checkpoints
and to store the relevant information required by the load balancing algorithm.

Search pypi with the prefix `azure-eventhub-checkpointstore` to
find packages that support this and use the PartitionManager implementation from one such package. Please note that both sync and async libraries are provided.

In the below example, we create an instance of `EventHubConsumerClient` and use a `BlobPartitionManager`. You need
to [create an Azure Storage account](https://docs.microsoft.com/en-us/azure/storage/common/storage-quickstart-create-account?tabs=azure-portal)
and a [Blob Container](https://docs.microsoft.com/en-us/azure/storage/blobs/storage-quickstart-blobs-portal#create-a-container) to run the code.

[Azure Blob Storage Partition Manager Async](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/eventhub/azure-eventhubs-checkpointstoreblob-aio)
and [Azure Blob Storage Partition Manager Sync](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/eventhub/azure-eventhubs-checkpointstoreblob)
are one of the `PartitionManager` implementations we provide that applies Azure Blob Storage as the persistent store.


```python
import asyncio

from azure.eventhub.aio import EventHubConsumerClient
from azure.storage.blob.aio import ContainerClient
from azure.eventhub.extensions.checkpointstoreblobaio import BlobPartitionManager

RECEIVE_TIMEOUT = 5  # timeout in seconds for a receiving operation. 0 or None means no timeout
RETRY_TOTAL = 3  # max number of retries for receive operations within the receive timeout. Actual number of retries clould be less if RECEIVE_TIMEOUT is too small
connection_str = '<< CONNECTION STRING FOR THE EVENT HUBS NAMESPACE >>'
storage_connection_str = '<< CONNECTION STRING FOR THE STORAGE >>'
blob_name_str = '<<STRING FOR THE BLOB NAME>>'

async def do_operation(event):
    # do some sync or async operations. If the operation is i/o intensive, async will have better performance
    print(event)

async def process_events(partition_context, events):
    await asyncio.gather(*[do_operation(event) for event in events])
    await partition_context.update_checkpoint(events[-1])

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    container_client = ContainerClient.from_connection_string(storage_connection_str, blob_name_str)
    partition_manager = BlobPartitionManager(container_client=container_client)
    client = EventHubConsumerClient.from_connection_string(connection_str, partition_manager=partition_manager, receive_timeout=RECEIVE_TIMEOUT, retry_total=RETRY_TOTAL)
    try:
        loop.run_until_complete(client.receive(process_events, "$default"))
    except KeyboardInterrupt:
        loop.run_until_complete(client.close())
    finally:
        loop.stop()
```

### Use EventHubConsumerClient to work with IoT Hub

You can use `EventHubConsumerClient` to work with IoT Hub as well. This is useful for receiving telemetry data of IoT Hub from the
linked EventHub. The associated connection string will not have send claims, hence sending events is not possible.

- Please notice that the connection string needs to be for an
  [Event Hub-compatible endpoint](https://docs.microsoft.com/en-us/azure/iot-hub/iot-hub-devguide-messages-read-builtin)
  e.g. "Endpoint=sb://my-iothub-namespace-[uid].servicebus.windows.net/;SharedAccessKeyName=my-SA-name;SharedAccessKey=my-SA-key;EntityPath=my-iot-hub-name"

```python
from azure.eventhub import EventHubConsumerClient

connection_str = 'Endpoint=sb://my-iothub-namespace-[uid].servicebus.windows.net/;SharedAccessKeyName=my-SA-name;SharedAccessKey=my-SA-key;EntityPath=my-iot-hub-name'
client = EventHubConsumerClient.from_connection_string(connection_str)

partition_ids = client.get_partition_ids()
```

## Troubleshooting

### General

The Event Hubs APIs generate the following exceptions.

- **AuthenticationError:** Failed to authenticate because of wrong address, SAS policy/key pair, SAS token or azure identity.
- **ConnectError:** Failed to connect to the EventHubs. The AuthenticationError is a type of ConnectError.
- **ConnectionLostError:** Lose connection after a connection has been built.
- **EventDataError:** The EventData to be sent fails data validation. 
For instance, this error is raised if you try to send an EventData that is already sent.
- **EventDataSendError:** The Eventhubs service responds with an error when an EventData is sent.
- **OperationTimeoutError:** EventHubConsumer.send() times out.
- **EventHubError:** All other Eventhubs related errors. It is also the root error class of all the above mentioned errors.

## Next steps

### Examples

These are [more samples](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventhub/azure-eventhubs/samples) in our repo demonstrating the usage of the library.

- [./samples/sync_samples/send.py](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventhub/azure-eventhubs/examples/send.py) - use EventHubProducerClient to publish events
- [./samples/sync_samples/recv.py](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventhub/azure-eventhubs/examples/recv.py) - use EventHubConsumerClient to consume events
- [./samples/async_examples/send_async.py](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventhub/azure-eventhubs/examples/async_examples/send_async.py) - async/await support of a EventHubProducerClient
- [./samples/async_examples/recv_async.py](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventhub/azure-eventhubs/examples/async_examples/recv_async.py) - async/await support of a EventHubConsumerClient

### Documentation

Reference documentation is available at https://azuresdkdocs.blob.core.windows.net/$web/python/azure-eventhub/5.0.0b5/azure.eventhub.html.

### Logging

- Enable `azure.eventhub` logger to collect traces from the library.
- Enable `uamqp` logger to collect traces from the underlying uAMQP library.
- Enable AMQP frame level trace by setting `logging_enable=True` when creating the client.

### Provide Feedback

If you encounter any bugs or have suggestions, please file an issue in the [Issues](https://github.com/Azure/azure-sdk-for-python/issues) section of the project.

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the
PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

![Impressions](https://azure-sdk-impressions.azurewebsites.net/api/impressions/azure-sdk-for-python/sdk/eventhub/azure-eventhubs/README.png)