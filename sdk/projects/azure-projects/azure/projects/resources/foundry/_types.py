# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=line-too-long

from __future__ import annotations
from typing import Literal, TypedDict, Union, Any

from ..._bicep.expressions import Parameter


VERSION = '2025-01-01-preview'


class MachineLearningWorkspaceComputeRuntimeDto(TypedDict, total=False):
    sparkRuntimeVersion: Union[str, Parameter]
    """"""


class MachineLearningWorkspaceCosmosDbSettings(TypedDict, total=False):
    collectionsThroughput: Union[int, Parameter]
    """"""


class MachineLearningWorkspaceEncryptionProperty(TypedDict, total=False):
    cosmosDbResourceId: Union[str, Parameter]
    """The byok cosmosdb account that customer brings to store customer's datawith encryption"""
    identity: Union[MachineLearningWorkspaceIdentityForCmk, Parameter]
    """Identity to be used with the keyVault"""
    keyVaultProperties: Union[MachineLearningWorkspaceKeyVaultProperties, Parameter]
    """KeyVault details to do the encryption"""
    searchAccountResourceId: Union[str, Parameter]
    """The byok search account that customer brings to store customer's datawith encryption"""
    status: Union[Literal['Disabled', 'Enabled'], Parameter]
    """Indicates whether or not the encryption is enabled for the workspace."""
    storageAccountResourceId: Union[str, Parameter]
    """The byok storage account that customer brings to store customer's datawith encryption"""


class MachineLearningWorkspaceFeatureStoreSettings(TypedDict, total=False):
    computeRuntime: Union[MachineLearningWorkspaceComputeRuntimeDto, Parameter]
    """"""
    offlineStoreConnectionName: Union[str, Parameter]
    """"""
    onlineStoreConnectionName: Union[str, Parameter]
    """"""


class MachineLearningWorkspaceFqdnOutboundRule(TypedDict, total=False):
    destination: Union[str, Parameter]
    """"""
    type: Union[Literal['FQDN'], Parameter]
    """Type of a managed network Outbound Rule of a machine learning workspace."""


class MachineLearningWorkspaceIdentityForCmk(TypedDict, total=False):
    userAssignedIdentity: Union[str, Parameter]
    """UserAssignedIdentity to be used to fetch the encryption key from keyVault"""


class MachineLearningWorkspaceIPRule(TypedDict, total=False):
    value: Union[str, Parameter]
    """An IPv4 address range in CIDR notation, such as '124.56.78.91' (simple IP address) or '124.56.78.0/24' (all addresses that start with 124.56.78). Value could be 'Allow' or  'Deny'."""


class MachineLearningWorkspaceKeyVaultProperties(TypedDict, total=False):
    identityClientId: Union[str, Parameter]
    """Currently, we support only SystemAssigned MSI.We need this when we support UserAssignedIdentities"""
    keyIdentifier: Union[str, Parameter]
    """KeyVault key identifier to encrypt the data"""
    keyVaultArmId: Union[str, Parameter]
    """KeyVault Arm Id that contains the data encryption key"""


class MachineLearningWorkspaceManagedNetworkProvisionStatus(TypedDict, total=False):
    sparkReady: Union[bool, Parameter]
    """"""
    status: Union[Literal['Inactive', 'Active'], Parameter]
    """Status for the managed network of a machine learning workspace."""


class MachineLearningWorkspaceManagedNetworkSettings(TypedDict, total=False):
    firewallSku: Union[Literal['Basic', 'Standard'], Parameter]
    """Firewall Sku used for FQDN Rules"""
    isolationMode: Union[Literal['AllowInternetOutbound', 'Disabled', 'AllowOnlyApprovedOutbound'], Parameter]
    """Isolation mode for the managed network of a machine learning workspace."""
    outboundRules: Union[dict[str, Any], Parameter]
    """Dictionary of <OutboundRule>"""
    status: Union[MachineLearningWorkspaceManagedNetworkProvisionStatus, Parameter]
    """Status of the Provisioning for the managed network of a machine learning workspace."""


