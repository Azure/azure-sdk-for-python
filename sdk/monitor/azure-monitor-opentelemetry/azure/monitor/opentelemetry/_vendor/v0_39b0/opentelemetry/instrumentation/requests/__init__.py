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
from timeit import default_timer
from typing import Callable, Collection, Optional
from urllib.parse import urlparse

from requests.models import PreparedRequest, Response
from requests.sessions import Session
from requests.structures import CaseInsensitiveDict

from opentelemetry import context

# FIXME: fix the importing of this private attribute when the location of the _SUPPRESS_HTTP_INSTRUMENTATION_KEY is defined.
from opentelemetry.context import _SUPPRESS_HTTP_INSTRUMENTATION_KEY
from azure.monitor.opentelemetry._vendor.v0_39b0.opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from azure.monitor.opentelemetry._vendor.v0_39b0.opentelemetry.instrumentation.requests.package import _instruments
from azure.monitor.opentelemetry._vendor.v0_39b0.opentelemetry.instrumentation.requests.version import __version__
from azure.monitor.opentelemetry._vendor.v0_39b0.opentelemetry.instrumentation.utils import (
    _SUPPRESS_INSTRUMENTATION_KEY,
    http_status_to_status_code,
)
from opentelemetry.metrics import Histogram, get_meter
from opentelemetry.propagate import inject
from opentelemetry.semconv.metrics import MetricInstruments
from opentelemetry.semconv.trace import SpanAttributes
from opentelemetry.trace import SpanKind, Tracer, get_tracer
from opentelemetry.trace.span import Span
from opentelemetry.trace.status import Status
from azure.monitor.opentelemetry._vendor.v0_39b0.opentelemetry.util.http import (
    ExcludeList,
    get_excluded_urls,
    parse_excluded_urls,
    remove_url_credentials,
)
from azure.monitor.opentelemetry._vendor.v0_39b0.opentelemetry.util.http.httplib import set_ip_on_next_http_connection

_excluded_urls_from_env = get_excluded_urls("REQUESTS")

_RequestHookT = Optional[Callable[[Span, PreparedRequest], None]]
_ResponseHookT = Optional[Callable[[Span, PreparedRequest], None]]


# pylint: disable=unused-argument
# pylint: disable=R0915
def _instrument(
    tracer: Tracer,
    duration_histogram: Histogram,
    request_hook: _RequestHookT = None,
    response_hook: _ResponseHookT = None,
    excluded_urls: ExcludeList = None,
):
    """Enables tracing of all requests calls that go through
    :code:`requests.session.Session.request` (this includes
    :code:`requests.get`, etc.)."""

    # Since
    # https://github.com/psf/requests/commit/d72d1162142d1bf8b1b5711c664fbbd674f349d1
    # (v0.7.0, Oct 23, 2011), get, post, etc are implemented via request which
    # again, is implemented via Session.request (`Session` was named `session`
    # before v1.0.0, Dec 17, 2012, see
    # https://github.com/psf/requests/commit/4e5c4a6ab7bb0195dececdd19bb8505b872fe120)

    wrapped_send = Session.send

    # pylint: disable-msg=too-many-locals,too-many-branches
    @functools.wraps(wrapped_send)
    def instrumented_send(self, request, **kwargs):
        if excluded_urls and excluded_urls.url_disabled(request.url):
            return wrapped_send(self, request, **kwargs)

        def get_or_create_headers():
            request.headers = (
                request.headers
                if request.headers is not None
                else CaseInsensitiveDict()
            )
            return request.headers

        if context.get_value(
            _SUPPRESS_INSTRUMENTATION_KEY
        ) or context.get_value(_SUPPRESS_HTTP_INSTRUMENTATION_KEY):
            return wrapped_send(self, request, **kwargs)

        # See
        # https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/trace/semantic_conventions/http.md#http-client
        method = request.method.upper()
        span_name = get_default_span_name(method)

        url = remove_url_credentials(request.url)

        span_attributes = {
            SpanAttributes.HTTP_METHOD: method,
            SpanAttributes.HTTP_URL: url,
        }

        metric_labels = {
            SpanAttributes.HTTP_METHOD: method,
        }

        try:
            parsed_url = urlparse(url)
            metric_labels[SpanAttributes.HTTP_SCHEME] = parsed_url.scheme
            if parsed_url.hostname:
                metric_labels[SpanAttributes.HTTP_HOST] = parsed_url.hostname
                metric_labels[
                    SpanAttributes.NET_PEER_NAME
                ] = parsed_url.hostname
            if parsed_url.port:
                metric_labels[SpanAttributes.NET_PEER_PORT] = parsed_url.port
        except ValueError:
            pass

        with tracer.start_as_current_span(
            span_name, kind=SpanKind.CLIENT, attributes=span_attributes
        ) as span, set_ip_on_next_http_connection(span):
            exception = None
            if callable(request_hook):
                request_hook(span, request)

            headers = get_or_create_headers()
            inject(headers)

            token = context.attach(
                context.set_value(_SUPPRESS_HTTP_INSTRUMENTATION_KEY, True)
            )

            start_time = default_timer()

            try:
                result = wrapped_send(self, request, **kwargs)  # *** PROCEED
            except Exception as exc:  # pylint: disable=W0703
                exception = exc
                result = getattr(exc, "response", None)
            finally:
                elapsed_time = max(
                    round((default_timer() - start_time) * 1000), 0
                )
                context.detach(token)

            if isinstance(result, Response):
                if span.is_recording():
                    span.set_attribute(
                        SpanAttributes.HTTP_STATUS_CODE, result.status_code
                    )
                    span.set_status(
                        Status(http_status_to_status_code(result.status_code))
                    )

                metric_labels[
                    SpanAttributes.HTTP_STATUS_CODE
                ] = result.status_code

                if result.raw is not None:
                    version = getattr(result.raw, "version", None)
                    if version:
                        metric_labels[SpanAttributes.HTTP_FLAVOR] = (
                            "1.1" if version == 11 else "1.0"
                        )

                if callable(response_hook):
                    response_hook(span, request, result)

            duration_histogram.record(elapsed_time, attributes=metric_labels)

            if exception is not None:
                raise exception.with_traceback(exception.__traceback__)

        return result

    instrumented_send.opentelemetry_instrumentation_requests_applied = True
    Session.send = instrumented_send


