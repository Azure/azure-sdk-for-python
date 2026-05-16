# The MIT License (MIT)
# Copyright (c) 2023 Microsoft Corporation

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Sample: use AzureOpenAIEmbeddingProvider with a synchronous CosmosClient.

Demonstrates two credential modes:

* Variant A — Azure OpenAI API key.
* Variant B — Entra (RBAC). The SAME ``DefaultAzureCredential`` is shared
  between ``CosmosClient`` (Cosmos RBAC) and the embedding provider
  (Azure OpenAI), so the user only needs one identity.

Required environment variables:

* ``COSMOS_ENDPOINT`` – e.g. ``https://my-cosmos.documents.azure.com:443/``
* ``COSMOS_KEY``       – only for Variant A
* ``AOAI_API_KEY``     – only for Variant A

Both samples assume a database ``samples-db`` with a container ``items``
whose ``vectorEmbeddingPolicy.embeddingSource`` already points at the
Azure OpenAI endpoint and deployment you intend to use.
"""

import os

from azure.cosmos import CosmosClient
from azure.cosmos.ai import AzureOpenAIEmbeddingProvider
from azure.identity import DefaultAzureCredential


def variant_a_api_key() -> None:
    cosmos_endpoint = os.environ["COSMOS_ENDPOINT"]
    cosmos_key = os.environ["COSMOS_KEY"]
    aoai_api_key = os.environ["AOAI_API_KEY"]

    with AzureOpenAIEmbeddingProvider(credential=aoai_api_key) as provider:
        client = CosmosClient(
            url=cosmos_endpoint,
            credential=cosmos_key,
            embedding_provider=provider,
        )
        _run_query(client)


def variant_b_shared_entra() -> None:
    cosmos_endpoint = os.environ["COSMOS_ENDPOINT"]

    cred = DefaultAzureCredential()
    with AzureOpenAIEmbeddingProvider(credential=cred) as provider:
        client = CosmosClient(
            url=cosmos_endpoint,
            credential=cred,
            embedding_provider=provider,
        )
        _run_query(client)


def _run_query(client: CosmosClient) -> None:
    db = client.get_database_client("samples-db")
    container = db.get_container_client("items")

    query = (
        "SELECT TOP 5 c.id, "
        "VectorDistance(c.embedding, GenerateEmbeddings('healthcare research papers')) AS score "
        "FROM c ORDER BY score"
    )
    for item in container.query_items(query=query, enable_cross_partition_query=True):
        print(item)


if __name__ == "__main__":
    variant_a_api_key()
