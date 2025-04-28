# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=line-too-long

from __future__ import annotations
from typing import TypedDict, Literal, Union

from ..._bicep.expressions import Parameter


VERSION = '2024-12-01-preview'


class KeyVaultAccessPolicyEntry(TypedDict, total=False):
    applicationId: Union[str, Parameter]
    """Application ID of the client making request on behalf of a principal"""
    objectId: Union[str, Parameter]
    """The object ID of a user, service principal or security group in the Azure Active Directory tenant for the vault. The object ID must be unique for the list of access policies."""
    permissions: Union[KeyVaultPermissions, Parameter]
    """Permissions the identity has for keys, secrets and certificates."""
    tenantId: Union[str, Parameter]
    """The Azure Active Directory tenant ID that should be used for authenticating requests to the key vault."""


class KeyVaultIPRule(TypedDict, total=False):
    value: Union[str, Parameter]
    """An IPv4 address range in CIDR notation, such as '124.56.78.91' (simple IP address) or '124.56.78.0/24' (all addresses that start with 124.56.78)."""


class KeyVaultResource(TypedDict, total=False):
    location: Union[str, Parameter]
    """The supported Azure location where the key vault should be created."""
    name: Union[str, Parameter]
    """The resource name"""
    properties: Union[KeyVaultVaultProperties, Parameter]
    """Properties of the vault"""
    tags: Union[dict[str, Union[str, Parameter]], Parameter]
    """Resource tags"""


class KeyVaultNetworkRuleSet(TypedDict, total=False):
    bypass: Union[Literal['None', 'AzureServices'], Parameter]
    """Tells what traffic can bypass network rules. This can be 'AzureServices' or 'None'.  If not specified the default is 'AzureServices'."""
    defaultAction: Union[Literal['Deny', 'Allow'], Parameter]
    """The default action when no rule from ipRules and from virtualNetworkRules match. This is only used after the bypass property has been evaluated."""
    ipRules: Union[list[KeyVaultIPRule], Parameter]
    """The list of IP address rules."""
    virtualNetworkRules: Union[list[KeyVaultVirtualNetworkRule], Parameter]
    """The list of virtual network rules."""


class KeyVaultPermissions(TypedDict, total=False):
    certificates: Union[Literal['restore', 'update', 'get', 'deleteissuers', 'recover', 'setissuers', 'purge', 'backup', 'all', 'delete', 'managecontacts', 'list', 'import', 'getissuers', 'create', 'listissuers', 'manageissuers'], Parameter]
    """Permissions to certificates"""
    keys: Union[Literal['verify', 'restore', 'recover', 'purge', 'backup', 'unwrapKey', 'import', 'create', 'release', 'get', 'getrotationpolicy', 'sign', 'wrapKey', 'rotate', 'list', 'setrotationpolicy', 'decrypt', 'update', 'all', 'delete', 'encrypt'], Parameter]
    """Permissions to keys"""
    secrets: Union[Literal['restore', 'get', 'recover', 'purge', 'backup', 'all', 'delete', 'list', 'set'], Parameter]
    """Permissions to secrets"""
    storage: Union[Literal['restore', 'update', 'get', 'recover', 'purge', 'backup', 'getsas', 'all', 'delete', 'list', 'set', 'listsas', 'setsas', 'regeneratekey', 'deletesas'], Parameter]
    """Permissions to storage accounts"""


class KeyVaultSku(TypedDict, total=False):
    family: Union[Literal['A'], Parameter]
    """SKU family name"""
    name: Union[Literal['premium', 'standard'], Parameter]
    """SKU name to specify whether the key vault is a standard vault or a premium vault."""


class KeyVaultVaultProperties(TypedDict, total=False):
    accessPolicies: Union[list[KeyVaultAccessPolicyEntry], Parameter]
    """An array of 0 to 1024 identities that have access to the key vault. All identities in the array must use the same tenant ID as the key vault's tenant ID. When createMode is set to recover, access policies are not required. Otherwise, access policies are required."""
    createMode: Union[Literal['default', 'recover'], Parameter]
    """The vault's create mode to indicate whether the vault need to be recovered or not."""
    enabledForDeployment: Union[bool, Parameter]
    """Property to specify whether Azure Virtual Machines are permitted to retrieve certificates stored as secrets from the key vault."""
    enabledForDiskEncryption: Union[bool, Parameter]
    """Property to specify whether Azure Disk Encryption is permitted to retrieve secrets from the vault and unwrap keys."""
    enabledForTemplateDeployment: Union[bool, Parameter]
    """Property to specify whether Azure Resource Manager is permitted to retrieve secrets from the key vault."""
    enablePurgeProtection: Union[bool, Parameter]
    """Property specifying whether protection against purge is enabled for this vault. Setting this property to true activates protection against purge for this vault and its content - only the Key Vault service may initiate a hard, irrecoverable deletion. The setting is effective only if soft delete is also enabled. Enabling this functionality is irreversible - that is, the property does not accept false as its value."""
    enableRbacAuthorization: Union[bool, Parameter]
    """Property that controls how data actions are authorized. When true, the key vault will use Role Based Access Control (RBAC) for authorization of data actions, and the access policies specified in vault properties will be  ignored. When false, the key vault will use the access policies specified in vault properties, and any policy stored on Azure Resource Manager will be ignored. If null or not specified, the vault is created with the default value of false. Note that management actions are always authorized with RBAC."""
    enableSoftDelete: Union[bool, Parameter]
    """Property to specify whether the 'soft delete' functionality is enabled for this key vault. If it's not set to any value(true or false) when creating new key vault, it will be set to true by default. Once set to true, it cannot be reverted to false."""
    networkAcls: Union[KeyVaultNetworkRuleSet, Parameter]
    """Rules governing the accessibility of the key vault from specific network locations."""
    provisioningState: Union[Literal['Succeeded', 'RegisteringDns'], Parameter]
    """Provisioning state of the vault."""
    publicNetworkAccess: Union[str, Parameter]
    """Property to specify whether the vault will accept traffic from public internet. If set to 'disabled' all traffic except private endpoint traffic and that that originates from trusted services will be blocked. This will override the set firewall rules, meaning that even if the firewall rules are present we will not honor the rules."""
    sku: Union[KeyVaultSku, Parameter]
    """SKU details"""
    softDeleteRetentionInDays: Union[int, Parameter]
    """softDelete data retention days. It accepts >=7 and <=90."""
    tenantId: Union[str, Parameter]
    """The Azure Active Directory tenant ID that should be used for authenticating requests to the key vault."""
    vaultUri: Union[str, Parameter]
    """The URI of the vault for performing operations on keys and secrets."""


class KeyVaultVirtualNetworkRule(TypedDict, total=False):
    id: Union[str, Parameter]
    """Full resource id of a vnet subnet, such as '/subscriptions/subid/resourceGroups/rg1/providers/Microsoft.Network/virtualNetworks/test-vnet/subnets/subnet1'."""
    ignoreMissingVnetServiceEndpoint: Union[bool, Parameter]
    """Property to specify whether NRP will ignore the check if parent subnet has serviceEndpoints configured."""
