# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_convert_to_and_from_dict.py

DESCRIPTION:
    This sample demonstrates how to convert models returned from an analyze operation
    to and from a dictionary. The dictionary in this sample is then converted to a
    JSON file, then the same dictionary is converted back to its original model.

USAGE:
    python sample_convert_to_and_from_dict.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Cognitive Services resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer API key
"""

import os
import json

def convert_to_and_from_dict():
    path_to_sample_documents = os.path.abspath(
        os.path.join(
            os.path.abspath(__file__),
            "..",
            "..",
            "./sample_forms/forms/Form_1.jpg",
        )
    )

    from azure.core.credentials import AzureKeyCredential
    from azure.ai.formrecognizer import DocumentAnalysisClient, AnalyzeResult

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

    # connvert the received model to a dictionary
    d = result.to_dict()

    # save the dictionary as a JSON content in a JSON file
    with open('data.json', 'w') as f:
        json.dump(d, f)

    # convert the dictionary back to the original model
    model = AnalyzeResult.from_dict(d)

    # use the model as normal
    for style in model.styles:
        if style.is_handwritten:
            print("Document contains handwritten content: ")
            print(",".join([model.content[span.offset:span.offset + span.length] for span in style.spans]))

    print("----Key-value pairs found in document----")
    for kv_pair in model.key_value_pairs:
        if kv_pair.key:
            print(
                    "Key '{}' found within '{}' bounding regions".format(
                        kv_pair.key.content,
                        kv_pair.key.bounding_regions,
                    )
                )
        if kv_pair.value:
            print(
                    "Value '{}' found within '{}' bounding regions\n".format(
                        kv_pair.value.content,
                        kv_pair.value.bounding_regions,
                    )
                )

    print("----Entities found in document----")
    for entity in model.entities:
        print("Entity of category '{}' with sub-category '{}'".format(entity.category, entity.sub_category))
        print("...has content '{}'".format(entity.content))
        print("...within '{}' bounding regions".format(entity.bounding_regions))
        print("...with confidence {}\n".format(entity.confidence))

    for table_idx, table in enumerate(model.tables):
        print(
            "Table # {} has {} rows and {} columns".format(
                table_idx, table.row_count, table.column_count
            )
        )
        for region in table.bounding_regions:
            print(
                "Table # {} location on page: {} is on {}".format(
                    table_idx,
                    region.page_number,
                    region.bounding_box,
                )
            )
        for cell in table.cells:
            print(
                "...Cell[{}][{}] has content '{}'".format(
                    cell.row_index,
                    cell.column_index,
                    cell.content,
                )
            )
    print("----------------------------------------")


if __name__ == "__main__":
    convert_to_and_from_dict()
