```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.monitor

    class azure.mgmt.monitor.MonitorManagementClient: implements ContextManager 
        action_groups: ActionGroupsOperations
        activity_log_alerts: ActivityLogAlertsOperations
        activity_logs: ActivityLogsOperations
        alert_rule_incidents: AlertRuleIncidentsOperations
        autoscale_settings: AutoscaleSettingsOperations
        azure_monitor_workspaces: AzureMonitorWorkspacesOperations
        baselines: BaselinesOperations
        data_collection_endpoints: DataCollectionEndpointsOperations
        data_collection_rule_associations: DataCollectionRuleAssociationsOperations
        data_collection_rules: DataCollectionRulesOperations
        diagnostic_settings: DiagnosticSettingsOperations
        diagnostic_settings_category: DiagnosticSettingsCategoryOperations
        event_categories: EventCategoriesOperations
        guest_diagnostics_settings: GuestDiagnosticsSettingsOperations
        guest_diagnostics_settings_association: GuestDiagnosticsSettingsAssociationOperations
        log_profiles: LogProfilesOperations
        metric_alerts: MetricAlertsOperations
        metric_alerts_status: MetricAlertsStatusOperations
        metric_definitions: MetricDefinitionsOperations
        metric_namespaces: MetricNamespacesOperations
        metrics: MetricsOperations
        monitor_operations: MonitorOperationsOperations
        operations: Operations
        predictive_metric: PredictiveMetricOperations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        private_link_scope_operation_status: PrivateLinkScopeOperationStatusOperations
        private_link_scoped_resources: PrivateLinkScopedResourcesOperations
        private_link_scopes: PrivateLinkScopesOperations
        scheduled_query_rules: ScheduledQueryRulesOperations
        service_diagnostic_settings: ServiceDiagnosticSettingsOperations
        subscription_diagnostic_settings: SubscriptionDiagnosticSettingsOperations
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

        def close(self) -> None: ...


namespace azure.mgmt.monitor.aio

    class azure.mgmt.monitor.aio.MonitorManagementClient: implements AsyncContextManager 
        action_groups: ActionGroupsOperations
        activity_log_alerts: ActivityLogAlertsOperations
        activity_logs: ActivityLogsOperations
        alert_rule_incidents: AlertRuleIncidentsOperations
        autoscale_settings: AutoscaleSettingsOperations
        azure_monitor_workspaces: AzureMonitorWorkspacesOperations
        baselines: BaselinesOperations
        data_collection_endpoints: DataCollectionEndpointsOperations
        data_collection_rule_associations: DataCollectionRuleAssociationsOperations
        data_collection_rules: DataCollectionRulesOperations
        diagnostic_settings: DiagnosticSettingsOperations
        diagnostic_settings_category: DiagnosticSettingsCategoryOperations
        event_categories: EventCategoriesOperations
        guest_diagnostics_settings: GuestDiagnosticsSettingsOperations
        guest_diagnostics_settings_association: GuestDiagnosticsSettingsAssociationOperations
        log_profiles: LogProfilesOperations
        metric_alerts: MetricAlertsOperations
        metric_alerts_status: MetricAlertsStatusOperations
        metric_definitions: MetricDefinitionsOperations
        metric_namespaces: MetricNamespacesOperations
        metrics: MetricsOperations
        monitor_operations: MonitorOperationsOperations
        operations: Operations
        predictive_metric: PredictiveMetricOperations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        private_link_scope_operation_status: PrivateLinkScopeOperationStatusOperations
        private_link_scoped_resources: PrivateLinkScopedResourcesOperations
        private_link_scopes: PrivateLinkScopesOperations
        scheduled_query_rules: ScheduledQueryRulesOperations
        service_diagnostic_settings: ServiceDiagnosticSettingsOperations
        subscription_diagnostic_settings: SubscriptionDiagnosticSettingsOperations
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

        async def close(self) -> None: ...


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
                notification_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TestNotificationDetailsResponse]: ...

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
                enable_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                action_group_name: str, 
                **kwargs: Any
            ) -> ActionGroupResource: ...

        @distributed_trace_async
        async def get_test_notifications_at_action_group_resource_level(
                self, 
                resource_group_name: str, 
                action_group_name: str, 
                notification_id: str, 
                **kwargs: Any
            ) -> TestNotificationDetailsResponse: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ActionGroupResource]: ...

        @distributed_trace
        def list_by_subscription_id(self, **kwargs: Any) -> AsyncItemPaged[ActionGroupResource]: ...

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
                filter: str, 
                select: Optional[str] = None, 
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
                autoscale_setting_resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutoscaleSettingResource: ...


    class azure.mgmt.monitor.aio.operations.AzureMonitorWorkspacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                azure_monitor_workspace_properties: AzureMonitorWorkspaceResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureMonitorWorkspaceResource: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                azure_monitor_workspace_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureMonitorWorkspaceResource: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                **kwargs: Any
            ) -> AzureMonitorWorkspaceResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AzureMonitorWorkspaceResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[AzureMonitorWorkspaceResource]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                azure_monitor_workspace_properties: Optional[AzureMonitorWorkspaceResourceForUpdate] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureMonitorWorkspaceResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                azure_monitor_workspace_properties: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureMonitorWorkspaceResource: ...


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
                metricnames: Optional[str] = None, 
                metricnamespace: Optional[str] = None, 
                timespan: Optional[str] = None, 
                interval: Optional[timedelta] = None, 
                aggregation: Optional[str] = None, 
                sensitivities: Optional[str] = None, 
                filter: Optional[str] = None, 
                result_type: Optional[Union[str, ResultType]] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[SingleMetricBaseline]: ...


    class azure.mgmt.monitor.aio.operations.DataCollectionEndpointsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
        async def delete(
                self, 
                resource_group_name: str, 
                data_collection_endpoint_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                data_collection_endpoint_name: str, 
                **kwargs: Any
            ) -> DataCollectionEndpointResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DataCollectionEndpointResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[DataCollectionEndpointResource]: ...

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
                delete_associations: bool = False, 
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

        @distributed_trace_async
        async def list(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> DiagnosticSettingsCategoryResourceCollection: ...


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


    class azure.mgmt.monitor.aio.operations.GuestDiagnosticsSettingsAssociationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_uri: str, 
                association_name: str, 
                diagnostic_settings_association: GuestDiagnosticSettingsAssociationResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GuestDiagnosticSettingsAssociationResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_uri: str, 
                association_name: str, 
                diagnostic_settings_association: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GuestDiagnosticSettingsAssociationResource: ...

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
            ) -> GuestDiagnosticSettingsAssociationResource: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[GuestDiagnosticSettingsAssociationResource]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[GuestDiagnosticSettingsAssociationResource]: ...

        @overload
        async def update(
                self, 
                resource_uri: str, 
                association_name: str, 
                parameters: GuestDiagnosticSettingsAssociationResourcePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GuestDiagnosticSettingsAssociationResource: ...

        @overload
        async def update(
                self, 
                resource_uri: str, 
                association_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GuestDiagnosticSettingsAssociationResource: ...


    class azure.mgmt.monitor.aio.operations.GuestDiagnosticsSettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                diagnostic_settings_name: str, 
                diagnostic_settings: GuestDiagnosticSettingsResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GuestDiagnosticSettingsResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                diagnostic_settings_name: str, 
                diagnostic_settings: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GuestDiagnosticSettingsResource: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                diagnostic_settings_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                diagnostic_settings_name: str, 
                **kwargs: Any
            ) -> GuestDiagnosticSettingsResource: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[GuestDiagnosticSettingsResource]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[GuestDiagnosticSettingsResource]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                diagnostic_settings_name: str, 
                parameters: GuestDiagnosticSettingsPatchResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GuestDiagnosticSettingsResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                diagnostic_settings_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GuestDiagnosticSettingsResource: ...


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
                metricnamespace: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[MetricDefinition]: ...

        @distributed_trace
        def list_at_subscription_scope(
                self, 
                region: str, 
                metricnamespace: Optional[str] = None, 
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
                start_time: Optional[str] = None, 
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
                timespan: Optional[str] = None, 
                interval: Optional[str] = None, 
                metricnames: Optional[str] = None, 
                aggregation: Optional[str] = None, 
                top: Optional[int] = None, 
                orderby: Optional[str] = None, 
                filter: Optional[str] = None, 
                result_type: Optional[Union[str, ResultType]] = None, 
                metricnamespace: Optional[str] = None, 
                auto_adjust_timegrain: Optional[bool] = None, 
                validate_dimensions: Optional[bool] = None, 
                rollupby: Optional[str] = None, 
                **kwargs: Any
            ) -> Response: ...

        @distributed_trace_async
        async def list_at_subscription_scope(
                self, 
                region: str, 
                timespan: Optional[str] = None, 
                interval: Optional[str] = None, 
                metricnames: Optional[str] = None, 
                aggregation: Optional[str] = None, 
                top: Optional[int] = None, 
                orderby: Optional[str] = None, 
                filter: Optional[str] = None, 
                result_type: Optional[Union[str, MetricResultType]] = None, 
                metricnamespace: Optional[str] = None, 
                auto_adjust_timegrain: Optional[bool] = None, 
                validate_dimensions: Optional[bool] = None, 
                rollupby: Optional[str] = None, 
                **kwargs: Any
            ) -> Response: ...

        @overload
        async def list_at_subscription_scope_post(
                self, 
                region: str, 
                timespan: Optional[str] = None, 
                interval: Optional[str] = None, 
                metricnames: Optional[str] = None, 
                aggregation: Optional[str] = None, 
                top: Optional[int] = None, 
                orderby: Optional[str] = None, 
                filter: Optional[str] = None, 
                result_type: Optional[Union[str, MetricResultType]] = None, 
                metricnamespace: Optional[str] = None, 
                auto_adjust_timegrain: Optional[bool] = None, 
                validate_dimensions: Optional[bool] = None, 
                rollupby: Optional[str] = None, 
                body: Optional[SubscriptionScopeMetricsRequestBodyParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Response: ...

        @overload
        async def list_at_subscription_scope_post(
                self, 
                region: str, 
                timespan: Optional[str] = None, 
                interval: Optional[str] = None, 
                metricnames: Optional[str] = None, 
                aggregation: Optional[str] = None, 
                top: Optional[int] = None, 
                orderby: Optional[str] = None, 
                filter: Optional[str] = None, 
                result_type: Optional[Union[str, MetricResultType]] = None, 
                metricnamespace: Optional[str] = None, 
                auto_adjust_timegrain: Optional[bool] = None, 
                validate_dimensions: Optional[bool] = None, 
                rollupby: Optional[str] = None, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Response: ...


    class azure.mgmt.monitor.aio.operations.MonitorOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[OperationAutoGenerated]: ...


    class azure.mgmt.monitor.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def list(self, **kwargs: Any) -> OperationListResult: ...


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
                timespan: str, 
                interval: timedelta, 
                metric_namespace: str, 
                metric_name: str, 
                aggregation: str, 
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
                private_link_scope_tags: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureMonitorPrivateLinkScope: ...


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
                service_diagnostic_settings_resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServiceDiagnosticSettingsResource: ...


    class azure.mgmt.monitor.aio.operations.SubscriptionDiagnosticSettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                name: str, 
                parameters: SubscriptionDiagnosticSettingsResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SubscriptionDiagnosticSettingsResource: ...

        @overload
        async def create_or_update(
                self, 
                name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SubscriptionDiagnosticSettingsResource: ...

        @distributed_trace_async
        async def delete(
                self, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                name: str, 
                **kwargs: Any
            ) -> SubscriptionDiagnosticSettingsResource: ...

        @distributed_trace_async
        async def list(self, **kwargs: Any) -> SubscriptionDiagnosticSettingsResourceCollection: ...


    class azure.mgmt.monitor.aio.operations.TenantActivityLogsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                filter: Optional[str] = None, 
                select: Optional[str] = None, 
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

    class azure.mgmt.monitor.models.ActionDetail(Model):
        detail: str
        mechanism_type: str
        name: str
        send_time: str
        status: str
        sub_state: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                detail: Optional[str] = ..., 
                mechanism_type: Optional[str] = ..., 
                name: Optional[str] = ..., 
                send_time: Optional[str] = ..., 
                status: Optional[str] = ..., 
                sub_state: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ActionGroup(Model):
        action_group_id: str
        webhook_properties: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                action_group_id: str, 
                webhook_properties: Optional[dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ActionGroupList(Model):
        next_link: str
        value: list[ActionGroupResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[list[ActionGroupResource]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ActionGroupPatchBody(Model):
        enabled: bool
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                enabled: bool = True, 
                tags: Optional[dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ActionGroupResource(AzureResource):
        arm_role_receivers: list[ArmRoleReceiver]
        automation_runbook_receivers: list[AutomationRunbookReceiver]
        azure_app_push_receivers: list[AzureAppPushReceiver]
        azure_function_receivers: list[AzureFunctionReceiver]
        email_receivers: list[EmailReceiver]
        enabled: bool
        event_hub_receivers: list[EventHubReceiver]
        group_short_name: str
        id: str
        itsm_receivers: list[ItsmReceiver]
        location: str
        logic_app_receivers: list[LogicAppReceiver]
        name: str
        sms_receivers: list[SmsReceiver]
        tags: dict[str, str]
        type: str
        voice_receivers: list[VoiceReceiver]
        webhook_receivers: list[WebhookReceiver]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                arm_role_receivers: Optional[list[ArmRoleReceiver]] = ..., 
                automation_runbook_receivers: Optional[list[AutomationRunbookReceiver]] = ..., 
                azure_app_push_receivers: Optional[list[AzureAppPushReceiver]] = ..., 
                azure_function_receivers: Optional[list[AzureFunctionReceiver]] = ..., 
                email_receivers: Optional[list[EmailReceiver]] = ..., 
                enabled: bool = True, 
                event_hub_receivers: Optional[list[EventHubReceiver]] = ..., 
                group_short_name: Optional[str] = ..., 
                itsm_receivers: Optional[list[ItsmReceiver]] = ..., 
                location: str, 
                logic_app_receivers: Optional[list[LogicAppReceiver]] = ..., 
                sms_receivers: Optional[list[SmsReceiver]] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                voice_receivers: Optional[list[VoiceReceiver]] = ..., 
                webhook_receivers: Optional[list[WebhookReceiver]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ActionList(Model):
        action_groups: list[ActionGroup]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                action_groups: Optional[list[ActionGroup]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.monitor.models.Actions(Model):
        action_groups: list[str]
        action_properties: dict[str, str]
        custom_properties: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                action_groups: Optional[list[str]] = ..., 
                action_properties: Optional[dict[str, str]] = ..., 
                custom_properties: Optional[dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ActivityLogAlertResource(AzureResourceAutoGenerated):
        actions: ActionList
        condition: AlertRuleAllOfCondition
        description: str
        enabled: bool
        id: str
        location: str
        name: str
        scopes: list[str]
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                actions: Optional[ActionList] = ..., 
                condition: Optional[AlertRuleAllOfCondition] = ..., 
                description: Optional[str] = ..., 
                enabled: bool = True, 
                location: str = "global", 
                scopes: Optional[list[str]] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.AdxDestination(Model):
        database_name: str
        ingestion_uri: str
        name: str
        resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                database_name: Optional[str] = ..., 
                name: Optional[str] = ..., 
                resource_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.AgentSetting(Model):
        name: Union[str, KnownAgentSettingName]
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[Union[str, KnownAgentSettingName]] = ..., 
                value: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.AgentSettingsSpec(Model):
        logs: list[AgentSetting]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                logs: Optional[list[AgentSetting]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


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


    class azure.mgmt.monitor.models.AlertRuleAllOfCondition(Model):
        all_of: list[AlertRuleAnyOfOrLeafCondition]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                all_of: list[AlertRuleAnyOfOrLeafCondition], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.AlertRuleAnyOfOrLeafCondition(AlertRuleLeafCondition):
        any_of: list[AlertRuleLeafCondition]
        contains_any: list[str]
        equals: str
        field: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                any_of: Optional[list[AlertRuleLeafCondition]] = ..., 
                contains_any: Optional[list[str]] = ..., 
                equals: Optional[str] = ..., 
                field: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.AlertRuleLeafCondition(Model):
        contains_any: list[str]
        equals: str
        field: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                contains_any: Optional[list[str]] = ..., 
                equals: Optional[str] = ..., 
                field: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.AlertRuleList(Model):
        next_link: str
        value: list[ActivityLogAlertResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[list[ActivityLogAlertResource]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.AlertRulePatchObject(Model):
        enabled: bool
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                enabled: bool = True, 
                tags: Optional[dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.AlertSeverity(int, Enum, metaclass=CaseInsensitiveEnumMeta):
        FOUR = 4
        ONE = 1
        THREE = 3
        TWO = 2
        ZERO = 0


    class azure.mgmt.monitor.models.ArmRoleReceiver(Model):
        name: str
        role_id: str
        use_common_alert_schema: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: str, 
                role_id: str, 
                use_common_alert_schema: bool = False, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.AutomationRunbookReceiver(Model):
        automation_account_id: str
        is_global_runbook: bool
        name: str
        runbook_name: str
        service_uri: str
        use_common_alert_schema: bool
        webhook_resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                automation_account_id: str, 
                is_global_runbook: bool, 
                name: Optional[str] = ..., 
                runbook_name: str, 
                service_uri: Optional[str] = ..., 
                use_common_alert_schema: bool = False, 
                webhook_resource_id: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.AutoscaleErrorResponse(Model):
        error: AutoscaleErrorResponseError
        system_data: SystemData

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error: Optional[AutoscaleErrorResponseError] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.AutoscaleErrorResponseError(Model):
        code: str
        details: str
        message: str
        target: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                details: Optional[str] = ..., 
                message: Optional[str] = ..., 
                target: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.AutoscaleNotification(Model):
        email: EmailNotification
        operation: str = "Scale"
        webhooks: list[WebhookNotification]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                email: Optional[EmailNotification] = ..., 
                webhooks: Optional[list[WebhookNotification]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.AutoscaleProfile(Model):
        capacity: ScaleCapacity
        fixed_date: TimeWindow
        name: str
        recurrence: Recurrence
        rules: list[ScaleRule]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                capacity: ScaleCapacity, 
                fixed_date: Optional[TimeWindow] = ..., 
                name: str, 
                recurrence: Optional[Recurrence] = ..., 
                rules: list[ScaleRule], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.AutoscaleSettingResource(Resource):
        enabled: bool
        id: str
        location: str
        name: str
        name_properties_name: str
        notifications: list[AutoscaleNotification]
        predictive_autoscale_policy: PredictiveAutoscalePolicy
        profiles: list[AutoscaleProfile]
        system_data: SystemData
        tags: dict[str, str]
        target_resource_location: str
        target_resource_uri: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                enabled: bool = False, 
                location: str, 
                name_properties_name: Optional[str] = ..., 
                notifications: Optional[list[AutoscaleNotification]] = ..., 
                predictive_autoscale_policy: Optional[PredictiveAutoscalePolicy] = ..., 
                profiles: list[AutoscaleProfile], 
                tags: Optional[dict[str, str]] = ..., 
                target_resource_location: Optional[str] = ..., 
                target_resource_uri: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.AutoscaleSettingResourceCollection(Model):
        next_link: str
        value: list[AutoscaleSettingResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[AutoscaleSettingResource], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.AutoscaleSettingResourcePatch(Model):
        enabled: bool
        name: str
        notifications: list[AutoscaleNotification]
        predictive_autoscale_policy: PredictiveAutoscalePolicy
        profiles: list[AutoscaleProfile]
        tags: dict[str, str]
        target_resource_location: str
        target_resource_uri: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                enabled: bool = False, 
                name: Optional[str] = ..., 
                notifications: Optional[list[AutoscaleNotification]] = ..., 
                predictive_autoscale_policy: Optional[PredictiveAutoscalePolicy] = ..., 
                profiles: Optional[list[AutoscaleProfile]] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                target_resource_location: Optional[str] = ..., 
                target_resource_uri: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.AzureAppPushReceiver(Model):
        email_address: str
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                email_address: str, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.AzureFunctionReceiver(Model):
        function_app_resource_id: str
        function_name: str
        http_trigger_url: str
        name: str
        use_common_alert_schema: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                function_app_resource_id: str, 
                function_name: str, 
                http_trigger_url: str, 
                name: str, 
                use_common_alert_schema: bool = False, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.AzureMonitorMetricsDestination(Model):
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.AzureMonitorPrivateLinkScope(PrivateLinkScopesResource):
        id: str
        location: str
        name: str
        private_endpoint_connections: list[PrivateEndpointConnection]
        provisioning_state: str
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: str, 
                tags: Optional[dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.AzureMonitorPrivateLinkScopeListResult(Model):
        next_link: str
        value: list[AzureMonitorPrivateLinkScope]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[AzureMonitorPrivateLinkScope], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.AzureMonitorWorkspace(Model):
        account_id: str
        default_ingestion_settings: AzureMonitorWorkspaceDefaultIngestionSettings
        metrics: AzureMonitorWorkspaceMetrics
        private_endpoint_connections: list[PrivateEndpointConnectionAutoGenerated]
        provisioning_state: Union[str, ProvisioningState]
        public_network_access: Union[str, PublicNetworkAccess]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.AzureMonitorWorkspaceDefaultIngestionSettings(IngestionSettings):
        data_collection_endpoint_resource_id: str
        data_collection_rule_resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.AzureMonitorWorkspaceMetrics(Metrics):
        internal_id: str
        prometheus_query_endpoint: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.AzureMonitorWorkspaceResource(TrackedResource):
        account_id: str
        default_ingestion_settings: AzureMonitorWorkspaceDefaultIngestionSettings
        etag: str
        id: str
        location: str
        metrics: AzureMonitorWorkspaceMetrics
        name: str
        private_endpoint_connections: list[PrivateEndpointConnectionAutoGenerated]
        provisioning_state: Union[str, ProvisioningState]
        public_network_access: Union[str, PublicNetworkAccess]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: str, 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.AzureMonitorWorkspaceResourceForUpdate(Model):
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.AzureMonitorWorkspaceResourceListResult(Model):
        next_link: str
        value: list[AzureMonitorWorkspaceResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[AzureMonitorWorkspaceResource], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.AzureMonitorWorkspaceResourceProperties(AzureMonitorWorkspace):
        account_id: str
        default_ingestion_settings: AzureMonitorWorkspaceDefaultIngestionSettings
        metrics: AzureMonitorWorkspaceMetrics
        private_endpoint_connections: list[PrivateEndpointConnectionAutoGenerated]
        provisioning_state: Union[str, ProvisioningState]
        public_network_access: Union[str, PublicNetworkAccess]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.AzureResource(Model):
        id: str
        location: str
        name: str
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: str, 
                tags: Optional[dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.AzureResourceAutoGenerated(Model):
        id: str
        location: str
        name: str
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: str = "global", 
                tags: Optional[dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.BaselineMetadata(Model):
        name: str
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: str, 
                value: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.BaselineSensitivity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "High"
        LOW = "Low"
        MEDIUM = "Medium"


    class azure.mgmt.monitor.models.CategoryType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOGS = "Logs"
        METRICS = "Metrics"


    class azure.mgmt.monitor.models.ColumnDefinition(Model):
        name: str
        type: Union[str, KnownColumnDefinitionType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                type: Optional[Union[str, KnownColumnDefinitionType]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ComparisonOperationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EQUALS = "Equals"
        GREATER_THAN = "GreaterThan"
        GREATER_THAN_OR_EQUAL = "GreaterThanOrEqual"
        LESS_THAN = "LessThan"
        LESS_THAN_OR_EQUAL = "LessThanOrEqual"
        NOT_EQUALS = "NotEquals"


    class azure.mgmt.monitor.models.Condition(Model):
        dimensions: list[Dimension]
        failing_periods: ConditionFailingPeriods
        metric_measure_column: str
        metric_name: str
        operator: Union[str, ConditionOperator]
        query: str
        resource_id_column: str
        threshold: float
        time_aggregation: Union[str, TimeAggregation]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                dimensions: Optional[list[Dimension]] = ..., 
                failing_periods: Optional[ConditionFailingPeriods] = ..., 
                metric_measure_column: Optional[str] = ..., 
                metric_name: Optional[str] = ..., 
                operator: Optional[Union[str, ConditionOperator]] = ..., 
                query: Optional[str] = ..., 
                resource_id_column: Optional[str] = ..., 
                threshold: Optional[float] = ..., 
                time_aggregation: Optional[Union[str, TimeAggregation]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ConditionFailingPeriods(Model):
        min_failing_periods_to_alert: int
        number_of_evaluation_periods: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                min_failing_periods_to_alert: int = 1, 
                number_of_evaluation_periods: int = 1, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ConditionOperator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EQUALS = "Equals"
        GREATER_THAN = "GreaterThan"
        GREATER_THAN_OR_EQUAL = "GreaterThanOrEqual"
        LESS_THAN = "LessThan"
        LESS_THAN_OR_EQUAL = "LessThanOrEqual"


    class azure.mgmt.monitor.models.ConfigurationAccessEndpointSpec(Model):
        endpoint: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.Context(Model):
        context_type: str
        notification_source: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                context_type: Optional[str] = ..., 
                notification_source: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.monitor.models.CriterionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DYNAMIC_THRESHOLD_CRITERION = "DynamicThresholdCriterion"
        STATIC_THRESHOLD_CRITERION = "StaticThresholdCriterion"


    class azure.mgmt.monitor.models.DataCollectionEndpoint(Model):
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

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                configuration_access: Optional[DataCollectionEndpointConfigurationAccess] = ..., 
                description: Optional[str] = ..., 
                immutable_id: Optional[str] = ..., 
                logs_ingestion: Optional[DataCollectionEndpointLogsIngestion] = ..., 
                metrics_ingestion: Optional[DataCollectionEndpointMetricsIngestion] = ..., 
                network_acls: Optional[DataCollectionEndpointNetworkAcls] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.DataCollectionEndpointConfigurationAccess(ConfigurationAccessEndpointSpec):
        endpoint: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.DataCollectionEndpointFailoverConfiguration(FailoverConfigurationSpec):
        active_location: str
        locations: list[LocationSpec]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                active_location: Optional[str] = ..., 
                locations: Optional[list[LocationSpec]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.DataCollectionEndpointLogsIngestion(LogsIngestionEndpointSpec):
        endpoint: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.DataCollectionEndpointMetadata(Metadata):
        provisioned_by: str
        provisioned_by_immutable_id: str
        provisioned_by_resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.DataCollectionEndpointMetricsIngestion(MetricsIngestionEndpointSpec):
        endpoint: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.DataCollectionEndpointNetworkAcls(NetworkRuleSet):
        public_network_access: Union[str, KnownPublicNetworkAccessOptions]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                public_network_access: Optional[Union[str, KnownPublicNetworkAccessOptions]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.DataCollectionEndpointResource(Model):
        configuration_access: DataCollectionEndpointConfigurationAccess
        description: str
        etag: str
        failover_configuration: DataCollectionEndpointFailoverConfiguration
        id: str
        identity: DataCollectionEndpointResourceIdentity
        immutable_id: str
        kind: Union[str, KnownDataCollectionEndpointResourceKind]
        location: str
        logs_ingestion: DataCollectionEndpointLogsIngestion
        metadata: DataCollectionEndpointMetadata
        metrics_ingestion: DataCollectionEndpointMetricsIngestion
        name: str
        network_acls: DataCollectionEndpointNetworkAcls
        private_link_scoped_resources: list[PrivateLinkScopedResource]
        provisioning_state: Union[str, KnownDataCollectionEndpointProvisioningState]
        system_data: DataCollectionEndpointResourceSystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                configuration_access: Optional[DataCollectionEndpointConfigurationAccess] = ..., 
                description: Optional[str] = ..., 
                identity: Optional[DataCollectionEndpointResourceIdentity] = ..., 
                immutable_id: Optional[str] = ..., 
                kind: Optional[Union[str, KnownDataCollectionEndpointResourceKind]] = ..., 
                location: str, 
                logs_ingestion: Optional[DataCollectionEndpointLogsIngestion] = ..., 
                metrics_ingestion: Optional[DataCollectionEndpointMetricsIngestion] = ..., 
                network_acls: Optional[DataCollectionEndpointNetworkAcls] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.DataCollectionEndpointResourceIdentity(ManagedServiceIdentity):
        principal_id: str
        tenant_id: str
        type: Union[str, ManagedServiceIdentityType]
        user_assigned_identities: dict[str, UserAssignedIdentity]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                type: Union[str, ManagedServiceIdentityType], 
                user_assigned_identities: Optional[dict[str, UserAssignedIdentity]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.DataCollectionEndpointResourceListResult(Model):
        next_link: str
        value: list[DataCollectionEndpointResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[DataCollectionEndpointResource], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


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

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                configuration_access: Optional[DataCollectionEndpointConfigurationAccess] = ..., 
                description: Optional[str] = ..., 
                immutable_id: Optional[str] = ..., 
                logs_ingestion: Optional[DataCollectionEndpointLogsIngestion] = ..., 
                metrics_ingestion: Optional[DataCollectionEndpointMetricsIngestion] = ..., 
                network_acls: Optional[DataCollectionEndpointNetworkAcls] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.DataCollectionEndpointResourceSystemData(SystemData):
        created_at: datetime
        created_by: str
        created_by_type: Union[str, CreatedByType]
        last_modified_at: datetime
        last_modified_by: str
        last_modified_by_type: Union[str, CreatedByType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                created_at: Optional[datetime] = ..., 
                created_by: Optional[str] = ..., 
                created_by_type: Optional[Union[str, CreatedByType]] = ..., 
                last_modified_at: Optional[datetime] = ..., 
                last_modified_by: Optional[str] = ..., 
                last_modified_by_type: Optional[Union[str, CreatedByType]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.DataCollectionRule(Model):
        agent_settings: DataCollectionRuleAgentSettings
        data_collection_endpoint_id: str
        data_flows: list[DataFlow]
        data_sources: DataCollectionRuleDataSources
        description: str
        destinations: DataCollectionRuleDestinations
        endpoints: DataCollectionRuleEndpoints
        immutable_id: str
        metadata: DataCollectionRuleMetadata
        provisioning_state: Union[str, KnownDataCollectionRuleProvisioningState]
        references: DataCollectionRuleReferences
        stream_declarations: dict[str, StreamDeclaration]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                agent_settings: Optional[DataCollectionRuleAgentSettings] = ..., 
                data_collection_endpoint_id: Optional[str] = ..., 
                data_flows: Optional[list[DataFlow]] = ..., 
                data_sources: Optional[DataCollectionRuleDataSources] = ..., 
                description: Optional[str] = ..., 
                destinations: Optional[DataCollectionRuleDestinations] = ..., 
                references: Optional[DataCollectionRuleReferences] = ..., 
                stream_declarations: Optional[dict[str, StreamDeclaration]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.DataCollectionRuleAgentSettings(AgentSettingsSpec):
        logs: list[AgentSetting]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                logs: Optional[list[AgentSetting]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.DataCollectionRuleAssociation(Model):
        data_collection_endpoint_id: str
        data_collection_rule_id: str
        description: str
        metadata: DataCollectionRuleAssociationMetadata
        provisioning_state: Union[str, KnownDataCollectionRuleAssociationProvisioningState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                data_collection_endpoint_id: Optional[str] = ..., 
                data_collection_rule_id: Optional[str] = ..., 
                description: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.DataCollectionRuleAssociationMetadata(Metadata):
        provisioned_by: str
        provisioned_by_immutable_id: str
        provisioned_by_resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.DataCollectionRuleAssociationProxyOnlyResource(Model):
        data_collection_endpoint_id: str
        data_collection_rule_id: str
        description: str
        etag: str
        id: str
        metadata: DataCollectionRuleAssociationMetadata
        name: str
        provisioning_state: Union[str, KnownDataCollectionRuleAssociationProvisioningState]
        system_data: DataCollectionRuleAssociationProxyOnlyResourceSystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                data_collection_endpoint_id: Optional[str] = ..., 
                data_collection_rule_id: Optional[str] = ..., 
                description: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.DataCollectionRuleAssociationProxyOnlyResourceListResult(Model):
        next_link: str
        value: list[DataCollectionRuleAssociationProxyOnlyResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[DataCollectionRuleAssociationProxyOnlyResource], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.DataCollectionRuleAssociationProxyOnlyResourceProperties(DataCollectionRuleAssociation):
        data_collection_endpoint_id: str
        data_collection_rule_id: str
        description: str
        metadata: DataCollectionRuleAssociationMetadata
        provisioning_state: Union[str, KnownDataCollectionRuleAssociationProvisioningState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                data_collection_endpoint_id: Optional[str] = ..., 
                data_collection_rule_id: Optional[str] = ..., 
                description: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.DataCollectionRuleAssociationProxyOnlyResourceSystemData(SystemData):
        created_at: datetime
        created_by: str
        created_by_type: Union[str, CreatedByType]
        last_modified_at: datetime
        last_modified_by: str
        last_modified_by_type: Union[str, CreatedByType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                created_at: Optional[datetime] = ..., 
                created_by: Optional[str] = ..., 
                created_by_type: Optional[Union[str, CreatedByType]] = ..., 
                last_modified_at: Optional[datetime] = ..., 
                last_modified_by: Optional[str] = ..., 
                last_modified_by_type: Optional[Union[str, CreatedByType]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.DataCollectionRuleDataSources(DataSourcesSpec):
        data_imports: DataSourcesSpecDataImports
        extensions: list[ExtensionDataSource]
        iis_logs: list[IisLogsDataSource]
        log_files: list[LogFilesDataSource]
        performance_counters: list[PerfCounterDataSource]
        platform_telemetry: list[PlatformTelemetryDataSource]
        prometheus_forwarder: list[PrometheusForwarderDataSource]
        syslog: list[SyslogDataSource]
        windows_event_logs: list[WindowsEventLogDataSource]
        windows_firewall_logs: list[WindowsFirewallLogsDataSource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                data_imports: Optional[DataSourcesSpecDataImports] = ..., 
                extensions: Optional[list[ExtensionDataSource]] = ..., 
                iis_logs: Optional[list[IisLogsDataSource]] = ..., 
                log_files: Optional[list[LogFilesDataSource]] = ..., 
                performance_counters: Optional[list[PerfCounterDataSource]] = ..., 
                platform_telemetry: Optional[list[PlatformTelemetryDataSource]] = ..., 
                prometheus_forwarder: Optional[list[PrometheusForwarderDataSource]] = ..., 
                syslog: Optional[list[SyslogDataSource]] = ..., 
                windows_event_logs: Optional[list[WindowsEventLogDataSource]] = ..., 
                windows_firewall_logs: Optional[list[WindowsFirewallLogsDataSource]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


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

        def __eq__(self, other: Any) -> bool: ...

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
                storage_tables_direct: Optional[list[StorageTableDestination]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.DataCollectionRuleEndpoints(EndpointsSpec):
        logs_ingestion: str
        metrics_ingestion: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.DataCollectionRuleMetadata(Metadata):
        provisioned_by: str
        provisioned_by_immutable_id: str
        provisioned_by_resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.DataCollectionRuleReferences(ReferencesSpec):
        enrichment_data: ReferencesSpecEnrichmentData

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                enrichment_data: Optional[ReferencesSpecEnrichmentData] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.DataCollectionRuleResource(Model):
        agent_settings: DataCollectionRuleAgentSettings
        data_collection_endpoint_id: str
        data_flows: list[DataFlow]
        data_sources: DataCollectionRuleDataSources
        description: str
        destinations: DataCollectionRuleDestinations
        endpoints: DataCollectionRuleEndpoints
        etag: str
        id: str
        identity: DataCollectionRuleResourceIdentity
        immutable_id: str
        kind: Union[str, KnownDataCollectionRuleResourceKind]
        location: str
        metadata: DataCollectionRuleMetadata
        name: str
        provisioning_state: Union[str, KnownDataCollectionRuleProvisioningState]
        references: DataCollectionRuleReferences
        stream_declarations: dict[str, StreamDeclaration]
        system_data: DataCollectionRuleResourceSystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                agent_settings: Optional[DataCollectionRuleAgentSettings] = ..., 
                data_collection_endpoint_id: Optional[str] = ..., 
                data_flows: Optional[list[DataFlow]] = ..., 
                data_sources: Optional[DataCollectionRuleDataSources] = ..., 
                description: Optional[str] = ..., 
                destinations: Optional[DataCollectionRuleDestinations] = ..., 
                identity: Optional[DataCollectionRuleResourceIdentity] = ..., 
                kind: Optional[Union[str, KnownDataCollectionRuleResourceKind]] = ..., 
                location: str, 
                references: Optional[DataCollectionRuleReferences] = ..., 
                stream_declarations: Optional[dict[str, StreamDeclaration]] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.DataCollectionRuleResourceIdentity(ManagedServiceIdentity):
        principal_id: str
        tenant_id: str
        type: Union[str, ManagedServiceIdentityType]
        user_assigned_identities: dict[str, UserAssignedIdentity]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                type: Union[str, ManagedServiceIdentityType], 
                user_assigned_identities: Optional[dict[str, UserAssignedIdentity]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.DataCollectionRuleResourceListResult(Model):
        next_link: str
        value: list[DataCollectionRuleResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[DataCollectionRuleResource], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.DataCollectionRuleResourceProperties(DataCollectionRule):
        agent_settings: DataCollectionRuleAgentSettings
        data_collection_endpoint_id: str
        data_flows: list[DataFlow]
        data_sources: DataCollectionRuleDataSources
        description: str
        destinations: DataCollectionRuleDestinations
        endpoints: DataCollectionRuleEndpoints
        immutable_id: str
        metadata: DataCollectionRuleMetadata
        provisioning_state: Union[str, KnownDataCollectionRuleProvisioningState]
        references: DataCollectionRuleReferences
        stream_declarations: dict[str, StreamDeclaration]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                agent_settings: Optional[DataCollectionRuleAgentSettings] = ..., 
                data_collection_endpoint_id: Optional[str] = ..., 
                data_flows: Optional[list[DataFlow]] = ..., 
                data_sources: Optional[DataCollectionRuleDataSources] = ..., 
                description: Optional[str] = ..., 
                destinations: Optional[DataCollectionRuleDestinations] = ..., 
                references: Optional[DataCollectionRuleReferences] = ..., 
                stream_declarations: Optional[dict[str, StreamDeclaration]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.DataCollectionRuleResourceSystemData(SystemData):
        created_at: datetime
        created_by: str
        created_by_type: Union[str, CreatedByType]
        last_modified_at: datetime
        last_modified_by: str
        last_modified_by_type: Union[str, CreatedByType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                created_at: Optional[datetime] = ..., 
                created_by: Optional[str] = ..., 
                created_by_type: Optional[Union[str, CreatedByType]] = ..., 
                last_modified_at: Optional[datetime] = ..., 
                last_modified_by: Optional[str] = ..., 
                last_modified_by_type: Optional[Union[str, CreatedByType]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.DataContainer(Model):
        workspace: WorkspaceInfo

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                workspace: WorkspaceInfo, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.DataFlow(Model):
        built_in_transform: str
        capture_overflow: bool
        destinations: list[str]
        output_stream: str
        streams: Union[list[str, KnownDataFlowStreams]]
        transform_kql: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                built_in_transform: Optional[str] = ..., 
                capture_overflow: Optional[bool] = ..., 
                destinations: Optional[list[str]] = ..., 
                output_stream: Optional[str] = ..., 
                streams: Optional[list[Union[str, KnownDataFlowStreams]]] = ..., 
                transform_kql: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.DataImportSources(Model):
        event_hub: DataImportSourcesEventHub

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                event_hub: Optional[DataImportSourcesEventHub] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.DataImportSourcesEventHub(EventHubDataSource):
        consumer_group: str
        name: str
        stream: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                consumer_group: Optional[str] = ..., 
                name: Optional[str] = ..., 
                stream: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.DataSource(Model):
        configuration: DataSourceConfiguration
        kind: Union[str, DataSourceKind]
        sinks: list[SinkConfiguration]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                configuration: DataSourceConfiguration, 
                kind: Union[str, DataSourceKind], 
                sinks: list[SinkConfiguration], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.DataSourceConfiguration(Model):
        event_logs: list[EventLogConfiguration]
        perf_counters: list[PerformanceCounterConfiguration]
        providers: list[EtwProviderConfiguration]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                event_logs: Optional[list[EventLogConfiguration]] = ..., 
                perf_counters: Optional[list[PerformanceCounterConfiguration]] = ..., 
                providers: Optional[list[EtwProviderConfiguration]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.DataSourceKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ETW_PROVIDERS = "ETWProviders"
        PERFORMANCE_COUNTER = "PerformanceCounter"
        WINDOWS_EVENT_LOGS = "WindowsEventLogs"


    class azure.mgmt.monitor.models.DataSourcesSpec(Model):
        data_imports: DataSourcesSpecDataImports
        extensions: list[ExtensionDataSource]
        iis_logs: list[IisLogsDataSource]
        log_files: list[LogFilesDataSource]
        performance_counters: list[PerfCounterDataSource]
        platform_telemetry: list[PlatformTelemetryDataSource]
        prometheus_forwarder: list[PrometheusForwarderDataSource]
        syslog: list[SyslogDataSource]
        windows_event_logs: list[WindowsEventLogDataSource]
        windows_firewall_logs: list[WindowsFirewallLogsDataSource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                data_imports: Optional[DataSourcesSpecDataImports] = ..., 
                extensions: Optional[list[ExtensionDataSource]] = ..., 
                iis_logs: Optional[list[IisLogsDataSource]] = ..., 
                log_files: Optional[list[LogFilesDataSource]] = ..., 
                performance_counters: Optional[list[PerfCounterDataSource]] = ..., 
                platform_telemetry: Optional[list[PlatformTelemetryDataSource]] = ..., 
                prometheus_forwarder: Optional[list[PrometheusForwarderDataSource]] = ..., 
                syslog: Optional[list[SyslogDataSource]] = ..., 
                windows_event_logs: Optional[list[WindowsEventLogDataSource]] = ..., 
                windows_firewall_logs: Optional[list[WindowsFirewallLogsDataSource]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.DataSourcesSpecDataImports(DataImportSources):
        event_hub: DataImportSourcesEventHub

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                event_hub: Optional[DataImportSourcesEventHub] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.DataStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_PRESENT = "notPresent"
        PRESENT = "present"


    class azure.mgmt.monitor.models.DestinationsSpec(Model):
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

        def __eq__(self, other: Any) -> bool: ...

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
                storage_tables_direct: Optional[list[StorageTableDestination]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.DestinationsSpecAzureMonitorMetrics(AzureMonitorMetricsDestination):
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.DiagnosticSettingsCategoryResource(ProxyOnlyResource):
        category_type: Union[str, CategoryType]
        id: str
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                category_type: Optional[Union[str, CategoryType]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.DiagnosticSettingsCategoryResourceCollection(Model):
        value: list[DiagnosticSettingsCategoryResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[list[DiagnosticSettingsCategoryResource]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.DiagnosticSettingsResource(ResourceAutoGenerated):
        event_hub_authorization_rule_id: str
        event_hub_name: str
        id: str
        log_analytics_destination_type: str
        logs: list[LogSettings]
        marketplace_partner_id: str
        metrics: list[MetricSettings]
        name: str
        service_bus_rule_id: str
        storage_account_id: str
        system_data: SystemData
        type: str
        workspace_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                event_hub_authorization_rule_id: Optional[str] = ..., 
                event_hub_name: Optional[str] = ..., 
                log_analytics_destination_type: Optional[str] = ..., 
                logs: Optional[list[LogSettings]] = ..., 
                marketplace_partner_id: Optional[str] = ..., 
                metrics: Optional[list[MetricSettings]] = ..., 
                service_bus_rule_id: Optional[str] = ..., 
                storage_account_id: Optional[str] = ..., 
                workspace_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.DiagnosticSettingsResourceCollection(Model):
        value: list[DiagnosticSettingsResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[list[DiagnosticSettingsResource]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.Dimension(Model):
        name: str
        operator: Union[str, DimensionOperator]
        values: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: str, 
                operator: Union[str, DimensionOperator], 
                values: list[str], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.DimensionOperator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXCLUDE = "Exclude"
        INCLUDE = "Include"


    class azure.mgmt.monitor.models.DynamicMetricCriteria(MultiMetricCriteria):
        additional_properties: dict[str, JSON]
        alert_sensitivity: Union[str, DynamicThresholdSensitivity]
        criterion_type: Union[str, CriterionType]
        dimensions: list[MetricDimension]
        failing_periods: DynamicThresholdFailingPeriods
        ignore_data_before: datetime
        metric_name: str
        metric_namespace: str
        name: str
        operator: Union[str, DynamicThresholdOperator]
        skip_metric_validation: bool
        time_aggregation: Union[str, AggregationTypeEnum]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_properties: Optional[dict[str, JSON]] = ..., 
                alert_sensitivity: Union[str, DynamicThresholdSensitivity], 
                dimensions: Optional[list[MetricDimension]] = ..., 
                failing_periods: DynamicThresholdFailingPeriods, 
                ignore_data_before: Optional[datetime] = ..., 
                metric_name: str, 
                metric_namespace: Optional[str] = ..., 
                name: str, 
                operator: Union[str, DynamicThresholdOperator], 
                skip_metric_validation: Optional[bool] = ..., 
                time_aggregation: Union[str, AggregationTypeEnum], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.DynamicPromQLCriteria(MultiPromQLCriteria):
        alert_sensitivity: Union[str, DynamicThresholdSensitivity]
        criterion_type: Union[str, CriterionType]
        ignore_data_before: datetime
        name: str
        operator: Union[str, DynamicThresholdOperator]
        query: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                alert_sensitivity: Union[str, DynamicThresholdSensitivity], 
                ignore_data_before: Optional[datetime] = ..., 
                name: str, 
                operator: Union[str, DynamicThresholdOperator], 
                query: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.DynamicThresholdFailingPeriods(Model):
        min_failing_periods_to_alert: float
        number_of_evaluation_periods: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                min_failing_periods_to_alert: float, 
                number_of_evaluation_periods: float, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.DynamicThresholdOperator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GREATER_OR_LESS_THAN = "GreaterOrLessThan"
        GREATER_THAN = "GreaterThan"
        LESS_THAN = "LessThan"


    class azure.mgmt.monitor.models.DynamicThresholdSensitivity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "High"
        LOW = "Low"
        MEDIUM = "Medium"


    class azure.mgmt.monitor.models.EmailNotification(Model):
        custom_emails: list[str]
        send_to_subscription_administrator: bool
        send_to_subscription_co_administrators: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                custom_emails: Optional[list[str]] = ..., 
                send_to_subscription_administrator: bool = False, 
                send_to_subscription_co_administrators: bool = False, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.EmailReceiver(Model):
        email_address: str
        name: str
        status: Union[str, ReceiverStatus]
        use_common_alert_schema: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                email_address: str, 
                name: str, 
                use_common_alert_schema: bool = False, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.EnableRequest(Model):
        receiver_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                receiver_name: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.EndpointsSpec(Model):
        logs_ingestion: str
        metrics_ingestion: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.EnrichmentData(Model):
        storage_blobs: list[StorageBlob]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                storage_blobs: Optional[list[StorageBlob]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.Error(Model):
        code: str
        message: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                code: str, 
                message: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ErrorAdditionalInfo(Model):
        info: JSON
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ErrorContract(Model):
        error: ErrorResponseAutoGenerated4

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error: Optional[ErrorResponseAutoGenerated4] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ErrorDetail(Model):
        additional_info: list[ErrorDetailAdditionalInfoItem]
        code: str
        message: str
        target: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_info: Optional[list[ErrorDetailAdditionalInfoItem]] = ..., 
                code: Optional[str] = ..., 
                message: Optional[str] = ..., 
                target: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ErrorDetailAdditionalInfoItem(Model):
        info: dict[str, any]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                info: Optional[dict[str, Any]] = ..., 
                type: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ErrorDetailAdditionalInfoItemAutoGenerated(Model):
        info: dict[str, any]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                info: Optional[dict[str, Any]] = ..., 
                type: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ErrorDetailAutoGenerated(Model):
        additional_info: list[ErrorDetailAdditionalInfoItemAutoGenerated]
        code: str
        message: str
        target: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_info: Optional[list[ErrorDetailAdditionalInfoItemAutoGenerated]] = ..., 
                code: Optional[str] = ..., 
                message: Optional[str] = ..., 
                target: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ErrorDetailAutoGenerated2(Model):
        additional_info: list[ErrorAdditionalInfo]
        code: str
        details: list[ErrorDetailAutoGenerated2]
        message: str
        target: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ErrorDetailAutoGenerated3(Model):
        additional_info: list[ErrorAdditionalInfo]
        code: str
        details: list[ErrorDetailAutoGenerated3]
        message: str
        target: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ErrorResponse(Model):
        code: str
        message: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                message: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ErrorResponseAutoGenerated(Model):
        code: str
        message: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ErrorResponseAutoGenerated2(Model):
        error: ErrorResponseError

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error: Optional[ErrorResponseError] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ErrorResponseAutoGenerated3(Model):
        error: ErrorResponseErrorAutoGenerated

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error: Optional[ErrorResponseErrorAutoGenerated] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ErrorResponseAutoGenerated4(Model):
        additional_info: list[ErrorAdditionalInfo]
        code: str
        details: list[ErrorResponseAutoGenerated4]
        message: str
        target: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ErrorResponseAutoGenerated5(Model):
        error: ErrorDetailAutoGenerated2

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetailAutoGenerated2] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ErrorResponseCommon(ErrorResponse):
        additional_info: list[ErrorAdditionalInfo]
        code: str
        details: list[ErrorResponseCommon]
        message: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                message: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ErrorResponseCommonV2(Model):
        error: ErrorDetailAutoGenerated3

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetailAutoGenerated3] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ErrorResponseError(Model):
        additional_info: list[ErrorResponseErrorAdditionalInfoItem]
        code: str
        details: list[ErrorDetail]
        message: str
        target: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_info: Optional[list[ErrorResponseErrorAdditionalInfoItem]] = ..., 
                code: Optional[str] = ..., 
                details: Optional[list[ErrorDetail]] = ..., 
                message: Optional[str] = ..., 
                target: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ErrorResponseErrorAdditionalInfoItem(Model):
        info: dict[str, any]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                info: Optional[dict[str, Any]] = ..., 
                type: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ErrorResponseErrorAdditionalInfoItemAutoGenerated(Model):
        info: dict[str, any]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                info: Optional[dict[str, Any]] = ..., 
                type: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ErrorResponseErrorAutoGenerated(Model):
        additional_info: list[ErrorResponseErrorAdditionalInfoItemAutoGenerated]
        code: str
        details: list[ErrorDetailAutoGenerated]
        message: str
        target: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_info: Optional[list[ErrorResponseErrorAdditionalInfoItemAutoGenerated]] = ..., 
                code: Optional[str] = ..., 
                details: Optional[list[ErrorDetailAutoGenerated]] = ..., 
                message: Optional[str] = ..., 
                target: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.EtwEventConfiguration(Model):
        filter: str
        id: int
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                filter: Optional[str] = ..., 
                id: int, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.EtwProviderConfiguration(Model):
        events: list[EtwEventConfiguration]
        id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                events: list[EtwEventConfiguration], 
                id: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.EventCategoryCollection(Model):
        value: list[LocalizableString]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: list[LocalizableString], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.EventData(Model):
        authorization: SenderAuthorization
        caller: str
        category: LocalizableString
        claims: dict[str, str]
        correlation_id: str
        description: str
        event_data_id: str
        event_name: LocalizableString
        event_timestamp: datetime
        http_request: HttpRequestInfo
        id: str
        level: Union[str, EventLevel]
        operation_id: str
        operation_name: LocalizableString
        properties: dict[str, str]
        resource_group_name: str
        resource_id: str
        resource_provider_name: LocalizableString
        resource_type: LocalizableString
        status: LocalizableString
        sub_status: LocalizableString
        submission_timestamp: datetime
        subscription_id: str
        tenant_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.EventDataCollection(Model):
        next_link: str
        value: list[EventData]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[EventData], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.EventHubDataSource(Model):
        consumer_group: str
        name: str
        stream: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                consumer_group: Optional[str] = ..., 
                name: Optional[str] = ..., 
                stream: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.EventHubDestination(Model):
        event_hub_resource_id: str
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                event_hub_resource_id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.EventHubDirectDestination(Model):
        event_hub_resource_id: str
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                event_hub_resource_id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.EventHubReceiver(Model):
        event_hub_name: str
        event_hub_name_space: str
        name: str
        subscription_id: str
        tenant_id: str
        use_common_alert_schema: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                event_hub_name: str, 
                event_hub_name_space: str, 
                name: str, 
                subscription_id: str, 
                tenant_id: Optional[str] = ..., 
                use_common_alert_schema: bool = False, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.EventLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CRITICAL = "Critical"
        ERROR = "Error"
        INFORMATIONAL = "Informational"
        VERBOSE = "Verbose"
        WARNING = "Warning"


    class azure.mgmt.monitor.models.EventLogConfiguration(Model):
        filter: str
        log_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                filter: Optional[str] = ..., 
                log_name: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ExtensionDataSource(Model):
        extension_name: str
        extension_settings: JSON
        input_data_sources: list[str]
        name: str
        streams: Union[list[str, KnownExtensionDataSourceStreams]]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                extension_name: str, 
                extension_settings: Optional[JSON] = ..., 
                input_data_sources: Optional[list[str]] = ..., 
                name: Optional[str] = ..., 
                streams: Optional[list[Union[str, KnownExtensionDataSourceStreams]]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.FailoverConfigurationSpec(Model):
        active_location: str
        locations: list[LocationSpec]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                active_location: Optional[str] = ..., 
                locations: Optional[list[LocationSpec]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.GuestDiagnosticSettingsAssociationList(Model):
        next_link: str
        value: list[GuestDiagnosticSettingsAssociationResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[list[GuestDiagnosticSettingsAssociationResource]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.GuestDiagnosticSettingsAssociationResource(ResourceAutoGenerated3):
        guest_diagnostic_settings_name: str
        id: str
        location: str
        name: str
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                guest_diagnostic_settings_name: str, 
                location: str, 
                tags: Optional[dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.GuestDiagnosticSettingsAssociationResourcePatch(Model):
        guest_diagnostic_settings_name: str
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                guest_diagnostic_settings_name: Optional[str] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.GuestDiagnosticSettingsList(Model):
        next_link: str
        value: list[GuestDiagnosticSettingsResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[list[GuestDiagnosticSettingsResource]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.GuestDiagnosticSettingsOsType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LINUX = "Linux"
        WINDOWS = "Windows"


    class azure.mgmt.monitor.models.GuestDiagnosticSettingsPatchResource(Model):
        data_sources: list[DataSource]
        os_type: Union[str, GuestDiagnosticSettingsOsType]
        proxy_setting: str
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                data_sources: Optional[list[DataSource]] = ..., 
                os_type: Optional[Union[str, GuestDiagnosticSettingsOsType]] = ..., 
                proxy_setting: Optional[str] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.GuestDiagnosticSettingsResource(ResourceAutoGenerated2):
        data_sources: list[DataSource]
        id: str
        location: str
        name: str
        os_type: Union[str, GuestDiagnosticSettingsOsType]
        proxy_setting: str
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                data_sources: Optional[list[DataSource]] = ..., 
                location: str, 
                os_type: Optional[Union[str, GuestDiagnosticSettingsOsType]] = ..., 
                proxy_setting: Optional[str] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.HttpRequestInfo(Model):
        client_ip_address: str
        client_request_id: str
        method: str
        uri: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                client_ip_address: Optional[str] = ..., 
                client_request_id: Optional[str] = ..., 
                method: Optional[str] = ..., 
                uri: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.Identity(Model):
        principal_id: str
        tenant_id: str
        type: Union[str, IdentityType]
        user_assigned_identities: dict[str, UserIdentityProperties]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                type: Union[str, IdentityType], 
                user_assigned_identities: Optional[dict[str, UserIdentityProperties]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.IdentityAutoGenerated(Model):
        principal_id: str
        tenant_id: str
        type: Union[str, IdentityType]
        user_assigned_identities: dict[str, UserIdentityPropertiesAutoGenerated]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                type: Union[str, IdentityType], 
                user_assigned_identities: Optional[dict[str, UserIdentityPropertiesAutoGenerated]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.IdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.monitor.models.IisLogsDataSource(Model):
        log_directories: list[str]
        name: str
        streams: list[str]
        transform_kql: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                log_directories: Optional[list[str]] = ..., 
                name: Optional[str] = ..., 
                streams: list[str], 
                transform_kql: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.Incident(Model):
        activated_time: datetime
        is_active: bool
        name: str
        resolved_time: datetime
        rule_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.IncidentListResult(Model):
        value: list[Incident]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[list[Incident]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.IngestionSettings(Model):
        data_collection_endpoint_resource_id: str
        data_collection_rule_resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ItsmReceiver(Model):
        connection_id: str
        name: str
        region: str
        ticket_configuration: str
        workspace_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                connection_id: str, 
                name: str, 
                region: str, 
                ticket_configuration: str, 
                workspace_id: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.Kind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOG_ALERT = "LogAlert"
        LOG_TO_METRIC = "LogToMetric"


    class azure.mgmt.monitor.models.KnownAgentSettingName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MAX_DISK_QUOTA_IN_MB = "MaxDiskQuotaInMB"
        USE_TIME_RECEIVED_FOR_FORWARDED_EVENTS = "UseTimeReceivedForForwardedEvents"


    class azure.mgmt.monitor.models.KnownColumnDefinitionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BOOLEAN = "boolean"
        DATETIME = "datetime"
        DYNAMIC = "dynamic"
        INT = "int"
        INT_ENUM = "int"
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


    class azure.mgmt.monitor.models.KnownPerfCounterDataSourceStreams(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MICROSOFT_INSIGHTS_METRICS = "Microsoft-InsightsMetrics"
        MICROSOFT_PERF = "Microsoft-Perf"


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


    class azure.mgmt.monitor.models.LocalizableString(Model):
        localized_value: str
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                localized_value: Optional[str] = ..., 
                value: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.LocalizableStringAutoGenerated(Model):
        localized_value: str
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                localized_value: Optional[str] = ..., 
                value: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.LocationSpec(Model):
        location: str
        provisioning_status: Union[str, KnownLocationSpecProvisioningStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                provisioning_status: Optional[Union[str, KnownLocationSpecProvisioningStatus]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.LogAnalyticsDestination(Model):
        name: str
        workspace_id: str
        workspace_resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                workspace_resource_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.LogFileSettings(Model):
        text: LogFileSettingsText

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                text: Optional[LogFileSettingsText] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.LogFileSettingsText(LogFileTextSettings):
        record_start_timestamp_format: Union[str, KnownLogFileTextSettingsRecordStartTimestampFormat]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                record_start_timestamp_format: Union[str, KnownLogFileTextSettingsRecordStartTimestampFormat], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.LogFileTextSettings(Model):
        record_start_timestamp_format: Union[str, KnownLogFileTextSettingsRecordStartTimestampFormat]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                record_start_timestamp_format: Union[str, KnownLogFileTextSettingsRecordStartTimestampFormat], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.LogFilesDataSource(Model):
        file_patterns: list[str]
        format: Union[str, KnownLogFilesDataSourceFormat]
        name: str
        settings: LogFilesDataSourceSettings
        streams: list[str]
        transform_kql: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                file_patterns: list[str], 
                format: Union[str, KnownLogFilesDataSourceFormat], 
                name: Optional[str] = ..., 
                settings: Optional[LogFilesDataSourceSettings] = ..., 
                streams: list[str], 
                transform_kql: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.LogFilesDataSourceSettings(LogFileSettings):
        text: LogFileSettingsText

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                text: Optional[LogFileSettingsText] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.LogProfileCollection(Model):
        value: list[LogProfileResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: list[LogProfileResource], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.LogProfileResource(ResourceAutoGenerated4):
        categories: list[str]
        id: str
        location: str
        locations: list[str]
        name: str
        retention_policy: RetentionPolicy
        service_bus_rule_id: str
        storage_account_id: str
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                categories: list[str], 
                location: str, 
                locations: list[str], 
                retention_policy: RetentionPolicy, 
                service_bus_rule_id: Optional[str] = ..., 
                storage_account_id: Optional[str] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.LogProfileResourcePatch(Model):
        categories: list[str]
        locations: list[str]
        retention_policy: RetentionPolicy
        service_bus_rule_id: str
        storage_account_id: str
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                categories: Optional[list[str]] = ..., 
                locations: Optional[list[str]] = ..., 
                retention_policy: Optional[RetentionPolicy] = ..., 
                service_bus_rule_id: Optional[str] = ..., 
                storage_account_id: Optional[str] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.LogSettings(Model):
        category: str
        category_group: str
        enabled: bool
        retention_policy: RetentionPolicy

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                category: Optional[str] = ..., 
                category_group: Optional[str] = ..., 
                enabled: bool, 
                retention_policy: Optional[RetentionPolicy] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.LogSettingsAutoGenerated(Model):
        category: str
        enabled: bool
        retention_policy: RetentionPolicy

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                category: Optional[str] = ..., 
                enabled: bool, 
                retention_policy: Optional[RetentionPolicy] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.LogicAppReceiver(Model):
        callback_url: str
        name: str
        resource_id: str
        use_common_alert_schema: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                callback_url: str, 
                name: str, 
                resource_id: str, 
                use_common_alert_schema: bool = False, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.LogsIngestionEndpointSpec(Model):
        endpoint: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ManagedServiceIdentity(Model):
        principal_id: str
        tenant_id: str
        type: Union[str, ManagedServiceIdentityType]
        user_assigned_identities: dict[str, UserAssignedIdentity]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                type: Union[str, ManagedServiceIdentityType], 
                user_assigned_identities: Optional[dict[str, UserAssignedIdentity]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.monitor.models.Metadata(Model):
        provisioned_by: str
        provisioned_by_immutable_id: str
        provisioned_by_resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.MetadataValue(Model):
        name: LocalizableStringAutoGenerated
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[LocalizableStringAutoGenerated] = ..., 
                value: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.Metric(Model):
        display_description: str
        error_code: str
        error_message: str
        id: str
        name: LocalizableStringAutoGenerated
        timeseries: list[TimeSeriesElement]
        type: str
        unit: Union[str, MetricUnit]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display_description: Optional[str] = ..., 
                error_code: Optional[str] = ..., 
                error_message: Optional[str] = ..., 
                id: str, 
                name: LocalizableStringAutoGenerated, 
                timeseries: list[TimeSeriesElement], 
                type: str, 
                unit: Union[str, MetricUnit], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.MetricAggregationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVERAGE = "Average"
        COUNT = "Count"
        MAXIMUM = "Maximum"
        MINIMUM = "Minimum"
        NONE = "None"
        TOTAL = "Total"


    class azure.mgmt.monitor.models.MetricAlertAction(Model):
        action_group_id: str
        web_hook_properties: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                action_group_id: Optional[str] = ..., 
                web_hook_properties: Optional[dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.MetricAlertCriteria(Model):
        additional_properties: dict[str, JSON]
        odata_type: Union[str, Odatatype]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_properties: Optional[dict[str, JSON]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.MetricAlertMultipleResourceMultipleMetricCriteria(MetricAlertCriteria):
        additional_properties: dict[str, JSON]
        all_of: list[MultiMetricCriteria]
        odata_type: Union[str, Odatatype]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_properties: Optional[dict[str, JSON]] = ..., 
                all_of: Optional[list[MultiMetricCriteria]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.MetricAlertResource(ResourceAutoGenerated5):
        action_properties: dict[str, str]
        actions: list[MetricAlertAction]
        auto_mitigate: bool
        criteria: MetricAlertCriteria
        custom_properties: dict[str, str]
        description: str
        enabled: bool
        evaluation_frequency: timedelta
        id: str
        identity: Identity
        is_migrated: bool
        last_updated_time: datetime
        location: str
        name: str
        resolve_configuration: ResolveConfiguration
        scopes: list[str]
        severity: int
        tags: dict[str, str]
        target_resource_region: str
        target_resource_type: str
        type: str
        window_size: timedelta

        def __eq__(self, other: Any) -> bool: ...

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
                identity: Optional[Identity] = ..., 
                location: str, 
                resolve_configuration: Optional[ResolveConfiguration] = ..., 
                scopes: list[str], 
                severity: int, 
                tags: Optional[dict[str, str]] = ..., 
                target_resource_region: Optional[str] = ..., 
                target_resource_type: Optional[str] = ..., 
                window_size: Optional[timedelta] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.MetricAlertResourceCollection(Model):
        value: list[MetricAlertResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[list[MetricAlertResource]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.MetricAlertResourcePatch(Model):
        action_properties: dict[str, str]
        actions: list[MetricAlertAction]
        auto_mitigate: bool
        criteria: MetricAlertCriteria
        custom_properties: dict[str, str]
        description: str
        enabled: bool
        evaluation_frequency: timedelta
        identity: Identity
        is_migrated: bool
        last_updated_time: datetime
        resolve_configuration: ResolveConfiguration
        scopes: list[str]
        severity: int
        tags: dict[str, str]
        target_resource_region: str
        target_resource_type: str
        window_size: timedelta

        def __eq__(self, other: Any) -> bool: ...

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
                identity: Optional[Identity] = ..., 
                resolve_configuration: Optional[ResolveConfiguration] = ..., 
                scopes: Optional[list[str]] = ..., 
                severity: Optional[int] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                target_resource_region: Optional[str] = ..., 
                target_resource_type: Optional[str] = ..., 
                window_size: Optional[timedelta] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.MetricAlertSingleResourceMultipleMetricCriteria(MetricAlertCriteria):
        additional_properties: dict[str, JSON]
        all_of: list[MetricCriteria]
        odata_type: Union[str, Odatatype]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_properties: Optional[dict[str, JSON]] = ..., 
                all_of: Optional[list[MetricCriteria]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.MetricAlertStatus(Model):
        id: str
        name: str
        properties: MetricAlertStatusProperties
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[MetricAlertStatusProperties] = ..., 
                type: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.MetricAlertStatusCollection(Model):
        value: list[MetricAlertStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[list[MetricAlertStatus]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.MetricAlertStatusProperties(Model):
        dimensions: dict[str, str]
        status: str
        timestamp: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                dimensions: Optional[dict[str, str]] = ..., 
                status: Optional[str] = ..., 
                timestamp: Optional[datetime] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.MetricAvailability(Model):
        retention: timedelta
        time_grain: timedelta

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                retention: Optional[timedelta] = ..., 
                time_grain: Optional[timedelta] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.MetricBaselinesResponse(Model):
        value: list[SingleMetricBaseline]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[list[SingleMetricBaseline]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.MetricClass(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABILITY = "Availability"
        ERRORS = "Errors"
        LATENCY = "Latency"
        SATURATION = "Saturation"
        TRANSACTIONS = "Transactions"


    class azure.mgmt.monitor.models.MetricCriteria(MultiMetricCriteria):
        additional_properties: dict[str, JSON]
        criterion_type: Union[str, CriterionType]
        dimensions: list[MetricDimension]
        metric_name: str
        metric_namespace: str
        name: str
        operator: Union[str, Operator]
        skip_metric_validation: bool
        threshold: float
        time_aggregation: Union[str, AggregationTypeEnum]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_properties: Optional[dict[str, JSON]] = ..., 
                dimensions: Optional[list[MetricDimension]] = ..., 
                metric_name: str, 
                metric_namespace: Optional[str] = ..., 
                name: str, 
                operator: Union[str, Operator], 
                skip_metric_validation: Optional[bool] = ..., 
                threshold: float, 
                time_aggregation: Union[str, AggregationTypeEnum], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.MetricDefinition(Model):
        category: str
        dimensions: list[LocalizableStringAutoGenerated]
        display_description: str
        id: str
        is_dimension_required: bool
        metric_availabilities: list[MetricAvailability]
        metric_class: Union[str, MetricClass]
        name: LocalizableStringAutoGenerated
        namespace: str
        primary_aggregation_type: Union[str, AggregationType]
        resource_id: str
        supported_aggregation_types: Union[list[str, AggregationType]]
        unit: Union[str, MetricUnit]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                category: Optional[str] = ..., 
                dimensions: Optional[list[LocalizableStringAutoGenerated]] = ..., 
                display_description: Optional[str] = ..., 
                id: Optional[str] = ..., 
                is_dimension_required: Optional[bool] = ..., 
                metric_availabilities: Optional[list[MetricAvailability]] = ..., 
                metric_class: Optional[Union[str, MetricClass]] = ..., 
                name: Optional[LocalizableStringAutoGenerated] = ..., 
                namespace: Optional[str] = ..., 
                primary_aggregation_type: Optional[Union[str, AggregationType]] = ..., 
                resource_id: Optional[str] = ..., 
                supported_aggregation_types: Optional[list[Union[str, AggregationType]]] = ..., 
                unit: Optional[Union[str, MetricUnit]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.MetricDefinitionCollection(Model):
        value: list[MetricDefinition]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: list[MetricDefinition], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.MetricDimension(Model):
        name: str
        operator: str
        values: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: str, 
                operator: str, 
                values: list[str], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.MetricNamespace(Model):
        classification: Union[str, NamespaceClassification]
        id: str
        name: str
        properties: MetricNamespaceName
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                classification: Optional[Union[str, NamespaceClassification]] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[MetricNamespaceName] = ..., 
                type: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.MetricNamespaceCollection(Model):
        value: list[MetricNamespace]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: list[MetricNamespace], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.MetricNamespaceName(Model):
        metric_namespace_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                metric_namespace_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.MetricResultType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DATA = "Data"
        METADATA = "Metadata"


    class azure.mgmt.monitor.models.MetricSettings(Model):
        category: str
        enabled: bool
        retention_policy: RetentionPolicy
        time_grain: timedelta

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                category: Optional[str] = ..., 
                enabled: bool, 
                retention_policy: Optional[RetentionPolicy] = ..., 
                time_grain: Optional[timedelta] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.MetricSettingsAutoGenerated(Model):
        enabled: bool
        retention_policy: RetentionPolicy
        time_grain: timedelta

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                enabled: bool, 
                retention_policy: Optional[RetentionPolicy] = ..., 
                time_grain: timedelta, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.MetricSingleDimension(Model):
        name: str
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: str, 
                value: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.MetricStatisticType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVERAGE = "Average"
        COUNT = "Count"
        MAX = "Max"
        MIN = "Min"
        SUM = "Sum"


    class azure.mgmt.monitor.models.MetricTrigger(Model):
        dimensions: list[ScaleRuleMetricDimension]
        divide_per_instance: bool
        metric_name: str
        metric_namespace: str
        metric_resource_location: str
        metric_resource_uri: str
        operator: Union[str, ComparisonOperationType]
        statistic: Union[str, MetricStatisticType]
        threshold: float
        time_aggregation: Union[str, TimeAggregationType]
        time_grain: timedelta
        time_window: timedelta

        def __eq__(self, other: Any) -> bool: ...

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
                time_window: timedelta, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


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


    class azure.mgmt.monitor.models.MetricValue(Model):
        average: float
        count: float
        maximum: float
        minimum: float
        time_stamp: datetime
        total: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                average: Optional[float] = ..., 
                count: Optional[float] = ..., 
                maximum: Optional[float] = ..., 
                minimum: Optional[float] = ..., 
                time_stamp: datetime, 
                total: Optional[float] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.Metrics(Model):
        internal_id: str
        prometheus_query_endpoint: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.MetricsIngestionEndpointSpec(Model):
        endpoint: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.MicrosoftFabricDestination(Model):
        artifact_id: str
        database_name: str
        ingestion_uri: str
        name: str
        tenant_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                artifact_id: Optional[str] = ..., 
                database_name: Optional[str] = ..., 
                ingestion_uri: Optional[str] = ..., 
                name: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.MonitoringAccountDestination(Model):
        account_id: str
        account_resource_id: str
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                account_resource_id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.MultiMetricCriteria(Model):
        additional_properties: dict[str, JSON]
        criterion_type: Union[str, CriterionType]
        dimensions: list[MetricDimension]
        metric_name: str
        metric_namespace: str
        name: str
        skip_metric_validation: bool
        time_aggregation: Union[str, AggregationTypeEnum]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_properties: Optional[dict[str, JSON]] = ..., 
                dimensions: Optional[list[MetricDimension]] = ..., 
                metric_name: str, 
                metric_namespace: Optional[str] = ..., 
                name: str, 
                skip_metric_validation: Optional[bool] = ..., 
                time_aggregation: Union[str, AggregationTypeEnum], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.MultiPromQLCriteria(Model):
        criterion_type: Union[str, CriterionType]
        name: str
        query: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: str, 
                query: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.NamespaceClassification(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM = "Custom"
        PLATFORM = "Platform"
        QOS = "Qos"


    class azure.mgmt.monitor.models.NetworkRuleSet(Model):
        public_network_access: Union[str, KnownPublicNetworkAccessOptions]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                public_network_access: Optional[Union[str, KnownPublicNetworkAccessOptions]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.NotificationRequestBody(Model):
        alert_type: str
        arm_role_receivers: list[ArmRoleReceiver]
        automation_runbook_receivers: list[AutomationRunbookReceiver]
        azure_app_push_receivers: list[AzureAppPushReceiver]
        azure_function_receivers: list[AzureFunctionReceiver]
        email_receivers: list[EmailReceiver]
        event_hub_receivers: list[EventHubReceiver]
        itsm_receivers: list[ItsmReceiver]
        logic_app_receivers: list[LogicAppReceiver]
        sms_receivers: list[SmsReceiver]
        voice_receivers: list[VoiceReceiver]
        webhook_receivers: list[WebhookReceiver]

        def __eq__(self, other: Any) -> bool: ...

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
                itsm_receivers: Optional[list[ItsmReceiver]] = ..., 
                logic_app_receivers: Optional[list[LogicAppReceiver]] = ..., 
                sms_receivers: Optional[list[SmsReceiver]] = ..., 
                voice_receivers: Optional[list[VoiceReceiver]] = ..., 
                webhook_receivers: Optional[list[WebhookReceiver]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.Odatatype(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MICROSOFT_AZURE_MONITOR_MULTIPLE_RESOURCE_MULTIPLE_METRIC_CRITERIA = "Microsoft.Azure.Monitor.MultipleResourceMultipleMetricCriteria"
        MICROSOFT_AZURE_MONITOR_PROM_QL_CRITERIA = "Microsoft.Azure.Monitor.PromQLCriteria"
        MICROSOFT_AZURE_MONITOR_SINGLE_RESOURCE_MULTIPLE_METRIC_CRITERIA = "Microsoft.Azure.Monitor.SingleResourceMultipleMetricCriteria"
        MICROSOFT_AZURE_MONITOR_WEBTEST_LOCATION_AVAILABILITY_CRITERIA = "Microsoft.Azure.Monitor.WebtestLocationAvailabilityCriteria"


    class azure.mgmt.monitor.models.OnboardingStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_ONBOARDED = "notOnboarded"
        ONBOARDED = "onboarded"
        UNKNOWN = "unknown"


    class azure.mgmt.monitor.models.Operation(Model):
        display: OperationDisplay
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
                name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.OperationAutoGenerated(Model):
        action_type: Union[str, ActionType]
        display: OperationDisplayAutoGenerated
        is_data_action: bool
        name: str
        origin: Union[str, Origin]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplayAutoGenerated] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.OperationDisplay(Model):
        operation: str
        provider: str
        resource: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                operation: Optional[str] = ..., 
                provider: Optional[str] = ..., 
                resource: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.OperationDisplayAutoGenerated(Model):
        description: str
        operation: str
        provider: str
        resource: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.OperationListResult(Model):
        next_link: str
        value: list[Operation]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[list[Operation]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.OperationListResultAutoGenerated(Model):
        next_link: str
        value: list[OperationAutoGenerated]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.OperationStatus(Model):
        end_time: datetime
        error: ErrorResponseCommon
        id: str
        name: str
        start_time: datetime
        status: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                error: Optional[ErrorResponseCommon] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                start_time: Optional[datetime] = ..., 
                status: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.Operator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EQUALS = "Equals"
        GREATER_THAN = "GreaterThan"
        GREATER_THAN_OR_EQUAL = "GreaterThanOrEqual"
        LESS_THAN = "LessThan"
        LESS_THAN_OR_EQUAL = "LessThanOrEqual"


    class azure.mgmt.monitor.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.monitor.models.PerfCounterDataSource(Model):
        counter_specifiers: list[str]
        name: str
        sampling_frequency_in_seconds: int
        streams: Union[list[str, KnownPerfCounterDataSourceStreams]]
        transform_kql: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                counter_specifiers: Optional[list[str]] = ..., 
                name: Optional[str] = ..., 
                sampling_frequency_in_seconds: Optional[int] = ..., 
                streams: Optional[list[Union[str, KnownPerfCounterDataSourceStreams]]] = ..., 
                transform_kql: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.PerformanceCounterConfiguration(Model):
        instance: str
        name: str
        sampling_period: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                instance: Optional[str] = ..., 
                name: str, 
                sampling_period: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.PlatformTelemetryDataSource(Model):
        name: str
        streams: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                streams: list[str], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.PredictiveAutoscalePolicy(Model):
        scale_look_ahead_time: timedelta
        scale_mode: Union[str, PredictiveAutoscalePolicyScaleMode]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                scale_look_ahead_time: Optional[timedelta] = ..., 
                scale_mode: Union[str, PredictiveAutoscalePolicyScaleMode], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.PredictiveAutoscalePolicyScaleMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        FORECAST_ONLY = "ForecastOnly"


    class azure.mgmt.monitor.models.PredictiveResponse(Model):
        data: list[PredictiveValue]
        interval: timedelta
        metric_name: str
        target_resource_id: str
        timespan: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                data: Optional[list[PredictiveValue]] = ..., 
                interval: Optional[timedelta] = ..., 
                metric_name: Optional[str] = ..., 
                target_resource_id: Optional[str] = ..., 
                timespan: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.PredictiveValue(Model):
        time_stamp: datetime
        value: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                time_stamp: datetime, 
                value: float, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.PrivateEndpoint(Model):
        id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.PrivateEndpointConnection(ProxyResource):
        id: str
        name: str
        private_endpoint: PrivateEndpointProperty
        private_link_service_connection_state: PrivateLinkServiceConnectionStateProperty
        provisioning_state: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                private_endpoint: Optional[PrivateEndpointProperty] = ..., 
                private_link_service_connection_state: Optional[PrivateLinkServiceConnectionStateProperty] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.PrivateEndpointConnectionAutoGenerated(ResourceAutoGenerated7):
        group_ids: list[str]
        id: str
        name: str
        private_endpoint: PrivateEndpoint
        private_link_service_connection_state: PrivateLinkServiceConnectionState
        provisioning_state: Union[str, PrivateEndpointConnectionProvisioningState]
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                private_endpoint: Optional[PrivateEndpoint] = ..., 
                private_link_service_connection_state: Optional[PrivateLinkServiceConnectionState] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.PrivateEndpointConnectionListResult(Model):
        next_link: str
        value: list[PrivateEndpointConnection]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.PrivateEndpointConnectionProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.monitor.models.PrivateEndpointProperty(Model):
        id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.PrivateEndpointServiceConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.monitor.models.PrivateLinkResource(ProxyResource):
        group_id: str
        id: str
        name: str
        required_members: list[str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.PrivateLinkResourceListResult(Model):
        next_link: str
        value: list[PrivateLinkResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.PrivateLinkScopedResource(Model):
        resource_id: str
        scope_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                resource_id: Optional[str] = ..., 
                scope_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.PrivateLinkScopesResource(Model):
        id: str
        location: str
        name: str
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: str, 
                tags: Optional[dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.PrivateLinkServiceConnectionState(Model):
        actions_required: str
        description: str
        status: Union[str, PrivateEndpointServiceConnectionStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                actions_required: Optional[str] = ..., 
                description: Optional[str] = ..., 
                status: Optional[Union[str, PrivateEndpointServiceConnectionStatus]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.PrivateLinkServiceConnectionStateProperty(Model):
        actions_required: str
        description: str
        status: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: str, 
                status: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.PromQLCriteria(MetricAlertCriteria):
        additional_properties: dict[str, JSON]
        all_of: list[MultiPromQLCriteria]
        failing_periods: QueryFailingPeriods
        odata_type: Union[str, Odatatype]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_properties: Optional[dict[str, JSON]] = ..., 
                all_of: Optional[list[MultiPromQLCriteria]] = ..., 
                failing_periods: Optional[QueryFailingPeriods] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.PrometheusForwarderDataSource(Model):
        label_include_filter: dict[str, str]
        name: str
        streams: Union[list[str, KnownPrometheusForwarderDataSourceStreams]]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                label_include_filter: Optional[dict[str, str]] = ..., 
                name: Optional[str] = ..., 
                streams: Optional[list[Union[str, KnownPrometheusForwarderDataSourceStreams]]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.monitor.models.ProxyOnlyResource(Model):
        id: str
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ProxyResource(Model):
        id: str
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.PublicNetworkAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.monitor.models.QueryFailingPeriods(Model):
        for_property: timedelta

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                for_property: timedelta, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ReceiverStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        NOT_SPECIFIED = "NotSpecified"


    class azure.mgmt.monitor.models.Recurrence(Model):
        frequency: Union[str, RecurrenceFrequency]
        schedule: RecurrentSchedule

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                frequency: Union[str, RecurrenceFrequency], 
                schedule: RecurrentSchedule, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.RecurrenceFrequency(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DAY = "Day"
        HOUR = "Hour"
        MINUTE = "Minute"
        MONTH = "Month"
        NONE = "None"
        SECOND = "Second"
        WEEK = "Week"
        YEAR = "Year"


    class azure.mgmt.monitor.models.RecurrentSchedule(Model):
        days: list[str]
        hours: list[int]
        minutes: list[int]
        time_zone: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                days: list[str], 
                hours: list[int], 
                minutes: list[int], 
                time_zone: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ReferencesSpec(Model):
        enrichment_data: ReferencesSpecEnrichmentData

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                enrichment_data: Optional[ReferencesSpecEnrichmentData] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ReferencesSpecEnrichmentData(EnrichmentData):
        storage_blobs: list[StorageBlob]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                storage_blobs: Optional[list[StorageBlob]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ResolveConfiguration(Model):
        auto_resolved: bool
        time_to_resolve: timedelta

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                auto_resolved: bool, 
                time_to_resolve: Optional[timedelta] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.Resource(Model):
        id: str
        location: str
        name: str
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: str, 
                tags: Optional[dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ResourceAutoGenerated(Model):
        id: str
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ResourceAutoGenerated2(Model):
        id: str
        location: str
        name: str
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: str, 
                tags: Optional[dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ResourceAutoGenerated3(Model):
        id: str
        location: str
        name: str
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: str, 
                tags: Optional[dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ResourceAutoGenerated4(Model):
        id: str
        location: str
        name: str
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: str, 
                tags: Optional[dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ResourceAutoGenerated5(Model):
        id: str
        identity: Identity
        location: str
        name: str
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                identity: Optional[Identity] = ..., 
                location: str, 
                tags: Optional[dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ResourceAutoGenerated6(Model):
        id: str
        location: str
        name: str
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: str, 
                tags: Optional[dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ResourceAutoGenerated7(Model):
        id: str
        name: str
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ResourceAutoGenerated8(Model):
        id: str
        name: str
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ResourceForUpdate(Model):
        identity: ResourceForUpdateIdentity
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                identity: Optional[ResourceForUpdateIdentity] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ResourceForUpdateIdentity(ManagedServiceIdentity):
        principal_id: str
        tenant_id: str
        type: Union[str, ManagedServiceIdentityType]
        user_assigned_identities: dict[str, UserAssignedIdentity]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                type: Union[str, ManagedServiceIdentityType], 
                user_assigned_identities: Optional[dict[str, UserAssignedIdentity]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.Response(Model):
        cost: int
        interval: str
        namespace: str
        resourceregion: str
        timespan: str
        value: list[Metric]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cost: Optional[int] = ..., 
                interval: Optional[str] = ..., 
                namespace: Optional[str] = ..., 
                resourceregion: Optional[str] = ..., 
                timespan: str, 
                value: list[Metric], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ResponseWithError(Model):
        error: Error

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error: Error, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ResultType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DATA = "Data"
        METADATA = "Metadata"


    class azure.mgmt.monitor.models.RetentionPolicy(Model):
        days: int
        enabled: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                days: int, 
                enabled: bool, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.RuleResolveConfiguration(Model):
        auto_resolved: bool
        time_to_resolve: timedelta

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                auto_resolved: Optional[bool] = ..., 
                time_to_resolve: Optional[timedelta] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ScaleAction(Model):
        cooldown: timedelta
        direction: Union[str, ScaleDirection]
        type: Union[str, ScaleType]
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cooldown: timedelta, 
                direction: Union[str, ScaleDirection], 
                type: Union[str, ScaleType], 
                value: str = "1", 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ScaleCapacity(Model):
        default: str
        maximum: str
        minimum: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                default: str, 
                maximum: str, 
                minimum: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ScaleDirection(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DECREASE = "Decrease"
        INCREASE = "Increase"
        NONE = "None"


    class azure.mgmt.monitor.models.ScaleRule(Model):
        metric_trigger: MetricTrigger
        scale_action: ScaleAction

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                metric_trigger: MetricTrigger, 
                scale_action: ScaleAction, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ScaleRuleMetricDimension(Model):
        dimension_name: str
        operator: Union[str, ScaleRuleMetricDimensionOperationType]
        values: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                dimension_name: str, 
                operator: Union[str, ScaleRuleMetricDimensionOperationType], 
                values: list[str], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ScaleRuleMetricDimensionOperationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EQUALS = "Equals"
        NOT_EQUALS = "NotEquals"


    class azure.mgmt.monitor.models.ScaleType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CHANGE_COUNT = "ChangeCount"
        EXACT_COUNT = "ExactCount"
        PERCENT_CHANGE_COUNT = "PercentChangeCount"
        SERVICE_ALLOWED_NEXT_VALUE = "ServiceAllowedNextValue"


    class azure.mgmt.monitor.models.ScheduledQueryRuleCriteria(Model):
        all_of: list[Condition]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                all_of: Optional[list[Condition]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ScheduledQueryRuleResource(Model):
        actions: Actions
        auto_mitigate: bool
        check_workspace_alerts_storage_configured: bool
        created_with_api_version: str
        criteria: ScheduledQueryRuleCriteria
        description: str
        display_name: str
        enabled: bool
        etag: str
        evaluation_frequency: timedelta
        id: str
        identity: IdentityAutoGenerated
        is_legacy_log_analytics_rule: bool
        is_workspace_alerts_storage_configured: bool
        kind: Union[str, Kind]
        location: str
        mute_actions_duration: timedelta
        name: str
        override_query_time_range: timedelta
        resolve_configuration: RuleResolveConfiguration
        scopes: list[str]
        severity: Union[int, AlertSeverity]
        skip_query_validation: bool
        system_data: SystemData
        tags: dict[str, str]
        target_resource_types: list[str]
        type: str
        window_size: timedelta

        def __eq__(self, other: Any) -> bool: ...

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
                identity: Optional[IdentityAutoGenerated] = ..., 
                kind: Optional[Union[str, Kind]] = ..., 
                location: str, 
                mute_actions_duration: Optional[timedelta] = ..., 
                override_query_time_range: Optional[timedelta] = ..., 
                resolve_configuration: Optional[RuleResolveConfiguration] = ..., 
                scopes: Optional[list[str]] = ..., 
                severity: Optional[Union[int, AlertSeverity]] = ..., 
                skip_query_validation: Optional[bool] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                target_resource_types: Optional[list[str]] = ..., 
                window_size: Optional[timedelta] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ScheduledQueryRuleResourceCollection(Model):
        next_link: str
        value: list[ScheduledQueryRuleResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[list[ScheduledQueryRuleResource]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ScheduledQueryRuleResourcePatch(Model):
        actions: Actions
        auto_mitigate: bool
        check_workspace_alerts_storage_configured: bool
        created_with_api_version: str
        criteria: ScheduledQueryRuleCriteria
        description: str
        display_name: str
        enabled: bool
        evaluation_frequency: timedelta
        identity: IdentityAutoGenerated
        is_legacy_log_analytics_rule: bool
        is_workspace_alerts_storage_configured: bool
        mute_actions_duration: timedelta
        override_query_time_range: timedelta
        resolve_configuration: RuleResolveConfiguration
        scopes: list[str]
        severity: Union[int, AlertSeverity]
        skip_query_validation: bool
        tags: dict[str, str]
        target_resource_types: list[str]
        window_size: timedelta

        def __eq__(self, other: Any) -> bool: ...

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
                identity: Optional[IdentityAutoGenerated] = ..., 
                mute_actions_duration: Optional[timedelta] = ..., 
                override_query_time_range: Optional[timedelta] = ..., 
                resolve_configuration: Optional[RuleResolveConfiguration] = ..., 
                scopes: Optional[list[str]] = ..., 
                severity: Optional[Union[int, AlertSeverity]] = ..., 
                skip_query_validation: Optional[bool] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                target_resource_types: Optional[list[str]] = ..., 
                window_size: Optional[timedelta] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ScopedResource(ProxyResource):
        id: str
        linked_resource_id: str
        name: str
        provisioning_state: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                linked_resource_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ScopedResourceListResult(Model):
        next_link: str
        value: list[ScopedResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.SenderAuthorization(Model):
        action: str
        role: str
        scope: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                action: Optional[str] = ..., 
                role: Optional[str] = ..., 
                scope: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ServiceDiagnosticSettingsResource(ResourceAutoGenerated6):
        event_hub_authorization_rule_id: str
        id: str
        location: str
        logs: list[LogSettingsAutoGenerated]
        metrics: list[MetricSettingsAutoGenerated]
        name: str
        service_bus_rule_id: str
        storage_account_id: str
        tags: dict[str, str]
        type: str
        workspace_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                event_hub_authorization_rule_id: Optional[str] = ..., 
                location: str, 
                logs: Optional[list[LogSettingsAutoGenerated]] = ..., 
                metrics: Optional[list[MetricSettingsAutoGenerated]] = ..., 
                service_bus_rule_id: Optional[str] = ..., 
                storage_account_id: Optional[str] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                workspace_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.ServiceDiagnosticSettingsResourcePatch(Model):
        event_hub_authorization_rule_id: str
        logs: list[LogSettingsAutoGenerated]
        metrics: list[MetricSettingsAutoGenerated]
        service_bus_rule_id: str
        storage_account_id: str
        tags: dict[str, str]
        workspace_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                event_hub_authorization_rule_id: Optional[str] = ..., 
                logs: Optional[list[LogSettingsAutoGenerated]] = ..., 
                metrics: Optional[list[MetricSettingsAutoGenerated]] = ..., 
                service_bus_rule_id: Optional[str] = ..., 
                storage_account_id: Optional[str] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                workspace_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.SingleBaseline(Model):
        high_thresholds: list[float]
        low_thresholds: list[float]
        sensitivity: Union[str, BaselineSensitivity]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                high_thresholds: list[float], 
                low_thresholds: list[float], 
                sensitivity: Union[str, BaselineSensitivity], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.SingleMetricBaseline(Model):
        baselines: list[TimeSeriesBaseline]
        id: str
        interval: timedelta
        name: str
        namespace: str
        timespan: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                baselines: list[TimeSeriesBaseline], 
                id: str, 
                interval: timedelta, 
                name: str, 
                namespace: Optional[str] = ..., 
                timespan: str, 
                type: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.SinkConfiguration(Model):
        kind: Union[str, SinkConfigurationKind]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                kind: Union[str, SinkConfigurationKind], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.SinkConfigurationKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION_INSIGHTS = "ApplicationInsights"
        EVENT_HUB = "EventHub"
        LOG_ANALYTICS = "LogAnalytics"


    class azure.mgmt.monitor.models.SmsReceiver(Model):
        country_code: str
        name: str
        phone_number: str
        status: Union[str, ReceiverStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                country_code: str, 
                name: str, 
                phone_number: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.StaticPromQLCriteria(MultiPromQLCriteria):
        criterion_type: Union[str, CriterionType]
        name: str
        query: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: str, 
                query: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.StorageBlob(Model):
        blob_url: str
        lookup_type: Union[str, KnownStorageBlobLookupType]
        name: str
        resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                blob_url: Optional[str] = ..., 
                lookup_type: Optional[Union[str, KnownStorageBlobLookupType]] = ..., 
                name: Optional[str] = ..., 
                resource_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.StorageBlobDestination(Model):
        container_name: str
        name: str
        storage_account_resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                container_name: Optional[str] = ..., 
                name: Optional[str] = ..., 
                storage_account_resource_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.StorageTableDestination(Model):
        name: str
        storage_account_resource_id: str
        table_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                storage_account_resource_id: Optional[str] = ..., 
                table_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.StreamDeclaration(Model):
        columns: list[ColumnDefinition]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                columns: Optional[list[ColumnDefinition]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.SubscriptionDiagnosticSettingsResource(SubscriptionProxyOnlyResource):
        event_hub_authorization_rule_id: str
        event_hub_name: str
        id: str
        location: str
        logs: list[SubscriptionLogSettings]
        name: str
        service_bus_rule_id: str
        storage_account_id: str
        type: str
        workspace_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                event_hub_authorization_rule_id: Optional[str] = ..., 
                event_hub_name: Optional[str] = ..., 
                location: Optional[str] = ..., 
                logs: Optional[list[SubscriptionLogSettings]] = ..., 
                service_bus_rule_id: Optional[str] = ..., 
                storage_account_id: Optional[str] = ..., 
                workspace_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.SubscriptionDiagnosticSettingsResourceCollection(Model):
        value: list[SubscriptionDiagnosticSettingsResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[list[SubscriptionDiagnosticSettingsResource]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.SubscriptionLogSettings(Model):
        category: str
        enabled: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                category: Optional[str] = ..., 
                enabled: bool, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.SubscriptionProxyOnlyResource(Model):
        id: str
        location: str
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.SubscriptionScopeMetricDefinition(Model):
        category: str
        dimensions: list[LocalizableStringAutoGenerated]
        display_description: str
        id: str
        is_dimension_required: bool
        metric_availabilities: list[MetricAvailability]
        metric_class: Union[str, MetricClass]
        name: LocalizableStringAutoGenerated
        namespace: str
        primary_aggregation_type: Union[str, MetricAggregationType]
        resource_id: str
        supported_aggregation_types: Union[list[str, MetricAggregationType]]
        unit: Union[str, MetricUnit]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                category: Optional[str] = ..., 
                dimensions: Optional[list[LocalizableStringAutoGenerated]] = ..., 
                display_description: Optional[str] = ..., 
                id: Optional[str] = ..., 
                is_dimension_required: Optional[bool] = ..., 
                metric_availabilities: Optional[list[MetricAvailability]] = ..., 
                metric_class: Optional[Union[str, MetricClass]] = ..., 
                name: Optional[LocalizableStringAutoGenerated] = ..., 
                namespace: Optional[str] = ..., 
                primary_aggregation_type: Optional[Union[str, MetricAggregationType]] = ..., 
                resource_id: Optional[str] = ..., 
                supported_aggregation_types: Optional[list[Union[str, MetricAggregationType]]] = ..., 
                unit: Optional[Union[str, MetricUnit]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.SubscriptionScopeMetricDefinitionCollection(Model):
        value: list[SubscriptionScopeMetricDefinition]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: list[SubscriptionScopeMetricDefinition], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.SubscriptionScopeMetricsRequestBodyParameters(Model):
        aggregation: str
        auto_adjust_timegrain: bool
        filter: str
        interval: str
        metric_names: str
        metric_namespace: str
        order_by: str
        result_type: Union[str, MetricResultType]
        roll_up_by: str
        timespan: str
        top: int
        validate_dimensions: bool

        def __eq__(self, other: Any) -> bool: ...

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
                validate_dimensions: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.SyslogDataSource(Model):
        facility_names: Union[list[str, KnownSyslogDataSourceFacilityNames]]
        log_levels: Union[list[str, KnownSyslogDataSourceLogLevels]]
        name: str
        streams: Union[list[str, KnownSyslogDataSourceStreams]]
        transform_kql: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                facility_names: Optional[list[Union[str, KnownSyslogDataSourceFacilityNames]]] = ..., 
                log_levels: Optional[list[Union[str, KnownSyslogDataSourceLogLevels]]] = ..., 
                name: Optional[str] = ..., 
                streams: Optional[list[Union[str, KnownSyslogDataSourceStreams]]] = ..., 
                transform_kql: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.SystemData(Model):
        created_at: datetime
        created_by: str
        created_by_type: Union[str, CreatedByType]
        last_modified_at: datetime
        last_modified_by: str
        last_modified_by_type: Union[str, CreatedByType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                created_at: Optional[datetime] = ..., 
                created_by: Optional[str] = ..., 
                created_by_type: Optional[Union[str, CreatedByType]] = ..., 
                last_modified_at: Optional[datetime] = ..., 
                last_modified_by: Optional[str] = ..., 
                last_modified_by_type: Optional[Union[str, CreatedByType]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.TagsResource(Model):
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.TestNotificationDetailsResponse(Model):
        action_details: list[ActionDetail]
        completed_time: str
        context: Context
        created_time: str
        state: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                action_details: Optional[list[ActionDetail]] = ..., 
                completed_time: Optional[str] = ..., 
                context: Optional[Context] = ..., 
                created_time: Optional[str] = ..., 
                state: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


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


    class azure.mgmt.monitor.models.TimeSeriesBaseline(Model):
        aggregation: str
        data: list[SingleBaseline]
        dimensions: list[MetricSingleDimension]
        metadata_values: list[BaselineMetadata]
        timestamps: list[datetime]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                aggregation: str, 
                data: list[SingleBaseline], 
                dimensions: Optional[list[MetricSingleDimension]] = ..., 
                metadata_values: Optional[list[BaselineMetadata]] = ..., 
                timestamps: list[datetime], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.TimeSeriesElement(Model):
        data: list[MetricValue]
        metadatavalues: list[MetadataValue]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                data: Optional[list[MetricValue]] = ..., 
                metadatavalues: Optional[list[MetadataValue]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.TimeWindow(Model):
        end: datetime
        start: datetime
        time_zone: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                end: datetime, 
                start: datetime, 
                time_zone: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.TrackedResource(ResourceAutoGenerated8):
        id: str
        location: str
        name: str
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: str, 
                tags: Optional[dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.UserAssignedIdentity(Model):
        client_id: str
        principal_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.UserIdentityProperties(Model):
        client_id: str
        principal_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.UserIdentityPropertiesAutoGenerated(Model):
        client_id: str
        principal_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.VMInsightsOnboardingStatus(ProxyResource):
        data: list[DataContainer]
        data_status: Union[str, DataStatus]
        id: str
        name: str
        onboarding_status: Union[str, OnboardingStatus]
        resource_id: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                data: Optional[list[DataContainer]] = ..., 
                data_status: Optional[Union[str, DataStatus]] = ..., 
                onboarding_status: Optional[Union[str, OnboardingStatus]] = ..., 
                resource_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.VoiceReceiver(Model):
        country_code: str
        name: str
        phone_number: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                country_code: str, 
                name: str, 
                phone_number: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.WebhookNotification(Model):
        properties: dict[str, str]
        service_uri: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[dict[str, str]] = ..., 
                service_uri: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.WebhookReceiver(Model):
        identifier_uri: str
        name: str
        object_id: str
        service_uri: str
        tenant_id: str
        use_aad_auth: bool
        use_common_alert_schema: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                identifier_uri: Optional[str] = ..., 
                name: str, 
                object_id: Optional[str] = ..., 
                service_uri: str, 
                tenant_id: Optional[str] = ..., 
                use_aad_auth: bool = False, 
                use_common_alert_schema: bool = False, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.WebtestLocationAvailabilityCriteria(MetricAlertCriteria):
        additional_properties: dict[str, JSON]
        component_id: str
        failed_location_count: float
        odata_type: Union[str, Odatatype]
        web_test_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_properties: Optional[dict[str, JSON]] = ..., 
                component_id: str, 
                failed_location_count: float, 
                web_test_id: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.WindowsEventLogDataSource(Model):
        name: str
        streams: Union[list[str, KnownWindowsEventLogDataSourceStreams]]
        transform_kql: str
        x_path_queries: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                streams: Optional[list[Union[str, KnownWindowsEventLogDataSourceStreams]]] = ..., 
                transform_kql: Optional[str] = ..., 
                x_path_queries: Optional[list[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.WindowsFirewallLogsDataSource(Model):
        name: str
        profile_filter: Union[list[str, KnownWindowsFirewallLogsDataSourceProfileFilter]]
        streams: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                profile_filter: Optional[list[Union[str, KnownWindowsFirewallLogsDataSourceProfileFilter]]] = ..., 
                streams: list[str], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.monitor.models.WorkspaceInfo(Model):
        customer_id: str
        id: str
        location: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                customer_id: str, 
                id: str, 
                location: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


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
                notification_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TestNotificationDetailsResponse]: ...

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
                enable_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                action_group_name: str, 
                **kwargs: Any
            ) -> ActionGroupResource: ...

        @distributed_trace
        def get_test_notifications_at_action_group_resource_level(
                self, 
                resource_group_name: str, 
                action_group_name: str, 
                notification_id: str, 
                **kwargs: Any
            ) -> TestNotificationDetailsResponse: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ActionGroupResource]: ...

        @distributed_trace
        def list_by_subscription_id(self, **kwargs: Any) -> ItemPaged[ActionGroupResource]: ...

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
                filter: str, 
                select: Optional[str] = None, 
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
                autoscale_setting_resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutoscaleSettingResource: ...


    class azure.mgmt.monitor.operations.AzureMonitorWorkspacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                azure_monitor_workspace_properties: AzureMonitorWorkspaceResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureMonitorWorkspaceResource: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                azure_monitor_workspace_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureMonitorWorkspaceResource: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                **kwargs: Any
            ) -> AzureMonitorWorkspaceResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AzureMonitorWorkspaceResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[AzureMonitorWorkspaceResource]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                azure_monitor_workspace_properties: Optional[AzureMonitorWorkspaceResourceForUpdate] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureMonitorWorkspaceResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                azure_monitor_workspace_properties: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureMonitorWorkspaceResource: ...


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
                metricnames: Optional[str] = None, 
                metricnamespace: Optional[str] = None, 
                timespan: Optional[str] = None, 
                interval: Optional[timedelta] = None, 
                aggregation: Optional[str] = None, 
                sensitivities: Optional[str] = None, 
                filter: Optional[str] = None, 
                result_type: Optional[Union[str, ResultType]] = None, 
                **kwargs: Any
            ) -> ItemPaged[SingleMetricBaseline]: ...


    class azure.mgmt.monitor.operations.DataCollectionEndpointsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
        def delete(
                self, 
                resource_group_name: str, 
                data_collection_endpoint_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                data_collection_endpoint_name: str, 
                **kwargs: Any
            ) -> DataCollectionEndpointResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DataCollectionEndpointResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[DataCollectionEndpointResource]: ...

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
                delete_associations: bool = False, 
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
            ) -> DiagnosticSettingsCategoryResourceCollection: ...


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


    class azure.mgmt.monitor.operations.GuestDiagnosticsSettingsAssociationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_uri: str, 
                association_name: str, 
                diagnostic_settings_association: GuestDiagnosticSettingsAssociationResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GuestDiagnosticSettingsAssociationResource: ...

        @overload
        def create_or_update(
                self, 
                resource_uri: str, 
                association_name: str, 
                diagnostic_settings_association: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GuestDiagnosticSettingsAssociationResource: ...

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
            ) -> GuestDiagnosticSettingsAssociationResource: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[GuestDiagnosticSettingsAssociationResource]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[GuestDiagnosticSettingsAssociationResource]: ...

        @overload
        def update(
                self, 
                resource_uri: str, 
                association_name: str, 
                parameters: GuestDiagnosticSettingsAssociationResourcePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GuestDiagnosticSettingsAssociationResource: ...

        @overload
        def update(
                self, 
                resource_uri: str, 
                association_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GuestDiagnosticSettingsAssociationResource: ...


    class azure.mgmt.monitor.operations.GuestDiagnosticsSettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                diagnostic_settings_name: str, 
                diagnostic_settings: GuestDiagnosticSettingsResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GuestDiagnosticSettingsResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                diagnostic_settings_name: str, 
                diagnostic_settings: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GuestDiagnosticSettingsResource: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                diagnostic_settings_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                diagnostic_settings_name: str, 
                **kwargs: Any
            ) -> GuestDiagnosticSettingsResource: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[GuestDiagnosticSettingsResource]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[GuestDiagnosticSettingsResource]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                diagnostic_settings_name: str, 
                parameters: GuestDiagnosticSettingsPatchResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GuestDiagnosticSettingsResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                diagnostic_settings_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GuestDiagnosticSettingsResource: ...


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
                metricnamespace: Optional[str] = None, 
                **kwargs: Any
            ) -> ItemPaged[MetricDefinition]: ...

        @distributed_trace
        def list_at_subscription_scope(
                self, 
                region: str, 
                metricnamespace: Optional[str] = None, 
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
                start_time: Optional[str] = None, 
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
                timespan: Optional[str] = None, 
                interval: Optional[str] = None, 
                metricnames: Optional[str] = None, 
                aggregation: Optional[str] = None, 
                top: Optional[int] = None, 
                orderby: Optional[str] = None, 
                filter: Optional[str] = None, 
                result_type: Optional[Union[str, ResultType]] = None, 
                metricnamespace: Optional[str] = None, 
                auto_adjust_timegrain: Optional[bool] = None, 
                validate_dimensions: Optional[bool] = None, 
                rollupby: Optional[str] = None, 
                **kwargs: Any
            ) -> Response: ...

        @distributed_trace
        def list_at_subscription_scope(
                self, 
                region: str, 
                timespan: Optional[str] = None, 
                interval: Optional[str] = None, 
                metricnames: Optional[str] = None, 
                aggregation: Optional[str] = None, 
                top: Optional[int] = None, 
                orderby: Optional[str] = None, 
                filter: Optional[str] = None, 
                result_type: Optional[Union[str, MetricResultType]] = None, 
                metricnamespace: Optional[str] = None, 
                auto_adjust_timegrain: Optional[bool] = None, 
                validate_dimensions: Optional[bool] = None, 
                rollupby: Optional[str] = None, 
                **kwargs: Any
            ) -> Response: ...

        @overload
        def list_at_subscription_scope_post(
                self, 
                region: str, 
                timespan: Optional[str] = None, 
                interval: Optional[str] = None, 
                metricnames: Optional[str] = None, 
                aggregation: Optional[str] = None, 
                top: Optional[int] = None, 
                orderby: Optional[str] = None, 
                filter: Optional[str] = None, 
                result_type: Optional[Union[str, MetricResultType]] = None, 
                metricnamespace: Optional[str] = None, 
                auto_adjust_timegrain: Optional[bool] = None, 
                validate_dimensions: Optional[bool] = None, 
                rollupby: Optional[str] = None, 
                body: Optional[SubscriptionScopeMetricsRequestBodyParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Response: ...

        @overload
        def list_at_subscription_scope_post(
                self, 
                region: str, 
                timespan: Optional[str] = None, 
                interval: Optional[str] = None, 
                metricnames: Optional[str] = None, 
                aggregation: Optional[str] = None, 
                top: Optional[int] = None, 
                orderby: Optional[str] = None, 
                filter: Optional[str] = None, 
                result_type: Optional[Union[str, MetricResultType]] = None, 
                metricnamespace: Optional[str] = None, 
                auto_adjust_timegrain: Optional[bool] = None, 
                validate_dimensions: Optional[bool] = None, 
                rollupby: Optional[str] = None, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Response: ...


    class azure.mgmt.monitor.operations.MonitorOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[OperationAutoGenerated]: ...


    class azure.mgmt.monitor.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> OperationListResult: ...


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
                timespan: str, 
                interval: timedelta, 
                metric_namespace: str, 
                metric_name: str, 
                aggregation: str, 
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
                private_link_scope_tags: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureMonitorPrivateLinkScope: ...


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
                service_diagnostic_settings_resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServiceDiagnosticSettingsResource: ...


    class azure.mgmt.monitor.operations.SubscriptionDiagnosticSettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                name: str, 
                parameters: SubscriptionDiagnosticSettingsResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SubscriptionDiagnosticSettingsResource: ...

        @overload
        def create_or_update(
                self, 
                name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SubscriptionDiagnosticSettingsResource: ...

        @distributed_trace
        def delete(
                self, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                name: str, 
                **kwargs: Any
            ) -> SubscriptionDiagnosticSettingsResource: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> SubscriptionDiagnosticSettingsResourceCollection: ...


    class azure.mgmt.monitor.operations.TenantActivityLogsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                filter: Optional[str] = None, 
                select: Optional[str] = None, 
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


```