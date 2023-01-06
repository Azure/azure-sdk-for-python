# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
from azure.core.credentials import AccessToken, AzureKeyCredential
from azure.maps.search import MapsSearchClient
from azure.maps.search.models import StructuredAddress
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy
from search_preparer import MapsSearchPreparer

# cSpell:disable
class TestMapsSearchClient(AzureRecordedTestCase):
    def setup_method(self, method):
        self.client = MapsSearchClient(
            credential=AzureKeyCredential(os.environ.get('AZURE_SUBSCRIPTION_KEY', "AzureMapsSubscriptionKey"))
        )
        assert self.client is not None

    @MapsSearchPreparer()
    @recorded_by_proxy
    def test_fuzzy_search_poi_coordinates(self):
        result = self.client.fuzzy_search("Taipei 101", coordinates=(25.0338053, 121.5640089))
        assert len(result.results) > 0
        top_answer = result.results[0]
        assert top_answer.point_of_interest.name == "Taipei 101"
        assert top_answer.address.street_name == "Xinyi Road Section 5"
        assert top_answer.address.municipality == "Taipei City"
        assert top_answer.address.postal_code == "110"
        assert top_answer.address.country_code_iso3 == "TWN"
        assert top_answer.position.lat > 25 and top_answer.position.lon > 121

    @MapsSearchPreparer()
    @recorded_by_proxy
    def test_fuzzy_search_poi_country_set(self):
        result = self.client.fuzzy_search("Taipei 101", country_filter=["TW"])
        assert len(result.results) > 0
        for item in result.results:
            assert item.address.country_code_iso3 == "TWN"

    @MapsSearchPreparer()
    @recorded_by_proxy
    def test_fuzzy_search_address(self):
        result = self.client.fuzzy_search("No. 221, Sec. 2, Zhishan Rd., Shilin Dist., Taipei City 111, Taiwan (R.O.C.)")
        assert len(result.results) > 0
        top_answer = result.results[0]
        assert top_answer.type == "Point Address"
        assert top_answer.address.street_name == "Zhishan Road Section 2"
        assert top_answer.address.municipality == "Taipei City"
        assert top_answer.address.postal_code == "111"
        assert top_answer.address.country_code_iso3 == "TWN"

    @MapsSearchPreparer()
    @recorded_by_proxy
    def test_fuzzy_search_top(self):
        result = self.client.fuzzy_search("Taiwan High Speed Rail", top=5)
        assert len(result.results) == 5

    @MapsSearchPreparer()
    @recorded_by_proxy
    def test_fuzzy_search_skip(self):
        result = self.client.fuzzy_search("Taiwan High Speed Rail")
        assert len(result.results) > 0

        assert result.total_results > result.num_results
        result2 = self.client.fuzzy_search("Taiwan High Speed Rail", skip=result.num_results)
        assert len(result2.results) > 0 and result2.results[0] != result.results[0]

    @MapsSearchPreparer()
    @recorded_by_proxy
    def test_fuzzy_search_multiple_results(self):
        result = self.client.fuzzy_search("Taiwan High Speed Rail")
        assert len(result.results) > 0

        assert result.total_results > result.num_results
        result2 = self.client.fuzzy_search("Taiwan High Speed Rail", skip=result.num_results)
        assert len(result2.results) > 0 and result2.results[0] != result.results[0]

    @MapsSearchPreparer()
    @recorded_by_proxy
    def test_search_point_of_interest(self):
        result = self.client.search_point_of_interest("Taipei")
        assert len(result.results) > 0
        for item in result.results:
            assert item.type == "POI"

    @MapsSearchPreparer()
    @recorded_by_proxy
    def test_search_address(self):
        result = self.client.search_address("Taipei")
        assert len(result.results) > 0
        for item in result.results:
            assert item.type != "POI"

    @MapsSearchPreparer()
    @recorded_by_proxy
    def test_search_nearby_point_of_interest(self):
        result = self.client.search_nearby_point_of_interest(coordinates=(25.0338053, 121.5640089))
        assert len(result.results) > 0
        for item in result.results:
            assert item.type == "POI"

    @MapsSearchPreparer()
    @recorded_by_proxy
    def test_search_point_of_interest_category(self):
        result = self.client.search_point_of_interest_category(
            "RESTAURANT", coordinates=(25.0338053, 121.5640089)
        )
        assert len(result.results) > 0
        for item in result.results:
            assert item.type == "POI"
            assert "RESTAURANT" in [category.code for category in item.point_of_interest.classifications]

    @MapsSearchPreparer()
    @recorded_by_proxy
    def test_search_structured_address(self):
        addr = StructuredAddress(street_number="221",
                                 street_name="Sec. 2, Zhishan Rd.",
                                 municipality_subdivision="Shilin Dist.",
                                 municipality="Taipei City",
                                 country_code="TW")
        result = self.client.search_structured_address(addr)
        assert len(result.results) > 0
        for item in result.results:
            assert item.type != "POI"
        top_answer = result.results[0]
        assert top_answer.type == "Point Address"
        assert top_answer.address.street_name == "Zhishan Road Section 2"
        assert top_answer.address.municipality == "Taipei City"
        assert top_answer.address.postal_code == "111"
        assert top_answer.address.country_code_iso3 == "TWN"

    @MapsSearchPreparer()
    @recorded_by_proxy
    def test_get_geometries(self):
        result = self.client.get_geometries(geometry_ids=["8bceafe8-3d98-4445-b29b-fd81d3e9adf5"])
        assert len(result) > 0
        assert result[0].provider_id == "8bceafe8-3d98-4445-b29b-fd81d3e9adf5"
        top_answer = result[0]
        assert top_answer.geometry_data.type == "FeatureCollection"
        assert len(top_answer.geometry_data.features) > 0

    @MapsSearchPreparer()
    @recorded_by_proxy
    def test_get_point_of_interest_categories(self):
        result = self.client.get_point_of_interest_categories()
        assert len(result) > 0
        assert result[0].name == 'Sports Center'
        assert result[0].id == 7320

    @MapsSearchPreparer()
    @recorded_by_proxy
    def test_reverse_search_address(self):
        result = self.client.reverse_search_address(coordinates=(25.0338053, 121.5640089))
        assert len(result.results) > 0
        top_answer = result.results[0]
        assert top_answer.address.building_number == '45'
        assert top_answer.address.postal_code == "110"
        assert top_answer.address.country_code_iso3 == "TWN"

    @MapsSearchPreparer()
    @recorded_by_proxy
    def test_reverse_search_cross_street_address(self):
        result = self.client.reverse_search_cross_street_address(coordinates=(25.0338053, 121.5640089))
        assert len(result.addresses) > 0
        top_answer = result.addresses[0]
        assert top_answer.address.postal_code == "110"
        assert top_answer.address.country_code_iso3 == "TWN"

    @MapsSearchPreparer()
    @recorded_by_proxy
    def test_search_inside_geometry(self):
        geo_json_obj = {
            'type': 'Polygon',
            'coordinates': [
                [[-122.43576049804686, 37.7524152343544],
                [-122.43301391601562, 37.70660472542312],
                [-122.36434936523438, 37.712059855877314],
                [-122.43576049804686, 37.7524152343544]]
            ]
        }
        result = self.client.search_inside_geometry(
            query="pizza",
            geometry=geo_json_obj
        )
        assert len(result.results) > 0
        top_answer = result.results[0]
        assert top_answer.score > 2
        assert top_answer.address.country_subdivision == "CA"
        assert top_answer.address.local_name == "San Francisco"

    @MapsSearchPreparer()
    @recorded_by_proxy
    def test_search_along_route(self):
        route_obj = {
            "route": {
                "type": "LineString",
                "coordinates": [
                    [-122.143035,47.653536],
                    [-122.187164,47.617556],
                    [-122.114981,47.570599],
                    [-122.132756,47.654009]
                ]
            }
        }
        result = self.client.search_along_route(
            query="burger",
            route=route_obj,
            max_detour_time=1000
        )
        assert len(result.results) > 0
        top_answer = result.results[0]
        assert top_answer.address.country_subdivision_name == "Washington"
        assert top_answer.address.country_subdivision == "WA"
        assert top_answer.address.country_code == "US"

    @MapsSearchPreparer()
    @recorded_by_proxy
    def test_search_address(self):
        result = self.client.search_address(query="15127 NE 24th Street, Redmond, WA 98052")
        assert len(result.results) > 0
        top_answer = result.results[0]
        assert top_answer.type == 'Point Address'
        assert top_answer.address.country_subdivision == "WA"
        assert top_answer.address.country_code == "US"

    @MapsSearchPreparer()
    @recorded_by_proxy
    def fuzzy_search_batch(self):
        result = self.client.fuzzy_search_batch(
            search_queries=[
                "350 5th Ave, New York, NY 10118&limit=1",
                "400 Broad St, Seattle, WA 98109&limit=3"
            ]
        )
        assert len(result.items) > 0
        top_answer = result.items[0]
        assert top_answer.response.results[0].address.country_subdivision == "NY"
        assert top_answer.response.results[0].address.country_code == "US"

    @MapsSearchPreparer()
    @recorded_by_proxy
    def search_address_batch(self):
        result = self.client.search_address_batch(
            search_queries=[
                "350 5th Ave, New York, NY 10118&limit=1",
                "400 Broad St, Seattle, WA 98109&limit=3"
            ]
        )
        assert len(result.items) > 0
        top_answer = result.items[0]
        assert top_answer.response.results[0].address.country_subdivision == "NY"
        assert top_answer.response.results[0].address.country_code == "US"
