# Azure Cosmos DB SQL API client library for Python

Azure Cosmos DB is a globally distributed, multi-model database service that supports document, key-value, wide-column, and graph databases.

Use the Azure Cosmos DB SQL API SDK for Python to manage databases and the JSON documents they contain in this NoSQL database service.

* Create Cosmos DB **databases** and modify their settings
* Create and modify **containers** to store collections of JSON documents
* Create, read, update, and delete the **items** (JSON documents) in your containers
* Query the documents in your database using **SQL-like syntax**

[SDK source code][source_code] | [Package (PyPI)][cosmos_pypi] | [API reference documentation][ref_cosmos_sdk] | [Product documentation][cosmos_docs] | [Samples][cosmos_samples]

> This SDK is used for the [SQL API](https://docs.microsoft.com/azure/cosmos-db/sql-query-getting-started). For all other APIs, please check the [Azure Cosmos DB documentation](https://docs.microsoft.com/azure/cosmos-db/introduction) to evaluate the best SDK for your project.

## Getting started

### Prerequisites

* Azure subscription - [Create a free account][azure_sub]
* Azure [Cosmos DB account][cosmos_account] - SQL API
* [Python 2.7 or 3.5.3+][python]

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

```Python
from azure.cosmos import CosmosClient

import os
url = os.environ['ACCOUNT_URI']
key = os.environ['ACCOUNT_KEY']
client = CosmosClient(url, credential=key)
```

## Key concepts

Once you've initialized a [CosmosClient][ref_cosmosclient], you can interact with the primary resource types in Cosmos DB:

* [Database][ref_database]: A Cosmos DB account can contain multiple databases. When you create a database, you specify the API you'd like to use when interacting with its documents: SQL, MongoDB, Gremlin, Cassandra, or Azure Table. Use the [DatabaseProxy][ref_database] object to manage its containers.

* [Container][ref_container]: A container is a collection of JSON documents. You create (insert), read, update, and delete items in a container by using methods on the [ContainerProxy][ref_container] object.

* Item: An Item is the dictionary-like representation of a JSON document stored in a container. Each Item you add to a container must include an `id` key with a value that uniquely identifies the item within the container.

For more information about these resources, see [Working with Azure Cosmos databases, containers and items][cosmos_resources].

## Limitations

As of August 2020 the features below are **not supported**.

* Group By queries (in roadmap for 2021)
* Language Native async i/o (in roadmap for 2021)
* Queries with COUNT from a DISTINCT subquery: SELECT COUNT (1) FROM (SELECT DISTINCT C.ID FROM C)
* Bulk/Transactional batch processing
* Direct TCP Mode access
* Continuation token for cross partitions queries
* Change Feed: Processor
* Change Feed: Read multiple partitions key values
* Change Feed: Read specific time 
* Change Feed: Read from the beggining
* Change Feed: Pull model
* Get CollectionSizeUsage, DatabaseUsage, and DocumentUsage metrics
* Create User
* Create Geospatial Index
* Provision Autoscale DBs or containers
* Cross-partition ORDER BY for mixed types
* Update analytical store ttl (time to live)
* Get the connection string
* Get the minimum RU/s of a container. For more information, click [here](https://docs.microsoft.com/azure/cosmos-db/concepts-limits#minimum-throughput-limits) or use [Azure CLI](https://docs.microsoft.com/azure/cosmos-db/scripts/cli/sql/throughput#sample-script) examples for Cosmos DB.

## Bulk processing limitation workaround

If you want to use Python SDK to perform bulk inserts to Cosmos DB, the best alternative is to use [stored procedures](https://docs.microsoft.com/azure/cosmos-db/how-to-write-stored-procedures-triggers-udfs) to write multiple items with the same partition key.

## Boolean Data Type

While the Python language [uses](https://docs.python.org/3/library/stdtypes.html?highlight=boolean#truth-value-testing) "True" and "False" for boolean types, Cosmos DB [accepts](https://docs.microsoft.com/azure/cosmos-db/sql-query-is-bool) "true" and "false" only. In other words, the Python language uses Boolean values with the first uppercase letter and all other lowercase letters, while Cosmos DB and its SQL language use only lowercase letters for those same Boolean values. How to deal with this challenge?

* Your JSON documents created with Python must use "True" and "False", to pass the language validation. The SDK will convert it to "true" and "false" for you. Meaning that "true" and "false" is what will be stored in Cosmos DB. 
* If you retrieve those documents with the Cosmos DB Portal's Data Explorer, you will see "true" and "false". 
* If you retrieve those documents with this Python SDK, "true" and "false" values will be automatically converted to "True" and "False".

## SQL Queries x FROM Clause Subitems

This SDK uses the [query_items](https://docs.microsoft.com/python/api/azure-cosmos/azure.cosmos.containerproxy?preserve-view=true&view=azure-python#query-items-query--parameters-none--partition-key-none--enable-cross-partition-query-none--max-item-count-none--enable-scan-in-query-none--populate-query-metrics-none----kwargs-) method to submit SQL queries to Azure Cosmos DB. 

Cosmos DB SQL language allows you to [get subitems by using the FROM clause](https://docs.microsoft.com/azure/cosmos-db/sql-query-from#get-subitems-by-using-the-from-clause), to reduce the source to a smaller subset. As an example, you can use `select * from Families.children` instead of `select * from Families`. But please note that:

* For SQL queries using the `query_items` method, this SDK demands that you specify the `partition_key` or use the `enable_cross_partition_query` flag. 
* If you are getting subitems and specifying the `partition_key`, please make sure that your partition key is included in the subitems, which is not true for most of the cases.

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

### Create a database

After authenticating your [CosmosClient][ref_cosmosclient], you can work with any resource in the account. The code snippet below creates a SQL API database, which is the default when no API is specified when [create_database][ref_cosmosclient_create_database] is invoked.

```Python
from azure.cosmos import CosmosClient, exceptions
import os

url = os.environ['ACCOUNT_URI']
key = os.environ['ACCOUNT_KEY']
client = CosmosClient(url, credential=key)
database_name = 'testDatabase'
try:
    database = client.create_database(database_name)
except exceptions.CosmosResourceExistsError:
    database = client.get_database_client(database_name)
```

### Create a container

This example creates a container with default settings. If a container with the same name already exists in the database (generating a `409 Conflict` error), the existing container is obtained instead.

```Python
from azure.cosmos import CosmosClient, PartitionKey, exceptions
import os

url = os.environ['ACCOUNT_URI']
key = os.environ['ACCOUNT_KEY']
client = CosmosClient(url, credential=key)
database_name = 'testDatabase'
database = client.get_database_client(database_name)
container_name = 'products'

try:
    container = database.create_container(id=container_name, partition_key=PartitionKey(path="/productName"))
except exceptions.CosmosResourceExistsError:
    container = database.get_container_client(container_name)
except exceptions.CosmosHttpResponseError:
    raise
```

### Create an analytical store enabled container

This example creates a container with [Analytical Store](https://docs.microsoft.com/azure/cosmos-db/analytical-store-introduction) enabled, for reporting, BI, AI, and Advanced Analytics with [Azure Synapse Link](https://docs.microsoft.com/azure/cosmos-db/synapse-link).

The options for analytical_storage_ttl are:

+ 0 or Null or not informed: Not enabled.
+ -1: The data will be stored infinitely.
+ Any other number: the actual ttl, in seconds.


```Python
container_name = 'products'
try:
    container = database.create_container(id=container_name, partition_key=PartitionKey(path="/productName"),analytical_storage_ttl=-1)
except exceptions.CosmosResourceExistsError:
    container = database.get_container_client(container_name)
except exceptions.CosmosHttpResponseError:
    raise
```

The preceding snippet also handles the [CosmosHttpResponseError][ref_httpfailure] exception if the container creation failed. For more information on error handling and troubleshooting, see the [Troubleshooting](#troubleshooting "Troubleshooting") section.

The preceding snippet also handles the [CosmosHttpResponseError][ref_httpfailure] exception if the container creation failed. For more information on error handling and troubleshooting, see the [Troubleshooting](#troubleshooting "Troubleshooting") section.

### Get an existing container

Retrieve an existing container from the database:

```Python
from azure.cosmos import CosmosClient
import os

url = os.environ['ACCOUNT_URI']
key = os.environ['ACCOUNT_KEY']
client = CosmosClient(url, credential=key)
database_name = 'testDatabase'
database = client.get_database_client(database_name)
container_name = 'products'
container = database.get_container_client(container_name)
```

### Insert data

To insert items into a container, pass a dictionary containing your data to [ContainerProxy.upsert_item][ref_container_upsert_item]. Each item you add to a container must include an `id` key with a value that uniquely identifies the item within the container.

This example inserts several items into the container, each with a unique `id`:

```Python
from azure.cosmos import CosmosClient
import os

url = os.environ['ACCOUNT_URI']
key = os.environ['ACCOUNT_KEY']
client = CosmosClient(url, credential=key)
database_name = 'testDatabase'
database = client.get_database_client(database_name)
container_name = 'products'
container = database.get_container_client(container_name)

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

```Python
from azure.cosmos import CosmosClient
import os

url = os.environ['ACCOUNT_URI']
key = os.environ['ACCOUNT_KEY']
client = CosmosClient(url, credential=key)
database_name = 'testDatabase'
database = client.get_database_client(database_name)
container_name = 'products'
container = database.get_container_client(container_name)

for item in container.query_items(
        query='SELECT * FROM products p WHERE p.productModel = "Model 2"',
        enable_cross_partition_query=True):
    container.delete_item(item, partition_key='Widget')
```

> NOTE: If you are using partitioned collection, the value of the `partitionKey` in the example code above, should be set to the value of the partition key for this particular item, not the name of the partition key column in your collection. This holds true for both point reads and deletes.

### Query the database

A Cosmos DB SQL API database supports querying the items in a container with [ContainerProxy.query_items][ref_container_query_items] using SQL-like syntax.

This example queries a container for items with a specific `id`:

```Python
from azure.cosmos import CosmosClient
import os

url = os.environ['ACCOUNT_URI']
key = os.environ['ACCOUNT_KEY']
client = CosmosClient(url, credential=key)
database_name = 'testDatabase'
database = client.get_database_client(database_name)
container_name = 'products'
container = database.get_container_client(container_name)

# Enumerate the returned items
import json
for item in container.query_items(
        query='SELECT * FROM mycontainer r WHERE r.id="item3"',
        enable_cross_partition_query=True):
    print(json.dumps(item, indent=True))
```

> NOTE: Although you can specify any value for the container name in the `FROM` clause, we recommend you use the container name for consistency.

Perform parameterized queries by passing a dictionary containing the parameters and their values to [ContainerProxy.query_items][ref_container_query_items]:

```Python
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

```Python
from azure.cosmos import CosmosClient
import os
import json

url = os.environ['ACCOUNT_URI']
key = os.environ['ACCOUNT_KEY']
client = CosmosClient(url, credential=key)
database_name = 'testDatabase'
database = client.get_database_client(database_name)
properties = database.read()
print(json.dumps(properties))
```

### Get database and container throughputs

Get and display the throughput values of a database and of a container with dedicated throughput:

```Python
from azure.cosmos import CosmosClient
import os
import json

url = os.environ['ACCOUNT_URI']
key = os.environ['ACCOUNT_KEY']
client = CosmosClient(url, credential=key)

# Database
database_name = 'testDatabase'
database = client.get_database_client(database_name)
db_offer = database.read_offer()
print('Found Offer \'{0}\' for Database \'{1}\' and its throughput is \'{2}\''.format(db_offer.properties['id'], database.id, db_offer.properties['content']['offerThroughput']))

# Container with dedicated throughput only. Will return error "offer not found" for containers without dedicated throughput
container_name = 'testContainer'
container = database.get_container_client(container_name)
container_offer = database.read_offer()
print('Found Offer \'{0}\' for Container \'{1}\' and its throughput is \'{2}\''.format(container_offer.properties['id'], container.id, container_offer.properties['content']['offerThroughput'])) 
```


### Modify container properties

Certain properties of an existing container can be modified. This example sets the default time to live (TTL) for items in the container to 10 seconds:

```Python
from azure.cosmos import CosmosClient, PartitionKey
import os
import json

url = os.environ['ACCOUNT_URI']
key = os.environ['ACCOUNT_KEY']
client = CosmosClient(url, credential=key)
database_name = 'testDatabase'
database = client.get_database_client(database_name)
container_name = 'products'
container = database.get_container_client(container_name)

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


## Troubleshooting

### General

When you interact with Cosmos DB using the Python SDK, exceptions returned by the service correspond to the same HTTP status codes returned for REST API requests:

[HTTP Status Codes for Azure Cosmos DB][cosmos_http_status_codes]

For example, if you try to create a container using an ID (name) that's already in use in your Cosmos DB database, a `409` error is returned, indicating the conflict. In the following snippet, the error is handled gracefully by catching the exception and displaying additional information about the error.

```Python
try:
    database.create_container(id=container_name, partition_key=PartitionKey(path="/productName"))
except exceptions.CosmosResourceExistsError:
    print("""Error creating container
HTTP status code 409: The ID (name) provided for the container is already in use.
The container name must be unique within the database.""")

```
### Logging

This library uses the standard
[logging](https://docs.python.org/3.5/library/logging.html) library for logging.
Basic information about HTTP sessions (URLs, headers, etc.) is logged at INFO
level.

Detailed DEBUG level logging, including request/response bodies and unredacted
headers, can be enabled on a client with the `logging_enable` argument:
```python
import sys
import logging
from azure.cosmos import CosmosClient

# Create a logger for the 'azure' SDK
logger = logging.getLogger('azure')
logger.setLevel(logging.DEBUG)

# Configure a console output
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

# This client will log detailed information about its HTTP sessions, at DEBUG level
client = CosmosClient(url, credential=key, logging_enable=True)
```

Similarly, `logging_enable` can enable detailed logging for a single operation,
even when it isn't enabled for the client:
```py
database = client.create_database(database_name, logging_enable=True)
```

## Next steps

For more extensive documentation on the Cosmos DB service, see the [Azure Cosmos DB documentation][cosmos_docs] on docs.microsoft.com.

<!-- LINKS -->
[azure_cli]: https://docs.microsoft.com/cli/azure
[azure_portal]: https://portal.azure.com
[azure_sub]: https://azure.microsoft.com/free/
[cloud_shell]: https://docs.microsoft.com/azure/cloud-shell/overview
[cosmos_account_create]: https://docs.microsoft.com/azure/cosmos-db/how-to-manage-database-account
[cosmos_account]: https://docs.microsoft.com/azure/cosmos-db/account-overview
[cosmos_container]: https://docs.microsoft.com/azure/cosmos-db/databases-containers-items#azure-cosmos-containers
[cosmos_database]: https://docs.microsoft.com/azure/cosmos-db/databases-containers-items#azure-cosmos-databases
[cosmos_docs]: https://docs.microsoft.com/azure/cosmos-db/
[cosmos_samples]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/cosmos/azure-cosmos/samples
[cosmos_pypi]: https://pypi.org/project/azure-cosmos/
[cosmos_http_status_codes]: https://docs.microsoft.com/rest/api/cosmos-db/http-status-codes-for-cosmosdb
[cosmos_item]: https://docs.microsoft.com/azure/cosmos-db/databases-containers-items#azure-cosmos-items
[cosmos_request_units]: https://docs.microsoft.com/azure/cosmos-db/request-units
[cosmos_resources]: https://docs.microsoft.com/azure/cosmos-db/databases-containers-items
[cosmos_sql_queries]: https://docs.microsoft.com/azure/cosmos-db/how-to-sql-query
[cosmos_ttl]: https://docs.microsoft.com/azure/cosmos-db/time-to-live
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
[sample_database_mgmt]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/cosmos/azure-cosmos/samples/database_management.py
[sample_document_mgmt]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/cosmos/azure-cosmos/samples/document_management.py
[sample_examples_misc]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/cosmos/azure-cosmos/samples/examples.py
[source_code]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/cosmos/azure-cosmos
[venv]: https://docs.python.org/3/library/venv.html
[virtualenv]: https://virtualenv.pypa.io

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
