# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_create_translation_job.py

DESCRIPTION:
    This sample demonstrates how to create a translation job for documents in your Azure Blob
    Storage container and wait until the job is completed.

    To set up your containers for translation and generate SAS tokens to your containers (or files)
    with the appropriate permissions, see the README.

USAGE:
    python sample_create_translation_job.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_DOCUMENT_TRANSLATION_ENDPOINT - the endpoint to your Document Translation resource.
    2) AZURE_DOCUMENT_TRANSLATION_KEY - your Document Translation API key.
    3) AZURE_SOURCE_CONTAINER_URL - the container SAS URL to your source container which has the documents
        to be translated.
    4) AZURE_TARGET_CONTAINER_URL - the container SAS URL to your target container where the translated documents
        will be written.
"""


def sample_translation():
    import os
    # [START wait_until_done]
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.translation.document import (
        DocumentTranslationClient,
        DocumentTranslationInput,
        TranslationTarget
    )

    endpoint = os.environ["AZURE_DOCUMENT_TRANSLATION_ENDPOINT"]
    key = os.environ["AZURE_DOCUMENT_TRANSLATION_KEY"]
    source_container_url = os.environ["AZURE_SOURCE_CONTAINER_URL"]
    target_container_url = os.environ["AZURE_TARGET_CONTAINER_URL"]

    client = DocumentTranslationClient(endpoint, AzureKeyCredential(key))

    job = client.create_translation_job(inputs=[
            DocumentTranslationInput(
                source_url=source_container_url,
                targets=[
                    TranslationTarget(
                        target_url=target_container_url,
                        language_code="es"
                    )
                ]
            )
        ]
    )  # type: JobStatusResult

    job_result = client.wait_until_done(job.id)  # type: JobStatusResult

    print("Job status: {}".format(job_result.status))
    print("Job created on: {}".format(job_result.created_on))
    print("Job last updated on: {}".format(job_result.last_updated_on))
    print("Total number of translations on documents: {}".format(job_result.documents_total_count))

    print("\nOf total documents...")
    print("{} failed".format(job_result.documents_failed_count))
    print("{} succeeded".format(job_result.documents_succeeded_count))
    # [END wait_until_done]

    # [START list_all_document_statuses]
    doc_results = client.list_all_document_statuses(job_result.id)  # type: ItemPaged[DocumentStatusResult]
    for document in doc_results:
        print("Document ID: {}".format(document.id))
        print("Document status: {}".format(document.status))
        if document.status == "Succeeded":
            print("Source document location: {}".format(document.source_document_url))
            print("Translated document location: {}".format(document.translated_document_url))
            print("Translated to language: {}\n".format(document.translate_to))
        else:
            print("Error Code: {}, Message: {}\n".format(document.error.code, document.error.message))
    # [END list_all_document_statuses]

if __name__ == '__main__':
    sample_translation()
