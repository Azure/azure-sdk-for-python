# Azure Cognitive Search client library for Python

[Azure Cognitive Search](https://docs.microsoft.com/azure/search/) is a
search-as-a-service cloud solution that gives developers APIs and tools
for adding a rich search experience over private, heterogeneous content
in web, mobile, and enterprise applications.

The Azure Cognitive Search service is well suited for the following
 application scenarios:

* Consolidate varied content types into a single searchable index.
  To populate an index, you can push JSON documents that contain your content,
  or if your data is already in Azure, create an indexer to pull in data
  automatically.
* Attach skillsets to an indexer to create searchable content from images
  and large text documents. A skillset leverages AI from Cognitive Services
  for built-in OCR, entity recognition, key phrase extraction, language
  detection, text translation, and sentiment analysis. You can also add
  custom skills to integrate external processing of your content during
  data ingestion.
* In a search client application, implement query logic and user experiences
  similar to commercial web search engines.

Use the Azure.Search.Documents client library to:

* Submit queries for simple and advanced query forms that include fuzzy
  search, wildcard search, regular expressions.
* Implement filtered queries for faceted navigation, geospatial search,
  or to narrow results based on filter criteria.
* Create and manage search indexes.
* Upload and update documents in the search index.
* Create and manage indexers that pull data from Azure into an index.
* Create and manage skillsets that add AI enrichment to data ingestion.
* Create and manage analyzers for advanced text analysis or multi-lingual content.
* Optimize results through scoring profiles to factor in business logic or freshness.

[Source code](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/search/azure-search-documents)
| [Package (PyPI)](https://pypi.org/project/azure-search-documents/)
| [Package (Conda)](https://anaconda.org/microsoft/azure-search-documents/)
| [API reference documentation](https://azuresdkdocs.blob.core.windows.net/$web/python/azure-search-documents/latest/index.html)
| [Product documentation](https://docs.microsoft.com/azure/search/search-what-is-azure-search)
| [Samples](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples)

## _Disclaimer_

_Azure SDK Python packages support for Python 2.7 has ended 01 January 2022. For more information and questions, please refer to https://github.com/Azure/azure-sdk-for-python/issues/20691_

## Getting started

### Install the package

Install the Azure Cognitive Search client library for Python with [pip](https://pypi.org/project/pip/):

```bash
pip install azure-search-documents
```

### Prerequisites

* Python 3.7 or later is required to use this package.
* You need an [Azure subscription][azure_sub] and a
[Azure Cognitive Search service][search_resource] to use this package.

To create a new search service, you can use the [Azure portal][create_search_service_docs], [Azure PowerShell][create_search_service_ps], or the [Azure CLI][create_search_service_cli].

```Powershell
az search service create --name <mysearch> --resource-group <mysearch-rg> --sku free --location westus
```

See [choosing a pricing tier](https://docs.microsoft.com/azure/search/search-sku-tier)
 for more information about available options.

### Authenticate the client

To interact with the Search service, you'll need to create an instance of the appropriate client class: `SearchClient` for searching indexed documents, `SearchIndexClient` for managing indexes, or `SearchIndexerClient` for crawling data sources and loading search documents into an index. To instantiate a client object, you'll need an **endpoint** and an **API key**. You can refer to the documentation for more information on [supported authenticating approaches](https://learn.microsoft.com/azure/search/search-security-overview#authentication) with the Search service.

#### Get an API Key

You can get the **endpoint** and an **API key** from the Search service in the [Azure Portal](https://portal.azure.com/). Please refer the [documentation](https://docs.microsoft.com/azure/search/search-security-api-keys) for instructions on how to get an API key.

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

#### Create a client using Azure Active Directory authentication

You can also create a `SearchClient`, `SearchIndexClient`, or `SearchIndexerClient` using Azure Active Directory (AAD) authentication. Your user or service principal must be assigned the "Search Index Data Reader" role.
Using the [DefaultAzureCredential](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity/README.md#defaultazurecredential) you can authenticate a service using Managed Identity or a service principal, authenticate as a developer working on an application, and more all without changing code. Please refer the [documentation](https://learn.microsoft.com/azure/search/search-security-rbac?tabs=config-svc-portal%2Croles-portal%2Ctest-portal%2Ccustom-role-portal%2Cdisable-keys-portal) for instructions on how to connect to Azure Cognitive Search using Azure role-based access control (Azure RBAC).

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

An Azure Cognitive Search service contains one or more indexes that provide
persistent storage of searchable data in the form of JSON documents.  _(If
you're brand new to search, you can make a very rough analogy between
indexes and database tables.)_  The Azure.Search.Documents client library
exposes operations on these resources through two main client types.

* `SearchClient` helps with:
  * [Searching](https://docs.microsoft.com/azure/search/search-lucene-query-architecture)
    your indexed documents using
    [rich queries](https://docs.microsoft.com/azure/search/search-query-overview)
    and [powerful data shaping](https://docs.microsoft.com/azure/search/search-filters)
  * [Autocompleting](https://docs.microsoft.com/rest/api/searchservice/autocomplete)
    partially typed search terms based on documents in the index
  * [Suggesting](https://docs.microsoft.com/rest/api/searchservice/suggestions)
    the most likely matching text in documents as a user types
  * [Adding, Updating or Deleting Documents](https://docs.microsoft.com/rest/api/searchservice/addupdate-or-delete-documents)
    documents from an index

* `SearchIndexClient` allows you to:
  * [Create, delete, update, or configure a search index](https://docs.microsoft.com/rest/api/searchservice/index-operations)
  * [Declare custom synonym maps to expand or rewrite queries](https://docs.microsoft.com/rest/api/searchservice/synonym-map-operations)
  * Most of the `SearchServiceClient` functionality is not yet available in our current preview

* `SearchIndexerClient` allows you to:
  * [Start indexers to automatically crawl data sources](https://docs.microsoft.com/rest/api/searchservice/indexer-operations)
  * [Define AI powered Skillsets to transform and enrich your data](https://docs.microsoft.com/rest/api/searchservice/skillset-operations)

Azure Cognitive Search provides two powerful features: **Semantic Search** and **Vector Search**.

**Semantic Search** enhances the quality of search results for text-based queries. By enabling Semantic Search on your search service, you can improve the relevance of search results in two ways:
- It applies secondary ranking to the initial result set, promoting the most semantically relevant results to the top.
- It extracts and returns captions and answers in the response, which can be displayed on a search page to enhance the user's search experience.

To learn more about Semantic Search, you can refer to the [documentation](https://learn.microsoft.com/azure/search/vector-search-overview).

**Vector Search** is an information retrieval technique that overcomes the limitations of traditional keyword-based search. Instead of relying solely on lexical analysis and matching individual query terms, Vector Search utilizes machine learning models to capture the contextual meaning of words and phrases. It represents documents and queries as vectors in a high-dimensional space called an embedding. By understanding the intent behind the query, Vector Search can deliver more relevant results that align with the user's requirements, even if the exact terms are not present in the document. Moreover, Vector Search can be applied to various types of content, including images and videos, not just text.

To learn how to index vector fields and perform vector search, you can refer to the [sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_vector_search.py). This sample provides detailed guidance on indexing vector fields and demonstrates how to perform vector search.

Additionally, for more comprehensive information about Vector Search, including its concepts and usage, you can refer to the [documentation](https://learn.microsoft.com/azure/search/vector-search-overview). The documentation provides in-depth explanations and guidance on leveraging the power of Vector Search in Azure Cognitive Search.

_The `Azure.Search.Documents` client library (v1) is a brand new offering for
Python developers who want to use search technology in their applications.  There
is an older, fully featured `Microsoft.Azure.Search` client library (v10) with
many similar looking APIs, so please be careful to avoid confusion when
exploring online resources._

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

The Azure Cognitive Search client will raise exceptions defined in [Azure Core][azure_core].

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
* Watch a [demo or deep dive video](https://azure.microsoft.com/resources/videos/index/?services=search)
* Read more about the [Azure Cognitive Search service](https://docs.microsoft.com/azure/search/search-what-is-azure-search)

## Contributing

See our [Search CONTRIBUTING.md][search_contrib] for details on building,
testing, and contributing to this library.

This project welcomes contributions and suggestions.  Most contributions require
you to agree to a Contributor License Agreement (CLA) declaring that you have
the right to, and actually do, grant us the rights to use your contribution. For
details, visit [cla.microsoft.com][cla].

This project has adopted the [Microsoft Open Source Code of Conduct][code_of_conduct].
For more information see the [Code of Conduct FAQ][coc_faq]
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
