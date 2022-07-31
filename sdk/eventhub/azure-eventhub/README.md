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

[Source code](https://github.com/Azure/azure-sdk-for-python/tree/feature/eventhub/pyproto/sdk/eventhub/azure-eventhub/) | [Package (PyPi)](https://pypi.org/project/azure-eventhub/) | [API reference documentation][api_reference] | [Product documentation](https://docs.microsoft.com/azure/event-hubs/) | [Samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/eventhub/azure-eventhub/samples)

## _Disclaimer_

_Azure SDK Python packages support for Python 2.7 has ended 01 January 2022. For more information and questions, please refer to https://github.com/Azure/azure-sdk-for-python/issues/20691_

_This version is our first efforts to build an Azure Event Hubs client library based on pure python implemented AMQP stack.
Please refer to the changelog for more details._

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
$ pip install azure-eventhub==5.8.0a4
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

### Consume events and save checkpoints using a checkpoint store

`EventHubConsumerClient` is a high level construct which allows you to receive events from multiple partitions at once
and load balance with other consumers using the same Event Hub and consumer group.

This also allows the user to track progress when events are processed using checkpoints.

A checkpoint is meant to represent the last successfully processed event by the user from a particular partition of
a consumer group in an Event Hub instance. The `EventHubConsumerClient` uses an instance of `CheckpointStore` to update checkpoints
and to store the relevant information required by the load balancing algorithm.

Search pypi with the prefix `azure-eventhub-checkpointstore` to
find packages that support this and use the `CheckpointStore` implementation from one such package.

In the below example, we create an instance of `EventHubConsumerClient` and use a `BlobCheckpointStore`. You need
to [create an Azure Storage account](https://docs.microsoft.com/azure/storage/common/storage-quickstart-create-account?tabs=azure-portal)
and a [Blob Container](https://docs.microsoft.com/azure/storage/blobs/storage-quickstart-blobs-portal#create-a-container) to run the code.

[Azure Blob Storage Checkpoint Store Sync](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventhub/azure-eventhub-checkpointstoreblob)
is one of the `CheckpointStore` implementations we provide that applies Azure Blob Storage as the persistent store.


```python
from azure.eventhub import EventHubConsumerClient
from azure.eventhub.extensions.checkpointstoreblob import BlobCheckpointStore

connection_str = '<< CONNECTION STRING FOR THE EVENT HUBS NAMESPACE >>'
consumer_group = '<< CONSUMER GROUP >>'
eventhub_name = '<< NAME OF THE EVENT HUB >>'
storage_connection_str = '<< CONNECTION STRING FOR THE STORAGE >>'
container_name = '<<NAME OF THE BLOB CONTAINER>>'

def on_event(partition_context, event):
    # do something
    partition_context.update_checkpoint(event)  # Or update_checkpoint every N events for better performance.

def receive(client):
    client.receive(
        on_event=on_event,
        starting_position="-1",  # "-1" is from the beginning of the partition.
    )

def main():
    checkpoint_store = BlobCheckpointStore.from_connection_string(storage_connection_str, container_name)
    client = EventHubConsumerClient.from_connection_string(
        connection_str,
        consumer_group,
        eventhub_name=eventhub_name,
        checkpoint_store=checkpoint_store,  # For load balancing and checkpoint. Leave None for no load balancing
    )
    with client:
        receive(client)

if __name__ == '__main__':
    main()
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

## Troubleshooting

See the `azure-eventhubs` [troubleshooting guide](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventhub/azure-eventhub/TROUBLESHOOTING.md) for details on how to diagnose various failure scenarios.

## Next steps

### More sample code

Please take a look at the [samples](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventhub/azure-eventhub/samples) directory for detailed examples of how to use this library to send and receive events to/from Event Hubs.

### Documentation

Reference documentation is available [here](https://azuresdkdocs.blob.core.windows.net/$web/python/azure-eventhub/latest/azure.eventhub.html).

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
