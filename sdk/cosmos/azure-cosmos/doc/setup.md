This document currently details Python commands for building Azure Cosmos SDK.

### Fork and clone the repository
To build and develop locally, fork and clone the [Azure Cosmos DB SDK repository][cosmos_db_sdk_repo]

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

![Add package 1](https://github.com/user-attachments/assets/915883ff-f4bb-4a0b-94c0-eebeba740dc3)

3. Add Path to dependent packages from disk
   * `/<PATH_TO_CLONED_REPO>/azure-sdk-for-python/sdk/cosmos/azure-cosmos`
     * azure-core
     * azure-cosmos
   * `/<PATH_TO_CLONED_REPO>/azure-sdk-for-python/sdk/identity/azure-identity`
   * `/<PATH_TO_CLONED_REPO>/azure-sdk-for-python/tools/azure-sdk-tools`

![Add package 2](https://github.com/user-attachments/assets/8c97f03a-8c74-48b5-a194-457815f3260b)

4. Add Path to dependent packages from `PyPl`
   * pytest
   * pyrebase
   * aiohttp
![Pytest install](https://github.com/user-attachments/assets/0c39d706-2c78-4e62-9b0a-9604d088c6f9)

#### Run Cosmos DB Emulator
Azure CosmosDB Emulator is required to run unit tests.

However, the emulator is not ready on MAC OSX yet. Please follow the instructions below to run unit tests on MAC OSX 

##### On Windows
1. Download [Azure Cosmos DB emulator][cosmos_db_emulator]
2. Run emulator

##### On MAC
**<u>NOTE:</u>** Unfortunately, Azure Cosmos DB Emulator is not supported on Mac OS. Alternatively, you can manually modify some config variables in `azure-cosmos/test/test_config.py` from your personal Cosmos DB accounts to run unit tests.

**<u>WARNING:</u>** Do not commit your updated `test_config.py`. Always revert the changes before pushing your commit.

1. Open `test_config.py`
2. Replace the default values of `ACCOUNT_KEY` and `ACCOUNT_HOST` to the values from Azure Cosmos DB account(Create new Cosmos DB account if you don't have any)
![test_config](https://github.com/user-attachments/assets/39574123-43bc-48dd-bd85-31097b6625ff)

    - `ACCOUNT_KEY`: Primary key from the keys from `Settings` in Azure Cosmos DB account home
![key](https://github.com/user-attachments/assets/145971bc-c28a-4df7-9e88-196fa15254b6)

    - `ACCOUNT_HOST`: URI from the overview page of Azure Cosmos DB account
![uri](https://github.com/user-attachments/assets/034a700d-47c7-41ee-90cd-afd534729d37)

3. Update the usage of `credential` in the `setUpClass` in `test_query.py`
    - `cls.credential` -> `cls.config.masterKey`
![Screenshot 2024-09-26 at 3 07 40 PM](https://github.com/user-attachments/assets/146cb09e-2123-4784-831b-4e731376ea92)

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
The unit tests can be run by right-clicking a specific test file or specific test function in test files

- Run all tests on a test file
![Screenshot 2024-09-26 at 3 08 50 PM](https://github.com/user-attachments/assets/c47760fc-8302-4c52-8826-23c81d13b123)

- Run a single test on a test file
![Screenshot 2024-09-26 at 3 09 38 PM](https://github.com/user-attachments/assets/65d01c13-82b7-4485-9103-fd7b8bde71fb)

<!-- LINKS -->
[cosmos_db_sdk_repo]: https://github.com/Azure/azure-sdk-for-python
[azure_sub]: https://azure.microsoft.com/free/
[cosmos_account]: https://learn.microsoft.com/azure/cosmos-db/account-overview
[python]: https://www.python.org/downloads/
[pycharm]: https://www.jetbrains.com/pycharm/
[cosmos_db_emulator]: https://learn.microsoft.com/azure/cosmos-db/emulator

