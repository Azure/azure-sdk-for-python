# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Rerank documents asynchronously using dictionaries and an API key."""

import argparse
import asyncio
import os

from azure.core.credentials import AzureKeyCredential
from azure.data.ai.aio import InferenceServiceClient


async def main(model: str | None = None) -> None:
    endpoint = os.environ["AZURE_DATA_AI_ENDPOINT"]
    credential = AzureKeyCredential(os.environ["AZURE_DATA_AI_KEY"])
    async with InferenceServiceClient(endpoint, credential) as client:
        request = {
            "query": "What is the capital of France?",
            "documents": ["Paris is the capital of France.", "Berlin is the capital of Germany."],
            "returnDocuments": True,
            "returnSentenceScore": True,
            "topK": 1,
            "batchSize": 2,
            "sort": True,
            "documentType": "text",
        }
        if model is not None:
            request["model"] = model
        result = await client.semantic_rerank(request)

    for score in result.get("scores", []):
        print(score["index"], score["score"], score.get("document"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rerank documents asynchronously with an Azure Inference Service key.")
    parser.add_argument("--model", help="Model supported by the endpoint; omitted by default.")
    asyncio.run(main(model=parser.parse_args().model))