class MachineLearningWorkspaceManagedServiceIdentity(TypedDict, total=False):
    type: Union[Literal['UserAssigned', 'None', 'SystemAssigned', 'SystemAssigned,UserAssigned'], Parameter]
    """Type of managed service identity (where both SystemAssigned and UserAssigned types are allowed)."""
    userAssignedIdentities: dict[Union[str, Parameter], Union[dict, Parameter]]
    """The set of user assigned identities associated with the resource. The userAssignedIdentities dictionary keys will be ARM resource ids in the form: '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{identityName}. The dictionary values can be empty objects ({}) in requests."""


class MachineLearningWorkspaceResource(TypedDict, total=False):
    identity: Union[MachineLearningWorkspaceManagedServiceIdentity, Parameter]
    """Managed service identity (system assigned and/or user assigned identities)"""
    kind: Union[str, Parameter]
    """"""
    location: Union[str, Parameter]
    """"""
    name: Union[str, Parameter]
    """The resource name"""
    properties: Union[MachineLearningWorkspaceWorkspaceProperties, Parameter]
    """Additional attributes of the entity."""
    sku: Union[MachineLearningWorkspaceSku, Parameter]
    """Optional. This field is required to be implemented by the RP because AML is supporting more than one tier"""
    tags: Union[dict[str, Union[str, Parameter]], Parameter]
    """Resource tags"""


class MachineLearningWorkspaceNetworkAcls(TypedDict, total=False):
    defaultAction: Union[Literal['Allow', 'Deny'], Parameter]
    """The default action when no rule from ipRules and from virtualNetworkRules match. This is only used after the bypass property has been evaluated."""
    ipRules: Union[list[MachineLearningWorkspaceIPRule], Parameter]
    """Rules governing the accessibility of a resource from a specific ip address or ip range."""


class MachineLearningWorkspaceOutboundRule(TypedDict, total=False):
    category: Union[Literal['Dependency', 'UserDefined', 'Recommended', 'Required'], Parameter]
    """Category of a managed network Outbound Rule of a machine learning workspace."""
    status: Union[Literal['Inactive', 'Active'], Parameter]
    """Type of a managed network Outbound Rule of a machine learning workspace."""
    type: Union[Literal['PrivateEndpoint', 'FQDN', 'ServiceTag'], Parameter]
    """Set to 'FQDN' for type FqdnOutboundRule. Set to 'PrivateEndpoint' for type PrivateEndpointOutboundRule. Set to 'ServiceTag' for type ServiceTagOutboundRule."""


class MachineLearningWorkspacePrivateEndpointDestination(TypedDict, total=False):
    serviceResourceId: Union[str, Parameter]
    """"""
    sparkEnabled: Union[bool, Parameter]
    """"""
    sparkStatus: Union[Literal['Inactive', 'Active'], Parameter]
    """Type of a managed network Outbound Rule of a machine learning workspace."""
    subresourceTarget: Union[str, Parameter]
    """"""


class MachineLearningWorkspacePrivateEndpointOutboundRule(TypedDict, total=False):
    destination: Union[MachineLearningWorkspacePrivateEndpointDestination, Parameter]
    """Private Endpoint destination for a Private Endpoint Outbound Rule for the managed network of a machine learning workspace."""
    fqdns: Union[list[Union[str, Parameter]], Parameter]
    """"""
    type: Union[Literal['PrivateEndpoint'], Parameter]
    """Type of a managed network Outbound Rule of a machine learning workspace."""


class MachineLearningWorkspaceServerlessComputeSettings(TypedDict, total=False):
    serverlessComputeCustomSubnet: Union[str, Parameter]
    """The resource ID of an existing virtual network subnet in which serverless compute nodes should be deployed"""
    serverlessComputeNoPublicIP: Union[bool, Parameter]
    """The flag to signal if serverless compute nodes deployed in custom vNet would have no public IP addresses for a workspace with private endpoint"""


