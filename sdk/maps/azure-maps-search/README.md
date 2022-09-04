# Azure Maps Search Package client library for Python

This package contains a Python SDK for Azure Maps Services for Search.
Read more about Azure Maps Services [here](https://docs.microsoft.com/azure/azure-maps/)

[Source code](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/maps/azure-maps-search) | [API reference documentation](https://docs.microsoft.com/rest/api/maps/search) | [Product documentation](https://docs.microsoft.com/azure/azure-maps/)

## _Disclaimer_

_Azure SDK Python packages support for Python 2.7 has ended 01 January 2022. For more information and questions, please refer to <https://github.com/Azure/azure-sdk-for-python/issues/20691>_

## Getting started

### Prerequisites

- Python 3.6 or later is required to use this package.
- An [Azure subscription][azure_subscription] and an [Azure Maps account](https://docs.microsoft.com/azure/azure-maps/how-to-manage-account-keys).
- A deployed Maps Services resource. You can create the resource via [Azure Portal][azure_portal] or [Azure CLI][azure_cli].

If you use Azure CLI, replace `<resource-group-name>` and `<account-name>` of your choice, and select a proper [pricing tier](https://docs.microsoft.com/azure/azure-maps/choose-pricing-tier) based on your needs via the `<sku-name>` parameter. Please refer to [this page](https://docs.microsoft.com/cli/azure/maps/account?view=azure-cli-latest#az_maps_account_create) for more details.

```bash
az maps account create --resource-group <resource-group-name> --account-name <account-name> --sku <sku-name>
```

### Install the package

Install the Azure Maps Service Search SDK.

```bash
pip install azure-maps-search
```

### Create and Authenticate the MapsSearchClient

To create a client object to access the Azure Maps Search API, you will need a **credential** object. Azure Maps Search client also support two ways to authenticate.

#### 1. Authenticate with a Subscription Key Credential

You can authenticate with your Azure Maps Subscription Key.
Once the Azure Maps Subscription Key is created, set the value of the key as environment variable: `AZURE_SUBSCRIPTION_KEY`.
Then pass an `AZURE_SUBSCRIPTION_KEY` as the `credential` parameter into an instance of [AzureKeyCredential][azure-key-credential].

```python
from azure.core.credentials import AzureKeyCredential
from azure.maps.search import MapsSearchClient

credential = AzureKeyCredential(os.environ.get("AZURE_SUBSCRIPTION_KEY"))

search_client = MapsSearchClient(
    credential=credential,
)
```

#### 2. Authenticate with an Azure Active Directory credential

You can authenticate with [Azure Active Directory (AAD) token credential][maps_authentication_aad] using the [Azure Identity library][azure_identity].
Authentication by using AAD requires some initial setup:

- Install [azure-identity][azure-key-credential]
- Register a [new AAD application][register_aad_app]
- Grant access to Azure Maps by assigning the suitable role to your service principal. Please refer to the [Manage authentication page][manage_aad_auth_page].

After setup, you can choose which type of [credential][azure-key-credential] from `azure.identity` to use.
As an example, [DefaultAzureCredential][default_azure_credential]
can be used to authenticate the client:

Next, set the values of the client ID, tenant ID, and client secret of the AAD application as environment variables:
`AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_CLIENT_SECRET`

You will also need to specify the Azure Maps resource you intend to use by specifying the `clientId` in the client options. The Azure Maps resource client id can be found in the Authentication sections in the Azure Maps resource. Please refer to the [documentation][how_to_manage_authentication] on how to find it.

```python
from azure.maps.search import MapsSearchClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
search_client = MapsSearchClient(credential=credential)
```

## Key concepts

The Azure Maps Search client library for Python allows you to interact with each of the components through the use of a dedicated client object.

### Sync Clients

`MapsSearchClient` is the primary client for developers using the Azure Maps Search client library for Python.
Once you initialized a `MapsSearchClient` class, you can explore the methods on this client object to understand the different features of the Azure Maps Search service that you can access.

### Async Clients

This library includes a complete async API supported on Python 3.5+. To use it, you must first install an async transport, such as [aiohttp](https://pypi.org/project/aiohttp/).
See [azure-core documentation](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#transport) for more information.

Async clients and credentials should be closed when they're no longer needed. These
objects are async context managers and define async `close` methods.

## Examples

The following sections provide several code snippets covering some of the most common Azure Maps Search tasks, including:

- [Request latitude and longitude coordinates for an address](#request-latitude-and-longitude-coordinates-for-an-address)

- [Search for an address or Point of Interest](#search-for-an-address-or-point-of-interest)

- [Make a Reverse Address Search to translate coordinate location to street address](#make-a-reverse-address-search-to-translate-coordinate-location-to-street-address)
- [Translate coordinate location into a human understandable cross street](#translate-coordinate-location-into-a-human-understandable-cross-street)
- [Get async fuzzy search batch with param and batchid](#get-async-fuzzy-search-batch-with-param-and-batchid)
- [Fail to get fuzzy search batch sync](#fail-to-get-fuzzy-search-batch-sync)
- [Search inside Geometry](#search-inside-geometry)

- [Working with exist library for Search](#working-with-exist-library-for-search)

### Request latitude and longitude coordinates for an address

You can use an authenticated client to convert an address into latitude and longitude coordinates. This process is also called geocoding. In addition to returning the coordinates, the response will also return detailed address properties such as street, postal code, municipality, and country/region information.

```python
from azure.maps.search import MapsSearchClient

search_result = client.search_address("400 Broad, Seattle");
```

### Search for an address or Point of Interest

You can use Fuzzy Search to search an address or a point of interest (POI). The following examples demostrate how to search for `pizza` over the scope of a specific country (`France`, in this example).

```python
from azure.maps.search import MapsSearchClient

fuzzy_search_result = client.fuzzy_search(query: "pizza", country_filter: "fr" );

result_address = fuzzy_search_result.results[0].address
```

### Make a Reverse Address Search to translate coordinate location to street address

You can translate coordinates into human readable street addresses. This process is also called reverse geocoding.
This is often used for applications that consume GPS feeds and want to discover addresses at specific coordinate points.

```python
from azure.maps.search import MapsSearchClient

coordinates=(47.60323, -122.33028)

reverse_search_result = client.reverse_search_address(coordinates=coordinates);

result_summary = reverse_search_result.summary
```

### Translate coordinate location into a human understandable cross street

Translate coordinate location into a human understandable cross street by using Search Address Reverse Cross Street API. Most often, this is needed in tracking applications that receive a GPS feed from a device or asset, and wish to know where the coordinate is located.

```python
from azure.maps.search import MapsSearchClient

coordinates=(47.60323, -122.33028)

reverse_search_result = client.reverse_search_cross_street_address(coordinates=coordinates);

result_address = reverse_search_result.results[0].address
```

### Get async fuzzy search batch with param and batchid

This sample demonstrates how to perform fuzzy search by location and lat/lon with async batch method. This function is accepting both `search_queries` and `batch_id` and returning an `AsyncLRO` object. The `batch_id` here can be use to retrieve the LRO object later which last 14 days.

```python
maps_search_client = MapsSearchClient(credential=AzureKeyCredential(subscription_key))

async with maps_search_client:
    result = await maps_search_client.begin_fuzzy_search_batch(
        search_queries=[
            "350 5th Ave, New York, NY 10118&limit=1",
            "400 Broad St, Seattle, WA 98109&limit=6"
        ]
    )

batch_id = result.batch_id
```

The method `begin_fuzzy_search_batch()` also accepts `batch_id` as the parameter. The `batch_id` here can be use to retrieve the LRO object later which last 14 days.

```python
maps_search_client = MapsSearchClient(credential=AzureKeyCredential(subscription_key))

async with maps_search_client:
    result = await maps_search_client.begin_fuzzy_search_batch(
        batch_id=batch_id
    )

result = result.response
```

### Fail to get fuzzy search batch sync

This sample demonstrates how to check if there are failures in search of fuzzy_search_batch.

```python
maps_search_client = MapsSearchClient(credential=AzureKeyCredential(subscription_key))

result = maps_search_client.fuzzy_search_batch(
    search_queries=[
        "350 5th Ave, New York, NY 10118&limit=1",
        "400 Broad St, Seattle, WA 98109&lim"
    ]
)
for item in result.items:
    count = 0
    if item.response.error is not None:
        count = count+1
        print(f"Error: {item.response.error.message}")
print(f"There are total of {count} search queries failed.")
```

### Search inside Geometry

This sample demonstrates how to perform search inside geometry by given target such as `pizza` and multiple different geometry as input with GeoJson object.

```python
maps_search_client = MapsSearchClient(credential=AzureKeyCredential(subscription_key))

geo_json_obj1 = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [-122.143035,47.653536],
                    [-122.187164,47.617556],
                    [-122.114981,47.570599],
                    [-122.132756,47.654009],
                    [-122.143035,47.653536]
                    ]]
            },
            "properties": {}
        },
        {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [-122.126986,47.639754]
            },
            "properties": {
                "subType": "Circle",
                "radius": 100
            }
        }
    ]
}
result1 = maps_search_client.search_inside_geometry(
    query="pizza",
    geometry=geo_json_obj1
)
print("Search inside geometry with standard GeoJson object as input, FeatureCollection:")
print(result1)
```

### Working with exist library for Search

This sample demonstrates how to working with other existing packages such as `shapely` to perform search inside geometry by given target such as `pizza`.

```python
maps_search_client = MapsSearchClient(credential=AzureKeyCredential(subscription_key))

from shapely.geometry import Polygon

geo_interface_obj = Polygon([
    [-122.43576049804686, 37.7524152343544],
    [-122.43301391601562, 37.70660472542312],
    [-122.36434936523438, 37.712059855877314],
    [-122.43576049804686, 37.7524152343544]
])

result3 = maps_search_client.search_inside_geometry(
    query="pizza",
    geometry=geo_interface_obj
)
print("Search inside geometry with Polygon from third party library `shapely` with geo_interface as result 3:")
print(result2)
```

## Troubleshooting

### General

Maps Search clients raise exceptions defined in [Azure Core](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/README.md).

This list can be used for reference to catch thrown exceptions. To get the specific error code of the exception, use the `error_code` attribute, i.e, `exception.error_code`.

### Logging

This library uses the standard [logging](https://docs.python.org/3/library/logging.html) library for logging.
Basic information about HTTP sessions (URLs, headers, etc.) is logged at INFO level.

Detailed DEBUG level logging, including request/response bodies and unredacted headers, can be enabled on a client with the `logging_enable` argument:

```python
import sys
import logging
from azure.maps.search import MapsSearchClient

# Create a logger for the 'azure.maps.search' SDK
logger = logging.getLogger('azure.maps.search')
logger.setLevel(logging.DEBUG)

# Configure a console output
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

```

Similarly, `logging_enable` can enable detailed logging for a single operation,
even when it isn't enabled for the client:

```python
service_client.get_service_stats(logging_enable=True)
```

### Additional

Still running into issues? If you encounter any bugs or have suggestions, please file an issue in the [Issues](<https://github.com/Azure/azure-sdk-for-python/issues>) section of the project.

## Next steps

### More sample code

Get started with our [Maps Search samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/maps/azure-maps-search/samples) ([Async Version samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/maps/azure-maps-search/samples/async_samples)).

Several Azure Maps Search Python SDK samples are available to you in the SDK's GitHub repository. These samples provide example code for additional scenarios commonly encountered while working with Maps Search

```bash
set AZURE_SUBSCRIPTION_KEY="<RealSubscriptionKey>"

pip install azure-maps-search --pre

python samples/sample_authentication.py
python sample/sample_fuzzy_search.py
python samples/sample_get_point_of_interest_categories.py
python samples/sample_reverse_search_address.py
python samples/sample_reverse_search_cross_street_address.py
python samples/sample_search_nearby_point_of_interest.py
python samples/sample_search_point_of_interest_category.py
python samples/sample_search_point_of_interest.py
python samples/sample_search_structured_address.py
```

> Notes: `--pre` flag can be optionally added, it is to include pre-release and development versions for `pip install`. By default, `pip` only finds stable versions.

Further detail please refer to [Samples Introduction](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/maps/azure-maps-search/samples/README.md)

### Additional documentation

For more extensive documentation on Azure Maps Search, see the [Azure Maps Search documentation](https://docs.microsoft.com/rest/api/maps/search) on docs.microsoft.com.

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit <https://cla.microsoft.com>.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

<!-- LINKS -->
[azure_subscription]: https://azure.microsoft.com/free/
[azure_identity]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/identity/azure-identity
[azure_portal]: https://portal.azure.com
[azure_cli]: https://docs.microsoft.com/cli/azure
[azure-key-credential]: https://aka.ms/azsdk/python/core/azurekeycredential
[default_azure_credential]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#defaultazurecredential
[register_aad_app]: https://docs.microsoft.com/powershell/module/Az.Resources/New-AzADApplication?view=azps-8.0.0
[maps_authentication_aad]: https://docs.microsoft.com/azure/azure-maps/how-to-manage-authentication
[create_new_application_registration]: https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps/applicationsListBlade/quickStartType/AspNetWebAppQuickstartPage/sourceType/docs
[manage_aad_auth_page]: https://docs.microsoft.com/azure/azure-maps/how-to-manage-authentication
[how_to_manage_authentication]: https://docs.microsoft.com/azure/azure-maps/how-to-manage-authentication#view-authentication-details
