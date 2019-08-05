# Azure Identity client library for Python
Azure Identity simplifies authentication across the Azure SDK.
It supports token authentication using an Azure Active Directory

This library is in preview and currently supports:
  - [Service principal authentication](https://docs.microsoft.com/en-us/azure/active-directory/develop/app-objects-and-service-principals)
  - [Managed identity authentication](https://docs.microsoft.com/en-us/azure/active-directory/managed-identities-azure-resources/overview)
  - User authentication

  [Source code](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/identity/azure-identity/azure/identity)
  | [Package (PyPI)](https://pypi.org/project/azure-identity/)
  | [API reference documentation](https://azure.github.io/azure-sdk-for-python/ref/azure.identity.html)
  | [Azure Active Directory documentation](https://docs.microsoft.com/en-us/azure/active-directory/)

# Getting started
## Prerequisites
- an [Azure subscription](https://azure.microsoft.com/free/)
- Python 2.7 or 3.5.3+
- an Azure Active Directory service principal. If you need to create one, you
can use the Azure Portal, or [Azure CLI](#creating-a-service-principal-with-the-azure-cli)

## Install the package
Install Azure Identity with pip:
```sh
pip install azure-identity
```

#### Creating a Service Principal with the Azure CLI
Use this [Azure CLI](https://docs.microsoft.com/cli/azure) snippet to create/get
client secret credentials.

 * Create a service principal:
    ```sh
    az ad sp create-for-rbac -n <your-application-name> --skip-assignment
    ```
    Example output:
    ```json
    {
        "appId": "generated-app-ID",
        "displayName": "app-name",
        "name": "http://app-name",
        "password": "random-password",
        "tenant": "tenant-ID"
    }
    ```
* Use the output to set  **AZURE_CLIENT_ID** (appId), **AZURE_CLIENT_SECRET**
(password) and **AZURE_TENANT_ID** (tenant)
[environment variables](#environment-variables).


# Key concepts
## Credentials
A credential is a class which contains or can obtain the data needed for a
service client to authenticate requests. Service clients across Azure SDK
accept credentials as constructor parameters. See
[next steps](#client-library-support) below for a list of client libraries
accepting Azure Identity credentials.

Credential classes are defined in the `azure.identity` namespace. These differ
in the types of Azure Active Directory identities they can authenticate, and in
configuration:

|credential class|identity|configuration
|-|-|-
|`DefaultAzureCredential`|service principal, managed identity or user|none for managed identity; [environment variables](#environment-variables) for service principal or user authentication
|`ManagedIdentityCredential`|managed identity|none
|`EnvironmentCredential`|service principal|[environment variables](#environment-variables)
|`ClientSecretCredential`|service principal|constructor parameters
|`CertificateCredential`|service principal|constructor parameters
|[`DeviceCodeCredential`](https://azure.github.io/azure-sdk-for-python/ref/azure.identity.html#azure.identity.credentials.DeviceCodeCredential)|user|constructor parameters
|[`InteractiveBrowserCredential`](https://azure.github.io/azure-sdk-for-python/ref/azure.identity.html#azure.identity.InteractiveBrowserCredential)|user|constructor parameters
|[`UsernamePasswordCredential`](https://azure.github.io/azure-sdk-for-python/ref/azure.identity.html#azure.identity.credentials.UsernamePasswordCredential)|user|constructor parameters

Credentials can be chained together and tried in turn until one succeeds; see
[chaining credentials](#chaining-credentials) for details.

Service principal and managed identity credentials have an async equivalent in
the `azure.identity.aio` namespace, supported on Python 3.5.3+. See the
[async credentials](#async-credentials) example for details. Async user
credentials will be part of a future release.

## DefaultAzureCredential
`DefaultAzureCredential` is appropriate for most applications intended to run
in Azure. It authenticates as a service principal or managed identity,
depending on its environment, and can be configured to work both during local
development and when deployed to the cloud.

To authenticate as a service principal, provide configuration in environment
variables as described in the next section.

Authenticating as a managed identity requires no configuration, but does
require platform support. See the
[managed identity documentation](https://docs.microsoft.com/en-us/azure/active-directory/managed-identities-azure-resources/services-support-managed-identities)
for more information.

## Environment variables

`DefaultAzureCredential` and `EnvironmentCredential` can be configured with
environment variables. Each type of authentication requires values for specific
variables:

#### Service principal with secret
>|variable name|value
>|-|-
>|`AZURE_CLIENT_ID`|service principal's app id
>|`AZURE_TENANT_ID`|id of the principal's Azure Active Directory tenant
>|`AZURE_CLIENT_SECRET`|one of the service principal's client secrets

#### Service principal with certificate
>|variable name|value
>|-|-
>|`AZURE_CLIENT_ID`|service principal's app id
>|`AZURE_TENANT_ID`|id of the principal's Azure Active Directory tenant
>|`AZURE_CLIENT_CERTIFICATE_PATH`|path to a PEM-encoded certificate file including private key (without password)

#### Username and password
>|variable name|value
>|-|-
>|`AZURE_CLIENT_ID`|id of an Azure Active Directory application
>|`AZURE_USERNAME`|a username (usually an email address)
>|`AZURE_PASSWORD`|that user's password

Configuration is attempted in the above order. For example, if both
`AZURE_CLIENT_SECRET` and `AZURE_CLIENT_CERTIFICATE_PATH` have values,
`AZURE_CLIENT_SECRET` will be used.

# Examples
## Authenticating with `DefaultAzureCredential`
This example demonstrates authenticating the `BlobServiceClient` from the
[`azure-storage-blob`][azure_storage_blob] library using
`DefaultAzureCredential`.
```py
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

# The default credential first checks environment variables for configuration as described above.
# If environment configuration is incomplete, it will try managed identity.
credential = DefaultAzureCredential()

client = BlobServiceClient(account_url=<your storage account url>, credential=credential)
```
Executing this on a development machine requires first
[configuring the environment][#environment-variables] with appropriate values
for your service principal.

## Authenticating a service principal with a client secret:
This example demonstrates authenticating the `KeyClient` from the
[`azure-keyvault-keys`][azure_keyvault_keys] library using
`ClientSecretCredential`.
```py
from azure.identity import ClientSecretCredential
from azure.keyvault.keys import KeyClient

credential = ClientSecretCredential(client_id, client_secret, tenant_id)

client = KeyClient(vault_url=<your vault url>, credential=credential)
```

## Authenticating a service principal with a certificate:
This example demonstrates authenticating the `SecretClient` from the
[`azure-keyvault-secrets`][azure_keyvault_secrets] library using
`CertificateCredential`.
```py
from azure.identity import CertificateCredential
from azure.keyvault.secrets import SecretClient

# requires a PEM-encoded certificate with private key, not protected with a password
cert_path = "/app/certs/certificate.pem"
credential = CertificateCredential(client_id, tenant_id, cert_path)

client = SecretClient(vault_url=<your vault url>, credential=credential)
```

## Chaining credentials:
The ChainedTokenCredential class links multiple credential instances to be tried
sequentially when authenticating. The following example demonstrates creating a
credential which will attempt to authenticate using managed identity, and fall
back to client secret authentication if a managed identity is unavailable in the
current environment. This example demonstrates authenticating an `EventHubClient`
from the [`azure-eventhubs`][azure_eventhubs] client library.
```py
from azure.eventhub import EventHubClient
from azure.identity import ChainedTokenCredential, ClientSecretCredential, ManagedIdentityCredential

managed_identity = ManagedIdentityCredential()
client_secret = ClientSecretCredential(client_id, client_secret, tenant_id)

# when an access token is requested, the chain will try each
# credential in order, stopping when one provides a token
credential_chain = ChainedTokenCredential(managed_identity, client_secret)

# the ChainedTokenCredential can be used anywhere a credential is required
client = EventHubClient(host, event_hub_path, credential)
```

## Async credentials:
This library includes an async API supported on Python 3.5+. To use the async
credentials in `azure.identity.aio`, you must first install an async transport,
such as [`aiohttp`](https://pypi.org/project/aiohttp/). See
[azure-core documentation](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/README.md#transport)
for more information.

This example demonstrates authenticating the asynchronous `SecretClient` from
[`azure-keyvault-secrets`][azure_keyvault_secrets] with asynchronous credentials.
```py
# all credentials have async equivalents supported on Python 3.5.3+
from azure.identity.aio import DefaultAzureCredential

default_credential = DefaultAzureCredential()

# async credentials have the same API and configuration their synchronous counterparts,
from azure.identity.aio import ClientSecretCredential

credential = ClientSecretCredential(client_id, client_secret, tenant_id)

# and are used with async Azure SDK clients in the same way
from azure.keyvault.aio import SecretClient

client = SecretClient(vault_url, credential)
```

# Troubleshooting
## General
Credentials raise `azure.core.exceptions.ClientAuthenticationError` when they fail
to authenticate. `ClientAuthenticationError` has a `message` attribute which
describes why authentication failed. When raised by `ChainedTokenCredential`,
the message collects error messages from each credential in the chain.

For more details on dealing with Azure Active Directory errors please refer to the
Azure Active Directory
[error code documentation](https://docs.microsoft.com/en-us/azure/active-directory/develop/reference-aadsts-error-codes).

# Next steps
## Client library support
Currently the following client libraries support authenticating with Azure
Identity credentials. You can learn more about them, and find additional
documentation on using these client libraries along with samples, at the links
below.
- [azure-eventhubs][azure_eventhubs]
- [azure-keyvault-keys][azure_keyvault_keys]
- [azure-keyvault-secrets][azure_keyvault_secrets]
- [azure-storage-blob][azure_storage_blob]
- [azure-storage-queue](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-queue)

## Provide Feedback
If you encounter bugs or have suggestions, please
[open an issue](https://github.com/Azure/azure-sdk-for-python/issues).

# Contributing
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

[azure_eventhubs]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventhub/azure-eventhubs
[azure_keyvault_keys]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-keys
[azure_keyvault_secrets]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-secrets
[azure_storage_blob]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-blob

![Impressions](https://azure-sdk-impressions.azurewebsites.net/api/impressions/azure-sdk-for-python%2Fsdk%2Fidentity%2Fazure-identity%2FREADME.png)
