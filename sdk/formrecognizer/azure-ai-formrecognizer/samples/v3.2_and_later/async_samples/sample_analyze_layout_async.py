# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_analyze_layout_async.py

DESCRIPTION:
    This sample demonstrates how to extract text, selection marks, and layout information from a document
    given through a file.

    Note that selection marks returned from begin_analyze_document(model_id="prebuilt-layout") do not return the text
    associated with the checkbox. For the API to return this information, build a custom model to analyze the
    checkbox and its text. See sample_build_model.py for more information.

USAGE:
    python sample_analyze_layout_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Form Recognizer resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer API key
"""

import os
import asyncio


def format_polygon(polygon):
    if not polygon:
        return "N/A"
    return ", ".join([f"[{p.x}, {p.y}]" for p in polygon])


async def analyze_layout_async():
    path_to_sample_documents = os.path.abspath(
        os.path.join(
            os.path.abspath(__file__),
            "..",
            "..",
            "..",
            "./sample_forms/forms/form_selection_mark.png",
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
                "prebuilt-layout", document=f
            )
        result = await poller.result()

    for style in result.styles:
        print(
            f"Document contains {'handwritten' if style.is_handwritten else 'no handwritten'} content"
        )

    for page in result.pages:
        print(f"----Analyzing layout from page #{page.page_number}----")
        print(
            f"Page has width: {page.width} and height: {page.height}, measured with unit: {page.unit}"
        )

        for line_idx, line in enumerate(page.lines):
            words = line.get_words()
            print(
                f"...Line # {line_idx} has word count {len(words)} and text '{line.content}' "
                f"within bounding polygon '{format_polygon(line.polygon)}'"
            )

            for word in words:
                print(
                    f"......Word '{word.content}' has a confidence of {word.confidence}"
                )

        for selection_mark in page.selection_marks:
            print(
                f"Selection mark is '{selection_mark.state}' within bounding polygon "
                f"'{format_polygon(selection_mark.polygon)}' and has a confidence of {selection_mark.confidence}"
            )

    for table_idx, table in enumerate(result.tables):
        print(
            f"Table # {table_idx} has {table.row_count} rows and "
            f"{table.column_count} columns"
        )
        for region in table.bounding_regions:
            print(
                f"Table # {table_idx} location on page: {region.page_number} is {format_polygon(region.polygon)}"
            )
        for cell in table.cells:
            print(
                f"...Cell[{cell.row_index}][{cell.column_index}] has text '{cell.content}'"
            )
            for region in cell.bounding_regions:
                print(
                    f"...content on page {region.page_number} is within bounding polygon '{format_polygon(region.polygon)}'"
                )

    print("----------------------------------------")


async def main():
    await analyze_layout_async()


if __name__ == "__main__":
    import sys
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
