# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=line-too-long, name-too-long

from __future__ import annotations
from typing import TypedDict, Literal, Union

from ..._bicep.expressions import Parameter
from .._extension import Identity

VERSION = "2024-01-01"


class StorageAccountAccountImmutabilityPolicyProperties(TypedDict, total=False):
    allowProtectedAppendWrites: Union[bool, Parameter]
    """This property can only be changed for disabled and unlocked time-based retention policies. When enabled, new blocks can be written to an append blob while maintaining immutability protection and compliance. Only new blocks can be added and any existing blocks cannot be modified or deleted."""
    immutabilityPeriodSinceCreationInDays: Union[int, Parameter]
    """The immutability period for the blobs in the container since the policy creation, in days."""
    state: Union[Literal["Locked", "Disabled", "Unlocked"], Parameter]
    """The ImmutabilityPolicy state defines the mode of the policy. Disabled state disables the policy, Unlocked state allows increase and decrease of immutability retention time and also allows toggling allowProtectedAppendWrites property, Locked state only allows the increase of the immutability retention time. A policy can only be created in a Disabled or Unlocked state and can be toggled between the two states. Only a policy in an Unlocked state can transition to a Locked state which cannot be reverted."""


class StorageAccountActiveDirectoryProperties(TypedDict, total=False):
    accountType: Union[Literal["Computer", "User"], Parameter]
    """Specifies the Active Directory account type for Azure Storage."""
    azureStorageSid: Union[str, Parameter]
    """Specifies the security identifier (SID) for Azure Storage."""
    domainGuid: Union[str, Parameter]
    """Specifies the domain GUID."""
    domainName: Union[str, Parameter]
    """Specifies the primary domain that the AD DNS server is authoritative for."""
    domainSid: Union[str, Parameter]
    """Specifies the security identifier (SID)."""
    forestName: Union[str, Parameter]
    """Specifies the Active Directory forest to get."""
    netBiosDomainName: Union[str, Parameter]
    """Specifies the NetBIOS domain name."""
    samAccountName: Union[str, Parameter]
    """Specifies the Active Directory SAMAccountName for Azure Storage."""


class StorageAccountAzureFilesIdentityBasedAuthentication(TypedDict, total=False):
    activeDirectoryProperties: Union[StorageAccountActiveDirectoryProperties, Parameter]
    """Required if directoryServiceOptions are AD, optional if they are AADKERB."""
    defaultSharePermission: Union[
        Literal[
            "StorageFileDataSmbShareElevatedContributor",
            "None",
            "StorageFileDataSmbShareReader",
            "StorageFileDataSmbShareContributor",
        ],
        Parameter,
    ]
    """Default share permission for users using Kerberos authentication if RBAC role is not assigned."""
    directoryServiceOptions: Union[Literal["AADDS", "AADKERB", "None", "AD"], Parameter]
    """Indicates the directory service used. Note that this enum may be extended in the future."""


class StorageAccountCustomDomain(TypedDict, total=False):
    name: Union[str, Parameter]
    """Gets or sets the custom domain name assigned to the storage account. Name is the CNAME source."""
    useSubDomainName: Union[bool, Parameter]
    """Indicates whether indirect CName validation is enabled. Default value is false. This should only be set on updates."""


class StorageAccountEncryption(TypedDict, total=False):
    identity: Union[StorageAccountEncryptionIdentity, Parameter]
    """The identity to be used with service-side encryption at rest."""
    keySource: Union[Literal["Microsoft.Keyvault", "Microsoft.Storage"], Parameter]
    """The encryption keySource (provider). Possible values (case-insensitive):  Microsoft.Storage, Microsoft.Keyvault"""
    keyvaultproperties: Union[StorageAccountKeyVaultProperties, Parameter]
    """Properties provided by key vault."""
    requireInfrastructureEncryption: Union[bool, Parameter]
    """A boolean indicating whether or not the service applies a secondary layer of encryption with platform managed keys for data at rest."""
    services: Union[StorageAccountEncryptionServices, Parameter]
    """List of services which support encryption."""


