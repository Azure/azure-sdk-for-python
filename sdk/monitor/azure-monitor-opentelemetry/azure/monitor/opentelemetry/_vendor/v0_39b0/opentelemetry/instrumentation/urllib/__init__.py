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


import functools
import types
import typing
from http import client
from timeit import default_timer
from typing import Collection, Dict
from urllib.request import (  # pylint: disable=no-name-in-module,import-error
    OpenerDirector,
    Request,
)

from opentelemetry import context

# FIXME: fix the importing of this private attribute when the location of the _SUPPRESS_HTTP_INSTRUMENTATION_KEY is defined.
from opentelemetry.context import _SUPPRESS_HTTP_INSTRUMENTATION_KEY
from azure.monitor.opentelemetry._vendor.v0_39b0.opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from azure.monitor.opentelemetry._vendor.v0_39b0.opentelemetry.instrumentation.urllib.package import _instruments
from azure.monitor.opentelemetry._vendor.v0_39b0.opentelemetry.instrumentation.urllib.version import __version__
from azure.monitor.opentelemetry._vendor.v0_39b0.opentelemetry.instrumentation.utils import (
    _SUPPRESS_INSTRUMENTATION_KEY,
    http_status_to_status_code,
)
from opentelemetry.metrics import Histogram, get_meter
from opentelemetry.propagate import inject
from opentelemetry.semconv.metrics import MetricInstruments
from opentelemetry.semconv.trace import SpanAttributes
from opentelemetry.trace import Span, SpanKind, get_tracer
from opentelemetry.trace.status import Status
from azure.monitor.opentelemetry._vendor.v0_39b0.opentelemetry.util.http import (
    ExcludeList,
    get_excluded_urls,
    parse_excluded_urls,
    remove_url_credentials,
)

_excluded_urls_from_env = get_excluded_urls("URLLIB")

_RequestHookT = typing.Optional[typing.Callable[[Span, Request], None]]
_ResponseHookT = typing.Optional[
    typing.Callable[[Span, Request, client.HTTPResponse], None]
]


class URLLibInstrumentor(BaseInstrumentor):
    """An instrumentor for urllib
    See `BaseInstrumentor`
    """

    def instrumentation_dependencies(self) -> Collection[str]:
        return _instruments

    def _instrument(self, **kwargs):
        """Instruments urllib module

        Args:
            **kwargs: Optional arguments
                ``tracer_provider``: a TracerProvider, defaults to global
                ``request_hook``: An optional callback invoked that is invoked right after a span is created.
                ``response_hook``: An optional callback which is invoked right before the span is finished processing a response
                ``excluded_urls``: A string containing a comma-delimited
                    list of regexes used to exclude URLs from tracking
        """
        tracer_provider = kwargs.get("tracer_provider")
        tracer = get_tracer(__name__, __version__, tracer_provider)
        excluded_urls = kwargs.get("excluded_urls")
        meter_provider = kwargs.get("meter_provider")
        meter = get_meter(__name__, __version__, meter_provider)

        histograms = _create_client_histograms(meter)

        _instrument(
            tracer,
            histograms,
            request_hook=kwargs.get("request_hook"),
            response_hook=kwargs.get("response_hook"),
            excluded_urls=_excluded_urls_from_env
            if excluded_urls is None
            else parse_excluded_urls(excluded_urls),
        )

    def _uninstrument(self, **kwargs):
        _uninstrument()

    def uninstrument_opener(
        self, opener: OpenerDirector
    ):  # pylint: disable=no-self-use
        """uninstrument_opener a specific instance of urllib.request.OpenerDirector"""
        _uninstrument_from(opener, restore_as_bound_func=True)


