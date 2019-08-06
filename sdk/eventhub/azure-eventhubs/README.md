# Azure Event Hubs client library for Python

Azure Event Hubs is a highly scalable publish-subscribe service that can ingest millions of events per second and stream them to multiple consumers. This lets you process and analyze the massive amounts of data produced by your connected devices and applications. Once Event Hubs has collected the data, you can retrieve, transform, and store it by using any real-time analytics provider or with batching/storage adapters. If you would like to know more about Azure Event Hubs, you may wish to review: [What is Event Hubs](https://docs.microsoft.com/en-us/azure/event-hubs/event-hubs-about)?

The Azure Event Hubs client library allows for publishing and consuming of Azure Event Hubs events and may be used to:

- Emit telemetry about your application for business intelligence and diagnostic purposes.
- Publish facts about the state of your application which interested parties may observe and use as a trigger for taking action.
- Observe interesting operations and interactions happening within your business or other ecosystem, allowing loosely coupled systems to interact without the need to bind them together.
- Receive events from one or more publishers, transform them to better meet the needs of your ecosystem, then publish the transformed events to a new stream for consumers to observe.

[Source code](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/eventhub/azure-eventhubs) | [Package (PyPi)](https://pypi.org/project/azure-eventhub/) | [API reference documentation](https://azure.github.io/azure-sdk-for-python) | [Product documentation](https://docs.microsoft.com/en-ca/azure/event-hubs/)

## Getting started

### Install the package

Install the Azure Event Hubs client library for Python with pip:

```
$ pip install --pre azure-eventhub
```

**Prerequisites**

- Python 2.7, 3.5 or later.
- **Microsoft Azure Subscription:**  To use Azure services, including Azure Event Hubs, you'll need a subscription.  If you do not have an existing Azure account, you may sign up for a free trial or use your MSDN subscriber benefits when you [create an account](https://account.windowsazure.com/Home/Index).

- **Event Hubs namespace with an Event Hub:** To interact with Azure Event Hubs, you'll also need to have a namespace and Event Hub  available.  If you are not familiar with creating Azure resources, you may wish to follow the step-by-step guide for [creating an Event Hub using the Azure portal](https://docs.microsoft.com/en-us/azure/event-hubs/event-hubs-create).  There, you can also find detailed instructions for using the Azure CLI, Azure PowerShell, or Azure Resource Manager (ARM) templates to create an Event Hub.

### Authenticate the client

Interaction with Event Hubs starts with an instance of the EventHubClient class. You need the host name, SAS/AAD credential and event hub name to instantiate the client object.

#### Obtain a connection string

For the Event Hubs client library to interact with an Event Hub, it will need to understand how to connect and authorize with it. The easiest means for doing so is to use a connection string, which is created automatically when creating an Event Hubs namespace. If you aren't familiar with shared access policies in Azure, you may wish to follow the step-by-step guide to [get an Event Hubs connection string](https://docs.microsoft.com/en-us/azure/event-hubs/event-hubs-get-connection-string).

#### Create client

There are several ways to instantiate the EventHubClient object and the following code snippets demonstrate two ways:

**Create client from connection string:**

```python
from azure.eventhub import EventHubClient

connection_str = '<< CONNECTION STRING FOR THE EVENT HUBS NAMESPACE >>'
event_hub_path = '<< NAME OF THE EVENT HUB >>'
client = EventHubClient.from_connection_string(connection_str, event_hub_path)
```

- The `from_connection_string` method takes the connection string of the form `Endpoint=sb://<yournamespace>.servicebus.windows.net/;SharedAccessKeyName=<yoursharedaccesskeyname>;SharedAccessKey=<yoursharedaccesskey>` and entity name to your Event Hub instance. You can get the connection string from the [Azure portal](https://docs.microsoft.com/en-us/azure/event-hubs/event-hubs-get-connection-string#get-connection-string-from-the-portal).

**Create client using the azure-identity library:**

```python
from azure.eventhub import EventHubClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()

host = '<< HOSTNAME OF THE EVENT HUB >>'
event_hub_path = '<< NAME OF THE EVENT HUB >>'
client = EventHubClient(host, event_hub_path, credential)
```

- This constructor takes the host name and entity name of your Event Hub instance and credential that implements the TokenCredential interface. There are implementations of the TokenCredential interface available in the [azure-identity package](https://pypi.org/project/azure-identity/). The host name is of the format `<yournamespace.servicebus.windows.net>`.

## Key concepts

- An **Event Hub client** is the primary interface for developers interacting with the Event Hubs client library, allowing for inspection of Event Hub metadata and providing a guided experience towards specific Event Hub operations such as the creation of producers and consumers.

- An **Event Hub producer** is a source of telemetry data, diagnostics information, usage logs, or other log data, as part of an embedded device solution, a mobile device application, a game title running on a console or other device, some client or server based business solution, or a web site.

- An **Event Hub consumer** picks up such information from the Event Hub and processes it. Processing may involve aggregation, complex computation, and filtering. Processing may also involve distribution or storage of the information in a raw or transformed fashion. Event Hub consumers are often robust and high-scale platform infrastructure parts with built-in analytics capabilities, like Azure Stream Analytics, Apache Spark, or Apache Storm.

- A **partition** is an ordered sequence of events that is held in an Event Hub. Azure Event Hubs provides message streaming through a partitioned consumer pattern in which each consumer only reads a specific subset, or partition, of the message stream. As newer events arrive, they are added to the end of this sequence. The number of partitions is specified at the time an Event Hub is created and cannot be changed.

- A **consumer group** is a view of an entire Event Hub. Consumer groups enable multiple consuming applications to each have a separate view of the event stream, and to read the stream independently at their own pace and from their own position. There can be at most 5 concurrent readers on a partition per consumer group; however it is recommended that there is only one active consumer for a given partition and consumer group pairing. Each active reader receives all of the events from its partition; if there are multiple readers on the same partition, then they will receive duplicate events.

For more concepts and deeper discussion, see: [Event Hubs Features](https://docs.microsoft.com/en-us/azure/event-hubs/event-hubs-features). Also, the concepts for AMQP are well documented in [OASIS Advanced Messaging Queuing Protocol (AMQP) Version 1.0](http://docs.oasis-open.org/amqp/core/v1.0/os/amqp-core-overview-v1.0-os.html).

## Examples

The following sections provide several code snippets covering some of the most common Event Hubs tasks, including:

- [Inspect an Event Hub](#inspect-an-event-hub)
- [Publish events to an Event Hub](#publish-events-to-an-event-hub)
- [Consume events from an Event Hub](#consume-events-from-an-event-hub)
- [Async publish events to an Event Hub](#async-publish-events-to-an-event-hub)
- [Async consume events from an Event Hub](#async-consume-events-from-an-event-hub)
- [Consume events using an Event Processor](#consume-events-using-an-event-processor)

### Inspect an Event Hub

Get the partition ids of an Event Hub.

```python
from azure.eventhub import EventHubClient

connection_str = '<< CONNECTION STRING FOR THE EVENT HUBS NAMESPACE >>'
event_hub_path = '<< NAME OF THE EVENT HUB >>'
client = EventHubClient.from_connection_string(connection_str, event_hub_path)
partition_ids = client.get_partition_ids()
```

### Publish events to an Event Hub

Publish events to an Event Hub.

```python
from azure.eventhub import EventHubClient, EventData

connection_str = '<< CONNECTION STRING FOR THE EVENT HUBS NAMESPACE >>'
event_hub_path = '<< NAME OF THE EVENT HUB >>'
client = EventHubClient.from_connection_string(connection_str, event_hub_path)
producer = client.create_producer(partition_id="0")

try:
 	event_list = []
 	for i in range(10):
 		event_list.append(EventData(b"A single event"))

 	with producer:
 	    producer.send(event_list)
except:
	raise
finally:
    pass
```

### Consume events from an Event Hub

Consume events from an Event Hub.

```python
import logging
from azure.eventhub import EventHubClient, EventData, EventPosition

connection_str = '<< CONNECTION STRING FOR THE EVENT HUBS NAMESPACE >>'
event_hub_path = '<< NAME OF THE EVENT HUB >>'
client = EventHubClient.from_connection_string(connection_str, event_hub_path)
consumer = client.create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition("-1"))

try:
    logger = logging.getLogger("azure.eventhub")
    with consumer:
        received = consumer.receive(max_batch_size=100, timeout=5)
        for event_data in received:
            logger.info("Message received:{}".format(event_data))
except:
    raise
finally:
    pass
```

### Async publish events to an Event Hub

Publish events to an Event Hub asynchronously.

```python
from azure.eventhub.aio import EventHubClient
from azure.eventhub import EventData

connection_str = '<< CONNECTION STRING FOR THE EVENT HUBS NAMESPACE >>'
event_hub_path = '<< NAME OF THE EVENT HUB >>'
client = EventHubClient.from_connection_string(connection_str, event_hub_path)
producer = client.create_producer(partition_id="0")

try:
 	event_list = []
 	for i in range(10):
 		event_list.append(EventData(b"A single event"))

	async with producer:
		await producer.send(event_list)
except:
	raise
finally:
    pass
```

### Async consume events from an Event Hub

Consume events asynchronously from an EventHub.

```python
import logging
from azure.eventhub.aio import EventHubClient
from azure.eventhub import EventData, EventPosition

connection_str = '<< CONNECTION STRING FOR THE EVENT HUBS NAMESPACE >>'
event_hub_path = '<< NAME OF THE EVENT HUB >>'
client = EventHubClient.from_connection_string(connection_str, event_hub_path)
consumer = client.create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition("-1"))

try:
    logger = logging.getLogger("azure.eventhub")
    async with consumer:
        received = await consumer.receive(max_batch_size=100, timeout=5)
        for event_data in received:
            logger.info("Message received:{}".format(event_data))
except:
    raise
finally:
    pass
```

### Consume events using an Event Processor

Using an `EventHubConsumer` to consume events like in the previous examples puts the responsibility of storing the checkpoints (the last processed event) on the user. Checkpoints are important for restarting the task of processing events from the right position in a partition. Ideally, you would also want to run multiple programs targeting different partitions with some load balancing. This is where an `EventProcessor` can help.

The `EventProcessor` will delegate the processing of events to a `PartitionProcessor` that you provide, allowing you to focus on business logic while the processor holds responsibility for managing the underlying consumer operations including checkpointing and load balancing.

While load balancing is a feature we will be adding in the next update, you can see how to use the `EventProcessor` in the below example, where we use an in memory `PartitionManager` that does checkpointing in memory.

```python
import asyncio

from azure.eventhub.aio import EventHubClient
from azure.eventhub.eventprocessor import EventProcessor, PartitionProcessor, Sqlite3PartitionManager

connection_str = '<< CONNECTION STRING FOR THE EVENT HUBS NAMESPACE >>'

async def do_operation(event):
    # do some sync or async operations. If the operation is i/o intensive, async will have better performance
    print(event)

class MyPartitionProcessor(PartitionProcessor):
    def __init__(self, checkpoint_manager):
        super(MyPartitionProcessor, self).__init__(checkpoint_manager)

    async def process_events(self, events):
        if events:
            await asyncio.gather(*[do_operation(event) for event in events])
            await self._checkpoint_manager.update_checkpoint(events[-1].offset, events[-1].sequence_number)

def partition_processor_factory(checkpoint_manager):
    return MyPartitionProcessor(checkpoint_manager)

async def main():
    client = EventHubClient.from_connection_string(connection_str, receive_timeout=5, retry_total=3)
    partition_manager = Sqlite3PartitionManager()  # in-memory PartitionManager
    try:
        event_processor = EventProcessor(client, "$default", MyPartitionProcessor, partition_manager)
        # You can also define a callable object for creating PartitionProcessor like below:
        # event_processor = EventProcessor(client, "$default", partition_processor_factory, partition_manager)
        asyncio.ensure_future(event_processor.start())
        await asyncio.sleep(60)
        await event_processor.stop()
    finally:
        await partition_manager.close()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
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
- **EventHubError:** All other Eventhubs related errors. It is also the root error class of all the above mentioned errors.

## Next steps

### Examples

These are the samples in our repo demonstraing the usage of the library.

- [./examples/send.py](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventhub/azure-eventhubs/examples/send.py) - use producer to publish events
- [./examples/recv.py](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventhub/azure-eventhubs/examples/recv.py) - use consumer to consume events
- [./examples/async_examples/send_async.py](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventhub/azure-eventhubs/examples/async_examples/send_async.py) - async/await support of a producer
- [./examples/async_examples/recv_async.py](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventhub/azure-eventhubs/examples/async_examples/recv_async.py) - async/await support of a consumer
- [./examples/eventprocessor/event_processor_example.py](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventhub/azure-eventhubs/examples/eventprocessor/event_processor_example.py) - event processor

### Documentation

Reference documentation is available at https://azure.github.io/azure-sdk-for-python.

### Logging

- Enable `azure.eventhub` logger to collect traces from the library.
- Enable `uamqp` logger to collect traces from the underlying uAMQP library.
- Enable AMQP frame level trace by setting `network_tracing=True` when creating the client.

### Provide Feedback

If you encounter any bugs or have suggestions, please file an issue in the [Issues](https://github.com/Azure/azure-sdk-for-python/issues) section of the project.

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

![Impressions](https://azure-sdk-impressions.azurewebsites.net/api/impressions/azure-sdk-for-python/sdk/eventhub/azure-eventhubs/README.png)