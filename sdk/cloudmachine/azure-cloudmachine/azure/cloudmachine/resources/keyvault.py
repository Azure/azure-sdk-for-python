# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import IO, ClassVar, Dict, List, Optional, Literal, TypedDict, Required
from dataclasses import field
from ._resource import (
    Output,
    UniqueName,
    _serialize_resource,
    Resource,
    LocatedResource,
    dataclass_model,
    generate_symbol,
    _SKIP,
    resolve_value
)


class Permissions(TypedDict, total=False):
    certificates: List[Literal['all', 'backup', 'create', 'delete', 'deleteissuers', 'get', 'getissuers', 'import', 'list', 'listissuers', 'managecontacts', 'manageissuers', 'purge', 'recover', 'restore', 'setissuers', 'update']]
    keys: List[Literal['all', 'backup', 'create', 'decrypt', 'delete', 'encrypt', 'get', 'getrotationpolicy', 'import', 'list', 'purge', 'recover', 'release', 'restore', 'rotate', 'setrotationpolicy', 'sign', 'unwrapKey', 'update', 'verify', 'wrapKey']]
    secrets: List[Literal['all', 'backup', 'delete', 'get', 'list', 'purge', 'recover', 'restore', 'set']]
    storage: List[Literal['all', 'backup', 'delete', 'deletesas', 'get', 'getsas', 'list', 'listsas', 'purge', 'recover', 'regeneratekey', 'restore', 'set', 'setsas', 'update']]


class AccessPolicyEntry(TypedDict, total=False):
    objectId: Required[str]
    permissions: Required[Permissions]
    tenantId: Required[str]
    applicationId: str


class IPRule(TypedDict, total=False):
    value: Required[str]


class VirtualNetworkRule(TypedDict, total=False):
    id: Required[str]
    ignoreMissingVnetServiceEndpoint: bool


class NetworkRuleSet(TypedDict, total=False):
    bypass: Literal['AzureServices', 'None']
    defaultAction: Literal['Allow', 'Deny']
    ipRules: List[IPRule]
    virtualNetworkRules: List[VirtualNetworkRule]


class Sku(TypedDict, total=False):
    family: Required[Literal['A']]
    name: Required[Literal['premium', 'standard']]


class KeyAttributes(TypedDict, total=False):
    enabled: bool
    exp: int
    exportable: bool
    nbf: int


class KeyReleasePolicy(TypedDict, total=False):
    contentType: str
    data: str


class KeyRotationPolicyAttributes(TypedDict, total=False):
    expiryTime: Required[str]


class Action(TypedDict, total=False):
    type: Required[Literal['notify', 'rotate']]


class Trigger(TypedDict, total=False):
    timeAfterCreate: str
    timeBeforeExpiry: str


class LifetimeAction(TypedDict, total=False):
    action: Action
    trigger: Trigger


class RotationPolicy(TypedDict, total=False):
    attributes: KeyRotationPolicyAttributes
    lifetimeActions: List[LifetimeAction]


class KeyProperties(TypedDict, total=False):
    attributes: KeyAttributes
    curveName: Literal['P-256', 'P-256K', 'P-384', 'P-521']
    keyOps: List[Literal['decrypt', 'encrypt', 'import', 'release', 'sign', 'unwrapKey', 'verify', 'wrapKey']]
    keySize: int
    kty: Literal['EC', 'EC-HSM', 'RSA', 'RSA-HSM']
    releasePolicy: KeyReleasePolicy
    rotationPolicy: RotationPolicy


class SecretAttributes(TypedDict, total=False):
    enabled: bool
    exp: int
    nbf: int


class SecretProperties(TypedDict, total=False):
    attributes: SecretAttributes
    contentType: str
    value: str


class VaultAccessPolicyProperties(TypedDict, total=False):
    accessPolicies: Required[List[AccessPolicyEntry]]


