# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

# pylint: disable=line-too-long, protected-access

from enum import Enum
from typing import IO, ClassVar, Dict, List, Optional, Literal, TypedDict
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


class StorageRoleAssignments(Enum):
    BLOB_DATA_CONTRIBUTOR = "ba92f5b4-2d11-453d-a403-e96b0029c9fe"
    BLOB_DATA_READER = "2a2b9908-6ea1-4ae2-8e65-a410df84e7d1"
    TABLE_DATA_CONTRIBUTOR = "0a9a7e1f-b9d0-4cc4-a60d-0319b160aaa3"


PrincipalType = Literal['User', 'Group', 'ServicePrincipal', 'Unknown', 'DirectoryRoleTemplate', 'ForeignGroup', 'Application', 'MSI', 'DirectoryObjectOrGroup', 'Everyone']


class Sku(TypedDict):
    # Required
    name: Literal['Premium_LRS', 'Premium_ZRS', 'Standard_GRS', 'Standard_GZRS', 'Standard_LRS', 'Standard_RAGRS', 'Standard_RAGZRS', 'Standard_ZRS']


class ExtendedLocation(TypedDict):
    # Required
    name: BicepStr
    # Required
    type: Literal['EdgeZone']


class Identity(TypedDict, total=False):
    # Required
    type: Literal['None', 'SystemAssigned', 'SystemAssigned,UserAssigned','UserAssigned']
    userAssignedIdentities: UserAssignedIdentities


class ActiveDirectoryProperties(TypedDict, total=False):
    # Required
    domainGuid: BicepStr
    # Required
    domainName: BicepStr
    # Required
    accountType: Literal['Computer', 'User']
    azureStorageSid: BicepStr
    domainSid: BicepStr
    forestName: BicepStr
    netBiosDomainName: BicepStr
    samAccountName: BicepStr


class AzureFilesIdentityBasedAuthentication(TypedDict, total=False):
    activeDirectoryProperties: ActiveDirectoryProperties
    defaultSharePermission: Literal['StorageFileDataSmbShareContributor', 'StorageFileDataSmbShareElevatedContributor', 'StorageFileDataSmbShareReader']
    # Required
    directoryServiceOptions: Literal['AADKERB', 'AD', 'None']


class CustomDomain(TypedDict, total=False):
    # Required
    name: BicepStr
    useSubDomainName: BicepBool


class EncryptionIdentity(TypedDict, total=False):
    federatedIdentityClientId: BicepStr
    userAssignedIdentity: BicepStr


class KeyVaultProperties(TypedDict, total=False):
    keyname: BicepStr
    keyvaulturi: BicepStr
    keyversion: BicepStr


class EncryptionService(TypedDict, total=False):
    enabled: BicepBool
    keyType: Literal['Account', 'Service']


class EncryptionServices(TypedDict, total=False):
    blob: EncryptionService
    file: EncryptionService
    queue: EncryptionService
    table: EncryptionService


class Encryption(TypedDict, total=False):
    identity: EncryptionIdentity
    keySource: Literal['Microsoft.Keyvault', 'Microsoft.Storage']
    keyvaultProperties: KeyVaultProperties
    requireInfrastructureEncryption: BicepBool
    services: EncryptionServices


class AccountImmutabilityPolicyProperties(TypedDict, total=False):
    allowProtectedAppendWrites: BicepBool
    immutabilityPeriodSinceCreationInDays: BicepInt
    state: Literal['Disabled', 'Locked', 'Unlocked']


class ImmutableStorageAccount(TypedDict, total=False):
    enabled: BicepBool
    immutabilityPolicy: AccountImmutabilityPolicyProperties


class KeyPolicy(TypedDict):
    # Required
    keyExpirationPeriodInDays: BicepInt


class IPRule(TypedDict):
    action: Literal['Allow']
    # Required
    value: BicepStr


class ResourceAccessRule(TypedDict):
    # Required
    resourceId: BicepStr
    # Required
    tenantId: BicepStr


class VirtualNetworkRule(TypedDict):
    action: Literal['Allow']
    # Required
    id: BicepStr


class NetworkRuleSet(TypedDict, total=False):
    bypass: Literal['AzureServices', 'Logging', 'Metrics', 'None']
    # Required
    defaultAction: Literal['Allow', 'Deny']
    ipRules: List[IPRule]
    resourceAccessRules: List[ResourceAccessRule]
    virtualNetworkRules: List[VirtualNetworkRule]


class RoutingPreference(TypedDict, total=False):
    publishInternetEndpoints: BicepBool
    publishMicrosoftEndpoints: BicepBool
    routingChoice: Literal['InternetRouting', 'MicrosoftRouting']


class SasPolicy(TypedDict):
    # Required
    expirationAction: Literal["Log"]
    # Required
    sasExpirationPeriod: BicepStr


class Properties(TypedDict, total=False):
    accessTier: Literal["Hot", "Cool", "Premium"]
    allowBlobPublicAccess: BicepBool
    allowCrossTenantReplication: BicepBool
    allowedCopyScope: Literal['AAD','PrivateLink']
    allowSharedKeyAccess: BicepBool
    customDomain: CustomDomain
    defaultToOAuthAuthentication: BicepBool
    dnsEndpointType: Literal['AzureDnsZone', 'Standard']
    immutableStorageWithVersioning: ImmutableStorageAccount
    isHnsEnabled: BicepBool
    isLocalUserEnabled: BicepBool
    isNfsV3Enabled: BicepBool
    isSftpEnabled: BicepBool
    keyPolicy: KeyPolicy
    largeFileSharesState: Literal['Disabled', 'Enabled']
    minimumTlsVersion: Literal['TLS1_0', 'TLS1_1', 'TLS1_2']
    networkAcls: NetworkRuleSet
    publicNetworkAccess: Literal['Disabled', 'Enabled']
    routingPreference: RoutingPreference
    sasPolicy: SasPolicy
    supportsHttpsTrafficOnly: BicepBool


