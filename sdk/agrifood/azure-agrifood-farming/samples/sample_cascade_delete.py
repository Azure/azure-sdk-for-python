# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

"""
FILE: sample_cascade_delete.py

DESCRIPTION:
    This sample demonstrates 
    - Getting a filtered list of parties based on last modified timestamp
    - Queuing a cascade delete job on a party, and polling for it to complete

USAGE:
    ```python sample_cascade_delete.py```

    Set the environment variables with your own values before running the sample:
    - `AZURE_TENANT_ID`: The tenant ID of your active directory application.
    - `AZURE_CLIENT_ID`: The client ID of your active directory application.
    - `AZURE_CLIENT_SECRET`: The client secret of your active directory application.
    - `FARMBEATS_ENDPOINT`: The FarmBeats endpoint that you want to run these samples on.
"""

from azure.identity import DefaultAzureCredential
from azure.agrifood.farming import FarmBeatsClient
import os
from datetime import datetime, timedelta
from random import randint
from isodate import UTC
from dotenv import load_dotenv


def sample_cascade_delete():

    farmbeats_endpoint = os.environ['FARMBEATS_ENDPOINT']

    credential = DefaultAzureCredential()

    client = FarmBeatsClient(
        endpoint=farmbeats_endpoint,
        credential=credential
    )

    job_id_prefix = "cascade-delete-job"

    # Getting list of parties modified in the last 7 days
    print("Getting list of recently modified party id's... ", end="", flush=True)
    parties = client.parties.list(
        min_last_modified_date_time=datetime.now(tz=UTC) - timedelta(days=7)
    )
    party_ids = [party["id"] for party in parties]
    print("Done")

    # Ask for the id of the party which is to be deleted.
    print(f"Recentely modified party id's:")
    print(*party_ids, sep="\n")
    party_id_to_delete = input("Please enter the id of the party you wish to delete resources for: ").strip()
    if party_id_to_delete not in party_ids:
        raise SystemExit("Entered id for party does not exist.")

    # Deleting the party and it's associated resources. Queuing the cascade delete job.

    job_id = f"{job_id_prefix}-{randint(0, 1000)}"
    print(f"Queuing cascade delete job {job_id}... ", end="", flush=True)
    cascade_delete_job_poller = client.parties.begin_create_cascade_delete_job(
        job_id=job_id,
        party_id = party_id_to_delete
    )
    print("Queued. Waiting for completion... ", end="", flush=True)
    cascade_delete_job_poller.result()
    print("The job completed with status", cascade_delete_job_poller.status())


if __name__ == "__main__":

    load_dotenv()

    sample_cascade_delete()
