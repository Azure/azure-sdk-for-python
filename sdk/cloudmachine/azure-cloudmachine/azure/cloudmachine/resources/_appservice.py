# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import IO, ClassVar, List, Optional, Dict, Literal
from dataclasses import InitVar, field

from ._resource import (
    _serialize_resource,
    Resource,
    LocatedResource,
    ResourceGroup,
    dataclass_model,
    generate_symbol,
    _UNSET,
    ResourceID
)

@dataclass_model
class Capability:
    name: str = field(default=_UNSET, metadata={'rest': 'name'})
    reason: str = field(default=_UNSET, metadata={'rest': 'reason'})
    value: str = field(default=_UNSET, metadata={'rest': 'value'})


@dataclass_model
class SkuCapacity:
    default: int = field(default=_UNSET, metadata={'rest': 'default'})
    elastic_maximum: int = field(default=_UNSET, metadata={'rest': 'elasticMaximum'})
    maximum: int = field(default=_UNSET, metadata={'rest': 'maximum'})
    minimum: int = field(default=_UNSET, metadata={'rest': 'minimum'})
    scale_type: str = field(default=_UNSET, metadata={'rest': 'scaleType'})


@dataclass_model
class SkuDescription:
    name: str = field(metadata={'rest': 'name'})
    capabilities: Optional[List[Capability]] = field(default=_UNSET, metadata={'rest': 'capabilities'})
    capacity: Optional[int] = field(default=_UNSET, metadata={'rest': 'capacity'})
    family: Optional[str] = field(default=_UNSET, metadata={'rest': 'family'})
    locations: Optional[List[str]] = field(default=_UNSET, metadata={'rest': 'locations'})
    size: Optional[str] = field(default=_UNSET, metadata={'rest': 'size'})
    sku_capacity: Optional[SkuCapacity] = field(default=_UNSET, metadata={'rest': 'skuCapacity'})
    tier: Optional[str] = field(default=_UNSET, metadata={'rest': 'tier'})


@dataclass_model
class ExtendedLocation:
    name: str = field(metadata={'rest': 'name'})


@dataclass_model
class KubeEnvironmentProfile:
    id: ResourceID = field(metadata={'rest': 'id'})


@dataclass_model
class HostingEnvironmentProfile:
    id: ResourceID = field(metadata={'rest': 'id'})


@dataclass_model
class AppServicePlanProperties:
    elastic_scale_enabled: Optional[bool] = field(default=_UNSET, metadata={'rest': 'elasticScaleEnabled'})
    free_offer_expiration_time: Optional[str] = field(default=_UNSET, metadata={'rest': 'freeOfferExpirationTime'})
    hosting_environment_profile: Optional[HostingEnvironmentProfile] = field(default=_UNSET, metadata={'rest': 'hostingEnvironmentProfile'})
    hyper_v: Optional[bool] = field(default=_UNSET, metadata={'rest': 'hyperV'})
    is_spot: Optional[bool] = field(default=_UNSET, metadata={'rest': 'isSpot'})
    is_xenon: Optional[bool] = field(default=_UNSET, metadata={'rest': 'isXenon'})
    kube_environment_profile: Optional[KubeEnvironmentProfile] = field(default=_UNSET, metadata={'rest': 'kubeEnvironmentProfile'})
    maximum_elastic_worker_count: Optional[int] = field(default=_UNSET, metadata={'rest': 'maximumElasticWorkerCount'})
    per_site_scaling: Optional[bool] = field(default=_UNSET, metadata={'rest': 'perSiteScaling'})
    reserved: Optional[bool] = field(default=_UNSET, metadata={'rest': 'reserved'})
    spot_expiration_time: Optional[str] = field(default=_UNSET, metadata={'rest': 'spotExpirationTime'})
    target_worker_count: Optional[int] = field(default=_UNSET, metadata={'rest': 'targetWorkerCount'})
    target_worker_size_id: Optional[int] = field(default=_UNSET, metadata={'rest': 'targetWorkerSizeId'})
    worker_tier_name: Optional[str] = field(default=_UNSET, metadata={'rest': 'workerTierName'})
    zone_redundant: Optional[bool] = field(default=_UNSET, metadata={'rest': 'zoneRedundant'})

