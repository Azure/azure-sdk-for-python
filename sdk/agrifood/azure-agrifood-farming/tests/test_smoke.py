# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import isodate
import json
import datetime
from azure.core.exceptions import HttpResponseError
from azure.agrifood.farming import FarmBeatsClient
from azure.agrifood.farming.models import Farmer, SatelliteDataIngestionJob, SatelliteData
from testcase import FarmBeatsPowerShellPreparer, FarmBeatsTest


class FarmBeatsSmokeTestCase(FarmBeatsTest):

    @FarmBeatsPowerShellPreparer()
    def test_farmer(self, farmbeats_endpoint, farmbeats_farmer_id):
        client = self.create_client(farmbeats_endpoint=farmbeats_endpoint)
        farmer = client.farmers.create_or_update(
            farmer_id=farmbeats_farmer_id,
            body=Farmer()
        )

        assert farmer.id == farmbeats_farmer_id
        assert farmer.e_tag
        assert farmer.created_date_time
        assert farmer.modified_date_time

        retrieved_farmer = client.farmers.get(farmer_id=farmbeats_farmer_id)
        assert farmer.id == retrieved_farmer.id
        assert farmer.e_tag == retrieved_farmer.e_tag
        assert farmer.created_date_time == retrieved_farmer.created_date_time
        assert farmer.modified_date_time == retrieved_farmer.modified_date_time

    @FarmBeatsPowerShellPreparer()
    def test_boundary(self, farmbeats_endpoint, farmbeats_farmer_id, farmbeats_boundary_id):
        client = self.create_client(farmbeats_endpoint=farmbeats_endpoint)
        boundary_id = farmbeats_boundary_id + "boundary"
        boundary = self.create_boundary_if_not_exist(client, farmbeats_farmer_id, boundary_id)
        assert boundary == client.boundaries.get(
            farmer_id=farmbeats_farmer_id,
            boundary_id=boundary_id
        )
        self.delete_boundary(client, farmbeats_farmer_id, boundary_id)

    @FarmBeatsPowerShellPreparer()
    def test_satellite_job(self, farmbeats_endpoint, farmbeats_farmer_id, farmbeats_boundary_id, farmbeats_job_id_prefix):
        client = self.create_client(farmbeats_endpoint=farmbeats_endpoint)
        boundary_id = "{}-scenes".format(farmbeats_boundary_id)
        try:
            # we create a boundary. If it fails, means that we've already created it, so ignoring
            self.create_boundary_if_not_exist(client, farmbeats_farmer_id, boundary_id)
        except HttpResponseError:
            pass
        job_id = self.generate_random_name(farmbeats_job_id_prefix)

        start_date_time = datetime.datetime(2020, 1, 1)
        end_date_time = datetime.datetime(2020, 12, 31)

        satellite_job_poller = client.scenes.begin_create_satellite_data_ingestion_job(
            job_id=job_id,
            body=SatelliteDataIngestionJob(
                farmer_id=farmbeats_farmer_id,
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
        satellite = satellite_job_poller.result()
        assert satellite.farmer_id == farmbeats_farmer_id
        assert satellite.id == job_id
        assert satellite.boundary_id == boundary_id
        assert satellite.start_date_time == start_date_time
        assert satellite.end_date_time == end_date_time

    @FarmBeatsPowerShellPreparer()
    def test_scenes(self, farmbeats_endpoint, farmbeats_farmer_id, farmbeats_boundary_id):
        client = self.create_client(farmbeats_endpoint=farmbeats_endpoint)
        boundary_id = "{}-scenes".format(farmbeats_boundary_id)
        start_date_time = datetime.datetime(2020, 1, 1)
        end_date_time = datetime.datetime(2020, 12, 31)
        scenes = client.scenes.list(
            farmer_id=farmbeats_farmer_id,
            boundary_id=boundary_id,
            start_date_time=start_date_time,
            end_date_time=end_date_time,
        )
        for scene in scenes:
            assert scene.farmer_id == farmbeats_farmer_id
            assert scene.boundary_id == boundary_id

    @FarmBeatsPowerShellPreparer()
    def test_download_image(self, farmbeats_endpoint, farmbeats_farmer_id, farmbeats_boundary_id):
        client = self.create_client(farmbeats_endpoint=farmbeats_endpoint)
        boundary_id = "{}-scenes".format(farmbeats_boundary_id)
        scenes = [f for f in client.scenes.list(farmer_id=farmbeats_farmer_id, boundary_id=boundary_id)]

        assert scenes
