# Azure Storage Blob ChangeFeed client library for Python

This preview package for Python enables users to get blob change feed events. These events can be lazily generated, iterated by page, retrieved for a specific time interval, or iterated from a specific continuation token.


[Source code](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-blob-changefeed/azure/storage/blob/changefeed) | [Package (PyPi)](https://pypi.org/project/azure-storage-blob-changefeed/) | [API reference documentation](https://aka.ms/azsdk-python-storage-blob-changefeed-ref) | [Product documentation](https://docs.microsoft.com/azure/storage/) | [Samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-blob-changefeed/samples)


## Getting started

### Prerequisites
* Python 3.7 or later is required to use this package. For more details, please read our page on [Azure SDK for Python version support policy](https://github.com/Azure/azure-sdk-for-python/wiki/Azure-SDKs-Python-version-support-policy).
* You must have an [Azure subscription](https://azure.microsoft.com/free/) and an
[Azure storage account](https://docs.microsoft.com/azure/storage/blobs/data-lake-storage-quickstart-create-account) to use this package.

### Install the package
Install the Azure Storage Blob ChangeFeed client library for Python with [pip](https://pypi.org/project/pip/):

```bash
pip install azure-storage-blob-changefeed --pre
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

To enable changefeed you can use:
[Azure Portal](https://docs.microsoft.com/azure/storage/blobs/storage-blob-change-feed?tabs=azure-portal#enable-and-disable-the-change-feed),
[Azure PowerShell](https://docs.microsoft.com/azure/storage/blobs/storage-blob-change-feed?tabs=azure-powershell#enable-and-disable-the-change-feed)
or [Template](https://docs.microsoft.com/azure/storage/blobs/storage-blob-change-feed?tabs=template#enable-and-disable-the-change-feed).

### Authenticate the client

Interaction with Blob ChangeFeed client starts with an instance of the ChangeFeedClient class. You need an existing storage account, its URL, and a credential to instantiate the client object.

#### Get credentials

To authenticate the client you have a few options:
1. Use a SAS token string
2. Use an account shared access key
3. Use a token credential from [azure.identity](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity)

Alternatively, you can authenticate with a storage connection string using the `from_connection_string` method. See example: [Client creation with a connection string](#client-creation-with-a-connection-string).

You can omit the credential if your account URL already has a SAS token.

#### Create client

Once you have your account URL and credentials ready, you can create the ChangeFeedClient:

```python
from azure.storage.blob.changefeed import ChangeFeedClient

service = ChangeFeedClient(account_url="https://<my-storage-account-name>.blob.core.windows.net/", credential=credential)
```

## Key concepts

#### Clients

The Blob ChangeFeed SDK provides one client:
* ChangeFeedClient: this client allows you to get change feed events by page, get all change feed events, get events in a time range, start listing events with a continuation token.

## Examples

The following sections provide several code snippets covering some of the most common Storage Blob ChangeFeed, including:

* [Client creation with a connection string](#client-creation-with-a-connection-string)
* [Enumerating Events Within a Time Range](#enumerating-events-within-a-time-range)
* [Enumerating All Events](#enumerating-all-events)
* [Enumerating Events by Page](#enumerating-events-by-page)


### Client creation with a connection string
Create the ChangeFeedClient using the connection string to your Azure Storage account.

```python
from azure.storage.blob.changefeed import ChangeFeedClient

service = ChangeFeedClient.from_connection_string(conn_str="my_connection_string")
```
### Enumerating Events Within a Time Range
List all events within a time range.

```python
from datetime import datetime
from azure.storage.blob.changefeed import ChangeFeedClient

cf_client = ChangeFeedClient("https://{}.blob.core.windows.net".format("YOUR_ACCOUNT_NAME"),
                             credential="Your_ACCOUNT_KEY")
start_time = datetime(2020, 1, 6)
end_time = datetime(2020, 3, 4)
change_feed = cf_client.list_changes(start_time=start_time, end_time=end_time)

# print range of events
for event in change_feed:
    print(event)
```

### Enumerating All Events
List all events.

```python
from azure.storage.blob.changefeed import ChangeFeedClient

cf_client = ChangeFeedClient("https://{}.blob.core.windows.net".format("YOUR_ACCOUNT_NAME"),
                             credential="Your_ACCOUNT_KEY")
change_feed = cf_client.list_changes()

# print all events
for event in change_feed:
    print(event)
```

### Enumerating Events by Page
List events by page.

```python
from azure.storage.blob.changefeed import ChangeFeedClient

cf_client = ChangeFeedClient("https://{}.blob.core.windows.net".format("YOUR_ACCOUNT_NAME"),
                             credential="Your_ACCOUNT_KEY")

change_feed = cf_client.list_changes().by_page()

# print first page of events
change_feed_page1 = next(change_feed)
for event in change_feed_page1:
    print(event)
```

## Troubleshooting

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
from azure.storage.blob.changefeed import ChangeFeedClient

# Create a logger for the 'azure.storage.blob.changefeed' SDK
logger = logging.getLogger('azure.storage')
logger.setLevel(logging.DEBUG)

# Configure a console output
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

# This client will log detailed information about its HTTP sessions, at DEBUG level
service_client = ChangeFeedClient.from_connection_string("your_connection_string", logging_enable=True)
```

## Next steps

### More sample code

Get started with our [Azure Blob ChangeFeed samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-blob-changefeed/samples).

Several Storage Blob ChangeFeed Python SDK samples are available to you in the SDK's GitHub repository. These samples provide example code for additional scenarios commonly encountered while working with Blob ChangeFeed:

* [change_feed_samples.py](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-blob-changefeed/samples/change_feed_samples.py) - Examples for authenticating and operating on the client:
    * list events by page
    * list all events
    * list events in a time range
    * list events starting from a continuation token


## Contributing
This project welcomes contributions and suggestions.  Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.