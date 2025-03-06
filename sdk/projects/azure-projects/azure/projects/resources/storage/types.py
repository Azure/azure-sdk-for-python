from typing import Any, Dict, List, TypedDict, Literal, Union
from typing_extensions import Required

from ..._bicep.expressions import Parameter

RESOURCE = "Microsoft.Storage/storageAccounts"
VERSION = "2023-05-01"


class Sku(TypedDict):
    name: Required[Union[Literal['Premium_LRS', 'Premium_ZRS', 'Standard_GRS', 'Standard_GZRS', 'Standard_LRS', 'Standard_RAGRS', 'Standard_RAGZRS', 'Standard_ZRS'], Parameter[str]]]
    """The SKU name. Required for account creation; optional for update. Note that in older versions, SKU name was called accountType."""


class ExtendedLocation(TypedDict):
    name: Union[str, Parameter[str]]
    """The name of the extended location."""
    type: Required[Union[Literal['EdgeZone'], Parameter[str]]]
    """The type of the extended location."""


class Identity(TypedDict, total=False):
    type: Required[Union[Literal['None', 'SystemAssigned', 'SystemAssigned,UserAssigned','UserAssigned'], Parameter[str]]]
    """The identity type."""
    userAssignedIdentities: Dict[Union[str, Parameter[str]], Dict]
    """The set of user assigned identities associated with the resource."""


class ActiveDirectoryProperties(TypedDict, total=False):
    domainGuid: Required[Union[str, Parameter[str]]]
    """Specifies the domain GUID."""
    domainName: Required[Union[str, Parameter[str]]]
    """Specifies the primary domain that the AD DNS server is authoritative for."""
    accountType: Union[Literal['Computer', 'User'], Parameter[str]]
    """Specifies the Active Directory account type for Azure Storage."""
    azureStorageSid: Union[str, Parameter[str]]
    """Specifies the security identifier (SID) for Azure Storage."""
    domainSid: Union[str, Parameter[str]]
    """Specifies the security identifier (SID)."""
    forestName: Union[str, Parameter[str]]
    """Specifies the Active Directory forest to get."""
    netBiosDomainName: Union[str, Parameter[str]]
    """Specifies the NetBIOS domain name."""
    samAccountName: Union[str, Parameter[str]]
    """Specifies the Active Directory SAMAccountName for Azure Storage."""


class AzureFilesIdentityBasedAuthentication(TypedDict, total=False):
    activeDirectoryProperties: Union[ActiveDirectoryProperties, Parameter[ActiveDirectoryProperties]]
    """Required if directoryServiceOptions are AD, optional if they are AADKERB."""
    defaultSharePermission: Union[Literal['None', 'StorageFileDataSmbShareContributor', 'StorageFileDataSmbShareElevatedContributor', 'StorageFileDataSmbShareReader'], Parameter[str]]
    """Default share permission for users using Kerberos authentication if RBAC role is not assigned."""
    directoryServiceOptions: Required[Union[Literal['AADDS', 'AADKERB', 'AD', 'None'], Parameter[str]]]
    """Indicates the directory service used. Note that this enum may be extended in the future."""


class CustomDomain(TypedDict, total=False):
    name: Required[Union[str, Parameter[str]]]
    """Gets or sets the custom domain name assigned to the storage account. Name is the CNAME source."""
    useSubDomainName: Union[bool, Parameter[bool]]
    """Indicates whether indirect CName validation is enabled. Default value is false. This should only be set on updates."""

	
class EncryptionIdentity(TypedDict, total=False):
    federatedIdentityClientId: Union[str, Parameter[str]]
    """ClientId of the multi-tenant application to be used in conjunction with the user-assigned identity for cross-tenant customer-managed-keys server-side encryption on the storage account."""
    userAssignedIdentity: Union[str, Parameter[str]]
    """Resource identifier of the UserAssigned identity to be associated with server-side encryption on the storage account."""


class KeyVaultProperties(TypedDict, total=False):
    keyname: Union[str, Parameter[str]]
    """The name of KeyVault key."""
    keyvaulturi: Union[str, Parameter[str]]
    """The Uri of KeyVault."""
    keyversion: Union[str, Parameter[str]]
    """The version of KeyVault key."""


