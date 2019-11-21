# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

__path__ = __import__('pkgutil').extend_path(__path__, __name__)  # type: ignore

from uamqp import constants  # type: ignore

from ._version import VERSION
__version__ = VERSION

from ._common import EventData, EventDataBatch, EventPosition
from ._producer_client import EventHubProducerClient
from ._consumer_client import EventHubConsumerClient
from ._common import EventHubSharedKeyCredential, EventHubSASTokenCredential
from ._eventprocessor.checkpoint_store import CheckpointStore
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
    "EventHubSASTokenCredential",
    "CheckpointStore",
    "CloseReason",
    "OwnershipLostError",
    "PartitionContext",
]
