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

import types
from logging import getLogger
from time import time
from timeit import default_timer
from typing import Callable

from django import VERSION as django_version
from django.http import HttpRequest, HttpResponse

from opentelemetry.context import detach
from azure.monitor.opentelemetry._vendor.v0_40b0.opentelemetry.instrumentation.propagators import (
    get_global_response_propagator,
)
from azure.monitor.opentelemetry._vendor.v0_40b0.opentelemetry.instrumentation.utils import (
    _start_internal_or_server_span,
    extract_attributes_from_object,
)
from azure.monitor.opentelemetry._vendor.v0_40b0.opentelemetry.instrumentation.wsgi import add_response_attributes
from azure.monitor.opentelemetry._vendor.v0_40b0.opentelemetry.instrumentation.wsgi import (
    collect_custom_request_headers_attributes as wsgi_collect_custom_request_headers_attributes,
)
from azure.monitor.opentelemetry._vendor.v0_40b0.opentelemetry.instrumentation.wsgi import (
    collect_custom_response_headers_attributes as wsgi_collect_custom_response_headers_attributes,
)
from azure.monitor.opentelemetry._vendor.v0_40b0.opentelemetry.instrumentation.wsgi import (
    collect_request_attributes as wsgi_collect_request_attributes,
)
from azure.monitor.opentelemetry._vendor.v0_40b0.opentelemetry.instrumentation.wsgi import wsgi_getter
from opentelemetry.semconv.trace import SpanAttributes
from opentelemetry.trace import Span, SpanKind, use_span
from azure.monitor.opentelemetry._vendor.v0_40b0.opentelemetry.util.http import (
    _parse_active_request_count_attrs,
    _parse_duration_attrs,
    get_excluded_urls,
    get_traced_request_attrs,
)

try:
    from django.core.urlresolvers import (  # pylint: disable=no-name-in-module
        Resolver404,
        resolve,
    )
except ImportError:
    from django.urls import Resolver404, resolve

DJANGO_2_0 = django_version >= (2, 0)
DJANGO_3_0 = django_version >= (3, 0)

if DJANGO_2_0:
    # Since Django 2.0, only `settings.MIDDLEWARE` is supported, so new-style
    # middlewares can be used.
    class MiddlewareMixin:
        def __init__(self, get_response):
            self.get_response = get_response

        def __call__(self, request):
            self.process_request(request)
            response = self.get_response(request)
            return self.process_response(request, response)

else:
    # Django versions 1.x can use `settings.MIDDLEWARE_CLASSES` and expect
    # old-style middlewares, which are created by inheriting from
    # `deprecation.MiddlewareMixin` since its creation in Django 1.10 and 1.11,
    # or from `object` for older versions.
    try:
        from django.utils.deprecation import MiddlewareMixin
    except ImportError:
        MiddlewareMixin = object

if DJANGO_3_0:
    from django.core.handlers.asgi import ASGIRequest
else:
    ASGIRequest = None

# try/except block exclusive for optional ASGI imports.
try:
    from azure.monitor.opentelemetry._vendor.v0_40b0.opentelemetry.instrumentation.asgi import asgi_getter, asgi_setter
    from azure.monitor.opentelemetry._vendor.v0_40b0.opentelemetry.instrumentation.asgi import (
        collect_custom_request_headers_attributes as asgi_collect_custom_request_attributes,
    )
    from azure.monitor.opentelemetry._vendor.v0_40b0.opentelemetry.instrumentation.asgi import (
        collect_custom_response_headers_attributes as asgi_collect_custom_response_attributes,
    )
    from azure.monitor.opentelemetry._vendor.v0_40b0.opentelemetry.instrumentation.asgi import (
        collect_request_attributes as asgi_collect_request_attributes,
    )
    from azure.monitor.opentelemetry._vendor.v0_40b0.opentelemetry.instrumentation.asgi import set_status_code

    _is_asgi_supported = True
except ImportError:
    asgi_getter = None
    asgi_collect_request_attributes = None
    set_status_code = None
    _is_asgi_supported = False


