#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import warnings

from azure.servicebus.control_client.constants import (
    _USER_AGENT_STRING,
    DEFAULT_RULE_NAME,
    AZURE_SERVICEBUS_NAMESPACE,
    AZURE_SERVICEBUS_ACCESS_KEY,
    AZURE_SERVICEBUS_ISSUER,
    SERVICE_BUS_HOST_BASE,
    DEFAULT_HTTP_TIMEOUT)


__all__ = [
    '_USER_AGENT_STRING',
    'DEFAULT_RULE_NAME',
    'AZURE_SERVICEBUS_NAMESPACE',
    'AZURE_SERVICEBUS_ACCESS_KEY',
    'AZURE_SERVICEBUS_ISSUER',
    'SERVICE_BUS_HOST_BASE',
    'DEFAULT_HTTP_TIMEOUT']


warnings.warn("The module 'azure.servicebus.constants' is deprecated and will be removed in v1.0. "
              "Please import from 'azure.servicebus.control_client.constants' instead.",
              DeprecationWarning)
