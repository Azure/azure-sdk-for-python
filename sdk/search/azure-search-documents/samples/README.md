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

* Authenticate the client with an API Key: [sample_authentication.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_authentication.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_authentication_async.py))

### Document Operations

* Upload, merge, get, and delete documents: [sample_documents_crud.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_documents_crud.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_documents_crud_async.py))
* High-throughput indexing with buffering: [sample_documents_buffered_sender.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_documents_buffered_sender.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_documents_buffered_sender_async.py))

### Query Operations

* Graph query, provenance, and diagnostics (2026-11-01-preview):
  [sample_query_graph_preview.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_query_graph_preview.py)
  ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_query_graph_preview_async.py)). Requires an existing graph index;
  the samples do not provision resources.
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

### Preview samples (2026-11-01-preview)

The following samples target an `azure-search-documents` build whose default API version is
`2026-11-01-preview`. Use a matching November-preview SDK build; a stable package or an older preview
does not provide these contracts. For the unreleased changes in this branch, run the following from
`sdk/search/azure-search-documents/` in your checked-out repository:

```bash
python -m pip install -e .
```

Behavior of preview APIs may change before GA.

Direct agentic Search and Microsoft Retriever 1:

* Search hotel documents using `query_type="agentic"` and `AgenticSearchOptions`, then inspect
  issued subqueries, termination, planning tokens, and `reasoning_tokens`:
  [sample_agentic_search_preview.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_agentic_search_preview.py)
  ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_agentic_search_preview_async.py)).
  This uses `SearchClient.search`, not knowledge-base retrieval.
* Explicitly configure `KnowledgeBaseMicrosoftRetriever1Model`, verify the saved selection,
  and retrieve hotel facts with minimal reasoning and extractive output:
  [sample_microsoft_retriever_preview.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_microsoft_retriever_preview.py)
  ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_microsoft_retriever_preview_async.py)).

Both require the corresponding November-preview capability, semantic search, and **paid standard
Knowledge Retrieval already enabled**. Microsoft Retriever 1 has no free tier. These samples
do not enable billing or configure a customer model deployment. Set `AZURE_SEARCH_SERVICE_ENDPOINT`
and optionally `AZURE_SEARCH_API_KEY`; otherwise the caller uses `DefaultAzureCredential`.
Only resources successfully created by the run are cleaned up. Returned usage is not a billing
reconciliation, and extractive output does not demonstrate external-model answer synthesis.

Random scoring:

* Create seeded and unseeded random scoring profiles over twenty synthetic hotel documents:
  [sample_random_scoring_preview.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_random_scoring_preview.py)
  ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_random_scoring_preview_async.py)).
  Demonstrates repeatable seeded orders and scores, different seeds, unseeded requests, signed
  64-bit seed boundaries, stable paging, filtered relative ordering, result counts, and the
  missing-seed error. It follows the core `random-score-fn.http` scenarios, not that file's
  exhaustive negative, older-API, vector, or multi-shard validation suite.
  Requires one free index slot; no model deployment is needed.
This pair uses `AZURE_SEARCH_SERVICE_ENDPOINT` and optionally `AZURE_SEARCH_API_KEY`.
It creates unique Search resources and cleans up only resources successfully created by that run.

Knowledge-base tools, compatible providers, and automatic query hints:

* Configure two named tools, retrieve using `tool_name`, verify a saved country filter and
  source restrictions, then clear the tools and restore normal retrieval:
  [sample_knowledge_base_tools_preview.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_knowledge_base_tools_preview.py)
  ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_knowledge_base_tools_preview_async.py)).
  This follows the SDK-supported direct retrieval portion of the KB Tools HTTP flow.
  MCP `tools/list` and `tools/call` are separate protocols, not typed operations on this SDK.
  The sample needs semantic search and two free index slots, but no model deployment.
* Configure an OpenAI-compatible chat provider and retrieve actual hotel evidence:
  [sample_openai_compatible_retrieval_preview.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_openai_compatible_retrieval_preview.py)
  ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_openai_compatible_retrieval_preview_async.py)).
  Set `AZURE_SEARCH_COMPATIBLE_CHAT_URI` to the **complete HTTPS POST URL**, including path and
  query parameters, and `AZURE_SEARCH_COMPATIBLE_CHAT_MODEL` to its supported model profile.
  No path or API version is appended. The endpoint or gateway selects the actual model;
  Search does not send a `model` field in its provider request.
