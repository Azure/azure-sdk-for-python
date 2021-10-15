# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_translation_with_custom_model.py

DESCRIPTION:
    This sample demonstrates how to create a translation operation and apply a custom translation model.

    To set up your containers for translation and generate SAS tokens to your containers (or files)
    with the appropriate permissions, see the README.

USAGE:
    python sample_translation_with_custom_model.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_DOCUMENT_TRANSLATION_ENDPOINT - the endpoint to your Document Translation resource.
    2) AZURE_DOCUMENT_TRANSLATION_KEY - your Document Translation API key.
    3) AZURE_SOURCE_CONTAINER_URL - the container SAS URL to your source container which has the documents
        to be translated.
    4) AZURE_TARGET_CONTAINER_URL - the container SAS URL to your target container where the translated documents
        will be written.
    5) AZURE_CUSTOM_MODEL_ID - the URL to your Azure custom translation model.
"""


def sample_translation_with_custom_model():
    import os
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.translation.document import (
        DocumentTranslationClient
    )

    endpoint = os.environ["AZURE_DOCUMENT_TRANSLATION_ENDPOINT"]
    key = os.environ["AZURE_DOCUMENT_TRANSLATION_KEY"]
    source_container_url = os.environ["AZURE_SOURCE_CONTAINER_URL"]
    target_container_url = os.environ["AZURE_TARGET_CONTAINER_URL"]
    custom_model_id = os.environ["AZURE_CUSTOM_MODEL_ID"]

    client = DocumentTranslationClient(endpoint, AzureKeyCredential(key))

    poller = client.begin_translation(
        source_container_url,
        target_container_url,
        "es",
        category_id=custom_model_id
    )
    result = poller.result()

    print("Operation status: {}".format(result.status))
    print("Operation created on: {}".format(result.created_on))
    print("Operation last updated on: {}".format(result.last_updated_on))
    print("Total number of translations on documents: {}".format(result.documents_total_count))

    print("\nOf total documents...")
    print("{} failed".format(result.documents_failed_count))
    print("{} succeeded".format(result.documents_succeeded_count))

    doc_results = client.list_document_statuses(result.id)
    for document in doc_results:
        print("Document ID: {}".format(document.id))
        print("Document status: {}".format(document.status))
        if document.status == "Succeeded":
            print("Source document location: {}".format(document.source_document_url))
            print("Translated document location: {}".format(document.translated_document_url))
            print("Translated to language: {}\n".format(document.translate_to))
        else:
            print("Error Code: {}, Message: {}\n".format(document.error.code, document.error.message))


if __name__ == '__main__':
    sample_translation_with_custom_model()
