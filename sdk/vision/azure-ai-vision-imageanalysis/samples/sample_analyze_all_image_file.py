# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to analyze all supported visual features from the image file sample.jpg,
    using a synchronous client.

    The synchronous (blocking) `analyze` method makes a single REST call to the Azure AI Vision
    service, where all visual features are analyzed in parallel. When the service responds, the method returns
    an `ImageAnalysisResult` object, which contains separate result properties for each one of the visual features.
    This sample prints all the results to the console.

    The sample also shows how to turn on SDK logs, which may be needed for troubleshooting purposes.

    For more information on a particular visual feature, and optional setting associated with it,
    have a look at the sample in this folder dedicated to that visual feature.

USAGE:
    python sample_analyze_all_image_file.py

    Set these two environment variables before running the sample:
    1) VISION_ENDPOINT - Your endpoint URL, in the form https://your-resource-name.cognitiveservices.azure.com
                         where `your-resource-name` is your unique Azure Computer Vision resource name.
    2) VISION_KEY - Your Computer Vision key (a 32-character Hexadecimal number)
"""


def sample_analyze_all_image_file():
    import os
    from azure.ai.vision.imageanalysis import ImageAnalysisClient
    from azure.ai.vision.imageanalysis.models import VisualFeatures
    from azure.core.credentials import AzureKeyCredential

    # [START logging]
    import sys
    import logging

    # Acquire the logger for this client library. Use 'azure' to affect both
    # 'azure.core` and `azure.ai.vision.imageanalysis' libraries.
    logger = logging.getLogger("azure")

    # Set the desired logging level. logging.INFO or logging.DEBUG are good options.
    logger.setLevel(logging.INFO)

    # Direct logging output to stdout (the default):
    handler = logging.StreamHandler(stream=sys.stdout)
    # Or direct logging output to a file:
    # handler = logging.FileHandler(filename = 'sample.log')
    logger.addHandler(handler)

    # Optional: change the default logging format. Here we add a timestamp.
    formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(name)s:%(message)s")
    handler.setFormatter(formatter)
    # [END logging]

    # Set the values of your computer vision endpoint and computer vision key as environment variables:
    try:
        endpoint = os.environ["VISION_ENDPOINT"]
        key = os.environ["VISION_KEY"]
    except KeyError:
        print("Missing environment variable 'VISION_ENDPOINT' or 'VISION_KEY'")
        print("Set them before running this sample.")
        exit()

    # Load image to analyze into a 'bytes' object
    with open("sample.jpg", "rb") as f:
        image_data = f.read()

    # [START create_client_with_logging]
    # Create an Image Analysis client with none redacted log
    client = ImageAnalysisClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key),
        logging_enable=True
    )
    # [END create_client_with_logging]

    # Analyze all visual features from an image stream. This will be a synchronously (blocking) call.
    result = client.analyze(
        image_data=image_data,
        visual_features=[
            VisualFeatures.TAGS,
            VisualFeatures.OBJECTS,
            VisualFeatures.CAPTION,
            VisualFeatures.DENSE_CAPTIONS,
            VisualFeatures.READ,
            VisualFeatures.SMART_CROPS,
            VisualFeatures.PEOPLE,
        ],  # Mandatory. Select one or more visual features to analyze.
        smart_crops_aspect_ratios=[0.9, 1.33],  # Optional. Relevant only if SMART_CROPS was specified above.
        gender_neutral_caption=True,  # Optional. Relevant only if CAPTION or DENSE_CAPTIONS were specified above.
        language="en",  # Optional. Relevant only if TAGS is specified above. See https://aka.ms/cv-languages for supported languages.
        model_version="latest",  # Optional. Analysis model version to use. Defaults to "latest".
    )

    # Print all analysis results to the console
    print("Image analysis results:")

    if result.caption is not None:
        print(" Caption:")
        print(f"   '{result.caption.text}', Confidence {result.caption.confidence:.4f}")

    if result.dense_captions is not None:
        print(" Dense Captions:")
        for caption in result.dense_captions.list:
            print(f"   '{caption.text}', {caption.bounding_box}, Confidence: {caption.confidence:.4f}")

    if result.read is not None:
        print(" Read:")
        for line in result.read.blocks[0].lines:
            print(f"   Line: '{line.text}', Bounding box {line.bounding_polygon}")
            for word in line.words:
                print(f"     Word: '{word.text}', Bounding polygon {word.bounding_polygon}, Confidence {word.confidence:.4f}")

    if result.tags is not None:
        print(" Tags:")
        for tag in result.tags.list:
            print(f"   '{tag.name}', Confidence {tag.confidence:.4f}")

    if result.objects is not None:
        print(" Objects:")
        for object in result.objects.list:
            print(f"   '{object.tags[0].name}', {object.bounding_box}, Confidence: {object.tags[0].confidence:.4f}")

    if result.people is not None:
        print(" People:")
        for person in result.people.list:
            print(f"   {person.bounding_box}, Confidence {person.confidence:.4f}")

    if result.smart_crops is not None:
        print(" Smart Cropping:")
        for smart_crop in result.smart_crops.list:
            print(f"   Aspect ratio {smart_crop.aspect_ratio}: Smart crop {smart_crop.bounding_box}")

    print(f" Image height: {result.metadata.height}")
    print(f" Image width: {result.metadata.width}")
    print(f" Model version: {result.model_version}")


if __name__ == "__main__":
    sample_analyze_all_image_file()
