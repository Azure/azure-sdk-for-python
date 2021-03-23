# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------


def sample_translation_status_checks():
    import os
    import time
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.documenttranslation import (
        DocumentTranslationClient,
        DocumentTranslationInput,
        TranslationTarget
    )

    endpoint = os.environ["AZURE_DOCUMENT_TRANSLATION_ENDPOINT"]
    key = os.environ["AZURE_DOCUMENT_TRANSLATION_KEY"]
    source_container_url = os.environ["AZURE_SOURCE_CONTAINER_URL"]
    target_container_url_es = os.environ["AZURE_TARGET_CONTAINER_URL_ES"]
    target_container_url_fr = os.environ["AZURE_TARGET_CONTAINER_URL_FR"]

    client = DocumentTranslationClient(endpoint, AzureKeyCredential(key))

    translation_inputs = [
        DocumentTranslationInput(
            source_url=source_container_url,
            targets=[
                TranslationTarget(
                    target_url=target_container_url_es,
                    language_code="es"
                ),
                TranslationTarget(
                    target_url=target_container_url_fr,
                    language_code="fr"
                )
            ],
            storage_type="folder",
            prefix="document_2021"
        )
    ]

    job_detail = client.create_translation_job(translation_inputs)

    while True:
        job_detail = client.get_job_status(job_detail.id)  # type: JobStatusResult
        if job_detail.status in ["NotStarted", "Running"]:
            time.sleep(30)
            continue

        elif job_detail.status in ["Failed", "ValidationFailed"]:
            if job_detail.error:
                print("Translation job failed: {}: {}".format(job_detail.error.code, job_detail.error.message))
            check_documents(client, job_detail.id)
            exit(1)

        elif job_detail.status == "Succeeded":
            print("We translated our documents!")
            if job_detail.documents_failed_count > 0:
                check_documents(client, job_detail.id)
            break


def check_documents(client, job_id):
    from azure.core.exceptions import ResourceNotFoundError

    try:
        doc_statuses = client.list_all_document_statuses(job_id)  # type: ItemPaged[DocumentStatusResult]
    except ResourceNotFoundError as err:
        print("Failed to process any documents in source/target container due to insufficient permissions.")
        raise err

    docs_to_retry = []
    for document in doc_statuses:
        if document.status == "Failed":
            print("Document at {} failed to be translated to {} language".format(
                document.translated_document_url, document.translate_to
            ))
            print("Document ID: {}, Error Code: {}, Message: {}".format(
                document.id, document.error.code, document.error.message
            ))
            if document.translated_document_url not in docs_to_retry:
                docs_to_retry.append(document.translated_document_url)


if __name__ == '__main__':
    sample_translation_status_checks()
