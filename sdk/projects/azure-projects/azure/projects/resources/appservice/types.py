# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=line-too-long

from typing import List, Dict, Union
from typing_extensions import TypedDict

from ..._bicep.expressions import Parameter


VERSION = "2024-04-01"


class SkuDescription(TypedDict, total=False):
    capabilities: Union[List[Union["Capability", Parameter]], Parameter]  # type: ignore[name-defined]  # TODO
    """Capabilities of the SKU, e.g., is traffic manager enabled?"""
    capacity: Union[int, Parameter]
    """Current number of instances assigned to the resource."""
    family: Union[str, Parameter]
    """Family code of the resource SKU."""
    locations: Union[List[Union[str, Parameter]], Parameter]
    """Locations of the SKU."""
    name: Union[str, Parameter]
    """Name of the resource SKU."""
    size: Union[str, Parameter]
    """Size specifier of the resource SKU."""
    skuCapacity: Union["SkuCapacity", Parameter]  # type: ignore[name-defined]  # TODO
    """Min, max, and default scale values of the SKU."""
    tier: Union[str, Parameter]
    """Service tier of the resource SKU."""


class AppServicePlanResource(TypedDict, total=False):
    extendedLocation: Union["ExtendedLocation", Parameter]  # type: ignore[name-defined]  # TODO
    """Extended Location."""
    kind: Union[str, Parameter]
    """Kind of resource. If the resource is an app, you can refer to https://github.com/Azure/app-service-linux-docs/blob/master/Things_You_Should_Know/kind_property.md#app-service-resource-kind-reference for details supported values for kind."""
    location: Union[str, Parameter]
    """The geo-location where the resource lives."""
    name: Union[str, Parameter]
    """The resource name."""
    properties: "AppServicePlanProperties"  # type: ignore[name-defined]  # TODO
    """AppServicePlan resource specific properties."""
    sku: Union["SkuDescription", Parameter]  # type: ignore[name-defined]  # TODO
    """Description of a SKU for a scalable resource."""
    tags: Union[Dict[str, Union[str, Parameter]], Parameter]
    """Dictionary of tag names and values."""
