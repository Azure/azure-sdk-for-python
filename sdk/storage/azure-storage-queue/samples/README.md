---
page_type: sample
languages:
  - python
products:
  - azure
  - azure-storage
urlFragment: storage-queue-samples
---

# Azure Storage Queue client library for Python Samples

These are code samples that show common scenario operations with the Azure Storage Queue client library.
The async versions of the samples (the python sample files appended with `_async`) show asynchronous operations
with queues and require Python 3.5 or later.

## Contents

* [queue_samples_hello_world.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-queue/samples/queue_samples_hello_world.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-queue/samples/queue_samples_hello_world_async.py)) - Examples for getting started with queues:
    * Client creation
    * Create a queue
    * Send messages
    * Receive messages

* [queue_samples_authentication.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-queue/samples/queue_samples_authentication.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-queue/samples/queue_samples_authentication_async.py)) - Examples for authenticating and creating the client:
    * From a connection string
    * From a shared access key
    * From a shared access signature token
    * From Azure Active Directory

* [queue_samples_service.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-queue/samples/queue_samples_service.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-queue/samples/queue_samples_service_async.py)) - Examples for interacting with the queue service:
    * Get and set service properties
    * List queues in a storage account
    * Create and delete a queue from the service
    * Get the QueueClient

* [queue_samples_message.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-queue/samples/queue_samples_message.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-queue/samples/queue_samples_message_async.py)) - Examples for working with queues and messages:
    * Set an access policy
    * Get and set queue metadata
    * Send and receive messages
    * Delete specified messages and clear all messages
    * Peek and update messages

* [network_activity_logging.py](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/storage/azure-storage-queue/samples/network_activity_logging.py) - Shows how to enable logging to console for the Storage Queues library:
    * Setting up the logger and configuring output to STDOUT
    * Setting the level on the logger
    * Enabling the logger for the service and printing any logging messages

## Prerequisites
* Python 2.7, or 3.5 or later is required to use this package (3.5 or later if using asyncio)
* You must have an [Azure subscription](https://azure.microsoft.com/free/) and an
[Azure storage account](https://docs.microsoft.com/azure/storage/common/storage-account-overview) to run these samples.

## Setup

1. Install the Azure Storage Queues client library for Python with [pip](https://pypi.org/project/pip/):

```bash
pip install azure-storage-queue
```

2. Clone or download this sample repository
3. Open the sample folder in Visual Studio Code or your IDE of choice.

## Running the samples

1. Open a terminal window and `cd` to the directory that the samples are saved in.
2. Set the environment variables specified in the sample file you wish to run.
3. Follow the usage described in the file, e.g. `python queue_samples_hello_world.py`

## Next steps

Check out the [API reference documentation](https://aka.ms/azsdk-python-storage-queue-ref) to learn more about
what you can do with the Azure Storage Queues client library.