# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------


def sample_batch_translation():
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
    source_container_url_en = os.environ["AZURE_SOURCE_CONTAINER_URL_EN"]
    source_container_url_de = os.environ["AZURE_SOURCE_CONTAINER_URL_DE"]
    target_container_url_es = os.environ["AZURE_TARGET_CONTAINER_URL_ES"]
    target_container_url_fr = os.environ["AZURE_TARGET_CONTAINER_URL_FR"]

    # create translation client
    client = DocumentTranslationClient(endpoint, AzureKeyCredential(key))

    # prepare translation input
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

    # submit documents for translation
    poller = client.begin_translation(batch)  # type: DocumentTranslationPoller[ItemPaged[DocumentStatusDetail]]
    
    # initial status
    translation_details = poller.details # type: TranslationStatusDetail
    print("Translation initial status: {}".format(translation_details.status))
    print("Number of translations on documents: {}".format(translation_details.documents_total_count))

    # get final status
    doc_statuses = poller.result()  # type: ItemPaged[DocumentStatusDetail]
    translation_details = poller.details # type: TranslationStatusDetail
    if translation_details.status == "Succeeded":
        print("We translated our documents!")
        if translation_details.documents_failed_count > 0:
            docs_to_retry = check_documents(doc_statuses)
            # do something with failed docs

    elif translation_details.status in ["Failed", "ValidationFailed"]:
        if translation_details.error:
            print("Translation job failed: {}: {}".format(translation_details.error.code, translation_details.error.message))
        docs_to_retry = check_documents(doc_statuses)
        # do something with failed docs
        exit(1)


def check_documents(doc_statuses):
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
    return docs_to_retry


if __name__ == '__main__':
    sample_batch_translation()
