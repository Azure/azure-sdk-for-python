# Azure Data AI client library for Python

`azure-data-ai` provides access to **Azure Data AI**, hosted by Azure Inference Service:

- **Embedding generation (preview)**: use **Microsoft Embedding 1**
  (`microsoft-embedding-1-large` in API requests) to generate embeddings for text,
  retrieval queries, and images with `InferenceClient.multi_modal_embed`.
- **Semantic reranking**: rank caller-supplied documents by their relevance to a
  query with `InferenceClient.semantic_rerank`, optionally returning documents
  and sentence-level scores.

Embedding generation returns vectors for retrieval. Reranking scores documents
you have already retrieved; it doesn't generate vectors.

The reranking package uses the `2026-10-30` service API. Embedding examples require
an embedding-enabled preview SDK and endpoint; reranking-only releases don't
provide `multi_modal_embed`.

## Getting started

### Install the package

```bash
python -m pip install --pre azure-data-ai
```

For local development, run `python -m pip install -e .` from this package directory instead.

### Prerequisites

- Python 3.10 or later.
- An [Azure subscription][azure_sub] and an Azure Data AI endpoint.
- A key issued for an Azure Data AI endpoint with key-based authentication
  enabled, or a Microsoft Entra identity with permission to invoke the service.

For Cosmos-linked reranking, the [Cosmos DB Semantic Reranker setup][cosmos_reranker]
handles provisioning when you enable the feature in the portal. Follow that guide
for assigning **Semantic Reranker User** at the Cosmos account scope; there is no
additional manual inference-resource creation step in that portal workflow.

For embedding generation, follow the [Azure Cosmos DB embedding-generation
setup][cosmos_embeddings] to enable the capability, copy its endpoint, and assign
**Embedding User** to the calling Microsoft Entra identity. Use that endpoint,
not the Cosmos DB document endpoint or a reranking endpoint.

Install `azure-identity` for the embedding examples. For image inputs, also
install `azure-storage-blob` and upload your image to Azure Blob Storage.
The calling identity needs blob read access and permission to obtain a
user-delegation key. **Storage Blob Data Reader** at storage-account scope
provides both. For container-scoped read access, additionally assign **Storage
Blob Delegator** at storage-account scope. The service must be able to reach
the image blob; a SAS doesn't bypass storage network restrictions.

```bash
python -m pip install azure-identity azure-storage-blob
```

### Authenticate the client

For reranking endpoints with key authentication enabled, use `AzureKeyCredential`:

```python
import os

from azure.core.credentials import AzureKeyCredential
from azure.data.ai import InferenceClient

with InferenceClient(
    endpoint=os.environ["AZURE_DATA_AI_ENDPOINT"],
    credential=AzureKeyCredential(os.environ["AZURE_DATA_AI_KEY"]),
) as client:
    result = client.semantic_rerank(
        {
            "query": "What is the capital of France?",
            "documents": [
                "Paris is the capital of France.",
                "Berlin is the capital of Germany.",
            ],
            "topK": 1,
            "returnDocuments": True,
        }
    )

    for score in result.get("scores", []):
        print(score["index"], score["score"], score.get("document"))
```

The key is sent in the `Ocp-Apim-Subscription-Key` header using Azure Core's
`AzureKeyCredentialPolicy`. Wrap key strings in `AzureKeyCredential` for both
synchronous and asynchronous clients:

```python
client = InferenceClient(endpoint, credential=AzureKeyCredential(key))
```

Use `AzureKeyCredential` when you need to rotate a key with `credential.update(new_key)`
without recreating the client. Key authentication does not require `azure-identity`
or a token credential.

Pass the endpoint and credential to the constructor. Environment variables in
these examples are only an application configuration choice; the SDK does not
read `AZURE_DATA_AI_ENDPOINT` or `AZURE_DATA_AI_KEY`.

For Microsoft Entra authentication, install `azure-identity` separately and pass a
token credential:

