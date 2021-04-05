# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: list_all_submitted_jobs_async.py

DESCRIPTION:
    This sample demonstrates how to list all the submitted translation jobs for the resource and
    wait until done on any jobs that are still running.

    To set up your containers for translation and generate SAS tokens to your containers (or files)
    with the appropriate permissions, see the README.

USAGE:
    python list_all_submitted_jobs_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_DOCUMENT_TRANSLATION_ENDPOINT - the endpoint to your Document Translation resource.
    2) AZURE_DOCUMENT_TRANSLATION_KEY - your Document Translation API key.
"""

import asyncio


async def sample_list_all_submitted_jobs_async():
    import os
    # [START list_all_jobs_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.translation.document.aio import DocumentTranslationClient

    endpoint = os.environ["AZURE_DOCUMENT_TRANSLATION_ENDPOINT"]
    key = os.environ["AZURE_DOCUMENT_TRANSLATION_KEY"]

    client = DocumentTranslationClient(endpoint, AzureKeyCredential(key))
    async with client:
        translation_jobs = client.list_submitted_jobs()  # type: AsyncItemPaged[JobStatusResult]

        async for job in translation_jobs:
            if job.status == "Running":
                job = await client.wait_until_done(job.id)

            print("Job ID: {}".format(job.id))
            print("Job status: {}".format(job.status))
            print("Job created on: {}".format(job.created_on))
            print("Job last updated on: {}".format(job.last_updated_on))
            print("Total number of translations on documents: {}".format(job.documents_total_count))
            print("Total number of characters charged: {}".format(job.total_characters_charged))

            print("\nOf total documents...")
            print("{} failed".format(job.documents_failed_count))
            print("{} succeeded".format(job.documents_succeeded_count))
            print("{} cancelled\n".format(job.documents_cancelled_count))
    # [END list_all_jobs_async]


async def main():
    await sample_list_all_submitted_jobs_async()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
