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


import logging
import typing
from typing import Collection

import fastapi
from starlette.routing import Match

from azure.monitor.opentelemetry._vendor.v0_40b0.opentelemetry.instrumentation.asgi import OpenTelemetryMiddleware
from azure.monitor.opentelemetry._vendor.v0_40b0.opentelemetry.instrumentation.fastapi.package import _instruments
from azure.monitor.opentelemetry._vendor.v0_40b0.opentelemetry.instrumentation.fastapi.version import __version__
from azure.monitor.opentelemetry._vendor.v0_40b0.opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.metrics import get_meter
from opentelemetry.semconv.trace import SpanAttributes
from opentelemetry.trace import Span
from azure.monitor.opentelemetry._vendor.v0_40b0.opentelemetry.util.http import get_excluded_urls, parse_excluded_urls

_excluded_urls_from_env = get_excluded_urls("FASTAPI")
_logger = logging.getLogger(__name__)

_ServerRequestHookT = typing.Optional[typing.Callable[[Span, dict], None]]
_ClientRequestHookT = typing.Optional[typing.Callable[[Span, dict], None]]
_ClientResponseHookT = typing.Optional[typing.Callable[[Span, dict], None]]


class FastAPIInstrumentor(BaseInstrumentor):
    """An instrumentor for FastAPI

    See `BaseInstrumentor`
    """

    _original_fastapi = None

    @staticmethod
    def instrument_app(
        app: fastapi.FastAPI,
        server_request_hook: _ServerRequestHookT = None,
        client_request_hook: _ClientRequestHookT = None,
        client_response_hook: _ClientResponseHookT = None,
        tracer_provider=None,
        meter_provider=None,
        excluded_urls=None,
    ):
        """Instrument an uninstrumented FastAPI application."""
        if not hasattr(app, "_is_instrumented_by_opentelemetry"):
            app._is_instrumented_by_opentelemetry = False

        if not getattr(app, "_is_instrumented_by_opentelemetry", False):
            if excluded_urls is None:
                excluded_urls = _excluded_urls_from_env
            else:
                excluded_urls = parse_excluded_urls(excluded_urls)
            meter = get_meter(__name__, __version__, meter_provider)

            app.add_middleware(
                OpenTelemetryMiddleware,
                excluded_urls=excluded_urls,
                default_span_details=_get_default_span_details,
                server_request_hook=server_request_hook,
                client_request_hook=client_request_hook,
                client_response_hook=client_response_hook,
                tracer_provider=tracer_provider,
                meter=meter,
            )
            app._is_instrumented_by_opentelemetry = True
            if app not in _InstrumentedFastAPI._instrumented_fastapi_apps:
                _InstrumentedFastAPI._instrumented_fastapi_apps.add(app)
        else:
            _logger.warning(
                "Attempting to instrument FastAPI app while already instrumented"
            )

    @staticmethod
    def uninstrument_app(app: fastapi.FastAPI):
        app.user_middleware = [
            x
            for x in app.user_middleware
            if x.cls is not OpenTelemetryMiddleware
        ]
        app.middleware_stack = app.build_middleware_stack()
        app._is_instrumented_by_opentelemetry = False

    def instrumentation_dependencies(self) -> Collection[str]:
        return _instruments

    def _instrument(self, **kwargs):
        self._original_fastapi = fastapi.FastAPI
        _InstrumentedFastAPI._tracer_provider = kwargs.get("tracer_provider")
        _InstrumentedFastAPI._server_request_hook = kwargs.get(
            "server_request_hook"
        )
        _InstrumentedFastAPI._client_request_hook = kwargs.get(
            "client_request_hook"
        )
        _InstrumentedFastAPI._client_response_hook = kwargs.get(
            "client_response_hook"
        )
        _excluded_urls = kwargs.get("excluded_urls")
        _InstrumentedFastAPI._excluded_urls = (
            _excluded_urls_from_env
            if _excluded_urls is None
            else parse_excluded_urls(_excluded_urls)
        )
        _InstrumentedFastAPI._meter_provider = kwargs.get("meter_provider")
        fastapi.FastAPI = _InstrumentedFastAPI

    def _uninstrument(self, **kwargs):
        for instance in _InstrumentedFastAPI._instrumented_fastapi_apps:
            self.uninstrument_app(instance)
        _InstrumentedFastAPI._instrumented_fastapi_apps.clear()
        fastapi.FastAPI = self._original_fastapi


class _InstrumentedFastAPI(fastapi.FastAPI):
    _tracer_provider = None
    _meter_provider = None
    _excluded_urls = None
    _server_request_hook: _ServerRequestHookT = None
    _client_request_hook: _ClientRequestHookT = None
    _client_response_hook: _ClientResponseHookT = None
    _instrumented_fastapi_apps = set()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        meter = get_meter(
            __name__, __version__, _InstrumentedFastAPI._meter_provider
        )
        self.add_middleware(
            OpenTelemetryMiddleware,
            excluded_urls=_InstrumentedFastAPI._excluded_urls,
            default_span_details=_get_default_span_details,
            server_request_hook=_InstrumentedFastAPI._server_request_hook,
            client_request_hook=_InstrumentedFastAPI._client_request_hook,
            client_response_hook=_InstrumentedFastAPI._client_response_hook,
            tracer_provider=_InstrumentedFastAPI._tracer_provider,
            meter=meter,
        )
        self._is_instrumented_by_opentelemetry = True
        _InstrumentedFastAPI._instrumented_fastapi_apps.add(self)

    def __del__(self):
        if self in _InstrumentedFastAPI._instrumented_fastapi_apps:
            _InstrumentedFastAPI._instrumented_fastapi_apps.remove(self)


def _get_route_details(scope):
    """
    Function to retrieve Starlette route from scope.

    TODO: there is currently no way to retrieve http.route from
    a starlette application from scope.
    See: https://github.com/encode/starlette/pull/804

    Args:
        scope: A Starlette scope
    Returns:
        A string containing the route or None
    """
    app = scope["app"]
    route = None

    for starlette_route in app.routes:
        match, _ = starlette_route.matches(scope)
        if match == Match.FULL:
            route = starlette_route.path
            break
        if match == Match.PARTIAL:
            route = starlette_route.path
    return route


def _get_default_span_details(scope):
    """
    Callback to retrieve span name and attributes from scope.

    Args:
        scope: A Starlette scope
    Returns:
        A tuple of span name and attributes
    """
    route = _get_route_details(scope)
    method = scope.get("method", "")
    attributes = {}
    if route:
        attributes[SpanAttributes.HTTP_ROUTE] = route
    if method and route:  # http
        span_name = f"{method} {route}"
    elif route:  # websocket
        span_name = route
    else:  # fallback
        span_name = method
    return span_name, attributes
