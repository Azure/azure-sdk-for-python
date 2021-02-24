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
        BatchTranslationInput,
        StorageTarget
    )

    endpoint = os.environ["AZURE_DOCUMENT_TRANSLATION_ENDPOINT"]
    key = os.environ["AZURE_DOCUMENT_TRANSLATION_KEY"]
    source_container_url = os.environ["AZURE_SOURCE_CONTAINER_URL"]
    target_container_url_es = os.environ["AZURE_TARGET_CONTAINER_URL_ES"]
    target_container_url_fr = os.environ["AZURE_TARGET_CONTAINER_URL_FR"]

    client = DocumentTranslationClient(endpoint, AzureKeyCredential(key))

    batch = [
        BatchTranslationInput(
            source_url=source_container_url,
            source_language="en",
            targets=[
                StorageTarget(
                    target_url=target_container_url_es,
                    language="es"
                ),
                StorageTarget(
                    target_url=target_container_url_fr,
                    language="fr"
                )
            ],
            storage_type="file"
        )
    ]

    poller = client.begin_batch_translation(batch)

    batch_detail = client.get_batch_status(poller.batch_id)  # type: BatchStatusDetail

    print("Batch initial status: {}".format(batch_detail.status))
    print("Number of translations on documents: {}".format(batch_detail.documents_total_count))

    batch_detail = poller.result()  # type: BatchStatusDetail
    if batch_detail.status == "Succeeded":
        print("We translated our documents!")
        if batch_detail.documents_failed_count > 0:
            check_documents(client, batch_detail.id)

    if batch_detail.status in ["Failed", "ValidationFailed"]:
        if batch_detail.error:
            print("Batch failed: {}: {}".format(batch_detail.error.code, batch_detail.error.message))
        check_documents(client, batch_detail.id)
        exit(1)


def check_documents(client, batch_id):
    from azure.core.exceptions import ResourceNotFoundError

    try:
        doc_statuses = client.list_statuses_of_documents(batch_id)  # type: ItemPaged[DocumentStatusDetail]
    except ResourceNotFoundError as err:
        print("Failed to process any documents in source/target container.")
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
