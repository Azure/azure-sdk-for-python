# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: list_job_documents.py

DESCRIPTION:
    This sample demonstrates how to create a job, wait for it to finish, and then list the files associated with the job.

USAGE:
    python list_job_documents.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_HEALTH_DEIDENTIFICATION_ENDPOINT - the service URL endpoint for a de-identification service.
    2) AZURE_STORAGE_ACCOUNT_LOCATION - an Azure Storage container endpoint, like "https://<storageaccount>.blob.core.windows.net/<container>".
    3) INPUT_PREFIX - the prefix of the input document name(s) in the container.
        For example, providing "folder1" would create a job that would process documents like "https://<storageaccount>.blob.core.windows.net/<container>/folder1/document1.txt".
"""


from azure.health.deidentification import DeidentificationClient
from azure.health.deidentification.models import (
    DeidentificationJob,
    SourceStorageLocation,
    TargetStorageLocation,
)
from azure.identity import DefaultAzureCredential
import os
import uuid


def list_job_documents():
    endpoint = os.environ["AZURE_HEALTH_DEIDENTIFICATION_ENDPOINT"]
    storage_location = os.environ["AZURE_STORAGE_ACCOUNT_LOCATION"]
    inputPrefix = os.environ["INPUT_PREFIX"]
    outputPrefix = "_output"

    credential = DefaultAzureCredential()

    client = DeidentificationClient(endpoint, credential)

    jobname = f"sample-job-{uuid.uuid4().hex[:8]}"

    job = DeidentificationJob(
        source_location=SourceStorageLocation(
            location=storage_location,
            prefix=inputPrefix,
        ),
        target_location=TargetStorageLocation(location=storage_location, prefix=outputPrefix, overwrite=True),
    )

    print(f"Creating job with name: {jobname}")

    job = client.begin_deidentify_documents(jobname, job).result(timeout=60)

    print(f"Job Status: {job.status}")

    files = client.list_job_documents(jobname)

    print("Completed files (Max 10):")
    filesToLookThrough = 10
    for f in files:
        print(f"\t - {f.input_location.location}")

        filesToLookThrough -= 1
        if filesToLookThrough <= 0:
            break


if __name__ == "__main__":
    list_job_documents()
