# Azure Cosmos DB AI extensions for Python

`azure-cosmos-ai` is a companion package to [`azure-cosmos`](https://pypi.org/project/azure-cosmos/) that provides AI-related extensions for the Azure Cosmos DB SDK.

It will host the default Azure OpenAI implementation of the `EmbeddingProvider` Protocol introduced in `azure-cosmos` 4.16.0b3, used by the SDK to generate vector embeddings for `GenerateEmbeddings(...)` query expressions.

## Getting started

### Install the package

```bash
pip install azure-cosmos-ai
```

### Prerequisites

- Python 3.9 or later
- An Azure subscription
- An existing Azure Cosmos DB for NoSQL account
- An Azure OpenAI resource with an embeddings deployment

## Contributing

This project welcomes contributions and suggestions. See the [Azure SDK for Python contributing guide](https://github.com/Azure/azure-sdk-for-python/blob/main/CONTRIBUTING.md) for details.
