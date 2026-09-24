# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Rerank documents using dictionaries and an API subscription key."""

import os

from azure.core.credentials import AzureKeyCredential
from azure.data.ai import AzureDataAIClient
from azure.data.ai.types import SemanticRerankingInferenceRequest


def get_sample_inputs() -> tuple[str, AzureKeyCredential, SemanticRerankingInferenceRequest]:
    """Return the configured endpoint, key, and request without making a service call."""
    endpoint = os.environ["AZURE_DATA_AI_ENDPOINT"]
    credential = AzureKeyCredential(os.environ["AZURE_DATA_AI_KEY"])
    request: SemanticRerankingInferenceRequest = {
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

    return endpoint, credential, request


def main() -> None:
    """Run the configured reranking example."""
    endpoint, credential, request = get_sample_inputs()
    with AzureDataAIClient(endpoint, credential) as client:
        result = client.semantic_rerank(request)

    for score in result.get("scores", []):
        print(score["index"], score["score"], score.get("document"))
        for sentence in score.get("sentenceScores", []):
            print("  Sentence", sentence["index"], "score:", sentence["score"])


if __name__ == "__main__":
    main()
