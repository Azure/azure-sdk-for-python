# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to generate an image from a prompt using an asynchronous client.

USAGE:
    python sample_image_generation_async.py

    Set these two environment variables before running the sample:
    1) IMAGE_GENERATION_ENDPOINT - Your endpoint URL, in the form
        https://<your-deployment-name>.<your-azure-region>.inference.ai.azure.com
        where `your-deployment-name` is your unique AI Model deployment name, and
        `your-azure-region` is the Azure region where your model is deployed.
    2) IMAGE_GENERATION_KEY - Your model key (a 32-character string). Keep it secret.
"""
import asyncio

async def sample_image_generation_async():
    import os
    import base64
    from azure.ai.inference.aio import ImageGenerationClient
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
    client = ImageGenerationClient(endpoint=endpoint, credential=AzureKeyCredential("key"))

    # Generate an image from text prompt. This will be an asynchronously (non-blocking) call.
    future = asyncio.ensure_future(
        client.create(prompt="A painting of a beautiful sunset over a mountain lake.", size="1024x768")
    )

    # Loop until the operation is done
    while not future.done():
        await asyncio.sleep(0.1)
        print("Waiting...")

    # Get the result
    result = future.result()
    await client.close()

    # Save generated image to file and print other results the the console
    print("Image generation result:")
    for index, item in enumerate(result.data):
        if item.b64_json is not None:
            with open(f"image_{index}.png", "wb") as image:
                image.write(base64.b64decode(item.b64_json))
    print(f"id: {result.id}")
    print(f"model: {result.model}")
    print(f"created: {result.created}")


async def main():
    await sample_image_generation_async()


if __name__ == "__main__":
    asyncio.run(main())
