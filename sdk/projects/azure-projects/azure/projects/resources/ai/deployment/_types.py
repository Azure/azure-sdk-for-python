# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=line-too-long

from __future__ import annotations
from typing import TypedDict, Literal, Union, Any

from ...._bicep.expressions import Parameter


VERSION = '2024-10-01'


class DeploymentResourceDeploymentCapacitySettings(TypedDict, total=False):
    designatedCapacity: Union[int, Parameter]
    """The designated capacity."""
    priority: Union[int, Parameter]
    """The priority of this capacity setting."""


class DeploymentResourceDeploymentModel(TypedDict, total=False):
    format: Union[str, Parameter]
    """Deployment model format."""
    name: Union[str, Parameter]
    """Deployment model name."""
    publisher: Union[str, Parameter]
    """Deployment model publisher."""
    source: Union[str, Parameter]
    """Optional. Deployment model source ARM resource ID."""
    sourceAccount: Union[str, Parameter]
    """Optional. Source of the model, another Microsoft.CognitiveServices accounts ARM resource ID."""
    version: Union[str, Parameter]
    """Optional. Deployment model version. If version is not specified, a default version will be assigned. The default version is different for different models and might change when there is new version available for a model. Default version for a model could be found from list models API."""


class DeploymentResourceDeploymentProperties(TypedDict, total=False):
    capacitySettings: Union[DeploymentResourceDeploymentCapacitySettings, Parameter]
    """Internal use only."""
    currentCapacity: Union[int, Parameter]
    """The current capacity."""
    model: Union[DeploymentResourceDeploymentModel, Parameter]
    """Properties of Cognitive Services account deployment model."""
    parentDeploymentName: Union[str, Parameter]
    """The name of parent deployment."""
    raiPolicyName: Union[str, Parameter]
    """The name of RAI policy."""
    scaleSettings: Union[DeploymentResourceDeploymentScaleSettings, Parameter]
    """Properties of Cognitive Services account deployment model. (Deprecated, please use Deployment.sku instead.)"""
    versionUpgradeOption: Union[Literal['OnceNewDefaultVersionAvailable', 'NoAutoUpgrade', 'OnceCurrentVersionExpired'], Parameter]
    """Deployment model version upgrade option."""


class DeploymentResourceDeploymentScaleSettings(TypedDict, total=False):
    capacity: Union[int, Parameter]
    """Deployment capacity."""
    scaleType: Union[Literal['Manual', 'Standard'], Parameter]
    """Deployment scale type."""


class DeploymentResource(TypedDict, total=False):
    name: Union[str, Parameter]
    """The resource name"""
    properties: Union[DeploymentResourceDeploymentProperties, Parameter]
    """Properties of Cognitive Services account deployment."""
    sku: Union[DeploymentResourceSku, Parameter]
    """The resource model definition representing SKU"""
    tags: Union[dict[str, Union[str, Parameter]], Parameter]
    """Resource tags"""
    parent: Any
    """The Symbolic name of the resource that is the parent for this resource."""


class DeploymentResourceSku(TypedDict, total=False):
    capacity: Union[int, Parameter]
    """If the SKU supports scale out/in then the capacity integer should be included. If scale out/in is not possible for the resource this may be omitted."""
    family: Union[str, Parameter]
    """If the service has different generations of hardware, for the same SKU, then that can be captured here."""
    name: Union[str, Parameter]
    """The name of the SKU. Ex - P3. It is typically a letter+number code"""
    size: Union[str, Parameter]
    """The SKU size. When the name field is the combination of tier and some other value, this would be the standalone code."""
    tier: Union[Literal['Standard', 'Premium', 'Free', 'Enterprise', 'Basic'], Parameter]
    """This field is required to be implemented by the Resource Provider if the service has more than one tier, but is not required on a PUT."""
