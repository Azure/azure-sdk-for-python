# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=arguments-differ

from collections import defaultdict
import inspect
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Generic,
    List,
    Literal,
    Mapping,
    Tuple,
    Type,
    Union,
    Optional,
    cast,
    overload,
)
from typing_extensions import TypeVar, Unpack, TypedDict

from ..resourcegroup import ResourceGroup
from .._identifiers import ResourceIdentifiers
from .._extension import ManagedIdentity, convert_managed_identities, RoleAssignment
from ..._parameters import GLOBAL_PARAMS
from ..._setting import StoredPrioritizedSetting
from ..._utils import find_all_resource_match, find_last_resource_match
from ..._bicep.expressions import Guid, ResourceSymbol, Parameter, ResourceGroup as RGSymbol, Output
from ..._resource import (
    Resource,
    FieldsType,
    ResourceReference,
    ExtensionResources,
    _build_envs,
    _load_dev_environment,
)
from ._connection import AIConnection

if TYPE_CHECKING:
    from .types import MachineLearningWorkspaceResource

    from azure.core.credentials import SupportsTokenInfo
    from azure.core.credentials_async import AsyncSupportsTokenInfo
    from azure.ai.projects import AIProjectClient
    from azure.ai.projects.aio import AIProjectClient as AsyncAIProjectClient


