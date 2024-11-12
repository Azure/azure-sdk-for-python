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


class AIRoleAssignments(Enum):
    OPENAI_USER = "5e0bd9bd-7b93-4f28-af87-19fc36ad61bd"
    OPENAI_CONTRIBUTOR = "a001fd3d-188f-4b5d-821b-7da978bf7442"
    COGNITIVE_SERVICES_USER = "a97b65f3-24c7-4388-baec-2e87135dc908"

class Identity(TypedDict, total=False):
    # Required
    type: Literal['None', 'SystemAssigned', 'SystemAssigned,UserAssigned','UserAssigned']
    userAssignedIdentities: UserAssignedIdentities


class Sku(TypedDict, total=False):
    capacity: int
    family: str
    # Required
    name: str
    size: str
    tier: Literal['Basic', 'Enterprise', 'Free', 'Premium', 'Standard']


class DeploymentScaleSettings(TypedDict, total=False):
    capacity: int
    scaleType: Literal['Manual', 'Standard']


class DeploymentModel(TypedDict, total=False):
    format: str
    name: str
    source: str
    version: str


class DeploymentProperties(TypedDict, total=False):
    model: DeploymentModel
    raiPolicyName: str
    scaleSettings: DeploymentScaleSettings
    versionUpgradeOption: Literal['NoAutoUpgrade', 'OnceCurrentVersionExpired', 'OnceNewDefaultVersionAvailable']


@dataclass(kw_only=True)
class AiDeployment(Resource):
    _resource: ClassVar[Literal['Microsoft.CognitiveServices/accounts/deployments']] = 'Microsoft.CognitiveServices/accounts/deployments'
    _version: ClassVar[str] = '2023-05-01'
    _symbolicname: str = field(default_factory=lambda: generate_symbol("aidep"), init=False, repr=False)
    name: str = field(metadata={'rest': 'name'})
    properties: DeploymentProperties = field(metadata={'rest': 'properties'})
    sku: Optional[Sku] = field(default=_UNSET, metadata={'rest': 'sku'})

    def write(self, bicep: IO[str]) -> Dict[str, str]:
        _serialize_resource(bicep, self)
        output_prefix = self.parent.kind + self.name.title()
        self._outputs[output_prefix + "Deployment"] = Output(f"{self._symbolicname}.name")
        self._outputs[output_prefix + "Model"] = Output(f"{self._symbolicname}.properties.model.name")
        return self._outputs


@dataclass(kw_only=True)
class CognitiveServices(LocatedResource):
    name: BicepStr = field(metadata={'rest': 'name'})
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
            role.name = GuidName(self, PrincipalId(), role.properties['roleDefinitionId'])
            role.scope = self
            self._outputs.update(role.write(bicep))

        if self._fname:
            output_prefix = self._fname.title()
        else:
            output_prefix = self.kind
        self._outputs[output_prefix + "Endpoint"] = Output(f"{self._symbolicname}.properties.endpoint")
        self._outputs[output_prefix + "Name"] = Output(f"{self._symbolicname}.name")
        self._outputs[output_prefix + "Id"] = Output(f"{self._symbolicname}.id")
        for key, value in self._outputs.items():
            bicep.write(f"output {key} string = {resolve_value(value)}\n")
        bicep.write("\n")
        return self._outputs
