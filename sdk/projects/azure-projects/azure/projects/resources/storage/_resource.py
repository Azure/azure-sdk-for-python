# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=arguments-differ

from collections import defaultdict
from typing import TYPE_CHECKING, Any, Dict, Generic, List, Literal, Mapping, Union, Optional, cast
from typing_extensions import TypeVar, Unpack, TypedDict

from .._identifiers import ResourceIdentifiers
from ..._resource import Resource, ExtensionResources, ResourceReference
from ..._bicep.expressions import Parameter
from .._extension import convert_managed_identities, ManagedIdentity, RoleAssignment
from ..resourcegroup import ResourceGroup
from ..._parameters import GLOBAL_PARAMS

if TYPE_CHECKING:
    from .types import (
        StorageAccountResource,
        StorageNetworkRuleSet,
        AzureFilesIdentityBasedAuthentication,
        StorageEncryption,
        CustomDomain,
    )


class StorageAccountKwargs(TypedDict, total=False):
    access_tier: Union[Literal["Cool", "Hot", "Premium"], Parameter]
    """Required if the Storage Account kind is set to BlobStorage. The access tier is used for billing. The "Premium"
    access tier is the default value for premium block blobs storage account type and it cannot be changed for the
    premium block blobs storage account type.
    """
    enable_hierarchical_namespace: Union[bool, Parameter]
    """If true, enables Hierarchical Namespace for the storage account. Required if enableSftp or enableNfsV3 is
    set to true.
    """
    allow_blob_public_access: Union[bool, Parameter]
    """Indicates whether public access is enabled for all blobs or containers in the storage account. For security
    reasons, it is recommended to set it to false.
    """
    allow_cross_tenant_replication: Union[bool, Parameter]
    """Allow or disallow cross AAD tenant object replication."""
    allowed_copy_scope: Union[Literal["AAD", "PrivateLink"], Parameter]
    """Restrict copy to and from Storage Accounts within an AAD tenant or with Private Links to the same VNet."""
    allow_shared_key_access: Union[bool, Parameter]
    """Indicates whether the storage account permits requests to be authorized with the account access key via Shared
    Key. If false, then all requests, including shared access signatures, must be authorized with Azure Active
    Directory (Azure AD). The default value is null, which is equivalent to true.
    """
    azure_files_identity_auth: Union["AzureFilesIdentityBasedAuthentication", Parameter]
    """Provides the identity based authentication settings for Azure Files."""
    custom_domain_name: Union[str, Parameter]
    """Sets the custom domain name assigned to the storage account. Name is the CNAME source."""
    custom_domain_use_subdomain_name: Union[bool, Parameter]
    """Indicates whether indirect CName validation is enabled. This should only be set on updates."""
    # TODO: Configure default encryption
    # customer_managed_key: 'CustomerManagedKey'
    # """The customer managed key definition."""
    default_to_oauth_authentication: Union[bool, Parameter]
    """A boolean flag which indicates whether the default authentication is OAuth or not."""
    # TODO: support diagnostics
    # diagnostic_settings: List['DiagnosticSetting']
    # """The diagnostic settings of the service."""
    dns_endpoint_type: Union[Literal["AzureDnsZone", "Standard"], Parameter]
    """Allows you to specify the type of endpoint. Set this to AzureDNSZone to create a large number of accounts in a
    single subscription, which creates accounts in an Azure DNS Zone and the endpoint URL will have an alphanumeric
    DNS Zone identifier.
    """
    enable_nfs_v3: Union[bool, Parameter]
    """If true, enables NFS 3.0 support for the storage account. Requires enableHierarchicalNamespace to be true."""
    enable_sftp: Union[bool, Parameter]
    """If true, enables Secure File Transfer Protocol for the storage account. Requires enableHierarchicalNamespace
    to be true.
    """
    # enable_telemetry: Union[bool, Parameter]
    # """Enable/Disable usage telemetry for module."""
    encryption: Union["StorageEncryption", Parameter]
    """Encryption settings to be used for server-side encryption for the storage account."""
    is_local_user_enabled: Union[bool, Parameter]
    """Enables local users feature, if set to true."""
    # key_type: Literal['Account', 'Service']
    # """The keyType to use with Queue & Table services."""
    kind: Union[Literal["BlobStorage", "BlockBlobStorage", "FileStorage", "Storage", "StorageV2"], Parameter]
    """Type of Storage Account to create."""
    large_file_shares_state: Union[Literal["Disabled", "Enabled"], Parameter]
    """Allow large file shares if sets to 'Enabled'. It cannot be disabled once it is enabled. Only supported on
    locally redundant and zone redundant file shares. It cannot be set on FileStorage storage accounts (storage
    accounts for premium file shares).
    """
    location: Union[str, Parameter]
    """Location for all resources."""
    # TODO: support locks
    # lock: 'Lock'
    # """The lock settings of the service."""
    managed_identities: Optional["ManagedIdentity"]
    """The managed identity definition for this resource."""
    # TODO: support management policies
    # management_policy_rules: List[object]
    # """The Storage Account ManagementPolicies Rules."""
    minimum_tls_version: Union[Literal["TLS1_2", "TLS1_3"], Parameter]
    """Set the minimum TLS version on request to storage. The TLS versions 1.0 and 1.1 are deprecated and not
    supported anymore.
    """
    network_acls: Union["StorageNetworkRuleSet", Parameter]
    """Networks ACLs, this value contains IPs to whitelist and/or Subnet information. If in use, bypass needs to be
    supplied. For security reasons, it is recommended to set the DefaultAction Deny.
    """
    # TODO: support private endpoints
    # private_endpoints: List['PrivateEndpoint']
    # """Configuration details for private endpoints. For security reasons, it is recommended to use private
    # endpoints whenever possible.
    # """
    public_network_access: Union[Literal["Disabled", "Enabled", "SecuredByPerimeter"], Parameter]
    """Whether or not public network access is allowed for this resource. For security reasons it should be disabled.
    If not specified, it will be disabled by default if private endpoints are set and networkAcls are not set.
    """
    require_infrastructure_encryption: Union[bool, Parameter]
    """A Boolean indicating whether or not the service applies a secondary layer of encryption with platform managed
    keys for data at rest. For security reasons, it is recommended to set it to true.
    """
    roles: Union[
        Parameter,
        List[
            Union[
                Parameter,
                "RoleAssignment",
                Literal[
                    "Contributor",
                    "Owner",
                    "Reader",
                    "Reader and Data Access",
                    "Role Based Access Control Administrator",
                    "Storage Account Backup Contributor",
                    "Storage Account Contributor",
                    "Storage Account Key Operator Service Role",
                    "Storage Blob Data Contributor",
                    "Storage Blob Data Owner",
                    "Storage Blob Data Reader",
                    "Storage Blob Delegator",
                    "Storage File Data Privileged Contributor",
                    "Storage File Data Privileged Reader",
                    "Storage File Data SMB Share Contributor",
                    "Storage File Data SMB Share Elevated Contributor",
                    "Storage File Data SMB Share Reader",
                    "Storage Queue Data Contributor",
                    "Storage Queue Data Message Processor",
                    "Storage Queue Data Message Sender",
                    "Storage Queue Data Reader",
                    "Storage Table Data Contributor",
                    "Storage Table Data Reader",
                    "User Access Administrator",
                ],
            ]
        ],
    ]
    """Array of role assignments to create for user-assigned identity."""
    user_roles: Union[
        Parameter,
        List[
            Union[
                Parameter,
                "RoleAssignment",
                Literal[
                    "Contributor",
                    "Owner",
                    "Reader",
                    "Reader and Data Access",
                    "Role Based Access Control Administrator",
                    "Storage Account Backup Contributor",
                    "Storage Account Contributor",
                    "Storage Account Key Operator Service Role",
                    "Storage Blob Data Contributor",
                    "Storage Blob Data Owner",
                    "Storage Blob Data Reader",
                    "Storage Blob Delegator",
                    "Storage File Data Privileged Contributor",
                    "Storage File Data Privileged Reader",
                    "Storage File Data SMB Share Contributor",
                    "Storage File Data SMB Share Elevated Contributor",
                    "Storage File Data SMB Share Reader",
                    "Storage Queue Data Contributor",
                    "Storage Queue Data Message Processor",
                    "Storage Queue Data Message Sender",
                    "Storage Queue Data Reader",
                    "Storage Table Data Contributor",
                    "Storage Table Data Reader",
                    "User Access Administrator",
                ],
            ]
        ],
    ]
    """Array or role assignments to create for user principal ID"""
    # TODO: support timedelta
    sas_expiration_period: Union[str, Parameter]
    """The SAS expiration period. DD.HH:MM:SS."""
    sku: Union[
        Literal[
            "Premium_LRS",
            "Premium_ZRS",
            "Standard_GRS",
            "Standard_GZRS",
            "Standard_LRS",
            "Standard_RAGRS",
            "Standard_RAGZRS",
            "Standard_ZRS",
        ],
        Parameter,
    ]
    """Storage Account Sku Name."""
    supports_https_traffic_only: Union[bool, Parameter]
    """Allows HTTPS traffic only to storage service if sets to true."""
    tags: Union[Dict[str, Union[str, Parameter]], Parameter]
    """Tags of the resource."""


