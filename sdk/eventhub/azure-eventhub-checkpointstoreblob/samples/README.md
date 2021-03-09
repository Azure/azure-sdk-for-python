---
page_type: sample
languages:
  - python
products:
  - azure
  - azure-event-hubs
urlFragment: eventhub-checkpointstore-samples
---

# Azure Event Hubs client library samples with persistent checkpointing for Python

These sample programs show how to use the sync Python client libraries for Azure Event Hubs in some common scenarios.

| **File Name**                                                | **Description**                                                                                                                                                  |
| ------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [receive_events_using_checkpoint_store.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/eventhub/azure-eventhub-checkpointstoreblob/samples/receive_events_using_checkpoint_store.py)        | Demonstrates how to use the async BlobCheckpointStore with EventHubConsumerClient to process events from all partitions of a consumer group in an Event Hubs instance. |
| [receive_events_using_checkpoint_store_storage_api_version.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/eventhub/azure-eventhub-checkpointstoreblob/samples/receive_events_using_checkpoint_store_storage_api_version.py) | Demonstrates how to use a specific Azure Storage Blobs API version with BlobCheckpointStore.                                                                     |

## Prerequisites
- Python2.7, Python 3.5.3 or later.
- **Microsoft Azure Subscription:**  To use Azure services, including Azure Event Hubs, you'll need a subscription. If you do not have an existing Azure account, you may sign up for a free trial or use your MSDN subscriber benefits when you [create an account](https://azure.microsoft.com/).

- **Event Hubs namespace with an Event Hub:** To interact with Azure Event Hubs, you'll also need to have a namespace and Event Hub  available.  If you are not familiar with creating Azure resources, you may wish to follow the step-by-step guide for [creating an Event Hub using the Azure portal](https://docs.microsoft.com/azure/event-hubs/event-hubs-create).  There, you can also find detailed instructions for using the Azure CLI, Azure PowerShell, or Azure Resource Manager (ARM) templates to create an Event Hub.

- **Azure Storage Account:** You'll need to have an Azure Storage Account and create a Azure Blob Storage Block Container to store the checkpoint data with blobs. You may follow the guide [creating an Azure Block Blob Storage Account](https://docs.microsoft.com/azure/storage/blobs/storage-blob-create-account-block-blob).

## Setup

1. Install the Azure Event Hubs client library for Python with [pip](https://pypi.org/project/pip/):
```bash
pip install azure-eventhub-checkpointstoreblob
```
2. Clone or download this sample repository.
3. Open the sample folder in Visual Studio Code or your IDE of choice.

## Running the samples

1. Open a terminal window and `cd` to the directory that the samples are saved in.
2. Set the environment variables specified in the sample file you wish to run.
3. Follow the usage described in the file.

## Next steps

Check out the [API reference documentation](https://azuresdkdocs.blob.core.windows.net/$web/python/azure-eventhub/5.3.1/azure.eventhub.html) to learn more about
what you can do with the Azure Event Hubs client library.
