# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_analyze_layout.py

DESCRIPTION:
    This sample demonstrates how to extract text, selection marks, and layout information from a document
    given through a file.

    Note that selection marks returned from begin_analyze_document(model_id="prebuilt-layout") do not return the text
    associated with the checkbox. For the API to return this information, build a custom model to analyze the
    checkbox and its text. See sample_build_model.py for more information.

USAGE:
    python sample_analyze_layout.py

    Set the environment variables with your own values before running the sample:
    1) DOCUMENTINTELLIGENCE_ENDPOINT - the endpoint to your Document Intelligence resource.
    2) DOCUMENTINTELLIGENCE_API_KEY - your Document Intelligence API key.
"""

import os


def analyze_layout():
    path_to_sample_documents = os.path.abspath(
        os.path.join(
            os.path.abspath(__file__),
            "..",
            "./sample_forms/forms/tabular_and_general_data.docx",
        )
    )

    # [START extract_layout]
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.documentintelligence import DocumentIntelligenceClient
    from azure.ai.documentintelligence.models import AnalyzeResult

    def _in_span(word, spans):
        for span in spans:
            if word.span.offset >= span.offset and (word.span.offset + word.span.length) <= (span.offset + span.length):
                return True
        return False

    def _format_polygon(polygon):
        if not polygon:
            return "N/A"
        return ", ".join([f"[{polygon[i]}, {polygon[i + 1]}]" for i in range(0, len(polygon), 2)])

    endpoint = os.environ["DOCUMENTINTELLIGENCE_ENDPOINT"]
    key = os.environ["DOCUMENTINTELLIGENCE_API_KEY"]

    document_intelligence_client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))
    with open(path_to_sample_documents, "rb") as f:
        poller = document_intelligence_client.begin_analyze_document("prebuilt-layout", body=f)
    result: AnalyzeResult = poller.result()

    if result.styles and any([style.is_handwritten for style in result.styles]):
        print("Document contains handwritten content")
    else:
        print("Document does not contain handwritten content")

    for page in result.pages:
        print(f"----Analyzing layout from page #{page.page_number}----")
        print(f"Page has width: {page.width} and height: {page.height}, measured with unit: {page.unit}")

        if page.lines:
            for line_idx, line in enumerate(page.lines):
                words = []
                if page.words:
                    for word in page.words:
                        print(f"......Word '{word.content}' has a confidence of {word.confidence}")
                        if _in_span(word, line.spans):
                            words.append(word)
                print(
                    f"...Line # {line_idx} has word count {len(words)} and text '{line.content}' "
                    f"within bounding polygon '{_format_polygon(line.polygon)}'"
                )

        if page.selection_marks:
            for selection_mark in page.selection_marks:
                print(
                    f"Selection mark is '{selection_mark.state}' within bounding polygon "
                    f"'{_format_polygon(selection_mark.polygon)}' and has a confidence of {selection_mark.confidence}"
                )

    if result.paragraphs:
        print(f"----Detected #{len(result.paragraphs)} paragraphs in the document----")
        # Sort all paragraphs by span's offset to read in the right order.
        result.paragraphs.sort(key=lambda p: (p.spans.sort(key=lambda s: s.offset), p.spans[0].offset))
        print("-----Print sorted paragraphs-----")
        for paragraph in result.paragraphs:
            if not paragraph.bounding_regions:
                print(f"Found paragraph with role: '{paragraph.role}' within N/A bounding region")
            else:
                print(f"Found paragraph with role: '{paragraph.role}' within")
                print(
                    ", ".join(
                        f" Page #{region.page_number}: {_format_polygon(region.polygon)} bounding region"
                        for region in paragraph.bounding_regions
                    )
                )
            print(f"...with content: '{paragraph.content}'")
            print(f"...with offset: {paragraph.spans[0].offset} and length: {paragraph.spans[0].length}")

    if result.tables:
        for table_idx, table in enumerate(result.tables):
            print(f"Table # {table_idx} has {table.row_count} rows and " f"{table.column_count} columns")
            if table.bounding_regions:
                for region in table.bounding_regions:
                    print(
                        f"Table # {table_idx} location on page: {region.page_number} is {_format_polygon(region.polygon)}"
                    )
            for cell in table.cells:
                print(f"...Cell[{cell.row_index}][{cell.column_index}] has text '{cell.content}'")
                if cell.bounding_regions:
                    for region in cell.bounding_regions:
                        print(
                            f"...content on page {region.page_number} is within bounding polygon '{_format_polygon(region.polygon)}'"
                        )

    print("----------------------------------------")
    # [END extract_layout]


if __name__ == "__main__":
    from azure.core.exceptions import HttpResponseError
    from dotenv import find_dotenv, load_dotenv

    try:
        load_dotenv(find_dotenv())
        analyze_layout()
    except HttpResponseError as error:
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
