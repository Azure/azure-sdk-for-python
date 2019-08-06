# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

__version__ = "5.0.0b2"

from azure.eventhub.common import EventData, EventDataBatch, EventPosition
from azure.eventhub.error import EventHubError, EventDataError, ConnectError, \
    AuthenticationError, EventDataSendError, ConnectionLostError
from azure.eventhub.client import EventHubClient
from azure.eventhub.producer import EventHubProducer
from azure.eventhub.consumer import EventHubConsumer
from uamqp import constants
from .common import EventHubSharedKeyCredential, EventHubSASTokenCredential

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
