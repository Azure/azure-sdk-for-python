# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest
import os
from datetime import datetime
from dateutil.parser import parse
from azure.core.exceptions import ResourceNotFoundError
from devtools_testutils import AzureRecordedTestCase
from devtools_testutils.aio import recorded_by_proxy_async
from testcase_async import FarmBeatsAsyncTestCase
from testcase import FarmBeatsPowerShellPreparer


class TestFarmHeirarchyAsync(FarmBeatsAsyncTestCase):    
    @FarmBeatsPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_farmer_operations(self, **kwargs):
        agrifood_endpoint = kwargs.pop("agrifood_endpoint")
        
        # Setup data
        farmer_id = "test-farmer-farmer-ops"
        farmer_request = {
            "name": "Test Farmer",
            "description": "Farmer created during testing.",
            "status": "Sample Status",
            "properties": {
                "foo": "bar",
                "numeric one": 1,
                1: "numeric key"
            }
        }

        # Setup client
        client = self.create_client(agrifood_endpoint=agrifood_endpoint)

        # Create
        farmer_response = await client.farmers.create_or_update(
            farmer_id=farmer_id,
            farmer=farmer_request
        )

        # Assert on immediate response
        assert farmer_response["id"] == farmer_id
        assert farmer_response["name"] == farmer_response["name"]
        assert farmer_response["description"] == farmer_response["description"]
        assert farmer_response["status"] == farmer_response["status"]

        assert len(farmer_response["properties"]) == 3
        assert farmer_response["properties"]["foo"] == "bar"
        assert farmer_response["properties"]["numeric one"] == 1
        assert farmer_response["properties"]["1"] == "numeric key"

        assert farmer_response["eTag"]
        assert type(parse(farmer_response["createdDateTime"])) is datetime
        assert type(parse(farmer_response["modifiedDateTime"])) is datetime

        # Retrieve created object
        retrieved_farmer = await client.farmers.get(farmer_id=farmer_id)

        # Assert on retrieved object
        assert retrieved_farmer["id"] == farmer_id

        # Setup data for update
        farmer_request["name"] += " Updated"

        # Update
        updated_farmer = await client.farmers.create_or_update(
            farmer_id=farmer_id,
            farmer=farmer_request
        )

        # Assert on immediate response
        # Assert on immediate response
        assert updated_farmer["name"] == farmer_request["name"]
        assert updated_farmer["createdDateTime"] == farmer_response["createdDateTime"]

        # Retrieve updated object
        retrieved_farmer = await client.farmers.get(farmer_id=farmer_id)

        # Assert updated object
        assert retrieved_farmer == updated_farmer

        # Delete
        await client.farmers.delete(farmer_id=farmer_id)

        # Assert object doesn't exist anymore
        with pytest.raises(ResourceNotFoundError):
            await client.farmers.get(farmer_id=farmer_id)
