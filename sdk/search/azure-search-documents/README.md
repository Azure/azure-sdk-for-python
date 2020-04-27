# Azure Cognitive Search client library for Python

Azure Cognitive Search is a fully managed cloud search service that provides a rich search experience to custom applications.

[Source code](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/search/azure-search-documents) |
[Package (PyPI)](https://pypi.org/project/azure-search-documents/) |
[API reference documentation](https://aka.ms/azsdk-python-search-ref-docs) |
[Product documentation](https://docs.microsoft.com/en-us/azure/search/search-what-is-azure-search) |
[Samples](samples)


## Getting started

### Prerequisites

* Python 2.7, or 3.5 or later is required to use this package.
* You must have an [Azure subscription][azure_sub] and an existing
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
pip install azure-search-documents --pre
```

## Key concepts

Azure Cognitive Search has the concepts of search services and indexes and documents, where a search service contains
one or more indexes that provides persistent storage of searchable data, and data is loaded in the form of JSON documents.
Data can be pushed to an index from an external data source, but if you use an indexer, it's possible to crawl a data
source to extract and load data into an index.

There are several types of operations that can be executed against the service:

-   [Index management operations](https://docs.microsoft.com/en-us/rest/api/searchservice/index-operations). Create, delete, update, or configure a search index.
-   [Document operations](https://docs.microsoft.com/en-us/rest/api/searchservice/document-operations). Add, update, or delete documents in the index, query the index, or look up specific documents by ID.
-   [Indexer operations](https://docs.microsoft.com/en-us/rest/api/searchservice/indexer-operations). Automate aspects of an indexing operation by configuring a data source and an indexer that you can schedule or run on demand. This feature is supported for a limited number of data source types.
-   [Skillset operations](https://docs.microsoft.com/en-us/rest/api/searchservice/skillset-operations). Part of a cognitive search workload, a skillset defines a series of a series of enrichment processing steps. A skillset is consumed by an indexer.
-   [Synonym map operations](https://docs.microsoft.com/en-us/rest/api/searchservice/synonym-map-operations). A synonym map is a service-level resource that contains user-defined synonyms. This resource is maintained independently from search indexes. Once uploaded, you can point any searchable field to the synonym map (one per field).

### Authenticate the client

In order to interact with the Cognitive Search service you'll need to create an instance of the Search Client class.
To make this possible you will need an [api-key of the Cognitive Search service](https://docs.microsoft.com/en-us/azure/search/search-security-api-keys).

The SDK provides two clients.

1. SearchIndexClient for all document operations.
2. SearchServiceClient for all CRUD operations on service resources.

### Create a SearchServiceClient

Once you have the values of the Cognitive Search Service [service endpoint](https://docs.microsoft.com/en-us/azure/search/search-create-service-portal#get-a-key-and-url-endpoint)
and [api key](https://docs.microsoft.com/en-us/azure/search/search-security-api-keys) you can create the Search Service client:

```python
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchServiceClient

credential = AzureKeyCredential("<api key>")

client = SearchServiceClient(endpoint="<service endpoint>"
                           credential=credential)
```

### Create a SearchIndexClient

To create a SearchIndexClient, you will need an existing index name as well as the values of the Cognitive Search Service
[service endpoint](https://docs.microsoft.com/en-us/azure/search/search-create-service-portal#get-a-key-and-url-endpoint) and
[api key](https://docs.microsoft.com/en-us/azure/search/search-security-api-keys).
Note that you will need an admin key to index documents (query keys only work for queries).

```python
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchIndexClient

credential = AzureKeyCredential("<api key>")

client = SearchIndexClient(endpoint="<service endpoint>",
                           index_name="<index name>",
                           credential=credential)
```

## Examples

### Create an index
Create a new index
```python
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchServiceClient, CorsOptions, Index, ScoringProfile
client = SearchServiceClient(service_endpoint, AzureKeyCredential(key))
name = "hotels"
    fields = [
        {
            "name": "hotelId",
            "type": "Edm.String",
            "key": True,
            "searchable": False
        },
        {
            "name": "baseRate",
            "type": "Edm.Double"
        }]
    cors_options = CorsOptions(allowed_origins=["*"], max_age_in_seconds=60)
    scoring_profiles = []
    index = Index(
        name=name,
        fields=fields,
        scoring_profiles=scoring_profiles,
        cors_options=cors_options)

    result = client.create_index(index)
```

### Upload documents to an index
Add documents (or update existing ones), e.g add a new document for a new hotel:
```python
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchIndexClient
search_client = SearchIndexClient(service_endpoint, index_name, AzureKeyCredential(key))

DOCUMENT = {
    'Category': 'Hotel',
    'HotelId': '1000',
    'Rating': 4.0,
    'Rooms': [],
    'HotelName': 'Azure Inn',
}

result = search_client.upload_documents(documents=[DOCUMENT])

print("Upload of new document succeeded: {}".format(result[0].succeeded))
```

### Retrieve a specific document from an index
Get a specific document from the index, e.f. obtain the document for hotel "23":
```python
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchIndexClient
search_client = SearchIndexClient(service_endpoint, index_name, AzureKeyCredential(key))

result = search_client.get_document(key="23")

print("Details for hotel '23' are:")
print("        Name: {}".format(result["HotelName"]))
print("      Rating: {}".format(result["Rating"]))
print("    Category: {}".format(result["Category"]))
```

### Perform a simple text search on documents
Search the entire index or documents matching a simple search text, e.g. find
hotels with the text "spa":
```python
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchIndexClient
search_client = SearchIndexClient(service_endpoint, index_name, AzureKeyCredential(key))

results = search_client.search(query="spa")

print("Hotels containing 'spa' in the name (or other fields):")
for result in results:
    print("    Name: {} (rating {})".format(result["HotelName"], result["Rating"]))
```

### Get search suggestions

Get search suggestions for related terms, e.g. find search suggestions for
the term "coffee":
```python
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchIndexClient, SuggestQuery
search_client = SearchIndexClient(service_endpoint, index_name, AzureKeyCredential(key))

query = SuggestQuery(search_text="coffee", suggester_name="sg")

results = search_client.suggest(query=query)

print("Search suggestions for 'coffee'")
for result in results:
    hotel = search_client.get_document(key=result["HotelId"])
    print("    Text: {} for Hotel: {}".format(repr(result["text"]), hotel["HotelName"]))
```

## Troubleshooting

### General

The Azure Cognitive Search client will raise exceptions defined in [Azure Core][azure_core].

### Logging

This library uses the standard [logging][python_logging] library for logging.
Basic information about HTTP sessions (URLs, headers, etc.) is logged at INFO
level.

etailed DEBUG level logging, including request/response bodies and unredacted
headers, can be enabled on a client with the `logging_enable` keyword argument:
```python
import sys
import logging
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchIndexClient

# Create a logger for the 'azure' SDK
logger = logging.getLogger('azure')
logger.setLevel(logging.DEBUG)

# Configure a console output
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

# This client will log detailed information about its HTTP sessions, at DEBUG level
search_client = SearchIndexClient(service_endpoint, index_name, AzureKeyCredential(key), logging_enable=True)
```

Similarly, `logging_enable` can enable detailed logging for a single operation,
even when it isn't enabled for the client:
```python
result =  search_client.search(query="spa", logging_enable=True)
```

## Next steps

### Additional documentation

For more extensive documentation on Cognitive Search, see the [Azure Cognitive Search documentation](https://docs.microsoft.com/en-us/azure/search/) on docs.microsoft.com.

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit [cla.microsoft.com][cla].

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct][code_of_conduct]. For more information see the [Code of Conduct FAQ][coc_faq] or contact [opencode@microsoft.com][coc_contact] with any additional questions or comments.

## Related projects

* [Microsoft Azure SDK for Python](https://github.com/Azure/azure-sdk-for-python)

<!-- LINKS -->

![Impressions](https://azure-sdk-impressions.azurewebsites.net/api/impressions/azure-sdk-for-python%2Fsdk%2Fsearch%2Fazure-search-documents%2FREADME.png)

[azure_cli]: https://docs.microsoft.com/cli/azure
[azure_core]: ../../core/azure-core/README.md
[azure_sub]: https://azure.microsoft.com/free/
[search_resource]: https://docs.microsoft.com/en-us/azure/search/search-create-service-portal
[azure_portal]: https://portal.azure.com

[python_logging]: https://docs.python.org/3.5/library/logging.html

[cla]: https://cla.microsoft.com
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[coc_faq]: https://opensource.microsoft.com/codeofconduct/faq/
[coc_contact]: mailto:opencode@microsoft.com