```python
import os

from azure.data.ai import InferenceClient
from azure.identity import DefaultAzureCredential

with DefaultAzureCredential() as credential:
    with InferenceClient(
        os.environ["AZURE_DATA_AI_ENDPOINT"], credential
    ) as client:
        result = client.semantic_rerank(
            {"query": "capital of France", "documents": ["Paris", "Berlin"]}
        )
```

The client requests tokens for `https://dbinference.azure.com/.default`.

## Key concepts

`InferenceClient` is the entry point. Call `client.multi_modal_embed(...)`
for embedding generation or `client.semantic_rerank(request)` for reranking.
There is no intermediate inference subclient. The embedding examples use
Microsoft Entra authentication.

### Embedding generation

Call `multi_modal_embed` with keyword arguments and pass plain dictionaries in
the `inputs` list. No request or input-item wrapper objects are needed. Set
`"type": "text"` for document text, `"type": "query"` for retrieval queries,
and `"type": "image"` for blob images. Text and query items use `content`;
image items use separate `url` and `sas_token` keys. Don't use `embed`.

| Keyword argument | Meaning |
| --- | --- |
| `model` | Required. Use `microsoft-embedding-1-large` for Microsoft Embedding 1. |
| `model_version` | Required released date-version identifier, echoed in the response. Pin the same released version for documents and queries in an index. |
| `inputs` | Required list of dictionaries. An optional item `id` associates each result with its input. Use separate calls for separate text documents; two text items in one request are invalid. |
| `vector_type` | `dense` (default), `multi`, or `both`. Multi-vectors require a compatible late-interaction retrieval strategy. |
| `dimensions` | Optional vector width as a string, such as `"1536"` or `"2560"`. Defaults to the model's native width. The dense examples request `"1536"`. |
| `max_num_vectors` | Limits token-level vectors for `multi` or `both` output. |
| `delivery` | `inline` (default) returns vectors in `data`; `link` returns a results-file reference in `output` and an empty `data` list. |

Pass these options directly as operation keyword arguments.
With inline dense output, each `MultimodalDenseEmbedding` in `response.data`
contains `embedding` and the input's `id`. With `vector_type="both"`,
`MultimodalDenseAndMultiVectorEmbedding` contains `embedding`, `multi_embedding`,
and `shape`. Don't flatten token-level vectors into a single-vector index.

Inspect `response.model`, `response.model_version`, and
`response.output_data_type` for the resolved model configuration.
`response.usage.text_tokens` and `response.usage.visual_tokens` distinguish
text and image token usage. For link delivery, use both `output.url` and
`output.sas_token` to download the results file and verify `output.bytes` and
`output.sha256` before processing it. Never log the results-file SAS.

### Semantic reranking

Dictionary keys use the service's JSON names, such as `"topK"`. Generated model
attributes use Python names, such as `top_k`. Both response access forms work:
`result["scores"][0]["score"]` and `result.scores[0].score`. Use `result.as_dict()`
when an ordinary nested dictionary is needed.

```python
from azure.data.ai.models import SemanticRerankingDocumentType, SemanticRerankingInferenceContent

request = SemanticRerankingInferenceContent(
    query="capital of France",
    documents=["Paris is the capital of France.", "Berlin is the capital of Germany."],
    top_k=1,
    return_documents=True,
    return_sentence_score=True,
    document_type=SemanticRerankingDocumentType.TEXT,
)
result = client.semantic_rerank(request)
for score in result.scores or []:
    print(score.index, score.score, score.document)
```

| Request key           | Type        | Meaning                                                                                                                                                |
|-----------------------|-------------|--------------------------------------------------------------------------------------------------------------------------------------------------------|
| `query`               | `str`       | Required nonempty query string.                                                                                                                        |
| `documents`           | `list[str]` | Required nonempty list of strings to rank.                                                                                                             |
| `model`               | `str`       | Optional model name supported by the endpoint. Omit it to use the service's default model.                                                             |
| `returnDocuments`     | `bool`      | Optional. Include document text in the response.                                                                                                       |
| `topK`                | `int`       | Optional. Maximum number of results to return, from 1 to 2147483647.                                                                                   |
| `batchSize`           | `int`       | Optional. Number of documents processed per batch, from 1 to 2147483647.                                                                               |
| `sort`                | `bool`      | Optional. Return scores sorted by relevance.                                                                                                           |
| `documentType`        | `str`       | Optional document format, such as `text` or `json`. JSON documents are JSON-encoded strings.                                                           |
| `targetPaths`         | `str`       | Required for JSON documents. Use dot notation for nested properties, such as `meta.content`, and commas for multiple paths, such as `meta.content,id`. |
| `returnSentenceScore` | `bool`      | Optional. Include sentence-level scores.                                                                                                               |

