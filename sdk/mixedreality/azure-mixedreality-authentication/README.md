[![Build Status](https://dev.azure.com/azure-sdk/public/_apis/build/status/azure-sdk-for-python.client?branchName=master)](https://dev.azure.com/azure-sdk/public/_build/latest?definitionId=46?branchName=master)

# Azure Mixed Reality Authentication Package client library for Python

Mixed Reality services, like Azure Spatial Anchors, Azure Remote Rendering, and others, use the Mixed Reality security
token service (STS) for authentication. This package supports exchanging Mixed Reality account credentials for an access
token from the STS that can be used to access Mixed Reality services.

![Mixed Reality service authentication diagram](https://docs.microsoft.com/azure/spatial-anchors/concepts/media/spatial-anchors-authentication-overview.png)

# Getting started

## Currently supported environments

This package has been tested with Python 2.7, 3.5, 3.6, 3.7, 3.8, and 3.9.

## Prerequisites

- An [Azure subscription][azure_sub].
- You must have an account with an [Azure Mixed Reality service](https://azure.microsoft.com/topic/mixed-reality/):
  - [Azure Remote Rendering](https://docs.microsoft.com/azure/remote-rendering/)
  - [Azure Spatial Anchors](https://docs.microsoft.com/azure/spatial-anchors/)
- Familiarity with the authentication and credential concepts from the [Azure Identity library][azure_identity].
- Python 2.7, or 3.5 or later is required to use this package.

## Install the package

Install the Azure Mixed Reality Authentication SDK.

```bash
pip install --pre azure-mixedreality-authentication
```

## Create and authenticate a `MixedRealityStsClient`

To create a client object to request an access token for a Mixed Reality service, you will need the `account identifier`
and `account domain` of your Mixed Reality service resource and a `credential`.

Mixed Reality services support a few different forms of authentication:

- Account Key authentication
  - Account keys enable you to get started quickly with using Mixed Reality services. But before you deploy your application
    to production, we recommend that you update your app to use Azure AD authentication.
- Azure Active Directory (AD) token authentication
  - If you're building an enterprise application and your company is using Azure AD as its identity system, you can use
    user-based Azure AD authentication in your app. You then grant access to your Mixed Reality accounts by using your
    existing Azure AD security groups. You can also grant access directly to users in your organization.
  - Otherwise, we recommend that you obtain Azure AD tokens from a web service that supports your app. We recommend this
    method for production applications because it allows you to avoid embedding the credentials for access to a Mixed
    Reality service in your client application.

See [here][register_aad_app] for detailed instructions and information.

### Using account key authentication

Use the [Azure Portal][azure_portal] to browse to your Mixed Reality service resource and retrieve an `account key`.

Once you have an account key, you can use the `AzureKeyCredential` class to authenticate the client as follows:

```python
from azure.core.credentials import AzureKeyCredential
from azure.mixedreality.authentication import MixedRealityStsClient

account_id = "<ACCOUNTD ID>"
account_domain = "<ACCOUNT_DOMAIN>"
account_key = "<ACCOUNT_KEY>"
key_credential = AzureKeyCredential(account_key)

client = MixedRealityStsClient(account_id, account_domain, key_credential)
```

> Note: Account key authentication is **not recommended** for production applications.

### Using an Azure Active Directory Credential

Account key authentication is used in most of the examples, but you can also authenticate with Azure Active Directory
using the [Azure Identity library][azure_identity]. This is the recommended method for production applications. To use
the [DefaultAzureCredential][defaultazurecredential] provider shown below, or other credential providers provided with
the Azure SDK, please install the `@azure/identity` package:

You will also need to [register a new AAD application][register_aad_app] and grant access to your Mixed Reality resource
by assigning the appropriate role for your Mixed Reality service to your service principal.

```python
from azure.identity import DefaultAzureCredential
from azure.mixedreality.authentication import MixedRealityStsClient

account_id = "<ACCOUNTD ID>"
account_domain = "<ACCOUNT_DOMAIN>"
default_credential = DefaultAzureCredential()

client = MixedRealityStsClient(account_id, account_domain, default_credential)
```

# Key concepts

## MixedRealityStsClient

The `MixedRealityStsClient` is the client library used to access the Mixed Reality STS to get an access token. An access
token can be retrieved by calling `get_token()` on an `MixedRealityStsClient` instance.

Tokens obtained from the Mixed Reality STS have a lifetime of **24 hours**.

### Token result value

The return value for a successful call to `get_token` is an `azure.core.credentials.AccessToken`.

See the authentication examples [above](#authenticate-the-client) or [Azure Identity][azure_identity] for more complex
authentication scenarios.

## Retrieve an access token synchronously

```python
from azure.core.credentials import AzureKeyCredential
from azure.mixedreality.authentication import MixedRealityStsClient

account_id = "<ACCOUNTD ID>"
account_domain = "<ACCOUNT_DOMAIN>"
account_key = "<ACCOUNT_KEY>"
key_credential = AzureKeyCredential(account_key)

client = MixedRealityStsClient(account_id, account_domain, key_credential)

token = client.get_token()
```

## Retrieve an access token asynchronously

```python
from azure.core.credentials import AzureKeyCredential
from azure.mixedreality.authentication.aio import MixedRealityStsClient

account_id = "<ACCOUNTD ID>"
account_domain = "<ACCOUNT_DOMAIN>"
account_key = "<ACCOUNT_KEY>"
key_credential = AzureKeyCredential(account_key)

client = MixedRealityStsClient(account_id, account_domain, key_credential)

token = await client.get_token()
```

# Examples

These are code samples that show common scenario operations with the Azure Mixed Reality Authentication client library.
The async versions of the samples (the python sample files appended with `_async`) show asynchronous operations,
and require Python 3.5 or later.
Before running the sample code, refer to Prerequisites
<!-- [Prerequisites](#Prerequisites) -->
to create a resource, then set some Environment Variables

```bash
set MIXEDREALITY_ACCOUNT_DOMAIN="<the Mixed Reality account domain>"
set MIXEDREALITY_ACCOUNT_ID="<the Mixed Reality account identifier>"
set MIXEDREALITY_ACCOUNT_KEY="<the Mixed Reality account primary or secondary key>"

pip install azure-mixedreality-authentication

python samples\client_sample.py
python samples\client_sample_async.py
```

# Troubleshooting

The [troubleshooting](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/identity/azure-identity#troubleshooting)
section for Azure Identity can be helpful when troubleshooting authentication issues.

# Next steps

## Mixed Reality client libraries

- Coming soon

## Contributing

This project welcomes contributions and suggestions. Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

If you'd like to contribute to this library, please read the
[contributing guide](https://github.com/Azure/azure-sdk-for-python/blob/master/CONTRIBUTING.md) to learn more about how to
build and test the code.

![Impressions](https://azure-sdk-impressions.azurewebsites.net/api/impressions/azure-sdk-for-python%2Fsdk%2Ftemplate%2Fazure-template%2FREADME.png)

[azure_cli]: https://docs.microsoft.com/cli/azure
[azure_sub]: https://azure.microsoft.com/free/
[azure_portal]: https://portal.azure.com
[azure_identity]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/identity/azure-identity
[register_aad_app]: https://docs.microsoft.com/azure/spatial-anchors/concepts/authentication
[defaultazurecredential]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/identity/azure-identity#defaultazurecredential
