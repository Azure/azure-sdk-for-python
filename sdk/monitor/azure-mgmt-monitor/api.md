```py
namespace azure.mgmt.monitor

    class azure.mgmt.monitor.MonitorManagementClient(_MonitorManagementClientOperationsMixin): implements ContextManager 
        action_groups: ActionGroupsOperations
        activity_log_alerts: ActivityLogAlertsOperations
        activity_logs: ActivityLogsOperations
        alert_rule_incidents: AlertRuleIncidentsOperations
        autoscale_settings: AutoscaleSettingsOperations
        baselines: BaselinesOperations
        data_collection_endpoints: DataCollectionEndpointsOperations
        data_collection_rule_associations: DataCollectionRuleAssociationsOperations
        data_collection_rules: DataCollectionRulesOperations
        diagnostic_settings: DiagnosticSettingsOperations
        diagnostic_settings_category: DiagnosticSettingsCategoryOperations
        event_categories: EventCategoriesOperations
        log_profiles: LogProfilesOperations
        metric_alerts: MetricAlertsOperations
        metric_alerts_status: MetricAlertsStatusOperations
        metric_definitions: MetricDefinitionsOperations
        metric_namespaces: MetricNamespacesOperations
        metrics: MetricsOperations
        predictive_metric: PredictiveMetricOperations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        private_link_scope_operation_status: PrivateLinkScopeOperationStatusOperations
        private_link_scoped_resources: PrivateLinkScopedResourcesOperations
        private_link_scopes: PrivateLinkScopesOperations
        scheduled_query_rule: ScheduledQueryRuleOperations
        scheduled_query_rules: ScheduledQueryRulesOperations
        service_diagnostic_settings: ServiceDiagnosticSettingsOperations
        tenant_action_groups: TenantActionGroupsOperations
        tenant_activity_logs: TenantActivityLogsOperations
        vm_insights: VMInsightsOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                cloud_setting: Optional[AzureClouds] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        def begin_create_notifications_at_tenant_action_group_resource_level(
                self, 
                management_group_id: str, 
                tenant_action_group_name: str, 
                notification_request: TenantNotificationRequestBody, 
                *, 
                content_type: str = "application/json", 
                x_ms_client_tenant_id: str, 
                **kwargs: Any
            ) -> LROPoller[TenantActionGroupTestNotificationDetailsResponse]: ...

        @overload
        def begin_create_notifications_at_tenant_action_group_resource_level(
                self, 
                management_group_id: str, 
                tenant_action_group_name: str, 
                notification_request: TenantNotificationRequestBody, 
                *, 
                content_type: str = "application/json", 
                x_ms_client_tenant_id: str, 
                **kwargs: Any
            ) -> LROPoller[TenantActionGroupTestNotificationDetailsResponse]: ...

        @overload
        def begin_create_notifications_at_tenant_action_group_resource_level(
                self, 
                management_group_id: str, 
                tenant_action_group_name: str, 
                notification_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                x_ms_client_tenant_id: str, 
                **kwargs: Any
            ) -> LROPoller[TenantActionGroupTestNotificationDetailsResponse]: ...

        def close(self) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2023-05-01-preview', params_added_on={'2023-05-01-preview': ['api_version', 'management_group_id', 'tenant_action_group_name', 'notification_id', 'x_ms_client_tenant_id', 'accept']}, api_versions_list=['2023-05-01-preview'])
        def get_test_notifications_at_tenant_action_group_resource_level(
                self, 
                management_group_id: str, 
                tenant_action_group_name: str, 
                notification_id: str, 
                *, 
                x_ms_client_tenant_id: str, 
                **kwargs: Any
            ) -> TenantActionGroupTestNotificationDetailsResponse: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


namespace azure.mgmt.monitor.aio

    class azure.mgmt.monitor.aio.MonitorManagementClient(_MonitorManagementClientOperationsMixin): implements AsyncContextManager 
        action_groups: ActionGroupsOperations
        activity_log_alerts: ActivityLogAlertsOperations
        activity_logs: ActivityLogsOperations
        alert_rule_incidents: AlertRuleIncidentsOperations
        autoscale_settings: AutoscaleSettingsOperations
        baselines: BaselinesOperations
        data_collection_endpoints: DataCollectionEndpointsOperations
        data_collection_rule_associations: DataCollectionRuleAssociationsOperations
        data_collection_rules: DataCollectionRulesOperations
        diagnostic_settings: DiagnosticSettingsOperations
        diagnostic_settings_category: DiagnosticSettingsCategoryOperations
        event_categories: EventCategoriesOperations
        log_profiles: LogProfilesOperations
        metric_alerts: MetricAlertsOperations
        metric_alerts_status: MetricAlertsStatusOperations
        metric_definitions: MetricDefinitionsOperations
        metric_namespaces: MetricNamespacesOperations
        metrics: MetricsOperations
        predictive_metric: PredictiveMetricOperations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        private_link_scope_operation_status: PrivateLinkScopeOperationStatusOperations
        private_link_scoped_resources: PrivateLinkScopedResourcesOperations
        private_link_scopes: PrivateLinkScopesOperations
        scheduled_query_rule: ScheduledQueryRuleOperations
        scheduled_query_rules: ScheduledQueryRulesOperations
        service_diagnostic_settings: ServiceDiagnosticSettingsOperations
        tenant_action_groups: TenantActionGroupsOperations
        tenant_activity_logs: TenantActivityLogsOperations
        vm_insights: VMInsightsOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                cloud_setting: Optional[AzureClouds] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def begin_create_notifications_at_tenant_action_group_resource_level(
                self, 
                management_group_id: str, 
                tenant_action_group_name: str, 
                notification_request: TenantNotificationRequestBody, 
                *, 
                content_type: str = "application/json", 
                x_ms_client_tenant_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[TenantActionGroupTestNotificationDetailsResponse]: ...

        @overload
        async def begin_create_notifications_at_tenant_action_group_resource_level(
                self, 
                management_group_id: str, 
                tenant_action_group_name: str, 
                notification_request: TenantNotificationRequestBody, 
                *, 
                content_type: str = "application/json", 
                x_ms_client_tenant_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[TenantActionGroupTestNotificationDetailsResponse]: ...

        @overload
        async def begin_create_notifications_at_tenant_action_group_resource_level(
                self, 
                management_group_id: str, 
                tenant_action_group_name: str, 
                notification_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                x_ms_client_tenant_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[TenantActionGroupTestNotificationDetailsResponse]: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2023-05-01-preview', params_added_on={'2023-05-01-preview': ['api_version', 'management_group_id', 'tenant_action_group_name', 'notification_id', 'x_ms_client_tenant_id', 'accept']}, api_versions_list=['2023-05-01-preview'])
        async def get_test_notifications_at_tenant_action_group_resource_level(
                self, 
                management_group_id: str, 
                tenant_action_group_name: str, 
                notification_id: str, 
                *, 
                x_ms_client_tenant_id: str, 
                **kwargs: Any
            ) -> TenantActionGroupTestNotificationDetailsResponse: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


namespace azure.mgmt.monitor.aio.operations

    class azure.mgmt.monitor.aio.operations.ActionGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_notifications_at_action_group_resource_level(
                self, 
                resource_group_name: str, 
                action_group_name: str, 
                notification_request: NotificationRequestBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TestNotificationDetailsResponse]: ...

        @overload
        async def begin_create_notifications_at_action_group_resource_level(
                self, 
                resource_group_name: str, 
                action_group_name: str, 
                notification_request: NotificationRequestBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TestNotificationDetailsResponse]: ...

        @overload
        async def begin_create_notifications_at_action_group_resource_level(
                self, 
                resource_group_name: str, 
                action_group_name: str, 
                notification_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TestNotificationDetailsResponse]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2021-10-01', params_added_on={'2021-10-01': ['api_version', 'subscription_id', 'resource_group_name', 'action_group_name', 'network_security_perimeter_configuration_name']}, api_versions_list=['2021-10-01'])
        async def begin_reconcile_nsp(
                self, 
                resource_group_name: str, 
                action_group_name: str, 
                network_security_perimeter_configuration_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                action_group_name: str, 
                action_group: ActionGroupResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ActionGroupResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                action_group_name: str, 
                action_group: ActionGroupResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ActionGroupResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                action_group_name: str, 
                action_group: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ActionGroupResource: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2024-10-01-preview', params_added_on={'2024-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'action_group_name']}, api_versions_list=['2024-10-01-preview'])
        async def delete(
                self, 
                resource_group_name: str, 
                action_group_name: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def enable_receiver(
                self, 
                resource_group_name: str, 
                action_group_name: str, 
                enable_request: EnableRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def enable_receiver(
                self, 
                resource_group_name: str, 
                action_group_name: str, 
                enable_request: EnableRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def enable_receiver(
                self, 
                resource_group_name: str, 
                action_group_name: str, 
                enable_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2024-10-01-preview', params_added_on={'2024-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'action_group_name', 'accept']}, api_versions_list=['2024-10-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                action_group_name: str, 
                **kwargs: Any
            ) -> ActionGroupResource: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2021-10-01', params_added_on={'2021-10-01': ['api_version', 'subscription_id', 'resource_group_name', 'action_group_name', 'network_security_perimeter_configuration_name', 'accept']}, api_versions_list=['2021-10-01'])
        async def get_nsp(
                self, 
                resource_group_name: str, 
                action_group_name: str, 
                network_security_perimeter_configuration_name: str, 
                **kwargs: Any
            ) -> NetworkSecurityPerimeterConfiguration: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2024-10-01-preview', params_added_on={'2024-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'action_group_name', 'notification_id', 'accept']}, api_versions_list=['2024-10-01-preview'])
        async def get_test_notifications_at_action_group_resource_level(
                self, 
                resource_group_name: str, 
                action_group_name: str, 
                notification_id: str, 
                **kwargs: Any
            ) -> TestNotificationDetailsResponse: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-10-01-preview', params_added_on={'2024-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2024-10-01-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ActionGroupResource]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-10-01-preview', params_added_on={'2024-10-01-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2024-10-01-preview'])
        def list_by_subscription_id(self, **kwargs: Any) -> AsyncItemPaged[ActionGroupResource]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2021-10-01', params_added_on={'2021-10-01': ['api_version', 'subscription_id', 'resource_group_name', 'action_group_name', 'accept']}, api_versions_list=['2021-10-01'])
        def list_nsp(
                self, 
                resource_group_name: str, 
                action_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[NetworkSecurityPerimeterConfiguration]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                action_group_name: str, 
                action_group_patch: ActionGroupPatchBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ActionGroupResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                action_group_name: str, 
                action_group_patch: ActionGroupPatchBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ActionGroupResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                action_group_name: str, 
                action_group_patch: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ActionGroupResource: ...


    class azure.mgmt.monitor.aio.operations.ActivityLogAlertsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                activity_log_alert_name: str, 
                activity_log_alert_rule: ActivityLogAlertResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ActivityLogAlertResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                activity_log_alert_name: str, 
                activity_log_alert_rule: ActivityLogAlertResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ActivityLogAlertResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                activity_log_alert_name: str, 
                activity_log_alert_rule: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ActivityLogAlertResource: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                activity_log_alert_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                activity_log_alert_name: str, 
                **kwargs: Any
            ) -> ActivityLogAlertResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ActivityLogAlertResource]: ...

        @distributed_trace
        def list_by_subscription_id(self, **kwargs: Any) -> AsyncItemPaged[ActivityLogAlertResource]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                activity_log_alert_name: str, 
                activity_log_alert_rule_patch: AlertRulePatchObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ActivityLogAlertResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                activity_log_alert_name: str, 
                activity_log_alert_rule_patch: AlertRulePatchObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ActivityLogAlertResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                activity_log_alert_name: str, 
                activity_log_alert_rule_patch: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ActivityLogAlertResource: ...


    class azure.mgmt.monitor.aio.operations.ActivityLogsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                *, 
                filter: str, 
                select: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[EventData]: ...


    class azure.mgmt.monitor.aio.operations.AlertRuleIncidentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                rule_name: str, 
                incident_name: str, 
                **kwargs: Any
            ) -> Incident: ...

        @distributed_trace
        def list_by_alert_rule(
                self, 
                resource_group_name: str, 
                rule_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Incident]: ...


    class azure.mgmt.monitor.aio.operations.AutoscaleSettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                autoscale_setting_name: str, 
                parameters: AutoscaleSettingResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutoscaleSettingResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                autoscale_setting_name: str, 
                parameters: AutoscaleSettingResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutoscaleSettingResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                autoscale_setting_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutoscaleSettingResource: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                autoscale_setting_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                autoscale_setting_name: str, 
                **kwargs: Any
            ) -> AutoscaleSettingResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AutoscaleSettingResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[AutoscaleSettingResource]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                autoscale_setting_name: str, 
                autoscale_setting_resource: AutoscaleSettingResourcePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutoscaleSettingResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                autoscale_setting_name: str, 
                autoscale_setting_resource: AutoscaleSettingResourcePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutoscaleSettingResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                autoscale_setting_name: str, 
                autoscale_setting_resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutoscaleSettingResource: ...


    class azure.mgmt.monitor.aio.operations.BaselinesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_uri: str, 
                *, 
                aggregation: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                interval: Optional[timedelta] = ..., 
                metricnames: Optional[str] = ..., 
                metricnamespace: Optional[str] = ..., 
                result_type: Optional[Union[str, ResultType]] = ..., 
                sensitivities: Optional[str] = ..., 
                timespan: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[SingleMetricBaseline]: ...


    class azure.mgmt.monitor.aio.operations.DataCollectionEndpointsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2021-10-01', params_added_on={'2021-10-01': ['api_version', 'subscription_id', 'resource_group_name', 'data_collection_endpoint_name', 'network_security_perimeter_configuration_name']}, api_versions_list=['2021-10-01'])
        async def begin_reconcile_nsp(
                self, 
                resource_group_name: str, 
                data_collection_endpoint_name: str, 
                network_security_perimeter_configuration_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                data_collection_endpoint_name: str, 
                body: Optional[DataCollectionEndpointResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataCollectionEndpointResource: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                data_collection_endpoint_name: str, 
                body: Optional[DataCollectionEndpointResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataCollectionEndpointResource: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                data_collection_endpoint_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataCollectionEndpointResource: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2024-03-11', params_added_on={'2024-03-11': ['api_version', 'subscription_id', 'resource_group_name', 'data_collection_endpoint_name']}, api_versions_list=['2024-03-11'])
        async def delete(
                self, 
                resource_group_name: str, 
                data_collection_endpoint_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2024-03-11', params_added_on={'2024-03-11': ['api_version', 'subscription_id', 'resource_group_name', 'data_collection_endpoint_name', 'accept']}, api_versions_list=['2024-03-11'])
        async def get(
                self, 
                resource_group_name: str, 
                data_collection_endpoint_name: str, 
                **kwargs: Any
            ) -> DataCollectionEndpointResource: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2021-10-01', params_added_on={'2021-10-01': ['api_version', 'subscription_id', 'resource_group_name', 'data_collection_endpoint_name', 'network_security_perimeter_configuration_name', 'accept']}, api_versions_list=['2021-10-01'])
        async def get_nsp(
                self, 
                resource_group_name: str, 
                data_collection_endpoint_name: str, 
                network_security_perimeter_configuration_name: str, 
                **kwargs: Any
            ) -> NetworkSecurityPerimeterConfiguration: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-03-11', params_added_on={'2024-03-11': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2024-03-11'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DataCollectionEndpointResource]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-03-11', params_added_on={'2024-03-11': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2024-03-11'])
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[DataCollectionEndpointResource]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2021-10-01', params_added_on={'2021-10-01': ['api_version', 'subscription_id', 'resource_group_name', 'data_collection_endpoint_name', 'accept']}, api_versions_list=['2021-10-01'])
        def list_nsp(
                self, 
                resource_group_name: str, 
                data_collection_endpoint_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[NetworkSecurityPerimeterConfiguration]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                data_collection_endpoint_name: str, 
                body: Optional[ResourceForUpdate] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataCollectionEndpointResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                data_collection_endpoint_name: str, 
                body: Optional[ResourceForUpdate] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataCollectionEndpointResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                data_collection_endpoint_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataCollectionEndpointResource: ...


    class azure.mgmt.monitor.aio.operations.DataCollectionRuleAssociationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                resource_uri: str, 
                association_name: str, 
                body: Optional[DataCollectionRuleAssociationProxyOnlyResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataCollectionRuleAssociationProxyOnlyResource: ...

        @overload
        async def create(
                self, 
                resource_uri: str, 
                association_name: str, 
                body: Optional[DataCollectionRuleAssociationProxyOnlyResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataCollectionRuleAssociationProxyOnlyResource: ...

        @overload
        async def create(
                self, 
                resource_uri: str, 
                association_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataCollectionRuleAssociationProxyOnlyResource: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_uri: str, 
                association_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_uri: str, 
                association_name: str, 
                **kwargs: Any
            ) -> DataCollectionRuleAssociationProxyOnlyResource: ...

        @distributed_trace
        def list_by_data_collection_endpoint(
                self, 
                resource_group_name: str, 
                data_collection_endpoint_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DataCollectionRuleAssociationProxyOnlyResource]: ...

        @distributed_trace
        def list_by_resource(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DataCollectionRuleAssociationProxyOnlyResource]: ...

        @distributed_trace
        def list_by_rule(
                self, 
                resource_group_name: str, 
                data_collection_rule_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DataCollectionRuleAssociationProxyOnlyResource]: ...


    class azure.mgmt.monitor.aio.operations.DataCollectionRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                data_collection_rule_name: str, 
                body: Optional[DataCollectionRuleResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataCollectionRuleResource: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                data_collection_rule_name: str, 
                body: Optional[DataCollectionRuleResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataCollectionRuleResource: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                data_collection_rule_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataCollectionRuleResource: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                data_collection_rule_name: str, 
                *, 
                delete_associations: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                data_collection_rule_name: str, 
                **kwargs: Any
            ) -> DataCollectionRuleResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DataCollectionRuleResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[DataCollectionRuleResource]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                data_collection_rule_name: str, 
                body: Optional[ResourceForUpdate] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataCollectionRuleResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                data_collection_rule_name: str, 
                body: Optional[ResourceForUpdate] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataCollectionRuleResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                data_collection_rule_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataCollectionRuleResource: ...


    class azure.mgmt.monitor.aio.operations.DiagnosticSettingsCategoryOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_uri: str, 
                name: str, 
                **kwargs: Any
            ) -> DiagnosticSettingsCategoryResource: ...

        @distributed_trace
        def list(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DiagnosticSettingsCategoryResource]: ...


    class azure.mgmt.monitor.aio.operations.DiagnosticSettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_uri: str, 
                name: str, 
                parameters: DiagnosticSettingsResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DiagnosticSettingsResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_uri: str, 
                name: str, 
                parameters: DiagnosticSettingsResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DiagnosticSettingsResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_uri: str, 
                name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DiagnosticSettingsResource: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_uri: str, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_uri: str, 
                name: str, 
                **kwargs: Any
            ) -> DiagnosticSettingsResource: ...

        @distributed_trace
        def list(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DiagnosticSettingsResource]: ...


    class azure.mgmt.monitor.aio.operations.EventCategoriesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[LocalizableString]: ...


    class azure.mgmt.monitor.aio.operations.LogProfilesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                log_profile_name: str, 
                parameters: LogProfileResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LogProfileResource: ...

        @overload
        async def create_or_update(
                self, 
                log_profile_name: str, 
                parameters: LogProfileResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LogProfileResource: ...

        @overload
        async def create_or_update(
                self, 
                log_profile_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LogProfileResource: ...

        @distributed_trace_async
        async def delete(
                self, 
                log_profile_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                log_profile_name: str, 
                **kwargs: Any
            ) -> LogProfileResource: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[LogProfileResource]: ...

        @overload
        async def update(
                self, 
                log_profile_name: str, 
                log_profiles_resource: LogProfileResourcePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LogProfileResource: ...

        @overload
        async def update(
                self, 
                log_profile_name: str, 
                log_profiles_resource: LogProfileResourcePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LogProfileResource: ...

        @overload
        async def update(
                self, 
                log_profile_name: str, 
                log_profiles_resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LogProfileResource: ...


    class azure.mgmt.monitor.aio.operations.MetricAlertsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                rule_name: str, 
                parameters: MetricAlertResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MetricAlertResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                rule_name: str, 
                parameters: MetricAlertResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MetricAlertResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                rule_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MetricAlertResource: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                rule_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                rule_name: str, 
                **kwargs: Any
            ) -> MetricAlertResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[MetricAlertResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[MetricAlertResource]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                rule_name: str, 
                parameters: MetricAlertResourcePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MetricAlertResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                rule_name: str, 
                parameters: MetricAlertResourcePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MetricAlertResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                rule_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MetricAlertResource: ...


    class azure.mgmt.monitor.aio.operations.MetricAlertsStatusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def list(
                self, 
                resource_group_name: str, 
                rule_name: str, 
                **kwargs: Any
            ) -> MetricAlertStatusCollection: ...

        @distributed_trace_async
        async def list_by_name(
                self, 
                resource_group_name: str, 
                rule_name: str, 
                status_name: str, 
                **kwargs: Any
            ) -> MetricAlertStatusCollection: ...


    class azure.mgmt.monitor.aio.operations.MetricDefinitionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_uri: str, 
                *, 
                metricnamespace: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[MetricDefinition]: ...

        @distributed_trace
        def list_at_subscription_scope(
                self, 
                *, 
                metricnamespace: Optional[str] = ..., 
                region: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SubscriptionScopeMetricDefinition]: ...


    class azure.mgmt.monitor.aio.operations.MetricNamespacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_uri: str, 
                *, 
                start_time: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[MetricNamespace]: ...


    class azure.mgmt.monitor.aio.operations.MetricsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def list(
                self, 
                resource_uri: str, 
                *, 
                aggregation: Optional[str] = ..., 
                auto_adjust_timegrain: Optional[bool] = ..., 
                filter: Optional[str] = ..., 
                interval: Optional[str] = ..., 
                metricnames: Optional[str] = ..., 
                metricnamespace: Optional[str] = ..., 
                orderby: Optional[str] = ..., 
                result_type: Optional[Union[str, ResultType]] = ..., 
                rollupby: Optional[str] = ..., 
                timespan: Optional[str] = ..., 
                top: Optional[int] = ..., 
                validate_dimensions: Optional[bool] = ..., 
                **kwargs: Any
            ) -> Response: ...

        @distributed_trace_async
        async def list_at_subscription_scope(
                self, 
                *, 
                aggregation: Optional[str] = ..., 
                auto_adjust_timegrain: Optional[bool] = ..., 
                filter: Optional[str] = ..., 
                interval: Optional[str] = ..., 
                metricnames: Optional[str] = ..., 
                metricnamespace: Optional[str] = ..., 
                orderby: Optional[str] = ..., 
                region: str, 
                result_type: Optional[Union[str, MetricResultType]] = ..., 
                rollupby: Optional[str] = ..., 
                timespan: Optional[str] = ..., 
                top: Optional[int] = ..., 
                validate_dimensions: Optional[bool] = ..., 
                **kwargs: Any
            ) -> Response: ...

        @overload
        async def list_at_subscription_scope_post(
                self, 
                body: Optional[SubscriptionScopeMetricsRequestBodyParameters] = None, 
                *, 
                aggregation: Optional[str] = ..., 
                auto_adjust_timegrain: Optional[bool] = ..., 
                content_type: str = "application/json", 
                filter: Optional[str] = ..., 
                interval: Optional[str] = ..., 
                metricnames: Optional[str] = ..., 
                metricnamespace: Optional[str] = ..., 
                orderby: Optional[str] = ..., 
                region: str, 
                result_type: Optional[Union[str, MetricResultType]] = ..., 
                rollupby: Optional[str] = ..., 
                timespan: Optional[str] = ..., 
                top: Optional[int] = ..., 
                validate_dimensions: Optional[bool] = ..., 
                **kwargs: Any
            ) -> Response: ...

        @overload
        async def list_at_subscription_scope_post(
                self, 
                body: Optional[SubscriptionScopeMetricsRequestBodyParameters] = None, 
                *, 
                aggregation: Optional[str] = ..., 
                auto_adjust_timegrain: Optional[bool] = ..., 
                content_type: str = "application/json", 
                filter: Optional[str] = ..., 
                interval: Optional[str] = ..., 
                metricnames: Optional[str] = ..., 
                metricnamespace: Optional[str] = ..., 
                orderby: Optional[str] = ..., 
                region: str, 
                result_type: Optional[Union[str, MetricResultType]] = ..., 
                rollupby: Optional[str] = ..., 
                timespan: Optional[str] = ..., 
                top: Optional[int] = ..., 
                validate_dimensions: Optional[bool] = ..., 
                **kwargs: Any
            ) -> Response: ...

        @overload
        async def list_at_subscription_scope_post(
                self, 
                body: Optional[IO[bytes]] = None, 
                *, 
                aggregation: Optional[str] = ..., 
                auto_adjust_timegrain: Optional[bool] = ..., 
                content_type: str = "application/json", 
                filter: Optional[str] = ..., 
                interval: Optional[str] = ..., 
                metricnames: Optional[str] = ..., 
                metricnamespace: Optional[str] = ..., 
                orderby: Optional[str] = ..., 
                region: str, 
                result_type: Optional[Union[str, MetricResultType]] = ..., 
                rollupby: Optional[str] = ..., 
                timespan: Optional[str] = ..., 
                top: Optional[int] = ..., 
                validate_dimensions: Optional[bool] = ..., 
                **kwargs: Any
            ) -> Response: ...


    class azure.mgmt.monitor.aio.operations.PredictiveMetricOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                autoscale_setting_name: str, 
                *, 
                aggregation: str, 
                interval: timedelta, 
                metric_name: str, 
                metric_namespace: str, 
                timespan: str, 
                **kwargs: Any
            ) -> PredictiveResponse: ...


    class azure.mgmt.monitor.aio.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                private_endpoint_connection_name: str, 
                parameters: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                private_endpoint_connection_name: str, 
                parameters: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                private_endpoint_connection_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list_by_private_link_scope(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateEndpointConnection]: ...


    class azure.mgmt.monitor.aio.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                group_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @distributed_trace
        def list_by_private_link_scope(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateLinkResource]: ...


    class azure.mgmt.monitor.aio.operations.PrivateLinkScopeOperationStatusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                async_operation_id: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> OperationStatus: ...


    class azure.mgmt.monitor.aio.operations.PrivateLinkScopedResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                name: str, 
                parameters: ScopedResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ScopedResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                name: str, 
                parameters: ScopedResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ScopedResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ScopedResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                name: str, 
                **kwargs: Any
            ) -> ScopedResource: ...

        @distributed_trace
        def list_by_private_link_scope(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                *, 
                kind: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ScopedResource]: ...


    class azure.mgmt.monitor.aio.operations.PrivateLinkScopesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                azure_monitor_private_link_scope_payload: AzureMonitorPrivateLinkScope, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureMonitorPrivateLinkScope: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                azure_monitor_private_link_scope_payload: AzureMonitorPrivateLinkScope, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureMonitorPrivateLinkScope: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                azure_monitor_private_link_scope_payload: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureMonitorPrivateLinkScope: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                **kwargs: Any
            ) -> AzureMonitorPrivateLinkScope: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[AzureMonitorPrivateLinkScope]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AzureMonitorPrivateLinkScope]: ...

        @overload
        async def update_tags(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                private_link_scope_tags: TagsResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureMonitorPrivateLinkScope: ...

        @overload
        async def update_tags(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                private_link_scope_tags: TagsResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureMonitorPrivateLinkScope: ...

        @overload
        async def update_tags(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                private_link_scope_tags: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureMonitorPrivateLinkScope: ...


    class azure.mgmt.monitor.aio.operations.ScheduledQueryRuleOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_reconcile_nsp(
                self, 
                resource_group_name: str, 
                rule_name: str, 
                network_security_perimeter_configuration_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get_nsp(
                self, 
                resource_group_name: str, 
                rule_name: str, 
                network_security_perimeter_configuration_name: str, 
                **kwargs: Any
            ) -> NetworkSecurityPerimeterConfiguration: ...

        @distributed_trace
        def list_nsp(
                self, 
                resource_group_name: str, 
                rule_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[NetworkSecurityPerimeterConfiguration]: ...


    class azure.mgmt.monitor.aio.operations.ScheduledQueryRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                rule_name: str, 
                parameters: ScheduledQueryRuleResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ScheduledQueryRuleResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                rule_name: str, 
                parameters: ScheduledQueryRuleResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ScheduledQueryRuleResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                rule_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ScheduledQueryRuleResource: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                rule_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                rule_name: str, 
                **kwargs: Any
            ) -> ScheduledQueryRuleResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ScheduledQueryRuleResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[ScheduledQueryRuleResource]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                rule_name: str, 
                parameters: ScheduledQueryRuleResourcePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ScheduledQueryRuleResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                rule_name: str, 
                parameters: ScheduledQueryRuleResourcePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ScheduledQueryRuleResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                rule_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ScheduledQueryRuleResource: ...


    class azure.mgmt.monitor.aio.operations.ServiceDiagnosticSettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_uri: str, 
                parameters: ServiceDiagnosticSettingsResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServiceDiagnosticSettingsResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_uri: str, 
                parameters: ServiceDiagnosticSettingsResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServiceDiagnosticSettingsResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_uri: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServiceDiagnosticSettingsResource: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> ServiceDiagnosticSettingsResource: ...

        @overload
        async def update(
                self, 
                resource_uri: str, 
                service_diagnostic_settings_resource: ServiceDiagnosticSettingsResourcePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServiceDiagnosticSettingsResource: ...

        @overload
        async def update(
                self, 
                resource_uri: str, 
                service_diagnostic_settings_resource: ServiceDiagnosticSettingsResourcePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServiceDiagnosticSettingsResource: ...

        @overload
        async def update(
                self, 
                resource_uri: str, 
                service_diagnostic_settings_resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServiceDiagnosticSettingsResource: ...


    class azure.mgmt.monitor.aio.operations.TenantActionGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                management_group_id: str, 
                tenant_action_group_name: str, 
                action_group: TenantActionGroupResource, 
                *, 
                content_type: str = "application/json", 
                x_ms_client_tenant_id: str, 
                **kwargs: Any
            ) -> TenantActionGroupResource: ...

        @overload
        async def create_or_update(
                self, 
                management_group_id: str, 
                tenant_action_group_name: str, 
                action_group: TenantActionGroupResource, 
                *, 
                content_type: str = "application/json", 
                x_ms_client_tenant_id: str, 
                **kwargs: Any
            ) -> TenantActionGroupResource: ...

        @overload
        async def create_or_update(
                self, 
                management_group_id: str, 
                tenant_action_group_name: str, 
                action_group: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                x_ms_client_tenant_id: str, 
                **kwargs: Any
            ) -> TenantActionGroupResource: ...

        @distributed_trace_async
        async def delete(
                self, 
                management_group_id: str, 
                tenant_action_group_name: str, 
                *, 
                x_ms_client_tenant_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                management_group_id: str, 
                tenant_action_group_name: str, 
                *, 
                x_ms_client_tenant_id: str, 
                **kwargs: Any
            ) -> TenantActionGroupResource: ...

        @distributed_trace
        def list_by_management_group_id(
                self, 
                management_group_id: str, 
                *, 
                x_ms_client_tenant_id: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[TenantActionGroupResource]: ...

        @overload
        async def update(
                self, 
                management_group_id: str, 
                tenant_action_group_name: str, 
                tenant_action_group_patch: TenantActionGroupPatchBody, 
                *, 
                content_type: str = "application/json", 
                x_ms_client_tenant_id: str, 
                **kwargs: Any
            ) -> TenantActionGroupResource: ...

        @overload
        async def update(
                self, 
                management_group_id: str, 
                tenant_action_group_name: str, 
                tenant_action_group_patch: TenantActionGroupPatchBody, 
                *, 
                content_type: str = "application/json", 
                x_ms_client_tenant_id: str, 
                **kwargs: Any
            ) -> TenantActionGroupResource: ...

        @overload
        async def update(
                self, 
                management_group_id: str, 
                tenant_action_group_name: str, 
                tenant_action_group_patch: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                x_ms_client_tenant_id: str, 
                **kwargs: Any
            ) -> TenantActionGroupResource: ...


    class azure.mgmt.monitor.aio.operations.TenantActivityLogsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                *, 
                filter: Optional[str] = ..., 
                select: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[EventData]: ...


    class azure.mgmt.monitor.aio.operations.VMInsightsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get_onboarding_status(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> VMInsightsOnboardingStatus: ...


namespace azure.mgmt.monitor.models

    class azure.mgmt.monitor.models.AccessMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OPEN = "Open"
        PRIVATE_ONLY = "PrivateOnly"


    class azure.mgmt.monitor.models.AccessModeSettings(_Model):
        exclusions: Optional[list[AccessModeSettingsExclusion]]
        ingestion_access_mode: Union[str, AccessMode]
        query_access_mode: Union[str, AccessMode]

        @overload
        def __init__(
                self, 
                *, 
                exclusions: Optional[list[AccessModeSettingsExclusion]] = ..., 
                ingestion_access_mode: Union[str, AccessMode], 
                query_access_mode: Union[str, AccessMode]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.AccessModeSettingsExclusion(_Model):
        ingestion_access_mode: Optional[Union[str, AccessMode]]
        private_endpoint_connection_name: Optional[str]
        query_access_mode: Optional[Union[str, AccessMode]]

        @overload
        def __init__(
                self, 
                *, 
                ingestion_access_mode: Optional[Union[str, AccessMode]] = ..., 
                private_endpoint_connection_name: Optional[str] = ..., 
                query_access_mode: Optional[Union[str, AccessMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.AccessRule(_Model):
        name: Optional[str]
        properties: Optional[AccessRuleProperties]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                properties: Optional[AccessRuleProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.AccessRuleDirection(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INBOUND = "Inbound"
        OUTBOUND = "Outbound"


    class azure.mgmt.monitor.models.AccessRuleProperties(_Model):
        address_prefixes: Optional[list[str]]
        direction: Optional[Union[str, AccessRuleDirection]]
        email_addresses: Optional[list[str]]
        fully_qualified_domain_names: Optional[list[str]]
        network_security_perimeters: Optional[list[NetworkSecurityPerimeter]]
        phone_numbers: Optional[list[str]]
        subscriptions: Optional[list[AccessRulePropertiesSubscription]]

        @overload
        def __init__(
                self, 
                *, 
                address_prefixes: Optional[list[str]] = ..., 
                direction: Optional[Union[str, AccessRuleDirection]] = ..., 
                email_addresses: Optional[list[str]] = ..., 
                fully_qualified_domain_names: Optional[list[str]] = ..., 
                network_security_perimeters: Optional[list[NetworkSecurityPerimeter]] = ..., 
                phone_numbers: Optional[list[str]] = ..., 
                subscriptions: Optional[list[AccessRulePropertiesSubscription]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.AccessRulePropertiesSubscription(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.ActionDetail(_Model):
        detail: Optional[str]
        mechanism_type: Optional[str]
        name: Optional[str]
        send_time: Optional[str]
        status: Optional[str]
        sub_state: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                detail: Optional[str] = ..., 
                mechanism_type: Optional[str] = ..., 
                name: Optional[str] = ..., 
                send_time: Optional[str] = ..., 
                status: Optional[str] = ..., 
                sub_state: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.ActionGroup(_Model):
        action_group_id: str
        action_properties: Optional[dict[str, str]]
        webhook_properties: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                action_group_id: str, 
                action_properties: Optional[dict[str, str]] = ..., 
                webhook_properties: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.ActionGroupPatch(_Model):
        enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.ActionGroupPatchBody(_Model):
        identity: Optional[ManagedServiceIdentity]
        properties: Optional[ActionGroupPatch]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                properties: Optional[ActionGroupPatch] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.monitor.models.ActionGroupResource(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: Optional[ActionGroupResourceProperties]
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
                properties: Optional[ActionGroupResourceProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.monitor.models.ActionGroupResourceProperties(_Model):
        arm_role_receivers: Optional[list[ArmRoleReceiver]]
        automation_runbook_receivers: Optional[list[AutomationRunbookReceiver]]
        azure_app_push_receivers: Optional[list[AzureAppPushReceiver]]
        azure_function_receivers: Optional[list[AzureFunctionReceiver]]
        email_receivers: Optional[list[EmailReceiver]]
        enabled: bool
        event_hub_receivers: Optional[list[EventHubReceiver]]
        group_short_name: str
        incident_receivers: Optional[list[IncidentReceiver]]
        itsm_receivers: Optional[list[ItsmReceiver]]
        logic_app_receivers: Optional[list[LogicAppReceiver]]
        sms_receivers: Optional[list[SmsReceiver]]
        voice_receivers: Optional[list[VoiceReceiver]]
        webhook_receivers: Optional[list[WebhookReceiver]]

        @overload
        def __init__(
                self, 
                *, 
                arm_role_receivers: Optional[list[ArmRoleReceiver]] = ..., 
                automation_runbook_receivers: Optional[list[AutomationRunbookReceiver]] = ..., 
                azure_app_push_receivers: Optional[list[AzureAppPushReceiver]] = ..., 
                azure_function_receivers: Optional[list[AzureFunctionReceiver]] = ..., 
                email_receivers: Optional[list[EmailReceiver]] = ..., 
                enabled: bool, 
                event_hub_receivers: Optional[list[EventHubReceiver]] = ..., 
                group_short_name: str, 
                incident_receivers: Optional[list[IncidentReceiver]] = ..., 
                itsm_receivers: Optional[list[ItsmReceiver]] = ..., 
                logic_app_receivers: Optional[list[LogicAppReceiver]] = ..., 
                sms_receivers: Optional[list[SmsReceiver]] = ..., 
                voice_receivers: Optional[list[VoiceReceiver]] = ..., 
                webhook_receivers: Optional[list[WebhookReceiver]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.ActionList(_Model):
        action_groups: Optional[list[ActionGroup]]

        @overload
        def __init__(
                self, 
                *, 
                action_groups: Optional[list[ActionGroup]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.Actions(_Model):
        action_groups: Optional[list[str]]
        action_properties: Optional[dict[str, str]]
        custom_properties: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                action_groups: Optional[list[str]] = ..., 
                action_properties: Optional[dict[str, str]] = ..., 
                custom_properties: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.ActivityLogAlertErrorResponse(_Model):
        code: Optional[str]
        message: Optional[str]


    class azure.mgmt.monitor.models.ActivityLogAlertResource(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[AlertRuleProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[AlertRuleProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.monitor.models.AdxDestination(_Model):
        database_name: Optional[str]
        ingestion_uri: Optional[str]
        name: Optional[str]
        resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                database_name: Optional[str] = ..., 
                name: Optional[str] = ..., 
                resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.AgentSetting(_Model):
        name: Optional[Union[str, KnownAgentSettingName]]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[Union[str, KnownAgentSettingName]] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.AgentSettingsSpec(_Model):
        logs: Optional[list[AgentSetting]]

        @overload
        def __init__(
                self, 
                *, 
                logs: Optional[list[AgentSetting]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.AggregationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVERAGE = "Average"
        COUNT = "Count"
        MAXIMUM = "Maximum"
        MINIMUM = "Minimum"
        NONE = "None"
        TOTAL = "Total"


    class azure.mgmt.monitor.models.AggregationTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVERAGE = "Average"
        COUNT = "Count"
        MAXIMUM = "Maximum"
        MINIMUM = "Minimum"
        TOTAL = "Total"


    class azure.mgmt.monitor.models.AlertRuleAllOfCondition(_Model):
        all_of: list[AlertRuleAnyOfOrLeafCondition]

        @overload
        def __init__(
                self, 
                *, 
                all_of: list[AlertRuleAnyOfOrLeafCondition]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.AlertRuleAnyOfOrLeafCondition(AlertRuleLeafCondition):
        any_of: Optional[list[AlertRuleLeafCondition]]
        contains_any: list[str]
        equals: str
        field: str

        @overload
        def __init__(
                self, 
                *, 
                any_of: Optional[list[AlertRuleLeafCondition]] = ..., 
                contains_any: Optional[list[str]] = ..., 
                equals: Optional[str] = ..., 
                field: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.AlertRuleLeafCondition(_Model):
        contains_any: Optional[list[str]]
        equals: Optional[str]
        field: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                contains_any: Optional[list[str]] = ..., 
                equals: Optional[str] = ..., 
                field: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.AlertRulePatchObject(_Model):
        properties: Optional[AlertRulePatchProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AlertRulePatchProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.monitor.models.AlertRulePatchProperties(_Model):
        enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.AlertRuleProperties(_Model):
        actions: ActionList
        condition: AlertRuleAllOfCondition
        description: Optional[str]
        enabled: Optional[bool]
        scopes: Optional[list[str]]
        tenant_scope: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                actions: ActionList, 
                condition: AlertRuleAllOfCondition, 
                description: Optional[str] = ..., 
                enabled: Optional[bool] = ..., 
                scopes: Optional[list[str]] = ..., 
                tenant_scope: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.AlertSeverity(int, Enum, metaclass=CaseInsensitiveEnumMeta):
        FOUR = 4
        ONE = 1
        THREE = 3
        TWO = 2
        ZERO = 0


    class azure.mgmt.monitor.models.ApplicationInsights(_Model):
        name: str
        resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.ArmRoleReceiver(_Model):
        name: str
        role_id: str
        use_common_alert_schema: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                role_id: str, 
                use_common_alert_schema: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.AutomationRunbookReceiver(_Model):
        automation_account_id: str
        is_global_runbook: bool
        managed_identity: Optional[str]
        name: Optional[str]
        runbook_name: str
        service_uri: Optional[str]
        use_common_alert_schema: Optional[bool]
        webhook_resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                automation_account_id: str, 
                is_global_runbook: bool, 
                managed_identity: Optional[str] = ..., 
                name: Optional[str] = ..., 
                runbook_name: str, 
                service_uri: Optional[str] = ..., 
                use_common_alert_schema: Optional[bool] = ..., 
                webhook_resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.AutoscaleErrorResponse(_Model):
        error: Optional[AutoscaleErrorResponseError]
        system_data: Optional[SystemData]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[AutoscaleErrorResponseError] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.AutoscaleErrorResponseError(_Model):
        code: Optional[str]
        details: Optional[str]
        message: Optional[str]
        target: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                details: Optional[str] = ..., 
                message: Optional[str] = ..., 
                target: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.AutoscaleNotification(_Model):
        email: Optional[EmailNotification]
        operation: Union[str, OperationType]
        webhooks: Optional[list[WebhookNotification]]

        @overload
        def __init__(
                self, 
                *, 
                email: Optional[EmailNotification] = ..., 
                operation: Union[str, OperationType], 
                webhooks: Optional[list[WebhookNotification]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.AutoscaleProfile(_Model):
        capacity: ScaleCapacity
        fixed_date: Optional[TimeWindow]
        name: str
        recurrence: Optional[Recurrence]
        rules: list[ScaleRule]

        @overload
        def __init__(
                self, 
                *, 
                capacity: ScaleCapacity, 
                fixed_date: Optional[TimeWindow] = ..., 
                name: str, 
                recurrence: Optional[Recurrence] = ..., 
                rules: list[ScaleRule]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.AutoscaleSetting(_Model):
        enabled: Optional[bool]
        name: Optional[str]
        notifications: Optional[list[AutoscaleNotification]]
        predictive_autoscale_policy: Optional[PredictiveAutoscalePolicy]
        profiles: list[AutoscaleProfile]
        target_resource_location: Optional[str]
        target_resource_uri: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                name: Optional[str] = ..., 
                notifications: Optional[list[AutoscaleNotification]] = ..., 
                predictive_autoscale_policy: Optional[PredictiveAutoscalePolicy] = ..., 
                profiles: list[AutoscaleProfile], 
                target_resource_location: Optional[str] = ..., 
                target_resource_uri: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.AutoscaleSettingResource(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: AutoscaleSetting
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
                properties: AutoscaleSetting, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.monitor.models.AutoscaleSettingResourcePatch(_Model):
        identity: Optional[ManagedServiceIdentity]
        properties: Optional[AutoscaleSetting]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                properties: Optional[AutoscaleSetting] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.monitor.models.AzureAppPushReceiver(_Model):
        email_address: str
        name: str

        @overload
        def __init__(
                self, 
                *, 
                email_address: str, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.AzureFunctionReceiver(_Model):
        function_app_resource_id: str
        function_name: str
        http_trigger_url: str
        managed_identity: Optional[str]
        name: str
        use_common_alert_schema: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                function_app_resource_id: str, 
                function_name: str, 
                http_trigger_url: str, 
                managed_identity: Optional[str] = ..., 
                name: str, 
                use_common_alert_schema: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.AzureMonitorMetricsDestination(_Model):
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.AzureMonitorPrivateLinkScope(TrackedResource):
        id: str
        location: str
        name: str
        properties: AzureMonitorPrivateLinkScopeProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: AzureMonitorPrivateLinkScopeProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.monitor.models.AzureMonitorPrivateLinkScopeProperties(_Model):
        access_mode_settings: AccessModeSettings
        private_endpoint_connections: Optional[list[PrivateEndpointConnection]]
        provisioning_state: Optional[Union[str, PrivateLinkScopeProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                access_mode_settings: AccessModeSettings
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.BaselineMetadata(_Model):
        name: str
        value: str

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.BaselineSensitivity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "High"
        LOW = "Low"
        MEDIUM = "Medium"


    class azure.mgmt.monitor.models.CategoryType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOGS = "Logs"
        METRICS = "Metrics"


    class azure.mgmt.monitor.models.ColumnDefinition(_Model):
        name: Optional[str]
        type: Optional[Union[str, KnownColumnDefinitionType]]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                type: Optional[Union[str, KnownColumnDefinitionType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.ComparisonOperationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EQUALS = "Equals"
        GREATER_THAN = "GreaterThan"
        GREATER_THAN_OR_EQUAL = "GreaterThanOrEqual"
        LESS_THAN = "LessThan"
        LESS_THAN_OR_EQUAL = "LessThanOrEqual"
        NOT_EQUALS = "NotEquals"


    class azure.mgmt.monitor.models.Condition(_Model):
        alert_sensitivity: Optional[str]
        criterion_type: Optional[Union[str, CriterionType]]
        dimensions: Optional[list[Dimension]]
        failing_periods: Optional[ConditionFailingPeriods]
        ignore_data_before: Optional[datetime]
        metric_measure_column: Optional[str]
        metric_name: Optional[str]
        min_recurrence_count: Optional[int]
        operator: Optional[Union[str, ConditionOperator]]
        query: Optional[str]
        resource_id_column: Optional[str]
        threshold: Optional[float]
        time_aggregation: Optional[Union[str, TimeAggregation]]

        @overload
        def __init__(
                self, 
                *, 
                alert_sensitivity: Optional[str] = ..., 
                criterion_type: Optional[Union[str, CriterionType]] = ..., 
                dimensions: Optional[list[Dimension]] = ..., 
                failing_periods: Optional[ConditionFailingPeriods] = ..., 
                ignore_data_before: Optional[datetime] = ..., 
                metric_measure_column: Optional[str] = ..., 
                metric_name: Optional[str] = ..., 
                min_recurrence_count: Optional[int] = ..., 
                operator: Optional[Union[str, ConditionOperator]] = ..., 
                query: Optional[str] = ..., 
                resource_id_column: Optional[str] = ..., 
                threshold: Optional[float] = ..., 
                time_aggregation: Optional[Union[str, TimeAggregation]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.ConditionFailingPeriods(_Model):
        min_failing_periods_to_alert: Optional[int]
        number_of_evaluation_periods: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                min_failing_periods_to_alert: Optional[int] = ..., 
                number_of_evaluation_periods: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.ConditionOperator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EQUALS = "Equals"
        GREATER_OR_LESS_THAN = "GreaterOrLessThan"
        GREATER_THAN = "GreaterThan"
        GREATER_THAN_OR_EQUAL = "GreaterThanOrEqual"
        LESS_THAN = "LessThan"
        LESS_THAN_OR_EQUAL = "LessThanOrEqual"


    class azure.mgmt.monitor.models.ConfigurationAccessEndpointSpec(_Model):
        endpoint: Optional[str]


    class azure.mgmt.monitor.models.Context(_Model):
        context_type: Optional[str]
        notification_source: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                context_type: Optional[str] = ..., 
                notification_source: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.monitor.models.CriterionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DYNAMIC_THRESHOLD_CRITERION = "DynamicThresholdCriterion"
        STATIC_THRESHOLD_CRITERION = "StaticThresholdCriterion"


    class azure.mgmt.monitor.models.DataCollectionEndpoint(_Model):
        configuration_access: Optional[DataCollectionEndpointConfigurationAccess]
        description: Optional[str]
        failover_configuration: Optional[DataCollectionEndpointFailoverConfiguration]
        immutable_id: Optional[str]
        logs_ingestion: Optional[DataCollectionEndpointLogsIngestion]
        metadata: Optional[DataCollectionEndpointMetadata]
        metrics_ingestion: Optional[DataCollectionEndpointMetricsIngestion]
        network_acls: Optional[DataCollectionEndpointNetworkAcls]
        private_link_scoped_resources: Optional[list[PrivateLinkScopedResource]]
        provisioning_state: Optional[Union[str, KnownDataCollectionEndpointProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                configuration_access: Optional[DataCollectionEndpointConfigurationAccess] = ..., 
                description: Optional[str] = ..., 
                immutable_id: Optional[str] = ..., 
                logs_ingestion: Optional[DataCollectionEndpointLogsIngestion] = ..., 
                metrics_ingestion: Optional[DataCollectionEndpointMetricsIngestion] = ..., 
                network_acls: Optional[DataCollectionEndpointNetworkAcls] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.DataCollectionEndpointConfigurationAccess(ConfigurationAccessEndpointSpec):
        endpoint: str


    class azure.mgmt.monitor.models.DataCollectionEndpointFailoverConfiguration(FailoverConfigurationSpec):
        active_location: str
        locations: list[LocationSpec]

        @overload
        def __init__(
                self, 
                *, 
                active_location: Optional[str] = ..., 
                locations: Optional[list[LocationSpec]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.DataCollectionEndpointLogsIngestion(LogsIngestionEndpointSpec):
        endpoint: str


    class azure.mgmt.monitor.models.DataCollectionEndpointMetadata(Metadata):
        provisioned_by: str
        provisioned_by_immutable_id: str
        provisioned_by_resource_id: str


    class azure.mgmt.monitor.models.DataCollectionEndpointMetricsIngestion(MetricsIngestionEndpointSpec):
        endpoint: str


    class azure.mgmt.monitor.models.DataCollectionEndpointNetworkAcls(NetworkRuleSet):
        public_network_access: Union[str, KnownPublicNetworkAccessOptions]

        @overload
        def __init__(
                self, 
                *, 
                public_network_access: Optional[Union[str, KnownPublicNetworkAccessOptions]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.DataCollectionEndpointResource(TrackedResource):
        etag: Optional[str]
        id: str
        identity: Optional[DataCollectionEndpointResourceIdentity]
        kind: Optional[Union[str, KnownDataCollectionEndpointResourceKind]]
        location: str
        name: str
        properties: Optional[DataCollectionEndpointResourceProperties]
        sku: Optional[DataCollectionEndpointResourceSku]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[DataCollectionEndpointResourceIdentity] = ..., 
                kind: Optional[Union[str, KnownDataCollectionEndpointResourceKind]] = ..., 
                location: str, 
                properties: Optional[DataCollectionEndpointResourceProperties] = ..., 
                sku: Optional[DataCollectionEndpointResourceSku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.monitor.models.DataCollectionEndpointResourceIdentity(ManagedServiceIdentity):
        principal_id: str
        tenant_id: str
        type: Union[str, ManagedServiceIdentityType]
        user_assigned_identities: dict[str, UserAssignedIdentity]

        @overload
        def __init__(
                self, 
                *, 
                type: Union[str, ManagedServiceIdentityType], 
                user_assigned_identities: Optional[dict[str, UserAssignedIdentity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.DataCollectionEndpointResourceProperties(DataCollectionEndpoint):
        configuration_access: DataCollectionEndpointConfigurationAccess
        description: str
        failover_configuration: DataCollectionEndpointFailoverConfiguration
        immutable_id: str
        logs_ingestion: DataCollectionEndpointLogsIngestion
        metadata: DataCollectionEndpointMetadata
        metrics_ingestion: DataCollectionEndpointMetricsIngestion
        network_acls: DataCollectionEndpointNetworkAcls
        private_link_scoped_resources: list[PrivateLinkScopedResource]
        provisioning_state: Union[str, KnownDataCollectionEndpointProvisioningState]

        @overload
        def __init__(
                self, 
                *, 
                configuration_access: Optional[DataCollectionEndpointConfigurationAccess] = ..., 
                description: Optional[str] = ..., 
                immutable_id: Optional[str] = ..., 
                logs_ingestion: Optional[DataCollectionEndpointLogsIngestion] = ..., 
                metrics_ingestion: Optional[DataCollectionEndpointMetricsIngestion] = ..., 
                network_acls: Optional[DataCollectionEndpointNetworkAcls] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.DataCollectionEndpointResourceSku(Sku):
        capacity: int
        family: str
        name: str
        size: str
        tier: Union[str, SkuTier]

        @overload
        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                family: Optional[str] = ..., 
                name: str, 
                size: Optional[str] = ..., 
                tier: Optional[Union[str, SkuTier]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.DataCollectionRule(_Model):
        agent_settings: Optional[DataCollectionRuleAgentSettings]
        data_collection_endpoint_id: Optional[str]
        data_flows: Optional[list[DataFlow]]
        data_sources: Optional[DataCollectionRuleDataSources]
        description: Optional[str]
        destinations: Optional[DataCollectionRuleDestinations]
        direct_data_sources: Optional[DataCollectionRuleDirectDataSources]
        endpoints: Optional[DataCollectionRuleEndpoints]
        immutable_id: Optional[str]
        ingestion_quotas: Optional[DataCollectionRuleIngestionQuotas]
        metadata: Optional[DataCollectionRuleMetadata]
        provisioning_state: Optional[Union[str, KnownDataCollectionRuleProvisioningState]]
        references: Optional[DataCollectionRuleReferences]
        stream_declarations: Optional[dict[str, StreamDeclaration]]

        @overload
        def __init__(
                self, 
                *, 
                agent_settings: Optional[DataCollectionRuleAgentSettings] = ..., 
                data_collection_endpoint_id: Optional[str] = ..., 
                data_flows: Optional[list[DataFlow]] = ..., 
                data_sources: Optional[DataCollectionRuleDataSources] = ..., 
                description: Optional[str] = ..., 
                destinations: Optional[DataCollectionRuleDestinations] = ..., 
                direct_data_sources: Optional[DataCollectionRuleDirectDataSources] = ..., 
                references: Optional[DataCollectionRuleReferences] = ..., 
                stream_declarations: Optional[dict[str, StreamDeclaration]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.DataCollectionRuleAgentSettings(AgentSettingsSpec):
        logs: list[AgentSetting]

        @overload
        def __init__(
                self, 
                *, 
                logs: Optional[list[AgentSetting]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.DataCollectionRuleAssociation(_Model):
        data_collection_endpoint_id: Optional[str]
        data_collection_rule_id: Optional[str]
        description: Optional[str]
        metadata: Optional[DataCollectionRuleAssociationMetadata]
        provisioning_state: Optional[Union[str, KnownDataCollectionRuleAssociationProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                data_collection_endpoint_id: Optional[str] = ..., 
                data_collection_rule_id: Optional[str] = ..., 
                description: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.DataCollectionRuleAssociationMetadata(Metadata):
        provisioned_by: str
        provisioned_by_immutable_id: str
        provisioned_by_resource_id: str


    class azure.mgmt.monitor.models.DataCollectionRuleAssociationProxyOnlyResource(ExtensionResource):
        etag: Optional[str]
        id: str
        name: str
        properties: Optional[DataCollectionRuleAssociationProxyOnlyResourceProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DataCollectionRuleAssociationProxyOnlyResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.monitor.models.DataCollectionRuleAssociationProxyOnlyResourceProperties(DataCollectionRuleAssociation):
        data_collection_endpoint_id: str
        data_collection_rule_id: str
        description: str
        metadata: DataCollectionRuleAssociationMetadata
        provisioning_state: Union[str, KnownDataCollectionRuleAssociationProvisioningState]

        @overload
        def __init__(
                self, 
                *, 
                data_collection_endpoint_id: Optional[str] = ..., 
                data_collection_rule_id: Optional[str] = ..., 
                description: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.DataCollectionRuleDataSources(DataSourcesSpec):
        data_imports: DataSourcesSpecDataImports
        etw_providers: list[EtwProviderDataSource]
        extensions: list[ExtensionDataSource]
        iis_logs: list[IisLogsDataSource]
        log_files: list[LogFilesDataSource]
        otel_logs: list[OtelLogsDataSource]
        otel_metrics: list[OtelMetricsDataSource]
        otel_traces: list[OtelTracesDataSource]
        performance_counters: list[PerfCounterDataSource]
        performance_counters_o_tel: list[PerformanceCountersOTelDataSource]
        platform_telemetry: list[PlatformTelemetryDataSource]
        prometheus_forwarder: list[PrometheusForwarderDataSource]
        syslog: list[SyslogDataSource]
        windows_event_logs: list[WindowsEventLogDataSource]
        windows_firewall_logs: list[WindowsFirewallLogsDataSource]

        @overload
        def __init__(
                self, 
                *, 
                data_imports: Optional[DataSourcesSpecDataImports] = ..., 
                etw_providers: Optional[list[EtwProviderDataSource]] = ..., 
                extensions: Optional[list[ExtensionDataSource]] = ..., 
                iis_logs: Optional[list[IisLogsDataSource]] = ..., 
                log_files: Optional[list[LogFilesDataSource]] = ..., 
                otel_logs: Optional[list[OtelLogsDataSource]] = ..., 
                otel_metrics: Optional[list[OtelMetricsDataSource]] = ..., 
                otel_traces: Optional[list[OtelTracesDataSource]] = ..., 
                performance_counters: Optional[list[PerfCounterDataSource]] = ..., 
                performance_counters_o_tel: Optional[list[PerformanceCountersOTelDataSource]] = ..., 
                platform_telemetry: Optional[list[PlatformTelemetryDataSource]] = ..., 
                prometheus_forwarder: Optional[list[PrometheusForwarderDataSource]] = ..., 
                syslog: Optional[list[SyslogDataSource]] = ..., 
                windows_event_logs: Optional[list[WindowsEventLogDataSource]] = ..., 
                windows_firewall_logs: Optional[list[WindowsFirewallLogsDataSource]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.DataCollectionRuleDestinations(DestinationsSpec):
        azure_data_explorer: list[AdxDestination]
        azure_monitor_metrics: DestinationsSpecAzureMonitorMetrics
        event_hubs: list[EventHubDestination]
        event_hubs_direct: list[EventHubDirectDestination]
        log_analytics: list[LogAnalyticsDestination]
        microsoft_fabric: list[MicrosoftFabricDestination]
        monitoring_accounts: list[MonitoringAccountDestination]
        storage_accounts: list[StorageBlobDestination]
        storage_blobs_direct: list[StorageBlobDestination]
        storage_tables_direct: list[StorageTableDestination]

        @overload
        def __init__(
                self, 
                *, 
                azure_data_explorer: Optional[list[AdxDestination]] = ..., 
                azure_monitor_metrics: Optional[DestinationsSpecAzureMonitorMetrics] = ..., 
                event_hubs: Optional[list[EventHubDestination]] = ..., 
                event_hubs_direct: Optional[list[EventHubDirectDestination]] = ..., 
                log_analytics: Optional[list[LogAnalyticsDestination]] = ..., 
                microsoft_fabric: Optional[list[MicrosoftFabricDestination]] = ..., 
                monitoring_accounts: Optional[list[MonitoringAccountDestination]] = ..., 
                storage_accounts: Optional[list[StorageBlobDestination]] = ..., 
                storage_blobs_direct: Optional[list[StorageBlobDestination]] = ..., 
                storage_tables_direct: Optional[list[StorageTableDestination]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.DataCollectionRuleDirectDataSources(DirectDataSourcesSpec):
        otel_logs: list[OtelLogsDirectDataSource]
        otel_metrics: list[OtelMetricsDirectDataSource]
        otel_traces: list[OtelTracesDirectDataSource]

        @overload
        def __init__(
                self, 
                *, 
                otel_logs: Optional[list[OtelLogsDirectDataSource]] = ..., 
                otel_metrics: Optional[list[OtelMetricsDirectDataSource]] = ..., 
                otel_traces: Optional[list[OtelTracesDirectDataSource]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.DataCollectionRuleEndpoints(EndpointsSpec):
        logs_ingestion: str
        metrics_ingestion: str


    class azure.mgmt.monitor.models.DataCollectionRuleIngestionQuotas(IngestionQuotas):
        logs: IngestionQuotasLogs

        @overload
        def __init__(
                self, 
                *, 
                logs: Optional[IngestionQuotasLogs] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.DataCollectionRuleMetadata(Metadata):
        provisioned_by: str
        provisioned_by_immutable_id: str
        provisioned_by_resource_id: str


    class azure.mgmt.monitor.models.DataCollectionRuleReferences(ReferencesSpec):
        application_insights: list[ApplicationInsights]
        enrichment_data: ReferencesSpecEnrichmentData

        @overload
        def __init__(
                self, 
                *, 
                application_insights: Optional[list[ApplicationInsights]] = ..., 
                enrichment_data: Optional[ReferencesSpecEnrichmentData] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.DataCollectionRuleResource(TrackedResource):
        etag: Optional[str]
        id: str
        identity: Optional[DataCollectionRuleResourceIdentity]
        kind: Optional[Union[str, KnownDataCollectionRuleResourceKind]]
        location: str
        name: str
        properties: Optional[DataCollectionRuleResourceProperties]
        sku: Optional[DataCollectionRuleResourceSku]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[DataCollectionRuleResourceIdentity] = ..., 
                kind: Optional[Union[str, KnownDataCollectionRuleResourceKind]] = ..., 
                location: str, 
                properties: Optional[DataCollectionRuleResourceProperties] = ..., 
                sku: Optional[DataCollectionRuleResourceSku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.monitor.models.DataCollectionRuleResourceIdentity(ManagedServiceIdentity):
        principal_id: str
        tenant_id: str
        type: Union[str, ManagedServiceIdentityType]
        user_assigned_identities: dict[str, UserAssignedIdentity]

        @overload
        def __init__(
                self, 
                *, 
                type: Union[str, ManagedServiceIdentityType], 
                user_assigned_identities: Optional[dict[str, UserAssignedIdentity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.DataCollectionRuleResourceProperties(DataCollectionRule):
        agent_settings: DataCollectionRuleAgentSettings
        data_collection_endpoint_id: str
        data_flows: list[DataFlow]
        data_sources: DataCollectionRuleDataSources
        description: str
        destinations: DataCollectionRuleDestinations
        direct_data_sources: DataCollectionRuleDirectDataSources
        endpoints: DataCollectionRuleEndpoints
        immutable_id: str
        ingestion_quotas: DataCollectionRuleIngestionQuotas
        metadata: DataCollectionRuleMetadata
        provisioning_state: Union[str, KnownDataCollectionRuleProvisioningState]
        references: DataCollectionRuleReferences
        stream_declarations: dict[str, StreamDeclaration]

        @overload
        def __init__(
                self, 
                *, 
                agent_settings: Optional[DataCollectionRuleAgentSettings] = ..., 
                data_collection_endpoint_id: Optional[str] = ..., 
                data_flows: Optional[list[DataFlow]] = ..., 
                data_sources: Optional[DataCollectionRuleDataSources] = ..., 
                description: Optional[str] = ..., 
                destinations: Optional[DataCollectionRuleDestinations] = ..., 
                direct_data_sources: Optional[DataCollectionRuleDirectDataSources] = ..., 
                references: Optional[DataCollectionRuleReferences] = ..., 
                stream_declarations: Optional[dict[str, StreamDeclaration]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.DataCollectionRuleResourceSku(Sku):
        capacity: int
        family: str
        name: str
        size: str
        tier: Union[str, SkuTier]

        @overload
        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                family: Optional[str] = ..., 
                name: str, 
                size: Optional[str] = ..., 
                tier: Optional[Union[str, SkuTier]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.DataContainer(_Model):
        workspace: WorkspaceInfo

        @overload
        def __init__(
                self, 
                *, 
                workspace: WorkspaceInfo
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.DataFlow(_Model):
        built_in_transform: Optional[str]
        capture_overflow: Optional[bool]
        destinations: Optional[list[str]]
        output_stream: Optional[str]
        streams: Optional[list[Union[str, KnownDataFlowStreams]]]
        transform_kql: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                built_in_transform: Optional[str] = ..., 
                capture_overflow: Optional[bool] = ..., 
                destinations: Optional[list[str]] = ..., 
                output_stream: Optional[str] = ..., 
                streams: Optional[list[Union[str, KnownDataFlowStreams]]] = ..., 
                transform_kql: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.DataImportSources(_Model):
        event_hub: Optional[DataImportSourcesEventHub]

        @overload
        def __init__(
                self, 
                *, 
                event_hub: Optional[DataImportSourcesEventHub] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.DataImportSourcesEventHub(EventHubDataSource):
        consumer_group: str
        name: str
        stream: str

        @overload
        def __init__(
                self, 
                *, 
                consumer_group: Optional[str] = ..., 
                name: Optional[str] = ..., 
                stream: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.DataSourcesSpec(_Model):
        data_imports: Optional[DataSourcesSpecDataImports]
        etw_providers: Optional[list[EtwProviderDataSource]]
        extensions: Optional[list[ExtensionDataSource]]
        iis_logs: Optional[list[IisLogsDataSource]]
        log_files: Optional[list[LogFilesDataSource]]
        otel_logs: Optional[list[OtelLogsDataSource]]
        otel_metrics: Optional[list[OtelMetricsDataSource]]
        otel_traces: Optional[list[OtelTracesDataSource]]
        performance_counters: Optional[list[PerfCounterDataSource]]
        performance_counters_o_tel: Optional[list[PerformanceCountersOTelDataSource]]
        platform_telemetry: Optional[list[PlatformTelemetryDataSource]]
        prometheus_forwarder: Optional[list[PrometheusForwarderDataSource]]
        syslog: Optional[list[SyslogDataSource]]
        windows_event_logs: Optional[list[WindowsEventLogDataSource]]
        windows_firewall_logs: Optional[list[WindowsFirewallLogsDataSource]]

        @overload
        def __init__(
                self, 
                *, 
                data_imports: Optional[DataSourcesSpecDataImports] = ..., 
                etw_providers: Optional[list[EtwProviderDataSource]] = ..., 
                extensions: Optional[list[ExtensionDataSource]] = ..., 
                iis_logs: Optional[list[IisLogsDataSource]] = ..., 
                log_files: Optional[list[LogFilesDataSource]] = ..., 
                otel_logs: Optional[list[OtelLogsDataSource]] = ..., 
                otel_metrics: Optional[list[OtelMetricsDataSource]] = ..., 
                otel_traces: Optional[list[OtelTracesDataSource]] = ..., 
                performance_counters: Optional[list[PerfCounterDataSource]] = ..., 
                performance_counters_o_tel: Optional[list[PerformanceCountersOTelDataSource]] = ..., 
                platform_telemetry: Optional[list[PlatformTelemetryDataSource]] = ..., 
                prometheus_forwarder: Optional[list[PrometheusForwarderDataSource]] = ..., 
                syslog: Optional[list[SyslogDataSource]] = ..., 
                windows_event_logs: Optional[list[WindowsEventLogDataSource]] = ..., 
                windows_firewall_logs: Optional[list[WindowsFirewallLogsDataSource]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.DataSourcesSpecDataImports(DataImportSources):
        event_hub: DataImportSourcesEventHub

        @overload
        def __init__(
                self, 
                *, 
                event_hub: Optional[DataImportSourcesEventHub] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.DataStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_PRESENT = "notPresent"
        PRESENT = "present"


    class azure.mgmt.monitor.models.DestinationsSpec(_Model):
        azure_data_explorer: Optional[list[AdxDestination]]
        azure_monitor_metrics: Optional[DestinationsSpecAzureMonitorMetrics]
        event_hubs: Optional[list[EventHubDestination]]
        event_hubs_direct: Optional[list[EventHubDirectDestination]]
        log_analytics: Optional[list[LogAnalyticsDestination]]
        microsoft_fabric: Optional[list[MicrosoftFabricDestination]]
        monitoring_accounts: Optional[list[MonitoringAccountDestination]]
        storage_accounts: Optional[list[StorageBlobDestination]]
        storage_blobs_direct: Optional[list[StorageBlobDestination]]
        storage_tables_direct: Optional[list[StorageTableDestination]]

        @overload
        def __init__(
                self, 
                *, 
                azure_data_explorer: Optional[list[AdxDestination]] = ..., 
                azure_monitor_metrics: Optional[DestinationsSpecAzureMonitorMetrics] = ..., 
                event_hubs: Optional[list[EventHubDestination]] = ..., 
                event_hubs_direct: Optional[list[EventHubDirectDestination]] = ..., 
                log_analytics: Optional[list[LogAnalyticsDestination]] = ..., 
                microsoft_fabric: Optional[list[MicrosoftFabricDestination]] = ..., 
                monitoring_accounts: Optional[list[MonitoringAccountDestination]] = ..., 
                storage_accounts: Optional[list[StorageBlobDestination]] = ..., 
                storage_blobs_direct: Optional[list[StorageBlobDestination]] = ..., 
                storage_tables_direct: Optional[list[StorageTableDestination]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.DestinationsSpecAzureMonitorMetrics(AzureMonitorMetricsDestination):
        name: str

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.DiagnosticSettings(_Model):
        event_hub_authorization_rule_id: Optional[str]
        event_hub_name: Optional[str]
        log_analytics_destination_type: Optional[str]
        logs: Optional[list[DiagnosticsLogSettings]]
        marketplace_partner_id: Optional[str]
        metrics: Optional[list[DiagnosticsMetricSettings]]
        service_bus_rule_id: Optional[str]
        storage_account_id: Optional[str]
        workspace_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                event_hub_authorization_rule_id: Optional[str] = ..., 
                event_hub_name: Optional[str] = ..., 
                log_analytics_destination_type: Optional[str] = ..., 
                logs: Optional[list[DiagnosticsLogSettings]] = ..., 
                marketplace_partner_id: Optional[str] = ..., 
                metrics: Optional[list[DiagnosticsMetricSettings]] = ..., 
                service_bus_rule_id: Optional[str] = ..., 
                storage_account_id: Optional[str] = ..., 
                workspace_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.DiagnosticSettingsCategory(_Model):
        category_groups: Optional[list[str]]
        category_type: Optional[Union[str, CategoryType]]

        @overload
        def __init__(
                self, 
                *, 
                category_groups: Optional[list[str]] = ..., 
                category_type: Optional[Union[str, CategoryType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.DiagnosticSettingsCategoryResource(ExtensionResource):
        id: str
        name: str
        properties: Optional[DiagnosticSettingsCategory]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DiagnosticSettingsCategory] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.monitor.models.DiagnosticSettingsResource(ExtensionResource):
        id: str
        name: str
        properties: Optional[DiagnosticSettings]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DiagnosticSettings] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.monitor.models.DiagnosticsLogSettings(_Model):
        category: Optional[str]
        category_group: Optional[str]
        enabled: bool
        retention_policy: Optional[RetentionPolicy]

        @overload
        def __init__(
                self, 
                *, 
                category: Optional[str] = ..., 
                category_group: Optional[str] = ..., 
                enabled: bool, 
                retention_policy: Optional[RetentionPolicy] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.DiagnosticsMetricSettings(_Model):
        category: Optional[str]
        enabled: bool
        retention_policy: Optional[RetentionPolicy]
        time_grain: Optional[timedelta]

        @overload
        def __init__(
                self, 
                *, 
                category: Optional[str] = ..., 
                enabled: bool, 
                retention_policy: Optional[RetentionPolicy] = ..., 
                time_grain: Optional[timedelta] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.Dimension(_Model):
        name: str
        operator: Union[str, DimensionOperator]
        values_property: list[str]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                operator: Union[str, DimensionOperator], 
                values_property: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.DimensionOperator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXCLUDE = "Exclude"
        INCLUDE = "Include"


    class azure.mgmt.monitor.models.DirectDataSourcesSpec(_Model):
        otel_logs: Optional[list[OtelLogsDirectDataSource]]
        otel_metrics: Optional[list[OtelMetricsDirectDataSource]]
        otel_traces: Optional[list[OtelTracesDirectDataSource]]

        @overload
        def __init__(
                self, 
                *, 
                otel_logs: Optional[list[OtelLogsDirectDataSource]] = ..., 
                otel_metrics: Optional[list[OtelMetricsDirectDataSource]] = ..., 
                otel_traces: Optional[list[OtelTracesDirectDataSource]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.DynamicMetricCriteria(MultiMetricCriteria, discriminator='DynamicThresholdCriterion'):
        alert_sensitivity: Union[str, DynamicThresholdSensitivity]
        criterion_type: Literal[CriterionType.DYNAMIC_THRESHOLD_CRITERION]
        dimensions: list[MetricDimension]
        failing_periods: DynamicThresholdFailingPeriods
        ignore_data_before: Optional[datetime]
        metric_name: str
        metric_namespace: str
        name: str
        operator: Union[str, DynamicThresholdOperator]
        skip_metric_validation: bool
        time_aggregation: Union[str, AggregationTypeEnum]

        @overload
        def __init__(
                self, 
                *, 
                alert_sensitivity: Union[str, DynamicThresholdSensitivity], 
                dimensions: Optional[list[MetricDimension]] = ..., 
                failing_periods: DynamicThresholdFailingPeriods, 
                ignore_data_before: Optional[datetime] = ..., 
                metric_name: str, 
                metric_namespace: Optional[str] = ..., 
                name: str, 
                operator: Union[str, DynamicThresholdOperator], 
                skip_metric_validation: Optional[bool] = ..., 
                time_aggregation: Union[str, AggregationTypeEnum]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.DynamicPromQLCriteria(MultiPromQLCriteria, discriminator='DynamicThresholdCriterion'):
        alert_sensitivity: Union[str, DynamicThresholdSensitivity]
        criterion_type: Literal[CriterionType.DYNAMIC_THRESHOLD_CRITERION]
        ignore_data_before: Optional[datetime]
        name: str
        operator: Union[str, DynamicThresholdOperator]
        query: str

        @overload
        def __init__(
                self, 
                *, 
                alert_sensitivity: Union[str, DynamicThresholdSensitivity], 
                ignore_data_before: Optional[datetime] = ..., 
                name: str, 
                operator: Union[str, DynamicThresholdOperator], 
                query: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.DynamicThresholdFailingPeriods(_Model):
        min_failing_periods_to_alert: float
        number_of_evaluation_periods: float

        @overload
        def __init__(
                self, 
                *, 
                min_failing_periods_to_alert: float, 
                number_of_evaluation_periods: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.DynamicThresholdOperator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GREATER_OR_LESS_THAN = "GreaterOrLessThan"
        GREATER_THAN = "GreaterThan"
        LESS_THAN = "LessThan"


    class azure.mgmt.monitor.models.DynamicThresholdSensitivity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "High"
        LOW = "Low"
        MEDIUM = "Medium"


    class azure.mgmt.monitor.models.EmailNotification(_Model):
        custom_emails: Optional[list[str]]
        send_to_subscription_administrator: Optional[bool]
        send_to_subscription_co_administrators: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                custom_emails: Optional[list[str]] = ..., 
                send_to_subscription_administrator: Optional[bool] = ..., 
                send_to_subscription_co_administrators: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.EmailReceiver(_Model):
        email_address: str
        name: str
        status: Optional[Union[str, ReceiverStatus]]
        use_common_alert_schema: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                email_address: str, 
                name: str, 
                use_common_alert_schema: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.EnableRequest(_Model):
        receiver_name: str

        @overload
        def __init__(
                self, 
                *, 
                receiver_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.EndpointsSpec(_Model):
        logs_ingestion: Optional[str]
        metrics_ingestion: Optional[str]


    class azure.mgmt.monitor.models.EnrichmentData(_Model):
        storage_blobs: Optional[list[StorageBlob]]

        @overload
        def __init__(
                self, 
                *, 
                storage_blobs: Optional[list[StorageBlob]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.Error(_Model):
        code: str
        message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: str, 
                message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.monitor.models.ErrorContract(_Model):
        error: Optional[ErrorResponseCommon]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorResponseCommon] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorDetailAdditionalInfoItem]]
        code: Optional[str]
        message: Optional[str]
        target: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                additional_info: Optional[list[ErrorDetailAdditionalInfoItem]] = ..., 
                code: Optional[str] = ..., 
                message: Optional[str] = ..., 
                target: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.ErrorDetailAdditionalInfoItem(_Model):
        info: Optional[dict[str, Any]]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                info: Optional[dict[str, Any]] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.ErrorDetailAutoGenerated(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetailAutoGenerated]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.monitor.models.ErrorResponse(_Model):
        code: Optional[str]
        message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.ErrorResponseAutoGenerated(_Model):
        error: Optional[ErrorDetailAutoGenerated]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetailAutoGenerated] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.ErrorResponseCommon(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorResponseCommon]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.monitor.models.ErrorResponseCommonV2(_Model):
        error: Optional[ErrorDetailAutoGenerated]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetailAutoGenerated] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.ErrorResponseError(_Model):
        additional_info: Optional[list[ErrorResponseErrorAdditionalInfoItem]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                additional_info: Optional[list[ErrorResponseErrorAdditionalInfoItem]] = ..., 
                code: Optional[str] = ..., 
                details: Optional[list[ErrorDetail]] = ..., 
                message: Optional[str] = ..., 
                target: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.ErrorResponseErrorAdditionalInfoItem(_Model):
        info: Optional[dict[str, Any]]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                info: Optional[dict[str, Any]] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.EtwProviderDataSource(_Model):
        event_ids: Optional[list[str]]
        keyword: Optional[str]
        log_level: Optional[Union[str, KnownEtwProviderDataSourceLogLevel]]
        name: Optional[str]
        provider: str
        provider_type: Union[str, KnownEtwProviderType]
        streams: list[str]

        @overload
        def __init__(
                self, 
                *, 
                event_ids: Optional[list[str]] = ..., 
                keyword: Optional[str] = ..., 
                log_level: Optional[Union[str, KnownEtwProviderDataSourceLogLevel]] = ..., 
                name: Optional[str] = ..., 
                provider: str, 
                provider_type: Union[str, KnownEtwProviderType], 
                streams: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.EventData(_Model):
        authorization: Optional[SenderAuthorization]
        caller: Optional[str]
        category: Optional[LocalizableString]
        claims: Optional[dict[str, str]]
        correlation_id: Optional[str]
        description: Optional[str]
        event_data_id: Optional[str]
        event_name: Optional[LocalizableString]
        event_timestamp: Optional[datetime]
        http_request: Optional[HttpRequestInfo]
        id: Optional[str]
        level: Optional[Union[str, EventLevel]]
        operation_id: Optional[str]
        operation_name: Optional[LocalizableString]
        properties: Optional[dict[str, str]]
        resource_group_name: Optional[str]
        resource_id: Optional[str]
        resource_provider_name: Optional[LocalizableString]
        resource_type: Optional[LocalizableString]
        status: Optional[LocalizableString]
        sub_status: Optional[LocalizableString]
        submission_timestamp: Optional[datetime]
        subscription_id: Optional[str]
        tenant_id: Optional[str]


    class azure.mgmt.monitor.models.EventHubDataSource(_Model):
        consumer_group: Optional[str]
        name: Optional[str]
        stream: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                consumer_group: Optional[str] = ..., 
                name: Optional[str] = ..., 
                stream: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.EventHubDestination(_Model):
        event_hub_resource_id: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                event_hub_resource_id: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.EventHubDirectDestination(_Model):
        event_hub_resource_id: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                event_hub_resource_id: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.EventHubReceiver(_Model):
        event_hub_name: str
        event_hub_name_space: str
        managed_identity: Optional[str]
        name: str
        subscription_id: str
        tenant_id: Optional[str]
        use_common_alert_schema: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                event_hub_name: str, 
                event_hub_name_space: str, 
                managed_identity: Optional[str] = ..., 
                name: str, 
                subscription_id: str, 
                tenant_id: Optional[str] = ..., 
                use_common_alert_schema: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.EventLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CRITICAL = "Critical"
        ERROR = "Error"
        INFORMATIONAL = "Informational"
        VERBOSE = "Verbose"
        WARNING = "Warning"


    class azure.mgmt.monitor.models.ExtensionDataSource(_Model):
        extension_name: str
        extension_settings: Optional[Any]
        input_data_sources: Optional[list[str]]
        name: Optional[str]
        streams: Optional[list[Union[str, KnownExtensionDataSourceStreams]]]

        @overload
        def __init__(
                self, 
                *, 
                extension_name: str, 
                extension_settings: Optional[Any] = ..., 
                input_data_sources: Optional[list[str]] = ..., 
                name: Optional[str] = ..., 
                streams: Optional[list[Union[str, KnownExtensionDataSourceStreams]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.ExtensionResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.monitor.models.FailoverConfigurationSpec(_Model):
        active_location: Optional[str]
        locations: Optional[list[LocationSpec]]

        @overload
        def __init__(
                self, 
                *, 
                active_location: Optional[str] = ..., 
                locations: Optional[list[LocationSpec]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.HttpRequestInfo(_Model):
        client_ip_address: Optional[str]
        client_request_id: Optional[str]
        method: Optional[str]
        uri: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                client_ip_address: Optional[str] = ..., 
                client_request_id: Optional[str] = ..., 
                method: Optional[str] = ..., 
                uri: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.Identity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Union[str, IdentityType]
        user_assigned_identities: Optional[dict[str, UserIdentityProperties]]

        @overload
        def __init__(
                self, 
                *, 
                type: Union[str, IdentityType], 
                user_assigned_identities: Optional[dict[str, UserIdentityProperties]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.IdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.monitor.models.IisLogsDataSource(_Model):
        log_directories: Optional[list[str]]
        name: Optional[str]
        streams: list[str]
        transform_kql: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                log_directories: Optional[list[str]] = ..., 
                name: Optional[str] = ..., 
                streams: list[str], 
                transform_kql: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.Incident(_Model):
        activated_time: Optional[datetime]
        is_active: Optional[bool]
        name: Optional[str]
        resolved_time: Optional[datetime]
        rule_name: Optional[str]


    class azure.mgmt.monitor.models.IncidentManagementService(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ICM = "Icm"


    class azure.mgmt.monitor.models.IncidentReceiver(_Model):
        connection: IncidentServiceConnection
        incident_management_service: Union[str, IncidentManagementService]
        mappings: dict[str, str]
        name: str

        @overload
        def __init__(
                self, 
                *, 
                connection: IncidentServiceConnection, 
                incident_management_service: Union[str, IncidentManagementService], 
                mappings: dict[str, str], 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.IncidentServiceConnection(_Model):
        id: str
        name: str

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.IngestionQuotas(_Model):
        logs: Optional[IngestionQuotasLogs]

        @overload
        def __init__(
                self, 
                *, 
                logs: Optional[IngestionQuotasLogs] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.IngestionQuotasLogs(LogsQuotaSpec):
        max_requests_per_minute: str
        max_size_per_minute_in_gb: str

        @overload
        def __init__(
                self, 
                *, 
                max_requests_per_minute: Optional[str] = ..., 
                max_size_per_minute_in_gb: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.IssueType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONFIGURATION_PROPAGATION_FAILURE = "ConfigurationPropagationFailure"
        MISSING_IDENTITY_CONFIGURATION = "MissingIdentityConfiguration"
        MISSING_PERIMETER_CONFIGURATION = "MissingPerimeterConfiguration"
        UNKNOWN = "Unknown"


    class azure.mgmt.monitor.models.ItsmReceiver(_Model):
        connection_id: str
        name: str
        region: str
        ticket_configuration: str
        workspace_id: str

        @overload
        def __init__(
                self, 
                *, 
                connection_id: str, 
                name: str, 
                region: str, 
                ticket_configuration: str, 
                workspace_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.Kind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOG_ALERT = "LogAlert"
        LOG_TO_METRIC = "LogToMetric"
        SIMPLE_LOG_ALERT = "SimpleLogAlert"


    class azure.mgmt.monitor.models.KnownAgentSettingName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MAX_DISK_QUOTA_IN_MB = "MaxDiskQuotaInMB"
        TAGS = "Tags"
        USE_TIME_RECEIVED_FOR_FORWARDED_EVENTS = "UseTimeReceivedForForwardedEvents"


    class azure.mgmt.monitor.models.KnownColumnDefinitionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BOOLEAN = "boolean"
        DATETIME = "datetime"
        DYNAMIC = "dynamic"
        INT = "int"
        LONG = "long"
        REAL = "real"
        STRING = "string"


    class azure.mgmt.monitor.models.KnownDataCollectionEndpointProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.monitor.models.KnownDataCollectionEndpointResourceKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LINUX = "Linux"
        WINDOWS = "Windows"


    class azure.mgmt.monitor.models.KnownDataCollectionRuleAssociationProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.monitor.models.KnownDataCollectionRuleProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.monitor.models.KnownDataCollectionRuleResourceKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LINUX = "Linux"
        WINDOWS = "Windows"


    class azure.mgmt.monitor.models.KnownDataFlowStreams(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MICROSOFT_EVENT = "Microsoft-Event"
        MICROSOFT_INSIGHTS_METRICS = "Microsoft-InsightsMetrics"
        MICROSOFT_PERF = "Microsoft-Perf"
        MICROSOFT_SYSLOG = "Microsoft-Syslog"
        MICROSOFT_WINDOWS_EVENT = "Microsoft-WindowsEvent"


    class azure.mgmt.monitor.models.KnownEtwProviderDataSourceLogLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CRITICAL = "Critical"
        ERROR = "Error"
        INFORMATIONAL = "Informational"
        VERBOSE = "Verbose"
        WARNING = "Warning"


    class azure.mgmt.monitor.models.KnownEtwProviderType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EVENT_SOURCE = "EventSource"
        MANIFEST = "Manifest"


    class azure.mgmt.monitor.models.KnownExtensionDataSourceStreams(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MICROSOFT_EVENT = "Microsoft-Event"
        MICROSOFT_INSIGHTS_METRICS = "Microsoft-InsightsMetrics"
        MICROSOFT_PERF = "Microsoft-Perf"
        MICROSOFT_SYSLOG = "Microsoft-Syslog"
        MICROSOFT_WINDOWS_EVENT = "Microsoft-WindowsEvent"


    class azure.mgmt.monitor.models.KnownLocationSpecProvisioningStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.monitor.models.KnownLogFileTextSettingsRecordStartTimestampFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DD_MMM_YYYY_HH_MM_SS_ZZZ = "dd/MMM/yyyy:HH:mm:ss zzz"
        DD_M_MYY_HH_MM_SS = "ddMMyy HH:mm:ss"
        ISO8601 = "ISO 8601"
        MMM_D_HH_MM_SS = "MMM d hh:mm:ss"
        MON_DD_YYYY_HH_MM_SS = "Mon DD, YYYY HH:MM:SS"
        M_D_YYYY_HH_MM_SS_AM_PM = "M/D/YYYY HH:MM:SS AM/PM"
        YYYY_MM_DD_HH_MM_SS = "YYYY-MM-DD HH:MM:SS"
        YYYY_MM_DD_THH_MM_SS_K = "yyyy-MM-ddTHH:mm:ssK"
        YY_M_MDD_HH_MM_SS = "yyMMdd HH:mm:ss"


    class azure.mgmt.monitor.models.KnownLogFilesDataSourceFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        JSON = "json"
        TEXT = "text"


    class azure.mgmt.monitor.models.KnownOtelLogsDataSourceStreams(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MICROSOFT_O_TEL_LOGS = "Microsoft-OTel-Logs"


    class azure.mgmt.monitor.models.KnownOtelLogsDirectDataSourceStreams(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MICROSOFT_O_TEL_LOGS = "Microsoft-OTel-Logs"


    class azure.mgmt.monitor.models.KnownOtelTracesDataSourceStreams(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MICROSOFT_O_TEL_TRACES_EVENTS = "Microsoft-OTel-Traces-Events"
        MICROSOFT_O_TEL_TRACES_RESOURCES = "Microsoft-OTel-Traces-Resources"
        MICROSOFT_O_TEL_TRACES_SPANS = "Microsoft-OTel-Traces-Spans"


    class azure.mgmt.monitor.models.KnownOtelTracesDirectDataSourceStreams(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MICROSOFT_O_TEL_TRACES_EVENTS = "Microsoft-OTel-Traces-Events"
        MICROSOFT_O_TEL_TRACES_RESOURCES = "Microsoft-OTel-Traces-Resources"
        MICROSOFT_O_TEL_TRACES_SPANS = "Microsoft-OTel-Traces-Spans"


    class azure.mgmt.monitor.models.KnownPerfCounterDataSourceStreams(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MICROSOFT_INSIGHTS_METRICS = "Microsoft-InsightsMetrics"
        MICROSOFT_PERF = "Microsoft-Perf"


    class azure.mgmt.monitor.models.KnownPerformanceCountersOTelDataSourceStreams(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MICROSOFT_OTEL_PERF_METRICS = "Microsoft-OtelPerfMetrics"


    class azure.mgmt.monitor.models.KnownPrometheusForwarderDataSourceStreams(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MICROSOFT_PROMETHEUS_METRICS = "Microsoft-PrometheusMetrics"


    class azure.mgmt.monitor.models.KnownPublicNetworkAccessOptions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        SECURED_BY_PERIMETER = "SecuredByPerimeter"


    class azure.mgmt.monitor.models.KnownStorageBlobLookupType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CIDR = "Cidr"
        STRING = "String"


    class azure.mgmt.monitor.models.KnownSyslogDataSourceFacilityNames(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALERT = "alert"
        ASTERISK = "*"
        AUDIT = "audit"
        AUTH = "auth"
        AUTHPRIV = "authpriv"
        CLOCK = "clock"
        CRON = "cron"
        DAEMON = "daemon"
        FTP = "ftp"
        KERN = "kern"
        LOCAL0 = "local0"
        LOCAL1 = "local1"
        LOCAL2 = "local2"
        LOCAL3 = "local3"
        LOCAL4 = "local4"
        LOCAL5 = "local5"
        LOCAL6 = "local6"
        LOCAL7 = "local7"
        LPR = "lpr"
        MAIL = "mail"
        MARK = "mark"
        NEWS = "news"
        NOPRI = "nopri"
        NTP = "ntp"
        SYSLOG = "syslog"
        USER = "user"
        UUCP = "uucp"


    class azure.mgmt.monitor.models.KnownSyslogDataSourceLogLevels(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALERT = "Alert"
        ASTERISK = "*"
        CRITICAL = "Critical"
        DEBUG = "Debug"
        EMERGENCY = "Emergency"
        ERROR = "Error"
        INFO = "Info"
        NOTICE = "Notice"
        WARNING = "Warning"


    class azure.mgmt.monitor.models.KnownSyslogDataSourceStreams(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MICROSOFT_SYSLOG = "Microsoft-Syslog"


    class azure.mgmt.monitor.models.KnownWindowsEventLogDataSourceStreams(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MICROSOFT_EVENT = "Microsoft-Event"
        MICROSOFT_WINDOWS_EVENT = "Microsoft-WindowsEvent"


    class azure.mgmt.monitor.models.KnownWindowsFirewallLogsDataSourceProfileFilter(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DOMAIN = "Domain"
        PRIVATE = "Private"
        PUBLIC = "Public"


    class azure.mgmt.monitor.models.LocalizableString(_Model):
        localized_value: Optional[str]
        value: str

        @overload
        def __init__(
                self, 
                *, 
                localized_value: Optional[str] = ..., 
                value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.LocationSpec(_Model):
        location: Optional[str]
        provisioning_status: Optional[Union[str, KnownLocationSpecProvisioningStatus]]

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                provisioning_status: Optional[Union[str, KnownLocationSpecProvisioningStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.LogAnalyticsDestination(_Model):
        name: Optional[str]
        workspace_id: Optional[str]
        workspace_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                workspace_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.LogFileSettings(_Model):
        text: Optional[LogFileSettingsText]

        @overload
        def __init__(
                self, 
                *, 
                text: Optional[LogFileSettingsText] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.LogFileSettingsText(LogFileTextSettings):
        record_start_timestamp_format: Union[str, KnownLogFileTextSettingsRecordStartTimestampFormat]

        @overload
        def __init__(
                self, 
                *, 
                record_start_timestamp_format: Union[str, KnownLogFileTextSettingsRecordStartTimestampFormat]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.LogFileTextSettings(_Model):
        record_start_timestamp_format: Union[str, KnownLogFileTextSettingsRecordStartTimestampFormat]

        @overload
        def __init__(
                self, 
                *, 
                record_start_timestamp_format: Union[str, KnownLogFileTextSettingsRecordStartTimestampFormat]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.LogFilesDataSource(_Model):
        file_patterns: list[str]
        format: Union[str, KnownLogFilesDataSourceFormat]
        name: Optional[str]
        settings: Optional[LogFilesDataSourceSettings]
        streams: list[str]
        transform_kql: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                file_patterns: list[str], 
                format: Union[str, KnownLogFilesDataSourceFormat], 
                name: Optional[str] = ..., 
                settings: Optional[LogFilesDataSourceSettings] = ..., 
                streams: list[str], 
                transform_kql: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.LogFilesDataSourceSettings(LogFileSettings):
        text: LogFileSettingsText

        @overload
        def __init__(
                self, 
                *, 
                text: Optional[LogFileSettingsText] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.LogProfileProperties(_Model):
        categories: list[str]
        locations: list[str]
        retention_policy: RetentionPolicy
        service_bus_rule_id: Optional[str]
        storage_account_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                categories: list[str], 
                locations: list[str], 
                retention_policy: RetentionPolicy, 
                service_bus_rule_id: Optional[str] = ..., 
                storage_account_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.LogProfileResource(TrackedResource):
        id: str
        location: str
        name: str
        properties: LogProfileProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: LogProfileProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.monitor.models.LogProfileResourcePatch(_Model):
        properties: Optional[LogProfileProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[LogProfileProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.monitor.models.LogicAppReceiver(_Model):
        callback_url: str
        managed_identity: Optional[str]
        name: str
        resource_id: str
        use_common_alert_schema: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                callback_url: str, 
                managed_identity: Optional[str] = ..., 
                name: str, 
                resource_id: str, 
                use_common_alert_schema: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.LogsIngestionEndpointSpec(_Model):
        endpoint: Optional[str]


    class azure.mgmt.monitor.models.LogsQuotaSpec(_Model):
        max_requests_per_minute: Optional[str]
        max_size_per_minute_in_gb: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                max_requests_per_minute: Optional[str] = ..., 
                max_size_per_minute_in_gb: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.ManagedServiceIdentity(_Model):
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


    class azure.mgmt.monitor.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.monitor.models.Metadata(_Model):
        provisioned_by: Optional[str]
        provisioned_by_immutable_id: Optional[str]
        provisioned_by_resource_id: Optional[str]


    class azure.mgmt.monitor.models.MetadataValue(_Model):
        name: Optional[LocalizableString]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[LocalizableString] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.Metric(_Model):
        display_description: Optional[str]
        error_code: Optional[str]
        error_message: Optional[str]
        id: str
        name: LocalizableString
        timeseries: list[TimeSeriesElement]
        type: str
        unit: Union[str, MetricUnit]

        @overload
        def __init__(
                self, 
                *, 
                display_description: Optional[str] = ..., 
                error_code: Optional[str] = ..., 
                error_message: Optional[str] = ..., 
                id: str, 
                name: LocalizableString, 
                timeseries: list[TimeSeriesElement], 
                type: str, 
                unit: Union[str, MetricUnit]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.MetricAggregationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVERAGE = "Average"
        COUNT = "Count"
        MAXIMUM = "Maximum"
        MINIMUM = "Minimum"
        NONE = "None"
        TOTAL = "Total"


    class azure.mgmt.monitor.models.MetricAlertAction(_Model):
        action_group_id: Optional[str]
        web_hook_properties: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                action_group_id: Optional[str] = ..., 
                web_hook_properties: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.MetricAlertCriteria(_Model):
        odata_type: str

        @overload
        def __init__(
                self, 
                *, 
                odata_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.MetricAlertErrorResponse(_Model):
        error: Optional[ErrorResponseError]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorResponseError] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.MetricAlertMultipleResourceMultipleMetricCriteria(MetricAlertCriteria, discriminator='Microsoft.Azure.Monitor.MultipleResourceMultipleMetricCriteria'):
        all_of: Optional[list[MultiMetricCriteria]]
        odata_type: Literal[Odatatype.MICROSOFT_AZURE_MONITOR_MULTIPLE_RESOURCE_MULTIPLE_METRIC_CRITERIA]

        @overload
        def __init__(
                self, 
                *, 
                all_of: Optional[list[MultiMetricCriteria]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.MetricAlertProperties(_Model):
        action_properties: Optional[dict[str, str]]
        actions: Optional[list[MetricAlertAction]]
        auto_mitigate: Optional[bool]
        criteria: MetricAlertCriteria
        custom_properties: Optional[dict[str, str]]
        description: Optional[str]
        enabled: bool
        evaluation_frequency: timedelta
        is_migrated: Optional[bool]
        last_updated_time: Optional[datetime]
        resolve_configuration: Optional[ResolveConfiguration]
        scopes: list[str]
        severity: int
        target_resource_region: Optional[str]
        target_resource_type: Optional[str]
        window_size: Optional[timedelta]

        @overload
        def __init__(
                self, 
                *, 
                action_properties: Optional[dict[str, str]] = ..., 
                actions: Optional[list[MetricAlertAction]] = ..., 
                auto_mitigate: Optional[bool] = ..., 
                criteria: MetricAlertCriteria, 
                custom_properties: Optional[dict[str, str]] = ..., 
                description: Optional[str] = ..., 
                enabled: bool, 
                evaluation_frequency: timedelta, 
                resolve_configuration: Optional[ResolveConfiguration] = ..., 
                scopes: list[str], 
                severity: int, 
                target_resource_region: Optional[str] = ..., 
                target_resource_type: Optional[str] = ..., 
                window_size: Optional[timedelta] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.MetricAlertPropertiesPatch(_Model):
        action_properties: Optional[dict[str, str]]
        actions: Optional[list[MetricAlertAction]]
        auto_mitigate: Optional[bool]
        criteria: Optional[MetricAlertCriteria]
        custom_properties: Optional[dict[str, str]]
        description: Optional[str]
        enabled: Optional[bool]
        evaluation_frequency: Optional[timedelta]
        is_migrated: Optional[bool]
        last_updated_time: Optional[datetime]
        resolve_configuration: Optional[ResolveConfiguration]
        scopes: Optional[list[str]]
        severity: Optional[int]
        target_resource_region: Optional[str]
        target_resource_type: Optional[str]
        window_size: Optional[timedelta]

        @overload
        def __init__(
                self, 
                *, 
                action_properties: Optional[dict[str, str]] = ..., 
                actions: Optional[list[MetricAlertAction]] = ..., 
                auto_mitigate: Optional[bool] = ..., 
                criteria: Optional[MetricAlertCriteria] = ..., 
                custom_properties: Optional[dict[str, str]] = ..., 
                description: Optional[str] = ..., 
                enabled: Optional[bool] = ..., 
                evaluation_frequency: Optional[timedelta] = ..., 
                resolve_configuration: Optional[ResolveConfiguration] = ..., 
                scopes: Optional[list[str]] = ..., 
                severity: Optional[int] = ..., 
                target_resource_region: Optional[str] = ..., 
                target_resource_type: Optional[str] = ..., 
                window_size: Optional[timedelta] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.MetricAlertResource(TrackedResource):
        id: str
        identity: Optional[Identity]
        location: str
        name: str
        properties: MetricAlertProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[Identity] = ..., 
                location: str, 
                properties: MetricAlertProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.monitor.models.MetricAlertResourcePatch(_Model):
        identity: Optional[Identity]
        properties: Optional[MetricAlertPropertiesPatch]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[Identity] = ..., 
                properties: Optional[MetricAlertPropertiesPatch] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.monitor.models.MetricAlertSingleResourceMultipleMetricCriteria(MetricAlertCriteria, discriminator='Microsoft.Azure.Monitor.SingleResourceMultipleMetricCriteria'):
        all_of: Optional[list[MetricCriteria]]
        odata_type: Literal[Odatatype.MICROSOFT_AZURE_MONITOR_SINGLE_RESOURCE_MULTIPLE_METRIC_CRITERIA]

        @overload
        def __init__(
                self, 
                *, 
                all_of: Optional[list[MetricCriteria]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.MetricAlertStatus(_Model):
        id: Optional[str]
        name: Optional[str]
        properties: Optional[MetricAlertStatusProperties]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[MetricAlertStatusProperties] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.MetricAlertStatusCollection(_Model):
        value: Optional[list[MetricAlertStatus]]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[list[MetricAlertStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.MetricAlertStatusProperties(_Model):
        dimensions: Optional[dict[str, str]]
        status: Optional[str]
        timestamp: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                dimensions: Optional[dict[str, str]] = ..., 
                status: Optional[str] = ..., 
                timestamp: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.MetricAvailability(_Model):
        retention: Optional[timedelta]
        time_grain: Optional[timedelta]

        @overload
        def __init__(
                self, 
                *, 
                retention: Optional[timedelta] = ..., 
                time_grain: Optional[timedelta] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.MetricBaselinesErrorResponse(_Model):
        error: Optional[ErrorResponseError]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorResponseError] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.MetricBaselinesProperties(_Model):
        baselines: list[TimeSeriesBaseline]
        interval: timedelta
        namespace: Optional[str]
        timespan: str

        @overload
        def __init__(
                self, 
                *, 
                baselines: list[TimeSeriesBaseline], 
                interval: timedelta, 
                namespace: Optional[str] = ..., 
                timespan: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.MetricClass(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABILITY = "Availability"
        ERRORS = "Errors"
        LATENCY = "Latency"
        SATURATION = "Saturation"
        TRANSACTIONS = "Transactions"


    class azure.mgmt.monitor.models.MetricCriteria(MultiMetricCriteria, discriminator='StaticThresholdCriterion'):
        criterion_type: Literal[CriterionType.STATIC_THRESHOLD_CRITERION]
        dimensions: list[MetricDimension]
        metric_name: str
        metric_namespace: str
        name: str
        operator: Union[str, Operator]
        skip_metric_validation: bool
        threshold: float
        time_aggregation: Union[str, AggregationTypeEnum]

        @overload
        def __init__(
                self, 
                *, 
                dimensions: Optional[list[MetricDimension]] = ..., 
                metric_name: str, 
                metric_namespace: Optional[str] = ..., 
                name: str, 
                operator: Union[str, Operator], 
                skip_metric_validation: Optional[bool] = ..., 
                threshold: float, 
                time_aggregation: Union[str, AggregationTypeEnum]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.MetricDefinition(_Model):
        category: Optional[str]
        dimensions: Optional[list[LocalizableString]]
        display_description: Optional[str]
        id: Optional[str]
        is_dimension_required: Optional[bool]
        metric_availabilities: Optional[list[MetricAvailability]]
        metric_class: Optional[Union[str, MetricClass]]
        name: Optional[LocalizableString]
        namespace: Optional[str]
        primary_aggregation_type: Optional[Union[str, AggregationType]]
        resource_id: Optional[str]
        supported_aggregation_types: Optional[list[Union[str, AggregationType]]]
        unit: Optional[Union[str, MetricUnit]]

        @overload
        def __init__(
                self, 
                *, 
                category: Optional[str] = ..., 
                dimensions: Optional[list[LocalizableString]] = ..., 
                display_description: Optional[str] = ..., 
                id: Optional[str] = ..., 
                is_dimension_required: Optional[bool] = ..., 
                metric_availabilities: Optional[list[MetricAvailability]] = ..., 
                metric_class: Optional[Union[str, MetricClass]] = ..., 
                name: Optional[LocalizableString] = ..., 
                namespace: Optional[str] = ..., 
                primary_aggregation_type: Optional[Union[str, AggregationType]] = ..., 
                resource_id: Optional[str] = ..., 
                supported_aggregation_types: Optional[list[Union[str, AggregationType]]] = ..., 
                unit: Optional[Union[str, MetricUnit]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.MetricDimension(_Model):
        name: str
        operator: str
        values_property: list[str]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                operator: str, 
                values_property: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.MetricNamespace(_Model):
        classification: Optional[Union[str, NamespaceClassification]]
        id: Optional[str]
        name: Optional[str]
        properties: Optional[MetricNamespaceName]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                classification: Optional[Union[str, NamespaceClassification]] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[MetricNamespaceName] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.MetricNamespaceName(_Model):
        metric_namespace_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                metric_namespace_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.MetricResultType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DATA = "Data"
        METADATA = "Metadata"


    class azure.mgmt.monitor.models.MetricSingleDimension(_Model):
        name: str
        value: str

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.MetricStatisticType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVERAGE = "Average"
        COUNT = "Count"
        MAX = "Max"
        MIN = "Min"
        SUM = "Sum"


    class azure.mgmt.monitor.models.MetricTrigger(_Model):
        dimensions: Optional[list[ScaleRuleMetricDimension]]
        divide_per_instance: Optional[bool]
        metric_name: str
        metric_namespace: Optional[str]
        metric_resource_location: Optional[str]
        metric_resource_uri: str
        operator: Union[str, ComparisonOperationType]
        statistic: Union[str, MetricStatisticType]
        threshold: float
        time_aggregation: Union[str, TimeAggregationType]
        time_grain: timedelta
        time_window: timedelta

        @overload
        def __init__(
                self, 
                *, 
                dimensions: Optional[list[ScaleRuleMetricDimension]] = ..., 
                divide_per_instance: Optional[bool] = ..., 
                metric_name: str, 
                metric_namespace: Optional[str] = ..., 
                metric_resource_location: Optional[str] = ..., 
                metric_resource_uri: str, 
                operator: Union[str, ComparisonOperationType], 
                statistic: Union[str, MetricStatisticType], 
                threshold: float, 
                time_aggregation: Union[str, TimeAggregationType], 
                time_grain: timedelta, 
                time_window: timedelta
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.MetricUnit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BITS_PER_SECOND = "BitsPerSecond"
        BYTES = "Bytes"
        BYTES_PER_SECOND = "BytesPerSecond"
        BYTE_SECONDS = "ByteSeconds"
        CORES = "Cores"
        COUNT = "Count"
        COUNT_PER_SECOND = "CountPerSecond"
        MILLI_CORES = "MilliCores"
        MILLI_SECONDS = "MilliSeconds"
        NANO_CORES = "NanoCores"
        PERCENT = "Percent"
        SECONDS = "Seconds"
        UNSPECIFIED = "Unspecified"


    class azure.mgmt.monitor.models.MetricValue(_Model):
        average: Optional[float]
        count: Optional[float]
        maximum: Optional[float]
        minimum: Optional[float]
        time_stamp: datetime
        total: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                average: Optional[float] = ..., 
                count: Optional[float] = ..., 
                maximum: Optional[float] = ..., 
                minimum: Optional[float] = ..., 
                time_stamp: datetime, 
                total: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.MetricsIngestionEndpointSpec(_Model):
        endpoint: Optional[str]


    class azure.mgmt.monitor.models.MicrosoftFabricDestination(_Model):
        artifact_id: Optional[str]
        database_name: Optional[str]
        ingestion_uri: Optional[str]
        name: Optional[str]
        tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                artifact_id: Optional[str] = ..., 
                database_name: Optional[str] = ..., 
                ingestion_uri: Optional[str] = ..., 
                name: Optional[str] = ..., 
                tenant_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.MonitoringAccountDestination(_Model):
        account_id: Optional[str]
        account_resource_id: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                account_resource_id: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.MultiMetricCriteria(_Model):
        criterion_type: str
        dimensions: Optional[list[MetricDimension]]
        metric_name: str
        metric_namespace: Optional[str]
        name: str
        skip_metric_validation: Optional[bool]
        time_aggregation: Union[str, AggregationTypeEnum]

        @overload
        def __init__(
                self, 
                *, 
                criterion_type: str, 
                dimensions: Optional[list[MetricDimension]] = ..., 
                metric_name: str, 
                metric_namespace: Optional[str] = ..., 
                name: str, 
                skip_metric_validation: Optional[bool] = ..., 
                time_aggregation: Union[str, AggregationTypeEnum]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.MultiPromQLCriteria(_Model):
        criterion_type: str
        name: str
        query: str

        @overload
        def __init__(
                self, 
                *, 
                criterion_type: str, 
                name: str, 
                query: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.NamespaceClassification(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM = "Custom"
        PLATFORM = "Platform"
        QOS = "Qos"


    class azure.mgmt.monitor.models.NetworkRuleSet(_Model):
        public_network_access: Optional[Union[str, KnownPublicNetworkAccessOptions]]

        @overload
        def __init__(
                self, 
                *, 
                public_network_access: Optional[Union[str, KnownPublicNetworkAccessOptions]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.NetworkSecurityPerimeter(_Model):
        id: Optional[str]
        location: Optional[str]
        perimeter_guid: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                location: Optional[str] = ..., 
                perimeter_guid: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.NetworkSecurityPerimeterConfiguration(ProxyResource):
        id: str
        name: str
        properties: Optional[NetworkSecurityPerimeterConfigurationProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[NetworkSecurityPerimeterConfigurationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.NetworkSecurityPerimeterConfigurationProperties(_Model):
        network_security_perimeter: Optional[NetworkSecurityPerimeter]
        profile: Optional[NetworkSecurityProfile]
        provisioning_issues: Optional[list[ProvisioningIssue]]
        provisioning_state: Optional[Union[str, NetworkSecurityPerimeterConfigurationProvisioningState]]
        resource_association: Optional[ResourceAssociation]

        @overload
        def __init__(
                self, 
                *, 
                network_security_perimeter: Optional[NetworkSecurityPerimeter] = ..., 
                profile: Optional[NetworkSecurityProfile] = ..., 
                resource_association: Optional[ResourceAssociation] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.NetworkSecurityPerimeterConfigurationProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.monitor.models.NetworkSecurityProfile(_Model):
        access_rules: Optional[list[AccessRule]]
        access_rules_version: Optional[int]
        diagnostic_settings_version: Optional[int]
        enabled_log_categories: Optional[list[str]]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                access_rules: Optional[list[AccessRule]] = ..., 
                access_rules_version: Optional[int] = ..., 
                diagnostic_settings_version: Optional[int] = ..., 
                enabled_log_categories: Optional[list[str]] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.NotificationRequestBody(_Model):
        alert_type: str
        arm_role_receivers: Optional[list[ArmRoleReceiver]]
        automation_runbook_receivers: Optional[list[AutomationRunbookReceiver]]
        azure_app_push_receivers: Optional[list[AzureAppPushReceiver]]
        azure_function_receivers: Optional[list[AzureFunctionReceiver]]
        email_receivers: Optional[list[EmailReceiver]]
        event_hub_receivers: Optional[list[EventHubReceiver]]
        incident_receivers: Optional[list[IncidentReceiver]]
        itsm_receivers: Optional[list[ItsmReceiver]]
        logic_app_receivers: Optional[list[LogicAppReceiver]]
        sms_receivers: Optional[list[SmsReceiver]]
        voice_receivers: Optional[list[VoiceReceiver]]
        webhook_receivers: Optional[list[WebhookReceiver]]

        @overload
        def __init__(
                self, 
                *, 
                alert_type: str, 
                arm_role_receivers: Optional[list[ArmRoleReceiver]] = ..., 
                automation_runbook_receivers: Optional[list[AutomationRunbookReceiver]] = ..., 
                azure_app_push_receivers: Optional[list[AzureAppPushReceiver]] = ..., 
                azure_function_receivers: Optional[list[AzureFunctionReceiver]] = ..., 
                email_receivers: Optional[list[EmailReceiver]] = ..., 
                event_hub_receivers: Optional[list[EventHubReceiver]] = ..., 
                incident_receivers: Optional[list[IncidentReceiver]] = ..., 
                itsm_receivers: Optional[list[ItsmReceiver]] = ..., 
                logic_app_receivers: Optional[list[LogicAppReceiver]] = ..., 
                sms_receivers: Optional[list[SmsReceiver]] = ..., 
                voice_receivers: Optional[list[VoiceReceiver]] = ..., 
                webhook_receivers: Optional[list[WebhookReceiver]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.Odatatype(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MICROSOFT_AZURE_MONITOR_MULTIPLE_RESOURCE_MULTIPLE_METRIC_CRITERIA = "Microsoft.Azure.Monitor.MultipleResourceMultipleMetricCriteria"
        MICROSOFT_AZURE_MONITOR_PROM_QL_CRITERIA = "Microsoft.Azure.Monitor.PromQLCriteria"
        MICROSOFT_AZURE_MONITOR_SINGLE_RESOURCE_MULTIPLE_METRIC_CRITERIA = "Microsoft.Azure.Monitor.SingleResourceMultipleMetricCriteria"
        MICROSOFT_AZURE_MONITOR_WEBTEST_LOCATION_AVAILABILITY_CRITERIA = "Microsoft.Azure.Monitor.WebtestLocationAvailabilityCriteria"


    class azure.mgmt.monitor.models.OnboardingStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_ONBOARDED = "notOnboarded"
        ONBOARDED = "onboarded"
        UNKNOWN = "unknown"


    class azure.mgmt.monitor.models.OperationStatus(_Model):
        end_time: Optional[datetime]
        error: Optional[ErrorDetailAutoGenerated]
        id: Optional[str]
        name: Optional[str]
        start_time: Optional[datetime]
        status: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                error: Optional[ErrorDetailAutoGenerated] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                start_time: Optional[datetime] = ..., 
                status: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.OperationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SCALE = "Scale"


    class azure.mgmt.monitor.models.Operator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EQUALS = "Equals"
        GREATER_THAN = "GreaterThan"
        GREATER_THAN_OR_EQUAL = "GreaterThanOrEqual"
        LESS_THAN = "LessThan"
        LESS_THAN_OR_EQUAL = "LessThanOrEqual"


    class azure.mgmt.monitor.models.OtelDataSourceResourceAttributeRouting(_Model):
        attribute_name: Optional[str]
        attribute_value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                attribute_name: Optional[str] = ..., 
                attribute_value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.OtelLogsDataSource(_Model):
        enrich_with_reference: Optional[str]
        enrich_with_resource_attributes: Optional[list[str]]
        name: Optional[str]
        replace_resource_id_with_reference: Optional[bool]
        resource_attribute_routing: Optional[OtelLogsDataSourceResourceAttributeRouting]
        streams: list[Union[str, KnownOtelLogsDataSourceStreams]]

        @overload
        def __init__(
                self, 
                *, 
                enrich_with_reference: Optional[str] = ..., 
                enrich_with_resource_attributes: Optional[list[str]] = ..., 
                name: Optional[str] = ..., 
                replace_resource_id_with_reference: Optional[bool] = ..., 
                resource_attribute_routing: Optional[OtelLogsDataSourceResourceAttributeRouting] = ..., 
                streams: list[Union[str, KnownOtelLogsDataSourceStreams]]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.OtelLogsDataSourceResourceAttributeRouting(OtelDataSourceResourceAttributeRouting):
        attribute_name: str
        attribute_value: str

        @overload
        def __init__(
                self, 
                *, 
                attribute_name: Optional[str] = ..., 
                attribute_value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.OtelLogsDirectDataSource(_Model):
        enrich_with_reference: Optional[str]
        enrich_with_resource_attributes: Optional[list[str]]
        name: Optional[str]
        replace_resource_id_with_reference: Optional[bool]
        streams: list[Union[str, KnownOtelLogsDirectDataSourceStreams]]

        @overload
        def __init__(
                self, 
                *, 
                enrich_with_reference: Optional[str] = ..., 
                enrich_with_resource_attributes: Optional[list[str]] = ..., 
                name: Optional[str] = ..., 
                replace_resource_id_with_reference: Optional[bool] = ..., 
                streams: list[Union[str, KnownOtelLogsDirectDataSourceStreams]]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.OtelMetricsDataSource(_Model):
        enrich_with_reference: Optional[str]
        enrich_with_resource_attributes: Optional[list[str]]
        name: Optional[str]
        resource_attribute_routing: Optional[OtelMetricsDataSourceResourceAttributeRouting]
        streams: list[str]

        @overload
        def __init__(
                self, 
                *, 
                enrich_with_reference: Optional[str] = ..., 
                enrich_with_resource_attributes: Optional[list[str]] = ..., 
                name: Optional[str] = ..., 
                resource_attribute_routing: Optional[OtelMetricsDataSourceResourceAttributeRouting] = ..., 
                streams: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.OtelMetricsDataSourceResourceAttributeRouting(OtelDataSourceResourceAttributeRouting):
        attribute_name: str
        attribute_value: str

        @overload
        def __init__(
                self, 
                *, 
                attribute_name: Optional[str] = ..., 
                attribute_value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.OtelMetricsDirectDataSource(_Model):
        enrich_with_reference: Optional[str]
        enrich_with_resource_attributes: Optional[list[str]]
        name: Optional[str]
        streams: list[str]

        @overload
        def __init__(
                self, 
                *, 
                enrich_with_reference: Optional[str] = ..., 
                enrich_with_resource_attributes: Optional[list[str]] = ..., 
                name: Optional[str] = ..., 
                streams: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.OtelTracesDataSource(_Model):
        enrich_with_reference: Optional[str]
        enrich_with_resource_attributes: Optional[list[str]]
        name: Optional[str]
        replace_resource_id_with_reference: Optional[bool]
        resource_attribute_routing: Optional[OtelTracesDataSourceResourceAttributeRouting]
        streams: list[Union[str, KnownOtelTracesDataSourceStreams]]

        @overload
        def __init__(
                self, 
                *, 
                enrich_with_reference: Optional[str] = ..., 
                enrich_with_resource_attributes: Optional[list[str]] = ..., 
                name: Optional[str] = ..., 
                replace_resource_id_with_reference: Optional[bool] = ..., 
                resource_attribute_routing: Optional[OtelTracesDataSourceResourceAttributeRouting] = ..., 
                streams: list[Union[str, KnownOtelTracesDataSourceStreams]]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.OtelTracesDataSourceResourceAttributeRouting(OtelDataSourceResourceAttributeRouting):
        attribute_name: str
        attribute_value: str

        @overload
        def __init__(
                self, 
                *, 
                attribute_name: Optional[str] = ..., 
                attribute_value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.OtelTracesDirectDataSource(_Model):
        enrich_with_reference: Optional[str]
        enrich_with_resource_attributes: Optional[list[str]]
        name: Optional[str]
        replace_resource_id_with_reference: Optional[bool]
        streams: list[Union[str, KnownOtelTracesDirectDataSourceStreams]]

        @overload
        def __init__(
                self, 
                *, 
                enrich_with_reference: Optional[str] = ..., 
                enrich_with_resource_attributes: Optional[list[str]] = ..., 
                name: Optional[str] = ..., 
                replace_resource_id_with_reference: Optional[bool] = ..., 
                streams: list[Union[str, KnownOtelTracesDirectDataSourceStreams]]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.PerfCounterDataSource(_Model):
        counter_specifiers: Optional[list[str]]
        name: Optional[str]
        sampling_frequency_in_seconds: Optional[int]
        streams: Optional[list[Union[str, KnownPerfCounterDataSourceStreams]]]
        transform_kql: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                counter_specifiers: Optional[list[str]] = ..., 
                name: Optional[str] = ..., 
                sampling_frequency_in_seconds: Optional[int] = ..., 
                streams: Optional[list[Union[str, KnownPerfCounterDataSourceStreams]]] = ..., 
                transform_kql: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.PerformanceCountersOTelDataSource(_Model):
        counter_specifiers: Optional[list[str]]
        name: Optional[str]
        sampling_frequency_in_seconds: Optional[int]
        streams: Optional[list[Union[str, KnownPerformanceCountersOTelDataSourceStreams]]]

        @overload
        def __init__(
                self, 
                *, 
                counter_specifiers: Optional[list[str]] = ..., 
                name: Optional[str] = ..., 
                sampling_frequency_in_seconds: Optional[int] = ..., 
                streams: Optional[list[Union[str, KnownPerformanceCountersOTelDataSourceStreams]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.PlatformTelemetryDataSource(_Model):
        name: Optional[str]
        streams: list[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                streams: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.PredictiveAutoscalePolicy(_Model):
        scale_look_ahead_time: Optional[timedelta]
        scale_mode: Union[str, PredictiveAutoscalePolicyScaleMode]

        @overload
        def __init__(
                self, 
                *, 
                scale_look_ahead_time: Optional[timedelta] = ..., 
                scale_mode: Union[str, PredictiveAutoscalePolicyScaleMode]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.PredictiveAutoscalePolicyScaleMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        FORECAST_ONLY = "ForecastOnly"


    class azure.mgmt.monitor.models.PredictiveResponse(_Model):
        data: Optional[list[PredictiveValue]]
        interval: Optional[timedelta]
        metric_name: Optional[str]
        target_resource_id: Optional[str]
        timespan: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                data: Optional[list[PredictiveValue]] = ..., 
                interval: Optional[timedelta] = ..., 
                metric_name: Optional[str] = ..., 
                target_resource_id: Optional[str] = ..., 
                timespan: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.PredictiveValue(_Model):
        time_stamp: datetime
        value: float

        @overload
        def __init__(
                self, 
                *, 
                time_stamp: datetime, 
                value: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.PrivateEndpoint(_Model):
        id: Optional[str]


    class azure.mgmt.monitor.models.PrivateEndpointConnection(Resource):
        id: str
        name: str
        properties: Optional[PrivateEndpointConnectionProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PrivateEndpointConnectionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.monitor.models.PrivateEndpointConnectionProperties(_Model):
        group_ids: Optional[list[str]]
        private_endpoint: Optional[PrivateEndpoint]
        private_link_service_connection_state: PrivateLinkServiceConnectionState
        provisioning_state: Optional[Union[str, PrivateEndpointConnectionProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                private_endpoint: Optional[PrivateEndpoint] = ..., 
                private_link_service_connection_state: PrivateLinkServiceConnectionState
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.PrivateEndpointConnectionProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.monitor.models.PrivateEndpointServiceConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.monitor.models.PrivateLinkResource(Resource):
        id: str
        name: str
        properties: Optional[PrivateLinkResourceProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PrivateLinkResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.PrivateLinkResourceProperties(_Model):
        group_id: Optional[str]
        required_members: Optional[list[str]]
        required_zone_names: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                required_zone_names: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.PrivateLinkScopeProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.monitor.models.PrivateLinkScopedResource(_Model):
        resource_id: Optional[str]
        scope_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                resource_id: Optional[str] = ..., 
                scope_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.PrivateLinkServiceConnectionState(_Model):
        actions_required: Optional[str]
        description: Optional[str]
        status: Optional[Union[str, PrivateEndpointServiceConnectionStatus]]

        @overload
        def __init__(
                self, 
                *, 
                actions_required: Optional[str] = ..., 
                description: Optional[str] = ..., 
                status: Optional[Union[str, PrivateEndpointServiceConnectionStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.PromQLCriteria(MetricAlertCriteria, discriminator='Microsoft.Azure.Monitor.PromQLCriteria'):
        all_of: Optional[list[MultiPromQLCriteria]]
        failing_periods: Optional[QueryFailingPeriods]
        odata_type: Literal[Odatatype.MICROSOFT_AZURE_MONITOR_PROM_QL_CRITERIA]

        @overload
        def __init__(
                self, 
                *, 
                all_of: Optional[list[MultiPromQLCriteria]] = ..., 
                failing_periods: Optional[QueryFailingPeriods] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.PrometheusForwarderDataSource(_Model):
        custom_vm_scrape_config: Optional[list[Any]]
        label_include_filter: Optional[dict[str, str]]
        name: Optional[str]
        streams: Optional[list[Union[str, KnownPrometheusForwarderDataSourceStreams]]]

        @overload
        def __init__(
                self, 
                *, 
                custom_vm_scrape_config: Optional[list[Any]] = ..., 
                label_include_filter: Optional[dict[str, str]] = ..., 
                name: Optional[str] = ..., 
                streams: Optional[list[Union[str, KnownPrometheusForwarderDataSourceStreams]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.ProvisioningIssue(_Model):
        name: Optional[str]
        properties: Optional[ProvisioningIssueProperties]


    class azure.mgmt.monitor.models.ProvisioningIssueProperties(_Model):
        description: Optional[str]
        issue_type: Optional[Union[str, IssueType]]
        severity: Optional[Union[str, Severity]]
        suggested_access_rules: Optional[list[AccessRule]]
        suggested_resource_ids: Optional[list[str]]


    class azure.mgmt.monitor.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.monitor.models.QueryFailingPeriods(_Model):
        for_property: timedelta

        @overload
        def __init__(
                self, 
                *, 
                for_property: timedelta
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.ReceiverStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        NOT_SPECIFIED = "NotSpecified"


    class azure.mgmt.monitor.models.Recurrence(_Model):
        frequency: Union[str, RecurrenceFrequency]
        schedule: RecurrentSchedule

        @overload
        def __init__(
                self, 
                *, 
                frequency: Union[str, RecurrenceFrequency], 
                schedule: RecurrentSchedule
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.RecurrenceFrequency(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DAY = "Day"
        HOUR = "Hour"
        MINUTE = "Minute"
        MONTH = "Month"
        NONE = "None"
        SECOND = "Second"
        WEEK = "Week"
        YEAR = "Year"


    class azure.mgmt.monitor.models.RecurrentSchedule(_Model):
        days: list[str]
        hours: list[int]
        minutes: list[int]
        time_zone: str

        @overload
        def __init__(
                self, 
                *, 
                days: list[str], 
                hours: list[int], 
                minutes: list[int], 
                time_zone: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.ReferencesSpec(_Model):
        application_insights: Optional[list[ApplicationInsights]]
        enrichment_data: Optional[ReferencesSpecEnrichmentData]

        @overload
        def __init__(
                self, 
                *, 
                application_insights: Optional[list[ApplicationInsights]] = ..., 
                enrichment_data: Optional[ReferencesSpecEnrichmentData] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.ReferencesSpecEnrichmentData(EnrichmentData):
        storage_blobs: list[StorageBlob]

        @overload
        def __init__(
                self, 
                *, 
                storage_blobs: Optional[list[StorageBlob]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.ResolveConfiguration(_Model):
        auto_resolved: bool
        time_to_resolve: Optional[timedelta]

        @overload
        def __init__(
                self, 
                *, 
                auto_resolved: bool, 
                time_to_resolve: Optional[timedelta] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.monitor.models.ResourceAssociation(_Model):
        access_mode: Optional[Union[str, ResourceAssociationAccessMode]]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                access_mode: Optional[Union[str, ResourceAssociationAccessMode]] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.ResourceAssociationAccessMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUDIT = "Audit"
        ENFORCED = "Enforced"
        LEARNING = "Learning"


    class azure.mgmt.monitor.models.ResourceForUpdate(_Model):
        identity: Optional[ResourceForUpdateIdentity]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ResourceForUpdateIdentity] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.ResourceForUpdateIdentity(ManagedServiceIdentity):
        principal_id: str
        tenant_id: str
        type: Union[str, ManagedServiceIdentityType]
        user_assigned_identities: dict[str, UserAssignedIdentity]

        @overload
        def __init__(
                self, 
                *, 
                type: Union[str, ManagedServiceIdentityType], 
                user_assigned_identities: Optional[dict[str, UserAssignedIdentity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.Response(_Model):
        cost: Optional[int]
        interval: Optional[str]
        namespace: Optional[str]
        resourceregion: Optional[str]
        timespan: str
        value: list[Metric]

        @overload
        def __init__(
                self, 
                *, 
                cost: Optional[int] = ..., 
                interval: Optional[str] = ..., 
                namespace: Optional[str] = ..., 
                resourceregion: Optional[str] = ..., 
                timespan: str, 
                value: list[Metric]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.ResponseWithError(_Model):
        error: Error

        @overload
        def __init__(
                self, 
                *, 
                error: Error
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.ResultType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DATA = "Data"
        METADATA = "Metadata"


    class azure.mgmt.monitor.models.RetentionPolicy(_Model):
        days: int
        enabled: bool

        @overload
        def __init__(
                self, 
                *, 
                days: int, 
                enabled: bool
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.RuleResolveConfiguration(_Model):
        auto_resolved: Optional[bool]
        time_to_resolve: Optional[timedelta]

        @overload
        def __init__(
                self, 
                *, 
                auto_resolved: Optional[bool] = ..., 
                time_to_resolve: Optional[timedelta] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.ScaleAction(_Model):
        cooldown: timedelta
        direction: Union[str, ScaleDirection]
        type: Union[str, ScaleType]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                cooldown: timedelta, 
                direction: Union[str, ScaleDirection], 
                type: Union[str, ScaleType], 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.ScaleCapacity(_Model):
        default: str
        maximum: str
        minimum: str

        @overload
        def __init__(
                self, 
                *, 
                default: str, 
                maximum: str, 
                minimum: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.ScaleDirection(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DECREASE = "Decrease"
        INCREASE = "Increase"
        NONE = "None"


    class azure.mgmt.monitor.models.ScaleRule(_Model):
        metric_trigger: MetricTrigger
        scale_action: ScaleAction

        @overload
        def __init__(
                self, 
                *, 
                metric_trigger: MetricTrigger, 
                scale_action: ScaleAction
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.ScaleRuleMetricDimension(_Model):
        dimension_name: str
        operator: Union[str, ScaleRuleMetricDimensionOperationType]
        values_property: list[str]

        @overload
        def __init__(
                self, 
                *, 
                dimension_name: str, 
                operator: Union[str, ScaleRuleMetricDimensionOperationType], 
                values_property: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.ScaleRuleMetricDimensionOperationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EQUALS = "Equals"
        NOT_EQUALS = "NotEquals"


    class azure.mgmt.monitor.models.ScaleType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CHANGE_COUNT = "ChangeCount"
        EXACT_COUNT = "ExactCount"
        PERCENT_CHANGE_COUNT = "PercentChangeCount"
        SERVICE_ALLOWED_NEXT_VALUE = "ServiceAllowedNextValue"


    class azure.mgmt.monitor.models.ScheduledQueryRuleCriteria(_Model):
        all_of: Optional[list[Condition]]

        @overload
        def __init__(
                self, 
                *, 
                all_of: Optional[list[Condition]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.ScheduledQueryRuleProperties(_Model):
        actions: Optional[Actions]
        auto_mitigate: Optional[bool]
        check_workspace_alerts_storage_configured: Optional[bool]
        created_with_api_version: Optional[str]
        criteria: Optional[ScheduledQueryRuleCriteria]
        description: Optional[str]
        display_name: Optional[str]
        enabled: Optional[bool]
        evaluation_frequency: Optional[timedelta]
        is_legacy_log_analytics_rule: Optional[bool]
        is_workspace_alerts_storage_configured: Optional[bool]
        mute_actions_duration: Optional[timedelta]
        override_query_time_range: Optional[timedelta]
        resolve_configuration: Optional[RuleResolveConfiguration]
        scopes: Optional[list[str]]
        severity: Optional[Union[int, AlertSeverity]]
        skip_query_validation: Optional[bool]
        target_resource_types: Optional[list[str]]
        window_size: Optional[timedelta]

        @overload
        def __init__(
                self, 
                *, 
                actions: Optional[Actions] = ..., 
                auto_mitigate: Optional[bool] = ..., 
                check_workspace_alerts_storage_configured: Optional[bool] = ..., 
                criteria: Optional[ScheduledQueryRuleCriteria] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                enabled: Optional[bool] = ..., 
                evaluation_frequency: Optional[timedelta] = ..., 
                mute_actions_duration: Optional[timedelta] = ..., 
                override_query_time_range: Optional[timedelta] = ..., 
                resolve_configuration: Optional[RuleResolveConfiguration] = ..., 
                scopes: Optional[list[str]] = ..., 
                severity: Optional[Union[int, AlertSeverity]] = ..., 
                skip_query_validation: Optional[bool] = ..., 
                target_resource_types: Optional[list[str]] = ..., 
                window_size: Optional[timedelta] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.ScheduledQueryRuleResource(ProxyResource):
        etag: Optional[str]
        id: str
        identity: Optional[Identity]
        kind: Optional[Union[str, Kind]]
        location: str
        name: str
        properties: ScheduledQueryRuleProperties
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[Identity] = ..., 
                kind: Optional[Union[str, Kind]] = ..., 
                location: str, 
                properties: ScheduledQueryRuleProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.monitor.models.ScheduledQueryRuleResourcePatch(_Model):
        identity: Optional[Identity]
        properties: Optional[ScheduledQueryRuleProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[Identity] = ..., 
                properties: Optional[ScheduledQueryRuleProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.monitor.models.ScopedResource(ProxyResource):
        id: str
        name: str
        properties: Optional[ScopedResourceProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ScopedResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.monitor.models.ScopedResourceKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        METRICS = "Metrics"
        RESOURCE = "Resource"


    class azure.mgmt.monitor.models.ScopedResourceProperties(_Model):
        kind: Optional[Union[str, ScopedResourceKind]]
        linked_resource_id: Optional[str]
        provisioning_state: Optional[Union[str, ScopedResourceProvisioningState]]
        subscription_location: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                kind: Optional[Union[str, ScopedResourceKind]] = ..., 
                linked_resource_id: Optional[str] = ..., 
                subscription_location: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.ScopedResourceProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.monitor.models.SenderAuthorization(_Model):
        action: Optional[str]
        role: Optional[str]
        scope: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                action: Optional[str] = ..., 
                role: Optional[str] = ..., 
                scope: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.ServiceDiagnosticSettings(_Model):
        event_hub_authorization_rule_id: Optional[str]
        logs: Optional[list[DiagnosticsLogSettings]]
        metrics: Optional[list[DiagnosticsMetricSettings]]
        service_bus_rule_id: Optional[str]
        storage_account_id: Optional[str]
        workspace_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                event_hub_authorization_rule_id: Optional[str] = ..., 
                logs: Optional[list[DiagnosticsLogSettings]] = ..., 
                metrics: Optional[list[DiagnosticsMetricSettings]] = ..., 
                service_bus_rule_id: Optional[str] = ..., 
                storage_account_id: Optional[str] = ..., 
                workspace_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.ServiceDiagnosticSettingsResource(ExtensionResource):
        id: str
        location: str
        name: str
        properties: Optional[ServiceDiagnosticSettings]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[ServiceDiagnosticSettings] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.monitor.models.ServiceDiagnosticSettingsResourcePatch(_Model):
        properties: Optional[ServiceDiagnosticSettings]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ServiceDiagnosticSettings] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.monitor.models.Severity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ERROR = "Error"
        WARNING = "Warning"


    class azure.mgmt.monitor.models.SingleBaseline(_Model):
        high_thresholds: list[float]
        low_thresholds: list[float]
        sensitivity: Union[str, BaselineSensitivity]

        @overload
        def __init__(
                self, 
                *, 
                high_thresholds: list[float], 
                low_thresholds: list[float], 
                sensitivity: Union[str, BaselineSensitivity]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.SingleMetricBaseline(_Model):
        id: str
        name: str
        properties: MetricBaselinesProperties
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                name: str, 
                properties: MetricBaselinesProperties, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.monitor.models.Sku(_Model):
        capacity: Optional[int]
        family: Optional[str]
        name: str
        size: Optional[str]
        tier: Optional[Union[str, SkuTier]]

        @overload
        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                family: Optional[str] = ..., 
                name: str, 
                size: Optional[str] = ..., 
                tier: Optional[Union[str, SkuTier]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.SkuTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC = "Basic"
        FREE = "Free"
        PREMIUM = "Premium"
        STANDARD = "Standard"


    class azure.mgmt.monitor.models.SmsReceiver(_Model):
        country_code: str
        name: str
        phone_number: str
        status: Optional[Union[str, ReceiverStatus]]

        @overload
        def __init__(
                self, 
                *, 
                country_code: str, 
                name: str, 
                phone_number: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.StaticPromQLCriteria(MultiPromQLCriteria, discriminator='StaticThresholdCriterion'):
        criterion_type: Literal[CriterionType.STATIC_THRESHOLD_CRITERION]
        name: str
        query: str

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                query: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.StorageBlob(_Model):
        blob_url: Optional[str]
        lookup_type: Optional[Union[str, KnownStorageBlobLookupType]]
        name: Optional[str]
        resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                blob_url: Optional[str] = ..., 
                lookup_type: Optional[Union[str, KnownStorageBlobLookupType]] = ..., 
                name: Optional[str] = ..., 
                resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.StorageBlobDestination(_Model):
        container_name: Optional[str]
        name: Optional[str]
        storage_account_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                container_name: Optional[str] = ..., 
                name: Optional[str] = ..., 
                storage_account_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.StorageTableDestination(_Model):
        name: Optional[str]
        storage_account_resource_id: Optional[str]
        table_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                storage_account_resource_id: Optional[str] = ..., 
                table_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.StreamDeclaration(_Model):
        columns: Optional[list[ColumnDefinition]]

        @overload
        def __init__(
                self, 
                *, 
                columns: Optional[list[ColumnDefinition]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.SubscriptionScopeMetricDefinition(_Model):
        category: Optional[str]
        dimensions: Optional[list[LocalizableString]]
        display_description: Optional[str]
        id: Optional[str]
        is_dimension_required: Optional[bool]
        metric_availabilities: Optional[list[MetricAvailability]]
        metric_class: Optional[Union[str, MetricClass]]
        name: Optional[LocalizableString]
        namespace: Optional[str]
        primary_aggregation_type: Optional[Union[str, MetricAggregationType]]
        resource_id: Optional[str]
        supported_aggregation_types: Optional[list[Union[str, MetricAggregationType]]]
        unit: Optional[Union[str, MetricUnit]]

        @overload
        def __init__(
                self, 
                *, 
                category: Optional[str] = ..., 
                dimensions: Optional[list[LocalizableString]] = ..., 
                display_description: Optional[str] = ..., 
                id: Optional[str] = ..., 
                is_dimension_required: Optional[bool] = ..., 
                metric_availabilities: Optional[list[MetricAvailability]] = ..., 
                metric_class: Optional[Union[str, MetricClass]] = ..., 
                name: Optional[LocalizableString] = ..., 
                namespace: Optional[str] = ..., 
                primary_aggregation_type: Optional[Union[str, MetricAggregationType]] = ..., 
                resource_id: Optional[str] = ..., 
                supported_aggregation_types: Optional[list[Union[str, MetricAggregationType]]] = ..., 
                unit: Optional[Union[str, MetricUnit]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.SubscriptionScopeMetricsRequestBodyParameters(_Model):
        aggregation: Optional[str]
        auto_adjust_timegrain: Optional[bool]
        filter: Optional[str]
        interval: Optional[str]
        metric_names: Optional[str]
        metric_namespace: Optional[str]
        order_by: Optional[str]
        result_type: Optional[Union[str, MetricResultType]]
        roll_up_by: Optional[str]
        timespan: Optional[str]
        top: Optional[int]
        validate_dimensions: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                aggregation: Optional[str] = ..., 
                auto_adjust_timegrain: Optional[bool] = ..., 
                filter: Optional[str] = ..., 
                interval: Optional[str] = ..., 
                metric_names: Optional[str] = ..., 
                metric_namespace: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
                result_type: Optional[Union[str, MetricResultType]] = ..., 
                roll_up_by: Optional[str] = ..., 
                timespan: Optional[str] = ..., 
                top: Optional[int] = ..., 
                validate_dimensions: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.SyslogDataSource(_Model):
        facility_names: Optional[list[Union[str, KnownSyslogDataSourceFacilityNames]]]
        log_levels: Optional[list[Union[str, KnownSyslogDataSourceLogLevels]]]
        name: Optional[str]
        streams: Optional[list[Union[str, KnownSyslogDataSourceStreams]]]
        transform_kql: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                facility_names: Optional[list[Union[str, KnownSyslogDataSourceFacilityNames]]] = ..., 
                log_levels: Optional[list[Union[str, KnownSyslogDataSourceLogLevels]]] = ..., 
                name: Optional[str] = ..., 
                streams: Optional[list[Union[str, KnownSyslogDataSourceStreams]]] = ..., 
                transform_kql: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.SystemData(_Model):
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


    class azure.mgmt.monitor.models.TagsResource(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.TenantActionGroup(_Model):
        azure_app_push_receivers: Optional[list[AzureAppPushReceiver]]
        email_receivers: Optional[list[EmailReceiver]]
        enabled: bool
        group_short_name: str
        sms_receivers: Optional[list[SmsReceiver]]
        voice_receivers: Optional[list[VoiceReceiver]]
        webhook_receivers: Optional[list[TenantActionGroupWebhookReceiver]]

        @overload
        def __init__(
                self, 
                *, 
                azure_app_push_receivers: Optional[list[AzureAppPushReceiver]] = ..., 
                email_receivers: Optional[list[EmailReceiver]] = ..., 
                enabled: bool, 
                group_short_name: str, 
                sms_receivers: Optional[list[SmsReceiver]] = ..., 
                voice_receivers: Optional[list[VoiceReceiver]] = ..., 
                webhook_receivers: Optional[list[TenantActionGroupWebhookReceiver]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.TenantActionGroupActionDetail(_Model):
        mechanism_type: Optional[str]
        message: Optional[str]
        name: Optional[str]
        send_time: Optional[str]
        status: Optional[str]
        sub_state: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                mechanism_type: Optional[str] = ..., 
                message: Optional[str] = ..., 
                name: Optional[str] = ..., 
                send_time: Optional[str] = ..., 
                status: Optional[str] = ..., 
                sub_state: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.TenantActionGroupPatchBody(_Model):
        properties: Optional[ActionGroupPatch]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ActionGroupPatch] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.monitor.models.TenantActionGroupResource(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[TenantActionGroup]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[TenantActionGroup] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.monitor.models.TenantActionGroupTestNotificationDetailsResponse(_Model):
        action_details: Optional[list[TenantActionGroupActionDetail]]
        completed_time: Optional[str]
        context: Optional[Context]
        created_time: Optional[str]
        state: str

        @overload
        def __init__(
                self, 
                *, 
                action_details: Optional[list[TenantActionGroupActionDetail]] = ..., 
                completed_time: Optional[str] = ..., 
                context: Optional[Context] = ..., 
                created_time: Optional[str] = ..., 
                state: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.TenantActionGroupWebhookReceiver(_Model):
        identifier_uri: Optional[str]
        name: str
        object_id: Optional[str]
        service_uri: str
        tenant_id: Optional[str]
        use_aad_auth: Optional[bool]
        use_common_alert_schema: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                identifier_uri: Optional[str] = ..., 
                name: str, 
                object_id: Optional[str] = ..., 
                service_uri: str, 
                tenant_id: Optional[str] = ..., 
                use_aad_auth: Optional[bool] = ..., 
                use_common_alert_schema: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.TenantNotificationRequestBody(_Model):
        alert_type: str
        azure_app_push_receivers: Optional[list[AzureAppPushReceiver]]
        email_receivers: Optional[list[EmailReceiver]]
        sms_receivers: Optional[list[SmsReceiver]]
        voice_receivers: Optional[list[VoiceReceiver]]
        webhook_receivers: Optional[list[TenantActionGroupWebhookReceiver]]

        @overload
        def __init__(
                self, 
                *, 
                alert_type: str, 
                azure_app_push_receivers: Optional[list[AzureAppPushReceiver]] = ..., 
                email_receivers: Optional[list[EmailReceiver]] = ..., 
                sms_receivers: Optional[list[SmsReceiver]] = ..., 
                voice_receivers: Optional[list[VoiceReceiver]] = ..., 
                webhook_receivers: Optional[list[TenantActionGroupWebhookReceiver]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.TestNotificationDetailsResponse(_Model):
        action_details: Optional[list[ActionDetail]]
        completed_time: Optional[str]
        context: Optional[Context]
        created_time: Optional[str]
        state: str

        @overload
        def __init__(
                self, 
                *, 
                action_details: Optional[list[ActionDetail]] = ..., 
                completed_time: Optional[str] = ..., 
                context: Optional[Context] = ..., 
                created_time: Optional[str] = ..., 
                state: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.TimeAggregation(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVERAGE = "Average"
        COUNT = "Count"
        MAXIMUM = "Maximum"
        MINIMUM = "Minimum"
        TOTAL = "Total"


    class azure.mgmt.monitor.models.TimeAggregationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVERAGE = "Average"
        COUNT = "Count"
        LAST = "Last"
        MAXIMUM = "Maximum"
        MINIMUM = "Minimum"
        TOTAL = "Total"


    class azure.mgmt.monitor.models.TimeSeriesBaseline(_Model):
        aggregation: str
        data: list[SingleBaseline]
        dimensions: Optional[list[MetricSingleDimension]]
        metadata_values: Optional[list[BaselineMetadata]]
        timestamps: list[datetime]

        @overload
        def __init__(
                self, 
                *, 
                aggregation: str, 
                data: list[SingleBaseline], 
                dimensions: Optional[list[MetricSingleDimension]] = ..., 
                metadata_values: Optional[list[BaselineMetadata]] = ..., 
                timestamps: list[datetime]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.TimeSeriesElement(_Model):
        data: Optional[list[MetricValue]]
        metadatavalues: Optional[list[MetadataValue]]

        @overload
        def __init__(
                self, 
                *, 
                data: Optional[list[MetricValue]] = ..., 
                metadatavalues: Optional[list[MetadataValue]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.TimeWindow(_Model):
        end: datetime
        start: datetime
        time_zone: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                end: datetime, 
                start: datetime, 
                time_zone: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.TrackedResource(Resource):
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


    class azure.mgmt.monitor.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.monitor.models.UserIdentityProperties(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.monitor.models.VMInsightsOnboardingStatus(ExtensionResource):
        id: str
        name: str
        properties: Optional[VMInsightsOnboardingStatusProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[VMInsightsOnboardingStatusProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.monitor.models.VMInsightsOnboardingStatusProperties(_Model):
        data: Optional[list[DataContainer]]
        data_status: Union[str, DataStatus]
        onboarding_status: Union[str, OnboardingStatus]
        resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                data: Optional[list[DataContainer]] = ..., 
                data_status: Union[str, DataStatus], 
                onboarding_status: Union[str, OnboardingStatus], 
                resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.VoiceReceiver(_Model):
        country_code: str
        name: str
        phone_number: str

        @overload
        def __init__(
                self, 
                *, 
                country_code: str, 
                name: str, 
                phone_number: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.WebhookNotification(_Model):
        properties: Optional[dict[str, str]]
        service_uri: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[dict[str, str]] = ..., 
                service_uri: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.WebhookReceiver(_Model):
        identifier_uri: Optional[str]
        managed_identity: Optional[str]
        name: str
        object_id: Optional[str]
        service_uri: str
        tenant_id: Optional[str]
        use_aad_auth: Optional[bool]
        use_common_alert_schema: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                identifier_uri: Optional[str] = ..., 
                managed_identity: Optional[str] = ..., 
                name: str, 
                object_id: Optional[str] = ..., 
                service_uri: str, 
                tenant_id: Optional[str] = ..., 
                use_aad_auth: Optional[bool] = ..., 
                use_common_alert_schema: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.WebtestLocationAvailabilityCriteria(MetricAlertCriteria, discriminator='Microsoft.Azure.Monitor.WebtestLocationAvailabilityCriteria'):
        component_id: str
        failed_location_count: float
        odata_type: Literal[Odatatype.MICROSOFT_AZURE_MONITOR_WEBTEST_LOCATION_AVAILABILITY_CRITERIA]
        web_test_id: str

        @overload
        def __init__(
                self, 
                *, 
                component_id: str, 
                failed_location_count: float, 
                web_test_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.WindowsEventLogDataSource(_Model):
        name: Optional[str]
        streams: Optional[list[Union[str, KnownWindowsEventLogDataSourceStreams]]]
        transform_kql: Optional[str]
        x_path_queries: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                streams: Optional[list[Union[str, KnownWindowsEventLogDataSourceStreams]]] = ..., 
                transform_kql: Optional[str] = ..., 
                x_path_queries: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.WindowsFirewallLogsDataSource(_Model):
        name: Optional[str]
        profile_filter: Optional[list[Union[str, KnownWindowsFirewallLogsDataSourceProfileFilter]]]
        streams: list[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                profile_filter: Optional[list[Union[str, KnownWindowsFirewallLogsDataSourceProfileFilter]]] = ..., 
                streams: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitor.models.WorkspaceInfo(_Model):
        id: str
        location: str
        properties: WorkspaceInfoProperties

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                location: str, 
                properties: WorkspaceInfoProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.monitor.models.WorkspaceInfoProperties(_Model):
        customer_id: str

        @overload
        def __init__(
                self, 
                *, 
                customer_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.monitor.operations

    class azure.mgmt.monitor.operations.ActionGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_notifications_at_action_group_resource_level(
                self, 
                resource_group_name: str, 
                action_group_name: str, 
                notification_request: NotificationRequestBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TestNotificationDetailsResponse]: ...

        @overload
        def begin_create_notifications_at_action_group_resource_level(
                self, 
                resource_group_name: str, 
                action_group_name: str, 
                notification_request: NotificationRequestBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TestNotificationDetailsResponse]: ...

        @overload
        def begin_create_notifications_at_action_group_resource_level(
                self, 
                resource_group_name: str, 
                action_group_name: str, 
                notification_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TestNotificationDetailsResponse]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2021-10-01', params_added_on={'2021-10-01': ['api_version', 'subscription_id', 'resource_group_name', 'action_group_name', 'network_security_perimeter_configuration_name']}, api_versions_list=['2021-10-01'])
        def begin_reconcile_nsp(
                self, 
                resource_group_name: str, 
                action_group_name: str, 
                network_security_perimeter_configuration_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                action_group_name: str, 
                action_group: ActionGroupResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ActionGroupResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                action_group_name: str, 
                action_group: ActionGroupResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ActionGroupResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                action_group_name: str, 
                action_group: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ActionGroupResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-10-01-preview', params_added_on={'2024-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'action_group_name']}, api_versions_list=['2024-10-01-preview'])
        def delete(
                self, 
                resource_group_name: str, 
                action_group_name: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        def enable_receiver(
                self, 
                resource_group_name: str, 
                action_group_name: str, 
                enable_request: EnableRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def enable_receiver(
                self, 
                resource_group_name: str, 
                action_group_name: str, 
                enable_request: EnableRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def enable_receiver(
                self, 
                resource_group_name: str, 
                action_group_name: str, 
                enable_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-10-01-preview', params_added_on={'2024-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'action_group_name', 'accept']}, api_versions_list=['2024-10-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                action_group_name: str, 
                **kwargs: Any
            ) -> ActionGroupResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2021-10-01', params_added_on={'2021-10-01': ['api_version', 'subscription_id', 'resource_group_name', 'action_group_name', 'network_security_perimeter_configuration_name', 'accept']}, api_versions_list=['2021-10-01'])
        def get_nsp(
                self, 
                resource_group_name: str, 
                action_group_name: str, 
                network_security_perimeter_configuration_name: str, 
                **kwargs: Any
            ) -> NetworkSecurityPerimeterConfiguration: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-10-01-preview', params_added_on={'2024-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'action_group_name', 'notification_id', 'accept']}, api_versions_list=['2024-10-01-preview'])
        def get_test_notifications_at_action_group_resource_level(
                self, 
                resource_group_name: str, 
                action_group_name: str, 
                notification_id: str, 
                **kwargs: Any
            ) -> TestNotificationDetailsResponse: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-10-01-preview', params_added_on={'2024-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2024-10-01-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ActionGroupResource]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-10-01-preview', params_added_on={'2024-10-01-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2024-10-01-preview'])
        def list_by_subscription_id(self, **kwargs: Any) -> ItemPaged[ActionGroupResource]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2021-10-01', params_added_on={'2021-10-01': ['api_version', 'subscription_id', 'resource_group_name', 'action_group_name', 'accept']}, api_versions_list=['2021-10-01'])
        def list_nsp(
                self, 
                resource_group_name: str, 
                action_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[NetworkSecurityPerimeterConfiguration]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                action_group_name: str, 
                action_group_patch: ActionGroupPatchBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ActionGroupResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                action_group_name: str, 
                action_group_patch: ActionGroupPatchBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ActionGroupResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                action_group_name: str, 
                action_group_patch: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ActionGroupResource: ...


    class azure.mgmt.monitor.operations.ActivityLogAlertsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                activity_log_alert_name: str, 
                activity_log_alert_rule: ActivityLogAlertResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ActivityLogAlertResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                activity_log_alert_name: str, 
                activity_log_alert_rule: ActivityLogAlertResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ActivityLogAlertResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                activity_log_alert_name: str, 
                activity_log_alert_rule: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ActivityLogAlertResource: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                activity_log_alert_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                activity_log_alert_name: str, 
                **kwargs: Any
            ) -> ActivityLogAlertResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ActivityLogAlertResource]: ...

        @distributed_trace
        def list_by_subscription_id(self, **kwargs: Any) -> ItemPaged[ActivityLogAlertResource]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                activity_log_alert_name: str, 
                activity_log_alert_rule_patch: AlertRulePatchObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ActivityLogAlertResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                activity_log_alert_name: str, 
                activity_log_alert_rule_patch: AlertRulePatchObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ActivityLogAlertResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                activity_log_alert_name: str, 
                activity_log_alert_rule_patch: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ActivityLogAlertResource: ...


    class azure.mgmt.monitor.operations.ActivityLogsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                *, 
                filter: str, 
                select: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[EventData]: ...


    class azure.mgmt.monitor.operations.AlertRuleIncidentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                rule_name: str, 
                incident_name: str, 
                **kwargs: Any
            ) -> Incident: ...

        @distributed_trace
        def list_by_alert_rule(
                self, 
                resource_group_name: str, 
                rule_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Incident]: ...


    class azure.mgmt.monitor.operations.AutoscaleSettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                autoscale_setting_name: str, 
                parameters: AutoscaleSettingResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutoscaleSettingResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                autoscale_setting_name: str, 
                parameters: AutoscaleSettingResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutoscaleSettingResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                autoscale_setting_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutoscaleSettingResource: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                autoscale_setting_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                autoscale_setting_name: str, 
                **kwargs: Any
            ) -> AutoscaleSettingResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AutoscaleSettingResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[AutoscaleSettingResource]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                autoscale_setting_name: str, 
                autoscale_setting_resource: AutoscaleSettingResourcePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutoscaleSettingResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                autoscale_setting_name: str, 
                autoscale_setting_resource: AutoscaleSettingResourcePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutoscaleSettingResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                autoscale_setting_name: str, 
                autoscale_setting_resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutoscaleSettingResource: ...


    class azure.mgmt.monitor.operations.BaselinesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_uri: str, 
                *, 
                aggregation: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                interval: Optional[timedelta] = ..., 
                metricnames: Optional[str] = ..., 
                metricnamespace: Optional[str] = ..., 
                result_type: Optional[Union[str, ResultType]] = ..., 
                sensitivities: Optional[str] = ..., 
                timespan: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[SingleMetricBaseline]: ...


    class azure.mgmt.monitor.operations.DataCollectionEndpointsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2021-10-01', params_added_on={'2021-10-01': ['api_version', 'subscription_id', 'resource_group_name', 'data_collection_endpoint_name', 'network_security_perimeter_configuration_name']}, api_versions_list=['2021-10-01'])
        def begin_reconcile_nsp(
                self, 
                resource_group_name: str, 
                data_collection_endpoint_name: str, 
                network_security_perimeter_configuration_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                data_collection_endpoint_name: str, 
                body: Optional[DataCollectionEndpointResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataCollectionEndpointResource: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                data_collection_endpoint_name: str, 
                body: Optional[DataCollectionEndpointResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataCollectionEndpointResource: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                data_collection_endpoint_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataCollectionEndpointResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-03-11', params_added_on={'2024-03-11': ['api_version', 'subscription_id', 'resource_group_name', 'data_collection_endpoint_name']}, api_versions_list=['2024-03-11'])
        def delete(
                self, 
                resource_group_name: str, 
                data_collection_endpoint_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-03-11', params_added_on={'2024-03-11': ['api_version', 'subscription_id', 'resource_group_name', 'data_collection_endpoint_name', 'accept']}, api_versions_list=['2024-03-11'])
        def get(
                self, 
                resource_group_name: str, 
                data_collection_endpoint_name: str, 
                **kwargs: Any
            ) -> DataCollectionEndpointResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2021-10-01', params_added_on={'2021-10-01': ['api_version', 'subscription_id', 'resource_group_name', 'data_collection_endpoint_name', 'network_security_perimeter_configuration_name', 'accept']}, api_versions_list=['2021-10-01'])
        def get_nsp(
                self, 
                resource_group_name: str, 
                data_collection_endpoint_name: str, 
                network_security_perimeter_configuration_name: str, 
                **kwargs: Any
            ) -> NetworkSecurityPerimeterConfiguration: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-03-11', params_added_on={'2024-03-11': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2024-03-11'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DataCollectionEndpointResource]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-03-11', params_added_on={'2024-03-11': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2024-03-11'])
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[DataCollectionEndpointResource]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2021-10-01', params_added_on={'2021-10-01': ['api_version', 'subscription_id', 'resource_group_name', 'data_collection_endpoint_name', 'accept']}, api_versions_list=['2021-10-01'])
        def list_nsp(
                self, 
                resource_group_name: str, 
                data_collection_endpoint_name: str, 
                **kwargs: Any
            ) -> ItemPaged[NetworkSecurityPerimeterConfiguration]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                data_collection_endpoint_name: str, 
                body: Optional[ResourceForUpdate] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataCollectionEndpointResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                data_collection_endpoint_name: str, 
                body: Optional[ResourceForUpdate] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataCollectionEndpointResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                data_collection_endpoint_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataCollectionEndpointResource: ...


    class azure.mgmt.monitor.operations.DataCollectionRuleAssociationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                resource_uri: str, 
                association_name: str, 
                body: Optional[DataCollectionRuleAssociationProxyOnlyResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataCollectionRuleAssociationProxyOnlyResource: ...

        @overload
        def create(
                self, 
                resource_uri: str, 
                association_name: str, 
                body: Optional[DataCollectionRuleAssociationProxyOnlyResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataCollectionRuleAssociationProxyOnlyResource: ...

        @overload
        def create(
                self, 
                resource_uri: str, 
                association_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataCollectionRuleAssociationProxyOnlyResource: ...

        @distributed_trace
        def delete(
                self, 
                resource_uri: str, 
                association_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_uri: str, 
                association_name: str, 
                **kwargs: Any
            ) -> DataCollectionRuleAssociationProxyOnlyResource: ...

        @distributed_trace
        def list_by_data_collection_endpoint(
                self, 
                resource_group_name: str, 
                data_collection_endpoint_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DataCollectionRuleAssociationProxyOnlyResource]: ...

        @distributed_trace
        def list_by_resource(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> ItemPaged[DataCollectionRuleAssociationProxyOnlyResource]: ...

        @distributed_trace
        def list_by_rule(
                self, 
                resource_group_name: str, 
                data_collection_rule_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DataCollectionRuleAssociationProxyOnlyResource]: ...


    class azure.mgmt.monitor.operations.DataCollectionRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                data_collection_rule_name: str, 
                body: Optional[DataCollectionRuleResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataCollectionRuleResource: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                data_collection_rule_name: str, 
                body: Optional[DataCollectionRuleResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataCollectionRuleResource: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                data_collection_rule_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataCollectionRuleResource: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                data_collection_rule_name: str, 
                *, 
                delete_associations: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                data_collection_rule_name: str, 
                **kwargs: Any
            ) -> DataCollectionRuleResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DataCollectionRuleResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[DataCollectionRuleResource]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                data_collection_rule_name: str, 
                body: Optional[ResourceForUpdate] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataCollectionRuleResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                data_collection_rule_name: str, 
                body: Optional[ResourceForUpdate] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataCollectionRuleResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                data_collection_rule_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataCollectionRuleResource: ...


    class azure.mgmt.monitor.operations.DiagnosticSettingsCategoryOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_uri: str, 
                name: str, 
                **kwargs: Any
            ) -> DiagnosticSettingsCategoryResource: ...

        @distributed_trace
        def list(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> ItemPaged[DiagnosticSettingsCategoryResource]: ...


    class azure.mgmt.monitor.operations.DiagnosticSettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_uri: str, 
                name: str, 
                parameters: DiagnosticSettingsResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DiagnosticSettingsResource: ...

        @overload
        def create_or_update(
                self, 
                resource_uri: str, 
                name: str, 
                parameters: DiagnosticSettingsResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DiagnosticSettingsResource: ...

        @overload
        def create_or_update(
                self, 
                resource_uri: str, 
                name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DiagnosticSettingsResource: ...

        @distributed_trace
        def delete(
                self, 
                resource_uri: str, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_uri: str, 
                name: str, 
                **kwargs: Any
            ) -> DiagnosticSettingsResource: ...

        @distributed_trace
        def list(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> ItemPaged[DiagnosticSettingsResource]: ...


    class azure.mgmt.monitor.operations.EventCategoriesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[LocalizableString]: ...


    class azure.mgmt.monitor.operations.LogProfilesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                log_profile_name: str, 
                parameters: LogProfileResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LogProfileResource: ...

        @overload
        def create_or_update(
                self, 
                log_profile_name: str, 
                parameters: LogProfileResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LogProfileResource: ...

        @overload
        def create_or_update(
                self, 
                log_profile_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LogProfileResource: ...

        @distributed_trace
        def delete(
                self, 
                log_profile_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                log_profile_name: str, 
                **kwargs: Any
            ) -> LogProfileResource: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[LogProfileResource]: ...

        @overload
        def update(
                self, 
                log_profile_name: str, 
                log_profiles_resource: LogProfileResourcePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LogProfileResource: ...

        @overload
        def update(
                self, 
                log_profile_name: str, 
                log_profiles_resource: LogProfileResourcePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LogProfileResource: ...

        @overload
        def update(
                self, 
                log_profile_name: str, 
                log_profiles_resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LogProfileResource: ...


    class azure.mgmt.monitor.operations.MetricAlertsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                rule_name: str, 
                parameters: MetricAlertResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MetricAlertResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                rule_name: str, 
                parameters: MetricAlertResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MetricAlertResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                rule_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MetricAlertResource: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                rule_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                rule_name: str, 
                **kwargs: Any
            ) -> MetricAlertResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[MetricAlertResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[MetricAlertResource]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                rule_name: str, 
                parameters: MetricAlertResourcePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MetricAlertResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                rule_name: str, 
                parameters: MetricAlertResourcePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MetricAlertResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                rule_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MetricAlertResource: ...


    class azure.mgmt.monitor.operations.MetricAlertsStatusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                rule_name: str, 
                **kwargs: Any
            ) -> MetricAlertStatusCollection: ...

        @distributed_trace
        def list_by_name(
                self, 
                resource_group_name: str, 
                rule_name: str, 
                status_name: str, 
                **kwargs: Any
            ) -> MetricAlertStatusCollection: ...


    class azure.mgmt.monitor.operations.MetricDefinitionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_uri: str, 
                *, 
                metricnamespace: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[MetricDefinition]: ...

        @distributed_trace
        def list_at_subscription_scope(
                self, 
                *, 
                metricnamespace: Optional[str] = ..., 
                region: str, 
                **kwargs: Any
            ) -> ItemPaged[SubscriptionScopeMetricDefinition]: ...


    class azure.mgmt.monitor.operations.MetricNamespacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_uri: str, 
                *, 
                start_time: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[MetricNamespace]: ...


    class azure.mgmt.monitor.operations.MetricsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_uri: str, 
                *, 
                aggregation: Optional[str] = ..., 
                auto_adjust_timegrain: Optional[bool] = ..., 
                filter: Optional[str] = ..., 
                interval: Optional[str] = ..., 
                metricnames: Optional[str] = ..., 
                metricnamespace: Optional[str] = ..., 
                orderby: Optional[str] = ..., 
                result_type: Optional[Union[str, ResultType]] = ..., 
                rollupby: Optional[str] = ..., 
                timespan: Optional[str] = ..., 
                top: Optional[int] = ..., 
                validate_dimensions: Optional[bool] = ..., 
                **kwargs: Any
            ) -> Response: ...

        @distributed_trace
        def list_at_subscription_scope(
                self, 
                *, 
                aggregation: Optional[str] = ..., 
                auto_adjust_timegrain: Optional[bool] = ..., 
                filter: Optional[str] = ..., 
                interval: Optional[str] = ..., 
                metricnames: Optional[str] = ..., 
                metricnamespace: Optional[str] = ..., 
                orderby: Optional[str] = ..., 
                region: str, 
                result_type: Optional[Union[str, MetricResultType]] = ..., 
                rollupby: Optional[str] = ..., 
                timespan: Optional[str] = ..., 
                top: Optional[int] = ..., 
                validate_dimensions: Optional[bool] = ..., 
                **kwargs: Any
            ) -> Response: ...

        @overload
        def list_at_subscription_scope_post(
                self, 
                body: Optional[SubscriptionScopeMetricsRequestBodyParameters] = None, 
                *, 
                aggregation: Optional[str] = ..., 
                auto_adjust_timegrain: Optional[bool] = ..., 
                content_type: str = "application/json", 
                filter: Optional[str] = ..., 
                interval: Optional[str] = ..., 
                metricnames: Optional[str] = ..., 
                metricnamespace: Optional[str] = ..., 
                orderby: Optional[str] = ..., 
                region: str, 
                result_type: Optional[Union[str, MetricResultType]] = ..., 
                rollupby: Optional[str] = ..., 
                timespan: Optional[str] = ..., 
                top: Optional[int] = ..., 
                validate_dimensions: Optional[bool] = ..., 
                **kwargs: Any
            ) -> Response: ...

        @overload
        def list_at_subscription_scope_post(
                self, 
                body: Optional[SubscriptionScopeMetricsRequestBodyParameters] = None, 
                *, 
                aggregation: Optional[str] = ..., 
                auto_adjust_timegrain: Optional[bool] = ..., 
                content_type: str = "application/json", 
                filter: Optional[str] = ..., 
                interval: Optional[str] = ..., 
                metricnames: Optional[str] = ..., 
                metricnamespace: Optional[str] = ..., 
                orderby: Optional[str] = ..., 
                region: str, 
                result_type: Optional[Union[str, MetricResultType]] = ..., 
                rollupby: Optional[str] = ..., 
                timespan: Optional[str] = ..., 
                top: Optional[int] = ..., 
                validate_dimensions: Optional[bool] = ..., 
                **kwargs: Any
            ) -> Response: ...

        @overload
        def list_at_subscription_scope_post(
                self, 
                body: Optional[IO[bytes]] = None, 
                *, 
                aggregation: Optional[str] = ..., 
                auto_adjust_timegrain: Optional[bool] = ..., 
                content_type: str = "application/json", 
                filter: Optional[str] = ..., 
                interval: Optional[str] = ..., 
                metricnames: Optional[str] = ..., 
                metricnamespace: Optional[str] = ..., 
                orderby: Optional[str] = ..., 
                region: str, 
                result_type: Optional[Union[str, MetricResultType]] = ..., 
                rollupby: Optional[str] = ..., 
                timespan: Optional[str] = ..., 
                top: Optional[int] = ..., 
                validate_dimensions: Optional[bool] = ..., 
                **kwargs: Any
            ) -> Response: ...


    class azure.mgmt.monitor.operations.PredictiveMetricOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                autoscale_setting_name: str, 
                *, 
                aggregation: str, 
                interval: timedelta, 
                metric_name: str, 
                metric_namespace: str, 
                timespan: str, 
                **kwargs: Any
            ) -> PredictiveResponse: ...


    class azure.mgmt.monitor.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                private_endpoint_connection_name: str, 
                parameters: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                private_endpoint_connection_name: str, 
                parameters: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                private_endpoint_connection_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list_by_private_link_scope(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PrivateEndpointConnection]: ...


    class azure.mgmt.monitor.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                group_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @distributed_trace
        def list_by_private_link_scope(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PrivateLinkResource]: ...


    class azure.mgmt.monitor.operations.PrivateLinkScopeOperationStatusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                async_operation_id: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> OperationStatus: ...


    class azure.mgmt.monitor.operations.PrivateLinkScopedResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                name: str, 
                parameters: ScopedResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ScopedResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                name: str, 
                parameters: ScopedResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ScopedResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ScopedResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                name: str, 
                **kwargs: Any
            ) -> ScopedResource: ...

        @distributed_trace
        def list_by_private_link_scope(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                *, 
                kind: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ScopedResource]: ...


    class azure.mgmt.monitor.operations.PrivateLinkScopesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                azure_monitor_private_link_scope_payload: AzureMonitorPrivateLinkScope, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureMonitorPrivateLinkScope: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                azure_monitor_private_link_scope_payload: AzureMonitorPrivateLinkScope, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureMonitorPrivateLinkScope: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                azure_monitor_private_link_scope_payload: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureMonitorPrivateLinkScope: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                **kwargs: Any
            ) -> AzureMonitorPrivateLinkScope: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[AzureMonitorPrivateLinkScope]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AzureMonitorPrivateLinkScope]: ...

        @overload
        def update_tags(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                private_link_scope_tags: TagsResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureMonitorPrivateLinkScope: ...

        @overload
        def update_tags(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                private_link_scope_tags: TagsResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureMonitorPrivateLinkScope: ...

        @overload
        def update_tags(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                private_link_scope_tags: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureMonitorPrivateLinkScope: ...


    class azure.mgmt.monitor.operations.ScheduledQueryRuleOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_reconcile_nsp(
                self, 
                resource_group_name: str, 
                rule_name: str, 
                network_security_perimeter_configuration_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get_nsp(
                self, 
                resource_group_name: str, 
                rule_name: str, 
                network_security_perimeter_configuration_name: str, 
                **kwargs: Any
            ) -> NetworkSecurityPerimeterConfiguration: ...

        @distributed_trace
        def list_nsp(
                self, 
                resource_group_name: str, 
                rule_name: str, 
                **kwargs: Any
            ) -> ItemPaged[NetworkSecurityPerimeterConfiguration]: ...


    class azure.mgmt.monitor.operations.ScheduledQueryRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                rule_name: str, 
                parameters: ScheduledQueryRuleResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ScheduledQueryRuleResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                rule_name: str, 
                parameters: ScheduledQueryRuleResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ScheduledQueryRuleResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                rule_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ScheduledQueryRuleResource: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                rule_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                rule_name: str, 
                **kwargs: Any
            ) -> ScheduledQueryRuleResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ScheduledQueryRuleResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[ScheduledQueryRuleResource]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                rule_name: str, 
                parameters: ScheduledQueryRuleResourcePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ScheduledQueryRuleResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                rule_name: str, 
                parameters: ScheduledQueryRuleResourcePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ScheduledQueryRuleResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                rule_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ScheduledQueryRuleResource: ...


    class azure.mgmt.monitor.operations.ServiceDiagnosticSettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_uri: str, 
                parameters: ServiceDiagnosticSettingsResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServiceDiagnosticSettingsResource: ...

        @overload
        def create_or_update(
                self, 
                resource_uri: str, 
                parameters: ServiceDiagnosticSettingsResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServiceDiagnosticSettingsResource: ...

        @overload
        def create_or_update(
                self, 
                resource_uri: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServiceDiagnosticSettingsResource: ...

        @distributed_trace
        def get(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> ServiceDiagnosticSettingsResource: ...

        @overload
        def update(
                self, 
                resource_uri: str, 
                service_diagnostic_settings_resource: ServiceDiagnosticSettingsResourcePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServiceDiagnosticSettingsResource: ...

        @overload
        def update(
                self, 
                resource_uri: str, 
                service_diagnostic_settings_resource: ServiceDiagnosticSettingsResourcePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServiceDiagnosticSettingsResource: ...

        @overload
        def update(
                self, 
                resource_uri: str, 
                service_diagnostic_settings_resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServiceDiagnosticSettingsResource: ...


    class azure.mgmt.monitor.operations.TenantActionGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                management_group_id: str, 
                tenant_action_group_name: str, 
                action_group: TenantActionGroupResource, 
                *, 
                content_type: str = "application/json", 
                x_ms_client_tenant_id: str, 
                **kwargs: Any
            ) -> TenantActionGroupResource: ...

        @overload
        def create_or_update(
                self, 
                management_group_id: str, 
                tenant_action_group_name: str, 
                action_group: TenantActionGroupResource, 
                *, 
                content_type: str = "application/json", 
                x_ms_client_tenant_id: str, 
                **kwargs: Any
            ) -> TenantActionGroupResource: ...

        @overload
        def create_or_update(
                self, 
                management_group_id: str, 
                tenant_action_group_name: str, 
                action_group: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                x_ms_client_tenant_id: str, 
                **kwargs: Any
            ) -> TenantActionGroupResource: ...

        @distributed_trace
        def delete(
                self, 
                management_group_id: str, 
                tenant_action_group_name: str, 
                *, 
                x_ms_client_tenant_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                management_group_id: str, 
                tenant_action_group_name: str, 
                *, 
                x_ms_client_tenant_id: str, 
                **kwargs: Any
            ) -> TenantActionGroupResource: ...

        @distributed_trace
        def list_by_management_group_id(
                self, 
                management_group_id: str, 
                *, 
                x_ms_client_tenant_id: str, 
                **kwargs: Any
            ) -> ItemPaged[TenantActionGroupResource]: ...

        @overload
        def update(
                self, 
                management_group_id: str, 
                tenant_action_group_name: str, 
                tenant_action_group_patch: TenantActionGroupPatchBody, 
                *, 
                content_type: str = "application/json", 
                x_ms_client_tenant_id: str, 
                **kwargs: Any
            ) -> TenantActionGroupResource: ...

        @overload
        def update(
                self, 
                management_group_id: str, 
                tenant_action_group_name: str, 
                tenant_action_group_patch: TenantActionGroupPatchBody, 
                *, 
                content_type: str = "application/json", 
                x_ms_client_tenant_id: str, 
                **kwargs: Any
            ) -> TenantActionGroupResource: ...

        @overload
        def update(
                self, 
                management_group_id: str, 
                tenant_action_group_name: str, 
                tenant_action_group_patch: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                x_ms_client_tenant_id: str, 
                **kwargs: Any
            ) -> TenantActionGroupResource: ...


    class azure.mgmt.monitor.operations.TenantActivityLogsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                *, 
                filter: Optional[str] = ..., 
                select: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[EventData]: ...


    class azure.mgmt.monitor.operations.VMInsightsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get_onboarding_status(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> VMInsightsOnboardingStatus: ...


namespace azure.mgmt.monitor.types

    class azure.mgmt.monitor.types.AccessModeSettings(TypedDict, total=False):
        key "ingestionAccessMode": Required[Union[str, AccessMode]]
        key "queryAccessMode": Required[Union[str, AccessMode]]
        exclusions: list[AccessModeSettingsExclusion]
        ingestionAccessMode: Union[str, AccessMode]
        queryAccessMode: Union[str, AccessMode]


    class azure.mgmt.monitor.types.AccessModeSettingsExclusion(TypedDict, total=False):
        key "ingestionAccessMode": Union[str, AccessMode]
        key "privateEndpointConnectionName": str
        key "queryAccessMode": Union[str, AccessMode]
        ingestionAccessMode: Union[str, AccessMode]
        privateEndpointConnectionName: str
        queryAccessMode: Union[str, AccessMode]


    class azure.mgmt.monitor.types.ActionGroup(TypedDict, total=False):
        key "actionGroupId": Required[str]
        actionGroupId: str
        actionProperties: dict[str, str]
        webhookProperties: dict[str, str]


    class azure.mgmt.monitor.types.ActionGroupPatch(TypedDict, total=False):
        key "enabled": bool
        enabled: bool


    class azure.mgmt.monitor.types.ActionGroupPatchBody(TypedDict, total=False):
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "properties": ForwardRef('ActionGroupPatch', module='types')
        identity: ManagedServiceIdentity
        properties: ActionGroupPatch
        tags: dict[str, str]


    class azure.mgmt.monitor.types.ActionGroupResource(TrackedResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('ActionGroupResourceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: ActionGroupResourceProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.monitor.types.ActionGroupResourceProperties(TypedDict, total=False):
        key "enabled": Required[bool]
        key "groupShortName": Required[str]
        armRoleReceivers: list[ArmRoleReceiver]
        automationRunbookReceivers: list[AutomationRunbookReceiver]
        azureAppPushReceivers: list[AzureAppPushReceiver]
        azureFunctionReceivers: list[AzureFunctionReceiver]
        emailReceivers: list[EmailReceiver]
        enabled: bool
        eventHubReceivers: list[EventHubReceiver]
        groupShortName: str
        incidentReceivers: list[IncidentReceiver]
        itsmReceivers: list[ItsmReceiver]
        logicAppReceivers: list[LogicAppReceiver]
        smsReceivers: list[SmsReceiver]
        voiceReceivers: list[VoiceReceiver]
        webhookReceivers: list[WebhookReceiver]


    class azure.mgmt.monitor.types.ActionList(TypedDict, total=False):
        actionGroups: list[ActionGroup]


    class azure.mgmt.monitor.types.Actions(TypedDict, total=False):
        actionGroups: list[str]
        actionProperties: dict[str, str]
        customProperties: dict[str, str]


    class azure.mgmt.monitor.types.ActivityLogAlertResource(ProxyResource):
        key "id": str
        key "location": str
        key "name": str
        key "properties": ForwardRef('AlertRuleProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: AlertRuleProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.monitor.types.AdxDestination(TypedDict, total=False):
        key "databaseName": str
        key "ingestionUri": str
        key "name": str
        key "resourceId": str
        databaseName: str
        ingestionUri: str
        name: str
        resourceId: str


    class azure.mgmt.monitor.types.AgentSetting(TypedDict, total=False):
        key "name": Union[str, KnownAgentSettingName]
        key "value": str
        name: Union[str, KnownAgentSettingName]
        value: str


    class azure.mgmt.monitor.types.AgentSettingsSpec(TypedDict, total=False):
        logs: list[AgentSetting]


    class azure.mgmt.monitor.types.AlertRuleAllOfCondition(TypedDict, total=False):
        key "allOf": Required[list[AlertRuleAnyOfOrLeafCondition]]
        allOf: list[AlertRuleAnyOfOrLeafCondition]


    class azure.mgmt.monitor.types.AlertRuleAnyOfOrLeafCondition(AlertRuleLeafCondition):
        key "equals": str
        key "field": str
        anyOf: list[AlertRuleLeafCondition]
        containsAny: list[str]
        equals: str
        field: str


    class azure.mgmt.monitor.types.AlertRuleLeafCondition(TypedDict, total=False):
        key "equals": str
        key "field": str
        containsAny: list[str]
        equals: str
        field: str


    class azure.mgmt.monitor.types.AlertRulePatchObject(TypedDict, total=False):
        key "properties": ForwardRef('AlertRulePatchProperties', module='types')
        properties: AlertRulePatchProperties
        tags: dict[str, str]


    class azure.mgmt.monitor.types.AlertRulePatchProperties(TypedDict, total=False):
        key "enabled": bool
        enabled: bool


    class azure.mgmt.monitor.types.AlertRuleProperties(TypedDict, total=False):
        key "actions": Required[ActionList]
        key "condition": Required[AlertRuleAllOfCondition]
        key "description": str
        key "enabled": bool
        key "tenantScope": str
        actions: ActionList
        condition: AlertRuleAllOfCondition
        description: str
        enabled: bool
        scopes: list[str]
        tenantScope: str


    class azure.mgmt.monitor.types.ApplicationInsights(TypedDict, total=False):
        key "name": Required[str]
        key "resourceId": Required[str]
        name: str
        resourceId: str


    class azure.mgmt.monitor.types.ArmRoleReceiver(TypedDict, total=False):
        key "name": Required[str]
        key "roleId": Required[str]
        key "useCommonAlertSchema": bool
        name: str
        roleId: str
        useCommonAlertSchema: bool


    class azure.mgmt.monitor.types.AutomationRunbookReceiver(TypedDict, total=False):
        key "automationAccountId": Required[str]
        key "isGlobalRunbook": Required[bool]
        key "managedIdentity": str
        key "name": str
        key "runbookName": Required[str]
        key "serviceUri": str
        key "useCommonAlertSchema": bool
        key "webhookResourceId": Required[str]
        automationAccountId: str
        isGlobalRunbook: bool
        managedIdentity: str
        name: str
        runbookName: str
        serviceUri: str
        useCommonAlertSchema: bool
        webhookResourceId: str


    class azure.mgmt.monitor.types.AutoscaleNotification(TypedDict, total=False):
        key "email": ForwardRef('EmailNotification', module='types')
        key "operation": Required[Union[str, OperationType]]
        email: EmailNotification
        operation: Union[str, OperationType]
        webhooks: list[WebhookNotification]


    class azure.mgmt.monitor.types.AutoscaleProfile(TypedDict, total=False):
        key "capacity": Required[ScaleCapacity]
        key "fixedDate": ForwardRef('TimeWindow', module='types')
        key "name": Required[str]
        key "recurrence": ForwardRef('Recurrence', module='types')
        key "rules": Required[list[ScaleRule]]
        capacity: ScaleCapacity
        fixedDate: TimeWindow
        name: str
        recurrence: Recurrence
        rules: list[ScaleRule]


    class azure.mgmt.monitor.types.AutoscaleSetting(TypedDict, total=False):
        key "enabled": bool
        key "name": str
        key "predictiveAutoscalePolicy": ForwardRef('PredictiveAutoscalePolicy', module='types')
        key "profiles": Required[list[AutoscaleProfile]]
        key "targetResourceLocation": str
        key "targetResourceUri": str
        enabled: bool
        name: str
        notifications: list[AutoscaleNotification]
        predictiveAutoscalePolicy: PredictiveAutoscalePolicy
        profiles: list[AutoscaleProfile]
        targetResourceLocation: str
        targetResourceUri: str


    class azure.mgmt.monitor.types.AutoscaleSettingResource(TrackedResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": Required[AutoscaleSetting]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: AutoscaleSetting
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.monitor.types.AutoscaleSettingResourcePatch(TypedDict, total=False):
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "properties": ForwardRef('AutoscaleSetting', module='types')
        identity: ManagedServiceIdentity
        properties: AutoscaleSetting
        tags: dict[str, str]


    class azure.mgmt.monitor.types.AzureAppPushReceiver(TypedDict, total=False):
        key "emailAddress": Required[str]
        key "name": Required[str]
        emailAddress: str
        name: str


    class azure.mgmt.monitor.types.AzureFunctionReceiver(TypedDict, total=False):
        key "functionAppResourceId": Required[str]
        key "functionName": Required[str]
        key "httpTriggerUrl": Required[str]
        key "managedIdentity": str
        key "name": Required[str]
        key "useCommonAlertSchema": bool
        functionAppResourceId: str
        functionName: str
        httpTriggerUrl: str
        managedIdentity: str
        name: str
        useCommonAlertSchema: bool


    class azure.mgmt.monitor.types.AzureMonitorMetricsDestination(TypedDict, total=False):
        key "name": str
        name: str


    class azure.mgmt.monitor.types.AzureMonitorPrivateLinkScope(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": Required[AzureMonitorPrivateLinkScopeProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: AzureMonitorPrivateLinkScopeProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.monitor.types.AzureMonitorPrivateLinkScopeProperties(TypedDict, total=False):
        key "accessModeSettings": Required[AccessModeSettings]
        key "provisioningState": Union[str, PrivateLinkScopeProvisioningState]
        accessModeSettings: AccessModeSettings
        privateEndpointConnections: list[PrivateEndpointConnection]
        provisioningState: Union[str, PrivateLinkScopeProvisioningState]


    class azure.mgmt.monitor.types.ColumnDefinition(TypedDict, total=False):
        key "name": str
        key "type": Union[str, KnownColumnDefinitionType]
        name: str
        type: Union[str, KnownColumnDefinitionType]


    class azure.mgmt.monitor.types.Condition(TypedDict, total=False):
        key "alertSensitivity": str
        key "criterionType": Union[str, CriterionType]
        key "failingPeriods": ForwardRef('ConditionFailingPeriods', module='types')
        key "ignoreDataBefore": str
        key "metricMeasureColumn": str
        key "metricName": str
        key "minRecurrenceCount": int
        key "operator": Union[str, ConditionOperator]
        key "query": str
        key "resourceIdColumn": str
        key "threshold": float
        key "timeAggregation": Union[str, TimeAggregation]
        alertSensitivity: str
        criterionType: Union[str, CriterionType]
        dimensions: list[Dimension]
        failingPeriods: ConditionFailingPeriods
        ignoreDataBefore: str
        metricMeasureColumn: str
        metricName: str
        minRecurrenceCount: int
        operator: Union[str, ConditionOperator]
        query: str
        resourceIdColumn: str
        threshold: float
        timeAggregation: Union[str, TimeAggregation]


    class azure.mgmt.monitor.types.ConditionFailingPeriods(TypedDict, total=False):
        key "minFailingPeriodsToAlert": int
        key "numberOfEvaluationPeriods": int
        minFailingPeriodsToAlert: int
        numberOfEvaluationPeriods: int


    class azure.mgmt.monitor.types.ConfigurationAccessEndpointSpec(TypedDict, total=False):
        key "endpoint": str
        endpoint: str


    class azure.mgmt.monitor.types.CriterionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DYNAMIC_THRESHOLD_CRITERION = "DynamicThresholdCriterion"
        STATIC_THRESHOLD_CRITERION = "StaticThresholdCriterion"


    class azure.mgmt.monitor.types.DataCollectionEndpoint(TypedDict, total=False):
        key "configurationAccess": ForwardRef('DataCollectionEndpointConfigurationAccess', module='types')
        key "description": str
        key "failoverConfiguration": ForwardRef('DataCollectionEndpointFailoverConfiguration', module='types')
        key "immutableId": str
        key "logsIngestion": ForwardRef('DataCollectionEndpointLogsIngestion', module='types')
        key "metadata": ForwardRef('DataCollectionEndpointMetadata', module='types')
        key "metricsIngestion": ForwardRef('DataCollectionEndpointMetricsIngestion', module='types')
        key "networkAcls": ForwardRef('DataCollectionEndpointNetworkAcls', module='types')
        key "provisioningState": Union[str, KnownDataCollectionEndpointProvisioningState]
        configurationAccess: DataCollectionEndpointConfigurationAccess
        description: str
        failoverConfiguration: DataCollectionEndpointFailoverConfiguration
        immutableId: str
        logsIngestion: DataCollectionEndpointLogsIngestion
        metadata: DataCollectionEndpointMetadata
        metricsIngestion: DataCollectionEndpointMetricsIngestion
        networkAcls: DataCollectionEndpointNetworkAcls
        privateLinkScopedResources: list[PrivateLinkScopedResource]
        provisioningState: Union[str, KnownDataCollectionEndpointProvisioningState]


    class azure.mgmt.monitor.types.DataCollectionEndpointConfigurationAccess(ConfigurationAccessEndpointSpec):
        key "endpoint": str
        endpoint: str


    class azure.mgmt.monitor.types.DataCollectionEndpointFailoverConfiguration(FailoverConfigurationSpec):
        key "activeLocation": str
        activeLocation: str
        locations: list[LocationSpec]


    class azure.mgmt.monitor.types.DataCollectionEndpointLogsIngestion(LogsIngestionEndpointSpec):
        key "endpoint": str
        endpoint: str


    class azure.mgmt.monitor.types.DataCollectionEndpointMetadata(Metadata):
        key "provisionedBy": str
        key "provisionedByImmutableId": str
        key "provisionedByResourceId": str
        provisionedBy: str
        provisionedByImmutableId: str
        provisionedByResourceId: str


    class azure.mgmt.monitor.types.DataCollectionEndpointMetricsIngestion(MetricsIngestionEndpointSpec):
        key "endpoint": str
        endpoint: str


    class azure.mgmt.monitor.types.DataCollectionEndpointNetworkAcls(NetworkRuleSet):
        key "publicNetworkAccess": Union[str, KnownPublicNetworkAccessOptions]
        publicNetworkAccess: Union[str, KnownPublicNetworkAccessOptions]


    class azure.mgmt.monitor.types.DataCollectionEndpointResource(TrackedResource):
        key "etag": str
        key "id": str
        key "identity": ForwardRef('DataCollectionEndpointResourceIdentity', module='types')
        key "kind": Union[str, KnownDataCollectionEndpointResourceKind]
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('DataCollectionEndpointResourceProperties', module='types')
        key "sku": ForwardRef('DataCollectionEndpointResourceSku', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        identity: DataCollectionEndpointResourceIdentity
        kind: Union[str, KnownDataCollectionEndpointResourceKind]
        location: str
        name: str
        properties: DataCollectionEndpointResourceProperties
        sku: DataCollectionEndpointResourceSku
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.monitor.types.DataCollectionEndpointResourceIdentity(ManagedServiceIdentity):
        key "principalId": str
        key "tenantId": str
        key "type": Required[Union[str, ManagedServiceIdentityType]]
        principalId: str
        tenantId: str
        type: Union[str, ManagedServiceIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentity]


    class azure.mgmt.monitor.types.DataCollectionEndpointResourceProperties(DataCollectionEndpoint):
        key "configurationAccess": ForwardRef('DataCollectionEndpointConfigurationAccess', module='types')
        key "description": str
        key "failoverConfiguration": ForwardRef('DataCollectionEndpointFailoverConfiguration', module='types')
        key "immutableId": str
        key "logsIngestion": ForwardRef('DataCollectionEndpointLogsIngestion', module='types')
        key "metadata": ForwardRef('DataCollectionEndpointMetadata', module='types')
        key "metricsIngestion": ForwardRef('DataCollectionEndpointMetricsIngestion', module='types')
        key "networkAcls": ForwardRef('DataCollectionEndpointNetworkAcls', module='types')
        key "provisioningState": Union[str, KnownDataCollectionEndpointProvisioningState]
        configurationAccess: DataCollectionEndpointConfigurationAccess
        description: str
        failoverConfiguration: DataCollectionEndpointFailoverConfiguration
        immutableId: str
        logsIngestion: DataCollectionEndpointLogsIngestion
        metadata: DataCollectionEndpointMetadata
        metricsIngestion: DataCollectionEndpointMetricsIngestion
        networkAcls: DataCollectionEndpointNetworkAcls
        privateLinkScopedResources: list[PrivateLinkScopedResource]
        provisioningState: Union[str, KnownDataCollectionEndpointProvisioningState]


    class azure.mgmt.monitor.types.DataCollectionEndpointResourceSku(Sku):
        key "capacity": int
        key "family": str
        key "name": Required[str]
        key "size": str
        key "tier": Union[str, SkuTier]
        capacity: int
        family: str
        name: str
        size: str
        tier: Union[str, SkuTier]


    class azure.mgmt.monitor.types.DataCollectionRule(TypedDict, total=False):
        key "agentSettings": ForwardRef('DataCollectionRuleAgentSettings', module='types')
        key "dataCollectionEndpointId": str
        key "dataSources": ForwardRef('DataCollectionRuleDataSources', module='types')
        key "description": str
        key "destinations": ForwardRef('DataCollectionRuleDestinations', module='types')
        key "directDataSources": ForwardRef('DataCollectionRuleDirectDataSources', module='types')
        key "endpoints": ForwardRef('DataCollectionRuleEndpoints', module='types')
        key "immutableId": str
        key "ingestionQuotas": ForwardRef('DataCollectionRuleIngestionQuotas', module='types')
        key "metadata": ForwardRef('DataCollectionRuleMetadata', module='types')
        key "provisioningState": Union[str, KnownDataCollectionRuleProvisioningState]
        key "references": ForwardRef('DataCollectionRuleReferences', module='types')
        agentSettings: DataCollectionRuleAgentSettings
        dataCollectionEndpointId: str
        dataFlows: list[DataFlow]
        dataSources: DataCollectionRuleDataSources
        description: str
        destinations: DataCollectionRuleDestinations
        directDataSources: DataCollectionRuleDirectDataSources
        endpoints: DataCollectionRuleEndpoints
        immutableId: str
        ingestionQuotas: DataCollectionRuleIngestionQuotas
        metadata: DataCollectionRuleMetadata
        provisioningState: Union[str, KnownDataCollectionRuleProvisioningState]
        references: DataCollectionRuleReferences
        streamDeclarations: dict[str, StreamDeclaration]


    class azure.mgmt.monitor.types.DataCollectionRuleAgentSettings(AgentSettingsSpec):
        logs: list[AgentSetting]


    class azure.mgmt.monitor.types.DataCollectionRuleAssociation(TypedDict, total=False):
        key "dataCollectionEndpointId": str
        key "dataCollectionRuleId": str
        key "description": str
        key "metadata": ForwardRef('DataCollectionRuleAssociationMetadata', module='types')
        key "provisioningState": Union[str, KnownDataCollectionRuleAssociationProvisioningState]
        dataCollectionEndpointId: str
        dataCollectionRuleId: str
        description: str
        metadata: DataCollectionRuleAssociationMetadata
        provisioningState: Union[str, KnownDataCollectionRuleAssociationProvisioningState]


    class azure.mgmt.monitor.types.DataCollectionRuleAssociationMetadata(Metadata):
        key "provisionedBy": str
        key "provisionedByImmutableId": str
        key "provisionedByResourceId": str
        provisionedBy: str
        provisionedByImmutableId: str
        provisionedByResourceId: str


    class azure.mgmt.monitor.types.DataCollectionRuleAssociationProxyOnlyResource(ExtensionResource):
        key "etag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('DataCollectionRuleAssociationProxyOnlyResourceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        name: str
        properties: DataCollectionRuleAssociationProxyOnlyResourceProperties
        systemData: SystemData
        type: str


    class azure.mgmt.monitor.types.DataCollectionRuleAssociationProxyOnlyResourceProperties(DataCollectionRuleAssociation):
        key "dataCollectionEndpointId": str
        key "dataCollectionRuleId": str
        key "description": str
        key "metadata": ForwardRef('DataCollectionRuleAssociationMetadata', module='types')
        key "provisioningState": Union[str, KnownDataCollectionRuleAssociationProvisioningState]
        dataCollectionEndpointId: str
        dataCollectionRuleId: str
        description: str
        metadata: DataCollectionRuleAssociationMetadata
        provisioningState: Union[str, KnownDataCollectionRuleAssociationProvisioningState]


    class azure.mgmt.monitor.types.DataCollectionRuleDataSources(DataSourcesSpec):
        key "dataImports": ForwardRef('DataSourcesSpecDataImports', module='types')
        dataImports: DataSourcesSpecDataImports
        etwProviders: list[EtwProviderDataSource]
        extensions: list[ExtensionDataSource]
        iisLogs: list[IisLogsDataSource]
        logFiles: list[LogFilesDataSource]
        otelLogs: list[OtelLogsDataSource]
        otelMetrics: list[OtelMetricsDataSource]
        otelTraces: list[OtelTracesDataSource]
        performanceCounters: list[PerfCounterDataSource]
        performanceCountersOTel: list[PerformanceCountersOTelDataSource]
        platformTelemetry: list[PlatformTelemetryDataSource]
        prometheusForwarder: list[PrometheusForwarderDataSource]
        syslog: list[SyslogDataSource]
        windowsEventLogs: list[WindowsEventLogDataSource]
        windowsFirewallLogs: list[WindowsFirewallLogsDataSource]


    class azure.mgmt.monitor.types.DataCollectionRuleDestinations(DestinationsSpec):
        key "azureMonitorMetrics": ForwardRef('DestinationsSpecAzureMonitorMetrics', module='types')
        azureDataExplorer: list[AdxDestination]
        azureMonitorMetrics: DestinationsSpecAzureMonitorMetrics
        eventHubs: list[EventHubDestination]
        eventHubsDirect: list[EventHubDirectDestination]
        logAnalytics: list[LogAnalyticsDestination]
        microsoftFabric: list[MicrosoftFabricDestination]
        monitoringAccounts: list[MonitoringAccountDestination]
        storageAccounts: list[StorageBlobDestination]
        storageBlobsDirect: list[StorageBlobDestination]
        storageTablesDirect: list[StorageTableDestination]


    class azure.mgmt.monitor.types.DataCollectionRuleDirectDataSources(DirectDataSourcesSpec):
        otelLogs: list[OtelLogsDirectDataSource]
        otelMetrics: list[OtelMetricsDirectDataSource]
        otelTraces: list[OtelTracesDirectDataSource]


    class azure.mgmt.monitor.types.DataCollectionRuleEndpoints(EndpointsSpec):
        key "logsIngestion": str
        key "metricsIngestion": str
        logsIngestion: str
        metricsIngestion: str


    class azure.mgmt.monitor.types.DataCollectionRuleIngestionQuotas(IngestionQuotas):
        key "logs": ForwardRef('IngestionQuotasLogs', module='types')
        logs: IngestionQuotasLogs


    class azure.mgmt.monitor.types.DataCollectionRuleMetadata(Metadata):
        key "provisionedBy": str
        key "provisionedByImmutableId": str
        key "provisionedByResourceId": str
        provisionedBy: str
        provisionedByImmutableId: str
        provisionedByResourceId: str


    class azure.mgmt.monitor.types.DataCollectionRuleReferences(ReferencesSpec):
        key "enrichmentData": ForwardRef('ReferencesSpecEnrichmentData', module='types')
        applicationInsights: list[ApplicationInsights]
        enrichmentData: ReferencesSpecEnrichmentData


    class azure.mgmt.monitor.types.DataCollectionRuleResource(TrackedResource):
        key "etag": str
        key "id": str
        key "identity": ForwardRef('DataCollectionRuleResourceIdentity', module='types')
        key "kind": Union[str, KnownDataCollectionRuleResourceKind]
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('DataCollectionRuleResourceProperties', module='types')
        key "sku": ForwardRef('DataCollectionRuleResourceSku', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        identity: DataCollectionRuleResourceIdentity
        kind: Union[str, KnownDataCollectionRuleResourceKind]
        location: str
        name: str
        properties: DataCollectionRuleResourceProperties
        sku: DataCollectionRuleResourceSku
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.monitor.types.DataCollectionRuleResourceIdentity(ManagedServiceIdentity):
        key "principalId": str
        key "tenantId": str
        key "type": Required[Union[str, ManagedServiceIdentityType]]
        principalId: str
        tenantId: str
        type: Union[str, ManagedServiceIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentity]


    class azure.mgmt.monitor.types.DataCollectionRuleResourceProperties(DataCollectionRule):
        key "agentSettings": ForwardRef('DataCollectionRuleAgentSettings', module='types')
        key "dataCollectionEndpointId": str
        key "dataSources": ForwardRef('DataCollectionRuleDataSources', module='types')
        key "description": str
        key "destinations": ForwardRef('DataCollectionRuleDestinations', module='types')
        key "directDataSources": ForwardRef('DataCollectionRuleDirectDataSources', module='types')
        key "endpoints": ForwardRef('DataCollectionRuleEndpoints', module='types')
        key "immutableId": str
        key "ingestionQuotas": ForwardRef('DataCollectionRuleIngestionQuotas', module='types')
        key "metadata": ForwardRef('DataCollectionRuleMetadata', module='types')
        key "provisioningState": Union[str, KnownDataCollectionRuleProvisioningState]
        key "references": ForwardRef('DataCollectionRuleReferences', module='types')
        agentSettings: DataCollectionRuleAgentSettings
        dataCollectionEndpointId: str
        dataFlows: list[DataFlow]
        dataSources: DataCollectionRuleDataSources
        description: str
        destinations: DataCollectionRuleDestinations
        directDataSources: DataCollectionRuleDirectDataSources
        endpoints: DataCollectionRuleEndpoints
        immutableId: str
        ingestionQuotas: DataCollectionRuleIngestionQuotas
        metadata: DataCollectionRuleMetadata
        provisioningState: Union[str, KnownDataCollectionRuleProvisioningState]
        references: DataCollectionRuleReferences
        streamDeclarations: dict[str, StreamDeclaration]


    class azure.mgmt.monitor.types.DataCollectionRuleResourceSku(Sku):
        key "capacity": int
        key "family": str
        key "name": Required[str]
        key "size": str
        key "tier": Union[str, SkuTier]
        capacity: int
        family: str
        name: str
        size: str
        tier: Union[str, SkuTier]


    class azure.mgmt.monitor.types.DataFlow(TypedDict, total=False):
        key "builtInTransform": str
        key "captureOverflow": bool
        key "outputStream": str
        key "transformKql": str
        builtInTransform: str
        captureOverflow: bool
        destinations: list[str]
        outputStream: str
        streams: list[Union[str, KnownDataFlowStreams]]
        transformKql: str


    class azure.mgmt.monitor.types.DataImportSources(TypedDict, total=False):
        key "eventHub": ForwardRef('DataImportSourcesEventHub', module='types')
        eventHub: DataImportSourcesEventHub


    class azure.mgmt.monitor.types.DataImportSourcesEventHub(EventHubDataSource):
        key "consumerGroup": str
        key "name": str
        key "stream": str
        consumerGroup: str
        name: str
        stream: str


    class azure.mgmt.monitor.types.DataSourcesSpec(TypedDict, total=False):
        key "dataImports": ForwardRef('DataSourcesSpecDataImports', module='types')
        dataImports: DataSourcesSpecDataImports
        etwProviders: list[EtwProviderDataSource]
        extensions: list[ExtensionDataSource]
        iisLogs: list[IisLogsDataSource]
        logFiles: list[LogFilesDataSource]
        otelLogs: list[OtelLogsDataSource]
        otelMetrics: list[OtelMetricsDataSource]
        otelTraces: list[OtelTracesDataSource]
        performanceCounters: list[PerfCounterDataSource]
        performanceCountersOTel: list[PerformanceCountersOTelDataSource]
        platformTelemetry: list[PlatformTelemetryDataSource]
        prometheusForwarder: list[PrometheusForwarderDataSource]
        syslog: list[SyslogDataSource]
        windowsEventLogs: list[WindowsEventLogDataSource]
        windowsFirewallLogs: list[WindowsFirewallLogsDataSource]


    class azure.mgmt.monitor.types.DataSourcesSpecDataImports(DataImportSources):
        key "eventHub": ForwardRef('DataImportSourcesEventHub', module='types')
        eventHub: DataImportSourcesEventHub


    class azure.mgmt.monitor.types.DestinationsSpec(TypedDict, total=False):
        key "azureMonitorMetrics": ForwardRef('DestinationsSpecAzureMonitorMetrics', module='types')
        azureDataExplorer: list[AdxDestination]
        azureMonitorMetrics: DestinationsSpecAzureMonitorMetrics
        eventHubs: list[EventHubDestination]
        eventHubsDirect: list[EventHubDirectDestination]
        logAnalytics: list[LogAnalyticsDestination]
        microsoftFabric: list[MicrosoftFabricDestination]
        monitoringAccounts: list[MonitoringAccountDestination]
        storageAccounts: list[StorageBlobDestination]
        storageBlobsDirect: list[StorageBlobDestination]
        storageTablesDirect: list[StorageTableDestination]


    class azure.mgmt.monitor.types.DestinationsSpecAzureMonitorMetrics(AzureMonitorMetricsDestination):
        key "name": str
        name: str


    class azure.mgmt.monitor.types.DiagnosticSettings(TypedDict, total=False):
        key "eventHubAuthorizationRuleId": str
        key "eventHubName": str
        key "logAnalyticsDestinationType": str
        key "marketplacePartnerId": str
        key "serviceBusRuleId": str
        key "storageAccountId": str
        key "workspaceId": str
        eventHubAuthorizationRuleId: str
        eventHubName: str
        logAnalyticsDestinationType: str
        logs: list[DiagnosticsLogSettings]
        marketplacePartnerId: str
        metrics: list[DiagnosticsMetricSettings]
        serviceBusRuleId: str
        storageAccountId: str
        workspaceId: str


    class azure.mgmt.monitor.types.DiagnosticSettingsResource(ExtensionResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('DiagnosticSettings', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: DiagnosticSettings
        systemData: SystemData
        type: str


    class azure.mgmt.monitor.types.DiagnosticsLogSettings(TypedDict, total=False):
        key "category": str
        key "categoryGroup": str
        key "enabled": Required[bool]
        key "retentionPolicy": ForwardRef('RetentionPolicy', module='types')
        category: str
        categoryGroup: str
        enabled: bool
        retentionPolicy: RetentionPolicy


    class azure.mgmt.monitor.types.DiagnosticsMetricSettings(TypedDict, total=False):
        key "category": str
        key "enabled": Required[bool]
        key "retentionPolicy": ForwardRef('RetentionPolicy', module='types')
        key "timeGrain": str
        category: str
        enabled: bool
        retentionPolicy: RetentionPolicy
        timeGrain: str


    class azure.mgmt.monitor.types.Dimension(TypedDict, total=False):
        key "name": Required[str]
        key "operator": Required[Union[str, DimensionOperator]]
        key "values": Required[list[str]]
        name: str
        operator: Union[str, DimensionOperator]
        values: list[str]


    class azure.mgmt.monitor.types.DirectDataSourcesSpec(TypedDict, total=False):
        otelLogs: list[OtelLogsDirectDataSource]
        otelMetrics: list[OtelMetricsDirectDataSource]
        otelTraces: list[OtelTracesDirectDataSource]


    class azure.mgmt.monitor.types.DynamicMetricCriteria(TypedDict, total=False):
        key "alertSensitivity": Required[Union[str, DynamicThresholdSensitivity]]
        key "criterionType": Required[Literal[CriterionType.DYNAMIC_THRESHOLD_CRITERION]]
        key "failingPeriods": Required[DynamicThresholdFailingPeriods]
        key "ignoreDataBefore": str
        key "metricName": Required[str]
        key "metricNamespace": str
        key "name": Required[str]
        key "operator": Required[Union[str, DynamicThresholdOperator]]
        key "skipMetricValidation": bool
        key "timeAggregation": Required[Union[str, AggregationTypeEnum]]
        alertSensitivity: Union[str, DynamicThresholdSensitivity]
        criterionType: Literal[CriterionType.DYNAMIC_THRESHOLD_CRITERION]
        dimensions: list[MetricDimension]
        failingPeriods: DynamicThresholdFailingPeriods
        ignoreDataBefore: str
        metricName: str
        metricNamespace: str
        name: str
        operator: Union[str, DynamicThresholdOperator]
        skipMetricValidation: bool
        timeAggregation: Union[str, AggregationTypeEnum]


    class azure.mgmt.monitor.types.DynamicPromQLCriteria(TypedDict, total=False):
        key "alertSensitivity": Required[Union[str, DynamicThresholdSensitivity]]
        key "criterionType": Required[Literal[CriterionType.DYNAMIC_THRESHOLD_CRITERION]]
        key "ignoreDataBefore": str
        key "name": Required[str]
        key "operator": Required[Union[str, DynamicThresholdOperator]]
        key "query": Required[str]
        alertSensitivity: Union[str, DynamicThresholdSensitivity]
        criterionType: Literal[CriterionType.DYNAMIC_THRESHOLD_CRITERION]
        ignoreDataBefore: str
        name: str
        operator: Union[str, DynamicThresholdOperator]
        query: str


    class azure.mgmt.monitor.types.DynamicThresholdFailingPeriods(TypedDict, total=False):
        key "minFailingPeriodsToAlert": Required[float]
        key "numberOfEvaluationPeriods": Required[float]
        minFailingPeriodsToAlert: float
        numberOfEvaluationPeriods: float


    class azure.mgmt.monitor.types.EmailNotification(TypedDict, total=False):
        key "sendToSubscriptionAdministrator": bool
        key "sendToSubscriptionCoAdministrators": bool
        customEmails: list[str]
        sendToSubscriptionAdministrator: bool
        sendToSubscriptionCoAdministrators: bool


    class azure.mgmt.monitor.types.EmailReceiver(TypedDict, total=False):
        key "emailAddress": Required[str]
        key "name": Required[str]
        key "status": Union[str, ReceiverStatus]
        key "useCommonAlertSchema": bool
        emailAddress: str
        name: str
        status: Union[str, ReceiverStatus]
        useCommonAlertSchema: bool


    class azure.mgmt.monitor.types.EnableRequest(TypedDict, total=False):
        key "receiverName": Required[str]
        receiverName: str


    class azure.mgmt.monitor.types.EndpointsSpec(TypedDict, total=False):
        key "logsIngestion": str
        key "metricsIngestion": str
        logsIngestion: str
        metricsIngestion: str


    class azure.mgmt.monitor.types.EnrichmentData(TypedDict, total=False):
        storageBlobs: list[StorageBlob]


    class azure.mgmt.monitor.types.EtwProviderDataSource(TypedDict, total=False):
        key "keyword": str
        key "logLevel": Union[str, KnownEtwProviderDataSourceLogLevel]
        key "name": str
        key "provider": Required[str]
        key "providerType": Required[Union[str, KnownEtwProviderType]]
        key "streams": Required[list[str]]
        eventIds: list[str]
        keyword: str
        logLevel: Union[str, KnownEtwProviderDataSourceLogLevel]
        name: str
        provider: str
        providerType: Union[str, KnownEtwProviderType]
        streams: list[str]


    class azure.mgmt.monitor.types.EventHubDataSource(TypedDict, total=False):
        key "consumerGroup": str
        key "name": str
        key "stream": str
        consumerGroup: str
        name: str
        stream: str


    class azure.mgmt.monitor.types.EventHubDestination(TypedDict, total=False):
        key "eventHubResourceId": str
        key "name": str
        eventHubResourceId: str
        name: str


    class azure.mgmt.monitor.types.EventHubDirectDestination(TypedDict, total=False):
        key "eventHubResourceId": str
        key "name": str
        eventHubResourceId: str
        name: str


    class azure.mgmt.monitor.types.EventHubReceiver(TypedDict, total=False):
        key "eventHubName": Required[str]
        key "eventHubNameSpace": Required[str]
        key "managedIdentity": str
        key "name": Required[str]
        key "subscriptionId": Required[str]
        key "tenantId": str
        key "useCommonAlertSchema": bool
        eventHubName: str
        eventHubNameSpace: str
        managedIdentity: str
        name: str
        subscriptionId: str
        tenantId: str
        useCommonAlertSchema: bool


    class azure.mgmt.monitor.types.ExtensionDataSource(TypedDict, total=False):
        key "extensionName": Required[str]
        key "extensionSettings": Any
        key "name": str
        extensionName: str
        extensionSettings: Any
        inputDataSources: list[str]
        name: str
        streams: list[Union[str, KnownExtensionDataSourceStreams]]


    class azure.mgmt.monitor.types.ExtensionResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.monitor.types.FailoverConfigurationSpec(TypedDict, total=False):
        key "activeLocation": str
        activeLocation: str
        locations: list[LocationSpec]


    class azure.mgmt.monitor.types.Identity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Required[Union[str, IdentityType]]
        principalId: str
        tenantId: str
        type: Union[str, IdentityType]
        userAssignedIdentities: dict[str, UserIdentityProperties]


    class azure.mgmt.monitor.types.IisLogsDataSource(TypedDict, total=False):
        key "name": str
        key "streams": Required[list[str]]
        key "transformKql": str
        logDirectories: list[str]
        name: str
        streams: list[str]
        transformKql: str


    class azure.mgmt.monitor.types.IncidentReceiver(TypedDict, total=False):
        key "connection": Required[IncidentServiceConnection]
        key "incidentManagementService": Required[Union[str, IncidentManagementService]]
        key "mappings": Required[dict[str, str]]
        key "name": Required[str]
        connection: IncidentServiceConnection
        incidentManagementService: Union[str, IncidentManagementService]
        mappings: dict[str, str]
        name: str


    class azure.mgmt.monitor.types.IncidentServiceConnection(TypedDict, total=False):
        key "id": Required[str]
        key "name": Required[str]
        id: str
        name: str


    class azure.mgmt.monitor.types.IngestionQuotas(TypedDict, total=False):
        key "logs": ForwardRef('IngestionQuotasLogs', module='types')
        logs: IngestionQuotasLogs


    class azure.mgmt.monitor.types.IngestionQuotasLogs(LogsQuotaSpec):
        key "maxRequestsPerMinute": str
        key "maxSizePerMinuteInGB": str
        maxRequestsPerMinute: str
        maxSizePerMinuteInGB: str


    class azure.mgmt.monitor.types.ItsmReceiver(TypedDict, total=False):
        key "connectionId": Required[str]
        key "name": Required[str]
        key "region": Required[str]
        key "ticketConfiguration": Required[str]
        key "workspaceId": Required[str]
        connectionId: str
        name: str
        region: str
        ticketConfiguration: str
        workspaceId: str


    class azure.mgmt.monitor.types.LocationSpec(TypedDict, total=False):
        key "location": str
        key "provisioningStatus": Union[str, KnownLocationSpecProvisioningStatus]
        location: str
        provisioningStatus: Union[str, KnownLocationSpecProvisioningStatus]


    class azure.mgmt.monitor.types.LogAnalyticsDestination(TypedDict, total=False):
        key "name": str
        key "workspaceId": str
        key "workspaceResourceId": str
        name: str
        workspaceId: str
        workspaceResourceId: str


    class azure.mgmt.monitor.types.LogFileSettings(TypedDict, total=False):
        key "text": ForwardRef('LogFileSettingsText', module='types')
        text: LogFileSettingsText


    class azure.mgmt.monitor.types.LogFileSettingsText(LogFileTextSettings):
        key "recordStartTimestampFormat": Required[Union[str, KnownLogFileTextSettingsRecordStartTimestampFormat]]
        recordStartTimestampFormat: Union[str, KnownLogFileTextSettingsRecordStartTimestampFormat]


    class azure.mgmt.monitor.types.LogFileTextSettings(TypedDict, total=False):
        key "recordStartTimestampFormat": Required[Union[str, KnownLogFileTextSettingsRecordStartTimestampFormat]]
        recordStartTimestampFormat: Union[str, KnownLogFileTextSettingsRecordStartTimestampFormat]


    class azure.mgmt.monitor.types.LogFilesDataSource(TypedDict, total=False):
        key "filePatterns": Required[list[str]]
        key "format": Required[Union[str, KnownLogFilesDataSourceFormat]]
        key "name": str
        key "settings": ForwardRef('LogFilesDataSourceSettings', module='types')
        key "streams": Required[list[str]]
        key "transformKql": str
        filePatterns: list[str]
        format: Union[str, KnownLogFilesDataSourceFormat]
        name: str
        settings: LogFilesDataSourceSettings
        streams: list[str]
        transformKql: str


    class azure.mgmt.monitor.types.LogFilesDataSourceSettings(LogFileSettings):
        key "text": ForwardRef('LogFileSettingsText', module='types')
        text: LogFileSettingsText


    class azure.mgmt.monitor.types.LogProfileProperties(TypedDict, total=False):
        key "categories": Required[list[str]]
        key "locations": Required[list[str]]
        key "retentionPolicy": Required[RetentionPolicy]
        key "serviceBusRuleId": str
        key "storageAccountId": str
        categories: list[str]
        locations: list[str]
        retentionPolicy: RetentionPolicy
        serviceBusRuleId: str
        storageAccountId: str


    class azure.mgmt.monitor.types.LogProfileResource(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": Required[LogProfileProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: LogProfileProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.monitor.types.LogProfileResourcePatch(TypedDict, total=False):
        key "properties": ForwardRef('LogProfileProperties', module='types')
        properties: LogProfileProperties
        tags: dict[str, str]


    class azure.mgmt.monitor.types.LogicAppReceiver(TypedDict, total=False):
        key "callbackUrl": Required[str]
        key "managedIdentity": str
        key "name": Required[str]
        key "resourceId": Required[str]
        key "useCommonAlertSchema": bool
        callbackUrl: str
        managedIdentity: str
        name: str
        resourceId: str
        useCommonAlertSchema: bool


    class azure.mgmt.monitor.types.LogsIngestionEndpointSpec(TypedDict, total=False):
        key "endpoint": str
        endpoint: str


    class azure.mgmt.monitor.types.LogsQuotaSpec(TypedDict, total=False):
        key "maxRequestsPerMinute": str
        key "maxSizePerMinuteInGB": str
        maxRequestsPerMinute: str
        maxSizePerMinuteInGB: str


    class azure.mgmt.monitor.types.ManagedServiceIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Required[Union[str, ManagedServiceIdentityType]]
        principalId: str
        tenantId: str
        type: Union[str, ManagedServiceIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentity]


    class azure.mgmt.monitor.types.Metadata(TypedDict, total=False):
        key "provisionedBy": str
        key "provisionedByImmutableId": str
        key "provisionedByResourceId": str
        provisionedBy: str
        provisionedByImmutableId: str
        provisionedByResourceId: str


    class azure.mgmt.monitor.types.MetricAlertAction(TypedDict, total=False):
        key "actionGroupId": str
        actionGroupId: str
        webHookProperties: dict[str, str]


    class azure.mgmt.monitor.types.MetricAlertMultipleResourceMultipleMetricCriteria(TypedDict):
        key "odata.type": Required[Literal[Odatatype.MICROSOFT_AZURE_MONITOR_MULTIPLE_RESOURCE_MULTIPLE_METRIC_CRITERIA]]
        allOf: list[MultiMetricCriteria]
        odata.type: Literal[Odatatype.MICROSOFT_AZURE_MONITOR_MULTIPLE_RESOURCE_MULTIPLE_METRIC_CRITERIA]


    class azure.mgmt.monitor.types.MetricAlertProperties(TypedDict, total=False):
        key "autoMitigate": bool
        key "criteria": Required[MetricAlertCriteria]
        key "description": str
        key "enabled": Required[bool]
        key "evaluationFrequency": Required[str]
        key "isMigrated": bool
        key "lastUpdatedTime": str
        key "resolveConfiguration": ForwardRef('ResolveConfiguration', module='types')
        key "scopes": Required[list[str]]
        key "severity": Required[int]
        key "targetResourceRegion": str
        key "targetResourceType": str
        key "windowSize": str
        actionProperties: dict[str, str]
        actions: list[MetricAlertAction]
        autoMitigate: bool
        criteria: MetricAlertCriteria
        customProperties: dict[str, str]
        description: str
        enabled: bool
        evaluationFrequency: str
        isMigrated: bool
        lastUpdatedTime: str
        resolveConfiguration: ResolveConfiguration
        scopes: list[str]
        severity: int
        targetResourceRegion: str
        targetResourceType: str
        windowSize: str


    class azure.mgmt.monitor.types.MetricAlertPropertiesPatch(TypedDict, total=False):
        key "autoMitigate": bool
        key "criteria": ForwardRef('MetricAlertCriteria', module='types')
        key "description": str
        key "enabled": bool
        key "evaluationFrequency": str
        key "isMigrated": bool
        key "lastUpdatedTime": str
        key "resolveConfiguration": ForwardRef('ResolveConfiguration', module='types')
        key "severity": int
        key "targetResourceRegion": str
        key "targetResourceType": str
        key "windowSize": str
        actionProperties: dict[str, str]
        actions: list[MetricAlertAction]
        autoMitigate: bool
        criteria: MetricAlertCriteria
        customProperties: dict[str, str]
        description: str
        enabled: bool
        evaluationFrequency: str
        isMigrated: bool
        lastUpdatedTime: str
        resolveConfiguration: ResolveConfiguration
        scopes: list[str]
        severity: int
        targetResourceRegion: str
        targetResourceType: str
        windowSize: str


    class azure.mgmt.monitor.types.MetricAlertResource(TrackedResource):
        key "id": str
        key "identity": ForwardRef('Identity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": Required[MetricAlertProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: Identity
        location: str
        name: str
        properties: MetricAlertProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.monitor.types.MetricAlertResourcePatch(TypedDict, total=False):
        key "identity": ForwardRef('Identity', module='types')
        key "properties": ForwardRef('MetricAlertPropertiesPatch', module='types')
        identity: Identity
        properties: MetricAlertPropertiesPatch
        tags: dict[str, str]


    class azure.mgmt.monitor.types.MetricAlertSingleResourceMultipleMetricCriteria(TypedDict):
        key "odata.type": Required[Literal[Odatatype.MICROSOFT_AZURE_MONITOR_SINGLE_RESOURCE_MULTIPLE_METRIC_CRITERIA]]
        allOf: list[MetricCriteria]
        odata.type: Literal[Odatatype.MICROSOFT_AZURE_MONITOR_SINGLE_RESOURCE_MULTIPLE_METRIC_CRITERIA]


    class azure.mgmt.monitor.types.MetricCriteria(TypedDict, total=False):
        key "criterionType": Required[Literal[CriterionType.STATIC_THRESHOLD_CRITERION]]
        key "metricName": Required[str]
        key "metricNamespace": str
        key "name": Required[str]
        key "operator": Required[Union[str, Operator]]
        key "skipMetricValidation": bool
        key "threshold": Required[float]
        key "timeAggregation": Required[Union[str, AggregationTypeEnum]]
        criterionType: Literal[CriterionType.STATIC_THRESHOLD_CRITERION]
        dimensions: list[MetricDimension]
        metricName: str
        metricNamespace: str
        name: str
        operator: Union[str, Operator]
        skipMetricValidation: bool
        threshold: float
        timeAggregation: Union[str, AggregationTypeEnum]


    class azure.mgmt.monitor.types.MetricDimension(TypedDict, total=False):
        key "name": Required[str]
        key "operator": Required[str]
        key "values": Required[list[str]]
        name: str
        operator: str
        values: list[str]


    class azure.mgmt.monitor.types.MetricTrigger(TypedDict, total=False):
        key "dividePerInstance": bool
        key "metricName": Required[str]
        key "metricNamespace": str
        key "metricResourceLocation": str
        key "metricResourceUri": Required[str]
        key "operator": Required[Union[str, ComparisonOperationType]]
        key "statistic": Required[Union[str, MetricStatisticType]]
        key "threshold": Required[float]
        key "timeAggregation": Required[Union[str, TimeAggregationType]]
        key "timeGrain": Required[str]
        key "timeWindow": Required[str]
        dimensions: list[ScaleRuleMetricDimension]
        dividePerInstance: bool
        metricName: str
        metricNamespace: str
        metricResourceLocation: str
        metricResourceUri: str
        operator: Union[str, ComparisonOperationType]
        statistic: Union[str, MetricStatisticType]
        threshold: float
        timeAggregation: Union[str, TimeAggregationType]
        timeGrain: str
        timeWindow: str


    class azure.mgmt.monitor.types.MetricsIngestionEndpointSpec(TypedDict, total=False):
        key "endpoint": str
        endpoint: str


    class azure.mgmt.monitor.types.MicrosoftFabricDestination(TypedDict, total=False):
        key "artifactId": str
        key "databaseName": str
        key "ingestionUri": str
        key "name": str
        key "tenantId": str
        artifactId: str
        databaseName: str
        ingestionUri: str
        name: str
        tenantId: str


    class azure.mgmt.monitor.types.MonitoringAccountDestination(TypedDict, total=False):
        key "accountId": str
        key "accountResourceId": str
        key "name": str
        accountId: str
        accountResourceId: str
        name: str


    class azure.mgmt.monitor.types.NetworkRuleSet(TypedDict, total=False):
        key "publicNetworkAccess": Union[str, KnownPublicNetworkAccessOptions]
        publicNetworkAccess: Union[str, KnownPublicNetworkAccessOptions]


    class azure.mgmt.monitor.types.NotificationRequestBody(TypedDict, total=False):
        key "alertType": Required[str]
        alertType: str
        armRoleReceivers: list[ArmRoleReceiver]
        automationRunbookReceivers: list[AutomationRunbookReceiver]
        azureAppPushReceivers: list[AzureAppPushReceiver]
        azureFunctionReceivers: list[AzureFunctionReceiver]
        emailReceivers: list[EmailReceiver]
        eventHubReceivers: list[EventHubReceiver]
        incidentReceivers: list[IncidentReceiver]
        itsmReceivers: list[ItsmReceiver]
        logicAppReceivers: list[LogicAppReceiver]
        smsReceivers: list[SmsReceiver]
        voiceReceivers: list[VoiceReceiver]
        webhookReceivers: list[WebhookReceiver]


    class azure.mgmt.monitor.types.Odatatype(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MICROSOFT_AZURE_MONITOR_MULTIPLE_RESOURCE_MULTIPLE_METRIC_CRITERIA = "Microsoft.Azure.Monitor.MultipleResourceMultipleMetricCriteria"
        MICROSOFT_AZURE_MONITOR_PROM_QL_CRITERIA = "Microsoft.Azure.Monitor.PromQLCriteria"
        MICROSOFT_AZURE_MONITOR_SINGLE_RESOURCE_MULTIPLE_METRIC_CRITERIA = "Microsoft.Azure.Monitor.SingleResourceMultipleMetricCriteria"
        MICROSOFT_AZURE_MONITOR_WEBTEST_LOCATION_AVAILABILITY_CRITERIA = "Microsoft.Azure.Monitor.WebtestLocationAvailabilityCriteria"


    class azure.mgmt.monitor.types.OtelDataSourceResourceAttributeRouting(TypedDict, total=False):
        key "attributeName": str
        key "attributeValue": str
        attributeName: str
        attributeValue: str


    class azure.mgmt.monitor.types.OtelLogsDataSource(TypedDict, total=False):
        key "enrichWithReference": str
        key "name": str
        key "replaceResourceIdWithReference": bool
        key "resourceAttributeRouting": ForwardRef('OtelLogsDataSourceResourceAttributeRouting', module='types')
        key "streams": Required[list[Union[str, KnownOtelLogsDataSourceStreams]]]
        enrichWithReference: str
        enrichWithResourceAttributes: list[str]
        name: str
        replaceResourceIdWithReference: bool
        resourceAttributeRouting: OtelLogsDataSourceResourceAttributeRouting
        streams: list[Union[str, KnownOtelLogsDataSourceStreams]]


    class azure.mgmt.monitor.types.OtelLogsDataSourceResourceAttributeRouting(OtelDataSourceResourceAttributeRouting):
        key "attributeName": str
        key "attributeValue": str
        attributeName: str
        attributeValue: str


    class azure.mgmt.monitor.types.OtelLogsDirectDataSource(TypedDict, total=False):
        key "enrichWithReference": str
        key "name": str
        key "replaceResourceIdWithReference": bool
        key "streams": Required[list[Union[str, KnownOtelLogsDirectDataSourceStreams]]]
        enrichWithReference: str
        enrichWithResourceAttributes: list[str]
        name: str
        replaceResourceIdWithReference: bool
        streams: list[Union[str, KnownOtelLogsDirectDataSourceStreams]]


    class azure.mgmt.monitor.types.OtelMetricsDataSource(TypedDict, total=False):
        key "enrichWithReference": str
        key "name": str
        key "resourceAttributeRouting": ForwardRef('OtelMetricsDataSourceResourceAttributeRouting', module='types')
        key "streams": Required[list[str]]
        enrichWithReference: str
        enrichWithResourceAttributes: list[str]
        name: str
        resourceAttributeRouting: OtelMetricsDataSourceResourceAttributeRouting
        streams: list[str]


    class azure.mgmt.monitor.types.OtelMetricsDataSourceResourceAttributeRouting(OtelDataSourceResourceAttributeRouting):
        key "attributeName": str
        key "attributeValue": str
        attributeName: str
        attributeValue: str


    class azure.mgmt.monitor.types.OtelMetricsDirectDataSource(TypedDict, total=False):
        key "enrichWithReference": str
        key "name": str
        key "streams": Required[list[str]]
        enrichWithReference: str
        enrichWithResourceAttributes: list[str]
        name: str
        streams: list[str]


    class azure.mgmt.monitor.types.OtelTracesDataSource(TypedDict, total=False):
        key "enrichWithReference": str
        key "name": str
        key "replaceResourceIdWithReference": bool
        key "resourceAttributeRouting": ForwardRef('OtelTracesDataSourceResourceAttributeRouting', module='types')
        key "streams": Required[list[Union[str, KnownOtelTracesDataSourceStreams]]]
        enrichWithReference: str
        enrichWithResourceAttributes: list[str]
        name: str
        replaceResourceIdWithReference: bool
        resourceAttributeRouting: OtelTracesDataSourceResourceAttributeRouting
        streams: list[Union[str, KnownOtelTracesDataSourceStreams]]


    class azure.mgmt.monitor.types.OtelTracesDataSourceResourceAttributeRouting(OtelDataSourceResourceAttributeRouting):
        key "attributeName": str
        key "attributeValue": str
        attributeName: str
        attributeValue: str


    class azure.mgmt.monitor.types.OtelTracesDirectDataSource(TypedDict, total=False):
        key "enrichWithReference": str
        key "name": str
        key "replaceResourceIdWithReference": bool
        key "streams": Required[list[Union[str, KnownOtelTracesDirectDataSourceStreams]]]
        enrichWithReference: str
        enrichWithResourceAttributes: list[str]
        name: str
        replaceResourceIdWithReference: bool
        streams: list[Union[str, KnownOtelTracesDirectDataSourceStreams]]


    class azure.mgmt.monitor.types.PerfCounterDataSource(TypedDict, total=False):
        key "name": str
        key "samplingFrequencyInSeconds": int
        key "transformKql": str
        counterSpecifiers: list[str]
        name: str
        samplingFrequencyInSeconds: int
        streams: list[Union[str, KnownPerfCounterDataSourceStreams]]
        transformKql: str


    class azure.mgmt.monitor.types.PerformanceCountersOTelDataSource(TypedDict, total=False):
        key "name": str
        key "samplingFrequencyInSeconds": int
        counterSpecifiers: list[str]
        name: str
        samplingFrequencyInSeconds: int
        streams: list[Union[str, KnownPerformanceCountersOTelDataSourceStreams]]


    class azure.mgmt.monitor.types.PlatformTelemetryDataSource(TypedDict, total=False):
        key "name": str
        key "streams": Required[list[str]]
        name: str
        streams: list[str]


    class azure.mgmt.monitor.types.PredictiveAutoscalePolicy(TypedDict, total=False):
        key "scaleLookAheadTime": str
        key "scaleMode": Required[Union[str, PredictiveAutoscalePolicyScaleMode]]
        scaleLookAheadTime: str
        scaleMode: Union[str, PredictiveAutoscalePolicyScaleMode]


    class azure.mgmt.monitor.types.PrivateEndpoint(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.monitor.types.PrivateEndpointConnection(Resource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('PrivateEndpointConnectionProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: PrivateEndpointConnectionProperties
        systemData: SystemData
        type: str


    class azure.mgmt.monitor.types.PrivateEndpointConnectionProperties(TypedDict, total=False):
        key "privateEndpoint": ForwardRef('PrivateEndpoint', module='types')
        key "privateLinkServiceConnectionState": Required[PrivateLinkServiceConnectionState]
        key "provisioningState": Union[str, PrivateEndpointConnectionProvisioningState]
        groupIds: list[str]
        privateEndpoint: PrivateEndpoint
        privateLinkServiceConnectionState: PrivateLinkServiceConnectionState
        provisioningState: Union[str, PrivateEndpointConnectionProvisioningState]


    class azure.mgmt.monitor.types.PrivateLinkScopedResource(TypedDict, total=False):
        key "resourceId": str
        key "scopeId": str
        resourceId: str
        scopeId: str


    class azure.mgmt.monitor.types.PrivateLinkServiceConnectionState(TypedDict, total=False):
        key "actionsRequired": str
        key "description": str
        key "status": Union[str, PrivateEndpointServiceConnectionStatus]
        actionsRequired: str
        description: str
        status: Union[str, PrivateEndpointServiceConnectionStatus]


    class azure.mgmt.monitor.types.PromQLCriteria(TypedDict):
        key "failingPeriods": ForwardRef('QueryFailingPeriods', module='types')
        key "odata.type": Required[Literal[Odatatype.MICROSOFT_AZURE_MONITOR_PROM_QL_CRITERIA]]
        allOf: list[MultiPromQLCriteria]
        failingPeriods: QueryFailingPeriods
        odata.type: Literal[Odatatype.MICROSOFT_AZURE_MONITOR_PROM_QL_CRITERIA]


    class azure.mgmt.monitor.types.PrometheusForwarderDataSource(TypedDict, total=False):
        key "name": str
        customVMScrapeConfig: list[Any]
        labelIncludeFilter: dict[str, str]
        name: str
        streams: list[Union[str, KnownPrometheusForwarderDataSourceStreams]]


    class azure.mgmt.monitor.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.monitor.types.QueryFailingPeriods(TypedDict):
        key "for": Required[str]
        for: str


    class azure.mgmt.monitor.types.Recurrence(TypedDict, total=False):
        key "frequency": Required[Union[str, RecurrenceFrequency]]
        key "schedule": Required[RecurrentSchedule]
        frequency: Union[str, RecurrenceFrequency]
        schedule: RecurrentSchedule


    class azure.mgmt.monitor.types.RecurrentSchedule(TypedDict, total=False):
        key "days": Required[list[str]]
        key "hours": Required[list[int]]
        key "minutes": Required[list[int]]
        key "timeZone": Required[str]
        days: list[str]
        hours: list[int]
        minutes: list[int]
        timeZone: str


    class azure.mgmt.monitor.types.ReferencesSpec(TypedDict, total=False):
        key "enrichmentData": ForwardRef('ReferencesSpecEnrichmentData', module='types')
        applicationInsights: list[ApplicationInsights]
        enrichmentData: ReferencesSpecEnrichmentData


    class azure.mgmt.monitor.types.ReferencesSpecEnrichmentData(EnrichmentData):
        storageBlobs: list[StorageBlob]


    class azure.mgmt.monitor.types.ResolveConfiguration(TypedDict, total=False):
        key "autoResolved": Required[bool]
        key "timeToResolve": str
        autoResolved: bool
        timeToResolve: str


    class azure.mgmt.monitor.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.monitor.types.ResourceForUpdate(TypedDict, total=False):
        key "identity": ForwardRef('ResourceForUpdateIdentity', module='types')
        identity: ResourceForUpdateIdentity
        tags: dict[str, str]


    class azure.mgmt.monitor.types.ResourceForUpdateIdentity(ManagedServiceIdentity):
        key "principalId": str
        key "tenantId": str
        key "type": Required[Union[str, ManagedServiceIdentityType]]
        principalId: str
        tenantId: str
        type: Union[str, ManagedServiceIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentity]


    class azure.mgmt.monitor.types.RetentionPolicy(TypedDict, total=False):
        key "days": Required[int]
        key "enabled": Required[bool]
        days: int
        enabled: bool


    class azure.mgmt.monitor.types.RuleResolveConfiguration(TypedDict, total=False):
        key "autoResolved": bool
        key "timeToResolve": str
        autoResolved: bool
        timeToResolve: str


    class azure.mgmt.monitor.types.ScaleAction(TypedDict, total=False):
        key "cooldown": Required[str]
        key "direction": Required[Union[str, ScaleDirection]]
        key "type": Required[Union[str, ScaleType]]
        key "value": str
        cooldown: str
        direction: Union[str, ScaleDirection]
        type: Union[str, ScaleType]
        value: str


    class azure.mgmt.monitor.types.ScaleCapacity(TypedDict, total=False):
        key "default": Required[str]
        key "maximum": Required[str]
        key "minimum": Required[str]
        default: str
        maximum: str
        minimum: str


    class azure.mgmt.monitor.types.ScaleRule(TypedDict, total=False):
        key "metricTrigger": Required[MetricTrigger]
        key "scaleAction": Required[ScaleAction]
        metricTrigger: MetricTrigger
        scaleAction: ScaleAction


    class azure.mgmt.monitor.types.ScaleRuleMetricDimension(TypedDict, total=False):
        key "DimensionName": Required[str]
        key "Operator": Required[Union[str, ScaleRuleMetricDimensionOperationType]]
        key "Values": Required[list[str]]
        DimensionName: str
        Operator: Union[str, ScaleRuleMetricDimensionOperationType]
        Values: list[str]


    class azure.mgmt.monitor.types.ScheduledQueryRuleCriteria(TypedDict, total=False):
        allOf: list[Condition]


    class azure.mgmt.monitor.types.ScheduledQueryRuleProperties(TypedDict, total=False):
        key "actions": ForwardRef('Actions', module='types')
        key "autoMitigate": bool
        key "checkWorkspaceAlertsStorageConfigured": bool
        key "createdWithApiVersion": str
        key "criteria": ForwardRef('ScheduledQueryRuleCriteria', module='types')
        key "description": str
        key "displayName": str
        key "enabled": bool
        key "evaluationFrequency": str
        key "isLegacyLogAnalyticsRule": bool
        key "isWorkspaceAlertsStorageConfigured": bool
        key "muteActionsDuration": str
        key "overrideQueryTimeRange": str
        key "resolveConfiguration": ForwardRef('RuleResolveConfiguration', module='types')
        key "severity": Union[int, AlertSeverity]
        key "skipQueryValidation": bool
        key "windowSize": str
        actions: Actions
        autoMitigate: bool
        checkWorkspaceAlertsStorageConfigured: bool
        createdWithApiVersion: str
        criteria: ScheduledQueryRuleCriteria
        description: str
        displayName: str
        enabled: bool
        evaluationFrequency: str
        isLegacyLogAnalyticsRule: bool
        isWorkspaceAlertsStorageConfigured: bool
        muteActionsDuration: str
        overrideQueryTimeRange: str
        resolveConfiguration: RuleResolveConfiguration
        scopes: list[str]
        severity: Union[int, AlertSeverity]
        skipQueryValidation: bool
        targetResourceTypes: list[str]
        windowSize: str


    class azure.mgmt.monitor.types.ScheduledQueryRuleResource(ProxyResource):
        key "etag": str
        key "id": str
        key "identity": ForwardRef('Identity', module='types')
        key "kind": Union[str, Kind]
        key "location": Required[str]
        key "name": str
        key "properties": Required[ScheduledQueryRuleProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        identity: Identity
        kind: Union[str, Kind]
        location: str
        name: str
        properties: ScheduledQueryRuleProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.monitor.types.ScheduledQueryRuleResourcePatch(TypedDict, total=False):
        key "identity": ForwardRef('Identity', module='types')
        key "properties": ForwardRef('ScheduledQueryRuleProperties', module='types')
        identity: Identity
        properties: ScheduledQueryRuleProperties
        tags: dict[str, str]


    class azure.mgmt.monitor.types.ScopedResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('ScopedResourceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ScopedResourceProperties
        systemData: SystemData
        type: str


    class azure.mgmt.monitor.types.ScopedResourceProperties(TypedDict, total=False):
        key "kind": Union[str, ScopedResourceKind]
        key "linkedResourceId": str
        key "provisioningState": Union[str, ScopedResourceProvisioningState]
        key "subscriptionLocation": str
        kind: Union[str, ScopedResourceKind]
        linkedResourceId: str
        provisioningState: Union[str, ScopedResourceProvisioningState]
        subscriptionLocation: str


    class azure.mgmt.monitor.types.ServiceDiagnosticSettings(TypedDict, total=False):
        key "eventHubAuthorizationRuleId": str
        key "serviceBusRuleId": str
        key "storageAccountId": str
        key "workspaceId": str
        eventHubAuthorizationRuleId: str
        logs: list[DiagnosticsLogSettings]
        metrics: list[DiagnosticsMetricSettings]
        serviceBusRuleId: str
        storageAccountId: str
        workspaceId: str


    class azure.mgmt.monitor.types.ServiceDiagnosticSettingsResource(ExtensionResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('ServiceDiagnosticSettings', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: ServiceDiagnosticSettings
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.monitor.types.ServiceDiagnosticSettingsResourcePatch(TypedDict, total=False):
        key "properties": ForwardRef('ServiceDiagnosticSettings', module='types')
        properties: ServiceDiagnosticSettings
        tags: dict[str, str]


    class azure.mgmt.monitor.types.Sku(TypedDict, total=False):
        key "capacity": int
        key "family": str
        key "name": Required[str]
        key "size": str
        key "tier": Union[str, SkuTier]
        capacity: int
        family: str
        name: str
        size: str
        tier: Union[str, SkuTier]


    class azure.mgmt.monitor.types.SmsReceiver(TypedDict, total=False):
        key "countryCode": Required[str]
        key "name": Required[str]
        key "phoneNumber": Required[str]
        key "status": Union[str, ReceiverStatus]
        countryCode: str
        name: str
        phoneNumber: str
        status: Union[str, ReceiverStatus]


    class azure.mgmt.monitor.types.StaticPromQLCriteria(TypedDict, total=False):
        key "criterionType": Required[Literal[CriterionType.STATIC_THRESHOLD_CRITERION]]
        key "name": Required[str]
        key "query": Required[str]
        criterionType: Literal[CriterionType.STATIC_THRESHOLD_CRITERION]
        name: str
        query: str


    class azure.mgmt.monitor.types.StorageBlob(TypedDict, total=False):
        key "blobUrl": str
        key "lookupType": Union[str, KnownStorageBlobLookupType]
        key "name": str
        key "resourceId": str
        blobUrl: str
        lookupType: Union[str, KnownStorageBlobLookupType]
        name: str
        resourceId: str


    class azure.mgmt.monitor.types.StorageBlobDestination(TypedDict, total=False):
        key "containerName": str
        key "name": str
        key "storageAccountResourceId": str
        containerName: str
        name: str
        storageAccountResourceId: str


    class azure.mgmt.monitor.types.StorageTableDestination(TypedDict, total=False):
        key "name": str
        key "storageAccountResourceId": str
        key "tableName": str
        name: str
        storageAccountResourceId: str
        tableName: str


    class azure.mgmt.monitor.types.StreamDeclaration(TypedDict, total=False):
        columns: list[ColumnDefinition]


    class azure.mgmt.monitor.types.SubscriptionScopeMetricsRequestBodyParameters(TypedDict, total=False):
        key "aggregation": str
        key "autoAdjustTimegrain": bool
        key "filter": str
        key "interval": str
        key "metricNames": str
        key "metricNamespace": str
        key "orderBy": str
        key "resultType": Union[str, MetricResultType]
        key "rollUpBy": str
        key "timespan": str
        key "top": int
        key "validateDimensions": bool
        aggregation: str
        autoAdjustTimegrain: bool
        filter: str
        interval: str
        metricNames: str
        metricNamespace: str
        orderBy: str
        resultType: Union[str, MetricResultType]
        rollUpBy: str
        timespan: str
        top: int
        validateDimensions: bool


    class azure.mgmt.monitor.types.SyslogDataSource(TypedDict, total=False):
        key "name": str
        key "transformKql": str
        facilityNames: list[Union[str, KnownSyslogDataSourceFacilityNames]]
        logLevels: list[Union[str, KnownSyslogDataSourceLogLevels]]
        name: str
        streams: list[Union[str, KnownSyslogDataSourceStreams]]
        transformKql: str


    class azure.mgmt.monitor.types.SystemData(TypedDict, total=False):
        key "createdAt": str
        key "createdBy": str
        key "createdByType": Union[str, CreatedByType]
        key "lastModifiedAt": str
        key "lastModifiedBy": str
        key "lastModifiedByType": Union[str, CreatedByType]
        createdAt: str
        createdBy: str
        createdByType: Union[str, CreatedByType]
        lastModifiedAt: str
        lastModifiedBy: str
        lastModifiedByType: Union[str, CreatedByType]


    class azure.mgmt.monitor.types.TagsResource(TypedDict, total=False):
        tags: dict[str, str]


    class azure.mgmt.monitor.types.TenantActionGroup(TypedDict, total=False):
        key "enabled": Required[bool]
        key "groupShortName": Required[str]
        azureAppPushReceivers: list[AzureAppPushReceiver]
        emailReceivers: list[EmailReceiver]
        enabled: bool
        groupShortName: str
        smsReceivers: list[SmsReceiver]
        voiceReceivers: list[VoiceReceiver]
        webhookReceivers: list[TenantActionGroupWebhookReceiver]


    class azure.mgmt.monitor.types.TenantActionGroupPatchBody(TypedDict, total=False):
        key "properties": ForwardRef('ActionGroupPatch', module='types')
        properties: ActionGroupPatch
        tags: dict[str, str]


    class azure.mgmt.monitor.types.TenantActionGroupResource(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('TenantActionGroup', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: TenantActionGroup
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.monitor.types.TenantActionGroupWebhookReceiver(TypedDict, total=False):
        key "identifierUri": str
        key "name": Required[str]
        key "objectId": str
        key "serviceUri": Required[str]
        key "tenantId": str
        key "useAadAuth": bool
        key "useCommonAlertSchema": bool
        identifierUri: str
        name: str
        objectId: str
        serviceUri: str
        tenantId: str
        useAadAuth: bool
        useCommonAlertSchema: bool


    class azure.mgmt.monitor.types.TenantNotificationRequestBody(TypedDict, total=False):
        key "alertType": Required[str]
        alertType: str
        azureAppPushReceivers: list[AzureAppPushReceiver]
        emailReceivers: list[EmailReceiver]
        smsReceivers: list[SmsReceiver]
        voiceReceivers: list[VoiceReceiver]
        webhookReceivers: list[TenantActionGroupWebhookReceiver]


    class azure.mgmt.monitor.types.TimeWindow(TypedDict, total=False):
        key "end": Required[str]
        key "start": Required[str]
        key "timeZone": str
        end: str
        start: str
        timeZone: str


    class azure.mgmt.monitor.types.TrackedResource(Resource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.monitor.types.UserAssignedIdentity(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        clientId: str
        principalId: str


    class azure.mgmt.monitor.types.UserIdentityProperties(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        clientId: str
        principalId: str


    class azure.mgmt.monitor.types.VoiceReceiver(TypedDict, total=False):
        key "countryCode": Required[str]
        key "name": Required[str]
        key "phoneNumber": Required[str]
        countryCode: str
        name: str
        phoneNumber: str


    class azure.mgmt.monitor.types.WebhookNotification(TypedDict, total=False):
        key "serviceUri": str
        properties: dict[str, str]
        serviceUri: str


    class azure.mgmt.monitor.types.WebhookReceiver(TypedDict, total=False):
        key "identifierUri": str
        key "managedIdentity": str
        key "name": Required[str]
        key "objectId": str
        key "serviceUri": Required[str]
        key "tenantId": str
        key "useAadAuth": bool
        key "useCommonAlertSchema": bool
        identifierUri: str
        managedIdentity: str
        name: str
        objectId: str
        serviceUri: str
        tenantId: str
        useAadAuth: bool
        useCommonAlertSchema: bool


    class azure.mgmt.monitor.types.WebtestLocationAvailabilityCriteria(TypedDict):
        key "componentId": Required[str]
        key "failedLocationCount": Required[float]
        key "odata.type": Required[Literal[Odatatype.MICROSOFT_AZURE_MONITOR_WEBTEST_LOCATION_AVAILABILITY_CRITERIA]]
        key "webTestId": Required[str]
        componentId: str
        failedLocationCount: float
        odata.type: Literal[Odatatype.MICROSOFT_AZURE_MONITOR_WEBTEST_LOCATION_AVAILABILITY_CRITERIA]
        webTestId: str


    class azure.mgmt.monitor.types.WindowsEventLogDataSource(TypedDict, total=False):
        key "name": str
        key "transformKql": str
        name: str
        streams: list[Union[str, KnownWindowsEventLogDataSourceStreams]]
        transformKql: str
        xPathQueries: list[str]


    class azure.mgmt.monitor.types.WindowsFirewallLogsDataSource(TypedDict, total=False):
        key "name": str
        key "streams": Required[list[str]]
        name: str
        profileFilter: list[Union[str, KnownWindowsFirewallLogsDataSourceProfileFilter]]
        streams: list[str]


```