# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from ._version import VERSION
from ._queue_client import QueueClient
from ._queue_service_client import QueueServiceClient
from ._shared_access_signature import generate_account_sas, generate_queue_sas
from ._shared.policies import ExponentialRetry, LinearRetry
from ._shared.models import (
    LocationMode,
    ResourceTypes,
    AccountSasPermissions,
    UserDelegationKey,
    StorageErrorCode,
    Services,
)
from ._message_encoding import (
    TextBase64EncodePolicy,
    TextBase64DecodePolicy,
    BinaryBase64EncodePolicy,
    BinaryBase64DecodePolicy,
)
from ._models import (
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
    "AccessPolicy",
    "AccountSasPermissions",
    "BinaryBase64DecodePolicy",
    "BinaryBase64EncodePolicy",
    "CorsRule",
    "ExponentialRetry",
    "generate_account_sas",
    "generate_queue_sas",
    "Metrics",
    "LinearRetry",
    "LocationMode",
    "ResourceTypes",
    "StorageErrorCode",
    "QueueClient",
    "QueueAnalyticsLogging",
    "QueueMessage",
    "QueueProperties",
    "QueueSasPermissions",
    "QueueServiceClient",
    "RetentionPolicy",
    "Services",
    "TextBase64EncodePolicy",
    "TextBase64DecodePolicy",
    "UserDelegationKey",
]
