# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=arguments-differ

from collections import defaultdict
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Generator,
    List,
    Literal,
    Mapping,
    Union,
    Optional,
)
from typing_extensions import TypeVar, Unpack, TypedDict

from ..resourcegroup import ResourceGroup
from .._identifiers import ResourceIdentifiers
from .._extension import convert_managed_identities, ManagedIdentity, RoleAssignment
from ..._parameters import GLOBAL_PARAMS
from ..._bicep.expressions import Output, Expression, ResourceSymbol, Parameter
from ..._resource import _ClientResource, FieldsType, FieldType, ResourceReference, ExtensionResources

if TYPE_CHECKING:
    from .types import CognitiveServicesAccountResource, ApiProperties, CognitiveServicesNetworkRuleSet


class CognitiveServicesKwargs(TypedDict, total=False):
    custom_subdomain_name: Union[str, Parameter]
    """Subdomain name used for token-based authentication. Required if 'networkAcls' or 'privateEndpoints' are set."""
    allowed_fqdn_list: Union[List[Union[str, Parameter]], Parameter]
    """List of allowed FQDN."""
    api_properties: Union["ApiProperties", Parameter]
    """The API properties for special APIs."""
    disable_local_auth: Union[bool, Parameter]
    """Allow only Azure AD authentication. Should be enabled for security reasons."""
    dynamic_throttling_enabled: Union[bool, Parameter]
    """The flag to enable dynamic throttling."""
    location: Union[str, Parameter]
    """Location for all Resources."""
    managed_identities: "ManagedIdentity"
    """The managed identity definition for this resource."""
    migration_token: Union[str, Parameter]
    """Resource migration token."""
    network_acls: Union["CognitiveServicesNetworkRuleSet", Parameter]
    """A collection of rules governing the accessibility from specific network locations."""
    public_network_access: Union[Literal["Disabled", "Enabled"], Parameter]
    """Whether or not public network access is allowed for this resource. For security reasons it should be disabled.
    If not specified, it will be disabled by default if private endpoints are set and networkAcls are not set.
    """
    restore: Union[bool, Parameter]
    """Restore a soft-deleted cognitive service at deployment time. Will fail if no such soft-deleted resource
    exists.
    """
    restrict_outbound_network_access: Union[bool, Parameter]
    """Restrict outbound network access."""
    roles: Union[
        Parameter,
        List[
            Union[
                Parameter,
                "RoleAssignment",
                Literal[
                    "Cognitive Services Contributor",
                    "Cognitive Services Custom Vision Contributor",
                    "Cognitive Services Custom Vision Deployment",
                    "Cognitive Services Custom Vision Labeler",
                    "Cognitive Services Custom Vision Reader",
                    "Cognitive Services Custom Vision Trainer",
                    "Cognitive Services Data Reader (Preview)",
                    "Cognitive Services Face Recognizer",
                    "Cognitive Services Immersive Reader User",
                    "Cognitive Services Language Owner",
                    "Cognitive Services Language Reader",
                    "Cognitive Services Language Writer",
                    "Cognitive Services LUIS Owner",
                    "Cognitive Services LUIS Reader",
                    "Cognitive Services LUIS Writer",
                    "Cognitive Services Metrics Advisor Administrator",
                    "Cognitive Services Metrics Advisor User",
                    "Cognitive Services OpenAI Contributor",
                    "Cognitive Services OpenAI User",
                    "Cognitive Services QnA Maker Editor",
                    "Cognitive Services QnA Maker Reader",
                    "Cognitive Services Speech Contributor",
                    "Cognitive Services Speech User",
                    "Cognitive Services User",
                    "Contributor",
                    "Owner",
                    "Reader",
                    "Role Based Access Control Administrator",
                    "User Access Administrator",
                ],
            ]
        ],
    ]
    """Array of role assignments to create."""
    user_roles: Union[
        Parameter,
        List[
            Union[
                Parameter,
                "RoleAssignment",
                Literal[
                    "Cognitive Services Contributor",
                    "Cognitive Services Custom Vision Contributor",
                    "Cognitive Services Custom Vision Deployment",
                    "Cognitive Services Custom Vision Labeler",
                    "Cognitive Services Custom Vision Reader",
                    "Cognitive Services Custom Vision Trainer",
                    "Cognitive Services Data Reader (Preview)",
                    "Cognitive Services Face Recognizer",
                    "Cognitive Services Immersive Reader User",
                    "Cognitive Services Language Owner",
                    "Cognitive Services Language Reader",
                    "Cognitive Services Language Writer",
                    "Cognitive Services LUIS Owner",
                    "Cognitive Services LUIS Reader",
                    "Cognitive Services LUIS Writer",
                    "Cognitive Services Metrics Advisor Administrator",
                    "Cognitive Services Metrics Advisor User",
                    "Cognitive Services OpenAI Contributor",
                    "Cognitive Services OpenAI User",
                    "Cognitive Services QnA Maker Editor",
                    "Cognitive Services QnA Maker Reader",
                    "Cognitive Services Speech Contributor",
                    "Cognitive Services Speech User",
                    "Cognitive Services User",
                    "Contributor",
                    "Owner",
                    "Reader",
                    "Role Based Access Control Administrator",
                    "User Access Administrator",
                ],
            ]
        ],
    ]
    """Array of Role assignments to create for user principal ID"""
    sku: Union[
        Literal["C2", "C3", "C4", "F0", "F1", "S", "S0", "S1", "S10", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "S9"],
        Parameter,
    ]
    """SKU of the Cognitive Services account. Use 'Get-AzCognitiveServicesAccountSku' to determine a valid
    combinations of 'kind' and 'SKU' for your Azure region.
    """
    tags: Union[Dict[str, Union[str, Parameter]], Parameter]
    """Tags of the resource."""
    # storage: List[object]
    # """The storage accounts for this resource."""


