# Azure Data AI client library for Python

`azure-data-ai` provides access to **Azure Inference Service**. This initial preview
supports semantic reranking: rank caller-supplied documents by their relevance to a
query, optionally returning the documents and sentence-level scores.

The Python API accepts and returns ordinary dictionaries. You do not need to import
or construct request or response model classes. This package does not depend on
`azure-cosmos`, `openai`, or another database SDK. Embedding APIs are not included
in this preview.

The package uses the `2026-09-01-preview` service API.

The runtime is a thin handwritten wrapper around Azure Core's `PipelineClient`
and `AsyncPipelineClient`. Azure Core performs the HTTP requests and supplies the
authentication, retry, transport, and diagnostic policies. The SDK only supplies
the service URL, API version, request dictionary, and error handling.
The public clients delegate reranking POST requests to internal `_reranker.py`
implementations, which reuse the clients' existing Azure Core pipelines.

## Getting started

### Install the package

```bash
python -m pip install --pre azure-data-ai
```

For local development before this preview is published, run `python -m pip install -e .`
from this package directory instead.

### Prerequisites

- Python 3.10 or later.
- An [Azure subscription][azure_sub] and an Azure Inference Service endpoint.
- A key issued for an Azure Inference Service endpoint with key-based authentication
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
from azure.data.ai import InferenceServiceClient

with InferenceServiceClient(
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
`AzureKeyCredentialPolicy`. Both synchronous and asynchronous clients also accept
a raw key string directly:

```python
client = InferenceServiceClient(endpoint, credential=key)
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

from azure.data.ai import InferenceServiceClient
from azure.identity import DefaultAzureCredential

with DefaultAzureCredential() as credential:
    with InferenceServiceClient(
        os.environ["AZURE_DATA_AI_ENDPOINT"], credential
    ) as client:
        result = client.semantic_rerank(
            {"query": "capital of France", "documents": ["Paris", "Berlin"]}
        )
```

The client requests tokens for `https://dbinference.azure.com/.default`.

## Key concepts

`InferenceServiceClient` is the entry point. Call `client.semantic_rerank(request)`
directly; there is no intermediate inference subclient.

Dictionary keys use the service's JSON names, not Python attribute names. For
example, use `"topK"`, not `"top_k"`, and read `result["scores"][0]["score"]`, not
`result.scores[0].score`. Dictionaries are sent as supplied; the service validates
their contents.

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
| `targetPaths` | `str` | Optional string identifying the JSON paths to rank when `documentType` is `json`. |
| `returnSentenceScore` | `bool` | Optional. Include sentence-level scores. |

Put these options inside the request dictionary, not in method keyword arguments.
Omitted options use service-defined defaults. The SDK does not restrict model names
or filter additional request fields.

Responses contain optional `scores` and `meta` keys. Score entries can include
`index`, `score`, `document`, and `sentenceScores`. Metadata can include
`tokenUsage`, `latency`, `modelName`, and `modelVersion`. All nested objects are
dictionaries too.

The SDK follows the pinned TypeSpec contract without renaming response keys or
normalizing legacy payloads. Use an endpoint implementing the
`2026-09-01-preview` contract. The samples accept an optional `--model` argument
and otherwise leave model selection to the service.

## Examples

See the [samples](samples/README.md) for runnable sync and async examples.

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
from azure.data.ai.aio import InferenceServiceClient

async def rerank():
    async with InferenceServiceClient(
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

Standard Azure Core retry policies apply, including `Retry-After` handling for
HTTP 429. Configure `retry_total`, `connection_timeout`, and `read_timeout` on the
client as needed. This package does not inherit the Cosmos DB SDK's retry defaults.

## Troubleshooting

Unsuccessful service responses raise `azure.core.exceptions.HttpResponseError`
or a more specific Azure Core exception, such as `ClientAuthenticationError`.
For a JSON `ProblemDetails` response, inspect `error.response.json()` to retrieve
its fields. Response headers retain `X-Correlation-ID` and `Retry-After`.

Do not log credentials or sensitive document content. For HTTP 401/403, confirm
the credential type and that the key belongs to the endpoint with key-based
authentication enabled, or that the Entra token has the correct audience and
resource permissions.

## Development

`tsp-location.yaml` records the REST contract from
[Azure/azure-rest-api-specs-pr#30255][spec_pr] at
`de6631e6066f6eb00afa338ac8544c950e1fdda0`. TypeSpec remains the contract reference,
but **does not generate this Python runtime**. Do not run `tsp-client update` in
this package: it would restore the generated implementation. Update the thin
clients, reranking helpers, and their contract tests deliberately when the service API changes.

The public surface is `InferenceServiceClient.semantic_rerank(request)`, plus
client lifecycle methods. Generic raw-request methods, binary-body overloads,
model classes, and general-purpose serialization helpers are intentionally absent.

To run the offline tests:

```bash
python -m pip install -r dev_requirements.txt
python -m pip install -e .
python -m pytest tests
```

This publishable package remains `sdk/inferenceservice/azure-data-ai`, with the
`azure.data.ai` import namespace. The separate prototype lives in
`sdk/cosmos/azure-data-ai-inference` and uses `azure.data.ai_inference`, so it cannot
shadow the publishable SDK when an IDE adds the prototype to its source roots.

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
[spec_pr]: https://github.com/Azure/azure-rest-api-specs-pr/pull/30255
[python_guidelines]: https://azure.github.io/azure-sdk/python_design.html