class StorageAccountEncryptionIdentity(TypedDict, total=False):
    federatedIdentityClientId: Union[str, Parameter]
    """ClientId of the multi-tenant application to be used in conjunction with the user-assigned identity for cross-tenant customer-managed-keys server-side encryption on the storage account."""
    userAssignedIdentity: Union[str, Parameter]
    """Resource identifier of the UserAssigned identity to be associated with server-side encryption on the storage account."""


class StorageAccountEncryptionService(TypedDict, total=False):
    enabled: Union[bool, Parameter]
    """A boolean indicating whether or not the service encrypts the data as it is stored. Encryption at rest is enabled by default today and cannot be disabled."""
    keyType: Union[Literal["Service", "Account"], Parameter]
    """Encryption key type to be used for the encryption service. 'Account' key type implies that an account-scoped encryption key will be used. 'Service' key type implies that a default service key is used."""


class StorageAccountEncryptionServices(TypedDict, total=False):
    blob: Union[StorageAccountEncryptionService, Parameter]
    """The encryption function of the blob storage service."""
    file: Union[StorageAccountEncryptionService, Parameter]
    """The encryption function of the file storage service."""
    queue: Union[StorageAccountEncryptionService, Parameter]
    """The encryption function of the queue storage service."""
    table: Union[StorageAccountEncryptionService, Parameter]
    """The encryption function of the table storage service."""


class StorageAccountExtendedLocation(TypedDict, total=False):
    name: Union[str, Parameter]
    """The name of the extended location."""
    type: Union[Literal["EdgeZone"], Parameter]
    """The type of the extended location."""


class StorageAccountImmutableStorageAccount(TypedDict, total=False):
    enabled: Union[bool, Parameter]
    """A boolean flag which enables account-level immutability. All the containers under such an account have object-level immutability enabled by default."""
    immutabilityPolicy: Union[StorageAccountAccountImmutabilityPolicyProperties, Parameter]
    """Specifies the default account-level immutability policy which is inherited and applied to objects that do not possess an explicit immutability policy at the object level. The object-level immutability policy has higher precedence than the container-level immutability policy, which has a higher precedence than the account-level immutability policy."""


class StorageAccountIPRule(TypedDict, total=False):
    action: Union[Literal["Allow"], Parameter]
    """The action of IP ACL rule."""
    value: Union[str, Parameter]
    """Specifies the IP or IP range in CIDR format. Only IPV4 address is allowed."""


class StorageAccountKeyPolicy(TypedDict, total=False):
    keyExpirationPeriodInDays: Union[int, Parameter]
    """The key expiration period in days."""


class StorageAccountKeyVaultProperties(TypedDict, total=False):
    keyname: Union[str, Parameter]
    """The name of KeyVault key."""
    keyvaulturi: Union[str, Parameter]
    """The Uri of KeyVault."""
    keyversion: Union[str, Parameter]
    """The version of KeyVault key."""


class StorageAccountResource(TypedDict, total=False):
    extendedLocation: Union[StorageAccountExtendedLocation, Parameter]
    """Optional. Set the extended location of the resource. If not set, the storage account will be created in Azure main region. Otherwise it will be created in the specified extended location"""
    identity: Union[Identity, Parameter]
    """The identity of the resource."""
    kind: Union[Literal["Storage", "StorageV2", "BlobStorage", "FileStorage", "BlockBlobStorage"], Parameter]
    """Required. Indicates the type of storage account."""
    location: Union[str, Parameter]
    """Required. Gets or sets the location of the resource. This will be one of the supported and registered Azure Geo Regions (e.g. West US, East US, Southeast Asia, etc.). The geo region of a resource cannot be changed once it is created, but if an identical geo region is specified on update, the request will succeed."""
    name: Union[str, Parameter]
    """The resource name"""
    properties: StorageAccountProperties
    """The parameters used to create the storage account."""
    sku: Union[StorageAccountSku, Parameter]
    """Required. Gets or sets the SKU name."""
    tags: Union[dict[str, Union[str, Parameter]], Parameter]
    """Resource tags"""


