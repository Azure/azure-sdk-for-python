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

- Python 3.10 or later is required to use this package.
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

#### Shared Access Signature Operations (`client.sas`)

- **Token Generation**: Generate SAS tokens with configurable duration for collections to enable secure access
- **Asset Signing**: Sign asset HREFs for secure downloads of managed storage assets using `get_url`
- **Token Revocation**: Revoke tokens when needed to control access, all secured via Microsoft Entra ID

## Examples

The following section provides several code snippets covering common GeoCatalog workflows. For complete working examples, see the [samples][pc_samples] directory.

- [List STAC collections](#list-stac-collections)
- [Search for STAC items](#search-for-stac-items)
- [Get STAC item details](#get-stac-item-details)
- [Create a STAC collection](#create-stac-collection)
- [Configure collection visualization](#configure-collection-visualization)
- [Register and render mosaic tiles](#register-and-render-mosaic-tiles)
- [Extract point values](#extract-point-values)
- [Generate map tiles](#generate-map-tiles)
- [Set up ingestion sources](#set-up-ingestion-sources)
- [Data ingestion management](#data-ingestion-management)
- [Generate SAS token for secure access](#generate-sas-token-for-secure-access)
- [Async operations](#async-operations)

### List STAC Collections

List all available STAC collections:

```python
from azure.planetarycomputer import PlanetaryComputerProClient
from azure.identity import DefaultAzureCredential

# Create client
endpoint = "https://your-endpoint.geocatalog.spatio.azure.com"
client = PlanetaryComputerProClient(endpoint=endpoint, credential=DefaultAzureCredential())

# List all collections
collections_response = client.stac.get_collections()

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

search_result = client.stac.search(body=search_params)
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
    StacCollectionTemporalExtent,
    StacExtensionExtent,
)
from azure.identity import DefaultAzureCredential

endpoint = "https://your-endpoint.geocatalog.spatio.azure.com"
client = PlanetaryComputerProClient(endpoint=endpoint, credential=DefaultAzureCredential())

# Define collection
collection = StacCollection(
    id="my-collection",
    description="A collection of geospatial data",
    license="proprietary",
    extent=StacExtensionExtent(
        spatial=StacExtensionSpatialExtent(bounding_box=[[-180.0, -90.0, 180.0, 90.0]]),
        temporal=StacCollectionTemporalExtent(interval=[[None, None]]),
    ),
    links=[],
    stac_version="1.0.0",
    type="Collection",
)

# Create the collection (long-running operation)
poller = client.stac.begin_create_collection(body=collection)
poller.result()  # Wait for completion

print(f"Created collection: {collection.id}")
```

### Configure Collection Visualization

Configure render options and tile settings to control how collection data is displayed:

```python
from azure.planetarycomputer import PlanetaryComputerProClient
from azure.planetarycomputer.models import RenderOption, TileSettings
from azure.identity import DefaultAzureCredential

endpoint = "https://your-endpoint.geocatalog.spatio.azure.com"
client = PlanetaryComputerProClient(endpoint=endpoint, credential=DefaultAzureCredential())

collection_id = "my-collection"

# Add a render option for visualizing data
render_option = RenderOption(
    id="true-color",
    name="True Color",
    type="raster-tile",
    options="assets=image&rescale=0,255",
)
client.stac.create_render_option(collection_id=collection_id, body=render_option)

# Configure tile settings
tile_settings = TileSettings(min_zoom=6, max_items_per_tile=10)
client.stac.replace_tile_settings(collection_id=collection_id, body=tile_settings)

# List all render options
for option in client.stac.get_render_options(collection_id=collection_id):
    print(f"Render option: {option.id} - {option.name}")
```

### Register and Render Mosaic Tiles

Register a STAC search as a mosaic and retrieve tiles from it:

```python
from azure.planetarycomputer import PlanetaryComputerProClient
from azure.identity import DefaultAzureCredential

endpoint = "https://your-endpoint.geocatalog.spatio.azure.com"
client = PlanetaryComputerProClient(endpoint=endpoint, credential=DefaultAzureCredential())

# Register a mosaic search
registration = client.data.register_mosaics_search(
    body={
        "collections": ["naip"],
        "filter-lang": "cql2-json",
        "filter": {
            "op": "=",
            "args": [{"property": "naip:year"}, "2021"]
        },
    }
)
print(f"Search ID: {registration.search_id}")

# Get TileJSON metadata for the registered mosaic
tile_json = client.data.get_search_tile_json(
    search_id=registration.search_id,
    tile_matrix_set_id="WebMercatorQuad",
    assets=["image"],
)
print(f"Tile URLs: {tile_json.tiles}")
print(f"Bounds: {tile_json.bounds}")
```

### Extract Point Values

Extract pixel values at a specific geographic coordinate:

```python
from azure.planetarycomputer import PlanetaryComputerProClient
from azure.identity import DefaultAzureCredential

endpoint = "https://your-endpoint.geocatalog.spatio.azure.com"
client = PlanetaryComputerProClient(endpoint=endpoint, credential=DefaultAzureCredential())

# Get pixel values at a coordinate for a specific item
point_data = client.data.get_item_point(
    collection_id="naip",
    item_id="ga_m_3308421_se_16_060_20211114",
    longitude=-84.41,
    latitude=33.65,
    assets=["image"],
)

print(f"Coordinates: {point_data.coordinates}")
print(f"Band names: {point_data.band_names}")
print(f"Values: {point_data.values_property}")
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
tile_response = client.data.get_tile(
    collection_id=collection_id,
    item_id=item_id,
    tile_matrix_set_id="WebMercatorQuad",
    z=14,  # Zoom level
    x=4322,  # Tile X coordinate
    y=6463,  # Tile Y coordinate
    assets=["image"],
    format="png",
)

# Save tile to file
with open("tile.png", "wb") as f:
    for chunk in tile_response:
        f.write(chunk)
```

### Set Up Ingestion Sources

Configure data sources for ingestion using Managed Identity or SAS token authentication:

```python
from azure.planetarycomputer import PlanetaryComputerProClient
from azure.planetarycomputer.models import (
    ManagedIdentityIngestionSource,
    ManagedIdentityConnection,
)
from azure.identity import DefaultAzureCredential

endpoint = "https://your-endpoint.geocatalog.spatio.azure.com"
client = PlanetaryComputerProClient(endpoint=endpoint, credential=DefaultAzureCredential())

# Create a Managed Identity ingestion source
source = ManagedIdentityIngestionSource(
    id="my-storage-source",
    connection_info=ManagedIdentityConnection(
        container_uri="https://mystorage.blob.core.windows.net/geospatial-data",
        object_id="00000000-0000-0000-0000-000000000000",
    ),
)
created_source = client.ingestion.create_source(body=source)
print(f"Created source: {created_source.id}")

# List available managed identities
for identity in client.ingestion.list_managed_identities():
    print(f"Identity: {identity.object_id} - {identity.resource_id}")

# List all configured sources
for src in client.ingestion.list_sources():
    print(f"Source: {src.id} ({src.kind})")
```

### Data Ingestion Management

Manage data ingestion operations:

```python
from azure.planetarycomputer import PlanetaryComputerProClient
from azure.planetarycomputer.models import IngestionDefinition, IngestionType
from azure.identity import DefaultAzureCredential

endpoint = "https://your-endpoint.geocatalog.spatio.azure.com"
client = PlanetaryComputerProClient(endpoint=endpoint, credential=DefaultAzureCredential())

# Create an ingestion definition
ingestion = IngestionDefinition(
    id="my-ingestion-001",
    import_type=IngestionType.STATIC_CATALOG,
    display_name="My data ingestion",
    source_catalog_url="https://example.com/catalog.json",
)

created = client.ingestion.create(
    collection_id="my-collection",
    body=ingestion,
)

print(f"Created ingestion: {created.id}")
print(f"Status: {created.status}")

# List all ingestions for a collection
ingestions = client.ingestion.list(collection_id="my-collection")
for ing in ingestions:
    print(f"Ingestion: {ing.id} - Status: {ing.status}")
```

### Generate SAS Token for Secure Access

Generate Shared Access Signatures for secure data access:

```python
from azure.planetarycomputer import PlanetaryComputerProClient
from azure.identity import DefaultAzureCredential

endpoint = "https://your-endpoint.geocatalog.spatio.azure.com"
client = PlanetaryComputerProClient(endpoint=endpoint, credential=DefaultAzureCredential())

# Generate a SAS token for a collection (valid for 60 minutes)
token_response = client.sas.get_token(
    collection_id="naip",
    duration_in_minutes=60,
)

print(f"SAS Token: {token_response.token}")
print(f"Expiry: {token_response.expires_on}")

# Sign an asset HREF for secure download
signed = client.sas.get_url(
    href="https://storage.blob.core.windows.net/container/path/to/asset.tif",
    duration_in_minutes=60,
)

print(f"Signed URL: {signed.href}")
```

### Async Operations

All operations are also available as async. Use `aio` for the async client:

```python
import asyncio
from azure.planetarycomputer.aio import PlanetaryComputerProClient
from azure.identity.aio import DefaultAzureCredential

async def main():
    endpoint = "https://your-endpoint.geocatalog.spatio.azure.com"
    credential = DefaultAzureCredential()

    async with PlanetaryComputerProClient(endpoint=endpoint, credential=credential) as client:
        # List collections
        collections_response = await client.stac.get_collections()
        for collection in collections_response.collections:
            print(f"Collection: {collection.id}")

        # Get a specific item
        item = await client.stac.get_item(
            collection_id="naip",
            item_id="ga_m_3308421_se_16_060_20211114",
        )
        print(f"Item: {item.id}")

    await credential.close()

asyncio.run(main())
```

## Troubleshooting

### General

Planetary Computer client library will raise exceptions defined in [Azure Core][python_azure_core_exceptions].

```python
from azure.core.exceptions import HttpResponseError
from azure.planetarycomputer import PlanetaryComputerProClient
from azure.identity import DefaultAzureCredential

client = PlanetaryComputerProClient(
    endpoint="https://your-endpoint.geocatalog.spatio.azure.com",
    credential=DefaultAzureCredential(),
)

try:
    client.stac.get_collection(collection_id="non-existent-collection")
except HttpResponseError as e:
    print(f"Status code: {e.status_code}")
    print(f"Reason: {e.reason}")
    print(f"Message: {e.message}")
```

### Logging

This library uses the standard [logging][python_logging] library for logging.
Basic information about HTTP sessions (URLs, headers, etc.) is logged at `INFO` level.

Detailed `DEBUG` level logging, including request/response bodies and **unredacted**
headers, can be enabled on the client or per-operation with the `logging_enable` keyword argument.

```python
import sys
import logging

from azure.planetarycomputer import PlanetaryComputerProClient
from azure.identity import DefaultAzureCredential

# Enable DEBUG logging for all SDK calls
logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

client = PlanetaryComputerProClient(
    endpoint="https://your-endpoint.geocatalog.spatio.azure.com",
    credential=DefaultAzureCredential(),
)

# Or enable logging for a single operation
item = client.stac.get_item(
    collection_id="naip",
    item_id="ga_m_3308421_se_16_060_20211114",
    logging_enable=True,
)
```

See full SDK logging documentation in the [Azure SDK documentation][sdk_logging_docs].

### Optional Configuration

Optional keyword arguments can be passed in at the client and per-operation level.
The azure-core [reference documentation][azure_core_ref_docs] describes available configurations for retries, logging, transport protocols, and more.

## Next steps

### More sample code

For complete working examples, see the individual sample files:

| Scenario | Sync | Async |
|---|---|---|
| STAC Collection Management | [sample][sample_00] | [async sample][sample_00_async] |
| Ingestion Management | [sample][sample_01] | [async sample][sample_01_async] |
| STAC Specification (Items, Search) | [sample][sample_02] | [async sample][sample_02_async] |
| Shared Access Signatures | [sample][sample_03] | [async sample][sample_03_async] |
| STAC Item Tiler | [sample][sample_04] | [async sample][sample_04_async] |
| Mosaics Tiler | [sample][sample_05] | [async sample][sample_05_async] |
| Map Legends | [sample][sample_06] | [async sample][sample_06_async] |

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

[sample_00]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/planetarycomputer/azure-planetarycomputer/samples/planetary_computer_00_stac_collection.py
[sample_00_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/planetarycomputer/azure-planetarycomputer/samples/async/planetary_computer_00_stac_collection_async.py
[sample_01]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/planetarycomputer/azure-planetarycomputer/samples/planetary_computer_01_ingestion_management.py
[sample_01_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/planetarycomputer/azure-planetarycomputer/samples/async/planetary_computer_01_ingestion_management_async.py
[sample_02]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/planetarycomputer/azure-planetarycomputer/samples/planetary_computer_02_stac_specification.py
[sample_02_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/planetarycomputer/azure-planetarycomputer/samples/async/planetary_computer_02_stac_specification_async.py
[sample_03]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/planetarycomputer/azure-planetarycomputer/samples/planetary_computer_03_shared_access_signature.py
[sample_03_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/planetarycomputer/azure-planetarycomputer/samples/async/planetary_computer_03_shared_access_signature_async.py
[sample_04]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/planetarycomputer/azure-planetarycomputer/samples/planetary_computer_04_stac_item_tiler.py
[sample_04_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/planetarycomputer/azure-planetarycomputer/samples/async/planetary_computer_04_stac_item_tiler_async.py
[sample_05]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/planetarycomputer/azure-planetarycomputer/samples/planetary_computer_05_mosaics_tiler.py
[sample_05_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/planetarycomputer/azure-planetarycomputer/samples/async/planetary_computer_05_mosaics_tiler_async.py
[sample_06]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/planetarycomputer/azure-planetarycomputer/samples/planetary_computer_06_map_legends.py
[sample_06_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/planetarycomputer/azure-planetarycomputer/samples/async/planetary_computer_06_map_legends_async.py

[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[microsoft_cla]: https://cla.microsoft.com
[opencode_email]: mailto:opencode@microsoft.com
