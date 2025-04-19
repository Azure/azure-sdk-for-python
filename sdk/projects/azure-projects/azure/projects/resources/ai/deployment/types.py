# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=line-too-long

from typing import List, Literal, Dict, Union
from typing_extensions import TypedDict

from ...._bicep.expressions import Parameter, ResourceSymbol


VERSION = "2024-10-01"


class DeploymentCapacitySettings(TypedDict, total=False):
    designatedCapacity: Union[int, Parameter]
    """The designated capacity."""
    priority: Union[int, Parameter]
    """The priority of this capacity setting."""


class DeploymentScaleSettings(TypedDict, total=False):
    capacity: Union[int, Parameter]
    """Deployment capacity."""
    scaleType: Union[Parameter, Literal["Manual", "Standard"]]
    """Deployment scale type."""


class DeploymentModel(TypedDict, total=False):
    """Properties of Cognitive Services account deployment model."""

    format: Union[str, Parameter]
    """Deployment model format."""
    name: Union[str, Parameter]
    """Deployment model name."""
    version: Union[str, Parameter]
    """Deployment model version. If version is not specified, a default version will be assigned. The default version is different for different models and might change when there is new version available for a model. Default version for a model could be found from list models API."""
    publisher: Union[str, Parameter]
    """Deployment model publisher."""
    source: Union[str, Parameter]
    """Deployment model source ARM resource ID."""
    sourceAccount: Union[str, Parameter]
    """Source of the model, another Microsoft.CognitiveServices accounts ARM resource ID."""


class DeploymentSku(TypedDict, total=False):
    """The resource model definition representing SKU."""

    name: Union[str, Parameter]
    """The name of the SKU. Ex - P3. It is typically a letter+number code."""
    capacity: Union[int, Parameter]
    """If the SKU supports scale out/in then the capacity integer should be included. If scale out/in is not possible for the resource this may be omitted."""
    family: Union[str, Parameter]
    """If the service has different generations of hardware, for the same SKU, then that can be captured here."""
    size: Union[str, Parameter]
    """The SKU size. When the name field is the combination of tier and some other value, this would be the standalone code."""
    tier: Union[Parameter, Literal["Basic", "Enterprise", "Free", "Premium", "Standard"]]
    """This field is required to be implemented by the Resource Provider if the service has more than one tier, but is not required on a PUT."""


class DeploymentProperties(TypedDict, total=False):
    capacitySettings: Union[DeploymentCapacitySettings, Parameter]
    """Internal use only."""
    currentCapacity: Union[int, Parameter]
    """The current capacity."""
    model: Union[DeploymentModel, Parameter]
    """Properties of Cognitive Services account deployment model."""
    parentDeploymentName: Union[str, Parameter]
    """The name of parent deployment."""
    raiPolicyName: Union[str, Parameter]
    """The name of RAI policy."""
    scaleSettings: Union[DeploymentScaleSettings, Parameter]
    """Properties of Cognitive Services account deployment model. (Deprecated, please use Deployment.sku instead.)"""
    versionUpgradeOption: Union[
        Parameter, Literal["NoAutoUpgrade", "OnceCurrentVersionExpired", "OnceNewDefaultVersionAvailable"]
    ]
    """Deployment model version upgrade option."""


class DeploymentResource(TypedDict, total=False):
    name: Union[str, Parameter]
    """The resource name."""
    properties: "DeploymentProperties"
    """Properties of Cognitive Services account deployment."""
    sku: Union["DeploymentSku", Parameter]
    """The resource model definition representing SKU"""
    tags: Union[Dict[str, Union[str, Parameter]], Parameter]
    """Dictionary of tag names and values. See Tags in templates"""
    parent: ResourceSymbol
    dependsOn: List[ResourceSymbol]
