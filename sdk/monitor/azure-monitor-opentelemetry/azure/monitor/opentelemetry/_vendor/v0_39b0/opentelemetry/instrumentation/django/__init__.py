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


from logging import getLogger
from os import environ
from typing import Collection

from django import VERSION as django_version
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from azure.monitor.opentelemetry._vendor.v0_39b0.opentelemetry.instrumentation.django.environment_variables import (
    OTEL_PYTHON_DJANGO_INSTRUMENT,
)
from azure.monitor.opentelemetry._vendor.v0_39b0.opentelemetry.instrumentation.django.middleware.otel_middleware import (
    _DjangoMiddleware,
)
from azure.monitor.opentelemetry._vendor.v0_39b0.opentelemetry.instrumentation.django.package import (
    _instruments
)
from azure.monitor.opentelemetry._vendor.v0_39b0.opentelemetry.instrumentation.django.version import (
    __version__
)
from azure.monitor.opentelemetry._vendor.v0_39b0.opentelemetry.instrumentation.instrumentor import (
    BaseInstrumentor
)
from opentelemetry.metrics import get_meter
from opentelemetry.semconv.metrics import MetricInstruments
from opentelemetry.trace import get_tracer
from azure.monitor.opentelemetry._vendor.v0_39b0.opentelemetry.util.http import get_excluded_urls, parse_excluded_urls

DJANGO_2_0 = django_version >= (2, 0)

_excluded_urls_from_env = get_excluded_urls("DJANGO")
_logger = getLogger(__name__)


def _get_django_middleware_setting() -> str:
    # In Django versions 1.x, setting MIDDLEWARE_CLASSES can be used as a legacy
    # alternative to MIDDLEWARE. This is the case when `settings.MIDDLEWARE` has
    # its default value (`None`).
    if not DJANGO_2_0 and getattr(settings, "MIDDLEWARE", None) is None:
        return "MIDDLEWARE_CLASSES"
    return "MIDDLEWARE"


class DjangoInstrumentor(BaseInstrumentor):
    """An instrumentor for Django

    See `BaseInstrumentor`
    """

    _opentelemetry_middleware = ".".join(
        [_DjangoMiddleware.__module__, _DjangoMiddleware.__qualname__]
    )

    _sql_commenter_middleware = "azure.monitor.opentelemetry._vendor.v0_39b0.opentelemetry.instrumentation.django.middleware.sqlcommenter_middleware.SqlCommenter"

    def instrumentation_dependencies(self) -> Collection[str]:
        return _instruments

    def _instrument(self, **kwargs):
        # FIXME this is probably a pattern that will show up in the rest of the
        # ext. Find a better way of implementing this.
        if environ.get(OTEL_PYTHON_DJANGO_INSTRUMENT) == "False":
            return

        tracer_provider = kwargs.get("tracer_provider")
        meter_provider = kwargs.get("meter_provider")
        _excluded_urls = kwargs.get("excluded_urls")
        tracer = get_tracer(
            __name__,
            __version__,
            tracer_provider=tracer_provider,
        )
        meter = get_meter(__name__, __version__, meter_provider=meter_provider)
        _DjangoMiddleware._tracer = tracer
        _DjangoMiddleware._meter = meter
        _DjangoMiddleware._excluded_urls = (
            _excluded_urls_from_env
            if _excluded_urls is None
            else parse_excluded_urls(_excluded_urls)
        )
        _DjangoMiddleware._otel_request_hook = kwargs.pop("request_hook", None)
        _DjangoMiddleware._otel_response_hook = kwargs.pop(
            "response_hook", None
        )
        _DjangoMiddleware._duration_histogram = meter.create_histogram(
            name=MetricInstruments.HTTP_SERVER_DURATION,
            unit="ms",
            description="measures the duration of the inbound http request",
        )
        _DjangoMiddleware._active_request_counter = meter.create_up_down_counter(
            name=MetricInstruments.HTTP_SERVER_ACTIVE_REQUESTS,
            unit="requests",
            description="measures the number of concurrent HTTP requests those are currently in flight",
        )
        # This can not be solved, but is an inherent problem of this approach:
        # the order of middleware entries matters, and here you have no control
        # on that:
        # https://docs.djangoproject.com/en/3.0/topics/http/middleware/#activating-middleware
        # https://docs.djangoproject.com/en/3.0/ref/middleware/#middleware-ordering

        _middleware_setting = _get_django_middleware_setting()
        settings_middleware = []
        try:
            settings_middleware = getattr(settings, _middleware_setting, [])
        except ImproperlyConfigured as exception:
            _logger.debug(
                "DJANGO_SETTINGS_MODULE environment variable not configured. Defaulting to empty settings: %s",
                exception,
            )
            settings.configure()
            settings_middleware = getattr(settings, _middleware_setting, [])
        except ModuleNotFoundError as exception:
            _logger.debug(
                "DJANGO_SETTINGS_MODULE points to a non-existent module. Defaulting to empty settings: %s",
                exception,
            )
            settings.configure()
            settings_middleware = getattr(settings, _middleware_setting, [])

        # Django allows to specify middlewares as a tuple, so we convert this tuple to a
        # list, otherwise we wouldn't be able to call append/remove
        if isinstance(settings_middleware, tuple):
            settings_middleware = list(settings_middleware)

        is_sql_commentor_enabled = kwargs.pop("is_sql_commentor_enabled", None)

        if is_sql_commentor_enabled:
            settings_middleware.insert(0, self._sql_commenter_middleware)

        settings_middleware.insert(0, self._opentelemetry_middleware)

        setattr(settings, _middleware_setting, settings_middleware)

    def _uninstrument(self, **kwargs):
        _middleware_setting = _get_django_middleware_setting()
        settings_middleware = getattr(settings, _middleware_setting, None)

        # FIXME This is starting to smell like trouble. We have 2 mechanisms
        # that may make this condition be True, one implemented in
        # BaseInstrumentor and another one implemented in _instrument. Both
        # stop _instrument from running and thus, settings_middleware not being
        # set.
        if settings_middleware is None or (
            self._opentelemetry_middleware not in settings_middleware
        ):
            return

        settings_middleware.remove(self._opentelemetry_middleware)
        setattr(settings, _middleware_setting, settings_middleware)
