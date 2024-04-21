# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_translation_with_custom_model_async.py

DESCRIPTION:
    This sample demonstrates how to create a translation operation and apply a custom translation model.

    To set up your containers for translation and generate SAS tokens to your containers (or files)
    with the appropriate permissions, see the README.

USAGE:
    python sample_translation_with_custom_model_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_DOCUMENT_TRANSLATION_ENDPOINT - the endpoint to your Document Translation resource.
    2) AZURE_DOCUMENT_TRANSLATION_KEY - your Document Translation API key.
    3) AZURE_SOURCE_CONTAINER_URL - the container SAS URL to your source container which has the documents
        to be translated.
    4) AZURE_TARGET_CONTAINER_URL - the container SAS URL to your target container where the translated documents
        will be written.
    5) AZURE_CUSTOM_MODEL_ID - the URL to your Azure custom translation model.
"""

import asyncio


async def sample_translation_with_custom_model_async():
    import os
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.translation.document.aio import DocumentTranslationClient

    endpoint = os.environ["AZURE_DOCUMENT_TRANSLATION_ENDPOINT"]
    key = os.environ["AZURE_DOCUMENT_TRANSLATION_KEY"]
    source_container_url = os.environ["AZURE_SOURCE_CONTAINER_URL"]
    target_container_url = os.environ["AZURE_TARGET_CONTAINER_URL"]
    custom_model_id = os.environ["AZURE_CUSTOM_MODEL_ID"]

    client = DocumentTranslationClient(endpoint, AzureKeyCredential(key))

    async with client:
        poller = await client.begin_translation(
            source_container_url, target_container_url, "es", category_id=custom_model_id
        )
        result = await poller.result()

        print(f"Operation status: {poller.details.status}")
        print(f"Operation created on: {poller.details.created_on}")
        print(f"Operation last updated on: {poller.details.last_updated_on}")
        print(f"Total number of translations on documents: {poller.details.documents_total_count}")

        print("\nOf total documents...")
        print(f"{poller.details.documents_failed_count} failed")
        print(f"{poller.details.documents_succeeded_count} succeeded")

        async for document in result:
            print(f"Document ID: {document.id}")
            print(f"Document status: {document.status}")
            if document.status == "Succeeded":
                print(f"Source document location: {document.source_document_url}")
                print(f"Translated document location: {document.translated_document_url}")
                print(f"Translated to language: {document.translated_to}\n")
            elif document.error:
                print(f"Error Code: {document.error.code}, Message: {document.error.message}\n")


async def main():
    await sample_translation_with_custom_model_async()


if __name__ == "__main__":
    asyncio.run(main())
