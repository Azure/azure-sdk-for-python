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
from .constants import (
    __author__,
    __version__,
    AZURE_MANAGEMENT_CERTFILE,
    AZURE_MANAGEMENT_SUBSCRIPTIONID,
    MANAGEMENT_HOST,
    X_MS_VERSION,
)

from .models import *

from .publishsettings import get_certificate_from_publish_settings
from .servicemanagementclient import parse_response_for_async_op

from .servicemanagementservice import ServiceManagementService
from .servicebusmanagementservice import ServiceBusManagementService
from .websitemanagementservice import WebsiteManagementService
from .sqldatabasemanagementservice import SqlDatabaseManagementService
from .schedulermanagementservice import SchedulerManagementService
