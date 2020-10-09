# Azure Data Tables client library for Python

Azure Data Tables is a NoSQL data storage service that can be accessed from anywhere in the world via authenticated calls using HTTP or HTTPS.
Tables scales as needed to support the amount of data inserted, and allow for the storing of data with non-complex accessing.
The Azure Data Tables client can be used to access Azure Storage or Cosmos accounts.

[Source code][source_code] | [Package (PyPI)][Tables_pypi] | [API reference documentation][Tables_ref_docs] | [Samples][Tables_samples]

## Getting started
The Azure Data Tables can be accessed using an Azure Storage or a CosmosDB account.

### Prerequisites
* Python 2.7, or 3.5 or later is required to use this package.
* You must have an [Azure subscription][azure_subscription] and either
    * an [Azure storage account][azure_storage_account] or
    * an [Azure Cosmos Account][azure_cosmos_account].

#### Create a storage account
If you wish to create a new storage account, you can use [Azure Portal][azure_portal_create_account],
[Azure PowerShell][azure_powershell_create_account], or [Azure CLI][azure_cli_create_account]:

```bash
# Create a new resource group to hold the storage account -
# if using an existing resource group, skip this step
az group create --name MyResourceGroup --location westus2
# Create the storage account
az storage account create -n MyStorageAccount -g MyResourceGroup
```

#### Creating a Cosmos DB
If you wish to create a new cosmos storage account, you can use [Azure Cosmos DB][azure_create_cosmos].
Create a Cosmos DB account `MyCosmosDBDatabaseAccount` in resource group `MyResourceGroup` in the subscription `MySubscription` and a table named `MyTableName` in the account.
```bash
az cosmosdb create --name MyCosmosDBDatabaseAccount --resource-group MyResourceGroup --subscription MySubscription
az cosmosdb table create --name MyTableName --resource-group MyResourceGroup --acount-name MyCosmosDBDatabaseAccount
```


### Install the package
Install the Azure Data Tables client library for Python with [pip][pip_link]:

```bash
pip install --pre azure-data-tables
```


