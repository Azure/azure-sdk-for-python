# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Rerank documents using a Microsoft Entra credential."""

import os

from azure.data.ai import AzureDataAIClient
from azure.data.ai.types import SemanticRerankingInferenceRequest
from azure.identity import DefaultAzureCredential


def main() -> None:
    endpoint = os.environ["AZURE_DATA_AI_ENDPOINT"]

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

    with DefaultAzureCredential() as credential:
        with AzureDataAIClient(endpoint=endpoint, credential=credential) as client:
            result = client.semantic_rerank(request)

    for score in result.get("scores", []):
        print(score["index"], score["score"], score.get("document"))
        for sentence in score.get("sentenceScores", []):
            print("  Sentence", sentence["index"], "score:", sentence["score"])


if __name__ == "__main__":
    main()
