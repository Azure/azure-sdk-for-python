# Azure Maps Route Package client library for Python

This package contains a Python SDK for Azure Maps Services for Route.
Read more about Azure Maps Services [here](https://learn.microsoft.com/azure/azure-maps/)

[Source code](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/maps/azure-maps-route) | [API reference documentation](https://learn.microsoft.com/rest/api/maps/route) | [Product documentation](https://learn.microsoft.com/azure/azure-maps/)

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

Install the Azure Maps Service Route SDK.

```bash
pip install azure-maps-route
```

### Create and Authenticate the MapsRouteClient

To create a client object to access the Azure Maps Route API, you will need a **credential** object. Azure Maps Route client also support three ways to authenticate.

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
from azure.maps.route import MapsRouteClient

credential = AzureSASCredential(os.environ.get("AZURE_SAS_TOKEN"))

route_client = MapsRouteClient(
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
from azure.maps.route import MapsRouteClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
route_client = MapsRouteClient(
    client_id="<Azure Maps Client ID>",
    credential=credential
)
```

## Key concepts

The Azure Maps Route client library for Python allows you to interact with each of the components through the use of a dedicated client object.

### Sync Clients

`MapsRouteClient` is the primary client for developers using the Azure Maps Route client library for Python.
Once you initialized a `MapsRouteClient` class, you can explore the methods on this client object to understand the different features of the Azure Maps Route service that you can access.

### Async Clients

This library includes a complete async API supported on Python 3.8+. To use it, you must first install an async transport, such as [aiohttp](https://pypi.org/project/aiohttp/).
See [azure-core documentation](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#transport) for more information.

Async clients and credentials should be closed when they're no longer needed. These
objects are async context managers and define async `close` methods.

## Examples

The following sections provide several code snippets covering some of the most common Azure Maps Route tasks, including:

- [Request and Get Route Directions](#request-and-get-route-directions)
- [Request and Get Route Range](#request-and-get-route-range)
- [Get Route Matrix](#get-route-matrix)
- [Get Route Directions Batch](#get-route-directions-batch)

### Request and Get Route Directions

This service request returns a route between an origin and a destination, passing through waypoints if they are specified. The route will take into account factors such as current traffic and the typical road speeds on the requested day of the week and time of day. Refer the sample code [here](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/maps/azure-maps-route/samples/sample_get_route_directions.py).

```python
from azure.maps.route import MapsRouteClient

route_directions_result = client.get_route_directions(route_points=[(47.60323, -122.33028), (53.2, -106)]);
```

### Request and Get Route Range

This service will calculate a set of locations that can be reached from the origin point by given coordinates and based on fuel, energy,  time or distance budget that is specified. Refer the sample code [here](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/maps/azure-maps-route/samples/sample_get_route_range.py).

```python
from azure.maps.route import MapsRouteClient

route_range_result = client.get_route_range(coordinates=(47.60323, -122.33028), time_budget_in_sec=6000);
```

### Get Route Matrix

If the Matrix Route request was accepted successfully, the Location header in the response contains the URL to download the results of the request. Refer the sample code [here](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/maps/azure-maps-route/samples/sample_get_route_matrix.py).

Retrieves the result of a previous route matrix request.
The method returns a poller for retrieving the result.

```python
from azure.maps.route import MapsRouteClient

route_matrix_result = client.begin_get_route_matrix_result(matrix_id="11111111-2222-3333-4444-555555555555");
```

### Get Route Directions Batch

Retrieves the result of a previous route direction batch request.
The method returns a poller for retrieving the result. Refer sample code [here](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/maps/azure-maps-route/samples/sample_get_route_directions_batch_sync.py).

```python
from azure.maps.route import MapsRouteClient

route_directions_batch_poller_result = client.begin_get_route_directions_batch_result(batch_id="11111111-2222-3333-4444-555555555555");
```

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

### Additional

Still running into issues? If you encounter any bugs or have suggestions, please file an issue in the [Issues](<https://github.com/Azure/azure-sdk-for-python/issues>) section of the project.

## Next steps

### More sample code

Get started with our [Maps Route samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/maps/azure-maps-route/samples) ([Async Version samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/maps/azure-maps-route/samples/async_samples)).

Several Azure Maps Route Python SDK samples are available to you in the SDK's GitHub repository. These samples provide example code for additional scenarios commonly encountered while working with Maps Route

```bash
set AZURE_SUBSCRIPTION_KEY="<RealSubscriptionKey>"

pip install azure-maps-route --pre

python samples/sample_authentication.py
python sample/sample_get_route_range.py
python samples/sample_get_route_directions.py
python samples/sample_request_route_matrix.py
python samples/async_samples/sample_authentication_async.py
python samples/async_samples/sample_get_route_range_async.py
python samples/async_samples/sample_request_route_matrix_async.py
python samples/async_samples/sample_get_route_directions_async.py
```

> Notes: `--pre` flag can be optionally added, it is to include pre-release and development versions for `pip install`. By default, `pip` only finds stable versions.

Further detail please refer to [Samples Introduction](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/maps/azure-maps-route/samples/README.md)

### Additional documentation

For more extensive documentation on Azure Maps Route, see the [Azure Maps Route documentation](https://learn.microsoft.com/rest/api/maps/route) on learn.microsoft.com.

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
