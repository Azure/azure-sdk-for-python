# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_recognize_identity_documents.py

DESCRIPTION:
    This sample demonstrates how to recognize fields from an identity document.

    See fields found on identity documents here:
    https://aka.ms/formrecognizer/iddocumentfields

USAGE:
    python sample_recognize_identity_documents.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Form Recognizer resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer API key
"""

import os


class RecognizeIdDocumentsSample(object):

    def recognize_identity_documents(self):
        path_to_sample_forms = os.path.abspath(os.path.join(os.path.abspath(__file__),
                                                            "..", "..", "./sample_forms/id_documents/license.jpg"))

        # [START recognize_identity_documents]
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.formrecognizer import FormRecognizerClient

        endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
        key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]

        form_recognizer_client = FormRecognizerClient(
            endpoint=endpoint, credential=AzureKeyCredential(key)
        )
        with open(path_to_sample_forms, "rb") as f:
            poller = form_recognizer_client.begin_recognize_identity_documents(identity_document=f)
        id_documents = poller.result()

        for idx, id_document in enumerate(id_documents):
            print("--------Recognizing ID document #{}--------".format(idx+1))
            first_name = id_document.fields.get("FirstName")
            if first_name:
                print("First Name: {} has confidence: {}".format(first_name.value, first_name.confidence))
            last_name = id_document.fields.get("LastName")
            if last_name:
                print("Last Name: {} has confidence: {}".format(last_name.value, last_name.confidence))
            document_number = id_document.fields.get("DocumentNumber")
            if document_number:
                print("Document Number: {} has confidence: {}".format(document_number.value, document_number.confidence))
            dob = id_document.fields.get("DateOfBirth")
            if dob:
                print("Date of Birth: {} has confidence: {}".format(dob.value, dob.confidence))
            doe = id_document.fields.get("DateOfExpiration")
            if doe:
                print("Date of Expiration: {} has confidence: {}".format(doe.value, doe.confidence))
            sex = id_document.fields.get("Sex")
            if sex:
                print("Sex: {} has confidence: {}".format(sex.value, sex.confidence))
            address = id_document.fields.get("Address")
            if address:
                print("Address: {} has confidence: {}".format(address.value, address.confidence))
            country_region = id_document.fields.get("CountryRegion")
            if country_region:
                print("Country/Region: {} has confidence: {}".format(country_region.value, country_region.confidence))
            region = id_document.fields.get("Region")
            if region:
                print("Region: {} has confidence: {}".format(region.value, region.confidence))
        # [END recognize_identity_documents]

if __name__ == '__main__':
    sample = RecognizeIdDocumentsSample()
    sample.recognize_identity_documents()
