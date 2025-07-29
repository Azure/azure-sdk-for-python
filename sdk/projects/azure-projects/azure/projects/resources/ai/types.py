# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=line-too-long

from typing import Literal, List, Dict, Union
from typing_extensions import Required, TypedDict

from ..._bicep.expressions import Parameter


VERSION = "2024-10-01"


class CognitiveServicesIdentity(TypedDict, total=False):
    type: Required[Union[Literal["None", "SystemAssigned", "SystemAssigned,UserAssigned", "UserAssigned"], Parameter]]
    """The identity type."""
    userAssignedIdentities: Dict[Union[str, Parameter], Dict]
    """The set of user assigned identities associated with the resource."""


class CognitiveServicesIpRule(TypedDict, total=False):
    value: Required[Union[str, Parameter]]
    """An IPv4 address range in CIDR notation, such as '124.56.78.91' (simple IP address) or '124.56.78.0/24' (all addresses that start with 124.56.78)."""


class CognitiveServicesSku(TypedDict, total=False):
    capacity: Union[int, Parameter]
    """If the SKU supports scale out/in then the capacity integer should be included. If scale out/in is not possible for the resource this may be omitted."""
    family: Union[str, Parameter]
    """If the service has different generations of hardware, for the same SKU, then that can be captured here."""
    name: Required[Union[str, Parameter]]
    """The name of the SKU. Ex - P3. It is typically a letter+number code."""
    size: Union[str, Parameter]
    """The SKU size. When the name field is the combination of tier and some other value, this would be the standalone code."""
    tier: Union[Parameter, Literal["Basic", "Enterprise", "Free", "Premium", "Standard"]]
    """This field is required to be implemented by the Resource Provider if the service has more than one tier, but is not required on a PUT."""


class KeyVaultProperties(TypedDict, total=False):
    identityClientId: Union[str, Parameter]
    """The identity client Id to access the Key Vault."""
    keyName: Union[str, Parameter]
    """Name of the Key from KeyVault."""
    keyVaultUri: Union[str, Parameter]
    """Uri of KeyVault."""
    keyVersion: Union[str, Parameter]
    """Version of the Key from KeyVault"""


class CognitiveServicesEncryption(TypedDict, total=False):
    keySource: Union[Parameter, Literal["Microsoft.CognitiveServices", "Microsoft.KeyVault"]]
    """Enumerates the possible value of keySource for Encryption."""
    keyVaultProperties: Union[Parameter, KeyVaultProperties]
    """Properties of KeyVault."""


class VirtualNetworkRule(TypedDict, total=False):
    id: Required[Union[str, Parameter]]
    """Full resource id of a vnet subnet, such as '/subscriptions/subid/resourceGroups/rg1/providers/Microsoft.Network/virtualNetworks/test-vnet/subnets/subnet1'."""
    ignoreMissingVnetServiceEndpoint: Union[bool, Parameter]
    """Ignore missing vnet service endpoint or not."""


class CognitiveServicesNetworkRuleSet(TypedDict, total=False):
    bypass: Union[Parameter, Literal["AzureServices", "None"]]
    """Setting for trusted services."""
    defaultAction: Union[Parameter, Literal["Allow", "Deny"]]
    """The default action when no rule from ipRules and from virtualNetworkRules match. This is only used after the bypass property has been evaluated."""
    ipRules: Union[
        Parameter,
        List[Union[CognitiveServicesIpRule, Parameter]],
    ]
    """The list of IP address rules."""
    virtualNetworkRules: Union[Parameter, List[Union[VirtualNetworkRule, Parameter]]]
    """The list of virtual network rules."""


class RegionSetting(TypedDict, total=False):
    customsubdomain: Union[str, Parameter]
    """Maps the region to the regional custom subdomain."""
    name: Union[str, Parameter]
    """Name of the region."""
    value: Union[int, Parameter]
    """A value for priority or weighted routing methods."""


class MultiRegionSettings(TypedDict, total=False):
    regions: Union[Parameter, List[Union[Parameter, RegionSetting]]]
    routingMethod: Union[Parameter, Literal["Performance", "Priority", "Weighted"]]
    """Multiregion routing methods."""


