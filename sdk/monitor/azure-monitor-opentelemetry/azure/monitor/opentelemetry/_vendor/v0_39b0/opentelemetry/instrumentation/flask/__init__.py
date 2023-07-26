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

# Note: This package is not named "flask" because of
# https://github.com/PyCQA/pylint/issues/2648


from logging import getLogger
from threading import get_ident
from time import time_ns
from timeit import default_timer
from typing import Collection

import flask

import azure.monitor.opentelemetry._vendor.v0_39b0.opentelemetry.instrumentation.wsgi as otel_wsgi
from opentelemetry import context, trace
from azure.monitor.opentelemetry._vendor.v0_39b0.opentelemetry.instrumentation.flask.package import _instruments
from azure.monitor.opentelemetry._vendor.v0_39b0.opentelemetry.instrumentation.flask.version import __version__
from azure.monitor.opentelemetry._vendor.v0_39b0.opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from azure.monitor.opentelemetry._vendor.v0_39b0.opentelemetry.instrumentation.propagators import (
    get_global_response_propagator,
)
from azure.monitor.opentelemetry._vendor.v0_39b0.opentelemetry.instrumentation.utils import _start_internal_or_server_span
from opentelemetry.metrics import get_meter
from opentelemetry.semconv.metrics import MetricInstruments
from opentelemetry.semconv.trace import SpanAttributes
from azure.monitor.opentelemetry._vendor.v0_39b0.opentelemetry.util.http import get_excluded_urls, parse_excluded_urls

_logger = getLogger(__name__)

_ENVIRON_STARTTIME_KEY = "opentelemetry-flask.starttime_key"
_ENVIRON_SPAN_KEY = "opentelemetry-flask.span_key"
_ENVIRON_ACTIVATION_KEY = "opentelemetry-flask.activation_key"
_ENVIRON_THREAD_ID_KEY = "opentelemetry-flask.thread_id_key"
_ENVIRON_TOKEN = "opentelemetry-flask.token"

_excluded_urls_from_env = get_excluded_urls("FLASK")


def get_default_span_name():
    try:
        span_name = flask.request.url_rule.rule
    except AttributeError:
        span_name = otel_wsgi.get_default_span_name(flask.request.environ)
    return span_name


def _rewrapped_app(
    wsgi_app,
    active_requests_counter,
    duration_histogram,
    response_hook=None,
    excluded_urls=None,
):
    def _wrapped_app(wrapped_app_environ, start_response):
        # We want to measure the time for route matching, etc.
        # In theory, we could start the span here and use
        # update_name later but that API is "highly discouraged" so
        # we better avoid it.
        wrapped_app_environ[_ENVIRON_STARTTIME_KEY] = time_ns()
        start = default_timer()
        attributes = otel_wsgi.collect_request_attributes(wrapped_app_environ)
        active_requests_count_attrs = (
            otel_wsgi._parse_active_request_count_attrs(attributes)
        )
        duration_attrs = otel_wsgi._parse_duration_attrs(attributes)
        active_requests_counter.add(1, active_requests_count_attrs)

        def _start_response(status, response_headers, *args, **kwargs):
            if flask.request and (
                excluded_urls is None
                or not excluded_urls.url_disabled(flask.request.url)
            ):
                span = flask.request.environ.get(_ENVIRON_SPAN_KEY)

                propagator = get_global_response_propagator()
                if propagator:
                    propagator.inject(
                        response_headers,
                        setter=otel_wsgi.default_response_propagation_setter,
                    )

                if span:
                    otel_wsgi.add_response_attributes(
                        span, status, response_headers
                    )
                    status_code = otel_wsgi._parse_status_code(status)
                    if status_code is not None:
                        duration_attrs[
                            SpanAttributes.HTTP_STATUS_CODE
                        ] = status_code
                    if (
                        span.is_recording()
                        and span.kind == trace.SpanKind.SERVER
                    ):
                        custom_attributes = otel_wsgi.collect_custom_response_headers_attributes(
                            response_headers
                        )
                        if len(custom_attributes) > 0:
                            span.set_attributes(custom_attributes)
                else:
                    _logger.warning(
                        "Flask environ's OpenTelemetry span "
                        "missing at _start_response(%s)",
                        status,
                    )
                if response_hook is not None:
                    response_hook(span, status, response_headers)
            return start_response(status, response_headers, *args, **kwargs)

        result = wsgi_app(wrapped_app_environ, _start_response)
        duration = max(round((default_timer() - start) * 1000), 0)
        duration_histogram.record(duration, duration_attrs)
        active_requests_counter.add(-1, active_requests_count_attrs)
        return result

    return _wrapped_app


