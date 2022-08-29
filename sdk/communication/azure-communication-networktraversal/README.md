# Azure Communication Network Traversal Package client library for Python

Azure Communication Network Traversal is managing TURN credentials for Azure Communication Services.

It will provide TURN credentials to a user.

[Source code](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/communication) | [API reference documentation](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/communication)

## _Disclaimer_

_Azure SDK Python packages support for Python 2.7 has ended 01 January 2022. For more information and questions, please refer to https://github.com/Azure/azure-sdk-for-python/issues/20691_

# Getting started

### Prerequisites

- Python 3.7 or later is required to use this package.
- You must have an [Azure subscription](https://azure.microsoft.com/free/)
- A deployed Communication Services resource. You can use the [Azure Portal](https://docs.microsoft.com/azure/communication-services/quickstarts/create-communication-resource?tabs=windows&pivots=platform-azp) or the [Azure PowerShell](https://docs.microsoft.com/powershell/module/az.communication/new-azcommunicationservice) to set it up.

### Install the package

Install the Azure Communication Identity client library for Python with [pip](https://pypi.org/project/pip/):
Install the Azure Communication Relay Client library for Python with [pip](https://pypi.org/project/pip/):

```bash
pip install azure-communication-identity
pip install azure-communication-networktraversal
```

# Key concepts

## Examples

### Initializing Relay Client

The following section provides code snippets covering some of the most common Azure Communication Network Traversal tasks, including:

- [Getting the relay configuration](#getting-the-relay-configuration)

```python
# You can find your endpoint and access token from your resource in the Azure Portal
import os
from azure.communication.networktraversal import CommunicationRelayClient
from azure.identity import DefaultAzureCredential
from azure.communication.identity import CommunicationIdentityClient

connection_str = "endpoint=ENDPOINT;accessKey=KEY"
endpoint = "https://<RESOURCE_NAME>.communication.azure.com"

# To use Azure Active Directory Authentication (DefaultAzureCredential) make sure to have
# AZURE_TENANT_ID, AZURE_CLIENT_ID and AZURE_CLIENT_SECRET as env variables.
# We also need Identity client to get a User Identifier
identity_client = CommunicationIdentityClient(endpoint, DefaultAzureCredential())
relay_client = CommunicationRelayClient(endpoint, DefaultAzureCredential())
```

#You can also authenticate using your connection string

```python
identity_client = CommunicationIdentityClient.from_connection_string(self.connection_string)
relay_client = CommunicationRelayClient.from_connection_string(self.connection_string)
```

### Getting the relay configuration providing a user

```python
# We need a user from Identity
user = identity_client.create_user()
relay_configuration = relay_client.get_relay_configuration(user=user)

for iceServer in config.ice_servers:
    assert iceServer.username is not None
    print('Username: ' + iceServer.username)

    assert iceServer.credential is not None
    print('Credential: ' + iceServer.credential)
    
    assert iceServer.urls is not None
    for url in iceServer.urls:
        print('Url:' + url)
```

### Getting the relay configuration without providing a user

```python
relay_configuration = relay_client.get_relay_configuration()

for iceServer in config.ice_servers:
    assert iceServer.username is not None
    print('Username: ' + iceServer.username)

    assert iceServer.credential is not None
    print('Credential: ' + iceServer.credential)
    
    assert iceServer.urls is not None
    for url in iceServer.urls:
        print('Url:' + url)
```

### Getting the relay configuration without providing a RouteType

```python
# We need a user from Identity
user = identity_client.create_user()
relay_configuration = relay_client.get_relay_configuration(user=user, route_type=RouteType.NEAREST)

for iceServer in config.ice_servers:
    assert iceServer.username is not None
    print('Username: ' + iceServer.username)

    assert iceServer.credential is not None
    print('Credential: ' + iceServer.credential)
    
    assert iceServer.urls is not None
    for url in iceServer.urls:
        print('Url:' + url)
```

# Troubleshooting

The Azure Communication Relay client will raise exceptions defined in [Azure Core][azure_core].

# Next steps

## More sample code

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
[azure_core]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/README.md
