# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=arguments-differ

from collections import defaultdict
from collections.abc import Mapping as ABCMapping
import inspect
from typing import (
    TYPE_CHECKING,
    Any,
    TypedDict,
    Generic,
    Literal,
    Mapping,
    Tuple,
    Type,
    Union,
    Optional,
    cast,
    overload,
    get_origin,
)
from typing_extensions import TypeVar, Unpack

from ..resourcegroup import ResourceGroup
from .._identifiers import ResourceIdentifiers
from .._extension import RoleAssignment, convert_managed_identities, ManagedIdentity
from ..._parameters import GLOBAL_PARAMS
from ..._bicep.expressions import Output, ResourceSymbol, Parameter
from ..._resource import _ClientResource, ResourceReference, ExtensionResources

if TYPE_CHECKING:
    from ._types import ConfigurationStoreResource

    from azure.core.credentials import SupportsTokenInfo
    from azure.core.credentials_async import AsyncSupportsTokenInfo
    from azure.appconfiguration import AzureAppConfigurationClient
    from azure.appconfiguration.aio import AzureAppConfigurationClient as AsyncAzureAppConfigurationClient


class ConfigStoreKwargs(TypedDict, total=False):
    create_mode: Union[Literal["Default", "Recover"], Parameter]
    """Indicates whether the configuration store need to be recovered."""
    # customerManagedKey: 'CustomerManagedKey'
    # """The customer managed key definition."""
    # diagnosticSettings: List['DiagnosticSetting']
    # """The diagnostic settings of the service."""
    disable_local_auth: Union[bool, Parameter]
    """Disables all authentication methods other than AAD authentication."""
    enable_purge_protection: Union[bool, Parameter]
    """Property specifying whether protection against purge is enabled for this configuration store. Defaults to true
    unless sku is set to Free, since purge protection is not available in Free tier.
    """
    # keyValues: List['KeyValue']
    # """All Key / Values to create. Requires local authentication to be enabled."""
    location: Union[str, Parameter]
    """Location for all Resources."""
    # lock: 'Lock'
    # """The lock settings of the service."""
    managed_identities: Optional[ManagedIdentity]
    """The managed identity definition for this resource."""
    # privateEndpoints: List['PrivateEndpoint']
    # """Configuration details for private endpoints. For security reasons, it is recommended to use private
    # endpoints whenever possible.
    # """
    public_network_access: Union[Literal["Disabled", "Enabled"], Parameter]
    """Whether or not public network access is allowed for this resource. For security reasons it should be
    disabled. If not specified, it will be disabled by default if private endpoints are set.
    """
    # replica_locations: Union[List[Union[str, Parameter]], Parameter]
    # """All Replicas to create."""
    roles: Union[
        Parameter,
        list[
            Union[
                Parameter,
                "RoleAssignment",
                Literal[
                    "App Compliance Automation Administrator",
                    "App Compliance Automation Reader",
                    "App Configuration Contributor",
                    "App Configuration Data Owner",
                    "App Configuration Data Reader",
                    "App Configuration Reader",
                    "Contributor",
                    "Owner",
                    "Reader",
                    "Role Based Access Control Administrator",
                    "User Access Administrator",
                ],
            ]
        ],
    ]
    """Array of role assignments to create for the managed identity."""
    user_roles: Union[
        Parameter,
        list[
            Union[
                Parameter,
                "RoleAssignment",
                Literal[
                    "App Compliance Automation Administrator",
                    "App Compliance Automation Reader",
                    "App Configuration Contributor",
                    "App Configuration Data Owner",
                    "App Configuration Data Reader",
                    "App Configuration Reader",
                    "Contributor",
                    "Owner",
                    "Reader",
                    "Role Based Access Control Administrator",
                    "User Access Administrator",
                ],
            ]
        ],
    ]
    """Array of role assignments to create for the user principal ID."""
    sku: Literal["Free", "Standard"]
    """Pricing tier of App Configuration."""
    soft_delete_retention: int
    """The amount of time in days that the configuration store will be retained when it is soft deleted."""
    tags: Union[dict[str, Union[str, Parameter]], Parameter]
    """Resource tags."""


