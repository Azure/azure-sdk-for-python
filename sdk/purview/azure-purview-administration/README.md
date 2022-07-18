# Azure Purview Administration client library for Python

Azure Purview is a fully managed cloud service.

**Please rely heavily on the [service's documentation][account_product_documentation] to use this library**

[Source code][source_code] |  [Package (PyPI)][account_pypi] | [API reference documentation][account_ref_docs]| [Product documentation][account_product_documentation]

## _Disclaimer_

_Azure SDK Python packages support for Python 2.7 has ended 01 January 2022. For more information and questions, please refer to https://github.com/Azure/azure-sdk-for-python/issues/20691_

## Getting started

### Prerequisites

- Python 3.6 or later is required to use this package.
- You must have an [Azure subscription][azure_subscription] and a [Purview][purview_resource] to use this package.

#### Create a Purview Resource

Follow [these][purview_resource] instructions to create your Purview resource

### Install the package

Install the Azure Purview Account client library for Python with [pip][pip]:

```bash
pip install azure-purview-administration
```

### Authenticate the client

To use an [Azure Active Directory (AAD) token credential][authenticate_with_token],
provide an instance of the desired credential type obtained from the
[azure-identity][azure_identity_credentials] library.

To authenticate with AAD, you must first [pip][pip] install [`azure-identity`][azure_identity_pip] and
[enable AAD authentication on your Purview resource][enable_aad]

After setup, you can choose which type of [credential][azure_identity_credentials] from azure.identity to use.
As an example, [DefaultAzureCredential][default_azure_credential]
can be used to authenticate the client:

Set the values of the client ID, tenant ID, and client secret of the AAD application as environment variables:
AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET

Use the returned token credential to authenticate the client:

```python
from azure.purview.administration.account import PurviewAccountClient
from azure.purview.administration.metadatapolicies import PurviewMetadataPoliciesClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
endpoint = "https://<my-account-name>.purview.azure.com"
account_client = PurviewAccountClient(endpoint=endpoint, credential=credential)
metadatapolicy_client = PurviewMetadataPoliciesClient(endpoint=endpoint, credential=credential)
```

## Key concepts

### Client

The package contains two kinds of client: `PurviewAccountClient` and `PurviewMetadataPoliciesClient`. You could use them 
with one package according to your requirements. 

## Examples

The following section shows you how to initialize and authenticate your client, then list all of your keys.

- [Get Keys](#get-keys "Get All Keys")

### Get Keys

```python
from azure.purview.administration.account import PurviewAccountClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
client = PurviewAccountClient(endpoint="https://<my-account-name>.purview.azure.com", credential=credential)
response = client.accounts.get_access_keys()
print(response)
```

The following section shows you how to initialize and authenticate your client, then list all of your roles.

- [List_Roles](#list-roles "List Roles")

### List Roles

```python
from azure.purview.administration.metadatapolicies import PurviewMetadataPoliciesClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
client = PurviewMetadataPoliciesClient(endpoint="https://<my-account-name>.purview.azure.com", credential=credential)
response = client.metadata_roles.list()
result = [item for item in response]
print(result)
```

## Troubleshooting

### General

The Purview client will raise exceptions if status code of your responses is not defined.

### Logging

This library uses the standard
[logging][python_logging] library for logging.
Basic information about HTTP sessions (URLs, headers, etc.) is logged at INFO
level.

Detailed DEBUG level logging, including request/response bodies and unredacted
headers, can be enabled on a client with the `logging_enable` keyword argument:

```python
import sys
import logging
from azure.identity import DefaultAzureCredential
from azure.purview.administration.account import PurviewAccountClient

# Create a logger for the 'azure' SDK
logger = logging.getLogger('azure')
logger.setLevel(logging.DEBUG)

# Configure a console output
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

endpoint = "https://<my-account-name>.purview.azure.com"
credential = DefaultAzureCredential()

# This client will log detailed information about its HTTP sessions, at DEBUG level
client = PurviewAccountClient(endpoint=endpoint, credential=credential, logging_enable=True)
```

Similarly, `logging_enable` can enable detailed logging for a single call,
even when it isn't enabled for the client:

```python
result = client.accounts.get_access_keys(logging_enable=True)
```

## Next steps

For more generic samples, see our [client docs][request_builders_and_client].

## Contributing

This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit [cla.microsoft.com][cla].

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct][code_of_conduct]. For more information see the [Code of Conduct FAQ][coc_faq] or contact [opencode@microsoft.com][coc_contact] with any additional questions or comments.

<!-- LINKS -->

[source_code]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/purview/
[account_pypi]: https://pypi.org/project/azure-purview-catalog/#history
[account_ref_docs]: https://azure.github.io/azure-sdk-for-python/
[account_product_documentation]: https://azure.microsoft.com/services/purview/
[azure_subscription]: https://azure.microsoft.com/free/
[purview_resource]: https://docs.microsoft.com/azure/purview/create-catalog-portal
[pip]: https://pypi.org/project/pip/
[authenticate_with_token]: https://docs.microsoft.com/azure/cognitive-services/authentication?tabs=powershell#authenticate-with-an-authentication-token
[azure_identity_credentials]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#credentials
[azure_identity_pip]: https://pypi.org/project/azure-identity/
[default_azure_credential]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#defaultazurecredential
[enable_aad]: https://docs.microsoft.com/azure/purview/create-catalog-portal#add-a-security-principal-to-a-data-plane-role
[python_logging]: https://docs.python.org/3.5/library/logging.html
[cla]: https://cla.microsoft.com
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[coc_faq]: https://opensource.microsoft.com/codeofconduct/faq/
[coc_contact]: mailto:opencode@microsoft.com
[request_builders_and_client]: https://aka.ms/azsdk/python/protocol/quickstart
