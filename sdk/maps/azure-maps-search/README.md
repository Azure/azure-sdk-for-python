# Azure Maps Search Package client library for Python

This package contains a Python SDK for Azure Maps Services for Search.
Read more about Azure Maps Services [here](https://docs.microsoft.com/en-us/azure/azure-maps/)

[Source code](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/maps/azure-maps-search) | [Package (Pypi)](https://pypi.org/project/azure-maps-search/) | [API reference documentation](https://docs.microsoft.com/en-us/rest/api/maps/search) | [Product documentation](https://docs.microsoft.com/en-us/azure/azure-maps/)

## _Disclaimer_

_Azure SDK Python packages support for Python 2.7 has ended 01 January 2022. For more information and questions, please refer to https://github.com/Azure/azure-sdk-for-python/issues/20691_

## Getting started

## Prerequisites

- Python 3.6 or later is required to use this package.
- A deployed Maps Services resource. You can use the [Azure Portal](https://docs.microsoft.com/azure/communication-services/quickstarts/create-communication-resource?tabs=windows&pivots=platform-azp) or the [Azure PowerShell](https://docs.microsoft.com/powershell/module/az.communication/new-azcommunicationservice) to set it up.

## Install the package

Install the Azure Maps Service Search SDK.

```bash
pip install --pre azure-maps-search
```

## Authenticate the client

In order to interact with the Document Translation feature service, you will need to create an instance of a client.
An **endpoint** and **credential** are necessary to instantiate the client object.


## Looking up the endpoint

You can find the endpoint for your Maps resource using the
[Azure Portal][azure_portal_get_endpoint].

> Note that the service requires a custom domain endpoint. Follow the instructions in the above link to format your endpoint:
> https://{NAME-OF-YOUR-RESOURCE}.mapsservices.azure.com/


## Create the client with AzureKeyCredential

To use an [API key] as the `credential` parameter,
pass the key as a string into an instance of [AzureKeyCredential][azure-key-credential].

```python
from azure.core.credentials import AzureKeyCredential
from azure.maps.search import SearchClient

endpoint = "https://<resource-name>.mapsservices.azure.com/"
credential = AzureKeyCredential("<api_key>")
search_client = SearchClient(endpoint, credential)
```

## Create the client with an Azure Active Directory credential

`AzureKeyCredential` authentication is used in the examples in this getting started guide, but you can also
authenticate with Azure Active Directory using the [azure-identity][azure_identity] library.

To use the [DefaultAzureCredential][default_azure_credential] type shown below, or other credential types provided
with the Azure SDK, please install the `azure-identity` package:

```pip install azure-identity```

You will also need to [register a new AAD application and grant access][register_aad_app] to your
Translator resource by assigning the `"Cognitive Services User"` role to your service principal.

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

to add all operations

## Examples

The following sections provide several code snippets covering some of the most common tasks, including:

- [Operations](#events-operations)

## Sample Code

These are code samples that show common scenario operations with the Azure Maps Search client library.
The async versions of the samples (the python sample files appended with `_async`) show asynchronous operations.
Before run the sample code, refer to Prerequisites
<!-- [Prerequisites](#Prerequisites) -->
to create a resource, then set some Environment Variables

```bash
set AZURE_MAPS_SERVICE_ENDPOINT="https://<RESOURCE_NAME>.mapsservices.azure.com"
set MAPS_SAMPLES_CONNECTION_STRING="<connection string of your Maps service>"

pip install azure-maps-search

python samples\search_client_sample.py
python samples\search_client_sample_async.py
```

## Troubleshooting

Running into issues? This section should contain details as to what to do there.

## Next steps

More sample code should go [here](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/maps/azure-maps-search/samples), along with links out to the appropriate example tests.

## Contributing

If you encounter any bugs or have suggestions, please file an issue in the [Issues](<https://github.com/Azure/azure-sdk-for-python/issues>) section of the project.

![Impressions](https://azure-sdk-impressions.azurewebsites.net/api/impressions/azure-sdk-for-python%2Fsdk%2Ftemplate%2Fazure-template%2FREADME.png)
