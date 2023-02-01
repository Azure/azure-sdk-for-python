# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_get_words_on_document_line_async.py

DESCRIPTION:
    This sample demonstrates how to get the words contained in a DocumentLine.
    Please note that `get_words` on DocumentLine is only available in SDK version
    3.2.0 and later.

USAGE:
    python sample_get_words_on_document_line_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Form Recognizer resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer API key
"""

import os
import asyncio

def format_bounding_region(bounding_regions):
    if not bounding_regions:
        return "N/A"
    return ", ".join("Page #{}: {}".format(region.page_number, format_polygon(region.polygon)) for region in bounding_regions)

def format_polygon(polygon):
    if not polygon:
        return "N/A"
    return ", ".join(["[{}, {}]".format(p.x, p.y) for p in polygon])


async def get_words_on_document_line_async():
    path_to_sample_documents = os.path.abspath(
        os.path.join(
            os.path.abspath(__file__),
            "..",
            "..",
            "..",
            "./sample_forms/forms/Form_1.jpg",
        )
    )

    from azure.core.credentials import AzureKeyCredential
    from azure.ai.formrecognizer.aio import DocumentAnalysisClient

    endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
    key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]

    document_analysis_client = DocumentAnalysisClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )
    async with document_analysis_client:
        with open(path_to_sample_documents, "rb") as f:
            poller = await document_analysis_client.begin_analyze_document(
                "prebuilt-document", document=f
            )
        result = await poller.result()

    for idx, page in enumerate(result.pages):
        print("----Analyzing lines and words from page #{}----".format(idx + 1))
        print(
            "Page has width: {} and height: {}, measured with unit: {}".format(
                page.width, page.height, page.unit
            )
        )

        if page.lines is not None:
            for line_idx, line in enumerate(page.lines):
                words = line.get_words()
                print(
                    "...Line # {} has word count {} and text '{}' within bounding polygon '{}'".format(
                        line_idx,
                        len(words),
                        line.content,
                        format_polygon(line.polygon),
                    )
                )

                for word in words:
                    print(
                        "......Word '{}' has a confidence of {}".format(
                            word.content, word.confidence
                        )
                    )

    print("----------------------------------------")


async def main():
    await get_words_on_document_line_async()


if __name__ == "__main__":
    import sys
    from azure.core.exceptions import HttpResponseError
    try:
        asyncio.run(main())
    except HttpResponseError as error:
        # Examples of how to check an HttpResponseError
        # Check by error code:
        if error.error is not None:
            if error.error.code == "InvalidRequest":
                print(f"Received an invalid request error: {error.error}")
                sys.exit(1)
            if error.error.code == "InvalidImage":
                print(f"Received an invalid image error: {error.error}")
                sys.exit(1)
        # If the inner error is None and then it is possible to check the message to get more information:
        filter_msg = ["Generic error", "Timeout", "Invalid request", "InvalidImage"]
        if any(example_error.casefold() in error.message.casefold() for example_error in filter_msg):
            print(f"Uh-oh! Something unexpected happened: {error}")
            sys.exit(1)
        # Print the full error content:
        print(f"Full HttpResponseError: {error}")
