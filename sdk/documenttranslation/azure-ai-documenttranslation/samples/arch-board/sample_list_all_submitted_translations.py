# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------


def sample_list_all_submitted_jobs():
    # import libraries
    import os
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.documenttranslation import (
        DocumentTranslationClient,
        DocumentTranslationPoller
    )

    # get service secrets
    endpoint = os.environ["AZURE_DOCUMENT_TRANSLATION_ENDPOINT"]
    key = os.environ["AZURE_DOCUMENT_TRANSLATION_KEY"]

    # create translation client
    client = DocumentTranslationClient(endpoint, AzureKeyCredential(key))

    # list submitted translations
    translation_operations = client.list_submitted_translations()  # type: ItemPaged[TranslationStatusDetail]

    for translation_operation in translation_operations:
        if translation_operation.status in ["NotStarted", "Running"]:
            poller = client.begin_translation(None, continuation_token=translation_operation.id)
            #poller = DocumentTranslationPoller.from_batch_id(translation_operation.id)
            translation_operation = poller.result()

        print("Translation ID: {}".format(translation_operation.id))
        print("Translation status: {}".format(translation_operation.status))
        print("Translation created on: {}".format(translation_operation.created_on))
        print("Translation last updated on: {}".format(translation_operation.last_updated_on))
        print("Total number of translations on documents: {}".format(translation_operation.documents_total_count))
        print("Total number of characters charged: {}".format(translation_operation.total_characters_charged))

        print("Of total documents...")
        print("{} failed".format(translation_operation.documents_failed_count))
        print("{} succeeded".format(translation_operation.documents_succeeded_count))
        print("{} in progress".format(translation_operation.documents_in_progress_count))
        print("{} not yet started".format(translation_operation.documents_not_yet_started_count))
        print("{} cancelled".format(translation_operation.documents_cancelled_count))


if __name__ == '__main__':
    sample_list_all_submitted_jobs()