# Azure Cosmos DB AI extensions for Python

`azure-cosmos-ai` is a companion package to [`azure-cosmos`](https://pypi.org/project/azure-cosmos/) that provides AI-related extensions for the Azure Cosmos DB SDK.

It ships the default Azure OpenAI implementation of the `EmbeddingProvider` Protocol introduced in `azure-cosmos` 4.16.0b3, used by the SDK to generate vector embeddings for `GenerateEmbeddings(...)` query expressions.

## Getting started

### Install the package

```bash
pip install azure-cosmos-ai
```

### Prerequisites

- Python 3.9 or later
- An Azure subscription
- An existing Azure Cosmos DB for NoSQL account
- An Azure OpenAI resource with an embeddings deployment (e.g. `text-embedding-3-small`)

## Key concepts

The provider stores **only the credential**. Endpoint, deployment name, and dimensions are read from the container's `vectorEmbeddingPolicy.embeddingSource` and forwarded to the provider by the Cosmos SDK at query time. This keeps the policy as the single source of truth.

## Examples

### API key (sync)

```python
from azure.cosmos import CosmosClient
from azure.cosmos.ai import AzureOpenAIEmbeddingProvider

provider = AzureOpenAIEmbeddingProvider(credential="<aoai-api-key>")

client = CosmosClient(
    url="https://my-cosmos.documents.azure.com:443/",
    credential="<cosmos-key>",
    embedding_provider=provider,
)
```

### Entra — shared credential (recommended)

Pass the same `TokenCredential` to `CosmosClient` (for Cosmos RBAC) and to the
provider (for Azure OpenAI). One identity covers both services.

```python
from azure.cosmos.aio import CosmosClient
from azure.cosmos.ai.aio import AzureOpenAIEmbeddingProvider
from azure.identity.aio import DefaultAzureCredential

async with DefaultAzureCredential() as cred:
    async with AzureOpenAIEmbeddingProvider(credential=cred) as provider:
        async with CosmosClient(
            url="https://my-cosmos.documents.azure.com:443/",
            credential=cred,
            embedding_provider=provider,
        ) as client:
            ...
```

### Supported credential types

| Type                                           | Auth mode |
|------------------------------------------------|-----------|
| `str`                                          | Azure OpenAI API key |
| `azure.core.credentials.AzureKeyCredential`    | Azure OpenAI API key |
| `azure.core.credentials.TokenCredential` (sync) / `azure.core.credentials_async.AsyncTokenCredential` (async) | Entra (RBAC) |

## Troubleshooting

The provider deliberately does not wrap exceptions thrown by the underlying
[`openai`](https://pypi.org/project/openai/) client (e.g. `openai.BadRequestError`,
`openai.AuthenticationError`, `openai.RateLimitError`, `openai.APIConnectionError`).
Inputs that exceed the model's context length surface as `openai.BadRequestError`
with code `context_length_exceeded`.

Retries are handled by the `openai` SDK; this provider adds no extra retry policy.

## Contributing

This project welcomes contributions and suggestions. See the [Azure SDK for Python contributing guide](https://github.com/Azure/azure-sdk-for-python/blob/main/CONTRIBUTING.md) for details.
