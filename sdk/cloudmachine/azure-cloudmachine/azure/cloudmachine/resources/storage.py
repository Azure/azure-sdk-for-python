# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from enum import Enum
from typing import IO, ClassVar, List, Optional, Literal
from dataclasses import field
from .roles import RoleAssignment
from .identity import UserAssignedIdentities
from ._resource import (
    PrincipalId,
    _serialize_resource,
    Resource,
    LocatedResource,
    dataclass_model,
    generate_symbol,
    _UNSET,
    _SKIP,
    GuidName
)


class StorageRoleAssignments(Enum):
    BLOB_DATA_CONTRIBUTOR = "ba92f5b4-2d11-453d-a403-e96b0029c9fe"
    TABLE_DATA_CONTRIBUTOR = "0a9a7e1f-b9d0-4cc4-a60d-0319b160aaa3"

PrincipalType = Literal['User', 'Group', 'ServicePrincipal', 'Unknown', 'DirectoryRoleTemplate', 'ForeignGroup', 'Application', 'MSI', 'DirectoryObjectOrGroup', 'Everyone']

@dataclass_model
class Sku:
    name: Literal['Premium_LRS', 'Premium_ZRS', 'Standard_GRS', 'Standard_GZRS', 'Standard_LRS', 'Standard_RAGRS', 'Standard_RAGZRS', 'Standard_ZRS'] = field(metadata={'rest': 'name'})


@dataclass_model
class ExtendedLocation:
    name: str = field(metadata={'rest': 'name'})
    type: str = field(default='EdgeZone', metadata={'rest': 'type'})


@dataclass_model
class Identity:
    type: Literal['None', 'SystemAssigned', 'SystemAssigned,UserAssigned','UserAssigned'] = field(metadata={'rest': 'type'})
    user_assigned_identities: Optional[UserAssignedIdentities] = field(default=_UNSET, metadata={'rest': 'userAssignedIdentities'})


@dataclass_model
class ActiveDirectoryProperties:
    domain_guid: str = field(metadata={'rest': 'domainGuid'})
    domain_name: str = field(metadata={'rest': 'domainName'})
    account_type: Literal['Computer', 'User'] = field(metadata={'rest': 'accountType'})
    azure_storage_sid: Optional[str] = field(default=_UNSET, metadata={'rest': 'azureStorageSid'})
    domain_sid: Optional[str] = field(default=_UNSET, metadata={'rest': 'domainSid'})
    forest_name: Optional[str] = field(default=_UNSET, metadata={'rest': 'forestName'})
    net_bios_domain_name: Optional[str] = field(default=_UNSET, metadata={'rest': 'netBiosDomainName'})
    sam_account_name: Optional[str] = field(default=_UNSET, metadata={'rest': 'samAccountName'})


@dataclass_model
class AzureFilesIdentityBasedAuthentication:
    active_directory_properties: Optional[ActiveDirectoryProperties] = field(default=_UNSET, metadata={'rest': 'activeDirectoryProperties'})
    default_share_permission: Optional[Literal['StorageFileDataSmbShareContributor', 'StorageFileDataSmbShareElevatedContributor', 'StorageFileDataSmbShareReader']] = field(default=_UNSET, metadata={'rest': 'defaultSharePermission'})
    directory_service_options: Literal['AADKERB', 'AD', 'None'] = field(metadata={'rest': 'directoryServiceOptions'})


@dataclass_model
class CustomDomain:
    name: str = field(metadata={'rest': 'name'})
    use_sub_domain_name: Optional[bool] = field(default=_UNSET, metadata={'rest': 'useSubDomainName'})


@dataclass_model
class EncryptionIdentity:
    federated_identity_client_id: Optional[str] = field(default=_UNSET, metadata={'rest': 'federatedIdentityClientId'})
    user_assigned_identity: Optional[str] = field(default=_UNSET, metadata={'rest': 'userAssignedIdentity'})


