# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from datetime import datetime
from azure.agrifood.farming.models import Farmer, SatelliteDataIngestionJob, SatelliteData
from azure.core.exceptions import ResourceNotFoundError
from testcase import FarmBeatsPowerShellPreparer, FarmBeatsTest
from random import randint
from isodate.tzinfo import Utc


class FarmBeatsSmokeTestCase(FarmBeatsTest):

    @FarmBeatsPowerShellPreparer()
    def test_satellite_flow(self, agrifood_endpoint):

        # Setup data
        common_id_prefix = "satellite-flow-"
        farmer_id_prefix = common_id_prefix + "test-farmer"
        boundary_id_prefix = common_id_prefix + "test-boundary"
        job_id_prefix = common_id_prefix + "job"

        job_id = self.generate_random_name(job_id_prefix)
        farmer_id = self.generate_random_name(farmer_id_prefix)
        boundary_id = self.generate_random_name(boundary_id_prefix)

        start_date_time = datetime(2020, 1, 1, tzinfo=Utc())
        end_date_time = datetime(2020, 1, 31, tzinfo=Utc())

        # Setup client
        client = self.create_client(agrifood_endpoint=agrifood_endpoint)

        # Create farmer
        farmer = client.farmers.create_or_update(farmer_id=farmer_id, farmer=Farmer())

        # Create boundary if not exists
        self.create_boundary_if_not_exist(client, farmer_id, boundary_id)

        # Create satellite job
        satellite_job_poller = client.scenes.begin_create_satellite_data_ingestion_job(
            job_id=job_id,
            job=SatelliteDataIngestionJob(
                farmer_id=farmer_id,
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

        # Get terminal job state and assert
        satellite_job = satellite_job_poller.result()

        assert satellite_job.farmer_id == farmer_id
        assert satellite_job.id == job_id
        assert satellite_job.boundary_id == boundary_id
        assert satellite_job.start_date_time == start_date_time
        assert satellite_job.end_date_time == end_date_time
        assert satellite_job.status == "Succeeded"

        # Get corresponding scenes
        scenes = client.scenes.list(
            farmer_id=farmer_id,
            boundary_id=boundary_id,
            start_date_time=start_date_time,
            end_date_time=end_date_time,
        )

        scenes_list = list(scenes)

        # Assert scenes got created
        assert len(scenes_list) > 0
        for scene in scenes_list:
            assert scene.farmer_id == farmer_id
            assert scene.boundary_id == boundary_id

        # TODO: What's a good way to assert the downloaded files?
