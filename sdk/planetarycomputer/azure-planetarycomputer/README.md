# Azure Planetary Computer client library for Python

The Azure Planetary Computer client library provides access to Microsoft's planetary-scale geospatial data platform. The Planetary Computer includes petabytes of environmental monitoring data, processing APIs, and applications designed to make global environmental data easily accessible.

Key capabilities include:

- **STAC Catalog Management**: Create, read, update, and delete STAC (SpatioTemporal Asset Catalog) collections and items
- **Geospatial Data Ingestion**: Manage data ingestion pipelines and sources
- **Tiling Services**: Access map tiles, tile matrix sets, and WMTS capabilities
- **Mosaicing Operations**: Create and manage mosaics from geospatial datasets
- **Data Analysis**: Statistical analysis and bounds calculation for geospatial assets
- **Authentication & Authorization**: Secure access with SAS tokens and Azure Maps integration

[Source code][source_code]
| [Package (PyPI)][pc_pypi]
| [API reference documentation][pc_ref_docs]
| [Product documentation][pc_product_docs]

## Getting started

### Prerequisites

- Python 3.9 or later is required to use this package.
- You need an [Azure subscription][azure_sub] to use this package.
- Access to Azure Planetary Computer services or an Azure Planetary Computer instance.

### Install the package

```bash
python -m pip install azure-planetarycomputer
```

### Authenticate the client

In order to interact with the Planetary Computer service, you will need to create an instance of a client.
A **credential** is necessary to instantiate the client object.

Microsoft Entra ID credential is supported to authenticate the client.
For enhanced security, we strongly recommend utilizing Microsoft Entra ID credential for authentication.

#### Create the client with Microsoft Entra ID credential

To use the [DefaultAzureCredential][azure_sdk_python_default_azure_credential] type shown below, or other credential types provided with the Azure SDK, please install the `azure-identity` package:

```bash
pip install azure-identity
```

You will also need to [register a new Microsoft Entra ID application and grant access][register_aad_app] to Planetary Computer by assigning appropriate roles to your service principal.

Once completed, set the values of the client ID, tenant ID, and client secret of the Microsoft Entra ID application as environment variables:
`AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_CLIENT_SECRET`.

```python
"""DefaultAzureCredential will use the values from these environment
variables: AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET
"""
from azure.planetarycomputer import PlanetaryComputerClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
pc_client = PlanetaryComputerClient(credential=credential)
```

## Key concepts

### PlanetaryComputerClient

`PlanetaryComputerClient` provides operations for interacting with the Azure Planetary Computer platform, including:

#### STAC Operations
- **STAC Items**: Manage individual data items in STAC collections
- **STAC Collections**: Create and manage STAC collections and their configurations
- **STAC Search**: Search for geospatial data using STAC API standards
- **STAC Conformance**: Check API conformance classes

#### Data Ingestion
- **Ingestions**: Manage data ingestion jobs and operations
- **Ingestion Sources**: Configure and manage data sources for ingestion

#### Tiling and Visualization
- **Tiler Operations**: Generate tiles, previews, and static images from geospatial data
- **Mosaics**: Create and manage mosaics from multiple datasets
- **Maps and Legends**: Generate map legends and visualizations
- **Tile Matrix Sets**: Manage tile matrix definitions and operations

#### Geospatial Analysis
- **Statistics**: Calculate statistics for geospatial assets and regions
- **Bounds**: Determine spatial bounds of datasets
- **Points and Parts**: Extract data at specific geographic points or regions

#### Authentication and Security
- **SAS Operations**: Generate and manage Shared Access Signatures for secure data access
- **Azure Maps Integration**: Integration with Azure Maps services

## Examples

The following section provides several code snippets covering some of the most common Planetary Computer tasks:

### Search for STAC Items

Search for geospatial data using STAC API standards:

```python
from azure.planetarycomputer import PlanetaryComputerClient
from azure.identity import DefaultAzureCredential

# Create client
pc_client = PlanetaryComputerClient(credential=DefaultAzureCredential())

# Search for items in a collection with spatial and temporal filters
search_body = {
    "collections": ["landsat-c2-l2"],
    "bbox": [-122.5, 37.7, -122.3, 37.9],  # San Francisco Bay Area
    "datetime": "2023-01-01/2023-12-31",
    "limit": 10
}

search_result = pc_client.stac_search_operations.create(body=search_body)
print(f"Found {len(search_result.get('features', []))} items")
```

### Get STAC Item Details

Retrieve detailed information about a specific STAC item:

```python
from azure.planetarycomputer import PlanetaryComputerClient
from azure.identity import DefaultAzureCredential

pc_client = PlanetaryComputerClient(credential=DefaultAzureCredential())

# Get a specific STAC item
item = pc_client.stac_items.get(
    collection_id="landsat-c2-l2",
    item_id="LC08_L2SP_044034_20231015_02_T1"
)

print(f"Item: {item.get('id')}")
print(f"Geometry: {item.get('geometry')}")
print(f"Properties: {item.get('properties')}")
```

### Create STAC Collection

Create a new STAC collection for organizing geospatial data:

```python
from azure.planetarycomputer import PlanetaryComputerClient
from azure.identity import DefaultAzureCredential

pc_client = PlanetaryComputerClient(credential=DefaultAzureCredential())

# Define collection metadata
collection_data = {
    "id": "my-collection",
    "title": "My Geospatial Collection",
    "description": "A collection of geospatial data",
    "extent": {
        "spatial": {
            "bbox": [[-180, -90, 180, 90]]
        },
        "temporal": {
            "interval": [["2023-01-01T00:00:00Z", "2023-12-31T23:59:59Z"]]
        }
    },
    "license": "CC-BY-4.0"
}

# Create the collection
collection = pc_client.stac_collection_operations.create(
    collection_id="my-collection",
    body=collection_data
)
print(f"Created collection: {collection.get('id')}")
```

### Generate Map Tiles

Generate map tiles from geospatial data:

```python
from azure.planetarycomputer import PlanetaryComputerClient
from azure.identity import DefaultAzureCredential

pc_client = PlanetaryComputerClient(credential=DefaultAzureCredential())

# Get tile data for specific coordinates
tile_data = pc_client.tiler_tiles.get(
    z=10,  # Zoom level
    x=256,  # Tile X coordinate
    y=384,  # Tile Y coordinate
    scale=1,  # Scale factor
    format="png",  # Output format
    collection="landsat-c2-l2",
    item="LC08_L2SP_044034_20231015_02_T1"
)

# Save tile to file
with open("tile.png", "wb") as f:
    f.write(tile_data)
```

### Data Ingestion Management

Manage data ingestion operations:

```python
from azure.planetarycomputer import PlanetaryComputerClient
from azure.identity import DefaultAzureCredential

pc_client = PlanetaryComputerClient(credential=DefaultAzureCredential())

# Create an ingestion source
source_config = {
    "id": "my-data-source",
    "type": "blob-storage",
    "configuration": {
        "container": "data-container",
        "path": "geotiff-files/"
    }
}

ingestion_source = pc_client.ingestion_sources.create(
    source_id="my-data-source",
    body=source_config
)

# Start an ingestion job
ingestion_config = {
    "sourceId": "my-data-source",
    "collectionId": "my-collection",
    "configuration": {
        "processingOptions": {
            "overviewGeneration": True,
            "cogOptimization": True
        }
    }
}

ingestion = pc_client.ingestions.create(
    ingestion_id="my-ingestion-job",
    body=ingestion_config
)

print(f"Started ingestion job: {ingestion.get('id')}")
print(f"Status: {ingestion.get('status')}")
```

### Generate SAS Token for Secure Access

Generate Shared Access Signatures for secure data access:

```python
from azure.planetarycomputer import PlanetaryComputerClient
from azure.identity import DefaultAzureCredential

pc_client = PlanetaryComputerClient(credential=DefaultAzureCredential())

# Generate SAS token for accessing data
sas_request = {
    "permissions": "r",  # Read permission
    "expiryTime": "2024-12-31T23:59:59Z",
    "resources": ["collection:landsat-c2-l2"]
}

sas_token = pc_client.sas.get_token(body=sas_request)
print(f"SAS Token: {sas_token.get('token')}")
print(f"Expires: {sas_token.get('expiry')}")
```

## Troubleshooting

### General

Planetary Computer client library will raise exceptions defined in [Azure Core][python_azure_core_exceptions].
Error codes and messages raised by the Planetary Computer service can be found in the service documentation.

### Logging

This library uses the standard [logging][python_logging] library for logging.

Basic information about HTTP sessions (URLs, headers, etc.) is logged at `INFO` level.

Detailed `DEBUG` level logging, including request/response bodies and **unredacted**
headers, can be enabled on the client or per-operation with the `logging_enable` keyword argument.

See full SDK logging documentation with examples in the [Azure SDK documentation][sdk_logging_docs].

```python
import sys
import logging

from azure.planetarycomputer import PlanetaryComputerClient
from azure.identity import DefaultAzureCredential

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    stream=sys.stdout)

credential = DefaultAzureCredential()
pc_client = PlanetaryComputerClient(credential=credential)

# Enable logging for a specific operation
response = pc_client.stac_items.get(..., logging_enable=True)
```

### Optional Configuration

Optional keyword arguments can be passed in at the client and per-operation level.
The azure-core [reference documentation][azure_core_ref_docs] describes available configurations for retries, logging, transport protocols, and more.

## Next steps

### More sample code

See the `samples` directory for several code snippets illustrating common patterns used in the Planetary Computer Python API.

### Additional documentation

For more extensive documentation on Azure Planetary Computer, see the [Planetary Computer documentation][pc_product_docs] on Microsoft Learn.

## Contributing

This project welcomes contributions and suggestions. Most contributions require
you to agree to a Contributor License Agreement (CLA) declaring that you have
the right to, and actually do, grant us the rights to use your contribution.
For details, visit [Microsoft CLA][microsoft_cla].

When you submit a pull request, a CLA-bot will automatically determine whether
you need to provide a CLA and decorate the PR appropriately (e.g., label,
comment). Simply follow the instructions provided by the bot. You will only
need to do this once across all repos using our CLA.

This project has adopted the
[Microsoft Open Source Code of Conduct][code_of_conduct]. For more information,
see the Code of Conduct FAQ or contact [opencode@microsoft.com][opencode_email] with any
additional questions or comments.

<!-- LINKS -->
[source_code]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/planetarycomputer/azure-planetarycomputer/azure/planetarycomputer
[pc_pypi]: https://pypi.org/project/azure-planetarycomputer/
[pc_ref_docs]: https://learn.microsoft.com/en-us/rest/api/planetarycomputer/
[pc_product_docs]: https://learn.microsoft.com/en-us/azure/planetary-computer/
[pc_samples]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/planetarycomputer/azure-planetarycomputer/samples

[azure_sub]: https://azure.microsoft.com/free/
[register_aad_app]: https://learn.microsoft.com/azure/cognitive-services/authentication#assign-a-role-to-a-service-principal

[azure_sdk_python_default_azure_credential]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#defaultazurecredential

[python_azure_core_exceptions]: https://aka.ms/azsdk/python/core/docs#module-azure.core.exceptions
[python_logging]: https://docs.python.org/3/library/logging.html
[sdk_logging_docs]: https://learn.microsoft.com/azure/developer/python/sdk/azure-sdk-logging
[azure_core_ref_docs]: https://aka.ms/azsdk/python/core/docs

[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[microsoft_cla]: https://cla.microsoft.com
[opencode_email]: mailto:opencode@microsoft.com
