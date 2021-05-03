import os
import pprint
from azure.core.exceptions import HttpResponseError
from azure.identity.aio import ClientSecretCredential
from azure.farmbeats.aio import FarmBeatsClient
from azure.farmbeats.models import Farmer, Boundary, Polygon, SatelliteDataIngestionJob, SatelliteData
import asyncio
from dotenv import find_dotenv, load_dotenv

from datetime import datetime, timedelta
from pytz import utc
from urllib.parse import unquote, urlparse, parse_qs
import random
from pathlib import Path
import os

load_dotenv(find_dotenv())

# sample
credential = ClientSecretCredential(
    tenant_id=os.environ['FARMBEATS_TENANT_ID'],
    client_id=os.environ['FARMBEATS_CLIENT_ID'],
    client_secret=os.environ['FARMBEATS_CLIENT_SECRET'],
    authority=os.environ['FARMBEATS_AUTHORITY']
)

client = FarmBeatsClient(
    endpoint=os.environ['FARMBEATS_ENDPOINT'],
    credential=credential,
)

# Define contstants for this script
farmer_id = os.environ['FARMBEATS_FARMER_ID']
boundary_id = os.environ['FARMBEATS_BOUNDARY_ID']
job_id_prefix = os.environ['FARMBEATS_JOB_ID_PREFIX']
start_date_time = datetime(2020, 1, 1, tzinfo=utc)
end_date_time = datetime(2020, 12, 31, tzinfo=utc)
data_root_dir = "./asyncio_test_downloads"

# Utility funcitons
def print_error(exception):
    print("Error:")
    try:
        pprint(exception.model.as_dict())
    except:
        print(exception.response.body())
        print("Couldn't print error info")


def parse_file_path_from_file_link(file_link):
    return parse_qs(urlparse(file_link).query)['filePath'][0]


async def aiter_to_list(aiter):
    l = list()
    async for obj in aiter:
        l.append(obj)
    return l


# Get the default event loop
loop = asyncio.get_event_loop()

# Ensure farmer
try:
    print(
        f"Create/updating farmer with id {farmer_id}... ", end="", flush=True)
    farmer = loop.run_until_complete(
        client.farmers.create_or_update(
            farmer_id=farmer_id,
            farmer=Farmer()
        )
    )
    print("Done")
    print(farmer.as_dict())
except HttpResponseError as e:
    print("Ooops... here's the error:")
    print_error(e)


# Ensure boundary
try:
    print(
        f"Checking if boundary with id {boundary_id} exists... ", end="", flush=True)
    boundary = loop.run_until_complete(
        client.boundaries.get(
            farmer_id=farmer_id,
            boundary_id=boundary_id
        )
    )
    if boundary:
        print("Exists")
    else:
        print("Boundary doesn't exist... Creating... ", end="", flush=True)
        boundary = loop.run_until_complete(
            client.boundaries.create_or_update(
                farmer_id=farmer_id,
                boundary_id=boundary_id,
                boundary=Boundary(
                    description="Created by SDK",
                    geometry=Polygon(
                        coordinates = [
                            [
                                [
                                    73.70457172393799,
                                    20.545385304358106
                                ],
                                [
                                    73.70457172393799,
                                    20.545385304358106
                                ],
                                [
                                    73.70448589324951,
                                    20.542411534243367
                                ],
                                [
                                    73.70877742767334,
                                    20.541688176010233
                                ],
                                [
                                    73.71023654937744,
                                    20.545083911372505
                                ],
                                [
                                    73.70663166046143,
                                    20.546992723579137
                                ],
                                [
                                    73.70457172393799,
                                    20.545385304358106
                                ]
                            ]
                        ]
                    )
                )
            )
        )
        print("Created")

    print(boundary.as_dict())
except HttpResponseError as e:
    print("Ooops... here's the error:")
    print_error(e)


# Queue satellite job and wait for completion
try:
    job_id = f"{job_id_prefix}-{random.randint(0, 1000)}"
    print(f"Queuing satellite job {job_id}... ", end="", flush=True)
    satellite_job_poller = loop.run_until_complete(
        client.scenes.begin_create_satellite_data_ingestion_job(
            job_id=job_id,
            job=SatelliteDataIngestionJob(
                farmer_id=farmer_id,
                boundary_id=boundary_id,
                start_date_time=start_date_time,
                end_date_time=end_date_time,
                data=SatelliteData(
                    image_names=[
                        # "B01",
                        # "B02",
                        # "B03",
                        # "B04",
                        # "B05",
                        "LAI"
                    ]
                )
            ),
            polling=True
        )
    )
    print("Queued... Waiting for completion... ", end="", flush=True)
    satellite_job_result = loop.run_until_complete(
        satellite_job_poller.result()
    )
    print("Done")
    print(satellite_job_result.as_dict())
except HttpResponseError as e:
    print_error(e)
    raise


# Get scenes
try:
    print("Getting scenes list... ", end="", flush=True)
    scenes_aiter = client.scenes.list(
        boundary.farmer_id,
        boundary.id,
        start_date_time=start_date_time,
        end_date_time=end_date_time,
    )
    scenes = loop.run_until_complete(
        aiter_to_list(scenes_aiter)
    )
    print("Done")
    print(scenes)
    print(scenes[0].as_dict())
except HttpResponseError as e:
    print_error(e)
    raise

# Set up async functions to parallel download
async def download_image(client, file_link, root_dir):
    print(f"Async downloading image {file_link}... ")
    file_path = parse_file_path_from_file_link(file_link)
    out_path = Path(os.path.join(root_dir, file_path))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'wb') as tif_file:
        file_stream = await client.scenes.download(file_path)
        async for bits in file_stream:
            tif_file.write(bits)
    return str(out_path)

files_to_download = list()
for scene in scenes:
    for image_file in scene.image_files:
        files_to_download.append(image_file.file_link)

all_downloads = asyncio.gather(*[download_image(client, file_link, data_root_dir) for file_link in files_to_download])

loop.run_until_complete(all_downloads)

print("Downloads done")

loop.run_until_complete(credential.close())
loop.run_until_complete(client.close())
loop.close()