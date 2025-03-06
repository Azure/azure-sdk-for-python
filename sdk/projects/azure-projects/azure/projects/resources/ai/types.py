from typing import TYPE_CHECKING, TypedDict, Literal, List, Dict, Union
from typing_extensions import Required

from ..._bicep.expressions import Parameter

RESOURCE = "Microsoft.CognitiveServices/accounts"
VERSION = "2024-10-01"


class Identity(TypedDict, total=False):
    type: Required[Union[Literal['None', 'SystemAssigned', 'SystemAssigned,UserAssigned','UserAssigned'], Parameter[str]]]
    """The identity type."""
    userAssignedIdentities: Dict[Union[str, Parameter[str]], Dict]
    """The set of user assigned identities associated with the resource."""


class IpRule(TypedDict, total=False):
    value: Required[Union[str, Parameter[str]]]
    """An IPv4 address range in CIDR notation, such as '124.56.78.91' (simple IP address) or '124.56.78.0/24' (all addresses that start with 124.56.78)."""


class Sku(TypedDict, total=False):
    capacity: Union[int, Parameter[int]]
    """If the SKU supports scale out/in then the capacity integer should be included. If scale out/in is not possible for the resource this may be omitted."""
    family: Union[str, Parameter[str]]
    """If the service has different generations of hardware, for the same SKU, then that can be captured here."""
    name: Required[Union[str, Parameter[str]]]
    """The name of the SKU. Ex - P3. It is typically a letter+number code."""
    size: Union[str, Parameter[str]]
    """The SKU size. When the name field is the combination of tier and some other value, this would be the standalone code."""
    tier: Union[Parameter[str], Literal['Basic', 'Enterprise', 'Free', 'Premium', 'Standard']]
    """This field is required to be implemented by the Resource Provider if the service has more than one tier, but is not required on a PUT."""


class KeyVaultProperties(TypedDict, total=False):
    identityClientId: Union[str, Parameter[str]]
    """The identity client Id to access the Key Vault."""
    keyName: Union[str, Parameter[str]]
    """Name of the Key from KeyVault."""
    keyVaultUri: Union[str, Parameter[str]]
    """Uri of KeyVault."""
    keyVersion: Union[str, Parameter[str]]
    """Version of the Key from KeyVault"""


class Encryption(TypedDict, total=False):
    keySource: Union[Parameter[str], Literal['Microsoft.CognitiveServices', 'Microsoft.KeyVault']]
    """Enumerates the possible value of keySource for Encryption."""
    keyVaultProperties: Union[Parameter[KeyVaultProperties], KeyVaultProperties]
    """Properties of KeyVault."""


class VirtualNetworkRule(TypedDict, total=False):
    id: Required[Union[str, Parameter[str]]]
    """Full resource id of a vnet subnet, such as '/subscriptions/subid/resourceGroups/rg1/providers/Microsoft.Network/virtualNetworks/test-vnet/subnets/subnet1'."""
    ignoreMissingVnetServiceEndpoint: Union[bool, Parameter[bool]]
    """Ignore missing vnet service endpoint or not."""


class NetworkRuleSet(TypedDict, total=False):
    bypass: Union[Parameter[str], Literal['AzureServices', 'None']]
    """Setting for trusted services."""
    defaultAction: Union[Parameter[str], Literal['Allow', 'Deny']]
    """The default action when no rule from ipRules and from virtualNetworkRules match. This is only used after the bypass property has been evaluated."""
    ipRules: Union[Parameter[List[IpRule]], List[Union[IpRule, Parameter[IpRule]]]]
    """The list of IP address rules."""
    virtualNetworkRules: Union[Parameter[List[VirtualNetworkRule]], List[Union[VirtualNetworkRule, Parameter[VirtualNetworkRule]]]]
    """The list of virtual network rules."""


class RegionSetting(TypedDict, total=False):
    customsubdomain: Union[str, Parameter[str]]
    """Maps the region to the regional custom subdomain."""
    name: Union[str, Parameter[str]]
    """Name of the region."""
    value: Union[int, Parameter[int]]
    """A value for priority or weighted routing methods."""


class MultiRegionSettings(TypedDict, total=False):
    regions: Union[Parameter[List[RegionSetting]], List[Union[Parameter[RegionSetting], RegionSetting]]]
    routingMethod: Union[Parameter[str], Literal['Performance', 'Priority', 'Weighted']]
    """Multiregion routing methods."""


class RaiMonitorConfig(TypedDict, total=False):
    adxStorageResourceId: Union[str, Parameter[str]]
    """The storage resource Id."""
    identityClientId: Union[str, Parameter[str]]
    """The identity client Id to access the storage."""


class UserOwnedAmlWorkspace(TypedDict, total=False):
    identityClientId: Union[str, Parameter[str]]
    """Identity Client id of a AML workspace resource."""
    resourceId: Union[str, Parameter[str]]
    """Full resource id of a AML workspace resource."""


