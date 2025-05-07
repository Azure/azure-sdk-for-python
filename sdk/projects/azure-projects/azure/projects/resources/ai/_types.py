# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=line-too-long, name-too-long

from __future__ import annotations
from typing import Literal, TypedDict, Union

from ..._bicep.expressions import Parameter
from .._extension import Identity


VERSION = "2024-10-01"


class CognitiveServicesAccountProperties(TypedDict, total=False):
    allowedFqdnList: Union[list[Union[str, Parameter]], Parameter]
    """"""
    allowProjectManagement: Union[bool, Parameter]
    """Specifies whether this resource support project management as child resources, used as containers for access management, data isolation and cost in AI Foundry."""
    amlWorkspace: Union[CognitiveServicesAccountUserOwnedAmlWorkspace, Parameter]
    """The user owned AML account properties."""
    apiProperties: Union[CognitiveServicesAccountApiProperties, Parameter]
    """The api properties for special APIs."""
    associatedProjects: Union[list[Union[str, Parameter]], Parameter]
    """Specifies the projects that are associated with this resource."""
    customSubDomainName: Union[str, Parameter]
    """Optional subdomain name used for token-based authentication."""
    defaultProject: Union[str, Parameter]
    """Specifies the project that is targeted when data plane endpoints are called without a project parameter."""
    disableLocalAuth: Union[bool, Parameter]
    """"""
    dynamicThrottlingEnabled: Union[bool, Parameter]
    """The flag to enable dynamic throttling."""
    encryption: Union[CognitiveServicesAccountEncryption, Parameter]
    """The encryption properties for this resource."""
    locations: Union[CognitiveServicesAccountMultiRegionSettings, Parameter]
    """The multiregion settings of Cognitive Services account."""
    migrationToken: Union[str, Parameter]
    """Resource migration token."""
    networkAcls: Union[CognitiveServicesAccountNetworkRuleSet, Parameter]
    """A collection of rules governing the accessibility from specific network locations."""
    networkInjections: Union[CognitiveServicesAccountNetworkInjections, Parameter]
    """Specifies in AI Foundry where virtual network injection occurs to secure scenarios like Agents entirely within the user's private network, eliminating public internet exposure while maintaining control over network configurations and resources."""
    publicNetworkAccess: Union[Literal["Enabled", "Disabled"], Parameter]
    """Whether or not public endpoint access is allowed for this account."""
    raiMonitorConfig: Union[CognitiveServicesAccountRaiMonitorConfig, Parameter]
    """Cognitive Services Rai Monitor Config."""
    restore: Union[bool, Parameter]
    """"""
    restrictOutboundNetworkAccess: Union[bool, Parameter]
    """"""
    userOwnedStorage: Union[list[CognitiveServicesAccountUserOwnedStorage], Parameter]
    """The storage accounts for this resource."""


class CognitiveServicesAccountApiProperties(TypedDict, total=False):
    aadClientId: Union[str, Parameter]
    """(Metrics Advisor Only) The Azure AD Client Id (Application Id)."""
    aadTenantId: Union[str, Parameter]
    """(Metrics Advisor Only) The Azure AD Tenant Id."""
    eventHubConnectionString: Union[str, Parameter]
    """(Personalization Only) The flag to enable statistics of Bing Search."""
    qnaAzureSearchEndpointId: Union[str, Parameter]
    """(QnAMaker Only) The Azure Search endpoint id of QnAMaker."""
    qnaAzureSearchEndpointKey: Union[str, Parameter]
    """(QnAMaker Only) The Azure Search endpoint key of QnAMaker."""
    qnaRuntimeEndpoint: Union[str, Parameter]
    """(QnAMaker Only) The runtime endpoint of QnAMaker."""
    statisticsEnabled: Union[bool, Parameter]
    """(Bing Search Only) The flag to enable statistics of Bing Search."""
    storageAccountConnectionString: Union[str, Parameter]
    """(Personalization Only) The storage account connection string."""
    superUser: Union[str, Parameter]
    """(Metrics Advisor Only) The super user of Metrics Advisor."""
    websiteName: Union[str, Parameter]
    """(Metrics Advisor Only) The website name of Metrics Advisor."""


class CognitiveServicesAccountEncryption(TypedDict, total=False):
    keySource: Union[Literal["Microsoft.CognitiveServices", "Microsoft.KeyVault"], Parameter]
    """Enumerates the possible value of keySource for Encryption"""
    keyVaultProperties: Union[CognitiveServicesAccountKeyVaultProperties, Parameter]
    """Properties of KeyVault"""


class CognitiveServicesAccountIpRule(TypedDict, total=False):
    value: Union[str, Parameter]
    """An IPv4 address range in CIDR notation, such as '124.56.78.91' (simple IP address) or '124.56.78.0/24' (all addresses that start with 124.56.78)."""