CognitiveServicesAccountResourceType = TypeVar(
    "CognitiveServicesAccountResourceType", bound=Mapping[str, Any], default="CognitiveServicesAccountResource"
)
_DEFAULT_COGNITIVE_SERVICES: "CognitiveServicesAccountResource" = {
    "name": GLOBAL_PARAMS["defaultName"],
    "location": GLOBAL_PARAMS["location"],
    "tags": GLOBAL_PARAMS["azdTags"],
}
_DEFAULT_COGNITIVE_SERVICES_EXTENSIONS: ExtensionResources = {"managed_identity_roles": [], "user_roles": []}


class CognitiveServicesAccount(_ClientResource[CognitiveServicesAccountResourceType]):
    DEFAULTS: "CognitiveServicesAccountResource" = _DEFAULT_COGNITIVE_SERVICES
    DEFAULT_EXTENSIONS: ExtensionResources = _DEFAULT_COGNITIVE_SERVICES_EXTENSIONS
    properties: CognitiveServicesAccountResourceType
    parent: None

    def __init__(
        self,
        properties: Optional["CognitiveServicesAccountResource"] = None,
        /,
        name: Optional[str] = None,
        *,
        kind: Union[
            Parameter,
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
        ],
        **kwargs: Unpack[CognitiveServicesKwargs],
    ) -> None:
        existing = kwargs.pop("existing", False)
        extensions: ExtensionResources = defaultdict(list)
        properties = properties or {}
        properties["kind"] = kind
        if "roles" in kwargs:
            extensions["managed_identity_roles"] = kwargs.pop("roles")  # type:ignore[misc] Popping from TypedDict
        if "user_roles" in kwargs:
            extensions["user_roles"] = kwargs.pop("user_roles")
        if not existing:
            if "properties" not in properties:
                properties["properties"] = {}
            if name:
                properties["name"] = name
            if "custom_subdomain_name" in kwargs:
                properties["properties"]["customSubDomainName"] = kwargs.pop("custom_subdomain_name")
            if "allowed_fqdn_list" in kwargs:
                properties["properties"]["allowedFqdnList"] = kwargs.pop("allowed_fqdn_list")
            if "api_properties" in kwargs:
                properties["properties"]["apiProperties"] = kwargs.pop("api_properties")
            if "disable_local_auth" in kwargs:
                properties["properties"]["disableLocalAuth"] = kwargs.pop("disable_local_auth")
            if "dynamic_throttling_enabled" in kwargs:
                properties["properties"]["dynamicThrottlingEnabled"] = kwargs.pop("dynamic_throttling_enabled")
            if "location" in kwargs:
                properties["location"] = kwargs.pop("location")
            if "managed_identities" in kwargs:
                properties["identity"] = convert_managed_identities(kwargs.pop("managed_identities"))
            if "migration_token" in kwargs:
                properties["properties"]["migrationToken"] = kwargs.pop("migration_token")
            if "network_acls" in kwargs:
                properties["properties"]["networkAcls"] = kwargs.pop("network_acls")
            if "public_network_access" in kwargs:
                properties["properties"]["publicNetworkAccess"] = kwargs.pop("public_network_access")
            if "restore" in kwargs:
                properties["properties"]["restore"] = kwargs.pop("restore")
            if "restrict_outbound_network_access" in kwargs:
                properties["properties"]["restrictOutboundNetworkAccess"] = kwargs.pop(
                    "restrict_outbound_network_access"
                )
            if "sku" in kwargs:
                properties["sku"] = properties.get("sku", {})
                properties["sku"]["name"] = kwargs.pop("sku")
            if "tags" in kwargs:
                properties["tags"] = kwargs.pop("tags")
        super().__init__(
            properties,
            extensions=extensions,
            service_prefix=[f"ai_{kind}"],
            existing=existing,
            identifier=kwargs.pop("identifier", ResourceIdentifiers.cognitive_services),
            **kwargs,
        )

    @classmethod
    def reference(
        cls,
        *,
        name: Union[str, Parameter],
        resource_group: Optional[Union[str, Parameter, ResourceGroup]] = None,
    ) -> "CognitiveServicesAccount[ResourceReference]":
        return super().reference(
            name=name,
            resource_group=resource_group,
        )

    @property
    def resource(self) -> Literal["Microsoft.CognitiveServices/accounts"]:
        return "Microsoft.CognitiveServices/accounts"

    @property
    def version(self) -> str:
        from .types import VERSION

        return VERSION

    def _build_endpoint(self, *, config_store: Mapping[str, Any]) -> str:  # pylint: disable=unused-argument
        raise RuntimeError("No deterministic endpoint.")

    def _build_symbol(self) -> ResourceSymbol:
        symbol = super()._build_symbol()
        symbol._value = f"{self.properties['kind'].lower()}_" + symbol._value  # pylint: disable=protected-access
        return symbol

    def _find_all_resource_match(
        self,
        fields: FieldsType,
        *,
        resource: Optional[str] = None,
        resource_group: Optional[ResourceSymbol] = None,
        name: Optional[Union[str, Expression]] = None,
        parent: Optional[ResourceSymbol] = None,
    ) -> Generator[FieldType, None, None]:
        resource = resource or self.resource
        for field in (f for f in reversed(list(fields.values())) if f.resource == resource):
            if resource == self.resource and field.properties["kind"] != self.properties["kind"]:
                continue
            if name and resource_group:
                if field.properties.get("name") == name and field.resource_group == resource_group:
                    yield field
            elif name and parent:
                if field.properties.get("name") == name and field.properties["parent"] == parent:
                    yield field
            elif resource_group:
                if field.resource_group == resource_group:
                    yield field
            elif parent:
                if field.properties["parent"] == parent:
                    yield field
            elif name:
                if field.properties.get("name") == name:
                    yield field
            else:
                yield field

    def _outputs(self, *, symbol: ResourceSymbol, suffix: Optional[str] = None, **kwargs) -> Dict[str, Output]:
        outputs = super()._outputs(symbol=symbol, suffix=suffix, **kwargs)
        outputs["endpoint"] = Output(
            f"AZURE_{self._prefixes[0].upper()}_ENDPOINT{suffix or self._suffix}", "properties.endpoint", symbol
        )
        return outputs


