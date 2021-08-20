# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_translation_with_glossaries.py

DESCRIPTION:
    This sample demonstrates how to translate documents and apply custom glossaries to the translation.

    To set up your containers for translation and generate SAS tokens to your containers (or files)
    with the appropriate permissions, see the README.

USAGE:
    python sample_translation_with_glossaries.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_DOCUMENT_TRANSLATION_ENDPOINT - the endpoint to your Document Translation resource.
    2) AZURE_DOCUMENT_TRANSLATION_KEY - your Document Translation API key.
    3) AZURE_SOURCE_CONTAINER_URL - the container SAS URL to your source container which has the documents
        to be translated.
    4) AZURE_TARGET_CONTAINER_URL - the container SAS URL to your target container where the translated documents
        will be written.
    5) AZURE_TRANSLATION_GLOSSARY_URL - the SAS URL to your glossary file
"""


def sample_translation_with_glossaries():
    import os
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.translation.document import (
        DocumentTranslationClient,
        TranslationGlossary
    )

    endpoint = os.environ["AZURE_DOCUMENT_TRANSLATION_ENDPOINT"]
    key = os.environ["AZURE_DOCUMENT_TRANSLATION_KEY"]
    source_container_url = os.environ["AZURE_SOURCE_CONTAINER_URL"]
    target_container_url = os.environ["AZURE_TARGET_CONTAINER_URL"]
    glossary_url = os.environ["AZURE_TRANSLATION_GLOSSARY_URL"]

    client = DocumentTranslationClient(endpoint, AzureKeyCredential(key))

    poller = client.begin_translation(
        source_container_url,
        target_container_url,
        "es",
        glossaries=[TranslationGlossary(glossary_url=glossary_url, file_format="TSV")]
    )

    result = poller.result()

    print("Status: {}".format(poller.status()))
    print("Created on: {}".format(poller.details.created_on))
    print("Last updated on: {}".format(poller.details.last_updated_on))
    print("Total number of translations on documents: {}".format(poller.details.documents_total_count))

    print("\nOf total documents...")
    print("{} failed".format(poller.details.documents_failed_count))
    print("{} succeeded".format(poller.details.documents_succeeded_count))

    for document in result:
        print("Document ID: {}".format(document.id))
        print("Document status: {}".format(document.status))
        if document.status == "Succeeded":
            print("Source document location: {}".format(document.source_document_url))
            print("Translated document location: {}".format(document.translated_document_url))
            print("Translated to language: {}\n".format(document.translated_to))
        else:
            print("Error Code: {}, Message: {}\n".format(document.error.code, document.error.message))


if __name__ == '__main__':
    sample_translation_with_glossaries()
