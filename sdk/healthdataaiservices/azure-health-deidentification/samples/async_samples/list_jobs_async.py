# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: list_jobs_async.py

DESCRIPTION:
    This sample demonstrates how to list the latest jobs in the de-identification service.

USAGE:
    python list_jobs_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_HEALTH_DEIDENTIFICATION_ENDPOINT - the service URL endpoint for a de-identification service.
"""


import asyncio
from azure.health.deidentification.aio import DeidentificationClient
from azure.identity.aio import DefaultAzureCredential
import os


async def list_jobs_async():
    endpoint = os.environ["AZURE_HEALTH_DEIDENTIFICATION_ENDPOINT"]
    credential = DefaultAzureCredential()
    client = DeidentificationClient(endpoint, credential)

    async with client:
        jobs = client.list_jobs()

        print("Listing latest 5 jobs:")
        jobsToLookThrough = 5
        async for j in jobs:
            print(f"Job Name: {j.job_name}")

            jobsToLookThrough -= 1
            if jobsToLookThrough <= 0:
                break

        await credential.close()


async def main():
    await list_jobs_async()


if __name__ == "__main__":
    asyncio.run(main())
