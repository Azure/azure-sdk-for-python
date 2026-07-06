```py
namespace azure.mgmt.dynatrace

    class azure.mgmt.dynatrace.DynatraceObservabilityMgmtClient: implements ContextManager 
        creation_supported: CreationSupportedOperations
        monitored_subscriptions: MonitoredSubscriptionsOperations
        monitors: MonitorsOperations
        operations: Operations
        single_sign_on: SingleSignOnOperations
        tag_rules: TagRulesOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
                cloud_setting: Optional[AzureClouds] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


namespace azure.mgmt.dynatrace.aio

    class azure.mgmt.dynatrace.aio.DynatraceObservabilityMgmtClient: implements AsyncContextManager 
        creation_supported: CreationSupportedOperations
        monitored_subscriptions: MonitoredSubscriptionsOperations
        monitors: MonitorsOperations
        operations: Operations
        single_sign_on: SingleSignOnOperations
        tag_rules: TagRulesOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
                cloud_setting: Optional[AzureClouds] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


namespace azure.mgmt.dynatrace.aio.operations

    class azure.mgmt.dynatrace.aio.operations.CreationSupportedOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                dynatrace_environment_id: str, 
                **kwargs: Any
            ) -> CreateResourceSupportedResponse: ...

        @distributed_trace_async
        async def list(
                self, 
                dynatrace_environment_id: str, 
                **kwargs: Any
            ) -> CreateResourceSupportedResponse: ...


    class azure.mgmt.dynatrace.aio.operations.MonitoredSubscriptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[MonitoredSubscriptionProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MonitoredSubscriptionProperties]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[MonitoredSubscriptionProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MonitoredSubscriptionProperties]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MonitoredSubscriptionProperties]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[MonitoredSubscriptionProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MonitoredSubscriptionProperties]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[MonitoredSubscriptionProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MonitoredSubscriptionProperties]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MonitoredSubscriptionProperties]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> MonitoredSubscriptionProperties: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[MonitoredSubscriptionProperties]: ...


    class azure.mgmt.dynatrace.aio.operations.MonitorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                resource: MonitorResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MonitorResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                resource: MonitorResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MonitorResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MonitorResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_upgrade_plan(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: UpgradePlanRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_upgrade_plan(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: UpgradePlanRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_upgrade_plan(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> MonitorResource: ...

        @overload
        async def get_all_connected_resources_count(
                self, 
                request: MarketplaceSubscriptionIdRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectedResourcesCountResponse: ...

        @overload
        async def get_all_connected_resources_count(
                self, 
                request: MarketplaceSubscriptionIdRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectedResourcesCountResponse: ...

        @overload
        async def get_all_connected_resources_count(
                self, 
                request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectedResourcesCountResponse: ...

        @overload
        async def get_marketplace_saa_s_resource_details(
                self, 
                request: MarketplaceSaaSResourceDetailsRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MarketplaceSaaSResourceDetailsResponse: ...

        @overload
        async def get_marketplace_saa_s_resource_details(
                self, 
                request: MarketplaceSaaSResourceDetailsRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MarketplaceSaaSResourceDetailsResponse: ...

        @overload
        async def get_marketplace_saa_s_resource_details(
                self, 
                request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MarketplaceSaaSResourceDetailsResponse: ...

        @overload
        async def get_metric_status(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: Optional[MetricStatusRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MetricsStatusResponse: ...

        @overload
        async def get_metric_status(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: Optional[MetricStatusRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MetricsStatusResponse: ...

        @overload
        async def get_metric_status(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MetricsStatusResponse: ...

        @overload
        async def get_sso_details(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: Optional[SSODetailsRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SSODetailsResponse: ...

        @overload
        async def get_sso_details(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: Optional[SSODetailsRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SSODetailsResponse: ...

        @overload
        async def get_sso_details(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SSODetailsResponse: ...

        @distributed_trace_async
        async def get_vm_host_payload(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> VMExtensionPayload: ...

        @distributed_trace
        def list_app_services(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AppServiceInfo]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[MonitorResource]: ...

        @distributed_trace
        def list_by_subscription_id(self, **kwargs: Any) -> AsyncItemPaged[MonitorResource]: ...

        @distributed_trace
        def list_hosts(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[VMInfo]: ...

        @overload
        def list_linkable_environments(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: LinkableEnvironmentRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncItemPaged[LinkableEnvironmentResponse]: ...

        @overload
        def list_linkable_environments(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: LinkableEnvironmentRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncItemPaged[LinkableEnvironmentResponse]: ...

        @overload
        def list_linkable_environments(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncItemPaged[LinkableEnvironmentResponse]: ...

        @overload
        def list_monitored_resources(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: Optional[LogStatusRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncItemPaged[MonitoredResource]: ...

        @overload
        def list_monitored_resources(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: Optional[LogStatusRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncItemPaged[MonitoredResource]: ...

        @overload
        def list_monitored_resources(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncItemPaged[MonitoredResource]: ...

        @overload
        async def manage_agent_installation(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: ManageAgentInstallationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def manage_agent_installation(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: ManageAgentInstallationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def manage_agent_installation(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                resource: MonitorResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MonitorResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                resource: MonitorResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MonitorResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MonitorResource: ...


    class azure.mgmt.dynatrace.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.dynatrace.aio.operations.SingleSignOnOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                configuration_name: str, 
                resource: DynatraceSingleSignOnResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DynatraceSingleSignOnResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                configuration_name: str, 
                resource: DynatraceSingleSignOnResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DynatraceSingleSignOnResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                configuration_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DynatraceSingleSignOnResource]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                configuration_name: str, 
                **kwargs: Any
            ) -> DynatraceSingleSignOnResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DynatraceSingleSignOnResource]: ...


    class azure.mgmt.dynatrace.aio.operations.TagRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                rule_set_name: str, 
                resource: TagRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TagRule]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                rule_set_name: str, 
                resource: TagRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TagRule]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                rule_set_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TagRule]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                rule_set_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                rule_set_name: str, 
                **kwargs: Any
            ) -> TagRule: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[TagRule]: ...


namespace azure.mgmt.dynatrace.models

    class azure.mgmt.dynatrace.models.AccountInfo(_Model):
        account_id: Optional[str]
        company_name: Optional[str]
        region_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                account_id: Optional[str] = ..., 
                company_name: Optional[str] = ..., 
                region_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dynatrace.models.Action(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INSTALL = "Install"
        UNINSTALL = "Uninstall"


    class azure.mgmt.dynatrace.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.dynatrace.models.AppServiceInfo(_Model):
        auto_update_setting: Optional[Union[str, AutoUpdateSetting]]
        availability_state: Optional[Union[str, AvailabilityState]]
        host_group: Optional[str]
        host_name: Optional[str]
        log_module: Optional[Union[str, LogModule]]
        monitoring_type: Optional[Union[str, MonitoringType]]
        resource_id: Optional[str]
        update_status: Optional[Union[str, UpdateStatus]]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                auto_update_setting: Optional[Union[str, AutoUpdateSetting]] = ..., 
                availability_state: Optional[Union[str, AvailabilityState]] = ..., 
                host_group: Optional[str] = ..., 
                host_name: Optional[str] = ..., 
                log_module: Optional[Union[str, LogModule]] = ..., 
                monitoring_type: Optional[Union[str, MonitoringType]] = ..., 
                resource_id: Optional[str] = ..., 
                update_status: Optional[Union[str, UpdateStatus]] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dynatrace.models.AutoUpdateSetting(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "DISABLED"
        ENABLED = "ENABLED"


    class azure.mgmt.dynatrace.models.AvailabilityState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CRASHED = "CRASHED"
        LOST = "LOST"
        MONITORED = "MONITORED"
        PRE_MONITORED = "PRE_MONITORED"
        SHUTDOWN = "SHUTDOWN"
        UNEXPECTED_SHUTDOWN = "UNEXPECTED_SHUTDOWN"
        UNKNOWN = "UNKNOWN"
        UNMONITORED = "UNMONITORED"


    class azure.mgmt.dynatrace.models.ConnectedResourcesCountResponse(_Model):
        connected_resources_count: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                connected_resources_count: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dynatrace.models.CreateResourceSupportedProperties(_Model):
        creation_supported: Optional[bool]
        name: Optional[str]


    class azure.mgmt.dynatrace.models.CreateResourceSupportedResponse(_Model):
        next_link: Optional[str]
        value: Optional[list[CreateResourceSupportedProperties]]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[list[CreateResourceSupportedProperties]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dynatrace.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.dynatrace.models.DynatraceEnvironmentProperties(_Model):
        account_info: Optional[AccountInfo]
        environment_info: Optional[EnvironmentInfo]
        single_sign_on_properties: Optional[DynatraceSingleSignOnProperties]
        user_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                account_info: Optional[AccountInfo] = ..., 
                environment_info: Optional[EnvironmentInfo] = ..., 
                single_sign_on_properties: Optional[DynatraceSingleSignOnProperties] = ..., 
                user_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dynatrace.models.DynatraceSingleSignOnProperties(_Model):
        aad_domains: Optional[list[str]]
        enterprise_app_id: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        single_sign_on_state: Optional[Union[str, SingleSignOnStates]]
        single_sign_on_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                aad_domains: Optional[list[str]] = ..., 
                enterprise_app_id: Optional[str] = ..., 
                single_sign_on_state: Optional[Union[str, SingleSignOnStates]] = ..., 
                single_sign_on_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dynatrace.models.DynatraceSingleSignOnResource(ProxyResource):
        id: str
        name: str
        properties: DynatraceSingleSignOnProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: DynatraceSingleSignOnProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.dynatrace.models.EnvironmentInfo(_Model):
        environment_id: Optional[str]
        ingestion_key: Optional[str]
        landing_url: Optional[str]
        logs_ingestion_endpoint: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                environment_id: Optional[str] = ..., 
                ingestion_key: Optional[str] = ..., 
                landing_url: Optional[str] = ..., 
                logs_ingestion_endpoint: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dynatrace.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.dynatrace.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.dynatrace.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dynatrace.models.FilteringTag(_Model):
        action: Optional[Union[str, TagAction]]
        name: Optional[str]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                action: Optional[Union[str, TagAction]] = ..., 
                name: Optional[str] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dynatrace.models.IdentityProperties(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Union[str, ManagedIdentityType]
        user_assigned_identities: Optional[dict[str, UserAssignedIdentity]]

        @overload
        def __init__(
                self, 
                *, 
                type: Union[str, ManagedIdentityType], 
                user_assigned_identities: Optional[dict[str, UserAssignedIdentity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dynatrace.models.LiftrResourceCategories(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MONITOR_LOGS = "MonitorLogs"
        UNKNOWN = "Unknown"


    class azure.mgmt.dynatrace.models.LinkableEnvironmentRequest(_Model):
        region: str
        tenant_id: str
        user_principal: str

        @overload
        def __init__(
                self, 
                *, 
                region: str, 
                tenant_id: str, 
                user_principal: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dynatrace.models.LinkableEnvironmentResponse(_Model):
        environment_id: Optional[str]
        environment_name: Optional[str]
        plan_data: Optional[PlanData]

        @overload
        def __init__(
                self, 
                *, 
                environment_id: Optional[str] = ..., 
                environment_name: Optional[str] = ..., 
                plan_data: Optional[PlanData] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dynatrace.models.LogModule(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "DISABLED"
        ENABLED = "ENABLED"


    class azure.mgmt.dynatrace.models.LogRules(_Model):
        filtering_tags: Optional[list[FilteringTag]]
        send_aad_logs: Optional[Union[str, SendAadLogsStatus]]
        send_activity_logs: Optional[Union[str, SendActivityLogsStatus]]
        send_subscription_logs: Optional[Union[str, SendSubscriptionLogsStatus]]

        @overload
        def __init__(
                self, 
                *, 
                filtering_tags: Optional[list[FilteringTag]] = ..., 
                send_aad_logs: Optional[Union[str, SendAadLogsStatus]] = ..., 
                send_activity_logs: Optional[Union[str, SendActivityLogsStatus]] = ..., 
                send_subscription_logs: Optional[Union[str, SendSubscriptionLogsStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dynatrace.models.LogStatusRequest(_Model):
        monitored_resource_ids: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                monitored_resource_ids: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dynatrace.models.ManageAgentInstallationRequest(_Model):
        action: Union[str, Action]
        manage_agent_installation_list: list[ManageAgentList]

        @overload
        def __init__(
                self, 
                *, 
                action: Union[str, Action], 
                manage_agent_installation_list: list[ManageAgentList]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dynatrace.models.ManageAgentList(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dynatrace.models.ManagedIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM_AND_USER_ASSIGNED = "SystemAndUserAssigned"
        SYSTEM_ASSIGNED = "SystemAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.dynatrace.models.ManagedServiceIdentity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Union[str, ManagedServiceIdentityType]
        user_assigned_identities: Optional[dict[str, UserAssignedIdentity]]

        @overload
        def __init__(
                self, 
                *, 
                type: Union[str, ManagedServiceIdentityType], 
                user_assigned_identities: Optional[dict[str, UserAssignedIdentity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dynatrace.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.dynatrace.models.MarketplaceSaaSResourceDetailsRequest(_Model):
        tenant_id: str

        @overload
        def __init__(
                self, 
                *, 
                tenant_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dynatrace.models.MarketplaceSaaSResourceDetailsResponse(_Model):
        marketplace_saa_s_resource_id: Optional[str]
        marketplace_saa_s_resource_name: Optional[str]
        marketplace_subscription_status: Optional[Union[str, MarketplaceSubscriptionStatus]]
        plan_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                marketplace_saa_s_resource_id: Optional[str] = ..., 
                marketplace_saa_s_resource_name: Optional[str] = ..., 
                marketplace_subscription_status: Optional[Union[str, MarketplaceSubscriptionStatus]] = ..., 
                plan_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dynatrace.models.MarketplaceSaasAutoRenew(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OFF = "Off"
        ON = "On"


    class azure.mgmt.dynatrace.models.MarketplaceSubscriptionIdRequest(_Model):
        marketplace_subscription_id: str

        @overload
        def __init__(
                self, 
                *, 
                marketplace_subscription_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dynatrace.models.MarketplaceSubscriptionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        SUSPENDED = "Suspended"
        UNSUBSCRIBED = "Unsubscribed"


    class azure.mgmt.dynatrace.models.MetricRules(_Model):
        filtering_tags: Optional[list[FilteringTag]]
        sending_metrics: Optional[Union[str, SendingMetricsStatus]]

        @overload
        def __init__(
                self, 
                *, 
                filtering_tags: Optional[list[FilteringTag]] = ..., 
                sending_metrics: Optional[Union[str, SendingMetricsStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dynatrace.models.MetricStatusRequest(_Model):
        monitored_resource_ids: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                monitored_resource_ids: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dynatrace.models.MetricsStatusResponse(_Model):
        azure_resource_ids: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                azure_resource_ids: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dynatrace.models.MonitorProperties(_Model):
        dynatrace_environment_properties: Optional[DynatraceEnvironmentProperties]
        liftr_resource_category: Optional[Union[str, LiftrResourceCategories]]
        liftr_resource_preference: Optional[int]
        marketplace_saas_auto_renew: Optional[Union[str, MarketplaceSaasAutoRenew]]
        marketplace_subscription_status: Optional[Union[str, MarketplaceSubscriptionStatus]]
        monitoring_status: Optional[Union[str, MonitoringStatus]]
        plan_data: Optional[PlanData]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        user_info: Optional[UserInfo]

        @overload
        def __init__(
                self, 
                *, 
                dynatrace_environment_properties: Optional[DynatraceEnvironmentProperties] = ..., 
                marketplace_saas_auto_renew: Optional[Union[str, MarketplaceSaasAutoRenew]] = ..., 
                marketplace_subscription_status: Optional[Union[str, MarketplaceSubscriptionStatus]] = ..., 
                monitoring_status: Optional[Union[str, MonitoringStatus]] = ..., 
                plan_data: Optional[PlanData] = ..., 
                user_info: Optional[UserInfo] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dynatrace.models.MonitorResource(TrackedResource):
        id: str
        identity: Optional[IdentityProperties]
        location: str
        name: str
        properties: MonitorProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[IdentityProperties] = ..., 
                location: str, 
                properties: MonitorProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.dynatrace.models.MonitorResourceUpdate(_Model):
        identity: Optional[ManagedServiceIdentity]
        properties: Optional[MonitorUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                properties: Optional[MonitorUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dynatrace.models.MonitorUpdateProperties(_Model):
        plan_data: Optional[PlanData]

        @overload
        def __init__(
                self, 
                *, 
                plan_data: Optional[PlanData] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dynatrace.models.MonitoredResource(_Model):
        id: Optional[str]
        reason_for_logs_status: Optional[str]
        reason_for_metrics_status: Optional[str]
        sending_logs: Optional[Union[str, SendingLogsStatus]]
        sending_metrics: Optional[Union[str, SendingMetricsStatus]]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                reason_for_logs_status: Optional[str] = ..., 
                reason_for_metrics_status: Optional[str] = ..., 
                sending_logs: Optional[Union[str, SendingLogsStatus]] = ..., 
                sending_metrics: Optional[Union[str, SendingMetricsStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dynatrace.models.MonitoredSubscription(_Model):
        error: Optional[str]
        status: Optional[Union[str, Status]]
        subscription_id: str
        tag_rules: Optional[MonitoringTagRulesProperties]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[str] = ..., 
                status: Optional[Union[str, Status]] = ..., 
                subscription_id: str, 
                tag_rules: Optional[MonitoringTagRulesProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dynatrace.models.MonitoredSubscriptionProperties(ProxyResource):
        id: str
        name: str
        properties: Optional[SubscriptionList]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SubscriptionList] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dynatrace.models.MonitoringStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.dynatrace.models.MonitoringTagRulesProperties(_Model):
        log_rules: Optional[LogRules]
        metric_rules: Optional[MetricRules]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                log_rules: Optional[LogRules] = ..., 
                metric_rules: Optional[MetricRules] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dynatrace.models.MonitoringType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLOUD_INFRASTRUCTURE = "CLOUD_INFRASTRUCTURE"
        DISCOVERY = "DISCOVERY"
        FULL_STACK = "FULL_STACK"


    class azure.mgmt.dynatrace.models.Operation(_Model):
        action_type: Optional[Union[str, ActionType]]
        display: Optional[OperationDisplay]
        is_data_action: Optional[bool]
        name: Optional[str]
        origin: Optional[Union[str, Origin]]

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dynatrace.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.dynatrace.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.dynatrace.models.PlanData(_Model):
        billing_cycle: Optional[str]
        effective_date: Optional[datetime]
        plan_details: Optional[str]
        usage_type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                billing_cycle: Optional[str] = ..., 
                effective_date: Optional[datetime] = ..., 
                plan_details: Optional[str] = ..., 
                usage_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dynatrace.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETED = "Deleted"
        DELETING = "Deleting"
        FAILED = "Failed"
        NOT_SPECIFIED = "NotSpecified"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.dynatrace.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.dynatrace.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.dynatrace.models.SSODetailsRequest(_Model):
        user_principal: str

        @overload
        def __init__(
                self, 
                *, 
                user_principal: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dynatrace.models.SSODetailsResponse(_Model):
        aad_domains: Optional[list[str]]
        admin_users: Optional[list[str]]
        is_sso_enabled: Optional[Union[str, SSOStatus]]
        metadata_url: Optional[str]
        single_sign_on_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                aad_domains: Optional[list[str]] = ..., 
                admin_users: Optional[list[str]] = ..., 
                is_sso_enabled: Optional[Union[str, SSOStatus]] = ..., 
                metadata_url: Optional[str] = ..., 
                single_sign_on_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dynatrace.models.SSOStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.dynatrace.models.SendAadLogsStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.dynatrace.models.SendActivityLogsStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.dynatrace.models.SendSubscriptionLogsStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.dynatrace.models.SendingLogsStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.dynatrace.models.SendingMetricsStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.dynatrace.models.SingleSignOnStates(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLE = "Disable"
        ENABLE = "Enable"
        EXISTING = "Existing"
        INITIAL = "Initial"


    class azure.mgmt.dynatrace.models.Status(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        DELETING = "Deleting"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"


    class azure.mgmt.dynatrace.models.SubscriptionList(_Model):
        monitored_subscription_list: Optional[list[MonitoredSubscription]]
        operation: Optional[Union[str, SubscriptionListOperation]]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                monitored_subscription_list: Optional[list[MonitoredSubscription]] = ..., 
                operation: Optional[Union[str, SubscriptionListOperation]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dynatrace.models.SubscriptionListOperation(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        ADD_BEGIN = "AddBegin"
        ADD_COMPLETE = "AddComplete"
        DELETE_BEGIN = "DeleteBegin"
        DELETE_COMPLETE = "DeleteComplete"


    class azure.mgmt.dynatrace.models.SystemData(_Model):
        created_at: Optional[datetime]
        created_by: Optional[str]
        created_by_type: Optional[Union[str, CreatedByType]]
        last_modified_at: Optional[datetime]
        last_modified_by: Optional[str]
        last_modified_by_type: Optional[Union[str, CreatedByType]]

        @overload
        def __init__(
                self, 
                *, 
                created_at: Optional[datetime] = ..., 
                created_by: Optional[str] = ..., 
                created_by_type: Optional[Union[str, CreatedByType]] = ..., 
                last_modified_at: Optional[datetime] = ..., 
                last_modified_by: Optional[str] = ..., 
                last_modified_by_type: Optional[Union[str, CreatedByType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dynatrace.models.TagAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXCLUDE = "Exclude"
        INCLUDE = "Include"


    class azure.mgmt.dynatrace.models.TagRule(ProxyResource):
        id: str
        name: str
        properties: MonitoringTagRulesProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: MonitoringTagRulesProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.dynatrace.models.TrackedResource(Resource):
        id: str
        location: str
        name: str
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dynatrace.models.UpdateStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INCOMPATIBLE = "INCOMPATIBLE"
        OUTDATED = "OUTDATED"
        SCHEDULED = "SCHEDULED"
        SUPPRESSED = "SUPPRESSED"
        UNKNOWN = "UNKNOWN"
        UP2_DATE = "UP2DATE"
        UPDATE_IN_PROGRESS = "UPDATE_IN_PROGRESS"
        UPDATE_PENDING = "UPDATE_PENDING"
        UPDATE_PROBLEM = "UPDATE_PROBLEM"


    class azure.mgmt.dynatrace.models.UpgradePlanRequest(_Model):
        plan_data: Optional[PlanData]

        @overload
        def __init__(
                self, 
                *, 
                plan_data: Optional[PlanData] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dynatrace.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.dynatrace.models.UserInfo(_Model):
        country: Optional[str]
        email_address: Optional[str]
        first_name: Optional[str]
        last_name: Optional[str]
        phone_number: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                country: Optional[str] = ..., 
                email_address: Optional[str] = ..., 
                first_name: Optional[str] = ..., 
                last_name: Optional[str] = ..., 
                phone_number: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dynatrace.models.VMExtensionPayload(_Model):
        environment_id: Optional[str]
        ingestion_key: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                environment_id: Optional[str] = ..., 
                ingestion_key: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dynatrace.models.VMInfo(_Model):
        auto_update_setting: Optional[Union[str, AutoUpdateSetting]]
        availability_state: Optional[Union[str, AvailabilityState]]
        host_group: Optional[str]
        host_name: Optional[str]
        log_module: Optional[Union[str, LogModule]]
        monitoring_type: Optional[Union[str, MonitoringType]]
        resource_id: Optional[str]
        update_status: Optional[Union[str, UpdateStatus]]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                auto_update_setting: Optional[Union[str, AutoUpdateSetting]] = ..., 
                availability_state: Optional[Union[str, AvailabilityState]] = ..., 
                host_group: Optional[str] = ..., 
                host_name: Optional[str] = ..., 
                log_module: Optional[Union[str, LogModule]] = ..., 
                monitoring_type: Optional[Union[str, MonitoringType]] = ..., 
                resource_id: Optional[str] = ..., 
                update_status: Optional[Union[str, UpdateStatus]] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.dynatrace.operations

    class azure.mgmt.dynatrace.operations.CreationSupportedOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                dynatrace_environment_id: str, 
                **kwargs: Any
            ) -> CreateResourceSupportedResponse: ...

        @distributed_trace
        def list(
                self, 
                dynatrace_environment_id: str, 
                **kwargs: Any
            ) -> CreateResourceSupportedResponse: ...


    class azure.mgmt.dynatrace.operations.MonitoredSubscriptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[MonitoredSubscriptionProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MonitoredSubscriptionProperties]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[MonitoredSubscriptionProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MonitoredSubscriptionProperties]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MonitoredSubscriptionProperties]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[MonitoredSubscriptionProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MonitoredSubscriptionProperties]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[MonitoredSubscriptionProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MonitoredSubscriptionProperties]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MonitoredSubscriptionProperties]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> MonitoredSubscriptionProperties: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> ItemPaged[MonitoredSubscriptionProperties]: ...


    class azure.mgmt.dynatrace.operations.MonitorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                resource: MonitorResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MonitorResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                resource: MonitorResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MonitorResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MonitorResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_upgrade_plan(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: UpgradePlanRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_upgrade_plan(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: UpgradePlanRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_upgrade_plan(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> MonitorResource: ...

        @overload
        def get_all_connected_resources_count(
                self, 
                request: MarketplaceSubscriptionIdRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectedResourcesCountResponse: ...

        @overload
        def get_all_connected_resources_count(
                self, 
                request: MarketplaceSubscriptionIdRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectedResourcesCountResponse: ...

        @overload
        def get_all_connected_resources_count(
                self, 
                request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectedResourcesCountResponse: ...

        @overload
        def get_marketplace_saa_s_resource_details(
                self, 
                request: MarketplaceSaaSResourceDetailsRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MarketplaceSaaSResourceDetailsResponse: ...

        @overload
        def get_marketplace_saa_s_resource_details(
                self, 
                request: MarketplaceSaaSResourceDetailsRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MarketplaceSaaSResourceDetailsResponse: ...

        @overload
        def get_marketplace_saa_s_resource_details(
                self, 
                request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MarketplaceSaaSResourceDetailsResponse: ...

        @overload
        def get_metric_status(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: Optional[MetricStatusRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MetricsStatusResponse: ...

        @overload
        def get_metric_status(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: Optional[MetricStatusRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MetricsStatusResponse: ...

        @overload
        def get_metric_status(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MetricsStatusResponse: ...

        @overload
        def get_sso_details(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: Optional[SSODetailsRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SSODetailsResponse: ...

        @overload
        def get_sso_details(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: Optional[SSODetailsRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SSODetailsResponse: ...

        @overload
        def get_sso_details(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SSODetailsResponse: ...

        @distributed_trace
        def get_vm_host_payload(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> VMExtensionPayload: ...

        @distributed_trace
        def list_app_services(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AppServiceInfo]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[MonitorResource]: ...

        @distributed_trace
        def list_by_subscription_id(self, **kwargs: Any) -> ItemPaged[MonitorResource]: ...

        @distributed_trace
        def list_hosts(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> ItemPaged[VMInfo]: ...

        @overload
        def list_linkable_environments(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: LinkableEnvironmentRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ItemPaged[LinkableEnvironmentResponse]: ...

        @overload
        def list_linkable_environments(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: LinkableEnvironmentRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ItemPaged[LinkableEnvironmentResponse]: ...

        @overload
        def list_linkable_environments(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ItemPaged[LinkableEnvironmentResponse]: ...

        @overload
        def list_monitored_resources(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: Optional[LogStatusRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ItemPaged[MonitoredResource]: ...

        @overload
        def list_monitored_resources(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: Optional[LogStatusRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ItemPaged[MonitoredResource]: ...

        @overload
        def list_monitored_resources(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ItemPaged[MonitoredResource]: ...

        @overload
        def manage_agent_installation(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: ManageAgentInstallationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def manage_agent_installation(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: ManageAgentInstallationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def manage_agent_installation(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                resource: MonitorResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MonitorResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                resource: MonitorResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MonitorResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MonitorResource: ...


    class azure.mgmt.dynatrace.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.dynatrace.operations.SingleSignOnOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                configuration_name: str, 
                resource: DynatraceSingleSignOnResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DynatraceSingleSignOnResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                configuration_name: str, 
                resource: DynatraceSingleSignOnResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DynatraceSingleSignOnResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                configuration_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DynatraceSingleSignOnResource]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                configuration_name: str, 
                **kwargs: Any
            ) -> DynatraceSingleSignOnResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DynatraceSingleSignOnResource]: ...


    class azure.mgmt.dynatrace.operations.TagRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                rule_set_name: str, 
                resource: TagRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TagRule]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                rule_set_name: str, 
                resource: TagRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TagRule]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                rule_set_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TagRule]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                rule_set_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                rule_set_name: str, 
                **kwargs: Any
            ) -> TagRule: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> ItemPaged[TagRule]: ...


namespace azure.mgmt.dynatrace.types

    class azure.mgmt.dynatrace.types.AccountInfo(TypedDict, total=False):
        key "accountId": str
        key "companyName": str
        key "regionId": str
        account_id: str
        company_name: str
        region_id: str


    class azure.mgmt.dynatrace.types.AppServiceInfo(TypedDict, total=False):
        key "autoUpdateSetting": Union[str, AutoUpdateSetting]
        key "availabilityState": Union[str, AvailabilityState]
        key "hostGroup": str
        key "hostName": str
        key "logModule": Union[str, LogModule]
        key "monitoringType": Union[str, MonitoringType]
        key "resourceId": str
        key "updateStatus": Union[str, UpdateStatus]
        key "version": str
        auto_update_setting: Union[str, AutoUpdateSetting]
        availability_state: Union[str, AvailabilityState]
        host_group: str
        host_name: str
        log_module: Union[str, LogModule]
        monitoring_type: Union[str, MonitoringType]
        resource_id: str
        update_status: Union[str, UpdateStatus]
        version: str


    class azure.mgmt.dynatrace.types.ConnectedResourcesCountResponse(TypedDict, total=False):
        key "connectedResourcesCount": int
        connected_resources_count: int


    class azure.mgmt.dynatrace.types.CreateResourceSupportedProperties(TypedDict, total=False):
        key "creationSupported": bool
        key "name": str
        creation_supported: bool
        name: str


    class azure.mgmt.dynatrace.types.CreateResourceSupportedResponse(TypedDict, total=False):
        key "nextLink": str
        next_link: str
        value: list[CreateResourceSupportedProperties]


    class azure.mgmt.dynatrace.types.DynatraceEnvironmentProperties(TypedDict, total=False):
        key "accountInfo": ForwardRef('AccountInfo', module='types')
        key "environmentInfo": ForwardRef('EnvironmentInfo', module='types')
        key "singleSignOnProperties": ForwardRef('DynatraceSingleSignOnProperties', module='types')
        key "userId": str
        account_info: AccountInfo
        environment_info: EnvironmentInfo
        single_sign_on_properties: DynatraceSingleSignOnProperties
        user_id: str


    class azure.mgmt.dynatrace.types.DynatraceSingleSignOnProperties(TypedDict, total=False):
        key "enterpriseAppId": str
        key "provisioningState": Union[str, ProvisioningState]
        key "singleSignOnState": Union[str, SingleSignOnStates]
        key "singleSignOnUrl": str
        aadDomains: list[str]
        aad_domains: list[str]
        enterprise_app_id: str
        provisioning_state: Union[str, ProvisioningState]
        single_sign_on_state: Union[str, SingleSignOnStates]
        single_sign_on_url: str


    class azure.mgmt.dynatrace.types.DynatraceSingleSignOnResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": Required[DynatraceSingleSignOnProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: DynatraceSingleSignOnProperties
        system_data: SystemData
        type: str


    class azure.mgmt.dynatrace.types.EnvironmentInfo(TypedDict, total=False):
        key "environmentId": str
        key "ingestionKey": str
        key "landingURL": str
        key "logsIngestionEndpoint": str
        environment_id: str
        ingestion_key: str
        landing_url: str
        logs_ingestion_endpoint: str


    class azure.mgmt.dynatrace.types.ErrorAdditionalInfo(TypedDict, total=False):
        key "info": Any
        key "type": str
        info: Any
        type: str


    class azure.mgmt.dynatrace.types.ErrorDetail(TypedDict, total=False):
        key "code": str
        key "message": str
        key "target": str
        additionalInfo: list[ErrorAdditionalInfo]
        additional_info: list[ErrorAdditionalInfo]
        code: str
        details: list[ErrorDetail]
        message: str
        target: str


    class azure.mgmt.dynatrace.types.ErrorResponse(TypedDict, total=False):
        key "error": ForwardRef('ErrorDetail', module='types')
        error: ErrorDetail


    class azure.mgmt.dynatrace.types.FilteringTag(TypedDict, total=False):
        key "action": Union[str, TagAction]
        key "name": str
        key "value": str
        action: Union[str, TagAction]
        name: str
        value: str


    class azure.mgmt.dynatrace.types.IdentityProperties(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Required[Union[str, ManagedIdentityType]]
        principal_id: str
        tenant_id: str
        type: Union[str, ManagedIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentity]
        user_assigned_identities: dict[str, UserAssignedIdentity]


    class azure.mgmt.dynatrace.types.LinkableEnvironmentRequest(TypedDict, total=False):
        key "region": Required[str]
        key "tenantId": Required[str]
        key "userPrincipal": Required[str]
        region: str
        tenant_id: str
        user_principal: str


    class azure.mgmt.dynatrace.types.LinkableEnvironmentResponse(TypedDict, total=False):
        key "environmentId": str
        key "environmentName": str
        key "planData": ForwardRef('PlanData', module='types')
        environment_id: str
        environment_name: str
        plan_data: PlanData


    class azure.mgmt.dynatrace.types.LogRules(TypedDict, total=False):
        key "sendAadLogs": Union[str, SendAadLogsStatus]
        key "sendActivityLogs": Union[str, SendActivityLogsStatus]
        key "sendSubscriptionLogs": Union[str, SendSubscriptionLogsStatus]
        filteringTags: list[FilteringTag]
        filtering_tags: list[FilteringTag]
        send_aad_logs: Union[str, SendAadLogsStatus]
        send_activity_logs: Union[str, SendActivityLogsStatus]
        send_subscription_logs: Union[str, SendSubscriptionLogsStatus]


    class azure.mgmt.dynatrace.types.LogStatusRequest(TypedDict, total=False):
        monitoredResourceIds: list[str]
        monitored_resource_ids: list[str]


    class azure.mgmt.dynatrace.types.ManageAgentInstallationRequest(TypedDict, total=False):
        key "action": Required[Union[str, Action]]
        key "manageAgentInstallationList": Required[list[ManageAgentList]]
        action: Union[str, Action]
        manage_agent_installation_list: list[ManageAgentList]


    class azure.mgmt.dynatrace.types.ManageAgentList(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.dynatrace.types.ManagedServiceIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Required[Union[str, ManagedServiceIdentityType]]
        principal_id: str
        tenant_id: str
        type: Union[str, ManagedServiceIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentity]
        user_assigned_identities: dict[str, UserAssignedIdentity]


    class azure.mgmt.dynatrace.types.MarketplaceSaaSResourceDetailsRequest(TypedDict, total=False):
        key "tenantId": Required[str]
        tenant_id: str


    class azure.mgmt.dynatrace.types.MarketplaceSaaSResourceDetailsResponse(TypedDict, total=False):
        key "marketplaceSaaSResourceId": str
        key "marketplaceSaaSResourceName": str
        key "marketplaceSubscriptionStatus": Union[str, MarketplaceSubscriptionStatus]
        key "planId": str
        marketplace_saa_s_resource_id: str
        marketplace_saa_s_resource_name: str
        marketplace_subscription_status: Union[str, MarketplaceSubscriptionStatus]
        plan_id: str


    class azure.mgmt.dynatrace.types.MarketplaceSubscriptionIdRequest(TypedDict, total=False):
        key "marketplaceSubscriptionId": Required[str]
        marketplace_subscription_id: str


    class azure.mgmt.dynatrace.types.MetricRules(TypedDict, total=False):
        key "sendingMetrics": Union[str, SendingMetricsStatus]
        filteringTags: list[FilteringTag]
        filtering_tags: list[FilteringTag]
        sending_metrics: Union[str, SendingMetricsStatus]


    class azure.mgmt.dynatrace.types.MetricStatusRequest(TypedDict, total=False):
        monitoredResourceIds: list[str]
        monitored_resource_ids: list[str]


    class azure.mgmt.dynatrace.types.MetricsStatusResponse(TypedDict, total=False):
        azureResourceIds: list[str]
        azure_resource_ids: list[str]


    class azure.mgmt.dynatrace.types.MonitorProperties(TypedDict, total=False):
        key "dynatraceEnvironmentProperties": ForwardRef('DynatraceEnvironmentProperties', module='types')
        key "liftrResourceCategory": Union[str, LiftrResourceCategories]
        key "liftrResourcePreference": int
        key "marketplaceSaasAutoRenew": Union[str, MarketplaceSaasAutoRenew]
        key "marketplaceSubscriptionStatus": Union[str, MarketplaceSubscriptionStatus]
        key "monitoringStatus": Union[str, MonitoringStatus]
        key "planData": ForwardRef('PlanData', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        key "userInfo": ForwardRef('UserInfo', module='types')
        dynatrace_environment_properties: DynatraceEnvironmentProperties
        liftr_resource_category: Union[str, LiftrResourceCategories]
        liftr_resource_preference: int
        marketplace_saas_auto_renew: Union[str, MarketplaceSaasAutoRenew]
        marketplace_subscription_status: Union[str, MarketplaceSubscriptionStatus]
        monitoring_status: Union[str, MonitoringStatus]
        plan_data: PlanData
        provisioning_state: Union[str, ProvisioningState]
        user_info: UserInfo


    class azure.mgmt.dynatrace.types.MonitorResource(TrackedResource):
        key "id": str
        key "identity": ForwardRef('IdentityProperties', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": Required[MonitorProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: IdentityProperties
        location: str
        name: str
        properties: MonitorProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.dynatrace.types.MonitorResourceUpdate(TypedDict, total=False):
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "properties": ForwardRef('MonitorUpdateProperties', module='types')
        identity: ManagedServiceIdentity
        properties: MonitorUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.dynatrace.types.MonitorUpdateProperties(TypedDict, total=False):
        key "planData": ForwardRef('PlanData', module='types')
        plan_data: PlanData


    class azure.mgmt.dynatrace.types.MonitoredResource(TypedDict, total=False):
        key "id": str
        key "reasonForLogsStatus": str
        key "reasonForMetricsStatus": str
        key "sendingLogs": Union[str, SendingLogsStatus]
        key "sendingMetrics": Union[str, SendingMetricsStatus]
        id: str
        reason_for_logs_status: str
        reason_for_metrics_status: str
        sending_logs: Union[str, SendingLogsStatus]
        sending_metrics: Union[str, SendingMetricsStatus]


    class azure.mgmt.dynatrace.types.MonitoredSubscription(TypedDict, total=False):
        key "error": str
        key "status": Union[str, Status]
        key "subscriptionId": Required[str]
        key "tagRules": ForwardRef('MonitoringTagRulesProperties', module='types')
        error: str
        status: Union[str, Status]
        subscription_id: str
        tag_rules: MonitoringTagRulesProperties


    class azure.mgmt.dynatrace.types.MonitoredSubscriptionProperties(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('SubscriptionList', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: SubscriptionList
        system_data: SystemData
        type: str


    class azure.mgmt.dynatrace.types.MonitoringTagRulesProperties(TypedDict, total=False):
        key "logRules": ForwardRef('LogRules', module='types')
        key "metricRules": ForwardRef('MetricRules', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        log_rules: LogRules
        metric_rules: MetricRules
        provisioning_state: Union[str, ProvisioningState]


    class azure.mgmt.dynatrace.types.Operation(TypedDict, total=False):
        key "actionType": Union[str, ActionType]
        key "display": ForwardRef('OperationDisplay', module='types')
        key "isDataAction": bool
        key "name": str
        key "origin": Union[str, Origin]
        action_type: Union[str, ActionType]
        display: OperationDisplay
        is_data_action: bool
        name: str
        origin: Union[str, Origin]


    class azure.mgmt.dynatrace.types.OperationDisplay(TypedDict, total=False):
        key "description": str
        key "operation": str
        key "provider": str
        key "resource": str
        description: str
        operation: str
        provider: str
        resource: str


    class azure.mgmt.dynatrace.types.PlanData(TypedDict, total=False):
        key "billingCycle": str
        key "effectiveDate": str
        key "planDetails": str
        key "usageType": str
        billing_cycle: str
        effective_date: str
        plan_details: str
        usage_type: str


    class azure.mgmt.dynatrace.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.dynatrace.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.dynatrace.types.SSODetailsRequest(TypedDict, total=False):
        key "userPrincipal": Required[str]
        user_principal: str


    class azure.mgmt.dynatrace.types.SSODetailsResponse(TypedDict, total=False):
        key "isSsoEnabled": Union[str, SSOStatus]
        key "metadataUrl": str
        key "singleSignOnUrl": str
        aadDomains: list[str]
        aad_domains: list[str]
        adminUsers: list[str]
        admin_users: list[str]
        is_sso_enabled: Union[str, SSOStatus]
        metadata_url: str
        single_sign_on_url: str


    class azure.mgmt.dynatrace.types.SubscriptionList(TypedDict, total=False):
        key "operation": Union[str, SubscriptionListOperation]
        key "provisioningState": Union[str, ProvisioningState]
        monitoredSubscriptionList: list[MonitoredSubscription]
        monitored_subscription_list: list[MonitoredSubscription]
        operation: Union[str, SubscriptionListOperation]
        provisioning_state: Union[str, ProvisioningState]


    class azure.mgmt.dynatrace.types.SystemData(TypedDict, total=False):
        key "createdAt": str
        key "createdBy": str
        key "createdByType": Union[str, CreatedByType]
        key "lastModifiedAt": str
        key "lastModifiedBy": str
        key "lastModifiedByType": Union[str, CreatedByType]
        created_at: str
        created_by: str
        created_by_type: Union[str, CreatedByType]
        last_modified_at: str
        last_modified_by: str
        last_modified_by_type: Union[str, CreatedByType]


    class azure.mgmt.dynatrace.types.TagRule(ProxyResource):
        key "id": str
        key "name": str
        key "properties": Required[MonitoringTagRulesProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: MonitoringTagRulesProperties
        system_data: SystemData
        type: str


    class azure.mgmt.dynatrace.types.TrackedResource(Resource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.dynatrace.types.UpgradePlanRequest(TypedDict, total=False):
        key "planData": ForwardRef('PlanData', module='types')
        plan_data: PlanData


    class azure.mgmt.dynatrace.types.UserAssignedIdentity(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        client_id: str
        principal_id: str


    class azure.mgmt.dynatrace.types.UserInfo(TypedDict, total=False):
        key "country": str
        key "emailAddress": str
        key "firstName": str
        key "lastName": str
        key "phoneNumber": str
        country: str
        email_address: str
        first_name: str
        last_name: str
        phone_number: str


    class azure.mgmt.dynatrace.types.VMExtensionPayload(TypedDict, total=False):
        key "environmentId": str
        key "ingestionKey": str
        environment_id: str
        ingestion_key: str


    class azure.mgmt.dynatrace.types.VMInfo(TypedDict, total=False):
        key "autoUpdateSetting": Union[str, AutoUpdateSetting]
        key "availabilityState": Union[str, AvailabilityState]
        key "hostGroup": str
        key "hostName": str
        key "logModule": Union[str, LogModule]
        key "monitoringType": Union[str, MonitoringType]
        key "resourceId": str
        key "updateStatus": Union[str, UpdateStatus]
        key "version": str
        auto_update_setting: Union[str, AutoUpdateSetting]
        availability_state: Union[str, AvailabilityState]
        host_group: str
        host_name: str
        log_module: Union[str, LogModule]
        monitoring_type: Union[str, MonitoringType]
        resource_id: str
        update_status: Union[str, UpdateStatus]
        version: str


```