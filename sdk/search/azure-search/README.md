# Azure Cognitive Search client library for Python
Azure Cognitive Search is a fully managed cloud search service that provides a rich search experience to custom applications.

[Source code](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/search/azure-search) |
[Package (PyPI)](https://pypi.org/project/azure-search/) |
[API reference documentation](https://aka.ms/azsdk-python-search-ref-docs) |
[Product documentation](https://docs.microsoft.com/en-us/azure/search/search-what-is-azure-search) |
[Samples](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/search/azure-search/samples)

## Getting started

### Prerequisites
* Python 2.7, or 3.5 or later is required to use this package.
* You must have an [Azure subscription][azure_sub] and an existing.
[Azure Cognitive Search service][search_resource] to use this package.

If you need to create the resource, you can use the [Azure Portal][azure_portal] or [Azure CLI][azure_cli].

If you use the Azure CLI, replace `<your-resource-group-name>` and `<your-resource-name>` with your own unique names:

```PowerShell
az search service create --resource-group <your-resource-group-name> --name <your-resource-name> --sku S
```

The above creates a resource with the "Standard" pricing tier. See [choosing a pricing tier](https://docs.microsoft.com/en-us/azure/search/search-sku-tier) for more information.


### Install the package
Install the Azure Cognitive Search client library for Python with [pip](https://pypi.org/project/pip/):

```bash
pip install azure-search --pre
```

### Create an Azure Cognitive Search service

### Using an Admin Key

Use the [Azure CLI][azure_cli] snippet below to get the Admin Key from the Cognitive Search resource.

```PowerShell
az search admin-key show --resource-group <your-resource-group-name> --service-name <your-resource-name>
```

Alternatively, you can get the endpoint and Admin Key from the resource information in the [Azure Portal][azure_portal].

### Authenticate the client
Interaction with this service begins with an instance of a [client](#client "search-client").
To create a client object, you will need the cognitive services or text analytics `endpoint` to
your resource and a `credential` that allows you access:

```python
from azure.search import SearchApiKeyCredential, SearchIndexClient

credential = SearchApiKeyCredential("<api key>")

client = SearchIndexClient(search_service_name="<service name>",
                           index_name="<index name>",
                           credential=credential)
```

## Key concepts

### Client
The Cognitive Search client library provides a [SearchIndexClient](https://aka.ms/azsdk-python-search-searchindexclient) to perform search operations on [batches of documents](#Examples "examples").
It provides both synchronous and asynchronous operations to access a specific use of Cognitive Search indices, such as querying, suggestions or autocompletion.


## Examples

## Troubleshooting

### General
The Azure Cognitive Search client will raise exceptions defined in [Azure Core](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/README.md).

### Logging
This library uses the standard
[logging](https://docs.python.org/3.5/library/logging.html) library for logging.
Basic information about HTTP sessions (URLs, headers, etc.) is logged at INFO
level.

## Next steps

### Additional documentation
For more extensive documentation on Cognitive Search, see the [Azure Cognitive Search documentation](https://docs.microsoft.com/en-us/azure/search/) on docs.microsoft.com.

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Related projects

- [Microsoft Azure SDK for Python](https://github.com/Azure/azure-sdk-for-python)

![Impressions](https://azure-sdk-impressions.azurewebsites.net/api/impressions/azure-sdk-for-python%2Fsdk%2Fsearch%2Fazure-search%2FREADME.png)

[azure_cli]: https://docs.microsoft.com/cli/azure
[azure_sub]: https://azure.microsoft.com/free/
[search_resource]: https://docs.microsoft.com/en-us/azure/search/search-create-service-portal
[azure_portal]: https://portal.azure.com
