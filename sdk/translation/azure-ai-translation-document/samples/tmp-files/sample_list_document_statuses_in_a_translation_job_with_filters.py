# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_list_document_statuses_in_a_translation_job_with_filters.py

DESCRIPTION:
    This sample demonstrates how to list all the docs in some translation job for the resource 
    using different kind of filters/sorting/paging options

    To set up your containers for translation and generate SAS tokens to your containers (or files)
    with the appropriate permissions, see the README.

USAGE:
    python sample_list_document_statuses_in_a_translation_job_with_filters.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_DOCUMENT_TRANSLATION_ENDPOINT - the endpoint to your Document Translation resource.
    2) AZURE_DOCUMENT_TRANSLATION_KEY - your Document Translation API key.
"""

def sample_list_document_statuses_in_a_translation_job_with_filters(self, client):
    # import libraries
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.translation.document import (
        DocumentTranslationClient,
    )
    import os
    from datetime import datetime
    import uuid

    # obtain client secrets
    endpoint = os.environ["AZURE_DOCUMENT_TRANSLATION_ENDPOINT"]
    key = os.environ["AZURE_DOCUMENT_TRANSLATION_KEY"]

    # authorize client
    client = DocumentTranslationClient(endpoint, AzureKeyCredential(key))

    # set your filters
    job_id = str(uuid.uuid4()) # this should be the id for the job you'd like to list docs for!
    start = datetime(2021, 4, 12)
    end = datetime(2021, 4, 14)
    statuses = ["Cancelled", "Failed"]
    order_by = ["createdDateTimeUtc desc"]
    results_per_page = 2
    skip = 3
    
    # list jobs
    filtered_docs = client.list_all_document_statuses(
        job_id,
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
    for page in filtered_docs:
        for job in page:
            display_doc_info(job)

def display_doc_info(job):
    # print("Job ID: {}".format(job.id))
    # print("Job status: {}".format(job.status))
    # print("Job created on: {}".format(job.created_on))
    # print("Job last updated on: {}".format(job.last_updated_on))
    # print("Total number of translations on documents: {}".format(job.documents_total_count))
    # print("Total number of characters charged: {}".format(job.total_characters_charged))
    # print("\nOf total documents...")
    # print("{} failed".format(job.documents_failed_count))
    # print("{} succeeded".format(job.documents_succeeded_count))
    # print("{} cancelled\n".format(job.documents_cancelled_count))


if __name__ == '__main__':
    sample_list_document_statuses_in_a_translation_job_with_filters()