StorageAccountResourceType = TypeVar(
    "StorageAccountResourceType", bound=Mapping[str, Any], default="StorageAccountResource"
)
_DEFAULT_STORAGE_ACCOUNT: "StorageAccountResource" = {
    "name": GLOBAL_PARAMS["defaultName"],
    "location": GLOBAL_PARAMS["location"],
    "tags": GLOBAL_PARAMS["azdTags"],
    "kind": "StorageV2",
    "sku": {"name": "Standard_GRS"},
    "properties": {"accessTier": "Hot", "allowCrossTenantReplication": False, "allowSharedKeyAccess": False},
    "identity": {"type": "UserAssigned", "userAssignedIdentities": {GLOBAL_PARAMS["managedIdentityId"]: {}}},
}


class StorageAccount(Resource, Generic[StorageAccountResourceType]):
    DEFAULTS: "StorageAccountResource" = _DEFAULT_STORAGE_ACCOUNT  # type: ignore[assignment]
    properties: StorageAccountResourceType
    parent: None  # type: ignore[reportIncompatibleVariableOverride]

    def __init__(  # pylint: disable=too-many-branches,too-many-statements
        self,
        properties: Optional["StorageAccountResource"] = None,
        /,
        name: Optional[Union[str, Parameter]] = None,
        **kwargs: Unpack[StorageAccountKwargs],
    ) -> None:
        # 'existing' is passed by the reference classmethod.
        existing = kwargs.pop("existing", False)  # type: ignore[typeddict-item]
        extensions: ExtensionResources = defaultdict(list)  # type: ignore  # Doesn't like the default dict.
        if "roles" in kwargs:
            extensions["managed_identity_roles"] = kwargs.pop("roles")
        if "user_roles" in kwargs:
            extensions["user_roles"] = kwargs.pop("user_roles")
        if not existing:
            properties = properties or {}
            if "properties" not in properties:
                properties["properties"] = {}
            if name:
                properties["name"] = name
            if "access_tier" in kwargs:
                properties["properties"]["accessTier"] = kwargs.pop("access_tier")
            if "enable_hierarchical_namespace" in kwargs:
                properties["properties"]["isHnsEnabled"] = kwargs.pop("enable_hierarchical_namespace")
            if "allow_blob_public_access" in kwargs:
                properties["properties"]["allowBlobPublicAccess"] = kwargs.pop("allow_blob_public_access")
            if "allow_cross_tenant_replication" in kwargs:
                properties["properties"]["allowCrossTenantReplication"] = kwargs.pop("allow_cross_tenant_replication")
            if "allowed_copy_scope" in kwargs:
                properties["properties"]["allowedCopyScope"] = kwargs.pop("allowed_copy_scope")
            if "allow_shared_key_access" in kwargs:
                properties["properties"]["allowSharedKeyAccess"] = kwargs.pop("allow_shared_key_access")
            if "custom_domain_name" in kwargs:
                properties["properties"]["customDomain"] = {"name": kwargs.pop("custom_domain_name")}
            if "custom_domain_use_subdomain_name" in kwargs:
                try:
                    # This wont work if "customDomain" is a Parameter, so catch the TypeError
                    properties["properties"]["customDomain"]["useSubDomainName"] = kwargs.pop(  # type: ignore[index]
                        "custom_domain_use_subdomain_name"
                    )
                except (KeyError, TypeError) as e:
                    raise ValueError(
                        "Cannot set 'custom_domain_use_subdomain_name' if 'custom_domain_name' not present."
                    ) from e
            if "default_to_oauth_authentication" in kwargs:
                properties["properties"]["defaultToOAuthAuthentication"] = kwargs.pop("default_to_oauth_authentication")
            if "dns_endpoint_type" in kwargs:
                properties["properties"]["dnsEndpointType"] = kwargs.pop("dns_endpoint_type")
            if "enable_nfs_v3" in kwargs:
                properties["properties"]["isNfsV3Enabled"] = kwargs.pop("enable_nfs_v3")
            if "enable_sftp" in kwargs:
                properties["properties"]["isSftpEnabled"] = kwargs.pop("enable_sftp")
            if "is_local_user_enabled" in kwargs:
                properties["properties"]["isLocalUserEnabled"] = kwargs.pop("is_local_user_enabled")
            if "kind" in kwargs:
                properties["kind"] = kwargs.pop("kind")
            if "location" in kwargs:
                properties["location"] = kwargs.pop("location")
            if "managed_identities" in kwargs:
                properties["identity"] = convert_managed_identities(kwargs.pop("managed_identities"))
            if "minimum_tls_version" in kwargs:
                properties["properties"]["minimumTlsVersion"] = kwargs.pop("minimum_tls_version")
            if "network_acls" in kwargs:
                properties["properties"]["networkAcls"] = kwargs.pop("network_acls")
            if "public_network_access" in kwargs:
                properties["properties"]["publicNetworkAccess"] = kwargs.pop("public_network_access")
            if "sas_expiration_period" in kwargs:
                properties["properties"]["sasPolicy"] = {
                    "sasExpirationPeriod": kwargs.pop("sas_expiration_period"),
                    "expirationAction": "Block",
                }
            if "sku" in kwargs:
                properties["sku"] = {"name": kwargs.pop("sku")}
            if "supports_https_traffic_only" in kwargs:
                properties["properties"]["supportsHttpsTrafficOnly"] = kwargs.pop("supports_https_traffic_only")
            if "tags" in kwargs:
                properties["tags"] = kwargs.pop("tags")

        super().__init__(
            properties,
            extensions=extensions,
            service_prefix=["storage"],
            existing=existing,
            identifier=ResourceIdentifiers.storage_account,
            **kwargs,
        )

    @property
    def resource(self) -> Literal["Microsoft.Storage/storageAccounts"]:
        return "Microsoft.Storage/storageAccounts"

    @property
    def version(self) -> str:
        from .types import VERSION

        return VERSION

    @classmethod
    def reference(  # type: ignore[override]  # Parameter subset and renames
        cls,
        *,
        name: Union[str, Parameter],
        resource_group: Optional[Union[str, Parameter, ResourceGroup[ResourceReference]]] = None,
    ) -> "StorageAccount[ResourceReference]":
        existing = super().reference(name=name, resource_group=resource_group)
        return cast(StorageAccount[ResourceReference], existing)