@dataclass_model
class ManagedServiceIdentity:
    type: Literal['None', 'SystemAssigned', 'SystemAssigned,UserAssigned','UserAssigned'] = field(metadata={'rest': 'type'})
    user_assigned_identities: Optional[Dict[str, ResourceID]] = field(default=_UNSET, metadata={'rest': 'userAssignedIdentities'})

@dataclass_model
class CloningInfo:
    # /subscriptions/{subId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Web/sites/{siteName} for production slots and
    # /subscriptions/{subId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Web/sites/{siteName}/slots/{slotName} for other slots.
    source_webapp_id: ResourceID  = field(metadata={'rest': 'sourceWebAppId'})
    app_settings_overrides: Optional[Dict[str, str]] = field(default=_UNSET, metadata={'rest': 'appSettingsOverrides'})
    clone_custom_hostnames: Optional[bool] = field(default=_UNSET, metadata={'rest': 'cloneCustomHostNames'})
    clone_source_control: Optional[bool] = field(default=_UNSET, metadata={'rest': 'cloneSourceControl'})
    configure_load_balancing: Optional[bool] = field(default=_UNSET, metadata={'rest': 'configureLoadBalancing'})
    correlation_id: Optional[str] = field(default=_UNSET, metadata={'rest': 'correlationId'})
    hosting_environment: Optional[str] = field(default=_UNSET, metadata={'rest': 'hostingEnvironment'})
    overwrite: Optional[bool] = field(default=_UNSET, metadata={'rest': 'overwrite'})
    source_webapp_location: Optional[str] = field(default=_UNSET, metadata={'rest': 'sourceWebAppLocation'})
    traffic_manager_profile_id: Optional[ResourceID] = field(default=_UNSET, metadata={'rest': 'trafficManagerProfileId'})
    traffic_manager_profile_name: Optional[str] = field(default=_UNSET, metadata={'rest': 'trafficManagerProfileName'})


@dataclass_model
class HostingEnvironmentProfile:
    id: ResourceID = field(metadata={'rest': 'id'})


@dataclass_model
class HostNameSslState:
    host_type: Optional[Literal['Repository', 'Standard']] = field(default=_UNSET, metadata={'rest': 'hostType'})
    name: Optional[str] = field(default=_UNSET, metadata={'rest': 'name'})
    ssl_state: Optional[Literal['Disabled', 'IpBasedEnabled', 'SniEnabled']] = field(default=_UNSET, metadata={'rest': 'sslState'})
    thumbprint: Optional[str] = field(default=_UNSET, metadata={'rest': 'thumbprint'})
    to_update: Optional[bool] = field(default=_UNSET, metadata={'rest': 'toUpdate'})
    virtual_ip: Optional[str] = field(default=_UNSET, metadata={'rest': 'virtualIP'})


@dataclass_model
class NameValuePair:
    name: str
    value: str


@dataclass_model
class SiteConfig:
    acrUseManagedIdentityCreds: Optional[bool]
    acrUserManagedIdentityID: Optional[str]
    alwaysOn: Optional[bool]
    # apiDefinition: Optional[ApiDefinitionInfo]
    # apiManagementConfig: Optional[ApiManagementConfig]
    # appCommandLine: Optional[str]
    # appSettings: Optional[List[NameValuePair]]
    # autoHealEnabled: Optional[bool]
    # autoHealRules: Optional[AutoHealRules]
    # autoSwapSlotName: Optional[str]
    # azureStorageAccounts: Optional[Dict[str, str]]
    # connectionStrings: Optional[List[ConnStringInfo]]
    # cors: Optional[CorsSettings]
    # defaultDocuments: Optional[List[str]]
    # detailedErrorLoggingEnabled: Optional[bool]
    # documentRoot: Optional[str]
    # elasticWebAppScaleLimit: Optional[int]
    # experiments: Optional[Experiments]
    # ftpsState: Optional[Literal['AllAllowed', 'Disabled', 'FtpsOnly']]

