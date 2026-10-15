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
They use the client's default `2026-10-01` GA API version, including custom HTTP requests.
Published filenames containing `_preview` are retained for compatibility; their scenarios use the GA surface.

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

* Authenticate the client with an API Key: [sample_authentication.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_authentication.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_authentication_async.py))

### Document Operations

* Upload, merge, get, and delete documents: [sample_documents_crud.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_documents_crud.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_documents_crud_async.py))
* High-throughput indexing with buffering: [sample_documents_buffered_sender.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_documents_buffered_sender.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_documents_buffered_sender_async.py))

### Query Operations

* Simple text search: [sample_query_simple.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_query_simple.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_query_simple_async.py))
* Filter and sort search results: [sample_query_filter.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_query_filter.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_query_filter_async.py))
* Faceted search: [sample_query_facets.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_query_facets.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_query_facets_async.py))
* Autocomplete suggestions: [sample_query_autocomplete.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_query_autocomplete.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_query_autocomplete_async.py))
* Search suggestions: [sample_query_suggestions.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_query_suggestions.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_query_suggestions_async.py))
* Semantic search: [sample_query_semantic.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_query_semantic.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_query_semantic_async.py))
* Vector search: [sample_query_vector.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_query_vector.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_query_vector_async.py))
* Session consistency: [sample_query_session.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_query_session.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_query_session_async.py))

### Index Operations

* Create, get, update, and delete indexes: [sample_index_crud.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_index_crud.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_index_crud_async.py))
* Analyze text: [sample_index_analyze_text.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_index_analyze_text.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_index_analyze_text_async.py))
* Index aliases: [sample_index_alias_crud.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_index_alias_crud.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_index_alias_crud_async.py))
* Synonym maps: [sample_index_synonym_map_crud.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_index_synonym_map_crud.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_index_synonym_map_crud_async.py))

### Indexer Operations

* Create, get, update, and delete indexers: [sample_indexer_crud.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_indexer_crud.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_indexer_crud_async.py))
* Create, get, update, and delete data sources: [sample_indexer_datasource_crud.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_indexer_datasource_crud.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_indexer_datasource_crud_async.py))
* Indexer workflow (DataSource, Index, Skillset, Indexer): [sample_indexer_workflow.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_indexer_workflow.py)

### Advanced

* Custom HTTP requests (SearchClient): [sample_search_client_custom_request.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_search_client_custom_request.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_search_client_custom_request_async.py))
* Custom HTTP requests (SearchIndexClient): [sample_index_client_custom_request.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_index_client_custom_request.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_index_client_custom_request_async.py))
* Knowledge base agentic retrieval: [sample_agentic_retrieval.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_agentic_retrieval.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_agentic_retrieval_async.py))

### Knowledge resources (2026-10-01 GA)

These samples target the `2026-10-01` GA API. Preview-only scenarios are not included in this branch.

The agentic retrieval pair demonstrates both `retrieve` and native `retrieve_stream`.
Streams yield typed payload models (or lists of reference models), not event-name/data wrappers.
The client and stream are closed using context managers, including when a streamed error occurs.
The semantic search pair uses GA fuzzy Lucene matching instead of the preview-only query speller;
existing snippet tags are retained.

* Knowledge base CRUD and cursor pagination: [sample_knowledge_base_crud.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_knowledge_base_crud.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_knowledge_base_crud_async.py))
* Knowledge source CRUD, private Blob ingestion, analyzer verification, and cursor pagination: [sample_knowledge_source_crud.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_knowledge_source_crud.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_knowledge_source_crud_async.py))
* File knowledge source lifecycle with relative-path metadata, multipart update, prefix paging, deletion, and service-selected modes: [sample_knowledge_source_file_preview.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_knowledge_source_file_preview.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_knowledge_source_file_preview_async.py))

## Running samples and preparing recordings

Samples make live calls and may create, update, or delete resources. Use a dedicated test service
and the prerequisites listed in each sample. The legacy indexer-workflow sample also requires
hotel JSON-array blobs in `hotels-sample-container` and a region supporting its enrichment skills.
Knowledge retrieval requires a populated index with a semantic configuration. File ingestion
additionally requires the embedding deployment and service permissions described in that sample.
Optional private-Blob ingestion requires its additional identity, network, storage, and AI Services
configuration; its returned ingestion settings are verified through the public `as_dict()` wire
representation rather than relying on cross-namespace model materialization.

Running a sample does **not** create test-proxy recordings. Use the corresponding recorded tests
and the [package recording guide](../.github/skills/azure-search-documents/references/testing.md).
That guide describes the environment template, serial recording/playback steps, and asset updates.
The test preparer deletes all Search resources on the configured service before each live test:
never point it at a shared or production service. Indexer permission-resync recording remains
blocked until a permission-ingestion data-source scenario is available.

## Next steps

Check out the [Azure AI Search REST API reference](https://learn.microsoft.com/rest/api/searchservice/)
to learn more about what you can do with the Azure AI Search client library.
