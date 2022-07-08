# Azure Maps Route Package client library for Python

This package contains a Python SDK for Azure Maps Services for Route.
Read more about Azure Maps Services [here](https://docs.microsoft.com/azure/azure-maps/)

[Source code](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/maps/azure-maps-route) | [API reference documentation](https://docs.microsoft.com/rest/api/maps/route) | [Product documentation](https://docs.microsoft.com/azure/azure-maps/)

## _Disclaimer_

_Azure SDK Python packages support for Python 2.7 has ended 01 January 2022. For more information and questions, please refer to <https://github.com/Azure/azure-sdk-for-python/issues/20691>_

## Getting started

### Prerequisites

- Python 3.6 or later is required to use this package.
- A deployed Maps Services resource. You can use the [Azure Portal](https://docs.microsoft.com/azure/azure-maps/quick-demo-map-app) to set it up.

### Install the package

Install the Azure Maps Service Route SDK.

```bash
pip install --pre azure-maps-route
```

### Authenticate the client

In order to interact with the Azure Maps Route service, you will need to create an instance of a client.
A **credential** is necessary to instantiate the client object.

### Create the client with AzureKeyCredential

Once completed, set the value of the subscription key as environment variable:
`AZURE_SUBSCRIPTION_KEY`.

To use an `AZURE_SUBSCRIPTION_KEY` as the `credential` parameter,
pass the key as a string into an instance of [AzureKeyCredential][azure-key-credential].

```python
from azure.core.credentials import AzureKeyCredential
from azure.maps.route import MapsRouteClient

credential = AzureKeyCredential(os.environ.get("AZURE_SUBSCRIPTION_KEY"))

route_client = MapsRouteClient(
    credential=credential,
)
```

### Create the client with an Azure Active Directory credential

To use an [Azure Active Directory (AAD) token credential][maps_authentication_aad],
provide an instance of the desired credential type obtained from the
[azure-identity][azure-key-credential] library.

Authentication with AAD requires some initial setup:

- [Install azure-identity][azure-key-credential]
- [Register a new AAD application][register_aad_app]

After setup, you can choose which type of [credential][azure-key-credential] from azure.identity to use.
As an example, [DefaultAzureCredential][default_azure_credential]
can be used to authenticate the client:

Set the values of the client ID, tenant ID, and client secret of the AAD application as environment variables:
`AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_CLIENT_SECRET`

Use the returned token credential to authenticate the client:

```python
from azure.maps.route import MapsRouteClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
route_client = MapsRouteClient(credential=credential)
```

## Key concepts

`MapsRouteClient` is the primary client for developers using the Azure Maps Route client library for Python.
Once you initialized a `MapsRouteClient` class, you can explore the methods on this client object to understand the different features of the Azure Maps Route service that you can access.

## Examples

The following sections provide several code snippets covering some of the most common Azure Maps Route tasks, including:

- [Get Route Directions](#get-route-directions)
- [More Sample Code](#sample-code)

### Get Route Directions

You can translate coordinates into human readable street addresses. This process is also called reverse geocoding.
This is often used for applications that consume GPS feeds and want to discover addresses at specific coordinate points.

```python
coordinates=LatLon(47.60323, -122.33028)

routePoints = LatLon() if not routePoints else routePoints

directions_results=client.get_route_directions(query=List[routePoints])
```

### Sample Code

These are code samples that show common scenario operations with the Azure Maps Route client library.
Before run the sample code, refer to [prerequisites](#prerequisites) to create a resource, then set some Environment Variables

```bash
set AZURE_SUBSCRIPTION_KEY="<RealSubscriptionKey>"

pip install azure-maps-route

python samples\route.py
```

More sample code should go [here](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/maps/azure-maps-route/samples), along with links out to the appropriate example tests.

## Troubleshooting

Running into issues? This section should contain details as to what to do there.

## Next steps

## Contributing

If you encounter any bugs or have suggestions, please file an issue in the [Issues](<https://github.com/Azure/azure-sdk-for-python/issues>) section of the project.

![Impressions](https://azure-sdk-impressions.azurewebsites.net/api/impressions/azure-sdk-for-python%2Fsdk%2Ftemplate%2Fazure-template%2FREADME.png)

<!-- LINKS -->
[azure_subscription]: https://azure.microsoft.com/free/
[azure_identity]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/identity/azure-identity
[default_azure_credential]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#defaultazurecredential
[azure-key-credential]: https://aka.ms/azsdk/python/core/azurekeycredential
[register_aad_app]: https://docs.microsoft.com/powershell/module/Az.Resources/New-AzADApplication?view=azps-8.0.0
[maps_authentication_aad]: https://docs.microsoft.com/azure/azure-maps/how-to-manage-authentication
[create_new_application_registration]: https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps/applicationsListBlade/quickStartType/AspNetWebAppQuickstartPage/sourceType/docs