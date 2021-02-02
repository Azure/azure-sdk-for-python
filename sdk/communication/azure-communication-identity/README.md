[![Build Status](https://dev.azure.com/azure-sdk/public/_apis/build/status/azure-sdk-for-python.client?branchName=master)](https://dev.azure.com/azure-sdk/public/_build/latest?definitionId=46?branchName=master)

# Azure Communication Identity Package client library for Python

Azure Communication Identity client package is intended to be used to setup the basics for opening a way to use Azure Communication Service offerings. This package helps to create identities user tokens to be used by other client packages such as chat, calling, sms. 

# Getting started
### Prerequisites
- Python 2.7, or 3.5 or later is required to use this package.
- You must have an [Azure subscription](https://azure.microsoft.com/free/)
- A deployed Communication Services resource. You can use the [Azure Portal](https://docs.microsoft.com/azure/communication-services/quickstarts/create-communication-resource?tabs=windows&pivots=platform-azp) or the [Azure PowerShell](https://docs.microsoft.com/powershell/module/az.communication/new-azcommunicationservice) to set it up.
### Install the package
Install the Azure Communication Identity client library for Python with [pip](https://pypi.org/project/pip/):

```bash
pip install azure-communication-identity
```

# Key concepts
## CommunicationIdentityClient
`CommunicationIdentityClient` provides operations for:

- Create/delete identities to be used in Azure Communication Services. Those identities can be used to make use of Azure Communication offerings and can be scoped to have limited abilities through token scopes.

- Create/revoke scoped user access tokens to access services such as chat, calling, sms. Tokens are issued for a valid Azure Communication identity and can be revoked at any time.

### Initializing Identity Client
```python
# You can find your endpoint and access token from your resource in the Azure Portal
import os
from azure.communication.identity import CommunicationIdentityClient
from azure.identity import DefaultAzureCredential

connection_str = os.getenv('AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING')
endpoint = os.getenv('AZURE_COMMUNICATION_SERVICE_ENDPOINT')

# To use Azure Active Directory Authentication (DefaultAzureCredential) make sure to have
# AZURE_TENANT_ID, AZURE_CLIENT_ID and AZURE_CLIENT_SECRET as env variables.
identity_client_managed_identity = CommunicationIdentityClient.(endpoint, DefaultAzureCredential())

#You can also authenticate using your connection string
identity_client = CommunicationIdentityClient.from_connection_string(connection_str)

```

# Examples
The following section provides several code snippets covering some of the most common Azure Communication Services tasks, including:

[Create/delete Azure Communication Service identities][identitysamples] 

[Create/revoke scoped user access tokens][identitysamples]

# Troubleshooting
The Azure Communication Service Identity client will raise exceptions defined in [Azure Core][azure_core].

# Next steps
## More sample code

Please take a look at the [samples](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/communication/azure-communication-identity/samples) directory for detailed examples of how to use this library to manage identities and tokens.

## Provide Feedback

If you encounter any bugs or have suggestions, please file an issue in the [Issues](https://github.com/Azure/azure-sdk-for-python/issues) section of the project

# Contributing
This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the
PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

<!-- LINKS -->
[identitysamples]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/communication/azure-communication-identity/samples/identity_samples.py
[azure_core]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/README.md
