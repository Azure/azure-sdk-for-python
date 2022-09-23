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

* [examples.py](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cosmos/azure-cosmos/samples/examples.py) - Examples of common tasks:
    * Create Database
    * Create Container
    * CRUD operations on Items in Container
    * Query a Container for Items
    * Create a Database user

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


* [access_cosmos_with_resource_token.py](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cosmos/azure-cosmos/samples/access_cosmos_with_resource_token.py) - Example demontrating how to get and use resource token that allows restricted access to data.


* [multi-master operations](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cosmos/azure-cosmos/samples/MultiMasterOperations) - Example demonstrating multi-master operations.

## Prerequisites
* Python 3.6+
* You must have an [Azure subscription](https://azure.microsoft.com/free/) and an
[Azure Cosmos DB account](https://docs.microsoft.com/azure/cosmos-db/create-sql-api-python#create-a-database-account) to run these samples.

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

## Next steps

Check out the [API reference documentation](https://aka.ms/azsdk-python-cosmos-ref) to learn more about
what you can do with the Azure Cosmos DB SQL API client library.