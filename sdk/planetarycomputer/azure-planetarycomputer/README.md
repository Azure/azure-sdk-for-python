# Azure Planetary Computer client library for Python

The Azure Planetary Computer client library provides programmatic access to Microsoft Planetary Computer Pro, a geospatial data management service built on Azure's hyperscale infrastructure. Microsoft Planetary Computer Pro empowers organizations to unlock the full potential of geospatial data by providing foundational capabilities to ingest, manage, search, and distribute geospatial datasets using the SpatioTemporal Asset Catalog (STAC) open specification.

This client library enables developers to interact with GeoCatalog resources, supporting workflows from gigabytes to tens of petabytes of geospatial data.

## Key capabilities

- **STAC Collection Management**: Create, read, update, and delete STAC collections and items to organize your geospatial datasets
- **Collection Configuration**: Configure render options, mosaics, tile settings, and queryables to optimize query performance and visualization
- **Data Visualization**: Generate map tiles (XYZ, TileJSON, WMTS), preview images, crop by GeoJSON or bounding box, extract point values, compute statistics for regions, and access tile matrix sets and asset metadata
- **Mosaic Operations**: Register STAC search-based mosaics for pixel-wise data query and retrieval, generate tiles from multiple items, get TileJSON and WMTS capabilities, and query mosaic assets for points and tiles
- **Map Legends**: Retrieve class map legends (categorical) and interval legends (continuous) as JSON or PNG images with predefined color maps
- **Data Ingestion**: Set up ingestion sources (Managed Identity or SAS token), define ingestions from STAC catalogs, create and monitor ingestion runs with detailed operation tracking for automated catalog ingestion
- **STAC API Operations**: Use the managed STAC API for full CRUD operations on items, search with spatial/temporal filters and sorting, retrieve queryable properties, check API conformance classes, and access landing page information
- **Secure Access**: Generate SAS tokens with configurable duration for collections, sign asset HREFs for secure downloads of managed storage assets, and revoke tokens when needed—all secured via Microsoft Entra ID

[Source code][source_code]
| [Package (PyPI)][pc_pypi]
| [API reference documentation][pc_ref_docs]
| [Product documentation][pc_product_docs]

## Getting started

### Prerequisites

- Python 3.9 or later is required to use this package.
- You need an [Azure subscription][azure_sub] to use this package.
- A deployed Microsoft Planetary Computer Pro GeoCatalog resource in your Azure subscription.

### Install the package

```bash
python -m pip install azure-planetarycomputer
```

### Authenticate the client

To interact with your GeoCatalog resource, create an instance of the client with your GeoCatalog endpoint and credentials.

Microsoft Entra ID authentication is required to ensure secure, unified enterprise identity and access management for your geospatial data.

#### Create the client with Microsoft Entra ID credential

To use the [DefaultAzureCredential][azure_sdk_python_default_azure_credential] type shown below, or other credential types provided with the Azure SDK, please install the `azure-identity` package:

```bash
pip install azure-identity
```

You will also need to [register a new Microsoft Entra ID application and grant access][register_aad_app] to your GeoCatalog by assigning the appropriate role to your service principal.

Once completed, set the values of the client ID, tenant ID, and client secret of the Microsoft Entra ID application as environment variables:
`AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_CLIENT_SECRET`.

```python
"""DefaultAzureCredential will use the values from these environment
variables: AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET
"""
from azure.planetarycomputer import PlanetaryComputerProClient
from azure.identity import DefaultAzureCredential

endpoint = "https://your-endpoint.geocatalog.spatio.azure.com"
credential = DefaultAzureCredential()
client = PlanetaryComputerProClient(endpoint=endpoint, credential=credential)
```

## Key concepts

### PlanetaryComputerProClient

`PlanetaryComputerProClient` provides operations for interacting with Microsoft Planetary Computer Pro GeoCatalog resources through these main operation groups:

#### STAC Operations (`client.stac`)

- **Collection Management**: Create, update, list, and delete STAC collections to organize your geospatial datasets
- **Item Management**: Create, read, update, and delete individual STAC items within collections
- **Search API**: Search for items using spatial and temporal filters, sorting, and queryable properties through the managed STAC API
- **API Conformance**: Retrieve STAC API conformance classes and landing page information

#### Data Operations (`client.data`)

- **Tile Generation**: Generate map tiles (XYZ, TileJSON, WMTS) from collections, items, and mosaics using the powerful mosaic and tiling API
- **Data Visualization**: Create preview images, crop by GeoJSON or bounding box, extract point values, and compute statistics for regions
- **Asset Metadata**: Retrieve tile matrix sets and asset metadata for collections and items
- **Map Legends**: Retrieve class map legends (categorical) and interval legends (continuous) as JSON or PNG images with predefined color maps

#### Ingestion Operations (`client.ingestion`)

