# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from typing import no_type_check, Optional, Tuple
from urllib.parse import urlparse

from opentelemetry.semconv.trace import DbSystemValues, SpanAttributes
from opentelemetry.util.types import Attributes


# pylint:disable=too-many-return-statements
def _get_default_port_db(db_system: str) -> int:
    if db_system == DbSystemValues.POSTGRESQL.value:
        return 5432
    if db_system == DbSystemValues.CASSANDRA.value:
        return 9042
    if db_system in (DbSystemValues.MARIADB.value, DbSystemValues.MYSQL.value):
        return 3306
    if db_system == DbSystemValues.MSSQL.value:
        return 1433
    # TODO: Add in memcached
    if db_system == "memcached":
        return 11211
    if db_system == DbSystemValues.DB2.value:
        return 50000
    if db_system == DbSystemValues.ORACLE.value:
        return 1521
    if db_system == DbSystemValues.H2.value:
        return 8082
    if db_system == DbSystemValues.DERBY.value:
        return 1527
    if db_system == DbSystemValues.REDIS.value:
        return 6379
    return 0


def _get_default_port_http(scheme: Optional[str]) -> int:
    if scheme == "http":
        return 80
    if scheme == "https":
        return 443
    return 0


def _is_sql_db(db_system: str) -> bool:
    return db_system in (
        DbSystemValues.DB2.value,
        DbSystemValues.DERBY.value,
        DbSystemValues.MARIADB.value,
        DbSystemValues.MSSQL.value,
        DbSystemValues.ORACLE.value,
        DbSystemValues.SQLITE.value,
        DbSystemValues.OTHER_SQL.value,
        # spell-checker:ignore HSQLDB
        DbSystemValues.HSQLDB.value,
        DbSystemValues.H2.value,
    )


def _get_azure_sdk_target_source(attributes: Attributes) -> Optional[str]:
    # Currently logic only works for ServiceBus and EventHub
    if attributes:
        peer_address = attributes.get("peer.address")
        destination = attributes.get("message_bus.destination")
        if peer_address and destination:
            return str(peer_address) + "/" + str(destination)
    return None


def _get_http_scheme(attributes: Attributes) -> Optional[str]:
    if attributes:
        scheme = attributes.get(SpanAttributes.HTTP_SCHEME)
        if scheme:
            return str(scheme)
    return None


@no_type_check
def _get_url_for_http_dependency(attributes: Attributes, scheme: Optional[str] = None) -> Optional[str]:
    url = None
    if attributes:
        if not scheme:
            scheme = _get_http_scheme(attributes)
        if SpanAttributes.HTTP_URL in attributes:
            url = attributes[SpanAttributes.HTTP_URL]
        elif scheme and SpanAttributes.HTTP_TARGET in attributes:
            http_target = attributes[SpanAttributes.HTTP_TARGET]
            if SpanAttributes.HTTP_HOST in attributes:
                url = "{}://{}{}".format(
                    str(scheme),
                    attributes[SpanAttributes.HTTP_HOST],
                    http_target,
                )
            elif SpanAttributes.NET_PEER_PORT in attributes:
                peer_port = attributes[SpanAttributes.NET_PEER_PORT]
                if SpanAttributes.NET_PEER_NAME in attributes:
                    peer_name = attributes[SpanAttributes.NET_PEER_NAME]
                    url = "{}://{}:{}{}".format(
                        scheme,
                        peer_name,
                        peer_port,
                        http_target,
                    )
                elif SpanAttributes.NET_PEER_IP in attributes:
                    peer_ip = attributes[SpanAttributes.NET_PEER_IP]
                    url = "{}://{}:{}{}".format(
                        scheme,
                        peer_ip,
                        peer_port,
                        http_target,
                    )
    return url  # type: ignore


@no_type_check
def _get_target_for_dependency_from_peer(attributes: Attributes) -> Optional[str]:
    target = ""
    if attributes:
        if SpanAttributes.PEER_SERVICE in attributes:
            target = attributes[SpanAttributes.PEER_SERVICE]  # type: ignore
        else:
            if SpanAttributes.NET_PEER_NAME in attributes:
                target = attributes[SpanAttributes.NET_PEER_NAME]  # type: ignore
            elif SpanAttributes.NET_PEER_IP in attributes:
                target = attributes[SpanAttributes.NET_PEER_IP]  # type: ignore
            if SpanAttributes.NET_PEER_PORT in attributes:
                port = attributes[SpanAttributes.NET_PEER_PORT]
                # TODO: check default port for rpc
                # This logic assumes default ports never conflict across dependency types
                # type: ignore
                if port != _get_default_port_http(
                    str(attributes.get(SpanAttributes.HTTP_SCHEME))
                ) and port != _get_default_port_db(str(attributes.get(SpanAttributes.DB_SYSTEM))):
                    target = "{}:{}".format(target, port)
    return target  # type: ignore


@no_type_check
def _get_target_and_path_for_http_dependency(
    attributes: Attributes,
    target: Optional[str],
    url: Optional[str],
    scheme: Optional[str] = None,
) -> Tuple[Optional[str], str]:
    target_from_url = None
    path = ""
    if attributes:
        if not scheme:
            scheme = _get_http_scheme(attributes)
        if url:
            try:
                parse_url = urlparse(url)
                path = parse_url.path
                if not path:
                    path = "/"
                if parse_url.port and parse_url.port == _get_default_port_http(scheme):
                    target_from_url = parse_url.hostname
                else:
                    target_from_url = parse_url.netloc
            except Exception:  # pylint: disable=broad-except
                pass
        if SpanAttributes.PEER_SERVICE not in attributes:
            if SpanAttributes.HTTP_HOST in attributes:
                host = attributes[SpanAttributes.HTTP_HOST]
                try:
                    # urlparse insists on absolute URLs starting with "//"
                    # This logic assumes host does not include a "//"
                    host_name = urlparse("//" + str(host))
                    if host_name.port == _get_default_port_http(scheme):
                        target = host_name.hostname
                    else:
                        target = str(host)
                except Exception:  # pylint: disable=broad-except
                    pass
            elif target_from_url and not target:
                target = target_from_url
    return (target, path)


@no_type_check
def _get_target_for_db_dependency(
    target: Optional[str],
    db_system: Optional[str],
    attributes: Attributes,
) -> Optional[str]:
    if attributes:
        db_name = attributes.get(SpanAttributes.DB_NAME)
        if db_name:
            if not target:
                target = str(db_name)
            else:
                target = "{}|{}".format(target, db_name)
        elif not target:
            target = db_system
    return target


@no_type_check
def _get_target_for_messaging_dependency(target: Optional[str], attributes: Attributes) -> Optional[str]:
    if attributes:
        if not target:
            if SpanAttributes.MESSAGING_DESTINATION in attributes:
                target = str(attributes[SpanAttributes.MESSAGING_DESTINATION])
            elif SpanAttributes.MESSAGING_SYSTEM in attributes:
                target = str(attributes[SpanAttributes.MESSAGING_SYSTEM])
    return target


@no_type_check
def _get_target_for_rpc_dependency(target: Optional[str], attributes: Attributes) -> Optional[str]:
    if attributes:
        if not target:
            if SpanAttributes.RPC_SYSTEM in attributes:
                target = str(attributes[SpanAttributes.RPC_SYSTEM])
    return target
