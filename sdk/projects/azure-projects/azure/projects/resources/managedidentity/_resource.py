# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=arguments-differ

from collections import defaultdict
from typing import TYPE_CHECKING, Any, Generic, List, Literal, Mapping, Union, Optional, Dict, cast
from typing_extensions import TypeVar, Unpack, TypedDict

from .._identifiers import ResourceIdentifiers
from ...resources.resourcegroup import ResourceGroup
from ..._bicep.expressions import Output, ResourceSymbol, Parameter
from ..._parameters import GLOBAL_PARAMS
from ..._resource import Resource, ResourceReference, ExtensionResources

if TYPE_CHECKING:
    from .types import UserAssignedIdentityResource


class UserAssignedIdentityKwargs(TypedDict, total=False):
    # lock: 'Lock'
    # """The lock settings of the service."""
    location: Union[str, Parameter]
    """Location of the Resource Group. It uses the deployment's location when not provided."""
    tags: Union[Dict[str, Union[str, Parameter]], Parameter]
    """Tags of the Resource Group."""


UserAssignedIdentityResourceType = TypeVar(
    "UserAssignedIdentityResourceType", bound=Mapping[str, Any], default="UserAssignedIdentityResource"
)
_DEFAULT_USER_ASSIGNED_IDENTITY: "UserAssignedIdentityResource" = {
    "location": GLOBAL_PARAMS["location"],
    "tags": GLOBAL_PARAMS["azdTags"],
    "name": GLOBAL_PARAMS["defaultName"],
}


class UserAssignedIdentity(Resource, Generic[UserAssignedIdentityResourceType]):
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
        from .types import VERSION

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

    def _outputs(self, **kwargs) -> Dict[str, List[Output]]:
        # TODO: This results in duplicate outputs if there's multiple identities.
        # Not sure if it's really needed as most people wont be using managedidentitycredential locally.
        # return {'client_id': Output("AZURE_CLIENT_ID", "properties.clientId", symbol)}
        return {}

    def __bicep__(self, fields, *, parameters, infra_component=None, **kwargs):
        symbols = super().__bicep__(fields, parameters=parameters, infra_component=infra_component, **kwargs)
        # TODO: This will get overwritten with subsequence managed identities....
        parameters["managedIdentityId"] = Output(None, "id", symbols[0])
        parameters["managedIdentityPrincipalId"] = Output(None, "properties.principalId", symbols[0])
        parameters["managedIdentityClientId"] = Output(None, "properties.clientId", symbols[0])
        return symbols
