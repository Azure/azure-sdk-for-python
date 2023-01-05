# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from typing import Optional, Dict, Any
from urllib.parse import urlparse

from azure.core.pipeline.policies import RetryMode
from ._constants import TransportType, DEFAULT_AMQPS_PORT, DEFAULT_AMQP_WSS_PORT



class Configuration(object):  # pylint:disable=too-many-instance-attributes
    def __init__(self, **kwargs):
        self.user_agent: Optional[str] = kwargs.get("user_agent")
        self.retry_total: int = kwargs.get("retry_total", 3)
        self.max_retries: int = self.retry_total
        self.retry_mode = RetryMode(kwargs.get("retry_mode", "exponential"))
        self.backoff_factor: int = kwargs.get("retry_backoff_factor", 0.8)
        self.backoff_max: int = kwargs.get("retry_backoff_max", 120)
        self.network_tracing: bool = kwargs.get("network_tracing", False)
        self.http_proxy: Optional[Dict[str, Any]] = kwargs.get("http_proxy")
        self.transport_type = (
            TransportType.AmqpOverWebsocket
            if self.http_proxy
            else kwargs.get("transport_type", TransportType.Amqp)
        )
        self.auth_timeout: int = kwargs.get("auth_timeout", 60)
        self.prefetch: int = kwargs.get("prefetch", 300)
        self.max_batch_size: int = kwargs.get("max_batch_size", self.prefetch)
        self.receive_timeout: int = kwargs.get("receive_timeout", 0)
        self.send_timeout: int = kwargs.get("send_timeout", 60)
        self.custom_endpoint_address: Optional[str] = kwargs.get("custom_endpoint_address")
        self.connection_verify: Optional[str] = kwargs.get("connection_verify")
        self.connection_port = DEFAULT_AMQPS_PORT
        self.custom_endpoint_hostname = None
        self.hostname = kwargs.pop("hostname")
        uamqp_transport = kwargs.pop("uamqp_transport")

        if self.http_proxy or self.transport_type.value == TransportType.AmqpOverWebsocket.value:
            self.transport_type = TransportType.AmqpOverWebsocket
            self.connection_port = DEFAULT_AMQP_WSS_PORT
            if not uamqp_transport:
                self.hostname += "/$servicebus/websocket"

        # custom end point
        if self.custom_endpoint_address:
            # if the custom_endpoint_address doesn't include the schema,
            # we prepend a default one to make urlparse work
            if self.custom_endpoint_address.find("//") == -1:
                self.custom_endpoint_address = "sb://" + self.custom_endpoint_address
            endpoint = urlparse(self.custom_endpoint_address)
            self.transport_type = TransportType.AmqpOverWebsocket
            self.custom_endpoint_hostname = endpoint.hostname
            if not uamqp_transport:
                self.custom_endpoint_address += "/$servicebus/websocket"
            # in case proxy and custom endpoint are both provided, we default port to 443 if it's not provided
            self.connection_port = endpoint.port or DEFAULT_AMQP_WSS_PORT
