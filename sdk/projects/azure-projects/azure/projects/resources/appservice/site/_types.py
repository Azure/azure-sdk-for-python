# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=line-too-long, name-too-long

from __future__ import annotations
from typing import Literal, TypedDict, Union

from ...._bicep.expressions import Parameter
from ..._extension import Identity


VERSION = "2024-04-01"


class AppSiteApiDefinitionInfo(TypedDict, total=False):
    url: Union[str, Parameter]
    """The URL of the API definition."""


class AppSiteApiManagementConfig(TypedDict, total=False):
    id: Union[str, Parameter]
    """APIM-Api Identifier."""


class AppSiteAutoHealActions(TypedDict, total=False):
    actionType: Union[Literal["Recycle", "LogEvent", "CustomAction"], Parameter]
    """Predefined action to be taken."""
    customAction: Union[AppSiteAutoHealCustomAction, Parameter]
    """Custom action to be taken."""
    minProcessExecutionTime: Union[str, Parameter]
    """Minimum time the process must executebefore taking the action"""


class AppSiteAutoHealCustomAction(TypedDict, total=False):
    exe: Union[str, Parameter]
    """Executable to be run."""
    parameters: Union[str, Parameter]
    """Parameters for the executable."""


class AppSiteAutoHealRules(TypedDict, total=False):
    actions: Union[AppSiteAutoHealActions, Parameter]
    """Actions to be executed when a rule is triggered."""
    triggers: Union[AppSiteAutoHealTriggers, Parameter]
    """Conditions that describe when to execute the auto-heal actions."""


class AppSiteAutoHealTriggers(TypedDict, total=False):
    privateBytesInKB: Union[int, Parameter]
    """A rule based on private bytes."""
    requests: Union[AppSiteRequestsBasedTrigger, Parameter]
    """A rule based on total requests."""
    slowRequests: Union[AppSiteRequestsBasedTrigger, Parameter]
    """A rule based on request execution time."""
    slowRequestsWithPath: Union[list[AppSiteRequestsBasedTrigger], Parameter]
    """A rule based on multiple Slow Requests Rule with path"""
    statusCodes: Union[list[AppSiteStatusCodesBasedTrigger], Parameter]
    """A rule based on status codes."""
    statusCodesRange: Union[list[AppSiteStatusCodesRangeBasedTrigger], Parameter]
    """A rule based on status codes ranges."""


class AppSiteAzureStorageInfoValue(TypedDict, total=False):
    accessKey: Union[str, Parameter]
    """Access key for the storage account."""
    accountName: Union[str, Parameter]
    """Name of the storage account."""
    mountPath: Union[str, Parameter]
    """Path to mount the storage within the site's runtime environment."""
    protocol: Union[Literal["Smb", "Nfs", "Http"], Parameter]
    """Mounting protocol to use for the storage account."""
    shareName: Union[str, Parameter]
    """Name of the file share (container name, for Blob storage)."""
    type: Union[Literal["AzureBlob", "AzureFiles"], Parameter]
    """Type of storage."""


class AppSiteCloningInfo(TypedDict, total=False):
    appSettingsOverrides: Union[AppSiteCloningInfo, Parameter]
    """Application setting overrides for cloned app. If specified, these settings override the settings cloned from source app. Otherwise, application settings from source app are retained."""
    cloneCustomHostNames: Union[bool, Parameter]
    """<code>true</code> to clone custom hostnames from source app; otherwise, <code>false</code>."""
    cloneSourceControl: Union[bool, Parameter]
    """<code>true</code> to clone source control from source app; otherwise, <code>false</code>."""
    configureLoadBalancing: Union[bool, Parameter]
    """<code>true</code> to configure load balancing for source and destination app."""
    correlationId: Union[str, Parameter]
    """Correlation ID of cloning operation. This ID ties multiple cloning operationstogether to use the same snapshot."""
    hostingEnvironment: Union[str, Parameter]
    """App Service Environment."""
    overwrite: Union[bool, Parameter]
    """<code>true</code> to overwrite destination app; otherwise, <code>false</code>."""
    sourceWebAppId: Union[str, Parameter]
    """ARM resource ID of the source app. App resource ID is of the form /subscriptions/{subId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Web/sites/{siteName} for production slots and /subscriptions/{subId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Web/sites/{siteName}/slots/{slotName} for other slots."""
    sourceWebAppLocation: Union[str, Parameter]
    """Location of source app ex: West US or North Europe"""
    trafficManagerProfileId: Union[str, Parameter]
    """ARM resource ID of the Traffic Manager profile to use, if it exists. Traffic Manager resource ID is of the form /subscriptions/{subId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Network/trafficManagerProfiles/{profileName}."""
    trafficManagerProfileName: Union[str, Parameter]
    """Name of Traffic Manager profile to create. This is only needed if Traffic Manager profile does not already exist."""


