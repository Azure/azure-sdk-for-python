# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------


def sample_batch_translation():
    import os
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.documenttranslation import (
        DocumentTranslationClient,
        BatchDocumentInput,
        StorageTarget
    )

    endpoint = os.environ["AZURE_DOCUMENT_TRANSLATION_ENDPOINT"]
    key = os.environ["AZURE_DOCUMENT_TRANSLATION_KEY"]
    source_container_url_en = os.environ["AZURE_SOURCE_CONTAINER_URL_EN"]
    source_container_url_de = os.environ["AZURE_SOURCE_CONTAINER_URL_DE"]
    target_container_url_es = os.environ["AZURE_TARGET_CONTAINER_URL_ES"]
    target_container_url_fr = os.environ["AZURE_TARGET_CONTAINER_URL_FR"]

    client = DocumentTranslationClient(endpoint, AzureKeyCredential(key))

    batch = [
        BatchDocumentInput(
            source_url=source_container_url_en,
            targets=[
                StorageTarget(
                    target_url=target_container_url_es,
                    language="es"
                ),
                StorageTarget(
                    target_url=target_container_url_fr,
                    language="fr"
                )
            ]
        ),
        BatchDocumentInput(
            source_url=source_container_url_de,
            targets=[
                StorageTarget(
                    target_url=target_container_url_es,
                    language="es"
                ),
                StorageTarget(
                    target_url=target_container_url_fr,
                    language="fr"
                )
            ]
        )
    ]

    job_detail = client.create_translation_job(batch)  # type: JobStatusDetail

    print("Job initial status: {}".format(job_detail.status))
    print("Number of translations on documents: {}".format(job_detail.documents_total_count))

    job_result = client.wait_until_done(job_detail.id)  # type: JobStatusDetail
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
        doc_statuses = client.list_documents_statuses(job_id)  # type: ItemPaged[DocumentStatusDetail]
    except ResourceNotFoundError as err:
        print("Failed to process any documents in source/target container due to insufficient permissions.")
        raise err

    docs_to_retry = []
    for document in doc_statuses:
        if document.status == "Failed":
            print("Document at {} failed to be translated to {} language".format(
                document.url, document.translate_to
            ))
            print("Document ID: {}, Error Code: {}, Message: {}".format(
                document.id, document.error.code, document.error.message
            ))
            if document.url not in docs_to_retry:
                docs_to_retry.append(document.url)


if __name__ == '__main__':
    sample_batch_translation()
