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


import collections.abc
import contextlib
import io
import typing
from timeit import default_timer
from typing import Collection

import urllib3.connectionpool
import wrapt

from opentelemetry import context

# FIXME: fix the importing of this private attribute when the location of the _SUPPRESS_HTTP_INSTRUMENTATION_KEY is defined.
from opentelemetry.context import _SUPPRESS_HTTP_INSTRUMENTATION_KEY
from azure.monitor.opentelemetry._vendor.v0_40b0.opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from azure.monitor.opentelemetry._vendor.v0_40b0.opentelemetry.instrumentation.urllib3.package import _instruments
from azure.monitor.opentelemetry._vendor.v0_40b0.opentelemetry.instrumentation.urllib3.version import __version__
from azure.monitor.opentelemetry._vendor.v0_40b0.opentelemetry.instrumentation.utils import (
    _SUPPRESS_INSTRUMENTATION_KEY,
    http_status_to_status_code,
    unwrap,
)
from opentelemetry.metrics import Histogram, get_meter
from opentelemetry.propagate import inject
from opentelemetry.semconv.metrics import MetricInstruments
from opentelemetry.semconv.trace import SpanAttributes
from opentelemetry.trace import Span, SpanKind, Tracer, get_tracer
from opentelemetry.trace.status import Status
from azure.monitor.opentelemetry._vendor.v0_40b0.opentelemetry.util.http import (
    ExcludeList,
    get_excluded_urls,
    parse_excluded_urls,
)
from azure.monitor.opentelemetry._vendor.v0_40b0.opentelemetry.util.http.httplib import set_ip_on_next_http_connection

_excluded_urls_from_env = get_excluded_urls("URLLIB3")

_UrlFilterT = typing.Optional[typing.Callable[[str], str]]
_RequestHookT = typing.Optional[
    typing.Callable[
        [
            Span,
            urllib3.connectionpool.HTTPConnectionPool,
            typing.Dict,
            typing.Optional[str],
        ],
        None,
    ]
]
_ResponseHookT = typing.Optional[
    typing.Callable[
        [
            Span,
            urllib3.connectionpool.HTTPConnectionPool,
            urllib3.response.HTTPResponse,
        ],
        None,
    ]
]

_URL_OPEN_ARG_TO_INDEX_MAPPING = {
    "method": 0,
    "url": 1,
    "body": 2,
}


class URLLib3Instrumentor(BaseInstrumentor):
    def instrumentation_dependencies(self) -> Collection[str]:
        return _instruments

    def _instrument(self, **kwargs):
        """Instruments the urllib3 module

        Args:
            **kwargs: Optional arguments
                ``tracer_provider``: a TracerProvider, defaults to global.
                ``request_hook``: An optional callback that is invoked right after a span is created.
                ``response_hook``: An optional callback which is invoked right before the span is finished processing a response.
                ``url_filter``: A callback to process the requested URL prior
                    to adding it as a span attribute.
                ``excluded_urls``: A string containing a comma-delimited
                    list of regexes used to exclude URLs from tracking
        """
        tracer_provider = kwargs.get("tracer_provider")
        tracer = get_tracer(__name__, __version__, tracer_provider)

        excluded_urls = kwargs.get("excluded_urls")

        meter_provider = kwargs.get("meter_provider")
        meter = get_meter(__name__, __version__, meter_provider)

        duration_histogram = meter.create_histogram(
            name=MetricInstruments.HTTP_CLIENT_DURATION,
            unit="ms",
            description="measures the duration outbound HTTP requests",
        )
        request_size_histogram = meter.create_histogram(
            name=MetricInstruments.HTTP_CLIENT_REQUEST_SIZE,
            unit="By",
            description="measures the size of HTTP request messages (compressed)",
        )
        response_size_histogram = meter.create_histogram(
            name=MetricInstruments.HTTP_CLIENT_RESPONSE_SIZE,
            unit="By",
            description="measures the size of HTTP response messages (compressed)",
        )

        _instrument(
            tracer,
            duration_histogram,
            request_size_histogram,
            response_size_histogram,
            request_hook=kwargs.get("request_hook"),
            response_hook=kwargs.get("response_hook"),
            url_filter=kwargs.get("url_filter"),
            excluded_urls=_excluded_urls_from_env
            if excluded_urls is None
            else parse_excluded_urls(excluded_urls),
        )

    def _uninstrument(self, **kwargs):
        _uninstrument()


