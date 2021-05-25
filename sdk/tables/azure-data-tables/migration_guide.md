# Guide for migrating to `azure-data-tables` from `azure-cosmos`

This guide is intended to assist in the migration to `azure-data-tables` from `azure-cosmos`. It will focus on side-by-side comparisons for similar operations between the two packages.

We assume that you are familiar with `azure-cosmos`. If not, please refer to the README for `azure-cosmos` rather than this guide.

## Table of contents

## Migration benefits

As Azure has matured and been embraced by a more diverse group of developers, we have been focused on learning the patterns and practices to best support developer productivity and to understand the gaps that the Python client libraries have.

There were several areas of consistent feedback expressed across the Azure client library ecosystem. One of the most important is that the client libraries for different Azure services have not had a consistent approach to organization, naming, and API structure. Additionally, many developers have felt that the learning curve was difficult, and the APIs did not offer a good, approachable, and consistent onboarding story for those learning Azure or exploring a specific Azure service.

To improve the development experience across Azure services, a set of uniform [design guidelines](https://azure.github.io/azure-sdk/general_introduction.html) were created for all languages to drive a consistent experience with established API patterns for all services. A set of [Python guidelines](https://azure.github.io/azure-sdk/python_design.html) were also introduced to ensure that Python clients have a natural and idiomatic feel with respect to the Python ecosystem. The new `azure-data-tables` follows these guidelines.

### Cross Service SDK improvements

The modern `azure-data-tables` client library also provides the ability to share in some of the cross-service improvements made to the Azure development experience, such as
<!-- # Not used in this library, should we still include?
- Using the new `azure-identity` library to share a single authentication approach between clients -->
- A unified logging and diagnostics pipeline offering a common view of the activities across each of the client libraries

### Performance improvements

Use this section to advertise the performance improvements in new package when compared to the old one. Skip this section if no perf improvements are found yet.

### New features

We have a variety of new features available in the new library:
* Ability to submit a batch of operations with the `TableClient.submit_transaction` method

## Important changes

### Package names and namespaces

The package name has been changed from `azure-cosmos` to `azure-data-tables`. This package can target either CosmosDB or Azure Storage Tables accounts.

### Client hierarchy and constructors

In the interest of simplicity, there are only two clients, `TableServiceClient` for account-level interactions and `TableClient` for table-level interactions. This is in contrast to the single `CosmosClient` used for interacting with the account level operations and the proxies used for interactions with specific resources (ie. `DatabaseProxy` and `ContainerProxy`).

### Table Level Scenarios

#### Create and Delete

In `azure-cosmos`:
```python

```

In `azure-data-tables`:
```python
from azure.data.tables import TableServiceClient, TableClient

# You can create a table from the TableServiceClient or TableClient
service_client = TableServiceClient.from_connection_string(conn_str)
table_client = service_client.create_table("tableName")
service_client.delete_table("tableName")

# The create_table_if_not_exists
table_client = TableClient.from_connection_string(conn_str, table_name="tableName")
table_client.create_table_if_not_exists()
table_client.delete_table()
```

#### List and Query

In `azure-cosmos`:
```python

```

In `azure-data-tables`:
```python
from azure.data.tables import TableServiceClient

service_client = TableServiceClient.from_connection_string(conn_str)

for table in service_client.list_tables():
    print(table.name)

query_filter = "TableName eq @name1 or TableName gt @name2'
parameters = {
    "name1": "myTableName1",
    "name2": "myTableName2",
}

for table in service_client.query_tables(query_filter, parameters=parameters):
    print(table.name)
```

### Entity Level Scenarios

#### Insert and Delete

In `azure-cosmos`:
```python

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
# endpoint = "https://{}.table.core.windows.net".format(account_name)
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

In `azure-cosmos`:
```python

```

In `azure-data-tables`:
```python
from azure.data.tables import UpdateMode

my_entity["Value"] += 5
table_client.update_entity(my_entity)

my_entity["StringProperty"] = "new_string"
table_client.upsert_entity(my_entity, mode=UpdateMode.MERGE)
```

#### Queries with OData

In `azure-cosmos`:
```python

```

In `azure-data-tables`:
```python
query_filter = "PartitionKey eq 'pk001' or RowKey eq 'rk001' or Value gt '5'"

for entity in table_client.query_entities(query_filter):
    print(entity)

query_filter = "age eq @age_param and married eq @married_param"
parameters = {
    "age_param": 25,
    "married_param": True,
}

for entity in table_client.query_entities(query_filter, parameters=parameters):
    print(entity)
```

#### Batch Operations

In `azure-cosmos`:
```python

```

In `azure-data-tables`:
```python
table_client = TableClient(...)

operations = [
    ("upsert", entity1),
    ("delete", entity2),
    ("update", entity3),
    ("create", entity4),
    ("update", entity5, {"mode": "replace"}),
]
```

## Additional samples

More examples can be found at the [library home page](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/tables/azure-data-tables/samples).