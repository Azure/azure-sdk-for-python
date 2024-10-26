# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------

# pylint: disable=line-too-long

from functools import partial
from typing import IO, Any, ClassVar, List, Optional, Dict, Literal, TypedDict
from dataclasses import field, dataclass

from ._resource import (
    _SKIP,
    Output,
    _serialize_resource,
    Resource,
    LocatedResource,
    generate_symbol,
    _UNSET,
    resolve_value,
    BicepStr,
    BicepBool,
    BicepInt
)


class Capability(TypedDict, total=False):
    name: BicepStr
    reason: BicepStr
    value: BicepStr


class SkuCapacity(TypedDict, total=False):
    default: BicepInt
    elasticMaximum: BicepInt
    maximum: BicepInt
    minimum: BicepInt
    scaleType: BicepStr


class SkuDescription(TypedDict, total=False):
    # Required
    name: BicepStr
    capabilities: List[Capability]
    capacity: BicepInt
    family: BicepStr
    locations: List[BicepStr]
    size: BicepStr
    skuCapacity: SkuCapacity
    tier: BicepStr


class ExtendedLocation(TypedDict):
    # Required
    name: BicepStr


class KubeEnvironmentProfile(TypedDict):
    # Required
    id: BicepStr


class HostingEnvironmentProfile(TypedDict):
    # Required
    id: BicepStr


class AppServicePlanProperties(TypedDict, total=False):
    elasticScaleEnabled: BicepBool
    freeOfferExpirationTime: BicepStr
    hostingEnvironmentProfile: HostingEnvironmentProfile
    hyperV: BicepBool
    isSpot: BicepBool
    isXenon: BicepBool
    kubeEnvironmentProfile: KubeEnvironmentProfile
    maximumElasticWorkerCount: BicepInt
    perSiteScaling: BicepBool
    reserved: BicepBool
    spotExpirationTime: BicepStr
    targetWorkerCount: BicepInt
    targetWorkerSizeId: BicepInt
    workerTierName: BicepStr
    zoneRedundant: BicepBool


class ManagedServiceIdentity(TypedDict, total=False):
    # Required
    type: Literal['None', 'SystemAssigned', 'SystemAssigned,UserAssigned','UserAssigned']
    userAssignedIdentities: Dict[BicepStr, BicepStr]


class CloningInfo(TypedDict, total=False):
    # Required
    sourceWebAppId: BicepStr
    appSettingsOverrides: Dict[BicepStr, BicepStr]
    cloneCustomHostNames: BicepBool
    cloneSourceControl: BicepBool
    configureLoadBalancing: BicepBool
    correlationId: BicepStr
    hostingEnvironment: BicepStr
    overwrite: BicepBool
    sourceWebAppLocation: BicepStr
    trafficManagerProfileId: BicepStr
    trafficManagerProfileName: BicepStr


class HostNameSslState(TypedDict, total=False):
    hostType: Literal['Repository', 'Standard']
    name: BicepStr
    sslState: Literal['Disabled', 'IpBasedEnabled', 'SniEnabled']
    thumbprint: BicepStr
    toUpdate: BicepBool
    virtualIP: BicepStr


class NameValuePair(TypedDict):
    # Required
    name: BicepStr
    # Required
    value: BicepStr


class ApiDefinitionInfo(TypedDict):
    # Required
    url: BicepStr


class ApiManagementConfig(TypedDict):
    # Required
    id: BicepStr


class AutoHealCustomAction(TypedDict, total=False):
    exe: BicepStr
    parameters: BicepStr


class AutoHealActions(TypedDict, total=False):
    actionType: Literal['CustomAction', 'LogEvent', 'Recycle']
    customAction: AutoHealCustomAction
    minProcessExecutionTime: BicepStr


class RequestsBasedTrigger(TypedDict, total=False):
    count: BicepInt
    timeInterval: BicepStr


class SlowRequestsBasedTrigger(TypedDict, total=False):
    count: BicepInt
    path: BicepStr
    timeTaken: BicepStr
    timeInterval: BicepStr


class StatusCodesBasedTrigger(TypedDict, total=False):
    count: BicepInt
    path: BicepStr
    status: BicepInt
    subStatus: BicepInt
    timeInterval: BicepStr
    win32Status: BicepInt


class StatusCodesRangeBasedTrigger(TypedDict, total=False):
    count: BicepInt
    path: BicepStr
    statusCodes: BicepStr
    timeInterval: BicepStr


