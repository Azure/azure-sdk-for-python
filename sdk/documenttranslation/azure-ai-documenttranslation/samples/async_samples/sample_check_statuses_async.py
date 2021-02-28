# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import os
import asyncio
import time

class CheckStatusesSampleAsync(object):
        
    async def check_statuses_async(self):

        # import libraries
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.documenttranslation.aio import DocumentTranslationClient
        from azure.ai.documenttranslation import (
            BatchDocumentInput,
            StorageTarget
        )

        # get service secrets
        endpoint = os.environ["AZURE_DOCUMENT_TRANSLATION_ENDPOINT"]
        key = os.environ["AZURE_DOCUMENT_TRANSLATION_KEY"]
        source_container_url = os.environ["AZURE_SOURCE_CONTAINER_URL"]
        target_container_url_es = os.environ["AZURE_TARGET_CONTAINER_URL_ES"]
        target_container_url_fr = os.environ["AZURE_TARGET_CONTAINER_URL_FR"]

        # prepare translation input
        batch = [
            BatchDocumentInput(
                source_url=source_container_url,
                source_language="en",
                targets=[
                    StorageTarget(
                        target_url=target_container_url_es,
                        language="es"
                    ),
                    StorageTarget(
                        target_url=target_container_url_fr,
                        language="fr"
                    )
                ],
                storage_type="folder",
                prefix="document_2021"
            )
        ]
        
        # create translation client
        client = DocumentTranslationClient(endpoint, AzureKeyCredential(key))

        # run translation job
        async with client:
            job_detail = await client.create_translation_job(batch)
            while True:
                job_detail = await client.get_job_status(job_detail.id)  # type: JobStatusDetail
                if job_detail.status in ["NotStarted", "Running"]:
                    time.sleep(10)
                    continue

                if job_detail.status in ["Failed", "ValidationFailed"]:
                    if job_detail.error:
                        print("Translation job failed: {}: {}".format(job_detail.error.code, job_detail.error.message))
                    self.check_documents(client, job_detail.id)
                    exit(1)

                if job_detail.status == "Succeeded":
                    print("We translated our documents!")
                    if job_detail.documents_failed_count > 0:
                        self.check_documents(client, job_detail.id)
                    break


    def check_documents(self, client, job_id):
        from azure.core.exceptions import ResourceNotFoundError

        try:
            doc_statuses = client.list_documents_statuses(job_id)  # type: AsyncItemPaged[DocumentStatusDetail]
        except ResourceNotFoundError as err:
            print("Failed to process any documents in source/target container.")
            raise err

        docs_to_retry = []
        async for document in doc_statuses:
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
    sample = CheckStatusesSampleAsync()
    await sample.check_statuses_async()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())