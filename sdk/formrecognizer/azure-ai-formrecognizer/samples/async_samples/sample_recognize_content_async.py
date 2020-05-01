# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_recognize_content_async.py

DESCRIPTION:
    This sample demonstrates how to extact text and content information from a document
    given through a file.

USAGE:
    python sample_recognize_content_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Cognitive Services resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer API key
"""

import os
import asyncio
from pathlib import Path


def format_bounding_box(bounding_box):
    if not bounding_box:
        return "N/A"
    return ", ".join(["[{}, {}]".format(p.x, p.y) for p in bounding_box])

class RecognizeContentSampleAsync(object):

    endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
    key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]

    async def recognize_content(self):
        # the sample forms are located in this file's parent's parent's files.
        path_to_sample_forms = Path(__file__).parent.parent.absolute() / Path("sample_forms/forms/Invoice_1.pdf")
        from azure.ai.formrecognizer import FormWord, FormLine
        # [START recognize_content_async]
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.formrecognizer.aio import FormRecognizerClient
        async with FormRecognizerClient(
            endpoint=self.endpoint, credential=AzureKeyCredential(self.key)
        ) as form_recognizer_client:

            with open(path_to_sample_forms, "rb") as f:
                contents = await form_recognizer_client.recognize_content(stream=f.read())

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
                        # [END recognize_content_async]
                for line_idx, line in enumerate(content.lines):
                    print("Line # {} has word count '{}' and text '{}' within bounding box '{}'".format(
                        line_idx,
                        len(line.words),
                        line.text,
                        format_bounding_box(line.bounding_box)
                    ))
                print("----------------------------------------")


async def main():
    sample = RecognizeContentSampleAsync()
    await sample.recognize_content()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
