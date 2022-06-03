# Azure Communication Identity Package client library for Python

Azure Communication Identity client package is intended to be used to setup the basics for opening a way to use Azure Communication Service offerings. This package helps to create identity user tokens to be used by other client packages such as chat, calling, sms.

[Source code](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/communication/azure-communication-identity) | [Package (Pypi)](https://pypi.org/project/azure-communication-identity/) | [API reference documentation](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/communication/azure-communication-identity) | [Product documentation](https://docs.microsoft.com/azure/communication-services/quickstarts/access-tokens?pivots=programming-language-python)

## _Disclaimer_

_Azure SDK Python packages support for Python 2.7 has ended 01 January 2022. For more information and questions, please refer to https://github.com/Azure/azure-sdk-for-python/issues/20691_

# Getting started
### Prerequisites
- Python 3.6 or later is required to use this package.
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

connection_str = "endpoint=ENDPOINT;accessKey=KEY"
endpoint = "https://<RESOURCE_NAME>.communication.azure.com"

# To use Azure Active Directory Authentication (DefaultAzureCredential) make sure to have
# AZURE_TENANT_ID, AZURE_CLIENT_ID and AZURE_CLIENT_SECRET as env variables.
identity_client_managed_identity = CommunicationIdentityClient(endpoint, DefaultAzureCredential())

#You can also authenticate using your connection string
identity_client = CommunicationIdentityClient.from_connection_string(connection_str)

```

## Examples
The following section provides several code snippets covering some of the most common Azure Communication Services tasks, including:

- [Creating a new user](#creating-a-new-user)
- [Issuing or Refreshing an access token for a user](#issuing-or-refreshing-an-access-token-for-a-user)
- [Creating a user and a token in a single request](#creating-a-user-and-a-token-in-a-single-request)
- [Revoking a user's access tokens](#revoking-a-users-access-tokens)
- [Deleting a user](#deleting-a-user)
- [Exchanging AAD access token of a Teams User for a Communication Identity access token](#exchanging-aad-access-token-of-a-teams-user-for-a-communication-identity-access-token)

### Creating a new user

Use the `create_user` method to create a new user.
```python
user = identity_client.create_user()
print("User created with id:" + user.properties['id'])
```

### Issuing or Refreshing an access token for a user

Use the `get_token` method to issue or refresh a scoped access token for the user. \
Pass in the user object as a parameter, and a list of `CommunicationTokenScope`. Scope options are:
- `CHAT` (Chat)
- `VOIP` (VoIP)

```python
tokenresponse = identity_client.get_token(user, scopes=[CommunicationTokenScope.CHAT])
print("Token issued with value: " + tokenresponse.token)
```
### Creating a user and a token in a single request
For convenience, use `create_user_and_token` to create a new user and issue a token with one function call. This translates into a single web request as opposed to creating a user first and then issuing a token.

```python
user, tokenresponse = identity_client.create_user_and_token(scopes=[CommunicationTokenScope.CHAT])
print("User id:" + user.properties['id'])
print("Token issued with value: " + tokenresponse.token)
```

### Revoking a user's access tokens

Use `revoke_tokens` to revoke all access tokens for a user. Pass in the user object as a parameter
```python
identity_client.revoke_tokens(user)
```

### Deleting a user

Use the `delete_user` method to delete a user. Pass in the user object as a parameter
```python
identity_client.delete_user(user)
```

### Exchanging AAD access token of a Teams User for a Communication Identity access token

Use the `get_token_for_teams_user` method to exchange an AAD access token of a Teams User for a new Communication Identity access token.
```python
identity_client.get_token_for_teams_user(add_token)
```

# Troubleshooting
The Azure Communication Service Identity client will raise exceptions defined in [Azure Core][azure_core].

# Next steps
## More sample code

Please take a look at the [samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/communication/azure-communication-identity/samples) directory for detailed examples of how to use this library to manage identities and tokens.

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
[azure_core]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/README.md
