# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to generate up to 10 human-readable sentences (captions) that describe
    the content of different sub-regions of the image file sample.jpg. The first caption returned
    always represents the whole image. The sample uses the synchronous client.

    By default the captions may contain gender terms such as "man", "woman", or "boy", "girl".
    You have the option to request gender-neutral terms such as "person" or "child" by setting
    `gender_neutral_caption = True` when calling `analyze`, as shown in this example.

    The synchronous (blocking) `analyze` method call returns an `ImageAnalysisResult` object.
    Its `dense_captions` property (a `DenseCaptionsResult` object) includes a list of up to 10 `DenseCaption`
    objects. Each one of them contains:
    - The text of the caption. Captions are only supported in English at the moment. 
    - A confidence score in the range [0, 1], with higher values indicating greater confidences in
      the caption.
    - A `BoundingBox` coordinates in pixels, for a rectangular marking the area in the image associated
      with this caption.

USAGE:
    python sample_dense_captions_image_file.py

    Set these two environment variables before running the sample:
    1) VISION_ENDPOINT - Your endpoint URL, in the form https://your-resource-name.cognitiveservices.azure.com
                         where `your-resource-name` is your unique Azure Computer Vision resource name.
    2) VISION_KEY - Your Computer Vision key (a 32-character Hexadecimal number)
"""


def sample_dense_captions_image_file():
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

    # Create an Image Analysis client.
    client = ImageAnalysisClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key)
    )

    # Load image to analyze into a 'bytes' object.
    with open("sample.jpg", "rb") as f:
        image_data = f.read()

    # Extract multiple captions, each for a different area of the image.
    # This will be a synchronously (blocking) call.
    result = client.analyze(
        image_data=image_data,
        visual_features=[VisualFeatures.DENSE_CAPTIONS],
        gender_neutral_caption=True,  # Optional (default is False)
    )

    # Print dense caption results to the console. The first caption always
    # corresponds to the entire image. The rest correspond to sub regions.
    print("Image analysis results:")
    print(" Dense Captions:")
    if result.dense_captions is not None:
        for caption in result.dense_captions.list:
            print(f"   '{caption.text}', {caption.bounding_box}, Confidence: {caption.confidence:.4f}")
    print(f" Image height: {result.metadata.height}")
    print(f" Image width: {result.metadata.width}")
    print(f" Model version: {result.model_version}")


if __name__ == "__main__":
    sample_dense_captions_image_file()