"""
SiteConfig

functionAppScaleLimit	Maximum number of workers that a site can scale out to.
This setting only applies to the Consumption and Elastic Premium Plans	int
functionsRuntimeScaleMonitoringEnabled	Gets or sets a value indicating whether functions runtime scale monitoring is enabled. When enabled,
the ScaleController will not monitor event sources directly, but will instead call to the
runtime to get scale status.	bool
handlerMappings	Handler mappings.	HandlerMapping[]
healthCheckPath	Health check path	string
http20Enabled	Http20Enabled: configures a web site to allow clients to connect over http2.0	bool
httpLoggingEnabled	true if HTTP logging is enabled; otherwise, false.	bool
ipSecurityRestrictions	IP security restrictions for main.	IpSecurityRestriction[]
ipSecurityRestrictionsDefaultAction	Default action for main access restriction if no rules are matched.	'Allow'
'Deny'
javaContainer	Java container.	string
javaContainerVersion	Java container version.	string
javaVersion	Java version.	string
keyVaultReferenceIdentity	Identity to use for Key Vault Reference authentication.	string
limits	Site limits.	SiteLimits
linuxFxVersion	Linux App Framework and version	string
loadBalancing	Site load balancing.	'LeastRequests'
'LeastResponseTime'
'PerSiteRoundRobin'
'RequestHash'
'WeightedRoundRobin'
'WeightedTotalTraffic'
localMySqlEnabled	true to enable local MySQL; otherwise, false.	bool
logsDirectorySizeLimit	HTTP logs directory size limit.	int
managedPipelineMode	Managed pipeline mode.	'Classic'
'Integrated'
managedServiceIdentityId	Managed Service Identity Id	int
metadata	Application metadata. This property cannot be retrieved, since it may contain secrets.	NameValuePair[]
minimumElasticInstanceCount	Number of minimum instance count for a site
This setting only applies to the Elastic Plans	int
minTlsVersion	MinTlsVersion: configures the minimum version of TLS required for SSL requests	'1.0'
'1.1'
'1.2'
netFrameworkVersion	.NET Framework version.	string
nodeVersion	Version of Node.js.	string
numberOfWorkers	Number of workers.	int
phpVersion	Version of PHP.	string
powerShellVersion	Version of PowerShell.	string
preWarmedInstanceCount	Number of preWarmed instances.
This setting only applies to the Consumption and Elastic Plans	int
publicNetworkAccess	Property to allow or block all public traffic.	string
publishingUsername	Publishing user name.	string
push	Push endpoint settings.	PushSettings
pythonVersion	Version of Python.	string
remoteDebuggingEnabled	true if remote debugging is enabled; otherwise, false.	bool
remoteDebuggingVersion	Remote debugging version.	string
requestTracingEnabled	true if request tracing is enabled; otherwise, false.	bool
requestTracingExpirationTime	Request tracing expiration time.	string
scmIpSecurityRestrictions	IP security restrictions for scm.	IpSecurityRestriction[]
scmIpSecurityRestrictionsDefaultAction	Default action for scm access restriction if no rules are matched.	'Allow'
'Deny'
scmIpSecurityRestrictionsUseMain	IP security restrictions for scm to use main.	bool
scmMinTlsVersion	ScmMinTlsVersion: configures the minimum version of TLS required for SSL requests for SCM site	'1.0'
'1.1'
'1.2'
scmType	SCM type.	'BitbucketGit'
'BitbucketHg'
'CodePlexGit'
'CodePlexHg'
'Dropbox'
'ExternalGit'
'ExternalHg'
'GitHub'
'LocalGit'
'None'
'OneDrive'
'Tfs'
'VSO'
'VSTSRM'
tracingOptions	Tracing options.	string
use32BitWorkerProcess	true to use 32-bit worker process; otherwise, false.	bool
virtualApplications	Virtual applications.	VirtualApplication[]
vnetName	Virtual Network name.	string
vnetPrivatePortsCount	The number of private ports assigned to this app. These will be assigned dynamically on runtime.	int
vnetRouteAllEnabled	Virtual Network Route All enabled. This causes all outbound traffic to have Virtual Network Security Groups and User Defined Routes applied.	bool
websiteTimeZone	Sets the time zone a site uses for generating timestamps. Compatible with Linux and Windows App Service. Setting the WEBSITE_TIME_ZONE app setting takes precedence over this config. For Linux, expects tz database values https://www.iana.org/time-zones (for a quick reference see https://en.wikipedia.org/wiki/List_of_tz_database_time_zones). For Windows, expects one of the time zones listed under HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Time Zones	string
webSocketsEnabled	true if WebSocket is enabled; otherwise, false.	bool
windowsFxVersion	Xenon App Framework and version	string
xManagedServiceIdentityId	Explicit Managed Service Identity Id	int

ApiDefinitionInfo
Name	Description	Value
url	The URL of the API definition.	string

ApiManagementConfig
Name	Description	Value
id	APIM-Api Identifier.	string

NameValuePair
Name	Description	Value
name	Pair name.	string
value	Pair value.	string

AutoHealRules
Name	Description	Value
actions	Actions to be executed when a rule is triggered.	AutoHealActions
triggers	Conditions that describe when to execute the auto-heal actions.	AutoHealTriggers


"""
@dataclass_model
class AutoHealCustomAction:
    exe: Optional[str] = field(default=_UNSET, metadata={'rest': 'exe'})
    parameters: Optional[str] = field(default=_UNSET, metadata={'rest': 'parameters'})