def _uninstrument():
    """Disables instrumentation of :code:`requests` through this module.

    Note that this only works if no other module also patches requests."""
    _uninstrument_from(Session)


def _uninstrument_from(instr_root, restore_as_bound_func=False):
    for instr_func_name in ("request", "send"):
        instr_func = getattr(instr_root, instr_func_name)
        if not getattr(
            instr_func,
            "opentelemetry_instrumentation_requests_applied",
            False,
        ):
            continue

        original = instr_func.__wrapped__  # pylint:disable=no-member
        if restore_as_bound_func:
            original = types.MethodType(original, instr_root)
        setattr(instr_root, instr_func_name, original)


def get_default_span_name(method):
    """Default implementation for name_callback, returns HTTP {method_name}."""
    return f"HTTP {method.strip()}"


class RequestsInstrumentor(BaseInstrumentor):
    """An instrumentor for requests
    See `BaseInstrumentor`
    """

    def instrumentation_dependencies(self) -> Collection[str]:
        return _instruments

    def _instrument(self, **kwargs):
        """Instruments requests module

        Args:
            **kwargs: Optional arguments
                ``tracer_provider``: a TracerProvider, defaults to global
                ``request_hook``: An optional callback that is invoked right after a span is created.
                ``response_hook``: An optional callback which is invoked right before the span is finished processing a response.
                ``excluded_urls``: A string containing a comma-delimited
                    list of regexes used to exclude URLs from tracking
        """
        tracer_provider = kwargs.get("tracer_provider")
        tracer = get_tracer(__name__, __version__, tracer_provider)
        excluded_urls = kwargs.get("excluded_urls")
        meter_provider = kwargs.get("meter_provider")
        meter = get_meter(
            __name__,
            __version__,
            meter_provider,
        )
        duration_histogram = meter.create_histogram(
            name=MetricInstruments.HTTP_CLIENT_DURATION,
            unit="ms",
            description="measures the duration of the outbound HTTP request",
        )
        _instrument(
            tracer,
            duration_histogram,
            request_hook=kwargs.get("request_hook"),
            response_hook=kwargs.get("response_hook"),
            excluded_urls=_excluded_urls_from_env
            if excluded_urls is None
            else parse_excluded_urls(excluded_urls),
        )

    def _uninstrument(self, **kwargs):
        _uninstrument()

    @staticmethod
    def uninstrument_session(session):
        """Disables instrumentation on the session object."""
        _uninstrument_from(session, restore_as_bound_func=True)