class AIServicesKwargs(TypedDict, total=False):
    custom_subdomain_name: Union[str, Parameter]
    """Subdomain name used for token-based authentication. Required if 'networkAcls' or 'privateEndpoints' are set."""
    allowed_fqdn_list: Union[List[Union[str, Parameter]], Parameter]
    """List of allowed FQDN."""
    disable_local_auth: Union[bool, Parameter]
    """Allow only Azure AD authentication. Should be enabled for security reasons."""
    dynamic_throttling_enabled: Union[bool, Parameter]
    """The flag to enable dynamic throttling."""
    location: Union[str, Parameter]
    """Location for all Resources."""
    managed_identities: "ManagedIdentity"
    """The managed identity definition for this resource."""
    migration_token: Union[str, Parameter]
    """Resource migration token."""
    network_acls: Union["CognitiveServicesNetworkRuleSet", Parameter]
    """A collection of rules governing the accessibility from specific network locations."""
    public_network_access: Union[Literal["Disabled", "Enabled"], Parameter]
    """Whether or not public network access is allowed for this resource. For security reasons it should be disabled.
    If not specified, it will be disabled by default if private endpoints are set and networkAcls are not set.
    """
    restore: Union[bool, Parameter]
    """Restore a soft-deleted cognitive service at deployment time. Will fail if no such soft-deleted resource
    exists.
    """
    restrict_outbound_network_access: Union[bool, Parameter]
    """Restrict outbound network access."""
    roles: Union[
        Parameter,
        List[
            Union[
                Parameter,
                "RoleAssignment",
                Literal[
                    "Cognitive Services Contributor",
                    "Cognitive Services Custom Vision Contributor",
                    "Cognitive Services Custom Vision Deployment",
                    "Cognitive Services Custom Vision Labeler",
                    "Cognitive Services Custom Vision Reader",
                    "Cognitive Services Custom Vision Trainer",
                    "Cognitive Services Data Reader (Preview)",
                    "Cognitive Services Face Recognizer",
                    "Cognitive Services Immersive Reader User",
                    "Cognitive Services Language Owner",
                    "Cognitive Services Language Reader",
                    "Cognitive Services Language Writer",
                    "Cognitive Services LUIS Owner",
                    "Cognitive Services LUIS Reader",
                    "Cognitive Services LUIS Writer",
                    "Cognitive Services Metrics Advisor Administrator",
                    "Cognitive Services Metrics Advisor User",
                    "Cognitive Services OpenAI Contributor",
                    "Cognitive Services OpenAI User",
                    "Cognitive Services QnA Maker Editor",
                    "Cognitive Services QnA Maker Reader",
                    "Cognitive Services Speech Contributor",
                    "Cognitive Services Speech User",
                    "Cognitive Services User",
                    "Contributor",
                    "Owner",
                    "Reader",
                    "Role Based Access Control Administrator",
                    "User Access Administrator",
                ],
            ]
        ],
    ]
    """Array of role assignments to create."""
    user_roles: Union[
        Parameter,
        List[
            Union[
                Parameter,
                "RoleAssignment",
                Literal[
                    "Cognitive Services Contributor",
                    "Cognitive Services Custom Vision Contributor",
                    "Cognitive Services Custom Vision Deployment",
                    "Cognitive Services Custom Vision Labeler",
                    "Cognitive Services Custom Vision Reader",
                    "Cognitive Services Custom Vision Trainer",
                    "Cognitive Services Data Reader (Preview)",
                    "Cognitive Services Face Recognizer",
                    "Cognitive Services Immersive Reader User",
                    "Cognitive Services Language Owner",
                    "Cognitive Services Language Reader",
                    "Cognitive Services Language Writer",
                    "Cognitive Services LUIS Owner",
                    "Cognitive Services LUIS Reader",
                    "Cognitive Services LUIS Writer",
                    "Cognitive Services Metrics Advisor Administrator",
                    "Cognitive Services Metrics Advisor User",
                    "Cognitive Services OpenAI Contributor",
                    "Cognitive Services OpenAI User",
                    "Cognitive Services QnA Maker Editor",
                    "Cognitive Services QnA Maker Reader",
                    "Cognitive Services Speech Contributor",
                    "Cognitive Services Speech User",
                    "Cognitive Services User",
                    "Contributor",
                    "Owner",
                    "Reader",
                    "Role Based Access Control Administrator",
                    "User Access Administrator",
                ],
            ]
        ],
    ]
    """Array of Role assignments to create for user principal ID"""
    sku: Union[
        Literal["C2", "C3", "C4", "F0", "F1", "S", "S0", "S1", "S10", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "S9"],
        Parameter,
    ]
    """SKU of the Cognitive Services account. Use 'Get-AzCognitiveServicesAccountSku' to determine a valid
    combinations of 'kind' and 'SKU' for your Azure region.
    """
    tags: Union[Dict[str, Union[str, Parameter]], Parameter]
    """Tags of the resource."""
    # storage: List[object]
    # """The storage accounts for this resource."""