@dataclass_model
class AutoHealActions:
    action_type: Optional[Literal['CustomAction', 'LogEvent', 'Recycle']] = field(default=_UNSET, metadata={'rest': 'actionType'})
    custom_action: Optional[AutoHealCustomAction] = field(default=_UNSET, metadata={'rest': 'customAction'})
    min_process_execution_time: Optional[str] = field(default=_UNSET, metadata={'rest': 'minProcessExecutionTime'})


@dataclass_model
class RequestsBasedTrigger:
    count: Optional[int] = field(default=_UNSET, metadata={'rest': 'count'})
    time_interval: Optional[str] = field(default=_UNSET, metadata={'rest': 'timeInterval'})


@dataclass_model
class SlowRequestsBasedTrigger:
    count: Optional[int] = field(default=_UNSET, metadata={'rest': 'count'})
    path: Optional[str] = field(default=_UNSET, metadata={'rest': 'path'})
    time_taken: Optional[str] = field(default=_UNSET, metadata={'rest': 'timeTaken'})
    time_interval: Optional[str] = field(default=_UNSET, metadata={'rest': 'timeInterval'})


@dataclass_model
class StatusCodesBasedTrigger:
    count: Optional[int] = field(default=_UNSET, metadata={'rest': 'count'})
    path: Optional[str] = field(default=_UNSET, metadata={'rest': 'path'})
    status: Optional[int] = field(default=_UNSET, metadata={'rest': 'status'})
    sub_status: Optional[int] = field(default=_UNSET, metadata={'rest': 'subStatus'})
    time_interval: Optional[str] = field(default=_UNSET, metadata={'rest': 'timeInterval'})
    win32_status: Optional[int] = field(default=_UNSET, metadata={'rest': 'win32Status'})


@dataclass_model
class StatusCodesRangeBasedTrigger:
    count: Optional[int] = field(default=_UNSET, metadata={'rest': 'count'})
    path: Optional[str] = field(default=_UNSET, metadata={'rest': 'path'})
    status_codes: Optional[str] = field(default=_UNSET, metadata={'rest': 'statusCodes'})
    time_interval: Optional[str] = field(default=_UNSET, metadata={'rest': 'timeInterval'})