class StorageAccountNetworkRuleSet(TypedDict, total=False):
    bypass: Union[Literal["AzureServices", "Logging", "None", "Metrics", "Logging, Metrics"], Parameter]
    """Specifies whether traffic is bypassed for Logging/Metrics/AzureServices. Possible values are any combination of Logging"""
    defaultAction: Union[Literal["Allow", "Deny"], Parameter]
    """Specifies the default action of allow or deny when no other rules match."""
    ipRules: Union[list[StorageAccountIPRule], Parameter]
    """Sets the IP ACL rules"""
    resourceAccessRules: Union[list[StorageAccountResourceAccessRule], Parameter]
    """Sets the resource access rules"""
    virtualNetworkRules: Union[list[StorageAccountVirtualNetworkRule], Parameter]
    """Sets the virtual network rules"""


class StorageAccountResourceAccessRule(TypedDict, total=False):
    resourceId: Union[str, Parameter]
    """Resource Id"""
    tenantId: Union[str, Parameter]
    """Tenant Id"""


class StorageAccountRoutingPreference(TypedDict, total=False):
    publishInternetEndpoints: Union[bool, Parameter]
    """A boolean flag which indicates whether internet routing storage endpoints are to be published"""
    publishMicrosoftEndpoints: Union[bool, Parameter]
    """A boolean flag which indicates whether microsoft routing storage endpoints are to be published"""
    routingChoice: Union[Literal["InternetRouting", "MicrosoftRouting"], Parameter]
    """Routing Choice defines the kind of network routing opted by the user."""


class StorageAccountSasPolicy(TypedDict, total=False):
    expirationAction: Union[Literal["Log", "Block"], Parameter]
    """The SAS Expiration Action defines the action to be performed when sasPolicy.sasExpirationPeriod is violated. The 'Log' action can be used for audit purposes and the 'Block' action can be used to block and deny the usage of SAS tokens that do not adhere to the sas policy expiration period."""
    sasExpirationPeriod: Union[str, Parameter]
    """The SAS expiration period, DD.HH:MM:SS."""


class StorageAccountSku(TypedDict, total=False):
    name: Union[
        Literal[
            "PremiumV2_LRS",
            "Standard_ZRS",
            "PremiumV2_ZRS",
            "StandardV2_GZRS",
            "Standard_GZRS",
            "Standard_GRS",
            "Standard_LRS",
            "Standard_RAGZRS",
            "Standard_RAGRS",
            "Premium_ZRS",
            "Premium_LRS",
            "StandardV2_GRS",
            "StandardV2_LRS",
            "StandardV2_ZRS",
        ],
        Parameter,
    ]
    """The SKU name. Required for account creation; optional for update. Note that in older versions, SKU name was called accountType."""


