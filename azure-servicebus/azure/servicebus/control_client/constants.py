# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from azure.servicebus import __version__


_USER_AGENT_STRING = 'azure-servicebus/{} Azure-SDK-For-Python'.format(__version__)

# default rule name for subscription
DEFAULT_RULE_NAME = '$Default'

# ----------------------------------------------------------------------------
# Constants for Azure app environment settings.
AZURE_SERVICEBUS_NAMESPACE = 'AZURE_SERVICEBUS_NAMESPACE'
AZURE_SERVICEBUS_ACCESS_KEY = 'AZURE_SERVICEBUS_ACCESS_KEY'
AZURE_SERVICEBUS_ISSUER = 'AZURE_SERVICEBUS_ISSUER'

# Live ServiceClient URLs
SERVICE_BUS_HOST_BASE = '.servicebus.windows.net'

# Default timeout for HTTP requests (in secs)
DEFAULT_HTTP_TIMEOUT = 65
