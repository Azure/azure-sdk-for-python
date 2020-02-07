# Azure Search Index Client Python SDK

Azure Cognitive Search is a fully managed cloud search service that provides a rich search experience to custom applications. The service provides a REST API with operations that create and manage indexes, load data, implement search features, execute queries, and handle results.

This document descibes a Python SDK for Azure Search. The API provides a primary `SearchIndexClient` that implments all of the support REST operations of the service. Since the data in the index may not have a schema, documents and results are represented at simple (JSON) dicts. CRUD operations may be batched using an `IndexOperationBatch` class.

*NOTE: This document borrows heavily from the existing work for the [Java Track 2 API for Azure Search](https://apiview.dev/Assemblies/Review/2abf935de65e4187964bea5b817872d6#com.azure.search.SearchIndexClient)*

## Implementation Considerations

### POST/GET Variants

Some of the service calls offer GET vs POST variants, with guidance similar to the following:

> **When to use POST instead of GET**
>
>When you use HTTP GET to call Suggestions, the length of the request URL cannot exceed 8 KB. This length is usually enough for most applications. However, some applications produce very large queries, specifically when OData filter expressions are used. For these applications, HTTP POST is a better choice because it allows larger filters than GET. With POST, the number of clauses in a filter is the limiting factor, not the size of the raw filter string since the request size limit for POST is approximately 16 MB.

In the generated Python API this is reflected in separate methods pairs such as `suggest_get` and `suggestpost`. This GET/POST dichotomy may be unfamiliar or confusing to many users, and does not seem like a useful distinction to directly expose in the user-facing API. Options incude:

* Attempt to automatically choose the variant to use based on the length of the generated query string.
* Always only use one of the variants (e.g. POST since it can accommodate longer queries).
* Expose two explicit variants through a flag, using terminology that may be more semantically meaningful to users, e.g.
  ```python
  client.get_search_results(search_text="...", mode="simple")   # GET
  client.get_search_results(search_text="...", mode="full")     # POST
  ```

*NOTE: Response from Bruce on this matter: "always use POST"*

### Control Information Leakage

There is a codegen bug:

> whereby a property defined alongside "additionalProperties" in the Swagger was nevertheless ending up in the dictionary (it's called @search.score) during deserialization.
>
> In general we need to be careful that no control information (represented as OData annotations starting with @) ends up in the dict that represents the document itself.

API methods that return document dicts must take care to filter these keys/values out before returning to users.

Bruce notes that `SeachIndexClient` operations should set a header
```
"Accept": "application/json;odata.metadata=none"
```
to suppress these values being returned in the first place.

### Lucene Search Query Text

The ``search_text`` field of the service accepts Lucene query strings, which may of two
formats: simple or full.

Propose that all search query text, e.g. ``"wifi AND parking NOT luxury"``
simply be supplied as-is by users. In this context an API is more likely to
get in the way, rather than provide useful structure for users to rely on.

## Design

### `SearchApiKeyCredential` API

The Azure Search service uses an HTTP header `"api-key"` to authenticate. This class abstracts the credential to provide room to support other methods of authentication that may become available in the future.

```python
azure.search.SearchApiKeyCredential(api_key)

# read only property
SearchAPIKeyCredential.api_key: str

def SearchAPIKeyCredential.update_key(key: str) -> None:
```

### `IndexOperationBatch` API

Azure Search Service affords the ability to batch CRUD-type operations, returning list of status results corresponding to each individual operation. This class represents a batch of CRUD operations to perfom on an Azure search index. The order of operations is maintained according to the order that a user invokes the methods on an instance.

*NOTE: The acceptibility of alternate CRUD verbs, specific to Azure Search, was discussed in the ADP Arch Board meeting **Azure Search for Java - 10/2/2019***

```python
azure.search.IndexOperationBatch()

class IndexOperationBatch:
    def add_upload_documents(self, documents: List[dict]) -> None:
    def add_delete_documents(self, documents: List[dict]) -> None:
    def add_merge_documents(self, documents: List[dict]) -> None:
    def add_merge_or_upload_documents(self, documents: List[dict]) -> None:
```

### `SearchIndexClient` API

The search index client is the primary interface for users to interact with an an Azure Search index from the Python API. It accepts credentials and information about the index on creation, and offers methods for all service REST operations.

```python
azure.search.SearchIndexClient(
    search_service_name: str,
    index_name: str,
    credential: SearchApiKeyCredential
)

class SearchIndexClient:

    def get_document_count(self) -> int:

    def get_document(
        self,
        key: str,
        selected_fields: List[str] = None
    ) -> dict:


    def get_search_results(
        self,
        search_text: str,
        **kwargs
    ) -> Iterable[dict]:


    def get_suggestions(
        self,
        search_text: str,
        suggester_name: str,
        **kwargs
    ) -> List[dict]:


    def get_autocompletions(
        self,
        search_text: str,
        suggester_name: str,
        **kwargs
    ) -> List[dict]:


    def upload_documents(
        self,
        documents: List[dict],
        **kwargs
    ) -> List[IndexingResult]:


    def delete_documents(
        self,
        documents: List[dict],
        **kwargs
    ) -> List[IndexingResult]:


    def merge_documents(
        self,
        documents: List[dict],
        **kwargs
    ) -> List[IndexingResult]:


    def merge_or_upload_documents(
        self,
        documents: List[dict],
        **kwargs
    ) -> List[IndexingResult]:

    def batch_update(
        self,
        batch: IndexOperationBatch,
        **kwargs
    ) -> List[IndexingResult]:
```

### `SearchQuery` API

In addition to simple text searches, Azure Search supports more sophisticated
search requests. These include ODATA queries for filtering, selecting, and
ordering result and Lucene queries for search.

```python
azure.search.SearchQuery(search_text: str, **kwargs)

class SearchQuery:
    def filter(expression:str) -> None:
    def orderby(*fields: List[str]) -> None:
    def select(*fields: List[str]) -> None:
```

## Scenarios

### 1. Get the number of documents in an Azure search index

```python
from azure.search import SearchApiKeyCredential, SearchIndexClient

client = SearchIndexClient(
    search_service_name="my-search-service",
    index_name="hotels-sample-index",
    credential=SearchApiKeyCredential(api_key="xxxxxxxxx")
)

print(client.get_document_count())
```

### 2. Get a specific document in an Azure search index

```python
from azure.search import SearchApiKeyCredential, SearchIndexClient

client = SearchIndexClient(
    search_service_name="my-search-service",
    index_name="hotels-sample-index",
    credential=SearchApiKeyCredential(api_key="xxxxxxxxx")
)

result = client.get_document(key="10")

print(result)
```

### 3. Search for documents in an Azure search index with simple text

```python
from azure.search import SearchApiKeyCredential, SearchIndexClient

client = SearchIndexClient(
    search_service_name="my-search-service",
    index_name="hotels-sample-index",
    credential=SearchApiKeyCredential(api_key="xxxxxxxxx")
)

results = client.get_search_results(search_text="WiFi")

for doc in results:
    print(doc['Description'])
    print(doc['Type'])
    print(doc['BaseRate'])
```

### 3. Filter results Azure search index

```python
from azure.search import SearchApiKeyCredential, SearchIndexClient, SearchQuery

client = SearchIndexClient(
    search_service_name="my-search-service",
    index_name="hotels-sample-index",
    credential=SearchApiKeyCredential(api_key="xxxxxxxxx")
)

query = SearchQuery(
    search_text="WiFi",
    highlightPreTag="<em>",
    highlightPostTag="</em>")

# Base API accepts strings, templating/substitution TBD
query.filter("Address/City eq 'Portland and Address/Country eq 'US'"))
query.orderby("Rating desc", "geo.distance(FOO, geography'POINT(10 20)') asc")
query.select("HotelId", "HotelName", "Rating")

results = client.get_search_results(search_query=query)

for doc in results:
    print(doc['HotelName'])
    print(doc['Rating'])
```

### 5. Get a list of search suggestions

```python
from azure.search import SearchApiKeyCredential, SearchIndexClient

client = SearchIndexClient(
    search_service_name="my-search-service",
    index_name="hotels-sample-index",
    credential=SearchApiKeyCredential(api_key="xxxxxxxxx")
)

results = client.get_suggestions(search_text="cof", suggester_name="sg")

for result in results:
    print(result['text'])
```

### 6. Get a list of search auto-completions

```python
from azure.search import SearchApiKeyCredential, SearchIndexClient

client = SearchIndexClient(
    search_service_name="my-search-service",
    index_name="hotels-sample-index",
    credential=SearchApiKeyCredential(api_key="xxxxxxxxx")
)

results = client.get_autocompletions(search_text="cof", suggester_name="sg")

for result in results:
    print(result['text'])
    print(result['query_plus_text'])
```

### 7. Upload documents to an Azure Search index

```python
from azure.search import SearchApiKeyCredential, SearchIndexClient

client = SearchIndexClient(
    search_service_name="my-search-service",
    index_name="hotels-sample-index",
    credential=SearchApiKeyCredential(api_key="xxxxxxxxx")
)

documents = [
    { "id": "10", "description": "new item" },
    { "id": "11", "description": "another new item" },
]

results = client.upload_documents(documents)

for result in results:
    print(result.status_code)
```

### 8. Delete documents from an Azure Search index

```python
from azure.search import SearchApiKeyCredential, SearchIndexClient

client = SearchIndexClient(
    search_service_name="my-search-service",
    index_name="hotels-sample-index",
    credential=SearchApiKeyCredential(api_key="xxxxxxxxx")
)

documents = [
    { "id": "10" },
    { "id": "11" },
]

results = client.delete_documents(documents)

for result in results:
    print(result.status_code)
```

### 9. Merge new fields in an existing document

```python
from azure.search import SearchApiKeyCredential, SearchIndexClient

client = SearchIndexClient(
    search_service_name="my-search-service",
    index_name="hotels-sample-index",
    credential=SearchApiKeyCredential(api_key="xxxxxxxxx")
)

documents = [
    { "id": "10", "description": None },
    { "id": "11", "description": "new item description" },
]

results = client.merge_documents(documents)

for result in results:
    print(result.status_code)
```

### 10. Merge or upload a document in an Azure Search index

```python
from azure.search import SearchApiKeyCredential, SearchIndexClient

client = SearchIndexClient(
    search_service_name="my-search-service",
    index_name="hotels-sample-index",
    credential=SearchApiKeyCredential(api_key="xxxxxxxxx")
)

documents = [
    { "id": "11", "description": None },
    { "id": "12", "description": "new item description" },
]

results = client.merge_documents(documents)

for result in results:
    print(result.status_code)
```

### 11. Batch CRUD operations on documents

```python
from azure.search import IndexOperationBatch, SearchApiKeyCredential, SearchIndexClient

client = SearchIndexClient(
    search_service_name="my-search-service",
    index_name="hotels-sample-index",
    credential=SearchApiKeyCredential(api_key="xxxxxxxxx")
)

work = IndexOperationBatch()
batch.add_upload_document([{ "id": "10", "description": "new item" }])
batch.add_delete_document([{ "id": "8"}, { "id": "9" }])
batch.add_merge_document([{ "id": "10", None }])

results = client.batch_update(work)

for result in results:
    print(result.status_code)
```