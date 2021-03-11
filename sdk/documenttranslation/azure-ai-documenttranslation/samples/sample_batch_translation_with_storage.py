# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------


def sample_batch_translation_with_storage():
    # import libraries
    import os
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.documenttranslation import (
        DocumentTranslationClient,
        BatchDocumentInput,
        StorageTarget
    )
    from azure.storage.blob import ContainerClient, generate_container_sas, ContainerSasPermissions

    # get service secrets
    endpoint = os.environ["AZURE_DOCUMENT_TRANSLATION_ENDPOINT"]
    key = os.environ["AZURE_DOCUMENT_TRANSLATION_KEY"]
    source_storage_endpoint = os.environ["AZURE_STORAGE_SOURCE_ENDPOINT"]
    source_storage_account_name = os.environ["AZURE_STORAGE_SOURCE_ACCOUNT_NAME"]
    source_storage_container_name = os.environ["AZURE_STORAGE_SOURCE_CONTAINER_NAME"]
    source_storage_key = os.environ["AZURE_STORAGE_SOURCE_KEY"]
    target_storage_endpoint = os.environ["AZURE_STORAGE_TARGET_ENDPOINT"]
    target_storage_account_name = os.environ["AZURE_STORAGE_TARGET_ACCOUNT_NAME"]
    target_storage_container_name = os.environ["AZURE_STORAGE_TARGET_CONTAINER_NAME"]
    target_storage_key = os.environ["AZURE_STORAGE_TARGET_KEY"]

    # create translation client
    translation_client = DocumentTranslationClient(
        endpoint, AzureKeyCredential(key)
    )

    # upload some document to source container
    container_client = ContainerClient(
        source_storage_endpoint,
        container_name=source_storage_container_name,
        credential=source_storage_key
    )

    with open("document.txt", "rb") as doc:
        container_client.upload_blob("document.txt", doc)

    # prepare translation input
    source_container_sas = generate_container_sas(
        account_name=source_storage_account_name,
        container_name=source_storage_container_name,
        account_key=source_storage_key,
        permission=ContainerSasPermissions.from_string("rl")
    )

    target_container_sas = generate_container_sas(
        account_name=target_storage_account_name,
        container_name=target_storage_container_name,
        account_key=target_storage_key,
        permission=ContainerSasPermissions.from_string("rlwd")
    )

    source_container_url = source_storage_endpoint + "/" + source_storage_container_name + "?" + source_container_sas
    target_container_url = target_storage_endpoint + "/" + target_storage_container_name + "?" + target_container_sas

    batch = [
        BatchDocumentInput(
            source_url=source_container_url,
            targets=[
                StorageTarget(
                    target_url=target_container_url,
                    language="es"
                )
            ],
            prefix="document"
        )
    ]

    # submit docs for translation
    poller = translation_client.begin_translation(batch) # type: DocumentTranslationPoller[ItemPaged[DocumentStatusDetail]]

    # initial status
    translation_details = poller.details # type: TranslationStatusDetail
    print("Translation initial status: {}".format(translation_details.status))
    print("Number of translations on documents: {}".format(translation_details.documents_total_count))

    # get final status
    doc_statuses = poller.result()  # type: ItemPaged[DocumentStatusDetail]
    translation_result = poller.details # type: TranslationStatusDetail
    if translation_result.status == "Succeeded":
        print("We translated our documents!")
        if translation_result.documents_failed_count > 0:
            docs_to_retry = check_documents(doc_statuses)
            # do something with failed docs

    elif translation_result.status in ["Failed", "ValidationFailed"]:
        if translation_result.error:
            print("Translation job failed: {}: {}".format(translation_result.error.code, translation_result.error.message))
        docs_to_retry = check_documents(doc_statuses)
        # do something with failed docs
        exit(1)


    # write translated document to desired storage
    container_client = ContainerClient(
        target_storage_endpoint,
        container_name=target_storage_container_name,
        credential=target_storage_key
    )

    target_container_client = container_client.from_container_url(target_container_url)

    with open("translated.txt", "wb") as my_blob:
        download_stream = target_container_client.download_blob("document.txt")
        my_blob.write(download_stream.readall())


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
    sample_batch_translation_with_storage()