@dataclass_model
class AutoHealTriggers:
    private_bytes_in_kb: Optional[int] = field(default=_UNSET, metadata={'rest': 'privateBytesInKB'})
    requests: Optional[RequestsBasedTrigger] = field(default=_UNSET, metadata={'rest': 'requests'})
    slow_requests: Optional[SlowRequestsBasedTrigger] = field(default=_UNSET, metadata={'rest': 'slowRequests'})
    slow_requests_with_path: Optional[SlowRequestsBasedTrigger] = field(default=_UNSET, metadata={'rest': 'slowRequestsWithPath'})
    status_codes: Optional[StatusCodesBasedTrigger] = field(default=_UNSET, metadata={'rest': 'statusCodes'})
    status_codes_range: Optional[StatusCodesRangeBasedTrigger] = field(default=_UNSET, metadata={'rest': 'statusCodesRange'})


@dataclass_model
class ConnStringInfo:
    connection_string: Optional[str] = field(default=_UNSET, metadata={'rest': 'connectionString'})
    name: Optional[str] = field(default=_UNSET, metadata={'rest': 'name'})
    type: Optional[Literal['ApiHub', 'Custom', 'DocDb', 'EventHub', 'MySql', 'NotificationHub', 'PostgreSQL', 'RedisCache', 'SQLAzure', 'SQLServer', 'ServiceBus']] = field(default=_UNSET, metadata={'rest': 'type'})


@dataclass_model
class CorsSettings:
    allowed_origins: Optional[List[str]] = field(default=_UNSET, metadata={'rest': 'allowedOrigins'})
    support_credentials: Optional[bool] = field(default=_UNSET, metadata={'rest': 'supportCredentials'})


@dataclass_model
class RampUpRule:
    action_hostname: Optional[str] = field(default=_UNSET, metadata={'rest': 'actionHostName'})
    change_decision_callback_url: Optional[str] = field(default=_UNSET, metadata={'rest': 'changeDecisionCallbackUrl'})
    change_interval_in_minutes: Optional[int] = field(default=_UNSET, metadata={'rest': 'changeIntervalInMinutes'})
    change_step: Optional[int] = field(default=_UNSET, metadata={'rest': 'changeStep'})
    max_reroute_percentage: Optional[int] = field(default=_UNSET, metadata={'rest': 'maxReroutePercentage'})
    min_reroute_percentage: Optional[int] = field(default=_UNSET, metadata={'rest': 'minReroutePercentage'})
    name: Optional[str] = field(default=_UNSET, metadata={'rest': 'name'})
    reroute_percentage: Optional[int] = field(default=_UNSET, metadata={'rest': 'reroutePercentage'})


@dataclass_model
class Experiments:
    ramp_up_rules: List[RampUpRule] = field(metadata={'rest': 'rampUpRules'})


@dataclass_model
class HandlerMapping:
    arguments: Optional[str] = field(default=_UNSET, metadata={'rest': 'arguments'})
    extension: Optional[str] = field(default=_UNSET, metadata={'rest': 'extension'})
    script_processor: Optional[str] = field(default=_UNSET, metadata={'rest': 'scriptProcessor'})


@dataclass_model
class IpSecurityRestriction:
    action: Optional[str] = field(default=_UNSET, metadata={'rest': 'action'})
    description: Optional[str] = field(default=_UNSET, metadata={'rest': 'description'})
    headers: Optional[Dict[str, str]] = field(default=_UNSET, metadata={'rest': 'headers'})
    ip_address: Optional[str] = field(default=_UNSET, metadata={'rest': 'ipAddress'})
    name: Optional[str] = field(default=_UNSET, metadata={'rest': 'name'})
    priority: Optional[int] = field(default=_UNSET, metadata={'rest': 'priority'})
    subnet_mask: Optional[str] = field(default=_UNSET, metadata={'rest': 'subnetMask'})
    subnet_traffic_tag: Optional[int] = field(default=_UNSET, metadata={'rest': 'subnetTrafficTag'})
    tag: Optional[Literal['Default', 'ServiceTag', 'XffProxy']] = field(default=_UNSET, metadata={'rest': 'tag'})
    vnet_subnet_resource_id: Optional[str] = field(default=_UNSET, metadata={'rest': 'vnetSubnetResourceId'})
    vnet_traffic_tag: Optional[int] = field(default=_UNSET, metadata={'rest': 'vnetTrafficTag'})


