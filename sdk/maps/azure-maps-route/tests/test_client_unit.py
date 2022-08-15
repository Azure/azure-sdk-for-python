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
from azure.core.credentials import AzureKeyCredential
from azure.maps.route import MapsRouteClient
from azure.maps.route.models import LatLon


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
    return MapsRouteClient(
        credential= Mock(AzureKeyCredential),
        transport=MockTransport(status_code, body, **kwargs)
    )

class AzureMapsRouteClientUnitTest(AzureTestCase):
    def __init__(self, *args, **kwargs):
        super(AzureMapsRouteClientUnitTest, self).__init__(*args, **kwargs)

    def setUp(self):
        super(AzureMapsRouteClientUnitTest, self).setUp()

    def test_get_route_directions(self):
        body = '''{
            "format_version": "0.0.12",
            "optimized_waypoints": null,
            "report": null,
            "routes": [
                {
                    "guidance": null,
                    "legs": [
                        {
                            "points": [
                                {
                                    "latitude": 52.5093,
                                    "longitude": 13.42937
                                },
                                {
                                    "latitude": 52.50904,
                                    "longitude": 13.42913
                                },
                                {
                                    "latitude": 52.50895,
                                    "longitude": 13.42904
                                },
                                {
                                    "latitude": 52.50868,
                                    "longitude": 13.4288
                                },
                                {
                                    "latitude": 52.5084,
                                    "longitude": 13.42857
                                },
                                {
                                    "latitude": 52.50816,
                                    "longitude": 13.42839
                                },
                                {
                                    "latitude": 52.50791,
                                    "longitude": 13.42825
                                },
                                {
                                    "latitude": 52.50757,
                                    "longitude": 13.42772
                                },
                                {
                                    "latitude": 52.50752,
                                    "longitude": 13.42785
                                },
                                {
                                    "latitude": 52.50742,
                                    "longitude": 13.42809
                                },
                                {
                                    "latitude": 52.50735,
                                    "longitude": 13.42824
                                },
                                {
                                    "latitude": 52.5073,
                                    "longitude": 13.42837
                                },
                                {
                                    "latitude": 52.50696,
                                    "longitude": 13.4291
                                },
                                {
                                    "latitude": 52.50673,
                                    "longitude": 13.42961
                                },
                                {
                                    "latitude": 52.50619,
                                    "longitude": 13.43092
                                },
                                {
                                    "latitude": 52.50608,
                                    "longitude": 13.43116
                                },
                                {
                                    "latitude": 52.50574,
                                    "longitude": 13.43195
                                },
                                {
                                    "latitude": 52.50564,
                                    "longitude": 13.43218
                                },
                                {
                                    "latitude": 52.50528,
                                    "longitude": 13.43299
                                },
                                {
                                    "latitude": 52.50513,
                                    "longitude": 13.43336
                                },
                                {
                                    "latitude": 52.505,
                                    "longitude": 13.43366
                                },
                                {
                                    "latitude": 52.50464,
                                    "longitude": 13.43451
                                },
                                {
                                    "latitude": 52.50451,
                                    "longitude": 13.43482
                                },
                                {
                                    "latitude": 52.50444,
                                    "longitude": 13.43499
                                },
                                {
                                    "latitude": 52.50418,
                                    "longitude": 13.43564
                                },
                                {
                                    "latitude": 52.50364,
                                    "longitude": 13.4369
                                },
                                {
                                    "latitude": 52.50343,
                                    "longitude": 13.43738
                                },
                                {
                                    "latitude": 52.5033,
                                    "longitude": 13.43767
                                },
                                {
                                    "latitude": 52.50275,
                                    "longitude": 13.43874
                                }
                            ],
                            "summary": {
                                "arrival_time": "2022-07-14T08:22:10+02:00",
                                "battery_consumption_ink_wh": null,
                                "departure_time": "2022-07-14T08:19:24+02:00",
                                "fuel_consumption_in_liters": null,
                                "historic_traffic_travel_time_in_seconds": null,
                                "length_in_meters": 1147,
                                "live_traffic_incidents_travel_time_in_seconds": null,
                                "no_traffic_travel_time_in_seconds": null,
                                "traffic_delay_in_seconds": 0,
                                "travel_time_in_seconds": 166
                            }
                        }
                    ],
                    "sections": [
                        {
                            "delay_in_seconds": null,
                            "effective_speed_in_kmh": null,
                            "end_point_index": 28,
                            "magnitude_of_delay": null,
                            "section_type": "TRAVEL_MODE",
                            "simple_category": null,
                            "start_point_index": 0,
                            "tec": null,
                            "travel_mode": "car"
                        }
                    ],
                    "summary": {
                        "arrival_time": "2022-07-14T08:22:10+02:00",
                        "departure_time": "2022-07-14T08:19:24+02:00",
                        "length_in_meters": 1147,
                        "traffic_delay_in_seconds": 0,
                        "travel_time_in_seconds": 166
                    }
                }
            ]
        }'''
        client = create_mock_client(status_code=200, body=body)
        result = client.get_route_directions(route_points=[(52.50931,13.42936), (52.50274,13.43872)])
        assert len(result.routes) == 1
        top_answer = result.routes[0]
        assert len(top_answer.legs[0].points) == 29


    def test_get_route_range(self):
        body='''{
                "formatVersion": "0.0.1",
                "reachableRange": {
                    "center": {
                    "latitude": 50.97452,
                    "longitude": 5.86605
                    },
                    "boundary": [
                        {
                            "latitude": 52.03704,
                            "longitude": 5.73602
                        },
                        {
                            "latitude": 52.09456,
                            "longitude": 5.59435
                        },
                        {
                            "latitude": 52.16815,
                            "longitude": 5.42279
                        },
                        {
                            "latitude": 52.25047,
                            "longitude": 5.21276
                        },
                        {
                            "latitude": 52.21374,
                            "longitude": 5.15355
                        },
                        {
                            "latitude": 52.25674,
                            "longitude": 4.96687
                        },
                        {
                            "latitude": 52.07834,
                            "longitude": 4.739
                        },
                        {
                            "latitude": 52.05647,
                            "longitude": 4.72513
                        },
                        {
                            "latitude": 51.94553,
                            "longitude": 4.53237
                        },
                        {
                            "latitude": 51.70119,
                            "longitude": 4.31165
                        }
                    ]
                }
            }'''
        client = create_mock_client(status_code=200, body=body)
        result = client.get_route_range(coordinates=(50.97452,5.86605), time_budget_in_sec=6000)
        top_answer = result.reachable_range
        assert top_answer.center.latitude == 50.97452
        assert top_answer.center.longitude == 5.86605
        assert len(top_answer.boundary) > 0
        assert top_answer.boundary[0].latitude > top_answer.center.latitude
        assert top_answer.boundary[0].longitude < top_answer.center.longitude


    def request_route_matrix(self):
        body='''{
                    "formatVersion": "0.0.1",
                    "matrix": [
                        [
                        {
                            "statusCode": 200,
                            "response": {
                            "routeSummary": {
                                "lengthInMeters": 495,
                                "travelTimeInSeconds": 134,
                                "trafficDelayInSeconds": 0,
                                "departureTime": "2018-07-27T22:55:29+00:00",
                                "arrivalTime": "2018-07-27T22:57:43+00:00"
                            }
                            }
                        },
                        {
                            "statusCode": 200,
                            "response": {
                            "routeSummary": {
                                "lengthInMeters": 647651,
                                "travelTimeInSeconds": 26835,
                                "trafficDelayInSeconds": 489,
                                "departureTime": "2018-07-27T22:55:29+00:00",
                                "arrivalTime": "2018-07-28T06:22:44+00:00"
                            }
                            }
                        }
                        ],
                        [
                        {
                            "statusCode": 200,
                            "response": {
                            "routeSummary": {
                                "lengthInMeters": 338,
                                "travelTimeInSeconds": 104,
                                "trafficDelayInSeconds": 0,
                                "departureTime": "2018-07-27T22:55:29+00:00",
                                "arrivalTime": "2018-07-27T22:57:13+00:00"
                            }
                            }
                        },
                        {
                            "statusCode": 200,
                            "response": {
                            "routeSummary": {
                                "lengthInMeters": 647494,
                                "travelTimeInSeconds": 26763,
                                "trafficDelayInSeconds": 469,
                                "departureTime": "2018-07-27T22:55:29+00:00",
                                "arrivalTime": "2018-07-28T06:21:32+00:00"
                            }
                            }
                        }
                        ]
                    ],
                    "summary": {
                        "successfulRoutes": 4,
                        "totalRoutes": 4
                    }
                }'''
        client = create_mock_client(status_code=200, body=body)
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
        result = client.post_route_matrix_sync(request_obj)
        assert len(result.matrix) > 0
        assert len(result.matrix) == result.summary.total_routes
        top_answer = result.matrix[0]
        assert top_answer.response.route_summary.length_in_meters == 495

if __name__ == "__main__" :
    testArgs = [ "-v" , "-s" ] if len(sys.argv) == 1 else sys.argv[1:]
    #testArgs = [ "-s" , "-n" , "auto" , "--dist=loadscope" ] if len(sys.argv) == 1 else sys.argv[1:]
    #pytest-xdist: -n auto --dist=loadscope
    #pytest-parallel: --tests-per-worker auto
    #print( "testArgs={}".format(testArgs) )

    pytest.main(args=testArgs)

    print("main() Leave")