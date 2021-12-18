# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

"""
FILE: sample_cascade_delete_async.py

DESCRIPTION:
    This sample demonstrates 
    - Getting a filterd list of farmers based on last modified timestamp
    - Queuing a cascade delete job on a farmer, and polling for it to complete

USAGE:
    ```python sample_cascade_delete_async.py```

    Set the environment variables with your own values before running the sample:
    - `AZURE_TENANT_ID`: The tenant ID of your active directory application.
    - `AZURE_CLIENT_ID`: The client ID of your active directory application.
    - `AZURE_CLIENT_SECRET`: The client secret of your active directory application.
    - `FARMBEATS_ENDPOINT`: The FarmBeats endpoint that you want to run these samples on.
"""

from azure.identity.aio import DefaultAzureCredential
from azure.agrifood.farming.aio import FarmBeatsClient
import os
from datetime import datetime, timedelta
from random import randint
from isodate import UTC
import asyncio
from dotenv import load_dotenv


async def sample_cascade_delete_async():

    farmbeats_endpoint = os.environ['FARMBEATS_ENDPOINT']

    credential = DefaultAzureCredential()

    client = FarmBeatsClient(
        endpoint=farmbeats_endpoint,
        credential=credential
    )

    job_id_prefix = "cascade-delete-job"

    # Getting list of farmers modified in the last 7 days
    print("Getting list of recently modified farmer id's... ", end="", flush=True)
    farmers = client.farmers.list(
        min_last_modified_date_time=datetime.now(tz=UTC) - timedelta(days=7)
    )
    farmer_ids = [farmer.id async for farmer in farmers]
    print("Done")

    # Ask for the id of the farmer which is to be deleted.
    print(f"Recentely modified farmer id's:")
    print(*farmer_ids, sep="\n")
    farmer_id_to_delete = input("Please enter the id of the farmer you wish to delete resources for: ").strip()
    if farmer_id_to_delete not in farmer_ids:
        raise SystemExit("Entered id for farmer does not exist.")

    # Deleting the farmer and it's associated resources. Queuing the cascade delete job.

    job_id = f"{job_id_prefix}-{randint(0, 1000)}"
    print(f"Queuing cascade delete job {job_id}... ", end="", flush=True)
    cascade_delete_job_poller = await client.farmers.begin_create_cascade_delete_job(
        job_id=job_id,
        farmer_id = farmer_id_to_delete
    )
    print("Queued. Waiting for completion... ", end="", flush=True)
    await cascade_delete_job_poller.result()

    print("The job completed with status", cascade_delete_job_poller.status())

    await client.close()
    await credential.close()


if __name__ == "__main__":

    load_dotenv()

    asyncio.get_event_loop().run_until_complete(sample_cascade_delete_async())
