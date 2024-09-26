This document currently details Python commands for building Azure Cosmos SDK.

### Fork and clone the repository
To build and develop locally, it is strongly recommended to fork and clone the repository: https://github.com/Azure/azure-sdk-for-python

### Setup SDK with Pycharm

#### Prerequisites
* [Pycharm][pycharm]
* Azure subscription - [Create a free account][azure_sub]
* Azure [Cosmos DB account][cosmos_account] - SQL API
* [Python 3.6+][python]

#### Add Interpreter
Your Python interpreter might not be the right version(**Python 3.6+**). Change the Python versions in Pycharm.
1. Add local interpreter
![Screenshot 2024-09-11 at 1 28 42 PM](https://github.com/user-attachments/assets/93b0815b-72e7-40ac-b865-c4f00c7627fa)

2. Select the right interpreter version
![Screenshot 2024-09-11 at 1 32 13 PM](https://github.com/user-attachments/assets/a4a881df-6e37-4a09-884c-dcece4daeefd)

#### Install dependent Packages
1. On the bottom left tool bar, go to `Python Packages`
2. Goto `Add Package` > `From Disk`
3. Add Path to dependent packages
   * pytest
   * pyrebase
   * aiohttp
   * `/<PATH_TO_CLONED_REPO>/azure-sdk-for-python/sdk/cosmos/azure-cosmos`
     * azure-core
     * azure-cosmos
   * `/<PATH_TO_CLONED_REPO>/azure-sdk-for-python/sdk/identity/azure-identity`
   * `/<PATH_TO_CLONED_REPO>/azure-sdk-for-python/tools/azure-sdk-tools`

#### Run Cosmos DB Emulator
Azure CosmosDB Emulator is required to run unit tests.

However, the emulator is not ready on MAC OSX yet. Please follow the instructions below to run unit tests on MAC OSX 

##### On Windows
1. Download [Azure Cosmos DB emulator][cosmos_db_emulator]
2. Run emulator

##### On MAC
**<u>NOTE:</u>** Unfortunately, emulator is not supported on Mac OS. As alternative way, you can manually modify some config variables in `azure-cosmos/test/test_config.py` from your personal Cosmos DB accounts

**<u>WARNING:</u>** Do not commit your updated `test_config.py`. Always revert those changes before pushing your commit

1. Open `test_config.py`
2. Replace the default values of `ACCOUNT_KEY` and `ACCOUNT_HOST` to the values from Azure Cosmos DB account(Create new Cosmos DB account if you don't have any)
    - `ACCOUNT_KEY`: Primary key from the keys from `Settings` in Azure Cosmos DB account home
    - `ACCOUNT_HOST`: URI from the overview page of Azure Cosmos DB account
3. Update the usage of `credential` in the `setUpClass` in `test_query.py`
    - `cls.credential` -> `cls.config.masterKey`

To run aad tests, follow the steps below to create `RoleAssignment` that uses the `RoleDefinition`
1. Save the following content into a JSON file named `expandedAction.json`
```json
{
    "RoleName": "ExpandedRBACActions",
    "Type": "CustomRole",
    "AssignableScopes": ["/"],
    "Permissions": [{
        "DataActions": [
            "Microsoft.DocumentDB/databaseAccounts/readMetadata",
            "Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers/*",
            "Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers/items/*"
        ]
    }]
}
```
2. Run the following commands:
   - Set account details
     - `<subscriptionId>`: Subscription ID to `CosmosDB-SDK-Dev`
     - `<resourceGroupName>`: Resource name of your Cosmos DB account
     - `<accountName>`: Your Cosmos DB account name
    ```shell
    subscriptionId='<subscriptionId>'
    resourceGroupName='<resourceGroupName>'
    accountName='<accountName>'
    ```

   - Set subscription
    ```shell
    az account set --subscription $subscriptionId
    ```
    
    - Create the RoleDefinition 
    ```shell
    az cosmosdb sql role definition create --account-name $accountName --resource-group $resourceGroupName --body expandedActions.json
    ```
    
    - Get the principalId associated with you Azure account. Replace with any other principalId if necessary. You can also get this value from Azure Portal, by visiting the EntraId Users page. It is called 'Object Id' there.
    ```shell
    az ad signed-in-user show --query id -o tsv
    ```
        
    - Set principalId to a variable
      - `<principalId>`: The returned id from the command above
    ```shell
    principalId=<principalId>
    ```
    
    - Create a RoleAssignment for the principalId that uses the RoleDefinition created above
    ```shell
    az cosmosdb sql role assignment create --account-name $accountName --resource-group $resourceGroupName  --role-definition-name "ExpandedRBACActions" --scope "/" --principal-id $principalId
    ```
#### Run unit tests
The unit tests can be ran by right-clicking a specific test file or specific test function in test files

<!-- LINKS -->
[azure_sub]: https://azure.microsoft.com/free/
[cosmos_account]: https://docs.microsoft.com/azure/cosmos-db/account-overview
[python]: https://www.python.org/downloads/
[pycharm]: https://www.jetbrains.com/pycharm/
[cosmos_db_emulator]: https://learn.microsoft.com/en-us/azure/cosmos-db/how-to-develop-emulator/

