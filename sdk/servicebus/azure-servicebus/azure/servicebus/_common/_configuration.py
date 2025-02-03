# # --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from typing import Optional, Dict, Any, Union, TYPE_CHECKING
from urllib.parse import urlparse

from azure.core.pipeline.policies import RetryMode
from .constants import DEFAULT_AMQPS_PORT, DEFAULT_AMQP_WSS_PORT, TransportType

if TYPE_CHECKING:
    from ssl import SSLContext
    from .._transport._base import AmqpTransport
    from ..aio._transport._base_async import AmqpTransportAsync


class Configuration(object):  # pylint:disable=too-many-instance-attributes
    def __init__(self, **kwargs):
        self.user_agent: Optional[str] = kwargs.get("user_agent")
        self.retry_total: int = kwargs.get("retry_total", 3)
        self.retry_mode = RetryMode(kwargs.get("retry_mode", "exponential"))
        self.retry_backoff_factor: float = kwargs.get("retry_backoff_factor", 0.8)
        self.retry_backoff_max: int = kwargs.get("retry_backoff_max", 120)
        self.logging_enable: bool = kwargs.get("logging_enable", False)
        self.http_proxy: Optional[Dict[str, Any]] = kwargs.get("http_proxy")

        self.custom_endpoint_address: Optional[str] = kwargs.get("custom_endpoint_address")
        self.connection_verify: Optional[str] = kwargs.get("connection_verify")
        self.ssl_context: Optional["SSLContext"] = kwargs.get("ssl_context")
        self.connection_port = DEFAULT_AMQPS_PORT
        self.custom_endpoint_hostname = None
        self.hostname = kwargs.pop("hostname")
        amqp_transport: Union["AmqpTransport", "AmqpTransportAsync"] = kwargs.pop("amqp_transport")

        self.transport_type = (
            TransportType.AmqpOverWebsocket if self.http_proxy else kwargs.get("transport_type", TransportType.Amqp)
        )
        # The following configs are not public, for internal usage only
        self.auth_timeout: float = kwargs.get("auth_timeout", 60)
        self.encoding = kwargs.get("encoding", "UTF-8")
        self.auto_reconnect = kwargs.get("auto_reconnect", True)
        self.keep_alive = kwargs.get("keep_alive", 30)
        self.timeout: float = kwargs.get("timeout", 60)
        self.use_tls = kwargs.get("use_tls", True)
        default_socket_timeout = 0.2

        if self.http_proxy or self.transport_type.value == TransportType.AmqpOverWebsocket.value:
            self.transport_type = TransportType.AmqpOverWebsocket
            self.connection_port = DEFAULT_AMQP_WSS_PORT
            default_socket_timeout = 1
            if amqp_transport.KIND == "pyamqp":
                self.hostname += "/$servicebus/websocket"

        self.socket_timeout = kwargs.get("socket_timeout") or default_socket_timeout

        # custom end point
        if self.custom_endpoint_address:
            # if the custom_endpoint_address doesn't include the schema,
            # we prepend a default one to make urlparse work
            if self.custom_endpoint_address.find("//") == -1:
                self.custom_endpoint_address = "sb://" + self.custom_endpoint_address
            endpoint = urlparse(self.custom_endpoint_address)
            self.transport_type = kwargs.get("transport_type") or TransportType.AmqpOverWebsocket
            self.custom_endpoint_hostname = endpoint.hostname
            if amqp_transport.KIND == "pyamqp":
                self.custom_endpoint_address += "/$servicebus/websocket"
            # in case proxy and custom endpoint are both provided, we default port to 443 if it's not provided
            self.connection_port = endpoint.port or DEFAULT_AMQP_WSS_PORT
