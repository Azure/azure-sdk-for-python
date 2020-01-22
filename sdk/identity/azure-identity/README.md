# Azure Identity client library for Python
Azure Identity authenticating with Azure Active Directory for Azure SDK
libraries. It provides credentials Azure SDK clients can use to authenticate
their requests.

This library currently supports:
  - [Service principal authentication](https://docs.microsoft.com/en-us/azure/active-directory/develop/app-objects-and-service-principals)
  - [Managed identity authentication](https://docs.microsoft.com/en-us/azure/active-directory/managed-identities-azure-resources/overview)
  - User authentication

  [Source code](./)
  | [Package (PyPI)](https://pypi.org/project/azure-identity/)
  | [API reference documentation][ref_docs]
  | [Azure Active Directory documentation](https://docs.microsoft.com/en-us/azure/active-directory/)

# Getting started
## Prerequisites
- an [Azure subscription](https://azure.microsoft.com/free/)
- Python 2.7 or 3.5.3+

## Install the package
Install Azure Identity with pip:
```sh
pip install azure-identity
```

#### Creating a Service Principal with the Azure CLI
This library doesn't require a service principal, but Azure applications
commonly use them for authentication. If you need to create one, you can use
this [Azure CLI](https://docs.microsoft.com/cli/azure) snippet. Before using
it, replace "http://my-application" with a more appropriate name for your
service principal.

Create a service principal:
```sh
az ad sp create-for-rbac --name http://my-application --skip-assignment
```

Example output:
```json
{
    "appId": "generated-app-id",
    "displayName": "app-name",
    "name": "http://my-application",
    "password": "random-password",
    "tenant": "tenant-id"
}
```
Azure Identity can authenticate as this service principal using its tenant id
("tenant" above), client id ("appId" above), and client secret ("password" above).


# Key concepts
## Credentials
A credential is a class which contains or can obtain the data needed for a
service client to authenticate requests. Service clients across the Azure SDK
accept credentials as constructor parameters, as described in their
documentation. The [next steps](#client-library-support) section below contains
a partial list of client libraries accepting Azure Identity credentials.

Credential classes are found in the `azure.identity` namespace. They differ
in the types of identities they can authenticate as, and in their configuration:

|credential class|identity|configuration
|-|-|-
|[DefaultAzureCredential](#defaultazurecredential "DefaultAzureCredential")|service principal, managed identity, user|none for managed identity, [environment variables](#environment-variables "environment variables") for service principal or user authentication
|[ManagedIdentityCredential][managed_id_cred_ref]|managed identity|none
|[EnvironmentCredential][environment_cred_ref]|service principal, user|[environment variables](#environment-variables "environment variables")
|[ClientSecretCredential][client_secret_cred_ref]|service principal|constructor parameters
|[CertificateCredential][cert_cred_ref]|service principal|constructor parameters
|[DeviceCodeCredential][device_code_cred_ref]|user|constructor parameters
|[InteractiveBrowserCredential][interactive_cred_ref]|user|constructor parameters
|[UsernamePasswordCredential][userpass_cred_ref]|user|constructor parameters

Credentials can be chained together and tried in turn until one succeeds; see
[chaining credentials](#chaining-credentials "chaining credentials") for details.

Service principal and managed identity credentials have async equivalents in
the [azure.identity.aio][ref_docs_aio] namespace, supported on Python 3.5.3+.
See the [async credentials](#async-credentials "async credentials") example for
details. Async user credentials will be part of a future release.

## DefaultAzureCredential
[DefaultAzureCredential][default_cred_ref] is appropriate for most
applications intended to run in Azure. It can authenticate as a service
principal, managed identity, or user, and can be configured for local
development and production environments without code changes.

To authenticate as a service principal, provide configuration in
[environment variables](#environment-variables "environment variables") as
described in the next section.

Authenticating as a managed identity requires no configuration but is only
possible in a supported hosting environment. See Azure Active Directory's
[managed identity documentation](https://docs.microsoft.com/en-us/azure/active-directory/managed-identities-azure-resources/services-support-managed-identities)
for more information.

#### Single sign-on
During local development on Windows, [DefaultAzureCredential][default_cred_ref]
can authenticate using a single sign-on shared with Microsoft applications, for
example Visual Studio 2019. This may require additional configuration when
multiple identities have signed in. In that case, set the environment variables
`AZURE_USERNAME` (typically an email address) and `AZURE_TENANT_ID` to select
the desired identity. Either, or both, may be set.

## Environment variables
[DefaultAzureCredential][default_cred_ref] and
[EnvironmentCredential][environment_cred_ref] can be configured with
environment variables. Each type of authentication requires values for specific
variables:

#### Service principal with secret
>|variable name|value
>|-|-
>|`AZURE_CLIENT_ID`|id of an Azure Active Directory application
>|`AZURE_TENANT_ID`|id of the application's Azure Active Directory tenant
>|`AZURE_CLIENT_SECRET`|one of the application's client secrets

#### Service principal with certificate
>|variable name|value
>|-|-
>|`AZURE_CLIENT_ID`|id of an Azure Active Directory application
>|`AZURE_TENANT_ID`|id of the application's Azure Active Directory tenant
>|`AZURE_CLIENT_CERTIFICATE_PATH`|path to a PEM-encoded certificate file including private key (without password protection)

#### Username and password
>|variable name|value
>|-|-
>|`AZURE_CLIENT_ID`|id of an Azure Active Directory application
>|`AZURE_USERNAME`|a username (usually an email address)
>|`AZURE_PASSWORD`|that user's password

> Note: username/password authentication is not supported by the async API
([azure.identity.aio][ref_docs_aio])

Configuration is attempted in the above order. For example, if values for a
client secret and certificate are both present, the client secret will be used.

# Examples
## Authenticating with `DefaultAzureCredential`
This example demonstrates authenticating the `BlobServiceClient` from the
[azure-storage-blob][azure_storage_blob] library using
[DefaultAzureCredential](#defaultazurecredential "DefaultAzureCredential").

```py
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

# This credential first checks environment variables for configuration as described above.
# If environment configuration is incomplete, it will try managed identity.
credential = DefaultAzureCredential()

client = BlobServiceClient(account_url, credential=credential)
```

## Authenticating a service principal with a client secret:
This example demonstrates authenticating the `KeyClient` from the
[azure-keyvault-keys][azure_keyvault_keys] library using
[ClientSecretCredential][client_secret_cred_ref].

```py
from azure.identity import ClientSecretCredential
from azure.keyvault.keys import KeyClient

credential = ClientSecretCredential(tenant_id, client_id, client_secret)

client = KeyClient("https://my-vault.vault.azure.net", credential)
```

## Authenticating a service principal with a certificate:
This example demonstrates authenticating the `SecretClient` from the
[azure-keyvault-secrets][azure_keyvault_secrets] library using
[CertificateCredential][cert_cred_ref].

```py
from azure.identity import CertificateCredential
from azure.keyvault.secrets import SecretClient

# requires a PEM-encoded certificate with private key, not protected with a password
cert_path = "/app/certs/certificate.pem"
credential = CertificateCredential(tenant_id, client_id, cert_path)

client = SecretClient("https://my-vault.vault.azure.net", credential)
```

## Chaining credentials:
[ChainedTokenCredential][chain_cred_ref] links multiple credential instances
to be tried sequentially when authenticating. The following example demonstrates
creating a credential which will attempt to authenticate using managed identity,
and fall back to a service principal if a managed identity is unavailable. This
example uses the `EventHubClient` from the [azure-eventhub][azure_eventhub]
client library.

```py
from azure.eventhub import EventHubClient
from azure.identity import ChainedTokenCredential, ClientSecretCredential, ManagedIdentityCredential

managed_identity = ManagedIdentityCredential()
service_principal = ClientSecretCredential(tenant_id, client_id, client_secret)

# when an access token is needed, the chain will try each
# credential in order, stopping when one provides a token
credential_chain = ChainedTokenCredential(managed_identity, service_principal)

# the ChainedTokenCredential can be used anywhere a credential is required
client = EventHubClient(host, event_hub_path, credential_chain)
```

## Async credentials:
This library includes an async API supported on Python 3.5+. To use the async
credentials in [azure.identity.aio][ref_docs_aio], you must first install an
async transport, such as [aiohttp](https://pypi.org/project/aiohttp/). See
[azure-core documentation](../../core/azure-core/README.md#transport)
for more information.

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
# most credentials have async equivalents supported on Python 3.5.3+
from azure.identity.aio import DefaultAzureCredential
from azure.keyvault.secrets.aio import SecretClient

# async credentials have the same API and configuration as their synchronous
# counterparts, and are used with (async) Azure SDK clients in the same way
default_credential = DefaultAzureCredential()
client = SecretClient("https://my-vault.vault.azure.net", default_credential)
```

# Troubleshooting
## General
Credentials raise `azure.core.exceptions.ClientAuthenticationError` when they fail
to authenticate. `ClientAuthenticationError` has a `message` attribute which
describes why authentication failed. When raised by
[DefaultAzureCredential](#defaultazurecredential) or `ChainedTokenCredential`,
the message collects error messages from each credential in the chain.

For more details on handling Azure Active Directory errors please refer to the
Azure Active Directory
[error code documentation](https://docs.microsoft.com/en-us/azure/active-directory/develop/reference-aadsts-error-codes).


# Next steps
## Client library support
This is an incomplete list of client libraries accepting Azure Identity
credentials. You can learn more about these libraries, and find additional
documentation of them, at the links below.
- [azure-appconfiguration](../../appconfiguration/azure-appconfiguration)
- [azure-eventhub][azure_eventhub]
- [azure-keyvault-certificates](../../keyvault/azure-keyvault-certificates)
- [azure-keyvault-keys][azure_keyvault_keys]
- [azure-keyvault-secrets][azure_keyvault_secrets]
- [azure-storage-blob][azure_storage_blob]
- [azure-storage-queue](../../storage/azure-storage-queue)

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

[azure_eventhubs]: ../../eventhub/azure-eventhub
[azure_keyvault_keys]: ../../keyvault/azure-keyvault-keys
[azure_keyvault_secrets]: ../../keyvault/azure-keyvault-secrets
[azure_storage_blob]: ../../storage/azure-storage-blob

[ref_docs]: https://aka.ms/azsdk-python-identity-docs
[ref_docs_aio]: https://aka.ms/azsdk-python-identity-aio-docs
[cert_cred_ref]: https://aka.ms/azsdk-python-identity-cert-cred-ref
[chain_cred_ref]: https://aka.ms/azsdk-python-identity-chain-cred-ref
[client_secret_cred_ref]: https://aka.ms/azsdk-python-identity-client-secret-cred-ref
[client_secret_cred_aio_ref]: https://aka.ms/azsdk-python-identity-client-secret-cred-aio-ref
[default_cred_ref]: https://aka.ms/azsdk-python-identity-default-cred-ref
[device_code_cred_ref]: https://aka.ms/azsdk-python-identity-device-code-cred-ref
[environment_cred_ref]: https://aka.ms/azsdk-python-identity-environment-cred-ref
[interactive_cred_ref]: https://aka.ms/azsdk-python-identity-interactive-cred-ref
[managed_id_cred_ref]: https://aka.ms/azsdk-python-identity-managed-id-cred-ref
[userpass_cred_ref]: https://aka.ms/azsdk-python-identity-userpass-cred-ref

![Impressions](https://azure-sdk-impressions.azurewebsites.net/api/impressions/azure-sdk-for-python%2Fsdk%2Fidentity%2Fazure-identity%2FREADME.png)
