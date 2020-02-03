# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import json

try:
    from unittest import mock
except ImportError:  # python < 3.3
    import mock  # type: ignore


class Request:
    def __init__(
        self, url=None, url_substring=None, method=None, required_headers={}, required_data={}, required_params={}
    ):
        self.method = method
        self.url = url
        self.url_substring = url_substring
        self.required_headers = required_headers
        self.required_data = required_data
        self.required_params = required_params

    def assert_matches(self, request):
        if self.url:
            assert request.url.split("?")[0] == self.url
        if self.url_substring:
            assert self.url_substring in request.url
        if self.method:
            assert request.method == self.method
        for param, expected_value in self.required_params.items():
            assert request.query.get(param) == expected_value
        for header, expected_value in self.required_headers.items():
            assert request.headers.get(header) == expected_value
        for field, expected_value in self.required_data.items():
            assert request.body.get(field) == expected_value


def mock_response(status_code=200, headers={}, json_payload=None):
    response = mock.Mock(status_code=status_code, headers=headers)
    if json_payload is not None:
        response.text = lambda encoding=None: json.dumps(json_payload)
        response.headers["content-type"] = "application/json"
        response.content_type = ["application/json"]
    return response


def validating_transport(requests, responses):
    if len(requests) != len(responses):
        raise ValueError("each request must have one response")

    sessions = zip(requests, responses)
    sessions = (s for s in sessions)  # 2.7's zip returns a list, and nesting a generator doesn't break it for 3.x

    def validate_request(request, **kwargs):
        expected_request, response = next(sessions)
        expected_request.assert_matches(request)
        return response

    return mock.Mock(send=validate_request)


try:
    import asyncio

    def async_validating_transport(requests, responses):
        sync_transport = validating_transport(requests, responses)
        return mock.Mock(send=asyncio.coroutine(sync_transport.send))


except ImportError:
    pass
