# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_manage_classifiers_async.py

DESCRIPTION:
    This sample demonstrates how to manage the classifiers on your account. To learn
    how to build a classifier, look at sample_build_classifier.py.

USAGE:
    python sample_manage_classifiers_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Form Recognizer resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer API key
    3) CLASSIFIER_CONTAINER_SAS_URL - The shared access signature (SAS) Url of your Azure Blob Storage container
"""

import os
import asyncio


async def sample_manage_classifiers_async():
    from azure.core.credentials import AzureKeyCredential
    from azure.core.exceptions import ResourceNotFoundError
    from azure.ai.formrecognizer.aio import DocumentModelAdministrationClient
    from azure.ai.formrecognizer import ClassifierDocumentTypeDetails, AzureBlobContentSource

    endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
    key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]
    container_sas_url = os.environ["CLASSIFIER_CONTAINER_SAS_URL"]

    document_model_admin_client = DocumentModelAdministrationClient(endpoint=endpoint, credential=AzureKeyCredential(key))

    async with document_model_admin_client:
        # build a document classifier
        poller = await document_model_admin_client.begin_build_document_classifier(
            doc_types={
                "IRS-1040-A": ClassifierDocumentTypeDetails(
                    azure_blob_source=AzureBlobContentSource(
                        container_url=container_sas_url,
                        prefix="IRS-1040-A/train"
                    )
                ),
                "IRS-1040-D": ClassifierDocumentTypeDetails(
                    azure_blob_source=AzureBlobContentSource(
                        container_url=container_sas_url,
                        prefix="IRS-1040-D/train"
                    )
                )
            },
        )
        classifier_model = await poller.result()
        print(f"Built classifier with ID: {classifier_model.classifier_id}\n")

        # Next, we get a paged list of all of our document classifiers
        # [START list_document_classifiers_async]
        classifiers = document_model_admin_client.list_document_classifiers()

        print("We have the following 'ready' models with IDs and descriptions:")
        async for classifier in classifiers:
            print("{} | {}".format(classifier.classifier_id, classifier.description))
        # [END list_document_classifiers_async]

        # [START get_document_classifier_async]
        my_classifier = await document_model_admin_client.get_document_classifier(classifier_id=classifier_model.classifier_id)
        print("\nClassifier ID: {}".format(my_classifier.classifier_id))
        print("Description: {}".format(my_classifier.description))
        print("Classifier created on: {}".format(my_classifier.created_on))
        # [END get_document_classifier_async]

        # Finally, we will delete this classifier by ID
        # [START delete_document_classifier_async]
        await document_model_admin_client.delete_document_classifier(classifier_id=my_classifier.classifier_id)

        try:
            await document_model_admin_client.get_document_classifier(classifier_id=my_classifier.classifier_id)
        except ResourceNotFoundError:
            print("Successfully deleted classifier with ID {}".format(my_classifier.classifier_id))
        # [END delete_document_classifier_async]


async def main():
    await sample_manage_classifiers_async()

if __name__ == '__main__':
    import sys
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
