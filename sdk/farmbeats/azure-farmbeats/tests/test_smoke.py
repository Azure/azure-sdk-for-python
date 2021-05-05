# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import isodate
import json
from dotenv import find_dotenv, load_dotenv
from azure.core.exceptions import HttpResponseError
from azure.identity import ClientSecretCredential
from azure.farmbeats import FarmBeatsClient
from testcase import FarmBeatsPowerShellPreparer, FarmBeatsTest
import asyncio

import datetime
from pytz import utc
from urllib.parse import unquote, urlparse, parse_qs
import random
from pathlib import Path
import os

# load_dotenv(find_dotenv())



# client = FarmBeatsClient(
#     endpoint=os.environ["FARMBEATS_ENDPOINT"],
#     credential=credential,
# )

# msrest_serializer = msrest.Serializer()
# # Define contstants for this script

# data_root_dir = "./asyncio_test_downloads"

# # Utility funcitons
# def print_error(exception):
#     print("Error:")
#     try:
#         pprint(exception.model.as_dict())
#     except:
#         print(exception.response.body())
#         print("Couldn't print error info")


# def parse_file_path_from_file_link(file_link):
#     return parse_qs(urlparse(file_link).query)['filePath'][0]


# async def aiter_to_list(aiter):
#     l = list()
#     async for obj in aiter:
#         l.append(obj)
#     return l

class FarmBeatsSmokeTestCase(FarmBeatsTest):

    @FarmBeatsPowerShellPreparer()
    def test_farmer(self, farmbeats_endpoint, farmbeats_farmer_id):
        client = self.create_client(farmbeats_endpoint=farmbeats_endpoint)
        farmer = client.farmers.create_or_update(
            farmer_id=farmbeats_farmer_id,
            farmer={}
        )
        print(farmer)
        assert farmer["id"] == farmbeats_farmer_id
        assert farmer["eTag"]
        assert farmer["createdDateTime"]
        assert farmer["modifiedDateTime"]

        retrieved_farmer = client.farmers.get(farmer_id=farmbeats_farmer_id)
        assert farmer == retrieved_farmer

    def _create_boundary(self, client, farmbeats_farmer_id, farmbeats_boundary_id):
        try:
            return client.boundaries.create_or_update(
                farmer_id=farmbeats_farmer_id,
                boundary_id=farmbeats_boundary_id,
                boundary={
                    "description": "Created by SDK",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
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
                    }
                }
            )
        except HttpResponseError as e:
            raise ValueError(json.loads(e.response.text()))

    def _delete_boundary(self, client, farmbeats_farmer_id, farmbeats_boundary_id):
        client.boundaries.delete(farmer_id=farmbeats_farmer_id, boundary_id=farmbeats_boundary_id)

    @FarmBeatsPowerShellPreparer()
    def test_boundary(self, farmbeats_endpoint, farmbeats_farmer_id, farmbeats_boundary_id):
        client = self.create_client(farmbeats_endpoint=farmbeats_endpoint)
        boundary_id = farmbeats_boundary_id + "boundary"
        boundary = self._create_boundary(client, farmbeats_farmer_id, boundary_id)
        assert boundary == client.boundaries.get(
            farmer_id=farmbeats_farmer_id,
            boundary_id=boundary_id
        )
        self._delete_boundary(client, farmbeats_farmer_id, boundary_id)

    @FarmBeatsPowerShellPreparer()
    def test_satellite_job(self, farmbeats_endpoint, farmbeats_farmer_id, farmbeats_boundary_id, farmbeats_job_id_prefix):
        client = self.create_client(farmbeats_endpoint=farmbeats_endpoint)
        boundary_id = "{}-scenes".format(farmbeats_boundary_id)
        job_id = "{}-{}".format(farmbeats_job_id_prefix, random.randint(0, 1000))

        start_date_time = datetime.datetime(2020, 1, 1, tzinfo=utc)
        end_date_time = datetime.datetime(2020, 12, 31, tzinfo=utc)

        job = {
            "boundaryId": boundary_id,
            "data": {
                "imageNames": [
                    # "B01",
                    # "B02",
                    # "B03",
                    # "B04",
                    # "B05",
                    "LAI"
                ]
            },
            "farmerId": farmbeats_farmer_id,
            "startDateTime": start_date_time,
            "endDateTime": end_date_time,
        }

        satellite_job_poller = client.scenes.begin_create_satellite_data_ingestion_job(
            job_id=job_id,
            job=job,
        )
        satellite = satellite_job_poller.result()
        assert satellite['farmerId'] == farmbeats_farmer_id
        assert satellite['id'] == job_id
        assert satellite['boundaryId'] == boundary_id
        assert isodate.parse_datetime(satellite['startDateTime']) == start_date_time
        assert isodate.parse_datetime(satellite['endDateTime']) == end_date_time

    @FarmBeatsPowerShellPreparer()
    def test_scenes(self, farmbeats_endpoint, farmbeats_farmer_id, farmbeats_boundary_id):
        client = self.create_client(farmbeats_endpoint=farmbeats_endpoint)
        boundary_id = "{}-scenes".format(farmbeats_boundary_id)
        start_date_time = datetime.datetime(2020, 1, 1, tzinfo=utc)
        end_date_time = datetime.datetime(2020, 12, 31, tzinfo=utc)
        scenes = client.scenes.list(
            farmer_id=farmbeats_farmer_id,
            boundary_id=boundary_id,
            start_date_time=start_date_time,
            end_date_time=end_date_time,
        )
        for scene in scenes:
            assert scene['farmerId'] == farmbeats_farmer_id
            assert scene['boundaryId'] == boundary_id

    @FarmBeatsPowerShellPreparer()
    def test_download_image(self, farmbeats_endpoint, farmbeats_farmer_id, farmbeats_boundary_id):
        client: FarmBeatsClient = self.create_client(farmbeats_endpoint=farmbeats_endpoint)
        boundary_id = "{}-scenes".format(farmbeats_boundary_id)
        scenes = [f for f in client.scenes.list(farmer_id=farmbeats_farmer_id, boundary_id=boundary_id)]

        assert scenes
        # let's just download the first file link
        first_file_link = scenes[0]['imageFiles'][0]['fileLink']
        try:
            my_bytes = [b for b in client.scenes.download(file_path=first_file_link)]
        except HttpResponseError as e:
            raise ValueError(json.loads(e.response.text()))
        assert my_bytes
# # Set up async functions to parallel download
# async def download_image(client, file_link, root_dir):
#     print(f"Async downloading image {file_link}... ")
#     file_path = parse_file_path_from_file_link(file_link)
#     out_path = Path(os.path.join(root_dir, file_path))
#     out_path.parent.mkdir(parents=True, exist_ok=True)
#     with open(out_path, 'wb') as tif_file:
#         file_stream = await client.scenes.download(file_path)
#         async for bits in file_stream:
#             tif_file.write(bits)
#     # print("Done")
#     return str(out_path)

# files_to_download = list()
# for scene in scenes:
#     for image_file in scene.image_files:
#         files_to_download.append(image_file.file_link)

# all_downloads = asyncio.gather(*[download_image(client, file_link, data_root_dir) for file_link in files_to_download])

# loop.run_until_complete(all_downloads)

# print("apparently done")

# loop.run_until_complete(credential.close())
# loop.run_until_complete(client.close())
# loop.close()