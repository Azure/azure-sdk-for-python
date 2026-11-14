# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Embed a document and a query concurrently with the asynchronous client.

A request has at most one text or query item, so the sample sends two requests. Set AZURE_DATA_AI_ENDPOINT.
Requires `aiohttp`.
"""

import asyncio
import os

from azure.data.ai.aio import InferenceClient
from azure.data.ai.models import MultimodalDenseEmbedding
from azure.identity.aio import DefaultAzureCredential


async def main() -> None:
    endpoint = os.environ["AZURE_DATA_AI_ENDPOINT"]
    items = [
        {"id": "doc-1", "kind": "text", "content": "Invoice terms: net 30."},
        {"id": "query-1", "kind": "query", "content": "When is the invoice due?"},
    ]

    async with DefaultAzureCredential() as credential:
        async with InferenceClient(endpoint=endpoint, credential=credential) as client:
            results = await asyncio.gather(
                *(client.get_embeddings(inputs=[item], model="microsoft-embedding-1-large") for item in items)
            )
            for result in results:
                item = result.data[0]
                if isinstance(item, MultimodalDenseEmbedding) and isinstance(item.embedding, list):
                    print(f"{item.id} ({item.content_kind}): {len(item.embedding)} dimensions")


if __name__ == "__main__":
    asyncio.run(main())
