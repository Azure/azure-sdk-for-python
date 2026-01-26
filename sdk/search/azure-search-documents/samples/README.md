---
page_type: sample
languages:
  - python
products:
  - azure
  - azure-search
---

# Azure AI Search Client Library Samples for Python

These samples demonstrate common scenarios and operations using the Azure AI Search client library.

## Prerequisites

* Python 3.10 or later
* An [Azure subscription](https://azure.microsoft.com/free/)
* An Azure AI Search service
* An index named `hotels-sample-index` created using the 'Import data' wizard with the 'hotels-sample' data source. See [Quickstart: Create a search index in the Azure portal](https://learn.microsoft.com/azure/search/search-get-started-portal?pivots=import-data).
* An Azure Storage account and a blob container named `hotels-sample-container`

### Install the package
```bash
pip install azure-search-documents
```

## Examples

### Authentication

* Authenticate the client with an API Key: [sample_authentication.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_authentication.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/async_samples/sample_authentication_async.py))

### Document Operations

* Upload, merge, get, and delete documents: [sample_documents_crud.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_documents_crud.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/async_samples/sample_documents_crud_async.py))
* High-throughput indexing with buffering: [sample_documents_buffered_sender.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_documents_buffered_sender.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/async_samples/sample_documents_buffered_sender_async.py))

### Query Operations

* Simple text search: [sample_query_simple.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_query_simple.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/async_samples/sample_query_simple_async.py))
* Filter and sort search results: [sample_query_filter.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_query_filter.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/async_samples/sample_query_filter_async.py))
* Faceted search: [sample_query_facets.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_query_facets.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/async_samples/sample_query_facets_async.py))
* Autocomplete suggestions: [sample_query_autocomplete.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_query_autocomplete.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/async_samples/sample_query_autocomplete_async.py))
* Search suggestions: [sample_query_suggestions.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_query_suggestions.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/async_samples/sample_query_suggestions_async.py))
* Semantic search: [sample_query_semantic.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_query_semantic.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/async_samples/sample_query_semantic_async.py))
* Vector search: [sample_query_vector.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_query_vector.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/async_samples/sample_query_vector_async.py))
* Session consistency: [sample_query_session.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_query_session.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/async_samples/sample_query_session_async.py))

### Index Operations

* Create, get, update, and delete indexes: [sample_index_crud.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_index_crud.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/async_samples/sample_index_crud_async.py))
* Analyze text: [sample_index_analyze_text.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_index_analyze_text.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/async_samples/sample_index_analyze_text_async.py))
* Index aliases: [sample_index_alias_crud.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_index_alias_crud.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/async_samples/sample_index_alias_crud_async.py))
* Synonym maps: [sample_index_synonym_map_crud.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_index_synonym_map_crud.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/async_samples/sample_index_synonym_map_crud_async.py))

### Indexer Operations

* Create, get, update, and delete indexers: [sample_indexer_crud.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_indexer_crud.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/async_samples/sample_indexer_crud_async.py))
* Create, get, update, and delete data sources: [sample_indexer_datasource_crud.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_indexer_datasource_crud.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/async_samples/sample_indexer_datasource_crud_async.py))
* Indexer workflow (DataSource, Index, Skillset, Indexer): [sample_indexer_workflow.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_indexer_workflow.py)

### Advanced

* Custom HTTP requests (SearchClient): [sample_search_client_custom_request.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_search_client_custom_request.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/async_samples/sample_search_client_custom_request_async.py))
* Custom HTTP requests (SearchIndexClient): [sample_index_client_custom_request.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_index_client_custom_request.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/async_samples/sample_index_client_custom_request_async.py))
* Knowledge base agentic retrieval: [sample_agentic_retrieval.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_agentic_retrieval.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/async_samples/sample_agentic_retrieval_async.py))

## Next steps

Check out the [Azure AI Search REST API reference](https://learn.microsoft.com/rest/api/searchservice/)
to learn more about what you can do with the Azure AI Search client library.
