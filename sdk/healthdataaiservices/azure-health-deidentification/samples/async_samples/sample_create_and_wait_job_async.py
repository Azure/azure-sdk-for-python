# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_create_and_wait_job_async.py

DESCRIPTION:
    This sample demonstrates the most simple job-based deidentification scenario. 
    It takes a blob uri as input and an input prefix. It will create a job and wait for the job to complete.

USAGE:
    python sample_create_and_wait_job_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_HEALTH_DEIDENTIFICATION_ENDPOINT - the endpoint to your Deidentification Service resource.
    2) AZURE_STORAGE_ACCOUNT_LOCATION - the location of the storage account where the input and output files are stored.
        This can be either a URL (which is configured with Managed Identity) or a SasURI.
    3) INPUT_PREFIX - the prefix of the input files in the storage account.
"""
import asyncio

import uuid


async def sample_create_and_wait_job_async():
    # [START sample_create_and_wait_job_async]
    import os
    from azure.identity import DefaultAzureCredential
    from azure.health.deidentification.aio import DeidentificationClient
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

    async with client:
        lro: LROPoller = await client.begin_create_job(jobname, job)
        finished_job: DeidentificationJob = await lro.result()

    print(f"Job Name: {finished_job.name}")
    print(f"Job Status: {finished_job.status}")  # Succeeded
    print(f"File Count: {finished_job.summary.total}")
    # [END sample_create_and_wait_job_async]


async def main():
    await sample_create_and_wait_job_async()


if __name__ == "__main__":
    asyncio.run(main())
