# Azure Planetary Computer client library for Python

This package provides a Python SDK for interacting with the **Azure Planetary Computer** data plane API. It enables developers to manage and explore geospatial collections using STAC standards, perform ingestion, rendering, mosaic configuration, and tile service access.

> ⚠️ This library is in **preview** and subject to change.

---

## Getting Started

### Prerequisites

- Python 3.9 or later
- An [Azure subscription][azure_sub]
- A deployed Azure Planetary Computer instance (endpoint)
- [Azure Identity SDK][azure_identity_pip] for authentication

---

### Installation

Install the SDK via [PyPI][pip]:

```bash
pip install azure-planetarycomputer
```

Install the Azure Identity library (required for authentication):

```bash
pip install azure-identity
```

---

### Authentication

To authenticate with the Azure Planetary Computer service, use `DefaultAzureCredential` from the `azure-identity` package.

Set the following environment variables for your Azure Active Directory (AAD) application:

```bash
AZURE_CLIENT_ID=<your-client-id>
AZURE_TENANT_ID=<your-tenant-id>
AZURE_CLIENT_SECRET=<your-client-secret>
```

Then create a client:

```python
from azure.planetarycomputer import MicrosoftPlanetaryComputerProClient
from azure.identity import DefaultAzureCredential

client = MicrosoftPlanetaryComputerProClient(
    endpoint="https://<your-endpoint>",  # Example: https://example.geocatalog.spatio.azure.com
    credential=DefaultAzureCredential()
)
```

---

## Usage Examples

### Basic API Call

```python
from azure.planetarycomputer import MicrosoftPlanetaryComputerProClient
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError

client = MicrosoftPlanetaryComputerProClient(
    endpoint="https://your-geocatalog-endpoint",
    credential=DefaultAzureCredential()
)

try:
    # Example operation
    result = client.stac_collection_operations.get_all()
    print(result)
except HttpResponseError as e:
    print("Error:", e.response.json())
```

---

## Directory Structure

```
sdk/
└── planetarycomputer/
    └── azure-planetarycomputer/
        ├── azure/planetarycomputer/         # ✅ Core SDK package
        ├── generated_samples/               # ✅ Auto-generated usage examples
        ├── generated_tests/                 # ✅ Auto-generated tests (not required for preview)
        ├── tutorial/                        # ✅ Jupyter notebook tutorial for real-world scenarios
        ├── README.md                        # ✅ This file
        ├── CHANGELOG.md                     # ✅ Version history
        ├── setup.py                         # ✅ Python packaging setup
        ├── LICENSE, MANIFEST.in             # ✅ Legal and package metadata
```

---

## Resources

- [Microsoft Planetary Computer Docs](https://planetarycomputer.microsoft.com/)
- [STAC Specification](https://stacspec.org/)
- [Azure SDK for Python](https://github.com/Azure/azure-sdk-for-python)
- [Azure Identity Authentication](https://learn.microsoft.com/azure/developer/python/sdk/authentication-overview)

---

## Contributing

This project welcomes contributions. To contribute:

1. Fork the repo and create your feature branch.
2. Ensure code passes validation.
3. Submit a pull request.

Before submitting, you must sign the [Microsoft CLA](https://cla.microsoft.com).

This project follows the [Microsoft Open Source Code of Conduct][code_of_conduct].

---

<!-- Links -->
[azure_sub]: https://azure.microsoft.com/free/
[azure_identity_pip]: https://pypi.org/project/azure-identity/
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[pip]: https://pypi.org/project/pip/