class StorageAccountProperties(TypedDict, total=False):
    accessTier: Union[Literal["Hot", "Premium", "Cool", "Cold"], Parameter]
    """Required for storage accounts where kind = BlobStorage. The access tier is used for billing. The 'Premium' access tier is the default value for premium block blobs storage account type and it cannot be changed for the premium block blobs storage account type."""
    allowBlobPublicAccess: Union[bool, Parameter]
    """Allow or disallow public access to all blobs or containers in the storage account. The default interpretation is false for this property."""
    allowCrossTenantReplication: Union[bool, Parameter]
    """Allow or disallow cross AAD tenant object replication. Set this property to true for new or existing accounts only if object replication policies will involve storage accounts in different AAD tenants. The default interpretation is false for new accounts to follow best security practices by default."""
    allowedCopyScope: Union[Literal["PrivateLink", "AAD"], Parameter]
    """Restrict copy to and from Storage Accounts within an AAD tenant or with Private Links to the same VNet."""
    allowSharedKeyAccess: Union[bool, Parameter]
    """Indicates whether the storage account permits requests to be authorized with the account access key via Shared Key. If false, then all requests, including shared access signatures, must be authorized with Azure Active Directory (Azure AD). The default value is null, which is equivalent to true."""
    azureFilesIdentityBasedAuthentication: Union[StorageAccountAzureFilesIdentityBasedAuthentication, Parameter]
    """Provides the identity based authentication settings for Azure Files."""
    customDomain: Union[StorageAccountCustomDomain, Parameter]
    """User domain assigned to the storage account. Name is the CNAME source. Only one custom domain is supported per storage account at this time. To clear the existing custom domain, use an empty string for the custom domain name property."""
    defaultToOAuthAuthentication: Union[bool, Parameter]
    """A boolean flag which indicates whether the default authentication is OAuth or not. The default interpretation is false for this property."""
    dnsEndpointType: Union[Literal["Standard", "AzureDnsZone"], Parameter]
    """Allows you to specify the type of endpoint. Set this to AzureDNSZone to create a large number of accounts in a single subscription, which creates accounts in an Azure DNS Zone and the endpoint URL will have an alphanumeric DNS Zone identifier."""
    enableExtendedGroups: Union[bool, Parameter]
    """Enables extended group support with local users feature, if set to true"""
    encryption: Union[StorageAccountEncryption, Parameter]
    """Encryption settings to be used for server-side encryption for the storage account."""
    immutableStorageWithVersioning: Union[StorageAccountImmutableStorageAccount, Parameter]
    """The property is immutable and can only be set to true at the account creation time. When set to true, it enables object level immutability for all the new containers in the account by default."""
    isHnsEnabled: Union[bool, Parameter]
    """Account HierarchicalNamespace enabled if sets to true."""
    isLocalUserEnabled: Union[bool, Parameter]
    """Enables local users feature, if set to true"""
    isNfsV3Enabled: Union[bool, Parameter]
    """NFS 3.0 protocol support enabled if set to true."""
    isSftpEnabled: Union[bool, Parameter]
    """Enables Secure File Transfer Protocol, if set to true"""
    keyPolicy: Union[StorageAccountKeyPolicy, Parameter]
    """KeyPolicy assigned to the storage account."""
    largeFileSharesState: Union[Literal["Disabled", "Enabled"], Parameter]
    """Allow large file shares if sets to Enabled. It cannot be disabled once it is enabled."""
    minimumTlsVersion: Union[Literal["TLS1_0", "TLS1_3", "TLS1_2", "TLS1_1"], Parameter]
    """Set the minimum TLS version to be permitted on requests to storage. The default interpretation is TLS 1.0 for this property."""
    networkAcls: Union[StorageAccountNetworkRuleSet, Parameter]
    """Network rule set"""
    publicNetworkAccess: Union[Literal["Disabled", "SecuredByPerimeter", "Enabled"], Parameter]
    """Allow, disallow, or let Network Security Perimeter configuration to evaluate public network access to Storage Account. Value is optional but if passed in, must be 'Enabled', 'Disabled' or 'SecuredByPerimeter'."""
    routingPreference: Union[StorageAccountRoutingPreference, Parameter]
    """Maintains information about the network routing choice opted by the user for data transfer"""
    sasPolicy: Union[StorageAccountSasPolicy, Parameter]
    """SasPolicy assigned to the storage account."""
    supportsHttpsTrafficOnly: Union[bool, Parameter]
    """Allows https traffic only to storage service if sets to true. The default value is true since API version 2019-04-01."""


class StorageAccountVirtualNetworkRule(TypedDict, total=False):
    action: Union[Literal["Allow"], Parameter]
    """The action of virtual network rule."""
    id: Union[str, Parameter]
    """Resource ID of a subnet, for example: /subscriptions/{subscriptionId}/resourceGroups/{groupName}/providers/Microsoft.Network/virtualNetworks/{vnetName}/subnets/{subnetName}."""
    state: Union[Literal["Deprovisioning", "Provisioning", "Succeeded", "NetworkSourceDeleted", "Failed"], Parameter]
    """Gets the state of virtual network rule."""