_logger = getLogger(__name__)
_attributes_by_preference = [
    [
        SpanAttributes.HTTP_SCHEME,
        SpanAttributes.HTTP_HOST,
        SpanAttributes.HTTP_TARGET,
    ],
    [
        SpanAttributes.HTTP_SCHEME,
        SpanAttributes.HTTP_SERVER_NAME,
        SpanAttributes.NET_HOST_PORT,
        SpanAttributes.HTTP_TARGET,
    ],
    [
        SpanAttributes.HTTP_SCHEME,
        SpanAttributes.NET_HOST_NAME,
        SpanAttributes.NET_HOST_PORT,
        SpanAttributes.HTTP_TARGET,
    ],
    [SpanAttributes.HTTP_URL],
]


def _is_asgi_request(request: HttpRequest) -> bool:
    return ASGIRequest is not None and isinstance(request, ASGIRequest)


class _DjangoMiddleware(MiddlewareMixin):
    """Django Middleware for OpenTelemetry"""

    _environ_activation_key = (
        "opentelemetry-instrumentor-django.activation_key"
    )
    _environ_token = "opentelemetry-instrumentor-django.token"
    _environ_span_key = "opentelemetry-instrumentor-django.span_key"
    _environ_exception_key = "opentelemetry-instrumentor-django.exception_key"
    _environ_active_request_attr_key = (
        "opentelemetry-instrumentor-django.active_request_attr_key"
    )
    _environ_duration_attr_key = (
        "opentelemetry-instrumentor-django.duration_attr_key"
    )
    _environ_timer_key = "opentelemetry-instrumentor-django.timer_key"
    _traced_request_attrs = get_traced_request_attrs("DJANGO")
    _excluded_urls = get_excluded_urls("DJANGO")
    _tracer = None
    _meter = None
    _duration_histogram = None
    _active_request_counter = None

    _otel_request_hook: Callable[[Span, HttpRequest], None] = None
    _otel_response_hook: Callable[
        [Span, HttpRequest, HttpResponse], None
    ] = None

    @staticmethod
    def _get_span_name(request):
        try:
            if getattr(request, "resolver_match"):
                match = request.resolver_match
            else:
                match = resolve(request.path)

            if hasattr(match, "route") and match.route:
                return f"{request.method} {match.route}"

            if hasattr(match, "url_name") and match.url_name:
                return f"{request.method} {match.url_name}"

            return request.method

        except Resolver404:
            return request.method

    # pylint: disable=too-many-locals
    def process_request(self, request):
        # request.META is a dictionary containing all available HTTP headers
        # Read more about request.META here:
        # https://docs.djangoproject.com/en/3.0/ref/request-response/#django.http.HttpRequest.META

        if self._excluded_urls.url_disabled(request.build_absolute_uri("?")):
            return

        is_asgi_request = _is_asgi_request(request)
        if not _is_asgi_supported and is_asgi_request:
            return

        # pylint:disable=W0212
        request._otel_start_time = time()
        request_meta = request.META

        if is_asgi_request:
            carrier = request.scope
            carrier_getter = asgi_getter
            collect_request_attributes = asgi_collect_request_attributes
        else:
            carrier = request_meta
            carrier_getter = wsgi_getter
            collect_request_attributes = wsgi_collect_request_attributes

        attributes = collect_request_attributes(carrier)
        span, token = _start_internal_or_server_span(
            tracer=self._tracer,
            span_name=self._get_span_name(request),
            start_time=request_meta.get(
                "opentelemetry-instrumentor-django.starttime_key"
            ),
            context_carrier=carrier,
            context_getter=carrier_getter,
            attributes=attributes,
        )

        active_requests_count_attrs = _parse_active_request_count_attrs(
            attributes
        )
        duration_attrs = _parse_duration_attrs(attributes)

        request.META[
            self._environ_active_request_attr_key
        ] = active_requests_count_attrs
        request.META[self._environ_duration_attr_key] = duration_attrs
        self._active_request_counter.add(1, active_requests_count_attrs)
        if span.is_recording():
            attributes = extract_attributes_from_object(
                request, self._traced_request_attrs, attributes
            )
            if is_asgi_request:
                # ASGI requests include extra attributes in request.scope.headers.
                attributes = extract_attributes_from_object(
                    types.SimpleNamespace(
                        **{
                            name.decode("latin1"): value.decode("latin1")
                            for name, value in request.scope.get("headers", [])
                        }
                    ),
                    self._traced_request_attrs,
                    attributes,
                )
                if span.is_recording() and span.kind == SpanKind.SERVER:
                    attributes.update(
                        asgi_collect_custom_request_attributes(carrier)
                    )
            else:
                if span.is_recording() and span.kind == SpanKind.SERVER:
                    custom_attributes = (
                        wsgi_collect_custom_request_headers_attributes(carrier)
                    )
                    if len(custom_attributes) > 0:
                        span.set_attributes(custom_attributes)

            for key, value in attributes.items():
                span.set_attribute(key, value)

        activation = use_span(span, end_on_exit=True)
        activation.__enter__()  # pylint: disable=E1101
        request_start_time = default_timer()
        request.META[self._environ_timer_key] = request_start_time
        request.META[self._environ_activation_key] = activation
        request.META[self._environ_span_key] = span
        if token:
            request.META[self._environ_token] = token

        if _DjangoMiddleware._otel_request_hook:
            _DjangoMiddleware._otel_request_hook(  # pylint: disable=not-callable
                span, request
            )

    # pylint: disable=unused-argument
    def process_view(self, request, view_func, *args, **kwargs):
        # Process view is executed before the view function, here we get the
        # route template from request.resolver_match.  It is not set yet in process_request
        if self._excluded_urls.url_disabled(request.build_absolute_uri("?")):
            return

        if (
            self._environ_activation_key in request.META.keys()
            and self._environ_span_key in request.META.keys()
        ):
            span = request.META[self._environ_span_key]

            if span.is_recording():
                match = getattr(request, "resolver_match", None)
                if match:
                    route = getattr(match, "route", None)
                    if route:
                        span.set_attribute(SpanAttributes.HTTP_ROUTE, route)

    def process_exception(self, request, exception):
        if self._excluded_urls.url_disabled(request.build_absolute_uri("?")):
            return

        if self._environ_activation_key in request.META.keys():
            request.META[self._environ_exception_key] = exception

    # pylint: disable=too-many-branches
    # pylint: disable=too-many-locals
    def process_response(self, request, response):
        if self._excluded_urls.url_disabled(request.build_absolute_uri("?")):
            return response

        is_asgi_request = _is_asgi_request(request)
        if not _is_asgi_supported and is_asgi_request:
            return response

        activation = request.META.pop(self._environ_activation_key, None)
        span = request.META.pop(self._environ_span_key, None)
        active_requests_count_attrs = request.META.pop(
            self._environ_active_request_attr_key, None
        )
        duration_attrs = request.META.pop(
            self._environ_duration_attr_key, None
        )
        if duration_attrs:
            duration_attrs[
                SpanAttributes.HTTP_STATUS_CODE
            ] = response.status_code
        request_start_time = request.META.pop(self._environ_timer_key, None)

        if activation and span:
            if is_asgi_request:
                set_status_code(span, response.status_code)

                if span.is_recording() and span.kind == SpanKind.SERVER:
                    custom_headers = {}
                    for key, value in response.items():
                        asgi_setter.set(custom_headers, key, value)

                    custom_res_attributes = (
                        asgi_collect_custom_response_attributes(custom_headers)
                    )
                    for key, value in custom_res_attributes.items():
                        span.set_attribute(key, value)
            else:
                add_response_attributes(
                    span,
                    f"{response.status_code} {response.reason_phrase}",
                    response.items(),
                )
                if span.is_recording() and span.kind == SpanKind.SERVER:
                    custom_attributes = (
                        wsgi_collect_custom_response_headers_attributes(
                            response.items()
                        )
                    )
                    if len(custom_attributes) > 0:
                        span.set_attributes(custom_attributes)

            propagator = get_global_response_propagator()
            if propagator:
                propagator.inject(response)

            # record any exceptions raised while processing the request
            exception = request.META.pop(self._environ_exception_key, None)
            if _DjangoMiddleware._otel_response_hook:
                _DjangoMiddleware._otel_response_hook(  # pylint: disable=not-callable
                    span, request, response
                )

            if exception:
                activation.__exit__(
                    type(exception),
                    exception,
                    getattr(exception, "__traceback__", None),
                )
            else:
                activation.__exit__(None, None, None)

        if request_start_time is not None:
            duration = max(
                round((default_timer() - request_start_time) * 1000), 0
            )
            self._duration_histogram.record(duration, duration_attrs)
        self._active_request_counter.add(-1, active_requests_count_attrs)
        if request.META.get(self._environ_token, None) is not None:
            detach(request.META.get(self._environ_token))
            request.META.pop(self._environ_token)

        return response
