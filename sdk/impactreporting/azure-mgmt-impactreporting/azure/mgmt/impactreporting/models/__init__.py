# coding=utf-8
# pylint: disable=wrong-import-position

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._patch import *  # pylint: disable=unused-wildcard-import


from ._models import (  # type: ignore
    ClientIncidentDetails,
    Connectivity,
    Connector,
    ConnectorProperties,
    ConnectorUpdate,
    ConnectorUpdateProperties,
    Content,
    ErrorAdditionalInfo,
    ErrorDetail,
    ErrorDetailProperties,
    ErrorResponse,
    ExpectedValueRange,
    ImpactCategory,
    ImpactCategoryProperties,
    ImpactDetails,
    Insight,
    InsightProperties,
    Operation,
    OperationDisplay,
    Performance,
    ProxyResource,
    RequiredImpactProperties,
    Resource,
    SourceOrTarget,
    SystemData,
    Workload,
    WorkloadImpact,
    WorkloadImpactProperties,
)

from ._enums import (  # type: ignore
    ActionType,
    ConfidenceLevel,
    CreatedByType,
    IncidentSource,
    MetricUnit,
    Origin,
    Platform,
    Protocol,
    ProvisioningState,
    Toolset,
)
from ._patch import __all__ as _patch_all
from ._patch import *
from ._patch import patch_sdk as _patch_sdk

__all__ = [
    "ClientIncidentDetails",
    "Connectivity",
    "Connector",
    "ConnectorProperties",
    "ConnectorUpdate",
    "ConnectorUpdateProperties",
    "Content",
    "ErrorAdditionalInfo",
    "ErrorDetail",
    "ErrorDetailProperties",
    "ErrorResponse",
    "ExpectedValueRange",
    "ImpactCategory",
    "ImpactCategoryProperties",
    "ImpactDetails",
    "Insight",
    "InsightProperties",
    "Operation",
    "OperationDisplay",
    "Performance",
    "ProxyResource",
    "RequiredImpactProperties",
    "Resource",
    "SourceOrTarget",
    "SystemData",
    "Workload",
    "WorkloadImpact",
    "WorkloadImpactProperties",
    "ActionType",
    "ConfidenceLevel",
    "CreatedByType",
    "IncidentSource",
    "MetricUnit",
    "Origin",
    "Platform",
    "Protocol",
    "ProvisioningState",
    "Toolset",
]
__all__.extend([p for p in _patch_all if p not in __all__])  # pyright: ignore
_patch_sdk()
