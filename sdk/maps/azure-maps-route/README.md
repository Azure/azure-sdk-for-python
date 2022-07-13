# Azure Maps Route Package client library for Python

This package contains a Python SDK for Azure Maps Services for Route.
Read more about Azure Maps Services [here](https://docs.microsoft.com/azure/azure-maps/)

[Source code](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/maps/azure-maps-route) | [API reference documentation](https://docs.microsoft.com/rest/api/maps/route) | [Product documentation](https://docs.microsoft.com/azure/azure-maps/)

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

Install the Azure Maps Service Route SDK.

```bash
pip install azure-maps-route
```

### Create and Authenticate the MapsRouteClient

To create a client object to access the Azure Maps Route API, you will need a **credential** object. Azure Maps Route client also support two ways to authenticate.

#### 1. Authenticate with a Subscription Key Credential

You can authenticate with your Azure Maps Subscription Key.
Once the Azure Maps Subscription Key is created, set the value of the key as environment variable: `AZURE_SUBSCRIPTION_KEY`.
Then pass an `AZURE_SUBSCRIPTION_KEY` as the `credential` parameter into an instance of [AzureKeyCredential][azure-key-credential].

```python
from azure.core.credentials import AzureKeyCredential
from azure.maps.route import MapsRouteClient

credential = AzureKeyCredential(os.environ.get("AZURE_SUBSCRIPTION_KEY"))

route_client = MapsRouteClient(
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
from azure.maps.route import MapsRouteClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
route_client = MapsRouteClient(credential=credential)
```

## Key concepts

The Azure Maps Route client library for Python allows you to interact with each of the components through the use of a dedicated client object.

### Sync Clients

`MapsRouteClient` is the primary client for developers using the Azure Maps Route client library for Python.
Once you initialized a `MapsRouteClient` class, you can explore the methods on this client object to understand the different features of the Azure Maps Route service that you can access.

### Async Clients

This library includes a complete async API supported on Python 3.5+. To use it, you must first install an async transport, such as [aiohttp](https://pypi.org/project/aiohttp/).
See [azure-core documentation](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#transport) for more information.

Async clients and credentials should be closed when they're no longer needed. These
objects are async context managers and define async `close` methods.

## Examples

The following sections provide several code snippets covering some of the most common Azure Maps Route tasks, including:

<!-- - [Request latitude and longitude coordinates for an address](#request-latitude-and-longitude-coordinates-for-an-address)

- [Route for an address or Point of Interest](#route-for-an-address-or-point-of-interest)

- [Make a Reverse Address Route to translate coordinate location to street address](#make-a-reverse-address-route-to-translate-coordinate-location-to-street-address)
- [Translate coordinate location into a human understandable cross street](#translate-coordinate-location-into-a-human-understandable-cross-street) -->

<!-- ### Request latitude and longitude coordinates for an address

You can use an authenticated client to convert an address into latitude and longitude coordinates. This process is also called geocoding. In addition to returning the coordinates, the response will also return detailed address properties such as street, postal code, municipality, and country/region information.

```python
from azure.maps.route import MapsRouteClient

route_result = client.route_address("400 Broad, Seattle");
```

### Route for an address or Point of Interest

You can use Fuzzy Route to route an address or a point of interest (POI). The following examples demostrate how to route for `pizza` over the scope of a specific country (`France`, in this example).

```python
from azure.maps.route import MapsRouteClient

fuzzy_route_result = client.fuzzy_route({ query: "pizza", country_filter: "fr" });
```

### Make a Reverse Address Route to translate coordinate location to street address

You can translate coordinates into human readable street addresses. This process is also called reverse geocoding.
This is often used for applications that consume GPS feeds and want to discover addresses at specific coordinate points.

```python
from azure.maps.route import MapsRouteClient

coordinates=LatLon(47.60323, -122.33028)

reverse_route_result = client.reverse_route_address(coordinates=coordinates);
```

### Translate coordinate location into a human understandable cross street

Translate coordinate location into a human understandable cross street by using Route Address Reverse Cross Street API. Most often, this is needed in tracking applications that receive a GPS feed from a device or asset, and wish to know where the coordinate is located.

```python
from azure.maps.route import MapsRouteClient

coordinates=LatLon(47.60323, -122.33028)

reverse_route_result = client.reverse_route_cross_street_address(coordinates=coordinates);
``` -->

## Troubleshooting

### General

Maps Route clients raise exceptions defined in [Azure Core](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/README.md).

This list can be used for reference to catch thrown exceptions. To get the specific error code of the exception, use the `error_code` attribute, i.e, `exception.error_code`.

### Logging

This library uses the standard [logging](https://docs.python.org/3/library/logging.html) library for logging.
Basic information about HTTP sessions (URLs, headers, etc.) is logged at INFO level.

Detailed DEBUG level logging, including request/response bodies and unredacted headers, can be enabled on a client with the `logging_enable` argument:

```python
import sys
import logging
from azure.maps.route import MapsRouteClient

# Create a logger for the 'azure.maps.route' SDK
logger = logging.getLogger('azure.maps.route')
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

<!-- Get started with our [Maps Route samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/maps/azure-maps-route/samples) ([Async Version samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/maps/azure-maps-route/samples/async_samples)).

Several Azure Maps Route Python SDK samples are available to you in the SDK's GitHub repository. These samples provide example code for additional scenarios commonly encountered while working with Maps Route -->

<!-- ```bash
set AZURE_SUBSCRIPTION_KEY="<RealSubscriptionKey>"

pip install azure-maps-route

python samples/sample_authentication.py
python sample/sample_fuzzy_route.py
python samples/sample_get_point_of_interest_categories.py
python samples/sample_reverse_route_address.py
python samples/sample_reverse_route_cross_street_address.py
python samples/sample_route_nearby_point_of_interest.py
python samples/sample_route_point_of_interest_category.py
python samples/sample_route_point_of_interest.py
python samples/sample_route_structured_address.py
``` -->
<!-- 
Further detail please refer to [Samples Introduction](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/maps/azure-maps-route/samples/README.md) -->

### Additional documentation

For more extensive documentation on Azure Maps Route, see the [Azure Maps Route documentation](https://docs.microsoft.com/rest/api/maps/route) on docs.microsoft.com.

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
