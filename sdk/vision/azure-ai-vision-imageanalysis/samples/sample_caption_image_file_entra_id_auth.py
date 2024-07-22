# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to generate a human-readable sentence that describes the content
    of the image file sample.jpg, using a synchronous client. It uses Entra ID authentication.

    By default the caption may contain gender terms such as "man", "woman", or "boy", "girl".
    You have the option to request gender-neutral terms such as "person" or "child" by setting
    `gender_neutral_caption = True` when calling `analyze`, as shown in this example.

    The synchronous (blocking) `analyze` method call returns an `ImageAnalysisResult` object.
    Its `caption` property (a `CaptionResult` object) contains:
    - The text of the caption. Captions are only supported in English at the moment. 
    - A confidence score in the range [0, 1], with higher values indicating greater confidences in
      the caption.

USAGE:
    python sample_caption_image_file_entra_id_auth.py

    Set this environment variables before running the sample:
    VISION_ENDPOINT - Your endpoint URL, in the form https://your-resource-name.cognitiveservices.azure.com
                      where `your-resource-name` is your unique Azure Computer Vision resource name.
"""


def sample_caption_image_file_entra_id_auth():
    # [START create_client]
    import os
    from azure.ai.vision.imageanalysis import ImageAnalysisClient
    from azure.ai.vision.imageanalysis.models import VisualFeatures
    from azure.identity import DefaultAzureCredential

    # Set the value of your computer vision endpoint as environment variable:
    try:
        endpoint = os.environ["VISION_ENDPOINT"]
    except KeyError:
        print("Missing environment variable 'VISION_ENDPOINT'.")
        print("Set it before running this sample.")
        exit()

    # Create an Image Analysis client for synchronous operations,
    # using Entra ID authentication
    client = ImageAnalysisClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential(exclude_interactive_browser_credential=False),
    )
    # [END create_client]

    # Load image to analyze into a 'bytes' object
    with open("sample.jpg", "rb") as f:
        image_data = f.read()

    # Get a caption for the image. This will be a synchronously (blocking) call.
    result = client.analyze(
        image_data=image_data,
        visual_features=[VisualFeatures.CAPTION],
        gender_neutral_caption=True,  # Optional (default is False)
    )

    # Print caption results to the console
    print("Image analysis results:")
    print(" Caption:")
    if result.caption is not None:
        print(f"   '{result.caption.text}', Confidence {result.caption.confidence:.4f}")
    print(f" Image height: {result.metadata.height}")
    print(f" Image width: {result.metadata.width}")
    print(f" Model version: {result.model_version}")


if __name__ == "__main__":
    sample_caption_image_file_entra_id_auth()
