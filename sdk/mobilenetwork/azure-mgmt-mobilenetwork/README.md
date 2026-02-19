# Microsoft Azure SDK for Python

This is the Microsoft Azure Mobilenetwork Management Client Library.
This package has been tested with Python 3.8+.
For a more complete view of Azure libraries, see the [azure sdk python release](https://aka.ms/azsdk/python/all).

## _Disclaimer_

This package has been deprecated and will no longer be maintained after 09-30-2025. This package will only receive security fixes until 09-30-2025.

Package source code and samples have been removed from the `main` branch and can be found under the release tag for the latest version. See [azure-mgmt-mobilenetwork_3.3.1](https://github.com/Azure/azure-sdk-for-python/tree/azure-mgmt-mobilenetwork_3.3.1/sdk/mobilenetwork/azure-mgmt-mobilenetwork). The latest release can be found on [PyPI](https://pypi.org/project/azure-mypackage/).

If you have any questions, please open a [GitHub Issue](https://github.com/Azure/azure-sdk-for-python/issues) or email `azpysdkhelp@microsoft.com`.

## Getting started

### Prerequisites

- Python 3.8+ is required to use this package.
- [Azure subscription](https://azure.microsoft.com/free/)

### Install the package

```bash
pip install azure-mgmt-mobilenetwork
pip install azure-identity
```

### Authentication

By default, [Azure Active Directory](https://aka.ms/awps/aad) token authentication depends on correct configure of following environment variables.

- `AZURE_CLIENT_ID` for Azure client ID.
- `AZURE_TENANT_ID` for Azure tenant ID.
- `AZURE_CLIENT_SECRET` for Azure client secret.

In addition, Azure subscription ID can be configured via environment variable `AZURE_SUBSCRIPTION_ID`.

With above configuration, client can be authenticated by following code:

```python
from azure.identity import DefaultAzureCredential
from azure.mgmt.mobilenetwork import MobileNetworkManagementClient
import os

sub_id = os.getenv("AZURE_SUBSCRIPTION_ID")
client = MobileNetworkManagementClient(credential=DefaultAzureCredential(), subscription_id=sub_id)
```

## Examples

Code samples for this package can be found at:
- [Search Mobilenetwork Management](https://docs.microsoft.com/samples/browse/?languages=python&term=Getting%20started%20-%20Managing&terms=Getting%20started%20-%20Managing) on docs.microsoft.com
- [Azure Python Mgmt SDK Samples Repo](https://aka.ms/azsdk/python/mgmt/samples)


## Troubleshooting

## Next steps

## Provide Feedback

If you encounter any bugs or have suggestions, please file an issue in the
[Issues](https://github.com/Azure/azure-sdk-for-python/issues)
section of the project. 
