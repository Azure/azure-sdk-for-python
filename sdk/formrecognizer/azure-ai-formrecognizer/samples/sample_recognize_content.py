# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_recognize_content.py

DESCRIPTION:
    This sample demonstrates how to extract text and content information from a document
    given through a file.
USAGE:
    python sample_recognize_content.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Cognitive Services resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer API key
"""

import os

def format_bounding_box(bounding_box):
    if not bounding_box:
        return "N/A"
    return ", ".join(["[{}, {}]".format(p.x, p.y) for p in bounding_box])

class RecognizeContentSample(object):

    def recognize_content(self):
        path_to_sample_forms = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./sample_forms/forms/Invoice_1.pdf"))
        # [START recognize_content]
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.formrecognizer import FormRecognizerClient

        endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
        key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]

        form_recognizer_client = FormRecognizerClient(endpoint=endpoint, credential=AzureKeyCredential(key))
        with open(path_to_sample_forms, "rb") as f:
            poller = form_recognizer_client.begin_recognize_content(form=f)
        contents = poller.result()

        for idx, content in enumerate(contents):
            print("----Recognizing content from page #{}----".format(idx))
            print("Has width: {} and height: {}, measured with unit: {}".format(
                content.width,
                content.height,
                content.unit
            ))
            for table_idx, table in enumerate(content.tables):
                print("Table # {} has {} rows and {} columns".format(table_idx, table.row_count, table.column_count))
                for cell in table.cells:
                    print("...Cell[{}][{}] has text '{}' within bounding box '{}'".format(
                        cell.row_index,
                        cell.column_index,
                        cell.text,
                        format_bounding_box(cell.bounding_box)
                    ))
                    # [END recognize_content]
            for line_idx, line in enumerate(content.lines):
                print("Line # {} has word count '{}' and text '{}' within bounding box '{}'".format(
                    line_idx,
                    len(line.words),
                    line.text,
                    format_bounding_box(line.bounding_box)
                ))
                for word in line.words:
                    print("...Word '{}' has a confidence of {}".format(word.text, word.confidence))
            print("----------------------------------------")


if __name__ == '__main__':
    sample = RecognizeContentSample()
    sample.recognize_content()
