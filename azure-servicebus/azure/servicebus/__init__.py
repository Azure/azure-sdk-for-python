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
    DEFAULT_RULE_NAME,
    AZURE_SERVICEBUS_NAMESPACE,
    AZURE_SERVICEBUS_ACCESS_KEY,
    AZURE_SERVICEBUS_ISSUER,
    SERVICE_BUS_HOST_BASE,
    DEFAULT_HTTP_TIMEOUT,
)

from .models import (
    AzureServiceBusPeekLockError,
    AzureServiceBusResourceNotFound,
    Queue,
    Topic,
    Subscription,
    Rule,
    EventHub,
    AuthorizationRule,
    Message,
)

from .servicebusservice import ServiceBusService
