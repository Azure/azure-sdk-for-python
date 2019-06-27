# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import json

try:
    from unittest import mock
except ImportError:  # python < 3.3
    import mock  # type: ignore


def mock_response(status_code=200, headers={}, payload=None):
    response = mock.Mock(status_code=status_code, headers=headers)
    if payload is not None:
        response.text = lambda: json.dumps(payload)
        response.headers["content-type"] = "application/json"
        response.content_type = ["application/json"]
    return response


class Request:
    def __init__(self, url, method=None, required_headers={}, required_data={}, required_params={}):
        self.method = method
        self.url = url
        self.required_headers = required_headers
        self.required_data = required_data
        self.required_params = required_params

    def assert_matches(self, request):
        assert request.url.split("?")[0] == self.url
        if self.method:
            assert request.method == self.method
        for param, expected_value in self.required_params.items():
            assert request.query.get(param) == expected_value
        for header, expected_value in self.required_headers.items():
            assert request.headers.get(header) == expected_value
        for field, expected_value in self.required_data.items():
            assert request.body.get(field) == expected_value


def validating_transport(requests, responses):
    if len(requests) != len(responses):
        raise ValueError("each request must have one response")

    sessions = zip(requests, responses)
    if isinstance(sessions, list):
        # 2.7's zip returns a list
        sessions = (s for s in sessions)

    def validate_request(request, **kwargs):
        expected_request, response = next(sessions)
        expected_request.assert_matches(request)
        return response

    return mock.Mock(send=validate_request)
