# Release History

## 1.1.0b2 (Unreleased)

### Features Added

### Breaking Changes

### Bugs Fixed

### Other Changes

## 1.1.0b1 (2026-11-13)

### Features Added

- Added synchronous and asynchronous `InferenceClient.get_embeddings` for text, search queries, and
  document images, using plain dictionaries in `inputs` or a complete request dictionary.
- Added dense, multi-vector, and combined vector results, with float or base64 encoding.
- Added Azure Blob image inputs and inline or linked result delivery.
- Added embedding usage, truncation warnings, SAS lifetime warnings, and typed service errors.
- Added support for service API version `2026-11-01-preview`, now the client default. Pass
  `api_version="2026-10-30"` to retain the generally available API version.

## 1.0.0 (2026-11-11)

### Features Added

- General availability of the Azure Data AI semantic reranking client.

### Breaking Changes

- Renamed `ProblemDetails.detail` to `ProblemDetails.explanation` so it isn't confused with
  `ProblemDetails.details`. The JSON property name is still `detail`.
- `SemanticRerankingInferenceContent.target_paths` is now a `list[str]` of up to 100 paths
  instead of a comma-separated `str`.

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

