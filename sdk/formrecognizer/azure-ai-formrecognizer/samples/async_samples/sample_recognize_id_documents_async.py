# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_recognize_id_documents_async.py

DESCRIPTION:
    This sample demonstrates how to recognize fields from an identity document.

    See fields found on an ID document here:
    https://aka.ms/formrecognizer/iddocumentfields

USAGE:
    python sample_recognize_id_documents_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Cognitive Services resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer API key
"""

import os
import asyncio


class RecognizeIdDocumentsSampleAsync(object):

    async def recognize_id_documents(self):
        path_to_sample_forms = os.path.abspath(os.path.join(os.path.abspath(__file__),
                                                            "..", "./../sample_forms/id_documents/license.jpg"))

        # [START recognize_id_documents]
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.formrecognizer.aio import FormRecognizerClient

        endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
        key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]

        async with FormRecognizerClient(
            endpoint=endpoint, credential=AzureKeyCredential(key)
        ) as form_recognizer_client:
            
            with open(path_to_sample_forms, "rb") as f:
                poller = await form_recognizer_client.begin_recognize_id_documents(id_document=f)
            
            id_documents = await poller.result()

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
                    print("Sex: {} has confidence: {}".format(sex.value_data.text, sex.confidence))
                address = id_document.fields.get("Address")
                if address:
                    print("Address: {} has confidence: {}".format(address.value, address.confidence))
                # FIXME: uncomment this
                # country = id_document.fields.get("Country")
                # if country:
                #     print("Country: {} has confidence: {}".format(country.value, country.confidence))
                region = id_document.fields.get("Region")
                if region:
                    print("Region: {} has confidence: {}".format(region.value, region.confidence))
        # [END recognize_id_documents]

async def main():
    sample = RecognizeIdDocumentsSampleAsync()
    await sample.recognize_id_documents()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