class AppSiteConnStringInfo(TypedDict, total=False):
    connectionString: Union[str, Parameter]
    """Connection string value."""
    name: Union[str, Parameter]
    """Name of connection string."""
    type: Union[
        Literal[
            "RedisCache",
            "SQLAzure",
            "Custom",
            "MySql",
            "PostgreSQL",
            "DocDb",
            "EventHub",
            "SQLServer",
            "ApiHub",
            "ServiceBus",
            "NotificationHub",
        ],
        Parameter,
    ]
    """Type of database."""


class AppSiteCorsSettings(TypedDict, total=False):
    allowedOrigins: Union[list[Union[str, Parameter]], Parameter]
    """Gets or sets the list of origins that should be allowed to make cross-origincalls (for example: http://example.com:12345). Use \"*\" to allow all."""
    supportCredentials: Union[bool, Parameter]
    """Gets or sets whether CORS requests with credentials are allowed. See https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS#Requests_with_credentialsfor more details."""


class AppSiteDaprConfig(TypedDict, total=False):
    appId: Union[str, Parameter]
    """Dapr application identifier"""
    appPort: Union[int, Parameter]
    """Tells Dapr which port your application is listening on"""
    enableApiLogging: Union[bool, Parameter]
    """Enables API logging for the Dapr sidecar"""
    enabled: Union[bool, Parameter]
    """Boolean indicating if the Dapr side car is enabled"""
    httpMaxRequestSize: Union[int, Parameter]
    """Increasing max size of request body http servers parameter in MB to handle uploading of big files. Default is 4 MB."""
    httpReadBufferSize: Union[int, Parameter]
    """Dapr max size of http header read buffer in KB to handle when sending multi-KB headers. Default is 65KB."""
    logLevel: Union[Literal["debug", "info", "warn", "error"], Parameter]
    """Sets the log level for the Dapr sidecar. Allowed values are debug, info, warn, error. Default is info."""


class AppSiteExperiments(TypedDict, total=False):
    rampUpRules: Union[list[AppSiteRampUpRule], Parameter]
    """List of ramp-up rules."""


class AppSiteExtendedLocation(TypedDict, total=False):
    name: Union[str, Parameter]
    """Name of extended location."""


class AppSiteFunctionAppConfig(TypedDict, total=False):
    deployment: Union[AppSiteFunctionsDeployment, Parameter]
    """Function app deployment configuration."""
    runtime: Union[AppSiteFunctionsRuntime, Parameter]
    """Function app runtime settings."""
    scaleAndConcurrency: Union[AppSiteFunctionsScaleAndConcurrency, Parameter]
    """Function app scale and concurrency settings."""


class AppSiteFunctionsAlwaysReadyConfig(TypedDict, total=False):
    instanceCount: Union[int, Parameter]
    """Sets the number of 'Always Ready' instances for a given function group or a specific function. For additional information see https://aka.ms/flexconsumption/alwaysready."""
    name: Union[str, Parameter]
    """Either a function group or a function name is required. For additional information see https://aka.ms/flexconsumption/alwaysready."""


class AppSiteFunctionsDeployment(TypedDict, total=False):
    storage: Union[AppSiteFunctionsDeployment, Parameter]
    """Storage for deployed package used by the function app."""


class AppSiteFunctionsDeploymentStorage(TypedDict, total=False):
    authentication: Union[AppSiteFunctionsDeployment, Parameter]
    """Authentication method to access the storage account for deployment."""
    type: Union[Literal["blobContainer"], Parameter]
    """Property to select Azure Storage type. Available options: blobContainer."""
    value: Union[str, Parameter]
    """Property to set the URL for the selected Azure Storage type. Example: For blobContainer, the value could be https://<storageAccountName>.blob.core.windows.net/<containerName>."""


class AppSiteFunctionsDeploymentStorageAuthentication(TypedDict, total=False):
    storageAccountConnectionStringName: Union[str, Parameter]
    """Use this property for StorageAccountConnectionString. Set the name of the app setting that has the storage account connection string. Do not set a value for this property when using other authentication type."""
    type: Union[Literal["StorageAccountConnectionString", "SystemAssignedIdentity", "UserAssignedIdentity"], Parameter]
    """Property to select authentication type to access the selected storage account. Available options: SystemAssignedIdentity, UserAssignedIdentity, StorageAccountConnectionString."""
    userAssignedIdentityResourceId: Union[str, Parameter]
    """Use this property for UserAssignedIdentity. Set the resource ID of the identity. Do not set a value for this property when using other authentication type."""


