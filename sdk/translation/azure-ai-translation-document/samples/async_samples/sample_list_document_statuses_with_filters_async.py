# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_list_document_statuses_with_filters_async.py

DESCRIPTION:
    This sample demonstrates how to list all the documents in a translation operation for the resource
    using different kind of filters/sorting/paging options.

    To set up your containers for translation and generate SAS tokens to your containers (or files)
    with the appropriate permissions, see the README.

USAGE:
    python sample_list_document_statuses_with_filters_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_DOCUMENT_TRANSLATION_ENDPOINT - the endpoint to your Document Translation resource.
    2) AZURE_DOCUMENT_TRANSLATION_KEY - your Document Translation API key.
    3) TRANSLATION_ID - The ID of the translation operation
"""

import os
import asyncio

async def sample_list_document_statuses_with_filters_async():
    # import libraries
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.translation.document.aio import (
        DocumentTranslationClient,
    )
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
    statuses = ["Cancelled", "Failed"]
    order_by = ["createdDateTimeUtc desc"]
    results_per_page = 2
    skip = 3

    async with client:
        filtered_docs = client.list_all_document_statuses(
            translation_id,
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
        async for page in filtered_docs:
            async for doc in page:
                display_doc_info(doc)

def display_doc_info(document):
    print("Document ID: {}".format(document.id))
    print("Document status: {}".format(document.status))
    if document.status == "Succeeded":
        print("Source document location: {}".format(document.source_document_url))
        print("Translated document location: {}".format(document.translated_document_url))
        print("Translated to language: {}\n".format(document.translated_to))


async def main():
    await sample_list_document_statuses_with_filters_async()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
