import sys
import pytest
try:
    from unittest.mock import Mock
except ImportError:  # python < 3.3
    from mock import Mock  # type: ignore

from devtools_testutils import AzureTestCase
from azure.core.pipeline.transport import HttpTransport, HttpResponse
from azure.core.exceptions import HttpResponseError
from azure.core.pipeline.policies import AzureKeyCredentialPolicy
from azure.maps.search import SearchClient
from azure.maps.search.models import LatLon, StructuredAddress


# cSpell:disable
class MockTransport(HttpTransport):
    def __init__(self, status_code, body, **kwargs):
        self.status_code = status_code
        self.body = body.encode("utf-8-sig") if body != None else None
        self.kwargs = kwargs
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    def close(self):
        pass
    def open(self):
        pass
    def send(self, request, **kwargs):  # type: (PipelineRequest, Any) -> PipelineResponse
        response = HttpResponse(request, None)
        response.status_code = self.status_code
        response.headers["content-type"] = "application/json"
        response.body = lambda: self.body
        for key, val in self.kwargs.items():
            setattr(response, key, val)
        return response

def create_mock_client(status_code=0, body=None, **kwargs):
    return SearchClient(credential="NotUsed",
                        authentication_policy = Mock(AzureKeyCredentialPolicy),
                        transport=MockTransport(status_code, body, **kwargs))

class AzureMapsSearchClientUnitTest(AzureTestCase):
    def __init__(self, *args, **kwargs):
        super(AzureMapsSearchClientUnitTest, self).__init__(*args, **kwargs)

    def setUp(self):
        super(AzureMapsSearchClientUnitTest, self).setUp()

    def test_fuzzy_search_poi(self):
        body = '''{
    "summary": {
        "query": "taipei 101",
        "queryType": "NON_NEAR",
        "queryTime": 83,
        "numResults": 1,
        "offset": 0,
        "totalResults": 1,
        "fuzzyLevel": 1,
        "geoBias": {
            "lat": 25.0338053,
            "lon": 25.0338053
        }
    },
    "results": [
        {
            "type": "POI",
            "id": "g6JpZK8xNTgwMDgwMDAwMTEwNTKhY6NUV06hdqdVbmlmaWVk",
            "score": 4.4091453552,
            "dist": 9460930.628752131,
            "info": "search:ta:158008000011052-TW",
            "poi": {
                "name": "Taipei 101",
                "phone": "+886 2 8101 8960",
                "categorySet": [
                    {
                        "id": 9382
                    }
                ],
                "url": "www.taipei-101.com.tw",
                "categories": [
                    "commercial building"
                ],
                "classifications": [
                    {
                        "code": "COMMERCIAL_BUILDING",
                        "names": [
                            {
                                "nameLocale": "en-US",
                                "name": "commercial building"
                            }
                        ]
                    }
                ]
            },
            "address": {
                "streetNumber": "7",
                "streetName": "Xinyi Road Section 5",
                "municipalitySubdivision": "Xinyi District",
                "municipality": "Taipei City",
                "countrySubdivision": "Taipei City",
                "postalCode": "110",
                "extendedPostalCode": "11049",
                "countryCode": "TW",
                "country": "Taiwan",
                "countryCodeISO3": "TWN",
                "freeformAddress": "7, Xinyi Road Section 5, Xinyi District, Taipei City 11049",
                "localName": "Xinyi District"
            },
            "position": {
                "lat": 25.03454,
                "lon": 121.56449
            },
            "viewport": {
                "topLeftPoint": {
                    "lat": 25.03611,
                    "lon": 121.56276
                },
                "btmRightPoint": {
                    "lat": 25.03297,
                    "lon": 121.56622
                }
            },
            "entryPoints": [
                {
                    "type": "main",
                    "position": {
                        "lat": 25.03297,
                        "lon": 121.5645
                    }
                }
            ]
        }
    ]
}'''
        client = create_mock_client(status_code=200, body=body)
        result = client.fuzzy_search("Taipei 101")
        assert len(result.results) == 1 and result.summary.total_results == 1
        top_answer = result.results[0]
        assert top_answer.type == "POI"
        assert top_answer.point_of_interest.name == "Taipei 101"
        assert top_answer.address.street_name == "Xinyi Road Section 5"
        assert top_answer.address.municipality == "Taipei City"
        assert top_answer.address.postal_code == "110"
        assert top_answer.address.country_code_iso3 == "TWN"
        assert top_answer.position.lat == 25.03454 and top_answer.position.lon == 121.56449

    def test_fuzzy_search_invalid_top(self):
        body = '''{
    "error": {
        "code": "400 BadRequest",
        "message": "limit value should be between 1 and 100 inclusive"
    }
}'''
        client = create_mock_client(status_code=400, body=body)
        with pytest.raises(HttpResponseError) as err:
            result = client.fuzzy_search("Taipei 101", top=0)
        assert err.value.status_code == 400 and "limit value" in err.value.message

    def test_fuzzy_search_invalid_skip(self):
        body = '''{
    "error": {
        "code": "400 BadRequest",
        "message": "ofs value should be between 0 and 1900 inclusive"
    }
}'''
        client = create_mock_client(status_code=400, body=body)
        with pytest.raises(HttpResponseError) as err:
            result = client.fuzzy_search("Taipei 101", skip=10000)
        assert err.value.status_code == 400 and "ofs value" in err.value.message

    def test_search_nearby_point_of_interest_miss_coordinates(self):
        client = create_mock_client()
        with pytest.raises(TypeError):
            result = client.search_nearby_point_of_interest()

    def test_search_nearby_point_of_interest_invalid_coordinates(self):
        client = create_mock_client()
        with pytest.raises(ValueError):
            result = client.search_nearby_point_of_interest(coordinates=LatLon())

    def test_search_point_of_interest_category(self):
        body = '''{
    "summary": {
        "query": "nonexistingcategory",
        "queryType": "NON_NEAR",
        "queryTime": 51,
        "numResults": 0,
        "offset": 0,
        "totalResults": 0,
        "fuzzyLevel": 3
    },
    "results": []
}'''
        client = create_mock_client(status_code=200, body=body)
        result = client.search_point_of_interest_category("NonExistingCategory", coordinates=LatLon(25.0338053, 121.5640089))
        assert len(result.results) == 0

    def test_search_structured_address(self):
        client = create_mock_client()
        with pytest.raises(TypeError):
             client.search_structured_address(StructuredAddress())




if __name__ == "__main__" :
    testArgs = [ "-v" , "-s" ] if len(sys.argv) == 1 else sys.argv[1:]
    #testArgs = [ "-s" , "-n" , "auto" , "--dist=loadscope" ] if len(sys.argv) == 1 else sys.argv[1:]
    #pytest-xdist: -n auto --dist=loadscope
    #pytest-parallel: --tests-per-worker auto
    #print( "testArgs={}".format(testArgs) )

    pytest.main(args=testArgs)

    print("main() Leave")