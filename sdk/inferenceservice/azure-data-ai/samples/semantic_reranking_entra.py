# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Rerank documents using a Microsoft Entra credential."""

import argparse
import os

from azure.data.ai import InferenceServiceClient
from azure.identity import DefaultAzureCredential


def main(model: str | None = None) -> None:
    endpoint = os.environ["AZURE_DATA_AI_ENDPOINT"]
    with DefaultAzureCredential() as credential:
        with InferenceServiceClient(endpoint, credential) as client:
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
            result = client.semantic_rerank(request)

    for score in result.get("scores", []):
        print(score["index"], score["score"], score.get("document"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rerank documents with Microsoft Entra authentication.")
    parser.add_argument("--model", help="Model supported by the endpoint; omitted by default.")
    main(model=parser.parse_args().model)
