# Azure Smoke Test for Python
This sample code is a smoke test to ensure that Azure Preview for Python work while loaded into the same process by performing 2 or more actions with them.

Libraries tested:
* keyvault-secrets
* identity
* storage-blob
* event-hubs
* cosmos

## Getting started
### Setup Azure resources
For this sample, it is necessary to create/have the following resources in the [Azure Portal](https://portal.azure.com/):
* **App registration**: Register a new app or use an existing one.
  * Under _Certificates & secrets_ create a new **client secret** and store the value in a safe place.
* **Key Vaults**: Create a new Key Vault resource or use an existing one.
  * Under _Access policies_, add the app registrated in the previous step.
* **Storage acounts**: Create a container in a new or existing storage account. The container in this sample is named "mycontainer", if you want to use other name you can change the value in `BlobStorage.ts` file:
`const containerName = "mycontainer";`
* **Event Hubs**: Create an event hub inside a new or existing Event Hubs Namespace. The container in this sample is named "myeventhub", if you want to use other name you can change the value in `EventHubsTest.ts` file: `let eventHubName = "myeventhub";`
* **Azure Cosmos DB**: Create a new account or use an existing one.

### Azure credentials
The following environment variables are needed:
* From **App Registration**, in the _Overview_ section:
    * AZURE_TENANT_ID: The directory tentant ID.
    * AZURE_CLIENT_ID: The application ID.
    * AZURE_CLIENT_SECRET: The client secret stored previusly when creating the _client secret_.

* From **Key Vault**, in the _Overview_ section:
  * AZURE_PROJECT_URL: The DNS Name

* From **Event Hubs**, in _Shared access policies_ section:
  * EVENT_HUBS_CONNECTION_STRING: Connection string from a policy

* From **Storage Account**, in the _Access Keys_ section:
  * STORAGE_CONNECTION_STRING : A connection strings.

* From **Azure Cosmos DB**, in the _Keys_ section, select the _Read-Write Keys_ tab:
  * COSMOS_ENDPOINT: URI.
  * COSMOS_KEY: Primary or secondary key.

```
# Bash code to create the environment variables
export AZURE_CLIENT_ID=""
export AZURE_CLIENT_SECRET=""
export AZURE_TENANT_ID=""
export EVENT_HUBS_CONNECTION_STRING=""
export AZURE_PROJECT_URL=""
export STORAGE_CONNECTION_STRING=""
export COSMOS_ENDPOINT=""
export COSMOS_KEY=""
```

### Running the console app
[Python](https://www.python.org/downloads/) version 2.7.16 and 3.7.4 were used to run this sample.

Install the libraries required using pip:
```
pip install -r requiriments.txt
```

In the \SmokeTest\ directory, run Program.py
```
python .\Program.py
```

#### Important: To run the async tests
In order to run the samples with the asynchronous clients, **python 3.5 or greater** is needed.

Install both requirements.txt and requirements_async.txt:
```
pip install -r requiriments.txt
pip install -r requiriments_async.txt
```

If a python version below 3.5 is being used, it is still possible to run the samples. When it gets to the async tests a message `'Async not supported'` will be displayed.

## Key concepts

## Examples
All the classes in this sample has a `Run()` method as entry point, and do not depend on each other.

It is possible to run them individually:
```python
from KeyVaultSecrets import KeyVault

KeyVault().Run()
```

They can be included in other projects by moving the class in it:
```python
from KeyVaultSecrets import KeyVault

...

def  myTests():
    console.log("Smoke Test imported from other project")
    KeyVault().Run()

myTests()
otherFunction()
...
```

The classes can be used as base code and be changed to satisfied specific needs. For example, the method `EventHub().SendAndReceiveEvents()` can be change to only send events from an array given from a parameter:
```python
def SendAndReceiveEvents(self, partitionID, events):
    producer = self.client.create_producer(partition_id=partitionID)
    producer.send(events)
    producer.close()
```

**Note:** The methods in the classes are not necessary independent on each other, and the order matters. For example, in order to run `BlobStorage().DeleteBlob();`, the method `BlobStorage().UploadBLob();` must be run before, since in the other way it will fail because there is not going to be a blob to delete.

## Troubleshooting

### Authentication
Be sure to set the environment variables and credentials required before running the sample.

### ImportError
`ImportError: cannot import name 'AsyncPipelineClient' from 'azure.core'`

The libraries in the `requiriments_async.txt` are not installed and the python version used has async capabilities. Install the libraries using pip.

## Next steps
Check the [Azure SDK for Python Repository](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk) for more samples inside the sdk folder.

## Contributing
This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

If you'd like to contribute to this library, please read the contributing guide to learn more about how to build and test the code.

This project has adopted the Microsoft Open Source Code of Conduct. For more information see the Code of Conduct FAQ or contact opencode@microsoft.com with any additional questions or comments.