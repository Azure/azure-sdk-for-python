# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import warnings

from ._version import VERSION
from ._file_client import ShareFileClient
from ._directory_client import ShareDirectoryClient
from ._share_client import ShareClient
from ._share_service_client import ShareServiceClient
from ._lease import ShareLeaseClient
from ._shared_access_signature import generate_account_sas, generate_share_sas, generate_file_sas
from ._shared.policies import ExponentialRetry, LinearRetry
from ._shared.models import (
    AccountSasPermissions,
    LocationMode,
    ResourceTypes,
    UserDelegationKey,
    StorageErrorCode,
    Services,
)
from ._models import (
    AccessPolicy,
    ContentSettings,
    CorsRule,
    DirectoryProperties,
    FileProperties,
    FileSasPermissions,
    Handle,
    Metrics,
    NfsEncryptionInTransit,
    NTFSAttributes,
    RetentionPolicy,
    ShareNfsSettings,
    ShareProperties,
    ShareSasPermissions,
    ShareSmbSettings,
    SmbMultichannel,
    SmbEncryptionInTransit,
    ShareProtocolSettings,
    ShareProtocols,
)
from ._generated.models import (
    ShareAccessTier,
    ShareRootSquash
)

__version__ = VERSION


__all__ = [
    'AccessPolicy',
    'AccountSasPermissions',
    'ContentSettings',
    'CorsRule',
    'DirectoryProperties',
    'ExponentialRetry',
    'FileProperties',
    'FileSasPermissions',
    'generate_account_sas',
    'generate_file_sas',
    'generate_share_sas',
    'Handle',
    'LinearRetry',
    'LocationMode',
    'Metrics',
    'NfsEncryptionInTransit',
    'NTFSAttributes',
    'ResourceTypes',
    'RetentionPolicy',
    'Services',
    'ShareAccessTier',
    'ShareClient',
    'ShareDirectoryClient',
    'ShareFileClient',
    'ShareLeaseClient',
    'ShareNfsSettings',
    'ShareProperties',
    'ShareProtocolSettings',
    'ShareProtocols',
    'ShareRootSquash',
    'ShareSasPermissions',
    'ShareServiceClient',
    'ShareSmbSettings',
    'SmbEncryptionInTransit',
    'SmbMultichannel',
    'StorageErrorCode',
    'UserDelegationKey'
]


# This function is added to deal with HandleItem which is a generated model that
# was mistakenly added to the module exports. It has been removed import and __all__
# to prevent it from showing in intellisense/docs but we handle it here to prevent
# breaking any existing code which may have imported it.
def __getattr__(name):
    if name == 'HandleItem':
        from ._generated.models import HandleItem
        warnings.warn(
            "HandleItem is deprecated and should not be used. Use Handle instead.",
            DeprecationWarning
        )
        return HandleItem

    raise AttributeError(f"module 'azure.storage.fileshare' has no attribute {name}")