class AppSiteFunctionsRuntime(TypedDict, total=False):
    name: Union[Literal["powershell", "dotnet-isolated", "node", "java", "custom", "python"], Parameter]
    """Function app runtime name. Available options: dotnet-isolated, node, java, powershell, python, custom"""
    version: Union[str, Parameter]
    """Function app runtime version. Example: 8 (for dotnet-isolated)"""


class AppSiteFunctionsScaleAndConcurrency(TypedDict, total=False):
    alwaysReady: Union[list[AppSiteFunctionsAlwaysReadyConfig], Parameter]
    """'Always Ready' configuration for the function app."""
    instanceMemoryMB: Union[int, Parameter]
    """Set the amount of memory allocated to each instance of the function app in MB. CPU and network bandwidth are allocated proportionally."""
    maximumInstanceCount: Union[int, Parameter]
    """The maximum number of instances for the function app."""
    triggers: Union[AppSiteFunctionsScaleAndConcurrency, Parameter]
    """Scale and concurrency settings for the function app triggers."""


class AppSiteFunctionsScaleAndConcurrencyTriggers(TypedDict, total=False):
    http: Union[AppSiteFunctionsScaleAndConcurrency, Parameter]
    """Scale and concurrency settings for the HTTP trigger."""


class AppSiteFunctionsScaleAndConcurrencyTriggersHttp(TypedDict, total=False):
    perInstanceConcurrency: Union[int, Parameter]
    """The maximum number of concurrent HTTP trigger invocations per instance."""


class AppSiteHandlerMapping(TypedDict, total=False):
    arguments: Union[str, Parameter]
    """Command-line arguments to be passed to the script processor."""
    extension: Union[str, Parameter]
    """Requests with this extension will be handled using the specified FastCGI application."""
    scriptProcessor: Union[str, Parameter]
    """The absolute path to the FastCGI application."""


class AppSiteHostingEnvironmentProfile(TypedDict, total=False):
    id: Union[str, Parameter]
    """Resource ID of the App Service Environment."""


class AppSiteHostNameSslState(TypedDict, total=False):
    hostType: Union[Literal["Repository", "Standard"], Parameter]
    """Indicates whether the hostname is a standard or repository hostname."""
    name: Union[str, Parameter]
    """Hostname."""
    sslState: Union[Literal["SniEnabled", "Disabled", "IpBasedEnabled"], Parameter]
    """SSL type."""
    thumbprint: Union[str, Parameter]
    """SSL certificate thumbprint."""
    toUpdate: Union[bool, Parameter]
    """Set to <code>true</code> to update existing hostname."""
    virtualIP: Union[str, Parameter]
    """Virtual IP address assigned to the hostname if IP based SSL is enabled."""


class AppSiteIpSecurityRestriction(TypedDict, total=False):
    action: Union[str, Parameter]
    """Allow or Deny access for this IP range."""
    description: Union[str, Parameter]
    """IP restriction rule description."""
    headers: Union[AppSiteIpSecurityRestriction, Parameter]
    """IP restriction rule headers.X-Forwarded-Host (https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-Host#Examples). The matching logic is ..- If the property is null or empty (default), all hosts(or lack of) are allowed.- A value is compared using ordinal-ignore-case (excluding port number).- Subdomain wildcards are permitted but don't match the root domain. For example, *.contoso.com matches the subdomain foo.contoso.com but not the root domain contoso.com or multi-level foo.bar.contoso.com- Unicode host names are allowed but are converted to Punycode for matching.X-Forwarded-For (https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-For#Examples).The matching logic is ..- If the property is null or empty (default), any forwarded-for chains (or lack of) are allowed.- If any address (excluding port number) in the chain (comma separated) matches the CIDR defined by the property.X-Azure-FDID and X-FD-HealthProbe.The matching logic is exact match."""
    ipAddress: Union[str, Parameter]
    """IP address the security restriction is valid for.It can be in form of pure ipv4 address (required SubnetMask property) orCIDR notation such as ipv4/mask (leading bit match). For CIDR,SubnetMask property must not be specified."""
    name: Union[str, Parameter]
    """IP restriction rule name."""
    priority: Union[int, Parameter]
    """Priority of IP restriction rule."""
    subnetMask: Union[str, Parameter]
    """Subnet mask for the range of IP addresses the restriction is valid for."""
    subnetTrafficTag: Union[int, Parameter]
    """(internal) Subnet traffic tag"""
    tag: Union[Literal["XffProxy", "ServiceTag", "Default"], Parameter]
    """Defines what this IP filter will be used for. This is to support IP filtering on proxies."""
    vnetSubnetResourceId: Union[str, Parameter]
    """Virtual network resource id"""
    vnetTrafficTag: Union[int, Parameter]
    """(internal) Vnet traffic tag"""


