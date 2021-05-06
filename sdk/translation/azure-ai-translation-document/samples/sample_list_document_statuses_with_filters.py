# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_list_document_statuses_with_filters.py

DESCRIPTION:
    This sample demonstrates how to list all the docs in some translation job for the resource 
    using different kind of filters/sorting/paging options

    To set up your containers for translation and generate SAS tokens to your containers (or files)
    with the appropriate permissions, see the README.

USAGE:
    python sample_list_document_statuses_with_filters.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_DOCUMENT_TRANSLATION_ENDPOINT - the endpoint to your Document Translation resource.
    2) AZURE_DOCUMENT_TRANSLATION_KEY - your Document Translation API key.
"""

def sample_list_document_statuses_with_filters(self, client):
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
    job_id = os.environ["JOB_ID"]  # this should be the id for the job you'd like to list docs for!

    # authorize client
    client = DocumentTranslationClient(endpoint, AzureKeyCredential(key))

    # set your filters
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
        translated_after=start,
        translated_before=end,
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

def display_doc_info(document):
    print("Document ID: {}".format(document.id))
    print("Document status: {}".format(document.status))
    if document.status == "Succeeded":
        print("Source document location: {}".format(document.source_document_url))
        print("Translated document location: {}".format(document.translated_document_url))
        print("Translated to language: {}\n".format(document.translate_to))

if __name__ == '__main__':
    sample_list_document_statuses_with_filters()
