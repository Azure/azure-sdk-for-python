# Azure Search Index Client Python SDK

## Design

Azure Cognitive Search is a fully managed cloud search service that provides a rich search experience to custom applications. The service provides a REST API with operations that create and manage indexes, load data, implement search features, execute queries, and handle results.

This document descibes a Python SDK for Azure Search. The API provides a primary `SearchIndexClient` that implments all of the support REST operations of the service. Since the data in the index may not have a schema, documents and results are represented at simple (JSON) dicts. CRUD operations may be batched using an `IndexOperationBatch` class.

*NOTE: This document borrows heavily from the existing work for the [Java Track 2 API for Azure Search](https://apiview.dev/Assemblies/Review/2abf935de65e4187964bea5b817872d6#com.azure.search.SearchIndexClient)*

### Considerations

#### POST/GET Variants

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

### `SearchApiKeyCredential` API

The Azure Search service uses an HTTP header `"api-key"` to authenticate. This class abstracts the credential to provide room to support other methods of authentication that may become available in the future.

```python
azure.search.SearchApiKeyCredential(api_key)

# read only property
SearchAPIKeyCredential.api_key: str
```

### `IndexOperationBatch` API

Azure Search Service affords the ability to batch CRUD-type operations, returning list of status results corresponding to each individual operation. This class represents a batch of CRUD operations to perfom on an Azure search index. The order of operations is maintained according to the order that a user invokes the methods on an instance.

*NOTE: The acceptibility of alternate CRUD verbs, specific to Azure Search, was discussed in the ADP Arch Board meeting **Azure Search for Java - 10/2/2019***

```python
azure.search.IndexOperationBatch()

IndexOperationBatch.add_update_documnents(documents: List[dict])

IndexOperationBatch.add_delete_documents(documents: List[dict])

IndexOperationBatch.add_merge_documents(documents: List[dict])

IndexOperationBatch.add_merge_or_update_documents(documents: List[dict])
```

### `IndexOperationResult` API

This class records a status result for an individual CRUD operation on an Azure Search index.

```python
# read only properties
IndexOperationResult.key: str
IndexOperationResult.error_message: str
IndexOperationResult.succeeded: bool
IndexOperationResult.status_code: int
```

### `SearchIndexClient` API

The search index client is the primary interface for users to interact with an an Azure Search index from the Python API. It accepts credentials and information about the index on creation, and offers methods for all service REST operations.

```python
azure.search.SearchIndexClient(
    search_service_name: str,
    index_name: str,
    credential: SearchApiKeyCredential
)


SearchIndexClient.get_document_count() -> int


SearchIndexClient.get_document(
    key: str,
    selected_fields: List[str] = None
) -> dict


SearchIndexClient.get_search_results(
    search_text: str,
    **kwargs
) -> List[dict]


SearchIndexClient.get_suggestions(
    search_text: str,
    suggester_name: str,
    **kwargs
) -> List[dict]


SearchIndexClient.get_autocompletions(
    search_text: str,
    suggester_name: str,
    **kwargs
) -> List[dict]


SearchIndexClient.upload_documents(
    documents: List[dict],
    **kwargs
) -> List[IndexOperationResult]


SearchIndexClient.delete_documents(
    documents: List[dict],
    **kwargs
) -> List[IndexOperationResult]


SearchIndexClient.merge_documents(
    documents: List[dict],
    **kwargs
) -> List[IndexOperationResult]


SearchIndexClient.merge_or_upload_documents(
    documents: List[dict],
    **kwargs
) -> List[IndexOperationResult]

SearchIndexClient.batch_update(
    batch: IndexOperationBatch,
    **kwargs
) -> List[IndexOperationResult]

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

### 3. Search for documents in an Azure search index

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

### 4. Get a list of search suggestions

```python
from azure.search import SearchApiKeyCredential, SearchIndexClient

client = SearchIndexClient(
    search_service_name="my-search-service",
    index_name="hotels-sample-index",
    credential=SearchApiKeyCredential(api_key="xxxxxxxxx")
)

results = service.documents.get_suggestions(search_text="cof", suggester_name="sg")

for result in results:
    print(result['text'])
```

### 5. Get a list of search auto-completions

```python
from azure.search import SearchApiKeyCredential, SearchIndexClient

client = SearchIndexClient(
    search_service_name="my-search-service",
    index_name="hotels-sample-index",
    credential=SearchApiKeyCredential(api_key="xxxxxxxxx")
)

results = service.documents.get_autocompletions(search_text="cof", suggester_name="sg")

for result in results:
    print(result['text'])
    print(result['query_plus_text'])
```

### 6. Upload documents to an Azure Search index

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

results = service.documents.upload_documents(documents)

for result in results:
    print(result.status_code)
```

### 7. Delete documents from an Azure Search index

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

results = service.documents.delete_documents(documents)

for result in results:
    print(result.status_code)
```

### 8. Merge new fields in an existing document

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

results = service.documents.merge_documents(documents)

for result in results:
    print(result.status_code)
```

### 9. Merge or upload a document in an Azure Search index

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

results = service.documents.merge_documents(documents)

for result in results:
    print(result.status_code)
```

### 10. Batch CRUD operations on documents

```python
from azure.search import IndexOperationBatch, SearchApiKeyCredential, SearchIndexClient

client = SearchIndexClient(
    search_service_name="my-search-service",
    index_name="hotels-sample-index",
    credential=SearchApiKeyCredential(api_key="xxxxxxxxx")
)

work = IndexOperationBatch()
batch.add_update_document([{ "id": "10", "description": "new item" }])
batch.add_delete_document([{ "id": "8"}, { "id": "9" }])
batch.add_merge_document([{ "id": "10", None }])

results = service.documents.batch_update(work)

for result in results:
    print(result.status_code)
```