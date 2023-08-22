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
# pylint: disable=too-many-locals


import typing
import urllib
from functools import wraps
from timeit import default_timer
from typing import Tuple

from asgiref.compatibility import guarantee_single_callable

from opentelemetry import context, trace
from azure.monitor.opentelemetry._vendor.v0_39b0.opentelemetry.instrumentation.asgi.version import (
    __version__
)  # noqa
from azure.monitor.opentelemetry._vendor.v0_39b0.opentelemetry.instrumentation.propagators import (
    get_global_response_propagator,
)
from azure.monitor.opentelemetry._vendor.v0_39b0.opentelemetry.instrumentation.utils import (
    _start_internal_or_server_span,
    http_status_to_status_code,
)
from opentelemetry.metrics import get_meter
from opentelemetry.propagators.textmap import Getter, Setter
from opentelemetry.semconv.metrics import MetricInstruments
from opentelemetry.semconv.trace import SpanAttributes
from opentelemetry.trace import Span, set_span_in_context
from opentelemetry.trace.status import Status, StatusCode
from azure.monitor.opentelemetry._vendor.v0_39b0.opentelemetry.util.http import (
    OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SANITIZE_FIELDS,
    OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SERVER_REQUEST,
    OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SERVER_RESPONSE,
    SanitizeValue,
    _parse_active_request_count_attrs,
    _parse_duration_attrs,
    get_custom_headers,
    normalise_request_header_name,
    normalise_response_header_name,
    remove_url_credentials,
)

_ServerRequestHookT = typing.Optional[typing.Callable[[Span, dict], None]]
_ClientRequestHookT = typing.Optional[typing.Callable[[Span, dict], None]]
_ClientResponseHookT = typing.Optional[typing.Callable[[Span, dict], None]]


class ASGIGetter(Getter[dict]):
    def get(
        self, carrier: dict, key: str
    ) -> typing.Optional[typing.List[str]]:
        """Getter implementation to retrieve a HTTP header value from the ASGI
        scope.

        Args:
            carrier: ASGI scope object
            key: header name in scope
        Returns:
            A list with a single string with the header value if it exists,
                else None.
        """
        headers = carrier.get("headers")
        if not headers:
            return None

        # ASGI header keys are in lower case
        key = key.lower()
        decoded = [
            _value.decode("utf8")
            for (_key, _value) in headers
            if _key.decode("utf8").lower() == key
        ]
        if not decoded:
            return None
        return decoded

    def keys(self, carrier: dict) -> typing.List[str]:
        headers = carrier.get("headers") or []
        return [_key.decode("utf8") for (_key, _value) in headers]


asgi_getter = ASGIGetter()


class ASGISetter(Setter[dict]):
    def set(
        self, carrier: dict, key: str, value: str
    ) -> None:  # pylint: disable=no-self-use
        """Sets response header values on an ASGI scope according to `the spec <https://asgi.readthedocs.io/en/latest/specs/www.html#response-start-send-event>`_.

        Args:
            carrier: ASGI scope object
            key: response header name to set
            value: response header value
        Returns:
            None
        """
        headers = carrier.get("headers")
        if not headers:
            headers = []
            carrier["headers"] = headers

        headers.append([key.lower().encode(), value.encode()])


asgi_setter = ASGISetter()


def collect_request_attributes(scope):
    """Collects HTTP request attributes from the ASGI scope and returns a
    dictionary to be used as span creation attributes."""
    server_host, port, http_url = get_host_port_url_tuple(scope)
    query_string = scope.get("query_string")
    if query_string and http_url:
        if isinstance(query_string, bytes):
            query_string = query_string.decode("utf8")
        http_url += "?" + urllib.parse.unquote(query_string)

    result = {
        SpanAttributes.HTTP_SCHEME: scope.get("scheme"),
        SpanAttributes.HTTP_HOST: server_host,
        SpanAttributes.NET_HOST_PORT: port,
        SpanAttributes.HTTP_FLAVOR: scope.get("http_version"),
        SpanAttributes.HTTP_TARGET: scope.get("path"),
        SpanAttributes.HTTP_URL: remove_url_credentials(http_url),
    }
    http_method = scope.get("method")
    if http_method:
        result[SpanAttributes.HTTP_METHOD] = http_method

    http_host_value_list = asgi_getter.get(scope, "host")
    if http_host_value_list:
        result[SpanAttributes.HTTP_SERVER_NAME] = ",".join(
            http_host_value_list
        )
    http_user_agent = asgi_getter.get(scope, "user-agent")
    if http_user_agent:
        result[SpanAttributes.HTTP_USER_AGENT] = http_user_agent[0]

    if "client" in scope and scope["client"] is not None:
        result[SpanAttributes.NET_PEER_IP] = scope.get("client")[0]
        result[SpanAttributes.NET_PEER_PORT] = scope.get("client")[1]

    # remove None values
    result = {k: v for k, v in result.items() if v is not None}

    return result


