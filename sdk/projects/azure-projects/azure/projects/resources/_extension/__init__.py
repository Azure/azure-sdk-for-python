# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Dict, List, Literal, Any, TypedDict, Union, TYPE_CHECKING
from typing_extensions import Required

from .roles import RoleAssignment as RoleResource, BUILT_IN_ROLES
from ..._bicep.expressions import Parameter, ResourceSymbol, Expression, Guid
from ..._bicep.utils import clean_name

if TYPE_CHECKING:
    from ..._resource import FieldsType


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


def convert_managed_identities(managed_identities: ManagedIdentity) -> Identity:
    identity: Identity = {"type": "None", "userAssignedIdentities": {}}
    user_assigned_identities = managed_identities.get("userAssignedResourceIds", [])
    if managed_identities.get("systemAssigned", False):
        if user_assigned_identities:
            identity["type"] = "SystemAssigned,UserAssigned"
            for uai in user_assigned_identities:
                identity["userAssignedIdentities"][uai] = {}
        else:
            identity["type"] = "SystemAssigned"
    elif user_assigned_identities:
        identity["type"] = "UserAssigned"
        for uai in user_assigned_identities:
            identity["userAssignedIdentities"][uai] = {}
    return identity


def _build_role_assignment(
    resource: str,
    role: Union[str, RoleAssignment],
    fields: "FieldsType",
    name: Union[str, Parameter],
    *,
    parameters: Dict[str, Parameter],
    symbol: ResourceSymbol,
    principal_id: Expression,
    principal_type: Literal["ServicePrincipal", "User"]
) -> ResourceSymbol:
    if isinstance(role, str):
        new_role = RoleResource(
            {
                "name": Guid(resource, name, principal_type, role),
                "properties": {
                    "principalId": principal_id,
                    "principalType": principal_type,
                    "roleDefinitionId": BUILT_IN_ROLES.get(role, role),
                },
                "scope": symbol,
            }
        )
        return new_role.__bicep__(fields, parameters=parameters)[0]
    new_role = RoleResource(
        {
            "name": role.get("name", Guid(resource, name, role["principalId"], role["roleDefinitionIdOrName"])),
            "properties": {
                "condition": role.get("condition"),
                "conditionVersion": role.get("conditionVersion"),
                "delegatedManagedIdentityResourceId": role.get("delegatedManagedIdentityResourceId"),
                "description": role.get("description"),
                "principalId": role["principalId"],
                "principalType": role["principalType"],
                "roleDefinitionId": BUILT_IN_ROLES.get(role["roleDefinitionIdOrName"], role["roleDefinitionIdOrName"]),
            },
            "scope": symbol,
        }
    )
    return new_role.__bicep__(fields, parameters=parameters)[0]


def add_extensions(fields: "FieldsType", parameters: Dict[str, "Parameter"]):
    for field in list(fields.values()):
        if parameters.get("managedIdentityPrincipalId"):
            role_symbols = []
            for role in field.extensions.get("managed_identity_roles", []):
                role_symbols.append(
                    _build_role_assignment(
                        clean_name(field.resource),
                        role,
                        fields,
                        field.properties["name"],
                        parameters=parameters,
                        symbol=field.symbol,
                        principal_id=parameters["managedIdentityPrincipalId"],
                        principal_type="ServicePrincipal",
                    )
                )
            field.extensions["managed_identity_roles"] = role_symbols
        if parameters.get("principalId"):
            role_symbols = []
            for role in field.extensions.get("user_roles", []):
                role_symbols.append(
                    _build_role_assignment(
                        clean_name(field.resource),
                        role,
                        fields,
                        field.properties["name"],
                        parameters=parameters,
                        symbol=field.symbol,
                        principal_id=parameters["principalId"],
                        principal_type="User",
                    )
                )
            field.extensions["user_roles"] = role_symbols
