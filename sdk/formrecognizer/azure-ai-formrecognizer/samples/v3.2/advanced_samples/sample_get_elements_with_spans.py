# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_get_elements_with_spans.py

DESCRIPTION:
    This sample demonstrates how to get elements that are contained in the spans of another element.
    In this sample, the examples attempt to find the lines and styles that have the same spans as the
    main search element. The purpose of this sample is to show how to search for document elements 
    that are within the same span area as other elements.

USAGE:
    python sample_get_elements_with_spans.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Form Recognizer resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer API key
"""

import os

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

def get_elements_with_spans():
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
    from azure.ai.formrecognizer import DocumentAnalysisClient

    endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
    key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]

    document_analysis_client = DocumentAnalysisClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )
    with open(path_to_sample_documents, "rb") as f:
        poller = document_analysis_client.begin_analyze_document(
            "prebuilt-document", document=f
        )
    result = poller.result()

    # Below is a method to search for the lines of a particular element by using spans.
    # This example uses DocumentTable, but other elements that also have a `spans` or `span` field
    # can also be used to search for related elements, such as lines in this case.
    # To see an example for searching for words which have a `span` field, see
    # `sample_get_words_on_document_line.py` under the samples v3.2-beta directory.
    for table_idx, table in enumerate(result.tables):
        print(
            "Table # {} has {} rows and {} columns".format(
                table_idx, table.row_count, table.column_count
            )
        )

        lines = []

        for region in table.bounding_regions:
            print(
                "Table # {} location on page: {}".format(
                    table_idx,
                    region.page_number,
                )
            )
            lines.extend(get_lines(table.spans, get_page(region.page_number, result.pages)))

        print("Found # {} lines in the table".format(len(lines)))
        for line in lines:
            print(
                "...Line '{}' is within bounding polygon: '{}'".format(
                    line.content,
                    line.polygon,
                )
            )

    # Below is a method to search for the style of a particular element by using spans.
    # This example uses DocumentLine, but other elements that also have a `spans` or `span`
    # field can also be used to search for document text style.
    for line in result.pages[0].lines:
        styles = get_styles(line.spans, result.styles)
        print(
            "Found line '{}' with style:".format(
                line.content
            )
        )
        if not styles:
            print(
                "...no handwritten text found"
            )
        for style in styles:
            if style.is_handwritten:
                print(
                    "...handwritten with confidence {}".format(style.confidence)
                )
    print("----------------------------------------")


if __name__ == "__main__":
    get_elements_with_spans()
