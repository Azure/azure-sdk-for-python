# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from uamqp import constants

from ._version import VERSION
__version__ = VERSION

from ._servicebus_client import ServiceBusClient
from ._servicebus_sender import ServiceBusSender
from ._servicebus_receiver import ServiceBusReceiver, ServiceBusSession
from ._base_handler import ServiceBusSharedKeyCredential
from ._common.message import Message, BatchMessage, PeekMessage, ReceivedMessage
from ._common.constants import ReceiveSettleMode, NEXT_AVAILABLE
from ._common.utils import AutoLockRenew
from .exceptions import (
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
    AutoLockRenewTimeout,)


TransportType = constants.TransportType

__all__ = [
    'Message',
    'BatchMessage',
    'PeekMessage',
    'ReceivedMessage',
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
    'ServiceBusClient',
    'ServiceBusReceiver',
    'ServiceBusSender',
    'ServiceBusSharedKeyCredential',
    'TransportType',
    'AutoLockRenew',
    'ServiceBusSession'
]
