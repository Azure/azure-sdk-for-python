# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: list_translations_async.py

DESCRIPTION:
    This sample demonstrates how to list all the submitted translation operations for the resource.

    To set up your containers for translation and generate SAS tokens to your containers (or files)
    with the appropriate permissions, see the README.

USAGE:
    python list_translations_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_DOCUMENT_TRANSLATION_ENDPOINT - the endpoint to your Document Translation resource.
    2) AZURE_DOCUMENT_TRANSLATION_KEY - your Document Translation API key.
"""

import asyncio


async def sample_list_translations_async():
    import os

    # [START list_translations_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.translation.document.aio import DocumentTranslationClient

    endpoint = os.environ["AZURE_DOCUMENT_TRANSLATION_ENDPOINT"]
    key = os.environ["AZURE_DOCUMENT_TRANSLATION_KEY"]

    client = DocumentTranslationClient(endpoint, AzureKeyCredential(key))
    async with client:
        operations = client.list_translation_statuses()

        async for operation in operations:
            print(f"ID: {operation.id}")
            print(f"Status: {operation.status}")
            print(f"Created on: {operation.created_on}")
            print(f"Last updated on: {operation.last_updated_on}")
            print(f"Total number of operations on documents: {operation.documents_total_count}")
            print(f"Total number of characters charged: {operation.total_characters_charged}")

            print("\nOf total documents...")
            print(f"{operation.documents_failed_count} failed")
            print(f"{operation.documents_succeeded_count} succeeded")
            print(f"{operation.documents_canceled_count} canceled\n")
    # [END list_translations_async]


async def main():
    await sample_list_translations_async()


if __name__ == "__main__":
    asyncio.run(main())
