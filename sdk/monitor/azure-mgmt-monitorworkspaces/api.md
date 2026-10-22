```py
namespace azure.mgmt.monitorworkspaces

    class azure.mgmt.monitorworkspaces.MonitorWorkspacesMgmtClient: implements ContextManager 
        azure_monitor_workspaces: AzureMonitorWorkspacesOperations
        issue: IssueOperations
        metric_configurations: MetricConfigurationsOperations
        metric_namespaces: MetricNamespacesOperations
        metrics_containers: MetricsContainersOperations
        operations: Operations
        trace_associations: TraceAssociationsOperations
        trace_associations_at_resource_group: TraceAssociationsAtResourceGroupOperations
        trace_associations_at_subscription: TraceAssociationsAtSubscriptionOperations
        trace_containers: TraceContainersOperations

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


namespace azure.mgmt.monitorworkspaces.aio

    class azure.mgmt.monitorworkspaces.aio.MonitorWorkspacesMgmtClient: implements AsyncContextManager 
        azure_monitor_workspaces: AzureMonitorWorkspacesOperations
        issue: IssueOperations
        metric_configurations: MetricConfigurationsOperations
        metric_namespaces: MetricNamespacesOperations
        metrics_containers: MetricsContainersOperations
        operations: Operations
        trace_associations: TraceAssociationsOperations
        trace_associations_at_resource_group: TraceAssociationsAtResourceGroupOperations
        trace_associations_at_subscription: TraceAssociationsAtSubscriptionOperations
        trace_containers: TraceContainersOperations

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


namespace azure.mgmt.monitorworkspaces.aio.operations

    class azure.mgmt.monitorworkspaces.aio.operations.AzureMonitorWorkspacesOperations:

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
        async def create_or_update(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                resource: AzureMonitorWorkspaceResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureMonitorWorkspaceResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                resource: AzureMonitorWorkspaceResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureMonitorWorkspaceResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                resource: IO[bytes], 
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
                properties: AzureMonitorWorkspaceResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureMonitorWorkspaceResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                properties: AzureMonitorWorkspaceResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureMonitorWorkspaceResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureMonitorWorkspaceResource: ...


    class azure.mgmt.monitorworkspaces.aio.operations.IssueOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def add_investigation_result(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                issue_name: str, 
                body: InvestigationResult, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> InvestigationResult: ...

        @overload
        async def add_investigation_result(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                issue_name: str, 
                body: InvestigationResult, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> InvestigationResult: ...

        @overload
        async def add_investigation_result(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                issue_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> InvestigationResult: ...

        @overload
        async def add_or_update_alerts(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                issue_name: str, 
                body: RelatedAlerts, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RelatedAlerts: ...

        @overload
        async def add_or_update_alerts(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                issue_name: str, 
                body: RelatedAlerts, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RelatedAlerts: ...

        @overload
        async def add_or_update_alerts(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                issue_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RelatedAlerts: ...

        @overload
        async def add_or_update_resources(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                issue_name: str, 
                body: RelatedResources, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RelatedResources: ...

        @overload
        async def add_or_update_resources(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                issue_name: str, 
                body: RelatedResources, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RelatedResources: ...

        @overload
        async def add_or_update_resources(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                issue_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RelatedResources: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                issue_name: str, 
                resource: IssueResource, 
                *, 
                content_type: str = "application/json", 
                related: Optional[str] = ..., 
                **kwargs: Any
            ) -> IssueResource: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                issue_name: str, 
                resource: IssueResource, 
                *, 
                content_type: str = "application/json", 
                related: Optional[str] = ..., 
                **kwargs: Any
            ) -> IssueResource: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                issue_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                related: Optional[str] = ..., 
                **kwargs: Any
            ) -> IssueResource: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                issue_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-10-03-preview', params_added_on={'2025-10-03-preview': ['api_version', 'subscription_id', 'resource_group_name', 'azure_monitor_workspace_name', 'issue_name', 'accept']}, api_versions_list=['2025-10-03-preview', '2025-10-03', '2026-09-03-preview'])
        async def fetch_background_visualization(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                issue_name: str, 
                **kwargs: Any
            ) -> BackgroundVisualization: ...

        @overload
        async def fetch_investigation_result(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                issue_name: str, 
                body: FetchInvestigationResultParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> InvestigationResult: ...

        @overload
        async def fetch_investigation_result(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                issue_name: str, 
                body: FetchInvestigationResultParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> InvestigationResult: ...

        @overload
        async def fetch_investigation_result(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                issue_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> InvestigationResult: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                issue_name: str, 
                **kwargs: Any
            ) -> IssueResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[IssueResource]: ...

        @overload
        async def list_alerts(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                issue_name: str, 
                body: ListParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PagedRelatedAlert: ...

        @overload
        async def list_alerts(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                issue_name: str, 
                body: ListParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PagedRelatedAlert: ...

        @overload
        async def list_alerts(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                issue_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PagedRelatedAlert: ...

        @overload
        async def list_resources(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                issue_name: str, 
                body: ListParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PagedRelatedResource: ...

        @overload
        async def list_resources(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                issue_name: str, 
                body: ListParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PagedRelatedResource: ...

        @overload
        async def list_resources(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                issue_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PagedRelatedResource: ...

        @overload
        async def set_background_visualization(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                issue_name: str, 
                body: BackgroundVisualization, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def set_background_visualization(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                issue_name: str, 
                body: BackgroundVisualization, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def set_background_visualization(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                issue_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                issue_name: str, 
                properties: IssueResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IssueResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                issue_name: str, 
                properties: IssueResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IssueResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                issue_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IssueResource: ...


    class azure.mgmt.monitorworkspaces.aio.operations.MetricConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                metrics_container_name: str, 
                encoded_metric_namespace: str, 
                encoded_metric_name: str, 
                resource: MetricConfigurationResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MetricConfigurationResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                metrics_container_name: str, 
                encoded_metric_namespace: str, 
                encoded_metric_name: str, 
                resource: MetricConfigurationResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MetricConfigurationResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                metrics_container_name: str, 
                encoded_metric_namespace: str, 
                encoded_metric_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MetricConfigurationResource: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-09-03-preview', params_added_on={'2026-09-03-preview': ['api_version', 'subscription_id', 'resource_group_name', 'azure_monitor_workspace_name', 'metrics_container_name', 'encoded_metric_namespace', 'encoded_metric_name']}, api_versions_list=['2026-09-03-preview'])
        async def delete(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                metrics_container_name: str, 
                encoded_metric_namespace: str, 
                encoded_metric_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-09-03-preview', params_added_on={'2026-09-03-preview': ['api_version', 'subscription_id', 'resource_group_name', 'azure_monitor_workspace_name', 'metrics_container_name', 'encoded_metric_namespace', 'encoded_metric_name', 'accept']}, api_versions_list=['2026-09-03-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                metrics_container_name: str, 
                encoded_metric_namespace: str, 
                encoded_metric_name: str, 
                **kwargs: Any
            ) -> MetricConfigurationResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-09-03-preview', params_added_on={'2026-09-03-preview': ['api_version', 'subscription_id', 'resource_group_name', 'azure_monitor_workspace_name', 'metrics_container_name', 'encoded_metric_namespace', 'filter', 'accept']}, api_versions_list=['2026-09-03-preview'])
        def list_by_metric_namespace(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                metrics_container_name: str, 
                encoded_metric_namespace: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[MetricConfigurationResource]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-09-03-preview', params_added_on={'2026-09-03-preview': ['api_version', 'subscription_id', 'resource_group_name', 'azure_monitor_workspace_name', 'metrics_container_name', 'filter', 'accept']}, api_versions_list=['2026-09-03-preview'])
        def list_by_metrics_container(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                metrics_container_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[MetricConfigurationResource]: ...


    class azure.mgmt.monitorworkspaces.aio.operations.MetricNamespacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-09-03-preview', params_added_on={'2026-09-03-preview': ['api_version', 'subscription_id', 'resource_group_name', 'azure_monitor_workspace_name', 'metrics_container_name', 'encoded_metric_namespace', 'accept']}, api_versions_list=['2026-09-03-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                metrics_container_name: str, 
                encoded_metric_namespace: str, 
                **kwargs: Any
            ) -> MetricNamespaceResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-09-03-preview', params_added_on={'2026-09-03-preview': ['api_version', 'subscription_id', 'resource_group_name', 'azure_monitor_workspace_name', 'metrics_container_name', 'accept']}, api_versions_list=['2026-09-03-preview'])
        def list_by_metrics_container(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                metrics_container_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[MetricNamespaceResource]: ...


    class azure.mgmt.monitorworkspaces.aio.operations.MetricsContainersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                metrics_container_name: str, 
                resource: MetricsContainerResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MetricsContainerResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                metrics_container_name: str, 
                resource: MetricsContainerResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MetricsContainerResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                metrics_container_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MetricsContainerResource: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                metrics_container_name: str, 
                **kwargs: Any
            ) -> MetricsContainerResource: ...

        @distributed_trace
        def list_by_azure_monitor_workspace(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[MetricsContainerResource]: ...


    class azure.mgmt.monitorworkspaces.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.monitorworkspaces.aio.operations.TraceAssociationsAtResourceGroupOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                resource: TraceAssociationResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TraceAssociationResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                resource: TraceAssociationResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TraceAssociationResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TraceAssociationResource: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-09-03-preview', params_added_on={'2026-09-03-preview': ['api_version', 'subscription_id', 'resource_group_name']}, api_versions_list=['2026-09-03-preview'])
        async def delete(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-09-03-preview', params_added_on={'2026-09-03-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2026-09-03-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> TraceAssociationResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-09-03-preview', params_added_on={'2026-09-03-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2026-09-03-preview'])
        def list(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[TraceAssociationResource]: ...


    class azure.mgmt.monitorworkspaces.aio.operations.TraceAssociationsAtSubscriptionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource: TraceAssociationResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TraceAssociationResource: ...

        @overload
        async def create_or_update(
                self, 
                resource: TraceAssociationResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TraceAssociationResource: ...

        @overload
        async def create_or_update(
                self, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TraceAssociationResource: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-09-03-preview', params_added_on={'2026-09-03-preview': ['api_version', 'subscription_id']}, api_versions_list=['2026-09-03-preview'])
        async def delete(self, **kwargs: Any) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-09-03-preview', params_added_on={'2026-09-03-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2026-09-03-preview'])
        async def get(self, **kwargs: Any) -> TraceAssociationResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-09-03-preview', params_added_on={'2026-09-03-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2026-09-03-preview'])
        def list(self, **kwargs: Any) -> AsyncItemPaged[TraceAssociationResource]: ...


    class azure.mgmt.monitorworkspaces.aio.operations.TraceAssociationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                provider_type: str, 
                resource_name: str, 
                resource: TraceAssociationResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TraceAssociationResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                provider_type: str, 
                resource_name: str, 
                resource: TraceAssociationResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TraceAssociationResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                provider_type: str, 
                resource_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TraceAssociationResource: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-09-03-preview', params_added_on={'2026-09-03-preview': ['api_version', 'subscription_id', 'resource_group_name', 'provider_name', 'provider_type', 'resource_name']}, api_versions_list=['2026-09-03-preview'])
        async def delete(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                provider_type: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-09-03-preview', params_added_on={'2026-09-03-preview': ['api_version', 'subscription_id', 'resource_group_name', 'provider_name', 'provider_type', 'resource_name', 'accept']}, api_versions_list=['2026-09-03-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                provider_type: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> TraceAssociationResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-09-03-preview', params_added_on={'2026-09-03-preview': ['api_version', 'subscription_id', 'resource_group_name', 'provider_name', 'provider_type', 'resource_name', 'accept']}, api_versions_list=['2026-09-03-preview'])
        def list(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                provider_type: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[TraceAssociationResource]: ...


    class azure.mgmt.monitorworkspaces.aio.operations.TraceContainersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                resource: TraceContainerResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TraceContainerResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                resource: TraceContainerResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TraceContainerResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TraceContainerResource]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-09-03-preview', params_added_on={'2026-09-03-preview': ['api_version', 'subscription_id', 'resource_group_name', 'azure_monitor_workspace_name']}, api_versions_list=['2026-09-03-preview'])
        async def delete(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-09-03-preview', params_added_on={'2026-09-03-preview': ['api_version', 'subscription_id', 'resource_group_name', 'azure_monitor_workspace_name', 'accept']}, api_versions_list=['2026-09-03-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                **kwargs: Any
            ) -> TraceContainerResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-09-03-preview', params_added_on={'2026-09-03-preview': ['api_version', 'subscription_id', 'resource_group_name', 'azure_monitor_workspace_name', 'accept']}, api_versions_list=['2026-09-03-preview'])
        def list_by_azure_monitor_workspace(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[TraceContainerResource]: ...


namespace azure.mgmt.monitorworkspaces.models

    class azure.mgmt.monitorworkspaces.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.monitorworkspaces.models.AddedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC = "Automatic"
        MANUAL = "Manual"


    class azure.mgmt.monitorworkspaces.models.ArmOrigin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.monitorworkspaces.models.AzureMonitorWorkspace(_Model):
        account_id: Optional[str]
        actions: Optional[AzureMonitorWorkspaceActions]
        default_ingestion_settings: Optional[AzureMonitorWorkspaceDefaultIngestionSettings]
        endpoints: Optional[AzureMonitorWorkspaceEndpoints]
        metrics: Optional[AzureMonitorWorkspaceMetrics]
        private_endpoint_connections: Optional[list[PrivateEndpointConnection]]
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]
        public_network_access: Optional[Union[str, PublicNetworkAccess]]

        @overload
        def __init__(
                self, 
                *, 
                actions: Optional[AzureMonitorWorkspaceActions] = ..., 
                metrics: Optional[AzureMonitorWorkspaceMetrics] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitorworkspaces.models.AzureMonitorWorkspaceActions(_Model):
        default_action_groups: Optional[list[DefaultActionGroupResource]]

        @overload
        def __init__(
                self, 
                *, 
                default_action_groups: Optional[list[DefaultActionGroupResource]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitorworkspaces.models.AzureMonitorWorkspaceDefaultIngestionSettings(_Model):
        data_collection_endpoint_resource_id: Optional[str]
        data_collection_rule_immutable_id: Optional[str]
        data_collection_rule_resource_id: Optional[str]
        ingestion_endpoints: Optional[IngestionEndpoints]


    class azure.mgmt.monitorworkspaces.models.AzureMonitorWorkspaceEndpoints(_Model):
        query: Optional[str]


    class azure.mgmt.monitorworkspaces.models.AzureMonitorWorkspaceMetrics(_Model):
        enable_access_using_resource_permissions: Optional[bool]
        internal_id: Optional[str]
        prometheus_query_endpoint: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                enable_access_using_resource_permissions: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitorworkspaces.models.AzureMonitorWorkspaceResource(TrackedResource):
        etag: Optional[str]
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: Optional[AzureMonitorWorkspace]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: str, 
                properties: Optional[AzureMonitorWorkspace] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitorworkspaces.models.AzureMonitorWorkspaceResourceUpdate(_Model):
        identity: Optional[ManagedServiceIdentity]
        properties: Optional[AzureMonitorWorkspace]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                properties: Optional[AzureMonitorWorkspace] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitorworkspaces.models.Background(_Model):
        details: Optional[list[BackgroundDetails]]
        text: Optional[str]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                details: Optional[list[BackgroundDetails]] = ..., 
                text: Optional[str] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitorworkspaces.models.BackgroundDetails(_Model):
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


    class azure.mgmt.monitorworkspaces.models.BackgroundVisualization(_Model):
        origin: Origin
        visualization: str

        @overload
        def __init__(
                self, 
                *, 
                visualization: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitorworkspaces.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.monitorworkspaces.models.DefaultActionGroupResource(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitorworkspaces.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.monitorworkspaces.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.monitorworkspaces.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitorworkspaces.models.ExtensionResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.monitorworkspaces.models.FetchInvestigationResultParameters(_Model):
        investigation_id: str

        @overload
        def __init__(
                self, 
                *, 
                investigation_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitorworkspaces.models.IngestionEndpoints(_Model):
        metrics: Optional[str]


    class azure.mgmt.monitorworkspaces.models.InvestigationMetadata(_Model):
        created_at: datetime
        id: str

        @overload
        def __init__(
                self, 
                *, 
                created_at: datetime, 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitorworkspaces.models.InvestigationResult(_Model):
        created_at: Optional[datetime]
        id: str
        last_modified_at: Optional[datetime]
        origin: Optional[Origin]
        result: str

        @overload
        def __init__(
                self, 
                *, 
                created_at: Optional[datetime] = ..., 
                id: str, 
                last_modified_at: Optional[datetime] = ..., 
                origin: Optional[Origin] = ..., 
                result: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitorworkspaces.models.IssueCreationNotificationType(IssueNotificationType, discriminator='IssueCreation'):
        update_type: Literal[UpdateType.ISSUE_CREATION]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitorworkspaces.models.IssueNotificationType(_Model):
        update_type: str

        @overload
        def __init__(
                self, 
                *, 
                update_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitorworkspaces.models.IssueProperties(_Model):
        background: Optional[Background]
        impact_time: datetime
        investigations: list[InvestigationMetadata]
        investigations_count: int
        notifications: Optional[Notifications]
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]
        severity: str
        status: Union[str, Status]
        title: str

        @overload
        def __init__(
                self, 
                *, 
                background: Optional[Background] = ..., 
                impact_time: datetime, 
                notifications: Optional[Notifications] = ..., 
                severity: str, 
                status: Union[str, Status], 
                title: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitorworkspaces.models.IssuePropertiesUpdate(_Model):
        background: Optional[Background]
        impact_time: Optional[datetime]
        notifications: Optional[Notifications]
        severity: Optional[str]
        status: Optional[Union[str, Status]]
        title: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                background: Optional[Background] = ..., 
                impact_time: Optional[datetime] = ..., 
                notifications: Optional[Notifications] = ..., 
                severity: Optional[str] = ..., 
                status: Optional[Union[str, Status]] = ..., 
                title: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitorworkspaces.models.IssueResource(ProxyResource):
        id: str
        name: str
        properties: Optional[IssueProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[IssueProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitorworkspaces.models.IssueResourceUpdate(_Model):
        properties: Optional[IssuePropertiesUpdate]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[IssuePropertiesUpdate] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitorworkspaces.models.ListParameter(_Model):
        filter: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                filter: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitorworkspaces.models.ManagedServiceIdentity(_Model):
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


    class azure.mgmt.monitorworkspaces.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.monitorworkspaces.models.MetricAggregationConfiguration(_Model):
        aggregation_functions: Optional[MetricAggregationFunctions]
        dimensions: Optional[list[str]]
        store_aggregated_data: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                aggregation_functions: Optional[MetricAggregationFunctions] = ..., 
                dimensions: Optional[list[str]] = ..., 
                store_aggregated_data: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitorworkspaces.models.MetricAggregationFunctions(_Model):
        enable_min_max: bool
        enable_percentiles: bool

        @overload
        def __init__(
                self, 
                *, 
                enable_min_max: bool, 
                enable_percentiles: bool
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitorworkspaces.models.MetricConfigurationProperties(_Model):
        aggregation_configurations: Optional[list[MetricAggregationConfiguration]]
        dimensions: Optional[list[str]]
        metric_name: Optional[str]
        metric_type: Optional[Union[str, MetricConfigurationType]]
        namespace: Optional[str]
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]
        source_metric_resource_id: Optional[str]
        store_raw_data: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                aggregation_configurations: Optional[list[MetricAggregationConfiguration]] = ..., 
                metric_name: Optional[str] = ..., 
                metric_type: Optional[Union[str, MetricConfigurationType]] = ..., 
                namespace: Optional[str] = ..., 
                source_metric_resource_id: Optional[str] = ..., 
                store_raw_data: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitorworkspaces.models.MetricConfigurationResource(ProxyResource):
        id: str
        name: str
        properties: Optional[MetricConfigurationProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[MetricConfigurationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitorworkspaces.models.MetricConfigurationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AGGREGATED = "Aggregated"
        RAW = "Raw"


    class azure.mgmt.monitorworkspaces.models.MetricNamespaceProperties(_Model):
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]


    class azure.mgmt.monitorworkspaces.models.MetricNamespaceResource(ProxyResource):
        id: str
        name: str
        properties: Optional[MetricNamespaceProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[MetricNamespaceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitorworkspaces.models.MetricsContainer(_Model):
        limits: Optional[MetricsLimits]
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                limits: Optional[MetricsLimits] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitorworkspaces.models.MetricsContainerResource(ProxyResource):
        id: str
        name: str
        properties: Optional[MetricsContainer]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[MetricsContainer] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitorworkspaces.models.MetricsLimits(_Model):
        enable_auto_scale: Optional[bool]
        max_active_time_series: Optional[int]
        max_events_per_minute: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                enable_auto_scale: Optional[bool] = ..., 
                max_active_time_series: Optional[int] = ..., 
                max_events_per_minute: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitorworkspaces.models.Notifications(_Model):
        action_group_ids: Optional[list[str]]
        exclude_default_action_groups: Optional[bool]
        update_types: Optional[list[IssueNotificationType]]

        @overload
        def __init__(
                self, 
                *, 
                action_group_ids: Optional[list[str]] = ..., 
                exclude_default_action_groups: Optional[bool] = ..., 
                update_types: Optional[list[IssueNotificationType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitorworkspaces.models.OnChangeNotificationType(IssueNotificationType, discriminator='OnChange'):
        update_type: Literal[UpdateType.ON_CHANGE]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitorworkspaces.models.Operation(_Model):
        action_type: Optional[Union[str, ActionType]]
        display: Optional[OperationDisplay]
        is_data_action: Optional[bool]
        name: Optional[str]
        origin: Optional[Union[str, ArmOrigin]]

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitorworkspaces.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.monitorworkspaces.models.Origin(_Model):
        added_by: str
        added_by_type: Union[str, AddedByType]

        @overload
        def __init__(
                self, 
                *, 
                added_by: str, 
                added_by_type: Union[str, AddedByType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitorworkspaces.models.PagedRelatedAlert(_Model):
        next_link: Optional[str]
        value: list[RelatedAlert]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[RelatedAlert]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitorworkspaces.models.PagedRelatedResource(_Model):
        next_link: Optional[str]
        value: list[RelatedResource]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[RelatedResource]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitorworkspaces.models.PrivateEndpoint(_Model):
        id: Optional[str]


    class azure.mgmt.monitorworkspaces.models.PrivateEndpointConnection(Resource):
        id: str
        name: str
        properties: Optional[PrivateEndpointConnectionProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PrivateEndpointConnectionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitorworkspaces.models.PrivateEndpointConnectionProperties(_Model):
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


    class azure.mgmt.monitorworkspaces.models.PrivateEndpointConnectionProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.monitorworkspaces.models.PrivateEndpointServiceConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.monitorworkspaces.models.PrivateLinkServiceConnectionState(_Model):
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


    class azure.mgmt.monitorworkspaces.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.monitorworkspaces.models.PublicNetworkAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.monitorworkspaces.models.RelatedAlert(_Model):
        added_at: datetime
        id: str
        last_modified_at: datetime
        origin: Origin
        relevance: Union[str, Relevance]

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                relevance: Union[str, Relevance]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitorworkspaces.models.RelatedAlerts(_Model):
        value: list[RelatedAlert]

        @overload
        def __init__(
                self, 
                *, 
                value: list[RelatedAlert]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitorworkspaces.models.RelatedResource(_Model):
        added_at: datetime
        id: str
        last_modified_at: datetime
        origin: Origin
        relevance: Union[str, Relevance]

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                relevance: Union[str, Relevance]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitorworkspaces.models.RelatedResources(_Model):
        value: list[RelatedResource]

        @overload
        def __init__(
                self, 
                *, 
                value: list[RelatedResource]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitorworkspaces.models.Relevance(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IRRELEVANT = "Irrelevant"
        NONE = "None"
        RELEVANT = "Relevant"


    class azure.mgmt.monitorworkspaces.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.monitorworkspaces.models.ResourceProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.monitorworkspaces.models.Status(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CLOSED = "Closed"
        IN_PROGRESS = "InProgress"
        MITIGATED = "Mitigated"
        NEW = "New"


    class azure.mgmt.monitorworkspaces.models.SystemData(_Model):
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


    class azure.mgmt.monitorworkspaces.models.TimeBasedUpdatesNotificationType(IssueNotificationType, discriminator='TimeBased'):
        update_interval: str
        update_type: Literal[UpdateType.TIME_BASED]

        @overload
        def __init__(
                self, 
                *, 
                update_interval: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitorworkspaces.models.TraceAssociation(_Model):
        azure_monitor_workspace_resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                azure_monitor_workspace_resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitorworkspaces.models.TraceAssociationResource(ExtensionResource):
        id: str
        name: str
        properties: Optional[TraceAssociation]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[TraceAssociation] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitorworkspaces.models.TraceContainer(_Model):
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]
        trace_duration_window_in_seconds: int
        trace_metrics_state: Union[str, TraceMetricsState]
        trace_retention_in_days: int

        @overload
        def __init__(
                self, 
                *, 
                trace_duration_window_in_seconds: int, 
                trace_metrics_state: Union[str, TraceMetricsState], 
                trace_retention_in_days: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitorworkspaces.models.TraceContainerResource(ProxyResource):
        id: str
        name: str
        properties: Optional[TraceContainer]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[TraceContainer] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitorworkspaces.models.TraceMetricsState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.monitorworkspaces.models.TrackedResource(Resource):
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


    class azure.mgmt.monitorworkspaces.models.UpdateType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ISSUE_CREATION = "IssueCreation"
        ON_CHANGE = "OnChange"
        TIME_BASED = "TimeBased"


    class azure.mgmt.monitorworkspaces.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


namespace azure.mgmt.monitorworkspaces.operations

    class azure.mgmt.monitorworkspaces.operations.AzureMonitorWorkspacesOperations:

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
        def create_or_update(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                resource: AzureMonitorWorkspaceResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureMonitorWorkspaceResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                resource: AzureMonitorWorkspaceResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureMonitorWorkspaceResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                resource: IO[bytes], 
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
                properties: AzureMonitorWorkspaceResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureMonitorWorkspaceResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                properties: AzureMonitorWorkspaceResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureMonitorWorkspaceResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureMonitorWorkspaceResource: ...


    class azure.mgmt.monitorworkspaces.operations.IssueOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def add_investigation_result(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                issue_name: str, 
                body: InvestigationResult, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> InvestigationResult: ...

        @overload
        def add_investigation_result(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                issue_name: str, 
                body: InvestigationResult, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> InvestigationResult: ...

        @overload
        def add_investigation_result(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                issue_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> InvestigationResult: ...

        @overload
        def add_or_update_alerts(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                issue_name: str, 
                body: RelatedAlerts, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RelatedAlerts: ...

        @overload
        def add_or_update_alerts(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                issue_name: str, 
                body: RelatedAlerts, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RelatedAlerts: ...

        @overload
        def add_or_update_alerts(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                issue_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RelatedAlerts: ...

        @overload
        def add_or_update_resources(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                issue_name: str, 
                body: RelatedResources, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RelatedResources: ...

        @overload
        def add_or_update_resources(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                issue_name: str, 
                body: RelatedResources, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RelatedResources: ...

        @overload
        def add_or_update_resources(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                issue_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RelatedResources: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                issue_name: str, 
                resource: IssueResource, 
                *, 
                content_type: str = "application/json", 
                related: Optional[str] = ..., 
                **kwargs: Any
            ) -> IssueResource: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                issue_name: str, 
                resource: IssueResource, 
                *, 
                content_type: str = "application/json", 
                related: Optional[str] = ..., 
                **kwargs: Any
            ) -> IssueResource: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                issue_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                related: Optional[str] = ..., 
                **kwargs: Any
            ) -> IssueResource: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                issue_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-03-preview', params_added_on={'2025-10-03-preview': ['api_version', 'subscription_id', 'resource_group_name', 'azure_monitor_workspace_name', 'issue_name', 'accept']}, api_versions_list=['2025-10-03-preview', '2025-10-03', '2026-09-03-preview'])
        def fetch_background_visualization(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                issue_name: str, 
                **kwargs: Any
            ) -> BackgroundVisualization: ...

        @overload
        def fetch_investigation_result(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                issue_name: str, 
                body: FetchInvestigationResultParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> InvestigationResult: ...

        @overload
        def fetch_investigation_result(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                issue_name: str, 
                body: FetchInvestigationResultParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> InvestigationResult: ...

        @overload
        def fetch_investigation_result(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                issue_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> InvestigationResult: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                issue_name: str, 
                **kwargs: Any
            ) -> IssueResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[IssueResource]: ...

        @overload
        def list_alerts(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                issue_name: str, 
                body: ListParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PagedRelatedAlert: ...

        @overload
        def list_alerts(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                issue_name: str, 
                body: ListParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PagedRelatedAlert: ...

        @overload
        def list_alerts(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                issue_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PagedRelatedAlert: ...

        @overload
        def list_resources(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                issue_name: str, 
                body: ListParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PagedRelatedResource: ...

        @overload
        def list_resources(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                issue_name: str, 
                body: ListParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PagedRelatedResource: ...

        @overload
        def list_resources(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                issue_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PagedRelatedResource: ...

        @overload
        def set_background_visualization(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                issue_name: str, 
                body: BackgroundVisualization, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def set_background_visualization(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                issue_name: str, 
                body: BackgroundVisualization, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def set_background_visualization(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                issue_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                issue_name: str, 
                properties: IssueResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IssueResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                issue_name: str, 
                properties: IssueResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IssueResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                issue_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IssueResource: ...


    class azure.mgmt.monitorworkspaces.operations.MetricConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                metrics_container_name: str, 
                encoded_metric_namespace: str, 
                encoded_metric_name: str, 
                resource: MetricConfigurationResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MetricConfigurationResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                metrics_container_name: str, 
                encoded_metric_namespace: str, 
                encoded_metric_name: str, 
                resource: MetricConfigurationResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MetricConfigurationResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                metrics_container_name: str, 
                encoded_metric_namespace: str, 
                encoded_metric_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MetricConfigurationResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-09-03-preview', params_added_on={'2026-09-03-preview': ['api_version', 'subscription_id', 'resource_group_name', 'azure_monitor_workspace_name', 'metrics_container_name', 'encoded_metric_namespace', 'encoded_metric_name']}, api_versions_list=['2026-09-03-preview'])
        def delete(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                metrics_container_name: str, 
                encoded_metric_namespace: str, 
                encoded_metric_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-09-03-preview', params_added_on={'2026-09-03-preview': ['api_version', 'subscription_id', 'resource_group_name', 'azure_monitor_workspace_name', 'metrics_container_name', 'encoded_metric_namespace', 'encoded_metric_name', 'accept']}, api_versions_list=['2026-09-03-preview'])
        def get(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                metrics_container_name: str, 
                encoded_metric_namespace: str, 
                encoded_metric_name: str, 
                **kwargs: Any
            ) -> MetricConfigurationResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-09-03-preview', params_added_on={'2026-09-03-preview': ['api_version', 'subscription_id', 'resource_group_name', 'azure_monitor_workspace_name', 'metrics_container_name', 'encoded_metric_namespace', 'filter', 'accept']}, api_versions_list=['2026-09-03-preview'])
        def list_by_metric_namespace(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                metrics_container_name: str, 
                encoded_metric_namespace: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[MetricConfigurationResource]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-09-03-preview', params_added_on={'2026-09-03-preview': ['api_version', 'subscription_id', 'resource_group_name', 'azure_monitor_workspace_name', 'metrics_container_name', 'filter', 'accept']}, api_versions_list=['2026-09-03-preview'])
        def list_by_metrics_container(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                metrics_container_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[MetricConfigurationResource]: ...


    class azure.mgmt.monitorworkspaces.operations.MetricNamespacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-09-03-preview', params_added_on={'2026-09-03-preview': ['api_version', 'subscription_id', 'resource_group_name', 'azure_monitor_workspace_name', 'metrics_container_name', 'encoded_metric_namespace', 'accept']}, api_versions_list=['2026-09-03-preview'])
        def get(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                metrics_container_name: str, 
                encoded_metric_namespace: str, 
                **kwargs: Any
            ) -> MetricNamespaceResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-09-03-preview', params_added_on={'2026-09-03-preview': ['api_version', 'subscription_id', 'resource_group_name', 'azure_monitor_workspace_name', 'metrics_container_name', 'accept']}, api_versions_list=['2026-09-03-preview'])
        def list_by_metrics_container(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                metrics_container_name: str, 
                **kwargs: Any
            ) -> ItemPaged[MetricNamespaceResource]: ...


    class azure.mgmt.monitorworkspaces.operations.MetricsContainersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                metrics_container_name: str, 
                resource: MetricsContainerResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MetricsContainerResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                metrics_container_name: str, 
                resource: MetricsContainerResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MetricsContainerResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                metrics_container_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MetricsContainerResource: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                metrics_container_name: str, 
                **kwargs: Any
            ) -> MetricsContainerResource: ...

        @distributed_trace
        def list_by_azure_monitor_workspace(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[MetricsContainerResource]: ...


    class azure.mgmt.monitorworkspaces.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.monitorworkspaces.operations.TraceAssociationsAtResourceGroupOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                resource: TraceAssociationResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TraceAssociationResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                resource: TraceAssociationResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TraceAssociationResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TraceAssociationResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-09-03-preview', params_added_on={'2026-09-03-preview': ['api_version', 'subscription_id', 'resource_group_name']}, api_versions_list=['2026-09-03-preview'])
        def delete(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-09-03-preview', params_added_on={'2026-09-03-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2026-09-03-preview'])
        def get(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> TraceAssociationResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-09-03-preview', params_added_on={'2026-09-03-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2026-09-03-preview'])
        def list(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[TraceAssociationResource]: ...


    class azure.mgmt.monitorworkspaces.operations.TraceAssociationsAtSubscriptionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource: TraceAssociationResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TraceAssociationResource: ...

        @overload
        def create_or_update(
                self, 
                resource: TraceAssociationResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TraceAssociationResource: ...

        @overload
        def create_or_update(
                self, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TraceAssociationResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-09-03-preview', params_added_on={'2026-09-03-preview': ['api_version', 'subscription_id']}, api_versions_list=['2026-09-03-preview'])
        def delete(self, **kwargs: Any) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-09-03-preview', params_added_on={'2026-09-03-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2026-09-03-preview'])
        def get(self, **kwargs: Any) -> TraceAssociationResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-09-03-preview', params_added_on={'2026-09-03-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2026-09-03-preview'])
        def list(self, **kwargs: Any) -> ItemPaged[TraceAssociationResource]: ...


    class azure.mgmt.monitorworkspaces.operations.TraceAssociationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                provider_type: str, 
                resource_name: str, 
                resource: TraceAssociationResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TraceAssociationResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                provider_type: str, 
                resource_name: str, 
                resource: TraceAssociationResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TraceAssociationResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                provider_type: str, 
                resource_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TraceAssociationResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-09-03-preview', params_added_on={'2026-09-03-preview': ['api_version', 'subscription_id', 'resource_group_name', 'provider_name', 'provider_type', 'resource_name']}, api_versions_list=['2026-09-03-preview'])
        def delete(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                provider_type: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-09-03-preview', params_added_on={'2026-09-03-preview': ['api_version', 'subscription_id', 'resource_group_name', 'provider_name', 'provider_type', 'resource_name', 'accept']}, api_versions_list=['2026-09-03-preview'])
        def get(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                provider_type: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> TraceAssociationResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-09-03-preview', params_added_on={'2026-09-03-preview': ['api_version', 'subscription_id', 'resource_group_name', 'provider_name', 'provider_type', 'resource_name', 'accept']}, api_versions_list=['2026-09-03-preview'])
        def list(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                provider_type: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ItemPaged[TraceAssociationResource]: ...


    class azure.mgmt.monitorworkspaces.operations.TraceContainersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                resource: TraceContainerResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TraceContainerResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                resource: TraceContainerResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TraceContainerResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TraceContainerResource]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-09-03-preview', params_added_on={'2026-09-03-preview': ['api_version', 'subscription_id', 'resource_group_name', 'azure_monitor_workspace_name']}, api_versions_list=['2026-09-03-preview'])
        def delete(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-09-03-preview', params_added_on={'2026-09-03-preview': ['api_version', 'subscription_id', 'resource_group_name', 'azure_monitor_workspace_name', 'accept']}, api_versions_list=['2026-09-03-preview'])
        def get(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                **kwargs: Any
            ) -> TraceContainerResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-09-03-preview', params_added_on={'2026-09-03-preview': ['api_version', 'subscription_id', 'resource_group_name', 'azure_monitor_workspace_name', 'accept']}, api_versions_list=['2026-09-03-preview'])
        def list_by_azure_monitor_workspace(
                self, 
                resource_group_name: str, 
                azure_monitor_workspace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[TraceContainerResource]: ...


namespace azure.mgmt.monitorworkspaces.types

    class azure.mgmt.monitorworkspaces.types.AzureMonitorWorkspace(TypedDict, total=False):
        key "accountId": str
        key "actions": ForwardRef('AzureMonitorWorkspaceActions', module='types')
        key "defaultIngestionSettings": ForwardRef('AzureMonitorWorkspaceDefaultIngestionSettings', module='types')
        key "endpoints": ForwardRef('AzureMonitorWorkspaceEndpoints', module='types')
        key "metrics": ForwardRef('AzureMonitorWorkspaceMetrics', module='types')
        key "provisioningState": Union[str, ResourceProvisioningState]
        key "publicNetworkAccess": Union[str, PublicNetworkAccess]
        accountId: str
        actions: AzureMonitorWorkspaceActions
        defaultIngestionSettings: AzureMonitorWorkspaceDefaultIngestionSettings
        endpoints: AzureMonitorWorkspaceEndpoints
        metrics: AzureMonitorWorkspaceMetrics
        privateEndpointConnections: list[PrivateEndpointConnection]
        provisioningState: Union[str, ResourceProvisioningState]
        publicNetworkAccess: Union[str, PublicNetworkAccess]


    class azure.mgmt.monitorworkspaces.types.AzureMonitorWorkspaceActions(TypedDict, total=False):
        defaultActionGroups: list[DefaultActionGroupResource]


    class azure.mgmt.monitorworkspaces.types.AzureMonitorWorkspaceDefaultIngestionSettings(TypedDict, total=False):
        key "dataCollectionEndpointResourceId": str
        key "dataCollectionRuleImmutableId": str
        key "dataCollectionRuleResourceId": str
        key "ingestionEndpoints": ForwardRef('IngestionEndpoints', module='types')
        dataCollectionEndpointResourceId: str
        dataCollectionRuleImmutableId: str
        dataCollectionRuleResourceId: str
        ingestionEndpoints: IngestionEndpoints


    class azure.mgmt.monitorworkspaces.types.AzureMonitorWorkspaceEndpoints(TypedDict, total=False):
        key "query": str
        query: str


    class azure.mgmt.monitorworkspaces.types.AzureMonitorWorkspaceMetrics(TypedDict, total=False):
        key "enableAccessUsingResourcePermissions": bool
        key "internalId": str
        key "prometheusQueryEndpoint": str
        enableAccessUsingResourcePermissions: bool
        internalId: str
        prometheusQueryEndpoint: str


    class azure.mgmt.monitorworkspaces.types.AzureMonitorWorkspaceResource(TrackedResource):
        key "etag": str
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('AzureMonitorWorkspace', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: AzureMonitorWorkspace
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.monitorworkspaces.types.AzureMonitorWorkspaceResourceUpdate(TypedDict, total=False):
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "properties": ForwardRef('AzureMonitorWorkspace', module='types')
        identity: ManagedServiceIdentity
        properties: AzureMonitorWorkspace
        tags: dict[str, str]


    class azure.mgmt.monitorworkspaces.types.Background(TypedDict, total=False):
        key "text": str
        key "type": str
        details: list[BackgroundDetails]
        text: str
        type: str


    class azure.mgmt.monitorworkspaces.types.BackgroundDetails(TypedDict, total=False):
        key "name": Required[str]
        key "value": Required[str]
        name: str
        value: str


    class azure.mgmt.monitorworkspaces.types.BackgroundVisualization(TypedDict, total=False):
        key "origin": Required[Origin]
        key "visualization": Required[str]
        origin: Origin
        visualization: str


    class azure.mgmt.monitorworkspaces.types.DefaultActionGroupResource(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.monitorworkspaces.types.ExtensionResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.monitorworkspaces.types.FetchInvestigationResultParameters(TypedDict, total=False):
        key "investigationId": Required[str]
        investigationId: str


    class azure.mgmt.monitorworkspaces.types.IngestionEndpoints(TypedDict, total=False):
        key "metrics": str
        metrics: str


    class azure.mgmt.monitorworkspaces.types.InvestigationMetadata(TypedDict, total=False):
        key "createdAt": Required[str]
        key "id": Required[str]
        createdAt: str
        id: str


    class azure.mgmt.monitorworkspaces.types.InvestigationResult(TypedDict, total=False):
        key "createdAt": str
        key "id": Required[str]
        key "lastModifiedAt": str
        key "origin": ForwardRef('Origin', module='types')
        key "result": Required[str]
        createdAt: str
        id: str
        lastModifiedAt: str
        origin: Origin
        result: str


    class azure.mgmt.monitorworkspaces.types.IssueCreationNotificationType(TypedDict, total=False):
        key "updateType": Required[Literal[UpdateType.ISSUE_CREATION]]
        updateType: Literal[UpdateType.ISSUE_CREATION]


    class azure.mgmt.monitorworkspaces.types.IssueProperties(TypedDict, total=False):
        key "background": ForwardRef('Background', module='types')
        key "impactTime": Required[str]
        key "investigations": Required[list[InvestigationMetadata]]
        key "investigationsCount": Required[int]
        key "notifications": ForwardRef('Notifications', module='types')
        key "provisioningState": Union[str, ResourceProvisioningState]
        key "severity": Required[str]
        key "status": Required[Union[str, Status]]
        key "title": Required[str]
        background: Background
        impactTime: str
        investigations: list[InvestigationMetadata]
        investigationsCount: int
        notifications: Notifications
        provisioningState: Union[str, ResourceProvisioningState]
        severity: str
        status: Union[str, Status]
        title: str


    class azure.mgmt.monitorworkspaces.types.IssuePropertiesUpdate(TypedDict, total=False):
        key "background": ForwardRef('Background', module='types')
        key "impactTime": str
        key "notifications": ForwardRef('Notifications', module='types')
        key "severity": str
        key "status": Union[str, Status]
        key "title": str
        background: Background
        impactTime: str
        notifications: Notifications
        severity: str
        status: Union[str, Status]
        title: str


    class azure.mgmt.monitorworkspaces.types.IssueResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('IssueProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: IssueProperties
        systemData: SystemData
        type: str


    class azure.mgmt.monitorworkspaces.types.IssueResourceUpdate(TypedDict, total=False):
        key "properties": ForwardRef('IssuePropertiesUpdate', module='types')
        properties: IssuePropertiesUpdate


    class azure.mgmt.monitorworkspaces.types.ListParameter(TypedDict, total=False):
        key "filter": str
        filter: str


    class azure.mgmt.monitorworkspaces.types.ManagedServiceIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Required[Union[str, ManagedServiceIdentityType]]
        principalId: str
        tenantId: str
        type: Union[str, ManagedServiceIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentity]


    class azure.mgmt.monitorworkspaces.types.MetricAggregationConfiguration(TypedDict, total=False):
        key "aggregationFunctions": ForwardRef('MetricAggregationFunctions', module='types')
        key "storeAggregatedData": bool
        aggregationFunctions: MetricAggregationFunctions
        dimensions: list[str]
        storeAggregatedData: bool


    class azure.mgmt.monitorworkspaces.types.MetricAggregationFunctions(TypedDict, total=False):
        key "enableMinMax": Required[bool]
        key "enablePercentiles": Required[bool]
        enableMinMax: bool
        enablePercentiles: bool


    class azure.mgmt.monitorworkspaces.types.MetricConfigurationProperties(TypedDict, total=False):
        key "metricName": str
        key "metricType": Union[str, MetricConfigurationType]
        key "namespace": str
        key "provisioningState": Union[str, ResourceProvisioningState]
        key "sourceMetricResourceId": str
        key "storeRawData": bool
        aggregationConfigurations: list[MetricAggregationConfiguration]
        dimensions: list[str]
        metricName: str
        metricType: Union[str, MetricConfigurationType]
        namespace: str
        provisioningState: Union[str, ResourceProvisioningState]
        sourceMetricResourceId: str
        storeRawData: bool


    class azure.mgmt.monitorworkspaces.types.MetricConfigurationResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('MetricConfigurationProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: MetricConfigurationProperties
        systemData: SystemData
        type: str


    class azure.mgmt.monitorworkspaces.types.MetricsContainer(TypedDict, total=False):
        key "limits": ForwardRef('MetricsLimits', module='types')
        key "provisioningState": Union[str, ResourceProvisioningState]
        key "version": str
        limits: MetricsLimits
        provisioningState: Union[str, ResourceProvisioningState]
        version: str


    class azure.mgmt.monitorworkspaces.types.MetricsContainerResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('MetricsContainer', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: MetricsContainer
        systemData: SystemData
        type: str


    class azure.mgmt.monitorworkspaces.types.MetricsLimits(TypedDict, total=False):
        key "enableAutoScale": bool
        key "maxActiveTimeSeries": int
        key "maxEventsPerMinute": int
        enableAutoScale: bool
        maxActiveTimeSeries: int
        maxEventsPerMinute: int


    class azure.mgmt.monitorworkspaces.types.Notifications(TypedDict, total=False):
        key "excludeDefaultActionGroups": bool
        actionGroupIds: list[str]
        excludeDefaultActionGroups: bool
        updateTypes: list[IssueNotificationType]


    class azure.mgmt.monitorworkspaces.types.OnChangeNotificationType(TypedDict, total=False):
        key "updateType": Required[Literal[UpdateType.ON_CHANGE]]
        updateType: Literal[UpdateType.ON_CHANGE]


    class azure.mgmt.monitorworkspaces.types.Origin(TypedDict, total=False):
        key "addedBy": Required[str]
        key "addedByType": Required[Union[str, AddedByType]]
        addedBy: str
        addedByType: Union[str, AddedByType]


    class azure.mgmt.monitorworkspaces.types.PrivateEndpoint(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.monitorworkspaces.types.PrivateEndpointConnection(Resource):
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


    class azure.mgmt.monitorworkspaces.types.PrivateEndpointConnectionProperties(TypedDict, total=False):
        key "privateEndpoint": ForwardRef('PrivateEndpoint', module='types')
        key "privateLinkServiceConnectionState": Required[PrivateLinkServiceConnectionState]
        key "provisioningState": Union[str, PrivateEndpointConnectionProvisioningState]
        groupIds: list[str]
        privateEndpoint: PrivateEndpoint
        privateLinkServiceConnectionState: PrivateLinkServiceConnectionState
        provisioningState: Union[str, PrivateEndpointConnectionProvisioningState]


    class azure.mgmt.monitorworkspaces.types.PrivateLinkServiceConnectionState(TypedDict, total=False):
        key "actionsRequired": str
        key "description": str
        key "status": Union[str, PrivateEndpointServiceConnectionStatus]
        actionsRequired: str
        description: str
        status: Union[str, PrivateEndpointServiceConnectionStatus]


    class azure.mgmt.monitorworkspaces.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.monitorworkspaces.types.RelatedAlert(TypedDict, total=False):
        key "addedAt": Required[str]
        key "id": Required[str]
        key "lastModifiedAt": Required[str]
        key "origin": Required[Origin]
        key "relevance": Required[Union[str, Relevance]]
        addedAt: str
        id: str
        lastModifiedAt: str
        origin: Origin
        relevance: Union[str, Relevance]


    class azure.mgmt.monitorworkspaces.types.RelatedAlerts(TypedDict, total=False):
        key "value": Required[list[RelatedAlert]]
        value: list[RelatedAlert]


    class azure.mgmt.monitorworkspaces.types.RelatedResource(TypedDict, total=False):
        key "addedAt": Required[str]
        key "id": Required[str]
        key "lastModifiedAt": Required[str]
        key "origin": Required[Origin]
        key "relevance": Required[Union[str, Relevance]]
        addedAt: str
        id: str
        lastModifiedAt: str
        origin: Origin
        relevance: Union[str, Relevance]


    class azure.mgmt.monitorworkspaces.types.RelatedResources(TypedDict, total=False):
        key "value": Required[list[RelatedResource]]
        value: list[RelatedResource]


    class azure.mgmt.monitorworkspaces.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.monitorworkspaces.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.monitorworkspaces.types.TimeBasedUpdatesNotificationType(TypedDict, total=False):
        key "updateInterval": Required[str]
        key "updateType": Required[Literal[UpdateType.TIME_BASED]]
        updateInterval: str
        updateType: Literal[UpdateType.TIME_BASED]


    class azure.mgmt.monitorworkspaces.types.TraceAssociation(TypedDict, total=False):
        key "azureMonitorWorkspaceResourceId": Required[str]
        azureMonitorWorkspaceResourceId: str


    class azure.mgmt.monitorworkspaces.types.TraceAssociationResource(ExtensionResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('TraceAssociation', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: TraceAssociation
        systemData: SystemData
        type: str


    class azure.mgmt.monitorworkspaces.types.TraceContainer(TypedDict, total=False):
        key "provisioningState": Union[str, ResourceProvisioningState]
        key "traceDurationWindowInSeconds": Required[int]
        key "traceMetricsState": Required[Union[str, TraceMetricsState]]
        key "traceRetentionInDays": Required[int]
        provisioningState: Union[str, ResourceProvisioningState]
        traceDurationWindowInSeconds: int
        traceMetricsState: Union[str, TraceMetricsState]
        traceRetentionInDays: int


    class azure.mgmt.monitorworkspaces.types.TraceContainerResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('TraceContainer', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: TraceContainer
        systemData: SystemData
        type: str


    class azure.mgmt.monitorworkspaces.types.TrackedResource(Resource):
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


    class azure.mgmt.monitorworkspaces.types.UpdateType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ISSUE_CREATION = "IssueCreation"
        ON_CHANGE = "OnChange"
        TIME_BASED = "TimeBased"


    class azure.mgmt.monitorworkspaces.types.UserAssignedIdentity(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        clientId: str
        principalId: str


```