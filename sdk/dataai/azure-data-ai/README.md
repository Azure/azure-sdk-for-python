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

The reranking package uses the `2026-10-30` service API. Embedding examples target
`2026-11-01-preview` and require an embedding-enabled preview SDK and endpoint;
reranking-only releases don't provide `multi_modal_embed`.

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
**Embedding User** to the calling Microsoft Entra identity at the companion
inference-account scope. Use the embedding endpoint, not the Cosmos DB document
endpoint or a reranking endpoint.

Install `azure-identity` for the embedding examples. Image inputs also require an
existing Azure Blob Storage image and a user-delegation SAS. See
[Prepare image inputs](#prepare-image-inputs) for permissions and token generation.

```bash
python -m pip install azure-identity
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

Embedding generation converts text and images into vectors for semantic
retrieval. Microsoft Embedding 1 embeds documents, search queries, and images
into the same vector space. Your application receives the vectors; the operation
doesn't write them to Azure Cosmos DB or search a container.

> **Note:** The embedding model used in Embedding Generation is based on the
> [Qwen 3.5 model](https://huggingface.co/Qwen/Qwen3.5-2B) and has been fine-tuned
> by Microsoft.

Call `client.multi_modal_embed(...)` with keyword arguments and plain
dictionaries in `inputs`. You don't need request or input-item wrapper objects.

#### Embedding API parameters

| Parameter | Required | Default | Description |
| --- | --- | --- | --- |
| `model` | Yes | None | Use `microsoft-embedding-1-large`. Don't use a Foundry deployment name. |
| `model_version` | Yes | None | The model version, such as `"5"`. Use the same version for documents and queries. |
| `inputs` | Yes | None | A list of dictionaries. See [Embedding input fields](#embedding-input-fields). |
| `dimensions` | No | Model's native width | Vector width as a string. Dense: `"2560"` or `"1536"`. Multi-vector: `"128"` or `"256"`. |
| `vector_type` | No | `dense` | `dense` returns one vector per input. `multi` returns token-level vectors for late-interaction scoring. `both` returns both. |
| `max_num_vectors` | No | No limit | The maximum number of token-level vectors per input for `multi` or `both`, not the batch size. |
| `delivery` | No | `inline` | `inline` returns vectors in the response for text, query, and image inputs. `link` returns a results-file reference. |

#### Embedding input fields

| Key | Used with | Description |
| --- | --- | --- |
| `type` | All | `text` for stored content, `query` for search queries, or `image`. |
| `content` | Text, query | The text to embed. |
| `url` | Image | The plain HTTPS blob URL, without a query string. |
| `sas_token` | Image | A read-only user-delegation SAS for the blob. |
| `id` | All (optional) | A label that the result echoes. It doesn't look up a Cosmos DB item. |

#### Embedding request limits

| Limit | Current preview value |
| --- | --- |
| Text or query inputs | At most one per request. Send separate requests for separate documents or queries. |
| Image inputs | Up to eight, plus one optional text or query input. |
| Image size | At most 20 MiB and 50 megapixels per image, and 20 MiB total per request. |
| Image formats | JPEG, PNG, GIF, and WebP. |
| Request body | At most 30,000,000 bytes. |

Split larger workloads into requests and reuse the client. The embedding API
has no `batch_size` or `top_k` argument; set search-result limits in your
retrieval query instead. Inputs over 8,192 text tokens can be truncated from
the end. Inspect `warnings` and each result's `truncated` indicator.

#### Read embedding output

Read each dense vector from `response.data` and match it to its input ID:

```python
vectors = {item.id: item.embedding for item in response.data}
```

Keep the model, version, vector type, and dimensions consistent for vectors you
compare. Multi-vector output returns a matrix in `multi_embedding` and its
`shape`; don't flatten it into one vector. Link delivery leaves `data` empty
and returns the results-file URL and a separate SAS token in `response.output`.
Don't log that token.

Use `response.model` and `response.model_version` to record the resolved model.
`response.usage.text_tokens` and `response.usage.visual_tokens` report input
usage. For inference charges, see the [embedding-generation pricing guide][cosmos_embedding_pricing].

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

### Generate text and image embeddings

Prepare the image SAS using [Prepare image inputs](#prepare-image-inputs).
Set the endpoint and image settings, then sign in as the identity that has
**Embedding User**. Sign the image SAS as that same identity.

```bash
export AZURE_DATA_AI_ENDPOINT="<embedding-endpoint>"
export IMAGE_BLOB_URL="https://<storage-account>.blob.core.windows.net/<container>/<image-blob-name>"
export IMAGE_SAS_TOKEN="<user-delegation-sas-without-leading-question-mark>"
az login
```

The following example embeds one text document and one image in a single call.
Save it as `generate_embeddings.py` and run `python generate_embeddings.py`:

```python
import os

from azure.data.ai import InferenceClient
from azure.identity import DefaultAzureCredential

with DefaultAzureCredential() as credential:
    with InferenceClient(
        endpoint=os.environ["AZURE_DATA_AI_ENDPOINT"],
        credential=credential,
    ) as client:
        response = client.multi_modal_embed(
            model="microsoft-embedding-1-large",
            model_version="5",
            dimensions="1536",  # Dense embeddings support up to 2,560 dimensions.
            inputs=[
                {
                    "id": "trail-guide",
                    "type": "text",
                    "content": "The lakeside walking route is accessible throughout the year.",
                },
                {
                    "id": "trail-map",
                    "type": "image",
                    "url": os.environ["IMAGE_BLOB_URL"],
                    "sas_token": os.environ["IMAGE_SAS_TOKEN"],
                },
            ],
        )

vectors = {item.id: item.embedding for item in response.data}
for item_id, vector in vectors.items():
    print(f"{item_id}: {len(vector)} dimensions")
```

To embed text only, omit the image dictionary. Keep `vectors` and `response`
if you want to store the embeddings with their model metadata.

### Generate a retrieval-query embedding

Use `query` for what users search with and `text` for content you store. The
model encodes them differently for retrieval. Append this code to the same
script, using the same model, version, and dimensions as the source vectors:

```python
with DefaultAzureCredential() as credential:
    with InferenceClient(
        endpoint=os.environ["AZURE_DATA_AI_ENDPOINT"],
        credential=credential,
    ) as client:
        query_response = client.multi_modal_embed(
            model="microsoft-embedding-1-large",
            model_version="5",
            dimensions="1536",  # Must match the stored vectors.
            inputs=[
                {
                    "id": "route-question",
                    "type": "query",
                    "content": "Which walking route follows the lake?",
                }
            ],
        )

query_vector = query_response.data[0].embedding
```

Use the Azure Cosmos DB SDK to store source vectors and compare them with
`query_vector`. The [Cosmos DB storage and search example][cosmos_embedding_search]
shows container requirements and a parameterized `VectorDistance` query.
**Embedding User** doesn't grant permission to read or write Cosmos DB documents;
assign the separate data-plane roles described in that guide.

### Prepare image inputs

The service reads images from Azure Blob Storage, not inline base64 content.
Pass a plain HTTPS blob URL and a separate blob-scoped, read-only user-delegation
SAS. Sign the SAS as the identity that calls the embedding endpoint; don't use an
account-key SAS or one signed by a different identity.

The caller needs blob read access and permission to obtain a user-delegation
key. **Storage Blob Data Reader** at storage-account scope provides both. For
container-scoped read access, also assign **Storage Blob Delegator** at
storage-account scope. A SAS doesn't bypass storage network restrictions.

Use HTTPS-only access and an expiry of about 15 minutes. Keep tokens out of logs,
telemetry, source code, and error messages. Don't enable HTTP body logging for
requests with image SAS tokens. Generate a fresh token if one expires before a retry.

For manual token creation, follow the [portal and CLI SAS steps][cosmos_embedding_images].
For application code, install the Storage library:

```bash
python -m pip install azure-storage-blob
```

Set `AZURE_STORAGE_ACCOUNT_NAME`, `AZURE_STORAGE_CONTAINER_NAME`, and
`AZURE_STORAGE_IMAGE_BLOB_NAME` to an existing image. This code creates
`blob_url` and `sas_token`; pass them as the image input's `url` and `sas_token`.
Reuse the same calling identity for Storage and inference.

```python
import os
from datetime import datetime, timedelta, timezone

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobSasPermissions, BlobServiceClient, generate_blob_sas

account_name = os.environ["AZURE_STORAGE_ACCOUNT_NAME"]
container_name = os.environ["AZURE_STORAGE_CONTAINER_NAME"]
blob_name = os.environ["AZURE_STORAGE_IMAGE_BLOB_NAME"]

with DefaultAzureCredential() as credential:
    now = datetime.now(timezone.utc)
    starts_on = now - timedelta(minutes=5)
    expires_on = now + timedelta(minutes=15)

    with BlobServiceClient(
        account_url=f"https://{account_name}.blob.core.windows.net",
        credential=credential,
    ) as storage:
        delegation_key = storage.get_user_delegation_key(starts_on, expires_on)
        blob_url = storage.get_blob_client(container_name, blob_name).url
        sas_token = generate_blob_sas(
            account_name=account_name,
            container_name=container_name,
            blob_name=blob_name,
            user_delegation_key=delegation_key,
            permission=BlobSasPermissions(read=True),
            start=starts_on,
            expiry=expires_on,
            protocol="https",
        )
```

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

For embedding errors, inspect the service error `code` on `error.model` when
available:

| Error | What to check |
| --- | --- |
| HTTP 403 | The caller's **Embedding User** role, inference-account scope, endpoint, and role-assignment propagation. |
| HTTP 429 | Respect `Retry-After` and cap the number of retries. |
| `EMBEDDING_INPUT_INVALID` | Check [input fields](#embedding-input-fields) and [request limits](#embedding-request-limits). |
| `EMBEDDING_BLOB_READ_FAILED` | Confirm the blob exists, the SAS is valid and signed by the inference caller, and network rules allow service access. |

Don't include image SAS tokens or request bodies in diagnostics.

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
[cosmos_embedding_pricing]: https://learn.microsoft.com/azure/cosmos-db/gen-ai/embedding-generation#pricing
[cosmos_embedding_search]: https://learn.microsoft.com/azure/cosmos-db/gen-ai/embedding-generation#store-and-search-vectors-in-azure-cosmos-db
[cosmos_embedding_images]: https://learn.microsoft.com/azure/cosmos-db/gen-ai/embedding-generation#prepare-image-inputs
[samples]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/dataai/azure-data-ai/samples/README.md
