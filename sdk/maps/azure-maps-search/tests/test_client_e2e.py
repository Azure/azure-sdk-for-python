import os
import sys
import pytest

from devtools_testutils import AzureTestCase
from azure_devtools.scenario_tests import RecordingProcessor
from azure.core.credentials import AzureKeyCredential
from _shared.utils import AzureKeyInQueryCredentialPolicy
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
        # import pdb; pdb.set_trace()
        self.client = SearchClient(
            credential='NotUsed',
            client_id=self.get_settings_value('CLIENT_ID'),
            authentication_policy = AzureKeyInQueryCredentialPolicy(AzureKeyCredential(self.get_settings_value('SUBSCRIPTION_KEY')), "subscription-key")
        )
        assert self.client is not None

    @pytest.mark.live_test_only
    def test_fuzzy_search_poi_coordinates(self):
        result = self.client.fuzzy_search("Taipei 101", coordinates=LatLon(25.0338053, 121.5640089))
        assert len(result.results) > 0
        top_answer = result.results[0]
        assert top_answer.point_of_interest.name == "Taipei 101"
        assert top_answer.address.street_name == "Xinyi Road Section 5"
        assert top_answer.address.municipality == "Taipei City"
        assert top_answer.address.postal_code == "110"
        assert top_answer.address.country_code_iso3 == "TWN"
        assert top_answer.position.lat == 25.03339 and top_answer.position.lon == 121.56437

    @pytest.mark.live_test_only
    def test_fuzzy_search_poi_country_set(self):
        result = self.client.fuzzy_search("Taipei 101", country_filter=["TW"])
        assert len(result.results) > 0
        for item in result.results:
            assert item.address.country_code_iso3 == "TWN"

    @pytest.mark.live_test_only
    def test_fuzzy_search_address(self):
        result = self.client.fuzzy_search("No. 221, Sec. 2, Zhishan Rd., Shilin Dist., Taipei City 111, Taiwan (R.O.C.)")
        assert len(result.results) > 0
        top_answer = result.results[0]
        assert top_answer.type == "Point Address"
        assert top_answer.address.street_name == "Zhishan Road Section 2"
        assert top_answer.address.municipality == "Taipei City"
        assert top_answer.address.postal_code == "111"
        assert top_answer.address.country_code_iso3 == "TWN"
        assert top_answer.position.lat == 25.09775 and top_answer.position.lon == 121.54639

    @pytest.mark.live_test_only
    def test_fuzzy_search_top(self):
        result = self.client.fuzzy_search("Taiwan High Speed Rail", top=5)
        assert len(result.results) == 5

    @pytest.mark.live_test_only
    def test_fuzzy_search_skip(self):
        result = self.client.fuzzy_search("Taiwan High Speed Rail")
        assert len(result.results) > 0

        assert result.summary.total_results > result.summary.num_results
        result2 = self.client.fuzzy_search("Taiwan High Speed Rail", skip=result.summary.num_results)
        assert len(result2.results) > 0 and result2.results[0] != result.results[0]

    @pytest.mark.live_test_only
    def test_fuzzy_search_multiple_results(self):
        result = self.client.fuzzy_search("Taiwan High Speed Rail")
        assert len(result.results) > 0

        assert result.summary.total_results > result.summary.num_results
        result2 = self.client.fuzzy_search("Taiwan High Speed Rail", skip=result.summary.num_results)
        assert len(result2.results) > 0 and result2.results[0] != result.results[0]

    @pytest.mark.live_test_only
    def test_search_point_of_interest(self):
        result = self.client.search_point_of_interest("Taipei")
        assert len(result.results) > 0
        for item in result.results:
            assert item.type == "POI"

    @pytest.mark.live_test_only
    def test_search_address(self):
        result = self.client.search_address("Taipei")
        assert len(result.results) > 0
        for item in result.results:
            assert item.type != "POI"

    @pytest.mark.live_test_only
    def test_search_nearby_point_of_interest(self):
        result = self.client.search_nearby_point_of_interest(coordinates=LatLon(25.0338053, 121.5640089))
        assert len(result.results) > 0
        for item in result.results:
            assert item.type == "POI"

    @pytest.mark.live_test_only
    def test_search_point_of_interest_category(self):
        result = self.client.search_point_of_interest_category("RESTAURANT", coordinates=LatLon(25.0338053, 121.5640089))
        assert len(result.results) > 0
        for item in result.results:
            assert item.type == "POI"
            assert "RESTAURANT" in [category.code for category in item.point_of_interest.classifications]

    @pytest.mark.live_test_only
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
        assert top_answer.position.lat == 25.10468 and top_answer.position.lon == 121.55715



if __name__ == "__main__" :
    testArgs = [ "-v" , "-s" ] if len(sys.argv) == 1 else sys.argv[1:]

    pytest.main(args=testArgs)

    print("main() Leave")
