# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to extract content tags in an image file sample.jpg, using a synchronous client.
    Tags are supported for thousands of recognizable objects, living beings, scenery, and actions that appear in images.

    Tags names are supported in multiple languages, the default being English. You can set the `language` argument when
    calling `analyze` to a 2-letter language code. See [Image Analysis supported languages](https://aka.ms/cv-languages).

    The synchronous (blocking) `analyze` method call returns an `ImageAnalysisResult` object.
    Its `tags` property (a `TagsResult` object) contains a list of `DetectedTag` objects. Each has:
    - The tag name, for example: "indoor", "table".
    - A confidence score in the range [0, 1], with higher values indicating greater confidences in the tag.

USAGE:
    python sample_tags_image_file.py

    Set these two environment variables before running the sample:
    1) VISION_ENDPOINT - Your endpoint URL, in the form https://your-resource-name.cognitiveservices.azure.com
                         where `your-resource-name` is your unique Azure Computer Vision resource name.
    2) VISION_KEY - Your Computer Vision key (a 32-character Hexadecimal number)
"""


def sample_tags_image_file():
    import os
    from azure.ai.vision.imageanalysis import ImageAnalysisClient
    from azure.ai.vision.imageanalysis.models import VisualFeatures
    from azure.core.credentials import AzureKeyCredential

    # Set the values of your computer vision endpoint and computer vision key
    # as environment variables:
    try:
        endpoint = os.environ["VISION_ENDPOINT"]
        key = os.environ["VISION_KEY"]
    except KeyError:
        print("Missing environment variable 'VISION_ENDPOINT' or 'VISION_KEY'")
        print("Set them before running this sample.")
        exit()

    # Create an Image Analysis client
    client = ImageAnalysisClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key)
    )

    # Load image to analyze into a 'bytes' object
    with open("sample.jpg", "rb") as f:
        image_data = f.read()

    # Do 'Tags' analysis on an image stream. This will be a synchronously (blocking) call.
    result = client.analyze(
        image_data=image_data,
        visual_features=[VisualFeatures.TAGS],
        language="en",  # Optional. See https://aka.ms/cv-languages for supported languages.
    )

    # Print Tags analysis results to the console
    print("Image analysis results:")
    print(" Tags:")
    if result.tags is not None:
        for tag in result.tags.list:
            print(f"   '{tag.name}', Confidence {tag.confidence:.4f}")
    print(f" Image height: {result.metadata.height}")
    print(f" Image width: {result.metadata.width}")
    print(f" Model version: {result.model_version}")


if __name__ == "__main__":
    sample_tags_image_file()
