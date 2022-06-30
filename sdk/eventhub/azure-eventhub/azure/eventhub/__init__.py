# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from ._common import EventData, EventDataBatch
from ._version import VERSION

__version__ = VERSION

from ._constants import TransportType
from ._producer_client import EventHubProducerClient
from ._consumer_client import EventHubConsumerClient
# TODO in pyamqp: from ._client_base import EventHubSharedKeyCredential
from ._transport._uamqp_transport import EventHubSharedKeyCredential
from ._eventprocessor.checkpoint_store import CheckpointStore
from ._eventprocessor.common import CloseReason, LoadBalancingStrategy
from ._eventprocessor.partition_context import PartitionContext
from ._connection_string_parser import (
    parse_connection_string,
    EventHubConnectionStringProperties
)

__all__ = [
    "EventData",
    "EventDataBatch",
    "EventHubProducerClient",
    "EventHubConsumerClient",
    "TransportType",
    "EventHubSharedKeyCredential",
    "CheckpointStore",
    "CloseReason",
    "LoadBalancingStrategy",
    "PartitionContext",
    "parse_connection_string",
    "EventHubConnectionStringProperties",
]
