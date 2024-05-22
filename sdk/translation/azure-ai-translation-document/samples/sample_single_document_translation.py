# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: synchronous_document_translation.py

DESCRIPTION:
    This sample demonstrates how to invoke synchronous document translation operations.

USAGE:
    python synchronous_document_translation.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_DOCUMENT_TRANSLATION_ENDPOINT - the endpoint to your Document Translation resource.
    2) AZURE_DOCUMENT_TRANSLATION_KEY - your Document Translation API key.
"""

import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.translation.document import SingleDocumentTranslationClient
from azure.ai.translation.document.models import DocumentTranslateContent


TEST_INPUT_FILE_NAME = os.path.abspath(
    os.path.join(os.path.abspath(__file__), "..", "../tests/TestData/test-input.txt")
)


def sample_single_document_translation():
    # [START synchronous_document_translation]
    endpoint = os.environ["AZURE_DOCUMENT_TRANSLATION_ENDPOINT"]
    key = os.environ["AZURE_DOCUMENT_TRANSLATION_KEY"]

    client = SingleDocumentTranslationClient(endpoint, AzureKeyCredential(key))
    target_languages = "hi"
    file_name = os.path.basename(TEST_INPUT_FILE_NAME)
    print(f"File for translation: {file_name}")
    file_type = "text/html"
    with open(TEST_INPUT_FILE_NAME, "r") as file:
        file_contents = file.read()

    document_content = (file_name, file_contents, file_type)
    document_translate_content = DocumentTranslateContent(document=document_content)

    response_stream = client.document_translate(body=document_translate_content, target_language=target_languages)
    translated_response = response_stream.decode("utf-8-sig")  # type: ignore[attr-defined]
    print(f"Translated response: {translated_response}")

    # [END synchronous_document_translation]


if __name__ == "__main__":
    sample_single_document_translation()
