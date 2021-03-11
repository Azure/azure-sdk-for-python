# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------


def sample_cancel_translation_job():
    import os
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.documenttranslation import (
        DocumentTranslationClient,
        BatchDocumentInput,
        StorageTarget
    )

    endpoint = os.environ["AZURE_DOCUMENT_TRANSLATION_ENDPOINT"]
    key = os.environ["AZURE_DOCUMENT_TRANSLATION_KEY"]
    source_container_url = os.environ["AZURE_SOURCE_CONTAINER_URL"]
    target_container_url_es = os.environ["AZURE_TARGET_CONTAINER_URL_ES"]

    client = DocumentTranslationClient(endpoint, AzureKeyCredential(key))

    batch = [
        BatchDocumentInput(
            source_url=source_container_url,
            targets=[
                StorageTarget(
                    target_url=target_container_url_es,
                    language="es"
                )
            ],
            storage_type="file"
        )
    ]

    job_detail = client.create_translation_job(batch)  # type: JobStatusDetail

    print("Job initial status: {}".format(job_detail.status))
    print("Number of translations on documents: {}".format(job_detail.documents_total_count))

    client.cancel_job(job_detail.id)
    job_detail = client.get_job_status(job_detail.id)  # type: JobStatusDetail

    if job_detail.status in ["Cancelled", "Cancelling"]:
        print("We cancelled job with ID: {}".format(job_detail.id))


if __name__ == '__main__':
    sample_cancel_translation_job()
