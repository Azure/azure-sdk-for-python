# Release History

## 0.1.0b1 (Unreleased)

### Features Added

- Initial preview of the Azure Inference Service semantic reranking client.
- Synchronous and asynchronous `InferenceServiceClient.semantic_rerank` APIs
  using dictionary requests and responses, without generated model classes.
- API-key authentication with raw strings or `AzureKeyCredential`, and Microsoft
  Entra authentication, for both synchronous and asynchronous clients.
- Reranking options for model selection, batching, sorting, and JSON document paths.
- Document and sentence-level scoring, response metadata, and standard Azure
  Core error handling and retry policies.