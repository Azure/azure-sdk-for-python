# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=line-too-long

from __future__ import annotations
from typing import TypedDict, Union

from ..._bicep.expressions import Parameter



VERSION = '2024-04-01'


class AppServicePlanProperties(TypedDict, total=False):
    elasticScaleEnabled: Union[bool, Parameter]
    """ServerFarm supports ElasticScale. Apps in this plan will scale as if the ServerFarm was ElasticPremium sku"""
    freeOfferExpirationTime: Union[str, Parameter]
    """The time when the server farm free offer expires."""
    hostingEnvironmentProfile: Union[AppServicePlanHostingEnvironmentProfile, Parameter]
    """Specification for the App Service Environment to use for the App Service plan."""
    hyperV: Union[bool, Parameter]
    """If Hyper-V container app service plan <code>true</code>, <code>false</code> otherwise."""
    isSpot: Union[bool, Parameter]
    """If <code>true</code>, this App Service Plan owns spot instances."""
    isXenon: Union[bool, Parameter]
    """Obsolete: If Hyper-V container app service plan <code>true</code>, <code>false</code> otherwise."""
    kubeEnvironmentProfile: Union[AppServicePlanKubeEnvironmentProfile, Parameter]
    """Specification for the Kubernetes Environment to use for the App Service plan."""
    maximumElasticWorkerCount: Union[int, Parameter]
    """Maximum number of total workers allowed for this ElasticScaleEnabled App Service Plan"""
    perSiteScaling: Union[bool, Parameter]
    """If <code>true</code>, apps assigned to this App Service plan can be scaled independently.If <code>false</code>, apps assigned to this App Service plan will scale to all instances of the plan."""
    reserved: Union[bool, Parameter]
    """If Linux app service plan <code>true</code>, <code>false</code> otherwise."""
    spotExpirationTime: Union[str, Parameter]
    """The time when the server farm expires. Valid only if it is a spot server farm."""
    targetWorkerCount: Union[int, Parameter]
    """Scaling worker count."""
    targetWorkerSizeId: Union[int, Parameter]
    """Scaling worker size ID."""
    workerTierName: Union[str, Parameter]
    """Target worker tier assigned to the App Service plan."""
    zoneRedundant: Union[bool, Parameter]
    """If <code>true</code>, this App Service Plan will perform availability zone balancing.If <code>false</code>, this App Service Plan will not perform availability zone balancing."""


class AppServicePlanCapability(TypedDict, total=False):
    name: Union[str, Parameter]
    """Name of the SKU capability."""
    reason: Union[str, Parameter]
    """Reason of the SKU capability."""
    value: Union[str, Parameter]
    """Value of the SKU capability."""


class AppServicePlanExtendedLocation(TypedDict, total=False):
    name: Union[str, Parameter]
    """Name of extended location."""


class AppServicePlanHostingEnvironmentProfile(TypedDict, total=False):
    id: Union[str, Parameter]
    """Resource ID of the App Service Environment."""


class AppServicePlanKubeEnvironmentProfile(TypedDict, total=False):
    id: Union[str, Parameter]
    """Resource ID of the Kubernetes Environment."""


class AppServicePlanResource(TypedDict, total=False):
    extendedLocation: Union[AppServicePlanExtendedLocation, Parameter]
    """Extended Location."""
    kind: Union[str, Parameter]
    """Kind of resource. If the resource is an app, you can refer to https://github.com/Azure/app-service-linux-docs/blob/master/Things_You_Should_Know/kind_property.md#app-service-resource-kind-reference for details supported values for kind."""
    location: Union[str, Parameter]
    """Resource Location."""
    name: Union[str, Parameter]
    """The resource name"""
    properties: Union[AppServicePlanProperties, Parameter]
    """AppServicePlan resource specific properties"""
    sku: Union[AppServicePlanSkuDescription, Parameter]
    """Description of a SKU for a scalable resource."""
    tags: Union[dict[str, Union[str, Parameter]], Parameter]
    """Resource tags"""


class AppServicePlanSkuCapacity(TypedDict, total=False):
    default: Union[int, Parameter]
    """Default number of workers for this App Service plan SKU."""
    elasticMaximum: Union[int, Parameter]
    """Maximum number of Elastic workers for this App Service plan SKU."""
    maximum: Union[int, Parameter]
    """Maximum number of workers for this App Service plan SKU."""
    minimum: Union[int, Parameter]
    """Minimum number of workers for this App Service plan SKU."""
    scaleType: Union[str, Parameter]
    """Available scale configurations for an App Service plan."""


class AppServicePlanSkuDescription(TypedDict, total=False):
    capabilities: Union[list[AppServicePlanCapability], Parameter]
    """Capabilities of the SKU, e.g., is traffic manager enabled?"""
    capacity: Union[int, Parameter]
    """Current number of instances assigned to the resource."""
    family: Union[str, Parameter]
    """Family code of the resource SKU."""
    locations: Union[list[Union[str, Parameter]], Parameter]
    """Locations of the SKU."""
    name: Union[str, Parameter]
    """Name of the resource SKU."""
    size: Union[str, Parameter]
    """Size specifier of the resource SKU."""
    skuCapacity: Union[AppServicePlanSkuCapacity, Parameter]
    """Min, max, and default scale values of the SKU."""
    tier: Union[str, Parameter]
    """Service tier of the resource SKU."""
