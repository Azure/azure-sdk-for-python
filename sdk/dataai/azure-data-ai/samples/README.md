# Azure Data AI samples

These samples use Azure Data AI, hosted by Azure Inference Service. The generated
SDK accepts dictionary requests or `SemanticRerankingInferenceContent` models and
returns `SemanticRerankingInferenceResult`. Dictionary-style response access remains supported.
The samples do not require a Cosmos DB account.

The SDK takes its endpoint and credential directly from the application. Environment
variables are optional configuration conventions, not SDK requirements.

The synchronous `semantic_reranking.py` sample uses the endpoint, key, and request configured
in `get_sample_inputs()`. Preserve local configuration privately; do not commit real credentials.
The samples read these environment variables:

| Variable | Value |
| --- | --- |
| `AZURE_DATA_AI_ENDPOINT` | Azure Data AI endpoint. |
| `AZURE_DATA_AI_KEY` | API subscription key, required for the key-auth samples. |

Never put real credentials in source code intended to be shared.

- `python samples/semantic_reranking.py`: synchronous `AzureKeyCredential` example with sentence scores.
- `python samples/semantic_reranking_async.py`: asynchronous `AzureKeyCredential` example.
- `python samples/semantic_reranking_entra.py`: synchronous Microsoft Entra example using
  `DefaultAzureCredential`. Install `azure-identity` and configure a supported credential with permission
  to invoke the service endpoint.
- `python samples/semantic_reranking_entra_json.py`: Microsoft Entra example for
  JSON documents, selected fields, and document/sentence scores, using `DefaultAzureCredential`.

For the async sample, install `aiohttp`. The Entra samples only need
`AZURE_DATA_AI_ENDPOINT`, not `AZURE_DATA_AI_KEY`.

## Multimodal embedding

- `python samples/multi_modal_embedding.py`: synchronous Microsoft Entra example. It embeds a document as a dense
  vector and prints its token count and any truncation warning, then embeds a query with `vector_type="both"`.
  If `AZURE_DATA_AI_IMAGE_URL` and `AZURE_DATA_AI_IMAGE_SAS` are set, it also embeds that blob image as base64
  multi-vectors, decodes them with `shape`, and reads the same image's results through a result link.
- `python samples/multi_modal_embedding_async.py`: asynchronous example that embeds a document and a query
  concurrently, one item per request.

A request has at most one text or query item. Text and queries are sent inline in `content`. Images are read
from Azure Blob Storage: `url` plus, in `sasToken`, a read-only, https-only user delegation SAS for that blob,
signed by the identity that calls the API (see the package README). Inline images work only where the endpoint
allows them. Each result item is a `MultimodalDenseEmbedding` (`embedding`), a
`MultimodalMultiVectorEmbedding` (`multi_embedding` and `shape`) or a `MultimodalDenseAndMultiVectorEmbedding`
(both), selected by its `kind`. A SAS, including a result link's `sas_token`, is a credential: don't log it.

Pass the items in `contents` and the options as keyword arguments, such as `vector_type`, `encoding_format` and
`delivery`. Items are `EmbeddingContentItem` models; `multi_modal_embed` also accepts the whole request as a
dictionary with the service's JSON names (`vectorType`, `sasToken`, ...), typed by `azure.data.ai.types.MultiModalEmbedRequest`.

Both clients accept `AzureKeyCredential` or the appropriate sync/async token
credential. Wrap raw keys with `AzureKeyCredential`. Key authentication uses `Ocp-Apim-Subscription-Key` and requires a
key issued for an endpoint with key-based authentication enabled.

## Model selection and request options

Each sample sets `model` directly in its request dictionary. Change that field to a
model supported by your endpoint, or remove it to leave model selection to the service.
The synchronous example configures its request in `get_sample_inputs()`.
The TypeSpec example uses `semantic-reranker-v1`; choose a model supported by your
endpoint rather than assuming that every endpoint exposes that model.

The request dictionaries demonstrate `topK`, `batchSize`, `sort`, `returnDocuments`,
`returnSentenceScore`, and `documentType`. They use the generated
`azure.data.ai.types.SemanticRerankingInferenceContent` TypedDict for type checking.
These are service request-body fields, not method keyword arguments.

For JSON documents, JSON-encode each document string and use `documentType: "json"`.
Supply `targetPaths`, using dot notation for nested properties and commas for
multiple paths, such as `"meta.content,id"`.
See the [JSON document and model-selection example](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/dataai/azure-data-ai/README.md#model-selection-and-json-documents).

Python method names use snake_case, but dictionary keys keep the service's JSON
names: `topK`, `returnDocuments`, `returnSentenceScore`, and `sentenceScores`.
Read response entries from `scores`, not the legacy `Scores` spelling.
Sentence-score indices are zero-based and can exceed 2; sentence scores range
from 0 to 1 inclusive. Iterate all returned sentence entries without truncation.

## JSON documents with Microsoft Entra

The JSON sample uses the same Entra prerequisites and `AZURE_DATA_AI_ENDPOINT`
configuration, without an API key:

```bash
python samples/semantic_reranking_entra_json.py
```

Use a model supported by your endpoint, or remove the request's `model` field for its default.
The sample serializes each document with `json.dumps`, sets `documentType` to
`"json"`, and passes `"title,description"` as the comma-separated `targetPaths`
string. Do not pass dictionaries directly in the `documents` array.

Returned document text remains a JSON-encoded string; the sample uses `json.loads`
to display its fields. It also prints any returned sentence scores. Only one
JSON sample is provided; automated coverage exercises both sync/async clients and
generated-model and dictionary requests with `AzureKeyCredential` and Entra authentication.
