# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import IO, Any, ClassVar, List, Optional, Dict, Literal, Required, TypedDict, Union
from dataclasses import field

from ._resource import (
    _SKIP,
    Output,
    _serialize_resource,
    Resource,
    ResourceId,
    LocatedResource,
    dataclass_model,
    generate_symbol,
    _UNSET,
    resolve_value,
)


class Capability(TypedDict, total=False):
    name: str
    reason: str
    value: str


class SkuCapacity(TypedDict, total=False):
    default: int
    elasticMaximum: int
    maximum: int
    minimum: int
    scaleType: str


class SkuDescription(TypedDict, total=False):
    name: Required[str]
    capabilities: List[Capability]
    capacity: int
    family: str
    locations: List[str]
    size: str
    skuCapacity: SkuCapacity
    tier: str


class ExtendedLocation(TypedDict, total=False):
    name: Required[str]


class KubeEnvironmentProfile(TypedDict, total=False):
    id: Required[str]


class HostingEnvironmentProfile(TypedDict, total=False):
    id: Required[str]


class AppServicePlanProperties(TypedDict, total=False):
    elasticScaleEnabled: bool
    freeOfferExpirationTime: str
    hostingEnvironmentProfile: HostingEnvironmentProfile
    hyperV: bool
    isSpot: bool
    isXenon: bool
    kubeEnvironmentProfile: KubeEnvironmentProfile
    maximumElasticWorkerCount: int
    perSiteScaling: bool
    reserved: bool
    spotExpirationTime: str
    targetWorkerCount: int
    targetWorkerSizeId: int
    workerTierName: str
    zoneRedundant: bool


class ManagedServiceIdentity(TypedDict, total=False):
    type: Required[Literal['None', 'SystemAssigned', 'SystemAssigned,UserAssigned','UserAssigned']]
    userAssignedIdentities: Dict[str, str]


class CloningInfo(TypedDict, total=False):
    sourceWebAppId: Required[str]
    appSettingsOverrides: Dict[str, str]
    cloneCustomHostNames: bool
    cloneSourceControl: bool
    configureLoadBalancing: bool
    correlationId: str
    hostingEnvironment: str
    overwrite: bool
    sourceWebAppLocation: str
    trafficManagerProfileId: str
    trafficManagerProfileName: str


class HostingEnvironmentProfile(TypedDict, total=False):
    id: Required[str]


class HostNameSslState(TypedDict, total=False):
    hostType: Literal['Repository', 'Standard']
    name: str
    sslState: Literal['Disabled', 'IpBasedEnabled', 'SniEnabled']
    thumbprint: str
    toUpdate: bool
    virtualIP: str


class NameValuePair(TypedDict, total=False):
    name: Required[str]
    value: Required[str]


class ApiDefinitionInfo(TypedDict, total=False):
    url: Required[str]


class ApiManagementConfig(TypedDict, total=False):
    id: Required[str]


class AutoHealCustomAction(TypedDict, total=False):
    exe: str
    parameters: str


class AutoHealActions(TypedDict, total=False):
    actionType: Literal['CustomAction', 'LogEvent', 'Recycle']
    customAction: AutoHealCustomAction
    minProcessExecutionTime: str


class RequestsBasedTrigger(TypedDict, total=False):
    count: int
    timeInterval: str


class SlowRequestsBasedTrigger(TypedDict, total=False):
    count: int
    path: str
    timeTaken: str
    timeInterval: str


class StatusCodesBasedTrigger(TypedDict, total=False):
    count: int
    path: str
    status: int
    subStatus: int
    timeInterval: str
    win32Status: int


class StatusCodesRangeBasedTrigger(TypedDict, total=False):
    count: int
    path: str
    statusCodes: str
    timeInterval: str


class AutoHealTriggers(TypedDict, total=False):
    privateBytesInKB: int
    requests: RequestsBasedTrigger
    slowRequests: SlowRequestsBasedTrigger
    slowRequestsWithPath: SlowRequestsBasedTrigger
    statusCodes: StatusCodesBasedTrigger
    statusCodesRange: StatusCodesRangeBasedTrigger


class AutoHealRules(TypedDict, total=False):
    actions: AutoHealActions
    triggers: AutoHealTriggers


