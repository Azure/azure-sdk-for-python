# Azure Cosmos DB SQL API client SDKs for Python

Azure Cosmos DB is a globally distributed, multi-model database service that supports document, key-value, wide-column, and graph databases. For more information, go to [https://www.gotcosmos.com/](https://www.gotcosmos.com/) .

Use the Azure Cosmos DB SQL API SDKs for application development and database management. For all other APIs, please check the [documentation](https://docs.microsoft.com/azure/cosmos-db/introduction) to evaluate the best SDK for your project.

## Contents of this folder

### [azure-cosmos](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cosmos/azure-cosmos)

This is the Azure Cosmos DB SQL API SDK for Python to manage databases and the JSON documents they contain in this NoSQL database service. High level capabilities are:

+ Create Cosmos DB databases and modify their settings
+ Create and modify containers to store collections of JSON documents
+ Create, read, update, and delete the items (JSON documents) in your containers
+ Query the documents in your database using SQL-like syntax

Use this package if you are creating an application or exploring data.

### [azure-mgmt-cosmosdb](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cosmos/azure-mgmt-cosmosdb)

This is the Microsoft Azure Cosmos DB Management Client Library. High level capabilities are:

+ Create an Azure Cosmos account
+ Add or remove regions
+ Enable multi-region writes
+ Set regional failover priority
+ Enable automatic failover
+ Trigger manual failover
+ List account keys
+ List read-only account keys
+ List connection strings
+ Regenerate account key

Use this package if you are creating an account level management application.

### [azure-mgmt-documentdb](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cosmos/azure-mgmt-documentdb)

Legacy DocumentDB SDK.

Use this package if you are maintaining legacy applications that can't be upgrade for the latest features and optimizations.

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