class AppSiteResource(TypedDict, total=False):
    extendedLocation: Union[AppSiteExtendedLocation, Parameter]
    """Extended Location."""
    identity: Union[Identity, Parameter]
    """Managed service identity."""
    kind: Union[str, Parameter]
    """Kind of resource. If the resource is an app, you can refer to https://github.com/Azure/app-service-linux-docs/blob/master/Things_You_Should_Know/kind_property.md#app-service-resource-kind-reference for details supported values for kind."""
    location: Union[str, Parameter]
    """Resource Location."""
    name: Union[str, Parameter]
    """The resource name"""
    properties: AppSiteProperties
    """Site resource specific properties"""
    tags: dict[str, Union[None, str, Parameter]]
    """Resource tags"""


class AppSiteNameValuePair(TypedDict, total=False):
    name: Union[str, Parameter]
    """Pair name."""
    value: Union[str, Parameter]
    """Pair value."""


class AppSitePushSettings(TypedDict, total=False):
    kind: Union[str, Parameter]
    """Kind of resource."""
    properties: Union[AppSitePushSettings, Parameter]
    """PushSettings resource specific properties"""


class AppSitePushSettingsProperties(TypedDict, total=False):
    dynamicTagsJson: Union[str, Parameter]
    """Gets or sets a JSON string containing a list of dynamic tags that will be evaluated from user claims in the push registration endpoint."""
    isPushEnabled: Union[bool, Parameter]
    """Gets or sets a flag indicating whether the Push endpoint is enabled."""
    tagsRequiringAuth: Union[str, Parameter]
    """Gets or sets a JSON string containing a list of tags that require user authentication to be used in the push registration endpoint.Tags can consist of alphanumeric characters and the following:'_', '@', '#', '.', ':', '-'. Validation should be performed at the PushRequestHandler."""
    tagWhitelistJson: Union[str, Parameter]
    """Gets or sets a JSON string containing a list of tags that are whitelisted for use by the push registration endpoint."""


class AppSiteRampUpRule(TypedDict, total=False):
    actionHostName: Union[str, Parameter]
    """Hostname of a slot to which the traffic will be redirected if decided to. E.g. myapp-stage.azurewebsites.net."""
    changeDecisionCallbackUrl: Union[str, Parameter]
    """Custom decision algorithm can be provided in TiPCallback site extension which URL can be specified."""
    changeIntervalInMinutes: Union[int, Parameter]
    """Specifies interval in minutes to reevaluate ReroutePercentage."""
    changeStep: Union[int, Parameter]
    """In auto ramp up scenario this is the step to add/remove from <code>ReroutePercentage</code> until it reaches \\n<code>MinReroutePercentage</code> or <code>MaxReroutePercentage</code>. Site metrics are checked every N minutes specified in <code>ChangeIntervalInMinutes</code>.\\nCustom decision algorithm can be provided in TiPCallback site extension which URL can be specified in <code>ChangeDecisionCallbackUrl</code>."""
    maxReroutePercentage: Union[int, Parameter]
    """Specifies upper boundary below which ReroutePercentage will stay."""
    minReroutePercentage: Union[int, Parameter]
    """Specifies lower boundary above which ReroutePercentage will stay."""
    name: Union[str, Parameter]
    """Name of the routing rule. The recommended name would be to point to the slot which will receive the traffic in the experiment."""
    reroutePercentage: Union[int, Parameter]
    """Percentage of the traffic which will be redirected to <code>ActionHostName</code>."""


class AppSiteRequestsBasedTrigger(TypedDict, total=False):
    count: Union[int, Parameter]
    """Request Count."""
    timeInterval: Union[str, Parameter]
    """Time interval."""


class AppSiteResourceConfig(TypedDict, total=False):
    cpu: Union[int, Parameter]
    """Required CPU in cores, e.g. 0.5"""
    memory: Union[str, Parameter]
    """Required memory, e.g. \"1Gi\""""


