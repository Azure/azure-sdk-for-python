# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_list_jobs.py

DESCRIPTION:
    This sample demonstrates how to list the latest 5 jobs in the Deidentification Service resource.
    It will create a job and then list it using the list_jobs method.

USAGE:
    python sample_list_jobs.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_HEALTH_DEIDENTIFICATION_ENDPOINT - the endpoint to your Deidentification Service resource.
    2) AZURE_STORAGE_ACCOUNT_LOCATION - the location of the storage account where the input and output files are stored.
        This can be either a URL (which is configured with Managed Identity) or a SasURI.
    3) INPUT_PREFIX - the prefix of the input files in the storage account.
"""


import uuid


def sample_list_jobs():
    # [START sample_list_jobs]
    import os
    from azure.identity import DefaultAzureCredential
    from azure.health.deidentification import DeidentificationClient
    from azure.health.deidentification.models import (
        DeidentificationJob,
        SourceStorageLocation,
        TargetStorageLocation,
        OperationType,
        DocumentDataType,
    )
    from azure.core.polling import LROPoller

    endpoint = os.environ["AZURE_HEALTH_DEIDENTIFICATION_ENDPOINT"]
    endpoint = endpoint.replace("https://", "")
    # uri decode
    print(endpoint)

    storage_location = os.environ["AZURE_STORAGE_ACCOUNT_LOCATION"]
    inputPrefix = os.environ["INPUT_PREFIX"]
    outputPrefix = "_output"

    credential = DefaultAzureCredential()

    client = DeidentificationClient(
        endpoint,
        DefaultAzureCredential(),
        connection_verify="localhost" not in endpoint,
    )

    jobname = f"sample-job-{uuid.uuid4().hex[:8]}"

    job = DeidentificationJob(
        source_location=SourceStorageLocation(
            location=storage_location,
            prefix=inputPrefix,
        ),
        target_location=TargetStorageLocation(
            location=storage_location, prefix=outputPrefix
        ),
        operation=OperationType.SURROGATE,
        data_type=DocumentDataType.PLAINTEXT,
    )

    print(f"Creating job with name: {jobname}")
    client.begin_create_job(jobname, job)

    jobs = client.list_jobs()

    print("Listing latest 5 jobs:")
    jobsToLookThrough = 5
    for j in jobs:
        print(f"Job Name: {j.name}")

        jobsToLookThrough -= 1
        if jobsToLookThrough <= 0:
            break

    # [END sample_list_jobs]


if __name__ == "__main__":
    sample_list_jobs()
