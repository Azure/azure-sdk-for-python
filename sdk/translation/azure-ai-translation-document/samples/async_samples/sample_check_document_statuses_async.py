# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_check_document_statuses_async.py

DESCRIPTION:
    This sample demonstrates how to begin translation and then monitor each document's status
    and progress.

    To set up your containers for translation and generate SAS tokens to your containers (or files)
    with the appropriate permissions, see the README.

USAGE:
    python sample_check_document_statuses_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_DOCUMENT_TRANSLATION_ENDPOINT - the endpoint to your Document Translation resource.
    2) AZURE_DOCUMENT_TRANSLATION_KEY - your Document Translation API key.
    3) AZURE_SOURCE_CONTAINER_URL - the container SAS URL to your source container which has the documents
        to be translated.
    4) AZURE_TARGET_CONTAINER_URL - the container SAS URL to your target container where the translated documents
        will be written.
"""

import asyncio


async def sample_document_status_checks_async():
    # [START list_document_statuses_async]
    import os
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.translation.document.aio import DocumentTranslationClient

    endpoint = os.environ["AZURE_DOCUMENT_TRANSLATION_ENDPOINT"]
    key = os.environ["AZURE_DOCUMENT_TRANSLATION_KEY"]
    source_container_url = os.environ["AZURE_SOURCE_CONTAINER_URL"]
    target_container_url = os.environ["AZURE_TARGET_CONTAINER_URL"]

    client = DocumentTranslationClient(endpoint, AzureKeyCredential(key))

    async with client:
        poller = await client.begin_translation(source_container_url, target_container_url, "es")

        completed_docs = []
        while poller.status() in ["Running", "NotStarted"]:
            await asyncio.sleep(30)

            doc_statuses = client.list_document_statuses(poller.id)
            async for document in doc_statuses:
                if document.id not in completed_docs:
                    if document.status == "Succeeded":
                        print(f"Document at {document.source_document_url} was translated to {document.translated_to} "
                              f"language. You can find translated document at {document.translated_document_url}")
                        completed_docs.append(document.id)
                    if document.status == "Failed":
                        print(f"Document at {document.source_document_url} failed translation. "
                              f"Error Code: {document.error.code}, Message: {document.error.message}")
                        completed_docs.append(document.id)
                    if document.status == "Running":
                        print(f"Document ID: {document.id}, translation progress is "
                              f"{document.translation_progress * 100} percent")

        print("\nTranslation completed.")
    # [END list_document_statuses_async]


async def main():
    await sample_document_status_checks_async()

if __name__ == '__main__':
    asyncio.run(main())
