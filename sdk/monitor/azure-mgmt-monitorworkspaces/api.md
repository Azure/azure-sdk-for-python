```py
namespace azure.mgmt.monitorworkspaces

    class azure.mgmt.monitorworkspaces.MonitorWorkspacesMgmtClient: implements ContextManager 
        azure_monitor_workspaces: AzureMonitorWorkspacesOperations
        issue: IssueOperations
        metrics_containers: MetricsContainersOperations
        operations: Operations

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
        metrics_containers: MetricsContainersOperations
        operations: Operations

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
                resource: JSON, 
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
                properties: JSON, 
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
                body: JSON, 
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
                body: JSON, 
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
                body: JSON, 
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
                resource: JSON, 
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
        @api_version_validation(method_added_on='2025-10-03-preview', params_added_on={'2025-10-03-preview': ['api_version', 'subscription_id', 'resource_group_name', 'azure_monitor_workspace_name', 'issue_name', 'accept']}, api_versions_list=['2025-10-03-preview', '2025-10-03'])
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
                body: JSON, 
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
                body: JSON, 
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
                body: JSON, 
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
                body: JSON, 
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
                properties: JSON, 
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
                resource: JSON, 
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
        default_ingestion_settings: Optional[AzureMonitorWorkspaceDefaultIngestionSettings]
        metrics: Optional[AzureMonitorWorkspaceMetrics]
        private_endpoint_connections: Optional[list[PrivateEndpointConnection]]
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]
        public_network_access: Optional[Union[str, PublicNetworkAccess]]

        @overload
        def __init__(
                self, 
                *, 
                metrics: Optional[AzureMonitorWorkspaceMetrics] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitorworkspaces.models.AzureMonitorWorkspaceDefaultIngestionSettings(_Model):
        data_collection_endpoint_resource_id: Optional[str]
        data_collection_rule_immutable_id: Optional[str]
        data_collection_rule_resource_id: Optional[str]
        ingestion_endpoints: Optional[IngestionEndpoints]


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


    class azure.mgmt.monitorworkspaces.models.MetricsContainer(_Model):
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
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
                resource: JSON, 
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
                properties: JSON, 
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
                body: JSON, 
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
                body: JSON, 
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
                body: JSON, 
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
                resource: JSON, 
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
        @api_version_validation(method_added_on='2025-10-03-preview', params_added_on={'2025-10-03-preview': ['api_version', 'subscription_id', 'resource_group_name', 'azure_monitor_workspace_name', 'issue_name', 'accept']}, api_versions_list=['2025-10-03-preview', '2025-10-03'])
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
                body: JSON, 
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
                body: JSON, 
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
                body: JSON, 
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
                body: JSON, 
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
                properties: JSON, 
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
                resource: JSON, 
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


```