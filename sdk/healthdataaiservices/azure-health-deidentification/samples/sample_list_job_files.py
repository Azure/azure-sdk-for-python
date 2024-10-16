# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_list_job_documents.py

DESCRIPTION:
    This sample demonstrates how to create a job, wait for it to finish, and then list the files associated with the job.

USAGE:
    python sample_list_job_documents.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_HEALTH_DEIDENTIFICATION_ENDPOINT - the endpoint to your Deidentification Service resource.
    2) AZURE_STORAGE_ACCOUNT_LOCATION - the location of the storage account where the input and output files are stored.
        This is an Azure Storage url to a container which must be configured with Managed Identity..
    3) INPUT_PREFIX - the prefix of the input files in the storage account.
"""


import uuid


def sample_list_job_documents():
    # [START sample_list_job_documents]
    import os
    from azure.identity import DefaultAzureCredential
    from azure.health.deidentification import DeidentificationClient
    from azure.health.deidentification.models import (
        DeidentificationJob,
        SourceStorageLocation,
        TargetStorageLocation,
    )
    from azure.core.polling import LROPoller

    endpoint = os.environ["AZURE_HEALTH_DEIDENTIFICATION_ENDPOINT"]
    endpoint = endpoint.replace("https://", "")

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
        target_location=TargetStorageLocation(
            location=storage_location, prefix=outputPrefix
        ),
    )

    print(f"Creating job with name: {jobname}")
    poller: LROPoller = client.begin_create_job(jobname, job)
    poller.wait(timeout=60)

    job = poller.result()
    print(f"Job Status: {job.status}")

    files = client.list_job_documents(job.name)

    print("Completed files (Max 10):")
    filesToLookThrough = 10
    for f in files:
        print(f"\t - {f.input.path}")

        filesToLookThrough -= 1
        if filesToLookThrough <= 0:
            break

    # [END sample_list_job_documents]


if __name__ == "__main__":
    sample_list_job_documents()