class UserOwnedStorage(TypedDict, total=False):
    identityClientId: Union[str, Parameter[str]]
    """The identity client Id to access the storage."""
    resourceId: Union[str, Parameter[str]]
    """Full resource id of a Microsoft.Storage resource."""


class ApiProperties(TypedDict, total=False):
    aadClientId: Union[str, Parameter[str]]
    """(Metrics Advisor Only) The Azure AD Client Id (Application Id)."""
    aadTenantId: Union[str, Parameter[str]]
    """(Metrics Advisor Only) The Azure AD Tenant Id."""
    eventHubConnectionString: Union[str, Parameter[str]]
    """(Personalization Only) The flag to enable statistics of Bing Search."""
    qnaAzureSearchEndpointId: Union[str, Parameter[str]]
    """(QnAMaker Only) The Azure Search endpoint id of QnAMaker."""
    qnaAzureSearchEndpointKey: Union[str, Parameter[str]]
    """(QnAMaker Only) The Azure Search endpoint key of QnAMaker."""
    qnaRuntimeEndpoint: Union[str, Parameter[str]]
    """(QnAMaker Only) The runtime endpoint of QnAMaker."""
    statisticsEnabled: Union[bool, Parameter[bool]]
    """(Bing Search Only) The flag to enable statistics of Bing Search."""
    storageAccountConnectionString: Union[str, Parameter[str]]
    """(Personalization Only) The storage account connection string."""
    superUser: Union[str, Parameter[str]]
    """(Metrics Advisor Only) The super user of Metrics Advisor."""
    websiteName: Union[str, Parameter[str]]
    """(Metrics Advisor Only) The website name of Metrics Advisor."""


class AccountProperties(TypedDict, total=False):
    allowedFqdnList: Union[List[Union[str, Parameter[str]]], Parameter[List[str]]]
    """List of allowed FQDN."""
    amlWorkspace: Union[UserOwnedAmlWorkspace, Parameter[UserOwnedAmlWorkspace]]
    """The user owned AML workspace properties."""
    apiProperties: Union[ApiProperties, Parameter[ApiProperties]]
    """The api properties for special APIs."""
    customSubDomainName: Union[str, Parameter[str]]
    """Optional subdomain name used for token-based authentication."""
    disableLocalAuth: Union[bool, Parameter[bool]]
    """Allow only Azure AD authentication. Should be enabled for security reasons."""
    dynamicThrottlingEnabled: Union[bool, Parameter[bool]]
    """The flag to enable dynamic throttling."""
    encryption: Union[Encryption, Parameter[Encryption]]
    """The encryption properties for this resource."""
    locations: Union[MultiRegionSettings, Parameter[MultiRegionSettings]]
    """The multiregion settings of Cognitive Services account."""
    migrationToken: Union[str, Parameter[str]]
    """Resource migration token."""
    networkAcls: Union[NetworkRuleSet, Parameter[NetworkRuleSet]]
    """A collection of rules governing the accessibility from specific network locations."""
    publicNetworkAccess: Union[Literal['Disabled', 'Enabled'], Parameter[str]]
    """Whether or not public endpoint access is allowed for this account."""
    raiMonitorConfig: Union[RaiMonitorConfig, Parameter[RaiMonitorConfig]]
    """Cognitive Services Rai Monitor Config."""
    restore: Union[bool, Parameter[bool]]
    """Restore a soft-deleted cognitive service at deployment time. Will fail if no such soft-deleted resource exists."""
    restrictOutboundNetworkAccess: Union[bool, Parameter[bool]]
    """Restrict outbound network access."""
    userOwnedStorage: Union[List[Union[UserOwnedStorage, Parameter[UserOwnedStorage]]], Parameter[List[UserOwnedStorage]]]
    """The storage accounts for this resource."""


class CognitiveServicesAccountResource(TypedDict, total=False):
    identity: 'Identity'
    """Identity for the resource."""
    kind: Union[Literal['AIServices', 'AnomalyDetector', 'CognitiveServices', 'ComputerVision', 'ContentModerator', 'ContentSafety', 'ConversationalLanguageUnderstanding', 'CustomVision.Prediction', 'CustomVision.Training', 'Face', 'FormRecognizer', 'HealthInsights', 'ImmersiveReader', 'Internal.AllInOne', 'LanguageAuthoring', 'LUIS', 'LUIS.Authoring', 'MetricsAdvisor', 'OpenAI', 'Personalizer', 'QnAMaker.v2', 'SpeechServices', 'TextAnalytics', 'TextTranslation'], Parameter[str]]
    """The Kind of the resource."""
    location: Union[str, Parameter[str]]
    """The geo-location where the resource lives."""
    name: Union[str, Parameter[str]]
    """The resource name."""
    properties:	'AccountProperties'
    """Properties of Cognitive Services account."""
    sku: Union['Sku', Parameter['Sku']]
    """The resource model definition representing SKU"""
    tags: Union[Dict[str, Union[str, Parameter[str]]], Parameter[Dict[str, str]]]
    """Dictionary of tag names and values. See Tags in templates"""
