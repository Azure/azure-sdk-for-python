# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to generate an image from a prompt.

USAGE:
    python sample_image_generation.py

    Set these two environment variables before running the sample:
    1) MODEL_ENDPOINT - Your endpoint URL, in the form https://<deployment-name>.<azure-region>.inference.ai.azure.com
                        where `deployment-name` is your unique AI Model deployment name, and
                        `azure-region` is the Azure region where your model is deployed.
    2) MODEL_KEY - Your model key (a 32-character string). Keep it secret.
"""


def sample_image_generation():
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

    # [START image_generation]
    # Generate a single image from a text prompt. This will be a synchronously (blocking) call.
    result = client.get_image_generations(
        prompt="A painting of a beautiful sunset over a mountain lake.",
        size="1024x768"
    )

    # Save generated image to file and print other results the the console
    print("Image generation result:")
    for index, item in enumerate(result.data):
        with open(f"image_{index}.png", "wb") as image:
            image.write(item.b64_json.decode("base64"))
    print(f"id: {result.id}")
    print(f"model: {result.model}")
    print(f"created: {result.created}")
    # [END image_generation]


if __name__ == "__main__":
    sample_image_generation()
