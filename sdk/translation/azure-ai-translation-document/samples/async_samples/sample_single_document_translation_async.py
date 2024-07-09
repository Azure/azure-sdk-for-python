# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: synchronous_document_translation_async.py

DESCRIPTION:
    This sample demonstrates how to invoke synchronous document translation operations.

USAGE:
    python synchronous_document_translation_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_DOCUMENT_TRANSLATION_ENDPOINT - the endpoint to your Document Translation resource.
    2) AZURE_DOCUMENT_TRANSLATION_KEY - your Document Translation API key.
"""

import asyncio, os
from azure.core.credentials import AzureKeyCredential
from azure.ai.translation.document.aio import SingleDocumentTranslationClient
from azure.ai.translation.document.models import DocumentTranslateContent


async def sample_single_document_translation_async():
    # [START synchronous_document_translation_async]
    endpoint = os.environ["AZURE_DOCUMENT_TRANSLATION_ENDPOINT"]
    key = os.environ["AZURE_DOCUMENT_TRANSLATION_KEY"]

    client = SingleDocumentTranslationClient(endpoint, AzureKeyCredential(key))
    target_languages = "hi"

    # Get the current directory of the script
    current_directory = os.path.abspath(__file__)

    # Navigate up three levels
    parent_directory = os.path.dirname(os.path.dirname(os.path.dirname(current_directory)))

    # Construct the path to the desired file
    file_path = os.path.join(parent_directory, "tests", "TestData", "test-input.txt")
    file_name = os.path.basename(file_path)
    file_type = "text/html"
    with open(file_path, "r") as file:
        file_contents = file.read()

    document_content = (file_name, file_contents, file_type)
    document_translate_content = DocumentTranslateContent(document=document_content)

    async with client:
        response_stream = await client.document_translate(
            body=document_translate_content, target_language=target_languages
        )
    translated_response = response_stream.decode("utf-8-sig")  # type: ignore[attr-defined]
    print(f"Translated response: {translated_response}")

    # [END synchronous_document_translation_async]


async def main():
    await sample_single_document_translation_async()


if __name__ == "__main__":
    asyncio.run(main())
