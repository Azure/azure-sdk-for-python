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
import logging
import re
import typing

import wrapt

from opentelemetry import trace as trace_api
from azure.monitor.opentelemetry._vendor.v0_39b0.opentelemetry.instrumentation.dbapi.version import (
    __version__
)
from azure.monitor.opentelemetry._vendor.v0_39b0.opentelemetry.instrumentation.sqlcommenter_utils import (
    _add_sql_comment
)
from azure.monitor.opentelemetry._vendor.v0_39b0.opentelemetry.instrumentation.utils import (
    _get_opentelemetry_values,
    unwrap,
)
from opentelemetry.semconv.trace import SpanAttributes
from opentelemetry.trace import SpanKind, TracerProvider, get_tracer

_logger = logging.getLogger(__name__)


def trace_integration(
    connect_module: typing.Callable[..., typing.Any],
    connect_method_name: str,
    database_system: str,
    connection_attributes: typing.Dict = None,
    tracer_provider: typing.Optional[TracerProvider] = None,
    capture_parameters: bool = False,
    enable_commenter: bool = False,
    db_api_integration_factory=None,
):
    """Integrate with DB API library.
    https://www.python.org/dev/peps/pep-0249/

    Args:
        connect_module: Module name where connect method is available.
        connect_method_name: The connect method name.
        database_system: An identifier for the database management system (DBMS)
            product being used.
        connection_attributes: Attribute names for database, port, host and
            user in Connection object.
        tracer_provider: The :class:`opentelemetry.trace.TracerProvider` to
            use. If omitted the current configured one is used.
        capture_parameters: Configure if db.statement.parameters should be captured.
        enable_commenter: Flag to enable/disable sqlcommenter.
        db_api_integration_factory: The `DatabaseApiIntegration` to use. If none is passed the
            default one is used.
    """
    wrap_connect(
        __name__,
        connect_module,
        connect_method_name,
        database_system,
        connection_attributes,
        version=__version__,
        tracer_provider=tracer_provider,
        capture_parameters=capture_parameters,
        enable_commenter=enable_commenter,
        db_api_integration_factory=db_api_integration_factory,
    )


def wrap_connect(
    name: str,
    connect_module: typing.Callable[..., typing.Any],
    connect_method_name: str,
    database_system: str,
    connection_attributes: typing.Dict = None,
    version: str = "",
    tracer_provider: typing.Optional[TracerProvider] = None,
    capture_parameters: bool = False,
    enable_commenter: bool = False,
    db_api_integration_factory=None,
    commenter_options: dict = None,
):
    """Integrate with DB API library.
    https://www.python.org/dev/peps/pep-0249/

    Args:
        connect_module: Module name where connect method is available.
        connect_method_name: The connect method name.
        database_system: An identifier for the database management system (DBMS)
            product being used.
        connection_attributes: Attribute names for database, port, host and
            user in Connection object.
        tracer_provider: The :class:`opentelemetry.trace.TracerProvider` to
            use. If omitted the current configured one is used.
        capture_parameters: Configure if db.statement.parameters should be captured.
        enable_commenter: Flag to enable/disable sqlcommenter.
        db_api_integration_factory: The `DatabaseApiIntegration` to use. If none is passed the
            default one is used.
        commenter_options: Configurations for tags to be appended at the sql query.

    """
    db_api_integration_factory = (
        db_api_integration_factory or DatabaseApiIntegration
    )

    # pylint: disable=unused-argument
    def wrap_connect_(
        wrapped: typing.Callable[..., typing.Any],
        instance: typing.Any,
        args: typing.Tuple[typing.Any, typing.Any],
        kwargs: typing.Dict[typing.Any, typing.Any],
    ):
        db_integration = db_api_integration_factory(
            name,
            database_system,
            connection_attributes=connection_attributes,
            version=version,
            tracer_provider=tracer_provider,
            capture_parameters=capture_parameters,
            enable_commenter=enable_commenter,
            commenter_options=commenter_options,
            connect_module=connect_module,
        )
        return db_integration.wrapped_connection(wrapped, args, kwargs)

    try:
        wrapt.wrap_function_wrapper(
            connect_module, connect_method_name, wrap_connect_
        )
    except Exception as ex:  # pylint: disable=broad-except
        _logger.warning("Failed to integrate with DB API. %s", str(ex))


def unwrap_connect(
    connect_module: typing.Callable[..., typing.Any], connect_method_name: str
):
    """Disable integration with DB API library.
    https://www.python.org/dev/peps/pep-0249/

    Args:
        connect_module: Module name where the connect method is available.
        connect_method_name: The connect method name.
    """
    unwrap(connect_module, connect_method_name)


