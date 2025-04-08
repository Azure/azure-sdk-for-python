# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Dict, List, Literal, Any, Optional, Union, TYPE_CHECKING, cast
from typing_extensions import Required, TypedDict

from .roles import RoleAssignment as RoleResource, BUILT_IN_ROLES
from .._identifiers import ResourceIdentifiers
from ..._bicep.expressions import Parameter, PlaceholderParameter, ResourceSymbol, Expression, Guid, ResourceGroup
from ..._bicep.utils import clean_name
from ..._parameters import GLOBAL_PARAMS

if TYPE_CHECKING:
    from ..._resource import FieldsType
    from .roles.types import RoleAssignmentProperties


class RoleAssignment(TypedDict, total=False):
    principalId: Required[Union[str, Parameter]]
    """The principal ID of the principal (user/group/identity) to assign the role to."""
    roleDefinitionIdOrName: Required[Union[str, Parameter]]
    """The role to assign. You can provide either the display name of the role definition, the
    role definition GUID, or its fully qualified ID in the following format:
    '/providers/Microsoft.Authorization/roleDefinitions/c2f4ef07-c644-48eb-af81-4b1b4947fb11'.
    """
    condition: Union[str, Parameter]
    """The conditions on the role assignment. This limits the resources it can be assigned to. e.g.: @Resource[
    Microsoft.Storage/storageAccounts/blobServices/containers:ContainerName] StringEqualsIgnoreCase
    "foo_storage_container".
    """
    conditionVersion: Literal["2.0"]
    """Version of the condition."""
    delegatedManagedIdentityResourceId: Union[str, Parameter]
    """The Resource Id of the delegated managed identity resource."""
    description: Union[str, Parameter]
    """The description of the role assignment."""
    name: Union[str, Parameter]
    """The name (as GUID) of the role assignment. If not provided, a GUID will be generated."""
    principalType: Union[Literal["Device", "ForeignGroup", "Group", "ServicePrincipal", "User"], Parameter]
    """The principal type of the assigned principal ID."""


class Identity(TypedDict, total=False):
    type: Required[Union[Literal["None", "SystemAssigned", "SystemAssigned,UserAssigned", "UserAssigned"], Parameter]]
    """The identity type."""
    userAssignedIdentities: Dict[Union[str, Parameter], Any]
    """Gets or sets a list of key value pairs that describe the set of User Assigned identities that will
    be used with this storage account. The key is the ARM resource identifier of the identity.
    """


class ManagedIdentity(TypedDict, total=False):
    systemAssigned: Union[bool, Parameter]
    """Enables system assigned managed identity on the resource."""
    userAssignedResourceIds: List[Union[str, Parameter]]
    """The resource ID(s) to assign to the resource. Required if a user assigned identity is used for encryption."""


# TODO: Automatically set None identities if there's no User Assigned identity in the infrastructure.
def convert_managed_identities(managed_identities: Optional[ManagedIdentity]) -> Identity:
    identity: Identity = {"type": "None"}
    if managed_identities is None:
        return identity
    user_assigned_identities = managed_identities.get("userAssignedResourceIds", [])
    if managed_identities.get("systemAssigned", False):
        if user_assigned_identities:
            identity["type"] = "SystemAssigned,UserAssigned"
            identity["userAssignedIdentities"] = {}
            for uai in user_assigned_identities:
                identity["userAssignedIdentities"][uai] = {}
        else:
            identity["type"] = "SystemAssigned"
    elif user_assigned_identities:
        identity["type"] = "UserAssigned"
        identity["userAssignedIdentities"] = {}
        for uai in user_assigned_identities:
            identity["userAssignedIdentities"][uai] = {}
    return identity


