# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=line-too-long

from typing import Literal, TypedDict, Union
from typing_extensions import Required

from ...._bicep.expressions import Parameter, ResourceSymbol, Output

RESOURCE = "Microsoft.Authorization/roleAssignments"
VERSION = "2022-04-01"


class RoleAssignmentProperties(TypedDict, total=False):
    condition: Union[str, Parameter]
    """The conditions on the role assignment. This limits the resources it can be assigned to. e.g.: @Resource[Microsoft.Storage/storageAccounts/blobServices/containers:ContainerName] StringEqualsIgnoreCase 'foo_storage_container'."""
    conditionVersion: Literal["2.0"]
    """Version of the condition. Currently the only accepted value is '2.0'."""
    delegatedManagedIdentityResourceId: Union[str, Parameter, Output]
    """Id of the delegated managed identity resource."""
    description: Union[str, Parameter]
    """Description of role assignment."""
    principalId: Required[Union[str, Parameter]]
    """The principal ID."""
    principalType: Required[Union[Literal["Device", "ForeignGroup", "Group", "ServicePrincipal", "User"], Parameter]]
    """The principal type of the assigned principal ID."""
    roleDefinitionId: Required[Union[str, Parameter]]
    """The role definition ID."""


class RoleAssignmentResource(TypedDict, total=False):
    name: Required[Union[str, Parameter]]
    """The resource name"""
    properties: Required[RoleAssignmentProperties]
    """Role assignment properties."""
    scope: ResourceSymbol
    """Use when creating a resource at a scope that is different than the deployment scope."""