Put these options inside the request dictionary, not in method keyword arguments.
Omitted options use service-defined defaults. The SDK does not restrict model names
or filter additional request fields.

Responses expose optional `scores` and `meta` fields. Score entries can include
`index`, `score`, `document`, and `sentenceScores`. Metadata can include
`tokenUsage`, `latency`, `modelName`, and `modelVersion` through dictionary access,
or `token_usage`, `latency`, `model_name`, and `model_version` as model attributes
on `SemanticRerankingMetaResult`.

Latency fields `dataPreprocessTime`, `inferenceTime`, and `postProcessTime` contain
numeric milliseconds in the JSON response. The corresponding `LatencyResult` model
attributes, `data_preprocess_duration`, `inference_duration`, and
`post_process_duration`, are `datetime.timedelta` values. Dictionary-style access
and `as_dict()` retain the numeric millisecond representation.

Each sentence score has a nonnegative, zero-based `index` and a `score` in the
inclusive range 0–1. Sentence indices are not capped at 2.

## Examples

See the [samples][samples] for runnable sync and async examples.

### Generate text and query embeddings

Set `AZURE_DATA_AI_ENDPOINT` to the embedding endpoint copied during setup.
Set `AZURE_DATA_AI_MODEL_VERSION` to a supported released date-version identifier,
not today's date or an internal numeric version. Sign in with your calling
identity, for example with `az login` for local development.

The example sends document text and a retrieval query in separate calls.
Both use the same model, version, vector type, and dimensions. Your application
stores and searches the returned vectors; this operation doesn't write to a
Cosmos DB container.

```python
import os

from azure.data.ai import InferenceClient
from azure.data.ai.models import MultimodalDenseEmbedding
from azure.identity import DefaultAzureCredential

items = [
    {
        "id": "camera-guide",
        "type": "text",
        "content": "Use a tripod and a longer exposure to photograph the night sky.",
    },
    {
        "id": "photography-question",
        "type": "query",
        "content": "What equipment helps with photographs of stars?",
    },
]

with DefaultAzureCredential() as credential:
    with InferenceClient(
        endpoint=os.environ["AZURE_DATA_AI_ENDPOINT"],
        credential=credential,
    ) as client:
        for item in items:
            response = client.multi_modal_embed(
                model="microsoft-embedding-1-large",
                model_version=os.environ["AZURE_DATA_AI_MODEL_VERSION"],
                dimensions="1536",
                inputs=[item],
                vector_type="dense",
                delivery="inline",
            )
            if len(response.data) != 1:
                raise ValueError("Expected one embedding for the input.")
            result = response.data[0]
            if not isinstance(result, MultimodalDenseEmbedding):
                raise ValueError("Expected an inline dense embedding.")
            if result.id != item["id"] or len(result.embedding) != 1536:
                raise ValueError("The embedding doesn't match the input.")
            print(result.id, len(result.embedding), response.model_version)
```

### Generate image embeddings with a user-delegation SAS

Image inputs require an existing Azure Blob Storage image and a shared access
signature (SAS). Use a blob-scoped, read-only, HTTPS-only user-delegation SAS
with a short expiry. The identity that signs the SAS must also call the
embedding endpoint. Don't use an account-key SAS or a token created by a
different identity.

Set `AZURE_STORAGE_ACCOUNT_NAME`, `AZURE_STORAGE_CONTAINER_NAME`, and
`AZURE_STORAGE_IMAGE_BLOB_NAME` to your image location. Keep the endpoint and
model version configured as in the text example. The example creates the SAS
at runtime and sends a retrieval query with the image.

