# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to find representatives sub-regions of the image file sample.jpg,
    for thumbnail generation, with priority given to include faces. It uses an asynchronous client.

    Thumbnails often need to have a certain aspect ratio, where aspect ratio is defined as the 
    width in pixels divided by the height in pixels. For example, 1.0 for a square image, or 1.77
    for a 16:9 widescreen image.

    You can optionally request one or more aspect ratios by setting the `smart_crops_aspect_ratios` 
    argument in the call to `analyze`. Supported values are from 0.75 to 1.8 (inclusive).
    If you do not set this value, the service will return one result with an aspect ratio it sees
    fit between 0.5 and 2.0 (inclusive).

    The synchronous (blocking ) `analyze` method call returns an `ImageAnalysisResult` object.
    Its `smart_crops` property (a `SmartCropsResult` object) contains a list of `CropRegion` objects.
    Each one contains:
    - The aspect ratio of the region
    - A `BoundingBox` coordinates in pixels, defining the region in the image.

USAGE:
    python sample_smart_crops_image_file.py

    Set these two environment variables before running the sample:
    1) VISION_ENDPOINT - Your endpoint URL, in the form https://your-resource-name.cognitiveservices.azure.com
                         where `your-resource-name` is your unique Azure Computer Vision resource name.
    2) VISION_KEY - Your Computer Vision key (a 32-character Hexadecimal number)
"""


def sample_smart_crops_image_file():
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

    # Do Smart Cropping analysis on an image stream. This will be a synchronously (blocking) call.
    result = client.analyze(
        image_data=image_data,
        visual_features=[VisualFeatures.SMART_CROPS],
        smart_crops_aspect_ratios=[0.9, 1.33],  # Optional. Specify one more desired aspect ratios
    )

    # Print smart crop analysis results to the console
    print("Image analysis results:")
    print(" Smart Cropping:")
    if result.smart_crops is not None:
        for smart_crop in result.smart_crops.list:
            print(f"   Aspect ratio {smart_crop.aspect_ratio}: Smart crop {smart_crop.bounding_box}")
    print(f" Image height: {result.metadata.height}")
    print(f" Image width: {result.metadata.width}")
    print(f" Model version: {result.model_version}")


if __name__ == "__main__":
    sample_smart_crops_image_file()
