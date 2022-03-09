# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest
import datetime
from azure.core.exceptions import HttpResponseError
from azure.agrifood.farming.models import Farmer, SatelliteDataIngestionJob, SatelliteData
from testcase_async import FarmBeatsTestAsync
from testcase import FarmBeatsPowerShellPreparer
from isodate.tzinfo import Utc
from random import randint


class FarmBeatsSmokeTestCaseAsync(FarmBeatsTestAsync):

    @pytest.mark.live_test_only
    @FarmBeatsPowerShellPreparer()
    async def test_satellite_flow(self, agrifood_endpoint):
        # not running in playback for now because the binary body is not being scrubbed properly

        # Setup data
        common_id_prefix = "satellite-flow-async-"
        farmer_id_prefix = common_id_prefix + "test-farmer"
        boundary_id_prefix = common_id_prefix + "test-boundary"
        job_id_prefix = common_id_prefix + "job"

        job_id = self.generate_random_name(job_id_prefix)
        farmer_id = self.generate_random_name(farmer_id_prefix)
        boundary_id = self.generate_random_name(boundary_id_prefix)

        start_date_time = datetime.datetime(2020, 1, 1, tzinfo=Utc())
        end_date_time = datetime.datetime(2020, 12, 31, tzinfo=Utc())

        # Setup client
        client = self.create_client(agrifood_endpoint=agrifood_endpoint)

        # Create farmer
        farmer = await client.farmers.create_or_update(farmer_id=farmer_id, farmer=Farmer())

        # Create boundary if not exists
        boundary = await self.create_boundary_if_not_exist(client, farmer_id, boundary_id)

        # Create satellite job
        satellite_job_poller = await client.scenes.begin_create_satellite_data_ingestion_job(
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
        satellite_job = await satellite_job_poller.result()

        assert satellite_job.farmer_id == farmer_id

        # in async, we're getting binary form of body, so can't scrub job id from binary
        assert job_id in satellite_job.id
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

        scenes_list = [scene async for scene in scenes]

        # Assert scenes got created
        assert len(scenes_list) > 0
        for scene in scenes_list:
            assert scene.farmer_id == farmer_id
            assert scene.boundary_id == boundary_id
