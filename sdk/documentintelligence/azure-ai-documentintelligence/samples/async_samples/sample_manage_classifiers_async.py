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
    1) DOCUMENTINTELLIGENCE_ENDPOINT - the endpoint to your Document Intelligence resource.
    2) DOCUMENTINTELLIGENCE_API_KEY - your Document Intelligence API key.
    3) DOCUMENTINTELLIGENCE_TRAINING_DATA_CLASSIFIER_SAS_URL - The shared access signature (SAS) Url of your Azure Blob Storage container
"""

import asyncio
import os


async def sample_manage_classifiers():
    import uuid
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.documentintelligence.aio import DocumentIntelligenceAdministrationClient
    from azure.ai.documentintelligence.models import (
        AzureBlobContentSource,
        ClassifierDocumentTypeDetails,
        BuildDocumentClassifierRequest,
        DocumentClassifierDetails,
    )

    endpoint = os.environ["DOCUMENTINTELLIGENCE_ENDPOINT"]
    key = os.environ["DOCUMENTINTELLIGENCE_API_KEY"]
    container_sas_url = os.environ["DOCUMENTINTELLIGENCE_TRAINING_DATA_CLASSIFIER_SAS_URL"]

    document_intelligence_admin_client = DocumentIntelligenceAdministrationClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )
    async with document_intelligence_admin_client:
        # build a document classifier
        poller = await document_intelligence_admin_client.begin_build_classifier(
            BuildDocumentClassifierRequest(
                classifier_id=str(uuid.uuid4()),
                doc_types={
                    "IRS-1040-A": ClassifierDocumentTypeDetails(
                        azure_blob_source=AzureBlobContentSource(
                            container_url=container_sas_url, prefix="IRS-1040-A/train"
                        )
                    ),
                    "IRS-1040-D": ClassifierDocumentTypeDetails(
                        azure_blob_source=AzureBlobContentSource(
                            container_url=container_sas_url, prefix="IRS-1040-D/train"
                        )
                    ),
                },
                description="IRS document classifier",
            )
        )
        classifier: DocumentClassifierDetails = await poller.result()
        print(f"Built classifier with ID: {classifier.classifier_id}")
        print(f"API version used to build the classifier model: {classifier.api_version}")
        print(f"Classifier description: {classifier.description}")
        print(f"Document classes used for training the model:")
        for doc_type, details in classifier.doc_types.items():
            print(f"Document type: {doc_type}")
            if details.azure_blob_source:
                print(f"Container source: {details.azure_blob_source.container_url}\n")

        # Next, we get a paged list of all of our document classifiers
        classifiers = document_intelligence_admin_client.list_classifiers()

        print("We have the following 'ready' models with IDs and descriptions:")
        async for classifier in classifiers:
            print(f"{classifier.classifier_id} | {classifier.description}")

        my_classifier = await document_intelligence_admin_client.get_classifier(classifier_id=classifier.classifier_id)
        print(f"\nClassifier ID: {my_classifier.classifier_id}")
        print(f"Description: {my_classifier.description}")
        print(f"Classifier created on: {my_classifier.created_date_time}")
        print(f"Classifier expires on: {my_classifier.expiration_date_time}")

        # Finally, we will delete this classifier by ID
        await document_intelligence_admin_client.delete_classifier(classifier_id=my_classifier.classifier_id)

        from azure.core.exceptions import ResourceNotFoundError

        try:
            await document_intelligence_admin_client.get_classifier(classifier_id=my_classifier.classifier_id)
        except ResourceNotFoundError:
            print(f"Successfully deleted classifier with ID {my_classifier.classifier_id}")


async def main():
    await sample_manage_classifiers()


if __name__ == "__main__":
    from azure.core.exceptions import HttpResponseError
    from dotenv import find_dotenv, load_dotenv

    try:
        load_dotenv(find_dotenv())
        asyncio.run(main())
    except HttpResponseError as error:
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
