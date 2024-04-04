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
    1) MODEL_ENDPOINT - Your endpoint URL, in the form https://<deployment-name>.<azure-region>.inference.ai.azure.com
                        where `deployment-name` is your unique AI Model deployment name, and
                        `azure-region` is the Azure region where your model is deployed.
    2) MODEL_KEY - Your model key (a 32-character string). Keep it secret.
"""


def sample_embeddings():
    import os

    from azure.ai.inference import ModelClient
    from azure.core.credentials import AzureKeyCredential

    # [START logging]
    import sys
    import logging

    # Acquire the logger for this client library. Use 'azure' to affect both
    # 'azure.core` and `azure.ai.vision.imageanalysis' libraries.
    logger = logging.getLogger("azure")

    # Set the desired logging level. logging.INFO or logging.DEBUG are good options.
    logger.setLevel(logging.DEBUG)

    # Direct logging output to stdout (the default):
    handler = logging.StreamHandler(stream=sys.stdout)
    # Or direct logging output to a file:
    # handler = logging.FileHandler(filename = 'sample.log')
    logger.addHandler(handler)

    # Optional: change the default logging format. Here we add a timestamp.
    formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(name)s:%(message)s")
    handler.setFormatter(formatter)
    # [END logging]

    # Read the values of your model endpoint and key from environment variables
    try:
        endpoint = os.environ["MODEL_ENDPOINT"]
        key = os.environ["MODEL_KEY"]
    except KeyError:
        print("Missing environment variable 'MODEL_ENDPOINT' or 'MODEL_KEY'")
        print("Set them before running this sample.")
        exit()

    # Create an Model for synchronous operations
    client = ModelClient(
        endpoint=endpoint,
        credential=AzureKeyCredential("key")
    )

    # [START embeddings]
    # Do a single embeddings operation. This will be a synchronously (blocking) call.
    result = client.get_embeddings(
        input=[
            "first sentence",
            "second sentence","third sentence"
        ]
    )

    # Print results the the console
    print("Embeddings result:")
    for index, item in enumerate(result.data):
        len = item.embedding.__len__()
        print(f"data[{index}].index: {item.index}")
        print(f"data[{index}].embedding[0]: {item.embedding[0]}")
        print(f"data[{index}].embedding[1]: {item.embedding[1]}")
        print("...")
        print(f"data[{index}].embedding[{len-2}]: {item.embedding[len-2]}")
        print(f"data[{index}].embedding[{len-1}]: {item.embedding[len-1]}")
    print(f"id: {result.id}")
    print(f"model: {result.model}")
    print(f"object: {result.object}")
    print(f"usage.prompt_tokens: {result.usage.prompt_tokens}")
    print(f"usage.total_tokens: {result.usage.total_tokens}")
    # [END embeddings]


if __name__ == "__main__":
    sample_embeddings()
