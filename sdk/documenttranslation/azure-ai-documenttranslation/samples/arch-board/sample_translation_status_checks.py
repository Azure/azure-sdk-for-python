# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------


def sample_translation_status_checks():
    # import libraries
    import os
    import time
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
    target_container_url_es = os.environ["AZURE_TARGET_CONTAINER_URL_ES"]
    target_container_url_fr = os.environ["AZURE_TARGET_CONTAINER_URL_FR"]

    # create translation client
    client = DocumentTranslationClient(endpoint, AzureKeyCredential(key))

    # submit docs for translation
    operation = client.begin_translation(
        [
            BatchDocumentInput(
                source_url=source_container_url_en,
                targets=[
                    StorageTarget(target_url=target_container_url_es, language="es"),
                    StorageTarget(target_url=target_container_url_fr, language="fr")
                ]
            )
        ]
    )  # type: DocumentTranslationPoller[ItemPaged[DocumentStatusDetail]]

    # check result
    completed_docs = []
    running_state = ["NotStarted", "Running"]

    while operation.details.status in running_state:
        time.sleep(30)
        for doc in client.list_documents_statuses(operation.batch_id):
            if doc.id not in completed_docs and doc.status not in running_state:
                completed_docs.append(doc.id)
                print("Document at {} completed with status: {}".format(doc.url, doc.status))

    print("Translation batch completed.")

if __name__ == '__main__':
    sample_translation_status_checks()