class EncryptionService(TypedDict, total=False):
    enabled: Union[bool, Parameter[bool]]
    """A boolean indicating whether or not the service encrypts the data as it is stored. Encryption at rest is enabled by default today and cannot be disabled."""
    keyType: Union[Literal['Account', 'Service'], Parameter[str]]
    """Encryption key type to be used for the encryption service. 'Account' key type implies that an account-scoped encryption key will be used. 'Service' key type implies that a default service key is used."""


class EncryptionServices(TypedDict, total=False):
    blob: Union[EncryptionService, Parameter[EncryptionService]]
    """The encryption function of the blob storage service."""
    file: Union[EncryptionService, Parameter[EncryptionService]]
    """The encryption function of the file storage service."""
    queue: Union[EncryptionService, Parameter[EncryptionService]]
    """The encryption function of the queue storage service."""
    table: Union[EncryptionService, Parameter[EncryptionService]]
    """The encryption function of the table storage service."""


class Encryption(TypedDict, total=False):
    identity: Union[EncryptionIdentity, Parameter[EncryptionIdentity]]
    """The identity to be used with service-side encryption at rest."""
    keySource: Union[Literal['Microsoft.Keyvault', 'Microsoft.Storage'], Parameter[str]]
    """The encryption keySource (provider). Possible values (case-insensitive): Microsoft.Storage, Microsoft.Keyvault"""
    keyvaultProperties: Union[KeyVaultProperties, Parameter[KeyVaultProperties]]
    """Properties provided by key vault."""
    requireInfrastructureEncryption: Union[bool, Parameter[bool]]
    """A boolean indicating whether or not the service applies a secondary layer of encryption with platform managed keys for data at rest."""
    services: Union[EncryptionServices, Parameter[EncryptionServices]]
    """List of services which support encryption."""


class AccountImmutabilityPolicyProperties(TypedDict, total=False):
    allowProtectedAppendWrites: Union[bool, Parameter[bool]]
    """This property can only be changed for disabled and unlocked time-based retention policies. When enabled, new blocks can be written to an append blob while maintaining immutability protection and compliance. Only new blocks can be added and any existing blocks cannot be modified or deleted."""
    immutabilityPeriodSinceCreationInDays: Union[int, Parameter[int]]
    """The immutability period for the blobs in the container since the policy creation, in days."""
    state: Union[Literal['Disabled', 'Locked', 'Unlocked'], Parameter[str]]
    """The ImmutabilityPolicy state defines the mode of the policy. Disabled state disables the policy, Unlocked state allows increase and decrease of immutability retention time and also allows toggling allowProtectedAppendWrites property, Locked state only allows the increase of the immutability retention time. A policy can only be created in a Disabled or Unlocked state and can be toggled between the two states. Only a policy in an Unlocked state can transition to a Locked state which cannot be reverted."""


class ImmutableStorageAccount(TypedDict, total=False):
    enabled: Union[bool, Parameter[bool]]
    """A boolean flag which enables account-level immutability. All the containers under such an account have object-level immutability enabled by default."""
    immutabilityPolicy: Union[AccountImmutabilityPolicyProperties, Parameter[AccountImmutabilityPolicyProperties]]
    """Specifies the default account-level immutability policy which is inherited and applied to objects that do not possess an explicit immutability policy at the object level. The object-level immutability policy has higher precedence than the container-level immutability policy, which has a higher precedence than the account-level immutability policy."""


class KeyPolicy(TypedDict):
    keyExpirationPeriodInDays: Required[Union[int, Parameter[int]]]
    """The key expiration period in days."""


class IPRule(TypedDict):
    action: Union[Literal['Allow'], Parameter[str]]
    """The action of IP ACL rule."""
    value: Required[Union[str, Parameter[str]]]
    """Specifies the IP or IP range in CIDR format. Only IPV4 address is allowed."""


class ResourceAccessRule(TypedDict):
    resourceId: Required[Union[str, Parameter[str]]]
    """Resource Id"""
    tenantId: Required[Union[str, Parameter[str]]]
    """Tenant Id"""


