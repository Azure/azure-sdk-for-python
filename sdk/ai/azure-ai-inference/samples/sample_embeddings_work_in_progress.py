# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to get text embeddings for a list of sentences
    using a synchronous client. It was modified for temporary testing of 
    base64 encoding format of embedding results.

USAGE:
    python sample_embeddings_work_in_progress.py

    Set these two environment variables before running the sample:
    1) AZURE_AI_EMBEDDINGS_ENDPOINT - Your endpoint URL, in the form 
        https://<your-deployment-name>.<your-azure-region>.inference.ai.azure.com
        where `your-deployment-name` is your unique AI Model deployment name, and
        `your-azure-region` is the Azure region where your model is deployed.
    2) AZURE_AI_EMBEDDINGS_KEY - Your model key (a 32-character string). Keep it secret.
"""

import sys
import logging
from azure.ai.inference import EmbeddingsClient
from azure.ai.inference.models import EmbeddingEncodingFormat, EmbeddingsResult
from azure.core.credentials import AzureKeyCredential
from typing import List, Union

logger = logging.getLogger("azure")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))

def sample_embeddings_work_in_progress():
    import os

    try:
        endpoint = os.environ["AZURE_AI_EMBEDDINGS_ENDPOINT"]
        key = os.environ["AZURE_AI_EMBEDDINGS_KEY"]
    except KeyError:
        print("Missing environment variable 'AZURE_AI_EMBEDDINGS_ENDPOINT' or 'AZURE_AI_EMBEDDINGS_KEY'")
        print("Set them before running this sample.")
        exit()

    client = EmbeddingsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key),
        logging_enable=True)

    response1 = client.embed(
        input=["some phrase"],
        encoding_format=EmbeddingEncodingFormat.FLOAT)

    # This works fine... the result is a vector of floats and I can print it.
    print_response(response1)

    response2 = client.embed(
        input=["some phrase"],
        encoding_format=EmbeddingEncodingFormat.BASE64)

    # This does not work... instead of printing the string (base64 encoded string of the embedding vector),
    # it prints `<generator object _deserialize_sequence.<locals>.<genexpr> at 0x0000021A8BA4B3E0>`
    print_response(response2)


def print_response(response: EmbeddingsResult):
    for item in response.data:
        if isinstance(item.embedding, str):
            print(item.embedding) # Why does this print `<generator object _deserialize_sequence.<locals>.<genexpr> at 0x0000021A8BA4B3E0>` and not the actual string?
        elif isinstance(item.embedding, List):
            length = len(item.embedding)
            print(
                f"data[{item.index}]: length={length}, [{item.embedding[0]}, {item.embedding[1]}, "
                f"..., {item.embedding[length-2]}, {item.embedding[length-1]}]"
            )
        else:
            raise Exception("Unknown type")


if __name__ == "__main__":
    sample_embeddings_work_in_progress()
