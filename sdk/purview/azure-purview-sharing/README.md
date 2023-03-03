# Azure Share client library for Python

Microsoft Purview Share is a fully managed cloud service.

**Please rely heavily on the [service's documentation][sharing_product_documentation] and our [protocol client docs][protocol_client_quickstart] to use this library**

[Source code][source_code] | [Package (PyPI)][client_pypi_package] | [Product documentation][sharing_product_documentation]

## Getting started

### Install the package

Install the Azure Purview Sharing client library for Python with [pip][pip]:

```bash
pip install azure-purview-sharing
```

### Prerequisites

- You must have an [Azure subscription][azure_subscription] and a [Purview resource][purview_resource] to use this package.
- Python 3.6 or later is required to use this package.

### Authenticate the client

#### Using Azure Active Directory

This document demonstrates using [DefaultAzureCredential][default_cred_ref] to authenticate via Azure Active Directory. However, any of the credentials offered by the [Azure.Identity][azure_identity] will be accepted.  See the [Azure.Identity][azure_identity] documentation for more information about other credentials.

Once you have chosen and configured your credential, you can create instances of the `PurviewSharing`.

```python
from azure.purview.sharing import PurviewSharing
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
client = PurviewSharing(endpoint="https://<my-account-name>.purview.azure.com", credential=credential)
```

## Key concepts

## Examples

The following section shows you how to initialize and authenticate your client and share data.

### Create sent share

```python Snippet:create_a_sent_share
```

### Get sent share

```python Snippet:get_a_sent_share
```

### List sent shares

```python Snippet:get_all_sent_shares
```

### Create sent share invitation

```python Snippet:send_a_user_invitation
```

### Get sent share invitation

```python Snippet:get_a_sent_invitation
```

### List sent share invitations

```python Snippet:view_sent_invitations
```

### List detached received shares

```python Snippet:get_all_detached_received_shares
```

### Create a received share

```python Snippet:attach_a_received_share
```

### Get received share

```python Snippet:get_a_received_share
```

### List attached received shares

```python Snippet:list_attached_received_shares
```

### Delete received share

```python Snippet:delete_a_received_share
```

### Delete sent share

```python Snippet:delete_a_sent_share
```

## Troubleshooting

### General

The Purview Catalog client will raise exceptions defined in [Azure Core][azure_core] if you call `.raise_for_status()` on your responses.

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
from azure.purview.catalog import PurviewCatalogClient

# Create a logger for the 'azure' SDK
logger = logging.getLogger('azure')
logger.setLevel(logging.DEBUG)

# Configure a console output
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

endpoint = "https://<my-account-name>.purview.azure.com"
credential = DefaultAzureCredential()

# This client will log detailed information about its HTTP sessions, at DEBUG level
client = PurviewCatalogClient(endpoint=endpoint, credential=credential, logging_enable=True)
```

Similarly, `logging_enable` can enable detailed logging for a single `send_request` call,
even when it isn't enabled for the client:

```python
result = client.types.get_all_type_definitions(logging_enable=True)
```

## Next steps

For more generic samples, see our [client docs][request_builders_and_client].

## Contributing

This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit [cla.microsoft.com][cla].

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct][code_of_conduct]. For more information see the [Code of Conduct FAQ][coc_faq] or contact [opencode@microsoft.com][coc_contact] with any additional questions or comments.

<!-- LINKS -->

[source_code]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/purview/azure-purview-sharing/azure/purview/sharing
[client_pypi_package]: https://aka.ms/azsdk/python/purviewsharing/pypi
[sharing_ref_docs]: https://aka.ms/azsdk/python/purviewcatalog/ref-docs
[sharing_product_documentation]: https://azure.microsoft.com/services/purview/
[azure_subscription]: https://azure.microsoft.com/free/
[purview_resource]: https://docs.microsoft.com/azure/purview
[pip]: https://pypi.org/project/pip/
[authenticate_with_token]: https://docs.microsoft.com/azure/cognitive-services/authentication?tabs=powershell#authenticate-with-an-authentication-token
[azure_identity_credentials]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#credentials
[azure_identity_pip]: https://pypi.org/project/azure-identity/
[default_azure_credential]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#defaultazurecredential
[request_builders_and_client]: https://aka.ms/azsdk/python/protocol/quickstart
[enable_aad]: https://docs.microsoft.com/azure/purview/
[azure_core]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/README.md
[python_logging]: https://docs.python.org/3.5/library/logging.html
[cla]: https://cla.microsoft.com
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[coc_faq]: https://opensource.microsoft.com/codeofconduct/faq/
[coc_contact]: mailto:opencode@microsoft.com