class ConnStringInfo(TypedDict, total=False):
    connectionString: str
    name: str
    type: Literal['ApiHub', 'Custom', 'DocDb', 'EventHub', 'MySql', 'NotificationHub', 'PostgreSQL', 'RedisCache', 'SQLAzure', 'SQLServer', 'ServiceBus']


class CorsSettings(TypedDict, total=False):
    allowedOrigins: List[str]
    supportCredentials: bool


class RampUpRule(TypedDict, total=False):
    actionHostName: str
    changeDecisionCallbackUrl: str
    changeIntervalInMinutes: int
    changeStep: int
    maxReroutePercentage: int
    minReroutePercentage: int
    name: str
    reroutePercentage: int


class Experiments(TypedDict, total=False):
    rampUpRules: Required[List[RampUpRule]]


class HandlerMapping(TypedDict, total=False):
    arguments: str
    extension: str
    scriptProcessor: str


class IpSecurityRestriction(TypedDict, total=False):
    action: str
    description: str
    headers: Dict[str, str]
    ipAddress: str
    name: str
    priority: int
    subnetMask: str
    subnetTrafficTag: int
    tag: Literal['Default', 'ServiceTag', 'XffProxy']
    vnetSubnetResourceId: str
    vnetTrafficTag: int


class SiteLimits(TypedDict, total=False):
    maxDiskSizeInMb: int
    maxMemoryInMb: int
    maxPercentageCpu: int


class PushSettingsProperties(TypedDict, total=False):
    isPushEnabled: Required[bool]
    dynamicTagsJson: str
    tagsRequiringAuth: str
    tagWhitelistJson: str


class PushSettings(TypedDict, total=False):
    kind: Required[str]
    properties: PushSettingsProperties


class VirtualDirectory(TypedDict, total=False):
    physicalPath: str
    virtualPath: str


class VirtualApplication(TypedDict, total=False):
    physicalPath: str
    preloadEnabled: bool
    virtualDirectories: List[VirtualDirectory]
    virtualPath: str


class SiteConfig(TypedDict, total=False):
    acrUseManagedIdentityCreds: bool
    acrUserManagedIdentityID: str
    alwaysOn: bool
    apiDefinition: ApiDefinitionInfo
    apiManagementConfig: ApiManagementConfig
    appCommandLine: str
    appSettings: List[NameValuePair]
    autoHealEnabled: bool
    autoHealRules: AutoHealRules
    autoSwapSlotName: str
    azureStorageAccounts: Dict[str, str]
    connectionStrings: List[ConnStringInfo]
    cors: CorsSettings
    defaultDocuments: List[str]
    detailedErrorLoggingEnabled: bool
    documentRoot: str
    elasticWebAppScaleLimit: int
    experiments: Experiments
    ftpsState: Literal['AllAllowed', 'Disabled', 'FtpsOnly']
    functionAppScaleLimit: int
    functionsRuntimeScaleMonitoringEnabled: bool
    handlerMappings: List[HandlerMapping]
    healthCheckPath: str
    http20Enabled: bool
    httpLoggingEnabled: bool
    ipSecurityRestrictions: List[IpSecurityRestriction]
    ipSecurityRestrictionsDefaultAction: Literal['Allow', 'Deny']
    javaContainer: str
    javaContainerVersion: str
    javaVersion: str
    keyVaultReferenceIdentity: str
    limits: SiteLimits
    linuxFxVersion: str
    loadBalancing: Literal['LeastRequests', 'LeastResponseTime', 'PerSiteRoundRobin', 'RequestHash', 'WeightedRoundRobin', 'WeightedTotalTraffic']
    localMySqlEnabled: bool
    logsDirectorySizeLimit: int
    managedPipelineMode: Literal['Classic', 'Integrated']
    managedServiceIdentityId: int
    metadata: List[NameValuePair]
    minimumElasticInstanceCount: int
    minTlsVersion: Literal['1.0', '1.1', '1.2']
    netFrameworkVersion: str
    nodeVersion: str
    numberOfWorkers: int
    phpVersion: str
    powerShellVersion: str
    preWarmedInstanceCount: int
    publicNetworkAccess: str
    publishingUsername: str
    push: PushSettings
    pythonVersion: str
    remoteDebuggingEnabled: bool
    remoteDebuggingVersion: str
    requestTracingEnabled: bool
    requestTracingExpirationTime: str
    scmIpSecurityRestrictions: List[IpSecurityRestriction]
    scmIpSecurityRestrictionsDefaultAction: Literal['Allow', 'Deny']
    scmIpSecurityRestrictionsUseMain: bool
    scmMinTlsVersion: Literal['1.0', '1.1', '1.2']
    scmType: Literal['BitbucketGit', 'BitbucketHg', 'CodePlexGit', 'CodePlexHg', 'Dropbox', 'ExternalGit', 'ExternalHg', 'GitHub', 'LocalGit', 'None', 'OneDrive', 'Tfs', 'VSO', 'VSTSRM']
    tracingOptions: str
    use32BitWorkerProcess: bool
    virtualApplications: List[VirtualApplication]
    vnetName: str
    vnetPrivatePortsCount: int
    vnetRouteAllEnabled: bool
    websiteTimeZone: str
    webSocketsEnabled: bool
    windowsFxVersion: str
    xManagedServiceIdentityId: int


