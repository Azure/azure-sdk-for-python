# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import datetime
from azure.core.exceptions import HttpResponseError
from azure.agrifood.farming.models import Farmer, SatelliteDataIngestionJob, SatelliteData
from testcase import FarmBeatsPowerShellPreparer, FarmBeatsTest
from isodate.tzinfo import Utc


class FarmBeatsSmokeTestCase(FarmBeatsTest):

    @FarmBeatsPowerShellPreparer()
    def test_farmer(self, agrifood_endpoint):
        client = self.create_client(agrifood_endpoint=agrifood_endpoint)

        farmer_id = self.generate_random_name("smoke-test-farmer")

        farmer = client.farmers.create_or_update(
            farmer_id=farmer_id,
            farmer=Farmer()
        )

        assert farmer.id == farmer_id
        assert farmer.e_tag
        assert farmer.created_date_time
        assert farmer.modified_date_time

        retrieved_farmer = client.farmers.get(farmer_id=farmer_id)
        assert farmer.id == retrieved_farmer.id
        assert farmer.e_tag == retrieved_farmer.e_tag
        assert farmer.created_date_time == retrieved_farmer.created_date_time
        assert farmer.modified_date_time == retrieved_farmer.modified_date_time

        client.farmers.delete(farmer_id=farmer_id)


    @FarmBeatsPowerShellPreparer()
    def test_boundary(self, agrifood_endpoint):
        client = self.create_client(agrifood_endpoint=agrifood_endpoint)

        farmer_id = self.generate_random_name("smoke-test-boundary-farmer")
        boundary_id = self.generate_random_name("smoke-test-boundary")

        farmer = client.farmers.create_or_update(
            farmer_id=farmer_id,
            farmer=Farmer()
        )
        boundary = self.create_boundary_if_not_exist(
            client, farmer_id, boundary_id)
        assert boundary == client.boundaries.get(
            farmer_id=farmer_id,
            boundary_id=boundary_id
        )
        self.delete_boundary(client, farmer_id, boundary_id)
        client.farmers.delete(farmer_id=farmer_id)