@dataclass(kw_only=True)
class Container(Resource):
    name: BicepStr = field(metadata={'rest': 'name'})
    _resource: ClassVar[Literal['Microsoft.Storage/storageAccounts/blobServices/containers']] = 'Microsoft.Storage/storageAccounts/blobServices/containers'
    _version: ClassVar[str] = '2023-01-01'
    _symbolicname: str = field(default_factory=lambda: generate_symbol("container"), init=False, repr=False)


@dataclass(kw_only=True)
class Table(Resource):
    name: BicepStr = field(metadata={'rest': 'name'})
    _resource: ClassVar[Literal['Microsoft.Storage/storageAccounts/tableServices/tables']] = 'Microsoft.Storage/storageAccounts/tableServices/tables'
    _version: ClassVar[str] = '2023-05-01'
    _symbolicname: str = field(default_factory=lambda: generate_symbol("table"), init=False, repr=False)


@dataclass(kw_only=True)
class BlobServices(Resource):
    _resource: ClassVar[Literal['Microsoft.Storage/storageAccounts/blobServices']] = 'Microsoft.Storage/storageAccounts/blobServices'
    _version: ClassVar[str] = '2023-01-01'
    _symbolicname: str = field(default_factory=lambda: generate_symbol("blobs"), init=False, repr=False)
    name: str = field(init=False, default="default", metadata={'rest': 'name'})
    containers: List[Container] = field(default_factory=list, metadata={'rest': _SKIP})

    def write(self, bicep: IO[str]) -> Dict[str, str]:
        # pylint: disable=protected-access
        _serialize_resource(bicep, self)
        for container in self.containers:
            container.parent = self
            self._outputs.update(container.write(bicep))
        if self.parent._fname:
            output_prefix = self.parent._fname.title()
        else:
            output_prefix = ""
        output_prefix = "Blob" + output_prefix
        self._outputs[output_prefix + "Endpoint"] = Output(f"{self.parent._symbolicname}.properties.primaryEndpoints.blob")
        return self._outputs


@dataclass(kw_only=True)
class TableServices(Resource):
    _resource: ClassVar[Literal['Microsoft.Storage/storageAccounts/tableServices']] = 'Microsoft.Storage/storageAccounts/tableServices'
    _version: ClassVar[str] = '2023-05-01'
    _symbolicname: str = field(default_factory=lambda: generate_symbol("tables"), init=False, repr=False)
    name: str = field(init=False, default="default", metadata={'rest': 'name'})
    tables: List[Container] = field(default_factory=list, metadata={'rest': _SKIP})

    def write(self, bicep: IO[str]) -> Dict[str, str]:
        # pylint: disable=protected-access
        _serialize_resource(bicep, self)
        for table in self.tables:
            table.parent = self
            self._outputs.update(table.write(bicep))
        if self.parent._fname:
            output_prefix = self.parent._fname.title()
        else:
            output_prefix = ""
        output_prefix = "Table" + output_prefix
        self._outputs[output_prefix + "Endpoint"] = Output(f"{self.parent._symbolicname}.properties.primaryEndpoints.table")
        return self._outputs


@dataclass(kw_only=True)
class StorageAccount(LocatedResource):
    sku: Sku = field(default=_UNSET, metadata={'rest': 'sku'})
    kind: BicepStr = field(default=_UNSET, metadata={'rest': 'kind'})
    extended_location : Optional[ExtendedLocation] = field(default=_UNSET, metadata={'rest': 'extendedLocation'})
    identity: Optional[Identity] = field(default=_UNSET, metadata={'rest': 'identity'})
    properties: Optional[Properties] = field(default=_UNSET, metadata={'rest': 'properties'})
    blobs: Optional[BlobServices] = field(default=None, metadata={'rest': _SKIP})
    tables: Optional[TableServices] = field(default=None, metadata={'rest': _SKIP})
    roles: Optional[List[RoleAssignment]] = field(default_factory=list, metadata={'rest': _SKIP})
    _resource: ClassVar[Literal['Microsoft.Storage/storageAccounts']] = 'Microsoft.Storage/storageAccounts'
    _version: ClassVar[str] = '2023-01-01'
    _symbolicname: str = field(default_factory=lambda: generate_symbol("storage"), init=False, repr=False)

    def write(self, bicep: IO[str]) -> Dict[str, str]:
        _serialize_resource(bicep, self)
        if self.blobs:
            self.blobs.parent = self
            self._outputs.update(self.blobs.write(bicep))
        if self.tables:
            self.tables.parent = self
            self._outputs.update(self.tables.write(bicep))
        for role in self.roles:
            role.name = GuidName(self, PrincipalId(), role.properties['roleDefinitionId'])
            role.scope = self
            self._outputs.update(role.write(bicep))

        if self._fname:
            output_prefix = self._fname.title()
        else:
            output_prefix = ""
        output_prefix = "Storage" + output_prefix
        self._outputs[output_prefix + "Id"] = Output(f"{self._symbolicname}.id")
        self._outputs[output_prefix + "Name"] = Output(f"{self._symbolicname}.name")
        for key, value in self._outputs.items():
            bicep.write(f"output {key} string = {resolve_value(value)}\n")
        bicep.write("\n")
        return self._outputs