class AppSiteConfig(TypedDict, total=False):
    acrUseManagedIdentityCreds: Union[bool, Parameter]
    """Flag to use Managed Identity Creds for ACR pull"""
    acrUserManagedIdentityID: Union[str, Parameter]
    """If using user managed identity, the user managed identity ClientId"""
    alwaysOn: Union[bool, Parameter]
    """<code>true</code> if Always On is enabled; otherwise, <code>false</code>."""
    apiDefinition: Union[AppSiteApiDefinitionInfo, Parameter]
    """Information about the formal API definition for the app."""
    apiManagementConfig: Union[AppSiteApiManagementConfig, Parameter]
    """Azure API management settings linked to the app."""
    appCommandLine: Union[str, Parameter]
    """App command line to launch."""
    appSettings: Union[list[AppSiteNameValuePair], Parameter]
    """Application settings."""
    autoHealEnabled: Union[bool, Parameter]
    """<code>true</code> if Auto Heal is enabled; otherwise, <code>false</code>."""
    autoHealRules: Union[AppSiteAutoHealRules, Parameter]
    """Auto Heal rules."""
    autoSwapSlotName: Union[str, Parameter]
    """Auto-swap slot name."""
    azureStorageAccounts: Union[AppSiteConfig, Parameter]
    """List of Azure Storage Accounts."""
    connectionStrings: Union[list[AppSiteConnStringInfo], Parameter]
    """Connection strings."""
    cors: Union[AppSiteCorsSettings, Parameter]
    """Cross-Origin Resource Sharing (CORS) settings."""
    defaultDocuments: Union[list[Union[str, Parameter]], Parameter]
    """Default documents."""
    detailedErrorLoggingEnabled: Union[bool, Parameter]
    """<code>true</code> if detailed error logging is enabled; otherwise, <code>false</code>."""
    documentRoot: Union[str, Parameter]
    """Document root."""
    elasticWebAppScaleLimit: Union[int, Parameter]
    """Maximum number of workers that a site can scale out to.This setting only applies to apps in plans where ElasticScaleEnabled is <code>true</code>"""
    experiments: Union[AppSiteExperiments, Parameter]
    """This is work around for polymorphic types."""
    ftpsState: Union[Literal["AllAllowed", "Disabled", "FtpsOnly"], Parameter]
    """State of FTP / FTPS service"""
    functionAppScaleLimit: Union[int, Parameter]
    """Maximum number of workers that a site can scale out to.This setting only applies to the Consumption and Elastic Premium Plans"""
    functionsRuntimeScaleMonitoringEnabled: Union[bool, Parameter]
    """Gets or sets a value indicating whether functions runtime scale monitoring is enabled. When enabled,the ScaleController will not monitor event sources directly, but will instead call to theruntime to get scale status."""
    handlerMappings: Union[list[AppSiteHandlerMapping], Parameter]
    """Handler mappings."""
    healthCheckPath: Union[str, Parameter]
    """Health check path"""
    http20Enabled: Union[bool, Parameter]
    """Http20Enabled: configures a web site to allow clients to connect over http2.0"""
    httpLoggingEnabled: Union[bool, Parameter]
    """<code>true</code> if HTTP logging is enabled; otherwise, <code>false</code>."""
    ipSecurityRestrictions: Union[list[AppSiteIpSecurityRestriction], Parameter]
    """IP security restrictions for main."""
    ipSecurityRestrictionsDefaultAction: Union[Literal["Deny", "Allow"], Parameter]
    """Default action for main access restriction if no rules are matched."""
    javaContainer: Union[str, Parameter]
    """Java container."""
    javaContainerVersion: Union[str, Parameter]
    """Java container version."""
    javaVersion: Union[str, Parameter]
    """Java version."""
    keyVaultReferenceIdentity: Union[str, Parameter]
    """Identity to use for Key Vault Reference authentication."""
    limits: Union[AppSiteLimits, Parameter]
    """Site limits."""
    linuxFxVersion: Union[str, Parameter]
    """Linux App Framework and version"""
    loadBalancing: Union[
        Literal[
            "LeastRequests",
            "LeastRequestsWithTieBreaker",
            "WeightedRoundRobin",
            "WeightedTotalTraffic",
            "LeastResponseTime",
            "PerSiteRoundRobin",
            "RequestHash",
        ],
        Parameter,
    ]
    """Site load balancing."""
    localMySqlEnabled: Union[bool, Parameter]
    """<code>true</code> to enable local MySQL; otherwise, <code>false</code>."""
    logsDirectorySizeLimit: Union[int, Parameter]
    """HTTP logs directory size limit."""
    managedPipelineMode: Union[Literal["Classic", "Integrated"], Parameter]
    """Managed pipeline mode."""
    managedServiceIdentityId: Union[int, Parameter]
    """Managed Service Identity Id"""
    metadata: Union[list[AppSiteNameValuePair], Parameter]
    """Application metadata. This property cannot be retrieved, since it may contain secrets."""
    minimumElasticInstanceCount: Union[int, Parameter]
    """Number of minimum instance count for a siteThis setting only applies to the Elastic Plans"""
    minTlsCipherSuite: Union[
        Literal[
            "TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256",
            "TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA256",
            "TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA",
            "TLS_RSA_WITH_AES_128_GCM_SHA256",
            "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
            "TLS_RSA_WITH_AES_256_GCM_SHA384",
            "TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA",
            "TLS_AES_128_GCM_SHA256",
            "TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA256",
            "TLS_RSA_WITH_AES_128_CBC_SHA256",
            "TLS_RSA_WITH_AES_256_CBC_SHA256",
            "TLS_RSA_WITH_AES_256_CBC_SHA",
            "TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384",
            "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256",
            "TLS_RSA_WITH_AES_128_CBC_SHA",
            "TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA384",
            "TLS_AES_256_GCM_SHA384",
        ],
        Parameter,
    ]
    """The minimum strength TLS cipher suite allowed for an application"""
    minTlsVersion: Union[Literal["1.0", "1.3", "1.1", "1.2"], Parameter]
    """MinTlsVersion: configures the minimum version of TLS required for SSL requests"""
    netFrameworkVersion: Union[str, Parameter]
    """.NET Framework version."""
    nodeVersion: Union[str, Parameter]
    """Version of Node.js."""
    numberOfWorkers: Union[int, Parameter]
    """Number of workers."""
    phpVersion: Union[str, Parameter]
    """Version of PHP."""
    powerShellVersion: Union[str, Parameter]
    """Version of PowerShell."""
    preWarmedInstanceCount: Union[int, Parameter]
    """Number of preWarmed instances.This setting only applies to the Consumption and Elastic Plans"""
    publicNetworkAccess: Union[str, Parameter]
    """Property to allow or block all public traffic."""
    publishingUsername: Union[str, Parameter]
    """Publishing user name."""
    push: Union[AppSitePushSettings, Parameter]
    """Push endpoint settings."""
    pythonVersion: Union[str, Parameter]
    """Version of Python."""
    remoteDebuggingEnabled: Union[bool, Parameter]
    """<code>true</code> if remote debugging is enabled; otherwise, <code>false</code>."""
    remoteDebuggingVersion: Union[str, Parameter]
    """Remote debugging version."""
    requestTracingEnabled: Union[bool, Parameter]
    """<code>true</code> if request tracing is enabled; otherwise, <code>false</code>."""
    requestTracingExpirationTime: Union[str, Parameter]
    """Request tracing expiration time."""
    scmIpSecurityRestrictions: Union[list[AppSiteIpSecurityRestriction], Parameter]
    """IP security restrictions for scm."""
    scmIpSecurityRestrictionsDefaultAction: Union[Literal["Deny", "Allow"], Parameter]
    """Default action for scm access restriction if no rules are matched."""
    scmIpSecurityRestrictionsUseMain: Union[bool, Parameter]
    """IP security restrictions for scm to use main."""
    scmMinTlsVersion: Union[Literal["1.0", "1.3", "1.1", "1.2"], Parameter]
    """ScmMinTlsVersion: configures the minimum version of TLS required for SSL requests for SCM site"""
    scmType: Union[
        Literal[
            "ExternalGit",
            "ExternalHg",
            "VSO",
            "CodePlexHg",
            "BitbucketGit",
            "VSTSRM",
            "Tfs",
            "Dropbox",
            "CodePlexGit",
            "None",
            "BitbucketHg",
            "GitHub",
            "OneDrive",
            "LocalGit",
        ],
        Parameter,
    ]
    """SCM type."""
    tracingOptions: Union[str, Parameter]
    """Tracing options."""
    use32BitWorkerProcess: Union[bool, Parameter]
    """<code>true</code> to use 32-bit worker process; otherwise, <code>false</code>."""
    virtualApplications: Union[list[AppSiteVirtualApplication], Parameter]
    """Virtual applications."""
    vnetName: Union[str, Parameter]
    """Virtual Network name."""
    vnetPrivatePortsCount: Union[int, Parameter]
    """The number of private ports assigned to this app. These will be assigned dynamically on runtime."""
    vnetRouteAllEnabled: Union[bool, Parameter]
    """Virtual Network Route All enabled. This causes all outbound traffic to have Virtual Network Security Groups and User Defined Routes applied."""
    websiteTimeZone: Union[str, Parameter]
    """Sets the time zone a site uses for generating timestamps. Compatible with Linux and Windows App Service. Setting the WEBSITE_TIME_ZONE app setting takes precedence over this config. For Linux, expects tz database values https://www.iana.org/time-zones (for a quick reference see https://en.wikipedia.org/wiki/List_of_tz_database_time_zones). For Windows, expects one of the time zones listed under HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Time Zones"""
    webSocketsEnabled: Union[bool, Parameter]
    """<code>true</code> if WebSocket is enabled; otherwise, <code>false</code>."""
    windowsFxVersion: Union[str, Parameter]
    """Xenon App Framework and version"""
    xManagedServiceIdentityId: Union[int, Parameter]
    """Explicit Managed Service Identity Id"""


