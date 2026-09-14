# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_translation_with_image_translation_async.py

DESCRIPTION:
    This sample demonstrates how to start a batch translation that also translates text
    embedded within images in your documents by enabling `translate_text_within_image`.
    When enabled, each document's status reports image scan usage details.

    To set up your containers for translation and generate SAS tokens to your containers (or files)
    with the appropriate permissions, see the README.

USAGE:
    python sample_translation_with_image_translation_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_DOCUMENT_TRANSLATION_ENDPOINT - the endpoint to your Document Translation resource.
    2) AZURE_DOCUMENT_TRANSLATION_KEY - your Document Translation API key.
    3) AZURE_SOURCE_CONTAINER_URL - the container SAS URL to your source container which has the documents
        to be translated.
    4) AZURE_TARGET_CONTAINER_URL - the container SAS URL to your target container where the translated documents
        will be written.
"""

import asyncio


async def sample_translation_with_image_translation_async():
    import os
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.translation.document.aio import DocumentTranslationClient

    endpoint = os.environ["AZURE_DOCUMENT_TRANSLATION_ENDPOINT"]
    key = os.environ["AZURE_DOCUMENT_TRANSLATION_KEY"]
    source_container_url = os.environ["AZURE_SOURCE_CONTAINER_URL"]
    target_container_url = os.environ["AZURE_TARGET_CONTAINER_URL"]

    client = DocumentTranslationClient(endpoint, AzureKeyCredential(key))

    async with client:
        # Enable translation of text embedded within images for the batch.
        poller = await client.begin_translation(
            source_container_url,
            target_container_url,
            "es",
            translate_text_within_image=True,
        )
        result = await poller.result()

        print(f"Operation status: {poller.details.status}")
        print(f"Total number of translations on documents: {poller.details.documents_total_count}")

        async for document in result:
            print(f"Document ID: {document.id}")
            print(f"Document status: {document.status}")
            if document.status == "Succeeded":
                print(f"Translated document location: {document.translated_document_url}")
                print(f"Characters charged: {document.characters_charged}")
                # Image scan usage is reported when image translation is enabled.
                print(f"Total image scans succeeded: {document.total_image_scans_succeeded}")
                print(f"Total image scans failed: {document.total_image_scans_failed}")
                print(f"Images charged: {document.images_charged}")
                print(f"Characters detected within images: {document.image_characters_detected}\n")
            elif document.error:
                print(f"Error Code: {document.error.code}, Message: {document.error.message}\n")


async def main():
    await sample_translation_with_image_translation_async()


if __name__ == "__main__":
    asyncio.run(main())