class SiteProperties(TypedDict, total=False):
    clientAffinityEnabled: bool
    clientCertEnabled: bool
    clientCertExclusionPaths: str
    clientCertMode: Literal["Required", "Optional", "OptionalInteractiveUser"]
    cloningInfo: CloningInfo
    customDomainVerificationId: str
    dailyMemoryTimeQuota: int
    enabled: bool
    hostingEnvironmentProfile: HostingEnvironmentProfile
    hostNamesDisabled: bool
    hostNameSslStates: List[HostNameSslState]
    httpsOnly: bool
    hyperV: bool
    isXenon: bool
    keyVaultReferenceIdentity: str
    managedEnvironmentId: str
    publicNetworkAccess: Literal["Enabled", "Disabled", ""]
    redundancyMode: Literal['ActiveActive', 'Failover', 'GeoRedundant', 'Manual', 'None']
    reserved: bool
    scmSiteAlsoStopped: bool
    serverFarmId: str
    siteConfig: SiteConfig
    storageAccountRequired: bool
    virtualNetworkSubnetId: str
    vnetContentShareEnabled: bool
    vnetImagePullEnabled: bool
    vnetRouteAllEnabled: bool


class AzureBlobStorageApplicationLogsConfig(TypedDict, total=False):
    level: Literal['Error', 'Information', 'Off', 'Verbose', 'Warning']
    retentionInDays: int
    sasUrl: Required[str]


class AzureTableStorageApplicationLogsConfig(TypedDict, total=False):
    level: Literal['Error', 'Information', 'Off', 'Verbose', 'Warning']
    sasUrl: Required[str]


class FileSystemApplicationLogsConfig(TypedDict, total=False):
    level: Required[Literal['Error', 'Information', 'Off', 'Verbose', 'Warning']]


class ApplicationLogsConfig(TypedDict, total=False):
    azureBlobStorage: AzureBlobStorageApplicationLogsConfig
    azureTableStorage: AzureTableStorageApplicationLogsConfig
    fileSystem: FileSystemApplicationLogsConfig


class EnabledConfig(TypedDict, total=False):
    enabled: Required[bool]


class AzureBlobStorageHttpLogsConfig(TypedDict, total=False):
    enabled: bool
    retentionInDays: int
    sasUrl: str


class FileSystemHttpLogsConfig(TypedDict, total=False):
    enabled: bool
    retentionInDays: int
    retentionInMb: int


class HttpLogsConfig(TypedDict, total=False):
    azureBlobStorage: AzureBlobStorageHttpLogsConfig
    fileSystem: FileSystemHttpLogsConfig


class SiteLogsConfigProperties(TypedDict, total=False):
    applicationLogs: ApplicationLogsConfig
    detailedErrorMessages: EnabledConfig
    failedRequestsTracing: EnabledConfig
    httpLogs: HttpLogsConfig


@dataclass_model
class AppServiceConfig(Resource):
    _resource: ClassVar[Literal['Microsoft.Web/sites/config']] = 'Microsoft.Web/sites/config'
    _version: ClassVar[str] = '2022-09-01'
    _symbolicname: str = field(default_factory=lambda: generate_symbol("siteconfig"), init=False, repr=False)
    kind: Optional[str] = field(default=_UNSET, metadata={'rest': 'kind'})


