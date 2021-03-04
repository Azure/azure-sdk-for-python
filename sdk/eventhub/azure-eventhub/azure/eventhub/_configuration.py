# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from typing import Optional, Any, Dict

try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

from uamqp.constants import TransportType, DEFAULT_AMQPS_PORT, DEFAULT_AMQP_WSS_PORT

from ._common import DictMixin
from ._utils import validate_producer_client_partition_config



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
    """
    The set of configurations that can be specified for an `EventHubProducerClient`
    to influence its behavior when publishing directly to an Event Hub partition.

    :ivar int producer_group_id: The identifier of the producer group that this producer is associated with when
     publishing to the associated partition.
    :ivar int owner_level: The owner level indicates that publishing is intended to be performed exclusively for
     events in the requested partition in the context of the associated producer group.
    :ivar int starting_sequence_number: The starting number that should be used for the automatic sequencing of
     events for the associated partition, when published by this producer.

    :keyword int producer_group_id: The identifier of the producer group that this producer is associated with when
     publishing to the associated partition. The producer group is only recognized and relevant when certain features
     of the producer are enabled. For example, it is used by idempotent publishing.
     The producer group id should be in the range from 0 to max signed long (2^63 - 1) as required by the service.
    :keyword int owner_level: The owner level indicates that publishing is intended to be performed exclusively for
     events in the requested partition in the context of the associated producer group. To do so, publishing will
     attempt to assert ownership over the partition; in the case where more than one publisher in the producer
     group attempts to assert ownership for the same partition, the one having a larger owner_level value will "win".
     The owner level is only recognized and relevant when certain features of the producer are enabled. For example,
     it is used by idempotent publishing.
     The owner level should be in the range from 0 to max signed short (2^16 - 1) as required by the service.
    :keyword int starting_sequence_number: The starting number that should be used for the automatic sequencing of
     events for the associated partition, when published by this producer. The starting sequence number is only
     recognized and relevant when certain features of the producer are enabled. For example, it is used by idempotent
     publishing.
     The starting sequence number should be in the range from 0 to max signed integer (2^31 - 1) as
     required by the service.

    """
    def __init__(self, **kwargs):
        validate_producer_client_partition_config(kwargs)
        self.owner_level = kwargs.get("owner_level")  # type: Optional[int]
        self.producer_group_id = kwargs.get("producer_group_id")  # type: Optional[int]
        self.starting_sequence_number = kwargs.get("starting_sequence_number")  # type: Optional[int]
