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
    Logging, Metrics, RetentionPolicy, CorsRule, AccessPolicy,
    QueueMessage, QueuePermissions, QueueProperties)

__version__ = VERSION

__all__ = [
    'QueueClient',
    'QueueServiceClient',
    'Logging',
    'Metrics',
    'RetentionPolicy',
    'CorsRule',
    'AccessPolicy',
    'QueueMessage',
    'MessagesPaged',
    'QueuePermissions',
    'QueueProperties',
    'QueuePropertiesPaged'
]
