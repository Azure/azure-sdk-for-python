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
        This is an Azure Storage url to a container which must be configured with Managed Identity..
    3) INPUT_PREFIX - the prefix of the input files in the storage account.
"""


import uuid


def sample_list_jobs():
    # [START sample_list_jobs]
    import os
    from azure.identity import DefaultAzureCredential
    from azure.health.deidentification import DeidentificationClient

    endpoint = os.environ["AZURE_HEALTH_DEIDENTIFICATION_ENDPOINT"]
    endpoint = endpoint.replace("https://", "")

    credential = DefaultAzureCredential()

    client = DeidentificationClient(endpoint, credential)

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