- **Ingestion Sources**: Set up ingestion sources using Managed Identity or SAS token authentication
- **Ingestion Definitions**: Define automated STAC catalog ingestion from public and private data sources
- **Ingestion Runs**: Create and monitor ingestion runs with detailed operation tracking
- **Partition Configuration**: Configure how data is partitioned and processed during ingestion

#### Shared Access Signature Operations (`client.shared_access_signature`)

- **Token Generation**: Generate SAS tokens with configurable duration for collections to enable secure access
- **Asset Signing**: Sign asset HREFs for secure downloads of managed storage assets
- **Token Revocation**: Revoke tokens when needed to control access, all secured via Microsoft Entra ID

## Examples

The following section provides several code snippets covering common GeoCatalog workflows. For complete working examples, see the [samples][pc_samples] directory.

### List STAC Collections

List all available STAC collections:

```python
from azure.planetarycomputer import PlanetaryComputerProClient
from azure.identity import DefaultAzureCredential

# Create client
endpoint = "https://your-endpoint.geocatalog.spatio.azure.com"
client = PlanetaryComputerProClient(endpoint=endpoint, credential=DefaultAzureCredential())

# List all collections
collections_response = client.stac.list_collections()

for collection in collections_response.collections:
    print(f"Collection: {collection.id}")
    print(f"  Title: {collection.title}")
    print(f"  Description: {collection.description[:100]}...")
```

### Search for STAC Items

Search for geospatial data items with spatial and temporal filters:

```python
from azure.planetarycomputer import PlanetaryComputerProClient
from azure.planetarycomputer.models import StacSearchParameters, FilterLanguage
from azure.identity import DefaultAzureCredential

endpoint = "https://your-endpoint.geocatalog.spatio.azure.com"
client = PlanetaryComputerProClient(endpoint=endpoint, credential=DefaultAzureCredential())

# Search with spatial filter
search_params = StacSearchParameters(
    collections=["naip"],
    filter_lang=FilterLanguage.CQL2_JSON,
    filter={
        "op": "s_intersects",
        "args": [
            {"property": "geometry"},
            {
                "type": "Polygon",
                "coordinates": [[
                    [-84.39, 33.76],
                    [-84.37, 33.76],
                    [-84.37, 33.78],
                    [-84.39, 33.78],
                    [-84.39, 33.76]
                ]]
            }
        ]
    },
    limit=10
)

search_result = client.stac.search_items(body=search_params)
print(f"Found {len(search_result.features)} items")
```

### Get STAC Item Details

Retrieve detailed information about a specific STAC item:

```python
from azure.planetarycomputer import PlanetaryComputerProClient
from azure.identity import DefaultAzureCredential

endpoint = "https://your-endpoint.geocatalog.spatio.azure.com"
client = PlanetaryComputerProClient(endpoint=endpoint, credential=DefaultAzureCredential())

# Get a specific STAC item
item = client.stac.get_item(
    collection_id="naip",
    item_id="ga_m_3308421_se_16_060_20211114"
)

print(f"Item ID: {item.id}")
print(f"Geometry type: {item.geometry.type}")
print(f"Assets: {list(item.assets.keys())}")
```

### Create STAC Collection

Create a new STAC collection for organizing geospatial data:

```python
from azure.planetarycomputer import PlanetaryComputerProClient
from azure.planetarycomputer.models import (
    StacCollection,
    StacExtensionSpatialExtent,
    StacExtensionTemporalExtent,
    StacExtent
)
from azure.identity import DefaultAzureCredential

endpoint = "https://your-endpoint.geocatalog.spatio.azure.com"
client = PlanetaryComputerProClient(endpoint=endpoint, credential=DefaultAzureCredential())

# Define collection with proper extent
spatial_extent = StacExtensionSpatialExtent(bbox=[[-180.0, -90.0, 180.0, 90.0]])
temporal_extent = StacExtensionTemporalExtent(interval=[["2023-01-01T00:00:00Z", None]])

collection = StacCollection(
    id="my-collection",
    type="Collection",
    stac_version="1.0.0",
    description="A collection of geospatial data",
    license="proprietary",
    extent=StacExtent(
        spatial=spatial_extent,
        temporal=temporal_extent
    ),
    links=[]
)

# Create the collection
created_collection = client.stac.create_or_update_collection(
    collection_id="my-collection",
    body=collection
)

print(f"Created collection: {created_collection.id}")
```

### Generate Map Tiles

Generate map tiles from geospatial data:

```python
from azure.planetarycomputer import PlanetaryComputerProClient
from azure.identity import DefaultAzureCredential

endpoint = "https://your-endpoint.geocatalog.spatio.azure.com"
client = PlanetaryComputerProClient(endpoint=endpoint, credential=DefaultAzureCredential())

collection_id = "naip"
item_id = "ga_m_3308421_se_16_060_20211114"

# Get a specific tile for the item
tile_response = client.data.get_item_tile(
    collection_id=collection_id,
    item_id=item_id,
    tile_matrix_set_id="WebMercatorQuad",
    z=14,  # Zoom level
    x=4322,  # Tile X coordinate
    y=6463,  # Tile Y coordinate
    assets=["image"]
)

# Save tile to file
with open("tile.png", "wb") as f:
    for chunk in tile_response:
        f.write(chunk)
```