@dataclass_model
class KeyVaultAccessPolicy(Resource):
    _resource: ClassVar[Literal['Microsoft.KeyVault/vaults/accessPolicies']] = 'Microsoft.KeyVault/vaults/accessPolicies'
    _version: ClassVar[str] = '2023-07-01'
    _symbolicname: str = field(default_factory=lambda: generate_symbol("keys"), init=False, repr=False)
    name: str = field(default_factory=lambda: UniqueName(prefix="kvkeys", length=24), metadata={'rest': 'name'})
    properties: VaultAccessPolicyProperties = field(metadata={'rest': 'properties'})


@dataclass_model
class KeyVaultKey(Resource):
    _resource: ClassVar[Literal['Microsoft.KeyVault/vaults/keys']] = 'Microsoft.KeyVault/vaults/keys'
    _version: ClassVar[str] = '2023-07-01'
    _symbolicname: str = field(default_factory=lambda: generate_symbol("keys"), init=False, repr=False)
    name: str = field(default_factory=lambda: UniqueName(prefix="kvkey", length=24), metadata={'rest': 'name'})
    tags: Dict[str, str] = field(default_factory=dict, metadata={'rest': 'tags'})
    properties: KeyProperties = field(metadata={'rest': 'properties'})


@dataclass_model
class KeyVaultSecret(Resource):
    _resource: ClassVar[Literal['Microsoft.KeyVault/vaults/secrets']] = 'Microsoft.KeyVault/vaults/secrets'
    _version: ClassVar[str] = '2023-07-01'
    _symbolicname: str = field(default_factory=lambda: generate_symbol("keys"), init=False, repr=False)
    name: str = field(default_factory=lambda: UniqueName(prefix="kvsecret", length=24), metadata={'rest': 'name'})
    tags: Dict[str, str] = field(default_factory=dict, metadata={'rest': 'tags'})
    properties: SecretProperties = field(metadata={'rest': 'properties'})


class VaultProperties(TypedDict, total=False):
    accessPolicies: List[AccessPolicyEntry]
    createMode: Literal['default', 'recover']
    enabledForDeployment: bool
    enabledForDiskEncryption: bool
    enabledForTemplateDeployment: bool
    enablePurgeProtection: bool
    enableRbacAuthorization: bool
    enableSoftDelete: bool
    networkAcls: NetworkRuleSet
    provisioningState: Literal['RegisteringDns', 'Succeeded']
    publicNetworkAccess: str
    sku: Required[Sku]
    softDeleteRetentionInDays: int
    tenantId: Required[str]
    vaultUri: str


@dataclass_model
class KeyVault(LocatedResource):
    properties: VaultProperties = field(metadata={'rest': 'properties'})
    keys: Optional[List[KeyVaultKey]] = field(default_factory=list, metadata={'rest': _SKIP})
    secrets: Optional[List[KeyVaultSecret]] = field(default_factory=list, metadata={'rest': _SKIP})
    access_policies: Optional[List[KeyVaultAccessPolicy]] = field(default_factory=list, metadata={'rest': _SKIP})
    _resource: ClassVar[Literal['Microsoft.KeyVault/vaults']] = 'Microsoft.KeyVault/vaults'
    _version: ClassVar[str] = '2023-07-01'
    _symbolicname: str = field(default_factory=lambda: generate_symbol("keyvault"), init=False, repr=False)

    def write(self, bicep: IO[str]) -> Dict[str, str]:
        _serialize_resource(bicep, self)
        for key in self.keys:
            key._parent = self
            self._outputs.update(key.write(bicep))
        for secret in self.secrets:
            secret._parent = self
            self._outputs.update(secret.write(bicep))
        for policy in self.access_policies:
            policy._scope = self
            self._outputs.update(policy.write(bicep))

        if self._fname:
            output_prefix = self._fname.title()
        else:
            output_prefix = ""
        output_prefix = "Keyvault" + output_prefix
        self._outputs[output_prefix + "VaultEndpoint"] = Output(f"{self._symbolicname}.properties.vaultUri")
        self._outputs[output_prefix + "Name"] = Output(f"{self._symbolicname}.name")
        for key, value in self._outputs.items():
            bicep.write(f"output {key} string = {resolve_value(value)}\n")
        bicep.write("\n")
        return self._outputs
