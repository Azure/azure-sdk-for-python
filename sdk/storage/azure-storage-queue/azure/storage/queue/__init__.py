# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from .version import VERSION
from .queue_client import QueueClient
from .queue_service_client import QueueServiceClient
from ._shared.policies import ExponentialRetry, LinearRetry
from ._shared.models import(
    LocationMode,
    ResourceTypes,
    AccountSasPermissions,
    StorageErrorCode
)
from ._message_encoding import (
    TextBase64EncodePolicy,
    TextBase64DecodePolicy,
    BinaryBase64EncodePolicy,
    BinaryBase64DecodePolicy,
    TextXMLEncodePolicy,
    TextXMLDecodePolicy
)
from .models import (
    QueueMessage,
    QueueProperties,
    QueueSasPermissions,
    AccessPolicy,
    QueueAnalyticsLogging,
    Metrics,
    CorsRule,
    RetentionPolicy,
)

__version__ = VERSION

__all__ = [
    'QueueClient',
    'QueueServiceClient',
    'ExponentialRetry',
    'LinearRetry',
    'LocationMode',
    'ResourceTypes',
    'AccountSasPermissions',
    'StorageErrorCode',
    'QueueMessage',
    'QueueProperties',
    'QueueSasPermissions',
    'AccessPolicy',
    'TextBase64EncodePolicy',
    'TextBase64DecodePolicy',
    'BinaryBase64EncodePolicy',
    'BinaryBase64DecodePolicy',
    'TextXMLEncodePolicy',
    'TextXMLDecodePolicy',
    'QueueAnalyticsLogging',
    'Metrics',
    'CorsRule',
    'RetentionPolicy',
]