* Exercise **GPT-6 Responses** using that same retrieval pair with a supported GPT-6 profile
  such as `gpt-6-sol` and a real Responses endpoint. The provider must implement stateless
  tool continuation. A successful configuration or returned Search activity alone does not
  establish that continuation exchange: confirm it in provider traces before live sign-off.
  Do not point a GPT-6 profile at a Chat Completions endpoint.
  For a **native Azure OpenAI GPT-6 deployment**, set `AZURE_SEARCH_GPT6_NATIVE=true`,
  `AZURE_OPENAI_ENDPOINT`, and optionally `AZURE_OPENAI_API_KEY`. The deployment and model
  variables `AZURE_OPENAI_GPT6_DEPLOYMENT` and `AZURE_OPENAI_GPT6_MODEL` default to `gpt-6-sol`.
  This uses `KnowledgeBaseAzureOpenAIModel` instead of compatible-provider configuration;
  no compatible-provider URI, headers, or model-routing gateway is needed for this variant.
* Configure an OpenAI-compatible embedding vectorizer and compare provider-vectorized text
  with a precomputed vector query:
  [sample_openai_compatible_embeddings_preview.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_openai_compatible_embeddings_preview.py)
  ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_openai_compatible_embeddings_preview_async.py)).
  Set `AZURE_SEARCH_COMPATIBLE_EMBEDDING_URI` to the full embeddings POST URL. The supplied
  hotel vectors in `data/hotels_compatible_ada002.json` use **text-embedding-ada-002, 1536
  dimensions**; the endpoint must select that same model. The stored spa-description vector
  and a provider-vectorized paraphrase must both rank the spa hotel first.
  This demonstrates query vectorization, not managed ingestion-time embedding.
* Populate country facets, configure `auto_configuration` without manual `field_values`,
  retrieve hotels, and verify generated query-hint filters and matching references:
  [sample_query_hints_auto_configuration_preview.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_query_hints_auto_configuration_preview.py)
  ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_query_hints_auto_configuration_preview_async.py)).
  Set `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_CHAT_DEPLOYMENT`, and `AZURE_OPENAI_CHAT_MODEL`;
  optionally set `AZURE_OPENAI_API_KEY`, otherwise Search uses its existing identity.
  The country field must be filterable and facetable. Automatic grounding is not supported
  with document-level permissions or sensitivity labels, or in request-time hint overrides.
  Set `AZURE_SEARCH_HINT_REFRESH=true` to add a country and query after a 60-second TTL.
  This demonstrates new-value availability after the TTL, **not cache-hit telemetry**.

All four areas use `AZURE_SEARCH_SERVICE_ENDPOINT` and optionally `AZURE_SEARCH_API_KEY`;
otherwise the caller uses `DefaultAzureCredential`. Each creates unique hotel fixtures and
cleans up **only its successfully created** KBs, sources, and indexes, including on failure.
Compatible providers additionally require exactly one authentication option per prefix:
`AZURE_SEARCH_COMPATIBLE_CHAT_HEADERS_JSON` or `AZURE_SEARCH_COMPATIBLE_CHAT_MI_AUDIENCE`,
and the equivalent `AZURE_SEARCH_COMPATIBLE_EMBEDDING_*` variables for embeddings.
Headers are a nonempty secret JSON map; never commit them or print the model configuration.
A managed-identity audience must be the third-party Entra application's **bare GUID**, not
an `api://` URI or a resource scope. Configure its authorization for Search separately.
Compatible-provider and GPT-6 scenarios require working provider endpoints and authentication;
configuration or static checks alone do not establish live success.

Enterprise Knowledge Graph (EKG):

* Create an edge-list graph and provenance index, upload hotel assertions, inspect a query plan,
  execute GQL with evidence IDs, and optionally hydrate source text:
  [sample_graph_index_preview.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_graph_index_preview.py)
  ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_graph_index_preview_async.py)).
* Ingest Blob documents with an enrichment cache and inline ontology, wait for a completed
  synchronization, query actual extracted relationships, and
  retrieve through a KB with generated GQL and graph references:
  [sample_graph_extraction_cache_preview.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_graph_extraction_cache_preview.py)
  ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_graph_extraction_cache_preview_async.py)).
  Optionally hydrate graph evidence with supporting source text. The source GET also verifies that the
  write-only cache connection string is omitted.

