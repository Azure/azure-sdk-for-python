#!/usr/bin/python
#
# Copyright The OpenTelemetry Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from contextlib import ExitStack
from logging import getLogger
from typing import Any, Type, TypeVar

# pylint: disable=no-name-in-module
from django import conf, get_version
from django.db import connections
from django.db.backends.utils import CursorDebugWrapper

from azure.monitor.opentelemetry._vendor.v0_39b0.opentelemetry.instrumentation.sqlcommenter_utils import (
    _add_sql_comment
)
from azure.monitor.opentelemetry._vendor.v0_39b0.opentelemetry.instrumentation.utils import (
    _get_opentelemetry_values
)
from opentelemetry.trace.propagation.tracecontext import (
    TraceContextTextMapPropagator,
)

_propagator = TraceContextTextMapPropagator()

_django_version = get_version()
_logger = getLogger(__name__)

T = TypeVar("T")  # pylint: disable-msg=invalid-name


class SqlCommenter:
    """
    Middleware to append a comment to each database query with details about
    the framework and the execution context.
    """

    def __init__(self, get_response) -> None:
        self.get_response = get_response

    def __call__(self, request) -> Any:
        with ExitStack() as stack:
            for db_alias in connections:
                stack.enter_context(
                    connections[db_alias].execute_wrapper(
                        _QueryWrapper(request)
                    )
                )
            return self.get_response(request)


class _QueryWrapper:
    def __init__(self, request) -> None:
        self.request = request

    def __call__(self, execute: Type[T], sql, params, many, context) -> T:
        # pylint: disable-msg=too-many-locals
        with_framework = getattr(
            conf.settings, "SQLCOMMENTER_WITH_FRAMEWORK", True
        )
        with_controller = getattr(
            conf.settings, "SQLCOMMENTER_WITH_CONTROLLER", True
        )
        with_route = getattr(conf.settings, "SQLCOMMENTER_WITH_ROUTE", True)
        with_app_name = getattr(
            conf.settings, "SQLCOMMENTER_WITH_APP_NAME", True
        )
        with_opentelemetry = getattr(
            conf.settings, "SQLCOMMENTER_WITH_OPENTELEMETRY", True
        )
        with_db_driver = getattr(
            conf.settings, "SQLCOMMENTER_WITH_DB_DRIVER", True
        )

        db_driver = context["connection"].settings_dict.get("ENGINE", "")
        resolver_match = self.request.resolver_match

        sql = _add_sql_comment(
            sql,
            # Information about the controller.
            controller=resolver_match.view_name
            if resolver_match and with_controller
            else None,
            # route is the pattern that matched a request with a controller i.e. the regex
            # See https://docs.djangoproject.com/en/stable/ref/urlresolvers/#django.urls.ResolverMatch.route
            # getattr() because the attribute doesn't exist in Django < 2.2.
            route=getattr(resolver_match, "route", None)
            if resolver_match and with_route
            else None,
            # app_name is the application namespace for the URL pattern that matches the URL.
            # See https://docs.djangoproject.com/en/stable/ref/urlresolvers/#django.urls.ResolverMatch.app_name
            app_name=(resolver_match.app_name or None)
            if resolver_match and with_app_name
            else None,
            # Framework centric information.
            framework=f"django:{_django_version}" if with_framework else None,
            # Information about the database and driver.
            db_driver=db_driver if with_db_driver else None,
            **_get_opentelemetry_values() if with_opentelemetry else {},
        )

        # TODO: MySQL truncates logs > 1024B so prepend comments
        # instead of statements, if the engine is MySQL.
        # See:
        #  * https://github.com/basecamp/marginalia/issues/61
        #  * https://github.com/basecamp/marginalia/pull/80

        # Add the query to the query log if debugging.
        if isinstance(context["cursor"], CursorDebugWrapper):
            context["connection"].queries_log.append(sql)

        return execute(sql, params, many, context)
