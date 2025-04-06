# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=line-too-long

from typing import Literal, Dict, Union
from typing_extensions import TypedDict, Required

from ...._bicep.expressions import Parameter


VERSION = "2024-04-01"


class SiteIdentity(TypedDict, total=False):
    type: Required[Union[Literal["None", "SystemAssigned", "SystemAssigned,UserAssigned", "UserAssigned"], Parameter]]
    """The identity type."""
    userAssignedIdentities: Dict[Union[str, Parameter], Dict]
    """The set of user assigned identities associated with the resource."""


class AppSiteResource(TypedDict, total=False):
    identity: Union[SiteIdentity, Parameter]
    """Managed service identity (system assigned and/or user assigned identities)."""
    extendedLocation: Union["ExtendedLocation", Parameter]  # type: ignore[name-defined]  # TODO
    """Extended Location."""
    kind: Union[str, Parameter]
    """Kind of resource. If the resource is an app, you can refer to https://github.com/Azure/app-service-linux-docs/blob/master/Things_You_Should_Know/kind_property.md#app-service-resource-kind-reference for details supported values for kind."""
    location: Union[str, Parameter]
    """The geo-location where the resource lives."""
    name: Union[str, Parameter]
    """The resource name."""
    properties: "AppSiteProperties"  # type: ignore[name-defined]  # TODO
    """AppServicePlan resource specific properties."""
    tags: Union[Dict[str, Union[str, Parameter]], Parameter]
    """Dictionary of tag names and values."""
