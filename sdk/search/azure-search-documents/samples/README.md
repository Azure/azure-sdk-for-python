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

* Simple text search and similar documents (`more_like_this`, restricted to top-level searchable text fields): [sample_query_simple.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_query_simple.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_query_simple_async.py)). The similarity example uses existing document key `"1"` without search text.
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
* Opt-in **ADLS Gen2** permission ingestion, `refresh_all_acls`, permission resync, source authorization, and explicitly authorized elevated reads: [sample_indexer_permissions.py](sample_indexer_permissions.py) ([async version](sample_indexer_permissions_async.py)). Requires a hierarchical-namespace filesystem with real named-user/group ACLs and Search managed-identity access; it is not a basic Blob ingestion scenario.
  Querying in this pair uses `azure-identity`'s `DefaultAzureCredential` and a caller with Search Index Data Reader. Elevated reads additionally require Search Index Data Contributor or a custom role granting elevated read; resource management retains the existing admin-key pattern.
* Content Understanding skillset configuration: fixed-size character chunks, semantic token chunks, and paired model/deployment settings: [sample_skillset_content_understanding.py](sample_skillset_content_understanding.py) ([async version](sample_skillset_content_understanding_async.py)). Requires a Foundry-created AI Services resource and a supported model deployment; this configures a skillset but does not execute enrichment.

### Service Operations

* Filtered, paged index statistics and resource definitions (indexes, aliases, synonym maps, indexers, data sources, and skillsets), plus service/indexer runtime reporting: [sample_service_statistics.py](sample_service_statistics.py) ([async version](sample_service_statistics_async.py)). This sample is read-only and preserves opaque continuation tokens through the SDK pager. Python's list-returning `get_*` convenience methods remain available alongside pageable `list_*` methods.

### Typed dictionary inputs

The public `azure.search.documents.types`, `azure.search.documents.indexes.types`, and
`azure.search.documents.knowledgebases.types` namespaces provide typed request dictionaries and
discriminated-union aliases. These inputs use REST field names, such as `k`, `chunkingProperties`,
and `includeActivity`, rather than the Python model constructors' keyword names.

The [vector query pair](sample_query_vector.py) ([async](sample_query_vector_async.py)) passes a
`VectorizedQuery` dictionary through the public `VectorQuery` alias to `search`.
The [Content Understanding pair](sample_skillset_content_understanding.py)
([async](sample_skillset_content_understanding_async.py)) uses a `ContentUnderstandingSkill`
dictionary through `SearchIndexerSkill` in a typed `SearchIndexerSkillset` update on the same resource.
The [agentic retrieval pair](sample_agentic_retrieval.py) ([async](sample_agentic_retrieval_async.py))
passes typed intent/reasoning-effort aliases in a `KnowledgeBaseRetrievalRequest` to `retrieve`.
Each example retains its model-based calls and demonstrates a closed, declared request shape;
none relies on typing arbitrary document fields as an open record.

### Advanced

* Custom HTTP requests (SearchClient): [sample_search_client_custom_request.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_search_client_custom_request.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_search_client_custom_request_async.py))
* Custom HTTP requests (SearchIndexClient): [sample_index_client_custom_request.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_index_client_custom_request.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_index_client_custom_request_async.py))
* Knowledge base agentic retrieval: [sample_agentic_retrieval.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_agentic_retrieval.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_agentic_retrieval_async.py))

### Knowledge resources (2026-10-01 GA)

These samples target the `2026-10-01` GA API. Preview-only scenarios are not included in this branch.

