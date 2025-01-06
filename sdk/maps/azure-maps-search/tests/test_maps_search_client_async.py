# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os

from azure.core.credentials import AzureKeyCredential
from azure.maps.search.aio import MapsSearchClient
from azure.maps.search import BoundaryResultType, Resolution
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import AzureRecordedTestCase, is_live

from search_preparer import MapsSearchPreparer


# cSpell:disable
class TestMapsSearchClientAsync(AzureRecordedTestCase):
    def setup_method(self, method):
        self.client = MapsSearchClient(
            credential=AzureKeyCredential(os.environ.get("AZURE_SUBSCRIPTION_KEY", "AzureMapsSubscriptionKey"))
        )
        assert self.client is not None

    @MapsSearchPreparer()
    @recorded_by_proxy_async
    async def test_geocode(self):
        async with self.client:
            result = await self.client.get_geocoding(query="15127 NE 24th Street, Redmond, WA 98052")

            assert result.get("features", False)
            coordinates = result["features"][0]["geometry"]["coordinates"]
            longitude = coordinates[0]
            latitude = coordinates[1]

            assert longitude == -122.138669
            assert latitude == 47.630359

    @MapsSearchPreparer()
    @recorded_by_proxy_async
    async def test_geocode_batch(self):
        async with self.client:
            result = await self.client.get_geocoding_batch(
                {
                    "batchItems": [
                        {"query": "400 Broad St, Seattle, WA 98109"},
                        {"query": "15127 NE 24th Street, Redmond, WA 98052"},
                    ],
                },
            )

            assert "batchItems" in result and result["batchItems"]

            expected_coordinates = [(-122.349309, 47.620498), (-122.138669, 47.630359)]

            for i, item in enumerate(result["batchItems"]):
                assert item.get("features")

                coordinates = item["features"][0]["geometry"]["coordinates"]
                longitude, latitude = coordinates

                expected_longitude, expected_latitude = expected_coordinates[i]

                assert longitude == expected_longitude
                assert latitude == expected_latitude

    @MapsSearchPreparer()
    @recorded_by_proxy_async
    async def test_reverse_geocode(self):
        async with self.client:
            result = await self.client.get_reverse_geocoding(coordinates=[-122.138679, 47.630356])
            assert result.get("features", False)
            props = result["features"][0].get("properties", {})

            assert props.get("address", False)
            assert (
                props["address"].get("formattedAddress", "No formatted address found")
                == "2265 152nd Ave NE, Redmond, Washington 98052, United States"
            )

    @MapsSearchPreparer()
    @recorded_by_proxy_async
    async def test_reverse_geocode_batch(self):
        async with self.client:
            result = await self.client.get_reverse_geocoding_batch(
                {
                    "batchItems": [
                        {"coordinates": [-122.349309, 47.620498]},
                        {"coordinates": [-122.138679, 47.630356]},
                    ],
                },
            )

            assert result.get("batchItems", False)

            expected_addresses = [
                "400 Broad St, Seattle, Washington 98109, United States",
                "2265 152nd Ave NE, Redmond, Washington 98052, United States",
            ]

            for i, item in enumerate(result["batchItems"]):
                features = item.get("features", [])
                assert features

                props = features[0].get("properties", {})
                assert props and props.get("address", False)

                formatted_address = props["address"].get(
                    "formattedAddress", f"No formatted address for item {i + 1} found"
                )
                assert formatted_address == expected_addresses[i]

    @MapsSearchPreparer()
    @recorded_by_proxy_async
    async def test_get_polygon(self):
        async with self.client:
            result = await self.client.get_polygon(
                **{
                    "coordinates": [-122.204141, 47.61256],
                    "result_type": BoundaryResultType.LOCALITY,
                    "resolution": Resolution.SMALL,
                }
            )

            assert result.get("geometry", False) and result["geometry"].get("geometries", False)
