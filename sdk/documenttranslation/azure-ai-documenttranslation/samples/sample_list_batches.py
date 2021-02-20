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
    batches = client.list_batches()

    print("Batches summary")
    for batch in batches:
        print("Batch ID: {}".format(batch.id))
        print("Batch status: {}".format(batch.status))
        print("Batch created on: {}".format(batch.created_on))
        print("Batch last updated on: {}".format(batch.last_updated))
        print("Batch number of translations on documents: {}".format(batch.summary.total))

        print("Of total documents...")
        print("{} failed".format(batch.summary.failed))
        print("{} succeeded".format(batch.summary.succeeded))
        print("{} in progress".format(batch.summary.in_progress))
        print("{} not yet started".format(batch.summary.not_yet_started))
        print("{} cancelled".format(batch.summary.cancelled))