_DEFAULT_AI_SERVICES: "CognitiveServicesAccountResource" = {
    "name": GLOBAL_PARAMS["defaultName"].format("{}-aiservices"),
    "location": GLOBAL_PARAMS["location"],
    "tags": GLOBAL_PARAMS["azdTags"],
    "kind": "AIServices",
    "sku": {"name": "S0"},
    "properties": {
        "publicNetworkAccess": "Enabled",
        "disableLocalAuth": True,
        "customSubDomainName": GLOBAL_PARAMS["defaultName"].format("{}-aiservices"),
        "networkAcls": {"defaultAction": "Allow", "virtualNetworkRules": [], "ipRules": []},
    },
    "identity": {"type": "UserAssigned", "userAssignedIdentities": {GLOBAL_PARAMS["managedIdentityId"]: {}}},
}
_DEFAULT_AI_SERVICES_EXTENSIONS: ExtensionResources = {
    "managed_identity_roles": [
        "Cognitive Services OpenAI Contributor",
        "Cognitive Services Contributor",
        "Cognitive Services OpenAI User",
        "Cognitive Services User",
    ],
    "user_roles": [
        "Cognitive Services OpenAI Contributor",
        "Cognitive Services Contributor",
        "Cognitive Services OpenAI User",
        "Cognitive Services User",
    ],
}


class AIServices(CognitiveServicesAccount[CognitiveServicesAccountResourceType]):
    DEFAULTS: "CognitiveServicesAccountResource" = _DEFAULT_AI_SERVICES
    DEFAULT_EXTENSIONS: ExtensionResources = _DEFAULT_AI_SERVICES_EXTENSIONS

    def __init__(
        self,
        properties: Optional["CognitiveServicesAccountResource"] = None,
        /,
        name: Optional[str] = None,
        **kwargs: Unpack[AIServicesKwargs],
    ) -> None:
        super().__init__(properties, name=name, kind="AIServices", identifier=ResourceIdentifiers.ai_services, **kwargs)

    def _build_endpoint(self, *, config_store: Mapping[str, Any]) -> str:
        return f"https://{self._settings['name'](config_store=config_store)}.openai.azure.com/"
