# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------


def sample_cancel_batch():
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

    client = DocumentTranslationClient(endpoint, AzureKeyCredential(key))

    batch = [
        BatchTranslationInput(
            source_url=source_container_url,
            source_language="en",
            targets=[
                StorageTarget(
                    target_url=target_container_url_es,
                    language="es"
                )
            ],
            storage_type="file"
        )
    ]

    poller = client.begin_batch_translation(batch)

    batch_detail = client.get_batch_status(poller.batch_id)  # type: BatchStatusDetail

    print("Batch status: {}".format(batch_detail.status))
    print("Number of translations on documents: {}".format(batch_detail.documents_total_count))

    client.cancel_batch(batch_detail.id)
    detail = client.get_batch_status(batch_detail.id)  # type: BatchStatusDetail

    if detail.status in ["Cancelled", "Cancelling"]:
        print("We cancelled batch with ID: {}".format(detail.id))
