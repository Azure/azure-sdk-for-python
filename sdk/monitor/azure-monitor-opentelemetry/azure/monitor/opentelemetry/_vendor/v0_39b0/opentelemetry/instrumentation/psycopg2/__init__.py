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

import psycopg2
from psycopg2.extensions import (
    cursor as pg_cursor,  # pylint: disable=no-name-in-module
)
from psycopg2.sql import Composed  # pylint: disable=no-name-in-module

from azure.monitor.opentelemetry._vendor.v0_39b0.opentelemetry.instrumentation import dbapi
from azure.monitor.opentelemetry._vendor.v0_39b0.opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from azure.monitor.opentelemetry._vendor.v0_39b0.opentelemetry.instrumentation.psycopg2.package import _instruments
from azure.monitor.opentelemetry._vendor.v0_39b0.opentelemetry.instrumentation.psycopg2.version import __version__

_logger = logging.getLogger(__name__)
_OTEL_CURSOR_FACTORY_KEY = "_otel_orig_cursor_factory"


class Psycopg2Instrumentor(BaseInstrumentor):
    _CONNECTION_ATTRIBUTES = {
        "database": "info.dbname",
        "port": "info.port",
        "host": "info.host",
        "user": "info.user",
    }

    _DATABASE_SYSTEM = "postgresql"

    def instrumentation_dependencies(self) -> Collection[str]:
        return _instruments

    def _instrument(self, **kwargs):
        """Integrate with PostgreSQL Psycopg library.
        Psycopg: http://initd.org/psycopg/
        """
        tracer_provider = kwargs.get("tracer_provider")
        enable_sqlcommenter = kwargs.get("enable_commenter", False)
        commenter_options = kwargs.get("commenter_options", {})
        dbapi.wrap_connect(
            __name__,
            psycopg2,
            "connect",
            self._DATABASE_SYSTEM,
            self._CONNECTION_ATTRIBUTES,
            version=__version__,
            tracer_provider=tracer_provider,
            db_api_integration_factory=DatabaseApiIntegration,
            enable_commenter=enable_sqlcommenter,
            commenter_options=commenter_options,
        )

    def _uninstrument(self, **kwargs):
        """ "Disable Psycopg2 instrumentation"""
        dbapi.unwrap_connect(psycopg2, "connect")

    # TODO(owais): check if core dbapi can do this for all dbapi implementations e.g, pymysql and mysql
    @staticmethod
    def instrument_connection(connection, tracer_provider=None):
        if not hasattr(connection, "_is_instrumented_by_opentelemetry"):
            connection._is_instrumented_by_opentelemetry = False

        if not connection._is_instrumented_by_opentelemetry:
            setattr(
                connection, _OTEL_CURSOR_FACTORY_KEY, connection.cursor_factory
            )
            connection.cursor_factory = _new_cursor_factory(
                tracer_provider=tracer_provider
            )
            connection._is_instrumented_by_opentelemetry = True
        else:
            _logger.warning(
                "Attempting to instrument Psycopg connection while already instrumented"
            )
        return connection

    # TODO(owais): check if core dbapi can do this for all dbapi implementations e.g, pymysql and mysql
    @staticmethod
    def uninstrument_connection(connection):
        connection.cursor_factory = getattr(
            connection, _OTEL_CURSOR_FACTORY_KEY, None
        )

        return connection


# TODO(owais): check if core dbapi can do this for all dbapi implementations e.g, pymysql and mysql
class DatabaseApiIntegration(dbapi.DatabaseApiIntegration):
    def wrapped_connection(
        self,
        connect_method: typing.Callable[..., typing.Any],
        args: typing.Tuple[typing.Any, typing.Any],
        kwargs: typing.Dict[typing.Any, typing.Any],
    ):
        """Add object proxy to connection object."""
        base_cursor_factory = kwargs.pop("cursor_factory", None)
        new_factory_kwargs = {"db_api": self}
        if base_cursor_factory:
            new_factory_kwargs["base_factory"] = base_cursor_factory
        kwargs["cursor_factory"] = _new_cursor_factory(**new_factory_kwargs)
        connection = connect_method(*args, **kwargs)
        self.get_connection_attributes(connection)
        return connection


class CursorTracer(dbapi.CursorTracer):
    def get_operation_name(self, cursor, args):
        if not args:
            return ""

        statement = args[0]
        if isinstance(statement, Composed):
            statement = statement.as_string(cursor)

        if isinstance(statement, str):
            # Strip leading comments so we get the operation name.
            return self._leading_comment_remover.sub("", statement).split()[0]

        return ""

    def get_statement(self, cursor, args):
        if not args:
            return ""

        statement = args[0]
        if isinstance(statement, Composed):
            statement = statement.as_string(cursor)
        return statement


def _new_cursor_factory(db_api=None, base_factory=None, tracer_provider=None):
    if not db_api:
        db_api = DatabaseApiIntegration(
            __name__,
            Psycopg2Instrumentor._DATABASE_SYSTEM,
            connection_attributes=Psycopg2Instrumentor._CONNECTION_ATTRIBUTES,
            version=__version__,
            tracer_provider=tracer_provider,
        )

    base_factory = base_factory or pg_cursor
    _cursor_tracer = CursorTracer(db_api)

    class TracedCursorFactory(base_factory):
        def execute(self, *args, **kwargs):
            return _cursor_tracer.traced_execution(
                self, super().execute, *args, **kwargs
            )

        def executemany(self, *args, **kwargs):
            return _cursor_tracer.traced_execution(
                self, super().executemany, *args, **kwargs
            )

        def callproc(self, *args, **kwargs):
            return _cursor_tracer.traced_execution(
                self, super().callproc, *args, **kwargs
            )

    return TracedCursorFactory
