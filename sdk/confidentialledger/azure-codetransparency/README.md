# Azure Code Transparency Service client library for Python

This is the Microsoft Azure Code Transparency Service client library for Python.

## Getting started

### Prerequisites

- Python 3.8 or later is required to use this package.
- You must have an [Azure subscription][azure_subscription] and a Code Transparency Service instance.

### Install the package

Install the Azure Code Transparency Service client library for Python with [pip][pip]:

```bash
pip install azure-codetransparency
```

### Authentication

To use Azure Code Transparency Service, you need to authenticate with your Azure credentials. The Azure Identity library makes this easy. Install it with:

```bash
pip install azure-identity
```

## Usage

```python
from azure.identity import DefaultAzureCredential
from azure.codetransparency import CodeTransparencyClient

credential = DefaultAzureCredential()
client = CodeTransparencyClient(
    endpoint="https://your-instance.confidentialledger.azure.com/",
    credential=credential
)

# Use the client for Code Transparency operations
# Example operations would be added here based on the actual API
```

### Async client usage

```python
import asyncio
from azure.identity.aio import DefaultAzureCredential
from azure.codetransparency.aio import CodeTransparencyClient

async def main():
    credential = DefaultAzureCredential()
    async with CodeTransparencyClient(
        endpoint="https://your-instance.confidentialledger.azure.com/",
        credential=credential
    ) as client:
        # Use the async client for Code Transparency operations
        pass

asyncio.run(main())
```

## API Version

This version of the client library supports the Azure Code Transparency Service API version `2025-01-31-preview`.

## Contributing

This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

[azure_subscription]: https://azure.microsoft.com/free/
[pip]: https://pypi.org/project/pip/