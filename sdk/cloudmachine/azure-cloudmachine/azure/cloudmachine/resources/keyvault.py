# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from enum import Enum
from typing import IO, ClassVar, Dict, List, Optional, Literal
from dataclasses import field
from .roles import RoleAssignment
from .identity import UserAssignedIdentities
from ._resource import (
    PrincipalId,
    ResourceId,
    UniqueName,
    _serialize_resource,
    Resource,
    LocatedResource,
    dataclass_model,
    generate_symbol,
    _UNSET,
    _SKIP,
    GuidName
)


@dataclass_model
class Permissions:
    certificates: Optional[List[Literal['all', 'backup', 'create', 'delete', 'deleteissuers', 'get', 'getissuers', 'import', 'list', 'listissuers', 'managecontacts', 'manageissuers', 'purge', 'recover', 'restore', 'setissuers', 'update']]] = field(default=_UNSET, metadata={'rest': 'certificates'})
    keys: Optional[List[Literal['all', 'backup', 'create', 'decrypt', 'delete', 'encrypt', 'get', 'getrotationpolicy', 'import', 'list', 'purge', 'recover', 'release', 'restore', 'rotate', 'setrotationpolicy', 'sign', 'unwrapKey', 'update', 'verify', 'wrapKey']]] = field(default=_UNSET, metadata={'rest': 'keys'})
    secrets: Optional[List[Literal['all', 'backup', 'delete', 'get', 'list', 'purge', 'recover', 'restore', 'set']]] = field(default=_UNSET, metadata={'rest': 'secrets'})
    storage: Optional[List[Literal['all', 'backup', 'delete', 'deletesas', 'get', 'getsas', 'list', 'listsas', 'purge', 'recover', 'regeneratekey', 'restore', 'set', 'setsas', 'update']]] = field(default=_UNSET, metadata={'rest': 'storage'})


@dataclass_model
class AccessPolicyEntry:
    object_id: str = field(metadata={'rest': 'objectId'})
    permissions: Permissions = field(metadata={'rest': 'permissions'})
    tenant_id: str = field(metadata={'rest': 'tenantId'})
    application_id: Optional[str] = field(default=_UNSET, metadata={'rest': 'applicationId'})


@dataclass_model
class IPRule:
    value: str = field(metadata={'rest': 'value'})


@dataclass_model
class VirtualNetworkRule:
    id: ResourceId = field(metadata={'rest': 'id'})
    ignore_missing_vnet_service_endpoint: Optional[bool] = field(default=_UNSET, metadata={'rest': 'ignoreMissingVnetServiceEndpoint'})

@dataclass_model
class NetworkRuleSet:
    bypass: Optional[Literal['AzureServices', 'None']] = field(default=_UNSET, metadata={'rest': 'bypass'})
    default_action: Optional[Literal['Allow', 'Deny']] = field(default=_UNSET, metadata={'rest': 'defaultAction'})
    ip_rules: Optional[List[IPRule]] = field(default=_UNSET, metadata={'rest': 'ipRules'})
    virtual_network_rules: Optional[List[VirtualNetworkRule]] = field(default=_UNSET, metadata={'rest': 'virtualNetworkRules'})

@dataclass_model
class Sku:
    family: Literal['A'] = field(metadata={'rest': 'family'})
    name: Literal['premium', 'standard'] = field(metadata={'rest': 'name'})


@dataclass_model
class KeyAttributes:
    enabled: Optional[bool] = field(default=_UNSET, metadata={'rest': 'enabled'})
    exp: Optional[int] = field(default=_UNSET, metadata={'rest': 'exp'})
    exportable: Optional[bool] = field(default=_UNSET, metadata={'rest': 'exportable'})
    nbf: Optional[int] = field(default=_UNSET, metadata={'rest': 'nbf'})


@dataclass_model
class KeyReleasePolicy:
    content_type: Optional[str] = field(default=_UNSET, metadata={'rest': 'contentType'})
    data: Optional[str] = field(default=_UNSET, metadata={'rest': 'data'})


@dataclass_model
class KeyRotationPolicyAttributes:
    expiry_time: str = field(metadata={'rest': 'expiryTime'})


@dataclass_model
class Action:
    type: Literal['notify', 'rotate'] = field(metadata={'rest': 'type'})


@dataclass_model
class Trigger:
    time_after_create: Optional[str] = field(default=_UNSET, metadata={'rest': 'timeAfterCreate'})
    time_before_expiry: Optional[str] = field(default=_UNSET, metadata={'rest': 'timeBeforeExpiry'})


@dataclass_model
class LifetimeAction:
    action: Optional[Action] = field(default=_UNSET, metadata={'rest': 'action'})
    trigger: Optional[Trigger] = field(default=_UNSET, metadata={'rest': 'trigger'})


@dataclass_model
class RotationPolicy:
    attributes: Optional[KeyRotationPolicyAttributes] = field(default=_UNSET, metadata={'rest': 'attributes'})
    lifetime_actions: Optional[List[LifetimeAction]] = field(default=_UNSET, metadata={'rest': 'lifetimeActions'})


