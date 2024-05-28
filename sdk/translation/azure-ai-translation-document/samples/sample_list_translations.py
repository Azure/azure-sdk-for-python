# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: list_translations.py

DESCRIPTION:
    This sample demonstrates how to list all the submitted translation operations for the resource.

    To set up your containers for translation and generate SAS tokens to your containers (or files)
    with the appropriate permissions, see the README.

USAGE:
    python list_translations.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_DOCUMENT_TRANSLATION_ENDPOINT - the endpoint to your Document Translation resource.
    2) AZURE_DOCUMENT_TRANSLATION_KEY - your Document Translation API key.
"""


def sample_list_translations():
    import os

    # [START list_translations]
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.translation.document import DocumentTranslationClient

    endpoint = os.environ["AZURE_DOCUMENT_TRANSLATION_ENDPOINT"]
    key = os.environ["AZURE_DOCUMENT_TRANSLATION_KEY"]

    client = DocumentTranslationClient(endpoint, AzureKeyCredential(key))
    operations = client.get_translations_status()

    for operation in operations:
        print(f"ID: {operation.id}")
        print(f"Status: {operation.status}")
        print(f"Created on: {operation.created_date_time_utc}")
        print(f"Last updated on: {operation.last_action_date_time_utc}")
        print(f"Total number of operations on documents: {operation.summary.total}")
        print(f"Total number of characters charged: {operation.summary.total_character_charged}")

        print("\nOf total documents...")
        print(f"{operation.summary.failed} failed")
        print(f"{operation.summary.success} succeeded")
        print(f"{operation.summary.cancelled} canceled\n")

    # [END list_translations]


if __name__ == "__main__":
    sample_list_translations()