ConfigStoreResourceType = TypeVar(
    "ConfigStoreResourceType", bound=Mapping[str, Any], default="ConfigurationStoreResource"
)
ClientType = TypeVar("ClientType")
_DEFAULT_CONFIG_STORE: "ConfigurationStoreResource" = {
    "name": GLOBAL_PARAMS["defaultName"],
    "sku": {"name": "Standard"},
    "properties": {
        "disableLocalAuth": True,
        "createMode": "Default",
        "dataPlaneProxy": {"authenticationMode": "Pass-through", "privateLinkDelegation": "Disabled"},
        "publicNetworkAccess": "Enabled",
    },
    "location": GLOBAL_PARAMS["location"],
    "tags": GLOBAL_PARAMS["azdTags"],
    "identity": {"type": "UserAssigned", "userAssignedIdentities": {GLOBAL_PARAMS["managedIdentityId"]: {}}},
}
_DEFAULT_CONFIG_STORE_EXTENSIONS: ExtensionResources = {
    # TODO: Not sure what the best roles are here, does the managed identity need to be able to
    # write config settings? Hopefully not.
    "managed_identity_roles": ["App Configuration Data Reader"],
    "user_roles": ["App Configuration Data Owner"],
}


class ConfigStore(_ClientResource, Generic[ConfigStoreResourceType]):
    """Azure App Configuration Store resource representation.

    A class representing an Azure App Configuration Store that provides centralized storage and management
    of application settings and feature flags.

    :ivar DEFAULTS: Default configuration settings for the Config Store resource
    :vartype DEFAULTS: ConfigurationStoreResource
    :ivar DEFAULT_EXTENSIONS: Default role assignments and extensions configuration
    :vartype DEFAULT_EXTENSIONS: ExtensionResources
    :ivar properties: Properties of the Config Store resource
    :vartype properties: ConfigStoreResourceType
    :ivar parent: Parent resource (None for ConfigStore as it's a top-level resource)
    :vartype parent: None

    :param properties: Optional dictionary containing the Config Store resource properties
    :type properties: Optional[ConfigurationStoreResource]
    :param name: Optional name for the Config Store
    :type name: Optional[Union[str, Parameter]]
    :keyword create_mode: Indicates whether the configuration store needs to be recovered
    :paramtype create_mode: Union[Literal["Default", "Recover"], Parameter]
    :keyword disable_local_auth: Disables all authentication methods other than AAD authentication
    :paramtype disable_local_auth: Union[bool, Parameter]
    :keyword enable_purge_protection: Property specifying whether protection against purge is enabled
    :paramtype enable_purge_protection: Union[bool, Parameter]
    :keyword location: Location for all resources
    :paramtype location: Union[str, Parameter]
    :keyword managed_identities: The managed identity definition for this resource
    :paramtype managed_identities: Optional[ManagedIdentity]
    :keyword public_network_access: Whether or not public network access is allowed for this resource
    :paramtype public_network_access: Union[Literal["Disabled", "Enabled"], Parameter]
    :keyword roles: Array of role assignments to create for the managed identity
    :paramtype roles: Union[Parameter, list[Union[Parameter, RoleAssignment, str]]]
    :keyword user_roles: Array of role assignments to create for the user principal ID
    :paramtype user_roles: Union[Parameter, list[Union[Parameter, RoleAssignment, str]]]
    :keyword sku: Pricing tier of App Configuration
    :paramtype sku: Literal["Free", "Standard"]
    :keyword soft_delete_retention: The amount of time in days that the configuration store will be
     retained when soft deleted
    :paramtype soft_delete_retention: int
    :keyword tags: Resource tags
    :paramtype tags: Union[dict[str, Union[str, Parameter]], Parameter]
    """

    DEFAULTS: "ConfigurationStoreResource" = _DEFAULT_CONFIG_STORE  # type: ignore[assignment]
    DEFAULT_EXTENSIONS: ExtensionResources = _DEFAULT_CONFIG_STORE_EXTENSIONS
    properties: ConfigStoreResourceType
    parent: None  # type: ignore[reportIncompatibleVariableOverride]

    def __init__(
        self,
        properties: Optional["ConfigurationStoreResource"] = None,
        /,
        name: Optional[Union[str, Parameter]] = None,
        **kwargs: Unpack[ConfigStoreKwargs],
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
            if "create_mode" in kwargs:
                properties["properties"]["createMode"] = kwargs.pop("create_mode")
            if "disable_local_auth" in kwargs:
                properties["properties"]["disableLocalAuth"] = kwargs.pop("disable_local_auth")
            if "enable_purge_protection" in kwargs:
                properties["properties"]["enablePurgeProtection"] = kwargs.pop("enable_purge_protection")
            if "location" in kwargs:
                properties["location"] = kwargs.pop("location")
            if "managed_identities" in kwargs:
                properties["identity"] = convert_managed_identities(kwargs.pop("managed_identities"))
            if "soft_delete_retention" in kwargs:
                properties["properties"]["softDeleteRetentionInDays"] = kwargs.pop("soft_delete_retention")
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
            identifier=ResourceIdentifiers.config_store,
            service_prefix=["appconfig", "app_config"],
            **kwargs,
        )

    @property
    def resource(self) -> Literal["Microsoft.AppConfiguration/configurationStores"]:
        return "Microsoft.AppConfiguration/configurationStores"

    @property
    def version(self) -> str:
        from ._types import VERSION

        return VERSION

    @classmethod
    def reference(  # type: ignore[override]  # Parameter subset and renames
        cls,
        *,
        name: Union[str, Parameter],
        resource_group: Optional[Union[str, Parameter, ResourceGroup[ResourceReference]]] = None,
    ) -> "ConfigStore[ResourceReference]":
        existing = super().reference(
            name=name,
            resource_group=resource_group,
        )
        return cast(ConfigStore[ResourceReference], existing)

    def _build_endpoint(self, *, config_store: Optional[Mapping[str, Any]]) -> str:
        return f"https://{self._settings['name'](config_store=config_store)}.azconfig.io"

    def _outputs(self, *, symbol: ResourceSymbol, suffix: str, **kwargs) -> dict[str, list[Output]]:
        if suffix == "_CONFIG_STORE":
            # This is the default config store attrname - let's just ignore it.
            suffix = ""
        outputs = super()._outputs(symbol=symbol, suffix=suffix, **kwargs)
        outputs["endpoint"].append(Output(f"AZURE_APPCONFIG_ENDPOINT{suffix}", "properties.endpoint", symbol))
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
    ) -> "AzureAppConfigurationClient": ...
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
    ) -> "AsyncAzureAppConfigurationClient": ...
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
                from azure.appconfiguration.aio import AzureAppConfigurationClient as AsyncAzureAppConfigurationClient

                cls = AsyncAzureAppConfigurationClient
            else:
                from azure.appconfiguration import AzureAppConfigurationClient as SyncAzureAppConfigurationClient

                cls = SyncAzureAppConfigurationClient
                use_async = False
        elif get_origin(cls) is ABCMapping or cls.__name__ == "AzureAppConfigurationProvider":
            # TODO: This should be two separate branches, default Mapping should be a simple
            # download of the config into a map using a simple raw PipelineClient (can still apply
            # pipeline config kwargs). Then we can remove dependency.
            if use_async or inspect.iscoroutinefunction(getattr(cls, "close", None)):
                from azure.appconfiguration.provider.aio import load

                cls = load
                use_async = True
            else:
                from azure.appconfiguration.provider import load

                cls = load
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
