# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os

from azure.core.credentials import AzureKeyCredential
from azure.maps.search import AzureMapsSearchClient
from azure.maps.search import BoundaryResultType, Resolution
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy, is_live

from search_preparer import MapsSearchPreparer


# cSpell:disable
class TestMapsSearchClient(AzureRecordedTestCase):
    def setup_method(self, method):
        self.client = AzureMapsSearchClient(
            credential=AzureKeyCredential(os.environ.get('AZURE_SUBSCRIPTION_KEY', "AzureMapsSubscriptionKey"))
        )
        assert self.client is not None

    @MapsSearchPreparer()
    @recorded_by_proxy
    def test_geocode(self):
        result = self.client.get_geocoding(query="15127 NE 24th Street, Redmond, WA 98052")

        assert 'features' in result and result['features']
        coordinates = result['features'][0]['geometry']['coordinates']
        longitude = coordinates[0]
        latitude = coordinates[1]

        assert longitude == -122.138669
        assert latitude == 47.630359

    @MapsSearchPreparer()
    @recorded_by_proxy
    def test_geocode_batch(self):
        result = self.client.get_geocoding_batch({
          "batchItems": [
            {"query": "400 Broad St, Seattle, WA 98109"},
            {"query": "15127 NE 24th Street, Redmond, WA 98052"},
          ],
        },)

        assert 'batchItems' in result and result['batchItems']

        item1, item2 = result['batchItems']

        assert item1.get('features')

        assert item2.get('features')

        coordinates1 = item1['features'][0]['geometry']['coordinates']
        coordinates2 = item2['features'][0]['geometry']['coordinates']

        longitude1, latitude1 = coordinates1
        longitude2, latitude2 = coordinates2

        assert longitude1 == -122.349309
        assert latitude1 == 47.620498

        assert longitude2 == -122.138669
        assert latitude2 == 47.630359

    @MapsSearchPreparer()
    @recorded_by_proxy
    def test_reverse_geocode(self):
        result = self.client.get_reverse_geocoding(coordinates=[-122.138679, 47.630356])
        assert 'features' in result and result['features']
        props = result['features'][0].get('properties', {})

        assert props and 'address' in props and props['address']
        assert props['address'].get('formattedAddress', 'No formatted address found') == "2265 152nd Ave NE, Redmond, Washington 98052, United States"

    @MapsSearchPreparer()
    @recorded_by_proxy
    def test_reverse_geocode_batch(self):
        result = self.client.get_reverse_geocoding_batch({
            "batchItems": [
                {"coordinates": [-122.349309, 47.620498]},
                {"coordinates": [-122.138679, 47.630356]},
            ],
        }, )

        assert 'batchItems' in result and result['batchItems']

        # item 1
        features = result['batchItems'][0]['features']
        assert features
        props = features[0].get('properties', {})
        assert props and 'address' in props and props['address']
        assert props['address'].get('formattedAddress', 'No formatted address for item 1 found') == "400 Broad St, Seattle, Washington 98109, United States"

        # item 2
        features = result['batchItems'][1]['features']
        assert features
        props = features[0].get('properties', {})
        assert props and 'address' in props and props['address']
        assert props['address'].get('formattedAddress', 'No formatted address for item 2 found') == "2265 152nd Ave NE, Redmond, Washington 98052, United States"

    @MapsSearchPreparer()
    @recorded_by_proxy
    def test_get_polygon(self):
        result = self.client.get_polygon(**{
            "coordinates": [-122.204141, 47.61256],
            "result_type": BoundaryResultType.LOCALITY,
            "resolution": Resolution.SMALL,
        })

        assert 'geometry' in result and result['geometry'] and result['geometry']['geometries']
