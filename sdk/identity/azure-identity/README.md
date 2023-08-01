# Azure Identity client library for Python

The Azure Identity library provides [Azure Active Directory (Azure AD)](https://learn.microsoft.com/azure/active-directory/fundamentals/active-directory-whatis) token authentication support across the Azure SDK. It provides a set of [`TokenCredential`](https://learn.microsoft.com/python/api/azure-core/azure.core.credentials.tokencredential?view=azure-python) implementations, which can be used to construct Azure SDK clients that support Azure AD token authentication.

[Source code](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity)
| [Package (PyPI)](https://pypi.org/project/azure-identity/)
| [Package (Conda)](https://anaconda.org/microsoft/azure-identity/)
| [API reference documentation][ref_docs]
| [Azure AD documentation](https://learn.microsoft.com/azure/active-directory/)

## Getting started

### Install the package

Install Azure Identity with pip:

```sh
pip install azure-identity
```

### Prerequisites

- An [Azure subscription](https://azure.microsoft.com/free/)
- Python 3.7 or a recent version of Python 3 (this library doesn't support end-of-life versions)

### Authenticate during local development

When debugging and executing code locally, it's typical for developers to use their own accounts for authenticating calls to Azure services. The Azure Identity library supports authenticating through developer tools to simplify local development.

#### Authenticate via Visual Studio Code

Developers using Visual Studio Code can use the [Azure Account extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode.azure-account) to authenticate via the editor. Apps using `DefaultAzureCredential` or `VisualStudioCodeCredential` can then use this account to authenticate calls in their app when running locally.

To authenticate in Visual Studio Code, ensure the Azure Account extension is installed. Once installed, open the **Command Palette** and run the **Azure: Sign In** command.

It's a [known issue](https://github.com/Azure/azure-sdk-for-python/issues/23249) that `VisualStudioCodeCredential` doesn't work with [Azure Account extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode.azure-account) versions newer than **0.9.11**. A long-term fix to this problem is in progress. In the meantime, consider [authenticating via the Azure CLI](#authenticate-via-the-azure-cli).

#### Authenticate via the Azure CLI

`DefaultAzureCredential` and `AzureCliCredential` can authenticate as the user signed in to the [Azure CLI][azure_cli]. To sign in to the Azure CLI, run `az login`. On a system with a default web browser, the Azure CLI will launch the browser to authenticate a user.

When no default browser is available, `az login` will use the device code authentication flow. This flow can also be selected manually by running `az login --use-device-code`.

#### Authenticate via the Azure Developer CLI

Developers coding outside of an IDE can also use the [Azure Developer CLI][azure_developer_cli] to authenticate. Applications using the `DefaultAzureCredential` or the `AzureDeveloperCliCredential` can then use this account to authenticate calls in their application when running locally.

To authenticate with the [Azure Developer CLI][azure_developer_cli], users can run the command `azd auth login`. For users running on a system with a default web browser, the Azure Developer CLI will launch the browser to authenticate the user.

For systems without a default web browser, the `azd auth login --use-device-code` command will use the device code authentication flow.

## Key concepts

### Credentials

A credential is a class that contains or can obtain the data needed for a service client to authenticate requests. Service clients across the Azure SDK accept a credential instance when they're constructed, and use that credential to authenticate requests.

The Azure Identity library focuses on OAuth authentication with Azure AD. It offers various credential classes capable of acquiring an Azure AD access token. See the [Credential classes](#credential-classes "Credential classes") section below for a list of this library's credential classes.

### DefaultAzureCredential

`DefaultAzureCredential` is appropriate for most applications that will run in Azure because it combines common production credentials with development credentials. `DefaultAzureCredential` attempts to authenticate via the following mechanisms, in this order, stopping when one succeeds:

>Note: `DefaultAzureCredential` is intended to simplify getting started with the library by handling common
>scenarios with reasonable default behaviors. Developers who want more control or whose scenario
>isn't served by the default settings should use other credential types.

![DefaultAzureCredential authentication flow](https://raw.githubusercontent.com/Azure/azure-sdk-for-python/main/sdk/identity/azure-identity/images/mermaidjs/DefaultAzureCredentialAuthFlow.svg)

1. **Environment** - `DefaultAzureCredential` will read account information specified via [environment variables](#environment-variables "environment variables") and use it to authenticate.
1. **Workload Identity** - If the application is deployed to Azure Kubernetes Service with Managed Identity enabled, `DefaultAzureCredential` will authenticate with it.
1. **Managed Identity** - If the application is deployed to an Azure host with Managed Identity enabled, `DefaultAzureCredential` will authenticate with it.
1. **Azure CLI** - If a user has signed in via the Azure CLI `az login` command, `DefaultAzureCredential` will authenticate as that user.
1. **Azure PowerShell** - If a user has signed in via Azure PowerShell's `Connect-AzAccount` command, `DefaultAzureCredential` will authenticate as that user.
1. **Azure Developer CLI** - If the developer has authenticated via the Azure Developer CLI `azd auth login` command, the `DefaultAzureCredential` will authenticate with that account.
1. **Interactive browser** - If enabled, `DefaultAzureCredential` will interactively authenticate a user via the default browser. This credential type is disabled by default.

#### Note about `VisualStudioCodeCredential`

Due to a [known issue](https://github.com/Azure/azure-sdk-for-python/issues/23249), `VisualStudioCodeCredential` has been removed from the `DefaultAzureCredential` token chain. When the issue is resolved in a future release, this change will be reverted.

## Examples

The following examples are provided below:

- [Authenticate with DefaultAzureCredential](#authenticate-with-defaultazurecredential "Authenticate with DefaultAzureCredential")
- [Define a custom authentication flow with ChainedTokenCredential](#define-a-custom-authentication-flow-with-chainedtokencredential "Define a custom authentication flow with ChainedTokenCredential")
- [Async credentials](#async-credentials "Async credentials")

### Authenticate with `DefaultAzureCredential`

More details on configuring your environment to use the `DefaultAzureCredential` can be found in the class's [reference documentation][default_cred_ref].

This example demonstrates authenticating the `BlobServiceClient` from the [azure-storage-blob][azure_storage_blob] library using `DefaultAzureCredential`.

```python
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

default_credential = DefaultAzureCredential()

client = BlobServiceClient(account_url, credential=default_credential)
```

#### Enable interactive authentication with `DefaultAzureCredential`

Interactive authentication is disabled in the `DefaultAzureCredential` by default and can be enabled with a keyword argument:

```python
DefaultAzureCredential(exclude_interactive_browser_credential=False)
```

When enabled, `DefaultAzureCredential` falls back to interactively authenticating via the system's default web browser when no other credential is available.

#### Specify a user-assigned managed identity for `DefaultAzureCredential`

Many Azure hosts allow the assignment of a user-assigned managed identity. To configure `DefaultAzureCredential` to authenticate a user-assigned identity, use the `managed_identity_client_id` keyword argument:

```python
DefaultAzureCredential(managed_identity_client_id=client_id)
```

Alternatively, set the environment variable `AZURE_CLIENT_ID` to the identity's client ID.

### Define a custom authentication flow with `ChainedTokenCredential`

`DefaultAzureCredential` is generally the quickest way to get started developing applications for Azure. For more advanced scenarios, [ChainedTokenCredential][chain_cred_ref] links multiple credential instances to be tried sequentially when authenticating. It will try each chained credential in turn until one provides a token or fails to authenticate due to an error.

The following example demonstrates creating a credential that will first attempt to authenticate using managed identity. The credential will fall back to authenticating via the Azure CLI when a managed identity is unavailable. This example uses the `EventHubProducerClient` from the [azure-eventhub][azure_eventhub] client library.

```python
from azure.eventhub import EventHubProducerClient
from azure.identity import AzureCliCredential, ChainedTokenCredential, ManagedIdentityCredential

managed_identity = ManagedIdentityCredential()
azure_cli = AzureCliCredential()
credential_chain = ChainedTokenCredential(managed_identity, azure_cli)

client = EventHubProducerClient(namespace, eventhub_name, credential_chain)
```

### Async credentials

This library includes a set of async APIs. To use the async credentials in [azure.identity.aio][ref_docs_aio], you must first install an async transport, such as [aiohttp](https://pypi.org/project/aiohttp/). For more information, see [azure-core documentation][azure_core_transport_doc].

Async credentials should be closed when they're no longer needed. Each async credential is an async context manager and defines an async `close` method. For example:

```python
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

This example demonstrates authenticating the asynchronous `SecretClient` from [azure-keyvault-secrets][azure_keyvault_secrets] with an asynchronous
credential.

```python
from azure.identity.aio import DefaultAzureCredential
from azure.keyvault.secrets.aio import SecretClient

default_credential = DefaultAzureCredential()
client = SecretClient("https://my-vault.vault.azure.net", default_credential)
```

## Managed identity support

[Managed identity authentication](https://learn.microsoft.com/azure/active-directory/managed-identities-azure-resources/overview) is supported via either the `DefaultAzureCredential` or the `ManagedIdentityCredential` directly for the following Azure services:

- [Azure App Service and Azure Functions](https://learn.microsoft.com/azure/app-service/overview-managed-identity?tabs=python)
- [Azure Arc](https://learn.microsoft.com/azure/azure-arc/servers/managed-identity-authentication)
- [Azure Cloud Shell](https://learn.microsoft.com/azure/cloud-shell/msi-authorization)
- [Azure Kubernetes Service](https://learn.microsoft.com/azure/aks/use-managed-identity)
- [Azure Service Fabric](https://learn.microsoft.com/azure/service-fabric/concepts-managed-identity)
- [Azure Virtual Machines](https://learn.microsoft.com/azure/active-directory/managed-identities-azure-resources/how-to-use-vm-token)
- [Azure Virtual Machines Scale Sets](https://learn.microsoft.com/azure/active-directory/managed-identities-azure-resources/qs-configure-powershell-windows-vmss)

### Examples

#### Authenticate with a user-assigned managed identity

```python
from azure.identity import ManagedIdentityCredential
from azure.keyvault.secrets import SecretClient

credential = ManagedIdentityCredential(client_id=managed_identity_client_id)
client = SecretClient("https://my-vault.vault.azure.net", credential)
```

#### Authenticate with a system-assigned managed identity

```python
from azure.identity import ManagedIdentityCredential
from azure.keyvault.secrets import SecretClient

credential = ManagedIdentityCredential()
client = SecretClient("https://my-vault.vault.azure.net", credential)
```

## Cloud configuration

Credentials default to authenticating to the Azure AD endpoint for Azure Public Cloud. To access resources in other clouds, such as Azure Government or a private cloud, configure credentials with the `authority` argument. [AzureAuthorityHosts](https://aka.ms/azsdk/python/identity/docs#azure.identity.AzureAuthorityHosts) defines authorities for well-known clouds:

```python
from azure.identity import AzureAuthorityHosts

DefaultAzureCredential(authority=AzureAuthorityHosts.AZURE_GOVERNMENT)
```

If the authority for your cloud isn't listed in `AzureAuthorityHosts`, you can explicitly specify its URL:

```python
DefaultAzureCredential(authority="https://login.partner.microsoftonline.cn")
```

As an alternative to specifying the `authority` argument, you can also set the `AZURE_AUTHORITY_HOST` environment variable to the URL of your cloud's authority. This approach is useful when configuring multiple credentials to authenticate to the same cloud:

```sh
AZURE_AUTHORITY_HOST=https://login.partner.microsoftonline.cn
```

Not all credentials require this configuration. Credentials that authenticate through a development tool, such as `AzureCliCredential`, use that tool's configuration. Similarly, `VisualStudioCodeCredential` accepts an `authority` argument but defaults to the authority matching VS Code's "Azure: Cloud" setting.

## Credential classes

### Authenticate Azure-hosted applications

|Credential|Usage
|-|-
|[`DefaultAzureCredential`][default_cred_ref]| Provides a simplified authentication experience to quickly start developing applications run in Azure.
|[`ChainedTokenCredential`][chain_cred_ref]| Allows users to define custom authentication flows composing multiple credentials.
|[`EnvironmentCredential`][environment_cred_ref]| Authenticates a service principal or user via credential information specified in environment variables.
|[`ManagedIdentityCredential`][managed_id_cred_ref]| Authenticates the managed identity of an Azure resource.
|[`WorkloadIdentityCredential`][workload_id_cred_ref]| Supports [Azure AD workload identity](https://learn.microsoft.com/azure/aks/workload-identity-overview) on Kubernetes.

### Authenticate service principals

|Credential|Usage|Reference
|-|-|-
|[`CertificateCredential`][cert_cred_ref]| Authenticates a service principal using a certificate. | [Service principal authentication](https://learn.microsoft.com/azure/active-directory/develop/app-objects-and-service-principals)
|[`ClientAssertionCredential`][client_assertion_cred_ref]| Authenticates a service principal using a signed client assertion. |
|[`ClientSecretCredential`][client_secret_cred_ref]| Authenticates a service principal using a secret. | [Service principal authentication](https://learn.microsoft.com/azure/active-directory/develop/app-objects-and-service-principals)

### Authenticate users

|Credential|Usage|Reference
|-|-|-
|[`AuthorizationCodeCredential`][auth_code_cred_ref]| Authenticates a user with a previously obtained authorization code. | [OAuth2 authentication code](https://learn.microsoft.com/azure/active-directory/develop/v2-oauth2-auth-code-flow)
|[`DeviceCodeCredential`][device_code_cred_ref]| Interactively authenticates a user on devices with limited UI. | [Device code authentication](https://learn.microsoft.com/azure/active-directory/develop/v2-oauth2-device-code)
|[`InteractiveBrowserCredential`][interactive_cred_ref]| Interactively authenticates a user with the default system browser. | [OAuth2 authentication code](https://learn.microsoft.com/azure/active-directory/develop/v2-oauth2-auth-code-flow)
|[`OnBehalfOfCredential`][obo_cred_ref]| Propagates the delegated user identity and permissions through the request chain. | [On-behalf-of authentication](https://learn.microsoft.com/azure/active-directory/develop/v2-oauth2-on-behalf-of-flow)
|[`UsernamePasswordCredential`][userpass_cred_ref]| Authenticates a user with a username and password (doesn't support multi-factor authentication). |  [Username + password authentication](https://learn.microsoft.com/azure/active-directory/develop/v2-oauth-ropc)

### Authenticate via development tools

|Credential|Usage|Reference
|-|-|-
|[`AzureCliCredential`][cli_cred_ref]| Authenticates in a development environment with the Azure CLI. | [Azure CLI authentication](https://learn.microsoft.com/cli/azure/authenticate-azure-cli)
|[`AzureDeveloperCliCredential`][azd_cli_cred_ref]| Authenticates in a development environment with the Azure Developer CLI. | [Azure Developer CLI Reference](https://learn.microsoft.com/azure/developer/azure-developer-cli/reference)
|[`AzurePowerShellCredential`][powershell_cred_ref]| Authenticates in a development environment with the Azure PowerShell. | [Azure PowerShell authentication](https://learn.microsoft.com/powershell/azure/authenticate-azureps)
|[`VisualStudioCodeCredential`][vscode_cred_ref]| Authenticates as the user signed in to the Visual Studio Code Azure Account extension. | [VS Code Azure Account extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode.azure-account)

## Environment variables

[DefaultAzureCredential][default_cred_ref] and [EnvironmentCredential][environment_cred_ref] can be configured with environment variables. Each type of authentication requires values for specific
variables:

### Service principal with secret

|Variable name|Value
|-|-
|`AZURE_CLIENT_ID`|ID of an Azure AD application
|`AZURE_TENANT_ID`|ID of the application's Azure AD tenant
|`AZURE_CLIENT_SECRET`|one of the application's client secrets

### Service principal with certificate

|Variable name|Value
|-|-
|`AZURE_CLIENT_ID`|ID of an Azure AD application
|`AZURE_TENANT_ID`|ID of the application's Azure AD tenant
|`AZURE_CLIENT_CERTIFICATE_PATH`|path to a PEM or PKCS12 certificate file including private key
|`AZURE_CLIENT_CERTIFICATE_PASSWORD`|password of the certificate file, if any

### Username and password

|Variable name|Value
|-|-
|`AZURE_CLIENT_ID`|ID of an Azure AD application
|`AZURE_USERNAME`|a username (usually an email address)
|`AZURE_PASSWORD`|that user's password

Configuration is attempted in the above order. For example, if values for a client secret and certificate are both present, the client secret will be used.

## Token caching

Token caching is a feature provided by the Azure Identity library that allows apps to:
- Cache tokens in memory (default) or on disk (opt-in).
- Improve resilience and performance.
- Reduce the number of requests made to Azure AD to obtain access tokens.

The Azure Identity library offers both in-memory and persistent disk caching. For more details, see the [token caching documentation](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity/TOKEN_CACHING.md).

## Troubleshooting

See the [troubleshooting guide][troubleshooting_guide] for details on how to diagnose various failure scenarios.

### Error handling

Credentials raise `CredentialUnavailableError` when they're unable to attempt authentication because they lack required data or state. For example,
[EnvironmentCredential][environment_cred_ref] will raise this exception when [its configuration](#environment-variables "its configuration") is incomplete.

Credentials raise `azure.core.exceptions.ClientAuthenticationError` when they fail to authenticate. `ClientAuthenticationError` has a `message` attribute, which describes why authentication failed. When raised by `DefaultAzureCredential` or `ChainedTokenCredential`, the message collects error messages from each credential in the chain.

For more information on handling specific Azure AD errors, see the Azure AD [error code documentation](https://learn.microsoft.com/azure/active-directory/develop/reference-aadsts-error-codes).

### Logging

This library uses the standard [logging](https://docs.python.org/3/library/logging.html) library for logging. Credentials log basic information, including HTTP sessions (URLs, headers, etc.) at INFO level. These log entries don't contain authentication secrets.

Detailed DEBUG level logging, including request/response bodies and header values, isn't enabled by default. It can be enabled with the `logging_enable` argument. For example:

```python
credential = DefaultAzureCredential(logging_enable=True)
```

> CAUTION: DEBUG level logs from credentials contain sensitive information.
> These logs must be protected to avoid compromising account security.

## Next steps

### Client library support

Client and management libraries listed on the [Azure SDK release page](https://azure.github.io/azure-sdk/releases/latest/python.html) that support Azure AD authentication accept credentials from this library. You can learn more about using these libraries in their documentation, which is linked from the release page.

### Known issues

This library doesn't support [Azure AD B2C][b2c].

For other open issues, refer to the library's [GitHub repository](https://github.com/Azure/azure-sdk-for-python/issues?q=is%3Aopen+is%3Aissue+label%3AAzure.Identity).

### Provide feedback

If you encounter bugs or have suggestions, [open an issue](https://github.com/Azure/azure-sdk-for-python/issues).

## Contributing

This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit [https://cla.microsoft.com](https://cla.microsoft.com).

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You'll only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information, see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

[auth_code_cred_ref]: https://aka.ms/azsdk/python/identity/authorizationcodecredential
[azd_cli_cred_ref]: https://aka.ms/azsdk/python/identity/azuredeveloperclicredential
[azure_cli]: https://learn.microsoft.com/cli/azure
[azure_developer_cli]:https://aka.ms/azure-dev
[azure_core_transport_doc]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#transport
[azure_eventhub]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventhub/azure-eventhub
[azure_keyvault_secrets]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/keyvault/azure-keyvault-secrets
[azure_storage_blob]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/storage/azure-storage-blob
[b2c]: https://learn.microsoft.com/azure/active-directory-b2c/overview
[cert_cred_ref]: https://aka.ms/azsdk/python/identity/certificatecredential
[chain_cred_ref]: https://aka.ms/azsdk/python/identity/chainedtokencredential
[cli_cred_ref]: https://aka.ms/azsdk/python/identity/azclicredential
[client_assertion_cred_ref]: https://aka.ms/azsdk/python/identity/clientassertioncredential
[client_secret_cred_ref]: https://aka.ms/azsdk/python/identity/clientsecretcredential
[default_cred_ref]: https://aka.ms/azsdk/python/identity/defaultazurecredential
[device_code_cred_ref]: https://aka.ms/azsdk/python/identity/devicecodecredential
[environment_cred_ref]: https://aka.ms/azsdk/python/identity/environmentcredential
[interactive_cred_ref]: https://aka.ms/azsdk/python/identity/interactivebrowsercredential
[managed_id_cred_ref]: https://aka.ms/azsdk/python/identity/managedidentitycredential
[obo_cred_ref]: https://aka.ms/azsdk/python/identity/onbehalfofcredential
[powershell_cred_ref]: https://aka.ms/azsdk/python/identity/powershellcredential
[ref_docs]: https://aka.ms/azsdk/python/identity/docs
[ref_docs_aio]: https://aka.ms/azsdk/python/identity/aio/docs
[troubleshooting_guide]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity/TROUBLESHOOTING.md
[userpass_cred_ref]: https://aka.ms/azsdk/python/identity/usernamepasswordcredential
[vscode_cred_ref]: https://aka.ms/azsdk/python/identity/vscodecredential
[workload_id_cred_ref]: https://aka.ms/azsdk/python/identity/workloadidentitycredential

![Impressions](https://azure-sdk-impressions.azurewebsites.net/api/impressions/azure-sdk-for-python%2Fsdk%2Fidentity%2Fazure-identity%2FREADME.png)