def collect_custom_request_headers_attributes(scope):
    """returns custom HTTP request headers to be added into SERVER span as span attributes
    Refer specification https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/trace/semantic_conventions/http.md#http-request-and-response-headers
    """

    sanitize = SanitizeValue(
        get_custom_headers(
            OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SANITIZE_FIELDS
        )
    )

    # Decode headers before processing.
    headers = {
        _key.decode("utf8"): _value.decode("utf8")
        for (_key, _value) in scope.get("headers")
    }

    return sanitize.sanitize_header_values(
        headers,
        get_custom_headers(
            OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SERVER_REQUEST
        ),
        normalise_request_header_name,
    )


def collect_custom_response_headers_attributes(message):
    """returns custom HTTP response headers to be added into SERVER span as span attributes
    Refer specification https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/trace/semantic_conventions/http.md#http-request-and-response-headers
    """

    sanitize = SanitizeValue(
        get_custom_headers(
            OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SANITIZE_FIELDS
        )
    )

    # Decode headers before processing.
    headers = {
        _key.decode("utf8"): _value.decode("utf8")
        for (_key, _value) in message.get("headers")
    }

    return sanitize.sanitize_header_values(
        headers,
        get_custom_headers(
            OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SERVER_RESPONSE
        ),
        normalise_response_header_name,
    )


def get_host_port_url_tuple(scope):
    """Returns (host, port, full_url) tuple."""
    server = scope.get("server") or ["0.0.0.0", 80]  # nosec
    port = server[1]
    server_host = server[0] + (":" + str(port) if str(port) != "80" else "")
    full_path = scope.get("root_path", "") + scope.get("path", "")
    http_url = scope.get("scheme", "http") + "://" + server_host + full_path
    return server_host, port, http_url


def set_status_code(span, status_code):
    """Adds HTTP response attributes to span using the status_code argument."""
    if not span.is_recording():
        return
    try:
        status_code = int(status_code)
    except ValueError:
        span.set_status(
            Status(
                StatusCode.ERROR,
                "Non-integer HTTP status: " + repr(status_code),
            )
        )
    else:
        span.set_attribute(SpanAttributes.HTTP_STATUS_CODE, status_code)
        span.set_status(
            Status(http_status_to_status_code(status_code, server_span=True))
        )


def get_default_span_details(scope: dict) -> Tuple[str, dict]:
    """Default implementation for get_default_span_details
    Args:
        scope: the ASGI scope dictionary
    Returns:
        a tuple of the span name, and any attributes to attach to the span.
    """
    span_name = (
        scope.get("path", "").strip()
        or f"HTTP {scope.get('method', '').strip()}"
    )

    return span_name, {}


def _collect_target_attribute(
    scope: typing.Dict[str, typing.Any]
) -> typing.Optional[str]:
    """
    Returns the target path as defined by the Semantic Conventions.

    This value is suitable to use in metrics as it should replace concrete
    values with a parameterized name. Example: /api/users/{user_id}

    Refer to the specification
    https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/metrics/semantic_conventions/http-metrics.md#parameterized-attributes

    Note: this function requires specific code for each framework, as there's no
    standard attribute to use.
    """
    # FastAPI
    root_path = scope.get("root_path", "")

    route = scope.get("route")
    path_format = getattr(route, "path_format", None)
    if path_format:
        return f"{root_path}{path_format}"

    return None