class AutoHealTriggers(TypedDict, total=False):
    privateBytesInKB: BicepInt
    requests: RequestsBasedTrigger
    slowRequests: SlowRequestsBasedTrigger
    slowRequestsWithPath: SlowRequestsBasedTrigger
    statusCodes: StatusCodesBasedTrigger
    statusCodesRange: StatusCodesRangeBasedTrigger


class AutoHealRules(TypedDict, total=False):
    actions: AutoHealActions
    triggers: AutoHealTriggers


class ConnStringInfo(TypedDict, total=False):
    connectionString: BicepStr
    name: BicepStr
    type: Literal['ApiHub', 'Custom', 'DocDb', 'EventHub', 'MySql', 'NotificationHub', 'PostgreSQL', 'RedisCache', 'SQLAzure', 'SQLServer', 'ServiceBus']


class CorsSettings(TypedDict, total=False):
    allowedOrigins: List[BicepStr]
    supportCredentials: BicepBool


class RampUpRule(TypedDict, total=False):
    actionHostName: BicepStr
    changeDecisionCallbackUrl: BicepStr
    changeIntervalInMinutes: BicepInt
    changeStep: BicepInt
    maxReroutePercentage: BicepInt
    minReroutePercentage: BicepInt
    name: BicepStr
    reroutePercentage: BicepInt


class Experiments(TypedDict):
    # Required
    rampUpRules: List[RampUpRule]


class HandlerMapping(TypedDict, total=False):
    arguments: BicepStr
    extension: BicepStr
    scriptProcessor: BicepStr


class IpSecurityRestriction(TypedDict, total=False):
    action: BicepStr
    description: BicepStr
    headers: Dict[str, str]
    ipAddress: BicepStr
    name: BicepStr
    priority: BicepInt
    subnetMask: BicepStr
    subnetTrafficTag: BicepInt
    tag: Literal['Default', 'ServiceTag', 'XffProxy']
    vnetSubnetResourceId: BicepStr
    vnetTrafficTag: BicepInt


class SiteLimits(TypedDict, total=False):
    maxDiskSizeInMb: BicepInt
    maxMemoryInMb: BicepInt
    maxPercentageCpu: BicepInt


class PushSettingsProperties(TypedDict, total=False):
    # Required
    isPushEnabled: BicepBool
    dynamicTagsJson: BicepStr
    tagsRequiringAuth: BicepStr
    tagWhitelistJson: BicepStr


class PushSettings(TypedDict, total=False):
    # Required
    kind: BicepStr
    properties: PushSettingsProperties


class VirtualDirectory(TypedDict, total=False):
    physicalPath: BicepStr
    virtualPath: BicepStr


class VirtualApplication(TypedDict, total=False):
    physicalPath: BicepStr
    preloadEnabled: BicepBool
    virtualDirectories: List[VirtualDirectory]
    virtualPath: BicepStr


