# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: list_all_translations.py

DESCRIPTION:
    This sample demonstrates how to list all the submitted translation operations for the resource.

    To set up your containers for translation and generate SAS tokens to your containers (or files)
    with the appropriate permissions, see the README.

USAGE:
    python list_all_translations.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_DOCUMENT_TRANSLATION_ENDPOINT - the endpoint to your Document Translation resource.
    2) AZURE_DOCUMENT_TRANSLATION_KEY - your Document Translation API key.
"""


def sample_list_all_translations():
    import os
    # [START list_all_translations]
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.translation.document import DocumentTranslationClient


    endpoint = os.environ["AZURE_DOCUMENT_TRANSLATION_ENDPOINT"]
    key = os.environ["AZURE_DOCUMENT_TRANSLATION_KEY"]

    client = DocumentTranslationClient(endpoint, AzureKeyCredential(key))
    operations = client.list_all_translation_statuses()  # type: ItemPaged[TranslationStatus]

    for operation in operations:
        print("ID: {}".format(operation.id))
        print("Status: {}".format(operation.status))
        print("Created on: {}".format(operation.created_on))
        print("Last updated on: {}".format(operation.last_updated_on))
        print("Total number of operations on documents: {}".format(operation.documents_total_count))
        print("Total number of characters charged: {}".format(operation.total_characters_charged))

        print("\nOf total documents...")
        print("{} failed".format(operation.documents_failed_count))
        print("{} succeeded".format(operation.documents_succeeded_count))
        print("{} cancelled\n".format(operation.documents_cancelled_count))

    # [END list_all_translations]


if __name__ == '__main__':
    sample_list_all_translations()
