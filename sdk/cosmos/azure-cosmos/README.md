# Azure Cosmos DB SQL API client library for Python

## _Disclaimer_
_Azure SDK Python packages support for Python 2.7 has ended 01 January 2022. For more information and questions, please refer to https://github.com/Azure/azure-sdk-for-python/issues/20691_

Azure Cosmos DB is a globally distributed, multi-model database service that supports document, key-value, wide-column, and graph databases.

Use the Azure Cosmos DB SQL API SDK for Python to manage databases and the JSON documents they contain in this NoSQL database service. High level capabilities are:

* Create Cosmos DB **databases** and modify their settings
* Create and modify **containers** to store collections of JSON documents
* Create, read, update, and delete the **items** (JSON documents) in your containers
* Query the documents in your database using **SQL-like syntax**

[SDK source code][source_code]
| [Package (PyPI)][cosmos_pypi]
| [Package (Conda)](https://anaconda.org/microsoft/azure-cosmos/)
| [API reference documentation][ref_cosmos_sdk]
| [Product documentation][cosmos_docs]
| [Samples][cosmos_samples]

> This SDK is used for the [SQL API](https://learn.microsoft.com/azure/cosmos-db/sql-query-getting-started). For all other APIs, please check the [Azure Cosmos DB documentation](https://learn.microsoft.com/azure/cosmos-db/introduction) to evaluate the best SDK for your project.

## Getting started

### Important update on Python 2.x Support

New releases of this SDK won't support Python 2.x starting January 1st, 2022. Please check the [CHANGELOG](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cosmos/azure-cosmos/CHANGELOG.md) for more information.

### Prerequisites

* Azure subscription - [Create a free account][azure_sub]
* Azure [Cosmos DB account][cosmos_account] - SQL API
* [Python 3.8+][python]

If you need a Cosmos DB SQL API account, you can create one with this [Azure CLI][azure_cli] command:

```Bash
az cosmosdb create --resource-group <resource-group-name> --name <cosmos-account-name>
```

### Install the package

```bash
pip install azure-cosmos
```

#### Configure a virtual environment (optional)

Although not required, you can keep your base system and Azure SDK environments isolated from one another if you use a virtual environment. Execute the following commands to configure and then enter a virtual environment with [venv][venv]:

```Bash
python3 -m venv azure-cosmosdb-sdk-environment
source azure-cosmosdb-sdk-environment/bin/activate
```

### Authenticate the client

Interaction with Cosmos DB starts with an instance of the [CosmosClient][ref_cosmosclient] class. You need an **account**, its **URI**, and one of its **account keys** to instantiate the client object.

Use the Azure CLI snippet below to populate two environment variables with the database account URI and its primary master key (you can also find these values in the Azure portal). The snippet is formatted for the Bash shell.

```Bash
RES_GROUP=<resource-group-name>
ACCT_NAME=<cosmos-db-account-name>

export ACCOUNT_URI=$(az cosmosdb show --resource-group $RES_GROUP --name $ACCT_NAME --query documentEndpoint --output tsv)
export ACCOUNT_KEY=$(az cosmosdb list-keys --resource-group $RES_GROUP --name $ACCT_NAME --query primaryMasterKey --output tsv)
```

### Create the client

Once you've populated the `ACCOUNT_URI` and `ACCOUNT_KEY` environment variables, you can create the [CosmosClient][ref_cosmosclient].

```python
from azure.cosmos import CosmosClient

import os
URL = os.environ['ACCOUNT_URI']
KEY = os.environ['ACCOUNT_KEY']
client = CosmosClient(URL, credential=KEY)
```

### AAD Authentication

You can also authenticate a client utilizing your service principal's AAD credentials and the azure identity package. 
You can directly pass in the credentials information to ClientSecretCredential, or use the DefaultAzureCredential:
```python
from azure.cosmos import CosmosClient
from azure.identity import ClientSecretCredential, DefaultAzureCredential

import os
url = os.environ['ACCOUNT_URI']
tenant_id = os.environ['TENANT_ID']
client_id = os.environ['CLIENT_ID']
client_secret = os.environ['CLIENT_SECRET']

# Using ClientSecretCredential
aad_credentials = ClientSecretCredential(
    tenant_id=tenant_id,
    client_id=client_id,
    client_secret=client_secret)

# Using DefaultAzureCredential (recommended)
aad_credentials = DefaultAzureCredential()

client = CosmosClient(url, aad_credentials)
```
Always ensure that the managed identity you use for AAD authentication has `readMetadata` permissions. <br>
More information on how to set up AAD authentication: [Set up RBAC for AAD authentication](https://learn.microsoft.com/azure/cosmos-db/how-to-setup-rbac) <br>
More information on allowed operations for AAD authenticated clients: [RBAC Permission Model](https://aka.ms/cosmos-native-rbac)

### Preferred Locations 
To enable multi-region support in CosmosClient, set the `preferred_locations` parameter. 
By default, all writes and reads go to the dedicated write region unless specified otherwise.
The `preferred_locations` parameter accepts a list of regions for read requests.
Requests are sent to the first region in the list, and if it fails, they move to the next region.

For example, to set West US as the read region, and Central US as the backup read region, the code would look like this:
```python
from azure.cosmos import CosmosClient

import os
URL = os.environ['ACCOUNT_URI']
KEY = os.environ['ACCOUNT_KEY']
client = CosmosClient(URL, credential=KEY, preferred_locations=["West US", "Central US"])
```
Also note that if all regions listed in preferred locations fail, read requests are sent to the main write region. 
For example if the write region is set to East US, then `preferred_locations=["West US", "Central US"]`
is equivalent to `preferred_locations=["West US", "Central US", "East US"]` since the client will send all requests to the write region if the preferred locations fail.

## Key concepts

Once you've initialized a [CosmosClient][ref_cosmosclient], you can interact with the primary resource types in Cosmos DB:

* [Database][ref_database]: A Cosmos DB account can contain multiple databases. When you create a database, you specify the API you'd like to use when interacting with its documents: SQL, MongoDB, Gremlin, Cassandra, or Azure Table. Use the [DatabaseProxy][ref_database] object to manage its containers.

* [Container][ref_container]: A container is a collection of JSON documents. You create (insert), read, update, and delete items in a container by using methods on the [ContainerProxy][ref_container] object.

* Item: An Item is the dictionary-like representation of a JSON document stored in a container. Each Item you add to a container must include an `id` key with a value that uniquely identifies the item within the container.

For more information about these resources, see [Working with Azure Cosmos databases, containers and items][cosmos_resources].


## How to use `enable_cross_partition_query`

The keyword-argument `enable_cross_partition_query` accepts 2 options: `None` (default) or `True`.

## Note on using queries by id

When using queries that try to find items based on an **id** value, always make sure you are passing in a string type variable. Azure Cosmos DB only allows string id values and if you use any other datatype, this SDK will return no results and no error messages.

## Note on client consistency levels

As of release version 4.3.0b3, if a user does not pass in an explicit consistency level to their client initialization,
their client will use their database account's default level. Previously, the default was being set to `Session` consistency.
If for some reason you'd like to keep doing this, you can change your client initialization to include the explicit parameter for this like shown:
```python
from azure.cosmos import CosmosClient

import os
URL = os.environ['ACCOUNT_URI']
KEY = os.environ['ACCOUNT_KEY']
client = CosmosClient(URL, credential=KEY, consistency_level='Session')
```

## Limitations

Currently, the features below are **not supported**. For alternatives options, check the **Workarounds** section below.

### Data Plane Limitations:

* Group By queries
* Queries with COUNT from a DISTINCT subquery: SELECT COUNT (1) FROM (SELECT DISTINCT C.ID FROM C)
* Direct TCP Mode access
* Continuation token support for aggregate cross-partition queries like sorting, counting, and distinct.
Streamable queries like `SELECT * FROM WHERE` *do* support continuation tokens.
* Change Feed: Processor
* Change Feed: Read multiple partitions key values
* Cross-partition ORDER BY for mixed types
* Enabling diagnostics for async query-type methods

### Control Plane Limitations:

* Get CollectionSizeUsage, DatabaseUsage, and DocumentUsage metrics
* Get the connection string
* Get the minimum RU/s of a container

## Workarounds

### Control Plane Limitations Workaround

Typically, you can use [Azure Portal](https://portal.azure.com/), [Azure Cosmos DB Resource Provider REST API](https://learn.microsoft.com/rest/api/cosmos-db-resource-provider), [Azure CLI](https://learn.microsoft.com/cli/azure/azure-cli-reference-for-cosmos-db) or [PowerShell](https://learn.microsoft.com/azure/cosmos-db/manage-with-powershell) for the control plane unsupported limitations.

### Using The Async Client as a Workaround to Bulk
While the SDK supports transactional batch, support for bulk requests is not yet implemented in the Python SDK. You can use the async client along with this [concurrency sample][cosmos_concurrency_sample] we have developed as a reference for a possible workaround. 
>[WARNING]
> Using the asynchronous client for concurrent operations like shown in this sample will consume a lot of RUs very fast. We **strongly recommend** testing this out against the cosmos emulator first to verify your code works well and avoid incurring charges.



## Boolean Data Type

While the Python language [uses](https://docs.python.org/3/library/stdtypes.html?highlight=boolean#truth-value-testing) "True" and "False" for boolean types, Cosmos DB [accepts](https://learn.microsoft.com/azure/cosmos-db/sql-query-is-bool) "true" and "false" only. In other words, the Python language uses Boolean values with the first uppercase letter and all other lowercase letters, while Cosmos DB and its SQL language use only lowercase letters for those same Boolean values. How to deal with this challenge?

* Your JSON documents created with Python must use "True" and "False", to pass the language validation. The SDK will convert it to "true" and "false" for you. Meaning that "true" and "false" is what will be stored in Cosmos DB.
* If you retrieve those documents with the Cosmos DB Portal's Data Explorer, you will see "true" and "false".
* If you retrieve those documents with this Python SDK, "true" and "false" values will be automatically converted to "True" and "False".

## SQL Queries x FROM Clause Subitems

This SDK uses the [query_items](https://learn.microsoft.com/python/api/azure-cosmos/azure.cosmos.containerproxy?preserve-view=true&view=azure-python#query-items-query--parameters-none--partition-key-none--enable-cross-partition-query-none--max-item-count-none--enable-scan-in-query-none--populate-query-metrics-none----kwargs-) method to submit SQL queries to Azure Cosmos DB.

Cosmos DB SQL language allows you to [get subitems by using the FROM clause](https://learn.microsoft.com/azure/cosmos-db/sql-query-from#get-subitems-by-using-the-from-clause), to reduce the source to a smaller subset. As an example, you can use `select * from Families.children` instead of `select * from Families`. But please note that:

* For SQL queries using the `query_items` method, this SDK demands that you specify the `partition_key` or use the `enable_cross_partition_query` flag.
* If you are getting subitems and specifying the `partition_key`, please make sure that your partition key is included in the subitems, which is not true for most of the cases.

## Max Item Count

This is a parameter of the query_items method, an integer indicating the maximum number of items to be returned per page. The `None` value can be specified to let the service determine the optimal item count. This is the recommended configuration value, and the default behavior of this SDK when it is not set.

## Examples

The following sections provide several code snippets covering some of the most common Cosmos DB tasks, including:

* [Create a database](#create-a-database "Create a database")
* [Create a container](#create-a-container "Create a container")
* [Create an analytical store enabled container](#create-an-analytical-store-enabled-container "Create a container")
* [Get an existing container](#get-an-existing-container "Get an existing container")
* [Insert data](#insert-data "Insert data")
* [Delete data](#delete-data "Delete data")
* [Query the database](#query-the-database "Query the database")
* [Get database properties](#get-database-properties "Get database properties")
* [Get database and container throughputs](#get-database-and-container-throughputs "Get database and container throughputs")
* [Modify container properties](#modify-container-properties "Modify container properties")
* [Using the asynchronous client](#using-the-asynchronous-client "Using the asynchronous client")

### Create a database

After authenticating your [CosmosClient][ref_cosmosclient], you can work with any resource in the account. The code snippet below creates a SQL API database, which is the default when no API is specified when [create_database][ref_cosmosclient_create_database] is invoked.

```python
from azure.cosmos import CosmosClient, exceptions
import os

URL = os.environ['ACCOUNT_URI']
KEY = os.environ['ACCOUNT_KEY']
client = CosmosClient(URL, credential=KEY)
DATABASE_NAME = 'testDatabase'
try:
    database = client.create_database(DATABASE_NAME)
except exceptions.CosmosResourceExistsError:
    database = client.get_database_client(DATABASE_NAME)
```

### Create a container

This example creates a container with default settings. If a container with the same name already exists in the database (generating a `409 Conflict` error), the existing container is obtained instead.

```python
from azure.cosmos import CosmosClient, PartitionKey, exceptions
import os

URL = os.environ['ACCOUNT_URI']
KEY = os.environ['ACCOUNT_KEY']
client = CosmosClient(URL, credential=KEY)
DATABASE_NAME = 'testDatabase'
database = client.get_database_client(DATABASE_NAME)
CONTAINER_NAME = 'products'

try:
    container = database.create_container(id=CONTAINER_NAME, partition_key=PartitionKey(path="/productName"))
except exceptions.CosmosResourceExistsError:
    container = database.get_container_client(CONTAINER_NAME)
except exceptions.CosmosHttpResponseError:
    raise
```

### Create an analytical store enabled container

This example creates a container with [Analytical Store](https://learn.microsoft.com/azure/cosmos-db/analytical-store-introduction) enabled, for reporting, BI, AI, and Advanced Analytics with [Azure Synapse Link](https://learn.microsoft.com/azure/cosmos-db/synapse-link).

The options for analytical_storage_ttl are:

+ 0 or Null or not informed: Not enabled.
+ -1: The data will be stored infinitely.
+ Any other number: the actual ttl, in seconds.


```python
CONTAINER_NAME = 'products'
try:
    container = database.create_container(id=CONTAINER_NAME, partition_key=PartitionKey(path="/productName"),analytical_storage_ttl=-1)
except exceptions.CosmosResourceExistsError:
    container = database.get_container_client(CONTAINER_NAME)
except exceptions.CosmosHttpResponseError:
    raise
```

The preceding snippets also handle the [CosmosHttpResponseError][ref_httpfailure] exception if the container creation failed. For more information on error handling and troubleshooting, see the [Troubleshooting](#troubleshooting "Troubleshooting") section.

### Get an existing container

Retrieve an existing container from the database:

```python
from azure.cosmos import CosmosClient
import os

URL = os.environ['ACCOUNT_URI']
KEY = os.environ['ACCOUNT_KEY']
client = CosmosClient(URL, credential=KEY)
DATABASE_NAME = 'testDatabase'
database = client.get_database_client(DATABASE_NAME)
CONTAINER_NAME = 'products'
container = database.get_container_client(CONTAINER_NAME)
```

### Insert data

To insert items into a container, pass a dictionary containing your data to [ContainerProxy.upsert_item][ref_container_upsert_item]. Each item you add to a container must include an `id` key with a value that uniquely identifies the item within the container.

This example inserts several items into the container, each with a unique `id`:

```python
from azure.cosmos import CosmosClient
import os

URL = os.environ['ACCOUNT_URI']
KEY = os.environ['ACCOUNT_KEY']
client = CosmosClient(URL, credential=KEY)
DATABASE_NAME = 'testDatabase'
database = client.get_database_client(DATABASE_NAME)
CONTAINER_NAME = 'products'
container = database.get_container_client(CONTAINER_NAME)

for i in range(1, 10):
    container.upsert_item({
            'id': 'item{0}'.format(i),
            'productName': 'Widget',
            'productModel': 'Model {0}'.format(i)
        }
    )
```

### Delete data

To delete items from a container, use [ContainerProxy.delete_item][ref_container_delete_item]. The SQL API in Cosmos DB does not support the SQL `DELETE` statement.

```python
from azure.cosmos import CosmosClient
import os

URL = os.environ['ACCOUNT_URI']
KEY = os.environ['ACCOUNT_KEY']
client = CosmosClient(URL, credential=KEY)
DATABASE_NAME = 'testDatabase'
database = client.get_database_client(DATABASE_NAME)
CONTAINER_NAME = 'products'
container = database.get_container_client(CONTAINER_NAME)

for item in container.query_items(
        query='SELECT * FROM products p WHERE p.productModel = "Model 2"',
        enable_cross_partition_query=True):
    container.delete_item(item, partition_key='Widget')
```

> NOTE: If you are using partitioned collection, the value of the `partitionKey` in the example code above, should be set to the value of the partition key for this particular item, not the name of the partition key column in your collection. This holds true for both point reads and deletes.

### Query the database

A Cosmos DB SQL API database supports querying the items in a container with [ContainerProxy.query_items][ref_container_query_items] using SQL-like syntax.

This example queries a container for items with a specific `id`:

```python
from azure.cosmos import CosmosClient
import os

URL = os.environ['ACCOUNT_URI']
KEY = os.environ['ACCOUNT_KEY']
client = CosmosClient(URL, credential=KEY)
DATABASE_NAME = 'testDatabase'
database = client.get_database_client(DATABASE_NAME)
CONTAINER_NAME = 'products'
container = database.get_container_client(CONTAINER_NAME)

# Enumerate the returned items
import json
for item in container.query_items(
        query='SELECT * FROM mycontainer r WHERE r.id="item3"',
        enable_cross_partition_query=True):
    print(json.dumps(item, indent=True))
```

> NOTE: Although you can specify any value for the container name in the `FROM` clause, we recommend you use the container name for consistency.

Perform parameterized queries by passing a dictionary containing the parameters and their values to [ContainerProxy.query_items][ref_container_query_items]:

```python
discontinued_items = container.query_items(
    query='SELECT * FROM products p WHERE p.productModel = @model',
    parameters=[
        dict(name='@model', value='Model 7')
    ],
    enable_cross_partition_query=True
)
for item in discontinued_items:
    print(json.dumps(item, indent=True))
```

For more information on querying Cosmos DB databases using the SQL API, see [Query Azure Cosmos DB data with SQL queries][cosmos_sql_queries].

### Get database properties

Get and display the properties of a database:

```python
from azure.cosmos import CosmosClient
import os
import json

URL = os.environ['ACCOUNT_URI']
KEY = os.environ['ACCOUNT_KEY']
client = CosmosClient(URL, credential=KEY)
DATABASE_NAME = 'testDatabase'
database = client.get_database_client(DATABASE_NAME)
properties = database.read()
print(json.dumps(properties))
```

### Get database and container throughputs

Get and display the throughput values of a database and of a container with dedicated throughput:

```python
from azure.cosmos import CosmosClient
import os
import json

URL = os.environ['ACCOUNT_URI']
KEY = os.environ['ACCOUNT_KEY']
client = CosmosClient(URL, credential=KEY)

# Database
DATABASE_NAME = 'testDatabase'
database = client.get_database_client(DATABASE_NAME)
db_offer = database.get_throughput()
print('Found Offer \'{0}\' for Database \'{1}\' and its throughput is \'{2}\''.format(db_offer.properties['id'], database.id, db_offer.properties['content']['offerThroughput']))

# Container with dedicated throughput only. Will return error "offer not found" for containers without dedicated throughput
CONTAINER_NAME = 'testContainer'
container = database.get_container_client(CONTAINER_NAME)
container_offer = container.get_throughput()
print('Found Offer \'{0}\' for Container \'{1}\' and its throughput is \'{2}\''.format(container_offer.properties['id'], container.id, container_offer.properties['content']['offerThroughput']))
```


### Modify container properties

Certain properties of an existing container can be modified. This example sets the default time to live (TTL) for items in the container to 10 seconds:

```python
from azure.cosmos import CosmosClient, PartitionKey
import os
import json

URL = os.environ['ACCOUNT_URI']
KEY = os.environ['ACCOUNT_KEY']
client = CosmosClient(URL, credential=KEY)
DATABASE_NAME = 'testDatabase'
database = client.get_database_client(DATABASE_NAME)
CONTAINER_NAME = 'products'
container = database.get_container_client(CONTAINER_NAME)

database.replace_container(
    container,
    partition_key=PartitionKey(path="/productName"),
    default_ttl=10,
)
# Display the new TTL setting for the container
container_props = container.read()
print(json.dumps(container_props['defaultTtl']))
```

For more information on TTL, see [Time to Live for Azure Cosmos DB data][cosmos_ttl].

### Using item point operation response headers

Response headers include metadata information from the executed operations like `etag`, which allows for optimistic concurrency scenarios, or `x-ms-request-charge` which lets you know how many RUs were consumed by the request.
This applies to all item point operations in both the sync and async clients - and can be used by referencing the `get_response_headers()` method of any response as such:
```python
from azure.cosmos import CosmosClient
import os

URL = os.environ['ACCOUNT_URI']
KEY = os.environ['ACCOUNT_KEY']
DATABASE_NAME = 'testDatabase'
CONTAINER_NAME = 'products'
client = CosmosClient(URL, credential=KEY)
database = client.get_database_client(DATABASE_NAME)
container = database.get_container_client(CONTAINER_NAME)

operation_response = container.create_item({"id": "test_item", "productName": "test_item"})
operation_headers = operation_response.get_response_headers()
etag_value = operation_headers['etag']
request_charge = operation_headers['x-ms-request-charge']
```

### Using the asynchronous client

The asynchronous cosmos client is a separate client that looks and works in a similar fashion to the existing synchronous client. However, the async client needs to be imported separately and its methods need to be used with the async/await keywords.
The Async client needs to be initialized and closed after usage, which can be done manually or with the use of a context manager. The example below shows how to do so manually. We don't recommend doing it this way, since it requires that you manually call __aenter__() before using the client.

```python
from azure.cosmos.aio import CosmosClient
import os

URL = os.environ['ACCOUNT_URI']
KEY = os.environ['ACCOUNT_KEY']
DATABASE_NAME = 'testDatabase'
CONTAINER_NAME = 'products'    

async def create_products():
    client = CosmosClient(URL, credential=KEY)
    await client.__aenter__() # this piece is important for the SDK to cache account information
    database = client.get_database_client(DATABASE_NAME)
    container = database.get_container_client(CONTAINER_NAME)
    for i in range(10):
        await container.upsert_item({
                'id': 'item{0}'.format(i),
                'productName': 'Widget',
                'productModel': 'Model {0}'.format(i)
            }
        )
    await client.close() # the async client must be closed manually if it's not initialized in a with statement
```

Instead of manually opening and closing the client, it is highly recommended to use the `async with` keywords. This creates a context manager that will initialize and later close the client once you're out of the statement, as well as cache important information the SDK needs. The example below shows how to do so.

```python
from azure.cosmos.aio import CosmosClient
import os

URL = os.environ['ACCOUNT_URI']
KEY = os.environ['ACCOUNT_KEY']
DATABASE_NAME = 'testDatabase'
CONTAINER_NAME = 'products'

async def create_products():
    async with CosmosClient(URL, credential=KEY) as client: # the with statement will automatically initialize and close the async client
        database = client.get_database_client(DATABASE_NAME)
        container = database.get_container_client(CONTAINER_NAME)
        for i in range(10):
            await container.upsert_item({
                    'id': 'item{0}'.format(i),
                    'productName': 'Widget',
                    'productModel': 'Model {0}'.format(i)
                }
            )
```

### Queries with the asynchronous client

Unlike the synchronous client, the async client does not have an `enable_cross_partition` flag in the request. Queries without a specified partition key value will attempt to do a cross partition query by default. 

Query results can be iterated, but the query's raw output returns an asynchronous iterator. This means that each object from the iterator is an awaitable object, and does not yet contain the true query result. In order to obtain the query results you can use an async for loop, which awaits each result as you iterate on the object, or manually await each query result as you iterate over the asynchronous iterator.

Since the query results are an asynchronous iterator, they can't be cast into lists directly; instead, if you need to create lists from your results, use an async for loop or Python's list comprehension to populate a list:

```python
from azure.cosmos.aio import CosmosClient
import os

URL = os.environ['ACCOUNT_URI']
KEY = os.environ['ACCOUNT_KEY']
client = CosmosClient(URL, credential=KEY)
DATABASE_NAME = 'testDatabase'
database = client.get_database_client(DATABASE_NAME)
CONTAINER_NAME = 'products'
container = database.get_container_client(CONTAINER_NAME)

async def create_lists():
    results = container.query_items(
            query='SELECT * FROM products p WHERE p.productModel = "Model 2"')

    # iterates on "results" iterator to asynchronously create a complete list of the actual query results

    item_list = []
    async for item in results:
        item_list.append(item)

    # Asynchronously creates a complete list of the actual query results. This code performs the same action as the for-loop example above.
    item_list = [item async for item in results]
    await client.close()
```

### Using Integrated Cache
An integrated cache is an in-memory cache that helps you ensure manageable costs and low latency as your request volume grows. The integrated cache has two parts: an item cache for point reads and a query cache for queries. The code snippet below shows you how to use this feature with the point read and query cache methods.

The benefit of using this is that the point reads and queries that hit the integrated cache won't use any RUs. This means you will have a much lower per-operation cost than reads from the backend.

[How to configure the Azure Cosmos DB integrated cache (Preview)][cosmos_configure_integrated_cache]

```python
import azure.cosmos.cosmos_client as cosmos_client
import os

URL = os.environ['ACCOUNT_URI']
KEY = os.environ['ACCOUNT_KEY']
client = cosmos_client.CosmosClient(URL, credential=KEY)
DATABASE_NAME = 'testDatabase'
database = client.get_database_client(DATABASE_NAME)
CONTAINER_NAME = 'testContainer'
container = database.get_container_client(CONTAINER_NAME)

def integrated_cache_snippet():
    item_id = body['id'] 
    query = 'SELECT * FROM c'

    #item cache
    container.read_item(item=item_id, partition_key=item_id, max_integrated_cache_staleness_in_ms=30000)

    #query cache   
    container.query_items(query=query,
         partition_key=item_id, max_integrated_cache_staleness_in_ms=30000)
```
For more information on Integrated Cache, see [Azure Cosmos DB integrated cache - Overview][cosmos_integrated_cache].

### Using Transactional Batch
Transactional batch requests allow you to send several operations to be executed at once within the same partition key.
If all operations succeed in the order they're described within the transactional batch operation, the transaction will be committed.
However, if any operation fails, the entire transaction is rolled back.

Transactional batches have a limit of 100 operations per batch, and a total size limit of 1.2Mb for the
batch operations being passed in.

Transactional Batch operations look very similar to the singular operations apis, and are tuples containing
(`operation_type_string`, `args_tuple`, `batch_operation_kwargs_dictionary`), with the kwargs dictionary being optional:
```python
batch_operations = [
        ("create", (item_body,), kwargs),
        ("replace", (item_id, item_body), kwargs),
        ("read", (item_id,), kwargs),
        ("upsert", (item_body,), kwargs),
        ("patch", (item_id, operations), kwargs),
        ("delete", (item_id,), kwargs),
    ]
batch_results = container.execute_item_batch(batch_operations=batch_operations, partition_key=partition_key)
```
The batch operation kwargs dictionary is limited, and only takes a total of three different key values.
In the case of wanting to use conditional patching within the batch, the use of `filter_predicate` key is available for the
patch operation, or in case of wanting to use etags with any of the operations, the use of the `if_match_etag`/`if_none_match_etag`
keys is available as well.
```python
batch_operations = [
        ("replace", (item_id, item_body), {"if_match_etag": etag}),
        ("patch", (item_id, operations), {"filter_predicate": filter_predicate, "if_none_match_etag": etag}),
    ]
```

We also have some samples showing these transactional batch operations in action with both the [sync][sample_document_mgmt]
and [async][sample_document_mgmt_async] clients.

If there is a failure for an operation within the batch, the SDK will raise a `CosmosBatchOperationError` letting you know which operation failed,
as well as containing the list of failed responses for the failed request.

For more information on Transactional Batch, see [Azure Cosmos DB Transactional Batch][cosmos_transactional_batch].

### Public Preview - Vector Embeddings and Vector Indexes
We have added new capabilities to utilize vector embeddings and vector indexing for users to leverage vector
search utilizing our Cosmos SDK. These two container-level configurations have to be turned on at the account-level
before you can use them.

Each vector embedding should have a path to the relevant vector field in your items being stored, a supported data type
(float32, int8, uint8), the vector's dimensions, and the distance function being used for that embedding. Vectors indexed 
with the flat index type can be at most 505 dimensions. Vectors indexed with the quantizedFlat index type can be at most 4,096 dimensions.
A sample vector embedding policy would look like this:
```python
vector_embedding_policy = {
    "vectorEmbeddings": [
        {
            "path": "/vector1",
            "dataType": "float32",
            "dimensions": 256,
            "distanceFunction": "euclidean"
        },
        {
            "path": "/vector2",
            "dataType": "int8",
            "dimensions": 200,
            "distanceFunction": "dotproduct"
        },
        {
            "path": "/vector3",
            "dataType": "uint8",
            "dimensions": 400,
            "distanceFunction": "cosine"
        }
    ]
}
```

Separately, vector indexes have been added to the already existing indexing_policy and only require two fields per index:
the path to the relevant field to be used, and the type of index from the possible options - flat, quantizedFlat, or diskANN.
A sample indexing policy with vector indexes would look like this:
```python
indexing_policy = {
        "automatic": True,
        "indexingMode": "consistent",
        "compositeIndexes": [
            [
                {"path": "/numberField", "order": "ascending"},
                {"path": "/stringField", "order": "descending"}
            ]
        ],
        "spatialIndexes": [
            {"path": "/location/*", "types": [
                "Point",
                "Polygon"]}
        ],
        "vectorIndexes": [
            {"path": "/vector1", "type": "flat"},
            {"path": "/vector2", "type": "quantizedFlat"},
            {"path": "/vector3", "type": "diskANN"}
        ]
    }
```

For vector index types of diskANN and quantizedFlat, there are additional options available as well. These are:

quantizationByteSize - the number of bytes used in product quantization of the vectors. A larger value may result in better recall for vector searches at the expense of latency. This applies to index types diskANN and quantizedFlat. The allowed range is between 1 and the minimum between 512 and the vector dimensions. The default value is 64.

indexingSearchListSize - which represents the size of the candidate list of approximate neighbors stored while building the diskANN index as part of the optimization processes. This applies only to index type diskANN. The allowed range is between 25 and 500.

vectorIndexShardKey - a list of strings containing the shard keys used for partitioning vector indexes. The maximum allowed size for this array is 1, meaning that there is only one allowed path. This applies to index types diskANN and quantizedFlat.
```python
indexing_policy = {
        "automatic": True,
        "indexingMode": "consistent",
        "vectorIndexes": [
            {"path": "/vector1", "type": "quantizedFlat", "quantizationByteSize": 8},
            {"path": "/vector2", "type": "diskANN", "indexingSearchListSize": 50},
            {"path": "/vector3", "type": "diskANN", "vectorIndexShardKey": ["/country/city"]}
        ]
    }
```

You would then pass in the relevant policies to your container creation method to ensure these configurations are used by it.
The operation will fail if you pass new vector indexes to your indexing policy but forget to pass in an embedding policy.
```python
database.create_container(id=container_id, partition_key=PartitionKey(path="/id"),
                          indexing_policy=indexing_policy, vector_embedding_policy=vector_embedding_policy)
```
***Note: vector embeddings and vector indexes CANNOT be edited by container replace operations. They are only available directly through creation.***

### Public Preview - Vector Search

With the addition of the vector indexing and vector embedding capabilities, the SDK can now perform order by vector search queries.
These queries specify the VectorDistance to use as a metric within the query text. These must always use a TOP or LIMIT clause within the query though,
since vector search queries have to look through a lot of data otherwise and may become too expensive or long-running.
Since these queries are relatively expensive, the SDK sets a default limit of 50000 max items per query - if you'd like to raise that further, you
can use the `AZURE_COSMOS_MAX_ITEM_BUFFER_VECTOR_SEARCH` environment variable to do so. However, be advised that queries with too many vector results
may have additional latencies associated with searching in the service.
The query syntax for these operations looks like this:
```python
VectorDistance(<embedding1>, <embedding2>, [,<exact_search>], [,<specification>])
```
Embeddings 1 and 2 are the arrays of values for the relevant embeddings, `exact_search` is an optional boolean indicating whether
to do an exact search vs. an approximate one (default value of false), and `specification` is an optional Json snippet with embedding
specs that can include `dataType`, `dimensions` and `distanceFunction`. The specifications within the query will take precedence
to any configurations previously set by a vector embedding policy.
A sample vector search query would look something like this:
```python
    query = "SELECT TOP 10 c.title,VectorDistance(c.embedding, [{}]) AS " \
            "SimilarityScore FROM c ORDER BY VectorDistance(c.embedding, [{}])".format(embeddings_string, embeddings_string)
```
Or if you'd like to add the optional parameters to the vector distance, you could do this:
```python
    query = "SELECT TOP 10 c.title,VectorDistance(c.embedding, [{}], true, {{'dataType': 'float32' , 'distanceFunction': 'cosine'}}) AS " \
            "SimilarityScore FROM c ORDER BY VectorDistance(c.embedding, [{}], true, {{'dataType': " \
            "'float32', 'distanceFunction': 'cosine'}})".format(embeddings_string, embeddings_string)
```
The `embeddings_string` above would be your string made from your vector embeddings.
You can find our sync samples [here][cosmos_index_sample] and our async samples [here][cosmos_index_sample_async] as well to help yourself out.

*Note: For a limited time, if your query operates against a region or emulator that has not yet been updated the client might run into some issues
not being able to recognize the new NonStreamingOrderBy capability that makes vector search possible.
If this happens, you can set the `AZURE_COSMOS_DISABLE_NON_STREAMING_ORDER_BY` environment variable to `"True"` to opt out of this
functionality and continue operating as usual.*

### Public Preview - Full Text Policy and Full Text Indexes
We have added new capabilities to utilize full text policies and full text indexing for users to leverage full text search
utilizing our Cosmos SDK. These two container-level configurations have to be turned on at the account-level
before you can use them.

A full text policy allows the user to define the default language to be used for all full text paths, or to set
a language for each path individually in case the user would like to use full text search on data containing different
languages in different fields.

A sample full text policy would look like this:
```python
full_text_policy = {
    "defaultLanguage": "en-US",
    "fullTextPaths": [
        {
            "path": "/text1",
            "language": "en-US"
        },
        {
            "path": "/text2",
            "language": "en-US"
        }
    ]
}
```
Currently, the only supported language is `en-US` - using the relevant ISO-639 language code to ISO-3166 country code.
Any non-supported language or code will return an exception when trying to use it - which will also include the list of supported languages.
This list will include more options in the future; for more information on supported languages, please see [here][cosmos_fts].

Full text search indexes have been added to the already existing indexing_policy and only require the path to the
relevant field to be used.
A sample indexing policy with full text search indexes would look like this:
```python
indexing_policy = {
        "automatic": True,
        "indexingMode": "consistent",
        "compositeIndexes": [
            [
                {"path": "/numberField", "order": "ascending"},
                {"path": "/stringField", "order": "descending"}
            ]
        ],
        "fullTextIndexes": [
            {"path": "/abstract"}
        ]
    }
```
Modifying the index in a container is an asynchronous operation that can take a long time to finish. See [here][cosmos_index_policy_change] for more information.
For more information on using full text policies and full text indexes, see [here][cosmos_fts].

### Public Preview - Full Text Search and Hybrid Search

With the addition of the full text indexing and full text policies, the SDK can now perform full text search and hybrid search queries.
These queries can utilize the new query functions `FullTextContains()`, `FullTextContainsAll`, and `FullTextContainsAny` to efficiently
search for the given terms within your item fields.

Beyond these, you can also utilize the new `Order By RANK` and `Order By RANK RRF` along with `FullTextScore` to execute the [BM25][BM25] scoring algorithm
or [Reciprocal Rank Fusion][RRF] (RRF) on your query, finding the items with the highest relevance to the terms you are looking for.
All of these mentioned queries would look something like this:

- `SELECT TOP 10 c.id, c.text FROM c WHERE FullTextContains(c.text, 'quantum')`


- `SELECT TOP 10 c.id, c.text FROM c WHERE FullTextContainsAll(c.text, 'quantum', 'theory')`


- `SELECT TOP 10 c.id, c.text FROM c WHERE FullTextContainsAny(c.text, 'quantum', 'theory')`


- `SELECT TOP 10 c.id, c.text FROM c ORDER BY RANK FullTextScore(c.text, ['quantum', 'theory'])`


- `SELECT TOP 10 c.id, c.text FROM c ORDER BY RANK RRF(FullTextScore(c.text, ['quantum', 'theory']), FullTextScore(c.text, ['model']))`


- `SELECT TOP 10 c.id, c.text FROM c ORDER BY RANK RRF(FullTextScore(c.text, ['quantum', 'theory']), FullTextScore(c.text, ['model']), VectorDistance(c.embedding, {item_embedding}))"`

These queries must always use a TOP or LIMIT clause within the query since hybrid search queries have to look through a lot of data otherwise and may become too expensive or long-running.
Since these queries are relatively expensive, the SDK sets a default limit of 1000 max items per query - if you'd like to raise that further, you
can use the `AZURE_COSMOS_HYBRID_SEARCH_MAX_ITEMS` environment variable to do so. However, be advised that queries with too many vector results
may have additional latencies associated with searching in the service.

You can find our sync samples [here][cosmos_index_sample] and our async samples [here][cosmos_index_sample_async] as well for additional guidance.

## Troubleshooting

### General

When you interact with Cosmos DB using the Python SDK, exceptions returned by the service correspond to the same HTTP status codes returned for REST API requests:

[HTTP Status Codes for Azure Cosmos DB][cosmos_http_status_codes]

For example, if you try to create a container using an ID (name) that's already in use in your Cosmos DB database, a `409` error is returned, indicating the conflict. In the following snippet, the error is handled gracefully by catching the exception and displaying additional information about the error.

```python
try:
    database.create_container(id=CONTAINER_NAME, partition_key=PartitionKey(path="/productName"))
except exceptions.CosmosResourceExistsError:
    print("""Error creating container
HTTP status code 409: The ID (name) provided for the container is already in use.
The container name must be unique within the database.""")

```
### Logging Diagnostics

This library uses the standard
[logging](https://docs.python.org/3.5/library/logging.html) library for logging diagnostics.
Basic information about HTTP sessions (URLs, headers, etc.) is logged at INFO
level.
**Note: You must use 'azure.cosmos' for the logger**
Detailed DEBUG level logging, including request/response bodies and unredacted
headers, can be enabled on a client with the `logging_enable` argument:
```python
import sys
import logging
from azure.cosmos import CosmosClient

# Create a logger for the 'azure' SDK
logger = logging.getLogger('azure.cosmos')
logger.setLevel(logging.DEBUG)

# Configure a console output
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

# This client will log detailed information about its HTTP sessions, at DEBUG level
client = CosmosClient(URL, credential=KEY, logging_enable=True)
```

Similarly, `logging_enable` can enable detailed logging for a single operation,
even when it isn't enabled for the client:
```python
database = client.create_database(DATABASE_NAME, logging_enable=True)
```
Alternatively, you can log using the CosmosHttpLoggingPolicy, which extends from the azure core HttpLoggingPolicy, by passing in your logger to the `logger` argument.
By default, it will use the behaviour from HttpLoggingPolicy. Passing in the `enable_diagnostics_logging` argument will enable the
CosmosHttpLoggingPolicy, and will have additional information in the response relevant to debugging Cosmos issues.
```python
import logging
from azure.cosmos import CosmosClient

#Create a logger for the 'azure' SDK
logger = logging.getLogger('azure.cosmos')
logger.setLevel(logging.DEBUG)

# Configure a file output
handler = logging.FileHandler(filename="azure")
logger.addHandler(handler)

# This client will log diagnostic information from the HTTP session by using the CosmosHttpLoggingPolicy.
# Since we passed in the logger to the client, it will log information on every request.
client = CosmosClient(URL, credential=KEY, logger=logger, enable_diagnostics_logging=True)
```
Similarly, logging can be enabled for a single operation by passing in a logger to the singular request.
However, if you desire to use the CosmosHttpLoggingPolicy to obtain additional information, the `enable_diagnostics_logging` argument needs to be passed in at the client constructor.
```python
# This example enables the CosmosHttpLoggingPolicy and uses it with the `logger` passed in to the `create_database` request.
client = CosmosClient(URL, credential=KEY, enable_diagnostics_logging=True)
database = client.create_database(DATABASE_NAME, logger=logger)
```
**NOTICE: The Following is a Preview Feature that is subject to significant change.**
To further customize what gets logged, you can use a  **PREVIEW** diagnostics handler to filter out the logs you don't want to see.
There are several ways to use the diagnostics handler, those include the following:
- Using the "CosmosDiagnosticsHandler" class, which has default behaviour that can be modified.
    **NOTE: The diagnostics handler will only be used if the `enable_diagnostics_logging` argument is passed in at the client constructor.
      The CosmosDiagnosticsHandler is also a special type of dictionary that is callable and that has preset keys. The values it expects are functions related to it's relevant diagnostic data. (e.g. ```diagnostics_handler["duration"]``` expects a function that takes in an int and returns a boolean as it relates to the duration of an operation to complete).**
    ```python
    from azure.cosmos import CosmosClient, CosmosDiagnosticsHandler
    import logging
    # Initialize the logger
    logger = logging.getLogger('azure.cosmos')
    logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler('diagnostics1.output')
    logger.addHandler(file_handler)
    diagnostics_handler = cosmos_diagnostics_handler.CosmosDiagnosticsHandler()
    diagnostics_handler["duration"] = lambda x: x > 2000
    client = CosmosClient(URL, credential=KEY,logger=logger, diagnostics_handler=diagnostics_handler, enable_diagnostics_logging=True)
    
    ```
- Using a dictionary with the relevant functions to filter out the logs you don't want to see.
    ```python
    # Initialize the logger
    logger = logging.getLogger('azure.cosmos')
    logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler('diagnostics2.output')
    logger.addHandler(file_handler)
    diagnostics_handler = {
        "duration": lambda x: x > 2000
    }
    client = CosmosClient(URL, credential=KEY,logger=logger, diagnostics_handler=diagnostics_handler, enable_diagnostics_logging=True)
    ```
- Using a function that will replace the should_log function in the CosmosHttpLoggingPolicy which expects certain paramameters and returns a boolean. **Note: the parameters of the custom should_log must match the parameters of the original should_log function as shown in the sample.**
  ```python
  # Custom should_log method
  def should_log(self, **kwargs):
      return kwargs.get('duration') and kwargs['duration'] > 2000
  
  # Initialize the logger
  logger = logging.getLogger('azure.cosmos')
  logger.setLevel(logging.INFO)
  file_handler = logging.FileHandler('diagnostics3.output')
  logger.addHandler(file_handler)
  
  # Initialize the Cosmos client with custom diagnostics handler
  client = CosmosClient(endpoint, key,logger=logger, diagnostics_handler=should_log, enable_diagnostics_logging=True)
    ```

### Telemetry
Azure Core provides the ability for our Python SDKs to use OpenTelemetry with them. The only packages that need to be installed
to use this functionality are the following:
```bash
pip install azure-core-tracing-opentelemetry
pip install opentelemetry-sdk
```
For more information on this, we recommend taking a look at this [document](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core-tracing-opentelemetry/README.md) 
from Azure Core describing how to set it up. We have also added a [sample file][telemetry_sample] to show how it can
be used with our SDK. This works the same way regardless of the Cosmos client you are using.

## Next steps

For more extensive documentation on the Cosmos DB service, see the [Azure Cosmos DB documentation][cosmos_docs] on learn.microsoft.com.

<!-- LINKS -->
[azure_cli]: https://learn.microsoft.com/cli/azure
[azure_portal]: https://portal.azure.com
[azure_sub]: https://azure.microsoft.com/free/
[cloud_shell]: https://learn.microsoft.com/azure/cloud-shell/overview
[cosmos_account_create]: https://learn.microsoft.com/azure/cosmos-db/how-to-manage-database-account
[cosmos_account]: https://learn.microsoft.com/azure/cosmos-db/account-overview
[cosmos_container]: https://learn.microsoft.com/azure/cosmos-db/databases-containers-items#azure-cosmos-containers
[cosmos_database]: https://learn.microsoft.com/azure/cosmos-db/databases-containers-items#azure-cosmos-databases
[cosmos_docs]: https://learn.microsoft.com/azure/cosmos-db/
[cosmos_samples]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cosmos/azure-cosmos/samples
[cosmos_pypi]: https://pypi.org/project/azure-cosmos/
[cosmos_http_status_codes]: https://learn.microsoft.com/rest/api/cosmos-db/http-status-codes-for-cosmosdb
[cosmos_item]: https://learn.microsoft.com/azure/cosmos-db/databases-containers-items#azure-cosmos-items
[cosmos_models]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cosmos/azure-cosmos/azure/cosmos/_models.py
[cosmos_request_units]: https://learn.microsoft.com/azure/cosmos-db/request-units
[cosmos_resources]: https://learn.microsoft.com/azure/cosmos-db/databases-containers-items
[cosmos_sql_queries]: https://learn.microsoft.com/azure/cosmos-db/how-to-sql-query
[cosmos_ttl]: https://learn.microsoft.com/azure/cosmos-db/time-to-live
[cosmos_integrated_cache]: https://learn.microsoft.com/azure/cosmos-db/integrated-cache
[cosmos_configure_integrated_cache]: https://learn.microsoft.com/azure/cosmos-db/how-to-configure-integrated-cache
[python]: https://www.python.org/downloads/
[ref_container_delete_item]: https://aka.ms/azsdk-python-cosmos-ref-delete-item
[ref_container_query_items]: https://aka.ms/azsdk-python-cosmos-ref-query-items
[ref_container_upsert_item]: https://aka.ms/azsdk-python-cosmos-ref-upsert-item
[ref_container]: https://aka.ms/azsdk-python-cosmos-ref-container
[ref_cosmos_sdk]: https://aka.ms/azsdk-python-cosmos-ref
[ref_cosmosclient_create_database]: https://aka.ms/azsdk-python-cosmos-ref-create-database
[ref_cosmosclient]: https://aka.ms/azsdk-python-cosmos-ref-cosmos-client
[ref_database]: https://aka.ms/azsdk-python-cosmos-ref-database
[ref_httpfailure]: https://aka.ms/azsdk-python-cosmos-ref-http-failure
[sample_database_mgmt]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cosmos/azure-cosmos/samples/database_management.py
[sample_document_mgmt]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cosmos/azure-cosmos/samples/document_management.py
[sample_document_mgmt_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cosmos/azure-cosmos/samples/document_management_async.py
[sample_examples_misc]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cosmos/azure-cosmos/samples/examples.py
[source_code]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cosmos/azure-cosmos
[venv]: https://docs.python.org/3/library/venv.html
[virtualenv]: https://virtualenv.pypa.io
[telemetry_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cosmos/azure-cosmos/samples/tracing_open_telemetry.py
[timeouts_document]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cosmos/azure-cosmos/docs/TimeoutAndRetriesConfig.md
[cosmos_transactional_batch]: https://learn.microsoft.com/azure/cosmos-db/nosql/transactional-batch
[cosmos_concurrency_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cosmos/azure-cosmos/samples/concurrency_sample.py
[cosmos_index_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cosmos/azure-cosmos/samples/index_management.py
[cosmos_index_sample_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cosmos/azure-cosmos/samples/index_management_async.py
[RRF]: https://learn.microsoft.com/azure/search/hybrid-search-ranking
[BM25]: https://learn.microsoft.com/azure/search/index-similarity-and-scoring
[cosmos_fts]: https://aka.ms/cosmosfulltextsearch
[cosmos_index_policy_change]: https://learn.microsoft.com/azure/cosmos-db/index-policy#modifying-the-indexing-policy

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.