# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from .version import VERSION
from .file_client import FileClient
from .directory_client import DirectoryClient
from .share_client import ShareClient
from .file_service_client import FileServiceClient
from ._shared.policies import ExponentialRetry, LinearRetry
from ._shared.models import(
    LocationMode,
    ResourceTypes,
    AccountSasPermissions,
    StorageErrorCode)
from .models import (
    ShareProperties,
    SharePropertiesPaged,
    DirectoryProperties,
    DirectoryPropertiesPaged,
    Handle,
    HandlesPaged,
    FileProperties,
    Metrics,
    RetentionPolicy,
    CorsRule,
    AccessPolicy,
    FileSasPermissions,
    ShareSasPermissions,
    ContentSettings,
    NTFSAttributes)
from ._generated.models import (
    HandleItem
)

__version__ = VERSION


__all__ = [
    'FileClient',
    'DirectoryClient',
    'ShareClient',
    'FileServiceClient',
    'ExponentialRetry',
    'LinearRetry',
    'LocationMode',
    'ResourceTypes',
    'AccountSasPermissions',
    'StorageErrorCode',
    'Metrics',
    'RetentionPolicy',
    'CorsRule',
    'AccessPolicy',
    'FileSasPermissions',
    'ShareSasPermissions',
    'ShareProperties',
    'SharePropertiesPaged',
    'DirectoryProperties',
    'DirectoryPropertiesPaged',
    'FileProperties',
    'ContentSettings',
    'Handle',
    'HandlesPaged',
    'NTFSAttributes',
    'HandleItem'
]
