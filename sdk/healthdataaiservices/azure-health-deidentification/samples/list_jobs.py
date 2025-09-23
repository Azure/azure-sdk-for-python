# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: list_jobs.py

DESCRIPTION:
    This sample demonstrates how to list the latest jobs in the de-identification service.

USAGE:
    python list_jobs.py

    Set the environment variables with your own values before running the sample:
    1) HEALTHDATAAISERVICES_DEID_SERVICE_ENDPOINT - the service URL endpoint for a de-identification service.
"""


from azure.health.deidentification import DeidentificationClient
from azure.identity import DefaultAzureCredential
import os


def list_jobs():
    endpoint = os.environ["HEALTHDATAAISERVICES_DEID_SERVICE_ENDPOINT"]
    credential = DefaultAzureCredential()
    client = DeidentificationClient(endpoint, credential)

    jobs = client.list_jobs()

    print("Listing latest 5 jobs:")
    jobsToLookThrough = 5
    for j in jobs:
        print(f"Job Name: {j.job_name}")

        jobsToLookThrough -= 1
        if jobsToLookThrough <= 0:
            break


if __name__ == "__main__":
    list_jobs()
