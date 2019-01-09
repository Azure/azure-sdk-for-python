#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

__version__ = '0.50.0'

import warnings

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
from azure.servicebus import control_client


__all__ = [
    'Message',
    'BatchMessage',
    'PeekMessage',
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
    'ServiceBusService']


class ServiceBusService(control_client.ServiceBusService):

    def __init__(self, service_namespace=None, account_key=None, issuer=None,
                 x_ms_version='2011-06-01', host_base=control_client.SERVICE_BUS_HOST_BASE,  # pylint: disable=unused-argument
                 shared_access_key_name=None, shared_access_key_value=None,
                 authentication=None, timeout=control_client.DEFAULT_HTTP_TIMEOUT,
                 request_session=None):
        warnings.warn(
            "The class 'azure.servicebus.ServiceBusService' is deprecated and will be removed in v1.0. "
            "Please import 'azure.servicebus.control_client.ServiceBusService' instead.",
            DeprecationWarning)
        super(ServiceBusService, self).__init__(
            service_namespace=service_namespace,
            account_key=account_key,
            issuer=issuer,
            x_ms_version=x_ms_version,
            host_base=host_base,
            shared_access_key_name=shared_access_key_name,
            shared_access_key_value=shared_access_key_value,
            authentication=authentication,
            timeout=timeout,
            request_session=request_session)
