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
    Union,
    Optional,
    cast,
)
from typing_extensions import TypeVar, Unpack, TypedDict

from ...resourcegroup import ResourceGroup
from ..._identifiers import ResourceIdentifiers
from ..._extension import ManagedIdentity, RoleAssignment
from ...._parameters import GLOBAL_PARAMS
from ...._bicep.expressions import ResourceSymbol, Parameter, Output
from ...._resource import (
    Resource,
    FieldsType,
    ResourceReference,
    ExtensionResources,
)
from ...._utils import find_last_resource_match
from .._resource import AppServicePlan
from ._config import SiteConfig

if TYPE_CHECKING:
    from .types import AppSiteResource


class AppSiteKwargs(TypedDict, total=False):
    kind: Literal[
        "api",
        "app",
        "app,container,windows",
        "app,linux",
        "app,linux,container",
        "functionapp",
        "functionapp,linux",
        "functionapp,linux,container",
        "functionapp,linux,container,azurecontainerapps",
        "functionapp,workflowapp",
        "functionapp,workflowapp,linux",
        "linux,api",
    ]
    """Type of site to deploy."""
    app_service_plan: Union[str, Parameter]
    """The resource ID of the app service plan to use for the site."""
    api_management_config: Dict[str, object]
    """The web settings api management configuration."""
    # app_insights: str
    # """Resource ID of the app insight to leverage for this resource."""
    # app_service_environment: str
    # """The resource ID of the app service environment to use for this resource."""
    app_settings: Dict[str, str]
    """The app settings-value pairs except for AzureWebJobsStorage, AzureWebJobsDashboard,
    APPINSIGHTS_INSTRUMENTATIONKEY and APPLICATIONINSIGHTS_CONNECTION_STRING.
    """
    # authSettingV2Configuration: Dict[str, object]
    # """The auth settings V2 configuration."""
    # basicPublishingCredentialsPolicies: List['BasicPublishingCredentialsPolicy']
    # """The site publishing credential policy names which are associated with the sites."""
    client_affinity_enabled: bool
    """If client affinity is enabled."""
    client_cert_enabled: bool
    """To enable client certificate authentication (TLS mutual authentication)."""
    client_cert_exclusion_paths: str
    """Client certificate authentication comma-separated exclusion paths."""
    client_cert_mode: Literal["Optional", "OptionalInteractiveUser", "Required"]
    """This composes with ClientCertEnabled setting."""
    cloning_info: Dict[str, object]
    """If specified during app creation, the app is cloned from a source app."""
    container_size: int
    """Size of the function container."""
    daily_memory_time_quota: int
    """Maximum allowed daily memory-time quota (applicable on dynamic apps only)."""
    # diagnosticSettings: List['DiagnosticSetting']
    # """The diagnostic settings of the service."""
    enabled: bool
    """Setting this value to false disables the app (takes the app offline)."""
    # function_app_config: Dict[str, object]
    # """The Function App configuration object."""
    hostname_ssl_states: List[object]
    """Hostname SSL states are used to manage the SSL bindings for app's hostnames."""
    https_only: bool
    """Configures a site to accept only HTTPS requests. Issues redirect for HTTP requests."""
    # hybrid_connection_relays: List[object]
    # """Names of hybrid connection relays to connect app with."""
    hyper_v: bool
    """Hyper-V sandbox."""
    keyvault_access_identity: Union[str, Parameter]
    """The resource ID of the assigned identity to be used to access a key vault with."""
    location: str
    """Location for all Resources."""
    # lock: 'Lock'
    # """The lock settings of the service."""
    # logsConfiguration: Dict[str, object]
    # """The logs settings configuration."""
    # managedEnvironmentId: str
    # """Azure Resource Manager ID of the customers selected Managed Environment on which to host this app."""
    managed_identities: "ManagedIdentity"
    """The managed identity definition for this resource."""
    # msDeployConfiguration: Dict[str, object]
    # """The extension MSDeployment configuration."""
    # privateEndpoints: List['PrivateEndpoint']
    # """Configuration details for private endpoints. For security reasons, it is recommended to use private
    # endpoints whenever possible.
    # """
    public_network_access: Literal["Disabled", "Enabled"]
    """Whether or not public network access is allowed for this resource. For security reasons it should be disabled.
    If not specified, it will be disabled by default if private endpoints are set.
    """
    redundancy_mode: Literal["ActiveActive", "Failover", "GeoRedundant", "Manual", "None"]
    """Site redundancy mode."""
    roles: Union[
        Parameter,
        List[
            Union[
                Parameter,
                "RoleAssignment",
                Literal[
                    "Web Plan Contributor",
                    "Website Contributor",
                    "App Compliance Automation Administrator",
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
                    "Web Plan Contributor",
                    "Website Contributor",
                    "App Compliance Automation Administrator",
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
    scm_site_also_stopped: bool
    """Stop SCM (KUDU) site when the app is stopped."""
    site_config: Dict[str, object]
    """The site config object. The defaults are set to the following values: alwaysOn: true,
    minTlsVersion: '1.2', ftpsState: 'FtpsOnly'.
    """
    # slots: List['Slot']
    # """Configuration for deployment slots for an app."""
    storage_account_required: bool
    """Checks if Customer provided storage account is required."""
    storage_account: Union[str, Parameter]
    """Required if app of kind functionapp. Resource ID of the storage account to manage triggers and logging
    function executions.
    """
    storage_account_use_identity_authentication: bool
    """If the provided storage account requires Identity based authentication ('allowSharedKeyAccess' is set to false).
    When set to true, the minimum role assignment required for the App Service Managed Identity to the storage account
    is 'Storage Blob Data Owner'.
    """
    tags: Union[Dict[str, Union[str, Parameter]], Parameter]
    """Tags of the resource."""
    # virtualNetworkSubnetId: str
    # """Azure Resource Manager ID of the Virtual network and subnet to be joined by Regional VNET Integration."""
    # vnetContentShareEnabled: bool
    # """To enable accessing content over virtual network."""
    # vnetImagePullEnabled: bool
    # """To enable pulling image over Virtual Network."""
    # vnetRouteAllEnabled: bool
    # """Virtual Network Route All enabled. This causes all outbound traffic to have Virtual Network Security Groups
    # and User Defined Routes applied.
    # """


AppSiteResourceType = TypeVar("AppSiteResourceType", bound=Mapping[str, Any], default="AppSiteResource")
_DEFAULT_APP_SITE: "AppSiteResource" = {
    "name": GLOBAL_PARAMS["defaultName"],
    "location": GLOBAL_PARAMS["location"],
    "tags": {"azd-service-name": GLOBAL_PARAMS["environmentName"]},
    "kind": "app,linux",
    "properties": {
        "httpsOnly": True,
        "clientAffinityEnabled": False,
        "siteConfig": {
            "minTlsVersion": "1.2",
            "use32BitWorkerProcess": False,
            "alwaysOn": True,
            "ftpsState": "FtpsOnly",
            "linuxFxVersion": "python|3.12",
            "cors": {"allowedOrigins": ["https://portal.azure.com", "https://ms.portal.azure.com"]},
        },
    },
    "identity": {"type": "UserAssigned", "userAssignedIdentities": {GLOBAL_PARAMS["managedIdentityId"]: {}}},
}
_DEFAULT_APP_SITE_EXTENSIONS: ExtensionResources = {"managed_identity_roles": [], "user_roles": []}


class AppSite(Resource, Generic[AppSiteResourceType]):
    DEFAULTS: "AppSiteResource" = _DEFAULT_APP_SITE  # type: ignore[assignment]
    DEFAULT_EXTENSIONS: ExtensionResources = _DEFAULT_APP_SITE_EXTENSIONS
    properties: AppSiteResourceType
    parent: None  # type: ignore[reportIncompatibleVariableOverride]

    def __init__(
        self,
        properties: Optional["AppSiteResource"] = None,
        /,
        name: Optional[Union[str, Parameter]] = None,
        plan: Optional[Union[str, Parameter, AppServicePlan]] = None,
        **kwargs: Unpack[AppSiteKwargs],
    ) -> None:
        existing = kwargs.pop("existing", False)  # type: ignore[typeddict-item]
        extensions: ExtensionResources = defaultdict(list)  # type: ignore  # Doesn't like the default dict.
        if "roles" in kwargs:
            extensions["managed_identity_roles"] = kwargs.pop("roles")
        if "user_roles" in kwargs:
            extensions["user_roles"] = kwargs.pop("user_roles")
        # TODO: Finish populating kwarg properties
        if isinstance(plan, AppServicePlan):
            self._plan = plan
        else:
            # 'parent' is passed by the reference classmethod.
            self._plan = kwargs.pop("parent", AppServicePlan(name=plan))  # type: ignore[typeddict-item]
        if not existing:
            properties = properties or {}
            if "properties" not in properties:
                properties["properties"] = {}
            if name:
                properties["name"] = name
            if "location" in kwargs:
                properties["location"] = kwargs.pop("location")
            if "tags" in kwargs:
                properties["tags"] = kwargs.pop("tags")
        self._app_settings = kwargs.pop("app_settings", {})
        super().__init__(
            properties,
            extensions=extensions,
            service_prefix=["app_site"],
            existing=existing,
            identifier=ResourceIdentifiers.app_service_site,
            **kwargs,
        )

    @classmethod
    def reference(  # type: ignore[override]  # Parameter subset and renames
        cls,
        *,
        name: Union[str, Parameter],
        plan: Union[str, Parameter, AppServicePlan[ResourceReference]],
        resource_group: Optional[Union[str, Parameter, ResourceGroup[ResourceReference]]] = None,
    ) -> "AppSite[ResourceReference]":
        if isinstance(plan, (str, Parameter)):
            parent = AppServicePlan.reference(
                name=plan,
                resource_group=resource_group,
            )
        else:
            parent = plan
        existing = super().reference(name=name, parent=parent)
        return cast(AppSite[ResourceReference], existing)

    @property
    def resource(self) -> Literal["Microsoft.Web/sites"]:
        return "Microsoft.Web/sites"

    @property
    def version(self) -> str:
        from .types import VERSION

        return VERSION

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
        if not merged_properties.get("serverFarmId"):
            symbols = self._plan.__bicep__(fields, parameters=parameters)
            merged_properties["serverFarmId"] = symbols[0].id

        app_settings = {
            "SCM_DO_BUILD_DURING_DEPLOYMENT": "true",
            "ENABLE_ORYX_BUILD": "true",
            "PYTHON_ENABLE_GUNICORN_MULTIWORKERS": "true",
            "AZURE_CLIENT_ID": parameters["managedIdentityClientId"],
        }
        app_config = find_last_resource_match(fields, resource=ResourceIdentifiers.config_store)
        if app_config:
            app_settings["AZURE_APPCONFIG_ENDPOINT"] = app_config.outputs["endpoint"][0]
        app_settings.update(self._app_settings)
        site_settings = SiteConfig({"parent": symbol}, name="appsettings", settings=app_settings, parent=self)
        site_settings.__bicep__(fields, parameters=parameters)
        app_logs = SiteConfig(
            {"parent": symbol},
            name="logs",
            settings={
                "applicationLogs": {"fileSystem": {"level": "Verbose"}},
                "detailedErrorMessages": {"enabled": True},
                "failedRequestsTracing": {"enabled": True},
                "httpLogs": {"fileSystem": {"enabled": True, "retentionInDays": 1, "retentionInMb": 35}},
            },
            parent=self,
        )
        app_logs.__bicep__(fields, parameters=parameters)
        return merged_properties

    def _outputs(self, **kwargs) -> Dict[str, List[Output]]:
        return {}
