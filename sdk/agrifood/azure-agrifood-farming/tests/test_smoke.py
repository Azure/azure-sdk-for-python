# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import datetime
from azure.core.exceptions import HttpResponseError
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