def instrument_connection(
    name: str,
    connection,
    database_system: str,
    connection_attributes: typing.Dict = None,
    version: str = "",
    tracer_provider: typing.Optional[TracerProvider] = None,
    capture_parameters: bool = False,
    enable_commenter: bool = False,
    commenter_options: dict = None,
):
    """Enable instrumentation in a database connection.

    Args:
        connection: The connection to instrument.
        database_system: An identifier for the database management system (DBMS)
            product being used.
        connection_attributes: Attribute names for database, port, host and
            user in a connection object.
        tracer_provider: The :class:`opentelemetry.trace.TracerProvider` to
            use. If omitted the current configured one is used.
        capture_parameters: Configure if db.statement.parameters should be captured.
        enable_commenter: Flag to enable/disable sqlcommenter.
        commenter_options: Configurations for tags to be appended at the sql query.

    Returns:
        An instrumented connection.
    """
    if isinstance(connection, wrapt.ObjectProxy):
        _logger.warning("Connection already instrumented")
        return connection

    db_integration = DatabaseApiIntegration(
        name,
        database_system,
        connection_attributes=connection_attributes,
        version=version,
        tracer_provider=tracer_provider,
        capture_parameters=capture_parameters,
        enable_commenter=enable_commenter,
        commenter_options=commenter_options,
    )
    db_integration.get_connection_attributes(connection)
    return get_traced_connection_proxy(connection, db_integration)


def uninstrument_connection(connection):
    """Disable instrumentation in a database connection.

    Args:
        connection: The connection to uninstrument.

    Returns:
        An uninstrumented connection.
    """
    if isinstance(connection, wrapt.ObjectProxy):
        return connection.__wrapped__

    _logger.warning("Connection is not instrumented")
    return connection


class DatabaseApiIntegration:
    def __init__(
        self,
        name: str,
        database_system: str,
        connection_attributes=None,
        version: str = "",
        tracer_provider: typing.Optional[TracerProvider] = None,
        capture_parameters: bool = False,
        enable_commenter: bool = False,
        commenter_options: dict = None,
        connect_module: typing.Callable[..., typing.Any] = None,
    ):
        self.connection_attributes = connection_attributes
        if self.connection_attributes is None:
            self.connection_attributes = {
                "database": "database",
                "port": "port",
                "host": "host",
                "user": "user",
            }
        self._name = name
        self._version = version
        self._tracer = get_tracer(
            self._name,
            instrumenting_library_version=self._version,
            tracer_provider=tracer_provider,
        )
        self.capture_parameters = capture_parameters
        self.enable_commenter = enable_commenter
        self.commenter_options = commenter_options
        self.database_system = database_system
        self.connection_props = {}
        self.span_attributes = {}
        self.name = ""
        self.database = ""
        self.connect_module = connect_module

    def wrapped_connection(
        self,
        connect_method: typing.Callable[..., typing.Any],
        args: typing.Tuple[typing.Any, typing.Any],
        kwargs: typing.Dict[typing.Any, typing.Any],
    ):
        """Add object proxy to connection object."""
        connection = connect_method(*args, **kwargs)
        self.get_connection_attributes(connection)
        return get_traced_connection_proxy(connection, self)

    def get_connection_attributes(self, connection):
        # Populate span fields using connection
        for key, value in self.connection_attributes.items():
            # Allow attributes nested in connection object
            attribute = functools.reduce(
                lambda attribute, attribute_value: getattr(
                    attribute, attribute_value, None
                ),
                value.split("."),
                connection,
            )
            if attribute:
                self.connection_props[key] = attribute
        self.name = self.database_system
        self.database = self.connection_props.get("database", "")
        if self.database:
            # PyMySQL encodes names with utf-8
            if hasattr(self.database, "decode"):
                self.database = self.database.decode(errors="ignore")
            self.name += "." + self.database
        user = self.connection_props.get("user")
        # PyMySQL encodes this data
        if user and isinstance(user, bytes):
            user = user.decode()
        if user is not None:
            self.span_attributes[SpanAttributes.DB_USER] = str(user)
        host = self.connection_props.get("host")
        if host is not None:
            self.span_attributes[SpanAttributes.NET_PEER_NAME] = host
        port = self.connection_props.get("port")
        if port is not None:
            self.span_attributes[SpanAttributes.NET_PEER_PORT] = port


def get_traced_connection_proxy(
    connection, db_api_integration, *args, **kwargs
):
    # pylint: disable=abstract-method
    class TracedConnectionProxy(wrapt.ObjectProxy):
        # pylint: disable=unused-argument
        def __init__(self, connection, *args, **kwargs):
            wrapt.ObjectProxy.__init__(self, connection)

        def __getattribute__(self, name):
            if object.__getattribute__(self, name):
                return object.__getattribute__(self, name)

            return object.__getattribute__(
                object.__getattribute__(self, "_connection"), name
            )

        def cursor(self, *args, **kwargs):
            return get_traced_cursor_proxy(
                self.__wrapped__.cursor(*args, **kwargs), db_api_integration
            )

        def __enter__(self):
            self.__wrapped__.__enter__()
            return self

        def __exit__(self, *args, **kwargs):
            self.__wrapped__.__exit__(*args, **kwargs)

    return TracedConnectionProxy(connection, *args, **kwargs)


