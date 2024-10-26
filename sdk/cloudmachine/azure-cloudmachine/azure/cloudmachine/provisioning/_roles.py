# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import ClassVar, Literal, TypedDict
from dataclasses import field, dataclass

from ._resource import (
    Resource,
    generate_symbol,
    BicepStr
)


class RoleAssignmentProperties(TypedDict, total=False):
    # Required
    principalId: BicepStr
    # Required
    roleDefinitionId: BicepStr
    condition: BicepStr
    conditionVersion: Literal['2.0']
    delegatedManagedIdentityResourceId: BicepStr
    description: BicepStr
    principalType: Literal['Device', 'ForeignGroup', 'Group', 'ServicePrincipal', 'User']


@dataclass(kw_only=True)
class RoleAssignment(Resource):
    name: BicepStr = field(init=False, default="", metadata={'rest': 'name'})
    properties: RoleAssignmentProperties = field(metadata={'rest': 'properties'})
    _resource: ClassVar[Literal['Microsoft.Authorization/roleAssignments']] = 'Microsoft.Authorization/roleAssignments'
    _version: ClassVar[str] = '2022-04-01'
    _symbolicname: str = field(default_factory=lambda: generate_symbol("role"), init=False, repr=False)
