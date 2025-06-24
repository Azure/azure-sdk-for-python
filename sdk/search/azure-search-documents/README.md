# Azure AI Search client library for Python

[Azure AI Search](https://docs.microsoft.com/azure/search/) (formerly known as "Azure Cognitive Search") is an AI-powered information retrieval platform that helps developers build rich search experiences and generative AI apps that combine large language models with enterprise data.

Azure AI Search is well suited for the following application scenarios:

* Consolidate varied content types into a single searchable index.
  To populate an index, you can push JSON documents that contain your content,
  or if your data is already in Azure, create an indexer to pull in data
  automatically.
* Attach skillsets to an indexer to create searchable content from images
  and unstructured documents. A skillset leverages APIs from Azure AI Services
  for built-in OCR, entity recognition, key phrase extraction, language
  detection, text translation, and sentiment analysis. You can also add
  custom skills to integrate external processing of your content during
  data ingestion.
* In a search client application, implement query logic and user experiences
  similar to commercial web search engines and chat-style apps.

Use the Azure.Search.Documents client library to:

* Submit queries using vector, keyword, and hybrid query forms.
* Implement filtered queries for metadata, geospatial search, faceted navigation, 
  or to narrow results based on filter criteria.
* Create and manage search indexes.
* Upload and update documents in the search index.
* Create and manage indexers that pull data from Azure into an index.
* Create and manage skillsets that add AI enrichment to data ingestion.
* Create and manage analyzers for advanced text analysis or multi-lingual content.
* Optimize results through semantic ranking and scoring profiles to factor in business logic or freshness.

[Source code](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/search/azure-search-documents)
| [Package (PyPI)](https://pypi.org/project/azure-search-documents/)
| [Package (Conda)](https://anaconda.org/microsoft/azure-search-documents/)
| [API reference documentation](https://azuresdkdocs.blob.core.windows.net/$web/python/azure-search-documents/latest/index.html)
| [Product documentation](https://docs.microsoft.com/azure/search/search-what-is-azure-search)
| [Samples](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples)

## Getting started

### Install the package

Install the Azure AI Search client library for Python with [pip](https://pypi.org/project/pip/):

```bash
pip install azure-search-documents
```

### Prerequisites

* Python 3.8 or later is required to use this package.
* You need an [Azure subscription][azure_sub] and an
[Azure AI Search service][search_resource] to use this package.

To create a new search service, you can use the [Azure portal][create_search_service_docs], [Azure PowerShell][create_search_service_ps], or the [Azure CLI][create_search_service_cli].

```Powershell
az search service create --name <mysearch> --resource-group <mysearch-rg> --sku free --location westus
```

See [choosing a pricing tier](https://docs.microsoft.com/azure/search/search-sku-tier)
 for more information about available options.

### Authenticate the client

To interact with the search service, you'll need to create an instance of the appropriate client class: `SearchClient` for searching indexed documents, `SearchIndexClient` for managing indexes, or `SearchIndexerClient` for crawling data sources and loading search documents into an index. To instantiate a client object, you'll need an **endpoint** and **Azure roles** or an **API key**. You can refer to the documentation for more information on [supported authenticating approaches](https://learn.microsoft.com/azure/search/search-security-overview#authentication) with the search service.

#### Get an API Key

An API key can be an easier approach to start with because it doesn't require pre-existing role assignments.

You can get the **endpoint** and an **API key** from the Search service in the [Azure portal](https://portal.azure.com/). Please refer the [documentation](https://docs.microsoft.com/azure/search/search-security-api-keys) for instructions on how to get an API key.

Alternatively, you can use the following [Azure CLI](https://learn.microsoft.com/cli/azure/) command to retrieve the API key from the Search service:

```Powershell
az search admin-key show --service-name <mysearch> --resource-group <mysearch-rg>
```

There are two types of keys used to access your search service: **admin**
*(read-write)* and **query** *(read-only)* keys.  Restricting access and
operations in client apps is essential to safeguarding the search assets on your
service.  Always use a query key rather than an admin key for any query
originating from a client app.

*Note: The example Azure CLI snippet above retrieves an admin key so it's easier
to get started exploring APIs, but it should be managed carefully.*

#### Create a SearchClient

To instantiate the `SearchClient`, you'll need the **endpoint**, **API key** and **index name**:

<!-- SNIPPET:sample_authentication.create_search_client_with_key -->

```python
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
index_name = os.environ["AZURE_SEARCH_INDEX_NAME"]
key = os.environ["AZURE_SEARCH_API_KEY"]

search_client = SearchClient(service_endpoint, index_name, AzureKeyCredential(key))
```

<!-- END SNIPPET -->

#### Create a client using Microsoft Entra ID authentication

You can also create a `SearchClient`, `SearchIndexClient`, or `SearchIndexerClient` using Microsoft Entra ID authentication. Your user or service principal must be assigned the "Search Index Data Reader" role.
Using the [DefaultAzureCredential](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity/README.md#defaultazurecredential) you can authenticate a service using Managed Identity or a service principal, authenticate as a developer working on an application, and more all without changing code. Please refer the [documentation](https://learn.microsoft.com/azure/search/search-security-rbac?tabs=config-svc-portal%2Croles-portal%2Ctest-portal%2Ccustom-role-portal%2Cdisable-keys-portal) for instructions on how to connect to Azure AI Search using Azure role-based access control (Azure RBAC).

Before you can use the `DefaultAzureCredential`, or any credential type from [Azure.Identity](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity/README.md), you'll first need to [install the Azure.Identity package](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity/README.md#install-the-package).

To use `DefaultAzureCredential` with a client ID and secret, you'll need to set the `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, and `AZURE_CLIENT_SECRET` environment variables; alternatively, you can pass those values
to the `ClientSecretCredential` also in Azure.Identity.

Make sure you use the right namespace for `DefaultAzureCredential` at the top of your source file:

```python
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient

service_endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
index_name = os.getenv("AZURE_SEARCH_INDEX_NAME")
credential = DefaultAzureCredential()

search_client = SearchClient(service_endpoint, index_name, credential)
```

## Key concepts

An Azure AI Search service contains one or more indexes that provide
persistent storage of searchable data in the form of JSON documents.  _(If
you're brand new to search, you can make a very rough analogy between
indexes and database tables.)_  The Azure.Search.Documents client library
exposes operations on these resources through three main client types.

* `SearchClient` helps with:
  * [Searching](https://docs.microsoft.com/azure/search/search-lucene-query-architecture)
    your indexed documents using [vector queries](https://learn.microsoft.com/azure/search/vector-search-how-to-query),
    [keyword queries](https://learn.microsoft.com/azure/search/search-query-create)
    and [hybrid queries](https://learn.microsoft.com/azure/search/hybrid-search-how-to-query)
  * [Vector query filters](https://learn.microsoft.com/azure/search/vector-search-filters) and [Text query filters](https://learn.microsoft.com/azure/search/search-filters)
  * [Semantic ranking](https://learn.microsoft.com/azure/search/semantic-how-to-query-request) and [scoring profiles](https://learn.microsoft.com/azure/search/index-add-scoring-profiles) for boosting relevance
  * [Autocompleting](https://docs.microsoft.com/rest/api/searchservice/autocomplete)
    partially typed search terms based on documents in the index
  * [Suggesting](https://docs.microsoft.com/rest/api/searchservice/suggestions)
    the most likely matching text in documents as a user types
  * [Adding, Updating or Deleting Documents](https://docs.microsoft.com/rest/api/searchservice/addupdate-or-delete-documents)
    documents from an index

* `SearchIndexClient` allows you to:
  * [Create, delete, update, or configure a search index](https://docs.microsoft.com/rest/api/searchservice/index-operations)
  * [Declare custom synonym maps to expand or rewrite queries](https://docs.microsoft.com/rest/api/searchservice/synonym-map-operations)
<!--   * Most of the `SearchServiceClient` functionality is not yet available in our current preview -->

* `SearchIndexerClient` allows you to:
  * [Start indexers to automatically crawl data sources](https://docs.microsoft.com/rest/api/searchservice/indexer-operations)
  * [Define AI powered Skillsets to transform and enrich your data](https://docs.microsoft.com/rest/api/searchservice/skillset-operations)

Azure AI Search provides two powerful features: **semantic ranking** and **vector search**.

**Semantic ranking** enhances the quality of search results for text-based queries. By enabling semantic ranking on your search service, you can improve the relevance of search results in two ways:
- It applies secondary ranking to the initial result set, promoting the most semantically relevant results to the top.
- It extracts and returns captions and answers in the response, which can be displayed on a search page to enhance the user's search experience.

To learn more about semantic ranking, you can refer to the [documentation](https://learn.microsoft.com/azure/search/vector-search-overview).

**Vector search** is an information retrieval technique that uses numeric representations of searchable documents and query strings. By searching for numeric representations of content that are most similar to the numeric query, vector search can find relevant matches, even if the exact terms of the query are not present in the index. Moreover, vector search can be applied to various types of content, including images and videos and translated text, not just same-language text.

To learn how to index vector fields and perform vector search, you can refer to the [sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_vector_search.py). This sample provides detailed guidance on indexing vector fields and demonstrates how to perform vector search.

Additionally, for more comprehensive information about vector search, including its concepts and usage, you can refer to the [documentation](https://learn.microsoft.com/azure/search/vector-search-overview). The documentation provides in-depth explanations and guidance on leveraging the power of vector search in Azure AI Search.

_The `Azure.Search.Documents` client library (v1) provides APIs for data plane operations. The
previous `Microsoft.Azure.Search` client library (v10) is now retired. It has many similar looking APIs, so please be careful to avoid confusion when exploring online resources. A good rule of thumb is to check for the namespace
`Azure.Search.Documents;` when you're looking for API reference.

## Examples

The following examples all use a simple [Hotel data set](https://github.com/Azure-Samples/azure-search-sample-data/blob/master/README.md)
that you can [import into your own index from the Azure portal.](https://docs.microsoft.com/azure/search/search-get-started-portal#step-1---start-the-import-data-wizard-and-create-a-data-source)
These are just a few of the basics - please [check out our Samples](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples) for
much more.


* [Querying](#querying)
* [Creating an index](#creating-an-index)
* [Adding documents to your index](#adding-documents-to-your-index)
* [Retrieving a specific document from your index](#retrieving-a-specific-document-from-your-index)
* [Async APIs](#async-apis)


### Querying

Let's start by importing our namespaces.

```python
import os
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
```

We'll then create a `SearchClient` to access our hotels search index.

```python
index_name = "hotels"
# Get the service endpoint and API key from the environment
endpoint = os.environ["SEARCH_ENDPOINT"]
key = os.environ["SEARCH_API_KEY"]

# Create a client
credential = AzureKeyCredential(key)
client = SearchClient(endpoint=endpoint,
                      index_name=index_name,
                      credential=credential)
```

Let's search for a "luxury" hotel.

```python
results = client.search(search_text="luxury")

for result in results:
    print("{}: {})".format(result["hotelId"], result["hotelName"]))
```


### Creating an index

You can use the `SearchIndexClient` to create a search index. Fields can be
defined using convenient `SimpleField`, `SearchableField`, or `ComplexField`
models. Indexes can also define suggesters, lexical analyzers, and more.

<!-- SNIPPET:sample_index_crud_operations.create_index -->

```python
client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))
name = "hotels"
fields = [
    SimpleField(name="hotelId", type=SearchFieldDataType.String, key=True),
    SimpleField(name="baseRate", type=SearchFieldDataType.Double),
    SearchableField(name="description", type=SearchFieldDataType.String, collection=True),
    ComplexField(
        name="address",
        fields=[
            SimpleField(name="streetAddress", type=SearchFieldDataType.String),
            SimpleField(name="city", type=SearchFieldDataType.String),
        ],
        collection=True,
    ),
]
cors_options = CorsOptions(allowed_origins=["*"], max_age_in_seconds=60)
scoring_profiles: List[ScoringProfile] = []
index = SearchIndex(name=name, fields=fields, scoring_profiles=scoring_profiles, cors_options=cors_options)

result = client.create_index(index)
```

<!-- END SNIPPET -->

### Adding documents to your index

You can `Upload`, `Merge`, `MergeOrUpload`, and `Delete` multiple documents from
an index in a single batched request.  There are
[a few special rules for merging](https://docs.microsoft.com/rest/api/searchservice/addupdate-or-delete-documents#document-actions)
to be aware of.

<!-- SNIPPET:sample_crud_operations.upload_document -->

```python
DOCUMENT = {
    "category": "Hotel",
    "hotelId": "1000",
    "rating": 4.0,
    "rooms": [],
    "hotelName": "Azure Inn",
}

result = search_client.upload_documents(documents=[DOCUMENT])

print("Upload of new document succeeded: {}".format(result[0].succeeded))
```

<!-- END SNIPPET -->

### Authenticate in a National Cloud

To authenticate in a [National Cloud](https://docs.microsoft.com/azure/active-directory/develop/authentication-national-cloud), you will need to make the following additions to your client configuration:

- Set the `AuthorityHost` in the credential options or via the `AZURE_AUTHORITY_HOST` environment variable
- Set the `audience` in `SearchClient`, `SearchIndexClient`, or `SearchIndexerClient`

```python
# Create a SearchClient that will authenticate through AAD in the China national cloud.
import os
from azure.identity import DefaultAzureCredential, AzureAuthorityHosts
from azure.search.documents import SearchClient

index_name = "hotels"
endpoint = os.environ["SEARCH_ENDPOINT"]
key = os.environ["SEARCH_API_KEY"]
credential = DefaultAzureCredential(authority=AzureAuthorityHosts.AZURE_CHINA)

search_client = SearchClient(endpoint, index_name, credential=credential, audience="https://search.azure.cn")
```

### Retrieving a specific document from your index

In addition to querying for documents using keywords and optional filters,
you can retrieve a specific document from your index if you already know the
key. You could get the key from a query, for example, and want to show more
information about it or navigate your customer to that document.

<!-- SNIPPET:sample_get_document.get_document -->

```python
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

search_client = SearchClient(service_endpoint, index_name, AzureKeyCredential(key))

result = search_client.get_document(key="23")

print("Details for hotel '23' are:")
print("        Name: {}".format(result["hotelName"]))
print("      Rating: {}".format(result["rating"]))
print("    Category: {}".format(result["category"]))
```

<!-- END SNIPPET -->

### Async APIs

This library includes a complete async API. To use it, you must
first install an async transport, such as [aiohttp](https://pypi.org/project/aiohttp/).
See
[azure-core documentation](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/README.md#transport)
for more information.

<!-- SNIPPET:sample_simple_query_async.simple_query_async -->

```python
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.aio import SearchClient

search_client = SearchClient(service_endpoint, index_name, AzureKeyCredential(key))

async with search_client:
    results = await search_client.search(search_text="spa")

    print("Hotels containing 'spa' in the name (or other fields):")
    async for result in results:
        print("    Name: {} (rating {})".format(result["hotelName"], result["rating"]))
```

<!-- END SNIPPET -->

## Troubleshooting

### General

The Azure AI Search client will raise exceptions defined in [Azure Core][azure_core].

### Logging

This library uses the standard [logging][python_logging] library for logging.
Basic information about HTTP sessions (URLs, headers, etc.) is logged at INFO
level.

Detailed DEBUG level logging, including request/response bodies and unredacted
headers, can be enabled on a client with the `logging_enable` keyword argument:
```python
import sys
import logging
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

# Create a logger for the 'azure' SDK
logger = logging.getLogger('azure')
logger.setLevel(logging.DEBUG)

# Configure a console output
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

# This client will log detailed information about its HTTP sessions, at DEBUG level
client = SearchClient("<service endpoint>", "<index_name>", AzureKeyCredential("<api key>"), logging_enable=True)

```

Similarly, `logging_enable` can enable detailed logging for a single operation,
even when it isn't enabled for the client:
```python
result =  client.search(search_text="spa", logging_enable=True)
```

## Next steps

* Go further with Azure.Search.Documents and our [https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/search/azure-search-documents/samples](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples)
* Read more about the [Azure AI Search service](https://docs.microsoft.com/azure/search/search-what-is-azure-search)

## Contributing

See our [Search CONTRIBUTING.md][search_contrib] for details on building,
testing, and contributing to this library.

This project welcomes contributions and suggestions.  Most contributions require
you to agree to a Contributor License Agreement (CLA) declaring that you have
the right to, and actually do, grant us the rights to use your contribution. For
details, visit [cla.microsoft.com][cla].

This project has adopted the [Microsoft Open Source Code of Conduct][code_of_conduct].
For more information, see the [Code of Conduct FAQ][coc_faq]
or contact [opencode@microsoft.com][coc_contact] with any
additional questions or comments.

![Impressions](https://azure-sdk-impressions.azurewebsites.net/api/impressions/azure-sdk-for-net%2Fsdk%2Fsearch%2FAzure.Search.Documents%2FREADME.png)

## Related projects

* [Microsoft Azure SDK for Python](https://github.com/Azure/azure-sdk-for-python)

<!-- LINKS -->

![Impressions](https://azure-sdk-impressions.azurewebsites.net/api/impressions/azure-sdk-for-python%2Fsdk%2Fsearch%2Fazure-search-documents%2FREADME.png)

[azure_cli]: https://docs.microsoft.com/cli/azure
[azure_core]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/README.md
[azure_sub]: https://azure.microsoft.com/free/
[search_resource]: https://docs.microsoft.com/azure/search/search-create-service-portal
[azure_portal]: https://portal.azure.com

[create_search_service_docs]: https://docs.microsoft.com/azure/search/search-create-service-portal
[create_search_service_ps]: https://docs.microsoft.com/azure/search/search-manage-powershell#create-or-delete-a-service
[create_search_service_cli]: https://docs.microsoft.com/cli/azure/search/service?view=azure-cli-latest#az-search-service-create
[search_contrib]: https://github.com/Azure/azure-sdk-for-python/blob/main/CONTRIBUTING.md
[python_logging]: https://docs.python.org/3.5/library/logging.html

[cla]: https://cla.microsoft.com
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[coc_faq]: https://opensource.microsoft.com/codeofconduct/faq/
[coc_contact]: mailto:opencode@microsoft.com
