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

## Live-test accounts

`tests.yml` runs two matrices through the shared Python live-test templates:

- `fixed-account-platform-matrix.json` contains key-auth jobs with an `AccountSelector`.
  These jobs omit subscription configuration, Azure resource deployment, provisioning login,
  and resource cleanup at template expansion. Tests run in plain PowerShell without a
  service-connection login or a `CI_HAS_DEPLOYED_RESOURCES` requirement.
- `live-platform-matrix.json` retains the AAD and GSI jobs. Their provisioning, AAD role
  assignments, federated test authentication, and cleanup are unchanged.

The fixed-account pre-step selects credentials from the secret
`sub-config-cosmos-azure-cloud-test-resources` in the existing Cosmos live-test variable
group. It exports `ACCOUNT_HOST`, `ACCOUNT_KEY`, and optional `SECONDARY_ACCOUNT_KEY`
directly, registering each with the Azure Pipelines log scrubber before setting the
environment-visible variable. The aggregate JSON is mapped only into the resolver task.
A missing selector or invalid configuration fails the job rather than falling back to
provisioning. There is no post-deployment credential rebinding.

When adding a key-auth job, put it in the fixed-account matrix and specify its selector.
Set client-side options such as `AZURE_COSMOS_ENABLE_CIRCUIT_BREAKER` in that matrix;
fixed jobs do not receive Bicep outputs. Retained `ArmConfig` labels preserve existing
job names and filters but do not cause deployment.

Offline regression checks (no Azure login or live provisioning):

```sh
pwsh -NoProfile -File sdk/cosmos/pipeline/resolve-cosmos-test-account.tests.ps1
python3 -m unittest discover -s sdk/cosmos/pipeline -p 'test_*.py'
```

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
