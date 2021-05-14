# Azure AgriFood Farming client library for Python

## Getting started

### Prerequisites

- Python 2.7, or 3.6 or later is required to use this package.
- You must have an [Azure subscription][azure_subscription] and an AgriFood resource to use this package.

#### Create an AgriFood Resource

### Install the package

Install the Azure AgriFood Farming client library for Python with [pip][pip]:

```bash
pip install azure-agrifood-farming
```

### Authenticate the client

To use an [Azure Active Directory (AAD) token credential][authenticate_with_token],
provide an instance of the desired credential type obtained from the
[azure-identity][azure_identity_credentials] library.

To authenticate with AAD, you must first [pip][pip] install [`azure-identity`][azure_identity_pip] and
enable AAD authentication on your AgriFood resource (ADD LINK).

After setup, you can choose which type of [credential][azure_identity_credentials] from azure.identity to use.
As an example, [DefaultAzureCredential][default_azure_credential]
can be used to authenticate the client:

Set the values of the client ID, tenant ID, and client secret of the AAD application as environment variables:
AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET

Use the returned token credential to authenticate the client:

```python
from azure.agrifood.farming import FarmBeatsClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
client = FarmBeatsClient(endpoint="https://<my-account-name>.farmbeats.azure.net", credential=credential)
```

## Key concepts

## Examples

The following section shows you how to initialize and authenticate your client, then get all of your type-defs.

## Troubleshooting

### General

The AgriFood Farming client will raise exceptions defined in [Azure Core][azure_core] if you call `.raise_for_status()` on your responses.

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
from azure.agrifood.farming import FarmBeatsClient

# Create a logger for the 'azure' SDK
logger = logging.getLogger('azure')
logger.setLevel(logging.DEBUG)

# Configure a console output
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

endpoint = "https://<my-account-name>.farmbeats.azure.net"
credential = DefaultAzureCredential()

# This client will log detailed information about its HTTP sessions, at DEBUG level
client = FarmBeatsClient(endpoint=endpoint, credential=credential, logging_enable=True)
```

Similarly, `logging_enable` can enable detailed logging for a single call,
even when it isn't enabled for the client:

```python
client.crops.get(crop_id="crop_id", logging_enable=True)
```

## Next steps

## Contributing

This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit [cla.microsoft.com][cla].

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct][code_of_conduct]. For more information see the [Code of Conduct FAQ][coc_faq] or contact [opencode@microsoft.com][coc_contact] with any additional questions or comments.

<!-- LINKS -->

[azure_subscription]: https://azure.microsoft.com/free/
[pip]: https://pypi.org/project/pip/
[authenticate_with_token]: https://docs.microsoft.com/azure/cognitive-services/authentication?tabs=powershell#authenticate-with-an-authentication-token
[azure_identity_credentials]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/identity/azure-identity#credentials
[azure_identity_pip]: https://pypi.org/project/azure-identity/
[default_azure_credential]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/identity/azure-identity#defaultazurecredential
[python_logging]: https://docs.python.org/3.5/library/logging.html
[cla]: https://cla.microsoft.com
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[coc_faq]: https://opensource.microsoft.com/codeofconduct/faq/
[coc_contact]: mailto:opencode@microsoft.com