@dataclass_model
class SiteLimits:
    max_disk_size_in_mb: Optional[int] = field(default=_UNSET, metadata={'rest': 'maxDiskSizeInMb'})
    max_memory_in_mb: Optional[int] = field(default=_UNSET, metadata={'rest': 'maxMemoryInMb'})
    max_percentage_cpu: Optional[int] = field(default=_UNSET, metadata={'rest': 'maxPercentageCpu'})


@dataclass_model
class PushSettingsProperties:
    is_push_enabled: bool = field(metadata={'rest': 'isPushEnabled'})
    dynamic_tags_json: Optional[str] = field(default=_UNSET, metadata={'rest': 'dynamicTagsJson'})
    tags_requiring_auth: Optional[str] = field(default=_UNSET, metadata={'rest': 'tagsRequiringAuth'})
    tag_whitelist_json: Optional[str] = field(default=_UNSET, metadata={'rest': 'tagWhitelistJson'})


@dataclass_model
class PushSettings:
    kind: str  = field(metadata={'rest': 'kind'})
    properties: Optional[PushSettingsProperties] = field(default=_UNSET, metadata={'rest': 'properties'})


@dataclass_model
class VirtualDirectory:
    physical_path: Optional[str] = field(default=_UNSET, metadata={'rest': 'physicalPath'})
    virtual_path: Optional[str] = field(default=_UNSET, metadata={'rest': 'virtualPath'})


@dataclass_model
class VirtualApplication:
    physical_path: Optional[str] = field(default=_UNSET, metadata={'rest': 'physicalPath'})
    preload_enabled: Optional[bool] = field(default=_UNSET, metadata={'rest': 'preloadEnabled'})
    virtual_directories: Optional[List[VirtualDirectory]] = field(default=_UNSET, metadata={'rest': 'virtualDirectories'})
    virtual_path: Optional[str] = field(default=_UNSET, metadata={'rest': 'virtualPath'})


