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
from .._extension import convert_managed_identities, ManagedIdentity, RoleAssignment
from ..._parameters import GLOBAL_PARAMS
from ..._bicep.expressions import Output, ResourceSymbol, Parameter
from ..._resource import _ClientResource, ResourceReference, ExtensionResources

if TYPE_CHECKING:
    from azure.core.credentials import SupportsTokenInfo
    from azure.core.credentials_async import AsyncSupportsTokenInfo
    from azure.search.documents.indexes import SearchIndexClient
    from azure.search.documents.indexes.aio import SearchIndexClient as AsyncSearchIndexClient
    from azure.search.documents import SearchClient
    from azure.search.documents.aio import SearchClient as AsyncSearchClient

    from .types import SearchServiceResource, SearchNetworkRuleSet


class SearchServiceKwargs(TypedDict, total=False):
    auth_options: "AuthOption"  # type: ignore[name-defined]  # TODO
    """Defines the options for how the data plane API of a Search service authenticates requests. Must remain an
    empty object {} if 'disableLocalAuth' is set to true.
    """
    cmk_enforcement: Union[Literal["Disabled", "Enabled", "Unspecified"], Parameter]
    """Describes a policy that determines how resources within the search service are to be encrypted with Customer
    Managed Keys.
    """
    # diagnostic_settings: List['DiagnosticSetting']
    # """The diagnostic settings of the service."""
    disable_local_auth: Union[bool, Parameter]
    """When set to true, calls to the search service will not be permitted to utilize API keys for authentication.
    This cannot be set to true if 'authOptions' are defined.
    """
    hosting_mode: Union[Literal["default", "highDensity"], Parameter]
    """Applicable only for the standard3 SKU. You can set this property to enable up to 3 high density partitions that
    allow up to 1000 indexes, which is much higher than the maximum indexes allowed for any other SKU. For the
    standard3 SKU, the value is either 'default' or 'highDensity'. For all other SKUs, this value must be 'default'.
    """
    location: Union[str, Parameter]
    """Location for all Resources."""
    # lock: 'Lock'
    # """The lock settings for all Resources in the solution."""
    managed_identities: Optional["ManagedIdentity"]
    """The managed identity definition for this resource."""
    network_acls: Union["SearchNetworkRuleSet", Parameter]
    """Network specific rules that determine how the Azure Cognitive Search service may be reached."""
    partition_count: Union[int, Parameter]
    """The number of partitions in the search service; if specified, it can be 1, 2, 3, 4, 6, or 12. Values greater
    than 1 are only valid for standard SKUs. For 'standard3' services with hostingMode set to 'highDensity', the
    allowed values are between 1 and 3.
    """
    # private_endpoints: List['PrivateEndpoint']
    # """Configuration details for private endpoints. For security reasons, it is recommended to use private endpoints
    # whenever possible.
    # """
    public_network_access: Union[Literal["Disabled", "Enabled"], Parameter]
    """This value can be set to 'Enabled' to avoid breaking changes on existing customer resources and templates. If
    set to 'Disabled', traffic over public interface is not allowed, and private endpoint connections would be the
    exclusive access method.
    """
    replica_count: Union[int, Parameter]
    """The number of replicas in the search service. If specified, it must be a value between 1 and 12 inclusive for
    standard SKUs or between 1 and 3 inclusive for basic SKU.
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
                    "Role Based Access Control Administrator",
                    "Search Index Data Contributor",
                    "Search Index Data Reader",
                    "Search Service Contributor",
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
                    "Contributor",
                    "Owner",
                    "Reader",
                    "Role Based Access Control Administrator",
                    "Search Index Data Contributor",
                    "Search Index Data Reader",
                    "Search Service Contributor",
                    "User Access Administrator",
                ],
            ]
        ],
    ]
    """Array of Role assignments to create for user principal ID"""
    semantic_search: Union[Literal["disabled", "free", "standard"], Parameter]
    """Sets options that control the availability of semantic search. This configuration is only possible for certain
    search SKUs in certain locations.
    """
    # shared_private_link_resources: List['SharedPrivateLinkResource']
    # """The sharedPrivateLinkResources to create as part of the search Service."""
    sku: Union[
        Literal["basic", "free", "standard", "standard2", "standard3", "storage_optimized_l1", "storage_optimized_l2"],
        Parameter,
    ]
    """Defines the SKU of an Azure Cognitive Search Service, which determines price tier and capacity limits."""
    tags: Union[Dict[str, Union[str, Parameter]], Parameter]
    """Tags to help categorize the resource in the Azure portal."""


SearchServiceResourceType = TypeVar(
    "SearchServiceResourceType", bound=Mapping[str, Any], default="SearchServiceResource"
)
ClientType = TypeVar("ClientType", default="SearchIndexClient")
_DEFAULT_SEARCH_SERVICE: "SearchServiceResource" = {
    "name": GLOBAL_PARAMS["defaultName"],
    "sku": {"name": "basic"},
    "properties": {
        "publicNetworkAccess": "Disabled",
    },
    "location": GLOBAL_PARAMS["location"],
    "tags": GLOBAL_PARAMS["azdTags"],
    "identity": {"type": "UserAssigned", "userAssignedIdentities": {GLOBAL_PARAMS["managedIdentityId"]: {}}},
}
_DEFAULT_SEARCH_SERVICE_EXTENSIONS: ExtensionResources = {
    "managed_identity_roles": [
        "Search Index Data Contributor",
        "Search Index Data Reader",
        "Search Service Contributor",
    ],
    "user_roles": ["Search Index Data Contributor", "Search Index Data Reader", "Search Service Contributor"],
}


class SearchService(_ClientResource, Generic[SearchServiceResourceType]):
    DEFAULTS: "SearchServiceResource" = _DEFAULT_SEARCH_SERVICE  # type: ignore[assignment]
    DEFAULT_EXTENSIONS: ExtensionResources = _DEFAULT_SEARCH_SERVICE_EXTENSIONS
    properties: SearchServiceResourceType
    parent: None  # type: ignore[reportIncompatibleVariableOverride]

    def __init__(
        self,
        properties: Optional["SearchServiceResource"] = None,
        /,
        name: Optional[Union[str, Parameter]] = None,
        **kwargs: Unpack[SearchServiceKwargs],
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
            # TODO: Finish full typing
            if "location" in kwargs:
                properties["location"] = kwargs.pop("location")
            if "managed_identities" in kwargs:
                properties["identity"] = convert_managed_identities(kwargs.pop("managed_identities"))
            if "network_acls" in kwargs:
                properties["properties"]["networkRuleSet"] = kwargs.pop("network_acls")
            if "public_network_access" in kwargs:
                properties["properties"]["publicNetworkAccess"] = kwargs.pop("public_network_access")
            if "sku" in kwargs:
                properties["sku"] = {"name": kwargs.pop("sku")}
            if "tags" in kwargs:
                properties["tags"] = kwargs.pop("tags")
        super().__init__(
            properties,
            extensions=extensions,
            existing=existing,
            identifier=ResourceIdentifiers.search,
            service_prefix=["search"],
            **kwargs,
        )

    @property
    def resource(self) -> Literal["Microsoft.Search/searchServices"]:
        return "Microsoft.Search/searchServices"

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
    ) -> "SearchService[ResourceReference]":
        existing = super().reference(
            name=name,
            resource_group=resource_group,
        )
        return cast(SearchService[ResourceReference], existing)

    def _build_endpoint(self, *, config_store: Optional[Mapping[str, Any]]) -> str:
        return f"https://{self._settings['name'](config_store=config_store)}.search.windows.net/"

    def _outputs(  # type: ignore[override]
        self, *, symbol: ResourceSymbol, suffix: str, **kwargs
    ) -> Dict[str, List[Output]]:
        outputs = super()._outputs(symbol=symbol, suffix=suffix, **kwargs)
        outputs["endpoint"].append(
            Output(
                f"AZURE_SEARCH_ENDPOINT{suffix}",
                Output("", "name", symbol).format("https://{}.search.windows.net/"),
            )
        )
        return outputs

    @overload
    def get_client(
        self,
        /,
        *,
        transport: Any = None,
        credential: Any = None,
        api_version: Optional[str] = None,
        audience: Optional[str] = None,
        config_store: Optional[Mapping[str, Any]] = None,
        use_async: Optional[Literal[False]] = None,
        **client_options,
    ) -> "SearchIndexClient": ...
    @overload
    def get_client(
        self,
        /,
        *,
        transport: Any = None,
        credential: Any = None,
        api_version: Optional[str] = None,
        audience: Optional[str] = None,
        config_store: Optional[Mapping[str, Any]] = None,
        use_async: Literal[True],
        **client_options,
    ) -> "AsyncSearchIndexClient": ...

    # TODO: I don't know why these don't work with either mypy or pyright.
    # @overload
    # def get_client(
    #     self,
    #     /,
    #     *,
    #     index_name: str,
    #     transport: Any = None,
    #     credential: Any = None,
    #     api_version: Optional[str] = None,
    #     audience: Optional[str] = None,
    #     config_store: Optional[Mapping[str, Any]] = None,
    #     use_async: Optional[Literal[False]] = None,
    #     **client_options,
    # ) -> "SearchClient":
    #     ...
    # @overload
    # def get_client(
    #     self,
    #     /,
    #     *,
    #     index_name: str,
    #     transport: Any = None,
    #     credential: Any = None,
    #     api_version: Optional[str] = None,
    #     audience: Optional[str] = None,
    #     config_store: Optional[Mapping[str, Any]] = None,
    #     use_async: Literal[True],
    #     **client_options,
    # ) -> "AsyncSearchClient":
    #     ...
    @overload
    def get_client(
        self,
        cls: Type[ClientType],
        /,
        *,
        transport: Any = None,
        credential: Any = None,
        api_version: Optional[str] = None,
        audience: Optional[str] = None,
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
        credential: Any = None,
        api_version: Optional[str] = None,
        audience: Optional[str] = None,
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
        api_version=None,
        audience=None,
        config_store=None,
        use_async=None,
        return_credential=False,
        **client_options,
    ):
        if cls is None:
            if use_async:
                if client_options.get("index_name"):
                    from azure.search.documents.aio import SearchClient as AsyncSearchClient

                    cls = AsyncSearchClient
                else:
                    from azure.search.documents.indexes.aio import SearchIndexClient as AsyncSearchIndexClient

                    cls = AsyncSearchIndexClient
            else:
                if client_options.get("index_name"):
                    from azure.search.documents import SearchClient as SyncSearchClient

                    cls = SyncSearchClient
                else:
                    from azure.search.documents.indexes import SearchIndexClient as SyncSearchIndexClient

                    cls = SyncSearchIndexClient
                use_async = False
        return super().get_client(
            cls,
            transport=transport,
            credential=credential,
            api_version=api_version,
            audience=audience,
            config_store=config_store,
            use_async=use_async,
            return_credential=return_credential,
            **client_options,
        )
