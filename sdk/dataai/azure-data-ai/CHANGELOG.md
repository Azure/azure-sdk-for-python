# Release History

## 1.1.0b1 (Unreleased)

### Features Added

- Added support for service API version `2026-11-01-preview`, now the default.
- Added synchronous and asynchronous `InferenceClient.multi_modal_embed` to embed text, search queries and document
  images with `microsoft-embedding-1-large`. Pass the `EmbeddingContentItem` items in `contents` and the options
  (`model`, `model_version`, `vector_type`, `dimensions`, `delivery`, ...) as keyword arguments, or the whole request as
  a dictionary (`azure.data.ai.types.MultiModalEmbedRequest`). A request has at most one text or query item. Results
  are `MultimodalDenseEmbedding`, `MultimodalMultiVectorEmbedding` or, with `vector_type="both"` (and
  `multi_dimensions`), `MultimodalDenseAndMultiVectorEmbedding` items, selected by `kind`.
- Images are read from Azure Blob Storage: `EmbeddingContentItem.url` plus a caller-signed user delegation SAS in
  `sas_token` (`content` is now optional). Inline images are off by default.
- Added `delivery` (`EmbeddingDelivery`) and `MultimodalEmbeddingResult.output`
  (`MultimodalEmbeddingOutput`): with `delivery` `link`, the results come back as a read-only link to a JSON file,
  valid for up to 15 minutes.
- Embedding results include per-item `tokens` and `visual_tokens`, and `MultimodalEmbeddingUsage.text_tokens`. Text
  over the model's token limit is embedded from its start and flagged with `truncated`, `input_tokens` and a
  `MultimodalEmbeddingResult.warnings` entry with code `EmbeddingWarningCode.INPUT_TRUNCATED`.
- Added warning `EmbeddingWarningCode.SAS_LONG_LIVED` and error codes `EMBEDDING_BLOB_READ_FAILED`,
  `EMBEDDING_DELIVERY_NOT_SUPPORTED` and `EMBEDDING_OUTPUT_WRITE_FAILED`. Embedding errors with status 413, 502, 503
  and 504 are deserialized as `EmbeddingError`.

### Breaking Changes

- `SemanticRerankingInferenceContent.target_paths` is now a list of paths (`list[str]`), sent as one comma-separated
  string.

### Other Changes

- Semantic reranking now sends `api-version=2026-11-01-preview` by default. Pass
  `api_version="2026-10-30"` to the client to keep using the generally available version.

## 1.0.0 (2026-10-30)

### Features Added

- General availability of the Azure Data AI semantic reranking client.

## 1.0.0b1 (2026-09-29)

### Features Added

- Initial preview of the Azure Data AI semantic reranking client.
- Synchronous and asynchronous `InferenceClient.semantic_rerank` APIs
  accepting generated request models or dictionaries and returning generated
  response models with dictionary-style access.
- API-key authentication with `AzureKeyCredential`, and Microsoft Entra
  authentication, for both synchronous and asynchronous clients.
- Reranking options for model selection, batching, sorting, and JSON document paths.
- Document and sentence-level scoring, response metadata, and standard Azure
  Core error handling and retry policies.
