# Azure Table client library for Python

Azure Table is a service for storing data that can be accessed from anywhere in the world via authenticated calls using HTTP or HTTPS. 

Common uses of Azure Table include:

* Storing structured data in the form of tables
* Quickly querying data using a clustered index

[Source code](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/table/azure-table/azure/table) | [Package (PyPI)](https://pypi.org/project/azure-table/) | [API reference documentation](https://aka.ms/azsdk/python/table/docs) | [Product documentation](https://docs.microsoft.com/azure/storage/) | [Samples](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/table/azure-table/samples)

## Getting started

### Prerequisites
* Python 2.7, or 3.5 or later is required to use this package.
* You must have an [Azure subscription](https://azure.microsoft.com/free/) and an
[Azure storage account](https://docs.microsoft.com/azure/storage/common/storage-account-overview) to use this package
 or you must have a [Azure Cosmos Account](https://docs.microsoft.com/en-us/azure/cosmos-db/account-overview).

### Install the package
Install the Azure Table client library for Python with [pip](https://pypi.org/project/pip/):

```bash
pip install --pre azure-table
```

### Create a storage account
If you wish to create a new storage account, you can use the
[Azure Portal](https://docs.microsoft.com/azure/storage/common/storage-quickstart-create-account?tabs=azure-portal),
[Azure PowerShell](https://docs.microsoft.com/azure/storage/common/storage-quickstart-create-account?tabs=azure-powershell),
or [Azure CLI](https://docs.microsoft.com/azure/storage/common/storage-quickstart-create-account?tabs=azure-cli):

```bash
# Create a new resource group to hold the storage account -
# if using an existing resource group, skip this step
az group create --name MyResourceGroup --location westus2

# Create the storage account
az storage account create -n mystorageaccount -g MyResourceGroup
```

### Create the client
The Azure Table client library for Python allows you to interact with two types of resources: the storage
account and tables, and entities. Interaction with these resources starts with an instance of a [client](#clients).
To create a client object, you will need the storage account's table service endpoint URL and a credential that allows
you to access the storage account:

```python
from azure.table import TableServiceClient

service = TableServiceClient(account_url="https://<mystorageaccount>.table.core.windows.net/", credential=credential)
```

#### Looking up the account URL
You can find the storage account's table service URL using the 
[Azure Portal](https://docs.microsoft.com/azure/storage/common/storage-account-overview#storage-account-endpoints),
[Azure PowerShell](https://docs.microsoft.com/powershell/module/az.storage/get-azstorageaccount),
or [Azure CLI](https://docs.microsoft.com/cli/azure/storage/account?view=azure-cli-latest#az-storage-account-show):

```bash
# Get the table service URL for the storage account
az storage account show -n mystorageaccount -g MyResourceGroup --query "primaryEndpoints.table"
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
    from azure.table import TableServiceClient, generate_account_shared_access_signature, ResourceTypes, AccountSasPermissions
    
    sas_token = generate_account_shared_access_signature(
        account_name="<storage-account-name>",
        account_key="<account-access-key>",
        resource_types=ResourceTypes(service=True),
        permission=AccountSasPermissions(read=True),
        expiry=datetime.utcnow() + timedelta(hours=1)
    )
    
    table_service_client = TableServiceClient(account_url="https://<my_account_name>.table.core.windows.net", credential=sas_token)
    ```

2. To use a storage account [shared key](https://docs.microsoft.com/rest/api/storageservices/authenticate-with-shared-key/)
   (aka account key or access key), provide the key as a string. This can be found in the Azure Portal under the "Access Keys" 
   section or by running the following Azure CLI command:

    ```az storage account keys list -g MyResourceGroup -n mystorageaccount```

    Use the key as the credential parameter to authenticate the client:
    ```python
    from azure.table import TableServiceClient
    service = TableServiceClient(account_url="https://<my_account_name>.table.core.windows.net", credential="<account_access_key>")
    ```

#### Creating the client from a connection string
Depending on your use case and authorization method, you may prefer to initialize a client instance with a storage
connection string instead of providing the account URL and credential separately. To do this, pass the storage
connection string to the client's `from_connection_string` class method:

```python
from azure.table import TableServiceClient

connection_string = "DefaultEndpointsProtocol=https;AccountName=xxxx;AccountKey=xxxx;EndpointSuffix=core.windows.net"
service = TableServiceClient.from_connection_string(conn_str=connection_string)
```

The connection string to your storage account can be found in the Azure Portal under the "Access Keys" section or by running the following CLI command:

```bash
az storage account show-connection-string -g MyResourceGroup -n mystorageaccount
```

## Key concepts
The following components make up the Azure Table Service:
* The storage account and a table within the storage account, which contains a set of entities
* An entity within a table, as a dictionary

The Azure Table client library for Python allows you to interact with each of these components through the
use of a dedicated client object.

### Clients
Two different clients are provided to to interact with the various components of the Table Service:
1. [TableServiceClient](https://aka.ms/azsdk/python/table/docs) -
    this client represents interaction with the Azure storage account itself, and allows you to acquire preconfigured
    client instances to access the tables within. It provides operations to retrieve and configure the account
    properties as well as query, create, and delete tables within the account. To perform operations on a specific table,
    retrieve a client using the `get_table_client` method.
2. [TableClient](https://aka.ms/azsdk/python/table/docs) -
    this client represents interaction with a specific table (which need not exist yet). It provides operations to
    create, delete, or update a table and includes operations to query, get, and upsert entities
    within it.
    
### Entities
* **Create** - Adds an entity to the table.
* **Delete** - Deletes an entity from the table.
* **Update** - Updates an entities information by either merging or replacing the existing entity.
* **Query** - Queries existing entities in a table based off of the QueryOptions (OData).
* **Get** - Gets a specific entity from a table by partition and row key.
* **Upsert** - Merges or replaces an entity in a table, or if the entity does not exist, inserts the entity. 

## Examples

The following sections provide several code snippets covering some of the most common Table tasks, including:

* [Creating a table](#creating-a-table "Creating a table")
* [Creating entities](#creating-entities "Creating entities")
* [Querying entities](#querying-entities "Querying entities")


### Creating a table
Create a table in your storage account

```python
from azure.table import TableServiceClient

table_service_client = TableServiceClient.from_connection_string(conn_str="<connection_string>")
table_service_client.create_table(table_name="myTable")
```

Use the async client to create a table
```python
from azure.table.aio import TableServiceClient

table_service_client = TableServiceClient.from_connection_string(conn_str="<connection_string>")
await table_service_client.create_table(table_name="myTable")
```

### Creating entities
Create entities in the table

```python
from azure.table import TableClient

my_entity = {'PartitionKey':'part','RowKey':'row'}

table_client = TableClient.from_connection_string(conn_str="<connection_string>", table_name="myTable")
entity = table_client.create_entity(entity=my_entity)
```

Create entities asynchronously

```python
from azure.table.aio import TableClient

my_entity = {
    'PartitionKey': 'color',
    'RowKey': 'brand',
    'text': 'Marker',
    'color': 'Purple',
    'price': '5',
}

table_client = TableClient.from_connection_string(conn_str="<connection_string>", table_name="mytable")
entity = await table_client.create_entity(entity=my_entity)
```

### Querying entities
Querying entities in the table

```python
from azure.table import TableClient

my_filter = "text eq Marker"

table_client = TableClient.from_connection_string(conn_str="<connection_string>", table_name="mytable")
entity = table_client.query_entities(filter=my_filter)
```

Querying entities asynchronously

```python
from azure.table.aio import TableClient

my_filter = "text eq Marker"

table_client = TableClient.from_connection_string(conn_str="<connection_string>", table_name="mytable")
entity = await table_client.query_entities(filter=my_filter)
```

## Optional Configuration

Optional keyword arguments can be passed in at the client and per-operation level. The azure-core [reference documentation](https://azuresdkdocs.blob.core.windows.net/$web/python/azure-core/latest/azure.core.html) describes available configurations for retries, logging, transport protocols, and more.


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

* __connection_timeout__ (int): Optionally sets the connect and read timeout value, in seconds.
* __transport__ (Any): User-provided transport to send the HTTP request.

**Per-operation keyword arguments:**

* __raw_response_hook__ (callable): The given callback uses the response returned from the service.
* __raw_request_hook__ (callable): The given callback uses the request before being sent to service.
* __client_request_id__ (str): Optional user specified identification of the request.
* __user_agent__ (str): Appends the custom value to the user-agent header to be sent with the request.
* __logging_enable__ (bool): Enables logging at the DEBUG level. Defaults to False. Can also be passed in at
the client level to enable it for all requests.
* __headers__ (dict): Pass in custom headers as key, value pairs. E.g. `headers={'CustomValue': value}`


## Troubleshooting
### General
Azure Table clients raise exceptions defined in [Azure Core](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/README.md).
All Table service operations will throw a `HttpResponseError` on failure with helpful [error codes](https://docs.microsoft.com/en-us/rest/api/storageservices/table-service-error-codes).

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
from azure.table import TableServiceClient

# Create a logger for the 'azure.table' SDK
logger = logging.getLogger('azure.table')
logger.setLevel(logging.DEBUG)

# Configure a console output
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

# This client will log detailed information about its HTTP sessions, at DEBUG level
service_client = TableServiceClient.from_connection_string("your_connection_string", logging_enable=True)
```

Similarly, `logging_enable` can enable detailed logging for a single operation,
even when it isn't enabled for the client:
```py
service_client.get_service_stats(logging_enable=True)
```

## Next steps

Get started with our [Table samples](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/table/azure-table/samples).

Several Azure Table Python SDK samples are available to you in the SDK's GitHub repository. These samples provide example code for additional scenarios commonly encountered while working with Tables:

* [table_samples_authentication.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/table/azure-table/samples/table_samples_authentication.py) - Examples found in this article:
    * From a connection string
    * From a shared access key
    * From a shared access signature token
* [table_samples_service.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/table/azure-table/samples/table_samples_service.py) - Examples found in this article:
    * Get and set service properties
    * List tables in a storage account
    * Create and delete a table from the service
    * Get the TableClient
* [table_samples_client.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/table/azure-table/samples/table_samples_client.py) - Examples found in this article:
    * Client creation
    * Create a table
    * Create and Delete entities
    * Query entities
    * Update entities
    * Upsert entities
    
### Additional documentation
For more extensive documentation on Azure Table, see the [Azure Table documentation](https://docs.microsoft.com/azure/storage/tables/) on docs.microsoft.com.

## Contributing
This project welcomes contributions and suggestions.  Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.
