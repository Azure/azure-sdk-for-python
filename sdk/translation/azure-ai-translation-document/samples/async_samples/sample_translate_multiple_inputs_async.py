# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_translate_multiple_inputs_async.py

DESCRIPTION:
    This sample demonstrates how to begin translating with documents in multiple source containers to
    multiple target containers in different languages.

    To set up your containers for translation and generate SAS tokens to your containers (or files)
    with the appropriate permissions, see the README.

USAGE:
    python sample_translate_multiple_inputs_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_DOCUMENT_TRANSLATION_ENDPOINT - the endpoint to your Document Translation resource.
    2) AZURE_DOCUMENT_TRANSLATION_KEY - your Document Translation API key.
    3) AZURE_SOURCE_CONTAINER_URL_1 - the first container SAS URL to your source container which has the documents
        to be translated.
    4) AZURE_SOURCE_CONTAINER_URL_2 - the second container SAS URL to your source container which has the documents
        to be translated.
    5) AZURE_TARGET_CONTAINER_URL_FR - the container SAS URL to your target container where the translated documents
        will be written in French.
    6) AZURE_TARGET_CONTAINER_URL_AR - the container SAS URL to your target container where the translated documents
        will be written in Arabic.
    7) AZURE_TARGET_CONTAINER_URL_ES - the container SAS URL to your target container where the translated documents
        will be written in Spanish.
"""

import asyncio


async def sample_multiple_translation_async():
    import os
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.translation.document.aio import DocumentTranslationClient
    from azure.ai.translation.document import DocumentTranslationInput, TranslationTarget

    endpoint = os.environ["AZURE_DOCUMENT_TRANSLATION_ENDPOINT"]
    key = os.environ["AZURE_DOCUMENT_TRANSLATION_KEY"]
    source_container_url_1 = os.environ["AZURE_SOURCE_CONTAINER_URL_1"]
    source_container_url_2 = os.environ["AZURE_SOURCE_CONTAINER_URL_2"]
    target_container_url_fr = os.environ["AZURE_TARGET_CONTAINER_URL_FR"]
    target_container_url_ar = os.environ["AZURE_TARGET_CONTAINER_URL_AR"]
    target_container_url_es = os.environ["AZURE_TARGET_CONTAINER_URL_ES"]

    client = DocumentTranslationClient(endpoint, AzureKeyCredential(key))

    async with client:
        poller = await client.begin_translation(
            inputs=[
                DocumentTranslationInput(
                    source_url=source_container_url_1,
                    targets=[
                        TranslationTarget(target_url=target_container_url_fr, language="fr"),
                        TranslationTarget(target_url=target_container_url_ar, language="ar"),
                    ],
                ),
                DocumentTranslationInput(
                    source_url=source_container_url_2,
                    targets=[TranslationTarget(target_url=target_container_url_es, language="es")],
                ),
            ]
        )
        result = await poller.result()

        print(f"Status: {poller.status()}")
        print(f"Created on: {poller.details.created_on}")
        print(f"Last updated on: {poller.details.last_updated_on}")
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
    await sample_multiple_translation_async()


if __name__ == "__main__":
    asyncio.run(main())
