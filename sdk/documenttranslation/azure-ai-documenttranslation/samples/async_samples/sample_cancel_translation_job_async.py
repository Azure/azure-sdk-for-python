# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import os
import asyncio

class CancelTranslationJobSampleAsync(object):

    async def cancel_translation_job_async(self):
        # import libraries
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.textanalytics.aio import DocumentTranslationClient
        from azure.ai.documenttranslation import (
            BatchDocumentInput,
            StorageTarget
        )

        # get service secrets
        endpoint = os.environ["AZURE_DOCUMENT_TRANSLATION_ENDPOINT"]
        key = os.environ["AZURE_DOCUMENT_TRANSLATION_KEY"]
        source_container_url = os.environ["AZURE_SOURCE_CONTAINER_URL"]
        target_container_url_es = os.environ["AZURE_TARGET_CONTAINER_URL_ES"]

        # prepare translation job input
        batch = [
            BatchDocumentInput(
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

        # create translation client
        client = DocumentTranslationClient(endpoint, AzureKeyCredential(key))

        # run job
        async with client:
            job_detail = await client.create_translation_job(batch)

            print("Job initial status: {}".format(job_detail.status))
            print("Number of translations on documents: {}".format(job_detail.documents_total_count))

            await client.cancel_job(job_detail.id)
            job_detail = client.get_job_status(job_detail.id)  # type: JobStatusDetail

            if job_detail.status in ["Cancelled", "Cancelling"]:
                print("We cancelled job with ID: {}".format(job_detail.id))


async def main():
    sample = CancelTranslationJobSampleAsync()
    await sample.cancel_translation_job_async()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())


