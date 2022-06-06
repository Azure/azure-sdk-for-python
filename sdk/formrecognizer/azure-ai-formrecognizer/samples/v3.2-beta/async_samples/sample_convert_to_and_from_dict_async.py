# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_convert_to_and_from_dict_async.py

DESCRIPTION:
    This sample demonstrates how to convert models returned from an analyze operation
    to and from a dictionary. The dictionary in this sample is then converted to a
    JSON file, then the same dictionary is converted back to its original model.

USAGE:
    python sample_convert_to_and_from_dict_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Form Recognizer resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer API key
"""

import os
import json
import asyncio

async def convert_to_and_from_dict_async():
    path_to_sample_documents = os.path.abspath(
        os.path.join(
            os.path.abspath(__file__),
            "..",
            "..",
            "..",
            "./sample_forms/forms/Form_1.jpg",
        )
    )

    from azure.core.serialization import AzureJSONEncoder
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.formrecognizer.aio import DocumentAnalysisClient
    from azure.ai.formrecognizer import AnalyzeResult

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

    # convert the received model to a dictionary
    analyze_result_dict = result.to_dict()

    # save the dictionary as JSON content in a JSON file, use the AzureJSONEncoder
    # to help make types, such as dates, JSON serializable
    # NOTE: AzureJSONEncoder is only available with azure.core>=1.18.0.
    with open('data.json', 'w') as f:
        json.dump(analyze_result_dict, f, cls=AzureJSONEncoder)

    # convert the dictionary back to the original model
    model = AnalyzeResult.from_dict(analyze_result_dict)

    # use the model as normal
    print("----Converted from dictionary AnalyzeResult----")
    print("Model ID: '{}'".format(model.model_id))
    print("Number of pages analyzed {}".format(len(model.pages)))
    print("API version used: {}".format(model.api_version))

    print("----------------------------------------")


async def main():
    await convert_to_and_from_dict_async()


if __name__ == '__main__':
    asyncio.run(main())