@dataclass_model
class AppServiceAppSettingsConfig(AppServiceConfig):
    name: str = field(init=False, default="appsettings", metadata={'rest': 'name'})
    properties: Dict[str, Any] = field(default_factory=dict, metadata={'rest': 'properties'})


@dataclass_model
class AppServiceLogsConfig(AppServiceConfig):
    name: str = field(init=False, default="logs", metadata={'rest': 'name'})
    properties: SiteLogsConfigProperties = field(metadata={'rest': 'properties'})


class PublishingCredentialsPoliciesProperties(TypedDict, total=False):
    allow: Required[bool]


@dataclass_model
class BasicPublishingCredentialsPolicy(Resource):
    _resource: ClassVar[Literal['Microsoft.Web/sites/basicPublishingCredentialsPolicies']] = 'Microsoft.Web/sites/basicPublishingCredentialsPolicies'
    _version: ClassVar[str] = '2022-09-01'
    _symbolicname: str = field(default_factory=lambda: generate_symbol("siteconfig"), init=False, repr=False)
    name: Literal['scm', 'ftp'] = field(metadata={'rest': 'name'})
    kind: Optional[str] = field(default=_UNSET, metadata={'rest': 'kind'})
    properties: PublishingCredentialsPoliciesProperties = field(metadata={'rest': 'properties'})


@dataclass_model
class AppServiceSite(LocatedResource):
    kind: str = field(metadata={'rest': 'kind'})
    extended_location : Optional[ExtendedLocation] = field(default=_UNSET, metadata={'rest': 'extendedLocation'})
    identity: Optional[ManagedServiceIdentity] = field(default=_UNSET, metadata={'rest': 'identity'})
    properties: Optional[SiteProperties] = field(default=_UNSET, metadata={'rest': 'properties'})
    configs: List[AppServiceConfig] = field(default_factory=list, metadata={'rest': _SKIP})
    policies: List[BasicPublishingCredentialsPolicy] = field(default_factory=list, metadata={'rest': _SKIP})
    _resource: ClassVar[Literal['Microsoft.Web/sites']] = 'Microsoft.Web/sites'
    _version: ClassVar[str] = '2022-09-01'
    _symbolicname: str = field(default_factory=lambda: generate_symbol("site"), init=False, repr=False)

    def write(self, bicep: IO[str]) -> Dict[str, str]:
        _serialize_resource(bicep, self)
        for policy in self.policies:
            policy._parent = self
            self._outputs.update(policy.write(bicep))
        for config in self.configs:
            config._parent = self
            self._outputs.update(config.write(bicep))

        output_prefix = "AppService"
        self._outputs[output_prefix + "Id"] = Output(f"{self._symbolicname}.id")
        # self._outputs[output_prefix + "PrincipalId"] = Output(f"{self._symbolicname}.identity.principalId")
        self._outputs[output_prefix + "Name"] = Output(f"{self._symbolicname}.name")
        self._outputs[output_prefix + "Url"] = f"https://${{{self._symbolicname}.properties.defaultHostName}}"
        for key, value in self._outputs.items():
            bicep.write(f"output {key} string = {resolve_value(value)}\n")
        bicep.write("\n")
        return self._outputs


@dataclass_model
class AppServicePlan(LocatedResource):
    sku: SkuDescription = field(metadata={'rest': 'sku'})
    kind: str = field(metadata={'rest': 'kind'})
    extended_location : Optional[ExtendedLocation] = field(default=_UNSET, metadata={'rest': 'extendedLocation'})
    properties: Optional[AppServicePlanProperties] = field(default=_UNSET, metadata={'rest': 'properties'})
    site: Optional[AppServiceSite] = field(default=None, metadata={'rest': _SKIP})
    _resource: ClassVar[Literal['Microsoft.Web/serverfarms']] = 'Microsoft.Web/serverfarms'
    _version: ClassVar[str] = '2022-09-01'
    _symbolicname: str = field(default_factory=lambda: generate_symbol("serverfarm"), init=False, repr=False)

    def write(self, bicep: IO[str]) -> Dict[str, str]:
        _serialize_resource(bicep, self)
        if self.site:
            self._outputs.update(self.site.write(bicep))
        return self._outputs