def _instrument(
    tracer,
    histograms: Dict[str, Histogram],
    request_hook: _RequestHookT = None,
    response_hook: _ResponseHookT = None,
    excluded_urls: ExcludeList = None,
):
    """Enables tracing of all requests calls that go through
    :code:`urllib.Client._make_request`"""

    opener_open = OpenerDirector.open

    @functools.wraps(opener_open)
    def instrumented_open(opener, fullurl, data=None, timeout=None):
        if isinstance(fullurl, str):
            request_ = Request(fullurl, data)
        else:
            request_ = fullurl

        def get_or_create_headers():
            return getattr(request_, "headers", {})

        def call_wrapped():
            return opener_open(opener, request_, data=data, timeout=timeout)

        return _instrumented_open_call(
            opener, request_, call_wrapped, get_or_create_headers
        )

    def _instrumented_open_call(
        _, request, call_wrapped, get_or_create_headers
    ):  # pylint: disable=too-many-locals
        if context.get_value(
            _SUPPRESS_INSTRUMENTATION_KEY
        ) or context.get_value(_SUPPRESS_HTTP_INSTRUMENTATION_KEY):
            return call_wrapped()

        url = request.full_url
        if excluded_urls and excluded_urls.url_disabled(url):
            return call_wrapped()

        method = request.get_method().upper()

        span_name = f"HTTP {method}".strip()

        url = remove_url_credentials(url)

        labels = {
            SpanAttributes.HTTP_METHOD: method,
            SpanAttributes.HTTP_URL: url,
        }

        with tracer.start_as_current_span(
            span_name, kind=SpanKind.CLIENT, attributes=labels
        ) as span:
            exception = None
            if callable(request_hook):
                request_hook(span, request)

            headers = get_or_create_headers()
            inject(headers)

            token = context.attach(
                context.set_value(_SUPPRESS_HTTP_INSTRUMENTATION_KEY, True)
            )
            try:
                start_time = default_timer()
                result = call_wrapped()  # *** PROCEED
            except Exception as exc:  # pylint: disable=W0703
                exception = exc
                result = getattr(exc, "file", None)
            finally:
                elapsed_time = round((default_timer() - start_time) * 1000)
                context.detach(token)

            if result is not None:
                code_ = result.getcode()
                labels[SpanAttributes.HTTP_STATUS_CODE] = str(code_)

                if span.is_recording() and code_ is not None:
                    span.set_attribute(SpanAttributes.HTTP_STATUS_CODE, code_)
                    span.set_status(Status(http_status_to_status_code(code_)))

                ver_ = str(getattr(result, "version", ""))
                if ver_:
                    labels[
                        SpanAttributes.HTTP_FLAVOR
                    ] = f"{ver_[:1]}.{ver_[:-1]}"

            _record_histograms(
                histograms, labels, request, result, elapsed_time
            )

            if callable(response_hook):
                response_hook(span, request, result)

            if exception is not None:
                raise exception.with_traceback(exception.__traceback__)

        return result

    instrumented_open.opentelemetry_instrumentation_urllib_applied = True
    OpenerDirector.open = instrumented_open


def _uninstrument():
    """Disables instrumentation of :code:`urllib` through this module.

    Note that this only works if no other module also patches urllib."""
    _uninstrument_from(OpenerDirector)


def _uninstrument_from(instr_root, restore_as_bound_func=False):
    instr_func_name = "open"
    instr_func = getattr(instr_root, instr_func_name)
    if not getattr(
        instr_func,
        "opentelemetry_instrumentation_urllib_applied",
        False,
    ):
        return

    original = instr_func.__wrapped__  # pylint:disable=no-member
    if restore_as_bound_func:
        original = types.MethodType(original, instr_root)
    setattr(instr_root, instr_func_name, original)


def _create_client_histograms(meter) -> Dict[str, Histogram]:
    histograms = {
        MetricInstruments.HTTP_CLIENT_DURATION: meter.create_histogram(
            name=MetricInstruments.HTTP_CLIENT_DURATION,
            unit="ms",
            description="measures the duration outbound HTTP requests",
        ),
        MetricInstruments.HTTP_CLIENT_REQUEST_SIZE: meter.create_histogram(
            name=MetricInstruments.HTTP_CLIENT_REQUEST_SIZE,
            unit="By",
            description="measures the size of HTTP request messages (compressed)",
        ),
        MetricInstruments.HTTP_CLIENT_RESPONSE_SIZE: meter.create_histogram(
            name=MetricInstruments.HTTP_CLIENT_RESPONSE_SIZE,
            unit="By",
            description="measures the size of HTTP response messages (compressed)",
        ),
    }

    return histograms


def _record_histograms(
    histograms, metric_attributes, request, response, elapsed_time
):
    histograms[MetricInstruments.HTTP_CLIENT_DURATION].record(
        elapsed_time, attributes=metric_attributes
    )

    data = getattr(request, "data", None)
    request_size = 0 if data is None else len(data)
    histograms[MetricInstruments.HTTP_CLIENT_REQUEST_SIZE].record(
        request_size, attributes=metric_attributes
    )

    if response is not None:
        response_size = int(response.headers.get("Content-Length", 0))
        histograms[MetricInstruments.HTTP_CLIENT_RESPONSE_SIZE].record(
            response_size, attributes=metric_attributes
        )