```python
import os
from datetime import datetime, timedelta, timezone

from azure.data.ai import InferenceClient
from azure.data.ai.models import MultimodalDenseEmbedding
from azure.identity import DefaultAzureCredential
from azure.storage.blob import (
    BlobSasPermissions,
    BlobServiceClient,
    generate_blob_sas,
)

account_name = os.environ["AZURE_STORAGE_ACCOUNT_NAME"]
container_name = os.environ["AZURE_STORAGE_CONTAINER_NAME"]
blob_name = os.environ["AZURE_STORAGE_IMAGE_BLOB_NAME"]
account_url = f"https://{account_name}.blob.core.windows.net"

with DefaultAzureCredential() as credential:
    now = datetime.now(timezone.utc)
    starts_on = now - timedelta(minutes=5)
    expires_on = now + timedelta(minutes=15)
    with BlobServiceClient(account_url, credential=credential) as storage:
        delegation_key = storage.get_user_delegation_key(starts_on, expires_on)
        image_url = storage.get_blob_client(container_name, blob_name).url
        image_sas = generate_blob_sas(
            account_name=account_name,
            container_name=container_name,
            blob_name=blob_name,
            user_delegation_key=delegation_key,
            permission=BlobSasPermissions(read=True),
            start=starts_on,
            expiry=expires_on,
            protocol="https",
        )

    with InferenceClient(
        endpoint=os.environ["AZURE_DATA_AI_ENDPOINT"],
        credential=credential,
    ) as client:
        response = client.multi_modal_embed(
            model="microsoft-embedding-1-large",
            model_version=os.environ["AZURE_DATA_AI_MODEL_VERSION"],
            dimensions="1536",
            inputs=[
                {
                    "id": "scene-question",
                    "type": "query",
                    "content": "A wooden footbridge crossing a forest stream.",
                },
                {
                    "id": "catalog-photo",
                    "type": "image",
                    "url": image_url,
                    "sas_token": image_sas,
                },
            ],
            vector_type="dense",
            delivery="inline",
        )

if len(response.data) != 2 or {item.id for item in response.data} != {
    "scene-question", "catalog-photo"
}:
    raise ValueError("Expected embeddings for the query and image.")
for result in response.data:
    if not isinstance(result, MultimodalDenseEmbedding):
        raise ValueError("Expected an inline dense embedding.")
    if len(result.embedding) != 1536:
        raise ValueError("Unexpected dense vector dimensions.")
    print(result.id, len(result.embedding))
```

Set `url` and `sas_token` as separate keys in the Python image-input dictionary.
Keep the blob URL free of SAS query parameters, and don't
send inline base64 image content. A SAS is a credential: don't print the token,
serialize the image request to logs, or enable HTTP body logging for it.
Generate a fresh token if it expires before a retry.

### Model selection and JSON documents

The TypeSpec example uses `semantic-reranker-v1` as a model name. Model availability
depends on the endpoint: use a model your endpoint supports, or omit `model` to use
its default.

```python
import json

result = client.semantic_rerank(
    {
        "query": "capital of France",
        "documents": [
            json.dumps({"description": "Paris is the capital of France."}),
            json.dumps({"description": "Berlin is the capital of Germany."}),
        ],
        "model": "semantic-reranker-v1",
        "documentType": "json",
        "targetPaths": "description",
        "topK": 1,
        "batchSize": 2,
        "sort": True,
        "returnDocuments": True,
        "returnSentenceScore": True,
    }
)

metadata = result.get("meta", {})
print(metadata.get("modelName"), metadata.get("modelVersion"))
```

### Sentence-level scores

```python
result = client.semantic_rerank(
    {
        "query": "capital of France",
        "documents": ["Paris is the capital of France. It is on the Seine."],
        "returnDocuments": True,
        "returnSentenceScore": True,
    }
)

for document in result.get("scores", []):
    for sentence in document.get("sentenceScores", []):
        print(document["index"], sentence["index"], sentence["score"])
```

### Async

Install `aiohttp` separately to use the default async transport. Use an async
token credential from `azure.identity.aio` if authenticating with Microsoft Entra.

