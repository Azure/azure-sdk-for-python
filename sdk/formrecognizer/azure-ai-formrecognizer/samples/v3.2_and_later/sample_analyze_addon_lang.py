# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_analyze_addon_lang.py

DESCRIPTION:
    This sample demonstrates how to extract font information using the add-on
    'font' capability.

    Add-on capabilities are available within all models except for the Business card
    model. The sample uses Layout model to demonstrate.

USAGE:
    python sample_analyze_addon_lang.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Form Recognizer resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer API key
"""

import os

from dotenv import load_dotenv


load_dotenv()


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


def get_text(styles, content):
    spans = [span for style in styles for span in style.spans]
    spans.sort(key=lambda span: span.offset)
    return ','.join([content[span.offset : span.offset + span.length] for span in spans])


def analyze_languages():
    path_to_sample_documents = os.path.abspath(
        os.path.join(
            os.path.abspath(__file__),
            "..",
            "..",
            "sample_forms/add_ons/font_and_languages.png",
        )
    )

    from azure.core.credentials import AzureKeyCredential
    from azure.ai.formrecognizer import DocumentAnalysisClient, AnalysisFeature

    endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
    key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]

    document_analysis_client = DocumentAnalysisClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )
    with open(path_to_sample_documents, "rb") as f:
        poller = document_analysis_client.begin_analyze_document(
            "prebuilt-layout", document=f, features=[AnalysisFeature.LANGUAGES]
        )
    result = poller.result()

    print("----Languages detected in the document----")
    print(f"Detected {len(result.languages)} languages:")
    for lang_idx, lang in enumerate(result.languages):
        print(f"- Language #{lang_idx}: locale '{lang.locale}'")
        print(f"  Confidence: {lang.confidence}")
        print(f"  Text: '{','.join([result.content[span.offset : span.offset + span.length] for span in lang.spans])}'")

    print("----------------------------------------")


if __name__ == "__main__":
    from azure.core.exceptions import HttpResponseError

    try:
        analyze_languages()
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
