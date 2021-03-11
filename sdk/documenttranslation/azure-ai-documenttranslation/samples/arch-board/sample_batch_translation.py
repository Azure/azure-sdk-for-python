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
        StorageTarget,
    )

    # get service secrets
    endpoint = os.environ["AZURE_DOCUMENT_TRANSLATION_ENDPOINT"]
    key = os.environ["AZURE_DOCUMENT_TRANSLATION_KEY"]
    source_container_url_en = os.environ["AZURE_SOURCE_CONTAINER_URL_EN"]
    target_container_url_es = os.environ["AZURE_TARGET_CONTAINER_URL_ES"]
    target_container_url_fr = os.environ["AZURE_TARGET_CONTAINER_URL_FR"]

    # create translation client
    client = DocumentTranslationClient(endpoint, AzureKeyCredential(key))

    # submit documents for translation
    operation = client.begin_translation(
        [
            BatchDocumentInput(
                source_url=source_container_url_en,
                targets=[
                    StorageTarget(target_url=target_container_url_es, language="es"),
                    StorageTarget(target_url=target_container_url_fr, language="fr"),
                ],
            )
        ]
    )  # type: DocumentTranslationPoller[ItemPaged[DocumentStatusDetail]]

    # get final status
    doc_statuses = operation.result()  # type: ItemPaged[DocumentStatusDetail]
    translation_details = operation.details # type: TranslationStatusDetail

    # print status
    print("Translation status: {}".format(translation_details.status))
    print("Translation created on: {}".format(translation_details.created_on))
    print("Translation last updated on: {}".format(translation_details.last_updated_on))
    print("Total number of translations on documents: {}".format(translation_details.documents_total_count))

    print("Of total documents...")
    print("{} failed".format(translation_details.documents_failed_count))
    print("{} succeeded".format(translation_details.documents_succeeded_count))
    print("{} in progress".format(translation_details.documents_in_progress_count))
    print("{} not yet started".format(translation_details.documents_not_yet_started_count))
    print("{} cancelled".format(translation_details.documents_cancelled_count))

    for document in doc_statuses:
        print("Document with ID: {} has status: {}".format(document.id, document.status))
        if document.status == "Succeeded":
            print("Document location: {}".format(document.url))
            print("Translated to langauge: {}".format(document.translate_to))
        else:
            print("Error Code: {}, Message: {}".format(document.error.code, document.error.message))



if __name__ == '__main__':
    sample_batch_translation()
