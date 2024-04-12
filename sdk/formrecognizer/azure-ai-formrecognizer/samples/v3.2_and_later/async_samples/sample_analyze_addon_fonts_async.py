# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_analyze_addon_fonts_async.py

DESCRIPTION:
    This sample demonstrates how to extract font information using the add-on
    'STYLE_FONT' capability.

    Add-on capabilities are available within all models except for the Business card
    model. This sample uses Layout model to demonstrate.

    Add-on capabilities accept a list of strings containing values from the `AnalysisFeature`
    enum class. For more information, see:
    https://learn.microsoft.com/en-us/python/api/azure-ai-formrecognizer/azure.ai.formrecognizer.analysisfeature?view=azure-python.

    The following capabilities are free:
    - BARCODES
    - LANGUAGES

    The following capabilities will incur additional charges:
    - FORMULAS
    - OCR_HIGH_RESOLUTION
    - STYLE_FONT

    See pricing: https://azure.microsoft.com/pricing/details/ai-document-intelligence/.

USAGE:
    python sample_analyze_addon_fonts_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Form Recognizer resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer API key
"""

import asyncio
import os
from collections import defaultdict


def format_bounding_region(bounding_regions):
    if not bounding_regions:
        return "N/A"
    return ", ".join(
        f"Page #{region.page_number}: {format_polygon(region.polygon)}"
        for region in bounding_regions
    )


def format_polygon(polygon):
    if not polygon:
        return "N/A"
    return ", ".join([f"[{p.x}, {p.y}]" for p in polygon])


def get_styled_text(styles, content):
    # Iterate over the styles and merge the spans from each style.
    spans = [span for style in styles for span in style.spans]
    spans.sort(key=lambda span: span.offset)
    return ','.join([content[span.offset : span.offset + span.length] for span in spans])


async def analyze_fonts():
    path_to_sample_documents = os.path.abspath(
        os.path.join(
            os.path.abspath(__file__),
            "..",
            "..",
            "..",
            "sample_forms/add_ons/fonts_and_languages.png",
        )
    )
    # [START analyze_fonts]
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.formrecognizer import AnalysisFeature
    from azure.ai.formrecognizer.aio import DocumentAnalysisClient

    endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
    key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]

    document_analysis_client = DocumentAnalysisClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )

    async with document_analysis_client:
        # Specify which add-on capabilities to enable.
        with open(path_to_sample_documents, "rb") as f:
            poller = await document_analysis_client.begin_analyze_document(
                "prebuilt-layout", document=f, features=[AnalysisFeature.STYLE_FONT]
            )
        result = await poller.result()

    # DocumentStyle has the following font related attributes:
    similar_font_families = defaultdict(list)  # e.g., 'Arial, sans-serif
    font_styles = defaultdict(list)             # e.g, 'italic'
    font_weights = defaultdict(list)            # e.g., 'bold'
    font_colors = defaultdict(list)             # in '#rrggbb' hexadecimal format
    font_background_colors = defaultdict(list)  # in '#rrggbb' hexadecimal format

    if any([style.is_handwritten for style in result.styles]):
        print("Document contains handwritten content")
    else:
        print("Document does not contain handwritten content")

    print("\n----Fonts styles detected in the document----")

    # Iterate over the styles and group them by their font attributes.
    for style in result.styles:
        if style.similar_font_family:
            similar_font_families[style.similar_font_family].append(style)
        if style.font_style:
            font_styles[style.font_style].append(style)
        if style.font_weight:
            font_weights[style.font_weight].append(style)
        if style.color:
            font_colors[style.color].append(style)
        if style.background_color:
            font_background_colors[style.background_color].append(style)

    print(f"Detected {len(similar_font_families)} font families:")
    for font_family, styles in similar_font_families.items():
        print(f"- Font family: '{font_family}'")
        print(f"  Text: '{get_styled_text(styles, result.content)}'")

    print(f"\nDetected {len(font_styles)} font styles:")
    for font_style, styles in font_styles.items():
        print(f"- Font style: '{font_style}'")
        print(f"  Text: '{get_styled_text(styles, result.content)}'")

    print(f"\nDetected {len(font_weights)} font weights:")
    for font_weight, styles in font_weights.items():
        print(f"- Font weight: '{font_weight}'")
        print(f"  Text: '{get_styled_text(styles, result.content)}'")

    print(f"\nDetected {len(font_colors)} font colors:")
    for font_color, styles in font_colors.items():
        print(f"- Font color: '{font_color}'")
        print(f"  Text: '{get_styled_text(styles, result.content)}'")

    print(f"\nDetected {len(font_background_colors)} font background colors:")
    for font_background_color, styles in font_background_colors.items():
        print(f"- Font background color: '{font_background_color}'")
        print(f"  Text: '{get_styled_text(styles, result.content)}'")

    print("----------------------------------------")
    # [END analyze_fonts]


async def main():
    await analyze_fonts()


if __name__ == "__main__":
    from azure.core.exceptions import HttpResponseError

    try:
        asyncio.run(main())
    except HttpResponseError as error:
        print(
            "For more information about troubleshooting errors, see the following guide: "
            "https://aka.ms/azsdk/python/formrecognizer/troubleshooting"
        )
        # Examples of how to check an HttpResponseError
        # Check by error code:
        if error.error is not None:
            if error.error.code == "InvalidImage":
                print(f"Received an invalid image error: {error.error}")
            if error.error.code == "InvalidRequest":
                print(f"Received an invalid request error: {error.error}")
            # Raise the error again after printing it
            raise
        # If the inner error is None and then it is possible to check the message to get more information:
        if "Invalid request".casefold() in error.message.casefold():
            print(f"Uh-oh! Seems there was an invalid request: {error}")
        # Raise the error again
        raise