#### Create the client
The Azure Data Tables client library for Python allows you to interact with two types of resources: the
tables in your account, and the entities within the tables. Interaction with these resources starts with an
instance of a [client](#clients). To create a client object, you will need the account's table service
endpoint URL and a credential that allows you to access the account:

```python
from azure.data.tables import TableServiceClient
service = TableServiceClient(account_url="https://<myaccount>.table.core.windows.net/", credential=credential)
```

```bash
# Get the table service URL for the account
az storage account show -n mystorageaccount -g MyResourceGroup --query "primaryEndpoints.table"
```

#### Types of credentials
The `credential` parameter may be provided in a number of different forms, depending on the type of authorization you wish to use:

##### Creating the client from a SAS token
To use a [shared access signature (SAS) token][azure_sas_token], provide the token as a string. If your account URL includes the SAS token, omit the credential parameter. You can generate a SAS token from the Azure Portal under [Shared access signature](https://docs.microsoft.com/rest/api/storageservices/create-service-sas) or use one of the `generate_*_sas()`
   functions to create a sas token for the account or table:

```python
    from datetime import datetime, timedelta
    from azure.data.tables import TableServiceClient, generate_account_sas, ResourceTypes, AccountSasPermissions

    sas_token = generate_account_sas(
        account_name="<account-name>",
        account_key="<account-access-key>",
        resource_types=ResourceTypes(service=True),
        permission=AccountSasPermissions(read=True),
        expiry=datetime.utcnow() + timedelta(hours=1)
    )

    table_service_client = TableServiceClient(account_url="https://<my_account_name>.table.core.windows.net", credential=sas_token)
```

##### Creating the client from a shared key
To use an account [shared key][azure_shared_key] (aka account key or access key), provide the key as a string. This can be found in the [Azure Portal][azure_portal_account_url] under the "Access Keys" section or by running the following Azure CLI command:

```az storage account keys list -g MyResourceGroup -n MyStorageAccount```

Use the key as the credential parameter to authenticate the client:
```python
    from azure.data.tables import TableServiceClient
    service = TableServiceClient(account_url="https://<my_account_name>.table.core.windows.net", credential="<account_access_key>")
```

##### Creating the client from a connection string
Depending on your use case and authorization method, you may prefer to initialize a client instance with a
connection string instead of providing the account URL and credential separately. To do this, pass the
connection string to the client's `from_connection_string` class method:

```python
    from azure.data.tables import TableServiceClient
    connection_string = "DefaultEndpointsProtocol=https;AccountName=xxxx;AccountKey=xxxx;EndpointSuffix=core.windows.net"
    service = TableServiceClient.from_connection_string(conn_str=connection_string)
```

The connection string to your account can be found in the Azure Portal under the "Access Keys" section or by running the following CLI command:

```bash
az storage account show-connection-string -g MyResourceGroup -n MyStorageAccount
```

#### Looking up the account URL
You can find the account's table service URL using the
[Azure Portal][azure_portal_account_url],
[Azure PowerShell][azure_powershell_account_url],
or [Azure CLI][azure_cli_account_url]:

```bash
# Get the table service URL for the account
az storage account show -n MyStorageAccount -g MyResourceGroup --query "primaryEndpoints.table"
```

## Key concepts
Common uses of the Table service included:
* Storing TBs of structured data capable of serving web scale applications
* Storing datasets that do not require complex joins, foreign keys, or stored procedures and can be de-normalized for fast access
* Quickly querying data using a clustered index
* Accessing data using the OData protocol and LINQ filter expressions

The following components make up the Azure Data Tables Service:
* The account
* A table within the account, which contains a set of entities
* An entity within a table, as a dictionary

The Azure Data Tables client library for Python allows you to interact with each of these components through the
use of a dedicated client object.

### Clients
Two different clients are provided to interact with the various components of the Table Service:
1. `TableServiceClient` -
    this client represents interaction with the Azure account itself, and allows you to acquire preconfigured
    client instances to access the tables within. It provides operations to retrieve and configure the account
    properties as well as query, create, and delete tables within the account. To perform operations on a specific table,
    retrieve a client using the `get_table_client` method.
2. `TableClient` -
    this client represents interaction with a specific table (which need not exist yet). It provides operations to
    create, delete, or update a table and includes operations to query, get, and upsert entities
    within it.

### Entities
Entities are similar to rows. An entity has a primary key, a row key and a set of properties. A property is a name value pair, similar to a column.
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
Create a table in your account

```python
from azure.data.tables import TableServiceClient
table_service_client = TableServiceClient.from_connection_string(conn_str="<connection_string>")
table_service_client.create_table(table_name="myTable")
```

### Creating entities
Create entities in the table

```python
from azure.data.tables import TableClient
my_entity = {'PartitionKey':'part','RowKey':'row'}
table_client = TableClient.from_connection_string(conn_str="<connection_string>", table_name="myTable")
entity = table_client.create_entity(entity=my_entity)
```

### Querying entities
Querying entities in the table

```python
from azure.data.tables import TableClient
my_filter = "text eq 'Marker'"
table_client = TableClient.from_connection_string(conn_str="<connection_string>", table_name="mytable")
entity = table_client.query_entities(filter=my_filter)
```


## Optional Configuration

Optional keyword arguments can be passed in at the client and per-operation level. The azure-core [reference documentation][azure_core_ref_docs] describes available configurations for retries, logging, transport protocols, and more.


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
Azure Data Tables clients raise exceptions defined in [Azure Core][azure_core_readme].
When you interact with the Azure table library using the Python SDK, errors returned by the service respond ot the same HTTP status codes for [REST API][tables_rest] requests. The Table service operations will throw a `HttpResponseError` on failure with helpful [error codes][tables_error_codes].

For examples, if you try to create a table that already exists, a `409` error is returned indicating "Conflict".
```python
from azure.data.tables import TableServiceClient
from azure.core.exceptions import HttpResponseError
table_name = 'YourTableName

service_client = TableServiceClient.from_connection_string(connection_string)

# Create the table if it does not already exist
tc = service_client.create_table_if_not_exists(table_name)

try:
    service_client.create_table(table_name)
except HttpResponseError:
    print("Table with name {} already exists".format(table_name))
```
### Logging
This library uses the standard
[logging][python_logging] library for logging.
Basic information about HTTP sessions (URLs, headers, etc.) is logged at INFO
level.

Detailed DEBUG level logging, including request/response bodies and unredacted
headers, can be enabled on a client with the `logging_enable` argument:
```python
import sys
import logging
from azure.data.tables import TableServiceClient
# Create a logger for the 'azure' SDK
logger = logging.getLogger('azure')
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
service_client.create_entity(entity=my_entity, logging_enable=True)
```

## Next steps

Get started with our [Table samples][tables_samples].

Several Azure Data Tables Python SDK samples are available to you in the SDK's GitHub repository. These samples provide example code for additional scenarios commonly encountered while working with Tables.

### Common Scenarios
These code samples show common scenario operations with the Azure Data tables client library. The async versions of the samples (the python sample files appended with _async) show asynchronous operations with Tables and require Python 3.5 or later.

* Create and delete tables: [sample_create_delete_table.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/tables/azure-data-tables/samples/sample_create_delete_table.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/tables/azure-data-tables/samples/async_samples/sample_create_delete_table_async.py))
* List and query tables: [sample_query_tables.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/tables/azure-data-tables/samples/sample_query_tables.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/tables/azure-data-tables/samples/async_samples/sample_query_tables_async.py))
* Insert and delete entities: [sample_insert_delete_entities.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/tables/azure-data-tables/samples/sample_insert_delete_entities.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/tables/azure-data-tables/samples/async_samples/sample_insert_delete_entities_async.py))
* Query and list entities: [sample_query_tables.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/tables/azure-data-tables/samples/sample_query_tables.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/tables/azure-data-tables/samples/async_samples/sample_query_tables_async.py))
* Update, upsert, and merge entities: [sample_update_upsert_merge_entities.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/tables/azure-data-tables/samples/sample_update_upsert_merge_entities.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/tables/azure-data-tables/samples/async_samples/sample_update_upsert_merge_entities_async.py))

