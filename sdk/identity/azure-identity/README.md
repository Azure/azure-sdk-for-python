# Azure Identity client library for Python
Azure Identity simplifies authentication across the Azure SDK.
It supports token authentication using an Azure Active Directory
[service principal](https://docs.microsoft.com/en-us/cli/azure/create-an-azure-service-principal-azure-cli)
or
[managed identity](https://docs.microsoft.com/en-us/azure/active-directory/managed-identities-azure-resources/overview).

# Getting started
## Prerequisites
- an Azure subscription
  - if you don't have one, you can sign up for a
  [free account](https://azure.microsoft.com/free/)
- Python 2.7 or 3.5.3+

## Install the package
Install Azure Identity with pip:
```sh
pip install azure-identity
```

# Key concepts
## Credentials
Azure Identity offers a variety of credential classes in the `azure.identity`
namespace. These are accepted by Azure SDK data plane clients. Each client
library documents its Azure Identity integration in its README and samples.
Azure SDK resource management libraries (which have `mgmt` in their names)
do not accept these credentials.

Credentials differ mostly in configuration:

|credential class|identity|configuration
|-|-|-
|`DefaultAzureCredential`|service principal or managed identity|none for managed identity; [environment variables](#environment-variables) for service principal
|`ManagedIdentityCredential`|managed identity|none
|`EnvironmentCredential`|service principal|[environment variables](#environment-variables)
|`ClientSecretCredential`|service principal|constructor parameters
|`CertificateCredential`|service principal|constructor parameters

Credentials can be chained and tried in turn until one succeeds; see
[chaining credentials](#chaining-credentials) for details.

All credentials have an async equivalent in the `azure.identity.aio` namespace.
These are supported on Python 3.5.3+. See the
[async credentials](#async-credentials) example for details.

## DefaultAzureCredential
`DefaultAzureCredential` is appropriate for most scenarios. It supports
authenticating as a service principal or managed identity. To authenticate
as a service principal, provide configuration in environment variables as
described in the next section.

Authenticating as a managed identity requires no configuration, but does
require platform support. See the
[managed identity documentation](https://docs.microsoft.com/en-us/azure/active-directory/managed-identities-azure-resources/services-support-managed-identities)
for more information.

## Environment variables

`DefaultAzureCredential` and `EnvironmentCredential` are configured for service
principal authentication with these environment variables:

|variable name|value
|-|-
|`AZURE_CLIENT_ID`|service principal's app id
|`AZURE_TENANT_ID`|id of the principal's Azure Active Directory tenant
|`AZURE_CLIENT_SECRET`|one of the service principal's client secrets
|`AZURE_CLIENT_CERTIFICATE_PATH`|path to a PEM-encoded certificate file including private key (without password)

Either `AZURE_CLIENT_SECRET` or `AZURE_CLIENT_CERTIFICATE_PATH` must be set.
If both are set, the client secret will be used.

# Examples

## `DefaultAzureCredential`
```py
# The default credential first checks environment variables for configuration as described above.
# If environment configuration is incomplete, it will try managed identity.
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()

# Azure SDK clients accept the credential as a parameter
from azure.keyvault.secrets import SecretClient

client = SecretClient(vault_url, credential)
```

## Authenticating as a service principal:
```py
# using a client secret
from azure.identity import ClientSecretCredential

credential = ClientSecretCredential(client_id, client_secret, tenant_id)

# using a certificate
from azure.identity import CertificateCredential

# requires a PEM-encoded certificate with private key, not protected with a password
cert_path = "/app/certs/certificate.pem"
credential = CertificateCredential(client_id, tenant_id, cert_path)

# using environment variables
from azure.identity import EnvironmentCredential

# authenticate with client secret or certificate,
# depending on environment variable settings
# (see "Environment variables" above for variable names and expected values)
credential = EnvironmentCredential()
```

## Chaining credentials:
```py
from azure.identity import ClientSecretCredential, ManagedIdentityCredential, ChainedTokenCredential

first_principal = ClientSecretCredential(client_id, client_secret, tenant_id)
second_principal = ClientSecretCredential(another_client_id, another_secret, tenant_id)

# when an access token is requested, the chain will try each
# credential in order, stopping when one provides a token
credential_chain = ChainedTokenCredential(first_principal, second_principal)

# the chain can be used anywhere a credential is required
from azure.keyvault.secrets import SecretClient

client = SecretClient(vault_url, credential=credential_chain)
```

## Async credentials:
```py
# all credentials have async equivalents supported on Python 3.5.3+
from azure.identity.aio import DefaultAzureCredential

default_credential = DefaultAzureCredential()

# async credentials have the same API and configuration as
# their synchronous counterparts...
from azure.identity.aio import ClientSecretCredential

credential = ClientSecretCredential(client_id, client_secret, tenant_id)

# ...and are used with async Azure SDK clients in the same way
from azure.keyvault.aio import SecretClient

client = SecretClient(vault_url, credential)
```

# Troubleshooting
## General
Credentials raise `azure.core.exceptions.ClientAuthenticationError` when they fail
to authenticate. `ClientAuthenticationError` has a `message` attribute which
describes why authentication failed. When raised by `ChainedTokenCredential`,
the message collects error messages from each credential in the chain.

# Next steps
## Provide Feedback
If you encounter bugs or have suggestions, please
[open an issue](https://github.com/Azure/azure-sdk-for-python/issues).

# Contributing
This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit [https://cla.microsoft.com](https://cla.microsoft.com).

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the
[Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information, see the
[Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/)
or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any
additional questions or comments.

![Impressions](https://azure-sdk-impressions.azurewebsites.net/api/impressions/azure-sdk-for-python%2Fsdk%2Fidentity%2Fazure-identity%2FREADME.png)
