#-------------------------------------------------------------------------
# Copyright (c) Microsoft.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#--------------------------------------------------------------------------

__author__ = 'Microsoft Corp. <ptvshelp@microsoft.com>'
__version__ = '0.21.1'

_USER_AGENT_STRING = 'pyazure/' + __version__

# default rule name for subscription
DEFAULT_RULE_NAME = '$Default'

#-----------------------------------------------------------------------------
# Constants for Azure app environment settings.
AZURE_SERVICEBUS_NAMESPACE = 'AZURE_SERVICEBUS_NAMESPACE'
AZURE_SERVICEBUS_ACCESS_KEY = 'AZURE_SERVICEBUS_ACCESS_KEY'
AZURE_SERVICEBUS_ISSUER = 'AZURE_SERVICEBUS_ISSUER'

# Live ServiceClient URLs
SERVICE_BUS_HOST_BASE = '.servicebus.windows.net'

# Default timeout for http requests (in secs)
DEFAULT_HTTP_TIMEOUT = 65