### Additional documentation
For more extensive documentation on Azure Data Tables, see the [Azure Data Tables documentation][Tables_product_doc] on docs.microsoft.com.

## Known Issues
A list of currently known issues relating to Cosmos DB table endpoints can be found [here](https://aka.ms/tablesknownissues).

## Contributing
This project welcomes contributions and suggestions.  Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct][msft_oss_coc]. For more information see the [Code of Conduct FAQ][msft_oss_coc_faq] or contact [opencode@microsoft.com][contact_msft_oss] with any additional questions or comments.

<!-- LINKS -->
[source_code]:https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/tables/azure-data-tables
[Tables_pypi]:https://aka.ms/azsdk/python/tablespypi
[Tables_ref_docs]:https://docs.microsoft.com/python/api/overview/azure/data-tables-readme-pre?view=azure-python-preview
[Tables_product_doc]:https://docs.microsoft.com/azure/cosmos-db/table-introduction
[Tables_samples]:https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/tables/azure-data-tables/samples

[azure_subscription]:https://azure.microsoft.com/free/
[azure_storage_account]:https://docs.microsoft.com/azure/storage/common/storage-account-create?tabs=azure-portal
[azure_cosmos_account]: https://docs.microsoft.com/azure/cosmos-db/account-overview
[pip_link]:https://pypi.org/project/pip/

[azure_create_cosmos]:https://docs.microsoft.com/azure/cosmos-db/create-cosmosdb-resources-portal
[azure_portal_create_account]:https://docs.microsoft.com/azure/storage/common/storage-account-create?tabs=azure-portal
[azure_powershell_create_account]:https://docs.microsoft.com/azure/storage/common/storage-account-create?tabs=azure-powershell
[azure_cli_create_account]: https://docs.microsoft.com/azure/storage/common/storage-account-create?tabs=azure-cli

[azure_cli_account_url]:https://docs.microsoft.com/cli/azure/storage/account?view=azure-cli-latest#az-storage-account-show
[azure_powershell_account_url]:https://docs.microsoft.com/powershell/module/az.storage/get-azstorageaccount?view=azps-4.6.1
[azure_portal_account_url]:https://docs.microsoft.com/azure/storage/common/storage-account-overview#storage-account-endpoints

[azure_sas_token]:https://docs.microsoft.com/azure/storage/common/storage-sas-overview
[azure_shared_key]:https://docs.microsoft.com/rest/api/storageservices/authorize-with-shared-key


[azure_core_ref_docs]: https://azuresdkdocs.blob.core.windows.net/$web/python/azure-core/latest/azure.core.html
[azure_core_readme]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/README.md

[python_logging]: https://docs.python.org/3/library/logging.html
[tables_error_codes]: https://docs.microsoft.com/rest/api/storageservices/table-service-error-codes

[msft_oss_coc]:https://opensource.microsoft.com/codeofconduct/
[msft_oss_coc_faq]:https://opensource.microsoft.com/codeofconduct/faq/
[contact_msft_oss]:mailto:opencode@microsoft.com

[tables_rest]: https://docs.microsoft.com/rest/api/storageservices/table-service-rest-api

![Impressions](https://azure-sdk-impressions.azurewebsites.net/api/impressions/azure-sdk-for-python/sdk/tables/azure-data-tables/README.png)
