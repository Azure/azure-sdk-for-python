# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------


def sample_list_all_jobs():
    import os
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.documenttranslation import (
        DocumentTranslationClient,
    )

    endpoint = os.environ["AZURE_DOCUMENT_TRANSLATION_ENDPOINT"]
    key = os.environ["AZURE_DOCUMENT_TRANSLATION_KEY"]

    client = DocumentTranslationClient(endpoint, AzureKeyCredential(key))
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
