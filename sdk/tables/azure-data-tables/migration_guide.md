# Guide for migrating to `azure-data-tables` from `azure-cosmosdb-table`

This guide is intended to assist in the migration to `azure-data-tables` from `azure-cosmosdb-table`. It will focus on side-by-side comparisons for similar operations between the two packages.

We assume that you are familiar with `azure-cosmosdb-table`. If not, please refer to the README for [`azure-data-tables`](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/tables/azure-data-tables#azure-data-tables-client-library-for-python) rather than this guide.

## Table of contents

* [Migration benefits](#migration-benefits)
* [Important changes](#important-changes)
    - [Package Names](#package-names-and-namespaces)
    - [Client hierarchy and constructors](#client-hierarchy-and-constructors)
    - [Authenticating Clients](#authenticating-clients)
    - [Table Level Scenarios](#table-level-scenarios)
    - [Entity Level Scenarios](#entity-level-scenarios)
* [Additional Samples](#additional-samples)

## Migration benefits

As Azure has matured and been embraced by a more diverse group of developers, we have been focused on learning the patterns and practices to best support developer productivity and to understand the gaps that the Python client libraries have.

There were several areas of consistent feedback expressed across the Azure client library ecosystem. One of the most important is that the client libraries for different Azure services have not had a consistent approach to organization, naming, and API structure. Additionally, many developers have felt that the learning curve was difficult, and the APIs did not offer a good, approachable, and consistent onboarding story for those learning Azure or exploring a specific Azure service.

To improve the development experience across Azure services, a set of uniform [design guidelines](https://azure.github.io/azure-sdk/general_introduction.html) were created for all languages to drive a consistent experience with established API patterns for all services. A set of [Python guidelines](https://azure.github.io/azure-sdk/python_design.html) were also introduced to ensure that Python clients have a natural and idiomatic feel with respect to the Python ecosystem. The new `azure-data-tables` follows these guidelines.

### Cross Service SDK improvements

The modern `azure-data-tables` client library also provides the ability to share in some of the cross-service improvements made to the Azure development experience, such as:
* A unified logging and diagnostics pipeline offering a common view of the activities across each of the client libraries
* A unified authentication experience using `azure-core` credentials

### New features

We have a variety of new features available in the new Azure Data Tables library:
* A batch of operations can be submitted using list-based transactions.
* Separates Table and Entity level operations into two clients, `TableServiceClient` and `TableClient`
* Adds the ability to query tables and list entities explicitly.

## Important changes

### Package names and namespaces

The package name has been changed from `azure-cosmosdb-table` to `azure-data-tables`. This package can be used to access and manipulate data stored in either a CosmosDB Table account or an Azure Storage Tables account.

### Client hierarchy and constructors

In order to provide an improved conceptual experience, we have divided the single `ServiceClient` into two clients: `TableServiceClient` and `TableClient`. The `TableServiceClient` is used for account-level interactions and the `TableClient` is used for table-level interactions. The two clients simplifies the method calls by not requiring a Table name to be included on each service call.

### Authenticating Clients

In `azure-cosmosdb-table`:
```python
import os
from azure.cosmosdb.table import TableService

client = TableService(account_name=os.environ["ACCOUNT_URI"], account_key=os.environ["ACCOUNT_KEY"])
```

In `azure-data-tables`:
```python
import os
from azure.core.credentials import AzureNamedKeyCredential
from azure.data.tables import TableClient, TableServiceClient

key = os.environ["TABLES_ACCOUNT_KEY"]
name = os.environ["TABLES_ACCOUNT_NAME"]
url = os.environ["TABLES_ACCOUNT_URL"]

credential = AzureNamedKeyCredential(key=key, name=name)

table_service_client = TableServiceClient(account_url, credential=credential)

table_client = TableClient(account_url, "tablename", credential=credential)
```


### Table Level Scenarios

#### Create and Delete

In `azure-cosmosdb-table`:
```python
from azure.cosmosdb.table import TableService
client = TableService(...)
table_name = "tableName"
# create_table returns True if a new table was created, False if the table already exists
created = client.create_table(table_name)

# Delete
table_name = "deleteTableName"
# delete_table returns True if a table was deleted, False if the table does not exist
client.delete_table(table_name)
```

In `azure-data-tables` the `TableClient` or `TableServiceClient` can be used to create a new table or delete an existing table:
```python
from azure.data.tables import TableServiceClient, TableClient

# You can create a table from the TableServiceClient or TableClient
service_client = TableServiceClient.from_connection_string(conn_str)
table_client = service_client.create_table("tableName")
service_client.delete_table("tableName")

# The create_table_if_not_exists is an alternative to create_table and is
# only available on the TableServiceClient
service_client = TableServiceClient.from_connection_string(conn_str)
service_client.create_table_if_not_exists("tableName")
service_client.delete_table("tableName")
```

#### List and Query

In `azure-cosmosdb-table`:
```python
from azure.cosmosdb.table import TableService
client = TableService(...)

# In the azure-cosmosdb-table library, there is no query table method
tables = list(service.list_tables())
for table in tables:
    print(table.name)
```

In `azure-data-tables`:
```python
from azure.data.tables import TableServiceClient

service_client = TableServiceClient.from_connection_string(conn_str)

for table in service_client.list_tables():
    print(table.name)

query_filter = "TableName eq @name1 or TableName gt @name2"
parameters = {
    "name1": "myTableName1",
    "name2": "myTableName2",
}

for table in service_client.query_tables(query_filter, parameters=parameters):
    print(table.name)
```

### Entity Level Scenarios

#### Insert and Delete

In `azure-cosmosdb-table`:
```python
from azure.cosmosdb.table import TableService
client = TableService(...)
table_name = "tableName"
entity = {
    "PartitionKey": "pk0001",
    "RowKey": "rk0001",
    "StringProperty": "stringystring",
    "BooleanProperty": False,
    "IntegerProperty": 31,
    "FloatProperty": 3.14159,
    "BinaryProperty": b"binary",
    "GuidProperty": uuid.uuid4(),
    "DatetimeProperty": datetime.datetime.now(),
}

etag = client.insert_entity(table_name, entity)
```

In `azure-data-tables`:
```python
import datetime
import os
import uuid
from azure.data.tables import TableServiceClient
from azure.identity import AzureNamedKeyCredential

entity = {
    "PartitionKey": "pk0001",
    "RowKey": "rk0001",
    "StringProperty": "stringystring",
    "BooleanProperty": False,
    "IntegerProperty": 31,
    "FloatProperty": 3.14159,
    "BinaryProperty": b"binary",
    "GuidProperty": uuid.uuid4(),
    "DatetimeProperty": datetime.datetime.now(),
}

endpoint = "https://{}.table.cosmos.azure.com".format(account_name)
table_name = "myTable"
credential = AzureNamedKeyCredential(
    key=os.environ["tables_primary_cosmos_account_key"],
    name=os.environ["tables_cosmos_account_name"]
)

table_client = TableClient(endpoint, table_name, credential)
resp = table_client.create_entity(entity)

# To delete an entity, you can provide either an entire entity or a partition key and a row key
table_client.delete_entity(entity)
# OR
pk = "pk_to_delete"
rk = "rk_to_delete"
table_client.delete_entity(pk, rk)
```

#### Update and Upsert

In `azure-cosmosdb-table`:
```python
from azure.cosmosdb.table import TableService
client = TableService(...)

my_entity["Value"] += 5
my_table = "tableName"

# This operation replaces an existing entity or inserts a new one if it does not exist
etag = client.insert_or_replace_entity(my_table, my_entity)

# update an existing entity, this replaces the entity entity and can be used to remove properties.
etag = client.update_entity(my_table, my_entity)
```

In `azure-data-tables`:
```python
from azure.data.tables import UpdateMode

my_entity["Value"] += 5

# Replace an existing entity or insert a new one if it does not exist
table_client.upsert_entity(my_entity, update_mode=UpdateMode.REPLACE)

my_entity["StringProperty"] = "new_string"

# Merge an existing entity or insert a new one if it does not exist
table_client.upsert_entity(my_entity, mode=UpdateMode.MERGE)

# Update an already existing entity
table_client.update_entity(my_entity, update_mode=UpdateMode.REPLACE)
```

`UpdateMode.REPLACE` will replace an existing entity with the given one, deleting an existing properties not included in the submitted entity.
`UpdateMode.MERGE` will add new properties to an existing entity, it will not delete existing properties.

#### Queries with OData

In `azure-cosmosdb-table`:
```python
from azure.cosmosdb.table import TableService
client = TableService(...)
query_filter = "PartitionKey eq 'pk001' or RowKey eq 'rk001' or Value gt '5'"
table_name = "tableName"

for entity in list(client.query_entities(table_name, filter=query_filter)):
    print(entity.RowKey)
```

In `azure-data-tables`:
```python
query_filter = "PartitionKey eq 'pk001' or RowKey eq 'rk001' or Value gt '5'"

for entity in table_client.query_entities(query_filter):
    print(entity)

# Query parameters can be provided as a dictionary with each key matching up to
# in the query filter with an '@' symbol prefix
query_filter = "age eq @age_param and married eq @married_param"
parameters = {
    "age_param": 25,
    "married_param": True,
}

for entity in table_client.query_entities(query_filter, parameters=parameters):
    print(entity)
```

#### Batch Operations

In `azure-cosmosdb-table`:
```python
from azure.cosmosdb.table import TableService
client = TableService(...)

table_name = "tableName"
with client.batch(table_name) as batch:
    for i in range(0, 5):
        entity["RowKey"] = "context_{}".format(i)
        batch.insert_entity(entity)
```

In `azure-data-tables`:
```python
table_client = TableClient(...)

# operations is a list of tuples formatted as:
# ("operation", entity, optional keyword args for the operation)
operations = [
    ("upsert", entity1),
    ("delete", entity2),
    ("update", entity3),
    ("create", entity4),
    ("update", entity5, {"mode": "replace"}),
]

table_client.submit_transaction(operations)

```

## Additional samples

More examples can be found at the [samples for `azure-data-tables` page](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/tables/azure-data-tables/samples).
