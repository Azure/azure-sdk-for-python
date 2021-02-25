# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import os
import asyncio

class ListAllSubmittedJobsSampleAsync(object):

    def list_all_submitted_jobs():
        # import libraries
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.textanalytics.aio import DocumentTranslationClient

        # get service secrets
        endpoint = os.environ["AZURE_DOCUMENT_TRANSLATION_ENDPOINT"]
        key = os.environ["AZURE_DOCUMENT_TRANSLATION_KEY"]

        # create translation client
        client = DocumentTranslationClient(endpoint, AzureKeyCredential(key))

        # list submitted jobs
        jobs = client.list_submitted_jobs()

        for job in jobs:
            print("Job ID: {}".format(job.id))
            print("Job status: {}".format(job.status))
            print("Job created on: {}".format(job.created_on))
            print("Job last updated on: {}".format(job.last_updated_on))
            print("Total number of translations on documents: {}".format(job.documents_total_count))

            print("Of total documents...")
            print("{} failed".format(job.documents_failed_count))
            print("{} succeeded".format(job.documents_succeeded_count))
            print("{} in progress".format(job.documents_in_progress_count))
            print("{} not yet started".format(job.documents_not_yet_started_count))
            print("{} cancelled".format(job.documents_cancelled_count))


async def main():
    sample = ListAllSubmittedJobsSampleAsync()
    await sample.list_all_submitted_jobs()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())