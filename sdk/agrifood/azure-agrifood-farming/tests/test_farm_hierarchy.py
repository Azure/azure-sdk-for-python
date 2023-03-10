# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest
from datetime import datetime
from dateutil.parser import parse
from azure.core.exceptions import ResourceNotFoundError
from devtools_testutils import recorded_by_proxy, set_custom_default_matcher
from testcase import FarmBeatsPowerShellPreparer, FarmBeatsTestCase


class TestFarmHierarchy(FarmBeatsTestCase):    
    @FarmBeatsPowerShellPreparer()
    @recorded_by_proxy
    def test_party_operations(self, **kwargs):
        set_custom_default_matcher(ignored_headers="Accept-Encoding")
        agrifood_endpoint = kwargs.pop("agrifood_endpoint")
        
        # Setup data
        party_id = "test-party-39574"
        party_request = {
            "name": "Test Party",
            "description": "Party created during testing.",
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
        party_response = client.parties.create_or_update(
            party_id=party_id,
            party=party_request
        )

        # Assert on immediate response
        assert party_response["id"] == party_id
        assert party_response["name"] == party_response["name"]
        assert party_response["description"] == party_response["description"]
        assert party_response["status"] == party_response["status"]

        assert len(party_response["properties"]) == 3
        assert party_response["properties"]["foo"] == "bar"
        assert party_response["properties"]["numeric one"] == 1
        assert party_response["properties"]["1"] == "numeric key"

        assert party_response["eTag"]
        assert type(parse(party_response["createdDateTime"])) is datetime
        assert type(parse(party_response["modifiedDateTime"])) is datetime

        # Retrieve created object
        retrieved_party = client.parties.get(
            party_id=party_id)

        # Assert on retrieved object
        assert retrieved_party["id"] == party_id

        # Setup data for update
        party_request["name"] += " Updated"

        # Update
        updated_party = client.parties.create_or_update(
            party_id=party_id,
            party=party_request
        )

        # Assert on immediate response
        # Assert on immediate response
        assert updated_party["name"] == party_request["name"]
        assert updated_party["createdDateTime"] == party_response["createdDateTime"]

        # Retrieve updated object
        retrieved_party = client.parties.get(party_id=party_id)

        # Assert updated object
        assert retrieved_party == updated_party

        # Delete
        client.parties.delete(party_id=party_id)

        # Assert object doesn't exist anymore
        with pytest.raises(ResourceNotFoundError):
            client.parties.get(party_id=party_id)