Install `azure-identity` and, for async execution, `aiohttp`. Both pairs require
`AZURE_SEARCH_SERVICE_ENDPOINT` and a November-preview service supporting the demonstrated APIs.
The caller's `DefaultAzureCredential` needs Search Service Contributor and Search Index Data
Contributor; alternatively set `AZURE_SEARCH_API_KEY` to an admin key.
Names include a run tag and random suffix. Override `SAMPLE_RUN_TAG`,
`AZURE_SEARCH_GRAPH_INDEX_NAME`, `AZURE_SEARCH_GRAPH_SOURCE_INDEX_NAME`,
`AZURE_SEARCH_KNOWLEDGE_SOURCE_NAME`, `AZURE_SEARCH_KNOWLEDGE_BASE_NAME`, or
`AZURE_SEARCH_GRAPH_NAME` as applicable. **Resource names must be new. Creates are conditional,
updates use ETags, and neither pair deletes anything, even after failure.**

For extraction/cache, first upload
[data/hotel_graph.txt](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/data/hotel_graph.txt)
to a new approved folder in a native Blob container, with Blob content type `text/plain`.
Set `AZURE_STORAGE_CONNECTION_STRING`,
`AZURE_STORAGE_CONTAINER`, and `AZURE_STORAGE_FOLDER` to that binding. The folder must be a nonempty
prefix, not the container root. Samples never upload, modify, or delete source blobs.
The synthetic hotel's operator, location, and founding-year facts are the validation fixture;
an unrelated corpus will not satisfy these examples.

Native Blob soft delete must be enabled **before** indexing. Set
`AZURE_SEARCH_GRAPH_CACHE_CONNECTION_STRING` to approved GPv2 storage with both Blob and Table
endpoints. Source and cache can use the same approved account. ResourceId-format connections use
the Search service's system-assigned identity: source reads need Storage Blob Data Reader,
while cache read/write needs Storage Blob Data Contributor **and** Storage Table Data Contributor.
The cache binding/identity cannot later be changed or removed. ADLS Gen2, ACL ingestion, and
sensitivity-label ingestion are not supported in this extraction workflow.

Set `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_CHAT_DEPLOYMENT`, `AZURE_OPENAI_CHAT_MODEL`,
`AZURE_OPENAI_EMBEDDING_DEPLOYMENT`, and `AZURE_OPENAI_EMBEDDING_MODEL` to supported, reachable
native Azure OpenAI deployments. Search needs Cognitive Services OpenAI User on the model resource,
or set `AZURE_OPENAI_API_KEY`. Extraction, embeddings, retrieval, and retained resources incur costs.
Samples do not deploy models or change permissions, feature flags, or storage settings.

Set `AZURE_SEARCH_GRAPH_HYDRATE=true` only when hydration is already supported and authorized.
Otherwise the samples demonstrate evidence IDs and graph-row KB retrieval, **not hydration**.
Actual cache reuse requires execution/service telemetry; unchanged chunks or faster execution
alone are not proof of a cache hit. Once attached, an ontology cannot be detached.

GraphRAG Zero (Topic Graph):

* Create a corpus and topic sidecar, link their profiles, compare ordinary/diverse/balanced vector
  search, run text vectorization, and retrieve through a knowledge base with stored and runtime
  topic settings: [sample_topic_graph_preview.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_topic_graph_preview.py)
  ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_topic_graph_preview_async.py)).
  These samples use nine synthetic hotel documents and three sampled representative vectors,
  not production topic clustering or a retrieval-quality benchmark. No offline build tool or
  private dataset is required.

Install the extra sample dependencies:

```bash
python -m pip install openai azure-identity aiohttp
```

Set `AZURE_SEARCH_SERVICE_ENDPOINT`, `AZURE_OPENAI_ENDPOINT`,
`AZURE_OPENAI_EMBEDDING_DEPLOYMENT`, and `AZURE_OPENAI_EMBEDDING_MODEL`.
Use `text-embedding-3-small` (1536 dimensions) or `text-embedding-3-large` (3072 dimensions);
`AZURE_OPENAI_EMBEDDING_DIMENSIONS` optionally selects a supported reduced size. The same
deployment and vector space are used for documents, representatives, and queries.
The Search service must support the November Topic Graph preview and semantic search.
Both your machine and Search must have network access to the embedding endpoint.

