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
from random import randint

class FarmBeatsSmokeTestCaseAsync(FarmBeatsTestAsync):

    @FarmBeatsPowerShellPreparer()
    async def test_farmer(self, agrifood_endpoint):
        client = self.create_client(agrifood_endpoint=agrifood_endpoint)

        farmer_id = self.generate_random_name("async-test-farmer")

        farmer = await client.farmers.create_or_update(
            farmer_id=farmer_id,
            farmer=Farmer()
        )

        assert farmer.id == farmer_id
        assert farmer.e_tag
        assert farmer.created_date_time
        assert farmer.modified_date_time

        retrieved_farmer = await client.farmers.get(farmer_id=farmer_id)
        assert farmer.id == retrieved_farmer.id
        assert farmer.e_tag == retrieved_farmer.e_tag
        assert farmer.created_date_time == retrieved_farmer.created_date_time
        assert farmer.modified_date_time == retrieved_farmer.modified_date_time

        await client.farmers.delete(farmer_id=farmer_id)

    @FarmBeatsPowerShellPreparer()
    async def test_boundary(self, agrifood_endpoint):
        client = self.create_client(agrifood_endpoint=agrifood_endpoint)
        
        boundary_id = self.generate_random_name("async-test-boundary")
        farmer_id = self.generate_random_name("async-test-boundary-farmer")
        
        farmer = await client.farmers.create_or_update(farmer_id=farmer_id, farmer=Farmer())
        boundary = await self.create_boundary_if_not_exist(client, farmer_id, boundary_id)
        assert boundary == await client.boundaries.get(
            farmer_id=farmer_id,
            boundary_id=boundary_id
        )
        await self.delete_boundary(client, farmer_id, boundary_id)
        await client.farmers.delete(farmer_id=farmer_id)