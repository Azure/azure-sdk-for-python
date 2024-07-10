# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to extract printed or hand-written text from a 
    publicly accessible image URL, using a synchronous client.

    The synchronous (blocking) `analyze` method call returns an `ImageAnalysisResult` object.
    Its `read` property (a `ReadResult` object) includes a list of `TextBlock` objects. Currently, the
    list will always contain one element only, as the service does not yet support grouping text lines
    into separate blocks. The `TextBlock` object contains a list of `DocumentLine` object. Each one includes: 
    - The text content of the line.
    - A `BoundingPolygon` coordinates in pixels, for a polygon surrounding the line of text in the image.
    - A list of `DocumentWord` objects.
    Each `DocumentWord` object contains:
    - The text content of the word.
    - A `BoundingPolygon` coordinates in pixels, for a polygon surrounding the word in the image.
    - A confidence score in the range [0, 1], with higher values indicating greater confidences in
      the recognition of the word. 

USAGE:
    python sample_ocr_image_url.py

    Set these two environment variables before running the sample:
    1) VISION_ENDPOINT - Your endpoint URL, in the form https://your-resource-name.cognitiveservices.azure.com
                         where `your-resource-name` is your unique Azure Computer Vision resource name.
    2) VISION_KEY - Your Computer Vision key (a 32-character Hexadecimal number)
"""


def sample_ocr_image_url():
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

    # [START read]
    # Extract text (OCR) from an image stream. This will be a synchronously (blocking) call.
    result = client.analyze_from_url(
        image_url="https://aka.ms/azsdk/image-analysis/sample.jpg",
        visual_features=[VisualFeatures.READ]
    )

    # Print text (OCR) analysis results to the console
    print("Image analysis results:")
    print(" Read:")
    if result.read is not None:
        for line in result.read.blocks[0].lines:
            print(f"   Line: '{line.text}', Bounding box {line.bounding_polygon}")
            for word in line.words:
                print(f"     Word: '{word.text}', Bounding polygon {word.bounding_polygon}, Confidence {word.confidence:.4f}")
    # [END read]
    print(f" Image height: {result.metadata.height}")
    print(f" Image width: {result.metadata.width}")
    print(f" Model version: {result.model_version}")


if __name__ == "__main__":
    sample_ocr_image_url()
