# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_list_job_documents_async.py

DESCRIPTION:
    This sample demonstrates how to create a job, wait for it to finish, and then list the files associated with the job.

USAGE:
    python sample_list_job_documents_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_HEALTH_DEIDENTIFICATION_ENDPOINT - the endpoint to your Deidentification Service resource.
    2) AZURE_STORAGE_ACCOUNT_LOCATION - the location of the storage account where the input and output files are stored.
        This is an Azure Storage url to a container which must be configured with Managed Identity..
    3) INPUT_PREFIX - the prefix of the input files in the storage account.
"""

import asyncio
import uuid


async def sample_list_job_documents_async():
    # [START sample_list_job_documents_async]
    import os
    from azure.identity.aio import DefaultAzureCredential
    from azure.health.deidentification.aio import DeidentificationClient
    from azure.health.deidentification.models import (
        DeidentificationJob,
        SourceStorageLocation,
        TargetStorageLocation,
    )
    from azure.core.polling import AsyncLROPoller

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
    async with client:
        poller: AsyncLROPoller = await client.begin_create_job(jobname, job)
        job = await poller.result()
        print(f"Job Status: {job.status}")

        files = client.list_job_documents(job.name)

        print("Completed files (Max 10):")
        filesToLookThrough = 10
        async for f in files:
            print(f"\t - {f.input.path}")

            filesToLookThrough -= 1
            if filesToLookThrough <= 0:
                break

    await credential.close()
    # [END sample_list_job_documents_async]


async def main():
    await sample_list_job_documents_async()


if __name__ == "__main__":
    asyncio.run(main())
