# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import TYPE_CHECKING, TypedDict, Literal, List, Dict, Union
from typing_extensions import Required

from ...._bicep.expressions import Parameter


RESOURCE = "Microsoft.CognitiveServices/accounts/deployments"
VERSION = "2024-10-01"


class DeploymentCapacitySettings(TypedDict, total=False):
    designatedCapacity: Union[int, Parameter[int]]
    """The designated capacity."""
    priority: Union[int, Parameter[int]]
    """The priority of this capacity setting."""


class DeploymentScaleSettings(TypedDict, total=False):
    capacity: Union[int, Parameter[int]]
    """Deployment capacity."""
    scaleType: Union[Parameter[str], Literal["Manual", "Standard"]]
    """Deployment scale type."""


class DeploymentModel(TypedDict, total=False):
    """Properties of Cognitive Services account deployment model."""

    format: Required[Union[str, Parameter[str]]]
    """Deployment model format."""
    name: Required[Union[str, Parameter[str]]]
    """Deployment model name."""
    version: Union[str, Parameter[str]]
    """Deployment model version. If version is not specified, a default version will be assigned. The default version is different for different models and might change when there is new version available for a model. Default version for a model could be found from list models API."""
    publisher: Union[str, Parameter[str]]
    """Deployment model publisher."""
    source: Union[str, Parameter[str]]
    """Deployment model source ARM resource ID."""
    sourceAccount: Union[str, Parameter[str]]
    """Source of the model, another Microsoft.CognitiveServices accounts ARM resource ID."""


class DeploymentSku(TypedDict, total=False):
    """The resource model definition representing SKU."""

    name: Required[Union[str, Parameter[str]]]
    """The name of the SKU. Ex - P3. It is typically a letter+number code."""
    capacity: Union[int, Parameter[int]]
    """If the SKU supports scale out/in then the capacity integer should be included. If scale out/in is not possible for the resource this may be omitted."""
    family: Union[str, Parameter[str]]
    """If the service has different generations of hardware, for the same SKU, then that can be captured here."""
    size: Union[str, Parameter[str]]
    """The SKU size. When the name field is the combination of tier and some other value, this would be the standalone code."""
    tier: Union[Parameter[str], Literal["Basic", "Enterprise", "Free", "Premium", "Standard"]]
    """This field is required to be implemented by the Resource Provider if the service has more than one tier, but is not required on a PUT."""


class DeploymentProperties(TypedDict, total=False):
    capacitySettings: Union[DeploymentCapacitySettings, Parameter[DeploymentCapacitySettings]]
    """Internal use only."""
    currentCapacity: Union[int, Parameter[int]]
    """The current capacity."""
    model: Union[DeploymentModel, Parameter[DeploymentModel]]
    """Properties of Cognitive Services account deployment model."""
    parentDeploymentName: Union[str, Parameter[str]]
    """The name of parent deployment."""
    raiPolicyName: Union[str, Parameter[str]]
    """The name of RAI policy."""
    scaleSettings: Union[DeploymentScaleSettings, Parameter[DeploymentScaleSettings]]
    """Properties of Cognitive Services account deployment model. (Deprecated, please use Deployment.sku instead.)"""
    versionUpgradeOption: Union[
        Parameter[str], Literal["NoAutoUpgrade", "OnceCurrentVersionExpired", "OnceNewDefaultVersionAvailable"]
    ]
    """Deployment model version upgrade option."""


class DeploymentResource(TypedDict, total=False):
    name: Union[str, Parameter[str]]
    """The resource name."""
    properties: "DeploymentProperties"
    """Properties of Cognitive Services account deployment."""
    sku: Union["DeploymentSku", Parameter["DeploymentSku"]]
    """The resource model definition representing SKU"""
    tags: Union[Dict[str, Union[str, Parameter[str]]], Parameter[Dict[str, str]]]
    """Dictionary of tag names and values. See Tags in templates"""
