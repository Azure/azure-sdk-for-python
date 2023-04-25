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
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Form Recognizer resource.
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

    from azure.core.serialization import AzureJSONEncoder
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

    # convert the received model to a dictionary
    analyze_result_dict = result.to_dict()

    # save the dictionary as JSON content in a JSON file, use the AzureJSONEncoder
    # to help make types, such as dates, JSON serializable
    # NOTE: AzureJSONEncoder is only available with azure.core>=1.18.0.
    with open('data.json', 'w') as output_file:
        json.dump(analyze_result_dict, output_file, cls=AzureJSONEncoder)

    # convert the dictionary back to the original model
    model = AnalyzeResult.from_dict(analyze_result_dict)

    # use the model as normal
    print("----Converted from dictionary AnalyzeResult----")
    print("Model ID: '{}'".format(model.model_id))
    print("Number of pages analyzed {}".format(len(model.pages)))
    print("API version used: {}".format(model.api_version))

    print("----------------------------------------")


if __name__ == "__main__":
    import sys
    from azure.core.exceptions import HttpResponseError
    try:
        convert_to_and_from_dict()
    except HttpResponseError as error:
        print("For more information about troubleshooting errors, see the following guide: "
              "https://aka.ms/azsdk/python/formrecognizer/troubleshooting")
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
