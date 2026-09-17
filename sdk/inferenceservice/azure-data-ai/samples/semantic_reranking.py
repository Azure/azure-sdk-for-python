# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Rerank documents using dictionaries and an API subscription key."""

import argparse
import os
from typing import Any

from azure.core.credentials import AzureKeyCredential
from azure.data.ai import InferenceServiceClient
from azure.identity import AzureCliCredential


def get_sample_inputs() -> tuple[str, AzureKeyCredential, dict[str, str | list[str] | int | bool]]:
    """Return the shared endpoint, key, and request without making a service call."""
    endpoint = os.environ["AZURE_DATA_AI_ENDPOINT"]
    credential = AzureKeyCredential(os.environ["AZURE_DATA_AI_KEY"])
    request = {
        "query": "What is the capital of France?",
        "documents": ["Paris is the capital of France.", "Berlin is the capital of Germany."],
        "topK": 2,
        "returnDocuments": True,
        "returnSentenceScore": False,
        "batchSize": 8,
        "sort": True,
        "documentType": "text",
        "model": "qwen3.8",
    }

    return endpoint, credential, request


def main() -> None:
    """Run the configured reranking example."""
    endpoint, credential, request = get_sample_inputs()
    with InferenceServiceClient(endpoint, credential) as client:
        result = client.semantic_rerank(request)

    for score in result.get("Scores", []):
        print(score["index"], score["score"], score.get("document"))
        for sentence in score.get("sentenceScores", []):
            print("  Sentence", sentence["index"], "score:", sentence["score"])
    print(result)


if __name__ == "__main__":
    main()
