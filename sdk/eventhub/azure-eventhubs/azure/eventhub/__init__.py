# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

__version__ = "2.0.0b1"

from azure.eventhub.common import EventData, EventPosition
from azure.eventhub.error import EventHubError, EventDataError, ConnectError, \
    AuthenticationError, EventDataSendError, ConnectionLostError
from azure.eventhub.client import EventHubClient
from azure.eventhub.sender import EventHubProducer
from azure.eventhub.receiver import EventHubConsumer
from .constants import MessageSendResult
from .constants import TransportType
from .common import EventHubSharedKeyCredential, EventHubSASTokenCredential

__all__ = [
    "__version__",
    "EventData",
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
    "MessageSendResult",
    "TransportType",
    "EventHubSharedKeyCredential",
    "EventHubSASTokenCredential",
]
