# Azure Data AI client library for Python

`azure-data-ai` provides access to **Azure Data AI**, hosted by Azure Inference Service. This initial preview
supports semantic reranking: rank caller-supplied documents by their relevance to a
query, optionally returning the documents and sentence-level scores.

The Python API accepts generated request models or ordinary dictionaries and returns
generated response models that also support dictionary-style access. This package does not depend on
`azure-cosmos`, `openai`, or another database SDK. Embedding APIs are not included
in this preview.

The package uses the `2026-09-01-preview` service API.

The runtime is generated from TypeSpec with `@azure-tools/typespec-python`.
It includes client configuration, operation implementations, request/response models,
TypedDict definitions, and serialization helpers. Azure Core supplies the HTTP
transport, authentication, retry, and diagnostic policies.

## Getting started

### Install the package

```bash
python -m pip install --pre azure-data-ai
```

For local development before this preview is published, run `python -m pip install -e .`
from this package directory instead.

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
from azure.data.ai import AzureDataAIClient

with AzureDataAIClient(
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
client = AzureDataAIClient(endpoint, credential=AzureKeyCredential(key))
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

from azure.data.ai import AzureDataAIClient
from azure.identity import DefaultAzureCredential

with DefaultAzureCredential() as credential:
    with AzureDataAIClient(
        os.environ["AZURE_DATA_AI_ENDPOINT"], credential
    ) as client:
        result = client.semantic_rerank(
            {"query": "capital of France", "documents": ["Paris", "Berlin"]}
        )
```

The client requests tokens for `https://dbinference.azure.com/.default`.

## Key concepts

`AzureDataAIClient` is the entry point. Call `client.semantic_rerank(request)`
directly; there is no intermediate inference subclient.

Dictionary keys use the service's JSON names, such as `"topK"`. Generated model
attributes use Python names, such as `top_k`. Both response access forms work:
`result["scores"][0]["score"]` and `result.scores[0].score`. Use `result.as_dict()`
when an ordinary nested dictionary is needed.

```python
from azure.data.ai.models import SemanticRerankingDocumentType, SemanticRerankingInferenceRequest

request = SemanticRerankingInferenceRequest(
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

| Request key | Type | Meaning |
| --- | --- | --- |
| `query` | `str` | Required nonempty query string. |
| `documents` | `list[str]` | Required nonempty list of strings to rank. |
| `model` | `str` | Optional model name supported by the endpoint. Omit it to use the service's default model. |
| `returnDocuments` | `bool` | Optional. Include document text in the response. |
| `topK` | `int` | Optional. Maximum number of results to return, from 1 to 2147483647. |
| `batchSize` | `int` | Optional. Number of documents processed per batch, from 1 to 2147483647. |
| `sort` | `bool` | Optional. Return scores sorted by relevance. |
| `documentType` | `str` | Optional document format, such as `text` or `json`. JSON documents are JSON-encoded strings. |
| `targetPaths` | `str` | Required for JSON documents. Use dot notation for nested properties, such as `meta.content`, and commas for multiple paths, such as `meta.content,id`. |
| `returnSentenceScore` | `bool` | Optional. Include sentence-level scores. |

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
attributes are `datetime.timedelta` values; dictionary-style access and `as_dict()`
retain the numeric millisecond representation.

Each sentence score has a nonnegative, zero-based `index` and a `score` in the
inclusive range 0–1. Sentence indices are not capped at 2.

The SDK follows the pinned TypeSpec contract without renaming response keys or
normalizing legacy payloads. Use an endpoint implementing the
`2026-09-01-preview` contract. The samples set `model` in their request dictionaries.
Choose a model supported by your endpoint, or remove that field to use the service's
default model.

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
from azure.data.ai.aio import AzureDataAIClient

async def rerank():
    async with AzureDataAIClient(
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
client = AzureDataAIClient(
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

## Development

`tsp-location.yaml` records the generation source and pins the TypeSpec contract to
`30d0780f8eb3b8c94e98fd681993ae8d6069317d`. Its service title is **Azure Data AI**
and its namespace is `Azure.Data.AI`; the route, authentication header/token
audience, request fields, and API version remain unchanged.
This package adopts the default output of `@azure-tools/typespec-python` 0.63.8,
generated from that contract. The emitter dependency and lock files under `eng/`
pin the generation toolchain. Request/response model generation is enabled.

The generated Python API uses `AzureDataAIClient` in both `azure.data.ai` and
`azure.data.ai.aio`. The TypeSpec explicitly selects this client name for Python
and C#. The package lives at
`sdk/dataai/azure-data-ai`, matching the spec's `sdk/dataai` service directory.

The public surface includes `AzureDataAIClient.semantic_rerank(request)`,
request/response models, TypedDict definitions, raw `send_request`, and client
lifecycle methods. Reranking accepts model, dictionary, and binary request forms
and treats HTTP 200 as the successful response.

Regenerate with the repository's standard TypeSpec workflow, for example from this
package directory:

```bash
npm exec --prefix ../../../eng/common/tsp-client --no -- tsp-client update \
  --emitter-options "package-version=0.1.0b1"
```

Do not edit files marked as generated. Keep handwritten customizations in the
supported `_patch.py` hooks, and retain tests and samples across regeneration.

To run the offline tests:

```bash
python -m pip install -r dev_requirements.txt
python -m pip install -e .
python -m pytest tests
```

Follow the [Azure SDK Python design guidelines][python_guidelines] for changes.

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
[python_guidelines]: https://azure.github.io/azure-sdk/python_design.html