def _wrapped_before_request(
    request_hook=None,
    tracer=None,
    excluded_urls=None,
    enable_commenter=True,
    commenter_options=None,
):
    def _before_request():
        if excluded_urls and excluded_urls.url_disabled(flask.request.url):
            return
        flask_request_environ = flask.request.environ
        span_name = get_default_span_name()

        span, token = _start_internal_or_server_span(
            tracer=tracer,
            span_name=span_name,
            start_time=flask_request_environ.get(_ENVIRON_STARTTIME_KEY),
            context_carrier=flask_request_environ,
            context_getter=otel_wsgi.wsgi_getter,
        )

        if request_hook:
            request_hook(span, flask_request_environ)

        if span.is_recording():
            attributes = otel_wsgi.collect_request_attributes(
                flask_request_environ
            )
            if flask.request.url_rule:
                # For 404 that result from no route found, etc, we
                # don't have a url_rule.
                attributes[
                    SpanAttributes.HTTP_ROUTE
                ] = flask.request.url_rule.rule
            for key, value in attributes.items():
                span.set_attribute(key, value)
            if span.is_recording() and span.kind == trace.SpanKind.SERVER:
                custom_attributes = (
                    otel_wsgi.collect_custom_request_headers_attributes(
                        flask_request_environ
                    )
                )
                if len(custom_attributes) > 0:
                    span.set_attributes(custom_attributes)

        activation = trace.use_span(span, end_on_exit=True)
        activation.__enter__()  # pylint: disable=E1101
        flask_request_environ[_ENVIRON_ACTIVATION_KEY] = activation
        flask_request_environ[_ENVIRON_THREAD_ID_KEY] = get_ident()
        flask_request_environ[_ENVIRON_SPAN_KEY] = span
        flask_request_environ[_ENVIRON_TOKEN] = token

        if enable_commenter:
            current_context = context.get_current()
            flask_info = {}

            # https://flask.palletsprojects.com/en/1.1.x/api/#flask.has_request_context
            if flask and flask.request:
                if commenter_options.get("framework", True):
                    flask_info["framework"] = f"flask:{flask.__version__}"
                if (
                    commenter_options.get("controller", True)
                    and flask.request.endpoint
                ):
                    flask_info["controller"] = flask.request.endpoint
                if (
                    commenter_options.get("route", True)
                    and flask.request.url_rule
                    and flask.request.url_rule.rule
                ):
                    flask_info["route"] = flask.request.url_rule.rule
            sqlcommenter_context = context.set_value(
                "SQLCOMMENTER_ORM_TAGS_AND_VALUES", flask_info, current_context
            )
            context.attach(sqlcommenter_context)

    return _before_request


def _wrapped_teardown_request(
    excluded_urls=None,
):
    def _teardown_request(exc):
        # pylint: disable=E1101
        if excluded_urls and excluded_urls.url_disabled(flask.request.url):
            return

        activation = flask.request.environ.get(_ENVIRON_ACTIVATION_KEY)
        thread_id = flask.request.environ.get(_ENVIRON_THREAD_ID_KEY)
        if not activation or thread_id != get_ident():
            # This request didn't start a span, maybe because it was created in
            # a way that doesn't run `before_request`, like when it is created
            # with `app.test_request_context`.
            #
            # Similarly, check the thread_id against the current thread to ensure
            # tear down only happens on the original thread. This situation can
            # arise if the original thread handling the request spawn children
            # threads and then uses something like copy_current_request_context
            # to copy the request context.
            return
        if exc is None:
            activation.__exit__(None, None, None)
        else:
            activation.__exit__(
                type(exc), exc, getattr(exc, "__traceback__", None)
            )

        if flask.request.environ.get(_ENVIRON_TOKEN, None):
            context.detach(flask.request.environ.get(_ENVIRON_TOKEN))

    return _teardown_request


class _InstrumentedFlask(flask.Flask):
    _excluded_urls = None
    _tracer_provider = None
    _request_hook = None
    _response_hook = None
    _enable_commenter = True
    _commenter_options = None
    _meter_provider = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._original_wsgi_app = self.wsgi_app
        self._is_instrumented_by_opentelemetry = True

        meter = get_meter(
            __name__, __version__, _InstrumentedFlask._meter_provider
        )
        duration_histogram = meter.create_histogram(
            name=MetricInstruments.HTTP_SERVER_DURATION,
            unit="ms",
            description="measures the duration of the inbound HTTP request",
        )
        active_requests_counter = meter.create_up_down_counter(
            name=MetricInstruments.HTTP_SERVER_ACTIVE_REQUESTS,
            unit="requests",
            description="measures the number of concurrent HTTP requests that are currently in-flight",
        )

        self.wsgi_app = _rewrapped_app(
            self.wsgi_app,
            active_requests_counter,
            duration_histogram,
            _InstrumentedFlask._response_hook,
            excluded_urls=_InstrumentedFlask._excluded_urls,
        )

        tracer = trace.get_tracer(
            __name__, __version__, _InstrumentedFlask._tracer_provider
        )

        _before_request = _wrapped_before_request(
            _InstrumentedFlask._request_hook,
            tracer,
            excluded_urls=_InstrumentedFlask._excluded_urls,
            enable_commenter=_InstrumentedFlask._enable_commenter,
            commenter_options=_InstrumentedFlask._commenter_options,
        )
        self._before_request = _before_request
        self.before_request(_before_request)

        _teardown_request = _wrapped_teardown_request(
            excluded_urls=_InstrumentedFlask._excluded_urls,
        )
        self.teardown_request(_teardown_request)


