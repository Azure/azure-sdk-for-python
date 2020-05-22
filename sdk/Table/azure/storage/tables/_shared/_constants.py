# -------------------------------------------------------------------------
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
# --------------------------------------------------------------------------
import platform

__author__ = 'Microsoft Corp. <ptvshelp@microsoft.com>'
__version__ = '1.0.6'

# x-ms-version for storage service.
X_MS_VERSION = '2017-04-17'

# UserAgent string sample: 'Azure-CosmosDB/0.32.0 (Python CPython 3.4.2; Windows 8)'
USER_AGENT_STRING = 'Azure-CosmosDB/{} (Python {} {}; {} {})'.format(__version__, platform.python_implementation(),
                                                                    platform.python_version(), platform.system(),
                                                                    platform.release())
DEV_TABLE_HOST = '127.0.0.1:10002'