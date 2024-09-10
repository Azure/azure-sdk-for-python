# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to get text embeddings for a list of sentences
    using a synchronous client. Here we request embeddings as base64
    encoded strings, instead of the service default of lists of floats.

    This sample assumes the AI model is hosted on a Serverless API or
    Managed Compute endpoint. For GitHub Models or Azure OpenAI endpoints,
    the client constructor needs to be modified. See package documentation:
    https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/README.md#key-concepts

USAGE:
    python sample_embeddings_with_base64_encoding.py

    Set these two environment variables before running the sample:
    1) AZURE_AI_EMBEDDINGS_ENDPOINT - Your endpoint URL, in the form 
        https://<your-deployment-name>.<your-azure-region>.models.ai.azure.com
        where `your-deployment-name` is your unique AI Model deployment name, and
        `your-azure-region` is the Azure region where your model is deployed.
    2) AZURE_AI_EMBEDDINGS_KEY - Your model key (a 32-character string). Keep it secret.
"""


def sample_embeddings_with_base64_encoding():
    import os

    try:
        endpoint = os.environ["AZURE_AI_EMBEDDINGS_ENDPOINT"]
        key = os.environ["AZURE_AI_EMBEDDINGS_KEY"]
    except KeyError:
        print("Missing environment variable 'AZURE_AI_EMBEDDINGS_ENDPOINT' or 'AZURE_AI_EMBEDDINGS_KEY'")
        print("Set them before running this sample.")
        exit()

    from azure.ai.inference import EmbeddingsClient
    from azure.ai.inference.models import EmbeddingEncodingFormat
    from azure.core.credentials import AzureKeyCredential

    client = EmbeddingsClient(endpoint=endpoint, credential=AzureKeyCredential(key))

    # Request embeddings as base64 encoded strings
    response = client.embed(
        input=["first phrase", "second phrase", "third phrase"],
        encoding_format=EmbeddingEncodingFormat.BASE64)

    for item in response.data:
        # Display the start and end of the resulting base64 string
        print(f"data[{item.index}] encoded (string length={len(item.embedding)}): "
              f"\"{item.embedding[:32]}...{item.embedding[-32:]}\"")

        # For display purposes, decode the string into a list of floating point numbers.
        # Display the first and last two elements of the list.
        decoded_embedding = decode_base64(item.embedding)
        length = len(decoded_embedding)
        print(
            f"data[{item.index}] decoded (vector length={length}): "
            f"[{decoded_embedding[0]}, {decoded_embedding[1]}, "
            f"..., {decoded_embedding[length-2]}, {decoded_embedding[length-1]}]"
        )


def decode_base64(base64_str):
    """
    Helper function that decodes a base64 string and returns a list of floats.
    Args:
        base64_str (str): The base64 string to decode.
    Returns:
        List[float]: A list of floats decoded from the base64 string.
    """

    import base64
    import numpy

    decoded_bytes = base64.b64decode(base64_str)
    return numpy.frombuffer(decoded_bytes, dtype=numpy.float32)


if __name__ == "__main__":
    sample_embeddings_with_base64_encoding()
