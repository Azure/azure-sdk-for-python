# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_get_document_elements.py

DESCRIPTION:
    This sample demonstrates how to get related document elements from the result of calling
    `begin_analyze_document()`.

USAGE:
    python sample_get_document_elements.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Cognitive Services resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer API key
"""

import os

def format_bounding_region(bounding_regions):
    if not bounding_regions:
        return "N/A"
    return ", ".join("Page #{}: {}".format(region.page_number, format_bounding_box(region.bounding_box)) for region in bounding_regions)

def format_bounding_box(bounding_box):
    if not bounding_box:
        return "N/A"
    return ", ".join(["[{}, {}]".format(p.x, p.y) for p in bounding_box])


def get_document_elements():
    path_to_sample_documents = os.path.abspath(
        os.path.join(
            os.path.abspath(__file__),
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

    print("----Getting words in key-value pairs found in document----")
    for kv_pair in result.key_value_pairs:
        if kv_pair.key:
            print(
                    "Key '{}' found within '{}' bounding regions".format(
                        kv_pair.key.content,
                        format_bounding_region(kv_pair.key.bounding_regions),
                    )
                )
            words = kv_pair.key.get_words()
            print(
                    "Key  has {} word(s):".format(
                        len(words),
                    )
                )
            for word in words:
                print(
                        "...found '{}' word with confidence {}".format(
                            word.content,
                            word.confidence,
                        )
                    )

    print("----Getting words in entities found in document----")
    for entity in result.entities:
        print("Entity of category '{}' with sub-category '{}'".format(entity.category, entity.sub_category))
        # NOTE: Calling get_lines() here will return a list of the DocumentLines that make up the entity.
        # These lines can be processed just like any other DocumentLine instance.
        words = entity.get_words()
        for word in words:
            print(
                    "...contains '{}' with confidence {}".format(
                        word.content,
                        word.confidence,
                    )
                )

    print("----Getting lines in tables found in document----")
    for table_idx, table in enumerate(result.tables):
        print(
            "Table # {} has {} rows and {} columns".format(
                table_idx, table.row_count, table.column_count
            )
        )
        print(
            "Table # {} has {} lines and {} words".format(
                table_idx, len(table.get_lines()), len(table.get_words())
            )
        )
        for line in table.get_lines():
            print(
                    "...found '{}' line".format(
                        line.content,
                    )
                )
            for word in line.get_words():
                print(
                    "......contains '{}' with confidence {}".format(
                        word.content,
                        word.confidence,
                    )
                )
    print("----------------------------------------")


if __name__ == "__main__":
    get_document_elements()
