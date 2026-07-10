```py
namespace azure.mgmt.newrelicobservability

    class azure.mgmt.newrelicobservability.NewRelicObservabilityMgmtClient: implements ContextManager 
        accounts: AccountsOperations
        billing_info: BillingInfoOperations
        connected_partner_resources: ConnectedPartnerResourcesOperations
        monitored_subscriptions: MonitoredSubscriptionsOperations
        monitors: MonitorsOperations
        operations: Operations
        organizations: OrganizationsOperations
        plans: PlansOperations
        saa_s: SaaSOperations
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


namespace azure.mgmt.newrelicobservability.aio

    class azure.mgmt.newrelicobservability.aio.NewRelicObservabilityMgmtClient: implements AsyncContextManager 
        accounts: AccountsOperations
        billing_info: BillingInfoOperations
        connected_partner_resources: ConnectedPartnerResourcesOperations
        monitored_subscriptions: MonitoredSubscriptionsOperations
        monitors: MonitorsOperations
        operations: Operations
        organizations: OrganizationsOperations
        plans: PlansOperations
        saa_s: SaaSOperations
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


namespace azure.mgmt.newrelicobservability.aio.operations

    class azure.mgmt.newrelicobservability.aio.operations.AccountsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                *, 
                location: str, 
                user_email: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AccountResource]: ...


    class azure.mgmt.newrelicobservability.aio.operations.BillingInfoOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> BillingInfoResponse: ...


    class azure.mgmt.newrelicobservability.aio.operations.ConnectedPartnerResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[ConnectedPartnerResourcesListFormat]: ...


    class azure.mgmt.newrelicobservability.aio.operations.MonitoredSubscriptionsOperations:

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
                configuration_name: Union[str, ConfigurationName], 
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
                configuration_name: Union[str, ConfigurationName], 
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
                configuration_name: Union[str, ConfigurationName], 
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
                configuration_name: Union[str, ConfigurationName], 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                configuration_name: Union[str, ConfigurationName], 
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
                configuration_name: Union[str, ConfigurationName], 
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
                configuration_name: Union[str, ConfigurationName], 
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
                configuration_name: Union[str, ConfigurationName], 
                **kwargs: Any
            ) -> MonitoredSubscriptionProperties: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[MonitoredSubscriptionProperties]: ...


    class azure.mgmt.newrelicobservability.aio.operations.MonitorsOperations:

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
                resource: NewRelicMonitorResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NewRelicMonitorResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                resource: NewRelicMonitorResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NewRelicMonitorResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NewRelicMonitorResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                *, 
                user_email: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_link_saa_s(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: SaaSData, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NewRelicMonitorResource]: ...

        @overload
        async def begin_link_saa_s(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: SaaSData, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NewRelicMonitorResource]: ...

        @overload
        async def begin_link_saa_s(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NewRelicMonitorResource]: ...

        @overload
        async def begin_resubscribe(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[ResubscribeProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NewRelicMonitorResource]: ...

        @overload
        async def begin_resubscribe(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[ResubscribeProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NewRelicMonitorResource]: ...

        @overload
        async def begin_resubscribe(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NewRelicMonitorResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                properties: NewRelicMonitorResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NewRelicMonitorResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                properties: NewRelicMonitorResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NewRelicMonitorResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NewRelicMonitorResource]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> NewRelicMonitorResource: ...

        @overload
        async def get_metric_rules(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: MetricsRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MetricRules: ...

        @overload
        async def get_metric_rules(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: MetricsRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MetricRules: ...

        @overload
        async def get_metric_rules(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MetricRules: ...

        @overload
        async def get_metric_status(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: MetricsStatusRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MetricsStatusResponse: ...

        @overload
        async def get_metric_status(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: MetricsStatusRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MetricsStatusResponse: ...

        @overload
        async def get_metric_status(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MetricsStatusResponse: ...

        @distributed_trace_async
        async def latest_linked_saa_s(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> LatestLinkedSaaSResponse: ...

        @overload
        def list_app_services(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: AppServicesGetRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncItemPaged[AppServiceInfo]: ...

        @overload
        def list_app_services(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: AppServicesGetRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncItemPaged[AppServiceInfo]: ...

        @overload
        def list_app_services(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncItemPaged[AppServiceInfo]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[NewRelicMonitorResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[NewRelicMonitorResource]: ...

        @overload
        def list_hosts(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: HostsGetRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncItemPaged[VMInfo]: ...

        @overload
        def list_hosts(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: HostsGetRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncItemPaged[VMInfo]: ...

        @overload
        def list_hosts(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncItemPaged[VMInfo]: ...

        @distributed_trace
        def list_linked_resources(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[LinkedResource]: ...

        @distributed_trace
        def list_monitored_resources(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[MonitoredResource]: ...

        @distributed_trace_async
        async def refresh_ingestion_key(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def switch_billing(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: SwitchBillingRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Optional[NewRelicMonitorResource]: ...

        @overload
        async def switch_billing(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: SwitchBillingRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Optional[NewRelicMonitorResource]: ...

        @overload
        async def switch_billing(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Optional[NewRelicMonitorResource]: ...

        @distributed_trace_async
        async def vm_host_payload(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> VMExtensionPayload: ...


    class azure.mgmt.newrelicobservability.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.newrelicobservability.aio.operations.OrganizationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                *, 
                location: str, 
                user_email: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[OrganizationResource]: ...


    class azure.mgmt.newrelicobservability.aio.operations.PlansOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                *, 
                account_id: Optional[str] = ..., 
                organization_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[PlanDataResource]: ...


    class azure.mgmt.newrelicobservability.aio.operations.SaaSOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def activate_resource(
                self, 
                request: ActivateSaaSParameterRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SaaSResourceDetailsResponse: ...

        @overload
        async def activate_resource(
                self, 
                request: ActivateSaaSParameterRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SaaSResourceDetailsResponse: ...

        @overload
        async def activate_resource(
                self, 
                request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SaaSResourceDetailsResponse: ...


    class azure.mgmt.newrelicobservability.aio.operations.TagRulesOperations:

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
        def list_by_new_relic_monitor_resource(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[TagRule]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                rule_set_name: str, 
                properties: TagRuleUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TagRule: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                rule_set_name: str, 
                properties: TagRuleUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TagRule: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                rule_set_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TagRule: ...


namespace azure.mgmt.newrelicobservability.models

    class azure.mgmt.newrelicobservability.models.AccountCreationSource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LIFTR = "LIFTR"
        NEWRELIC = "NEWRELIC"


    class azure.mgmt.newrelicobservability.models.AccountInfo(_Model):
        account_id: Optional[str]
        ingestion_key: Optional[str]
        region: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                account_id: Optional[str] = ..., 
                ingestion_key: Optional[str] = ..., 
                region: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.newrelicobservability.models.AccountProperties(_Model):
        account_id: Optional[str]
        account_name: Optional[str]
        organization_id: Optional[str]
        region: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                account_id: Optional[str] = ..., 
                account_name: Optional[str] = ..., 
                organization_id: Optional[str] = ..., 
                region: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.newrelicobservability.models.AccountResource(ProxyResource):
        id: str
        name: str
        properties: Optional[AccountProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AccountProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.newrelicobservability.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.newrelicobservability.models.ActivateSaaSParameterRequest(_Model):
        publisher_id: str
        saas_guid: str

        @overload
        def __init__(
                self, 
                *, 
                publisher_id: str, 
                saas_guid: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.newrelicobservability.models.AppServiceInfo(_Model):
        agent_status: Optional[str]
        agent_version: Optional[str]
        azure_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                agent_status: Optional[str] = ..., 
                agent_version: Optional[str] = ..., 
                azure_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.newrelicobservability.models.AppServicesGetRequest(_Model):
        azure_resource_ids: Optional[list[str]]
        user_email: str

        @overload
        def __init__(
                self, 
                *, 
                azure_resource_ids: Optional[list[str]] = ..., 
                user_email: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.newrelicobservability.models.BillingInfoResponse(_Model):
        marketplace_saas_info: Optional[MarketplaceSaaSInfo]
        partner_billing_entity: Optional[PartnerBillingEntity]

        @overload
        def __init__(
                self, 
                *, 
                marketplace_saas_info: Optional[MarketplaceSaaSInfo] = ..., 
                partner_billing_entity: Optional[PartnerBillingEntity] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.newrelicobservability.models.BillingSource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE = "AZURE"
        NEWRELIC = "NEWRELIC"


    class azure.mgmt.newrelicobservability.models.ConfigurationName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "default"


    class azure.mgmt.newrelicobservability.models.ConnectedPartnerResourceProperties(_Model):
        account_id: Optional[str]
        account_name: Optional[str]
        azure_resource_id: Optional[str]
        location: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                account_id: Optional[str] = ..., 
                account_name: Optional[str] = ..., 
                azure_resource_id: Optional[str] = ..., 
                location: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.newrelicobservability.models.ConnectedPartnerResourcesListFormat(_Model):
        properties: Optional[ConnectedPartnerResourceProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ConnectedPartnerResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.newrelicobservability.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.newrelicobservability.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.newrelicobservability.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.newrelicobservability.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.newrelicobservability.models.FilteringTag(_Model):
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


    class azure.mgmt.newrelicobservability.models.HostsGetRequest(_Model):
        user_email: str
        vm_ids: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                user_email: str, 
                vm_ids: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.newrelicobservability.models.LatestLinkedSaaSResponse(_Model):
        is_hidden_saa_s: Optional[bool]
        saa_s_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                is_hidden_saa_s: Optional[bool] = ..., 
                saa_s_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.newrelicobservability.models.LiftrResourceCategories(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MONITOR_LOGS = "MonitorLogs"
        UNKNOWN = "Unknown"


    class azure.mgmt.newrelicobservability.models.LinkedResource(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.newrelicobservability.models.LogRules(_Model):
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


    class azure.mgmt.newrelicobservability.models.ManagedServiceIdentity(_Model):
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


    class azure.mgmt.newrelicobservability.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.newrelicobservability.models.MarketplaceSaaSInfo(_Model):
        billed_azure_subscription_id: Optional[str]
        marketplace_resource_id: Optional[str]
        marketplace_status: Optional[str]
        marketplace_subscription_id: Optional[str]
        marketplace_subscription_name: Optional[str]
        offer_id: Optional[str]
        publisher_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                billed_azure_subscription_id: Optional[str] = ..., 
                marketplace_resource_id: Optional[str] = ..., 
                marketplace_status: Optional[str] = ..., 
                marketplace_subscription_id: Optional[str] = ..., 
                marketplace_subscription_name: Optional[str] = ..., 
                offer_id: Optional[str] = ..., 
                publisher_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.newrelicobservability.models.MarketplaceSubscriptionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        SUSPENDED = "Suspended"


    class azure.mgmt.newrelicobservability.models.MetricRules(_Model):
        filtering_tags: Optional[list[FilteringTag]]
        send_metrics: Optional[Union[str, SendMetricsStatus]]
        user_email: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                filtering_tags: Optional[list[FilteringTag]] = ..., 
                send_metrics: Optional[Union[str, SendMetricsStatus]] = ..., 
                user_email: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.newrelicobservability.models.MetricsRequest(_Model):
        user_email: str

        @overload
        def __init__(
                self, 
                *, 
                user_email: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.newrelicobservability.models.MetricsStatusRequest(_Model):
        azure_resource_ids: Optional[list[str]]
        user_email: str

        @overload
        def __init__(
                self, 
                *, 
                azure_resource_ids: Optional[list[str]] = ..., 
                user_email: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.newrelicobservability.models.MetricsStatusResponse(_Model):
        azure_resource_ids: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                azure_resource_ids: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.newrelicobservability.models.MonitorProperties(_Model):
        account_creation_source: Optional[Union[str, AccountCreationSource]]
        liftr_resource_category: Optional[Union[str, LiftrResourceCategories]]
        liftr_resource_preference: Optional[int]
        marketplace_subscription_id: Optional[str]
        marketplace_subscription_status: Optional[Union[str, MarketplaceSubscriptionStatus]]
        monitoring_status: Optional[Union[str, MonitoringStatus]]
        new_relic_account_properties: Optional[NewRelicAccountProperties]
        org_creation_source: Optional[Union[str, OrgCreationSource]]
        plan_data: Optional[PlanData]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        saa_s_azure_subscription_status: Optional[str]
        saa_s_data: Optional[SaaSData]
        subscription_state: Optional[str]
        user_info: Optional[UserInfo]

        @overload
        def __init__(
                self, 
                *, 
                account_creation_source: Optional[Union[str, AccountCreationSource]] = ..., 
                new_relic_account_properties: Optional[NewRelicAccountProperties] = ..., 
                org_creation_source: Optional[Union[str, OrgCreationSource]] = ..., 
                plan_data: Optional[PlanData] = ..., 
                saa_s_azure_subscription_status: Optional[str] = ..., 
                saa_s_data: Optional[SaaSData] = ..., 
                subscription_state: Optional[str] = ..., 
                user_info: Optional[UserInfo] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.newrelicobservability.models.MonitoredResource(_Model):
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


    class azure.mgmt.newrelicobservability.models.MonitoredSubscription(_Model):
        error: Optional[str]
        status: Optional[Union[str, Status]]
        subscription_id: Optional[str]
        tag_rules: Optional[MonitoringTagRulesProperties]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[str] = ..., 
                status: Optional[Union[str, Status]] = ..., 
                subscription_id: Optional[str] = ..., 
                tag_rules: Optional[MonitoringTagRulesProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.newrelicobservability.models.MonitoredSubscriptionProperties(ProxyResource):
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


    class azure.mgmt.newrelicobservability.models.MonitoringStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.newrelicobservability.models.MonitoringTagRulesProperties(_Model):
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


    class azure.mgmt.newrelicobservability.models.NewRelicAccountProperties(_Model):
        account_info: Optional[AccountInfo]
        organization_info: Optional[OrganizationInfo]
        single_sign_on_properties: Optional[NewRelicSingleSignOnProperties]
        user_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                account_info: Optional[AccountInfo] = ..., 
                organization_info: Optional[OrganizationInfo] = ..., 
                single_sign_on_properties: Optional[NewRelicSingleSignOnProperties] = ..., 
                user_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.newrelicobservability.models.NewRelicMonitorResource(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
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
                identity: Optional[ManagedServiceIdentity] = ..., 
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


    class azure.mgmt.newrelicobservability.models.NewRelicMonitorResourceUpdate(_Model):
        identity: Optional[ManagedServiceIdentity]
        properties: Optional[NewRelicMonitorResourceUpdateProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                properties: Optional[NewRelicMonitorResourceUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.newrelicobservability.models.NewRelicMonitorResourceUpdateProperties(_Model):
        account_creation_source: Optional[Union[str, AccountCreationSource]]
        new_relic_account_properties: Optional[NewRelicAccountProperties]
        org_creation_source: Optional[Union[str, OrgCreationSource]]
        plan_data: Optional[PlanData]
        saa_s_data: Optional[SaaSData]
        user_info: Optional[UserInfo]

        @overload
        def __init__(
                self, 
                *, 
                account_creation_source: Optional[Union[str, AccountCreationSource]] = ..., 
                new_relic_account_properties: Optional[NewRelicAccountProperties] = ..., 
                org_creation_source: Optional[Union[str, OrgCreationSource]] = ..., 
                plan_data: Optional[PlanData] = ..., 
                saa_s_data: Optional[SaaSData] = ..., 
                user_info: Optional[UserInfo] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.newrelicobservability.models.NewRelicSingleSignOnProperties(_Model):
        enterprise_app_id: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        single_sign_on_state: Optional[Union[str, SingleSignOnStates]]
        single_sign_on_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                enterprise_app_id: Optional[str] = ..., 
                provisioning_state: Optional[Union[str, ProvisioningState]] = ..., 
                single_sign_on_state: Optional[Union[str, SingleSignOnStates]] = ..., 
                single_sign_on_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.newrelicobservability.models.Operation(_Model):
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


    class azure.mgmt.newrelicobservability.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.newrelicobservability.models.OrgCreationSource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LIFTR = "LIFTR"
        NEWRELIC = "NEWRELIC"


    class azure.mgmt.newrelicobservability.models.OrganizationInfo(_Model):
        organization_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                organization_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.newrelicobservability.models.OrganizationProperties(_Model):
        billing_source: Optional[Union[str, BillingSource]]
        organization_id: Optional[str]
        organization_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                billing_source: Optional[Union[str, BillingSource]] = ..., 
                organization_id: Optional[str] = ..., 
                organization_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.newrelicobservability.models.OrganizationResource(ProxyResource):
        id: str
        name: str
        properties: Optional[OrganizationProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[OrganizationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.newrelicobservability.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.newrelicobservability.models.PartnerBillingEntity(_Model):
        organization_id: Optional[str]
        organization_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                organization_id: Optional[str] = ..., 
                organization_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.newrelicobservability.models.PatchOperation(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        ADD_BEGIN = "AddBegin"
        ADD_COMPLETE = "AddComplete"
        DELETE_BEGIN = "DeleteBegin"
        DELETE_COMPLETE = "DeleteComplete"


    class azure.mgmt.newrelicobservability.models.PlanData(_Model):
        billing_cycle: Optional[str]
        effective_date: Optional[datetime]
        plan_details: Optional[str]
        usage_type: Optional[Union[str, UsageType]]

        @overload
        def __init__(
                self, 
                *, 
                billing_cycle: Optional[str] = ..., 
                effective_date: Optional[datetime] = ..., 
                plan_details: Optional[str] = ..., 
                usage_type: Optional[Union[str, UsageType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.newrelicobservability.models.PlanDataProperties(_Model):
        account_creation_source: Optional[Union[str, AccountCreationSource]]
        org_creation_source: Optional[Union[str, OrgCreationSource]]
        plan_data: Optional[PlanData]

        @overload
        def __init__(
                self, 
                *, 
                account_creation_source: Optional[Union[str, AccountCreationSource]] = ..., 
                org_creation_source: Optional[Union[str, OrgCreationSource]] = ..., 
                plan_data: Optional[PlanData] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.newrelicobservability.models.PlanDataResource(ProxyResource):
        id: str
        name: str
        properties: Optional[PlanDataProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PlanDataProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.newrelicobservability.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETED = "Deleted"
        DELETING = "Deleting"
        FAILED = "Failed"
        NOT_SPECIFIED = "NotSpecified"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.newrelicobservability.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.newrelicobservability.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.newrelicobservability.models.ResubscribeProperties(_Model):
        offer_id: Optional[str]
        organization_id: Optional[str]
        plan_id: Optional[str]
        publisher_id: Optional[str]
        resource_group: Optional[str]
        subscription_id: Optional[str]
        term_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                offer_id: Optional[str] = ..., 
                organization_id: Optional[str] = ..., 
                plan_id: Optional[str] = ..., 
                publisher_id: Optional[str] = ..., 
                resource_group: Optional[str] = ..., 
                subscription_id: Optional[str] = ..., 
                term_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.newrelicobservability.models.SaaSData(_Model):
        saa_s_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                saa_s_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.newrelicobservability.models.SaaSResourceDetailsResponse(ProxyResource):
        id: str
        name: str
        saas_id: Optional[str]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                saas_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.newrelicobservability.models.SendAadLogsStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.newrelicobservability.models.SendActivityLogsStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.newrelicobservability.models.SendMetricsStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.newrelicobservability.models.SendSubscriptionLogsStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.newrelicobservability.models.SendingLogsStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.newrelicobservability.models.SendingMetricsStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.newrelicobservability.models.SingleSignOnStates(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLE = "Disable"
        ENABLE = "Enable"
        EXISTING = "Existing"
        INITIAL = "Initial"


    class azure.mgmt.newrelicobservability.models.Status(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        DELETING = "Deleting"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"


    class azure.mgmt.newrelicobservability.models.SubscriptionList(_Model):
        monitored_subscription_list: Optional[list[MonitoredSubscription]]
        patch_operation: Optional[Union[str, PatchOperation]]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                monitored_subscription_list: Optional[list[MonitoredSubscription]] = ..., 
                patch_operation: Optional[Union[str, PatchOperation]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.newrelicobservability.models.SwitchBillingRequest(_Model):
        azure_resource_id: Optional[str]
        organization_id: Optional[str]
        plan_data: Optional[PlanData]
        user_email: str

        @overload
        def __init__(
                self, 
                *, 
                azure_resource_id: Optional[str] = ..., 
                organization_id: Optional[str] = ..., 
                plan_data: Optional[PlanData] = ..., 
                user_email: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.newrelicobservability.models.SystemData(_Model):
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


    class azure.mgmt.newrelicobservability.models.TagAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXCLUDE = "Exclude"
        INCLUDE = "Include"


    class azure.mgmt.newrelicobservability.models.TagRule(ProxyResource):
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


    class azure.mgmt.newrelicobservability.models.TagRuleUpdate(_Model):
        properties: Optional[TagRuleUpdateProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[TagRuleUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.newrelicobservability.models.TagRuleUpdateProperties(_Model):
        log_rules: Optional[LogRules]
        metric_rules: Optional[MetricRules]

        @overload
        def __init__(
                self, 
                *, 
                log_rules: Optional[LogRules] = ..., 
                metric_rules: Optional[MetricRules] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.newrelicobservability.models.TrackedResource(Resource):
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


    class azure.mgmt.newrelicobservability.models.UsageType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMMITTED = "COMMITTED"
        PAYG = "PAYG"


    class azure.mgmt.newrelicobservability.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.newrelicobservability.models.UserInfo(_Model):
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


    class azure.mgmt.newrelicobservability.models.VMExtensionPayload(_Model):
        ingestion_key: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                ingestion_key: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.newrelicobservability.models.VMInfo(_Model):
        agent_status: Optional[str]
        agent_version: Optional[str]
        vm_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                agent_status: Optional[str] = ..., 
                agent_version: Optional[str] = ..., 
                vm_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.newrelicobservability.operations

    class azure.mgmt.newrelicobservability.operations.AccountsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                *, 
                location: str, 
                user_email: str, 
                **kwargs: Any
            ) -> ItemPaged[AccountResource]: ...


    class azure.mgmt.newrelicobservability.operations.BillingInfoOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> BillingInfoResponse: ...


    class azure.mgmt.newrelicobservability.operations.ConnectedPartnerResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[str] = None, 
                **kwargs: Any
            ) -> ItemPaged[ConnectedPartnerResourcesListFormat]: ...


    class azure.mgmt.newrelicobservability.operations.MonitoredSubscriptionsOperations:

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
                configuration_name: Union[str, ConfigurationName], 
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
                configuration_name: Union[str, ConfigurationName], 
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
                configuration_name: Union[str, ConfigurationName], 
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
                configuration_name: Union[str, ConfigurationName], 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                configuration_name: Union[str, ConfigurationName], 
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
                configuration_name: Union[str, ConfigurationName], 
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
                configuration_name: Union[str, ConfigurationName], 
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
                configuration_name: Union[str, ConfigurationName], 
                **kwargs: Any
            ) -> MonitoredSubscriptionProperties: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> ItemPaged[MonitoredSubscriptionProperties]: ...


    class azure.mgmt.newrelicobservability.operations.MonitorsOperations:

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
                resource: NewRelicMonitorResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NewRelicMonitorResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                resource: NewRelicMonitorResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NewRelicMonitorResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NewRelicMonitorResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                *, 
                user_email: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_link_saa_s(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: SaaSData, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NewRelicMonitorResource]: ...

        @overload
        def begin_link_saa_s(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: SaaSData, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NewRelicMonitorResource]: ...

        @overload
        def begin_link_saa_s(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NewRelicMonitorResource]: ...

        @overload
        def begin_resubscribe(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[ResubscribeProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NewRelicMonitorResource]: ...

        @overload
        def begin_resubscribe(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[ResubscribeProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NewRelicMonitorResource]: ...

        @overload
        def begin_resubscribe(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NewRelicMonitorResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                properties: NewRelicMonitorResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NewRelicMonitorResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                properties: NewRelicMonitorResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NewRelicMonitorResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NewRelicMonitorResource]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> NewRelicMonitorResource: ...

        @overload
        def get_metric_rules(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: MetricsRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MetricRules: ...

        @overload
        def get_metric_rules(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: MetricsRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MetricRules: ...

        @overload
        def get_metric_rules(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MetricRules: ...

        @overload
        def get_metric_status(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: MetricsStatusRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MetricsStatusResponse: ...

        @overload
        def get_metric_status(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: MetricsStatusRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MetricsStatusResponse: ...

        @overload
        def get_metric_status(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MetricsStatusResponse: ...

        @distributed_trace
        def latest_linked_saa_s(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> LatestLinkedSaaSResponse: ...

        @overload
        def list_app_services(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: AppServicesGetRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ItemPaged[AppServiceInfo]: ...

        @overload
        def list_app_services(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: AppServicesGetRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ItemPaged[AppServiceInfo]: ...

        @overload
        def list_app_services(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ItemPaged[AppServiceInfo]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[NewRelicMonitorResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[NewRelicMonitorResource]: ...

        @overload
        def list_hosts(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: HostsGetRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ItemPaged[VMInfo]: ...

        @overload
        def list_hosts(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: HostsGetRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ItemPaged[VMInfo]: ...

        @overload
        def list_hosts(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ItemPaged[VMInfo]: ...

        @distributed_trace
        def list_linked_resources(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> ItemPaged[LinkedResource]: ...

        @distributed_trace
        def list_monitored_resources(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> ItemPaged[MonitoredResource]: ...

        @distributed_trace
        def refresh_ingestion_key(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        def switch_billing(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: SwitchBillingRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Optional[NewRelicMonitorResource]: ...

        @overload
        def switch_billing(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: SwitchBillingRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Optional[NewRelicMonitorResource]: ...

        @overload
        def switch_billing(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Optional[NewRelicMonitorResource]: ...

        @distributed_trace
        def vm_host_payload(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> VMExtensionPayload: ...


    class azure.mgmt.newrelicobservability.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.newrelicobservability.operations.OrganizationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                *, 
                location: str, 
                user_email: str, 
                **kwargs: Any
            ) -> ItemPaged[OrganizationResource]: ...


    class azure.mgmt.newrelicobservability.operations.PlansOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                *, 
                account_id: Optional[str] = ..., 
                organization_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[PlanDataResource]: ...


    class azure.mgmt.newrelicobservability.operations.SaaSOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def activate_resource(
                self, 
                request: ActivateSaaSParameterRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SaaSResourceDetailsResponse: ...

        @overload
        def activate_resource(
                self, 
                request: ActivateSaaSParameterRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SaaSResourceDetailsResponse: ...

        @overload
        def activate_resource(
                self, 
                request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SaaSResourceDetailsResponse: ...


    class azure.mgmt.newrelicobservability.operations.TagRulesOperations:

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
        def list_by_new_relic_monitor_resource(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> ItemPaged[TagRule]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                rule_set_name: str, 
                properties: TagRuleUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TagRule: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                rule_set_name: str, 
                properties: TagRuleUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TagRule: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                rule_set_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TagRule: ...


namespace azure.mgmt.newrelicobservability.types

    class azure.mgmt.newrelicobservability.types.AccountInfo(TypedDict, total=False):
        key "accountId": str
        key "ingestionKey": str
        key "region": str
        account_id: str
        ingestion_key: str
        region: str


    class azure.mgmt.newrelicobservability.types.AccountProperties(TypedDict, total=False):
        key "accountId": str
        key "accountName": str
        key "organizationId": str
        key "region": str
        account_id: str
        account_name: str
        organization_id: str
        region: str


    class azure.mgmt.newrelicobservability.types.AccountResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('AccountProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: AccountProperties
        system_data: SystemData
        type: str


    class azure.mgmt.newrelicobservability.types.ActivateSaaSParameterRequest(TypedDict, total=False):
        key "publisherId": Required[str]
        key "saasGuid": Required[str]
        publisher_id: str
        saas_guid: str


    class azure.mgmt.newrelicobservability.types.AppServiceInfo(TypedDict, total=False):
        key "agentStatus": str
        key "agentVersion": str
        key "azureResourceId": str
        agent_status: str
        agent_version: str
        azure_resource_id: str


    class azure.mgmt.newrelicobservability.types.AppServicesGetRequest(TypedDict, total=False):
        key "userEmail": Required[str]
        azureResourceIds: list[str]
        azure_resource_ids: list[str]
        user_email: str


    class azure.mgmt.newrelicobservability.types.BillingInfoResponse(TypedDict, total=False):
        key "marketplaceSaasInfo": ForwardRef('MarketplaceSaaSInfo', module='types')
        key "partnerBillingEntity": ForwardRef('PartnerBillingEntity', module='types')
        marketplace_saas_info: MarketplaceSaaSInfo
        partner_billing_entity: PartnerBillingEntity


    class azure.mgmt.newrelicobservability.types.ConnectedPartnerResourceProperties(TypedDict, total=False):
        key "accountId": str
        key "accountName": str
        key "azureResourceId": str
        key "location": str
        account_id: str
        account_name: str
        azure_resource_id: str
        location: str


    class azure.mgmt.newrelicobservability.types.ConnectedPartnerResourcesListFormat(TypedDict, total=False):
        key "properties": ForwardRef('ConnectedPartnerResourceProperties', module='types')
        properties: ConnectedPartnerResourceProperties


    class azure.mgmt.newrelicobservability.types.ErrorAdditionalInfo(TypedDict, total=False):
        key "info": Any
        key "type": str
        info: Any
        type: str


    class azure.mgmt.newrelicobservability.types.ErrorDetail(TypedDict, total=False):
        key "code": str
        key "message": str
        key "target": str
        additionalInfo: list[ErrorAdditionalInfo]
        additional_info: list[ErrorAdditionalInfo]
        code: str
        details: list[ErrorDetail]
        message: str
        target: str


    class azure.mgmt.newrelicobservability.types.ErrorResponse(TypedDict, total=False):
        key "error": ForwardRef('ErrorDetail', module='types')
        error: ErrorDetail


    class azure.mgmt.newrelicobservability.types.FilteringTag(TypedDict, total=False):
        key "action": Union[str, TagAction]
        key "name": str
        key "value": str
        action: Union[str, TagAction]
        name: str
        value: str


    class azure.mgmt.newrelicobservability.types.HostsGetRequest(TypedDict, total=False):
        key "userEmail": Required[str]
        user_email: str
        vmIds: list[str]
        vm_ids: list[str]


    class azure.mgmt.newrelicobservability.types.LatestLinkedSaaSResponse(TypedDict, total=False):
        key "isHiddenSaaS": bool
        key "saaSResourceId": str
        is_hidden_saa_s: bool
        saa_s_resource_id: str


    class azure.mgmt.newrelicobservability.types.LinkedResource(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.newrelicobservability.types.LogRules(TypedDict, total=False):
        key "sendAadLogs": Union[str, SendAadLogsStatus]
        key "sendActivityLogs": Union[str, SendActivityLogsStatus]
        key "sendSubscriptionLogs": Union[str, SendSubscriptionLogsStatus]
        filteringTags: list[FilteringTag]
        filtering_tags: list[FilteringTag]
        send_aad_logs: Union[str, SendAadLogsStatus]
        send_activity_logs: Union[str, SendActivityLogsStatus]
        send_subscription_logs: Union[str, SendSubscriptionLogsStatus]


    class azure.mgmt.newrelicobservability.types.ManagedServiceIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Required[Union[str, ManagedServiceIdentityType]]
        principal_id: str
        tenant_id: str
        type: Union[str, ManagedServiceIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentity]
        user_assigned_identities: dict[str, UserAssignedIdentity]


    class azure.mgmt.newrelicobservability.types.MarketplaceSaaSInfo(TypedDict, total=False):
        key "billedAzureSubscriptionId": str
        key "marketplaceResourceId": str
        key "marketplaceStatus": str
        key "marketplaceSubscriptionId": str
        key "marketplaceSubscriptionName": str
        key "offerId": str
        key "publisherId": str
        billed_azure_subscription_id: str
        marketplace_resource_id: str
        marketplace_status: str
        marketplace_subscription_id: str
        marketplace_subscription_name: str
        offer_id: str
        publisher_id: str


    class azure.mgmt.newrelicobservability.types.MetricRules(TypedDict, total=False):
        key "sendMetrics": Union[str, SendMetricsStatus]
        key "userEmail": str
        filteringTags: list[FilteringTag]
        filtering_tags: list[FilteringTag]
        send_metrics: Union[str, SendMetricsStatus]
        user_email: str


    class azure.mgmt.newrelicobservability.types.MetricsRequest(TypedDict, total=False):
        key "userEmail": Required[str]
        user_email: str


    class azure.mgmt.newrelicobservability.types.MetricsStatusRequest(TypedDict, total=False):
        key "userEmail": Required[str]
        azureResourceIds: list[str]
        azure_resource_ids: list[str]
        user_email: str


    class azure.mgmt.newrelicobservability.types.MetricsStatusResponse(TypedDict, total=False):
        azureResourceIds: list[str]
        azure_resource_ids: list[str]


    class azure.mgmt.newrelicobservability.types.MonitorProperties(TypedDict, total=False):
        key "accountCreationSource": Union[str, AccountCreationSource]
        key "liftrResourceCategory": Union[str, LiftrResourceCategories]
        key "liftrResourcePreference": int
        key "marketplaceSubscriptionId": str
        key "marketplaceSubscriptionStatus": Union[str, MarketplaceSubscriptionStatus]
        key "monitoringStatus": Union[str, MonitoringStatus]
        key "newRelicAccountProperties": ForwardRef('NewRelicAccountProperties', module='types')
        key "orgCreationSource": Union[str, OrgCreationSource]
        key "planData": ForwardRef('PlanData', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        key "saaSAzureSubscriptionStatus": str
        key "saaSData": ForwardRef('SaaSData', module='types')
        key "subscriptionState": str
        key "userInfo": ForwardRef('UserInfo', module='types')
        account_creation_source: Union[str, AccountCreationSource]
        liftr_resource_category: Union[str, LiftrResourceCategories]
        liftr_resource_preference: int
        marketplace_subscription_id: str
        marketplace_subscription_status: Union[str, MarketplaceSubscriptionStatus]
        monitoring_status: Union[str, MonitoringStatus]
        new_relic_account_properties: NewRelicAccountProperties
        org_creation_source: Union[str, OrgCreationSource]
        plan_data: PlanData
        provisioning_state: Union[str, ProvisioningState]
        saa_s_azure_subscription_status: str
        saa_s_data: SaaSData
        subscription_state: str
        user_info: UserInfo


    class azure.mgmt.newrelicobservability.types.MonitoredResource(TypedDict, total=False):
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


    class azure.mgmt.newrelicobservability.types.MonitoredSubscription(TypedDict, total=False):
        key "error": str
        key "status": Union[str, Status]
        key "subscriptionId": str
        key "tagRules": ForwardRef('MonitoringTagRulesProperties', module='types')
        error: str
        status: Union[str, Status]
        subscription_id: str
        tag_rules: MonitoringTagRulesProperties


    class azure.mgmt.newrelicobservability.types.MonitoredSubscriptionProperties(ProxyResource):
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


    class azure.mgmt.newrelicobservability.types.MonitoringTagRulesProperties(TypedDict, total=False):
        key "logRules": ForwardRef('LogRules', module='types')
        key "metricRules": ForwardRef('MetricRules', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        log_rules: LogRules
        metric_rules: MetricRules
        provisioning_state: Union[str, ProvisioningState]


    class azure.mgmt.newrelicobservability.types.NewRelicAccountProperties(TypedDict, total=False):
        key "accountInfo": ForwardRef('AccountInfo', module='types')
        key "organizationInfo": ForwardRef('OrganizationInfo', module='types')
        key "singleSignOnProperties": ForwardRef('NewRelicSingleSignOnProperties', module='types')
        key "userId": str
        account_info: AccountInfo
        organization_info: OrganizationInfo
        single_sign_on_properties: NewRelicSingleSignOnProperties
        user_id: str


    class azure.mgmt.newrelicobservability.types.NewRelicMonitorResource(TrackedResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": Required[MonitorProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: MonitorProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.newrelicobservability.types.NewRelicMonitorResourceUpdate(TypedDict, total=False):
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "properties": ForwardRef('NewRelicMonitorResourceUpdateProperties', module='types')
        identity: ManagedServiceIdentity
        properties: NewRelicMonitorResourceUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.newrelicobservability.types.NewRelicMonitorResourceUpdateProperties(TypedDict, total=False):
        key "accountCreationSource": Union[str, AccountCreationSource]
        key "newRelicAccountProperties": ForwardRef('NewRelicAccountProperties', module='types')
        key "orgCreationSource": Union[str, OrgCreationSource]
        key "planData": ForwardRef('PlanData', module='types')
        key "saaSData": ForwardRef('SaaSData', module='types')
        key "userInfo": ForwardRef('UserInfo', module='types')
        account_creation_source: Union[str, AccountCreationSource]
        new_relic_account_properties: NewRelicAccountProperties
        org_creation_source: Union[str, OrgCreationSource]
        plan_data: PlanData
        saa_s_data: SaaSData
        user_info: UserInfo


    class azure.mgmt.newrelicobservability.types.NewRelicSingleSignOnProperties(TypedDict, total=False):
        key "enterpriseAppId": str
        key "provisioningState": Union[str, ProvisioningState]
        key "singleSignOnState": Union[str, SingleSignOnStates]
        key "singleSignOnUrl": str
        enterprise_app_id: str
        provisioning_state: Union[str, ProvisioningState]
        single_sign_on_state: Union[str, SingleSignOnStates]
        single_sign_on_url: str


    class azure.mgmt.newrelicobservability.types.Operation(TypedDict, total=False):
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


    class azure.mgmt.newrelicobservability.types.OperationDisplay(TypedDict, total=False):
        key "description": str
        key "operation": str
        key "provider": str
        key "resource": str
        description: str
        operation: str
        provider: str
        resource: str


    class azure.mgmt.newrelicobservability.types.OrganizationInfo(TypedDict, total=False):
        key "organizationId": str
        organization_id: str


    class azure.mgmt.newrelicobservability.types.OrganizationProperties(TypedDict, total=False):
        key "billingSource": Union[str, BillingSource]
        key "organizationId": str
        key "organizationName": str
        billing_source: Union[str, BillingSource]
        organization_id: str
        organization_name: str


    class azure.mgmt.newrelicobservability.types.OrganizationResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('OrganizationProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: OrganizationProperties
        system_data: SystemData
        type: str


    class azure.mgmt.newrelicobservability.types.PartnerBillingEntity(TypedDict, total=False):
        key "organizationId": str
        key "organizationName": str
        organization_id: str
        organization_name: str


    class azure.mgmt.newrelicobservability.types.PlanData(TypedDict, total=False):
        key "billingCycle": str
        key "effectiveDate": str
        key "planDetails": str
        key "usageType": Union[str, UsageType]
        billing_cycle: str
        effective_date: str
        plan_details: str
        usage_type: Union[str, UsageType]


    class azure.mgmt.newrelicobservability.types.PlanDataProperties(TypedDict, total=False):
        key "accountCreationSource": Union[str, AccountCreationSource]
        key "orgCreationSource": Union[str, OrgCreationSource]
        key "planData": ForwardRef('PlanData', module='types')
        account_creation_source: Union[str, AccountCreationSource]
        org_creation_source: Union[str, OrgCreationSource]
        plan_data: PlanData


    class azure.mgmt.newrelicobservability.types.PlanDataResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('PlanDataProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: PlanDataProperties
        system_data: SystemData
        type: str


    class azure.mgmt.newrelicobservability.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.newrelicobservability.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.newrelicobservability.types.ResubscribeProperties(TypedDict, total=False):
        key "offerId": str
        key "organizationId": str
        key "planId": str
        key "publisherId": str
        key "resourceGroup": str
        key "subscriptionId": str
        key "termId": str
        offer_id: str
        organization_id: str
        plan_id: str
        publisher_id: str
        resource_group: str
        subscription_id: str
        term_id: str


    class azure.mgmt.newrelicobservability.types.SaaSData(TypedDict, total=False):
        key "saaSResourceId": str
        saa_s_resource_id: str


    class azure.mgmt.newrelicobservability.types.SaaSResourceDetailsResponse(ProxyResource):
        key "id": str
        key "name": str
        key "saasId": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        saas_id: str
        system_data: SystemData
        type: str


    class azure.mgmt.newrelicobservability.types.SubscriptionList(TypedDict, total=False):
        key "patchOperation": Union[str, PatchOperation]
        key "provisioningState": Union[str, ProvisioningState]
        monitoredSubscriptionList: list[MonitoredSubscription]
        monitored_subscription_list: list[MonitoredSubscription]
        patch_operation: Union[str, PatchOperation]
        provisioning_state: Union[str, ProvisioningState]


    class azure.mgmt.newrelicobservability.types.SwitchBillingRequest(TypedDict, total=False):
        key "azureResourceId": str
        key "organizationId": str
        key "planData": ForwardRef('PlanData', module='types')
        key "userEmail": Required[str]
        azure_resource_id: str
        organization_id: str
        plan_data: PlanData
        user_email: str


    class azure.mgmt.newrelicobservability.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.newrelicobservability.types.TagRule(ProxyResource):
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


    class azure.mgmt.newrelicobservability.types.TagRuleUpdate(TypedDict, total=False):
        key "properties": ForwardRef('TagRuleUpdateProperties', module='types')
        properties: TagRuleUpdateProperties


    class azure.mgmt.newrelicobservability.types.TagRuleUpdateProperties(TypedDict, total=False):
        key "logRules": ForwardRef('LogRules', module='types')
        key "metricRules": ForwardRef('MetricRules', module='types')
        log_rules: LogRules
        metric_rules: MetricRules


    class azure.mgmt.newrelicobservability.types.TrackedResource(Resource):
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


    class azure.mgmt.newrelicobservability.types.UserAssignedIdentity(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        client_id: str
        principal_id: str


    class azure.mgmt.newrelicobservability.types.UserInfo(TypedDict, total=False):
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


    class azure.mgmt.newrelicobservability.types.VMExtensionPayload(TypedDict, total=False):
        key "ingestionKey": str
        ingestion_key: str


    class azure.mgmt.newrelicobservability.types.VMInfo(TypedDict, total=False):
        key "agentStatus": str
        key "agentVersion": str
        key "vmId": str
        agent_status: str
        agent_version: str
        vm_id: str


```