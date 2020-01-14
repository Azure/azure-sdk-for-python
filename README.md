# Azure SDK for Python

[![Packages](https://img.shields.io/badge/packages-latest-blue.svg)](https://azure.github.io/azure-sdk/releases/latest/python.html) [![Dependencies](https://img.shields.io/badge/dependencies-analyzed-blue.svg)](https://azuresdkartifacts.blob.core.windows.net/azure-sdk-for-python/dependencies/dependencies.html) [![Python](https://img.shields.io/pypi/pyversions/azure-core.svg?maxAge=2592000)](https://pypi.python.org/pypi/azure/) [![Build Status](https://dev.azure.com/azure-sdk/public/_apis/build/status/python/python%20-%20core%20-%20ci?branchName=master)](https://dev.azure.com/azure-sdk/public/_build/latest?definitionId=458&branchName=master)

This repository is for active development of the Azure SDK for Python. For consumers of the SDK we recommend visiting our [public developer docs](https://docs.microsoft.com/en-us/python/azure/) or our versioned [developer docs](https://azure.github.io/azure-sdk-for-python).

## Getting started

For your convenience, each service has a separate set of libraries that you can choose to use instead of one, large Azure package. To get started with a specific library, see the `README.md` (or `README.rst`) file located in the library's project folder.

You can find service libraries in the `/sdk` directory.

### Prerequisites

The client libraries are supported on Python 2.7 and 3.5.3 or later.

## Packages available

Each service might have a number of libraries available from each of the following categories:
* [Client - November 2019 Releases](#Client-November-2019-Releases)
* [Client - Previous Versions](#Client-Previous-Versions)
* [Management](#Management)

### Client: November 2019 Releases

New wave of packages that we are announcing as **GA** and several that are currently releasing in **preview**. These libraries allow you to use and consume existing resources and interact with them, for example: upload a blob. These libraries share a number of core functionalities such as: retries, logging, transport protocols, authentication protocols, etc. that can be found in the [azure-core](./sdk/core/azure-core) library. You can learn more about these libraries by reading guidelines that they follow [here](https://azure.github.io/azure-sdk/python_introduction.html).

The libraries released in the November 2019 GA release:
- [azure-keyvault-keys](./sdk/keyvault/azure-keyvault-keys)
- [azure-keyvault-secrets](./sdk/keyvault/azure-keyvault-secrets)
- [azure-identity](./sdk/identity/azure-identity)
- [azure-storage-blob](./sdk/storage/azure-storage-blob)
- [azure-storage-queue](./sdk/storage/azure-storage-queue)

The libraries released in the November 2019 preview:
- [azure-cosmos](./sdk/cosmos/azure-cosmos)
- [azure-eventhub](./sdk/eventhub/azure-eventhub)
- [azure-storage-file-share](./sdk/storage/azure-storage-file-share)

> NOTE: If you need to ensure your code is ready for production use one of the stable, non-preview libraries.

### Client: Previous Versions

Last stable versions of packages that have been provided for usage with Azure and are production-ready. These libraries provide you with similar functionalities to the Preview ones as they allow you to use and consume existing resources and interact with them, for example: upload a blob. They might not implement the [guidelines](https://azure.github.io/azure-sdk/python_introduction.html) or have the same feature set as the Novemeber releases. They do however offer wider coverage of services.

### Management

Libraries which enable you to provision specific resources. They are responsible for directly mirroring and consuming Azure service's REST endpoints. The management libraries use the `azure-mgmt-<service name>` convention for their package names.

## Need help?

* For detailed documentation visit our [Azure SDK for Python documentation](https://aka.ms/python-docs)
* File an issue via [Github Issues](../../issues)
* Check [previous questions](https://stackoverflow.com/questions/tagged/azure+python) or ask new ones on StackOverflow using `azure` and `python` tags.

### Reporting security issues and security bugs

Security issues and bugs should be reported privately, via email, to the Microsoft Security Response Center (MSRC) <secure@microsoft.com>. You should receive a response within 24 hours. If for some reason you do not, please follow up via email to ensure we received your original message. Further information, including the MSRC PGP key, can be found in the [Security TechCenter](https://www.microsoft.com/msrc/faqs-report-an-issue).

## Contributing

For details on contributing to this repository, see the [contributing guide](CONTRIBUTING.md).

This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit
https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repositories using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/)
or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

![Impressions](https://azure-sdk-impressions.azurewebsites.net/api/impressions/azure-sdk-for-python%2FREADME.png)

