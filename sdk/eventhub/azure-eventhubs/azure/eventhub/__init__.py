# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

__path__ = __import__('pkgutil').extend_path(__path__, __name__)  # type: ignore
__version__ = "5.0.0b6"
from uamqp import constants  # type: ignore
from ._common import EventData, EventDataBatch, EventPosition
from ._producer_client import EventHubProducerClient
from ._consumer_client import EventHubConsumerClient
from ._client_base import EventHubSharedKeyCredential
from ._eventprocessor.partition_manager import PartitionManager
from ._eventprocessor.common import CloseReason, OwnershipLostError
from ._eventprocessor.partition_context import PartitionContext
from .exceptions import (
    EventHubError,
    EventDataError,
    ConnectError,
    AuthenticationError,
    EventDataSendError,
    ConnectionLostError
)

TransportType = constants.TransportType

__all__ = [
    "EventData",
    "EventDataBatch",
    "EventHubError",
    "ConnectError",
    "ConnectionLostError",
    "EventDataError",
    "EventDataSendError",
    "AuthenticationError",
    "EventPosition",
    "EventHubProducerClient",
    "EventHubConsumerClient",
    "TransportType",
    "EventHubSharedKeyCredential",
    "PartitionManager",
    "CloseReason",
    "OwnershipLostError",
    "PartitionContext",
]