class MachineLearningWorkspaceServiceManagedResourcesSettings(TypedDict, total=False):
    cosmosDb: Union[MachineLearningWorkspaceCosmosDbSettings, Parameter]
    """"""


class MachineLearningWorkspaceServiceTagDestination(TypedDict, total=False):
    action: Union[Literal['Allow', 'Deny'], Parameter]
    """The action enum for networking rule."""
    addressPrefixes: Union[list[Union[str, Parameter]], Parameter]
    """Optional, if provided, the ServiceTag property will be ignored."""
    portRanges: Union[str, Parameter]
    """"""
    protocol: Union[str, Parameter]
    """"""
    serviceTag: Union[str, Parameter]
    """"""


class MachineLearningWorkspaceServiceTagOutboundRule(TypedDict, total=False):
    destination: Union[MachineLearningWorkspaceServiceTagDestination, Parameter]
    """Service Tag destination for a Service Tag Outbound Rule for the managed network of a machine learning workspace."""
    type: Union[Literal['ServiceTag'], Parameter]
    """Type of a managed network Outbound Rule of a machine learning workspace."""


class MachineLearningWorkspaceSharedPrivateLinkResource(TypedDict, total=False):
    name: Union[str, Parameter]
    """Unique name of the private link"""
    properties: Union[MachineLearningWorkspaceSharedPrivateLinkResource, Parameter]
    """Properties of a shared private link resource."""


class MachineLearningWorkspaceSharedPrivateLinkResourceProperty(TypedDict, total=False):
    groupId: Union[str, Parameter]
    """group id of the private link"""
    privateLinkResourceId: Union[str, Parameter]
    """the resource id that private link links to"""
    requestMessage: Union[str, Parameter]
    """Request message"""
    status: Union[Literal['Disconnected', 'Approved', 'Rejected', 'Pending', 'Timeout'], Parameter]
    """Connection status of the service consumer with the service provider"""


class MachineLearningWorkspaceSku(TypedDict, total=False):
    capacity: Union[int, Parameter]
    """If the SKU supports scale out/in then the capacity integer should be included. If scale out/in is not possible for the resource this may be omitted."""
    family: Union[str, Parameter]
    """If the service has different generations of hardware, for the same SKU, then that can be captured here."""
    name: Union[str, Parameter]
    """The name of the SKU. Ex - P3. It is typically a letter+number code"""
    size: Union[str, Parameter]
    """The SKU size. When the name field is the combination of tier and some other value, this would be the standalone code."""
    tier: Union[Literal['Premium', 'Basic', 'Free', 'Standard'], Parameter]
    """This field is required to be implemented by the Resource Provider if the service has more than one tier, but is not required on a PUT."""


class MachineLearningWorkspaceWorkspaceHubConfig(TypedDict, total=False):
    additionalWorkspaceStorageAccounts: Union[list[Union[str, Parameter]], Parameter]
    """"""
    defaultWorkspaceResourceGroup: Union[str, Parameter]
    """"""


