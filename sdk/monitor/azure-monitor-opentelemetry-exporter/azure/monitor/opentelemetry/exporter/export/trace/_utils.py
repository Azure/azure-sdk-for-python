# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from typing import no_type_check, Optional, Tuple
from urllib.parse import urlparse

from opentelemetry.semconv.attributes import (
    client_attributes,
    server_attributes,
    url_attributes,
    user_agent_attributes,
)
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


def _get_default_port_http(attributes: Attributes) -> int:
    scheme = _get_http_scheme(attributes)
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
        # New semconv attributes: https://github.com/Azure/azure-sdk-for-python/pull/29203
        peer_address = (
            attributes.get("server.address") or attributes.get("net.peer.name") or attributes.get("peer.address")
        )
        destination = attributes.get("messaging.destination.name") or attributes.get("message_bus.destination")
        if peer_address and destination:
            return str(peer_address) + "/" + str(destination)
    return None


def _get_http_scheme(attributes: Attributes) -> Optional[str]:
    if attributes:
        scheme = attributes.get(url_attributes.URL_SCHEME) or \
            attributes.get(SpanAttributes.HTTP_SCHEME)
        if scheme:
            return str(scheme)
    return None


# Dependency


@no_type_check
def _get_url_for_http_dependency(attributes: Attributes) -> Optional[str]:
    url = ""
    if attributes:
        # Stable sem conv only supports populating url from `url.full`
        if url_attributes.URL_FULL in attributes:
            return attributes[url_attributes.URL_FULL]
        if SpanAttributes.HTTP_URL in attributes:
            return attributes[SpanAttributes.HTTP_URL]
        # Scheme
        scheme = _get_http_scheme(attributes)
        if scheme and SpanAttributes.HTTP_TARGET in attributes:
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
    return url


@no_type_check
def _get_target_for_dependency_from_peer(attributes: Attributes) -> Optional[str]:
    target = ""
    if attributes:
        if SpanAttributes.PEER_SERVICE in attributes:
            target = attributes[SpanAttributes.PEER_SERVICE]
        else:
            if SpanAttributes.NET_PEER_NAME in attributes:
                target = attributes[SpanAttributes.NET_PEER_NAME]
            elif SpanAttributes.NET_PEER_IP in attributes:
                target = attributes[SpanAttributes.NET_PEER_IP]
            if SpanAttributes.NET_PEER_PORT in attributes:
                port = attributes[SpanAttributes.NET_PEER_PORT]
                # TODO: check default port for rpc
                # This logic assumes default ports never conflict across dependency types
                if port != _get_default_port_http(attributes) and \
                    port != _get_default_port_db(str(attributes.get(SpanAttributes.DB_SYSTEM))):
                    target = "{}:{}".format(target, port)
    return target


@no_type_check
def _get_target_and_path_for_http_dependency(
    attributes: Attributes,
    url: Optional[str] = "",  # Usually populated by _get_url_for_http_dependency()
) -> Tuple[Optional[str], str]:
    parsed_url = None
    target = ""
    path = "/"
    default_port = _get_default_port_http(attributes)
    # Find path from url
    if not url:
        url = _get_url_for_http_dependency(attributes)
    try:
        parsed_url = urlparse(url)
        if parsed_url.path:
            path = parsed_url.path
    except Exception:  # pylint: disable=broad-except
        pass
    # Derive target
    if attributes:
        # Target from server.*
        if server_attributes.SERVER_ADDRESS in attributes:
            target = attributes[server_attributes.SERVER_ADDRESS]
            server_port = attributes.get(server_attributes.SERVER_PORT)
            # if not default port, include port in target
            if server_port != default_port:
                target = "{}:{}".format(target, server_port)
        # Target from peer.service
        elif SpanAttributes.PEER_SERVICE in attributes:
            target = attributes[SpanAttributes.PEER_SERVICE]
        # Target from http.host
        elif SpanAttributes.HTTP_HOST in attributes:
            host = attributes[SpanAttributes.HTTP_HOST]
            try:
                # urlparse insists on absolute URLs starting with "//"
                # This logic assumes host does not include a "//"
                host_name = urlparse("//" + str(host))
                # Ignore port from target if default port
                if host_name.port == default_port:
                    target = host_name.hostname
                else:
                    # Else include the whole host as the target
                    target = str(host)
            except Exception:  # pylint: disable=broad-except
                pass
        elif parsed_url:
            # Target from httpUrl
            if parsed_url.port and parsed_url.port == default_port:
                if parsed_url.hostname:
                    target = parsed_url.hostname
            elif parsed_url.netloc:
                target = parsed_url.netloc
        if not target:
            # Get target from peer.* attributes that are NOT peer.service
            target = _get_target_for_dependency_from_peer(attributes)
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


# Request

@no_type_check
def _get_location_ip(attributes: Attributes) -> Optional[str]:
    return attributes.get(client_attributes.CLIENT_ADDRESS) or \
        attributes.get(SpanAttributes.HTTP_CLIENT_IP) or \
        attributes.get(SpanAttributes.NET_PEER_IP) # We assume non-http spans don't have http related attributes


@no_type_check
def _get_user_agent(attributes: Attributes) -> Optional[str]:
    return attributes.get(user_agent_attributes.USER_AGENT_ORIGINAL) or \
        attributes.get(SpanAttributes.HTTP_USER_AGENT)


@no_type_check
def _get_url_for_http_request(attributes: Attributes) -> Optional[str]:
    url = ""
    if attributes:
        # Url
        if url_attributes.URL_FULL in attributes:
            return attributes[url_attributes.URL_FULL]
        if SpanAttributes.HTTP_URL in attributes:
            return attributes[SpanAttributes.HTTP_URL]
        # Scheme
        scheme = _get_http_scheme(attributes)
        # Target
        http_target = ""
        if url_attributes.URL_PATH in attributes:
            http_target = attributes.get(url_attributes.URL_PATH, "")
            if http_target and url_attributes.URL_QUERY in attributes:
                http_target = "{}?{}".format(
                    http_target,
                    attributes.get(url_attributes.URL_QUERY, "")
                )
        elif SpanAttributes.HTTP_TARGET in attributes:
            http_target = attributes.get(SpanAttributes.HTTP_TARGET)
        if scheme and http_target:
            # Host
            http_host = ""
            if server_attributes.SERVER_ADDRESS in attributes:
                http_host = attributes.get(server_attributes.SERVER_ADDRESS, "")
                if http_host and server_attributes.SERVER_PORT in attributes:
                    http_host = "{}:{}".format(
                        http_host,
                        attributes.get(server_attributes.SERVER_PORT, "")
                    )
            elif SpanAttributes.HTTP_HOST in attributes:
                http_host = attributes.get(SpanAttributes.HTTP_HOST, "")
            if http_host:
                url = "{}://{}{}".format(
                    scheme,
                    http_host,
                    http_target,
                )
            elif SpanAttributes.HTTP_SERVER_NAME in attributes:
                server_name = attributes[SpanAttributes.HTTP_SERVER_NAME]
                host_port = attributes.get(SpanAttributes.NET_HOST_PORT, "")
                url = "{}://{}:{}{}".format(
                    scheme,
                    server_name,
                    host_port,
                    http_target,
                )
            elif SpanAttributes.NET_HOST_NAME in attributes:
                host_name = attributes[SpanAttributes.NET_HOST_NAME]
                host_port = attributes.get(SpanAttributes.NET_HOST_PORT, "")
                url = "{}://{}:{}{}".format(
                    scheme,
                    host_name,
                    host_port,
                    http_target,
                )
    return url
