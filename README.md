# Azure SDK for Python

[![Python](https://img.shields.io/pypi/pyversions/azure-core.svg?maxAge=2592000)](https://pypi.python.org/pypi/azure/) [![BuildStatus](https://dev.azure.com/azure-sdk/public/_apis/build/status/46?branchName=master)](https://dev.azure.com/azure-sdk/public/_build/latest?definitionId=46&branchName=master) [![Dependencies](https://img.shields.io/badge/dependencies-analyzed-blue.svg)](https://azuresdkartifacts.blob.core.windows.net/azure-sdk-for-python/dependencies/dependencies.html)

This repository contains official Python libraries for Azure services. For documentation go to [Azure SDK for Python documentation](http://aka.ms/python-docs).

You can find a complete list of all the packages for these libraries [here](./packages.md).

## Getting started

For your convenience, each service has a separate set of libraries that you can choose to use instead of one, large Azure package. To get started with a specific library, see the `README.md` (or `README.rst`) file located in the library's project folder.

You can find service libraries in the `/sdk` directory.

### Prerequisites
The client libraries are supported on Python 2.7 and 3.5.3 or later.

## Packages available
Each service might have a number of libraries available from each of the following categories:
* [Client - July 2019 Preview](#Client-July-2019-Preview)
* [Client - Stable](#Client-Stable)
* [Management](#Management)


### Client: July 2019 Preview
New wave of packages that we are currently releasing in **Preview**. These libraries allow you to use and consume existing resources and interact with them, for example: upload a blob. These libraries share a number of core functionalities such as: retries, logging, transport protocols, authentication protocols, etc. that can be found in the [azure-core](./sdk/core/azure-core) library. You can learn more about these libraries by reading guidelines that they follow [here](https://azuresdkspecs.z5.web.core.windows.net/PythonSpec.html).

The libraries released in July preview:

- [azure-cosmos](./sdk/cosmos/azure-cosmos)
- [azure-eventhubs](./sdk/eventhub/azure-eventhubs)
- [azure-keyvault-keys](./sdk/keyvault/azure-keyvault-keys)
- [azure-keyvault-secrets](./sdk/keyvault/azure-keyvault-secrets)
- [azure-identity](./sdk/identity/azure-identity)
- [azure-storage-blob](./sdk/storage/azure-storage-blob)
- [azure-storage-file](./sdk/storage/azure-storage-file)
- [azure-storage-queue](./sdk/storage/azure-storage-queue)

>NOTE: If you need to ensure your code is ready for production use one of the stable libraries.


### Client: Stable
Last stable versions of packages that have been provided for usage with Azure and are production-ready. These libraries provide you with similar functionalities to the Preview ones as they allow you to use and consume existing resources and interact with them, for example: upload a blob.

### Management
Libraries which enable you to provision specific resources. They are responsible for directly mirroring and consuming Azure service's REST endpoints. The management libraries use the `azure-mgmt-<service name>` convention for their package names.

## Need help?
* For detailed documentation visit our [Azure SDK for Python documentation](aka.ms/python-docs)
* File an issue via [Github Issues](../../issues)
* Check [previous questions](https://stackoverflow.com/questions/tagged/azure+python) or ask new ones on StackOverflow using `azure` and `python` tags.

## Contributing
For details on contributing to this repository, see the [contributing guide](CONTRIBUTING.md).

## Code of Conduct

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

![Impressions](https://azure-sdk-impressions.azurewebsites.net/api/impressions/azure-sdk-for-python%2FREADME.png)

