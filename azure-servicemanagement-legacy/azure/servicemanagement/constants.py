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
__version__ = '0.20.6'

_USER_AGENT_STRING = 'pyazure/' + __version__

#-----------------------------------------------------------------------------
# Constants for Azure app environment settings.
AZURE_MANAGEMENT_CERTFILE = 'AZURE_MANAGEMENT_CERTFILE'
AZURE_MANAGEMENT_SUBSCRIPTIONID = 'AZURE_MANAGEMENT_SUBSCRIPTIONID'

# Live ServiceClient URLs
MANAGEMENT_HOST = 'management.core.windows.net'

# Default timeout for http requests (in secs)
DEFAULT_HTTP_TIMEOUT = 65

# x-ms-version for service management.
X_MS_VERSION = '2014-10-01'
