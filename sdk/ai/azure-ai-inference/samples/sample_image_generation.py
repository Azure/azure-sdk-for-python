# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to generate an image from a prompt
    using a synchronous client.

USAGE:
    python sample_image_generation.py

    Set these two environment variables before running the sample:
    1) IMAGE_GENERATION_ENDPOINT - Your endpoint URL, in the form
        https://<your-deployment-name>.<your-azure-region>.inference.ai.azure.com
        where `your-deployment-name` is your unique AI Model deployment name, and
        `your-azure-region` is the Azure region where your model is deployed.
    2) IMAGE_GENERATION_KEY - Your model key (a 32-character string). Keep it secret.
"""

def sample_image_generation():
    import os
    import base64

    try:
        endpoint = os.environ["IMAGE_GENERATION_ENDPOINT"]
        key = os.environ["IMAGE_GENERATION_KEY"]
    except KeyError:
        print("Missing environment variable 'IMAGE_GENERATION_ENDPOINT' or 'IMAGE_GENERATION_KEY'")
        print("Set them before running this sample.")
        exit()

    # [START image_generation]
    from azure.ai.inference import ImageGenerationClient
    from azure.core.credentials import AzureKeyCredential

    client = ImageGenerationClient(endpoint=endpoint, credential=AzureKeyCredential(key))

    result = client.create(prompt="A painting of a beautiful sunset over a mountain lake.", size="1024x768")

    if result.data[0].b64_json is not None:
        with open(f"image.png", "wb") as image:
            image.write(base64.b64decode(result.data[0].b64_json))
    # [END image_generation]


if __name__ == "__main__":
    sample_image_generation()