@dataclass_model
class SiteProperties:
    client_affinity_enabled: Optional[bool] = field(default=_UNSET, metadata={'rest': 'clientAffinityEnabled'})
    client_cert_enabled: Optional[bool] = field(default=_UNSET, metadata={'rest': 'clientCertEnabled'})
    client_cert_exclusion_paths: Optional[str] = field(default=_UNSET, metadata={'rest': 'clientCertExclusionPaths'})
    client_cert_mode: Optional[Literal["Required", "Optional", "OptionalInteractiveUser"]] = field(default=_UNSET, metadata={'rest': 'clientCertMode'})
    cloningInfo: Optional[CloningInfo] = field(default=_UNSET, metadata={'rest': 'cloningInfo'})
    custom_domain_verification_id: Optional[str] = field(default=_UNSET, metadata={'rest': 'customDomainVerificationId'})
    daily_memory_time_quota: Optional[int] = field(default=_UNSET, metadata={'rest': 'dailyMemoryTimeQuota'})
    enabled: Optional[bool] = field(default=_UNSET, metadata={'rest': 'enabled'})
    hosting_environment_profile: Optional[HostingEnvironmentProfile] = field(default=_UNSET, metadata={'rest': 'hostingEnvironmentProfile'})
    hostnames_disabled: Optional[bool] = field(default=_UNSET, metadata={'rest': 'hostNamesDisabled'})
    hostname_ssl_states: Optional[List[HostNameSslState]] = field(default=_UNSET, metadata={'rest': 'hostNameSslStates'})
    https_only: Optional[bool] = field(default=_UNSET, metadata={'rest': 'httpsOnly'})
    hyper_v: Optional[bool] = field(default=_UNSET, metadata={'rest': 'hyperV'})
    is_xenon: Optional[bool] = field(default=_UNSET, metadata={'rest': 'isXenon'})
    keyvault_reference_identity: Optional[str] = field(default=_UNSET, metadata={'rest': 'keyVaultReferenceIdentity'})
    managed_environment_id: Optional[ResourceID] = field(default=_UNSET, metadata={'rest': 'managedEnvironmentId'})
    public_network_access: Optional[Literal["Enabled", "Disabled", ""]] = field(default=_UNSET, metadata={'rest': 'publicNetworkAccess'})
    redundancy_mode: Optional[Literal['ActiveActive', 'Failover', 'GeoRedundant', 'Manual', 'None']] = field(default=_UNSET, metadata={'rest': 'redundancyMode'})
    reserved: Optional[bool] = field(default=_UNSET, metadata={'rest': 'reserved'})
    scm_site_also_stopped: Optional[bool] = field(default=_UNSET, metadata={'rest': 'scmSiteAlsoStopped'})
    server_farm_id: Optional[ResourceID] = field(default=_UNSET, metadata={'rest': 'serverFarmId'})
    site_config: Optional[SiteConfig] = field(default=_UNSET, metadata={'rest': 'siteConfig'})
    storage_account_required: Optional[bool] = field(default=_UNSET, metadata={'rest': 'storageAccountRequired'})
    virtual_network_subnet_id: Optional[ResourceID] = field(default=_UNSET, metadata={'rest': 'virtualNetworkSubnetId'})
    vnet_content_share_enabled: Optional[bool] = field(default=_UNSET, metadata={'rest': 'vnetContentShareEnabled'})
    vnet_image_pull_enabled: Optional[bool] = field(default=_UNSET, metadata={'rest': 'vnetImagePullEnabled'})
    vnet_route_all_enabled: Optional[bool] = field(default=_UNSET, metadata={'rest': 'vnetRouteAllEnabled'})


@dataclass_model
class AppServiceSite(LocatedResource):
    kind: str = field(metadata={'rest': 'kind'})
    extended_location : Optional[ExtendedLocation] = field(default=_UNSET, metadata={'rest': 'extendedLocation'})
    identity: Optional[ManagedServiceIdentity] = field(default=_UNSET, metadata={'rest': 'identity'})
    properties: Optional[SiteProperties] = field(default=_UNSET, metadata={'rest': 'properties'})


@dataclass_model
class AppServicePlan(LocatedResource):
    sku: SkuDescription = field(metadata={'rest': 'sku'})
    kind: str = field(metadata={'rest': 'kind'})
    extended_location : Optional[ExtendedLocation] = field(default=_UNSET, metadata={'rest': 'extendedLocation'})
    properties: Optional[AppServicePlanProperties] = field(default=_UNSET, metadata={'rest': 'properties'})
    sites: InitVar[Optional[List[AppServiceSite]]] = None
    _sites: List[AppServiceSite] = field(init=False, default_factory=list)
    _resource: ClassVar[Literal['Microsoft.Web/serverfarms']] = 'Microsoft.Web/serverfarms'
    _version: ClassVar[str] = '2022-09-01'
    _symbolicname: str = field(default_factory=lambda: generate_symbol("serverfarm"), init=False, repr=False)

    def __post_init__(
            self,
            parent: Optional[Resource],
            scope: Optional[ResourceGroup],
            name: Optional[str],
            sites: Optional[List[AppServiceSite]]
    ):
        if sites:
            for s in sites:
                s._parent = self
                self._sites.append(s)
        super().__post_init__(parent, scope, name)


    def write(self, bicep: IO[str]) -> None:
        _serialize_resource(bicep, self)
        self._services.write(bicep)
        for container in self._containers:
            container.write(bicep)