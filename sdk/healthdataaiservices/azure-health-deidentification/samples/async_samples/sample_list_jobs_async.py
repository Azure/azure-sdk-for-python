# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_list_jobs_async.py

DESCRIPTION:
    This sample demonstrates how to list the latest 5 jobs in the Deidentification Service resource.
    It will create a job and then list it using the list_jobs method.

USAGE:
    python sample_list_jobs_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_HEALTH_DEIDENTIFICATION_ENDPOINT - the endpoint to your Deidentification Service resource.
    2) AZURE_STORAGE_ACCOUNT_LOCATION - the location of the storage account where the input and output files are stored.
        This is an Azure Storage url to a container which must be configured with Managed Identity..
    3) INPUT_PREFIX - the prefix of the input files in the storage account.
"""
import asyncio
import uuid


async def sample_list_jobs_async():
    # [START sample_list_jobs_async]
    import os
    from azure.identity.aio import DefaultAzureCredential
    from azure.health.deidentification.aio import DeidentificationClient

    endpoint = os.environ["AZURE_HEALTH_DEIDENTIFICATION_ENDPOINT"]
    endpoint = endpoint.replace("https://", "")

    credential = DefaultAzureCredential()

    client = DeidentificationClient(endpoint, credential)

    async with client:
        jobs = client.list_jobs()

        print("Listing latest 5 jobs:")
        jobsToLookThrough = 5
        async for j in jobs:
            print(f"Job Name: {j.name}")

            jobsToLookThrough -= 1
            if jobsToLookThrough <= 0:
                break

    await credential.close()
    # [END sample_list_jobs_async]


async def main():
    await sample_list_jobs_async()


if __name__ == "__main__":
    asyncio.run(main())
