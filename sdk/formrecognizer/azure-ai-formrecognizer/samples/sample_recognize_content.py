# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_recognize_content.py

DESCRIPTION:
    This sample demonstrates how to extact text and layout information from a document
    given through a file.
USAGE:
    python sample_recognize_content.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Cognitive Services resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer subscription key
"""

import os


class RecognizeContentSample(object):

    endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
    key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]

    def recognize_content(self):
        # TODO: this can be used as examples in sphinx
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.formrecognizer import FormRecognizerClient
        form_recognizer_client = FormRecognizerClient(endpoint=self.endpoint, credential=AzureKeyCredential(self.key))
        with open("sample_forms/forms/Invoice_1.pdf", "rb") as f:
            poller = form_recognizer_client.begin_recognize_content(stream=f.read())
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
                    print("Cell[{}][{}] has text '{}' within bounding box '{}'".format(
                        cell.row_index,
                        cell.column_index,
                        cell.text,
                        ", ".join(["[{}, {}]".format(p.x, p.y) for p in cell.bounding_box]),
                    ))
            print("----------------------------------------")


if __name__ == '__main__':
    sample = RecognizeContentSample()
    sample.recognize_content()
