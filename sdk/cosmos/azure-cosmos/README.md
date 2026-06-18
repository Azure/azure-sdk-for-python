# Azure Cosmos DB SQL API client library for Python

This is the `azure-cosmos` Python package. It contains the usual Python
client (`CosmosClient`, `Container.create_item`, etc.) plus a Rust
backend that some operations can route through instead of the legacy
Python HTTP path.

This README only covers **building it locally and running the tests**.
For architecture and design, see the docs under `docs/`.

---

## Before you start

You need three things on your machine:

1. **Python 3.9 or newer.** Run `python --version` to check.
2. **A Rust toolchain**, because part of this package compiles from Rust.
   Install via [rustup](https://rustup.rs/); any stable version ≥ 1.75 works.
   Run `cargo --version` to check.
3. **Either the Cosmos DB Emulator running on `https://localhost:8081`,
   or a real Cosmos DB account.** The emulator is the simpler choice for
   local work — [download here](https://learn.microsoft.com/azure/cosmos-db/local-emulator).
   You only need this for the integration tests; pure unit tests run
   without it.

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

### Native Retryable Writes
We have added native retryable writes to the SDK, a feature that can be used by customers who don't mind the
non-idempotency of these retries and would instead like to ensure that the given operation executed in case of timeouts
or connectivity issues (status codes 408, 5xx).

This feature can be enabled either at the client level, to retry all write operations under these conditions, 
or at the per-request level to enable the retries for an individual request.

If enabled at the client level, the one exception to the rule would be patch requests, since the operations can change
the nature of the overall request - replace, set, and copy for example would be idempotent while add, move or remove would
not be idempotent unless combined with patch precondition checks. So, for patch we allow opting-in into automatic
retries only on the request options level.

The snippet below shows how to enable this feature at the client and request level:
```python
cosmos_client = CosmosClient(
    url=URL,
    credential=KEY,
    retry_write=1,  # enables a single native retryable write at the client level
)

database = cosmos_client.get_database_client(DATABASE_NAME)
container = database.get_container_client(CONTAINER_NAME)

container.create_item(
    item_body,
    retry_write=1  # enables a single native retryable write at the request level
)
```


### Vector Embeddings and Vector Indexes
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

### Public Preview - Embedding Generation Service (EGS)

A vector embedding may optionally include an `embeddingSource` describing how the embedding is generated by the
service. The source specifies the item paths whose values are embedded (`sourcePaths`), the embedding model
deployment (`deploymentName`, `modelName`), the embedding service `endpoint`, and the `authType` used to call
that endpoint (one of `ApiKey` or `Entra`).

The `endpoint` is the HTTPS URL of the Azure AI Foundry / Azure OpenAI resource that hosts the embedding model
deployment named by `deploymentName` (for example, `https://<resource>.openai.azure.com/`). This is the
model-serving endpoint, not the Cosmos account endpoint.

When `authType` is `Entra`, the Cosmos account's managed identity is used to call the embedding endpoint; that
identity must be granted the appropriate role on the embedding resource (for example, `Cognitive Services OpenAI
User`). The SDK is not in the call path, so role assignments on the application's identity do not affect this
flow.

A vector embedding policy that includes an embedding source looks like this:
```python
vector_embedding_policy = {
    "vectorEmbeddings": [
        {
            "path": "/embedding",
            "dataType": "float32",
            "dimensions": 1536,
            "distanceFunction": "cosine",
            "embeddingSource": {
                "sourcePaths": [
                    "/journal_title",
                    "/title",
                    "/toc_abstract",
                    "/abstract",
                    "/full_text"
                ],
                "deploymentName": "text-embedding-3-small",
                "modelName": "text-embedding-3-small",
                "endpoint": "https://<resource>.openai.azure.com/",
                "authType": "ApiKey"
            }
        }
    ]
}
```

A few service-side invariants are worth keeping in mind when using EGS:

* **`vectorIndexes[*].path` must match the embedding's `path`, not any `sourcePaths` entry.** In the example above,
  the indexable path is `/embedding`; the `sourcePaths` (`/journal_title`, `/title`, ...) are only the inputs that
  the service reads to compute the vector stored at `/embedding`.
* **`embeddingSource` should be treated as fixed at container creation.** The vector embedding paths themselves
  are immutable via `replace_container`; the SDK currently does not test or guarantee that the sub-fields of
  `embeddingSource` (`sourcePaths`, `deploymentName`, `modelName`, `endpoint`, `authType`) can be safely modified
  after creation. Plan to set them once at creation time.
* **RU cost on the write path.** When `embeddingSource` is configured, every insert and upsert incurs the
  additional work of calling the embedding endpoint, persisting the generated vector, and indexing it. This is a
  non-trivial new RU charge that should be accounted for during capacity planning.

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

### Vector Search

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

You can also use Weighted Reciprocal Rank Fusion to assign different weights to the different scores being used in the RRF function.
This is done by passing in a list of weights to the RRF function in the query. **NOTE: If more weights are given than there are components of the RRF function, or if weights are missing a BAD REQUEST exception will occur.**
- `SELECT TOP 10 c.id, c.text FROM c ORDER BY RANK RRF(FullTextScore(c.text, ['quantum', 'theory']), FullTextScore(c.text, ['model']), VectorDistance(c.embedding, {item_embedding}), [0.5, 0.3, 0.2])`


- `SELECT TOP 10 c.id, c.text FROM c ORDER BY RANK RRF(FullTextScore(c.text, ['quantum', 'theory']), FullTextScore(c.text, ['model']), VectorDistance(c.embedding, {item_embedding}), [-0.5, 0.3, 0.2])`

These queries must always use a TOP or LIMIT clause within the query since hybrid search queries have to look through a lot of data otherwise and may become too expensive or long-running.
Since these queries are relatively expensive, the SDK sets a default limit of 1000 max items per query - if you'd like to raise that further, you
can use the `AZURE_COSMOS_HYBRID_SEARCH_MAX_ITEMS` environment variable to do so. However, be advised that queries with too many vector results
may have additional latencies associated with searching in the service.

You can find our sync samples [here][cosmos_index_sample] and our async samples [here][cosmos_index_sample_async] as well for additional guidance.

### Public Preview - Throughput Buckets
When multiple workloads share the same Azure Cosmos DB container, resource contention can lead to throttling, increased latency, and potential business impact.
To address this, Cosmos DB allows you to allocate throughput buckets, which help manage resource consumption for workloads sharing a Cosmos DB container by limiting the maximum throughput a bucket can consume.
However, throughput isn't reserved for any bucket, it remains shared across all workloads.

Up to five (5) throughput buckets can be configured per container, with an ID ranging from 1-5. Each bucket has a maximum throughput percentage, capping the fraction of the container’s total throughput that it can consume.
Requests assigned to a bucket can consume throughput only up to this limit. If the bucket exceeds its configured limit, subsequent requests are throttled. 
This ensures that no single workload consumes excessive throughput and impacts others.

Throughput bucket configurations can be changed once every 10 minutes, otherwise the request is throttled with an HTTP 429 status code and substatus code 3213.
Also, requests with an invalid bucket ID (less than 1 or greater than 5) results in an error, as only bucket IDs 1 to 5 are valid.

See [here][cosmos_throughput_bucket_configuration] for instructions on configuring throughput buckets through the Azure portal.
After throughput buckets have been configured, you can find our sync samples [here][cosmos_throughput_bucket_sample] and our async samples [here][cosmos_throughput_bucket_sample_async] as well for additional guidance.

### Per Partition Circuit Breaker 
Per partition circuit breaker is a feature that allows the SDK to failover requests on a partition level to another region based on client side statistics on 408 and 5xx error codes. This feature is only applicable for 
reads in single write region accounts and reads and writes for multi-write region accounts. The following are the environment variables to enable per partition circuit breaker and to modify the thresholds for failing over 
requests to another region:
- `AZURE_COSMOS_ENABLE_CIRCUIT_BREAKER`: Default is `False`.
  - Enables the per partition circuit breaker feature.
- `AZURE_COSMOS_CONSECUTIVE_ERROR_COUNT_TOLERATED_FOR_READ`: Default is `10` consecutive errors.
  - After a partition has encountered 10 consecutive errors for read requests, the SDK will send requests routed to that partition to another region.
- `AZURE_COSMOS_CONSECUTIVE_ERROR_COUNT_TOLERATED_FOR_WRITE`: Default is `5` consecutive errors.
    - After a partition has encountered 5 consecutive errors for write requests, the SDK will send requests routed to that partition to another region.
- `AZURE_COSMOS_FAILURE_PERCENTAGE_TOLERATED`: Default is a `90` percent failure rate.
  - After a partition reaches a 90 percent failure rate for all requests, the SDK will send requests routed to that partition to another region.

### Per Partition Automatic Failover (Public Preview)
Per partition automatic failover enables the SDK to automatically redirect write requests at the partition level to another region based on service-side signals. This feature is available 
only for single write region accounts that have at least one read-only region. When per partition automatic failover is enabled, per partition circuit breaker and cross-region hedging is enabled by default, meaning 
all its configurable options also apply to per partition automatic failover. To enable this feature, follow the guide [here](https://learn.microsoft.com/azure/cosmos-db/how-to-configure-per-partition-automatic-failover).

### Cross Region Hedging Availability Strategy

Cross region hedging availability strategy improves availability and reduces latency by sending duplicate requests to secondary regions if the primary region is slow or unavailable. The SDK uses the first successful response, helping to mitigate regional outages or high latency.

#### Key Concepts

- **Hedged Requests**: The SDK sends a parallel request to another region if the primary region does not respond within a configured delay.
- **Configurable**: Hedging can be enabled or disabled, and the delay before sending a hedged request is tunable.
- **ThreadPoolExecutor**: The sync CosmosClient instance will use a ThreadPoolExecutor under the hood for parallelizing requests. Users can choose whether to use the default ThreadPoolExecutor the SDK uses, or to pass in their own instance. *The async client does not need the executor since it uses asynchronous logic to parallelize requests.*

#### Enabling Cross Region Hedging

You can enable cross region hedging by passing the `availability_strategy` parameter to the `CosmosClient` or per-request. This parameter accepts:

- **`True`**: Enable hedging with default values (`threshold_ms=500`, `threshold_steps_ms=100`) or override client settings to this default at the request level.
- **`False`**: Explicitly disable hedging at the client or request level (overrides client-level settings)
- **`dict`**: Enable hedging with custom values. The keys are `threshold_ms` (delay before sending a hedged request) and `threshold_steps_ms` (step interval for additional hedged requests). Missing keys will use default values.
- **`None`**: Default value only usable at the request level. Use the client-level configurations.

Hedging will also be implicitly enabled when per-partition automatic failover is enabled, in which case the `CrossRegionHedgingStrategy` applies the default values outlined above of 500 ms for `threshold_ms` and 100 ms for `threshold_steps_ms` unless you override them via `availability_strategy`.

#### Client-level configuration

```python
from azure.cosmos import CosmosClient

# Enable with default values
client = CosmosClient(
    "<account-uri>",
    "<account-key>",
    availability_strategy=True
)

# Enable with custom values
client = CosmosClient(
    "<account-uri>",
    "<account-key>",
    availability_strategy={"threshold_ms": 150, "threshold_steps_ms": 50}
)
```

#### Request-level configuration

```python
# Override or provide the strategy per request with custom values
container.read_item(
    item="item_id",
    partition_key="pk_value",
    availability_strategy={"threshold_ms": 150, "threshold_steps_ms": 50}
)

# Enable with default values for a specific request
container.read_item(
    item="item_id",
    partition_key="pk_value",
    availability_strategy=True
)
```

#### Disable availability strategy on request level

```python
# Disable cross region hedging for a specific request, even if enabled at client level
container.read_item(
    item="item_id",
    partition_key="pk_value",
    availability_strategy=False
)
```

#### Customized executor for hedging for sync client

```python
# Pass in your own custom TheadPoolExecutor to use with the sync client
from concurrent.futures import ThreadPoolExecutor
from azure.cosmos import CosmosClient

executor = ThreadPoolExecutor(max_workers=2)
client = CosmosClient(
    "<account-uri>",
    "<account-key>",
    availability_strategy=True,  # or use a dict for custom values
    availability_strategy_executor=executor
)
```

#### Customized max concurrency for hedging for async client

```python
# Customize the max concurrency for the async client
from azure.cosmos.aio import CosmosClient

client = CosmosClient(
    "<account-uri>",
    "<account-key>",
    availability_strategy=True,  # or use a dict for custom values
    availability_strategy_max_concurrency=2
)
```

### Cross Region Hedging - Best Practices

1. Configure appropriate thresholds based on your application's needs:
   - Lower thresholds: More aggressive hedging, potentially higher costs
   - Higher thresholds: More conservative, may impact latency

2. Use request-level overrides judiciously:
   - Disable hedging for non-critical operations
   - Use custom thresholds for latency-sensitive operations

3. Monitor usage:
   - Track hedging patterns
   - Adjust thresholds based on observed performance

4. Enable multiple write regions when write availability is critical

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
>>>>>>> main

```
<your repos folder>/
├── azure-sdk-for-python/   ← you are here
└── azure-sdk-for-rust/
```

If you don't have it, clone it now:

```powershell
cd ..\..\..\..\..        # back up to <your repos folder>
git clone https://github.com/Azure/azure-sdk-for-rust.git
cd azure-sdk-for-python\sdk\cosmos\azure-cosmos
```

The build will tell you immediately if it can't find that clone — see
"When the build complains" at the bottom.

---

## Set things up once

From this directory (`sdk/cosmos/azure-cosmos`):

```powershell
# maturin = build tool that compiles Rust + drops the result into the
# Python package. The other three are test deps. Install straight into
# whatever Python you're using (system Python is fine -- maturin 1.x
# installs into system site-packages without complaint; a venv works
# too if you prefer one).
pip install -U pip maturin pytest pytest-asyncio
pip install -r dev_requirements.txt
```

> **Note.** Earlier versions of this README claimed maturin "refuses to
> install into your system Python" and required a venv. That was true
> of older maturin (pre-1.0) but is no longer the case. If you already
> have a `.venv` activated, maturin will use it; if you don't, maturin
> installs the wheel into the system Python's `site-packages` like any
> other `pip install -e` would.

---

## Build the Rust part

The Rust code compiles into a single file called `_rust.pyd` (Windows)
or `_rust.so` (Linux/macOS). It lands in `azure/cosmos/` next to the
`.py` files, and Python imports it as `azure.cosmos._rust`.

**One thing to know first:** if an old `_rust.pyd` is sitting in
`azure/cosmos/` from a previous build, Python will load *that* and
ignore your new code. Symptom is usually
`AttributeError: module 'azure.cosmos._rust' has no attribute 'init_client'`
at runtime, even though `init_client` is right there in the source.
So clean before you build:

```powershell
# 1. Wipe any old _rust.pyd.
Get-ChildItem azure\cosmos -Filter "_rust*" -Recurse -ErrorAction SilentlyContinue |
    Remove-Item -Force

# 2. Build + install in editable mode.
maturin develop
```

First build pulls and compiles a few hundred Rust crates; expect 5–10
minutes. Subsequent builds are seconds — Cargo caches everything in
`target/`.

Did it work? This one-liner imports the new module and prints what it
exposes:

```powershell
python -c "from azure.cosmos import _rust; print(sorted(a for a in dir(_rust) if not a.startswith('_')))"
# Expected: ['create_item', 'init_client']
```

If you see anything other than those two names, you have a stale `.pyd`
— re-run the cleanup step.

(If you can't use a venv for some reason, `maturin build --release`
followed by `Copy-Item target\release\azure_cosmos_rust.dll azure\cosmos\_rust.pyd -Force`
does the same thing by hand.)

---

## Smoke test: one round trip Python → Rust → Cosmos

Before running any test suite, run the smoke test. It cuts out the
*entire* Python helper layer (request-prep, options parsing, PK
serialization, body marshalling, auto-id) and exercises only:

  PyO3 marshalling → driver authenticates → driver opens HTTPS
   → driver POSTs to /docs → driver parses response → PyO3 back

So a green smoke test means the binding + driver round-trip is wired
correctly all the way to your Cosmos endpoint. A failure here is below
the helper layer; a failure in the parity suite on top of a green
smoke test is in the helper layer or in response translation.

```powershell
python tests\create_item\smoke_test_rust_create_item.py
```

By default this points at the emulator and expects:

- a database named `pyo3test`
- inside it, a container named `items` partitioned on `/pk`

Create those once via the emulator's Data Explorer (or the Azure CLI
commands shown in the script's module docstring).

To point at a real account instead:

```powershell
$env:COSMOS_ENDPOINT = "<your-cosmos-account-uri>"
$env:COSMOS_KEY      = "<your-cosmos-account-key>"
python tests\create_item\smoke_test_rust_create_item.py
```

What the smoke test prints, in order: the endpoint, the container
link, the item id it minted, then `status_code`, `sub_status`, and the
first 200 bytes of the response body. A successful run ends with
`OK -- round trip Python -> PyO3 -> driver -> Cosmos succeeded.` and
exits 0. Exit codes: `0` round-trip OK, `1` non-2xx from the service
(error body is printed above), `2` the compiled `_rust` module is not
importable (run `maturin develop`).

What the smoke test does **not** check (so don't read too much into a
green run): response-header parity, typed exceptions on 4xx/5xx,
response-body parsing into a Python dict, or any routing options
(consistency level, session token, priority, throughput bucket, ...).
Those are covered by the parity suite below.

---

## Run the parity suite (Rust path vs. Python path)

The parity suite calls `create_item` with the same input twice — once
through the legacy Python backend, once through the Rust backend — and
diffs the results. It's how we catch behaviour drift while the Rust
path is being built out.

```powershell
$env:ACCOUNT_URI = "https://localhost:8081"
$env:ACCOUNT_KEY = "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw=="

pytest tests/create_item/sync/test_create_item_parity.py -v          # only failures show diffs
pytest tests/create_item/sync/test_create_item_parity.py -v -s -rA   # show diff + every test in the summary
```

If you don't set the env vars, the suite skips cleanly. If you set them
but never built the Rust extension, the suite skips with a "run maturin
develop" message.

The in-process parity tests above are a CI gate, not an audit-doc
source. Each test runs both backends inside one pytest process via
`BackendComparison` and asserts on the diff; a failure prints the full
`PARITY CALL:` block to the CI log so the contributor sees the
evidence directly.

A rolling, human-readable per-operation audit doc is produced by a
separate workflow: two pytest runs against per-op `legacy/` folders
(one on core-python, one on rust), then `scripts/v5/build_legacy_parity_audit.py`
pairs the two transcripts and writes the audit markdown. The rendered
markdown is per-developer-run output and is not checked in.

Tests marked `@pytest.mark.skip(reason="...")` cover known driver- or
binding-side gaps; the reason string names the specific limitation in
plain English. `git grep "Permanent skip"` finds every test waiting on
a Python-only feature that the Rust path can't match.

---

## Run the unit tests (no emulator needed)

Everything under `tests/` that doesn't talk to Cosmos:

```powershell
pytest tests/ -q
```

Just the Rust-integration unit subset (the ones that exercise the
binding without making network calls):

```powershell
pytest tests/test_backend_wiring_unit.py `
       tests/test_item_helper_unit.py `
       tests/test_request_prep_unit.py `
       tests/test_response_parse_unit.py `
       tests/test_pk_wire_unit.py `
       tests/test_body_wire_unit.py `
       tests/test_auto_id_unit.py `
       tests/test_options_unit.py `
       tests/test_container_rid_helper_unit.py `
       tests/test_create_item_parity.py -q
```

---

## When the build complains

A few specific failure modes show up enough to be worth naming.

**`failed to read .../azure-sdk-for-rust/...Cargo.toml`** — your sibling
`azure-sdk-for-rust` clone is missing or in a different folder. Either
clone it next to `azure-sdk-for-python` (see the layout in "Before you
start"), or edit the three `path = ...` lines (one in
`azure_cosmos_rust/Cargo.toml`, two in `Cargo.toml`) to point at where
your clone actually lives.

**`expected struct azure_core::Error, found struct azure_core::Error`**
— same type name, two different copies. Means the binding crate and the
driver crate ended up pulling `azure_core` from two different sources.
Check `Cargo.toml` (the one in this directory): `azure_core` and
`azure_identity` must both be `path = ...` deps into the same external
`azure-sdk-for-rust` clone the driver is using. Don't mix `path` and
`git`.

**`AttributeError: module 'azure.cosmos._rust' has no attribute ...`** —
stale `_rust.pyd`. Clean and rebuild:

```powershell
Get-ChildItem azure\cosmos -Filter "_rust*" -Recurse | Remove-Item -Force
maturin develop
```

**Anything else, before reaching for `cargo clean`:**

```powershell
cargo check          # compiles without linking — fastest "did Rust break?" signal
```

If `cargo check` is green and you still can't run, the issue is in the
Python wiring or in maturin's install step, not in the Rust code.

`cargo clean` (nukes `target/`) is the last resort — it costs you the
5–10-minute first-build time again.

---

## What rebuilds when

- Edited Python? Nothing to rebuild. Editable install picks it up.
- Edited Rust (anything under `azure_cosmos_rust/` or in the external
  driver clone)? Run `maturin develop` again before `pytest`.
- Edited a `Cargo.toml`? `maturin develop` will pick it up; if you only
  changed deps, `cargo check` first is faster.