class RaiMonitorConfig(TypedDict, total=False):
    adxStorageResourceId: Union[str, Parameter]
    """The storage resource Id."""
    identityClientId: Union[str, Parameter]
    """The identity client Id to access the storage."""


class UserOwnedAmlWorkspace(TypedDict, total=False):
    identityClientId: Union[str, Parameter]
    """Identity Client id of a AML workspace resource."""
    resourceId: Union[str, Parameter]
    """Full resource id of a AML workspace resource."""


class UserOwnedStorage(TypedDict, total=False):
    identityClientId: Union[str, Parameter]
    """The identity client Id to access the storage."""
    resourceId: Union[str, Parameter]
    """Full resource id of a Microsoft.Storage resource."""


class ApiProperties(TypedDict, total=False):
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


class CognitiveServicesAccountProperties(TypedDict, total=False):
    allowedFqdnList: Union[List[Union[str, Parameter]], Parameter]
    """List of allowed FQDN."""
    amlWorkspace: Union[UserOwnedAmlWorkspace, Parameter]
    """The user owned AML workspace properties."""
    apiProperties: Union[ApiProperties, Parameter]
    """The api properties for special APIs."""
    customSubDomainName: Union[str, Parameter]
    """Optional subdomain name used for token-based authentication."""
    disableLocalAuth: Union[bool, Parameter]
    """Allow only Azure AD authentication. Should be enabled for security reasons."""
    dynamicThrottlingEnabled: Union[bool, Parameter]
    """The flag to enable dynamic throttling."""
    encryption: Union[CognitiveServicesEncryption, Parameter]
    """The encryption properties for this resource."""
    locations: Union[MultiRegionSettings, Parameter]
    """The multiregion settings of Cognitive Services account."""
    migrationToken: Union[str, Parameter]
    """Resource migration token."""
    networkAcls: Union[CognitiveServicesNetworkRuleSet, Parameter]
    """A collection of rules governing the accessibility from specific network locations."""
    publicNetworkAccess: Union[Literal["Disabled", "Enabled"], Parameter]
    """Whether or not public endpoint access is allowed for this account."""
    raiMonitorConfig: Union[RaiMonitorConfig, Parameter]
    """Cognitive Services Rai Monitor Config."""
    restore: Union[bool, Parameter]
    """Restore a soft-deleted cognitive service at deployment time. Will fail if no such soft-deleted resource exists."""
    restrictOutboundNetworkAccess: Union[bool, Parameter]
    """Restrict outbound network access."""
    userOwnedStorage: Union[List[Union[UserOwnedStorage, Parameter]], Parameter]
    """The storage accounts for this resource."""


class CognitiveServicesAccountResource(TypedDict, total=False):
    identity: "CognitiveServicesIdentity"
    """Identity for the resource."""
    kind: Union[
        Literal[
            "AIServices",
            "AnomalyDetector",
            "CognitiveServices",
            "ComputerVision",
            "ContentModerator",
            "ContentSafety",
            "ConversationalLanguageUnderstanding",
            "CustomVision.Prediction",
            "CustomVision.Training",
            "Face",
            "FormRecognizer",
            "HealthInsights",
            "ImmersiveReader",
            "Internal.AllInOne",
            "LanguageAuthoring",
            "LUIS",
            "LUIS.Authoring",
            "MetricsAdvisor",
            "OpenAI",
            "Personalizer",
            "QnAMaker.v2",
            "SpeechServices",
            "TextAnalytics",
            "TextTranslation",
        ],
        Parameter,
    ]
    """The Kind of the resource."""
    location: Union[str, Parameter]
    """The geo-location where the resource lives."""
    name: Union[str, Parameter]
    """The resource name."""
    properties: "CognitiveServicesAccountProperties"
    """Properties of Cognitive Services account."""
    sku: Union["CognitiveServicesSku", Parameter]
    """The resource model definition representing SKU"""
    tags: Union[Dict[str, Union[str, Parameter]], Parameter]
    """Dictionary of tag names and values. See Tags in templates"""
