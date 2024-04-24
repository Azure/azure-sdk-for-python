# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
from azure.core.credentials import AccessToken, AzureKeyCredential
from azure.maps.search import MapsSearchClient
from azure.maps.search._generated.models import GeocodingBatchRequestItem, GeocodingBatchRequestBody, \
    ReverseGeocodingBatchRequestItem, ReverseGeocodingBatchRequestBody
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy
from search_preparer import MapsSearchPreparer

# cSpell:disable
class TestMapsSearchClient(AzureRecordedTestCase):
    def setup_method(self, method):
        self.client = MapsSearchClient(
            credential=AzureKeyCredential("xxxxxxxx-xxxx-xxxx")
        )
        assert self.client is not None

    @MapsSearchPreparer()
    def test_geocode(self):
        result = self.client.get_geocoding(query="15127 NE 24th Street, Redmond, WA 98052")

        assert len(result.features) > 0
        coordinates = result.features[0].geometry.coordinates
        longitude = coordinates[0]
        latitude = coordinates[1]

        assert longitude == -122.138679
        assert latitude == 47.630356

    @MapsSearchPreparer()
    def test_geocode_batch(self):
        request_item1 = GeocodingBatchRequestItem(query="15127 NE 24th Street, Redmond, WA 98052", top=5)
        request_item2 = GeocodingBatchRequestItem(query="15127 NE 24th Street, Redmond, WA 98052", top=5)

        batch_request_body = GeocodingBatchRequestBody(batch_items=[request_item1, request_item2])

        result = self.client.get_geocoding_batch(batch_request_body)

        assert len(result.batch_items) == 2

        result1 = result.batch_items[0]
        result2 = result.batch_items[1]

        assert len(result1.features) == 1
        coordinates1 = result1.features[0].geometry.coordinates
        longitude1 = coordinates1[0]
        latitude1 = coordinates1[1]

        assert longitude1 == -122.138679
        assert latitude1 == 47.630356

        assert len(result2.features) == 1
        coordinates2 = result2.features[0].geometry.coordinates
        longitude2 = coordinates2[0]
        latitude2 = coordinates2[1]

        assert longitude2 == -122.138679
        assert latitude2 == 47.630356

    @MapsSearchPreparer()
    def test_reverse_geocode(self):
        result = self.client.get_reverse_geocoding(coordinates=[-122.138679, 47.630356])
        assert len(result.features) == 1
        address = result.features[0].properties.address
        assert address.formatted_address == "2265 152nd Ave NE, Redmond, WA 98052, United States"

    @MapsSearchPreparer()
    def test_reverse_geocode_batch(self):
        coordinates1 = ReverseGeocodingBatchRequestItem(coordinates=[-122.138679, 47.630356])
        coordinates2 = ReverseGeocodingBatchRequestItem(coordinates=[-122.138679, 47.630356])
        reverse_geocode_batch_request = ReverseGeocodingBatchRequestBody(batch_items=[coordinates1, coordinates2])

        result = self.client.get_reverse_geocoding_batch(reverse_geocode_batch_request)
        assert len(result.batch_items) == 2
        result1 = result.batch_items[0]
        result2 = result.batch_items[1]

        assert len(result1.features) == 1
        address1 = result1.features[0].properties.address
        assert address1.formatted_address == "2265 152nd Ave NE, Redmond, WA 98052, United States"

        assert len(result2.features) == 1
        address2 = result2.features[0].properties.address
        assert address2.formatted_address == "2265 152nd Ave NE, Redmond, WA 98052, United States"
