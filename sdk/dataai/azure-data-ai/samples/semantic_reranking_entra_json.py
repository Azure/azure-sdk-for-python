# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Rerank JSON documents using Microsoft Entra authentication."""

import json
import os

from azure.data.ai import InferenceClient
from azure.data.ai.types import SemanticRerankingInferenceRequest
from azure.identity import DefaultAzureCredential


def main() -> None:
    endpoint = os.environ["AZURE_DATA_AI_ENDPOINT"]
    documents = [
        {
            "id": "cosmos-db",
            "title": "Azure Cosmos DB",
            "description": "Azure Cosmos DB is a globally distributed NoSQL database.",
            "metadata": {"category": "database"},
        },
        {
            "id": "paris",
            "title": "The Eiffel Tower",
            "description": "The Eiffel Tower is located in Paris.",
            "metadata": {"category": "travel"},
        },
        {
            "id": "global-scaling",
            "title": "Global distribution",
            "description": "Cosmos DB supports elastic scaling and global distribution.",
            "metadata": {"category": "database"},
        },
    ]
    request: SemanticRerankingInferenceRequest = {
        "query": "How does Azure Cosmos DB scale globally?",
        # Each document is a JSON-encoded string, not a dictionary.
        "documents": [json.dumps(document) for document in documents],
        "topK": 2,
        "returnDocuments": True,
        "returnSentenceScore": True,
        "batchSize": len(documents),
        "sort": True,
        "documentType": "json",
        "targetPaths": "title,description",
        "model": "aisearch-reranker",
    }
    with DefaultAzureCredential() as credential:
        with InferenceClient(endpoint=endpoint, credential=credential) as client:
            result = client.semantic_rerank(request)

    for score in result.get("scores", []):
        print(score["index"], score["score"])
        if "document" in score:
            print("Document:", json.loads(score["document"]))
        for sentence in score.get("sentenceScores", []):
            print("  Sentence", sentence["index"], "score:", sentence["score"])


if __name__ == "__main__":
    main()
