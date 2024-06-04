# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to generate a human-readable sentence that describes the content
    of the image file sample.jpg, using an asynchronous client.

    By default the caption may contain gender terms such as "man", "woman", or "boy", "girl".
    You have the option to request gender-neutral terms such as "person" or "child" by setting
    `gender_neutral_caption = True` when calling `analyze`, as shown in this example.

    The asynchronous (non-blocking) `analyze` method call, when completes, returns 
    an `ImageAnalysisResult` object. Its `caption` property (a `CaptionResult` object) contains:
    - The text of the caption. Captions are only supported in English at the moment. 
    - A confidence score in the range [0, 1], with higher values indicating greater confidences in
      the caption.

USAGE:
    python sample_caption_image_file_async.py

    Set these two environment variables before running the sample:
    1) VISION_ENDPOINT - Your endpoint URL, in the form https://your-resource-name.cognitiveservices.azure.com
                         where `your-resource-name` is your unique Azure Computer Vision resource name.
    2) VISION_KEY - Your Computer Vision key (a 32-character Hexadecimal number)
"""
import asyncio


async def sample_caption_image_file_async():
    import os
    from azure.ai.vision.imageanalysis.aio import ImageAnalysisClient
    from azure.ai.vision.imageanalysis.models import VisualFeatures
    from azure.core.credentials import AzureKeyCredential

    # Set the values of your computer vision endpoint and computer vision key as environment variables:
    try:
        endpoint = os.environ["VISION_ENDPOINT"]
        key = os.environ["VISION_KEY"]
    except KeyError:
        print("Missing environment variable 'VISION_ENDPOINT' or 'VISION_KEY'.")
        print("Set them before running this sample.")
        exit()

    # Load image to analyze into a 'bytes' object
    with open("sample.jpg", "rb") as f:
        image_data = f.read()

    # Create an asynchronous Image Analysis client
    client = ImageAnalysisClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key)
    )

    # Get a caption for the image, asynchronously.
    result = await client.analyze(
        image_data=image_data,
        visual_features=[VisualFeatures.CAPTION]
    )

    await client.close()

    # Print caption results to the console
    print("Image analysis results:")
    print(" Caption:")
    if result.caption is not None:
        print(f"   '{result.caption.text}', Confidence {result.caption.confidence:.4f}")
    print(f" Image height: {result.metadata.height}")
    print(f" Image width: {result.metadata.width}")
    print(f" Model version: {result.model_version}")


async def main():
    await sample_caption_image_file_async()


if __name__ == "__main__":
    asyncio.run(main())
