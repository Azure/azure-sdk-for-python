# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import os
import asyncio


class BatchTranslationWithStorageSampleAsync(object):

    async def batch_translation_with_storage_async(self):
        # import libraries
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.textanalytics.aio import DocumentTranslationClient
        from azure.ai.documenttranslation import (
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

        # create service clients
        translation_client = DocumentTranslationClient(
            endpoint, AzureKeyCredential(key)
        )

        container_client = ContainerClient(
            source_storage_endpoint,
            container_name=source_storage_container_name,
            credential=source_storage_key
        )

        # upload some document for translation
        with open("document.txt", "rb") as doc:
            container_client.upload_blob("document.txt", doc)

        # prepare translation job input
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
                source_language="en",
                targets=[
                    StorageTarget(
                        target_url=target_container_url,
                        language="es"
                    )
                ],
                prefix="document"
            )
        ]

        # run job
        async with translation_client:
            job_detail = await translation_client.create_translation_job(batch)
            job_result = await translation_client.wait_until_done(job_detail.id)

            # poll status result
            if job_result.status == "Succeeded":
                print("We translated our documents!")
                if job_result.documents_failed_count > 0:
                    check_documents(translation_client, job_result.id)

            if job_result.status in ["Failed", "ValidationFailed"]:
                if job_result.error:
                    print("Translation job failed: {}: {}".format(job_result.error.code, job_result.error.message))
                check_documents(translation_client, job_result.id)
                exit(1)

            # store result documents
            container_client = ContainerClient(
                target_storage_endpoint,
                container_name=target_storage_container_name,
                credential=target_storage_key
            )

            target_container_client = container_client.from_container_url(target_container_url)

            with open("translated.txt", "wb") as my_blob:
                download_stream = target_container_client.download_blob("document.txt")
                my_blob.write(download_stream.readall())


    def check_documents(self, client, job_id):
        from azure.core.exceptions import ResourceNotFoundError

        try:
            doc_statuses = client.list_documents_statuses(job_id)  # type: ItemPaged[DocumentStatusDetail]
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

async def main():
    sample = BatchTranslationWithStorageSampleAsync()
    await sample.batch_translation_with_storage_async()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