@dataclass_model
class KeyProperties:
    attributes: Optional[KeyAttributes] = field(default=_UNSET, metadata={'rest': 'attributes'})
    curve_name: Optional[Literal['P-256', 'P-256K', 'P-384', 'P-521']] = field(default=_UNSET, metadata={'rest': 'curveName'})
    key_ops: Optional[List[Literal['decrypt', 'encrypt', 'import', 'release', 'sign', 'unwrapKey', 'verify', 'wrapKey']]] = field(default=_UNSET, metadata={'rest': 'keyOps'})
    key_size: Optional[int] = field(default=_UNSET, metadata={'rest': 'keySize'})
    kty: Optional[Literal['EC', 'EC-HSM', 'RSA', 'RSA-HSM']] = field(default=_UNSET, metadata={'rest': 'kty'})
    release_policy: Optional[KeyReleasePolicy] = field(default=_UNSET, metadata={'rest': 'releasePolicy'})
    rotation_policy: Optional[RotationPolicy] = field(default=_UNSET, metadata={'rest': 'rotationPolicy'})


@dataclass_model
class SecretAttributes:
    enabled: Optional[bool] = field(default=_UNSET, metadata={'rest': 'enabled'})
    exp: Optional[int] = field(default=_UNSET, metadata={'rest': 'exp'})
    nbf: Optional[int] = field(default=_UNSET, metadata={'rest': 'nbf'})


@dataclass_model
class SecretProperties:
    attributes: Optional[SecretAttributes] = field(default=_UNSET, metadata={'rest': 'attributes'})
    content_type: Optional[str] = field(default=_UNSET, metadata={'rest': 'contentType'})
    value: Optional[str] = field(default=_UNSET, metadata={'rest': 'value'})


@dataclass_model
class VaultAccessPolicyProperties:
    access_policies: List[AccessPolicyEntry] = field(metadata={'rest': 'accessPolicies'})


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


@dataclass_model
class VaultProperties:
    access_policies: Optional[List[AccessPolicyEntry]] = field(default=_UNSET, metadata={'rest': 'accessPolicies'})
    create_mode: Optional[Literal['default', 'recover']] = field(default=_UNSET, metadata={'rest': 'createMode'})
    enabled_for_deployment: Optional[bool] = field(default=_UNSET, metadata={'rest': 'enabledForDeployment'})
    enabled_for_disk_encryption: Optional[bool] = field(default=_UNSET, metadata={'rest': 'enabledForDiskEncryption'})
    enabled_for_template_deployment: Optional[bool] = field(default=_UNSET, metadata={'rest': 'enabledForTemplateDeployment'})
    enable_purge_protection: Optional[bool] = field(default=_UNSET, metadata={'rest': 'enablePurgeProtection'})
    enable_rbac_authorization: Optional[bool] = field(default=_UNSET, metadata={'rest': 'enableRbacAuthorization'})
    enable_soft_delete: Optional[bool] = field(default=_UNSET, metadata={'rest': 'enableSoftDelete'})
    network_acls: Optional[NetworkRuleSet] = field(default=_UNSET, metadata={'rest': 'networkAcls'})
    provisioning_state: Optional[Literal['RegisteringDns', 'Succeeded']] = field(default=_UNSET, metadata={'rest': 'provisioningState'})
    public_network_access: Optional[str] = field(default=_UNSET, metadata={'rest': 'publicNetworkAccess'})
    sku: Sku = field(metadata={'rest': 'sku'})
    soft_delete_retention_in_days: Optional[int] = field(default=_UNSET, metadata={'rest': 'softDeleteRetentionInDays'})
    tenant_id: str = field(metadata={'rest': 'tenantId'})
    vault_uri: Optional[str] = field(default=_UNSET, metadata={'rest': 'vaultUri'})


@dataclass_model
class KeyVault(LocatedResource):
    properties: VaultProperties = field(metadata={'rest': 'properties'})
    keys: Optional[List[KeyVaultKey]] = field(default_factory=list, metadata={'rest': _SKIP})
    secrets: Optional[List[KeyVaultSecret]] = field(default_factory=list, metadata={'rest': _SKIP})
    access_policies: Optional[List[KeyVaultAccessPolicy]] = field(default_factory=list, metadata={'rest': _SKIP})
    _resource: ClassVar[Literal['Microsoft.KeyVault/vaults']] = 'Microsoft.KeyVault/vaults'
    _version: ClassVar[str] = '2023-07-01'
    _symbolicname: str = field(default_factory=lambda: generate_symbol("keyvault"), init=False, repr=False)

    def write(self, bicep: IO[str]) -> None:
        _serialize_resource(bicep, self)
        for key in self.keys:
            key._parent = self
            key.write(bicep)
        for secret in self.secrets:
            secret._parent = self
            secret.write(bicep)
        for policy in self.access_policies:
            policy._scope = self
            policy.write(bicep)

        if self._fname:
            output_prefix = self._fname.title()
        else:
            output_prefix = ""
        output_prefix = "Keyvault" + output_prefix
        self._outputs.append(output_prefix + 'Name')
        bicep.write(f"output {output_prefix}Name string = {self._symbolicname}.name\n")
        output_name = output_prefix + "VaultEndpoint"
        self._outputs.append(output_name)
        bicep.write(f"output {output_name} string = {self._symbolicname}.properties.vaultUri\n\n")
