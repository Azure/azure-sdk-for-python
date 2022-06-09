import os
import sys
import pytest

from devtools_testutils import AzureTestCase
from azure_devtools.scenario_tests import RecordingProcessor
from azure.maps.search import SearchClient
from azure.maps.search.models import LatLon, StructuredAddress


# cSpell:disable
class HeaderReplacer(RecordingProcessor):
    def __init__(self):
        self.headers = []

    def register_header(self, header_name, new_val):
        self.headers.append((header_name, new_val))

    def process_request(self, request):
        for header_name, new_val in self.headers:
            for key in request.headers.keys():
                if key.lower() == header_name.lower():
                    request.headers[key] = new_val
                    break
        return request


# cSpell:disable
class AzureMapsSearchClientE2ETest(AzureTestCase):
    def __init__(self, *args, **kwargs):
        super(AzureMapsSearchClientE2ETest, self).__init__(*args, **kwargs)
        header_replacer = HeaderReplacer()
        header_replacer.register_header("subscription-key", "<RealSubscriptionKey>")
        header_replacer.register_header("x-ms-client-id", "<RealClientId>")
        self.recording_processors.append(header_replacer)

    def setUp(self):
        super(AzureMapsSearchClientE2ETest, self).setUp()
        self.client = self.create_client_from_credential(SearchClient,
            credential="NotUsed",
            client_id=self.get_settings_value("CLIENT_ID"),
            authentication_policy = self.get_credential(SearchClient))
        assert self.client is not None

    def test_fuzzy_search_poi_coordinates(self):
        result = self.client.fuzzy_search("Taipei 101", coordinates=LatLon(25.0338053, 121.5640089))
        assert len(result.results) > 0 and result.results[0].type == "POI"

    def test_fuzzy_search_poi_country_set(self):
        result = self.client.fuzzy_search("Taipei 101", country_filter=["TW"])
        assert len(result.results) > 0
        for item in result.results:
            assert item.address.country_code_iso3 == "TWN"

        result = self.client.fuzzy_search("Taipei 101", country_filter=["US"])
        assert len(result.results) > 0
        for item in result.results:
            assert item.address.country_code_iso3 == "USA"

        result = self.client.fuzzy_search("Taipei 101", country_filter=["AQ"])
        assert len(result.results) == 0

    def test_fuzzy_search_address(self):
        result = self.client.fuzzy_search("19F., No. 68, Sec. 5, Zhongxiao E. Rd., Xinyi Dist., Taipei City, Taiwan")
        assert len(result.results) > 0 and result.results[0].address.municipality == "Taipei City"

    def test_fuzzy_search_multiple_results(self):
        result = self.client.fuzzy_search("Taiwan High Speed Rail")
        assert len(result.results) > 0

        assert result.summary.total_results > result.summary.num_results
        result2 = self.client.fuzzy_search("Taiwan High Speed Rail", skip=result.summary.num_results)
        assert len(result2.results) > 0 and result2.results[0] != result.results[0]

    def test_search_point_of_interest(self):
        result = self.client.search_point_of_interest("Taipei")
        assert len(result.results) > 0
        for item in result.results:
            assert item.type == "POI"

    def test_search_address(self):
        result = self.client.search_address("Taipei")
        assert len(result.results) > 0
        for item in result.results:
            assert item.type != "POI"

    def test_search_nearby_point_of_interest(self):
        result = self.client.search_nearby_point_of_interest(coordinates=LatLon(25.0338053, 121.5640089))
        assert len(result.results) > 0
        for item in result.results:
            assert item.type == "POI"

    def test_search_point_of_interest_category(self):
        result = self.client.search_point_of_interest_category("RESTAURANT", coordinates=LatLon(25.0338053, 121.5640089))
        assert len(result.results) > 0
        for item in result.results:
            assert item.type == "POI"
            assert "RESTAURANT" in [category.code for category in item.point_of_interest.classifications]

    def test_search_structured_address(self):
        addr = StructuredAddress(street_number=68,
                                 street_name="Sec. 5, Zhongxiao E. Rd.",
                                 municipality_subdivision="Xinyi Dist.",
                                 municipality="Taipei City",
                                 country_code="TW")
        result = self.client.search_structured_address(addr)
        assert len(result.results) > 0
        for item in result.results:
            assert item.type != "POI"



if __name__ == "__main__" :
    testArgs = [ "-v" , "-s" ] if len(sys.argv) == 1 else sys.argv[1:]
    #testArgs = [ "-s" , "-n" , "auto" , "--dist=loadscope" ] if len(sys.argv) == 1 else sys.argv[1:]
    #pytest-xdist: -n auto --dist=loadscope
    #pytest-parallel: --tests-per-worker auto
    #print( "testArgs={}".format(testArgs) )

    pytest.main(args=testArgs)

    print("main() Leave")
