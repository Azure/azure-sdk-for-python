# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_create_and_wait_job.py

DESCRIPTION:
    This sample demonstrates the most simple job-based deidentification scenario. 
    It takes a blob uri as input and an input prefix. It will create a job and wait for the job to complete.

USAGE:
    python sample_create_and_wait_job.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_HEALTH_DEIDENTIFICATION_ENDPOINT - the endpoint to your Deidentification Service resource.
    2) AZURE_STORAGE_ACCOUNT_LOCATION - the location of the storage account where the input and output files are stored.
        This is an Azure Storage url to a container which must be configured with Managed Identity..
    3) INPUT_PREFIX - the prefix of the input files in the storage account.
"""


import uuid


def sample_create_and_wait_job():
    # [START sample_create_and_wait_job]
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

    lro: LROPoller = client.begin_create_job(jobname, job)
    lro.wait(timeout=60)

    finished_job: DeidentificationJob = lro.result()
    print(f"Job Name: {finished_job.name}")
    print(f"Job Status: {finished_job.status}")
    print(
        f"File Count: {finished_job.summary.total if finished_job.summary is not None else 0}"
    )
    # [END sample_create_and_wait_job]


if __name__ == "__main__":
    sample_create_and_wait_job()
