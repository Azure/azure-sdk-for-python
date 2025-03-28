# coding=utf-8
# pylint: disable=wrong-import-position

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._patch import *  # pylint: disable=unused-wildcard-import


from ._models import (  # type: ignore
    ErrorAdditionalInfo,
    ErrorDetail,
    ErrorResponse,
    ExtendedZone,
    ExtendedZoneProperties,
    Operation,
    OperationDisplay,
    ProxyResource,
    Resource,
    SystemData,
)

from ._enums import (  # type: ignore
    ActionType,
    CreatedByType,
    Origin,
    ProvisioningState,
    RegistrationState,
)
from ._patch import __all__ as _patch_all
from ._patch import *
from ._patch import patch_sdk as _patch_sdk

__all__ = [
    "ErrorAdditionalInfo",
    "ErrorDetail",
    "ErrorResponse",
    "ExtendedZone",
    "ExtendedZoneProperties",
    "Operation",
    "OperationDisplay",
    "ProxyResource",
    "Resource",
    "SystemData",
    "ActionType",
    "CreatedByType",
    "Origin",
    "ProvisioningState",
    "RegistrationState",
]
__all__.extend([p for p in _patch_all if p not in __all__])  # pyright: ignore
_patch_sdk()