class FlaskInstrumentor(BaseInstrumentor):
    # pylint: disable=protected-access,attribute-defined-outside-init
    """An instrumentor for flask.Flask

    See `BaseInstrumentor`
    """

    def instrumentation_dependencies(self) -> Collection[str]:
        return _instruments

    def _instrument(self, **kwargs):
        self._original_flask = flask.Flask
        request_hook = kwargs.get("request_hook")
        response_hook = kwargs.get("response_hook")
        if callable(request_hook):
            _InstrumentedFlask._request_hook = request_hook
        if callable(response_hook):
            _InstrumentedFlask._response_hook = response_hook
        tracer_provider = kwargs.get("tracer_provider")
        _InstrumentedFlask._tracer_provider = tracer_provider
        excluded_urls = kwargs.get("excluded_urls")
        _InstrumentedFlask._excluded_urls = (
            _excluded_urls_from_env
            if excluded_urls is None
            else parse_excluded_urls(excluded_urls)
        )
        enable_commenter = kwargs.get("enable_commenter", True)
        _InstrumentedFlask._enable_commenter = enable_commenter

        commenter_options = kwargs.get("commenter_options", {})
        _InstrumentedFlask._commenter_options = commenter_options
        meter_provider = kwargs.get("meter_provider")
        _InstrumentedFlask._meter_provider = meter_provider
        flask.Flask = _InstrumentedFlask

    def _uninstrument(self, **kwargs):
        flask.Flask = self._original_flask

    @staticmethod
    def instrument_app(
        app,
        request_hook=None,
        response_hook=None,
        tracer_provider=None,
        excluded_urls=None,
        enable_commenter=True,
        commenter_options=None,
        meter_provider=None,
    ):
        if not hasattr(app, "_is_instrumented_by_opentelemetry"):
            app._is_instrumented_by_opentelemetry = False

        if not app._is_instrumented_by_opentelemetry:
            excluded_urls = (
                parse_excluded_urls(excluded_urls)
                if excluded_urls is not None
                else _excluded_urls_from_env
            )
            meter = get_meter(__name__, __version__, meter_provider)
            duration_histogram = meter.create_histogram(
                name=MetricInstruments.HTTP_SERVER_DURATION,
                unit="ms",
                description="measures the duration of the inbound HTTP request",
            )
            active_requests_counter = meter.create_up_down_counter(
                name=MetricInstruments.HTTP_SERVER_ACTIVE_REQUESTS,
                unit="requests",
                description="measures the number of concurrent HTTP requests that are currently in-flight",
            )

            app._original_wsgi_app = app.wsgi_app
            app.wsgi_app = _rewrapped_app(
                app.wsgi_app,
                active_requests_counter,
                duration_histogram,
                response_hook,
                excluded_urls=excluded_urls,
            )

            tracer = trace.get_tracer(__name__, __version__, tracer_provider)

            _before_request = _wrapped_before_request(
                request_hook,
                tracer,
                excluded_urls=excluded_urls,
                enable_commenter=enable_commenter,
                commenter_options=commenter_options
                if commenter_options
                else {},
            )
            app._before_request = _before_request
            app.before_request(_before_request)

            _teardown_request = _wrapped_teardown_request(
                excluded_urls=excluded_urls,
            )
            app._teardown_request = _teardown_request
            app.teardown_request(_teardown_request)
            app._is_instrumented_by_opentelemetry = True
        else:
            _logger.warning(
                "Attempting to instrument Flask app while already instrumented"
            )

    @staticmethod
    def uninstrument_app(app):
        if hasattr(app, "_original_wsgi_app"):
            app.wsgi_app = app._original_wsgi_app

            # FIXME add support for other Flask blueprints that are not None
            app.before_request_funcs[None].remove(app._before_request)
            app.teardown_request_funcs[None].remove(app._teardown_request)
            del app._original_wsgi_app
            app._is_instrumented_by_opentelemetry = False
        else:
            _logger.warning(
                "Attempting to uninstrument Flask "
                "app while already uninstrumented"
            )
