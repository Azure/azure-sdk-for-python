# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=line-too-long

from typing import TypedDict, Literal, Dict, Union
from typing_extensions import Required

from ..._bicep.expressions import Parameter


RESOURCE = "Microsoft.MachineLearningServices/workspaces"
VERSION = "2024-04-01-preview"


class MLIdentity(TypedDict, total=False):
    type: Required[Union[Literal["None", "SystemAssigned", "SystemAssigned,UserAssigned", "UserAssigned"], Parameter]]
    """The identity type."""
    userAssignedIdentities: Dict[Union[str, Parameter], Dict]
    """The set of user assigned identities associated with the resource."""


class MachineLearningWorkspaceResource(TypedDict, total=False):
    identity: Union[MLIdentity, Parameter]
    """Managed service identity (system assigned and/or user assigned identities)."""
    kind: Union[Literal["Default", "FeatureStore", "Hub", "Project"], Parameter]
    """The type of Azure Machine Learning workspace to create."""
    location: Union[str, Parameter]
    """The geo-location where the resource lives."""
    name: Union[str, Parameter]
    """The resource name."""
    properties: Union["WorkspaceProperties", Parameter]
    """Additional attributes of the entity."""
    sku: Union["Sku", Parameter]
    """This field is required to be implemented by the RP because AML is supporting more than one tier."""
    tags: Union[Dict[str, Union[str, Parameter]], Parameter]
    """Dictionary of tag names and values."""
