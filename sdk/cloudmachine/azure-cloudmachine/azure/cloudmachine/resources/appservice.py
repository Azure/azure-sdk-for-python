# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import IO, Any, ClassVar, List, Optional, Dict, Literal
from dataclasses import field

from ._resource import (
    _SKIP,
    _serialize_resource,
    Resource,
    ResourceId,
    LocatedResource,
    dataclass_model,
    generate_symbol,
    _UNSET,
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
    id: ResourceId = field(metadata={'rest': 'id'})


@dataclass_model
class HostingEnvironmentProfile:
    id: ResourceId = field(metadata={'rest': 'id'})


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
    user_assigned_identities: Optional[Dict[str, ResourceId]] = field(default=_UNSET, metadata={'rest': 'userAssignedIdentities'})


@dataclass_model
class CloningInfo:
    source_webapp_id: ResourceId  = field(metadata={'rest': 'sourceWebAppId'})
    app_settings_overrides: Optional[Dict[str, str]] = field(default=_UNSET, metadata={'rest': 'appSettingsOverrides'})
    clone_custom_hostnames: Optional[bool] = field(default=_UNSET, metadata={'rest': 'cloneCustomHostNames'})
    clone_source_control: Optional[bool] = field(default=_UNSET, metadata={'rest': 'cloneSourceControl'})
    configure_load_balancing: Optional[bool] = field(default=_UNSET, metadata={'rest': 'configureLoadBalancing'})
    correlation_id: Optional[str] = field(default=_UNSET, metadata={'rest': 'correlationId'})
    hosting_environment: Optional[str] = field(default=_UNSET, metadata={'rest': 'hostingEnvironment'})
    overwrite: Optional[bool] = field(default=_UNSET, metadata={'rest': 'overwrite'})
    source_webapp_location: Optional[str] = field(default=_UNSET, metadata={'rest': 'sourceWebAppLocation'})
    traffic_manager_profile_id: Optional[ResourceId] = field(default=_UNSET, metadata={'rest': 'trafficManagerProfileId'})
    traffic_manager_profile_name: Optional[str] = field(default=_UNSET, metadata={'rest': 'trafficManagerProfileName'})


@dataclass_model
class HostingEnvironmentProfile:
    id: ResourceId = field(metadata={'rest': 'id'})


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
    name: str = field(metadata={'rest': 'name'})
    value: str = field(metadata={'rest': 'value'})


@dataclass_model
class ApiDefinitionInfo:
    url: str = field(metadata={'rest': 'url'})


@dataclass_model
class ApiManagementConfig:
    id: ResourceId = field(metadata={'rest': 'id'})


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


class AutoHealRules:
    actions: Optional[AutoHealActions] = field(metadata={'rest': 'actions'})
    triggers: Optional[AutoHealTriggers] = field(metadata={'rest': 'triggers'})


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
class SiteConfig:
    acr_use_managed_identity_creds: Optional[bool] = field(default=_UNSET, metadata={'rest': 'acrUseManagedIdentityCreds'})
    acr_user_managed_identity_id: Optional[str] = field(default=_UNSET, metadata={'rest': 'acrUserManagedIdentityID'})
    always_on: Optional[bool] = field(default=_UNSET, metadata={'rest': 'alwaysOn'})
    api_definition: Optional[ApiDefinitionInfo] = field(default=_UNSET, metadata={'rest': 'apiDefinition'})
    api_management_config: Optional[ApiManagementConfig] = field(default=_UNSET, metadata={'rest': 'apiManagementConfig'})
    app_command_line: Optional[str] = field(default=_UNSET, metadata={'rest': 'appCommandLine'})
    app_settings: Optional[List[NameValuePair]] = field(default=_UNSET, metadata={'rest': 'appSettings'})
    auto_heal_enabled: Optional[bool] = field(default=_UNSET, metadata={'rest': 'autoHealEnabled'})
    auto_heal_rules: Optional[AutoHealRules] = field(default=_UNSET, metadata={'rest': 'autoHealRules'})
    auto_swap_slot_name: Optional[str] = field(default=_UNSET, metadata={'rest': 'autoSwapSlotName'})
    azure_storage_accounts: Optional[Dict[str, str]] = field(default=_UNSET, metadata={'rest': 'azureStorageAccounts'})
    connection_strings: Optional[List[ConnStringInfo]] = field(default=_UNSET, metadata={'rest': 'connectionStrings'})
    cors: Optional[CorsSettings] = field(default=_UNSET, metadata={'rest': 'cors'})
    default_documents: Optional[List[str]] = field(default=_UNSET, metadata={'rest': 'defaultDocuments'})
    detailed_error_logging_enabled: Optional[bool] = field(default=_UNSET, metadata={'rest': 'detailedErrorLoggingEnabled'})
    document_root: Optional[str] = field(default=_UNSET, metadata={'rest': 'documentRoot'})
    elastic_web_app_scale_limit: Optional[int] = field(default=_UNSET, metadata={'rest': 'elasticWebAppScaleLimit'})
    experiments: Optional[Experiments] = field(default=_UNSET, metadata={'rest': 'experiments'})
    ftps_state: Optional[Literal['AllAllowed', 'Disabled', 'FtpsOnly']] = field(default=_UNSET, metadata={'rest': 'ftpsState'})
    function_app_scale_limit: Optional[int] = field(default=_UNSET, metadata={'rest': 'functionAppScaleLimit'})
    functions_runtime_scale_monitoring_enabled: Optional[bool] = field(default=_UNSET, metadata={'rest': 'functionsRuntimeScaleMonitoringEnabled'})
    handler_mappings: Optional[List[HandlerMapping]] = field(default=_UNSET, metadata={'rest': 'handlerMappings'})
    health_check_path: Optional[str] = field(default=_UNSET, metadata={'rest': 'healthCheckPath'})
    http20_enabled: Optional[bool] = field(default=_UNSET, metadata={'rest': 'http20Enabled'})
    http_logging_enabled: Optional[bool] = field(default=_UNSET, metadata={'rest': 'httpLoggingEnabled'})
    ip_security_restrictions: Optional[List[IpSecurityRestriction]] = field(default=_UNSET, metadata={'rest': 'ipSecurityRestrictions'})
    ip_security_restrictions_default_action: Optional[Literal['Allow', 'Deny']] = field(default=_UNSET, metadata={'rest': 'ipSecurityRestrictionsDefaultAction'})
    java_container: Optional[str] = field(default=_UNSET, metadata={'rest': 'javaContainer'})
    java_container_version: Optional[str] = field(default=_UNSET, metadata={'rest': 'javaContainerVersion'})
    java_version: Optional[str] = field(default=_UNSET, metadata={'rest': 'javaVersion'})
    keyvault_reference_identity: Optional[str] = field(default=_UNSET, metadata={'rest': 'keyVaultReferenceIdentity'})
    limits: Optional[SiteLimits] = field(default=_UNSET, metadata={'rest': 'limits'})
    linux_fx_version: Optional[str] = field(default=_UNSET, metadata={'rest': 'linuxFxVersion'})
    load_balancing: Optional[Literal['LeastRequests', 'LeastResponseTime', 'PerSiteRoundRobin', 'RequestHash', 'WeightedRoundRobin', 'WeightedTotalTraffic']] = field(default=_UNSET, metadata={'rest': 'loadBalancing'})
    local_mysql_enabled: Optional[bool] = field(default=_UNSET, metadata={'rest': 'localMySqlEnabled'})
    logs_directory_size_limit: Optional[int] = field(default=_UNSET, metadata={'rest': 'logsDirectorySizeLimit'})
    managed_pipeline_mode: Optional[Literal['Classic', 'Integrated']] = field(default=_UNSET, metadata={'rest': 'managedPipelineMode'})
    managed_service_identity_id: Optional[int] = field(default=_UNSET, metadata={'rest': 'managedServiceIdentityId'})
    metadata: Optional[List[NameValuePair]] = field(default=_UNSET, metadata={'rest': 'metadata'})
    minimum_elastic_instance_count: Optional[int] = field(default=_UNSET, metadata={'rest': 'minimumElasticInstanceCount'})
    min_tls_version: Optional[Literal['1.0', '1.1', '1.2']] = field(default=_UNSET, metadata={'rest': 'minTlsVersion'})
    net_framework_version: Optional[str] = field(default=_UNSET, metadata={'rest': 'netFrameworkVersion'})
    node_version: Optional[str] = field(default=_UNSET, metadata={'rest': 'nodeVersion'})
    number_of_workers: Optional[int] = field(default=_UNSET, metadata={'rest': 'numberOfWorkers'})
    php_version: Optional[str] = field(default=_UNSET, metadata={'rest': 'phpVersion'})
    powershell_version: Optional[str] = field(default=_UNSET, metadata={'rest': 'powerShellVersion'})
    pre_warmed_instance_count: Optional[int] = field(default=_UNSET, metadata={'rest': 'preWarmedInstanceCount'})
    public_network_access: Optional[str] = field(default=_UNSET, metadata={'rest': 'publicNetworkAccess'})
    publishing_username: Optional[str] = field(default=_UNSET, metadata={'rest': 'publishingUsername'})
    push: Optional[PushSettings] = field(default=_UNSET, metadata={'rest': 'push'})
    python_version: Optional[str] = field(default=_UNSET, metadata={'rest': 'pythonVersion'})
    remote_debugging_enabled: Optional[bool] = field(default=_UNSET, metadata={'rest': 'remoteDebuggingEnabled'})
    remote_debugging_version: Optional[str] = field(default=_UNSET, metadata={'rest': 'remoteDebuggingVersion'})
    request_tracing_enabled: Optional[bool] = field(default=_UNSET, metadata={'rest': 'requestTracingEnabled'})
    request_tracing_expiration_time: Optional[str] = field(default=_UNSET, metadata={'rest': 'requestTracingExpirationTime'})
    scm_ip_security_restrictions: Optional[List[IpSecurityRestriction]] = field(default=_UNSET, metadata={'rest': 'scmIpSecurityRestrictions'})
    scm_ip_security_restrictions_default_action: Optional[Literal['Allow', 'Deny']] = field(default=_UNSET, metadata={'rest': 'scmIpSecurityRestrictionsDefaultAction'})
    scm_ip_security_restrictions_use_main: Optional[bool] = field(default=_UNSET, metadata={'rest': 'scmIpSecurityRestrictionsUseMain'})
    scm_min_tls_version: Optional[Literal['1.0', '1.1', '1.2']] = field(default=_UNSET, metadata={'rest': 'scmMinTlsVersion'})
    scm_type: Optional[Literal['BitbucketGit', 'BitbucketHg', 'CodePlexGit', 'CodePlexHg', 'Dropbox', 'ExternalGit', 'ExternalHg', 'GitHub', 'LocalGit', 'None', 'OneDrive', 'Tfs', 'VSO', 'VSTSRM']] = field(default=_UNSET, metadata={'rest': 'scmType'})
    tracing_options: Optional[str] = field(default=_UNSET, metadata={'rest': 'tracingOptions'})
    use_32bit_worker_process: Optional[bool] = field(default=_UNSET, metadata={'rest': 'use32BitWorkerProcess'})
    virtual_applications: Optional[List[VirtualApplication]] = field(default=_UNSET, metadata={'rest': 'virtualApplications'})
    vnet_name: Optional[str] = field(default=_UNSET, metadata={'rest': 'vnetName'})
    vnet_private_ports_count: Optional[int] = field(default=_UNSET, metadata={'rest': 'vnetPrivatePortsCount'})
    vnet_route_all_enabled: Optional[bool] = field(default=_UNSET, metadata={'rest': 'vnetRouteAllEnabled'})
    website_timezone: Optional[str] = field(default=_UNSET, metadata={'rest': 'websiteTimeZone'})
    web_sockets_enabled: Optional[bool] = field(default=_UNSET, metadata={'rest': 'webSocketsEnabled'})
    windows_fx_version: Optional[str] = field(default=_UNSET, metadata={'rest': 'windowsFxVersion'})
    x_managed_service_identity_id: Optional[int] = field(default=_UNSET, metadata={'rest': 'xManagedServiceIdentityId'})


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
    managed_environment_id: Optional[ResourceId] = field(default=_UNSET, metadata={'rest': 'managedEnvironmentId'})
    public_network_access: Optional[Literal["Enabled", "Disabled", ""]] = field(default=_UNSET, metadata={'rest': 'publicNetworkAccess'})
    redundancy_mode: Optional[Literal['ActiveActive', 'Failover', 'GeoRedundant', 'Manual', 'None']] = field(default=_UNSET, metadata={'rest': 'redundancyMode'})
    reserved: Optional[bool] = field(default=_UNSET, metadata={'rest': 'reserved'})
    scm_site_also_stopped: Optional[bool] = field(default=_UNSET, metadata={'rest': 'scmSiteAlsoStopped'})
    server_farm_id: Optional[ResourceId] = field(default=_UNSET, metadata={'rest': 'serverFarmId'})
    site_config: Optional[SiteConfig] = field(default=_UNSET, metadata={'rest': 'siteConfig'})
    storage_account_required: Optional[bool] = field(default=_UNSET, metadata={'rest': 'storageAccountRequired'})
    virtual_network_subnet_id: Optional[ResourceId] = field(default=_UNSET, metadata={'rest': 'virtualNetworkSubnetId'})
    vnet_content_share_enabled: Optional[bool] = field(default=_UNSET, metadata={'rest': 'vnetContentShareEnabled'})
    vnet_image_pull_enabled: Optional[bool] = field(default=_UNSET, metadata={'rest': 'vnetImagePullEnabled'})
    vnet_route_all_enabled: Optional[bool] = field(default=_UNSET, metadata={'rest': 'vnetRouteAllEnabled'})

@dataclass_model
class AzureBlobStorageApplicationLogsConfig:
    level: Optional[Literal['Error', 'Information', 'Off', 'Verbose', 'Warning']] = field(default=_UNSET, metadata={'rest': 'level'})
    retention_in_days: Optional[int] = field(default=_UNSET, metadata={'rest': 'retentionInDays'})
    sas_url: str = field(metadata={'rest': 'sasUrl'})


@dataclass_model
class AzureTableStorageApplicationLogsConfig:
    level: Optional[Literal['Error', 'Information', 'Off', 'Verbose', 'Warning']] = field(default=_UNSET, metadata={'rest': 'level'})
    sas_url: str = field(metadata={'rest': 'sasUrl'})


@dataclass_model
class FileSystemApplicationLogsConfig:
    level: Optional[Literal['Error', 'Information', 'Off', 'Verbose', 'Warning']] = field(default=_UNSET, metadata={'rest': 'level'})


@dataclass_model
class ApplicationLogsConfig:
    azure_blob_storage: Optional[AzureBlobStorageApplicationLogsConfig] = field(default=_UNSET, metadata={'rest': 'azureBlobStorage'})
    azure_table_storage: Optional[AzureTableStorageApplicationLogsConfig] = field(default=_UNSET, metadata={'rest': 'azureTableStorage'})
    file_system: Optional[FileSystemApplicationLogsConfig] = field(default=_UNSET, metadata={'rest': 'fileSystem'})


@dataclass_model
class EnabledConfig:
    enabled: bool = field(metadata={'rest': 'enabled'})


@dataclass_model
class AzureBlobStorageHttpLogsConfig:
    enabled: Optional[bool] = field(default=_UNSET, metadata={'rest': 'enabled'})
    retention_in_days: Optional[int] = field(default=_UNSET, metadata={'rest': 'retentionInDays'})
    sas_url: Optional[str] = field(default=_UNSET, metadata={'rest': 'sasUrl'})


@dataclass_model
class FileSystemHttpLogsConfig:
    enabled: Optional[bool] = field(default=_UNSET, metadata={'rest': 'enabled'})
    retention_in_days: Optional[int] = field(default=_UNSET, metadata={'rest': 'retentionInDays'})
    retention_in_mb: Optional[int] = field(default=_UNSET, metadata={'rest': 'retentionInMb'})


@dataclass_model
class HttpLogsConfig:
    azure_blob_storage: Optional[AzureBlobStorageHttpLogsConfig] = field(default=_UNSET, metadata={'rest': 'azureBlobStorage'})
    file_system: Optional[FileSystemHttpLogsConfig] = field(default=_UNSET, metadata={'rest': 'fileSystem'})


@dataclass_model
class SiteLogsConfigProperties:
    application_logs: Optional[ApplicationLogsConfig] = field(default=_UNSET, metadata={'rest': 'applicationLogs'})
    detailed_error_messages: Optional[EnabledConfig] = field(default=_UNSET, metadata={'rest': 'detailedErrorMessages'})
    failed_requests_tracing: Optional[EnabledConfig] = field(default=_UNSET, metadata={'rest': 'failedRequestsTracing'})
    http_logs: Optional[HttpLogsConfig] = field(default=_UNSET, metadata={'rest': 'httpLogs'})


@dataclass_model
class AppServiceConfig(Resource):
    _resource: ClassVar[Literal['Microsoft.Web/sites/config']] = 'Microsoft.Web/sites/config'
    _version: ClassVar[str] = '2022-09-01'
    _symbolicname: str = field(default_factory=lambda: generate_symbol("siteconfig"), init=False, repr=False)
    kind: str = field(metadata={'rest': 'kind'})


@dataclass_model
class AppServiceAppSettingsConfig(AppServiceConfig):
    name: str = field(init=False, default="appsettings", metadata={'rest': 'name'})
    properties: Dict[str, Any] = field(default_factory=dict, metadata={'rest': 'properties'})


@dataclass_model
class AppServiceLogsConfig(AppServiceConfig):
    name: str = field(init=False, default="logs", metadata={'rest': 'name'})
    properties: Dict[str, Any] = field(default_factory=dict, metadata={'rest': 'properties'})


@dataclass_model
class AppServiceSite(LocatedResource):
    kind: str = field(metadata={'rest': 'kind'})
    extended_location : Optional[ExtendedLocation] = field(default=_UNSET, metadata={'rest': 'extendedLocation'})
    identity: Optional[ManagedServiceIdentity] = field(default=_UNSET, metadata={'rest': 'identity'})
    properties: Optional[SiteProperties] = field(default=_UNSET, metadata={'rest': 'properties'})
    configs: Optional[List[AppServiceConfig]] = field(default_factory=list, metadata={'rest': _SKIP})
    _resource: ClassVar[Literal['Microsoft.Web/sites']] = 'Microsoft.Web/sites'
    _version: ClassVar[str] = '2022-09-01'
    _symbolicname: str = field(default_factory=lambda: generate_symbol("site"), init=False, repr=False)

    def write(self, bicep: IO[str]) -> None:
        _serialize_resource(bicep, self)
        for config in self.configs:
            config._parent = self
            config.write(bicep)

@dataclass_model
class AppServicePlan(LocatedResource):
    sku: SkuDescription = field(metadata={'rest': 'sku'})
    kind: str = field(metadata={'rest': 'kind'})
    extended_location : Optional[ExtendedLocation] = field(default=_UNSET, metadata={'rest': 'extendedLocation'})
    properties: Optional[AppServicePlanProperties] = field(default=_UNSET, metadata={'rest': 'properties'})
    sites: Optional[List[AppServiceSite]] = field(default_factory=list, metadata={'rest': _SKIP})
    _resource: ClassVar[Literal['Microsoft.Web/serverfarms']] = 'Microsoft.Web/serverfarms'
    _version: ClassVar[str] = '2022-09-01'
    _symbolicname: str = field(default_factory=lambda: generate_symbol("serverfarm"), init=False, repr=False)

    def write(self, bicep: IO[str]) -> None:
        _serialize_resource(bicep, self)
        for site in self.sites:
            site._parent = self
            site.write(bicep)