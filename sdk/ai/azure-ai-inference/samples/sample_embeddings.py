# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to get embeddings for a list of sentences using a synchronous client.

USAGE:
    python sample_embeddings.py

    Set these two environment variables before running the sample:
    1) EMBEDDINGS_ENDPOINT - Your endpoint URL, in the form 
        https://<your-deployment-name>.<your-azure-region>.inference.ai.azure.com
        where `your-deployment-name` is your unique AI Model deployment name, and
        `your-azure-region` is the Azure region where your model is deployed.
    2) EMBEDDINGS_KEY - Your model key (a 32-character string). Keep it secret.
"""


def sample_embeddings():
    import os
    from azure.ai.inference import ModelClient
    from azure.core.credentials import AzureKeyCredential

    # Read the values of your model endpoint and key from environment variables
    try:
        endpoint = os.environ["EMBEDDINGS_ENDPOINT"]
        key = os.environ["EMBEDDINGS_KEY"]
    except KeyError:
        print("Missing environment variable 'EMBEDDINGS_ENDPOINT' or 'EMBEDDINGS_KEY'")
        print("Set them before running this sample.")
        exit()

    # Create an Model for synchronous operations
    client = ModelClient(endpoint=endpoint, credential=AzureKeyCredential(key), logging_enable=True)

    # [START embeddings]
    # Do a single embeddings operation. This will be a synchronously (blocking) call.
    result = client.get_embeddings(input=["first phrase", "second phrase", "third phrase"])

    # Print results the the console
    print("Embeddings result:")
    for item in result.data:
        length = len(item.embedding)
        print(
            f"data[{item.index}]: length={length}, [{item.embedding[0]}, {item.embedding[1]}, ..., {item.embedding[length-2]}, {item.embedding[length-1]}]"
        )
    print(f"id: {result.id}")
    print(f"model: {result.model}")
    print(f"object: {result.object}")
    print(f"usage.input_tokens: {result.usage.input_tokens}")
    print(f"usage.prompt_tokens: {result.usage.prompt_tokens}")
    print(f"usage.total_tokens: {result.usage.total_tokens}")
    # [END embeddings]


if __name__ == "__main__":
    sample_embeddings()
