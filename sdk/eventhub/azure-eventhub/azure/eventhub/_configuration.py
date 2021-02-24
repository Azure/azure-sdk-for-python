# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from typing import Optional, Any

try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

from uamqp.constants import TransportType, DEFAULT_AMQPS_PORT, DEFAULT_AMQP_WSS_PORT

from ._common import DictMixin


class Configuration(object):  # pylint:disable=too-many-instance-attributes
    def __init__(self, **kwargs):
        self.user_agent = kwargs.get("user_agent")  # type: Optional[str]
        self.retry_total = kwargs.get("retry_total", 3)  # type: int
        self.max_retries = self.retry_total  # type: int
        self.backoff_factor = kwargs.get("retry_backoff_factor", 0.8)  # type: float
        self.backoff_max = kwargs.get("retry_backoff_max", 120)  # type: int
        self.network_tracing = kwargs.get("network_tracing", False)  # type: bool
        self.http_proxy = kwargs.get("http_proxy")  # type: Optional[Dict[str, Any]]
        self.transport_type = (
            TransportType.AmqpOverWebsocket
            if self.http_proxy
            else kwargs.get("transport_type", TransportType.Amqp)
        )
        self.auth_timeout = kwargs.get("auth_timeout", 60)  # type: int
        self.prefetch = kwargs.get("prefetch", 300)  # type: int
        self.max_batch_size = kwargs.get("max_batch_size", self.prefetch)  # type: int
        self.receive_timeout = kwargs.get("receive_timeout", 0)  # type: int
        self.send_timeout = kwargs.get("send_timeout", 60)  # type: int
        self.custom_endpoint_address = kwargs.get("custom_endpoint_address")  # type: Optional[str]
        self.connection_verify = kwargs.get("connection_verify")  # type: Optional[str]
        self.connection_port = DEFAULT_AMQPS_PORT
        self.custom_endpoint_hostname = None
        self.enable_idempotent_partitions = kwargs.get("enable_idempotent_partitions", False)  # type: bool

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


class PartitionPublishingConfiguration(DictMixin):
    def __init__(self, **kwargs):
        self._owner_level = kwargs.get("owner_level")  # type: Optional[int]
        self._producer_group_id = kwargs.get("producer_group_id")  # type: Optional[int]
        self._starting_sequence_number = kwargs.get("starting_sequence_number")  # type: Optional[int]

    @property
    def owner_level(self):
        # type: () -> Optional[int]
        return self._owner_level

    @owner_level.setter
    def owner_level(self, value):
        # type: (int) -> None
        self._owner_level = value

    @property
    def producer_group_id(self):
        # type: () -> Optional[int]
        return self._producer_group_id

    @producer_group_id.setter
    def producer_group_id(self, value):
        # type: (int) -> None
        self._producer_group_id = value

    @property
    def starting_sequence_number(self):
        # type: () -> Optional[int]
        return self._starting_sequence_number

    @starting_sequence_number.setter
    def starting_sequence_number(self, value):
        # type: (int) -> None
        self._starting_sequence_number = value
