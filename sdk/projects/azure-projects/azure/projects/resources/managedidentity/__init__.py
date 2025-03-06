# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from collections import defaultdict
from typing import TYPE_CHECKING, List, Literal, TypedDict, Union, overload, Optional, Dict
from typing_extensions import TypeVar, Unpack

from .._identifiers import ResourceIdentifiers
from ...resources.resourcegroup import ResourceGroup
from ..._bicep.expressions import Output, ResourceSymbol, Parameter, Variable
from ..._parameters import GLOBAL_PARAMS
from ..._resource import FieldType, Resource, ResourceReference, ExtensionResources

if TYPE_CHECKING:
    from .types import UserAssignedIdentityResource


class UserAssignedIdentityKwargs(TypedDict, total=False):
    # lock: 'Lock'
    # """The lock settings of the service."""
    location: Union[str, Parameter[str]]
    """Location of the Resource Group. It uses the deployment's location when not provided."""
    tags: Union[Dict[str, Union[str, Parameter[str]]], Parameter[Dict[str, str]]]
    """Tags of the Resource Group."""


UserAssignedIdentityResourceType = TypeVar('UserAssignedIdentityResourceType', default='UserAssignedIdentityResource')
_DEFAULT_USER_ASSIGNED_IDENTITY: 'UserAssignedIdentityResource' = {
    'location': GLOBAL_PARAMS['location'],
    'tags': GLOBAL_PARAMS['azdTags'],
    'name': GLOBAL_PARAMS['defaultName']
}


class UserAssignedIdentity(Resource[UserAssignedIdentityResourceType]):
    DEFAULTS: 'UserAssignedIdentityResource' = _DEFAULT_USER_ASSIGNED_IDENTITY
    resource: Literal["Microsoft.ManagedIdentity/userAssignedIdentities"]
    properties: UserAssignedIdentityResourceType

    def __init__(
            self,
            properties: Optional['UserAssignedIdentityResource'] = None,
            /,
            name: Optional[Union[str, Parameter[str]]] = None,
            **kwargs: Unpack['UserAssignedIdentityKwargs']
    ) -> None:
        extensions: ExtensionResources = defaultdict(list)
        existing = kwargs.pop('existing', False)
        if not existing:
            properties = properties or {}
            if name:
                properties['name'] = name
            if 'location' in kwargs:
                properties['location'] = kwargs.pop('location')
            if 'tags' in kwargs:
                properties['tags'] = kwargs.pop('tags')
        super().__init__(
            properties,
            extensions=extensions,
            service_prefix=["identity"],
            existing=existing,
            identifier=ResourceIdentifiers.user_assigned_identity,
            **kwargs
        )

    @property
    def resource(self) -> str:
        if self._resource:
            return self._resource
        from .types import RESOURCE
        self._resource = RESOURCE
        return self._resource

    @property
    def version(self) -> str:
        if self._version:
            return self._version
        from .types import VERSION
        self._version = VERSION
        return self._version

    @classmethod
    def reference(
            cls,
            *,
            name: str,
            resource_group: Optional[Union[str, 'ResourceGroup']] = None,
    ) -> 'UserAssignedIdentity[ResourceReference]':
        from .types import RESOURCE, VERSION
        resource = f"{RESOURCE}@{VERSION}"
        return super().reference(
            resource=resource,
            name=name,
            resource_group=resource_group
        )

    def _symbol(self) -> ResourceSymbol:
        resource_ref = self.resource.split("/")[-1].lower()
        if resource_ref.endswith("ies"):
            resource_ref = resource_ref.rstrip("ies") + "y"
        else:
            resource_ref = resource_ref.rstrip('s')
        symbol = f"{resource_ref}{self._suffix.lower()}" if self._suffix else resource_ref
        return ResourceSymbol(symbol, principal_id=True)

    def _outputs(self, symbol, **kwargs) -> Dict[str, Output]:
        # TODO: This results in duplicate outputs if there's multiple identities.
        # Not sure if it's really needed as most people wont be using managedidentitycredential locally.
        # return {'client_id': Output("AZURE_CLIENT_ID", "properties.clientId", symbol)}
        return {}

    def __bicep__(self, fields, *, parameters, infra_component = None, module_name, **kwargs):
        symbols = super().__bicep__(fields, parameters=parameters, infra_component=infra_component, module_name=module_name, **kwargs)
        parameters['managedIdentityId'] = Variable('managedIdentityId', Output(None, 'id', symbols[0]), module="")
        parameters['managedIdentityPrincipalId'] = Variable('managedIdentityPrincipalId', Output(None, 'properties.principalId', symbols[0]), module="")
        parameters['managedIdentityClientId'] = Variable('managedIdentityClientId', Output(None, 'properties.clientId', symbols[0]), module="")
        return symbols