```python
import os

from azure.core.credentials import AzureKeyCredential
from azure.data.ai.aio import InferenceClient

async def rerank():
    async with InferenceClient(
        os.environ["AZURE_DATA_AI_ENDPOINT"],
        AzureKeyCredential(os.environ["AZURE_DATA_AI_KEY"]),
    ) as client:
        return await client.semantic_rerank(
            {"query": "capital of France", "documents": ["Paris", "Berlin"]}
        )
```

### Response diagnostics and retries

Use the standard Azure Core response hook to capture `X-Correlation-ID` for
service diagnostics:

```python
from azure.core.utils import case_insensitive_dict

response_headers = case_insensitive_dict()
result = client.semantic_rerank(
    {"query": "capital of France", "documents": ["Paris", "Berlin"]},
    raw_response_hook=lambda response: response_headers.update(
        response.http_response.headers
    ),
)
print(response_headers.get("X-Correlation-ID"))
```

The generated clients inherit Azure Core's native retry and timeout defaults.
These are not necessarily identical to the .NET SDK's defaults. Configure the
desired values when constructing the client:

```python
client = InferenceClient(
    endpoint,
    credential,
    retry_total=3,          # Use 0 to disable automatic retries.
    retry_backoff_max=60,
    connection_timeout=100,
    read_timeout=100,
)
```

Azure Core also supports separate `retry_connect`, `retry_read`, and `retry_status`
limits. For reranking POST requests, include `retry_on_methods=["POST"]` on the
operation call when retries should apply to statuses such as 429 and 502 even
without `Retry-After`:

```python
result = client.semantic_rerank(request, retry_on_methods=["POST"])
```

A service `Retry-After` can require a wait longer than the calculated backoff cap.
Connection/read timeouts are not an overall deadline including retries. Automatic
service-level .NET retry-default customization is not part of this generated baseline.

## Troubleshooting

Unsuccessful service responses raise `azure.core.exceptions.HttpResponseError`
or a more specific Azure Core exception, such as `ClientAuthenticationError`.
For reranking JSON error responses, inspect `error.response.json()["error"]` to retrieve
the required `code` and `message` and any additional `ProblemDetails` fields.
Errors can include a `target`, detailed errors, and nested `innererror` information.
Response headers retain `x-ms-error-code`, `X-Correlation-ID`, and `Retry-After`.

Embedding errors can expose a typed model through `error.model`; inspect its
`code` for the service error. For `EMBEDDING_INPUT_INVALID`, check the request
shape and content types. For `EMBEDDING_BLOB_READ_FAILED`, check that the blob
exists, is reachable, and has a valid read-only user-delegation SAS signed by
the inference caller. Don't include the SAS or request body in diagnostics.

Do not log credentials or sensitive document content. For HTTP 401/403, confirm
the credential type and that the key belongs to the endpoint with key-based
authentication enabled, or that the Entra token has the correct audience and
resource permissions.

## Next steps

Follow the [embedding-generation guide][cosmos_embeddings] to configure the
Cosmos DB experience and use returned vectors in your retrieval workflow.
Explore the [samples][samples] for additional reranking examples.

## Contributing

This project welcomes contributions and suggestions. Most contributions require
you to agree to a Contributor License Agreement (CLA) declaring that you have
the right to, and actually do, grant us the rights to use your contribution.
For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether
you need to provide a CLA and decorate the PR appropriately (e.g., label,
comment). Simply follow the instructions provided by the bot. You will only
need to do this once across all repos using our CLA.

This project has adopted the
[Microsoft Open Source Code of Conduct][code_of_conduct]. For more information,
see the Code of Conduct FAQ or contact opencode@microsoft.com with any
additional questions or comments.

<!-- LINKS -->
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[azure_sub]: https://azure.microsoft.com/free/
[cosmos_reranker]: https://learn.microsoft.com/azure/cosmos-db/gen-ai/semantic-reranker
[cosmos_embeddings]: https://learn.microsoft.com/azure/cosmos-db/gen-ai/embedding-generation
[samples]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/dataai/azure-data-ai/samples/README.md
