# Azure EventHubs Checkpoint Store client library for Python using Storage Blobs

Azure EventHubs Checkpoint Store is used for storing checkpoints while processing events from Azure Event Hubs.
This Checkpoint Store package works as a plug-in package to `EventHubConsumerClient`. It uses Azure Storage Blob as the persistent store for maintaining checkpoints and partition ownership information.

Please note that this is an async library, for sync version of the Azure EventHubs Checkpoint Store client library, please refer to [azure-eventhub-checkpointstoreblob](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventhub/azure-eventhub-checkpointstoreblob).

[Source code](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventhub/azure-eventhub-checkpointstoreblob-aio/) | [Package (PyPi)](https://pypi.org/project/azure-eventhub-checkpointstoreblob-aio/) | [API reference documentation](https://azuresdkdocs.blob.core.windows.net/$web/python/azure-eventhub/5.3.1/azure.eventhub.aio.html#azure.eventhub.aio.CheckpointStore) | [Azure Eventhubs documentation](https://docs.microsoft.com/azure/event-hubs/) | [Azure Storage documentation](https://docs.microsoft.com/azure/storage/)

## Getting started

### Prerequisites

- Python 3.5.3 or later.
- **Microsoft Azure Subscription:**  To use Azure services, including Azure Event Hubs, you'll need a subscription.  If you do not have an existing Azure account, you may sign up for a free trial or use your MSDN subscriber benefits when you [create an account](https://azure.microsoft.com/).

- **Event Hubs namespace with an Event Hub:** To interact with Azure Event Hubs, you'll also need to have a namespace and Event Hub  available.  If you are not familiar with creating Azure resources, you may wish to follow the step-by-step guide for [creating an Event Hub using the Azure portal](https://docs.microsoft.com/azure/event-hubs/event-hubs-create).  There, you can also find detailed instructions for using the Azure CLI, Azure PowerShell, or Azure Resource Manager (ARM) templates to create an Event Hub.

- **Azure Storage Account:** You'll need to have an Azure Storage Account and create a Azure Blob Storage Block Container to store the checkpoint data with blobs. You may follow the guide [creating an Azure Block Blob Storage Account](https://docs.microsoft.com/azure/storage/blobs/storage-blob-create-account-block-blob).

### Install the package

```
$ pip install azure-eventhub-checkpointstoreblob-aio
```

## Key concepts

### Checkpointing

Checkpointing is a process by which readers mark or commit their position within a partition event sequence.
Checkpointing is the responsibility of the consumer and occurs on a per-partition basis within a consumer group.
This responsibility means that for each consumer group, each partition reader must keep track of its current position
in the event stream, and can inform the service when it considers the data stream complete. If a reader disconnects from
a partition, when it reconnects it begins reading at the checkpoint that was previously submitted by the last reader of
that partition in that consumer group. When the reader connects, it passes the offset to the event hub to specify the
location at which to start reading. In this way, you can use checkpointing to both mark events as "complete" by
downstream applications, and to provide resiliency if a failover between readers running on different machines occurs.
It is possible to return to older data by specifying a lower offset from this checkpointing process. Through this
mechanism, checkpointing enables both failover resiliency and event stream replay.

### Offsets & sequence numbers
Both offset & sequence number refer to the position of an event within a partition. You can think of them as a
client-side cursor. The offset is a byte numbering of the event. The offset/sequence number enables an event consumer
(reader) to specify a point in the event stream from which they want to begin reading events. You can specify a
timestamp such that you receive events enqueued only after the given timestamp. Consumers are responsible for
storing their own offset values outside of the Event Hubs service. Within a partition, each event includes an offset,
sequence number and the timestamp of when it was enqueued.

## Examples
- [Create an Azure EventHubs `EventHubConsumerClient`](#create-an-eventhubconsumerclient)
- [Consume events using a `BlobCheckpointStore`](#consume-events-using-a-blobcheckpointstore-to-do-checkpoint)

### Create an `EventHubConsumerClient`
The easiest way to create a `EventHubConsumerClient` is to use a connection string.
```python
from azure.eventhub.aio import EventHubConsumerClient
eventhub_client = EventHubConsumerClient.from_connection_string("my_eventhub_namespace_connection_string", "my_consumer_group", eventhub_name="my_eventhub")
```
For other ways of creating a `EventHubConsumerClient`, refer to [EventHubs library](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventhub/azure-eventhub) for more details.

### Consume events using a `BlobCheckpointStore` to do checkpoint
```python
import asyncio

from azure.eventhub.aio import EventHubConsumerClient
from azure.eventhub.extensions.checkpointstoreblobaio import BlobCheckpointStore

connection_str = '<< CONNECTION STRING FOR THE EVENT HUBS NAMESPACE >>'
consumer_group = '<< CONSUMER GROUP >>'
eventhub_name = '<< NAME OF THE EVENT HUB >>'
storage_connection_str = '<< CONNECTION STRING OF THE STORAGE >>'
container_name = '<< STORAGE CONTAINER NAME>>'

async def on_event(partition_context, event):
    # Put your code here.
    await partition_context.update_checkpoint(event)  # Or update_checkpoint every N events for better performance.

async def main():
    checkpoint_store = BlobCheckpointStore.from_connection_string(
        storage_connection_str,
        container_name
    )
    client = EventHubConsumerClient.from_connection_string(
        connection_str,
        consumer_group,
        eventhub_name=eventhub_name,
        checkpoint_store=checkpoint_store,
    )

    async with client:
        await client.receive(on_event)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
```

#### Use `BlobCheckpointStore` with a different version of Azure Storage Service API
Some environments have different versions of Azure Storage Service API. 
`BlobCheckpointStore` by default uses the Storage Service API version 2019-07-07. To use it against a different
version, specify `api_version` when you create the `BlobCheckpointStore` object.


## Troubleshooting

### General
Enabling logging will be helpful to do trouble shooting.

### Logging

- Enable `azure.eventhub.extensions.checkpointstoreblobaio` logger to collect traces from the library.
- Enable `azure.eventhub` logger to collect traces from the main azure-eventhub library.
- Enable `azure.eventhub.extensions.checkpointstoreblobaio._vendor.storage` logger to collect traces from azure storage blob library.
- Enable `uamqp` logger to collect traces from the underlying uAMQP library.
- Enable AMQP frame level trace by setting `logging_enable=True` when creating the client.

## Next steps

### More sample code

Get started with our [EventHubs Checkpoint Store async samples](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventhub/azure-eventhub-checkpointstoreblob-aio/samples).

- [receive_events_using_checkpoint_store_async.py](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventhub/azure-eventhub-checkpointstoreblob-aio/samples/receive_events_using_checkpoint_store_async.py) - EventHubConsumerClient with blob checkpoint store example
- [receive_events_using_checkpoint_store_storage_api_version_async.py](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventhub/azure-eventhub-checkpointstoreblob-aio/samples/receive_events_using_checkpoint_store_storage_api_version_async.py) - EventHubConsumerClient with blob checkpoint store and storage version example

### Documentation

Reference documentation is available [here](https://azuresdkdocs.blob.core.windows.net/$web/python/azure-eventhub/5.3.1/azure.eventhub.aio.html#azure.eventhub.aio.CheckpointStore).

### Provide Feedback

If you encounter any bugs or have suggestions, please file an issue in the [Issues](https://github.com/Azure/azure-sdk-for-python/issues) section of the project.

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

![Impressions](https://azure-sdk-impressions.azurewebsites.net/api/impressions/azure-sdk-for-python/sdk/eventhub/azure-eventhub-checkpointstoreblob-aio/README.png)
