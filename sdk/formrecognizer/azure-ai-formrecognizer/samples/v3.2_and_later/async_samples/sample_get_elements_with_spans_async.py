# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_get_elements_with_spans_async.py

DESCRIPTION:
    This sample demonstrates how to get elements that are contained in the spans of another element.
    In this sample, the examples attempt to find the lines and styles that have the same spans as the
    main search element. The purpose of this sample is to show how to search for document elements 
    that are within the same span area as other elements.

USAGE:
    python sample_get_elements_with_spans_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Form Recognizer resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer API key
"""

import os
import asyncio


def get_styles(element_spans, styles):
    result = []
    for span in element_spans:
        for style in styles:
            for style_span in style.spans:
                if style_span.offset >= span.offset and (
                    style_span.offset + style_span.length
                ) <= (span.offset + span.length):
                    result.append(style)
    return result


def get_lines(element_spans, document_page):
    result = []
    for span in element_spans:
        for line in document_page.lines:
            for line_span in line.spans:
                if line_span.offset >= span.offset and (
                    line_span.offset + line_span.length
                ) <= (span.offset + span.length):
                    result.append(line)
    return result


def get_page(page_number, pages):
    for page in pages:
        if page.page_number == page_number:
            return page
    raise ValueError("could not find the requested page")


async def get_elements_with_spans_async():
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

    # Below is a method to search for the lines of a particular element by using spans.
    # This example uses DocumentTable, but other elements that also have a `spans` or `span` field
    # can also be used to search for related elements, such as lines in this case.
    # To see an example for searching for words which have a `span` field, see
    # `sample_get_words_on_document_line.py` under the samples v3.2_and_later directory.
    if result.tables is not None:
        for table_idx, table in enumerate(result.tables):
            print(
                f"Table # {table_idx} has {table.row_count} rows and {table.column_count} columns"
            )

            lines = []

            if table.bounding_regions is not None:
                for region in table.bounding_regions:
                    print(f"Table # {table_idx} location on page: {region.page_number}")
                    lines.extend(
                        get_lines(
                            table.spans, get_page(region.page_number, result.pages)
                        )
                    )

            print(f"Found # {len(lines)} lines in the table")
            for line in lines:
                print(
                    f"...Line '{line.content}' is within bounding polygon: '{line.polygon}'"
                )

    # Below is a method to search for the style of a particular element by using spans.
    # This example uses DocumentLine, but other elements that also have a `spans` or `span`
    # field can also be used to search for document text style.
    if result.pages[0].lines is not None:
        for line in result.pages[0].lines:
            styles = get_styles(line.spans, result.styles)
            print(f"Found line '{line.content}' with style:")
            if not styles:
                print("...no handwritten text found")
            for style in styles:
                if style.is_handwritten:
                    print(f"...handwritten with confidence {style.confidence}")
    print("----------------------------------------")


async def main():
    await get_elements_with_spans_async()


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
