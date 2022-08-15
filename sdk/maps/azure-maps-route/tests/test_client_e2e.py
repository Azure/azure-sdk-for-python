import os
import sys
import pytest

from devtools_testutils import AzureTestCase
from azure_devtools.scenario_tests import RecordingProcessor
from azure.core.credentials import AzureKeyCredential
from azure.maps.route import MapsRouteClient
from azure.maps.route.models import LatLon


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
class AzureMapsRouteClientE2ETest(AzureTestCase):
    def __init__(self, *args, **kwargs):
        super(AzureMapsRouteClientE2ETest, self).__init__(*args, **kwargs)
        header_replacer = HeaderReplacer()
        header_replacer.register_header("subscription-key", "<RealSubscriptionKey>")
        header_replacer.register_header("x-ms-client-id", "<RealClientId>")
        self.recording_processors.append(header_replacer)

    def setUp(self):
        super(AzureMapsRouteClientE2ETest, self).setUp()
        self.client = MapsRouteClient(
            client_id=self.get_settings_value('CLIENT_ID'),
            credential=AzureKeyCredential(self.get_settings_value('SUBSCRIPTION_KEY')),
        )
        assert self.client is not None

    @pytest.mark.live_test_only
    def test_get_route_directions(self):
        result = self.client.get_route_directions(route_points=[(52.50931,13.42936), (52.50274,13.43872)])
        assert len(result.routes) > 0
        top_answer = result.routes[0]
        assert top_answer.summary.length_in_meters == 1147
        assert len(top_answer.legs) > 0
        assert len(top_answer.legs[0].points) > 0

    @pytest.mark.live_test_only
    def test_get_route_range(self):
        result = self.client.get_route_range(coordinates=(50.97452,5.86605), time_budget_in_sec=6000)
        top_answer = result.reachable_range
        assert top_answer.center.latitude == 50.97452
        assert top_answer.center.longitude == 5.86605
        assert len(top_answer.boundary) > 0
        assert top_answer.boundary[0].latitude > top_answer.center.latitude
        assert top_answer.boundary[0].longitude < top_answer.center.longitude

    @pytest.mark.live_test_only
    def request_route_matrix(self):
        request_obj = {
            "origins": {
                "type": "MultiPoint",
                "coordinates": [
                [
                    4.85106,
                    52.36006
                ],
                [
                    4.85056,
                    52.36187
                ]
                ]
            },
            "destinations": {
                "type": "MultiPoint",
                "coordinates": [
                [
                    4.85003,
                    52.36241
                ],
                [
                    13.42937,
                    52.50931
                ]
                ]
            }
        }
        result = self.client.post_route_matrix_sync(request_obj)
        assert len(result.matrix) > 0
        assert len(result.matrix) == result.summary.total_routes
        top_answer = result.matrix[0]
        assert top_answer.response.route_summary.length_in_meters == 495


if __name__ == "__main__" :
    testArgs = [ "-v" , "-s" ] if len(sys.argv) == 1 else sys.argv[1:]

    pytest.main(args=testArgs)

    print("main() Leave")