class SiteConfig(TypedDict, total=False):
    acrUseManagedIdentityCreds: BicepBool
    acrUserManagedIdentityID: BicepStr
    alwaysOn: BicepBool
    apiDefinition: ApiDefinitionInfo
    apiManagementConfig: ApiManagementConfig
    appCommandLine: BicepStr
    appSettings: List[NameValuePair]
    autoHealEnabled: BicepBool
    autoHealRules: AutoHealRules
    autoSwapSlotName: BicepStr
    azureStorageAccounts: Dict[BicepStr, BicepStr]
    connectionStrings: List[ConnStringInfo]
    cors: CorsSettings
    defaultDocuments: List[BicepStr]
    detailedErrorLoggingEnabled: BicepBool
    documentRoot: BicepStr
    elasticWebAppScaleLimit: BicepInt
    experiments: Experiments
    ftpsState: Literal['AllAllowed', 'Disabled', 'FtpsOnly']
    functionAppScaleLimit: BicepInt
    functionsRuntimeScaleMonitoringEnabled: BicepBool
    handlerMappings: List[HandlerMapping]
    healthCheckPath: BicepStr
    http20Enabled: BicepBool
    httpLoggingEnabled: BicepBool
    ipSecurityRestrictions: List[IpSecurityRestriction]
    ipSecurityRestrictionsDefaultAction: Literal['Allow', 'Deny']
    javaContainer: BicepStr
    javaContainerVersion: BicepStr
    javaVersion: BicepStr
    keyVaultReferenceIdentity: BicepStr
    limits: SiteLimits
    linuxFxVersion: BicepStr
    loadBalancing: Literal['LeastRequests', 'LeastResponseTime', 'PerSiteRoundRobin', 'RequestHash', 'WeightedRoundRobin', 'WeightedTotalTraffic']
    localMySqlEnabled: BicepBool
    logsDirectorySizeLimit: BicepInt
    managedPipelineMode: Literal['Classic', 'Integrated']
    managedServiceIdentityId: BicepInt
    metadata: List[NameValuePair]
    minimumElasticInstanceCount: BicepInt
    minTlsVersion: Literal['1.0', '1.1', '1.2']
    netFrameworkVersion: BicepStr
    nodeVersion: BicepStr
    numberOfWorkers: BicepInt
    phpVersion: BicepStr
    powerShellVersion: BicepStr
    preWarmedInstanceCount: BicepInt
    publicNetworkAccess: BicepStr
    publishingUsername: BicepStr
    push: PushSettings
    pythonVersion: BicepStr
    remoteDebuggingEnabled: BicepBool
    remoteDebuggingVersion: BicepStr
    requestTracingEnabled: BicepBool
    requestTracingExpirationTime: BicepStr
    scmIpSecurityRestrictions: List[IpSecurityRestriction]
    scmIpSecurityRestrictionsDefaultAction: Literal['Allow', 'Deny']
    scmIpSecurityRestrictionsUseMain: BicepBool
    scmMinTlsVersion: Literal['1.0', '1.1', '1.2']
    scmType: Literal['BitbucketGit', 'BitbucketHg', 'CodePlexGit', 'CodePlexHg', 'Dropbox', 'ExternalGit', 'ExternalHg', 'GitHub', 'LocalGit', 'None', 'OneDrive', 'Tfs', 'VSO', 'VSTSRM']
    tracingOptions: BicepStr
    use32BitWorkerProcess: BicepBool
    virtualApplications: List[VirtualApplication]
    vnetName: BicepStr
    vnetPrivatePortsCount: BicepInt
    vnetRouteAllEnabled: BicepBool
    websiteTimeZone: BicepStr
    webSocketsEnabled: BicepBool
    windowsFxVersion: BicepStr
    xManagedServiceIdentityId: BicepInt


class SiteProperties(TypedDict, total=False):
    clientAffinityEnabled: BicepBool
    clientCertEnabled: BicepBool
    clientCertExclusionPaths: BicepStr
    clientCertMode: Literal["Required", "Optional", "OptionalInteractiveUser"]
    cloningInfo: CloningInfo
    customDomainVerificationId: BicepStr
    dailyMemoryTimeQuota: BicepInt
    enabled: BicepBool
    hostingEnvironmentProfile: HostingEnvironmentProfile
    hostNamesDisabled: BicepBool
    hostNameSslStates: List[HostNameSslState]
    httpsOnly: BicepBool
    hyperV: BicepBool
    isXenon: BicepBool
    keyVaultReferenceIdentity: BicepStr
    managedEnvironmentId: BicepStr
    publicNetworkAccess: Literal["Enabled", "Disabled", ""]
    redundancyMode: Literal['ActiveActive', 'Failover', 'GeoRedundant', 'Manual', 'None']
    reserved: BicepBool
    scmSiteAlsoStopped: BicepBool
    serverFarmId: BicepStr
    siteConfig: SiteConfig
    storageAccountRequired: BicepBool
    virtualNetworkSubnetId: BicepStr
    vnetContentShareEnabled: BicepBool
    vnetImagePullEnabled: BicepBool
    vnetRouteAllEnabled: BicepBool


class AzureBlobStorageApplicationLogsConfig(TypedDict, total=False):
    level: Literal['Error', 'Information', 'Off', 'Verbose', 'Warning']
    retentionInDays: BicepInt
    # Required
    sasUrl: BicepStr


class AzureTableStorageApplicationLogsConfig(TypedDict, total=False):
    level: Literal['Error', 'Information', 'Off', 'Verbose', 'Warning']
    # Required
    sasUrl: BicepStr


class FileSystemApplicationLogsConfig(TypedDict):
    # Required
    level: Literal['Error', 'Information', 'Off', 'Verbose', 'Warning']


class ApplicationLogsConfig(TypedDict, total=False):
    azureBlobStorage: AzureBlobStorageApplicationLogsConfig
    azureTableStorage: AzureTableStorageApplicationLogsConfig
    fileSystem: FileSystemApplicationLogsConfig


class EnabledConfig(TypedDict):
    # Required
    enabled: BicepBool


class AzureBlobStorageHttpLogsConfig(TypedDict, total=False):
    enabled: BicepBool
    retentionInDays: BicepInt
    sasUrl: BicepStr


class FileSystemHttpLogsConfig(TypedDict, total=False):
    enabled: BicepBool
    retentionInDays: BicepInt
    retentionInMb: BicepInt


