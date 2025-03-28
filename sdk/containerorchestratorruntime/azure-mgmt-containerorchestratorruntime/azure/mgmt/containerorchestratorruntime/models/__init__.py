# coding=utf-8
# pylint: disable=wrong-import-position

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._patch import *  # pylint: disable=unused-wildcard-import


from ._models import (  # type: ignore
    BgpPeer,
    BgpPeerProperties,
    BlobStorageClassTypeProperties,
    ErrorAdditionalInfo,
    ErrorDetail,
    ErrorResponse,
    ExtensionResource,
    LoadBalancer,
    LoadBalancerProperties,
    NativeStorageClassTypeProperties,
    NfsStorageClassTypeProperties,
    Operation,
    OperationDisplay,
    Resource,
    RwxStorageClassTypeProperties,
    ServiceProperties,
    ServiceResource,
    SmbStorageClassTypeProperties,
    StorageClassProperties,
    StorageClassPropertiesUpdate,
    StorageClassResource,
    StorageClassResourceUpdate,
    StorageClassTypeProperties,
    StorageClassTypePropertiesUpdate,
    SystemData,
)

from ._enums import (  # type: ignore
    AccessMode,
    ActionType,
    AdvertiseMode,
    CreatedByType,
    DataResilienceTier,
    FailoverTier,
    NfsDirectoryActionOnVolumeDeletion,
    Origin,
    PerformanceTier,
    ProvisioningState,
    SCType,
    VolumeBindingMode,
    VolumeExpansion,
)
from ._patch import __all__ as _patch_all
from ._patch import *
from ._patch import patch_sdk as _patch_sdk

__all__ = [
    "BgpPeer",
    "BgpPeerProperties",
    "BlobStorageClassTypeProperties",
    "ErrorAdditionalInfo",
    "ErrorDetail",
    "ErrorResponse",
    "ExtensionResource",
    "LoadBalancer",
    "LoadBalancerProperties",
    "NativeStorageClassTypeProperties",
    "NfsStorageClassTypeProperties",
    "Operation",
    "OperationDisplay",
    "Resource",
    "RwxStorageClassTypeProperties",
    "ServiceProperties",
    "ServiceResource",
    "SmbStorageClassTypeProperties",
    "StorageClassProperties",
    "StorageClassPropertiesUpdate",
    "StorageClassResource",
    "StorageClassResourceUpdate",
    "StorageClassTypeProperties",
    "StorageClassTypePropertiesUpdate",
    "SystemData",
    "AccessMode",
    "ActionType",
    "AdvertiseMode",
    "CreatedByType",
    "DataResilienceTier",
    "FailoverTier",
    "NfsDirectoryActionOnVolumeDeletion",
    "Origin",
    "PerformanceTier",
    "ProvisioningState",
    "SCType",
    "VolumeBindingMode",
    "VolumeExpansion",
]
__all__.extend([p for p in _patch_all if p not in __all__])  # pyright: ignore
_patch_sdk()
