# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_list_translations_with_filters.py

DESCRIPTION:
    This sample demonstrates how to list all the submitted translation operations for the resource
    using different kind of filters/sorting/paging options.

    To set up your containers for translation and generate SAS tokens to your containers (or files)
    with the appropriate permissions, see the README.

USAGE:
    python sample_list_translations_with_filters.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_DOCUMENT_TRANSLATION_ENDPOINT - the endpoint to your Document Translation resource.
    2) AZURE_DOCUMENT_TRANSLATION_KEY - your Document Translation API key.
"""



def sample_list_translations_with_filters():
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
    skip = 3

    # list translation operations
    submitted_translations = client.list_translation_statuses(
        # filters
        statuses=statuses,
        created_after=start,
        created_before=end,
        # ordering
        order_by=order_by,
        # paging
        skip=skip,
    ).by_page()

    # check statuses
    for page in submitted_translations:
        for translation in page:
            display_translation_info(translation)


def display_translation_info(translation):
    print(f"ID: {translation.id}")
    print(f"Status: {translation.status}")
    print(f"Created on: {translation.created_on}")
    print(f"Last updated on: {translation.last_updated_on}")
    print(f"Total number of translations on documents: {translation.documents_total_count}")
    print(f"Total number of characters charged: {translation.total_characters_charged}")
    print("\nOf total documents...")
    print(f"{translation.documents_failed_count} failed")
    print(f"{translation.documents_succeeded_count} succeeded")
    print(f"{translation.documents_canceled_count} canceled\n")


if __name__ == '__main__':
    sample_list_translations_with_filters()
