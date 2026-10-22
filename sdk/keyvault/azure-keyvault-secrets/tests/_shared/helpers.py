# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import json
from urllib import parse

try:
    from unittest import mock
except ImportError:  # python < 3.3
    import mock  # type: ignore


class Request:
    def __init__(
        self,
        base_url=None,
        url=None,
        authority=None,
        url_substring=None,
        method=None,
        required_headers=None,
        required_data=None,
        required_params=None,
    ):
        self.authority = authority
        self.base_url = base_url
        self.method = method
        self.url = url
        self.url_substring = url_substring
        self.required_headers = required_headers or {}
        self.required_data = required_data or {}
        self.required_params = required_params or {}

    def assert_matches(self, request):
        discrepancies = []

        def add_discrepancy(name, expected, actual):
            discrepancies.append("{}:\n\t expected: {}\n\t   actual: {}".format(name, expected, actual))

        if self.base_url and self.base_url != request.url.split("?")[0]:
            add_discrepancy("base url", self.base_url, request.url)

        if self.url and self.url != request.url:
            add_discrepancy("url", self.url, request.url)

        if self.url_substring and self.url_substring not in request.url:
            add_discrepancy("url substring", self.url_substring, request.url)

        parsed = parse.urlparse(request.url)
        if self.authority and parsed.netloc != self.authority:
            add_discrepancy("authority", self.authority, parsed.netloc)

        if self.method and request.method != self.method:
            add_discrepancy("method", self.method, request.method)

        for param, expected_value in self.required_params.items():
            actual_value = request.query.get(param)
            if actual_value != expected_value:
                add_discrepancy(param, expected_value, actual_value)

        for header, expected_value in self.required_headers.items():
            actual_value = request.headers.get(header)

            # UserAgentPolicy appends the value of $AZURE_HTTP_USER_AGENT, which is set in
            # pipelines, so we accept a user agent which merely contains the expected value
            if header.lower() == "user-agent":
                if expected_value not in actual_value:
                    add_discrepancy("user-agent", "contains " + expected_value, actual_value)
            elif actual_value != expected_value:
                add_discrepancy(header, expected_value, actual_value)

        for field, expected_value in self.required_data.items():
            actual_value = request.body.get(field)
            if actual_value != expected_value:
                add_discrepancy("form field", expected_value, actual_value)

        assert not discrepancies, "Unexpected request\n\t" + "\n\t".join(discrepancies)


def mock_response(status_code=200, headers=None, json_payload=None):
    response = mock.Mock(status_code=status_code, headers=headers or {})
    if json_payload is not None:
        response.text = lambda encoding=None: json.dumps(json_payload)
        response.headers["content-type"] = "application/json"
        response.content_type = "application/json"
    return response


def validating_transport(requests, responses):
    if len(requests) != len(responses):
        raise ValueError("each request must have one response")

    sessions = zip(requests, responses)
    sessions = (s for s in sessions)  # 2.7's zip returns a list, and nesting a generator doesn't break it for 3.x

    def validate_request(request, **kwargs):  # pylint:disable=unused-argument
        expected_request, response = next(sessions)
        expected_request.assert_matches(request)
        return response

    return mock.Mock(send=validate_request)