class HttpLogsConfig(TypedDict, total=False):
    azureBlobStorage: AzureBlobStorageHttpLogsConfig
    fileSystem: FileSystemHttpLogsConfig


class SiteLogsConfigProperties(TypedDict, total=False):
    applicationLogs: ApplicationLogsConfig
    detailedErrorMessages: EnabledConfig
    failedRequestsTracing: EnabledConfig
    httpLogs: HttpLogsConfig


@dataclass(kw_only=True)
class AppServiceConfig(Resource):
    _resource: ClassVar[Literal['Microsoft.Web/sites/config']] = 'Microsoft.Web/sites/config'
    _version: ClassVar[str] = '2022-09-01'
    _symbolicname: str = field(default_factory=partial(generate_symbol, "siteconfig"), init=False, repr=False)
    kind: Optional[BicepStr] = field(default=_UNSET, metadata={'rest': 'kind'})


@dataclass(kw_only=True)
class AppServiceAppSettingsConfig(AppServiceConfig):
    name: str = field(init=False, default="appsettings", metadata={'rest': 'name'})
    properties: Dict[str, Any] = field(default_factory=dict, metadata={'rest': 'properties'})


@dataclass(kw_only=True)
class AppServiceLogsConfig(AppServiceConfig):
    name: str = field(init=False, default="logs", metadata={'rest': 'name'})
    properties: SiteLogsConfigProperties = field(metadata={'rest': 'properties'})


class PublishingCredentialsPoliciesProperties(TypedDict):
    # Required
    allow: BicepBool


@dataclass(kw_only=True)
class BasicPublishingCredentialsPolicy(Resource):
    _resource: ClassVar[Literal['Microsoft.Web/sites/basicPublishingCredentialsPolicies']] = 'Microsoft.Web/sites/basicPublishingCredentialsPolicies'
    _version: ClassVar[str] = '2022-09-01'
    _symbolicname: str = field(default_factory=partial(generate_symbol, "siteconfig"), init=False, repr=False)
    name: Literal['scm', 'ftp'] = field(metadata={'rest': 'name'})
    kind: Optional[BicepStr] = field(default=_UNSET, metadata={'rest': 'kind'})
    properties: PublishingCredentialsPoliciesProperties = field(metadata={'rest': 'properties'})


@dataclass(kw_only=True)
class AppServiceSite(LocatedResource):
    kind: BicepStr = field(metadata={'rest': 'kind'})
    extended_location : Optional[ExtendedLocation] = field(default=_UNSET, metadata={'rest': 'extendedLocation'})
    identity: Optional[ManagedServiceIdentity] = field(default=_UNSET, metadata={'rest': 'identity'})
    properties: Optional[SiteProperties] = field(default=_UNSET, metadata={'rest': 'properties'})
    configs: List[AppServiceConfig] = field(default_factory=list, metadata={'rest': _SKIP})
    policies: List[BasicPublishingCredentialsPolicy] = field(default_factory=list, metadata={'rest': _SKIP})
    _resource: ClassVar[Literal['Microsoft.Web/sites']] = 'Microsoft.Web/sites'
    _version: ClassVar[str] = '2022-09-01'
    _symbolicname: str = field(default_factory=partial(generate_symbol, "site"), init=False, repr=False)

    def write(self, bicep: IO[str]) -> Dict[str, str]:
        _serialize_resource(bicep, self)
        for policy in self.policies:
            policy.parent = self
            self._outputs.update(policy.write(bicep))
        for config in self.configs:
            config.parent = self
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


@dataclass(kw_only=True)
class AppServicePlan(LocatedResource):
    sku: SkuDescription = field(metadata={'rest': 'sku'})
    kind: BicepStr = field(metadata={'rest': 'kind'})
    extended_location : Optional[ExtendedLocation] = field(default=_UNSET, metadata={'rest': 'extendedLocation'})
    properties: Optional[AppServicePlanProperties] = field(default=_UNSET, metadata={'rest': 'properties'})
    site: Optional[AppServiceSite] = field(default=None, metadata={'rest': _SKIP})
    _resource: ClassVar[Literal['Microsoft.Web/serverfarms']] = 'Microsoft.Web/serverfarms'
    _version: ClassVar[str] = '2022-09-01'
    _symbolicname: str = field(default_factory=partial(generate_symbol, "serverfarm"), init=False, repr=False)

    def write(self, bicep: IO[str]) -> Dict[str, str]:
        _serialize_resource(bicep, self)
        if self.site:
            self._outputs.update(self.site.write(bicep))
        return self._outputs
