# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: list_all_translations_async.py

DESCRIPTION:
    This sample demonstrates how to list all the submitted translation operations for the resource.

    To set up your containers for translation and generate SAS tokens to your containers (or files)
    with the appropriate permissions, see the README.

USAGE:
    python list_all_translations_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_DOCUMENT_TRANSLATION_ENDPOINT - the endpoint to your Document Translation resource.
    2) AZURE_DOCUMENT_TRANSLATION_KEY - your Document Translation API key.
"""

import asyncio


async def sample_list_all_translations_async():
    import os
    # [START list_all_translations_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.translation.document.aio import DocumentTranslationClient

    endpoint = os.environ["AZURE_DOCUMENT_TRANSLATION_ENDPOINT"]
    key = os.environ["AZURE_DOCUMENT_TRANSLATION_KEY"]

    client = DocumentTranslationClient(endpoint, AzureKeyCredential(key))
    async with client:
        operations = client.list_all_translation_statuses()  # type: AsyncItemPaged[TranslationStatus]

        async for operation in operations:
            print("ID: {}".format(operation.id))
            print("Status: {}".format(operation.status))
            print("Created on: {}".format(operation.created_on))
            print("Last updated on: {}".format(operation.last_updated_on))
            print("Total number of operations on documents: {}".format(operation.documents_total_count))
            print("Total number of characters charged: {}".format(operation.total_characters_charged))

            print("\nOf total documents...")
            print("{} failed".format(operation.documents_failed_count))
            print("{} succeeded".format(operation.documents_succeeded_count))
            print("{} cancelled\n".format(operation.documents_cancelled_count))
    # [END list_all_translations_async]


async def main():
    await sample_list_all_translations_async()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
