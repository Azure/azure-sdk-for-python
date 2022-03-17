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
    path_to_sample_forms = os.path.abspath(
        os.path.join(
            os.path.abspath(__file__),
            "..",
            "..",
            "./sample_forms/id_documents/license.jpg",
        )
    )

    from azure.core.serialization import AzureJSONEncoder
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.formrecognizer import FormRecognizerClient, RecognizedForm

    endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
    key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]

    form_recognizer_client = FormRecognizerClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )
    with open(path_to_sample_forms, "rb") as f:
        poller = form_recognizer_client.begin_recognize_identity_documents(identity_document=f)
    
    id_documents = poller.result()

    # convert the received model to a dictionary
    recognized_form_dict = [doc.to_dict() for doc in id_documents]

    # save the dictionary as JSON content in a JSON file, use the AzureJSONEncoder
    # to help make types, such as dates, JSON serializable
    # NOTE: AzureJSONEncoder is only available with azure.core>=1.18.0.
    with open('data.json', 'w') as f:
        json.dump(recognized_form_dict, f, cls=AzureJSONEncoder)

    # convert the dictionary back to the original model
    model = [RecognizedForm.from_dict(doc) for doc in recognized_form_dict]

    # use the model as normal
    for idx, id_document in enumerate(model):
        print("--------Recognizing converted ID document #{}--------".format(idx+1))
        first_name = id_document.fields.get("FirstName")
        if first_name:
            print("First Name: {} has confidence: {}".format(first_name.value, first_name.confidence))
        last_name = id_document.fields.get("LastName")
        if last_name:
            print("Last Name: {} has confidence: {}".format(last_name.value, last_name.confidence))
        document_number = id_document.fields.get("DocumentNumber")
        if document_number:
            print("Document Number: {} has confidence: {}".format(document_number.value, document_number.confidence))

    print("----------------------------------------")


if __name__ == "__main__":
    convert_to_and_from_dict()
