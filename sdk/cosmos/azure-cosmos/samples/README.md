---
page_type: sample
languages:
  - python
products:
  - azure
  - azure-cosmos-db
urlFragment: cosmos-db-samples
---

# Azure Cosmos DB SQL API client library for Python Samples

The following are code samples that show common scenario operations with the Azure Cosmos DB SQL API client library. Note that the samples use the terms 'Document' and 'Item' interchangably.

These samples target the Rust-backed SDK. Stored-procedure management and
execution, trigger management and invocation, and UDF definition management
are not exposed by either the synchronous or asynchronous client. Samples
for those operations have been retired, not left waiting for Rust parity.

`query_items` can still call an already-deployed UDF in its SQL expression.
Deploying the function is separate from querying items; this exception does
not restore `ContainerProxy.scripts` or UDF-management methods.

Authentication samples use an account key or Microsoft Entra ID (AAD).
Resource-token authentication and Cosmos user/permission management are
removed from both clients; selecting the legacy backend does not restore
them. Entra identities and role assignments are separate from Cosmos users
and resource permissions, so the AAD samples remain.

* [client_from_connection_string.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cosmos/azure-cosmos/samples/client_from_connection_string.py) and
  [client_from_connection_string_async.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cosmos/azure-cosmos/samples/client_from_connection_string_async.py) -
  Create a client from a connection string, read an existing order, and close
  the client using `with` or `async with`. These examples target the Rust-default
  SDK and do not select a backend.

* `runtime_configuration.py` - Explicitly initialize and share a custom Rust
  runtime, configure connection and HTTP-request timeouts, and apply a separate
  overall timeout. Run with `--async` for asynchronous initialization. Other
  samples normally omit `runtime` and use the default process singleton.

* [examples.py](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cosmos/azure-cosmos/samples/examples.py) - Examples of common tasks:
    * Create Database
    * Create Container
    * CRUD operations on Items in Container
    * Query a Container for Items

* [database_management.py](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cosmos/azure-cosmos/samples/database_management.py) - Example demonstrating:
    * Basic CRUD operations on a Database resource
    * Query for Database
    * List all Database resources on an account

* [container_management.py](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cosmos/azure-cosmos/samples/container_management.py) - Example demonstrating:
    * Basic CRUD operations on a Container resource
    * Query for Container
    * Manage Container Provisioned Throughput
    * List all Container resources in a Database


* [document_management.py](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cosmos/azure-cosmos/samples/document_management.py) - Example demonstrating basic CRUD operations on an Item resource.


* [index_management.py](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cosmos/azure-cosmos/samples/index_management.py) - Example demonstrating basic CRUD operations on a Item resource in a non-partitioned Container.


* [change_feed_management.py](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cosmos/azure-cosmos/samples/change_feed_management.py) - Example demontrating how to consume the Change Feed and iterate on the results.

* [feed_range_management.py](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cosmos/azure-cosmos/samples/feed_range_management.py) - Example demonstrating feed range operations including:
    * Reading feed ranges from a container
    * Getting a feed range for a specific partition key
    * Checking feed range subset relationships
    * Querying items scoped to a feed range
    * Comparing queries scoped to feed ranges with `partition_key`-based queries
    * Consuming change feed scoped to a feed range
    * Parallel change feed processing using feed ranges

* [multi-master operations](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cosmos/azure-cosmos/samples/MultiMasterOperations) - Example demonstrating multi-master operations.

* [tracing-open-telemetry](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cosmos/azure-cosmos/samples/tracing_open_telemetry.py) - Example demonstrating how to use OpenTelemetry tracing with our SDK.

* [diagnostics_filter_sample.py](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cosmos/azure-cosmos/samples/diagnostics_filter_sample.py) - Example using logging filters for diagnostics filtering

* [compact_utf8_item_writes.py](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cosmos/azure-cosmos/samples/compact_utf8_item_writes.py) - Example demonstrating the `enable_compact_utf8_item_writes` client option:
    * Sending item write bodies as compact UTF-8 instead of `\uXXXX` escape sequences
    * Comparing the resulting request body size for Unicode-heavy items
    * Async version: [compact_utf8_item_writes_async.py](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cosmos/azure-cosmos/samples/compact_utf8_item_writes_async.py)

## Prerequisites
* Python 3.8+
* You must have an [Azure subscription](https://azure.microsoft.com/free/) and an
[Azure Cosmos DB account](https://learn.microsoft.com/azure/cosmos-db/create-sql-api-python#create-a-database-account) to run these samples.

## Setup

1. Install the latest beta version of Azure Cosmos that the samples use:

```bash
pip install azure-cosmos
```

2. Clone or download this sample repository.
3. Open the sample folder in Visual Studio Code or your IDE of choice.

## Running the samples

1. Open a terminal window and `cd` to the directory that the samples are saved in.
2. Set the environment variables specified in the sample file you wish to run.
3. Follow the usage described in the file, e.g. `python database_management.py`

### Connection-string samples

Set `AZURE_COSMOS_CONNECTION_STRING` to a string containing `AccountEndpoint`
and `AccountKey`. The `sales` database and `orders` container must already
contain an item with ID `order-42` and partition key value `customer-17`.
These samples only read that item; they do not create or delete resources.

Run `python client_from_connection_string.py` or
`python client_from_connection_string_async.py`.

The connection string supplies the account and key. Pass optional client
settings, such as `consistency_level="Session"`, as keyword arguments, not
inside the connection string. A separate `credential` is not accepted.
For Microsoft Entra authentication, use `CosmosClient(endpoint, credential=...)`
instead.

## Next steps

Check out the [API reference documentation](https://aka.ms/azsdk-python-cosmos-ref) to learn more about
what you can do with the Azure Cosmos DB SQL API client library.