class CognitiveServicesAccountKeyVaultProperties(TypedDict, total=False):
    identityClientId: Union[str, Parameter]
    """"""
    keyName: Union[str, Parameter]
    """Name of the Key from KeyVault"""
    keyVaultUri: Union[str, Parameter]
    """Uri of KeyVault"""
    keyVersion: Union[str, Parameter]
    """Version of the Key from KeyVault"""


class CognitiveServicesAccountResource(TypedDict, total=False):
    identity: Union[Identity, Parameter]
    """Identity for the resource."""
    kind: Union[str, Parameter]
    """The Kind of the resource."""
    location: Union[str, Parameter]
    """The geo-location where the resource lives"""
    name: Union[str, Parameter]
    """The resource name"""
    properties: CognitiveServicesAccountProperties
    """Properties of Cognitive Services account."""
    sku: Union[CognitiveServicesAccountSku, Parameter]
    """The resource model definition representing SKU"""
    tags: dict[str, Union[None, str, Parameter]]
    """Resource tags"""


class CognitiveServicesAccountMultiRegionSettings(TypedDict, total=False):
    regions: Union[list[CognitiveServicesAccountRegionSetting], Parameter]
    """"""
    routingMethod: Union[Literal["Weighted", "Performance", "Priority"], Parameter]
    """Multiregion routing methods."""


class CognitiveServicesAccountNetworkInjections(TypedDict, total=False):
    scenario: Union[Literal["agent", "none"], Parameter]
    """Specifies what features in AI Foundry network injection applies to. Currently only supports 'agent' for agent scenarios. 'none' means no network injection."""
    subnetArmId: Union[str, Parameter]
    """Specify the subnet for which your Agent Client is injected into."""
    useMicrosoftManagedNetwork: Union[bool, Parameter]
    """Boolean to enable Microsoft Managed Network for subnet delegation"""


class CognitiveServicesAccountNetworkRuleSet(TypedDict, total=False):
    bypass: Union[Literal["AzureServices", "None"], Parameter]
    """Setting for trusted services."""
    defaultAction: Union[Literal["Deny", "Allow"], Parameter]
    """The default action when no rule from ipRules and from virtualNetworkRules match. This is only used after the bypass property has been evaluated."""
    ipRules: Union[list[CognitiveServicesAccountIpRule], Parameter]
    """The list of IP address rules."""
    virtualNetworkRules: Union[list[CognitiveServicesAccountVirtualNetworkRule], Parameter]
    """The list of virtual network rules."""


class CognitiveServicesAccountRaiMonitorConfig(TypedDict, total=False):
    adxStorageResourceId: Union[str, Parameter]
    """The storage resource Id."""
    identityClientId: Union[str, Parameter]
    """The identity client Id to access the storage."""


class CognitiveServicesAccountRegionSetting(TypedDict, total=False):
    customsubdomain: Union[str, Parameter]
    """Maps the region to the regional custom subdomain."""
    name: Union[str, Parameter]
    """Name of the region."""
    value: Union[int, Parameter]
    """A value for priority or weighted routing methods."""


class CognitiveServicesAccountSku(TypedDict, total=False):
    capacity: Union[int, Parameter]
    """If the SKU supports scale out/in then the capacity integer should be included. If scale out/in is not possible for the resource this may be omitted."""
    family: Union[str, Parameter]
    """If the service has different generations of hardware, for the same SKU, then that can be captured here."""
    name: Union[str, Parameter]
    """The name of the SKU. Ex - P3. It is typically a letter+number code"""
    size: Union[str, Parameter]
    """The SKU size. When the name field is the combination of tier and some other value, this would be the standalone code."""
    tier: Union[Literal["Basic", "Enterprise", "Standard", "Premium", "Free"], Parameter]
    """This field is required to be implemented by the Resource Provider if the service has more than one tier, but is not required on a PUT."""


class CognitiveServicesAccountUserOwnedAmlWorkspace(TypedDict, total=False):
    identityClientId: Union[str, Parameter]
    """Identity Client id of a AML account resource."""
    resourceId: Union[str, Parameter]
    """Full resource id of a AML account resource."""


class CognitiveServicesAccountUserOwnedStorage(TypedDict, total=False):
    identityClientId: Union[str, Parameter]
    """"""
    resourceId: Union[str, Parameter]
    """Full resource id of a Microsoft.Storage resource."""


class CognitiveServicesAccountVirtualNetworkRule(TypedDict, total=False):
    id: Union[str, Parameter]
    """Full resource id of a vnet subnet, such as '/subscriptions/subid/resourceGroups/rg1/providers/Microsoft.Network/virtualNetworks/test-vnet/subnets/subnet1'."""
    ignoreMissingVnetServiceEndpoint: Union[bool, Parameter]
    """Ignore missing vnet service endpoint or not."""
    state: Union[str, Parameter]
    """Gets the state of virtual network rule."""
