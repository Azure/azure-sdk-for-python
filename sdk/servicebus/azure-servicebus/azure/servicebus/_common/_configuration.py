# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from typing import Optional, Dict, Any
from urllib.parse import urlparse

from uamqp.constants import TransportType, DEFAULT_AMQP_WSS_PORT, DEFAULT_AMQPS_PORT
from azure.core.pipeline.policies import RetryMode


class Configuration(object):  # pylint:disable=too-many-instance-attributes
    def __init__(self, **kwargs):
        self.user_agent = kwargs.get("user_agent")  # type: Optional[str]
        self.retry_total = kwargs.get("retry_total", 3)  # type: int
        self.retry_mode = RetryMode(kwargs.get("retry_mode", 'exponential'))
        self.retry_backoff_factor = kwargs.get(
            "retry_backoff_factor", 0.8
        )  # type: float
        self.retry_backoff_max = kwargs.get("retry_backoff_max", 120)  # type: int
        self.logging_enable = kwargs.get("logging_enable", False)  # type: bool
        self.http_proxy = kwargs.get("http_proxy")  # type: Optional[Dict[str, Any]]

        self.custom_endpoint_address = kwargs.get("custom_endpoint_address")  # type: Optional[str]
        self.connection_verify = kwargs.get("connection_verify")  # type: Optional[str]
        self.connection_port = DEFAULT_AMQPS_PORT
        self.custom_endpoint_hostname = None

        self.transport_type = (
            TransportType.AmqpOverWebsocket
            if self.http_proxy or self.custom_endpoint_address
            else kwargs.get("transport_type", TransportType.Amqp)
        )
        # The following configs are not public, for internal usage only
        self.auth_timeout = kwargs.get("auth_timeout", 60)  # type: int
        self.encoding = kwargs.get("encoding", "UTF-8")
        self.auto_reconnect = kwargs.get("auto_reconnect", True)
        self.keep_alive = kwargs.get("keep_alive", 30)
        self.timeout = kwargs.get("timeout", 60)  # type: float

        if self.http_proxy or self.transport_type == TransportType.AmqpOverWebsocket:
            self.transport_type = TransportType.AmqpOverWebsocket
            self.connection_port = DEFAULT_AMQP_WSS_PORT

        # custom end point
        if self.custom_endpoint_address:
            # if the custom_endpoint_address doesn't include the schema,
            # we prepend a default one to make urlparse work
            if self.custom_endpoint_address.find("//") == -1:
                self.custom_endpoint_address = "sb://" + self.custom_endpoint_address
            endpoint = urlparse(self.custom_endpoint_address)
            self.transport_type = TransportType.AmqpOverWebsocket
            self.custom_endpoint_hostname = endpoint.hostname
            # in case proxy and custom endpoint are both provided, we default port to 443 if it's not provided
            self.connection_port = endpoint.port or DEFAULT_AMQP_WSS_PORT
