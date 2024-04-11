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
    1) IMAGE_GENERATION_ENDPOINT - Your endpoint URL, in the form
        https://<your-deployment-name>.<your-azure-region>.inference.ai.azure.com
        where `your-deployment-name` is your unique AI Model deployment name, and
        `your-azure-region` is the Azure region where your model is deployed.
    2) IMAGE_GENERATION_KEY - Your model key (a 32-character string). Keep it secret.
"""

def sample_image_generation():
    import os
    from azure.ai.inference import ModelClient
    from azure.core.credentials import AzureKeyCredential

    # Read the values of your model endpoint and key from environment variables
    try:
        endpoint = os.environ["IMAGE_GENERATION_ENDPOINT"]
        key = os.environ["IMAGE_GENERATION_KEY"]
    except KeyError:
        print("Missing environment variable 'IMAGE_GENERATION_ENDPOINT' or 'IMAGE_GENERATION_KEY'")
        print("Set them before running this sample.")
        exit()

    # Create an Model for synchronous operations
    client = ModelClient(endpoint=endpoint, credential=AzureKeyCredential(key))

    # [START image_generation]
    # Generate a single image from a text prompt. This will be a synchronously (blocking) call.
    result = client.get_image_generations(
        prompt="A painting of a beautiful sunset over a mountain lake.", size="1024x768"
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