class MachineLearningWorkspaceWorkspaceProperties(TypedDict, total=False):
    allowPublicAccessWhenBehindVnet: Union[bool, Parameter]
    """The flag to indicate whether to allow public access when behind VNet."""
    allowRoleAssignmentOnRG: Union[bool, Parameter]
    """The flag to indicate whether we will do role assignment for the workspace MSI on resource group level."""
    applicationInsights: Union[str, Parameter]
    """ARM id of the application insights associated with this workspace."""
    associatedWorkspaces: Union[list[Union[str, Parameter]], Parameter]
    """"""
    containerRegistries: Union[list[Union[str, Parameter]], Parameter]
    """"""
    containerRegistry: Union[str, Parameter]
    """ARM id of the container registry associated with this workspace."""
    description: Union[str, Parameter]
    """The description of this workspace."""
    discoveryUrl: Union[str, Parameter]
    """Url for the discovery service to identify regional endpoints for machine learning experimentation services"""
    enableDataIsolation: Union[bool, Parameter]
    """"""
    enableServiceSideCMKEncryption: Union[bool, Parameter]
    """"""
    enableSimplifiedCmk: Union[bool, Parameter]
    """Flag to tell if simplified CMK should be enabled for this workspace."""
    enableSoftwareBillOfMaterials: Union[bool, Parameter]
    """Flag to tell if SoftwareBillOfMaterials should be enabled for this workspace."""
    encryption: Union[MachineLearningWorkspaceEncryptionProperty, Parameter]
    """"""
    existingWorkspaces: Union[list[Union[str, Parameter]], Parameter]
    """"""
    featureStoreSettings: Union[MachineLearningWorkspaceFeatureStoreSettings, Parameter]
    """Settings for feature store type workspace."""
    friendlyName: Union[str, Parameter]
    """The friendly name for this workspace. This name in mutable"""
    hbiWorkspace: Union[bool, Parameter]
    """The flag to signal HBI data in the workspace and reduce diagnostic data collected by the service"""
    hubResourceId: Union[str, Parameter]
    """"""
    imageBuildCompute: Union[str, Parameter]
    """The compute name for image build"""
    ipAllowlist: Union[list[Union[str, Parameter]], Parameter]
    """The list of IPv4  addresses that are allowed to access the workspace."""
    keyVault: Union[str, Parameter]
    """ARM id of the key vault associated with this workspace. This cannot be changed once the workspace has been created"""
    keyVaults: Union[list[Union[str, Parameter]], Parameter]
    """"""
    managedNetwork: Union[MachineLearningWorkspaceManagedNetworkSettings, Parameter]
    """Managed Network settings for a machine learning workspace."""
    networkAcls: Union[MachineLearningWorkspaceNetworkAcls, Parameter]
    """A set of rules governing the network accessibility of the workspace."""
    primaryUserAssignedIdentity: Union[str, Parameter]
    """The user assigned identity resource id that represents the workspace identity."""
    provisionNetworkNow: Union[bool, Parameter]
    """Set to trigger the provisioning of the managed VNet with the default Options when creating a Workspace with the managed VNet enabled, or else it does nothing."""
    publicNetworkAccess: Union[Literal['Disabled', 'Enabled'], Parameter]
    """Whether requests from Public Network are allowed."""
    serverlessComputeSettings: Union[MachineLearningWorkspaceServerlessComputeSettings, Parameter]
    """Settings for serverless compute in a workspace"""
    serviceManagedResourcesSettings: Union[MachineLearningWorkspaceServiceManagedResourcesSettings, Parameter]
    """The service managed resource settings."""
    sharedPrivateLinkResources: Union[list[MachineLearningWorkspaceSharedPrivateLinkResource], Parameter]
    """The list of shared private link resources in this workspace."""
    softDeleteRetentionInDays: Union[int, Parameter]
    """Retention time in days after workspace get soft deleted."""
    storageAccount: Union[str, Parameter]
    """ARM id of the storage account associated with this workspace. This cannot be changed once the workspace has been created"""
    storageAccounts: Union[list[Union[str, Parameter]], Parameter]
    """"""
    systemDatastoresAuthMode: Union[Literal['UserDelegationSAS', 'AccessKey', 'Identity'], Parameter]
    """The auth mode used for accessing the system datastores of the workspace."""
    v1LegacyMode: Union[bool, Parameter]
    """Enabling v1_legacy_mode may prevent you from using features provided by the v2 API."""
    workspaceHubConfig: Union[MachineLearningWorkspaceWorkspaceHubConfig, Parameter]
    """WorkspaceHub's configuration object."""
