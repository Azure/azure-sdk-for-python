# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_check_document_statuses.py

DESCRIPTION:
    This sample demonstrates how to create a translation job and then monitor each document's status
    and progress within the job.

    To set up your containers for translation and generate SAS tokens to your containers (or files)
    with the appropriate permissions, see the README.

USAGE:
    python sample_check_document_statuses.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_DOCUMENT_TRANSLATION_ENDPOINT - the endpoint to your Document Translation resource.
    2) AZURE_DOCUMENT_TRANSLATION_KEY - your Document Translation API key.
    3) AZURE_SOURCE_CONTAINER_URL - the container SAS URL to your source container which has the documents
        to be translated.
    4) AZURE_TARGET_CONTAINER_URL - the container SAS URL to your target container where the translated documents
        will be written.
"""


def sample_document_status_checks():
    import os
    import time
    # [START create_translation_job]
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

    job_result = client.create_translation_job(inputs=[
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
    # [END create_translation_job]

    completed_docs = []
    while not job_result.has_completed:
        time.sleep(30)

        doc_statuses = client.list_all_document_statuses(job_result.id)
        for document in doc_statuses:
            if document.id not in completed_docs:
                if document.status == "Succeeded":
                    print("Document at {} was translated to {} language. You can find translated document at {}".format(
                        document.source_document_url, document.translate_to, document.translated_document_url
                    ))
                    completed_docs.append(document.id)
                if document.status == "Failed":
                    print("Document ID: {}, Error Code: {}, Message: {}".format(
                        document.id, document.error.code, document.error.message
                    ))
                    completed_docs.append(document.id)
                if document.status == "Running":
                    print("Document ID: {}, translation progress is {} percent".format(
                        document.id, document.translation_progress * 100
                    ))

        job_result = client.get_job_status(job_result.id)

    print("\nTranslation job completed.")


if __name__ == '__main__':
    sample_document_status_checks()
