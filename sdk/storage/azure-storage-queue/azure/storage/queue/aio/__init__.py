# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from azure.storage.queue.version import VERSION
from .queue_client_async import QueueClient
from .queue_service_client_async import QueueServiceClient
from .models import MessagesPaged, QueuePropertiesPaged
from ..models import (
    QueueAnalyticsLogging, Metrics, RetentionPolicy, CorsRule, AccessPolicy,
    QueueMessage, QueueSasPermissions, QueueProperties)

__version__ = VERSION

__all__ = [
    'QueueClient',
    'QueueServiceClient',
    'QueueAnalyticsLogging',
    'Metrics',
    'RetentionPolicy',
    'CorsRule',
    'AccessPolicy',
    'QueueMessage',
    'MessagesPaged',
    'QueueSasPermissions',
    'QueueProperties',
    'QueuePropertiesPaged'
]
