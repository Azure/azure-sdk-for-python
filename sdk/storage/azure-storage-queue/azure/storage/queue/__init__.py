# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from .version import VERSION
from .queue_client import QueueClient
from .queue_service_client import QueueServiceClient
from ._shared.policies import ExponentialRetry, LinearRetry, NoRetry
from ._shared.models import(
    LocationMode,
    ResourceTypes,
    AccountPermissions,
    StorageErrorCode
)
from ._message_encoding import (
    TextBase64EncodePolicy,
    TextBase64DecodePolicy,
    BinaryBase64EncodePolicy,
    BinaryBase64DecodePolicy,
    TextXMLEncodePolicy,
    TextXMLDecodePolicy,
    NoEncodePolicy,
    NoDecodePolicy
)
from .models import (
    QueueMessage,
    QueueProperties,
    QueuePropertiesPaged,
    QueuePermissions,
    AccessPolicy,
    Logging,
    Metrics,
    CorsRule,
    RetentionPolicy,
    MessagesPaged,
)

__version__ = VERSION

__all__ = [
    'QueueClient',
    'QueueServiceClient',
    'ExponentialRetry',
    'LinearRetry',
    'NoRetry',
    'LocationMode',
    'ResourceTypes',
    'AccountPermissions',
    'StorageErrorCode',
    'QueueMessage',
    'QueueProperties',
    'QueuePropertiesPaged',
    'QueuePermissions',
    'AccessPolicy',
    'TextBase64EncodePolicy',
    'TextBase64DecodePolicy',
    'BinaryBase64EncodePolicy',
    'BinaryBase64DecodePolicy',
    'TextXMLEncodePolicy',
    'TextXMLDecodePolicy',
    'NoEncodePolicy',
    'NoDecodePolicy',
    'Logging',
    'Metrics',
    'CorsRule',
    'RetentionPolicy',
    'MessagesPaged',
]
