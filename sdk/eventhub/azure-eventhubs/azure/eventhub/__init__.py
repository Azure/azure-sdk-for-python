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
from ._consumer import EventHubConsumer
from ._common import EventHubSharedKeyCredential, EventHubSASTokenCredential

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
    "TransportType",
    "EventHubSharedKeyCredential",
    "EventHubSASTokenCredential",
]