The samples use `DefaultAzureCredential`, which can select a developer login such as `az login`,
an environment-configured service principal, or a managed identity. The caller needs
**Search Service Contributor** to create/configure objects, **Search Index Data Contributor**
to upload/query documents, and **Cognitive Services OpenAI User** on the embedding resource.
For service-side vectorization, grant the Search service's system-assigned managed identity
**Cognitive Services OpenAI User** on that resource too. Alternatively, set
`AZURE_SEARCH_API_KEY` to a Search admin key and/or `AZURE_OPENAI_API_KEY` to an embedding
resource key. Keep credentials outside committed files. No chat model or Storage account is
needed for the minimal-reasoning, extractive knowledge-base flow.

Resource names default to `hotels-grz-<run-tag>`, `hotels-grz-<run-tag>-topicgraph`,
`hotels-grz-source-<run-tag>`, and `hotels-grz-base-<run-tag>`. Set `SAMPLE_RUN_TAG` or
override `AZURE_SEARCH_INDEX_NAME`, `AZURE_SEARCH_TOPIC_GRAPH_INDEX_NAME`,
`AZURE_SEARCH_KNOWLEDGE_SOURCE_NAME`, and `AZURE_SEARCH_KNOWLEDGE_BASE_NAME`.
All names must be new; the sidecar name must end in `-topicgraph`. Creates use
`If-None-Match: *`; linkage uses the corpus ETag. **The samples never delete resources,
even on failure**, and must not be used to update existing shared indexes. Retained resources
consume quota/storage; use the printed names to manage only your newly created resources.
Embedding and vectorization calls incur model usage.

Knowledge base and retrieval:

* Knowledge base CRUD with tags metadata and cursor pagination: [sample_knowledge_base_crud.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_knowledge_base_crud.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_knowledge_base_crud_async.py))
* Knowledge base preview configuration with reasoning precedence, retrieval defaults, CORS, tags, and query hints: [sample_knowledge_base_configuration_preview.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_knowledge_base_configuration_preview.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_knowledge_base_configuration_preview_async.py))
* Retrieve responses with Search-owned citation URLs, results processing, and typed server-sent events: [sample_knowledge_retrieval_response_preview.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_knowledge_retrieval_response_preview.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_knowledge_retrieval_response_preview_async.py))
* Service stats with knowledge base / source counters and the per-index vector-size limit: [sample_knowledge_service_stats_preview.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_knowledge_service_stats_preview.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_knowledge_service_stats_preview_async.py))
* Source attach-time defaults (`enable_freshness`, `enable_image_serving`): [sample_knowledge_source_freshness_preview.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_knowledge_source_freshness_preview.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_knowledge_source_freshness_preview_async.py))

Knowledge source kinds:

* Knowledge source CRUD with query hints, private Blob ingestion, analyzer verification, and cursor pagination: [sample_knowledge_source_crud.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_knowledge_source_crud.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_knowledge_source_crud_async.py))
* File knowledge source ingestion LROs with multipart upload, replacement, completion/error checks,
  preserved file identity, relative-path metadata, prefix paging, updated-content retrieval, and deletion:
  [sample_knowledge_source_file_preview.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_knowledge_source_file_preview.py)
  ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_knowledge_source_file_preview_async.py)).
  The samples call `begin_ingest_knowledge_source_file_multipart` and
  `begin_ingest_knowledge_source_file_replacement`, waiting for both pollers.
  Configure the native Azure OpenAI embedding variables listed in the scripts; Search's identity
  needs access to that deployment. No Blob source is required.
* MCP server knowledge source: [sample_knowledge_source_mcp_server_preview.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_knowledge_source_mcp_server_preview.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_knowledge_source_mcp_server_preview_async.py))
* Work IQ knowledge source with customer-owned Entra app authentication, optional tenant behavior, and separate authorization channels: [sample_knowledge_source_workiq_preview.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_knowledge_source_workiq_preview.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_knowledge_source_workiq_preview_async.py))
* Fabric ontology knowledge source: [sample_knowledge_source_fabric_ontology_preview.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_knowledge_source_fabric_ontology_preview.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_knowledge_source_fabric_ontology_preview_async.py))
* Fabric data agent knowledge source: [sample_knowledge_source_fabric_data_agent_preview.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_knowledge_source_fabric_data_agent_preview.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_knowledge_source_fabric_data_agent_preview_async.py))

## Next steps

Check out the [Azure AI Search REST API reference](https://learn.microsoft.com/rest/api/searchservice/)
to learn more about what you can do with the Azure AI Search client library.