class AppSiteDnsConfig(TypedDict, total=False):
    dnsAltServer: Union[str, Parameter]
    """Alternate DNS server to be used by apps. This property replicates the WEBSITE_DNS_ALT_SERVER app setting."""
    dnsMaxCacheTimeout: Union[int, Parameter]
    """Custom time for DNS to be cached in seconds. Allowed range: 0-60. Default is 30 seconds. 0 means caching disabled."""
    dnsRetryAttemptCount: Union[int, Parameter]
    """Total number of retries for dns lookup. Allowed range: 1-5. Default is 3."""
    dnsRetryAttemptTimeout: Union[int, Parameter]
    """Timeout for a single dns lookup in seconds. Allowed range: 1-30. Default is 3."""
    dnsServers: Union[list[Union[str, Parameter]], Parameter]
    """List of custom DNS servers to be used by an app for lookups. Maximum 5 dns servers can be set."""


class AppSiteLimits(TypedDict, total=False):
    maxDiskSizeInMb: Union[int, Parameter]
    """Maximum allowed disk size usage in MB."""
    maxMemoryInMb: Union[int, Parameter]
    """Maximum allowed memory usage in MB."""
    maxPercentageCpu: Union[int, Parameter]
    """Maximum allowed CPU usage percentage."""


class AppSiteProperties(TypedDict, total=False):
    autoGeneratedDomainNameLabelScope: Union[
        Literal["NoReuse", "ResourceGroupReuse", "TenantReuse", "SubscriptionReuse"], Parameter
    ]
    """Specifies the scope of uniqueness for the default hostname during resource creation"""
    clientAffinityEnabled: Union[bool, Parameter]
    """<code>true</code> to enable client affinity; <code>false</code> to stop sending session affinity cookies, which route client requests in the same session to the same instance. Default is <code>true</code>."""
    clientCertEnabled: Union[bool, Parameter]
    """<code>true</code> to enable client certificate authentication (TLS mutual authentication); otherwise, <code>false</code>. Default is <code>false</code>."""
    clientCertExclusionPaths: Union[str, Parameter]
    """client certificate authentication comma-separated exclusion paths"""
    clientCertMode: Union[Literal["Optional", "Required", "OptionalInteractiveUser"], Parameter]
    """This composes with ClientCertEnabled setting.- ClientCertEnabled: false means ClientCert is ignored.- ClientCertEnabled: true and ClientCertMode: Required means ClientCert is required.- ClientCertEnabled: true and ClientCertMode: Optional means ClientCert is optional or accepted."""
    cloningInfo: Union[AppSiteCloningInfo, Parameter]
    """If specified during app creation, the app is cloned from a source app."""
    containerSize: Union[int, Parameter]
    """Size of the function container."""
    customDomainVerificationId: Union[str, Parameter]
    """Unique identifier that verifies the custom domains assigned to the app. Customer will add this id to a txt record for verification."""
    dailyMemoryTimeQuota: Union[int, Parameter]
    """Maximum allowed daily memory-time quota (applicable on dynamic apps only)."""
    daprConfig: Union[AppSiteDaprConfig, Parameter]
    """Dapr configuration of the app."""
    dnsConfiguration: Union[AppSiteDnsConfig, Parameter]
    """Property to configure various DNS related settings for a site."""
    enabled: Union[bool, Parameter]
    """<code>true</code> if the app is enabled; otherwise, <code>false</code>. Setting this value to false disables the app (takes the app offline)."""
    endToEndEncryptionEnabled: Union[bool, Parameter]
    """Whether to use end to end encryption between the FrontEnd and the Worker"""
    functionAppConfig: Union[AppSiteFunctionAppConfig, Parameter]
    """Configuration specific of the Azure Function app."""
    hostingEnvironmentProfile: Union[AppSiteHostingEnvironmentProfile, Parameter]
    """App Service Environment to use for the app."""
    hostNamesDisabled: Union[bool, Parameter]
    """<code>true</code> to disable the public hostnames of the app; otherwise, <code>false</code>. If <code>true</code>, the app is only accessible via API management process."""
    hostNameSslStates: Union[list[AppSiteHostNameSslState], Parameter]
    """Hostname SSL states are used to manage the SSL bindings for app's hostnames."""
    httpsOnly: Union[bool, Parameter]
    """HttpsOnly: configures a web site to accept only https requests. Issues redirect forhttp requests"""
    hyperV: Union[bool, Parameter]
    """Hyper-V sandbox."""
    ipMode: Union[Literal["IPv4", "IPv6", "IPv4AndIPv6"], Parameter]
    """Specifies the IP mode of the app."""
    isXenon: Union[bool, Parameter]
    """Obsolete: Hyper-V sandbox."""
    keyVaultReferenceIdentity: Union[str, Parameter]
    """Identity to use for Key Vault Reference authentication."""
    managedEnvironmentId: Union[str, Parameter]
    """Azure Resource Manager ID of the customer's selected Managed Environment on which to host this app. This must be of the form /subscriptions/{subscriptionId}/resourceGroups/{resourceGroup}/providers/Microsoft.App/managedEnvironments/{managedEnvironmentName}"""
    publicNetworkAccess: Union[str, Parameter]
    """Property to allow or block all public traffic. Allowed Values: 'Enabled', 'Disabled' or an empty string."""
    redundancyMode: Union[Literal["Manual", "ActiveActive", "GeoRedundant", "Failover", "None"], Parameter]
    """Site redundancy mode"""
    reserved: Union[bool, Parameter]
    """<code>true</code> if reserved; otherwise, <code>false</code>."""
    resourceConfig: Union[AppSiteResourceConfig, Parameter]
    """Function app resource requirements."""
    scmSiteAlsoStopped: Union[bool, Parameter]
    """<code>true</code> to stop SCM (KUDU) site when the app is stopped; otherwise, <code>false</code>. The default is <code>false</code>."""
    serverFarmId: Union[str, Parameter]
    """Resource ID of the associated App Service plan, formatted as: \"/subscriptions/{subscriptionID}/resourceGroups/{groupName}/providers/Microsoft.Web/serverfarms/{appServicePlanName}\"."""
    siteConfig: Union[AppSiteConfig, Parameter]
    """Configuration of the app."""
    storageAccountRequired: Union[bool, Parameter]
    """Checks if Customer provided storage account is required"""
    virtualNetworkSubnetId: Union[str, Parameter]
    """Azure Resource Manager ID of the Virtual network and subnet to be joined by Regional VNET Integration.This must be of the form /subscriptions/{subscriptionName}/resourceGroups/{resourceGroupName}/providers/Microsoft.Network/virtualNetworks/{vnetName}/subnets/{subnetName}"""
    vnetBackupRestoreEnabled: Union[bool, Parameter]
    """To enable Backup and Restore operations over virtual network"""
    vnetContentShareEnabled: Union[bool, Parameter]
    """To enable accessing content over virtual network"""
    vnetImagePullEnabled: Union[bool, Parameter]
    """To enable pulling image over Virtual Network"""
    vnetRouteAllEnabled: Union[bool, Parameter]
    """Virtual Network Route All enabled. This causes all outbound traffic to have Virtual Network Security Groups and User Defined Routes applied."""
    workloadProfileName: Union[str, Parameter]
    """Workload profile name for function app to execute on."""