def _instrument(
    tracer: Tracer,
    duration_histogram: Histogram,
    request_size_histogram: Histogram,
    response_size_histogram: Histogram,
    request_hook: _RequestHookT = None,
    response_hook: _ResponseHookT = None,
    url_filter: _UrlFilterT = None,
    excluded_urls: ExcludeList = None,
):
    def instrumented_urlopen(wrapped, instance, args, kwargs):
        if _is_instrumentation_suppressed():
            return wrapped(*args, **kwargs)

        url = _get_url(instance, args, kwargs, url_filter)
        if excluded_urls and excluded_urls.url_disabled(url):
            return wrapped(*args, **kwargs)

        method = _get_url_open_arg("method", args, kwargs).upper()
        headers = _prepare_headers(kwargs)
        body = _get_url_open_arg("body", args, kwargs)

        span_name = method.strip()
        span_attributes = {
            SpanAttributes.HTTP_METHOD: method,
            SpanAttributes.HTTP_URL: url,
        }

        with tracer.start_as_current_span(
            span_name, kind=SpanKind.CLIENT, attributes=span_attributes
        ) as span, set_ip_on_next_http_connection(span):
            if callable(request_hook):
                request_hook(span, instance, headers, body)
            inject(headers)

            with _suppress_further_instrumentation():
                start_time = default_timer()
                response = wrapped(*args, **kwargs)
                elapsed_time = round((default_timer() - start_time) * 1000)

            _apply_response(span, response)
            if callable(response_hook):
                response_hook(span, instance, response)

            request_size = _get_body_size(body)
            response_size = int(response.headers.get("Content-Length", 0))

            metric_attributes = _create_metric_attributes(
                instance, response, method
            )

            duration_histogram.record(
                elapsed_time, attributes=metric_attributes
            )
            if request_size is not None:
                request_size_histogram.record(
                    request_size, attributes=metric_attributes
                )
            response_size_histogram.record(
                response_size, attributes=metric_attributes
            )

            return response

    wrapt.wrap_function_wrapper(
        urllib3.connectionpool.HTTPConnectionPool,
        "urlopen",
        instrumented_urlopen,
    )


def _get_url_open_arg(name: str, args: typing.List, kwargs: typing.Mapping):
    arg_idx = _URL_OPEN_ARG_TO_INDEX_MAPPING.get(name)
    if arg_idx is not None:
        try:
            return args[arg_idx]
        except IndexError:
            pass
    return kwargs.get(name)


def _get_url(
    instance: urllib3.connectionpool.HTTPConnectionPool,
    args: typing.List,
    kwargs: typing.Mapping,
    url_filter: _UrlFilterT,
) -> str:
    url_or_path = _get_url_open_arg("url", args, kwargs)
    if not url_or_path.startswith("/"):
        url = url_or_path
    else:
        url = instance.scheme + "://" + instance.host
        if _should_append_port(instance.scheme, instance.port):
            url += ":" + str(instance.port)
        url += url_or_path

    if url_filter:
        return url_filter(url)
    return url


def _get_body_size(body: object) -> typing.Optional[int]:
    if body is None:
        return 0
    if isinstance(body, collections.abc.Sized):
        return len(body)
    if isinstance(body, io.BytesIO):
        return body.getbuffer().nbytes
    return None


def _should_append_port(scheme: str, port: typing.Optional[int]) -> bool:
    if not port:
        return False
    if scheme == "http" and port == 80:
        return False
    if scheme == "https" and port == 443:
        return False
    return True


def _prepare_headers(urlopen_kwargs: typing.Dict) -> typing.Dict:
    headers = urlopen_kwargs.get("headers")

    # avoid modifying original headers on inject
    headers = headers.copy() if headers is not None else {}
    urlopen_kwargs["headers"] = headers

    return headers


def _apply_response(span: Span, response: urllib3.response.HTTPResponse):
    if not span.is_recording():
        return

    span.set_attribute(SpanAttributes.HTTP_STATUS_CODE, response.status)
    span.set_status(Status(http_status_to_status_code(response.status)))


def _is_instrumentation_suppressed() -> bool:
    return bool(
        context.get_value(_SUPPRESS_INSTRUMENTATION_KEY)
        or context.get_value(_SUPPRESS_HTTP_INSTRUMENTATION_KEY)
    )


def _create_metric_attributes(
    instance: urllib3.connectionpool.HTTPConnectionPool,
    response: urllib3.response.HTTPResponse,
    method: str,
) -> dict:
    metric_attributes = {
        SpanAttributes.HTTP_METHOD: method,
        SpanAttributes.HTTP_HOST: instance.host,
        SpanAttributes.HTTP_SCHEME: instance.scheme,
        SpanAttributes.HTTP_STATUS_CODE: response.status,
        SpanAttributes.NET_PEER_NAME: instance.host,
        SpanAttributes.NET_PEER_PORT: instance.port,
    }

    version = getattr(response, "version")
    if version:
        metric_attributes[SpanAttributes.HTTP_FLAVOR] = (
            "1.1" if version == 11 else "1.0"
        )

    return metric_attributes


@contextlib.contextmanager
def _suppress_further_instrumentation():
    token = context.attach(
        context.set_value(_SUPPRESS_HTTP_INSTRUMENTATION_KEY, True)
    )
    try:
        yield
    finally:
        context.detach(token)


def _uninstrument():
    unwrap(urllib3.connectionpool.HTTPConnectionPool, "urlopen")
