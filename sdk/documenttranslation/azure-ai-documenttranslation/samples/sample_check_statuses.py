# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------


def sample_batch_translation():
    import os
    import time
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.documenttranslation import (
        DocumentTranslationClient,
        BatchDocumentInput,
        StorageSourceInput,
        StorageTargetInput
    )

    endpoint = os.environ["AZURE_DOCUMENT_TRANSLATION_ENDPOINT"]
    key = os.environ["AZURE_DOCUMENT_TRANSLATION_KEY"]
    source_container_url = os.environ["AZURE_SOURCE_CONTAINER_URL"]
    target_container_url_es = os.environ["AZURE_TARGET_CONTAINER_URL_ES"]
    target_container_url_fr = os.environ["AZURE_TARGET_CONTAINER_URL_FR"]

    client = DocumentTranslationClient(endpoint, AzureKeyCredential(key))

    batch = [
        BatchDocumentInput(
            source=StorageSourceInput(
                source_url=source_container_url,
                language="en",
                prefix="document_2021"
            ),
            targets=[
                StorageTargetInput(
                    target_url=target_container_url_es,
                    language="es"
                ),
                StorageTargetInput(
                    target_url=target_container_url_fr,
                    language="fr"
                )
            ],
            storage_type="folder"
        )
    ]

    poller = client.begin_batch_translation(batch)

    while True:
        batch_detail = client.get_batch_status(poller)  # type: BatchStatusDetail
        if batch_detail.status == ["NotStarted", "Running"]:
            time.sleep(5)
            continue

        if batch_detail.status == ["Failed", "ValidationFailed"]:
            print("Batch failed: {}: {}".format(batch_detail.error.code, batch_detail.error.message))
            check_documents(client, batch_detail.id)
            exit(1)

        if batch_detail.status == "Succeeded":
            print("We translated our documents!")
            if batch_detail.summary.failed > 0:
                check_documents(client, batch_detail.id)
            break


def check_documents(client, batch_id):
    docs_to_retry = []
    doc_statuses = client.list_documents_statuses(batch_id)  # type: ItemPaged[DocumentStatusDetail]
    for document in doc_statuses:
        if document.status == "Failed":
            print("Document at {} failed to be translated to {} language".format(
                document.document_url, document.translate_to
            ))
            print("Document ID: {}, Error Code: {}, Message: {}".format(
                document.id, document.error.code, document.error.message
            ))
            if document.id not in docs_to_retry:
                docs_to_retry.append(document.id)
