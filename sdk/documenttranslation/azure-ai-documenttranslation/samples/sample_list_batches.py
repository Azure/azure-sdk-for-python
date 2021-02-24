# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------


def sample_list_all_batches():
    import os
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.documenttranslation import (
        DocumentTranslationClient,
    )

    endpoint = os.environ["AZURE_DOCUMENT_TRANSLATION_ENDPOINT"]
    key = os.environ["AZURE_DOCUMENT_TRANSLATION_KEY"]

    client = DocumentTranslationClient(endpoint, AzureKeyCredential(key))
    batches = client.list_statuses_of_batches()

    print("Batches summary")
    for batch in batches:
        print("Batch ID: {}".format(batch.id))
        print("Batch status: {}".format(batch.status))
        print("Batch created on: {}".format(batch.created_on))
        print("Batch last updated on: {}".format(batch.last_updated_on))
        print("Batch number of translations on documents: {}".format(batch.documents_total_count))

        print("Of total documents...")
        print("{} failed".format(batch.documents_failed_count))
        print("{} succeeded".format(batch.documents_succeeded_count))
        print("{} in progress".format(batch.documents_in_progress_count))
        print("{} not yet started".format(batch.documents_not_yet_started_count))
        print("{} cancelled".format(batch.documents_cancelled_count))
