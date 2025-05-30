# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: deidentify_documents.py

DESCRIPTION:
    This sample demonstrates a basic scenario of de-identifying documents in Azure Storage. 
    Taking a container URI and an input prefix, the sample will create a job and wait for the job to complete.

USAGE:
    python deidentify_documents.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_HEALTH_DEIDENTIFICATION_ENDPOINT - the service URL endpoint for a de-identification service.
    2) AZURE_STORAGE_ACCOUNT_LOCATION - an Azure Storage container endpoint, like "https://<storageaccount>.blob.core.windows.net/<container>".
    3) INPUT_PREFIX - the prefix of the input document name(s) in the container. 
        For example, providing "folder1" would create a job that would process documents like "https://<storageaccount>.blob.core.windows.net/<container>/folder1/document1.txt".
    4) OUTPUT_PREFIX - the prefix of the output document name(s) in the container. This will appear as a folder which will be created if it does not exist, and defaults to "_output" if not provided.
        For example, providing "_output1" would output documents like "https://<storageaccount>.blob.core.windows.net/<container>/_output1/document1.txt".
"""


def deidentify_documents():
    # [START sample]
    from azure.health.deidentification import DeidentificationClient
    from azure.health.deidentification.models import (
        DeidentificationJob,
        DeidentificationOperationType,
        SourceStorageLocation,
        TargetStorageLocation,
    )
    from azure.identity import DefaultAzureCredential
    import os
    import uuid


    endpoint = os.environ["AZURE_HEALTH_DEIDENTIFICATION_ENDPOINT"]
    storage_location = os.environ["AZURE_STORAGE_ACCOUNT_LOCATION"]
    inputPrefix = os.environ["INPUT_PREFIX"]
    outputPrefix = os.environ.get("OUTPUT_PREFIX", "_output")

    credential = DefaultAzureCredential()

    client = DeidentificationClient(endpoint, credential)

    jobname = f"sample-job-{uuid.uuid4().hex[:8]}"

    job = DeidentificationJob(
        operation_type=DeidentificationOperationType.SURROGATE,
        source_location=SourceStorageLocation(
            location=storage_location,
            prefix=inputPrefix,
        ),
        target_location=TargetStorageLocation(location=storage_location, prefix=outputPrefix, overwrite=True),
    )

    finished_job: DeidentificationJob = client.begin_deidentify_documents(jobname, job).result(timeout=120)

    print(f"Job Name:   {finished_job.job_name}")
    print(f"Job Status: {finished_job.status}")
    print(f"File Count: {finished_job.summary.total_count if finished_job.summary is not None else 0}")
    # [END sample]


if __name__ == "__main__":
    deidentify_documents()
