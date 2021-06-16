# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_list_translations_with_filters_async.py

DESCRIPTION:
    This sample demonstrates how to list all the submitted translation operations for the resource
    using different kind of filters/sorting/paging options.

    To set up your containers for translation and generate SAS tokens to your containers (or files)
    with the appropriate permissions, see the README.

USAGE:
    python sample_list_translations_with_filters_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_DOCUMENT_TRANSLATION_ENDPOINT - the endpoint to your Document Translation resource.
    2) AZURE_DOCUMENT_TRANSLATION_KEY - your Document Translation API key.
"""

import os
import asyncio

async def sample_list_translations_with_filters_async():
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

        # list translation operations
        submitted_translations = client.list_all_translation_statuses(
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
        async for page in submitted_translations:
            async for translation in page:
                display_translation_info(translation)


def display_translation_info(translation):
    print("ID: {}".format(translation.id))
    print("Status: {}".format(translation.status))
    print("Created on: {}".format(translation.created_on))
    print("Last updated on: {}".format(translation.last_updated_on))
    print("Total number of translations on documents: {}".format(translation.documents_total_count))
    print("Total number of characters charged: {}".format(translation.total_characters_charged))
    print("\nOf total documents...")
    print("{} failed".format(translation.documents_failed_count))
    print("{} succeeded".format(translation.documents_succeeded_count))
    print("{} cancelled\n".format(translation.documents_cancelled_count))


async def main():
    await sample_list_translations_with_filters_async()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
