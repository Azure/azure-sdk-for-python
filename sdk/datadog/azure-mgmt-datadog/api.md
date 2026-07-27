```py
namespace azure.mgmt.datadog

    class azure.mgmt.datadog.MicrosoftDatadogClient: implements ContextManager 
        billing_info: BillingInfoOperations
        creation_supported: CreationSupportedOperations
        datadog_monitor_resources: DatadogMonitorResourcesOperations
        marketplace_agreements: MarketplaceAgreementsOperations
        monitored_subscriptions: MonitoredSubscriptionsOperations
        monitors: MonitorsOperations
        operations: Operations
        organizations: OrganizationsOperations
        saa_soperation_group: SaaSOperationGroupOperations
        single_sign_on_configurations: SingleSignOnConfigurationsOperations
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


namespace azure.mgmt.datadog.aio

    class azure.mgmt.datadog.aio.MicrosoftDatadogClient: implements AsyncContextManager 
        billing_info: BillingInfoOperations
        creation_supported: CreationSupportedOperations
        datadog_monitor_resources: DatadogMonitorResourcesOperations
        marketplace_agreements: MarketplaceAgreementsOperations
        monitored_subscriptions: MonitoredSubscriptionsOperations
        monitors: MonitorsOperations
        operations: Operations
        organizations: OrganizationsOperations
        saa_soperation_group: SaaSOperationGroupOperations
        single_sign_on_configurations: SingleSignOnConfigurationsOperations
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


namespace azure.mgmt.datadog.aio.operations

    class azure.mgmt.datadog.aio.operations.BillingInfoOperations:

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


    class azure.mgmt.datadog.aio.operations.CreationSupportedOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                *, 
                datadog_organization_id: str, 
                **kwargs: Any
            ) -> CreateResourceSupportedResponse: ...

        @distributed_trace
        def list(
                self, 
                *, 
                datadog_organization_id: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[CreateResourceSupportedResponse]: ...


    class azure.mgmt.datadog.aio.operations.DatadogMonitorResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_link_saa_s(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: SaaSData, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DatadogMonitorResource]: ...

        @overload
        async def begin_link_saa_s(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: SaaSData, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DatadogMonitorResource]: ...

        @overload
        async def begin_link_saa_s(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DatadogMonitorResource]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-12-26-preview', params_added_on={'2025-12-26-preview': ['api_version', 'subscription_id', 'resource_group_name', 'monitor_name', 'accept']}, api_versions_list=['2025-12-26-preview'])
        async def latest_linked_saa_s(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> LatestLinkedSaaSResponse: ...


    class azure.mgmt.datadog.aio.operations.MarketplaceAgreementsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                body: Optional[DatadogAgreementResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DatadogAgreementResource: ...

        @overload
        async def create_or_update(
                self, 
                body: Optional[DatadogAgreementResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DatadogAgreementResource: ...

        @overload
        async def create_or_update(
                self, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DatadogAgreementResource: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[DatadogAgreementResource]: ...


    class azure.mgmt.datadog.aio.operations.MonitoredSubscriptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_createor_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                configuration_name: str, 
                body: Optional[MonitoredSubscriptionProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MonitoredSubscriptionProperties]: ...

        @overload
        async def begin_createor_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                configuration_name: str, 
                body: Optional[MonitoredSubscriptionProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MonitoredSubscriptionProperties]: ...

        @overload
        async def begin_createor_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                configuration_name: str, 
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
                configuration_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                configuration_name: str, 
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
                configuration_name: str, 
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
                configuration_name: str, 
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
                configuration_name: str, 
                **kwargs: Any
            ) -> MonitoredSubscriptionProperties: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[MonitoredSubscriptionProperties]: ...


    class azure.mgmt.datadog.aio.operations.MonitorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[DatadogMonitorResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DatadogMonitorResource]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[DatadogMonitorResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DatadogMonitorResource]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DatadogMonitorResource]: ...

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
                body: Optional[DatadogMonitorResourceUpdateParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DatadogMonitorResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[DatadogMonitorResourceUpdateParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DatadogMonitorResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DatadogMonitorResource]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> DatadogMonitorResource: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-11-03-preview', params_added_on={'2025-11-03-preview': ['api_version', 'subscription_id', 'resource_group_name', 'monitor_name', 'accept']}, api_versions_list=['2025-11-03-preview', '2025-12-26-preview'])
        async def get_default_application_key(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> DatadogApplicationKey: ...

        @distributed_trace_async
        async def get_default_key(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> DatadogApiKey: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[DatadogMonitorResource]: ...

        @distributed_trace
        def list_api_keys(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DatadogApiKey]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DatadogMonitorResource]: ...

        @distributed_trace
        def list_hosts(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DatadogHost]: ...

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

        @overload
        async def manage_sre_agent_connectors(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: SreAgentConnectorRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SreAgentConfigurationListResponse: ...

        @overload
        async def manage_sre_agent_connectors(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: SreAgentConnectorRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SreAgentConfigurationListResponse: ...

        @overload
        async def manage_sre_agent_connectors(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SreAgentConfigurationListResponse: ...

        @distributed_trace_async
        async def refresh_set_password_link(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> DatadogSetPasswordLink: ...

        @overload
        async def set_default_key(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[DatadogApiKey] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def set_default_key(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[DatadogApiKey] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def set_default_key(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.datadog.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[OperationResult]: ...


    class azure.mgmt.datadog.aio.operations.OrganizationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_resubscribe(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[ResubscribeProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DatadogMonitorResource]: ...

        @overload
        async def begin_resubscribe(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[ResubscribeProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DatadogMonitorResource]: ...

        @overload
        async def begin_resubscribe(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DatadogMonitorResource]: ...


    class azure.mgmt.datadog.aio.operations.SaaSOperationGroupOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def activate_resource(
                self, 
                body: ActivateSaaSParameterRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SaaSResourceDetailsResponse: ...

        @overload
        async def activate_resource(
                self, 
                body: ActivateSaaSParameterRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SaaSResourceDetailsResponse: ...

        @overload
        async def activate_resource(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SaaSResourceDetailsResponse: ...


    class azure.mgmt.datadog.aio.operations.SingleSignOnConfigurationsOperations:

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
                body: Optional[DatadogSingleSignOnResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DatadogSingleSignOnResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                configuration_name: str, 
                body: Optional[DatadogSingleSignOnResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DatadogSingleSignOnResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                configuration_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DatadogSingleSignOnResource]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                configuration_name: str, 
                **kwargs: Any
            ) -> DatadogSingleSignOnResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DatadogSingleSignOnResource]: ...


    class azure.mgmt.datadog.aio.operations.TagRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                rule_set_name: str, 
                body: Optional[MonitoringTagRules] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MonitoringTagRules: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                rule_set_name: str, 
                body: Optional[MonitoringTagRules] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MonitoringTagRules: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                rule_set_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MonitoringTagRules: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                rule_set_name: str, 
                **kwargs: Any
            ) -> MonitoringTagRules: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[MonitoringTagRules]: ...


namespace azure.mgmt.datadog.models

    class azure.mgmt.datadog.models.ActivateSaaSParameterRequest(_Model):
        datadog_organization_properties: Optional[DatadogOrganizationProperties]
        saa_s_resource_id: str
        user_info: Optional[UserInfo]

        @overload
        def __init__(
                self, 
                *, 
                datadog_organization_properties: Optional[DatadogOrganizationProperties] = ..., 
                saa_s_resource_id: str, 
                user_info: Optional[UserInfo] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datadog.models.AgentRules(_Model):
        enable_agent_monitoring: Optional[bool]
        filtering_tags: Optional[list[FilteringTag]]

        @overload
        def __init__(
                self, 
                *, 
                enable_agent_monitoring: Optional[bool] = ..., 
                filtering_tags: Optional[list[FilteringTag]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datadog.models.BillingInfoResponse(_Model):
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


    class azure.mgmt.datadog.models.ConnectorAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADD = "Add"
        REMOVE = "Remove"


    class azure.mgmt.datadog.models.CreateResourceSupportedProperties(_Model):
        creation_supported: Optional[bool]
        name: Optional[str]


    class azure.mgmt.datadog.models.CreateResourceSupportedResponse(_Model):
        properties: Optional[CreateResourceSupportedProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CreateResourceSupportedProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datadog.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.datadog.models.DatadogAgreementProperties(_Model):
        accepted: Optional[bool]
        license_text_link: Optional[str]
        plan: Optional[str]
        privacy_policy_link: Optional[str]
        product: Optional[str]
        publisher: Optional[str]
        retrieve_datetime: Optional[datetime]
        signature: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                accepted: Optional[bool] = ..., 
                license_text_link: Optional[str] = ..., 
                plan: Optional[str] = ..., 
                privacy_policy_link: Optional[str] = ..., 
                product: Optional[str] = ..., 
                publisher: Optional[str] = ..., 
                retrieve_datetime: Optional[datetime] = ..., 
                signature: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datadog.models.DatadogAgreementResource(_Model):
        id: Optional[str]
        name: Optional[str]
        properties: Optional[DatadogAgreementProperties]
        system_data: Optional[SystemData]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DatadogAgreementProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datadog.models.DatadogApiKey(_Model):
        created: Optional[str]
        created_by: Optional[str]
        key: str
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                created: Optional[str] = ..., 
                created_by: Optional[str] = ..., 
                key: str, 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datadog.models.DatadogApplicationKey(_Model):
        created_by: Optional[str]
        key: str
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                created_by: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datadog.models.DatadogHost(_Model):
        aliases: Optional[list[str]]
        apps: Optional[list[str]]
        meta: Optional[DatadogHostMetadata]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                aliases: Optional[list[str]] = ..., 
                apps: Optional[list[str]] = ..., 
                meta: Optional[DatadogHostMetadata] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datadog.models.DatadogHostMetadata(_Model):
        agent_version: Optional[str]
        install_method: Optional[DatadogInstallMethod]
        logs_agent: Optional[DatadogLogsAgent]

        @overload
        def __init__(
                self, 
                *, 
                agent_version: Optional[str] = ..., 
                install_method: Optional[DatadogInstallMethod] = ..., 
                logs_agent: Optional[DatadogLogsAgent] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datadog.models.DatadogInstallMethod(_Model):
        installer_version: Optional[str]
        tool: Optional[str]
        tool_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                installer_version: Optional[str] = ..., 
                tool: Optional[str] = ..., 
                tool_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datadog.models.DatadogLogsAgent(_Model):
        transport: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                transport: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datadog.models.DatadogMonitorResource(TrackedResource):
        id: str
        identity: Optional[IdentityProperties]
        location: str
        name: str
        properties: Optional[MonitorProperties]
        sku: Optional[ResourceSku]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[IdentityProperties] = ..., 
                location: str, 
                properties: Optional[MonitorProperties] = ..., 
                sku: Optional[ResourceSku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datadog.models.DatadogMonitorResourceUpdateParameters(_Model):
        properties: Optional[MonitorUpdateProperties]
        sku: Optional[ResourceSku]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[MonitorUpdateProperties] = ..., 
                sku: Optional[ResourceSku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datadog.models.DatadogOrganizationProperties(_Model):
        api_key: Optional[str]
        application_key: Optional[str]
        cspm: Optional[bool]
        enterprise_app_id: Optional[str]
        id: Optional[str]
        linking_auth_code: Optional[str]
        linking_client_id: Optional[str]
        name: Optional[str]
        redirect_uri: Optional[str]
        resource_collection: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                api_key: Optional[str] = ..., 
                application_key: Optional[str] = ..., 
                cspm: Optional[bool] = ..., 
                enterprise_app_id: Optional[str] = ..., 
                id: Optional[str] = ..., 
                linking_auth_code: Optional[str] = ..., 
                linking_client_id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                redirect_uri: Optional[str] = ..., 
                resource_collection: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datadog.models.DatadogSetPasswordLink(_Model):
        set_password_link: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                set_password_link: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datadog.models.DatadogSingleSignOnProperties(_Model):
        enterprise_app_id: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        single_sign_on_state: Optional[Union[str, SingleSignOnStates]]
        single_sign_on_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                enterprise_app_id: Optional[str] = ..., 
                single_sign_on_state: Optional[Union[str, SingleSignOnStates]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datadog.models.DatadogSingleSignOnResource(ProxyResource):
        id: str
        name: str
        properties: Optional[DatadogSingleSignOnProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DatadogSingleSignOnProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datadog.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.datadog.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.datadog.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datadog.models.FilteringTag(_Model):
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


    class azure.mgmt.datadog.models.IdentityProperties(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Optional[Union[str, ManagedIdentityTypes]]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, ManagedIdentityTypes]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datadog.models.LatestLinkedSaaSResponse(_Model):
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


    class azure.mgmt.datadog.models.LiftrResourceCategories(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MONITOR_LOGS = "MonitorLogs"
        UNKNOWN = "Unknown"


    class azure.mgmt.datadog.models.LinkedResource(_Model):
        id: Optional[str]
        location: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                location: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datadog.models.LogRules(_Model):
        filtering_tags: Optional[list[FilteringTag]]
        send_aad_logs: Optional[bool]
        send_resource_logs: Optional[bool]
        send_subscription_logs: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                filtering_tags: Optional[list[FilteringTag]] = ..., 
                send_aad_logs: Optional[bool] = ..., 
                send_resource_logs: Optional[bool] = ..., 
                send_subscription_logs: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datadog.models.ManagedIdentityTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM_ASSIGNED = "SystemAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.datadog.models.MarketplaceOfferDetails(_Model):
        offer_id: Optional[str]
        publisher_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                offer_id: Optional[str] = ..., 
                publisher_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datadog.models.MarketplaceSaaSInfo(_Model):
        billed_azure_subscription_id: Optional[str]
        marketplace_name: Optional[str]
        marketplace_status: Optional[str]
        marketplace_subscription_id: Optional[str]
        offer_id: Optional[str]
        subscribed: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                billed_azure_subscription_id: Optional[str] = ..., 
                marketplace_name: Optional[str] = ..., 
                marketplace_status: Optional[str] = ..., 
                marketplace_subscription_id: Optional[str] = ..., 
                offer_id: Optional[str] = ..., 
                subscribed: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datadog.models.MarketplaceSubscriptionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        PROVISIONING = "Provisioning"
        SUSPENDED = "Suspended"
        UNSUBSCRIBED = "Unsubscribed"


    class azure.mgmt.datadog.models.MetricRules(_Model):
        filtering_tags: Optional[list[FilteringTag]]

        @overload
        def __init__(
                self, 
                *, 
                filtering_tags: Optional[list[FilteringTag]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datadog.models.MonitorProperties(_Model):
        datadog_organization_properties: Optional[DatadogOrganizationProperties]
        liftr_resource_category: Optional[Union[str, LiftrResourceCategories]]
        liftr_resource_preference: Optional[int]
        marketplace_offer_details: Optional[MarketplaceOfferDetails]
        marketplace_subscription_status: Optional[Union[str, MarketplaceSubscriptionStatus]]
        monitoring_status: Optional[Union[str, MonitoringStatus]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        saa_s_data: Optional[SaaSData]
        sre_agent_configuration: Optional[list[SreAgentConfiguration]]
        user_info: Optional[UserInfo]

        @overload
        def __init__(
                self, 
                *, 
                datadog_organization_properties: Optional[DatadogOrganizationProperties] = ..., 
                marketplace_offer_details: Optional[MarketplaceOfferDetails] = ..., 
                monitoring_status: Optional[Union[str, MonitoringStatus]] = ..., 
                saa_s_data: Optional[SaaSData] = ..., 
                sre_agent_configuration: Optional[list[SreAgentConfiguration]] = ..., 
                user_info: Optional[UserInfo] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datadog.models.MonitorUpdateProperties(_Model):
        cspm: Optional[bool]
        monitoring_status: Optional[Union[str, MonitoringStatus]]
        resource_collection: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                cspm: Optional[bool] = ..., 
                monitoring_status: Optional[Union[str, MonitoringStatus]] = ..., 
                resource_collection: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datadog.models.MonitoredResource(_Model):
        id: Optional[str]
        reason_for_logs_status: Optional[str]
        reason_for_metrics_status: Optional[str]
        sending_logs: Optional[bool]
        sending_metrics: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                reason_for_logs_status: Optional[str] = ..., 
                reason_for_metrics_status: Optional[str] = ..., 
                sending_logs: Optional[bool] = ..., 
                sending_metrics: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datadog.models.MonitoredSubscription(_Model):
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


    class azure.mgmt.datadog.models.MonitoredSubscriptionProperties(ProxyResource):
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


    class azure.mgmt.datadog.models.MonitoringStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.datadog.models.MonitoringTagRules(ProxyResource):
        id: str
        name: str
        properties: Optional[MonitoringTagRulesProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[MonitoringTagRulesProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datadog.models.MonitoringTagRulesProperties(_Model):
        agent_rules: Optional[AgentRules]
        automuting: Optional[bool]
        custom_metrics: Optional[bool]
        log_rules: Optional[LogRules]
        metric_rules: Optional[MetricRules]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                agent_rules: Optional[AgentRules] = ..., 
                automuting: Optional[bool] = ..., 
                custom_metrics: Optional[bool] = ..., 
                log_rules: Optional[LogRules] = ..., 
                metric_rules: Optional[MetricRules] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datadog.models.Operation(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        ADD_BEGIN = "AddBegin"
        ADD_COMPLETE = "AddComplete"
        DELETE_BEGIN = "DeleteBegin"
        DELETE_COMPLETE = "DeleteComplete"


    class azure.mgmt.datadog.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                operation: Optional[str] = ..., 
                provider: Optional[str] = ..., 
                resource: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datadog.models.OperationResult(_Model):
        display: Optional[OperationDisplay]
        is_data_action: Optional[bool]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
                is_data_action: Optional[bool] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datadog.models.PartnerBillingEntity(_Model):
        id: Optional[str]
        name: Optional[str]
        partner_entity_uri: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                partner_entity_uri: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datadog.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETED = "Deleted"
        DELETING = "Deleting"
        FAILED = "Failed"
        NOT_SPECIFIED = "NotSpecified"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.datadog.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.datadog.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.datadog.models.ResourceSku(_Model):
        name: str

        @overload
        def __init__(
                self, 
                *, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datadog.models.ResubscribeProperties(_Model):
        azure_subscription_id: Optional[str]
        resource_group: Optional[str]
        sku: Optional[ResourceSku]

        @overload
        def __init__(
                self, 
                *, 
                azure_subscription_id: Optional[str] = ..., 
                resource_group: Optional[str] = ..., 
                sku: Optional[ResourceSku] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datadog.models.SaaSData(_Model):
        saa_s_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                saa_s_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datadog.models.SaaSResourceDetailsResponse(ProxyResource):
        id: str
        name: str
        saa_s_id: Optional[str]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                saa_s_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datadog.models.SingleSignOnStates(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLE = "Disable"
        ENABLE = "Enable"
        EXISTING = "Existing"
        INITIAL = "Initial"


    class azure.mgmt.datadog.models.SreAgentConfiguration(_Model):
        mcp_connector_resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                mcp_connector_resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datadog.models.SreAgentConfigurationListResponse(_Model):
        next_link: Optional[str]
        value: list[SreAgentConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[SreAgentConfiguration]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datadog.models.SreAgentConnectorRequest(_Model):
        action: Union[str, ConnectorAction]
        mcp_connector_resource_id_list: list[SreAgentConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                action: Union[str, ConnectorAction], 
                mcp_connector_resource_id_list: list[SreAgentConfiguration]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datadog.models.Status(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        DELETING = "Deleting"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"


    class azure.mgmt.datadog.models.SubscriptionList(_Model):
        monitored_subscription_list: Optional[list[MonitoredSubscription]]
        operation: Optional[Union[str, Operation]]

        @overload
        def __init__(
                self, 
                *, 
                monitored_subscription_list: Optional[list[MonitoredSubscription]] = ..., 
                operation: Optional[Union[str, Operation]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datadog.models.SystemData(_Model):
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


    class azure.mgmt.datadog.models.TagAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXCLUDE = "Exclude"
        INCLUDE = "Include"


    class azure.mgmt.datadog.models.TrackedResource(Resource):
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


    class azure.mgmt.datadog.models.UserInfo(_Model):
        email_address: Optional[str]
        name: Optional[str]
        phone_number: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                email_address: Optional[str] = ..., 
                name: Optional[str] = ..., 
                phone_number: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.datadog.operations

    class azure.mgmt.datadog.operations.BillingInfoOperations:

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


    class azure.mgmt.datadog.operations.CreationSupportedOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                *, 
                datadog_organization_id: str, 
                **kwargs: Any
            ) -> CreateResourceSupportedResponse: ...

        @distributed_trace
        def list(
                self, 
                *, 
                datadog_organization_id: str, 
                **kwargs: Any
            ) -> ItemPaged[CreateResourceSupportedResponse]: ...


    class azure.mgmt.datadog.operations.DatadogMonitorResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_link_saa_s(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: SaaSData, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DatadogMonitorResource]: ...

        @overload
        def begin_link_saa_s(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: SaaSData, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DatadogMonitorResource]: ...

        @overload
        def begin_link_saa_s(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DatadogMonitorResource]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-12-26-preview', params_added_on={'2025-12-26-preview': ['api_version', 'subscription_id', 'resource_group_name', 'monitor_name', 'accept']}, api_versions_list=['2025-12-26-preview'])
        def latest_linked_saa_s(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> LatestLinkedSaaSResponse: ...


    class azure.mgmt.datadog.operations.MarketplaceAgreementsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                body: Optional[DatadogAgreementResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DatadogAgreementResource: ...

        @overload
        def create_or_update(
                self, 
                body: Optional[DatadogAgreementResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DatadogAgreementResource: ...

        @overload
        def create_or_update(
                self, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DatadogAgreementResource: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[DatadogAgreementResource]: ...


    class azure.mgmt.datadog.operations.MonitoredSubscriptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_createor_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                configuration_name: str, 
                body: Optional[MonitoredSubscriptionProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MonitoredSubscriptionProperties]: ...

        @overload
        def begin_createor_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                configuration_name: str, 
                body: Optional[MonitoredSubscriptionProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MonitoredSubscriptionProperties]: ...

        @overload
        def begin_createor_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                configuration_name: str, 
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
                configuration_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                configuration_name: str, 
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
                configuration_name: str, 
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
                configuration_name: str, 
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
                configuration_name: str, 
                **kwargs: Any
            ) -> MonitoredSubscriptionProperties: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> ItemPaged[MonitoredSubscriptionProperties]: ...


    class azure.mgmt.datadog.operations.MonitorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[DatadogMonitorResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DatadogMonitorResource]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[DatadogMonitorResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DatadogMonitorResource]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DatadogMonitorResource]: ...

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
                body: Optional[DatadogMonitorResourceUpdateParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DatadogMonitorResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[DatadogMonitorResourceUpdateParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DatadogMonitorResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DatadogMonitorResource]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> DatadogMonitorResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-11-03-preview', params_added_on={'2025-11-03-preview': ['api_version', 'subscription_id', 'resource_group_name', 'monitor_name', 'accept']}, api_versions_list=['2025-11-03-preview', '2025-12-26-preview'])
        def get_default_application_key(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> DatadogApplicationKey: ...

        @distributed_trace
        def get_default_key(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> DatadogApiKey: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[DatadogMonitorResource]: ...

        @distributed_trace
        def list_api_keys(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DatadogApiKey]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DatadogMonitorResource]: ...

        @distributed_trace
        def list_hosts(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DatadogHost]: ...

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

        @overload
        def manage_sre_agent_connectors(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: SreAgentConnectorRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SreAgentConfigurationListResponse: ...

        @overload
        def manage_sre_agent_connectors(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: SreAgentConnectorRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SreAgentConfigurationListResponse: ...

        @overload
        def manage_sre_agent_connectors(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SreAgentConfigurationListResponse: ...

        @distributed_trace
        def refresh_set_password_link(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> DatadogSetPasswordLink: ...

        @overload
        def set_default_key(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[DatadogApiKey] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def set_default_key(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[DatadogApiKey] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def set_default_key(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.datadog.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[OperationResult]: ...


    class azure.mgmt.datadog.operations.OrganizationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_resubscribe(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[ResubscribeProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DatadogMonitorResource]: ...

        @overload
        def begin_resubscribe(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[ResubscribeProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DatadogMonitorResource]: ...

        @overload
        def begin_resubscribe(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DatadogMonitorResource]: ...


    class azure.mgmt.datadog.operations.SaaSOperationGroupOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def activate_resource(
                self, 
                body: ActivateSaaSParameterRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SaaSResourceDetailsResponse: ...

        @overload
        def activate_resource(
                self, 
                body: ActivateSaaSParameterRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SaaSResourceDetailsResponse: ...

        @overload
        def activate_resource(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SaaSResourceDetailsResponse: ...


    class azure.mgmt.datadog.operations.SingleSignOnConfigurationsOperations:

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
                body: Optional[DatadogSingleSignOnResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DatadogSingleSignOnResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                configuration_name: str, 
                body: Optional[DatadogSingleSignOnResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DatadogSingleSignOnResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                configuration_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DatadogSingleSignOnResource]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                configuration_name: str, 
                **kwargs: Any
            ) -> DatadogSingleSignOnResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DatadogSingleSignOnResource]: ...


    class azure.mgmt.datadog.operations.TagRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                rule_set_name: str, 
                body: Optional[MonitoringTagRules] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MonitoringTagRules: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                rule_set_name: str, 
                body: Optional[MonitoringTagRules] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MonitoringTagRules: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                rule_set_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MonitoringTagRules: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                rule_set_name: str, 
                **kwargs: Any
            ) -> MonitoringTagRules: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                **kwargs: Any
            ) -> ItemPaged[MonitoringTagRules]: ...


namespace azure.mgmt.datadog.types

    class azure.mgmt.datadog.types.ActivateSaaSParameterRequest(TypedDict, total=False):
        key "datadogOrganizationProperties": ForwardRef('DatadogOrganizationProperties', module='types')
        key "saaSResourceId": Required[str]
        key "userInfo": ForwardRef('UserInfo', module='types')
        datadog_organization_properties: DatadogOrganizationProperties
        saa_s_resource_id: str
        user_info: UserInfo


    class azure.mgmt.datadog.types.AgentRules(TypedDict, total=False):
        key "enableAgentMonitoring": bool
        enable_agent_monitoring: bool
        filteringTags: list[FilteringTag]
        filtering_tags: list[FilteringTag]


    class azure.mgmt.datadog.types.BillingInfoResponse(TypedDict, total=False):
        key "marketplaceSaasInfo": ForwardRef('MarketplaceSaaSInfo', module='types')
        key "partnerBillingEntity": ForwardRef('PartnerBillingEntity', module='types')
        marketplace_saas_info: MarketplaceSaaSInfo
        partner_billing_entity: PartnerBillingEntity


    class azure.mgmt.datadog.types.CreateResourceSupportedProperties(TypedDict, total=False):
        key "creationSupported": bool
        key "name": str
        creation_supported: bool
        name: str


    class azure.mgmt.datadog.types.CreateResourceSupportedResponse(TypedDict, total=False):
        key "properties": ForwardRef('CreateResourceSupportedProperties', module='types')
        properties: CreateResourceSupportedProperties


    class azure.mgmt.datadog.types.DatadogAgreementProperties(TypedDict, total=False):
        key "accepted": bool
        key "licenseTextLink": str
        key "plan": str
        key "privacyPolicyLink": str
        key "product": str
        key "publisher": str
        key "retrieveDatetime": str
        key "signature": str
        accepted: bool
        license_text_link: str
        plan: str
        privacy_policy_link: str
        product: str
        publisher: str
        retrieve_datetime: str
        signature: str


    class azure.mgmt.datadog.types.DatadogAgreementResource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "properties": ForwardRef('DatadogAgreementProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: DatadogAgreementProperties
        system_data: SystemData
        type: str


    class azure.mgmt.datadog.types.DatadogApiKey(TypedDict, total=False):
        key "created": str
        key "createdBy": str
        key "key": Required[str]
        key "name": str
        created: str
        created_by: str
        key: str
        name: str


    class azure.mgmt.datadog.types.DatadogApplicationKey(TypedDict, total=False):
        key "createdBy": str
        key "key": Required[str]
        key "name": str
        created_by: str
        key: str
        name: str


    class azure.mgmt.datadog.types.DatadogHost(TypedDict, total=False):
        key "meta": ForwardRef('DatadogHostMetadata', module='types')
        key "name": str
        aliases: list[str]
        apps: list[str]
        meta: DatadogHostMetadata
        name: str


    class azure.mgmt.datadog.types.DatadogHostMetadata(TypedDict, total=False):
        key "agentVersion": str
        key "installMethod": ForwardRef('DatadogInstallMethod', module='types')
        key "logsAgent": ForwardRef('DatadogLogsAgent', module='types')
        agent_version: str
        install_method: DatadogInstallMethod
        logs_agent: DatadogLogsAgent


    class azure.mgmt.datadog.types.DatadogInstallMethod(TypedDict, total=False):
        key "installerVersion": str
        key "tool": str
        key "toolVersion": str
        installer_version: str
        tool: str
        tool_version: str


    class azure.mgmt.datadog.types.DatadogLogsAgent(TypedDict, total=False):
        key "transport": str
        transport: str


    class azure.mgmt.datadog.types.DatadogMonitorResource(TrackedResource):
        key "id": str
        key "identity": ForwardRef('IdentityProperties', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('MonitorProperties', module='types')
        key "sku": ForwardRef('ResourceSku', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: IdentityProperties
        location: str
        name: str
        properties: MonitorProperties
        sku: ResourceSku
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.datadog.types.DatadogMonitorResourceUpdateParameters(TypedDict, total=False):
        key "properties": ForwardRef('MonitorUpdateProperties', module='types')
        key "sku": ForwardRef('ResourceSku', module='types')
        properties: MonitorUpdateProperties
        sku: ResourceSku
        tags: dict[str, str]


    class azure.mgmt.datadog.types.DatadogOrganizationProperties(TypedDict, total=False):
        key "apiKey": str
        key "applicationKey": str
        key "cspm": bool
        key "enterpriseAppId": str
        key "id": str
        key "linkingAuthCode": str
        key "linkingClientId": str
        key "name": str
        key "redirectUri": str
        key "resourceCollection": bool
        api_key: str
        application_key: str
        cspm: bool
        enterprise_app_id: str
        id: str
        linking_auth_code: str
        linking_client_id: str
        name: str
        redirect_uri: str
        resource_collection: bool


    class azure.mgmt.datadog.types.DatadogSetPasswordLink(TypedDict, total=False):
        key "setPasswordLink": str
        set_password_link: str


    class azure.mgmt.datadog.types.DatadogSingleSignOnProperties(TypedDict, total=False):
        key "enterpriseAppId": str
        key "provisioningState": Union[str, ProvisioningState]
        key "singleSignOnState": Union[str, SingleSignOnStates]
        key "singleSignOnUrl": str
        enterprise_app_id: str
        provisioning_state: Union[str, ProvisioningState]
        single_sign_on_state: Union[str, SingleSignOnStates]
        single_sign_on_url: str


    class azure.mgmt.datadog.types.DatadogSingleSignOnResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('DatadogSingleSignOnProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: DatadogSingleSignOnProperties
        system_data: SystemData
        type: str


    class azure.mgmt.datadog.types.ErrorAdditionalInfo(TypedDict, total=False):
        key "info": Any
        key "type": str
        info: Any
        type: str


    class azure.mgmt.datadog.types.ErrorDetail(TypedDict, total=False):
        key "code": str
        key "message": str
        key "target": str
        additionalInfo: list[ErrorAdditionalInfo]
        additional_info: list[ErrorAdditionalInfo]
        code: str
        details: list[ErrorDetail]
        message: str
        target: str


    class azure.mgmt.datadog.types.ErrorResponse(TypedDict, total=False):
        key "error": ForwardRef('ErrorDetail', module='types')
        error: ErrorDetail


    class azure.mgmt.datadog.types.FilteringTag(TypedDict, total=False):
        key "action": Union[str, TagAction]
        key "name": str
        key "value": str
        action: Union[str, TagAction]
        name: str
        value: str


    class azure.mgmt.datadog.types.IdentityProperties(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Union[str, ManagedIdentityTypes]
        principal_id: str
        tenant_id: str
        type: Union[str, ManagedIdentityTypes]


    class azure.mgmt.datadog.types.LatestLinkedSaaSResponse(TypedDict, total=False):
        key "isHiddenSaaS": bool
        key "saaSResourceId": str
        is_hidden_saa_s: bool
        saa_s_resource_id: str


    class azure.mgmt.datadog.types.LinkedResource(TypedDict, total=False):
        key "id": str
        key "location": str
        id: str
        location: str


    class azure.mgmt.datadog.types.LogRules(TypedDict, total=False):
        key "sendAadLogs": bool
        key "sendResourceLogs": bool
        key "sendSubscriptionLogs": bool
        filteringTags: list[FilteringTag]
        filtering_tags: list[FilteringTag]
        send_aad_logs: bool
        send_resource_logs: bool
        send_subscription_logs: bool


    class azure.mgmt.datadog.types.MarketplaceOfferDetails(TypedDict, total=False):
        key "offerId": str
        key "publisherId": str
        offer_id: str
        publisher_id: str


    class azure.mgmt.datadog.types.MarketplaceSaaSInfo(TypedDict, total=False):
        key "billedAzureSubscriptionId": str
        key "marketplaceName": str
        key "marketplaceStatus": str
        key "marketplaceSubscriptionId": str
        key "offerId": str
        key "subscribed": bool
        billed_azure_subscription_id: str
        marketplace_name: str
        marketplace_status: str
        marketplace_subscription_id: str
        offer_id: str
        subscribed: bool


    class azure.mgmt.datadog.types.MetricRules(TypedDict, total=False):
        filteringTags: list[FilteringTag]
        filtering_tags: list[FilteringTag]


    class azure.mgmt.datadog.types.MonitorProperties(TypedDict, total=False):
        key "datadogOrganizationProperties": ForwardRef('DatadogOrganizationProperties', module='types')
        key "liftrResourceCategory": Union[str, LiftrResourceCategories]
        key "liftrResourcePreference": int
        key "marketplaceOfferDetails": ForwardRef('MarketplaceOfferDetails', module='types')
        key "marketplaceSubscriptionStatus": Union[str, MarketplaceSubscriptionStatus]
        key "monitoringStatus": Union[str, MonitoringStatus]
        key "provisioningState": Union[str, ProvisioningState]
        key "saaSData": ForwardRef('SaaSData', module='types')
        key "userInfo": ForwardRef('UserInfo', module='types')
        datadog_organization_properties: DatadogOrganizationProperties
        liftr_resource_category: Union[str, LiftrResourceCategories]
        liftr_resource_preference: int
        marketplace_offer_details: MarketplaceOfferDetails
        marketplace_subscription_status: Union[str, MarketplaceSubscriptionStatus]
        monitoring_status: Union[str, MonitoringStatus]
        provisioning_state: Union[str, ProvisioningState]
        saa_s_data: SaaSData
        sreAgentConfiguration: list[SreAgentConfiguration]
        sre_agent_configuration: list[SreAgentConfiguration]
        user_info: UserInfo


    class azure.mgmt.datadog.types.MonitorUpdateProperties(TypedDict, total=False):
        key "cspm": bool
        key "monitoringStatus": Union[str, MonitoringStatus]
        key "resourceCollection": bool
        cspm: bool
        monitoring_status: Union[str, MonitoringStatus]
        resource_collection: bool


    class azure.mgmt.datadog.types.MonitoredResource(TypedDict, total=False):
        key "id": str
        key "reasonForLogsStatus": str
        key "reasonForMetricsStatus": str
        key "sendingLogs": bool
        key "sendingMetrics": bool
        id: str
        reason_for_logs_status: str
        reason_for_metrics_status: str
        sending_logs: bool
        sending_metrics: bool


    class azure.mgmt.datadog.types.MonitoredSubscription(TypedDict, total=False):
        key "error": str
        key "status": Union[str, Status]
        key "subscriptionId": str
        key "tagRules": ForwardRef('MonitoringTagRulesProperties', module='types')
        error: str
        status: Union[str, Status]
        subscription_id: str
        tag_rules: MonitoringTagRulesProperties


    class azure.mgmt.datadog.types.MonitoredSubscriptionProperties(ProxyResource):
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


    class azure.mgmt.datadog.types.MonitoringTagRules(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('MonitoringTagRulesProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: MonitoringTagRulesProperties
        system_data: SystemData
        type: str


    class azure.mgmt.datadog.types.MonitoringTagRulesProperties(TypedDict, total=False):
        key "agentRules": ForwardRef('AgentRules', module='types')
        key "automuting": bool
        key "customMetrics": bool
        key "logRules": ForwardRef('LogRules', module='types')
        key "metricRules": ForwardRef('MetricRules', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        agent_rules: AgentRules
        automuting: bool
        custom_metrics: bool
        log_rules: LogRules
        metric_rules: MetricRules
        provisioning_state: Union[str, ProvisioningState]


    class azure.mgmt.datadog.types.OperationDisplay(TypedDict, total=False):
        key "description": str
        key "operation": str
        key "provider": str
        key "resource": str
        description: str
        operation: str
        provider: str
        resource: str


    class azure.mgmt.datadog.types.OperationResult(TypedDict, total=False):
        key "display": ForwardRef('OperationDisplay', module='types')
        key "isDataAction": bool
        key "name": str
        display: OperationDisplay
        is_data_action: bool
        name: str


    class azure.mgmt.datadog.types.PartnerBillingEntity(TypedDict, total=False):
        key "id": str
        key "name": str
        key "partnerEntityUri": str
        id: str
        name: str
        partner_entity_uri: str


    class azure.mgmt.datadog.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.datadog.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.datadog.types.ResourceSku(TypedDict, total=False):
        key "name": Required[str]
        name: str


    class azure.mgmt.datadog.types.ResubscribeProperties(TypedDict, total=False):
        key "azureSubscriptionId": str
        key "resourceGroup": str
        key "sku": ForwardRef('ResourceSku', module='types')
        azure_subscription_id: str
        resource_group: str
        sku: ResourceSku


    class azure.mgmt.datadog.types.SaaSData(TypedDict, total=False):
        key "saaSResourceId": str
        saa_s_resource_id: str


    class azure.mgmt.datadog.types.SaaSResourceDetailsResponse(ProxyResource):
        key "id": str
        key "name": str
        key "saaSId": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        saa_s_id: str
        system_data: SystemData
        type: str


    class azure.mgmt.datadog.types.SreAgentConfiguration(TypedDict, total=False):
        key "mcpConnectorResourceId": Required[str]
        mcp_connector_resource_id: str


    class azure.mgmt.datadog.types.SreAgentConfigurationListResponse(TypedDict, total=False):
        key "nextLink": str
        key "value": Required[list[SreAgentConfiguration]]
        next_link: str
        value: list[SreAgentConfiguration]


    class azure.mgmt.datadog.types.SreAgentConnectorRequest(TypedDict, total=False):
        key "action": Required[Union[str, ConnectorAction]]
        key "mcpConnectorResourceIdList": Required[list[SreAgentConfiguration]]
        action: Union[str, ConnectorAction]
        mcp_connector_resource_id_list: list[SreAgentConfiguration]


    class azure.mgmt.datadog.types.SubscriptionList(TypedDict, total=False):
        key "operation": Union[str, Operation]
        monitoredSubscriptionList: list[MonitoredSubscription]
        monitored_subscription_list: list[MonitoredSubscription]
        operation: Union[str, Operation]


    class azure.mgmt.datadog.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.datadog.types.TrackedResource(Resource):
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


    class azure.mgmt.datadog.types.UserInfo(TypedDict, total=False):
        key "emailAddress": str
        key "name": str
        key "phoneNumber": str
        email_address: str
        name: str
        phone_number: str


```