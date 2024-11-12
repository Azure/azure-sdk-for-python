# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

# pylint: disable=line-too-long, protected-access

from enum import Enum
from typing import IO, Any, ClassVar, Dict, List, Optional, Literal, TypedDict
from dataclasses import field, dataclass
from ._roles import RoleAssignment
from ._identity import UserAssignedIdentities
from ._resource import (
    Output,
    PrincipalId,
    _serialize_resource,
    Resource,
    LocatedResource,
    generate_symbol,
    _UNSET,
    _SKIP,
    GuidName,
    resolve_value,
    BicepBool,
    BicepInt,
    BicepStr
)


class SearchRoleAssignments(Enum):
    INDEX_DATA_CONTRIBUTOR = "8ebe5a00-799e-43f5-93ac-243d3dce84a7"
    INDEX_DATA_READER = "1407120a-92aa-4202-b7e9-c0e197c71c8f"
    SERVICE_CONTRIBUTOR = "7ca78c08-252a-4471-8644-bb5ff32d4ba0"


PrincipalType = Literal['User', 'Group', 'ServicePrincipal', 'Unknown', 'DirectoryRoleTemplate', 'ForeignGroup', 'Application', 'MSI', 'DirectoryObjectOrGroup', 'Everyone']


class Sku(TypedDict):
    # Required
    name: Literal['basic', 'free', 'standard', 'standard2', 'standard3', 'storage_optimized_l1', 'storage_optimized_l2']


class Identity(TypedDict, total=False):
    # Required
    type: Literal['None', 'SystemAssigned', 'SystemAssigned,UserAssigned','UserAssigned']
    userAssignedIdentities: UserAssignedIdentities


class DataPlaneAadOrApiKeyAuthOption(TypedDict):
    aadAuthFailureMode:	Literal['http401WithBearerChallenge', 'http403']


class DataPlaneAuthOptions(TypedDict, total=False):
    aadOrApiKey: DataPlaneAadOrApiKeyAuthOption
    apiKeyOnly: Any


class EncryptionWithCmk(TypedDict):
    enforcement: Literal['Disabled', 'Enabled', 'Unspecified']


class IpRule(TypedDict):
    value: str


class NetworkRuleSet(TypedDict, total=False):
    bypass: Literal['AzurePortal', 'None']
    ipRules: List[IpRule]


class SearchServiceProperties(TypedDict, total=False):
    authOptions: DataPlaneAuthOptions
    disabledDataExfiltrationOptions: List[Literal['All']]
    disableLocalAuth: bool
    encryptionWithCmk: EncryptionWithCmk
    hostingMode: Literal['default', 'highDensity']
    networkRuleSet: NetworkRuleSet
    partitionCount: int
    publicNetworkAccess: Literal['disabled', 'enabled']
    replicaCount: int
    semanticSearch: Literal['disabled', 'free', 'standard']


@dataclass(kw_only=True)
class SearchServices(LocatedResource):
    sku: Sku = field(metadata={'rest': 'sku'})
    identity: Optional[Identity] = field(default=_UNSET, metadata={'rest': 'identity'})
    properties: Optional[SearchServiceProperties] = field(default=_UNSET, metadata={'rest': 'properties'})
    roles: Optional[List[RoleAssignment]] = field(default_factory=list, metadata={'rest': _SKIP})
    _resource: ClassVar[Literal['Microsoft.Search/searchServices']] = 'Microsoft.Search/searchServices'
    _version: ClassVar[str] = '2023-11-01'
    _symbolicname: str = field(default_factory=lambda: generate_symbol("search"), init=False, repr=False)

    def write(self, bicep: IO[str]) -> Dict[str, str]:
        _serialize_resource(bicep, self)
        for role in self.roles:
            role.name = GuidName(self, PrincipalId(), role.properties['roleDefinitionId'])
            role.scope = self
            self._outputs.update(role.write(bicep))

        if self._fname:
            output_prefix = self._fname.title()
        else:
            output_prefix = ""
        output_prefix = "Search" + output_prefix
        self._outputs[output_prefix + "Id"] = Output(f"{self._symbolicname}.id")
        self._outputs[output_prefix + "Name"] = Output(f"{self._symbolicname}.name")
        self._outputs[output_prefix + "Endpoint"] = Output(f"'https://${{{self._symbolicname}.name}}.search.windows.net/'")
        for key, value in self._outputs.items():
            bicep.write(f"output {key} string = {resolve_value(value)}\n")
        bicep.write("\n")
        return self._outputs