@dataclass_model
class KeyVaultProperties:
    keyname: Optional[str] = field(default=_UNSET, metadata={'rest': 'keyname'})
    keyvaulturi: Optional[str] = field(default=_UNSET, metadata={'rest': 'keyvaulturi'})
    keyversion: Optional[str] = field(default=_UNSET, metadata={'rest': 'keyversion'})


@dataclass_model
class EncryptionService:
    enabled: Optional[bool] = field(default=_UNSET, metadata={'rest': 'enabled'})
    key_type: Optional[Literal['Account', 'Service']] = field(default=_UNSET, metadata={'rest': 'keyType'})


@dataclass_model
class EncryptionServices:
    blob: Optional[EncryptionService] = field(default=_UNSET, metadata={'rest': 'blob'})
    file: Optional[EncryptionService] = field(default=_UNSET, metadata={'rest': 'file'})
    queue: Optional[EncryptionService] = field(default=_UNSET, metadata={'rest': 'queue'})
    table: Optional[EncryptionService] = field(default=_UNSET, metadata={'rest': 'table'})


@dataclass_model
class Encryption:
    identity: Optional[EncryptionIdentity] = field(default=_UNSET, metadata={'rest': 'identity'})
    key_source: Optional[Literal['Microsoft.Keyvault', 'Microsoft.Storage']] = field(default=_UNSET, metadata={'rest': 'keySource'})
    keyvault_properties: Optional[KeyVaultProperties] = field(default=_UNSET, metadata={'rest': 'keyvaultProperties'})
    require_infrastructure_encryption: Optional[bool] = field(default=_UNSET, metadata={'rest': 'requireInfrastructureEncryption'})
    services: Optional[EncryptionServices] = field(default=_UNSET, metadata={'rest': 'services'})


@dataclass_model
class AccountImmutabilityPolicyProperties:
    allow_protected_append_writes: Optional[bool] = field(default=_UNSET, metadata={'rest': 'allowProtectedAppendWrites'})
    immutability_period_since_creation_in_days: Optional[int] = field(default=_UNSET, metadata={'rest': 'immutabilityPeriodSinceCreationInDays'})
    state: Optional[Literal['Disabled', 'Locked', 'Unlocked']] = field(default=_UNSET, metadata={'rest': 'state'})


@dataclass_model
class ImmutableStorageAccount:
    enabled: Optional[bool] = field(default=_UNSET, metadata={'rest': 'enabled'})
    immutability_policy: Optional[AccountImmutabilityPolicyProperties] = field(default=_UNSET, metadata={'rest': 'immutabilityPolicy'})


@dataclass_model
class KeyPolicy:
    key_expiration_period_in_days: int = field(metadata={'rest': 'keyExpirationPeriodInDays'})


@dataclass_model
class IPRule:
    action: Optional[Literal['Allow']] = field(default=_UNSET, metadata={'rest': 'action'})
    value: str = field(metadata={'rest': 'value'})


@dataclass_model
class ResourceAccessRule:
    resource_id: str = field(metadata={'rest': 'resourceId'})
    tenant_id: str = field(metadata={'rest': 'tenantId'})


@dataclass_model
class VirtualNetworkRule:
    action: Optional[Literal['Allow']] = field(default=_UNSET, metadata={'rest': 'action'})
    id: str = field(metadata={'rest': 'id'})


@dataclass_model
class NetworkRuleSet:
    bypass: Optional[Literal['AzureServices', 'Logging', 'Metrics', 'None']] = field(default=_UNSET, metadata={'rest': 'bypass'})
    default_action: Literal['Allow', 'Deny'] = field(metadata={'rest': 'defaultAction'})
    ip_rules: Optional[List[IPRule]] = field(default=_UNSET, metadata={'rest': 'ipRules'})
    resource_access_rules: Optional[List[ResourceAccessRule]] = field(default=_UNSET, metadata={'rest': 'resourceAccessRules'})
    virtual_network_rules: Optional[List[VirtualNetworkRule]] = field(default=_UNSET, metadata={'rest': 'virtualNetworkRules'})


