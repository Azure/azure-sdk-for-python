# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import datetime
from azure.core.exceptions import HttpResponseError
from azure.agrifood.farming.models import Farmer, SatelliteDataIngestionJob, SatelliteData
from testcase_async import FarmBeatsTestAsync
from testcase import FarmBeatsPowerShellPreparer
from isodate.tzinfo import Utc

class FarmBeatsSmokeTestCaseAsync(FarmBeatsTestAsync):

    @FarmBeatsPowerShellPreparer()
    async def test_farmer(self, agrifood_endpoint, agrifood_farmer_id):
        client = self.create_client(agrifood_endpoint=agrifood_endpoint)
        farmer = await client.farmers.create_or_update(
            farmer_id=agrifood_farmer_id,
            body=Farmer()
        )

        assert farmer.id == agrifood_farmer_id
        assert farmer.e_tag
        assert farmer.created_date_time
        assert farmer.modified_date_time

        retrieved_farmer = await client.farmers.get(farmer_id=agrifood_farmer_id)
        assert farmer.id == retrieved_farmer.id
        assert farmer.e_tag == retrieved_farmer.e_tag
        assert farmer.created_date_time == retrieved_farmer.created_date_time
        assert farmer.modified_date_time == retrieved_farmer.modified_date_time

    @FarmBeatsPowerShellPreparer()
    async def test_boundary(self, agrifood_endpoint, agrifood_farmer_id, agrifood_boundary_id):
        client = self.create_client(agrifood_endpoint=agrifood_endpoint)
        boundary_id = agrifood_boundary_id + "boundary"
        boundary = await self.create_boundary_if_not_exist(client, agrifood_farmer_id, boundary_id)
        assert boundary == await client.boundaries.get(
            farmer_id=agrifood_farmer_id,
            boundary_id=boundary_id
        )
        self.delete_boundary(client, agrifood_farmer_id, boundary_id)

    @FarmBeatsPowerShellPreparer()
    async def test_satellite_job(self, agrifood_endpoint, agrifood_farmer_id, agrifood_boundary_id, agrifood_job_id_prefix):
        client = self.create_client(agrifood_endpoint=agrifood_endpoint)
        boundary_id = "{}-scenes".format(agrifood_boundary_id)
        try:
            # we create a boundary. If it fails, means that we've already created it, so ignoring
            self.create_boundary_if_not_exist(client, agrifood_farmer_id, boundary_id)
        except HttpResponseError:
            pass
        job_id = self.generate_random_name(agrifood_job_id_prefix)

        start_date_time = datetime.datetime(2020, 1, 1, tzinfo=Utc())
        end_date_time = datetime.datetime(2020, 12, 31, tzinfo=Utc())

        satellite_job_poller = await client.scenes.begin_create_satellite_data_ingestion_job(
            job_id=job_id,
            body=SatelliteDataIngestionJob(
                farmer_id=agrifood_farmer_id,
                boundary_id=boundary_id,
                start_date_time=start_date_time,
                end_date_time=end_date_time,
                data=SatelliteData(
                    image_names=[
                        "LAI"
                    ]
                )
            ),
        )
        satellite = await satellite_job_poller.result()
        assert satellite.farmer_id == agrifood_farmer_id
        assert satellite.id == job_id
        assert satellite.boundary_id == boundary_id
        assert satellite.start_date_time == start_date_time
        assert satellite.end_date_time == end_date_time

    @FarmBeatsPowerShellPreparer()
    async def test_scenes(self, agrifood_endpoint, agrifood_farmer_id, agrifood_boundary_id):
        client = self.create_client(agrifood_endpoint=agrifood_endpoint)
        boundary_id = "{}-scenes".format(agrifood_boundary_id)
        start_date_time = datetime.datetime(2020, 1, 1, tzinfo=Utc())
        end_date_time = datetime.datetime(2020, 12, 31, tzinfo=Utc())
        scenes = client.scenes.list(
            farmer_id=agrifood_farmer_id,
            boundary_id=boundary_id,
            start_date_time=start_date_time,
            end_date_time=end_date_time,
        )
        async for scene in scenes:
            assert scene.farmer_id == agrifood_farmer_id
            assert scene.boundary_id == boundary_id

    @FarmBeatsPowerShellPreparer()
    async def test_download_image(self, agrifood_endpoint, agrifood_farmer_id, agrifood_boundary_id):
        client = self.create_client(agrifood_endpoint=agrifood_endpoint)
        boundary_id = "{}-scenes".format(agrifood_boundary_id)
        scenes = [f async for f in client.scenes.list(farmer_id=agrifood_farmer_id, boundary_id=boundary_id)]

        assert scenes
