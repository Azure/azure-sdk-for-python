# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from datetime import datetime
from dateutil.parser import parse
from testcase import FarmBeatsPowerShellPreparer, FarmBeatsTestCase
from isodate.tzinfo import Utc
from devtools_testutils import recorded_by_proxy


class TestFarmBeatsSmoke(FarmBeatsTestCase):

    @FarmBeatsPowerShellPreparer()
    @recorded_by_proxy
    def test_farmer(self, **kwargs):
        agrifood_endpoint = kwargs.pop("agrifood_endpoint")
        client = self.create_client(agrifood_endpoint=agrifood_endpoint)

        farmer_id = "smoke-test-farmer"

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
        farmer_response = client.farmers.create_or_update(
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

        client.farmers.delete(farmer_id=farmer_id)


    @FarmBeatsPowerShellPreparer()
    @recorded_by_proxy
    def test_boundary(self, **kwargs):
        agrifood_endpoint = kwargs.pop("agrifood_endpoint")
        client = self.create_client(agrifood_endpoint=agrifood_endpoint)

        farmer_id = "smoke-test-farmer"
        boundary_id = "smoke-test-boundary"

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
        farmer = client.farmers.create_or_update(
            farmer_id=farmer_id,
            farmer=farmer_request
        )
        
        boundary = client.boundaries.create_or_update(
            farmer_id=farmer_id,
            boundary_id=boundary_id,
            boundary={
                "geometry":
                {
                    "type": "Polygon",
                    "coordinates":
                        [
                            [
                                [73.70457172393799, 20.545385304358106],
                                [73.70457172393799, 20.545385304358106],
                                [73.70448589324951, 20.542411534243367],
                                [73.70877742767334, 20.541688176010233],
                                [73.71023654937744, 20.545083911372505],
                                [73.70663166046143, 20.546992723579137],
                                [73.70457172393799, 20.545385304358106],
                            ]
                        ]
                },
                "status": "<string>",
                "name": "<string>",
                "description": "<string>"
            }
        )

        assert boundary == client.boundaries.get(
            farmer_id=farmer_id,
            boundary_id=boundary_id
        )
        client.boundaries.delete(farmer_id=farmer_id, boundary_id=boundary_id)
        client.farmers.delete(farmer_id=farmer_id)
