# Azure Identity client library for Python
Azure Identity simplifies authentication across the Azure SDK.
It supports token authentication using an Azure Active Directory
[service principal](https://docs.microsoft.com/en-us/cli/azure/create-an-azure-service-principal-azure-cli?view=azure-cli-latest)
or
[Azure managed identity](https://docs.microsoft.com/en-us/azure/active-directory/managed-identities-azure-resources/overview).

# Getting started
## Prerequisites
- an Azure subscription
- Python 2.7, or Python 3.3 or later
  - Python 3.5 or later for `asyncio` support

## Install the package
Install Azure Identity with pip:
```sh
pip install azure-identity
```

# Key concepts
## Credentials
Azure Identity offers a variety of credential classes accepted by Azure SDK
data plane libraries. Integration with Azure Identity is documented in each
library's documentation. Azure SDK management libraries do not presently
accept Azure Identity credentials.

Credentials differ mostly in configuration.

|credential class|identity|configuration
|-|-|-
|`DefaultAzureCredential`|service principal or managed identity|none for managed identity; environment variables for service principal
|`ManagedIdentityCredential`|managed identity|none
|`EnvironmentCredential`|service principal (client secret or certificate)|environment variables
|`ClientSecretCredential`|service principal (with client secret)|constructor parameters
|`CertificateCredential`|service principal (with certificate)|constructor parameters

Credentials can be chained so that each is tried in turn until one succeeds;
see the examples below for details.

## DefaultAzureCredential
`DefaultAzureCredential` is appropriate for most scenarios. It supports
authenticating as a service principal or a managed identity. Authenticating
as a managed identity requires no configuration.

To authenticate as a service
principal, provide configuration in environment variables:
|variable name|value
|-|-
|`AZURE_CLIENT_ID`|the principal's app id
|`AZURE_TENANT_ID`|id of the principal's Azure Active Directory tenant
|`AZURE_CLIENT_SECRET`|an authentication secret for the principal
|`AZURE_CLIENT_CERTIFICATE_PATH`|path to a PEM-encoded certificate file including private key

Either `AZURE_CLIENT_SECRET` or `AZURE_CLIENT_CERTIFICATE_PATH` must be set.
If both are set, the client secret will be used.

# Examples

## `DefaultAzureCredential`
```py
# The default credential first checks environment variables for configuration as described above.
# If environment configuration is incomplete, it will try managed identity.
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()

# Azure SDK clients accept credentials as a parameter
from azure.security.keyvault import VaultClient

client = VaultClient(vault_url, credential)
```

## Authenticating as a service principal:
```py
# using a client secret
from azure.identity import ClientSecretCredential

credential = ClientSecretCredential(client_id, client_secret, tenant_id)

# using a certificate requires a PEM-encoded private key file
from azure.identity import CertificateCredential

credential = CertificateCredential(client_id, tenant_id, "/certs/private-key.pem")

# using environment variables
from azure.identity import EnvironmentCredential

# will authenticate with client secret or certificate,
# depending on which environment variables are set
# (see Key Concepts above for variable names and expected values)
credential = EnvironmentCredential()
```

## Chaining credentials:
```py
from azure.identity import ClientSecretCredential, ManagedIdentityCredential, ChainedTokenCredential

first_principal = ClientSecretCredential(client_id, client_secret, tenant_id)
second_principal = ClientSecretCredential(another_client_id, another_secret, tenant_id)
credentials = [first_principal, second_principal, ManagedIdentityCredential()]

# when an access token is requested, the chain will try each
# credential in order, stopping when one provides a token
credential_chain = ChainedTokenCredential(credentials)

# the chain can be used anywhere a credential is required
from azure.security.keyvault import VaultClient

client = VaultClient(vault_url, credential=credential_chain)
```

# Troubleshooting

# Next steps

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
