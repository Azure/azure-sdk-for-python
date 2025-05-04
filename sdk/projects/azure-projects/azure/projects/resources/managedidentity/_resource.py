# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=arguments-differ

from collections import defaultdict
from typing import TYPE_CHECKING, Any, Generic, TypedDict, Literal, Mapping, Union, Optional, cast
from typing_extensions import TypeVar, Unpack

from .._identifiers import ResourceIdentifiers
from ...resources.resourcegroup import ResourceGroup
from ..._bicep.expressions import Output, ResourceSymbol, Parameter
from ..._parameters import GLOBAL_PARAMS
from ..._resource import Resource, ResourceReference, ExtensionResources

if TYPE_CHECKING:
    from ._types import UserAssignedIdentityResource


class UserAssignedIdentityKwargs(TypedDict, total=False):
    # lock: 'Lock'
    # """The lock settings of the service."""
    location: Union[str, Parameter]
    """Location of the User Assigned Identity. It uses the deployment's location when not provided."""
    tags: Union[dict[str, Union[str, Parameter]], Parameter]
    """Tags of the User Assigned Identity."""


UserAssignedIdentityResourceType = TypeVar(
    "UserAssignedIdentityResourceType", bound=Mapping[str, Any], default="UserAssignedIdentityResource"
)
_DEFAULT_USER_ASSIGNED_IDENTITY: "UserAssignedIdentityResource" = {
    "location": GLOBAL_PARAMS["location"],
    "name": GLOBAL_PARAMS["defaultName"],
}


class UserAssignedIdentity(Resource, Generic[UserAssignedIdentityResourceType]):
    """A user-assigned managed identity in Azure.

    User-assigned managed identities are Azure resources that can be used to authenticate to services
    that support Azure AD authentication.

    :ivar DEFAULTS: Default values for the resource properties
    :vartype DEFAULTS: UserAssignedIdentityResource
    :ivar properties: Properties of the user-assigned identity resource
    :vartype properties: UserAssignedIdentityResourceType
    :ivar extensions: Extension resources associated with this identity (roles, etc.)
    :vartype extensions: ExtensionResources
    :ivar parent: Parent resource, None for user-assigned identities
    :vartype parent: None
    :ivar identifier: Resource identifier for the user-assigned identity
    :vartype identifier: ResourceIdentifiers
    :ivar resource: The Azure resource type string
    :vartype resource: str
    :ivar version: The API version of the resource
    :vartype version: str

    :param properties: Properties for the user-assigned identity
    :type properties: Optional[UserAssignedIdentityResource]
    :param name: Name of the user-assigned identity
    :type name: Optional[Union[str, Parameter]]
    :keyword str location: Location of the User Assigned Identity. It uses the deployment's location when not provided.
    :paramtype location: Union[str, Parameter]
    :keyword dict tags: Tags of the User Assigned Identity.
    :paramtype tags: Union[dict[str, Union[str, Parameter]], Parameter]
    """

    DEFAULTS: "UserAssignedIdentityResource" = _DEFAULT_USER_ASSIGNED_IDENTITY  # type: ignore[assignment]
    properties: UserAssignedIdentityResourceType
    parent: None

    def __init__(
        self,
        properties: Optional["UserAssignedIdentityResource"] = None,
        /,
        name: Optional[Union[str, Parameter]] = None,
        **kwargs: Unpack["UserAssignedIdentityKwargs"],
    ) -> None:
        extensions: ExtensionResources = defaultdict(list)  # type: ignore  # Doesn't like the default dict.
        # 'existing' is passed by the reference classmethod.
        existing = kwargs.pop("existing", False)  # type: ignore[typeddict-item]
        if not existing:
            properties = properties or {}
            if name:
                properties["name"] = name
            if "location" in kwargs:
                properties["location"] = kwargs.pop("location")
            if "tags" in kwargs:
                properties["tags"] = kwargs.pop("tags")
            elif "tags" not in properties:
                properties["tags"] = {}
            if "azd-env-name" not in properties["tags"]:
                properties["tags"]["azd-env-name"] = None
        super().__init__(
            properties,
            extensions=extensions,
            service_prefix=["identity"],
            existing=existing,
            identifier=ResourceIdentifiers.user_assigned_identity,
            **kwargs,
        )

    @property
    def resource(self) -> Literal["Microsoft.ManagedIdentity/userAssignedIdentities"]:
        return "Microsoft.ManagedIdentity/userAssignedIdentities"

    @property
    def version(self) -> str:
        from ._types import VERSION

        return VERSION

    @classmethod
    def reference(  # type: ignore[override]  # Parameter subset and renames
        cls,
        *,
        name: Union[str, Parameter],
        resource_group: Optional[Union[str, Parameter, ResourceGroup[ResourceReference]]] = None,
    ) -> "UserAssignedIdentity[ResourceReference]":
        existing = super().reference(name=name, resource_group=resource_group)
        return cast(UserAssignedIdentity[ResourceReference], existing)

    def _build_symbol(self, suffix: Optional[Union[str, Parameter]]):
        symbol = super()._build_symbol(suffix)
        return ResourceSymbol(cast(str, symbol._value), principal_id=True)  # pylint: disable=protected-access

    def _outputs(self, **kwargs) -> dict[str, list[Output]]:
        return {}

    def __bicep__(self, fields, *, parameters, infra_component=None, **kwargs):
        symbols = super().__bicep__(fields, parameters=parameters, infra_component=infra_component, **kwargs)
        # TODO: This will get overwritten with subsequence managed identities....
        parameters["managedIdentityId"] = Output(None, "id", symbols[0])
        parameters["managedIdentityPrincipalId"] = Output(None, "properties.principalId", symbols[0])
        parameters["managedIdentityClientId"] = Output(None, "properties.clientId", symbols[0])
        return symbols
