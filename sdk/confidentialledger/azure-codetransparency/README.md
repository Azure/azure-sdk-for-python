# Code Transparency Service client library for Python

The Azure Code Transparency Service is a part of Microsoft's Confidential Ledger services, providing a transparent and immutable record of code artifacts. It allows you to register code entries and verify their authenticity and integrity through a secure, distributed ledger system.

This client library allows you to interact with the Code Transparency Service to:

- Register new code entries on the ledger
- Retrieve registered code entries
- Obtain statements for code entries
- Verify the status of operations
- Access public keys and service configuration

[Source code](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/confidentialledger/azure-codetransparency) | [Package (PyPI)](https://pypi.org/project/azure-codetransparency/) | [API reference documentation](#) | [Product documentation](#)

## Getting started

### Prerequisites

- Python 3.9 or later is required to use this package.
- You need an [Azure subscription][azure_sub] to use this package.
- An existing Code Transparency Service instance.

### Install the package

```bash
python -m pip install azure-codetransparency
```

### Authenticate the client

The Code Transparency Service supports authentication with API keys or Azure Active Directory credentials through [azure-identity](https://pypi.org/project/azure-identity/).

#### Using an API Key

```python
from azure.codetransparency import CodeTransparencyClient
from azure.core.credentials import AzureKeyCredential

client = CodeTransparencyClient(
    endpoint="https://<service-name>.confidentialledger.azure.com",
    credential=AzureKeyCredential(key="<api-key>")
)
```

#### Using Azure Active Directory Authentication

```python
from azure.codetransparency import CodeTransparencyClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
client = CodeTransparencyClient(
    endpoint="https://<service-name>.confidentialledger.azure.com",
    credential=credential
)
```

## Key concepts

### Client

The `CodeTransparencyClient` is the primary interface for working with the Code Transparency Service. It provides methods for all supported operations with the service.

### Binary Data

Most of the methods in this SDK deal with binary data. The service accepts and returns binary data for entries, configurations, and statements. The SDK exposes these as `bytes` objects or iterators of `bytes`.

## Examples

### Create a code entry

```python
from azure.codetransparency import CodeTransparencyClient
from azure.core.credentials import AzureKeyCredential
import os

# Get credentials from environment variables
api_key = os.getenv("AZURE_KEY")
if api_key is None:
    raise ValueError("Environment variable AZURE_KEY must be set")

# Create a client
client = CodeTransparencyClient(
    endpoint="https://<service-name>.confidentialledger.azure.com",
    credential=AzureKeyCredential(key=api_key)
)

# Create a new entry with binary data
binary_data = b"Sample binary data for code entry"
response = client.create_entry(body=binary_data)

# Process the response
for chunk in response:
    print(f"Received {len(chunk)} bytes")
```

### Get a code entry by ID

```python
from azure.codetransparency import CodeTransparencyClient
from azure.core.credentials import AzureKeyCredential
import os

# Get credentials from environment variables
api_key = os.getenv("AZURE_KEY")
if api_key is None:
    raise ValueError("Environment variable AZURE_KEY must be set")

# Create a client
client = CodeTransparencyClient(
    endpoint="https://<service-name>.confidentialledger.azure.com",
    credential=AzureKeyCredential(key=api_key)
)

# Get a code entry by its ID
entry_id = "example-entry-id"
response = client.get_entry(entry_id=entry_id)

# Process the binary response
for chunk in response:
    print(f"Received {len(chunk)} bytes")
```

### Get the transparency service configuration

```python
from azure.codetransparency import CodeTransparencyClient
from azure.core.credentials import AzureKeyCredential
import os

# Get credentials from environment variables
api_key = os.getenv("AZURE_KEY")
if api_key is None:
    raise ValueError("Environment variable AZURE_KEY must be set")

# Create a client
client = CodeTransparencyClient(
    endpoint="https://<service-name>.confidentialledger.azure.com",
    credential=AzureKeyCredential(key=api_key)
)

# Get the transparency service configuration in CBOR format
response = client.get_transparency_config_cbor()

# Process the binary response
for chunk in response:
    print(f"Received {len(chunk)} bytes of configuration data")
```

## Troubleshooting

### Logging

This library uses the standard [logging](https://docs.python.org/3/library/logging.html) module for logging. Basic information about HTTP sessions (URLs, headers, etc.) is logged at the INFO level.

Detailed DEBUG level logging, including request/response bodies and unredacted headers, can be enabled on the client with the `logging_enable` argument:

```python
import sys
import logging
from azure.codetransparency import CodeTransparencyClient
from azure.core.credentials import AzureKeyCredential

# Create a logger for the SDK
logger = logging.getLogger('azure')
logger.setLevel(logging.DEBUG)

# Configure a console output
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

# Create a client with logging enabled
client = CodeTransparencyClient(
    endpoint="https://<service-name>.confidentialledger.azure.com",
    credential=AzureKeyCredential(key="<api-key>"),
    logging_enable=True
)
```

### Handle exceptions

Operations will raise exceptions if the service returns an error. These exceptions are derived from `azure.core.exceptions.HttpResponseError`.

```python
from azure.core.exceptions import HttpResponseError

try:
    client.get_entry(entry_id="nonexistent-entry-id")
except HttpResponseError as e:
    print(f"Error: {e.message}")
```

## Contributing

This project welcomes contributions and suggestions. Most contributions require
you to agree to a Contributor License Agreement (CLA) declaring that you have
the right to, and actually do, grant us the rights to use your contribution.
For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether
you need to provide a CLA and decorate the PR appropriately (e.g., label,
comment). Simply follow the instructions provided by the bot. You will only
need to do this once across all repos using our CLA.

This project has adopted the
[Microsoft Open Source Code of Conduct][code_of_conduct]. For more information,
see the Code of Conduct FAQ or contact opencode@microsoft.com with any
additional questions or comments.

<!-- LINKS -->
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[authenticate_with_token]: https://docs.microsoft.com/azure/cognitive-services/authentication?tabs=powershell#authenticate-with-an-authentication-token
[azure_identity_credentials]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#credentials
[azure_identity_pip]: https://pypi.org/project/azure-identity/
[default_azure_credential]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#defaultazurecredential
[pip]: https://pypi.org/project/pip/
[azure_sub]: https://azure.microsoft.com/free/
