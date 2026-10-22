# Azure Maps Search Package client library for Python

This package contains a Python SDK for Azure Maps Services for Search.
Read more about Azure Maps Services [here](https://learn.microsoft.com/azure/azure-maps/)

[Source code](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/maps/azure-maps-search) | [API reference documentation](https://learn.microsoft.com/rest/api/maps/search) | [Product documentation](https://learn.microsoft.com/azure/azure-maps/)

## _Disclaimer_

_Azure SDK Python packages support for Python 2.7 has ended 01 January 2022. For more information and questions, please refer to <https://github.com/Azure/azure-sdk-for-python/issues/20691>_

## Getting started

### Prerequisites

- Python 3.8 or later is required to use this package.
- An [Azure subscription][azure_subscription] and an [Azure Maps account](https://learn.microsoft.com/azure/azure-maps/how-to-manage-account-keys).
- A deployed Maps Services resource. You can create the resource via [Azure Portal][azure_portal] or [Azure CLI][azure_cli].

If you use Azure CLI, replace `<resource-group-name>` and `<account-name>` of your choice, and select a proper [pricing tier](https://learn.microsoft.com/azure/azure-maps/choose-pricing-tier) based on your needs via the `<sku-name>` parameter. Please refer to [this page](https://learn.microsoft.com/cli/azure/maps/account?view=azure-cli-latest#az_maps_account_create) for more details.

```bash
az maps account create --resource-group <resource-group-name> --account-name <account-name> --sku <sku-name>
```

### Install the package

Install the Azure Maps Service Search SDK.

```bash
pip install azure-maps-search
```

### Create and Authenticate the MapsSearchClient

To create a client object to access the Azure Maps Search API, you will need a **credential** object. Azure Maps Search client also support three ways to authenticate.

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

#### 2. Authenticate with a SAS Credential

Shared access signature (SAS) tokens are authentication tokens created using the JSON Web token (JWT) format and are cryptographically signed to prove authentication for an application to the Azure Maps REST API.

To authenticate with a SAS token in Python, you'll need to generate one using the azure-mgmt-maps package. 

We need to tell user to install `azure-mgmt-maps`: `pip install azure-mgmt-maps`

Here's how you can generate the SAS token using the list_sas method from azure-mgmt-maps:

```python
from azure.identity import DefaultAzureCredential
from azure.mgmt.maps import AzureMapsManagementClient

"""
# PREREQUISITES
    pip install azure-identity
    pip install azure-mgmt-maps
# USAGE
    python account_list_sas.py
    Before run the sample, please set the values of the client ID, tenant ID and client secret
    of the AAD application as environment variables: AZURE_CLIENT_ID, AZURE_TENANT_ID,
    AZURE_CLIENT_SECRET. For more info about how to get the value, please see:
    https://learn.microsoft.com/azure/active-directory/develop/howto-create-service-principal-portal
"""


def main():
    client = AzureMapsManagementClient(
        credential=DefaultAzureCredential(),
        subscription_id="your-subscription-id",
    )

    response = client.accounts.list_sas(
        resource_group_name="myResourceGroup",
        account_name="myMapsAccount",
        maps_account_sas_parameters={
            "expiry": "2017-05-24T11:42:03.1567373Z",
            "maxRatePerSecond": 500,
            "principalId": "your-principal-id",
            "regions": ["eastus"],
            "signingKey": "primaryKey",
            "start": "2017-05-24T10:42:03.1567373Z",
        },
    )
    print(response)
```

Once the SAS token is created, set the value of the token as environment variable: `AZURE_SAS_TOKEN`.
Then pass an `AZURE_SAS_TOKEN` as the `credential` parameter into an instance of AzureSasCredential.

```python
import os

from azure.core.credentials import AzureSASCredential
from azure.maps.search import MapsSearchClient

credential = AzureSASCredential(os.environ.get("AZURE_SAS_TOKEN"))

search_client = MapsSearchClient(
    credential=credential,
)
```

#### 3. Authenticate with an Microsoft Entra ID credential

You can authenticate with [Microsoft Entra ID token credential][maps_authentication_microsoft_entra_id] using the [Azure Identity library][azure_identity].
Authentication by using Microsoft Entra ID requires some initial setup:

- Install [azure-identity][azure-key-credential]
- Register a [new Microsoft Entra ID application][register_microsoft_entra_id_app]
- Grant access to Azure Maps by assigning the suitable role to your service principal. Please refer to the [Manage authentication page][manage_microsoft_entra_id_auth_page].

After setup, you can choose which type of [credential][azure-key-credential] from `azure.identity` to use.
As an example, [DefaultAzureCredential][default_azure_credential]
can be used to authenticate the client:

Next, set the values of the client ID, tenant ID, and client secret of the Microsoft Entra ID application as environment variables:
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

Async clients and credentials should be closed when they're no longer needed. These objects are async context managers and define async `close` methods.

## Examples

The following sections provide several code snippets covering some of the most common Azure Maps Search tasks, including:

- [Geocode an address](#geocode-an-address)
- [Batch geocode addresses](#batch-geocode-addresses)
- [Get polygons for a given location](#get-polygons-for-a-given-location)
- [Make a Reverse Address Search to translate coordinate location to street address](#make-a-reverse-address-search-to-translate-coordinate-location-to-street-address)
- [Batch request for reverse geocoding](#batch-request-for-reverse-geocoding)

### Geocode an address

You can use an authenticated client to convert an address into latitude and longitude coordinates. This process is also called geocoding. In addition to returning the coordinates, the response will also return detailed address properties such as street, postal code, municipality, and country/region information.

```python
import os

from azure.core.exceptions import HttpResponseError

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY", "your subscription key")

def geocode():
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.search import MapsSearchClient

    maps_search_client = MapsSearchClient(credential=AzureKeyCredential(subscription_key))
    try:
        result = maps_search_client.get_geocoding(query="15127 NE 24th Street, Redmond, WA 98052")
        if result.get('features', False):
            coordinates = result['features'][0]['geometry']['coordinates']
            longitude = coordinates[0]
            latitude = coordinates[1]

            print(longitude, latitude)
        else:
            print("No results")

    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")

if __name__ == '__main__':
    geocode()
```

### Batch geocode addresses

This sample demonstrates how to perform batch search address.

```python
import os

from azure.core.exceptions import HttpResponseError

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY", "your subscription key")

def geocode_batch():
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.search import MapsSearchClient

    maps_search_client = MapsSearchClient(credential=AzureKeyCredential(subscription_key))
    try:
        result = maps_search_client.get_geocoding_batch({
          "batchItems": [
            {"query": "400 Broad St, Seattle, WA 98109"},
            {"query": "15127 NE 24th Street, Redmond, WA 98052"},
          ],
        },)

        if not result.get('batchItems', False):
            print("No batchItems in geocoding")
            return

        for item in result['batchItems']:
            if not item.get('features', False):
                print(f"No features in item: {item}")
                continue

            coordinates = item['features'][0]['geometry']['coordinates']
            longitude, latitude = coordinates
            print(longitude, latitude)

    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")

if __name__ == '__main__':
    geocode_batch()
```

### Get polygons for a given location

This sample demonstrates how to search polygons.

```python
import os

from azure.core.exceptions import HttpResponseError
from azure.maps.search import Resolution
from azure.maps.search import BoundaryResultType


subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY", "your subscription key")

def get_polygon():
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.search import MapsSearchClient

    maps_search_client = MapsSearchClient(credential=AzureKeyCredential(subscription_key))
    try:
        result = maps_search_client.get_polygon(
          coordinates=[-122.204141, 47.61256],
          result_type=BoundaryResultType.LOCALITY,
          resolution=Resolution.SMALL,
        )

        if not result.get('geometry', False):
            print("No geometry found")
            return

        print(result["geometry"])
    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")

if __name__ == '__main__':
    get_polygon()
```

### Make a Reverse Address Search to translate coordinate location to street address

You can translate coordinates into human-readable street addresses. This process is also called reverse geocoding. This is often used for applications that consume GPS feeds and want to discover addresses at specific coordinate points.

```python
import os

from azure.core.exceptions import HttpResponseError

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY", "your subscription key")

def reverse_geocode():
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.search import MapsSearchClient

    maps_search_client = MapsSearchClient(credential=AzureKeyCredential(subscription_key))
    try:
        result = maps_search_client.get_reverse_geocoding(coordinates=[-122.138679, 47.630356])
        if result.get('features', False):
            props = result['features'][0].get('properties', {})
            if props and props.get('address', False):
                print(props['address'].get('formattedAddress', 'No formatted address found'))
            else:
                print("Address is None")
        else:
            print("No features available")
    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")


if __name__ == '__main__':
   reverse_geocode()
```

### Batch request for reverse geocoding

This sample demonstrates how to perform reverse search by given coordinates in batch.

```python
import os
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from azure.maps.search import MapsSearchClient

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY", "your subscription key")

def reverse_geocode_batch():
    maps_search_client = MapsSearchClient(credential=AzureKeyCredential(subscription_key))
    try:
        result = maps_search_client.get_reverse_geocoding_batch({
              "batchItems": [
                {"coordinates": [-122.349309, 47.620498]},
                {"coordinates": [-122.138679, 47.630356]},
              ],
            },)

        if result.get('batchItems', False):
            for idx, item in enumerate(result['batchItems']):
                features = item['features']
                if features:
                    props = features[0].get('properties', {})
                    if props and props.get('address', False):
                        print(
                            props['address'].get('formattedAddress', f'No formatted address for item {idx + 1} found'))
                    else:
                        print(f"Address {idx + 1} is None")
                else:
                    print(f"No features available for item {idx + 1}")
        else:
            print("No batch items found")
    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")


if __name__ == '__main__':
   reverse_geocode_batch()
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

python samples/sample_geocode.py
python samples/sample_geocode_batch.py
python samples/sample_get_polygon.py
python samples/sample_reverse_geocode.py
python samples/sample_reverse_geocode_batch.py
```

> Notes: `--pre` flag can be optionally added, it is to include pre-release and development versions for `pip install`. By default, `pip` only finds stable versions.

Further detail please refer to [Samples Introduction](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/maps/azure-maps-search/samples/README.md)

### Additional documentation

For more extensive documentation on Azure Maps Search, see the [Azure Maps Search documentation](https://learn.microsoft.com/rest/api/maps/search) on learn.microsoft.com.

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit <https://cla.microsoft.com>.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

<!-- LINKS -->
[azure_subscription]: https://azure.microsoft.com/free/
[azure_identity]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/identity/azure-identity
[azure_portal]: https://portal.azure.com
[azure_cli]: https://learn.microsoft.com/cli/azure
[azure-key-credential]: https://aka.ms/azsdk/python/core/azurekeycredential
[default_azure_credential]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#defaultazurecredential
[register_microsoft_entra_id_app]: https://learn.microsoft.com/powershell/module/Az.Resources/New-AzADApplication?view=azps-8.0.0
[maps_authentication_microsoft_entra_id]: https://learn.microsoft.com/azure/azure-maps/how-to-manage-authentication
[create_new_application_registration]: https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps/applicationsListBlade/quickStartType/AspNetWebAppQuickstartPage/sourceType/docs
[manage_microsoft_entra_id_auth_page]: https://learn.microsoft.com/azure/azure-maps/how-to-manage-authentication
[how_to_manage_authentication]: https://learn.microsoft.com/azure/azure-maps/how-to-manage-authentication#view-authentication-details
