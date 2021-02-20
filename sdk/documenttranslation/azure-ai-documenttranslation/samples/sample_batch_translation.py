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
            storage_type="file"
        )
    ]

    poller = client.begin_batch_translation(batch)

    batch_detail = client.get_batch_status(poller)  # type: BatchStatusDetail

    print("Batch initial status: {}".format(batch_detail.status))
    print("Number of translations on documents: {}".format(batch_detail.summary.total))

    batch_result = poller.result()  # type: BatchStatusDetail
    if batch_result.status == "Succeeded":
        print("We translated our documents!")
        if batch_result.summary.failed > 0:
            check_documents(client, batch_detail.id)

    if batch_result.status == "Failed":
        print("Batch failed: {}: {}".format(batch_result.error.code, batch_result.error.message))
        check_documents(client, batch_detail.id)


def check_documents(client, batch_id):
    doc_statuses = client.list_documents_statuses(batch_id)  # type: ItemPaged[DocumentStatusDetail]
    for document in doc_statuses:
        if document.status == "Failed":
            print("Document at {} failed to be translated to {} language".format(
                document.document_url, document.translate_to
            ))
            print("Document ID: {}, Error Code: {}, Message: {}".format(
                document.id, document.error.code, document.error.message
            ))