class AppSiteSlowRequestsBasedTrigger(TypedDict, total=False):
    count: Union[int, Parameter]
    """Request Count."""
    path: Union[str, Parameter]
    """Request Path."""
    timeInterval: Union[str, Parameter]
    """Time interval."""
    timeTaken: Union[str, Parameter]
    """Time taken."""


class AppSiteStatusCodesBasedTrigger(TypedDict, total=False):
    count: Union[int, Parameter]
    """Request Count."""
    path: Union[str, Parameter]
    """Request Path"""
    status: Union[int, Parameter]
    """HTTP status code."""
    subStatus: Union[int, Parameter]
    """Request Sub Status."""
    timeInterval: Union[str, Parameter]
    """Time interval."""
    win32Status: Union[int, Parameter]
    """Win32 error code."""


class AppSiteStatusCodesRangeBasedTrigger(TypedDict, total=False):
    count: Union[int, Parameter]
    """Request Count."""
    path: Union[str, Parameter]
    """"""
    statusCodes: Union[str, Parameter]
    """HTTP status code."""
    timeInterval: Union[str, Parameter]
    """Time interval."""


class AppSiteVirtualApplication(TypedDict, total=False):
    physicalPath: Union[str, Parameter]
    """Physical path."""
    preloadEnabled: Union[bool, Parameter]
    """<code>true</code> if preloading is enabled; otherwise, <code>false</code>."""
    virtualDirectories: Union[list[AppSiteVirtualDirectory], Parameter]
    """Virtual directories for virtual application."""
    virtualPath: Union[str, Parameter]
    """Virtual path."""


class AppSiteVirtualDirectory(TypedDict, total=False):
    physicalPath: Union[str, Parameter]
    """Physical path."""
    virtualPath: Union[str, Parameter]
    """Path to virtual application."""
