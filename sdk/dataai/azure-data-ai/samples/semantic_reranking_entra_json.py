# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Rerank JSON documents using Microsoft Entra authentication."""

import json
import os

from azure.data.ai import InferenceClient
from azure.data.ai.models import SemanticRerankingInferenceContent
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
    request = SemanticRerankingInferenceContent(
        query="How does Azure Cosmos DB scale globally?",
        # Each document is a JSON-encoded string, not a dictionary.
        documents=[json.dumps(document) for document in documents],
        top_k=2,
        return_documents=True,
        return_sentence_score=True,
        batch_size=len(documents),
        sort=True,
        document_type="json",
        target_paths=["title", "description"],
        model="aisearch-reranker",
    )
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
