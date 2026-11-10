# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Embed a document and a query concurrently with the asynchronous client.

A request has at most one text or query item, so the sample sends two requests. Set AZURE_DATA_AI_ENDPOINT.
Requires `aiohttp`.
"""

import asyncio
import os

from azure.data.ai.aio import InferenceClient
from azure.data.ai.models import EmbeddingContentItem, MultimodalDenseEmbedding
from azure.identity.aio import DefaultAzureCredential


async def main() -> None:
    endpoint = os.environ["AZURE_DATA_AI_ENDPOINT"]
    items = [
        EmbeddingContentItem(id="doc-1", type="text", content="Invoice terms: net 30."),
        EmbeddingContentItem(id="query-1", type="query", content="When is the invoice due?"),
    ]

    async with DefaultAzureCredential() as credential:
        async with InferenceClient(endpoint=endpoint, credential=credential) as client:
            results = await asyncio.gather(*(client.multi_modal_embed(contents=[item]) for item in items))
            for result in results:
                item = result.data[0]
                if isinstance(item, MultimodalDenseEmbedding) and isinstance(item.embedding, list):
                    print(f"{item.id} ({item.type}): {len(item.embedding)} dimensions")


if __name__ == "__main__":
    asyncio.run(main())
