# Azure Identity client library for Python

The Azure Identity library provides [Azure Active Directory (AAD)](https://docs.microsoft.com/azure/active-directory/fundamentals/active-directory-whatis) token authentication through a set of convenient TokenCredential implementations. It enables Azure SDK clients to authenticate with AAD, while also allowing other Python apps to authenticate with AAD work and school accounts, Microsoft personal accounts (MSA), and other Identity providers like [AAD B2C](https://docs.microsoft.com/azure/active-directory-b2c/overview) service.

[Source code](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity)
| [Package (PyPI)](https://pypi.org/project/azure-identity/)
| [API reference documentation][ref_docs]
| [Azure Active Directory documentation](https://docs.microsoft.com/azure/active-directory/)

## _Disclaimer_

_Azure SDK Python packages support for Python 2.7 has ended 01 January 2022. For more information and questions, please refer to https://github.com/Azure/azure-sdk-for-python/issues/20691_

## Getting started

### Install the package

Install Azure Identity with pip:

```sh
pip install azure-identity
```

### Prerequisites

- an [Azure subscription](https://azure.microsoft.com/free/)
- Python 3.6 or a recent version of Python 3 (this library doesn't support
  end-of-life versions)

### Authenticate during local development

When debugging and executing code locally it is typical for developers to use
their own accounts for authenticating calls to Azure services. The Azure
Identity library supports authenticating through developer tools to simplify
local development.

#### Authenticate via Visual Studio Code

Developers using Visual Studio Code can use the [Azure Account extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode.azure-account) to authenticate via the editor. Apps using `DefaultAzureCredential` or `VisualStudioCodeCredential` can then use this account to authenticate calls in their app when running locally.

To authenticate in Visual Studio Code, ensure **version 0.9.11 or earlier** of the Azure Account extension is installed. To track progress toward supporting newer extension versions, see [this GitHub issue](https://github.com/Azure/azure-sdk-for-net/issues/27263). Once installed, open the **Command Palette** and run the **Azure: Sign In** command.

#### Authenticate via the Azure CLI

`DefaultAzureCredential` and `AzureCliCredential` can authenticate as the user
signed in to the [Azure CLI][azure_cli]. To sign in to the Azure CLI, run
`az login`. On a system with a default web browser, the Azure CLI will launch
the browser to authenticate a user.

When no default browser is available, `az login` will use the device code
authentication flow. This can also be selected manually by running `az login --use-device-code`.

## Key concepts

### Credentials

A credential is a class which contains or can obtain the data needed for a
service client to authenticate requests. Service clients across the Azure SDK
accept a credential instance when they are constructed, and use that credential
to authenticate requests.

The Azure Identity library focuses on OAuth authentication with Azure Active
Directory (AAD). It offers a variety of credential classes capable of acquiring
an AAD access token. See the [Credential classes](#credential-classes "Credential classes") section below for a list of
this library's credential classes.

### DefaultAzureCredential

`DefaultAzureCredential` is appropriate for most applications which will run in the Azure Cloud because it combines common production credentials with development credentials. `DefaultAzureCredential` attempts to authenticate via the following mechanisms in this order, stopping when one succeeds:

![DefaultAzureCredential authentication flow](https://raw.githubusercontent.com/Azure/azure-sdk-for-python/main/sdk/identity/azure-identity/images/mermaidjs/DefaultAzureCredentialAuthFlow.svg)

1. **Environment** - `DefaultAzureCredential` will read account information specified via [environment variables](#environment-variables "environment variables") and use it to authenticate.
2. **Managed Identity** - If the application is deployed to an Azure host with Managed Identity enabled, `DefaultAzureCredential` will authenticate with it.
3. **Visual Studio Code** - If a user has signed in to the Visual Studio Code Azure Account extension, `DefaultAzureCredential` will authenticate as that user.
4. **Azure CLI** - If a user has signed in via the Azure CLI `az login` command, `DefaultAzureCredential` will authenticate as that user.
5. **Azure PowerShell** - If a user has signed in via Azure PowerShell's `Connect-AzAccount` command, `DefaultAzureCredential` will authenticate as that user.
6. **Interactive browser** - If enabled, `DefaultAzureCredential` will interactively authenticate a user via the default browser. This is disabled by default.

>`DefaultAzureCredential` is intended to simplify getting started with the SDK by handling common
>scenarios with reasonable default behaviors. Developers who want more control or whose scenario
>isn't served by the default settings should use other credential types.

### Managed Identity
`DefaultAzureCredential` and `ManagedIdentityCredential` support
[managed identity authentication](https://docs.microsoft.com/azure/active-directory/managed-identities-azure-resources/overview)
in any hosting environment which supports managed identities, such as (this list is not exhaustive):
* [Azure Virtual Machines](https://docs.microsoft.com/azure/active-directory/managed-identities-azure-resources/how-to-use-vm-token)
* [Azure App Service](https://docs.microsoft.com/azure/app-service/overview-managed-identity?tabs=dotnet)
* [Azure Kubernetes Service](https://docs.microsoft.com/azure/aks/use-managed-identity)
* [Azure Cloud Shell](https://docs.microsoft.com/azure/cloud-shell/msi-authorization)
* [Azure Arc](https://docs.microsoft.com/azure/azure-arc/servers/managed-identity-authentication)
* [Azure Service Fabric](https://docs.microsoft.com/azure/service-fabric/concepts-managed-identity)

## Examples

The following examples are provided below:

- [Authenticate with DefaultAzureCredential](#authenticate-with-defaultazurecredential "Authenticate with DefaultAzureCredential")
- [Define a custom authentication flow with ChainedTokenCredential](#define-a-custom-authentication-flow-with-chainedtokencredential "Define a custom authentication flow with ChainedTokenCredential")
- [Async credentials](#async-credentials "Async credentials")

### Authenticate with `DefaultAzureCredential`

More details on configuring your environment to use the `DefaultAzureCredential`
can be found in the class's [reference documentation][default_cred_ref].

This example demonstrates authenticating the `BlobServiceClient` from the
[azure-storage-blob][azure_storage_blob] library using
`DefaultAzureCredential`.

```py
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

default_credential = DefaultAzureCredential()

client = BlobServiceClient(account_url, credential=default_credential)
```

#### Enable interactive authentication with `DefaultAzureCredential`

Interactive authentication is disabled in the `DefaultAzureCredential` by
default and can be enabled with a keyword argument:

```py
DefaultAzureCredential(exclude_interactive_browser_credential=False)
```

When enabled, `DefaultAzureCredential` falls back to interactively
authenticating via the system's default web browser when no other credential is
available.

#### Specify a user assigned managed identity for `DefaultAzureCredential`

Many Azure hosts allow the assignment of a user assigned managed identity. To
configure `DefaultAzureCredential` to authenticate a user assigned identity,
use the `managed_identity_client_id` keyword argument:

```py
DefaultAzureCredential(managed_identity_client_id=client_id)
```

Alternatively, set the environment variable `AZURE_CLIENT_ID` to the identity's
client ID.

### Define a custom authentication flow with `ChainedTokenCredential`

`DefaultAzureCredential` is generally the quickest way to get started developing
applications for Azure. For more advanced scenarios,
[ChainedTokenCredential][chain_cred_ref] links multiple credential instances
to be tried sequentially when authenticating. It will try each chained
credential in turn until one provides a token or fails to authenticate due to
an error.

The following example demonstrates creating a credential which will attempt to
authenticate using managed identity, and fall back to authenticating via the
Azure CLI when a managed identity is unavailable. This example uses the
`EventHubProducerClient` from the [azure-eventhub][azure_eventhub] client library.

```py
from azure.eventhub import EventHubProducerClient
from azure.identity import AzureCliCredential, ChainedTokenCredential, ManagedIdentityCredential

managed_identity = ManagedIdentityCredential()
azure_cli = AzureCliCredential()
credential_chain = ChainedTokenCredential(managed_identity, azure_cli)

client = EventHubProducerClient(namespace, eventhub_name, credential_chain)
```

### Async credentials

This library includes a set of async APIs. To use the async
credentials in [azure.identity.aio][ref_docs_aio], you must first install an
async transport, such as [aiohttp](https://pypi.org/project/aiohttp/). See
[azure-core documentation][azure_core_transport_doc] for more information.

Async credentials should be closed when they're no longer needed. Each async
credential is an async context manager and defines an async `close` method. For
example:

```py
from azure.identity.aio import DefaultAzureCredential

# call close when the credential is no longer needed
credential = DefaultAzureCredential()
...
await credential.close()

# alternatively, use the credential as an async context manager
credential = DefaultAzureCredential()
async with credential:
  ...
```

This example demonstrates authenticating the asynchronous `SecretClient` from
[azure-keyvault-secrets][azure_keyvault_secrets] with an asynchronous
credential.

```py
from azure.identity.aio import DefaultAzureCredential
from azure.keyvault.secrets.aio import SecretClient

default_credential = DefaultAzureCredential()
client = SecretClient("https://my-vault.vault.azure.net", default_credential)
```

## Cloud configuration
Credentials default to authenticating to the Azure Active Directory endpoint for
Azure Public Cloud. To access resources in other clouds, such as Azure Government
or a private cloud, configure credentials with the `authority` argument.
[AzureAuthorityHosts](https://aka.ms/azsdk/python/identity/docs#azure.identity.AzureAuthorityHosts)
defines authorities for well-known clouds:
```py
from azure.identity import AzureAuthorityHosts

DefaultAzureCredential(authority=AzureAuthorityHosts.AZURE_GOVERNMENT)
```
Not all credentials require this configuration. Credentials which authenticate
through a development tool, such as `AzureCliCredential`, use that tool's
configuration. Similarly, `VisualStudioCodeCredential` accepts an `authority`
argument but defaults to the authority matching VS Code's "Azure: Cloud" setting.

## Credential classes

### Authenticate Azure hosted applications

|credential|usage
|-|-
|[DefaultAzureCredential][default_cred_ref]|simplified authentication to get started developing applications for the Azure cloud
|[ChainedTokenCredential][chain_cred_ref]|define custom authentication flows composing multiple credentials
|[EnvironmentCredential][environment_cred_ref]|authenticate a service principal or user configured by environment variables
|[ManagedIdentityCredential][managed_id_cred_ref]|authenticate the managed identity of an Azure resource

### Authenticate service principals

|credential|usage
|-|-
|[ClientSecretCredential][client_secret_cred_ref]| authenticate a service principal using a secret
|[CertificateCredential][cert_cred_ref]| authenticate a service principal using a certificate

### Authenticate users

|credential|usage
|-|-
|[InteractiveBrowserCredential][interactive_cred_ref]|interactively authenticate a user with the default web browser
|[DeviceCodeCredential][device_code_cred_ref]| interactively authenticate a user on a device with limited UI
|[UsernamePasswordCredential][userpass_cred_ref]| authenticate a user with a username and password (does not support multi-factor authentication)

### Authenticate via development tools

|credential|usage
|-|-
|[AzureCliCredential][cli_cred_ref]|authenticate as the user signed in to the Azure CLI
|[VisualStudioCodeCredential][vscode_cred_ref]|authenticate as the user signed in to the Visual Studio Code Azure Account extension

## Environment variables

[DefaultAzureCredential][default_cred_ref] and
[EnvironmentCredential][environment_cred_ref] can be configured with
environment variables. Each type of authentication requires values for specific
variables:

#### Service principal with secret
|variable name|value
|-|-
|`AZURE_CLIENT_ID`|id of an Azure Active Directory application
|`AZURE_TENANT_ID`|id of the application's Azure Active Directory tenant
|`AZURE_CLIENT_SECRET`|one of the application's client secrets

#### Service principal with certificate
|variable name|value
|-|-
|`AZURE_CLIENT_ID`|id of an Azure Active Directory application
|`AZURE_TENANT_ID`|id of the application's Azure Active Directory tenant
|`AZURE_CLIENT_CERTIFICATE_PATH`|path to a PEM or PKCS12 certificate file including private key (without password protection)

#### Username and password
|variable name|value
|-|-
|`AZURE_CLIENT_ID`|id of an Azure Active Directory application
|`AZURE_USERNAME`|a username (usually an email address)
|`AZURE_PASSWORD`|that user's password

Configuration is attempted in the above order. For example, if values for a
client secret and certificate are both present, the client secret will be used.

## Troubleshooting

See the [troubleshooting guide][troubleshooting_guide] for details on how to diagnose various failure scenarios.

### Error handling

Credentials raise `CredentialUnavailableError` when they're unable to attempt
authentication because they lack required data or state. For example,
[EnvironmentCredential][environment_cred_ref] will raise this exception when
[its configuration](#environment-variables "its configuration") is incomplete.

Credentials raise `azure.core.exceptions.ClientAuthenticationError` when they fail
to authenticate. `ClientAuthenticationError` has a `message` attribute which
describes why authentication failed. When raised by
`DefaultAzureCredential` or `ChainedTokenCredential`,
the message collects error messages from each credential in the chain.

For more details on handling specific Azure Active Directory errors please refer to the
Azure Active Directory
[error code documentation](https://docs.microsoft.com/azure/active-directory/develop/reference-aadsts-error-codes).

### Logging

This library uses the standard
[logging](https://docs.python.org/3/library/logging.html) library for logging.
Credentials log basic information, including HTTP sessions (URLs, headers, etc.) at INFO level. These log entries do not contain authentication secrets.

Detailed DEBUG level logging, including request/response bodies and header values, is not enabled by default. It can be enabled with the `logging_enable` argument, for example:

```py
credential = DefaultAzureCredential(logging_enable=True)
```

> CAUTION: DEBUG level logs from credentials contain sensitive information.
> These logs must be protected to avoid compromising account security.

## Next steps

### Client library support

Client and management libraries listed on the
[Azure SDK release page](https://azure.github.io/azure-sdk/releases/latest/python.html)
which support Azure AD authentication accept credentials from this library. You can learn more
about using these libraries in their documentation, which is linked from the release page.

### Known issues

This library doesn't support [Azure AD B2C][b2c].

For other open issues, refer to the library's [GitHub repository](https://github.com/Azure/azure-sdk-for-python/issues?q=is%3Aopen+is%3Aissue+label%3AAzure.Identity).

### Provide feedback

If you encounter bugs or have suggestions, please
[open an issue](https://github.com/Azure/azure-sdk-for-python/issues).

## Contributing

This project welcomes contributions and suggestions. Most contributions require
you to agree to a Contributor License Agreement (CLA) declaring that you have
the right to, and actually do, grant us the rights to use your contribution.
For details, visit [https://cla.microsoft.com](https://cla.microsoft.com).

When you submit a pull request, a CLA-bot will automatically determine whether
you need to provide a CLA and decorate the PR appropriately (e.g., label,
comment). Simply follow the instructions provided by the bot. You will only
need to do this once across all repos using our CLA.

This project has adopted the
[Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information, see the
[Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/)
or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any
additional questions or comments.

[azure_appconfiguration]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/appconfiguration/azure-appconfiguration
[azure_cli]: https://docs.microsoft.com/cli/azure
[azure_core_transport_doc]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#transport
[azure_eventhub]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventhub/azure-eventhub
[azure_keyvault_certificates]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk//keyvault/azure-keyvault-certificates
[azure_keyvault_keys]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/keyvault/azure-keyvault-keys
[azure_keyvault_secrets]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/keyvault/azure-keyvault-secrets
[azure_storage_blob]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/storage/azure-storage-blob
[azure_storage_queue]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/storage/azure-storage-queue
[b2c]: https://docs.microsoft.com/azure/active-directory-b2c/overview
[cert_cred_ref]: https://aka.ms/azsdk/python/identity/certificatecredential
[chain_cred_ref]: https://aka.ms/azsdk/python/identity/chainedtokencredential
[cli_cred_ref]: https://aka.ms/azsdk/python/identity/azclicredential
[client_secret_cred_ref]: https://aka.ms/azsdk/python/identity/clientsecretcredential
[default_cred_ref]: https://aka.ms/azsdk/python/identity/defaultazurecredential
[device_code_cred_ref]: https://aka.ms/azsdk/python/identity/devicecodecredential
[environment_cred_ref]: https://aka.ms/azsdk/python/identity/environmentcredential
[interactive_cred_ref]: https://aka.ms/azsdk/python/identity/interactivebrowsercredential
[managed_id_cred_ref]: https://aka.ms/azsdk/python/identity/managedidentitycredential
[ref_docs]: https://aka.ms/azsdk/python/identity/docs
[ref_docs_aio]: https://aka.ms/azsdk/python/identity/aio/docs
[troubleshooting_guide]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity/TROUBLESHOOTING.md
[userpass_cred_ref]: https://aka.ms/azsdk/python/identity/usernamepasswordcredential
[vscode_cred_ref]: https://aka.ms/azsdk/python/identity/vscodecredential

![Impressions](https://azure-sdk-impressions.azurewebsites.net/api/impressions/azure-sdk-for-python%2Fsdk%2Fidentity%2Fazure-identity%2FREADME.png)
