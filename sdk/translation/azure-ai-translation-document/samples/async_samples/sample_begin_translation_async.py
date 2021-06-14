# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_begin_translation_async.py

DESCRIPTION:
    This sample demonstrates how to translate documents in your Azure Blob Storage container.

    To set up your containers for translation and generate SAS tokens to your containers (or files)
    with the appropriate permissions, see the README.

USAGE:
    python sample_begin_translation_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_DOCUMENT_TRANSLATION_ENDPOINT - the endpoint to your Document Translation resource.
    2) AZURE_DOCUMENT_TRANSLATION_KEY - your Document Translation API key.
    3) AZURE_SOURCE_CONTAINER_URL - the container SAS URL to your source container which has the documents
        to be translated.
    4) AZURE_TARGET_CONTAINER_URL - the container SAS URL to your target container where the translated documents
        will be written.
"""


import asyncio


async def sample_translation_async():
    # [START begin_translation_async]
    import os
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.translation.document.aio import DocumentTranslationClient

    endpoint = os.environ["AZURE_DOCUMENT_TRANSLATION_ENDPOINT"]
    key = os.environ["AZURE_DOCUMENT_TRANSLATION_KEY"]
    source_container_url = os.environ["AZURE_SOURCE_CONTAINER_URL"]
    target_container_url = os.environ["AZURE_TARGET_CONTAINER_URL"]

    client = DocumentTranslationClient(endpoint, AzureKeyCredential(key))

    async with client:
        poller = await client.begin_translation(source_container_url, target_container_url, "fr")
        result = await poller.result()

        print("Status: {}".format(poller.status()))
        print("Created on: {}".format(poller.details.created_on))
        print("Last updated on: {}".format(poller.details.last_updated_on))
        print("Total number of translations on documents: {}".format(poller.details.documents_total_count))

        print("\nOf total documents...")
        print("{} failed".format(poller.details.documents_failed_count))
        print("{} succeeded".format(poller.details.documents_succeeded_count))

        async for document in result:
            print("Document ID: {}".format(document.id))
            print("Document status: {}".format(document.status))
            if document.status == "Succeeded":
                print("Source document location: {}".format(document.source_document_url))
                print("Translated document location: {}".format(document.translated_document_url))
                print("Translated to language: {}\n".format(document.translated_to))
            else:
                print("Error Code: {}, Message: {}\n".format(document.error.code, document.error.message))
    # [END begin_translation_async]


async def main():
    await sample_translation_async()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
