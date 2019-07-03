# Azure Storage Queues client library for Python

Azure Storage Queues is a service for storing large numbers of messages that can be accessed from anywhere in the world via authenticated calls using HTTP or HTTPS. A single queue message can be up to 64 KB in size, and a queue can contain millions of messages, up to the total capacity limit of a storage account.

Common uses of Queue storage include:

* Creating a backlog of work to process asynchronously
* Passing messages between different parts of a distributed application

[Source code](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-queue/azure/storage/queue) | [Package (PyPi)](https://pypi.org/project/azure-storage-queue/) | [API reference documentation](https://docs.microsoft.com/rest/api/storageservices/queue-service-rest-api) | [Product documentation](https://docs.microsoft.com/azure/storage/) | [Samples](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-queue/tests)

## Getting started

### Install the package
Install the Azure Storage Queue client library for Python with [pip](https://pypi.org/project/pip/):

```bash
pip install azure-storage-queue
```

**Prerequisites**: You must have an [Azure subscription](https://azure.microsoft.com/free/), and a
[Storage Account](https://docs.microsoft.com/azure/storage/common/storage-account-overview) to use this package.

To create a Storage Account, you can use the [Azure Portal](https://docs.microsoft.com/azure/storage/common/storage-quickstart-create-account?tabs=azure-portal),
[Azure PowerShell](https://docs.microsoft.com/azure/storage/common/storage-quickstart-create-account?tabs=azure-powershell) or [Azure CLI](https://docs.microsoft.com/azure/storage/common/storage-quickstart-create-account?tabs=azure-cli):

```bash
az storage account create -n MyStorageAccountName -g MyResourceGroupName
```

Requires Python 2.7, 3.5 or later to use this package.

### Authenticate the client

Interaction with Storage Queues starts with an instance of the QueueServiceClient class. You need an existing storage account, its URL, and a credential to instantiate the client object.

#### Get credentials

To authenticate the client you have a few options:
1. Use a SAS token string 
2. Use an account shared access key
3. Use a token credential from [azure.identity](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/identity/azure-identity)

Alternatively, you can authenticate with a storage connection string using the `from_connection_string` method. See example: [Client creation with a connection string](#client-creation-with-a-connection-string).

You can omit the credential if your account URL already has a SAS token.

#### Create client

Once you have your account URL and credentials ready, you can create the QueueServiceClient:

```python
from azure.storage.queue import QueueServiceClient

service = QueueServiceClient(account_url="https://<my-storage-account-name>.queue.core.windows.net/", credential=credential)
```

## Key concepts

The Queue service contains the following components:
 
* The storage account
* A queue which contains a set of messages
* A message, in any format, of up to 64 KB

#### Clients

The Storage Queues SDK provides two different clients to interact with the Queues Service:
1. **QueueServiceClient** - this client interacts with the Queue Service at the account level. 
    It provides operations to retrieve and configure the account properties
    as well as list, create, and delete queues within the account.
    For operations relating to a specific queue, a client for that entity
    can also be retrieved using the `get_queue_client` function.
2. **QueueClient** - this client represents interaction with a specific
    queue, although that queue need not exist yet. It provides operations to create, delete, or
    configure queues and includes operations to enqueue, receive, peak, delete, and update messages in the queue.

#### Messages

Once you've initialized a Client, you can use the following operations to work with the messages in the queue:
* **Enqueue** - Adds a message to the queue and optionally sets a visibility timeout for the message.
* **Receive** - Retrieves a message from the queue and makes it invisible to other consumers.
* **Peek** - Retrieves a message from the front of the queue, without changing the message visibility.
* **Update** - Updates the visibility timeout of a message and/or the message contents.
* **Delete** - Deletes a specified message from the queue.
* **Clear** - Clears all messages from the queue.


## Examples

The following sections provide several code snippets covering some of the most common Storage Queue tasks, including:

* [Client creation with a connection string](#client-creation-with-a-connection-string)
* [Create a queue](#create-a-queue)
* [Enqueue messages](#enqueue-messages)
* [Receive messages](#receive-messages)


### Client creation with a connection string
Create the QueueServiceClient using the connection string to your Azure Storage account.

```python
from azure.storage.queue import QueueServiceClient

service = QueueServiceClient.from_connection_string(conn_str="my_connection_string")
```

### Create a queue
Create a queue in your storage account.

```python
from azure.storage.queue import QueueClient

queue = QueueClient.from_connection_string(conn_str="my_connection_string", queue="myqueue")
queue.create_queue()
```
### Enqueue messages
Enqueue a message in your queue.

```python
from azure.storage.queue import QueueClient

queue = QueueClient.from_connection_string(conn_str="my_connection_string", queue="myqueue")
queue.enqueue_message("I'm using queues!")
queue.enqueue_message("This is my second message")
```

### Receive messages
Receive messages from your queue.

```python
from azure.storage.queue import QueueClient

queue = QueueClient.from_connection_string(conn_str="my_connection_string", queue="myqueue")
response = queue.receive_messages()

for message in response:
    print(message.content)

# Printed messages from the front of the queue
# >>I'm using queues!   
# >>This is my second message
```

## Troubleshooting
Storage Queue clients raise exceptions defined in [Azure Core](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/docs/exceptions.md).

All Queue service operations will throw a StorageErrorException on failure with helpful [error codes](https://docs.microsoft.com/rest/api/storageservices/queue-service-error-codes).

## Next steps
### More sample code

Get started with our [Queue samples](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-queue/tests).

Several Storage Queues Python SDK samples are available to you in the SDK's GitHub repository. These samples provide example code for additional scenarios commonly encountered while working with Storage Queues:

* [`test_queue_samples_hello_world.py`](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-queue/tests/test_queue_samples_hello_world.py) - Examples found in this article:
    * Client creation
    * Create a queue
    * Enqueue messages
    * Receive messages

* [`test_queue_samples_authentication.py`](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-queue/tests/test_queue_samples_authentication.py) - Examples for authenticating and creating the client:
    * From a connection string
    * From a shared access key
    * From a shared access signature token
    * From active directory

* [`test_queue_samples_service.py`](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-queue/tests/test_queue_samples_service.py) - Examples for interacting with the queue service:
    * Get and set service properties
    * List queues in a storage account
    * Create and delete a queue from the service
    * Get the QueueClient

* [`test_queue_samples_message.py`](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-queue/tests/test_queue_samples_message.py) - Examples for working with queues and messages:
    * Set an access policy
    * Get and set queue metadata
    * Enqueue and receive messages
    * Delete specified messages and clear all messages
    * Peek and update messages
    
### Additional documentation

For more extensive documentation on the Azure Storage Queues, see the [Azure Storage Queues documentation](https://docs.microsoft.com/azure/storage/) on docs.microsoft.com.


## Contributing
This project welcomes contributions and suggestions.  Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.