class VirtualNetworkRule(TypedDict):
    action: Required[Union[Literal['Allow'], Parameter[str]]]
    """The action of virtual network rule."""
    id: Required[Union[str, Parameter[str]]]
    """Resource ID of a subnet, for example: /subscriptions/{subscriptionId}/resourceGroups/{groupName}/providers/Microsoft.Network/virtualNetworks/{vnetName}/subnets/{subnetName}."""


class NetworkRuleSet(TypedDict, total=False):
    bypass: Literal['AzureServices', 'Logging', 'Metrics', 'None']
    """Specifies whether traffic is bypassed for Logging/Metrics/AzureServices. Possible values are any combination of Logging	Metrics	AzureServices (For example, "Logging, Metrics"), or None to bypass none of those traffics."""
    defaultAction: Required[Union[Literal['Allow', 'Deny'], Parameter[str]]]
    """Specifies the default action of allow or deny when no other rules match."""
    ipRules: List[Union[IPRule, Parameter[IPRule]]]
    """Sets the IP ACL rules."""
    resourceAccessRules: List[Union[ResourceAccessRule, Parameter[ResourceAccessRule]]]
    """Sets the resource access rules."""
    virtualNetworkRules: List[Union[VirtualNetworkRule, Parameter[VirtualNetworkRule]]]
    """Sets the virtual network rules."""


class RoutingPreference(TypedDict, total=False):
    publishInternetEndpoints: Union[bool, Parameter[bool]]
    """A boolean flag which indicates whether internet routing storage endpoints are to be published."""
    publishMicrosoftEndpoints: Union[bool, Parameter[bool]]
    """A boolean flag which indicates whether microsoft routing storage endpoints are to be published."""
    routingChoice: Union[Literal['InternetRouting', 'MicrosoftRouting'], Parameter[str]]
    """Routing Choice defines the kind of network routing opted by the user."""


class SasPolicy(TypedDict):
    expirationAction: Required[Union[Literal['Block', "Log"], Parameter[str]]]
    """The SAS Expiration Action defines the action to be performed when sasPolicy.sasExpirationPeriod is violated. The 'Log' action can be used for audit purposes and the 'Block' action can be used to block and deny the usage of SAS tokens that do not adhere to the sas policy expiration period."""
    sasExpirationPeriod: Required[Union[str, Parameter[str]]]
    """The SAS expiration period, DD.HH:MM:SS."""


