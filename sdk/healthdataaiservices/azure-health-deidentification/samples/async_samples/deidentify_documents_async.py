# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: deidentify_documents_async.py

DESCRIPTION:
    This sample demonstrates a basic scenario of de-identifying documents in Azure Storage. 
    Taking a container URI and an input prefix, the sample will create a job and wait for the job to complete.

USAGE:
    python deidentify_documents_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_HEALTH_DEIDENTIFICATION_ENDPOINT - the service URL endpoint for a de-identification service.
    2) AZURE_STORAGE_ACCOUNT_LOCATION - an Azure Storage container endpoint, like "https://<storageaccount>.blob.core.windows.net/<container>".
    3) INPUT_PREFIX - the prefix of the input document name(s) in the container.
        For example, providing "folder1" would create a job that would process documents like "https://<storageaccount>.blob.core.windows.net/<container>/folder1/document1.txt".
"""


import asyncio
from azure.core.polling import AsyncLROPoller
from azure.health.deidentification.aio import DeidentificationClient
from azure.health.deidentification.models import (
    DeidentificationJob,
    SourceStorageLocation,
    TargetStorageLocation,
)
from azure.identity.aio import DefaultAzureCredential
import os
import uuid


async def deidentify_documents_async():
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

    async with client:
        lro: AsyncLROPoller = await client.begin_deidentify_documents(jobname, job)
        finished_job: DeidentificationJob = await lro.result()

        await credential.close()

        print(f"Job Name:   {finished_job.job_name}")
        print(f"Job Status: {finished_job.status}")  # Succeeded
        print(f"File Count: {finished_job.summary.total_count if finished_job.summary is not None else 0}")


async def main():
    await deidentify_documents_async()


if __name__ == "__main__":
    asyncio.run(main())
