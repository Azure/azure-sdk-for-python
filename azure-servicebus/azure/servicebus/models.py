#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import warnings

from azure.servicebus.control_client.models import (
    AzureServiceBusPeekLockError,
    AzureServiceBusResourceNotFound,
    Queue,
    Topic,
    Subscription,
    Rule,
    EventHub,
    AuthorizationRule,
    Message)


__all__ = [
    'AzureServiceBusPeekLockError',
    'AzureServiceBusResourceNotFound',
    'Queue',
    'Topic',
    'Subscription',
    'Rule',
    'EventHub',
    'AuthorizationRule',
    'Message']

warnings.warn("The module 'azure.servicebus.models' is deprecated and will be removed in v1.0. "
              "Please import from 'azure.servicebus.control_client.models' instead.",
              DeprecationWarning)
