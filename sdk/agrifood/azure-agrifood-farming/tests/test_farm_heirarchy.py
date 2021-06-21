# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest
from datetime import datetime
from azure.agrifood.farming.models import Farmer
from azure.core.exceptions import ResourceNotFoundError
from testcase import FarmBeatsPowerShellPreparer, FarmBeatsTest


class FarmHeirarchyTestCase(FarmBeatsTest):

    @FarmBeatsPowerShellPreparer()
    def test_farmer_operations(self, agrifood_endpoint):

        # Setup data
        farmer_id = self.generate_random_name("test-farmer-farmer-ops")
        farmer_name = "Test Farmer"
        farmer_description = "Farmer created during testing."
        farmer_status = "Sample Status"
        farmer_properties= {
            "foo": "bar",
            "numeric one": 1,
            1: "numeric key"
        }

        # Setup client
        client = self.create_client(agrifood_endpoint=agrifood_endpoint)

        # Create
        farmer = client.farmers.create_or_update(
            farmer_id=farmer_id,
            farmer=Farmer(
                name=farmer_name,
                description=farmer_description,
                status=farmer_status,
                properties=farmer_properties
            )
        )

        # Assert on immediate response
        assert farmer.id == farmer_id
        assert farmer.name == farmer_name
        assert farmer.description == farmer_description
        assert farmer.status == farmer_status

        assert len(farmer.properties) == 3
        assert farmer.properties["foo"] == "bar"
        assert farmer.properties["numeric one"] == 1
        assert farmer.properties["1"] == "numeric key"

        assert farmer.e_tag
        assert type(farmer.created_date_time) is datetime
        assert type(farmer.modified_date_time) is datetime

        # Retrieve created object
        retrieved_farmer = client.farmers.get(farmer_id=farmer_id)

        # Assert on retrieved object
        assert farmer == retrieved_farmer

        # Setup data for update
        farmer.name += " Updated"

        # Update
        updated_farmer = client.farmers.create_or_update(
            farmer_id=farmer_id,
            farmer=farmer
        )

        # Assert on immediate response
        assert farmer.name == updated_farmer.name
        assert farmer.created_date_time == updated_farmer.created_date_time

        # Retrieve updated object
        updated_retrieved_farmer = client.farmers.get(farmer_id=farmer_id)

        # Assert updated object
        assert updated_retrieved_farmer == updated_farmer

        # Delete
        client.farmers.delete(farmer_id=farmer_id)

        # Assert object doesn't exist anymore
        with pytest.raises(ResourceNotFoundError):
            client.farmers.get(farmer_id=farmer_id)
