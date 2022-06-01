# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_list_document_statuses_with_filters.py

DESCRIPTION:
    This sample demonstrates how to list all the documents in a translation operation for the resource
    using different kind of filters/sorting/paging options.

    To set up your containers for translation and generate SAS tokens to your containers (or files)
    with the appropriate permissions, see the README.

USAGE:
    python sample_list_document_statuses_with_filters.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_DOCUMENT_TRANSLATION_ENDPOINT - the endpoint to your Document Translation resource.
    2) AZURE_DOCUMENT_TRANSLATION_KEY - your Document Translation API key.
    3) TRANSLATION_ID - The ID of the translation operation
"""

def sample_list_document_statuses_with_filters():
    # import libraries
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.translation.document import (
        DocumentTranslationClient,
    )
    import os
    from datetime import datetime

    # obtain client secrets
    endpoint = os.environ["AZURE_DOCUMENT_TRANSLATION_ENDPOINT"]
    key = os.environ["AZURE_DOCUMENT_TRANSLATION_KEY"]
    translation_id = os.environ["TRANSLATION_ID"]  # this should be the id for the translation operation you'd like to list docs for!

    # authorize client
    client = DocumentTranslationClient(endpoint, AzureKeyCredential(key))

    # set your filters
    '''
        Note:
            these are just sample values for the filters!
            please comment/uncomment/change what you are interested in using.
    '''
    start = datetime(2021, 4, 12)
    end = datetime(2021, 4, 14)
    statuses = ["Canceled", "Failed"]
    order_by = ["created_on desc"]
    results_per_page = 2
    skip = 3

    filtered_docs = client.list_document_statuses(
        translation_id,
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
        for doc in page:
            display_doc_info(doc)

def display_doc_info(document):
    print(f"Document ID: {document.id}")
    print(f"Document status: {document.status}")
    if document.status == "Succeeded":
        print(f"Source document location: {document.source_document_url}")
        print(f"Translated document location: {document.translated_document_url}")
        print(f"Translated to language: {document.translated_to}\n")

if __name__ == '__main__':
    sample_list_document_statuses_with_filters()
