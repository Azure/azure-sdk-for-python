# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

"""
FILE: sample_satellite_download_async.py

DESCRIPTION:
    This sample demonstrates:
    - Creating a Party and a Boundary
    - Queuing a satellite data ingestion job, and waiting for its completion
    - Dowloading the data parallelly with a set max degree of concurrency

USAGE:
    ```python sample_satellite_download_async.py```

    Set the environment variables with your own values before running the sample:
    - `AZURE_TENANT_ID`: The tenant ID of your active directory application.
    - `AZURE_CLIENT_ID`: The client ID of your active directory application.
    - `AZURE_CLIENT_SECRET`: The client secret of your active directory application.
    - `FARMBEATS_ENDPOINT`: The FarmBeats endpoint that you want to run these samples on.
"""

from azure.core.exceptions import ResourceNotFoundError
from azure.identity.aio import DefaultAzureCredential
from azure.agrifood.farming.aio import FarmBeatsClient
import asyncio
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from random import randint
from pathlib import Path
import os
from isodate import UTC
from dotenv import load_dotenv
import random

# Helper to retrive local file path from FarmBeats data store path.
def parse_file_path_from_file_link(file_link):
    return parse_qs(urlparse(file_link).query)['filePath'][0]

# Helper to download a given scene file path and store it to
# the specified out path.
async def download_image(client, file_link, root_dir):
    file_path = parse_file_path_from_file_link(file_link)
    out_path = Path(os.path.join(root_dir, file_path))
    out_path.parent.mkdir(parents=True, exist_ok=True)

    print(
        f"Async downloading image to {out_path.resolve()}... ", end="", flush=True)
    with open(out_path, 'wb') as tif_file:
        file_stream = await client.scenes.download(file_path=file_path)
        async for bits in file_stream:
            tif_file.write(bits)
    print("Done")
    return str(out_path.resolve())
        
async def sample_satellite_download_async():
    farmbeats_endpoint = os.environ['FARMBEATS_ENDPOINT']

    credential = DefaultAzureCredential()

    client = FarmBeatsClient(
        endpoint=farmbeats_endpoint,
        credential=credential
    )

    party_id = f"contoso-party-{random.randint(0,1000)}"
    boundary_id = "contoso-boundary"
    job_id_prefix = "contoso-job"
    start_date_time = datetime(2020, 1, 1, tzinfo=UTC)
    end_date_time = datetime(2020, 1, 31, tzinfo=UTC)
    data_root_dir = "./data"

    # Create or update a party within FarmBeats.
    print(
        f"Ensure party with id {party_id} exists... ", end="", flush=True)
    party = await client.parties.create_or_update(
        party_id=party_id,
        party={}
    )
    print("Done")

    # Create a boundary if the boundary does not exist.
    try:
        print(
            f"Checking if boundary with id {boundary_id} exists... ", end="", flush=True)
        boundary = await client.boundaries.get(
            party_id=party_id,
            boundary_id=boundary_id
        )
        print("Exists")
        
    except ResourceNotFoundError as e:
        print("Boundary doesn't exist. Creating... ", end="", flush=True)
        # Creating a boundary.
        boundary = await client.boundaries.create_or_update(
            party_id=party_id,
            boundary_id=boundary_id,
            boundary={
                "geometry":
                {
                    "type": "Polygon",
                    "coordinates":
                        [
                            [
                                [73.70457172393799, 20.545385304358106],
                                [73.70457172393799, 20.545385304358106],
                                [73.70448589324951, 20.542411534243367],
                                [73.70877742767334, 20.541688176010233],
                                [73.71023654937744, 20.545083911372505],
                                [73.70663166046143, 20.546992723579137],
                                [73.70457172393799, 20.545385304358106],
                            ]
                        ]
                },
                "status": "<string>",
                "name": "<string>",
                "description": "<string>"
            }
        )
        print("Created")

    # Queue a satellite job and wait for completion.
    job_id = f"{job_id_prefix}-{randint(0, 1000)}"
    print(f"Queuing satellite job {job_id}... ", end="", flush=True)
    satellite_job_poller = await client.scenes.begin_create_satellite_data_ingestion_job(
        job_id=job_id,
        job={
            "boundaryId": boundary_id,
            "endDateTime": end_date_time,
            "partyId": party_id,
            "startDateTime": start_date_time,
            "provider": "Microsoft",
            "source": "Sentinel_2_L2A",
            "data": {
                "imageNames": [
                    "NDVI"
                ],
                "imageFormats": [
                    "TIF"
                ],
                "imageResolution": [10]
            },
            "name": "<string>",
            "description": "<string>"
        }
    )
    print("Queued. Waiting for completion... ", end="", flush=True)
    await satellite_job_poller.result()
    print(f"Job completed with status {satellite_job_poller.status()}")

    # Get scenes which are available in FarmBeats for our party and boundary of intrest.
    print("Getting scenes list... ", end="", flush=True)
    scenes = client.scenes.list(
        party_id=party_id,
        boundary_id=boundary_id,
        start_date_time=start_date_time,
        end_date_time=end_date_time,
        provider="Microsoft",
        source="Sentinel_2_L2A"
    )
    print("Done")        

    async for scene in scenes:
        for image_file in scene["imageFiles"]:
            await download_image(client, image_file["fileLink"], data_root_dir)

    print("Downloads done")

    await client.close()
    await credential.close()


if __name__ == "__main__":

    load_dotenv()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    asyncio.run(sample_satellite_download_async())