@dataclass_model
class RoutingPreference:
    publish_internet_endpoints: Optional[bool] = field(default=_UNSET, metadata={'rest': 'publishInternetEndpoints'})
    publish_microsoft_endpoints: Optional[bool] = field(default=_UNSET, metadata={'rest': 'publishMicrosoftEndpoints'})
    routing_choice: Optional[Literal['InternetRouting', 'MicrosoftRouting']] = field(default=_UNSET, metadata={'rest': 'routingChoice'})


@dataclass_model
class SasPolicy:
    expiration_action: Literal["Log"] = field(metadata={'rest': 'expirationAction'})
    sas_expiration_period: str = field(metadata={'rest': 'sasExpirationPeriod'})


@dataclass_model
class Properties:
    access_tier: Optional[Literal["Hot", "Cool", "Premium"]] = field(default=_UNSET, metadata={'rest': 'accessTier'})
    allow_blob_public_access: Optional[bool] = field(default=_UNSET, metadata={'rest': 'allowBlobPublicAccess'})
    allow_cross_tenant_replication: Optional[bool] = field(default=_UNSET, metadata={'rest': 'allowCrossTenantReplication'})
    allowed_copy_scope: Optional[Literal['AAD','PrivateLink']] = field(default=_UNSET, metadata={'rest': 'allowedCopyScope'})
    allow_shared_key_access: Optional[bool] = field(default=_UNSET, metadata={'rest': 'allowSharedKeyAccess'})
    custom_domain: Optional[CustomDomain] = field(default=_UNSET, metadata={'rest': 'customDomain'})
    default_to_oauth_authentication: Optional[bool] = field(default=_UNSET, metadata={'rest': 'defaultToOAuthAuthentication'})
    dns_endpoint_type: Optional[Literal['AzureDnsZone', 'Standard']] = field(default=_UNSET, metadata={'rest': 'dnsEndpointType'})
    immutable_storage_with_versioning: Optional[ImmutableStorageAccount] = field(default=_UNSET, metadata={'rest': 'immutableStorageWithVersioning'})
    is_hns_enabled: Optional[bool] = field(default=_UNSET, metadata={'rest': 'isHnsEnabled'})
    is_local_user_enabled: Optional[bool] = field(default=_UNSET, metadata={'rest': 'isLocalUserEnabled'})
    is_nfsv3_enabled: Optional[bool] = field(default=_UNSET, metadata={'rest': 'isNfsV3Enabled'})
    is_sftp_enabled: Optional[bool] = field(default=_UNSET, metadata={'rest': 'isSftpEnabled'})
    key_policy: Optional[KeyPolicy] = field(default=_UNSET, metadata={'rest': 'keyPolicy'})
    large_file_shares_state: Optional[Literal['Disabled', 'Enabled']] = field(default=_UNSET, metadata={'rest': 'largeFileSharesState'})
    minimum_tls_version: Optional[Literal['TLS1_0', 'TLS1_1', 'TLS1_2']] = field(default=_UNSET, metadata={'rest': 'minimumTlsVersion'})
    network_acls: Optional[NetworkRuleSet] = field(default=_UNSET, metadata={'rest': 'networkAcls'})
    public_network_access: Optional[Literal['Disabled', 'Enabled']] = field(default=_UNSET, metadata={'rest': 'publicNetworkAccess'})
    routing_preference: Optional[RoutingPreference] = field(default=_UNSET, metadata={'rest': 'routingPreference'})
    sas_policy: Optional[SasPolicy] = field(default=_UNSET, metadata={'rest': 'sasPolicy'})
    supports_https_traffic_only: Optional[bool] = field(default=_UNSET, metadata={'rest': 'supportsHttpsTrafficOnly'})


@dataclass_model
class Container(Resource):
    name: str = field(metadata={'rest': 'name'})
    _resource: ClassVar[Literal['Microsoft.Storage/storageAccounts/blobServices/containers']] = 'Microsoft.Storage/storageAccounts/blobServices/containers'
    _version: ClassVar[str] = '2023-01-01'
    _symbolicname: str = field(default_factory=lambda: generate_symbol("container"), init=False, repr=False)


