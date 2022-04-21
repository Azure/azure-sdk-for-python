# Azure Storage Queues client library for Python

Azure Queue storage is a service for storing large numbers of messages that can be accessed from anywhere in the world via authenticated calls using HTTP or HTTPS. A single queue message can be up to 64 KiB in size, and a queue can contain millions of messages, up to the total capacity limit of a storage account.

Common uses of Queue storage include:

* Creating a backlog of work to process asynchronously
* Passing messages between different parts of a distributed application

[Source code](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-queue/azure/storage/queue) | [Package (PyPI)](https://pypi.org/project/azure-storage-queue/) | [API reference documentation](https://aka.ms/azsdk-python-storage-queue-ref) | [Product documentation](https://docs.microsoft.com/azure/storage/) | [Samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-queue/samples)

## Getting started

### Prerequisites
* Python 3.6 or later is required to use this package.
* You must have an [Azure subscription](https://azure.microsoft.com/free/) and an
[Azure storage account](https://docs.microsoft.com/azure/storage/common/storage-account-overview) to use this package.

### Install the package
Install the Azure Storage Queues client library for Python with [pip](https://pypi.org/project/pip/):

```bash
pip install azure-storage-queue
```

### Create a storage account
If you wish to create a new storage account, you can use the
[Azure Portal](https://docs.microsoft.com/azure/storage/common/storage-quickstart-create-account?tabs=azure-portal),
[Azure PowerShell](https://docs.microsoft.com/azure/storage/common/storage-quickstart-create-account?tabs=azure-powershell),
or [Azure CLI](https://docs.microsoft.com/azure/storage/common/storage-quickstart-create-account?tabs=azure-cli):

```bash
# Create a new resource group to hold the storage account -
# if using an existing resource group, skip this step
az group create --name my-resource-group --location westus2

# Create the storage account
az storage account create -n my-storage-account-name -g my-resource-group
```

### Create the client
The Azure Storage Queues client library for Python allows you to interact with three types of resources: the storage
account itself, queues, and messages. Interaction with these resources starts with an instance of a [client](#clients).
To create a client object, you will need the storage account's queue service endpoint URL and a credential that allows
you to access the storage account:

```python
from azure.storage.queue import QueueServiceClient

service = QueueServiceClient(account_url="https://<my-storage-account-name>.queue.core.windows.net/", credential=credential)
```

#### Looking up the account URL
You can find the storage account's queue service URL using the
[Azure Portal](https://docs.microsoft.com/azure/storage/common/storage-account-overview#storage-account-endpoints),
[Azure PowerShell](https://docs.microsoft.com/powershell/module/az.storage/get-azstorageaccount),
or [Azure CLI](https://docs.microsoft.com/cli/azure/storage/account?view=azure-cli-latest#az-storage-account-show):

```bash
# Get the queue service URL for the storage account
az storage account show -n my-storage-account-name -g my-resource-group --query "primaryEndpoints.queue"
```

#### Types of credentials
The `credential` parameter may be provided in a number of different forms, depending on the type of
[authorization](https://docs.microsoft.com/azure/storage/common/storage-auth) you wish to use:
1. To use a [shared access signature (SAS) token](https://docs.microsoft.com/azure/storage/common/storage-sas-overview),
   provide the token as a string. If your account URL includes the SAS token, omit the credential parameter.
   You can generate a SAS token from the Azure Portal under "Shared access signature" or use one of the `generate_sas()`
   functions to create a sas token for the storage account or queue:

    ```python
    from datetime import datetime, timedelta
    from azure.storage.queue import QueueServiceClient, generate_account_sas, ResourceTypes, AccountSasPermissions

    sas_token = generate_account_sas(
        account_name="<storage-account-name>",
        account_key="<account-access-key>",
        resource_types=ResourceTypes(service=True),
        permission=AccountSasPermissions(read=True),
        start=datetime.utcnow(),
        expiry=datetime.utcnow() + timedelta(hours=1)
    )

    queue_service_client = QueueServiceClient(account_url="https://<my_account_name>.queue.core.windows.net", credential=sas_token)
    ```

2. To use a storage account [shared key](https://docs.microsoft.com/rest/api/storageservices/authenticate-with-shared-key/)
   (aka account key or access key), provide the key as a string. This can be found in the Azure Portal under the "Access Keys"
   section or by running the following Azure CLI command:

    ```az storage account keys list -g MyResourceGroup -n MyStorageAccount```

    Use the key as the credential parameter to authenticate the client:
    ```python
    from azure.storage.queue import QueueServiceClient
    service = QueueServiceClient(account_url="https://<my_account_name>.queue.core.windows.net", credential="<account_access_key>")
    ```

3. To use an [Azure Active Directory (AAD) token credential](https://docs.microsoft.com/azure/storage/common/storage-auth-aad),
   provide an instance of the desired credential type obtained from the
   [azure-identity](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#credentials) library.
   For example, [DefaultAzureCredential](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#defaultazurecredential)
   can be used to authenticate the client.

   This requires some initial setup:
   * [Install azure-identity](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#install-the-package)
   * [Register a new AAD application](https://docs.microsoft.com/azure/active-directory/develop/quickstart-register-app) and give permissions to access Azure Storage
   * [Grant access](https://docs.microsoft.com/azure/storage/common/storage-auth-aad-rbac-portal) to Azure Queue data with RBAC in the Azure Portal
   * Set the values of the client ID, tenant ID, and client secret of the AAD application as environment variables:
     AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET

   Use the returned token credential to authenticate the client:
    ```python
        from azure.identity import DefaultAzureCredential
        from azure.storage.queue import QueueServiceClient
        token_credential = DefaultAzureCredential()

        queue_service_client = QueueServiceClient(
            account_url="https://<my_account_name>.queue.core.windows.net",
            credential=token_credential
        )
    ```

#### Creating the client from a connection string
Depending on your use case and authorization method, you may prefer to initialize a client instance with a storage
connection string instead of providing the account URL and credential separately. To do this, pass the storage
connection string to the client's `from_connection_string` class method:

```python
from azure.storage.queue import QueueServiceClient

connection_string = "DefaultEndpointsProtocol=https;AccountName=xxxx;AccountKey=xxxx;EndpointSuffix=core.windows.net"
service = QueueServiceClient.from_connection_string(conn_str=connection_string)
```

The connection string to your storage account can be found in the Azure Portal under the "Access Keys" section or by running the following CLI command:

```bash
az storage account show-connection-string -g MyResourceGroup -n MyStorageAccount
```

## Key concepts
The following components make up the Azure Queue Service:
* The storage account itself
* A queue within the storage account, which contains a set of messages
* A message within a queue, in any format, of up to 64 KiB

The Azure Storage Queues client library for Python allows you to interact with each of these components through the
use of a dedicated client object.

### Async Clients 
This library includes a complete async API supported on Python 3.5+. To use it, you must
first install an async transport, such as [aiohttp](https://pypi.org/project/aiohttp/).
See
[azure-core documentation](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#transport)
for more information.

Async clients and credentials should be closed when they're no longer needed. These
objects are async context managers and define async `close` methods.

### Clients
Two different clients are provided to interact with the various components of the Queue Service:
1. [QueueServiceClient](https://aka.ms/azsdk-python-storage-queue-queueserviceclient) -
    this client represents interaction with the Azure storage account itself, and allows you to acquire preconfigured
    client instances to access the queues within. It provides operations to retrieve and configure the account
    properties as well as list, create, and delete queues within the account. To perform operations on a specific queue,
    retrieve a client using the `get_queue_client` method.
2. [QueueClient](https://aka.ms/azsdk-python-storage-queue-queueclient) -
    this client represents interaction with a specific queue (which need not exist yet). It provides operations to
    create, delete, or configure a queue and includes operations to send, receive, peek, delete, and update messages
    within it.

### Messages
* **Send** - Adds a message to the queue and optionally sets a visibility timeout for the message.
* **Receive** - Retrieves a message from the queue and makes it invisible to other consumers.
* **Peek** - Retrieves a message from the front of the queue, without changing the message visibility.
* **Update** - Updates the visibility timeout of a message and/or the message contents.
* **Delete** - Deletes a specified message from the queue.
* **Clear** - Clears all messages from the queue.


## Examples

The following sections provide several code snippets covering some of the most common Storage Queue tasks, including:

* [Creating a queue](#creating-a-queue "Creating a queue")
* [Sending messages](#sending-messages "Sending messages")
* [Receiving messages](#receiving-messages "Receiving messages")

### Creating a queue
Create a queue in your storage account

```python
from azure.storage.queue import QueueClient

queue = QueueClient.from_connection_string(conn_str="<connection_string>", queue_name="my_queue")
queue.create_queue()
```

Use the async client to create a queue
```python
from azure.storage.queue.aio import QueueClient

queue = QueueClient.from_connection_string(conn_str="<connection_string>", queue_name="my_queue")
await queue.create_queue()
```

### Sending messages
Send messages to your queue

```python
from azure.storage.queue import QueueClient

queue = QueueClient.from_connection_string(conn_str="<connection_string>", queue_name="my_queue")
queue.send_message("I'm using queues!")
queue.send_message("This is my second message")
```

Send messages asynchronously

```python
import asyncio
from azure.storage.queue.aio import QueueClient

queue = QueueClient.from_connection_string(conn_str="<connection_string>", queue_name="my_queue")
await asyncio.gather(
    queue.send_message("I'm using queues!"),
    queue.send_message("This is my second message")
)
```

### Receiving messages
Receive and process messages from your queue

```python
from azure.storage.queue import QueueClient

queue = QueueClient.from_connection_string(conn_str="<connection_string>", queue_name="my_queue")
response = queue.receive_messages()

for message in response:
    print(message.content)
    queue.delete_message(message)

# Printed messages from the front of the queue:
# >> I'm using queues!
# >> This is my second message
```

Receive and process messages in batches

```python
from azure.storage.queue import QueueClient

queue = QueueClient.from_connection_string(conn_str="<connection_string>", queue_name="my_queue")
response = queue.receive_messages(messages_per_page=10)

for message_batch in response.by_page():
    for message in message_batch:
        print(message.content)
        queue.delete_message(message)
```

Receive and process messages asynchronously

```python
from azure.storage.queue.aio import QueueClient

queue = QueueClient.from_connection_string(conn_str="<connection_string>", queue_name="my_queue")
response = queue.receive_messages()

async for message in response:
    print(message.content)
    await queue.delete_message(message)
```

## Optional Configuration

Optional keyword arguments that can be passed in at the client and per-operation level.

### Retry Policy configuration

Use the following keyword arguments when instantiating a client to configure the retry policy:

* __retry_total__ (int): Total number of retries to allow. Takes precedence over other counts.
Pass in `retry_total=0` if you do not want to retry on requests. Defaults to 10.
* __retry_connect__ (int): How many connection-related errors to retry on. Defaults to 3.
* __retry_read__ (int): How many times to retry on read errors. Defaults to 3.
* __retry_status__ (int): How many times to retry on bad status codes. Defaults to 3.
* __retry_to_secondary__ (bool): Whether the request should be retried to secondary, if able.
This should only be enabled of RA-GRS accounts are used and potentially stale data can be handled.
Defaults to `False`.

### Other client / per-operation configuration

Other optional configuration keyword arguments that can be specified on the client or per-operation.

**Client keyword arguments:**

* __connection_timeout__ (int): The number of seconds the client will wait to establish a connection to the server.
* __read_timeout__ (int): The number of seconds the client will wait, after the connections has been established, for the server to send a response.
* __transport__ (Any): User-provided transport to send the HTTP request.

**Per-operation keyword arguments:**

* __raw_response_hook__ (callable): The given callback uses the response returned from the service.
* __raw_request_hook__ (callable): The given callback uses the request before being sent to service.
* __client_request_id__ (str): Optional user specified identification of the request.
* __user_agent__ (str): Appends the custom value to the user-agent header to be sent with the request.
* __logging_enable__ (bool): Enables logging at the DEBUG level. Defaults to False. Can also be passed in at
the client level to enable it for all requests.
* __logging_body__ (bool): Enables logging the request and response body. Defaults to False. Can also be passed in at
the client level to enable it for all requests.
* __headers__ (dict): Pass in custom headers as key, value pairs. E.g. `headers={'CustomValue': value}`


## Troubleshooting
### General
Storage Queue clients raise exceptions defined in [Azure Core](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/README.md).

This list can be used for reference to catch thrown exceptions. To get the specific error code of the exception, use the `error_code` attribute, i.e, `exception.error_code`.

### Logging
This library uses the standard
[logging](https://docs.python.org/3/library/logging.html) library for logging.
Basic information about HTTP sessions (URLs, headers, etc.) is logged at INFO
level.

Detailed DEBUG level logging, including request/response bodies and unredacted
headers, can be enabled on a client with the `logging_enable` argument:
```python
import sys
import logging
from azure.storage.queue import QueueServiceClient

# Create a logger for the 'azure.storage.queue' SDK
logger = logging.getLogger('azure.storage.queue')
logger.setLevel(logging.DEBUG)

# Configure a console output
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

# This client will log detailed information about its HTTP sessions, at DEBUG level
service_client = QueueServiceClient.from_connection_string("your_connection_string", logging_enable=True)
```

Similarly, `logging_enable` can enable detailed logging for a single operation,
even when it isn't enabled for the client:
```py
service_client.get_service_stats(logging_enable=True)
```

## Next steps
### More sample code

Get started with our [Queue samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-queue/samples).

Several Storage Queues Python SDK samples are available to you in the SDK's GitHub repository. These samples provide example code for additional scenarios commonly encountered while working with Storage Queues:

* [queue_samples_hello_world.py](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-queue/samples/queue_samples_hello_world.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-queue/samples/queue_samples_hello_world_async.py)) - Examples found in this article:
    * Client creation
    * Create a queue
    * Send messages
    * Receive messages

* [queue_samples_authentication.py](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-queue/samples/queue_samples_authentication.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-queue/samples/queue_samples_authentication_async.py)) - Examples for authenticating and creating the client:
    * From a connection string
    * From a shared access key
    * From a shared access signature token
    * From Azure Active Directory

* [queue_samples_service.py](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-queue/samples/queue_samples_service.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-queue/samples/queue_samples_service_async.py)) - Examples for interacting with the queue service:
    * Get and set service properties
    * List queues in a storage account
    * Create and delete a queue from the service
    * Get the QueueClient

* [queue_samples_message.py](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-queue/samples/queue_samples_message.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-queue/samples/queue_samples_message_async.py)) - Examples for working with queues and messages:
    * Set an access policy
    * Get and set queue metadata
    * Send and receive messages
    * Delete specified messages and clear all messages
    * Peek and update messages

### Additional documentation
For more extensive documentation on Azure Queue storage, see the [Azure Queue storage documentation](https://docs.microsoft.com/azure/storage/queues/) on docs.microsoft.com.

## Contributing
This project welcomes contributions and suggestions.  Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.