class OpenTelemetryMiddleware:
    """The ASGI application middleware.

    This class is an ASGI middleware that starts and annotates spans for any
    requests it is invoked with.

    Args:
        app: The ASGI application callable to forward requests to.
        default_span_details: Callback which should return a string and a tuple, representing the desired default span name and a
                      dictionary with any additional span attributes to set.
                      Optional: Defaults to get_default_span_details.
        server_request_hook: Optional callback which is called with the server span and ASGI
                      scope object for every incoming request.
        client_request_hook: Optional callback which is called with the internal span and an ASGI
                      scope which is sent as a dictionary for when the method receive is called.
        client_response_hook: Optional callback which is called with the internal span and an ASGI
                      event which is sent as a dictionary for when the method send is called.
        tracer_provider: The optional tracer provider to use. If omitted
            the current globally configured one is used.
    """

    # pylint: disable=too-many-branches
    def __init__(
        self,
        app,
        excluded_urls=None,
        default_span_details=None,
        server_request_hook: _ServerRequestHookT = None,
        client_request_hook: _ClientRequestHookT = None,
        client_response_hook: _ClientResponseHookT = None,
        tracer_provider=None,
        meter_provider=None,
        meter=None,
    ):
        self.app = guarantee_single_callable(app)
        self.tracer = trace.get_tracer(__name__, __version__, tracer_provider)
        self.meter = (
            get_meter(__name__, __version__, meter_provider)
            if meter is None
            else meter
        )
        self.duration_histogram = self.meter.create_histogram(
            name=MetricInstruments.HTTP_SERVER_DURATION,
            unit="ms",
            description="measures the duration of the inbound HTTP request",
        )
        self.active_requests_counter = self.meter.create_up_down_counter(
            name=MetricInstruments.HTTP_SERVER_ACTIVE_REQUESTS,
            unit="requests",
            description="measures the number of concurrent HTTP requests that are currently in-flight",
        )
        self.excluded_urls = excluded_urls
        self.default_span_details = (
            default_span_details or get_default_span_details
        )
        self.server_request_hook = server_request_hook
        self.client_request_hook = client_request_hook
        self.client_response_hook = client_response_hook

    async def __call__(self, scope, receive, send):
        """The ASGI application

        Args:
            scope: An ASGI environment.
            receive: An awaitable callable yielding dictionaries
            send: An awaitable callable taking a single dictionary as argument.
        """
        if scope["type"] not in ("http", "websocket"):
            return await self.app(scope, receive, send)

        _, _, url = get_host_port_url_tuple(scope)
        if self.excluded_urls and self.excluded_urls.url_disabled(url):
            return await self.app(scope, receive, send)

        span_name, additional_attributes = self.default_span_details(scope)

        attributes = collect_request_attributes(scope)
        attributes.update(additional_attributes)
        span, token = _start_internal_or_server_span(
            tracer=self.tracer,
            span_name=span_name,
            start_time=None,
            context_carrier=scope,
            context_getter=asgi_getter,
            attributes=attributes,
        )
        active_requests_count_attrs = _parse_active_request_count_attrs(
            attributes
        )
        duration_attrs = _parse_duration_attrs(attributes)

        if scope["type"] == "http":
            self.active_requests_counter.add(1, active_requests_count_attrs)
        try:
            with trace.use_span(span, end_on_exit=True) as current_span:
                if current_span.is_recording():
                    for key, value in attributes.items():
                        current_span.set_attribute(key, value)

                    if current_span.kind == trace.SpanKind.SERVER:
                        custom_attributes = (
                            collect_custom_request_headers_attributes(scope)
                        )
                        if len(custom_attributes) > 0:
                            current_span.set_attributes(custom_attributes)

                if callable(self.server_request_hook):
                    self.server_request_hook(current_span, scope)

                otel_receive = self._get_otel_receive(
                    span_name, scope, receive
                )

                otel_send = self._get_otel_send(
                    current_span,
                    span_name,
                    scope,
                    send,
                    duration_attrs,
                )
                start = default_timer()

                await self.app(scope, otel_receive, otel_send)
        finally:
            if scope["type"] == "http":
                target = _collect_target_attribute(scope)
                if target:
                    duration_attrs[SpanAttributes.HTTP_TARGET] = target
                duration = max(round((default_timer() - start) * 1000), 0)
                self.duration_histogram.record(duration, duration_attrs)
                self.active_requests_counter.add(
                    -1, active_requests_count_attrs
                )
            if token:
                context.detach(token)

    # pylint: enable=too-many-branches

    def _get_otel_receive(self, server_span_name, scope, receive):
        @wraps(receive)
        async def otel_receive():
            with self.tracer.start_as_current_span(
                " ".join((server_span_name, scope["type"], "receive"))
            ) as receive_span:
                if callable(self.client_request_hook):
                    self.client_request_hook(receive_span, scope)
                message = await receive()
                if receive_span.is_recording():
                    if message["type"] == "websocket.receive":
                        set_status_code(receive_span, 200)
                    receive_span.set_attribute("type", message["type"])
            return message

        return otel_receive

    def _get_otel_send(
        self, server_span, server_span_name, scope, send, duration_attrs
    ):
        @wraps(send)
        async def otel_send(message):
            with self.tracer.start_as_current_span(
                " ".join((server_span_name, scope["type"], "send"))
            ) as send_span:
                if callable(self.client_response_hook):
                    self.client_response_hook(send_span, message)
                if send_span.is_recording():
                    if message["type"] == "http.response.start":
                        status_code = message["status"]
                        duration_attrs[
                            SpanAttributes.HTTP_STATUS_CODE
                        ] = status_code
                        set_status_code(server_span, status_code)
                        set_status_code(send_span, status_code)
                    elif message["type"] == "websocket.send":
                        set_status_code(server_span, 200)
                        set_status_code(send_span, 200)
                    send_span.set_attribute("type", message["type"])
                    if (
                        server_span.is_recording()
                        and server_span.kind == trace.SpanKind.SERVER
                        and "headers" in message
                    ):
                        custom_response_attributes = (
                            collect_custom_response_headers_attributes(message)
                        )
                        if len(custom_response_attributes) > 0:
                            server_span.set_attributes(
                                custom_response_attributes
                            )

                propagator = get_global_response_propagator()
                if propagator:
                    propagator.inject(
                        message,
                        context=set_span_in_context(
                            server_span, trace.context_api.Context()
                        ),
                        setter=asgi_setter,
                    )

                await send(message)

        return otel_send
