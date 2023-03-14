# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_classify_document_async.py

DESCRIPTION:
    This sample demonstrates how to classify a document using a trained document classifier.

USAGE:
    python sample_classify_document_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Form Recognizer resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer API key
    3) CLASSIFIER_ID - the ID of your trained document classifier
        -OR-
       CONTAINER_SAS_URL - The shared access signature (SAS) Url of your Azure Blob Storage container with your training files.
       A document classifier will be built and used to run the sample.
"""

import os
import asyncio

async def classify_document_async(classifier_id):
    path_to_sample_documents = os.path.abspath(
        os.path.join(
            os.path.abspath(__file__),
            "..",
            "..",
            "..",
            "./sample_forms/forms/Form_1.jpg",
        )
    )

    # [START classify_document_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.formrecognizer.aio import DocumentAnalysisClient

    endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
    key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]
    classifier_id = os.getenv("CLASSIFIER_ID", classifier_id)

    document_analysis_client = DocumentAnalysisClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )
    async with document_analysis_client:
        with open(path_to_sample_documents, "rb") as f:
            poller = await document_analysis_client.begin_classify_document(
                classifier_id, document=f
            )
        result = await poller.result()

    print("----Classified documents----")
    for doc in result.documents:
        print("Found document of type '{}' with confidence of {}".format(doc.doc_type or "N/A", doc.confidence))

    print("----------------------------------------")
    # [END classify_document_async]


async def main():
    classifier_id = None
    if os.getenv("CONTAINER_SAS_URL") and not os.getenv("CLASSIFIER_ID"):

        from azure.core.credentials import AzureKeyCredential
        from azure.ai.formrecognizer.aio import DocumentModelAdministrationClient

        endpoint = os.getenv("AZURE_FORM_RECOGNIZER_ENDPOINT")
        key = os.getenv("AZURE_FORM_RECOGNIZER_KEY")

        if not endpoint or not key:
            raise ValueError("Please provide endpoint and API key to run the samples.")

        document_model_admin_client = DocumentModelAdministrationClient(
            endpoint=endpoint, credential=AzureKeyCredential(key)
        )
        async with document_model_admin_client:
            blob_container_sas_url = os.getenv("CONTAINER_SAS_URL")
            if blob_container_sas_url is not None:
                poller = await document_model_admin_client.begin_build_document_classifier(
                    blob_container_url=blob_container_sas_url
                )
                classifier = await poller.result()
                classifier_id = classifier.model_id

    await classify_document_async(classifier_id)

if __name__ == '__main__':
    from azure.core.exceptions import HttpResponseError
    try:
        asyncio.run(main())
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
