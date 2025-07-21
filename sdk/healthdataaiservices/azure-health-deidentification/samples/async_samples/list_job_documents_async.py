# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: list_job_documents_async.py

DESCRIPTION:
    This sample demonstrates how to create a job, wait for it to finish, and then list the files associated with the job.

USAGE:
    python list_job_documents_async.py

    Set the environment variables with your own values before running the sample:
    1) HEALTHDATAAISERVICES_DEID_SERVICE_ENDPOINT - the service URL endpoint for a de-identification service.
    2) HEALTHDATAAISERVICES_STORAGE_ACCOUNT_LOCATION - an Azure Storage container endpoint, like "https://<storageaccount>.blob.core.windows.net/<container>".
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


async def list_job_documents_async():
    endpoint = os.environ["HEALTHDATAAISERVICES_DEID_SERVICE_ENDPOINT"]
    storage_location = os.environ["HEALTHDATAAISERVICES_STORAGE_ACCOUNT_LOCATION"]
    inputPrefix = os.environ.get("INPUT_PREFIX", "example_patient_1")
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
    async with client:
        poller: AsyncLROPoller = await client.begin_deidentify_documents(jobname, job)
        job = await poller.result()
        print(f"Job Status: {job.status}")

        files = client.list_job_documents(jobname)

        print("Completed files (Max 10):")
        filesToLookThrough = 10
        async for f in files:
            print(f"\t - {f.input_location.location}")

            filesToLookThrough -= 1
            if filesToLookThrough <= 0:
                break

        await credential.close()


async def main():
    await list_job_documents_async()


if __name__ == "__main__":
    asyncio.run(main())
