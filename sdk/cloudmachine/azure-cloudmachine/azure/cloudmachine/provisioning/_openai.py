"""
esource openai_CognitiveServicesOpenAIContributor 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(openai.id, principalId, subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'a001fd3d-188f-4b5d-821b-7da978bf7442'))
  properties: {
    principalId: principalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'a001fd3d-188f-4b5d-821b-7da978bf7442')
    principalType: 'User'
  }
  scope: openai
}

resource openai 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: 'cmeefe07f94c22421'
  location: location
  kind: 'OpenAI'
  properties: {
    customSubDomainName: 'cmeefe07f94c22421'
    publicNetworkAccess: 'Enabled'
  }
  sku: {
    name: 'S0'
  }
}

resource openai_deployment 'Microsoft.CognitiveServices/accounts/deployments@2023-05-01' = {
  name: 'cmeefe07f94c22421'
  properties: {
    model: {
      format: 'OpenAI'
      name: 'gpt-35-turbo'
      version: '0125'
    }
  }
  parent: openai
}"""
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

# pylint: disable=line-too-long

from typing import IO, Any, ClassVar, Dict, List, Optional, Literal, TypedDict
from dataclasses import field, dataclass
from enum import Enum

from ._identity import UserAssignedIdentities
from ._roles import RoleAssignment
from ._resource import (
    _UNSET,
    GuidName,
    Output,
    PrincipalId,
    UniqueName,
    _serialize_resource,
    Resource,
    LocatedResource,
    generate_symbol,
    _SKIP,
    resolve_value,
    BicepStr,
    BicepInt,
    BicepBool
)


class OpenAIRoleAssignments(Enum):
    USER = "5e0bd9bd-7b93-4f28-af87-19fc36ad61bd"
    CONTRIBUTOR = "a001fd3d-188f-4b5d-821b-7da978bf7442"

class Identity(TypedDict, total=False):
    # Required
    type: Literal['None', 'SystemAssigned', 'SystemAssigned,UserAssigned','UserAssigned']
    userAssignedIdentities: UserAssignedIdentities


@dataclass(kw_only=True)
class AiDeployment(Resource):
    _resource: ClassVar[Literal['Microsoft.CognitiveServices/accounts/deployments']] = 'Microsoft.CognitiveServices/accounts/deployments'
    _version: ClassVar[str] = '2023-05-01'
    _symbolicname: str = field(default_factory=lambda: generate_symbol("aidep"), init=False, repr=False)
    properties: Dict[str, Any] = field(metadata={'rest': 'properties'})
    sku: Optional[Dict[str, Any]] = field(default=_UNSET, metadata={'rest': 'sku'})


@dataclass(kw_only=True)
class CognitiveServices(LocatedResource):
    kind: str = field(metadata={'rest': 'kind'})
    properties: Dict[str, Any] = field(metadata={'rest': 'properties'})
    sku: Dict[str, Any] = field(metadata={'rest': 'sku'})
    identity: Optional[Identity] = field(default=_UNSET, metadata={'rest': 'identity'})
    roles: Optional[List[RoleAssignment]] = field(default_factory=list, metadata={'rest': _SKIP})
    deployments: Optional[List[AiDeployment]] = field(default_factory=list, metadata={'rest': _SKIP})
    _resource: ClassVar[Literal['Microsoft.CognitiveServices/accounts']] = 'Microsoft.CognitiveServices/accounts'
    _version: ClassVar[str] = '2023-05-01'
    _symbolicname: str = field(default_factory=lambda: generate_symbol("cogservices"), init=False, repr=False)

    def write(self, bicep: IO[str]) -> Dict[str, str]:
        _serialize_resource(bicep, self)
        for deployment in self.deployments:
            deployment.parent = self
            self._outputs.update(deployment.write(bicep))

        for role in self.roles:
            role.name = GuidName(self, PrincipalId(), role.properties.role_definition_id)
            role.scope = self
            self._outputs.update(role.write(bicep))

        if self._fname:
            output_prefix = self._fname.title()
        else:
            output_prefix = ""
        output_prefix = "Ai" + output_prefix
        self._outputs[output_prefix + "VaultEndpoint"] = Output(f"{self._symbolicname}.properties.vaultUri")
        self._outputs[output_prefix + "Name"] = Output(f"{self._symbolicname}.name")
        for key, value in self._outputs.items():
            bicep.write(f"output {key} string = {resolve_value(value)}\n")
        bicep.write("\n")
        return self._outputs