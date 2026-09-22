# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Rerank documents asynchronously using dictionaries and an API key."""

import asyncio
import os

from azure.core.credentials import AzureKeyCredential
from azure.data.ai.aio import AzureDataAIClient


async def main() -> None:
    endpoint = os.environ["AZURE_DATA_AI_ENDPOINT"]
    credential = AzureKeyCredential(os.environ["AZURE_DATA_AI_KEY"])
    async with AzureDataAIClient(endpoint, credential) as client:
        request = {
            "query": "What is the capital of France?",
            "documents": ["Paris is the capital of France.", "Berlin is the capital of Germany."],
            "topK": 2,
            "returnDocuments": True,
            "returnSentenceScore": True,
            "batchSize": 8,
            "sort": True,
            "documentType": "text",
            "model": "aisearch-reranker",
        }
        result = await client.semantic_rerank(request)

    for score in result.get("Scores", []):
        print(score["index"], score["score"], score.get("document"))
        for sentence in score.get("sentenceScores", []):
            print("  Sentence", sentence["index"], "score:", sentence["score"])


if __name__ == "__main__":
    asyncio.run(main())
