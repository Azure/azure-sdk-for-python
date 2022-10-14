# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
from azure.core.credentials import AccessToken, AzureKeyCredential
from azure.maps.route import MapsRouteClient
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy, is_live
from route_preparer import MapsRoutePreparer

class TestMapsRouteClient(AzureRecordedTestCase):
    def setup_method(self, method):
        self.client = MapsRouteClient(
            credential=AzureKeyCredential(os.environ.get('AZURE_SUBSCRIPTION_KEY', "AzureMapsSubscriptionKey"))
        )
        assert self.client is not None

    @MapsRoutePreparer()
    @recorded_by_proxy
    def test_get_route_directions(self):
        result = self.client.get_route_directions(route_points=[(52.50931,13.42936), (52.50274,13.43872)])
        assert len(result.routes) > 0
        top_answer = result.routes[0]
        assert top_answer.summary.length_in_meters == 1147
        assert len(top_answer.legs) > 0
        assert len(top_answer.legs[0].points) > 0

    # cSpell:ignore CEST
    @MapsRoutePreparer()
    @recorded_by_proxy
    def test_get_route_range(self):
        result = self.client.get_route_range(coordinates=(50.97452,5.86605), time_budget_in_sec=6000)
        top_answer = result.reachable_range
        assert top_answer.center.latitude == 50.97452
        assert top_answer.center.longitude == 5.86605
        assert len(top_answer.boundary) > 0
        assert top_answer.boundary[0].latitude > top_answer.center.latitude
        assert top_answer.boundary[0].longitude < top_answer.center.longitude

    @MapsRoutePreparer()
    @recorded_by_proxy
    def get_route_matrix(self):
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
        result = self.client.get_route_matrix(request_obj)
        assert len(result.matrix) > 0
        top_answer = result.matrix[0][0]
        assert top_answer.response.summary.length_in_meters == 495