class MachineLearningWorkspaceKwargs(TypedDict, total=False):
    friendly_name: Union[str, Parameter]
    """Friendly name of the workspace."""
    sku: Union[Literal["Basic", "Free", "Premium", "Standard"], Parameter]
    """Specifies the SKU, also referred as 'edition' of the Azure Machine Learning workspace."""
    application_insights: Union[str, Parameter]
    """The resource ID of the associated Application Insights. Required if 'kind' is 'Default' or 'FeatureStore'."""
    keyvault: Union[str, Parameter]
    """The resource ID of the associated Key Vault. Required if 'kind' is 'Default', 'FeatureStore' or 'Hub'."""
    storage: Union[str, Parameter]
    """The resource ID of the associated Storage Account. Required if 'kind' is 'Default', 'FeatureStore' or 'Hub'."""
    feature_store_settings: Union["FeatureStoreSetting", Parameter]  # type: ignore[name-defined]  # TODO
    """Settings for feature store type workspaces. Required if 'kind' is set to 'FeatureStore'."""
    hub: Union[str, Parameter]
    """The resource ID of the hub to associate with the workspace. Required if 'kind' is set to 'Project'."""
    primary_user_assigned_identity: Union[str, Parameter]
    """The user assigned identity resource ID that represents the workspace identity. Required if
    'userAssignedIdentities' is not empty and may not be used if 'systemAssignedIdentity' is enabled.
    """
    container_registry: Union[str, Parameter]
    """The resource ID of the associated Container Registry."""
    description: Union[str, Parameter]
    """The description of this workspace."""
    # diagnostic_settings: List['DiagnosticSetting']
    # """The diagnostic settings of the service."""
    discovery_url: Union[str, Parameter]
    """URL for the discovery service to identify regional endpoints for machine learning experimentation services."""
    hbi_workspace: Union[bool, Parameter]
    """The flag to signal HBI data in the workspace and reduce diagnostic data collected by the service."""
    image_build_compute: Union[str, Parameter]
    """The compute name for image build."""
    location: Union[str, Parameter]
    """Location for all resources."""
    # lock: 'Lock'
    # """The lock settings of the service."""
    managed_identities: Optional["ManagedIdentity"]
    """The managed identity definition for this resource. At least one identity type is required."""
    managed_network: Union["ManagedNetworkSetting", Parameter]  # type: ignore[name-defined]  # TODO
    """Managed Network settings for a machine learning workspace."""
    # private_endpoints: List['PrivateEndpoint']
    # """Configuration details for private endpoints. For security reasons, it is recommended to use private endpoints
    # whenever possible.
    # """
    public_network_access: Union[Literal["Disabled", "Enabled"], Parameter]
    """Whether or not public network access is allowed for this resource. For security reasons it should be
    disabled.
    """
    roles: Union[
        Parameter,
        List[
            Union[
                Parameter,
                "RoleAssignment",
                Literal[
                    "AzureML Compute Operator",
                    "AzureML Data Scientist",
                    "AzureML Metrics Writer (preview)",
                    "AzureML Registry User",
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
                    "AzureML Compute Operator",
                    "AzureML Data Scientist",
                    "AzureML Metrics Writer (preview)",
                    "AzureML Registry User",
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
    serverless_compute_settings: Union["ServerlessComputeSetting", Parameter]  # type: ignore[name-defined]  # TODO
    """Settings for serverless compute created in the workspace."""
    service_managed_resources_settings: Union[Dict[str, Any], Parameter]  # TODO: Proper typed dict
    """The service managed resource settings."""
    shared_private_link_resources: Union[List[Any], Parameter]  # TODO: Proper typed dict
    """The list of shared private link resources in this workspace. Note: This property is not idempotent."""
    system_datastores_auth_mode: Union[Literal["accessKey", "identity"], Parameter]
    """The authentication mode used by the workspace when connecting to the default storage account."""
    tags: Union[Dict[str, Union[str, Parameter]], Parameter]
    """Tags of the resource."""
    workspacehub_config: Union["WorkspaceHubConfig", Parameter]  # type: ignore[name-defined]  # TODO
    """Configuration for workspace hub settings."""


MachineLearningWorkspaceResourceType = TypeVar(
    "MachineLearningWorkspaceResourceType", bound=Mapping[str, Any], default="MachineLearningWorkspaceResource"
)
_DEFAULT_ML_WORKSPACE: "MachineLearningWorkspaceResource" = {
    "name": GLOBAL_PARAMS["defaultName"],
    "location": GLOBAL_PARAMS["location"],
    "tags": GLOBAL_PARAMS["azdTags"],
    "properties": {
        "primaryUserAssignedIdentity": GLOBAL_PARAMS["managedIdentityId"],
    },
    "identity": {"type": "UserAssigned", "userAssignedIdentities": {GLOBAL_PARAMS["managedIdentityId"]: {}}},
}
_DEFAULT_ML_WORKSPACE_EXTENSIONS: ExtensionResources = {"managed_identity_roles": [], "user_roles": []}


class MLWorkspace(Resource, Generic[MachineLearningWorkspaceResourceType]):
    DEFAULTS: "MachineLearningWorkspaceResource" = _DEFAULT_ML_WORKSPACE  # type: ignore[assignment]
    DEFAULT_EXTENSIONS: ExtensionResources = _DEFAULT_ML_WORKSPACE_EXTENSIONS
    properties: MachineLearningWorkspaceResourceType
    parent: None  # type: ignore[reportIncompatibleVariableOverride]

    def __init__(
        self,
        properties: Optional["MachineLearningWorkspaceResource"] = None,
        /,
        name: Optional[Union[str, Parameter]] = None,
        *,
        kind: Literal["Default", "FeatureStore", "Hub", "Project"],
        **kwargs: Unpack[MachineLearningWorkspaceKwargs],
    ) -> None:
        # TODO: Support explicit 'storage', 'keyvault' and connections.
        # 'existing' is passed by the reference classmethod.
        existing = kwargs.pop("existing", False)  # type: ignore[typeddict-item]
        extensions: ExtensionResources = defaultdict(list)  # type: ignore  # Doesn't like the default dict.
        properties = properties or {}
        properties["kind"] = kind
        self._kind = kind
        if "roles" in kwargs:
            extensions["managed_identity_roles"] = kwargs.pop("roles")
        if "user_roles" in kwargs:
            extensions["user_roles"] = kwargs.pop("user_roles")
        # TODO: Finish populating kwarg properties
        if not existing:
            if "properties" not in properties:
                properties["properties"] = {}
            if name:
                properties["name"] = name
            if "friendly_name" in kwargs:
                properties["properties"]["friendlyName"] = kwargs.pop("friendly_name")
            if "description" in kwargs:
                properties["properties"]["description"] = kwargs.pop("description")
            if "location" in kwargs:
                properties["location"] = kwargs.pop("location")
            if "managed_identities" in kwargs:
                properties["identity"] = convert_managed_identities(kwargs.pop("managed_identities"))
            if "public_network_access" in kwargs:
                properties["properties"]["publicNetworkAccess"] = kwargs.pop("public_network_access")
            if "sku" in kwargs:
                sku = kwargs.pop("sku")
                properties["sku"] = {"name": sku, "tier": "sku"}
                properties["sku"] = properties.get("sku", {})
            if "tags" in kwargs:
                properties["tags"] = kwargs.pop("tags")
        # The kwargs service_prefix and identifier can be passed by child classes.
        super().__init__(
            properties,
            extensions=extensions,
            service_prefix=kwargs.pop("service_prefix", [f"ml_{kind}"]),  # type: ignore[typeddict-item]
            existing=existing,
            identifier=kwargs.pop("identifier", ResourceIdentifiers.ml_workspace),  # type: ignore[typeddict-item]
            **kwargs,
        )

    @classmethod
    def reference(  # type: ignore[override]  # Parameter subset and renames
        cls,
        *,
        name: Union[str, Parameter],
        resource_group: Optional[Union[str, Parameter, ResourceGroup[ResourceReference]]] = None,
    ) -> "MLWorkspace[ResourceReference]":
        existing = super().reference(
            name=name,
            resource_group=resource_group,
        )
        return cast(MLWorkspace[ResourceReference], existing)

    @property
    def resource(self) -> Literal["Microsoft.MachineLearningServices/workspaces"]:
        return "Microsoft.MachineLearningServices/workspaces"

    @property
    def version(self) -> str:
        from .types import VERSION

        return VERSION

    def _build_symbol(self, suffix: Optional[Union[str, Parameter]]) -> ResourceSymbol:
        symbol = super()._build_symbol(suffix)
        symbol._value = f"{self._kind.lower()}_" + symbol.value  # pylint: disable=protected-access
        return symbol

    def _merge_properties(  # type: ignore[override]  # Parameter superset
        self,
        current_properties: Dict[str, Any],
        new_properties: Dict[str, Any],
        *,
        parameters: Dict[str, Parameter],
        symbol: ResourceSymbol,
        fields: FieldsType,
        **kwargs,
    ) -> Dict[str, Any]:
        merged_properties = super()._merge_properties(
            current_properties,
            new_properties,
            symbol=symbol,
            fields=fields,
            parameters=parameters,
            **kwargs,
        )
        if self._kind in ["Project", "Hub"]:
            if not merged_properties.get("workspaceHubConfig"):
                merged_properties["workspaceHubConfig"] = {}
            if not merged_properties["workspaceHubConfig"].get("defaultWorkspaceResourceGroup"):
                merged_properties["workspaceHubConfig"]["defaultWorkspaceResourceGroup"] = RGSymbol().id

            for searchservices in find_all_resource_match(fields, resource_types=[ResourceIdentifiers.search]):
                search_connection = AIConnection(
                    {
                        # We have to do this to prevent infinit recursion on calling self.parent.__bicep__()
                        "parent": symbol
                    },
                    parent=cast(Union[AIHub, AIProject], self),  # We already filtered for 'kind' above.
                    category="CognitiveSearch",
                    target=searchservices.outputs["endpoint"][0],
                    name=Guid(
                        searchservices.properties.get("name", parameters["defaultName"]),
                        "connection",
                        self._kind,
                        "AISearch",
                    ),
                    metadata={
                        "ApiType": "Azure",
                        "ResourceId": searchservices.symbol.id,
                        "location": merged_properties.get("location", parameters["location"]),
                    },
                )
                search_connection.__bicep__(fields, parameters=parameters)
            # TODO: Support "OpenaI" cognitive services once it supports AAD.
            for aiservices in find_all_resource_match(fields, resource_types=[ResourceIdentifiers.ai_services]):

                # TODO: This will actually fail if there's more than one.... should more than one even be supported?
                ai_connection = AIConnection(
                    {"parent": symbol},
                    parent=cast(Union[AIHub, AIProject], self),  # We already filtered for 'kind' above.
                    category="AIServices",
                    target=aiservices.outputs["endpoint"][0],
                    name=Guid(
                        aiservices.properties.get("name", parameters["defaultName"]),
                        "connection",
                        self._kind,
                        "AIServices",
                    ),
                    metadata={
                        "ApiType": "Azure",
                        "ResourceId": aiservices.symbol.id,
                        "location": merged_properties.get("location", parameters["location"]),
                    },
                )
                ai_connection.__bicep__(fields, parameters=parameters)
        return merged_properties


_DEFAULT_AI_HUB: "MachineLearningWorkspaceResource" = {
    "kind": "Hub",
    "name": GLOBAL_PARAMS["defaultName"].format("{}-hub"),
    "location": GLOBAL_PARAMS["location"],
    "tags": GLOBAL_PARAMS["azdTags"],
    "properties": {
        "primaryUserAssignedIdentity": GLOBAL_PARAMS["managedIdentityId"],
        "publicNetworkAccess": "Enabled",
        "enableDataIsolation": True,
        "v1LegacyMode": False,
        "hbiWorkspace": False,
        "managedNetwork": {"isolationMode": "Disabled"},
    },
    "sku": {
        "name": "Basic",
        "tier": "Basic",
    },
    "identity": {"type": "UserAssigned", "userAssignedIdentities": {GLOBAL_PARAMS["managedIdentityId"]: {}}},
}
_DEFAULT_AI_HUB_EXTENSIONS: ExtensionResources = {"managed_identity_roles": [], "user_roles": []}


class AIHub(MLWorkspace[MachineLearningWorkspaceResourceType]):
    DEFAULTS: "MachineLearningWorkspaceResource" = _DEFAULT_AI_HUB
    DEFAULT_EXTENSIONS: ExtensionResources = _DEFAULT_AI_HUB_EXTENSIONS
    properties: MachineLearningWorkspaceResourceType

    def __init__(
        self,
        properties: Optional["MachineLearningWorkspaceResource"] = None,
        /,
        name: Optional[str] = None,
        **kwargs: Unpack[MachineLearningWorkspaceKwargs],
    ) -> None:
        super().__init__(
            properties,
            name=name,
            kind="Hub",
            service_prefix=["aifoundry_hub"],  # type: ignore[call-arg]
            identifier=ResourceIdentifiers.ai_hub,  # type: ignore[call-arg]
            **kwargs,
        )

    @classmethod
    def reference(  # type: ignore[override]  # Parameter subset and renames
        cls,
        *,
        name: Union[str, Parameter],
        resource_group: Optional[Union[str, Parameter, ResourceGroup[ResourceReference]]] = None,
    ) -> "AIHub[ResourceReference]":
        existing = super().reference(
            name=name,
            resource_group=resource_group,
        )
        return cast(AIHub[ResourceReference], existing)

    def _merge_properties(  # type: ignore[override]  # Parameter superset
        self,
        current_properties: Dict[str, Any],
        new_properties: Dict[str, Any],
        *,
        fields: FieldsType,
        **kwargs,
    ) -> Dict[str, Any]:
        merged_properties = super()._merge_properties(
            current_properties,
            new_properties,
            fields=fields,
            **kwargs,
        )
        if not merged_properties.get("storageAccount"):
            storage = find_last_resource_match(fields, resource=ResourceIdentifiers.storage_account)
            if not storage:
                blob_storage = find_last_resource_match(fields, resource=ResourceIdentifiers.blob_storage)
                if not blob_storage:
                    raise ValueError("Cannot create AI Hub without associated Storage account.")
                merged_properties["storageAccount"] = blob_storage.properties["parent"].id
            else:
                merged_properties["storageAccount"] = storage.symbol.id
        if not merged_properties.get("keyVault"):
            vault = find_last_resource_match(fields, resource=ResourceIdentifiers.keyvault)
            if not vault:
                raise ValueError("Cannot create an AI Hub without associated KeyVault account.")
            merged_properties["keyVault"] = vault.symbol.id
        return merged_properties


_DEFAULT_AI_PROJECT: "MachineLearningWorkspaceResource" = {
    "kind": "Project",
    "name": GLOBAL_PARAMS["defaultName"].format("{}-project"),
    "location": GLOBAL_PARAMS["location"],
    "tags": GLOBAL_PARAMS["azdTags"],
    "properties": {
        "primaryUserAssignedIdentity": GLOBAL_PARAMS["managedIdentityId"],
        "publicNetworkAccess": "Enabled",
        "enableDataIsolation": True,
        "v1LegacyMode": False,
        "hbiWorkspace": False,
    },
    "sku": {
        "name": "Basic",
        "tier": "Basic",
    },
    "identity": {"type": "UserAssigned", "userAssignedIdentities": {GLOBAL_PARAMS["managedIdentityId"]: {}}},
}
_DEFAULT_AI_PROJECT_EXTENSIONS: ExtensionResources = {
    "managed_identity_roles": ["Contributor"],
    "user_roles": ["Contributor"],
}

ClientType = TypeVar("ClientType", default="AIProjectClient")


class AIProject(MLWorkspace[MachineLearningWorkspaceResourceType]):
    DEFAULTS: "MachineLearningWorkspaceResource" = _DEFAULT_AI_PROJECT
    DEFAULT_EXTENSIONS: ExtensionResources = _DEFAULT_AI_PROJECT_EXTENSIONS
    properties: MachineLearningWorkspaceResourceType

    def __init__(
        self,
        properties: Optional["MachineLearningWorkspaceResource"] = None,
        /,
        name: Optional[str] = None,
        **kwargs: Unpack[MachineLearningWorkspaceKwargs],
    ) -> None:
        super().__init__(
            properties,
            name=name,
            kind="Project",
            service_prefix=["aifoundry_project"],  # type: ignore[call-arg]
            identifier=ResourceIdentifiers.ai_project,  # type: ignore[call-arg]
            **kwargs,
        )
        self._settings["endpoint"] = StoredPrioritizedSetting(
            name="endpoint", env_vars=_build_envs(self._prefixes, ["ENDPOINT"]), suffix=self._env_suffix
        )

    @classmethod
    def reference(  # type: ignore[override]  # Parameter subset and renames
        cls,
        *,
        name: Union[str, Parameter],
        resource_group: Optional[Union[str, Parameter, ResourceGroup[ResourceReference]]] = None,
    ) -> "AIProject[ResourceReference]":
        existing = super().reference(
            name=name,
            resource_group=resource_group,
        )
        return cast(AIProject[ResourceReference], existing)

    def _outputs(self, *, symbol: ResourceSymbol, suffix: str, **kwargs) -> Dict[str, List[Output]]:
        outputs = super()._outputs(symbol=symbol, suffix=suffix, **kwargs)

        outputs["endpoint"].append(
            Output(f"AZURE_AIFOUNDRY_PROJECT_ENDPOINT{suffix}", "properties.discoveryUrl", symbol)
        )
        return outputs

    def _merge_properties(  # type: ignore[override]  # Parameter superset
        self,
        current_properties: Dict[str, Any],
        new_properties: Dict[str, Any],
        *,
        fields: FieldsType,
        **kwargs,
    ) -> Dict[str, Any]:
        merged_properties = super()._merge_properties(
            current_properties,
            new_properties,
            fields=fields,
            **kwargs,
        )
        if not merged_properties.get("hubResourceId"):
            hub = find_last_resource_match(fields, resource=ResourceIdentifiers.ai_hub)
            if not hub:
                raise ValueError("Cannot create AI Project without associated AI Hub.")
            merged_properties["hubResourceId"] = hub.symbol.id
        return merged_properties

    def _build_credential(self, cls: Type[ClientType], *, use_async: Optional[bool], credential: Any) -> Any:
        # TODO: This needs work - how to close the credential.
        if credential:
            try:
                return credential()
            except TypeError:
                return credential
        if use_async is None:
            try:
                use_async = inspect.iscoroutinefunction(getattr(cls, "close"))
            except AttributeError:
                raise TypeError(
                    f"Cannot determine whether cls type '{cls.__name__}' is async or not. "
                    "Please specify 'use_async' keyword argument."
                ) from None
        if use_async:
            from azure.identity.aio import DefaultAzureCredential as AsyncDefaultAzureCredential

            return AsyncDefaultAzureCredential()
        from azure.identity import DefaultAzureCredential as SyncDefaultAzureCredential

        return SyncDefaultAzureCredential()

    @overload
    def get_client(
        self,
        /,
        *,
        transport: Any = None,
        credential: Optional[Union["SupportsTokenInfo", "AsyncSupportsTokenInfo"]] = None,
        config_store: Optional[Mapping[str, Any]] = None,
        use_async: Optional[Literal[False]] = None,
        **client_options,
    ) -> "AIProjectClient": ...
    @overload
    def get_client(
        self,
        /,
        *,
        transport: Any = None,
        credential: Optional[Union["SupportsTokenInfo", "AsyncSupportsTokenInfo"]] = None,
        config_store: Optional[Mapping[str, Any]] = None,
        use_async: Literal[True],
        **client_options,
    ) -> "AsyncAIProjectClient": ...
    @overload
    def get_client(
        self,
        cls: Type[ClientType],
        /,
        *,
        transport: Any = None,
        credential: Optional[Union["SupportsTokenInfo", "AsyncSupportsTokenInfo"]] = None,
        config_store: Optional[Mapping[str, Any]] = None,
        use_async: Optional[bool] = None,
        return_credential: Literal[False] = False,
        **client_options,
    ) -> ClientType: ...
    @overload
    def get_client(
        self,
        cls: Type[ClientType],
        /,
        *,
        transport: Any = None,
        credential: Optional[Union["SupportsTokenInfo", "AsyncSupportsTokenInfo"]] = None,
        config_store: Optional[Mapping[str, Any]] = None,
        use_async: Optional[bool] = None,
        return_credential: Literal[True],
        **client_options,
    ) -> Tuple[ClientType, Union["SupportsTokenInfo", "AsyncSupportsTokenInfo"]]: ...
    def get_client(
        self,
        cls=None,
        /,
        *,
        transport=None,
        credential=None,
        config_store=None,
        use_async=None,
        return_credential=False,
        **client_options,
    ):
        if config_store is None:
            config_store = _load_dev_environment()
        if cls is None:
            if use_async:
                from azure.ai.projects.aio import (  # pylint: disable=no-name-in-module,import-error
                    AIProjectClient as AsyncAIProjectClient,
                )

                cls = AsyncAIProjectClient
            else:
                from azure.ai.projects import (  # pylint: disable=no-name-in-module,import-error
                    AIProjectClient as SyncAIProjectClient,
                )

                cls = SyncAIProjectClient
                use_async = False
        if transport:
            client_options["transport"] = transport
        credential = self._build_credential(cls, use_async=use_async, credential=credential)
        client = cls(
            endpoint=self._settings["endpoint"](config_store=config_store).rstrip("/discovery/").lstrip("https://"),
            subscription_id=self._settings["subscription"](config_store=config_store),
            resource_group_name=self._settings["resource_group"](config_store=config_store),
            project_name=self._settings["name"](config_store=config_store),
            credential=credential,
            **client_options,
        )
        if return_credential:
            return client, credential
        return client
