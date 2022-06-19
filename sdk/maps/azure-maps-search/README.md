# Azure Maps Search Package client library for Python

This package contains a Python SDK for Azure Maps Services for Search.
Read more about Azure Maps Services [here](https://docs.microsoft.com/azure/azure-maps/)

[Source code](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/maps/azure-maps-search) | [API reference documentation](https://docs.microsoft.com/rest/api/maps/search) | [Product documentation](https://docs.microsoft.com/azure/azure-maps/)

## _Disclaimer_

_Azure SDK Python packages support for Python 2.7 has ended 01 January 2022. For more information and questions, please refer to <https://github.com/Azure/azure-sdk-for-python/issues/20691>_

## Getting started

### Prerequisites

- Python 3.6 or later is required to use this package.
- A deployed Maps Services resource. You can use the [Azure Portal](https://docs.microsoft.com/azure/azure-maps/quick-demo-map-app) to set it up.

### Install the package

Install the Azure Maps Service Search SDK.

```bash
pip install --pre azure-maps-search
```

### Authenticate the client

In order to interact with the Document Translation feature service, you will need to create an instance of a client.
An **endpoint** and **credential** are necessary to instantiate the client object.

### Create the client with AzureKeyCredential

To use an [API key] as the `credential` parameter,
pass the key as a string into an instance of [AzureKeyCredential][azure-key-credential].

```python
from azure.core.credentials import AzureKeyCredential
from azure.maps.search import SearchClient

endpoint = "https://<resource-name>.mapsservices.azure.com/"
credential = AzureKeyCredential("<api_key>")
search_client = SearchClient(endpoint, credential)
```

### Create the client with an Azure Active Directory credential

`AzureKeyCredential` authentication is used in the examples in this getting started guide, but you can also
authenticate with Azure Active Directory using the [azure-identity][azure_identity] library.

To use the [DefaultAzureCredential][default_azure_credential] type shown below, or other credential types provided
with the Azure SDK, please install the `azure-identity` package:

```pip install azure-identity```

Once completed, set the values of the client ID, and client secret of the AAD application as environment variables:
`AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`.

```python
from azure.identity import DefaultAzureCredential
from azure.maps.search import SearchClient
credential = DefaultAzureCredential()

search_client = SearchClient(
    endpoint="https://<resource-name>.mapsservices.azure.com/",
    credential=credential
)
```

## Key concepts

`SearchClient` is the primary client for developers using the Azure Maps Search client library for Python.
Once you initialized a `SearchClient` class, you can explore the methods on this client object to understand the different features of the Azure Maps Search service that you can access.

## Examples

The following sections provide several code snippets covering some of the most common Azure Maps Search tasks, including:

- [Request latitude and longitude coordinates for an address](#request-latitude-and-longitude-coordinates-for-an-address)

- [Search for an address or Point of Interest](#search-for-an-address-or-point-of-interest)

- [Make a Reverse Address Search to translate coordinate location to street address](#make-a-reverse-address-search-to-translate-coordinate-location-to-street-address)
- [Translate coordinate location into a human understandable cross street](#translate-coordinate-location-into-a-human-understandable-cross-street)
- [More Sample Code](#sample-code)

### Request latitude and longitude coordinates for an address

You can use an authenticated client to convert an address into latitude and longitude coordinates. This process is also called geocoding. In addition to returning the coordinates, the response will also return detailed address properties such as street, postal code, municipality, and country/region information.

```python
search_result = client.search_address("400 Broad, Seattle");
```

### Search for an address or Point of Interest

You can use Fuzzy Search to search an address or a point of interest (POI). The following examples demostrate how to search for `pizza` over the scope of a specific country (`France`, in this example).

```python
fuzzy_search_result = client.fuzzy_search({ query: "pizza", country_filter: "fr" });
```

### Make a Reverse Address Search to translate coordinate location to street address

You can translate coordinates into human readable street addresses. This process is also called reverse geocoding.
This is often used for applications that consume GPS feeds and want to discover addresses at specific coordinate points.

```python
coordinates: LatLon = {
  latitude: 47.59118,
  longitude: -122.3327,
};

reverse_search_result = client.reverse_search_address(coordinates);
```

### Translate coordinate location into a human understandable cross street

Translate coordinate location into a human understandable cross street by using Search Address Reverse Cross Street API. Most often, this is needed in tracking applications that receive a GPS feed from a device or asset, and wish to know where the coordinate is located.

```python
coordinates: LatLon = {
  latitude: 47.59118,
  longitude: -122.3327,
};

const reverse_search_result = client.reverse_search_cross_street_address(coordinates);
```

### Sample Code

These are code samples that show common scenario operations with the Azure Maps Search client library.
The async versions of the samples (the python sample files appended with `_async`) show asynchronous operations.
Before run the sample code, refer to Prerequisites
<!-- [Prerequisites](#Prerequisites) -->
to create a resource, then set some Environment Variables

```bash
set AZURE_MAPS_SERVICE_ENDPOINT="https://<RESOURCE_NAME>.mapsservices.azure.com"
set MAPS_SAMPLES_CONNECTION_STRING="<connection string of your Maps service>"

pip install azure-maps-search

python samples\search.py
```

## Troubleshooting

Running into issues? This section should contain details as to what to do there.

## Next steps

More sample code should go [here](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/maps/azure-maps-search/samples), along with links out to the appropriate example tests.

## Contributing

If you encounter any bugs or have suggestions, please file an issue in the [Issues](<https://github.com/Azure/azure-sdk-for-python/issues>) section of the project.

![Impressions](https://azure-sdk-impressions.azurewebsites.net/api/impressions/azure-sdk-for-python%2Fsdk%2Ftemplate%2Fazure-template%2FREADME.png)

<!-- LINKS -->
[azure_subscription]: https://azure.microsoft.com/free/
[azure_identity]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/identity/azure-identity
[default_azure_credential]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#defaultazurecredential
[azure-key-credential]: https://aka.ms/azsdk/python/core/azurekeycredential
