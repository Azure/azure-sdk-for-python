# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------


def sample_custom_translation():
    import os
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.documenttranslation import (
        DocumentTranslationClient,
        DocumentTranslationInput,
        TranslationTarget
    )

    endpoint = os.environ["AZURE_DOCUMENT_TRANSLATION_ENDPOINT"]
    key = os.environ["AZURE_DOCUMENT_TRANSLATION_KEY"]
    source_container_url = os.environ["AZURE_SOURCE_CONTAINER_URL"]
    target_container_url_fr = os.environ["AZURE_TARGET_CONTAINER_URL_FR"]
    category_id = os.environ["AZURE_DOCUMENT_TRANSLATION_MODEL_ID"]

    client = DocumentTranslationClient(endpoint, AzureKeyCredential(key))

    translation_inputs = [
        DocumentTranslationInput(
            source_url=source_container_url,
            targets=[
                TranslationTarget(
                    target_url=target_container_url_fr,
                    language_code="fr",
                    category_id=category_id,
                    glossaries=["https://exampleglossary"]
                )
            ],
            prefix="document_2021"
        )
    ]

    job_detail = client.create_translation_job(translation_inputs)  # type: JobStatusResult

    print("Job initial status: {}".format(job_detail.status))
    print("Number of translations on documents: {}".format(job_detail.documents_total_count))

    job_result = client.wait_until_done(job_detail.id)  # type: JobStatusResult
    if job_result.status == "Succeeded":
        print("We translated our documents!")
        if job_result.documents_failed_count > 0:
            check_documents(client, job_result.id)

    elif job_result.status in ["Failed", "ValidationFailed"]:
        if job_result.error:
            print("Translation job failed: {}: {}".format(job_result.error.code, job_result.error.message))
        check_documents(client, job_result.id)
        exit(1)


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
    sample_custom_translation()
