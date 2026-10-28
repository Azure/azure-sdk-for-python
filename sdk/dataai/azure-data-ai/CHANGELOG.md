# Release History

## 1.0.0 (2026-10-29)

### Features Added

- General availability of the Azure Data AI semantic reranking client.

### Other Changes

- The client now targets the generally available service API version `2026-10-30` by default,
  replacing `2026-09-01-preview`.

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