The agentic retrieval pair demonstrates both `retrieve` and native `retrieve_stream`.
Streams yield typed payload models (or lists of reference models), not event-name/data wrappers.
The client and stream are closed using context managers, including when a streamed error occurs.
Completion status `200` means complete results; `206` means partial results, not a transport failure.
There are no token-delta events. The retrieval examples also show base filters, source selection/error
controls, document limits, typed activity timestamps/warnings/token usage, and Search-owned citation URLs.
Following a citation URL requires Search authorization; the samples do not fetch URLs anonymously.
The common response consumer recognizes Search Index, Blob, OneLake, web, File, indexed SharePoint,
and indexed SQL activity, and the applicable Search-owned citation references. The agentic setup
itself creates only a Search Index source; other source kinds appear only when configured on a
knowledge base. No Blob/OneLake retrieval or permission behavior is established by running that setup.
Optional chat configuration demonstrates CORS, retrieval/answer instructions, low/medium reasoning
effort, message-based query planning, and answer synthesis versus extractive output. Supply an actual
deployment/model pair such as `gpt-5.4` (other supported GA model names include `gpt-5.5`,
`gpt-5.6-sol`, `gpt-5.6-terra`, and `gpt-5.6-luna`); enum support alone does not provision a model or
establish that a deployment is available in your region.
The semantic search pair uses GA fuzzy Lucene matching instead of the preview-only query speller;
existing snippet tags are retained.

* Knowledge base CRUD and cursor pagination: [sample_knowledge_base_crud.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_knowledge_base_crud.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_knowledge_base_crud_async.py))
* Knowledge source CRUD, private Blob ingestion, analyzer verification, and cursor pagination: [sample_knowledge_source_crud.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_knowledge_source_crud.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_knowledge_source_crud_async.py))
* File knowledge source lifecycle with capacity checks, relative-path metadata, multipart update, prefix paging, deletion, timestamps/errors, and service-selected parsing/extraction modes: [sample_knowledge_source_file_preview.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_knowledge_source_file_preview.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_knowledge_source_file_preview_async.py))
* Opt-in indexed SQL (content/embedding column mappings), indexed SharePoint (container selection, permission ingestion, optional federated identity), and web sources (domains, language, market, result count, freshness): [sample_knowledge_source_indexed.py](sample_knowledge_source_indexed.py) ([async version](sample_knowledge_source_indexed_async.py)). Each scenario documents its real data/identity prerequisites and creates a temporary knowledge base for retrieval. An additional opt-in SharePoint schema example configures connector app registration, permission fields, organization-link expiration, and the site-URL field without pretending to ingest SharePoint content.

These GA scenarios were aligned with the public [.NET reference PR #63555](https://github.com/Azure/azure-sdk-for-net/pull/63555),
using the Python `2026-10-01` models and method signatures rather than copying .NET-specific APIs.
In particular, Python streaming yields native typed payloads rather than .NET event wrappers.

## Running samples and preparing recordings

Samples make live calls and may create, update, or delete resources. Use a dedicated test service
and the prerequisites listed in each sample. The legacy indexer-workflow sample also requires
hotel JSON-array blobs in `hotels-sample-container` and a region supporting its enrichment skills.
Knowledge retrieval requires a populated index with a semantic configuration. File ingestion
additionally requires the embedding deployment and service permissions described in that sample.
Optional private-Blob ingestion requires its additional identity, network, storage, and AI Services
configuration; its returned ingestion settings are verified through the public `as_dict()` wire
representation rather than relying on cross-namespace model materialization.
Use a `ResourceId=/subscriptions/.../providers/Microsoft.Storage/storageAccounts/<account>/;`
connection string and an authorized managed identity where supported; do not enable Storage shared
keys just to run these samples. Source-authorization values, connection strings, and service keys
must not be committed or printed. New external-source and enrichment scenarios are opt-in, may incur
charges, and cannot be validated for service acceptance without their actual resources.

Running a sample does **not** create test-proxy recordings. Use the corresponding recorded tests
and the [package recording guide](../.github/skills/azure-search-documents/references/testing.md).
That guide describes the environment template, serial recording/playback steps, and asset updates.
The test preparer deletes all Search resources on the configured service before each live test:
never point it at a shared or production service. The opt-in ADLS example documents a permission-ingestion
configuration, but permission-resync recording remains blocked until a real hierarchical-namespace
filesystem with ACL fixtures and an authorized Search identity is available. Offline serialization
checks are not evidence of ACL enforcement, model execution, or service acceptance.

## Next steps

Check out the [Azure AI Search REST API reference](https://learn.microsoft.com/rest/api/searchservice/)
to learn more about what you can do with the Azure AI Search client library.
