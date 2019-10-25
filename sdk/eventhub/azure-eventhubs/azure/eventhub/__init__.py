# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

__path__ = __import__('pkgutil').extend_path(__path__, __name__)  # type: ignore
__version__ = "5.0.0b5"
from uamqp import constants  # type: ignore
from ._common import EventData, EventDataBatch, EventPosition
from ._error import EventHubError, EventDataError, ConnectError, \
    AuthenticationError, EventDataSendError, ConnectionLostError
from ._client import EventHubClient
from ._producer import EventHubProducer
from ._producer_client import EventHubProducerClient
from ._consumer import EventHubConsumer
from ._consumer_client import EventHubConsumerClient
from ._common import EventHubSharedKeyCredential, EventHubSASTokenCredential
from ._eventprocessor.partition_manager import PartitionManager
from ._eventprocessor.local_partition_manager import FileBasedPartitionManager
from ._eventprocessor.event_processor import CloseReason

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
    "EventHubClient",
    "EventHubProducer",
    "EventHubConsumer",
    "EventHubProducerClient",
    "EventHubConsumerClient",
    "TransportType",
    "EventHubSharedKeyCredential",
    "EventHubSASTokenCredential",
    "PartitionManager",
    "FileBasedPartitionManager",
    "CloseReason",
]
