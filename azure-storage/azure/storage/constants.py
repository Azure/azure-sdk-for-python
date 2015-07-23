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
__version__ = '0.20.0'

# x-ms-version for storage service.
X_MS_VERSION = '2014-02-14'

_USER_AGENT_STRING = 'pyazure/' + __version__

# Live ServiceClient URLs
BLOB_SERVICE_HOST_BASE = '.blob.core.windows.net'
QUEUE_SERVICE_HOST_BASE = '.queue.core.windows.net'
TABLE_SERVICE_HOST_BASE = '.table.core.windows.net'
FILE_SERVICE_HOST_BASE = '.file.core.windows.net'

# Development ServiceClient URLs
DEV_BLOB_HOST = '127.0.0.1:10000'
DEV_QUEUE_HOST = '127.0.0.1:10001'
DEV_TABLE_HOST = '127.0.0.1:10002'
DEV_FILE_HOST = '127.0.0.1:10003'

# Default credentials for Development Storage Service
DEV_ACCOUNT_NAME = 'devstoreaccount1'
DEV_ACCOUNT_KEY = 'Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw=='

# Default timeout for http requests (in secs)
DEFAULT_HTTP_TIMEOUT = 65

#--------------------------------------------------------------------------
# constants for azure app setting environment variables
AZURE_STORAGE_ACCOUNT = 'AZURE_STORAGE_ACCOUNT'
AZURE_STORAGE_ACCESS_KEY = 'AZURE_STORAGE_ACCESS_KEY'
EMULATED = 'EMULATED'
