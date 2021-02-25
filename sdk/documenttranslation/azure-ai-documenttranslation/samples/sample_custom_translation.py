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
        BatchTranslationInput,
        StorageTarget
    )

    endpoint = os.environ["AZURE_DOCUMENT_TRANSLATION_ENDPOINT"]
    key = os.environ["AZURE_DOCUMENT_TRANSLATION_KEY"]
    source_container_url = os.environ["AZURE_SOURCE_CONTAINER_URL"]
    target_container_url_fr = os.environ["AZURE_TARGET_CONTAINER_URL_FR"]
    category_id = os.environ["AZURE_DOCUMENT_TRANSLATION_MODEL_ID"]

    client = DocumentTranslationClient(endpoint, AzureKeyCredential(key))

    batch = [
        BatchTranslationInput(
            source_url=source_container_url,
            source_language="en",
            targets=[
                StorageTarget(
                    target_url=target_container_url_fr,
                    language="fr",
                    category_id=category_id
                )
            ],
            prefix="document_2021"
        )
    ]

    batch_detail = client.create_batch(batch)  # type: BatchStatusDetail

    print("Batch initial status: {}".format(batch_detail.status))
    print("Number of translations on documents: {}".format(batch_detail.documents_total_count))

    batch_result = client.wait_until_done(batch_detail.id)  # type: BatchStatusDetail
    if batch_result.status == "Succeeded":
        print("We translated our documents!")
        if batch_result.documents_failed_count > 0:
            check_documents(client, batch_result.id)

        if batch_result.status in ["Failed", "ValidationFailed"]:
            if batch_result.error:
                print("Batch failed: {}: {}".format(batch_result.error.code, batch_result.error.message))
            check_documents(client, batch_result.id)
            exit(1)


def check_documents(client, batch_id):
    from azure.core.exceptions import ResourceNotFoundError

    try:
        doc_statuses = client.list_documents_statuses(batch_id)  # type: ItemPaged[DocumentStatusDetail]
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