@dataclass_model
class Table(Resource):
    name: str = field(metadata={'rest': 'name'})
    _resource: ClassVar[Literal['Microsoft.Storage/storageAccounts/tableServices/tables']] = 'Microsoft.Storage/storageAccounts/tableServices/tables'
    _version: ClassVar[str] = '2023-05-01'
    _symbolicname: str = field(default_factory=lambda: generate_symbol("table"), init=False, repr=False)


@dataclass_model
class BlobServices(Resource):
    _resource: ClassVar[Literal['Microsoft.Storage/storageAccounts/blobServices']] = 'Microsoft.Storage/storageAccounts/blobServices'
    _version: ClassVar[str] = '2023-01-01'
    _symbolicname: str = field(default_factory=lambda: generate_symbol("blobs"), init=False, repr=False)
    name: str = field(init=False, default="default", metadata={'rest': 'name'})
    containers: List[Container] = field(default_factory=list, metadata={'rest': _SKIP})

    def write(self, bicep: IO[str]) -> None:
        _serialize_resource(bicep, self)
        for container in self.containers:
            container._parent = self
            container.write(bicep)


@dataclass_model
class TableServices(Resource):
    _resource: ClassVar[Literal['Microsoft.Storage/storageAccounts/tableServices']] = 'Microsoft.Storage/storageAccounts/tableServices'
    _version: ClassVar[str] = '2023-05-01'
    _symbolicname: str = field(default_factory=lambda: generate_symbol("tables"), init=False, repr=False)
    name: str = field(init=False, default="default", metadata={'rest': 'name'})
    tables: List[Container] = field(default_factory=list, metadata={'rest': _SKIP})

    def write(self, bicep: IO[str]) -> None:
        _serialize_resource(bicep, self)
        for table in self.tables:
            table._parent = self
            table.write(bicep)


@dataclass_model
class StorageAccount(LocatedResource):
    sku: Sku = field(metadata={'rest': 'sku'})
    kind: str = field(metadata={'rest': 'kind'})
    extended_location : Optional[ExtendedLocation] = field(default=_UNSET, metadata={'rest': 'extendedLocation'})
    identity: Optional[Identity] = field(default=_UNSET, metadata={'rest': 'identity'})
    properties: Optional[Properties] = field(default=_UNSET, metadata={'rest': 'properties'})
    blobs: Optional[BlobServices] = field(default=None, metadata={'rest': _SKIP})
    tables: Optional[TableServices] = field(default=None, metadata={'rest': _SKIP})
    roles: Optional[List[RoleAssignment]] = field(default_factory=list, metadata={'rest': _SKIP})
    _resource: ClassVar[Literal['Microsoft.Storage/storageAccounts']] = 'Microsoft.Storage/storageAccounts'
    _version: ClassVar[str] = '2023-01-01'
    _symbolicname: str = field(default_factory=lambda: generate_symbol("storage"), init=False, repr=False)

    def write(self, bicep: IO[str]) -> None:
        _serialize_resource(bicep, self)
        if self.blobs:
            self.blobs._parent = self
            self.blobs.write(bicep)
        if self.tables:
           self.tables._parent = self
           self.tables.write(bicep)
        for role in self.roles:
            role.name = GuidName(self, PrincipalId(), role.properties.role_definition_id)
            role._scope = self
            role.write(bicep)

        if self._fname:
            output_prefix = self._fname.title()
        else:
            output_prefix = ""

        output_prefix = "Storage" + output_prefix
        self._outputs.append(output_prefix + 'Id')
        bicep.write(f"output {output_prefix}Id string = {self._symbolicname}.id\n")
        self._outputs.append(output_prefix + 'Name')
        bicep.write(f"output {output_prefix}Name string = {self._symbolicname}.name\n")
        if self.blobs:
            output_name = output_prefix + "BlobEndpoint"
            self._outputs.append(output_name)
            bicep.write(f"output {output_name} string = {self._symbolicname}.properties.primaryEndpoints.blob\n")
        if self.tables:
            output_name = output_prefix + "TableEndpoint"
            self._outputs.append(output_name)
            bicep.write(f"output {output_name} string = {self._symbolicname}.properties.primaryEndpoints.table\n\n")
