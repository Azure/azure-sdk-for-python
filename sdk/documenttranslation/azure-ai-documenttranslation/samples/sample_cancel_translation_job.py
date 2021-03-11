# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------


def sample_cancel_translation_job():
    # import libraries
    import os
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.documenttranslation import (
        DocumentTranslationClient,
        BatchDocumentInput,
        StorageTarget
    )

    # get service secrets
    endpoint = os.environ["AZURE_DOCUMENT_TRANSLATION_ENDPOINT"]
    key = os.environ["AZURE_DOCUMENT_TRANSLATION_KEY"]
    source_container_url = os.environ["AZURE_SOURCE_CONTAINER_URL"]
    target_container_url_es = os.environ["AZURE_TARGET_CONTAINER_URL_ES"]

    # create translation client
    client = DocumentTranslationClient(endpoint, AzureKeyCredential(key))

    # prepare translation inout
    batch = [
        BatchDocumentInput(
            source_url=source_container_url,
            targets=[
                StorageTarget(
                    target_url=target_container_url_es,
                    language="es"
                )
            ],
            storage_type="file"
        )
    ]

    # submit documents for translation
    poller = client.begin_translation(batch)  # type: DocumentTranslationPoller[ItemPaged[DocumentStatusDetail]]

    # initial status
    translation_details = poller.details # type: TranslationStatusDetail
    print("Translation initial status: {}".format(translation_details.status))
    print("Number of translations on documents: {}".format(translation_details.documents_total_count))

    # cancel job
    client.cancel_job(poller.batch_id)

    # get result
    translation_details = poller.details  # type: TranslationStatusDetail

    if translation_details.status in ["Cancelled", "Cancelling"]:
        print("We cancelled job with ID: {}".format(translation_details.id))


if __name__ == '__main__':
    sample_cancel_translation_job()
