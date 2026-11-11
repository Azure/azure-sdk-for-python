# Azure Data AI client library for Python

`azure-data-ai` provides access to **Azure Data AI**, hosted by Azure Inference Service. It
supports semantic reranking: rank caller-supplied documents by their relevance to a
query, optionally returning the documents and sentence-level scores. Version 1.1.0b1 adds multimodal
embedding (preview), which embeds text, search queries and document images.

Version 1.0.0 uses the `2026-10-30` service API. Version 1.1.0b1 uses `2026-11-01-preview` by default,
which multimodal embedding requires; semantic reranking also works with `2026-10-30`.

## Getting started

### Install the package

```bash
python -m pip install azure-data-ai
```

For multimodal embedding (preview), install the latest beta with `python -m pip install --pre azure-data-ai`.

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

### Authenticate the client

Use `AzureKeyCredential` for API-key authentication:

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

`InferenceClient` is the entry point. Call `client.semantic_rerank(request)`
directly; there is no intermediate inference subclient.

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

### Multimodal embedding

Call `client.get_embeddings(inputs=[...], ...)` to embed text documents (`kind="text"`), search queries
(`kind="query"`) and document images (`kind="image"`) with Microsoft Embedding 1-large
(`microsoft-embedding-1-large`). Items are plain dictionaries using JSON field names, and the request options (`model`,
`dimensions`, `vector_kind`, `delivery`, ...) are keyword arguments. A request can currently have at most one text or
query item and up to 8 images. You can also pass the whole request as a dictionary with the service's JSON names.

- **Text and queries** are sent inline in `content`. Text over the model's token limit (currently 8,192 tokens)
  isn't rejected: only its start is embedded, the item has `truncated=True` and `input_tokens`, and
  `result.warnings` has an entry with code `EmbeddingWarningCode.INPUT_TRUNCATED` (number 1001).
- **Images** are read from your Azure Blob Storage, where the endpoint enables blob inputs: send the blob's `url`
  and, in `sasToken`, a user delegation SAS for that blob. The SAS must be read-only (`sp=r`), https-only and
  signed by the same Microsoft Entra identity that calls the API; a SAS valid for more than 15 minutes is accepted
  with warning `EmbeddingWarningCode.SAS_LONG_LIVED` (number 1002). Inline images (a `data:` URI or base64 in
  `content`) work only where the endpoint allows them, which is off by default.
- **Vectors:** each item in `result.data` is a `MultimodalDenseEmbedding` (`embedding`), a
  `MultimodalMultiVectorEmbedding` (`multi_embedding` with `shape`) or, with `vector_kind="dense_multi"`, a
  `MultimodalDenseAndMultiVectorEmbedding` with both from one model run (`multi_dimensions` sets the
  multi-vector width). With `encoding_format="base64"`, vectors are little-endian values of `output_data_kind`.
- **Usage:** items report `tokens` (and `visual_tokens` for images); `result.usage` reports `prompt_tokens`,
  `text_tokens`, `visual_tokens` and `image_count`. A request body can be up to 30,000,000 bytes.

```python
from azure.data.ai.models import MultimodalDenseEmbedding

result = client.get_embeddings(
    inputs=[{"id": "doc-1", "kind": "text", "content": "Invoice terms: net 30."}],
    dimensions=1536,
)
item = result.data[0]
if isinstance(item, MultimodalDenseEmbedding):
    print(item.id, len(item.embedding))
```

To embed an image, make a user delegation SAS for the blob with the identity that calls the API. For example,
with `azure-storage-blob` (not a dependency of this package):

```python
import datetime as dt

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobSasPermissions, BlobServiceClient, generate_blob_sas

credential = DefaultAzureCredential()  # also pass this credential to InferenceClient
account, container, blob = "<storage-account>", "pages", "p1.jpg"
service = BlobServiceClient(f"https://{account}.blob.core.windows.net", credential=credential)
now = dt.datetime.now(dt.timezone.utc)
key = service.get_user_delegation_key(now - dt.timedelta(minutes=5), now + dt.timedelta(hours=1))
sas_token = generate_blob_sas(
    account, container, blob, user_delegation_key=key, permission=BlobSasPermissions(read=True),
    protocol="https", start=now - dt.timedelta(minutes=5), expiry=now + dt.timedelta(minutes=15),
)

result = client.get_embeddings(
    inputs=[
        {"kind": "query", "content": "When is the invoice due?"},
        {
            "id": "page-1",
            "kind": "image",
            "url": f"https://{account}.blob.core.windows.net/{container}/{blob}",
            "sasToken": sas_token,
        },
    ],
    delivery="inline",
)
```

Results come back in `result.data`, or with `delivery="link"` as `result.output`: a read-only link, valid for up
to 15 minutes, to a JSON file with the same body as an inline response. Without `delivery`, a request with images
gets a link where the endpoint has a result store. Read the file with any HTTP client, or with
`BlobClient.from_blob_url(output.url, credential=AzureSasCredential(output.sas_token))`, and check its size and
hash. `output.sas_token` is a credential: don't log or store it.

```python
import hashlib
import json
import urllib.request

from azure.data.ai.models import EmbeddingResult

output = result.output  # from a request with delivery="link"
with urllib.request.urlopen(f"{output.url}?{output.sas_token}") as response:
    data = response.read()
if len(data) != output.size_in_bytes or hashlib.sha256(data).hexdigest() != output.sha256:
    raise ValueError("The result file doesn't match output.size_in_bytes and output.sha256.")
results = EmbeddingResult(json.loads(data))
```

## Examples

See the [samples][samples] for runnable sync and async examples.

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
For a JSON error response, inspect `error.response.json()["error"]` to retrieve
the required `code` and `message` and any additional `ProblemDetails` fields.
Errors can include a `target`, detailed errors, and nested `innererror` information.
Response headers retain `x-ms-error-code`, `X-Correlation-ID`, and `Retry-After`.

Do not log credentials or sensitive document content. For HTTP 401/403, confirm
the credential type and that the key belongs to the endpoint with key-based
authentication enabled, or that the Entra token has the correct audience and
resource permissions.

## Next steps

Explore the [samples][samples] to rerank text or JSON documents with API-key or
Microsoft Entra authentication. Adapt the request's model, target paths, and
scoring options to your application's documents and endpoint.

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
[samples]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/dataai/azure-data-ai/samples/README.md