def _build_role_assignment(
    resource: str,
    role: Union[str, Parameter, RoleAssignment],
    fields: "FieldsType",
    name: Union[str, Parameter],
    *,
    parent: Optional[ResourceSymbol],
    parameters: Dict[str, Parameter],
    symbol: Expression,
    principal_id: Expression,
    principal_type: Literal["ServicePrincipal", "User"],
) -> ResourceSymbol:
    if isinstance(role, (str, Parameter)):
        if parent:
            # TODO: Should 'Guid' be a subtype of Parameter?
            unique_name = Guid(resource, GLOBAL_PARAMS["environmentName"], parent.name, name, principal_type, role)
        else:
            unique_name = Guid(resource, GLOBAL_PARAMS["environmentName"], name, principal_type, role)
        new_role = RoleResource(
            {
                "name": unique_name,
                "properties": {
                    "principalId": principal_id,
                    "principalType": principal_type,
                    "roleDefinitionId": BUILT_IN_ROLES.get(cast(str, role), role),
                },
                "scope": symbol,
            }
        )
        return new_role.__bicep__(fields, parameters=parameters)[0]

    role_properties: "RoleAssignmentProperties" = {
        "principalId": role["principalId"],
        "principalType": role["principalType"],
        "roleDefinitionId": BUILT_IN_ROLES.get(
            cast(str, role["roleDefinitionIdOrName"]), role["roleDefinitionIdOrName"]
        ),
    }
    if "condition" in role:
        role_properties["condition"] = role["condition"]
    if "conditionVersion" in role:
        role_properties["conditionVersion"] = role["conditionVersion"]
    if "delegatedManagedIdentityResourceId" in role:
        role_properties["delegatedManagedIdentityResourceId"] = role["delegatedManagedIdentityResourceId"]
    if "description" in role:
        role_properties["description"] = role["description"]
    new_role = RoleResource(
        {
            "name": role.get("name", Guid(resource, name, role["principalId"], role["roleDefinitionIdOrName"])),
            "properties": role_properties,
            "scope": symbol,
        }
    )
    return new_role.__bicep__(fields, parameters=parameters)[0]


def load_roles(
    roles_parameter: Parameter, parameters: Dict[str, Parameter]  # pylint: disable=unused-argument  # TODO
) -> List[Union[str, RoleAssignment]]:
    # TODO: How to resolve a parameter with a list of names? Need to pass in provision config.
    # Can use _setting.convert_parameter logic.
    # if roles_parameter.name in parameters:
    #     return parameters[roles_parameter.name]
    if roles_parameter.default:
        return roles_parameter.default
    raise ValueError(f"Unable to resolve parameter '{roles_parameter.name}' to build role assignments.")


def add_extensions(fields: "FieldsType", parameters: Dict[str, Parameter]):
    for field in list(fields.values()):
        if not isinstance(parameters["managedIdentityPrincipalId"], PlaceholderParameter):
            roles = field.extensions.get("managed_identity_roles", [])
            if isinstance(roles, Parameter):
                roles = load_roles(roles, parameters)
            role_symbols = []
            for role in roles:
                role_symbols.append(
                    _build_role_assignment(
                        clean_name(field.resource),
                        role,
                        fields,
                        field.properties["name"],
                        parent=field.properties.get("parent"),
                        parameters=parameters,
                        symbol=field.symbol,
                        principal_id=parameters["managedIdentityPrincipalId"],
                        principal_type="ServicePrincipal",
                    )
                )
            # TODO: We shouldn't do this - not sure if we need to find a way to surface the resource
            # symbols or if we can just safely remove it.
            field.extensions["managed_identity_roles"] = role_symbols  # type: ignore[typeddict-item]  # TODO
        if parameters.get("principalId"):
            roles = field.extensions.get("user_roles", [])
            if isinstance(roles, Parameter):
                roles = load_roles(roles, parameters)
            role_symbols = []
            for role in roles:
                role_symbols.append(
                    _build_role_assignment(
                        clean_name(field.resource),
                        role,
                        fields,
                        field.properties["name"],
                        parent=field.properties.get("parent"),
                        parameters=parameters,
                        symbol=field.symbol,
                        principal_id=parameters["principalId"],
                        principal_type="User",
                    )
                )
            # TODO: We shouldn't do this - not sure if we need to find a way to surface the resource
            # symbols or if we can just safely remove it.
            field.extensions["user_roles"] = role_symbols  # type: ignore[typeddict-item]  # TODO

    # We need to set up a special role for deploying config settings.
    config_stores = [field for field in fields.values() if field.identifier == ResourceIdentifiers.config_store]
    for store in config_stores:
        keyvalues = [
            f
            for f in fields.values()
            if f.identifier == ResourceIdentifiers.config_setting and f.properties["parent"] == store.symbol
        ]
        if keyvalues:
            _build_role_assignment(
                clean_name("Microsoft.Resources/resourceGroups"),
                "App Configuration Data Owner",
                fields,
                name=store.properties["name"],
                parent=None,
                parameters=parameters,
                symbol=ResourceGroup(),
                principal_id=GLOBAL_PARAMS["principalId"],
                principal_type="User",
            )
