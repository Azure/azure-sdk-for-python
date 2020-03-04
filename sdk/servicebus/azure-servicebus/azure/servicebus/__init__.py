# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from ._version import VERSION
__version__ = VERSION

from uamqp import constants
from azure.servicebus._sender_client import ServiceBusSenderClient
from azure.servicebus._receiver_client import ServiceBusReceiverClient
from azure.servicebus._client_base import ServiceBusSharedKeyCredential
from azure.servicebus.common.message import Message, BatchMessage, PeekMessage, DeferredMessage
from azure.servicebus.servicebus_client import ServiceBusClient, QueueClient, TopicClient, SubscriptionClient
from azure.servicebus.common.constants import ReceiveSettleMode, NEXT_AVAILABLE
from azure.servicebus.common.utils import AutoLockRenew
from azure.servicebus.common.errors import (
    ServiceBusError,
    ServiceBusResourceNotFound,
    ServiceBusConnectionError,
    ServiceBusAuthorizationError,
    InvalidHandlerState,
    NoActiveSession,
    MessageAlreadySettled,
    MessageSettleFailed,
    MessageSendFailed,
    MessageLockExpired,
    SessionLockExpired,
    AutoLockRenewFailed,
    AutoLockRenewTimeout)

TransportType = constants.TransportType

__all__ = [
    'Message',
    'BatchMessage',
    'PeekMessage',
    'AutoLockRenew',
    'DeferredMessage',
    'ServiceBusClient',
    'QueueClient',
    'TopicClient',
    'SubscriptionClient',
    'ReceiveSettleMode',
    'NEXT_AVAILABLE',
    'ServiceBusError',
    'ServiceBusResourceNotFound',
    'ServiceBusConnectionError',
    'ServiceBusAuthorizationError',
    'InvalidHandlerState',
    'NoActiveSession',
    'MessageAlreadySettled',
    'MessageSettleFailed',
    'MessageSendFailed',
    'MessageLockExpired',
    'SessionLockExpired',
    'AutoLockRenewFailed',
    'AutoLockRenewTimeout',
    'ServiceBusReceiverClient',
    'ServiceBusSenderClient',
    'ServiceBusSharedKeyCredential',
    "TransportType",
]
