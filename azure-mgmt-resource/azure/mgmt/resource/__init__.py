# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from .features import FeatureClient
from .locks import ManagementLockClient
from .policy import PolicyClient
from .resources import ResourceManagementClient
from .subscriptions import SubscriptionClient
from .links import ManagementLinkClient
from .managedapplications import ManagedApplicationClient

from .version import VERSION

__version__ = VERSION
