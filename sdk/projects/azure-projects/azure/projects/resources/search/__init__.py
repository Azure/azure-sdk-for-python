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
    Callable,
    Dict,
    List,
    Literal,
    Mapping,
    TypedDict,
    Union,
    Optional,
    overload,
)
from typing_extensions import TypeVar, Unpack

from ..resourcegroup import ResourceGroup
from .._identifiers import ResourceIdentifiers
from ..._component import ComponentField
from .._extension import convert_managed_identities, ManagedIdentity, RoleAssignment
from ..._parameters import GLOBAL_PARAMS
from ..._bicep.expressions import Output, ResourceSymbol, Parameter
from ..._resource import _ClientResource, ResourceReference, ExtensionResources

if TYPE_CHECKING:
    from .types import SearchServiceResource, SearchNetworkRuleSet
    from azure.search.documents import SearchClient
    from azure.search.documents.indexes import SearchIndexClient


class SearchServiceKwargs(TypedDict, total=False):
    auth_options: "AuthOption"
    """Defines the options for how the data plane API of a Search service authenticates requests. Must remain an
    empty object {} if 'disableLocalAuth' is set to true.
    """
    cmk_enforcement: Literal["Disabled", "Enabled", "Unspecified"]
    """Describes a policy that determines how resources within the search service are to be encrypted with Customer
    Managed Keys.
    """
    # diagnostic_settings: List['DiagnosticSetting']
    # """The diagnostic settings of the service."""
    disable_local_auth: bool
    """When set to true, calls to the search service will not be permitted to utilize API keys for authentication.
    This cannot be set to true if 'authOptions' are defined.
    """
    hosting_mode: Literal["default", "highDensity"]
    """Applicable only for the standard3 SKU. You can set this property to enable up to 3 high density partitions that
    allow up to 1000 indexes, which is much higher than the maximum indexes allowed for any other SKU. For the
    standard3 SKU, the value is either 'default' or 'highDensity'. For all other SKUs, this value must be 'default'.
    """
    location: str
    """Location for all Resources."""
    # lock: 'Lock'
    # """The lock settings for all Resources in the solution."""
    managed_identities: "ManagedIdentity"
    """The managed identity definition for this resource."""
    network_acls: "SearchNetworkRuleSet"
    """Network specific rules that determine how the Azure Cognitive Search service may be reached."""
    partition_count: int
    """The number of partitions in the search service; if specified, it can be 1, 2, 3, 4, 6, or 12. Values greater
    than 1 are only valid for standard SKUs. For 'standard3' services with hostingMode set to 'highDensity', the
    allowed values are between 1 and 3.
    """
    # private_endpoints: List['PrivateEndpoint']
    # """Configuration details for private endpoints. For security reasons, it is recommended to use private endpoints
    # whenever possible.
    # """
    public_network_access: Literal["Disabled", "Enabled"]
    """This value can be set to 'Enabled' to avoid breaking changes on existing customer resources and templates. If
    set to 'Disabled', traffic over public interface is not allowed, and private endpoint connections would be the
    exclusive access method.
    """
    replica_count: int
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
    semantic_search: Literal["disabled", "free", "standard"]
    """Sets options that control the availability of semantic search. This configuration is only possible for certain
    search SKUs in certain locations.
    """
    # shared_private_link_resources: List['SharedPrivateLinkResource']
    # """The sharedPrivateLinkResources to create as part of the search Service."""
    sku: Literal["basic", "free", "standard", "standard2", "standard3", "storage_optimized_l1", "storage_optimized_l2"]
    """Defines the SKU of an Azure Cognitive Search Service, which determines price tier and capacity limits."""
    tags: Dict[str, object]
    """Tags to help categorize the resource in the Azure portal."""


SearchServiceResourceType = TypeVar("SearchServiceResourceType", default="SearchServiceResource")
ClientType = TypeVar("ClientType", default="SearchIndexClient")
_DEFAULT_SEARCH_SERVICE: "SearchServiceResource" = {
    "name": GLOBAL_PARAMS["defaultName"],
    "sku": {"name": "basic"},
    "properties": {
        "publicNetworkAccess": "Disabled",
    },
    "location": GLOBAL_PARAMS["location"],
    "tags": GLOBAL_PARAMS["azdTags"],
    "identity": {"type": "UserAssigned", "userAssignedIdentities": {GLOBAL_PARAMS["managedIdentityId"].format(): {}}},
}
_DEFAULT_SEARCH_SERVICE_EXTENSIONS: ExtensionResources = {
    "managed_identity_roles": [
        "Search Index Data Contributor",
        "Search Index Data Reader",
        "Search Service Contributor",
    ],
    "user_roles": ["Search Index Data Contributor", "Search Index Data Reader", "Search Service Contributor"],
}


