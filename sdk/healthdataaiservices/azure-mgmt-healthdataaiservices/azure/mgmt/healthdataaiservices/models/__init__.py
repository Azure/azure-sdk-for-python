# coding=utf-8
# pylint: disable=wrong-import-position

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._patch import *  # pylint: disable=unused-wildcard-import


from ._models import (  # type: ignore
    DeidPropertiesUpdate,
    DeidService,
    DeidServiceProperties,
    DeidUpdate,
    ErrorAdditionalInfo,
    ErrorDetail,
    ErrorResponse,
    ManagedServiceIdentity,
    ManagedServiceIdentityUpdate,
    Operation,
    OperationDisplay,
    PrivateEndpoint,
    PrivateEndpointConnection,
    PrivateEndpointConnectionProperties,
    PrivateEndpointConnectionResource,
    PrivateLinkResource,
    PrivateLinkResourceProperties,
    PrivateLinkServiceConnectionState,
    ProxyResource,
    Resource,
    SystemData,
    TrackedResource,
    UserAssignedIdentity,
)

from ._enums import (  # type: ignore
    ActionType,
    CreatedByType,
    ManagedServiceIdentityType,
    Origin,
    PrivateEndpointConnectionProvisioningState,
    PrivateEndpointServiceConnectionStatus,
    ProvisioningState,
    PublicNetworkAccess,
)
from ._patch import __all__ as _patch_all
from ._patch import *
from ._patch import patch_sdk as _patch_sdk

__all__ = [
    "DeidPropertiesUpdate",
    "DeidService",
    "DeidServiceProperties",
    "DeidUpdate",
    "ErrorAdditionalInfo",
    "ErrorDetail",
    "ErrorResponse",
    "ManagedServiceIdentity",
    "ManagedServiceIdentityUpdate",
    "Operation",
    "OperationDisplay",
    "PrivateEndpoint",
    "PrivateEndpointConnection",
    "PrivateEndpointConnectionProperties",
    "PrivateEndpointConnectionResource",
    "PrivateLinkResource",
    "PrivateLinkResourceProperties",
    "PrivateLinkServiceConnectionState",
    "ProxyResource",
    "Resource",
    "SystemData",
    "TrackedResource",
    "UserAssignedIdentity",
    "ActionType",
    "CreatedByType",
    "ManagedServiceIdentityType",
    "Origin",
    "PrivateEndpointConnectionProvisioningState",
    "PrivateEndpointServiceConnectionStatus",
    "ProvisioningState",
    "PublicNetworkAccess",
]
__all__.extend([p for p in _patch_all if p not in __all__])  # pyright: ignore
_patch_sdk()