class CursorTracer:
    def __init__(self, db_api_integration: DatabaseApiIntegration) -> None:
        self._db_api_integration = db_api_integration
        self._commenter_enabled = self._db_api_integration.enable_commenter
        self._commenter_options = (
            self._db_api_integration.commenter_options
            if self._db_api_integration.commenter_options
            else {}
        )
        self._connect_module = self._db_api_integration.connect_module
        self._leading_comment_remover = re.compile(r"^/\*.*?\*/")

    def _populate_span(
        self,
        span: trace_api.Span,
        cursor,
        *args: typing.Tuple[typing.Any, typing.Any],
    ):
        if not span.is_recording():
            return
        statement = self.get_statement(cursor, args)
        span.set_attribute(
            SpanAttributes.DB_SYSTEM, self._db_api_integration.database_system
        )
        span.set_attribute(
            SpanAttributes.DB_NAME, self._db_api_integration.database
        )
        span.set_attribute(SpanAttributes.DB_STATEMENT, statement)

        for (
            attribute_key,
            attribute_value,
        ) in self._db_api_integration.span_attributes.items():
            span.set_attribute(attribute_key, attribute_value)

        if self._db_api_integration.capture_parameters and len(args) > 1:
            span.set_attribute("db.statement.parameters", str(args[1]))

    def get_operation_name(self, cursor, args):  # pylint: disable=no-self-use
        if args and isinstance(args[0], str):
            # Strip leading comments so we get the operation name.
            return self._leading_comment_remover.sub("", args[0]).split()[0]
        return ""

    def get_statement(self, cursor, args):  # pylint: disable=no-self-use
        if not args:
            return ""
        statement = args[0]
        if isinstance(statement, bytes):
            return statement.decode("utf8", "replace")
        return statement

    def traced_execution(
        self,
        cursor,
        query_method: typing.Callable[..., typing.Any],
        *args: typing.Tuple[typing.Any, typing.Any],
        **kwargs: typing.Dict[typing.Any, typing.Any],
    ):
        name = self.get_operation_name(cursor, args)
        if not name:
            name = (
                self._db_api_integration.database
                if self._db_api_integration.database
                else self._db_api_integration.name
            )

        with self._db_api_integration._tracer.start_as_current_span(
            name, kind=SpanKind.CLIENT
        ) as span:
            self._populate_span(span, cursor, *args)
            if args and self._commenter_enabled:
                try:
                    args_list = list(args)
                    commenter_data = dict(
                        # Psycopg2/framework information
                        db_driver=f"psycopg2:{self._connect_module.__version__.split(' ')[0]}",
                        dbapi_threadsafety=self._connect_module.threadsafety,
                        dbapi_level=self._connect_module.apilevel,
                        libpq_version=self._connect_module.__libpq_version__,
                        driver_paramstyle=self._connect_module.paramstyle,
                    )
                    if self._commenter_options.get(
                        "opentelemetry_values", True
                    ):
                        commenter_data.update(**_get_opentelemetry_values())

                    # Filter down to just the requested attributes.
                    commenter_data = {
                        k: v
                        for k, v in commenter_data.items()
                        if self._commenter_options.get(k, True)
                    }
                    statement = _add_sql_comment(
                        args_list[0], **commenter_data
                    )

                    args_list[0] = statement
                    args = tuple(args_list)

                except Exception as exc:  # pylint: disable=broad-except
                    _logger.exception(
                        "Exception while generating sql comment: %s", exc
                    )
            return query_method(*args, **kwargs)


def get_traced_cursor_proxy(cursor, db_api_integration, *args, **kwargs):
    _cursor_tracer = CursorTracer(db_api_integration)

    # pylint: disable=abstract-method
    class TracedCursorProxy(wrapt.ObjectProxy):
        # pylint: disable=unused-argument
        def __init__(self, cursor, *args, **kwargs):
            wrapt.ObjectProxy.__init__(self, cursor)

        def execute(self, *args, **kwargs):
            return _cursor_tracer.traced_execution(
                self.__wrapped__, self.__wrapped__.execute, *args, **kwargs
            )

        def executemany(self, *args, **kwargs):
            return _cursor_tracer.traced_execution(
                self.__wrapped__, self.__wrapped__.executemany, *args, **kwargs
            )

        def callproc(self, *args, **kwargs):
            return _cursor_tracer.traced_execution(
                self.__wrapped__, self.__wrapped__.callproc, *args, **kwargs
            )

        def __enter__(self):
            self.__wrapped__.__enter__()
            return self

        def __exit__(self, *args, **kwargs):
            self.__wrapped__.__exit__(*args, **kwargs)

    return TracedCursorProxy(cursor, *args, **kwargs)