### Data Ingestion Management

Manage data ingestion operations:

```python
from azure.planetarycomputer import PlanetaryComputerProClient
from azure.planetarycomputer.models import IngestionJob, PartitionType
from azure.identity import DefaultAzureCredential

endpoint = "https://your-endpoint.geocatalog.spatio.azure.com"
client = PlanetaryComputerProClient(endpoint=endpoint, credential=DefaultAzureCredential())

# Create an ingestion job
ingestion_job = IngestionJob(
    collection_id="my-collection",
    partition_type=PartitionType.YEAR_MONTH,
    description="Ingestion job for geospatial data"
)

created_job = client.ingestion.create_or_update_job(
    job_id="ingestion-job-001",
    body=ingestion_job
)

print(f"Created job: {created_job.id}")
print(f"Status: {created_job.status}")

# List all ingestion jobs
jobs = client.ingestion.list_jobs()
for job in jobs.value:
    print(f"Job: {job.id} - Status: {job.status}")
```

### Generate SAS Token for Secure Access

Generate Shared Access Signatures for secure data access:

```python
from azure.planetarycomputer import PlanetaryComputerProClient
from azure.planetarycomputer.models import SignedUrlRequest, AccessPermission
from azure.identity import DefaultAzureCredential
from datetime import datetime, timedelta

endpoint = "https://your-endpoint.geocatalog.spatio.azure.com"
client = PlanetaryComputerProClient(endpoint=endpoint, credential=DefaultAzureCredential())

# Generate a SAS token for a collection
sas_request = SignedUrlRequest(
    permissions=[AccessPermission.READ],
    expires_on=datetime.utcnow() + timedelta(hours=1)
)

sas_response = client.shared_access_signature.generate_collection_signed_url(
    collection_id="naip",
    body=sas_request
)

print(f"SAS URL: {sas_response.url}")
print(f"Expires on: {sas_response.expires_on}")
```

### Troubleshooting

### General

Planetary Computer client library will raise exceptions defined in [Azure Core][python_azure_core_exceptions].
Error codes and messages raised by the GeoCatalog service can be found in the service documentation.

### Logging

This library uses the standard [logging][python_logging] library for logging.

Basic information about HTTP sessions (URLs, headers, etc.) is logged at `INFO` level.

Detailed `DEBUG` level logging, including request/response bodies and **unredacted**
headers, can be enabled on the client or per-operation with the `logging_enable` keyword argument.

See full SDK logging documentation with examples in the [Azure SDK documentation][sdk_logging_docs].

```python
import sys
import logging

from azure.planetarycomputer import PlanetaryComputerProClient
from azure.identity import DefaultAzureCredential

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    stream=sys.stdout)

endpoint = "https://your-endpoint.geocatalog.spatio.azure.com"
credential = DefaultAzureCredential()
client = PlanetaryComputerProClient(endpoint=endpoint, credential=credential)

# Enable logging for a specific operation
item = client.stac.get_item(
    collection_id="naip",
    item_id="ga_m_3308421_se_16_060_20211114",
    logging_enable=True
)
```

### Optional Configuration

Optional keyword arguments can be passed in at the client and per-operation level.
The azure-core [reference documentation][azure_core_ref_docs] describes available configurations for retries, logging, transport protocols, and more.

## Next steps

### More sample code

See the `samples` directory for several code snippets illustrating common patterns for working with GeoCatalog resources.

### Additional documentation

For more extensive documentation on Microsoft Planetary Computer Pro, see the [Planetary Computer documentation][pc_product_docs] on Microsoft Learn.

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
[pc_ref_docs]: https://learn.microsoft.com/rest/api/planetarycomputer/
[pc_product_docs]: https://learn.microsoft.com/azure/planetary-computer/
[pc_samples]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/planetarycomputer/azure-planetarycomputer/samples

[azure_sub]: https://azure.microsoft.com
[register_aad_app]: https://learn.microsoft.com/azure/cognitive-services/authentication#assign-a-role-to-a-service-principal

[azure_sdk_python_default_azure_credential]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#defaultazurecredential

[python_azure_core_exceptions]: https://aka.ms/azsdk/python/core/docs#module-azure.core.exceptions
[python_logging]: https://docs.python.org/3/library/logging.html
[sdk_logging_docs]: https://learn.microsoft.com/azure/developer/python/sdk/azure-sdk-logging
[azure_core_ref_docs]: https://aka.ms/azsdk/python/core/docs

[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[microsoft_cla]: https://cla.microsoft.com
[opencode_email]: mailto:opencode@microsoft.com
