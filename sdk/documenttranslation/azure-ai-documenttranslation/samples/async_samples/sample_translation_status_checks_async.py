# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import os
import asyncio
import time

class TranslationStatusChecksSampleAsync(object):
        
    async def translation_status_checks_async(self):

        # import libraries
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.documenttranslation.aio import DocumentTranslationClient
        from azure.ai.documenttranslation import (
            DocumentTranslationInput,
            TranslationTarget
        )

        # get service secrets
        endpoint = os.environ["AZURE_DOCUMENT_TRANSLATION_ENDPOINT"]
        key = os.environ["AZURE_DOCUMENT_TRANSLATION_KEY"]
        source_container_url = os.environ["AZURE_SOURCE_CONTAINER_URL"]
        target_container_url_es = os.environ["AZURE_TARGET_CONTAINER_URL_ES"]
        target_container_url_fr = os.environ["AZURE_TARGET_CONTAINER_URL_FR"]

        # prepare translation input
        translation_inputs = [
            DocumentTranslationInput(
                source_url=source_container_url,
                targets=[
                    TranslationTarget(
                        target_url=target_container_url_es,
                        language_code="es"
                    ),
                    TranslationTarget(
                        target_url=target_container_url_fr,
                        language_code="fr"
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
            job_detail = await client.create_translation_job(translation_inputs)
            while True:
                job_detail = await client.get_job_status(job_detail.id)  # type: JobStatusResult
                if job_detail.status in ["NotStarted", "Running"]:
                    await asyncio.sleep(30)
                    continue

                elif job_detail.status in ["Failed", "ValidationFailed"]:
                    if job_detail.error:
                        print("Translation job failed: {}: {}".format(job_detail.error.code, job_detail.error.message))
                    await self.check_documents(client, job_detail.id)
                    exit(1)

                elif job_detail.status == "Succeeded":
                    print("We translated our documents!")
                    if job_detail.documents_failed_count > 0:
                        await self.check_documents(client, job_detail.id)
                    break


    async def check_documents(self, client, job_id):
        from azure.core.exceptions import ResourceNotFoundError

        try:
            doc_statuses = client.list_all_document_statuses(job_id)  # type: AsyncItemPaged[DocumentStatusResult]
        except ResourceNotFoundError as err:
            print("Failed to process any documents in source/target container due to insufficient permissions.")
            raise err

        docs_to_retry = []
        async for document in doc_statuses:
            if document.status == "Failed":
                print("Document at {} failed to be translated to {} language".format(
                    document.translated_document_url, document.translate_to
                ))
                print("Document ID: {}, Error Code: {}, Message: {}".format(
                    document.id, document.error.code, document.error.message
                ))
                if document.translated_document_url not in docs_to_retry:
                    docs_to_retry.append(document.translated_document_url)


async def main():
    sample = TranslationStatusChecksSampleAsync()
    await sample.translation_status_checks_async()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())