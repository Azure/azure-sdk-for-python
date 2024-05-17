# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_begin_translation_with_filters.py

DESCRIPTION:
    This sample demonstrates how to translate documents under a particular folder in your container, or how
    to translate only a specific document in a container. To see how to translate all documents in your container,
    see sample_begin_translation.py.

USAGE:
    python sample_begin_translation_with_filters.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_DOCUMENT_TRANSLATION_ENDPOINT - the endpoint to your Document Translation resource.
    2) AZURE_DOCUMENT_TRANSLATION_KEY - your Document Translation API key.
    3) AZURE_SOURCE_CONTAINER_URL - the container SAS URL to your source container which has the documents
        to be translated. For this sample, the source container should contain a document within a folder.
    4) AZURE_TARGET_CONTAINER_URL - the container SAS URL to your target container where the translated documents
        will be written.
    5) AZURE_SOURCE_BLOB_URL - the blob SAS URL to the specific document to translate.
        e.g. https://mystorage.blob.core.windows.net/srccontainer/document.pdf?<sas-token>
    6) AZURE_TARGET_BLOB_URL - the target container SAS URL, including the document name for the translated file
        (which does not exist yet). E.g. https://mystorage.blob.core.windows.net/targetcontainer/document_french.pdf?<sas-token>
"""


def sample_translation_under_folder():
    import os
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.translation.document import DocumentTranslationClient

    endpoint = os.environ["AZURE_DOCUMENT_TRANSLATION_ENDPOINT"]
    key = os.environ["AZURE_DOCUMENT_TRANSLATION_KEY"]
    source_container_url = os.environ["AZURE_SOURCE_CONTAINER_URL"]  # do not include the folder name in source url
    target_container_url = os.environ["AZURE_TARGET_CONTAINER_URL"]

    client = DocumentTranslationClient(endpoint, AzureKeyCredential(key))

    poller = client.begin_translation(source_container_url, target_container_url, "fr", prefix="myfoldername")
    result = poller.result()

    for document in result:
        print(f"Document ID: {document.id}")
        print(f"Document status: {document.status}")
        if document.status == "Succeeded":
            print(f"Source document location: {document.source_document_url}")
            print(f"Translated document location: {document.translated_document_url}")
            print(f"Translated to language: {document.translated_to}\n")
        elif document.error:
            print(f"Error Code: {document.error.code}, Message: {document.error.message}\n")


def sample_translation_specific_document():
    import os
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.translation.document import DocumentTranslationClient

    endpoint = os.environ["AZURE_DOCUMENT_TRANSLATION_ENDPOINT"]
    key = os.environ["AZURE_DOCUMENT_TRANSLATION_KEY"]
    source_blob_url = os.environ["AZURE_SOURCE_BLOB_URL"]
    target_blob_url = os.environ["AZURE_TARGET_BLOB_URL"]

    client = DocumentTranslationClient(endpoint, AzureKeyCredential(key))

    poller = client.begin_translation(source_blob_url, target_blob_url, "fr", storage_type="File")
    result = poller.result()

    for document in result:
        print(f"Document ID: {document.id}")
        print(f"Document status: {document.status}")
        if document.status == "Succeeded":
            print(f"Source document location: {document.source_document_url}")
            print(f"Translated document location: {document.translated_document_url}")
            print(f"Translated to language: {document.translated_to}\n")
        elif document.error:
            print(f"Error Code: {document.error.code}, Message: {document.error.message}\n")


if __name__ == "__main__":
    sample_translation_under_folder()
    sample_translation_specific_document()
