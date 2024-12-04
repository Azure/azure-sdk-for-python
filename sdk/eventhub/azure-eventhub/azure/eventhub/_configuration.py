# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import warnings
from typing import Optional, Dict, Any, Union, TYPE_CHECKING
from urllib.parse import urlparse

from azure.core.pipeline.policies import RetryMode
from ._constants import TransportType, DEFAULT_AMQPS_PORT, DEFAULT_AMQP_WSS_PORT

if TYPE_CHECKING:
    from ssl import SSLContext
    from ._transport._base import AmqpTransport
    from .aio._transport._base_async import AmqpTransportAsync


class Configuration:  # pylint:disable=too-many-instance-attributes
    def __init__(
        self,  # pylint:disable=unused-argument
        *,
        hostname: str,
        amqp_transport: Union["AmqpTransport", "AmqpTransportAsync"],
        socket_timeout: Optional[float] = None,
        user_agent: Optional[str] = None,
        retry_total: int = 3,
        retry_mode: Union[str, RetryMode] = RetryMode.Exponential,
        retry_backoff_factor: float = 0.8,
        retry_backoff_max: int = 120,
        network_tracing: bool = False,
        http_proxy: Optional[Dict[str, Any]] = None,
        transport_type: Optional[TransportType] = None,
        auth_timeout: int = 60,
        prefetch: int = 300,
        max_batch_size: int = 300,
        receive_timeout: int = 0,
        send_timeout: int = 60,
        custom_endpoint_address: Optional[str] = None,
        connection_verify: Optional[str] = None,
        ssl_context: Optional["SSLContext"] = None,
        use_tls: bool = True,
        **kwargs: Any
    ):
        self.user_agent = user_agent
        self.retry_total = retry_total
        self.max_retries = self.retry_total
        self.retry_mode = retry_mode
        self.backoff_factor = retry_backoff_factor
        self.backoff_max = retry_backoff_max
        self.network_tracing = network_tracing
        self.http_proxy = http_proxy
        self.transport_type = TransportType.AmqpOverWebsocket if self.http_proxy else transport_type
        # if transport_type is not provided, it is None, we will default to Amqp
        self.transport_type = self.transport_type or TransportType.Amqp
        self.auth_timeout = auth_timeout
        self.prefetch = prefetch
        self.max_batch_size = max_batch_size
        self.receive_timeout = receive_timeout
        self.send_timeout = send_timeout
        self.custom_endpoint_address = custom_endpoint_address
        self.connection_verify = connection_verify
        self.ssl_context = ssl_context
        if self.ssl_context and self.connection_verify:
            warnings.warn("ssl_context is specified, connection_verify will be ignored.")
        self.custom_endpoint_hostname = None
        self.hostname = hostname
        self.use_tls = use_tls

        if self.http_proxy or self.transport_type.value == TransportType.AmqpOverWebsocket.value:
            self.transport_type = TransportType.AmqpOverWebsocket
            self.connection_port = DEFAULT_AMQP_WSS_PORT
            self.socket_timeout = socket_timeout or 1
            if amqp_transport.KIND == "pyamqp":
                self.hostname += "/$servicebus/websocket"
        else:
            self.socket_timeout = socket_timeout or 0.2
            self.connection_port = DEFAULT_AMQPS_PORT

        # custom end point
        if self.custom_endpoint_address:
            # if the custom_endpoint_address doesn't include the schema,
            # we prepend a default one to make urlparse work
            if self.custom_endpoint_address.find("//") == -1:
                self.custom_endpoint_address = "sb://" + self.custom_endpoint_address
            endpoint = urlparse(self.custom_endpoint_address)
            # this line is to maintain backward compatibility for custom endpoint
            # if the transport_type is not provided, we will default to AmqpOverWebsocket
            self.transport_type = transport_type or TransportType.AmqpOverWebsocket
            self.custom_endpoint_hostname = endpoint.hostname
            if amqp_transport.KIND == "pyamqp":
                # if transport is amqp, we will not append this path to the final endpoint
                self.custom_endpoint_address += "/$servicebus/websocket"
            # in case proxy and custom endpoint are both provided, we default port to 443 if it's not provided
            self.connection_port = endpoint.port or DEFAULT_AMQP_WSS_PORT
