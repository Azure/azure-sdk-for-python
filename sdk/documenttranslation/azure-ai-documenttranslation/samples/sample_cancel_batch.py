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
        BatchDocumentInput,
        StorageSourceInput,
        StorageTargetInput
    )

    endpoint = os.environ["AZURE_DOCUMENT_TRANSLATION_ENDPOINT"]
    key = os.environ["AZURE_DOCUMENT_TRANSLATION_KEY"]
    source_container_url = os.environ["AZURE_SOURCE_CONTAINER_URL"]
    target_container_url_es = os.environ["AZURE_TARGET_CONTAINER_URL_ES"]

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
                )
            ],
            storage_type="file"
        )
    ]

    poller = client.begin_batch_translation(batch)

    batch_detail = client.get_batch_status(poller)  # type: BatchStatusDetail

    print("Batch status: {}".format(batch_detail.status))
    print("Number of translations on documents: {}".format(batch_detail.summary.total))

    client.cancel_batch(poller)
    detail = client.get_batch_status(poller)  # type: BatchStatusDetail

    if detail.status in ["Cancelled", "Cancelling"]:
        print("We cancelled batch with ID: {}".format(detail.id))
