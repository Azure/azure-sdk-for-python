# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_list_submitted_jobs_with_filters_async.py

DESCRIPTION:
    This sample demonstrates how to list all the submitted translation jobs for the resource 
    using differen kind of filters/sorting/paging options

    To set up your containers for translation and generate SAS tokens to your containers (or files)
    with the appropriate permissions, see the README.

USAGE:
    python sample_list_submitted_jobs_with_filters_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_DOCUMENT_TRANSLATION_ENDPOINT - the endpoint to your Document Translation resource.
    2) AZURE_DOCUMENT_TRANSLATION_KEY - your Document Translation API key.
"""

import os
import asyncio

async def sample_list_submitted_jobs_with_filters_async():
    # import libraries
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.translation.document.aio import DocumentTranslationClient

    from datetime import datetime

    # obtain client secrets
    endpoint = os.environ["AZURE_DOCUMENT_TRANSLATION_ENDPOINT"]
    key = os.environ["AZURE_DOCUMENT_TRANSLATION_KEY"]

    # authorize client
    client = DocumentTranslationClient(endpoint, AzureKeyCredential(key))
    async with client:
        # set your filters
        start = datetime(2021, 4, 12)
        end = datetime(2021, 4, 14)
        statuses = ["Cancelled", "Failed"]
        order_by = ["createdDateTimeUtc desc"]
        results_per_page = 2
        skip = 3

        # list jobs
        submitted_jobs = client.list_submitted_jobs(
            # filters
            statuses=statuses,
            created_after=start,
            created_before=end,
            # ordering
            order_by=order_by,
            # paging
            skip=skip,
            results_per_page=results_per_page
        ).by_page()

        # check statuses
        async for page in submitted_jobs:
            async for job in page:
                display_job_info(job)


def display_job_info(job):
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


async def main():
    await sample_list_submitted_jobs_with_filters_async()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