class SearchService(_ClientResource[SearchServiceResourceType]):
    DEFAULTS: "SearchServiceResource" = _DEFAULT_SEARCH_SERVICE
    DEFAULT_EXTENSIONS: ExtensionResources = _DEFAULT_SEARCH_SERVICE_EXTENSIONS
    resource: Literal["Microsoft.Search/searchServices"]
    properties: SearchServiceResourceType

    def __init__(
        self,
        properties: Optional["SearchServiceResource"] = None,
        /,
        name: Optional[Union[str, Parameter]] = None,
        **kwargs: Unpack[SearchServiceKwargs],
    ) -> None:
        existing = kwargs.pop("existing", False)
        extensions: ExtensionResources = defaultdict(list)
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
                properties["sku"] = properties.get("sku", {})
                properties["sku"]["name"] = kwargs.pop("sku")
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
    def resource(self) -> str:
        if self._resource:
            return self._resource
        from .types import RESOURCE

        self._resource = RESOURCE
        return self._resource

    @property
    def version(self) -> str:
        if self._version:
            return self._version
        from .types import VERSION

        self._version = VERSION
        return self._version

    @classmethod
    def reference(
        cls,
        *,
        name: Union[str, Parameter, ComponentField],
        resource_group: Optional[Union[str, Parameter, ResourceGroup]] = None,
    ) -> "SearchService[ResourceReference]":
        from .types import RESOURCE, VERSION

        resource = f"{RESOURCE}@{VERSION}"
        return super().reference(
            resource=resource,
            name=name,
            resource_group=resource_group,
        )

    def _build_endpoint(self, *, config_store: Mapping[str, Any]) -> str:
        return f"https://{self._settings['name'](config_store=config_store)}.search.windows.net/"

    def _outputs(self, *, symbol: ResourceSymbol, **kwargs) -> Dict[str, Output]:
        outputs = super()._outputs(symbol=symbol, **kwargs)
        outputs["endpoint"] = Output(
            f"AZURE_SEARCH_ENDPOINT{self._suffix}", Output("", "name", symbol).format("https://{}.search.windows.net/")
        )
        return outputs

    @overload
    def get_client(
        self,
        *,
        transport: Any = None,
        api_version: Optional[str] = None,
        audience: Optional[str] = None,
        config_store: Optional[Mapping[str, Any]] = None,
        env_name: Optional[str] = None,
        use_async: Optional[bool] = None,
        **client_options,
    ) -> "SearchIndexClient": ...
    @overload
    def get_client(
        self,
        *,
        transport: Any = None,
        api_version: Optional[str] = None,
        audience: Optional[str] = None,
        config_store: Optional[Mapping[str, Any]] = None,
        env_name: Optional[str] = None,
        use_async: Optional[bool] = None,
        index_name: str,
        **client_options,
    ) -> "SearchClient": ...
    @overload
    def get_client(
        self,
        cls: Callable[..., ClientType],
        /,
        *,
        transport: Any = None,
        api_version: Optional[str] = None,
        audience: Optional[str] = None,
        config_store: Optional[Mapping[str, Any]] = None,
        env_name: Optional[str] = None,
        use_async: Optional[bool] = None,
        **client_options,
    ) -> ClientType: ...
    def get_client(
        self,
        cls: Optional[Callable[..., ClientType]] = None,
        /,
        *,
        use_async: Optional[bool] = None,
        **kwargs,
    ) -> ClientType:
        if cls is None:
            if use_async:
                if kwargs.get("index_name"):
                    from azure.search.documents.aio import SearchClient

                    cls = SearchClient
                else:
                    from azure.search.documents.indexes.aio import SearchIndexClient

                    cls = SearchIndexClient
            else:
                if kwargs.get("index_name"):
                    from azure.search.documents import SearchClient

                    cls = SearchClient
                else:
                    from azure.search.documents.indexes import SearchIndexClient

                    cls = SearchIndexClient
                use_async = False
        return super().get_client(cls, use_async=use_async, **kwargs)