class StorageAccountProperties(TypedDict, total=False):
    accessTier: Union[Literal["Hot", "Cold", "Cool", "Premium"], Parameter[str]]
    """Required for storage accounts where kind = BlobStorage. The access tier is used for billing. The 'Premium' access tier is the default value for premium block blobs storage account type and it cannot be changed for the premium block blobs storage account type."""
    allowBlobPublicAccess: Union[bool, Parameter[bool]]
    """Allow or disallow public access to all blobs or containers in the storage account. The default interpretation is false for this property."""
    allowCrossTenantReplication: Union[bool, Parameter[bool]]
    """Allow or disallow cross AAD tenant object replication. Set this property to true for new or existing accounts only if object replication policies will involve storage accounts in different AAD tenants. The default interpretation is false for new accounts to follow best security practices by default."""
    allowedCopyScope: Union[Literal['AAD','PrivateLink'], Parameter[str]]
    """Restrict copy to and from Storage Accounts within an AAD tenant or with Private Links to the same VNet."""
    allowSharedKeyAccess: Union[bool, Parameter[bool]]
    """Indicates whether the storage account permits requests to be authorized with the account access key via Shared Key. If false, then all requests, including shared access signatures, must be authorized with Azure Active Directory (Azure AD). The default value is null, which is equivalent to true."""
    azureFilesIdentityBasedAuthentication: Union[AzureFilesIdentityBasedAuthentication, Parameter[AzureFilesIdentityBasedAuthentication]]
    """Provides the identity based authentication settings for Azure Files."""
    customDomain: Union[CustomDomain, Parameter[CustomDomain]]
    """User domain assigned to the storage account. Name is the CNAME source. Only one custom domain is supported per storage account at this time. To clear the existing custom domain, use an empty string for the custom domain name property."""
    defaultToOAuthAuthentication: Union[bool, Parameter[bool]]
    """A boolean flag which indicates whether the default authentication is OAuth or not. The default interpretation is false for this property."""
    dnsEndpointType: Union[Literal['AzureDnsZone', 'Standard'], Parameter[str]]
    """Allows you to specify the type of endpoint. Set this to AzureDNSZone to create a large number of accounts in a single subscription, which creates accounts in an Azure DNS Zone and the endpoint URL will have an alphanumeric DNS Zone identifier."""
    enableExtendedGroups: Union[bool, Parameter[bool]]
    """Enables extended group support with local users feature, if set to true."""
    encryption: Union[Encryption, Parameter[Encryption]]
    """Encryption settings to be used for server-side encryption for the storage account."""
    immutableStorageWithVersioning: Union[ImmutableStorageAccount, Parameter[ImmutableStorageAccount]]
    """The property is immutable and can only be set to true at the account creation time. When set to true, it enables object level immutability for all the new containers in the account by default."""
    isHnsEnabled: Union[bool, Parameter[bool]]
    """Account HierarchicalNamespace enabled if sets to true."""
    isLocalUserEnabled: Union[bool, Parameter[bool]]
    """Enables local users feature, if set to true."""
    isNfsV3Enabled: Union[bool, Parameter[bool]]
    """NFS 3.0 protocol support enabled if set to true."""
    isSftpEnabled: Union[bool, Parameter[bool]]
    """Enables Secure File Transfer Protocol, if set to true."""
    keyPolicy: Union[KeyPolicy, Parameter[KeyPolicy]]
    """KeyPolicy assigned to the storage account."""
    largeFileSharesState: Union[Literal['Disabled', 'Enabled'], Parameter[str]]
    """Allow large file shares if sets to Enabled. It cannot be disabled once it is enabled."""
    minimumTlsVersion: Union[Literal['TLS1_0', 'TLS1_1', 'TLS1_2', 'TLS1_3'], Parameter[str]]
    """Set the minimum TLS version to be permitted on requests to storage. The default interpretation is TLS 1.0 for this property."""
    networkAcls: Union[NetworkRuleSet, Parameter[NetworkRuleSet]]
    """Network rule set."""
    publicNetworkAccess: Union[Literal['Disabled', 'Enabled', 'SecuredByPerimeter'], Parameter[str]]
    """Allow, disallow, or let Network Security Perimeter configuration to evaluate public network access to Storage Account. Value is optional but if passed in, must be 'Enabled', 'Disabled' or 'SecuredByPerimeter'."""
    routingPreference: Union[RoutingPreference, Parameter[RoutingPreference]]
    """Maintains information about the network routing choice opted by the user for data transfer."""
    sasPolicy: Union[SasPolicy, Parameter[SasPolicy]]
    """SasPolicy assigned to the storage account."""
    supportsHttpsTrafficOnly: Union[bool, Parameter[bool]]
    """Allows https traffic only to storage service if sets to true. The default value is true since API version 2019-04-01."""


class StorageAccountResource(TypedDict, total=False):
    extendedLocation: Union[ExtendedLocation, Parameter[ExtendedLocation]]
    """Set the extended location of the resource. If not set, the storage account will be created in Azure main region. Otherwise it will be created in the specified extended location."""
    identity: Union[Identity, Parameter[Identity]]
    """The identity of the resource."""
    kind: Union[Literal['BlobStorage', 'BlockBlobStorage', 'FileStorage', 'Storage', 'StorageV2'], Parameter[str]]
    """Indicates the type of storage account."""
    location: Union[str, Parameter[str]]
    """Gets or sets the location of the resource. This will be one of the supported and registered Azure Geo Regions (e.g. West US, East US, Southeast Asia, etc.). The geo region of a resource cannot be changed once it is created, but if an identical geo region is specified on update, the request will succeed."""
    name: Union[str, Parameter[str]]
    """The resource name."""
    properties: Union[StorageAccountProperties, Parameter[StorageAccountProperties]]
    """The parameters used to create the storage account."""
    sku: Union[Sku, Parameter[Sku]]
    """Gets or sets the SKU name."""
    tags: Union[Dict[str, Union[str, Parameter[str]]], Parameter[Dict[str, str]]]
    """Dictionary of resource tag names and values."""
