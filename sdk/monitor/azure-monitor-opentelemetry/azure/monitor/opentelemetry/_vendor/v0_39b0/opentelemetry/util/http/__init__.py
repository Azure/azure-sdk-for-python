# Copyright The OpenTelemetry Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from os import environ
from re import IGNORECASE as RE_IGNORECASE
from re import compile as re_compile
from re import search
from typing import Iterable, List
from urllib.parse import urlparse, urlunparse

from opentelemetry.semconv.trace import SpanAttributes

OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SANITIZE_FIELDS = (
    "OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SANITIZE_FIELDS"
)
OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SERVER_REQUEST = (
    "OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SERVER_REQUEST"
)
OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SERVER_RESPONSE = (
    "OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SERVER_RESPONSE"
)

# List of recommended metrics attributes
_duration_attrs = {
    SpanAttributes.HTTP_METHOD,
    SpanAttributes.HTTP_HOST,
    SpanAttributes.HTTP_SCHEME,
    SpanAttributes.HTTP_STATUS_CODE,
    SpanAttributes.HTTP_FLAVOR,
    SpanAttributes.HTTP_SERVER_NAME,
    SpanAttributes.NET_HOST_NAME,
    SpanAttributes.NET_HOST_PORT,
}

_active_requests_count_attrs = {
    SpanAttributes.HTTP_METHOD,
    SpanAttributes.HTTP_HOST,
    SpanAttributes.HTTP_SCHEME,
    SpanAttributes.HTTP_FLAVOR,
    SpanAttributes.HTTP_SERVER_NAME,
}


class ExcludeList:
    """Class to exclude certain paths (given as a list of regexes) from tracing requests"""

    def __init__(self, excluded_urls: Iterable[str]):
        self._excluded_urls = excluded_urls
        if self._excluded_urls:
            self._regex = re_compile("|".join(excluded_urls))

    def url_disabled(self, url: str) -> bool:
        return bool(self._excluded_urls and search(self._regex, url))


class SanitizeValue:
    """Class to sanitize (remove sensitive data from) certain headers (given as a list of regexes)"""

    def __init__(self, sanitized_fields: Iterable[str]):
        self._sanitized_fields = sanitized_fields
        if self._sanitized_fields:
            self._regex = re_compile("|".join(sanitized_fields), RE_IGNORECASE)

    def sanitize_header_value(self, header: str, value: str) -> str:
        return (
            "[REDACTED]"
            if (self._sanitized_fields and search(self._regex, header))
            else value
        )

    def sanitize_header_values(
        self, headers: dict, header_regexes: list, normalize_function: callable
    ) -> dict:
        values = {}

        if header_regexes:
            header_regexes_compiled = re_compile(
                "|".join("^" + i + "$" for i in header_regexes),
                RE_IGNORECASE,
            )

            for header_name in list(
                filter(
                    header_regexes_compiled.match,
                    headers.keys(),
                )
            ):
                header_values = headers.get(header_name)
                if header_values:
                    key = normalize_function(header_name.lower())
                    values[key] = [
                        self.sanitize_header_value(
                            header=header_name, value=header_values
                        )
                    ]

        return values


_root = r"OTEL_PYTHON_{}"


def get_traced_request_attrs(instrumentation):
    traced_request_attrs = environ.get(
        _root.format(f"{instrumentation}_TRACED_REQUEST_ATTRS"), []
    )

    if traced_request_attrs:
        traced_request_attrs = [
            traced_request_attr.strip()
            for traced_request_attr in traced_request_attrs.split(",")
        ]

    return traced_request_attrs


def get_excluded_urls(instrumentation: str) -> ExcludeList:
    # Get instrumentation-specific excluded URLs. If not set, retrieve them
    # from generic variable.
    excluded_urls = environ.get(
        _root.format(f"{instrumentation}_EXCLUDED_URLS"),
        environ.get(_root.format("EXCLUDED_URLS"), ""),
    )

    return parse_excluded_urls(excluded_urls)


def parse_excluded_urls(excluded_urls: str) -> ExcludeList:
    """
    Small helper to put an arbitrary url list inside an ExcludeList
    """
    if excluded_urls:
        excluded_url_list = [
            excluded_url.strip() for excluded_url in excluded_urls.split(",")
        ]
    else:
        excluded_url_list = []

    return ExcludeList(excluded_url_list)


def remove_url_credentials(url: str) -> str:
    """Given a string url, remove the username and password only if it is a valid url"""

    try:
        parsed = urlparse(url)
        if all([parsed.scheme, parsed.netloc]):  # checks for valid url
            parsed_url = urlparse(url)
            netloc = (
                (":".join(((parsed_url.hostname or ""), str(parsed_url.port))))
                if parsed_url.port
                else (parsed_url.hostname or "")
            )
            return urlunparse(
                (
                    parsed_url.scheme,
                    netloc,
                    parsed_url.path,
                    parsed_url.params,
                    parsed_url.query,
                    parsed_url.fragment,
                )
            )
    except ValueError:  # an unparsable url was passed
        pass
    return url


def normalise_request_header_name(header: str) -> str:
    key = header.lower().replace("-", "_")
    return f"http.request.header.{key}"


def normalise_response_header_name(header: str) -> str:
    key = header.lower().replace("-", "_")
    return f"http.response.header.{key}"


def get_custom_headers(env_var: str) -> List[str]:
    custom_headers = environ.get(env_var, [])
    if custom_headers:
        custom_headers = [
            custom_headers.strip()
            for custom_headers in custom_headers.split(",")
        ]
    return custom_headers


def _parse_active_request_count_attrs(req_attrs):
    active_requests_count_attrs = {
        key: req_attrs[key]
        for key in _active_requests_count_attrs.intersection(req_attrs.keys())
    }
    return active_requests_count_attrs


def _parse_duration_attrs(req_attrs):
    duration_attrs = {
        key: req_attrs[key]
        for key in _duration_attrs.intersection(req_attrs.keys())
    }
    return duration_attrs
