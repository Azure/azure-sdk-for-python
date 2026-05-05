```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.dashboard

    class azure.mgmt.dashboard.DashboardManagementClient: implements ContextManager 
        grafana: GrafanaOperations
        integration_fabrics: IntegrationFabricsOperations
        managed_dashboards: ManagedDashboardsOperations
        managed_private_endpoints: ManagedPrivateEndpointsOperations
        operations: Operations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations

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


namespace azure.mgmt.dashboard.aio

    class azure.mgmt.dashboard.aio.DashboardManagementClient: implements AsyncContextManager 
        grafana: GrafanaOperations
        integration_fabrics: IntegrationFabricsOperations
        managed_dashboards: ManagedDashboardsOperations
        managed_private_endpoints: ManagedPrivateEndpointsOperations
        operations: Operations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations

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


namespace azure.mgmt.dashboard.aio.operations

    class azure.mgmt.dashboard.aio.operations.GrafanaOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                request_body_parameters: ManagedGrafana, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedGrafana]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                request_body_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedGrafana]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                request_body_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedGrafana]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                request_body_parameters: ManagedGrafanaUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedGrafana]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                request_body_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedGrafana]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                request_body_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedGrafana]: ...

        @distributed_trace_async
        async def check_enterprise_details(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> EnterpriseDetails: ...

        @distributed_trace_async
        async def fetch_available_plugins(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> GrafanaAvailablePluginListResponse: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> ManagedGrafana: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[ManagedGrafana]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ManagedGrafana]: ...


    class azure.mgmt.dashboard.aio.operations.IntegrationFabricsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_fabric_name: str, 
                request_body_parameters: IntegrationFabric, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[IntegrationFabric]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_fabric_name: str, 
                request_body_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[IntegrationFabric]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_fabric_name: str, 
                request_body_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[IntegrationFabric]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_fabric_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_fabric_name: str, 
                request_body_parameters: IntegrationFabricUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[IntegrationFabric]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_fabric_name: str, 
                request_body_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[IntegrationFabric]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_fabric_name: str, 
                request_body_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[IntegrationFabric]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_fabric_name: str, 
                **kwargs: Any
            ) -> IntegrationFabric: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[IntegrationFabric]: ...


    class azure.mgmt.dashboard.aio.operations.ManagedDashboardsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                dashboard_name: str, 
                request_body_parameters: ManagedDashboard, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedDashboard]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                dashboard_name: str, 
                request_body_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedDashboard]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                dashboard_name: str, 
                request_body_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedDashboard]: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                dashboard_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                dashboard_name: str, 
                **kwargs: Any
            ) -> ManagedDashboard: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ManagedDashboard]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[ManagedDashboard]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                dashboard_name: str, 
                request_body_parameters: ManagedDashboardUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagedDashboard: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                dashboard_name: str, 
                request_body_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagedDashboard: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                dashboard_name: str, 
                request_body_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagedDashboard: ...


    class azure.mgmt.dashboard.aio.operations.ManagedPrivateEndpointsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                managed_private_endpoint_name: str, 
                request_body_parameters: ManagedPrivateEndpointModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedPrivateEndpointModel]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                managed_private_endpoint_name: str, 
                request_body_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedPrivateEndpointModel]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                managed_private_endpoint_name: str, 
                request_body_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedPrivateEndpointModel]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                managed_private_endpoint_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_refresh(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                managed_private_endpoint_name: str, 
                request_body_parameters: ManagedPrivateEndpointUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedPrivateEndpointModel]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                managed_private_endpoint_name: str, 
                request_body_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedPrivateEndpointModel]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                managed_private_endpoint_name: str, 
                request_body_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedPrivateEndpointModel]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                managed_private_endpoint_name: str, 
                **kwargs: Any
            ) -> ManagedPrivateEndpointModel: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ManagedPrivateEndpointModel]: ...


    class azure.mgmt.dashboard.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.dashboard.aio.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_approve(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                private_endpoint_connection_name: str, 
                body: Optional[PrivateEndpointConnection] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @overload
        async def begin_approve(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                private_endpoint_connection_name: str, 
                body: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @overload
        async def begin_approve(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                private_endpoint_connection_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateEndpointConnection]: ...


    class azure.mgmt.dashboard.aio.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                private_link_resource_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateLinkResource]: ...


namespace azure.mgmt.dashboard.models

    class azure.mgmt.dashboard.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.dashboard.models.ApiKey(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.dashboard.models.AutoGeneratedDomainNameLabelScope(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        TENANT_REUSE = "TenantReuse"


    class azure.mgmt.dashboard.models.AvailablePromotion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FREE_TRIAL = "FreeTrial"
        NONE = "None"


    class azure.mgmt.dashboard.models.AzureMonitorWorkspaceIntegration(_Model):
        azure_monitor_workspace_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                azure_monitor_workspace_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dashboard.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.dashboard.models.CreatorCanAdmin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.dashboard.models.DeterministicOutboundIP(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.dashboard.models.EnterpriseConfigurations(_Model):
        marketplace_auto_renew: Optional[Union[str, MarketplaceAutoRenew]]
        marketplace_plan_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                marketplace_auto_renew: Optional[Union[str, MarketplaceAutoRenew]] = ..., 
                marketplace_plan_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dashboard.models.EnterpriseDetails(_Model):
        marketplace_trial_quota: Optional[MarketplaceTrialQuota]
        saas_subscription_details: Optional[SaasSubscriptionDetails]

        @overload
        def __init__(
                self, 
                *, 
                marketplace_trial_quota: Optional[MarketplaceTrialQuota] = ..., 
                saas_subscription_details: Optional[SaasSubscriptionDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dashboard.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.dashboard.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.dashboard.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dashboard.models.GrafanaAvailablePlugin(_Model):
        author: Optional[str]
        name: Optional[str]
        plugin_id: Optional[str]
        type: Optional[str]


    class azure.mgmt.dashboard.models.GrafanaAvailablePluginListResponse(_Model):
        next_link: Optional[str]
        value: Optional[list[GrafanaAvailablePlugin]]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[list[GrafanaAvailablePlugin]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dashboard.models.GrafanaConfigurations(_Model):
        security: Optional[Security]
        smtp: Optional[Smtp]
        snapshots: Optional[Snapshots]
        unified_alerting_screenshots: Optional[UnifiedAlertingScreenshots]
        users: Optional[Users]

        @overload
        def __init__(
                self, 
                *, 
                security: Optional[Security] = ..., 
                smtp: Optional[Smtp] = ..., 
                snapshots: Optional[Snapshots] = ..., 
                unified_alerting_screenshots: Optional[UnifiedAlertingScreenshots] = ..., 
                users: Optional[Users] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dashboard.models.GrafanaIntegrations(_Model):
        azure_monitor_workspace_integrations: Optional[list[AzureMonitorWorkspaceIntegration]]

        @overload
        def __init__(
                self, 
                *, 
                azure_monitor_workspace_integrations: Optional[list[AzureMonitorWorkspaceIntegration]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dashboard.models.GrafanaPlugin(_Model):
        plugin_id: Optional[str]


    class azure.mgmt.dashboard.models.IntegrationFabric(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[IntegrationFabricProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[IntegrationFabricProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dashboard.models.IntegrationFabricProperties(_Model):
        data_source_resource_id: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        scenarios: Optional[list[str]]
        target_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                data_source_resource_id: Optional[str] = ..., 
                scenarios: Optional[list[str]] = ..., 
                target_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dashboard.models.IntegrationFabricPropertiesUpdateParameters(_Model):
        scenarios: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                scenarios: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dashboard.models.IntegrationFabricUpdateParameters(_Model):
        properties: Optional[IntegrationFabricPropertiesUpdateParameters]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[IntegrationFabricPropertiesUpdateParameters] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dashboard.models.ManagedDashboard(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[ManagedDashboardProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[ManagedDashboardProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.dashboard.models.ManagedDashboardProperties(_Model):
        provisioning_state: Optional[Union[str, ProvisioningState]]


    class azure.mgmt.dashboard.models.ManagedDashboardUpdateParameters(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dashboard.models.ManagedGrafana(ProxyResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: Optional[str]
        name: str
        properties: Optional[ManagedGrafanaProperties]
        sku: Optional[ResourceSku]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[ManagedGrafanaProperties] = ..., 
                sku: Optional[ResourceSku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dashboard.models.ManagedGrafanaProperties(_Model):
        api_key: Optional[Union[str, ApiKey]]
        auto_generated_domain_name_label_scope: Optional[Union[str, AutoGeneratedDomainNameLabelScope]]
        creator_can_admin: Optional[Union[str, CreatorCanAdmin]]
        deterministic_outbound_ip: Optional[Union[str, DeterministicOutboundIP]]
        endpoint: Optional[str]
        enterprise_configurations: Optional[EnterpriseConfigurations]
        grafana_configurations: Optional[GrafanaConfigurations]
        grafana_integrations: Optional[GrafanaIntegrations]
        grafana_major_version: Optional[str]
        grafana_plugins: Optional[dict[str, GrafanaPlugin]]
        grafana_version: Optional[str]
        outbound_i_ps: Optional[list[str]]
        private_endpoint_connections: Optional[list[PrivateEndpointConnection]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        public_network_access: Optional[Union[str, PublicNetworkAccess]]
        zone_redundancy: Optional[Union[str, ZoneRedundancy]]

        @overload
        def __init__(
                self, 
                *, 
                api_key: Optional[Union[str, ApiKey]] = ..., 
                auto_generated_domain_name_label_scope: Optional[Union[str, AutoGeneratedDomainNameLabelScope]] = ..., 
                creator_can_admin: Optional[Union[str, CreatorCanAdmin]] = ..., 
                deterministic_outbound_ip: Optional[Union[str, DeterministicOutboundIP]] = ..., 
                enterprise_configurations: Optional[EnterpriseConfigurations] = ..., 
                grafana_configurations: Optional[GrafanaConfigurations] = ..., 
                grafana_integrations: Optional[GrafanaIntegrations] = ..., 
                grafana_major_version: Optional[str] = ..., 
                grafana_plugins: Optional[dict[str, GrafanaPlugin]] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                zone_redundancy: Optional[Union[str, ZoneRedundancy]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dashboard.models.ManagedGrafanaPropertiesUpdateParameters(_Model):
        api_key: Optional[Union[str, ApiKey]]
        creator_can_admin: Optional[Union[str, CreatorCanAdmin]]
        deterministic_outbound_ip: Optional[Union[str, DeterministicOutboundIP]]
        enterprise_configurations: Optional[EnterpriseConfigurations]
        grafana_configurations: Optional[GrafanaConfigurations]
        grafana_integrations: Optional[GrafanaIntegrations]
        grafana_major_version: Optional[str]
        grafana_plugins: Optional[dict[str, GrafanaPlugin]]
        public_network_access: Optional[Union[str, PublicNetworkAccess]]
        zone_redundancy: Optional[Union[str, ZoneRedundancy]]

        @overload
        def __init__(
                self, 
                *, 
                api_key: Optional[Union[str, ApiKey]] = ..., 
                creator_can_admin: Optional[Union[str, CreatorCanAdmin]] = ..., 
                deterministic_outbound_ip: Optional[Union[str, DeterministicOutboundIP]] = ..., 
                enterprise_configurations: Optional[EnterpriseConfigurations] = ..., 
                grafana_configurations: Optional[GrafanaConfigurations] = ..., 
                grafana_integrations: Optional[GrafanaIntegrations] = ..., 
                grafana_major_version: Optional[str] = ..., 
                grafana_plugins: Optional[dict[str, GrafanaPlugin]] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                zone_redundancy: Optional[Union[str, ZoneRedundancy]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dashboard.models.ManagedGrafanaUpdateParameters(_Model):
        identity: Optional[ManagedServiceIdentity]
        properties: Optional[ManagedGrafanaPropertiesUpdateParameters]
        sku: Optional[ResourceSku]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                properties: Optional[ManagedGrafanaPropertiesUpdateParameters] = ..., 
                sku: Optional[ResourceSku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dashboard.models.ManagedPrivateEndpointConnectionState(_Model):
        description: Optional[str]
        status: Optional[Union[str, ManagedPrivateEndpointConnectionStatus]]


    class azure.mgmt.dashboard.models.ManagedPrivateEndpointConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        DISCONNECTED = "Disconnected"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.dashboard.models.ManagedPrivateEndpointModel(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[ManagedPrivateEndpointModelProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[ManagedPrivateEndpointModelProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.dashboard.models.ManagedPrivateEndpointModelProperties(_Model):
        connection_state: Optional[ManagedPrivateEndpointConnectionState]
        group_ids: Optional[list[str]]
        private_link_resource_id: Optional[str]
        private_link_resource_region: Optional[str]
        private_link_service_private_ip: Optional[str]
        private_link_service_url: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        request_message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                group_ids: Optional[list[str]] = ..., 
                private_link_resource_id: Optional[str] = ..., 
                private_link_resource_region: Optional[str] = ..., 
                private_link_service_url: Optional[str] = ..., 
                request_message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dashboard.models.ManagedPrivateEndpointUpdateParameters(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dashboard.models.ManagedServiceIdentity(_Model):
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


    class azure.mgmt.dashboard.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.dashboard.models.MarketplaceAutoRenew(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.dashboard.models.MarketplaceTrialQuota(_Model):
        available_promotion: Optional[Union[str, AvailablePromotion]]
        grafana_resource_id: Optional[str]
        trial_end_at: Optional[datetime]
        trial_start_at: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                available_promotion: Optional[Union[str, AvailablePromotion]] = ..., 
                grafana_resource_id: Optional[str] = ..., 
                trial_end_at: Optional[datetime] = ..., 
                trial_start_at: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dashboard.models.Operation(_Model):
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


    class azure.mgmt.dashboard.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.dashboard.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.dashboard.models.PrivateEndpoint(_Model):
        id: Optional[str]


    class azure.mgmt.dashboard.models.PrivateEndpointConnection(ProxyResource):
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


    class azure.mgmt.dashboard.models.PrivateEndpointConnectionProperties(_Model):
        group_ids: Optional[list[str]]
        private_endpoint: Optional[PrivateEndpoint]
        private_link_service_connection_state: PrivateLinkServiceConnectionState
        provisioning_state: Optional[Union[str, PrivateEndpointConnectionProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                group_ids: Optional[list[str]] = ..., 
                private_endpoint: Optional[PrivateEndpoint] = ..., 
                private_link_service_connection_state: PrivateLinkServiceConnectionState
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dashboard.models.PrivateEndpointConnectionProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.dashboard.models.PrivateEndpointServiceConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.dashboard.models.PrivateLinkResource(ProxyResource):
        id: str
        name: str
        properties: Optional[PrivateLinkResourceProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PrivateLinkResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.dashboard.models.PrivateLinkResourceProperties(_Model):
        group_id: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
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


    class azure.mgmt.dashboard.models.PrivateLinkServiceConnectionState(_Model):
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


    class azure.mgmt.dashboard.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETED = "Deleted"
        DELETING = "Deleting"
        FAILED = "Failed"
        NOT_SPECIFIED = "NotSpecified"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.dashboard.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.dashboard.models.PublicNetworkAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.dashboard.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.dashboard.models.ResourceSku(_Model):
        name: str
        size: Optional[Union[str, Size]]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                size: Optional[Union[str, Size]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dashboard.models.SaasSubscriptionDetails(_Model):
        offer_id: Optional[str]
        plan_id: Optional[str]
        publisher_id: Optional[str]
        term: Optional[SubscriptionTerm]

        @overload
        def __init__(
                self, 
                *, 
                offer_id: Optional[str] = ..., 
                plan_id: Optional[str] = ..., 
                publisher_id: Optional[str] = ..., 
                term: Optional[SubscriptionTerm] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dashboard.models.Security(_Model):
        csrf_always_check: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                csrf_always_check: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dashboard.models.Size(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        X1 = "X1"
        X2 = "X2"


    class azure.mgmt.dashboard.models.Smtp(_Model):
        enabled: Optional[bool]
        from_address: Optional[str]
        from_name: Optional[str]
        host: Optional[str]
        password: Optional[str]
        skip_verify: Optional[bool]
        start_tls_policy: Optional[Union[str, StartTLSPolicy]]
        user: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                from_address: Optional[str] = ..., 
                from_name: Optional[str] = ..., 
                host: Optional[str] = ..., 
                password: Optional[str] = ..., 
                skip_verify: Optional[bool] = ..., 
                start_tls_policy: Optional[Union[str, StartTLSPolicy]] = ..., 
                user: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dashboard.models.Snapshots(_Model):
        external_enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                external_enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dashboard.models.StartTLSPolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MANDATORY_START_TLS = "MandatoryStartTLS"
        NO_START_TLS = "NoStartTLS"
        OPPORTUNISTIC_START_TLS = "OpportunisticStartTLS"


    class azure.mgmt.dashboard.models.SubscriptionTerm(_Model):
        end_date: Optional[datetime]
        start_date: Optional[datetime]
        term_unit: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                end_date: Optional[datetime] = ..., 
                start_date: Optional[datetime] = ..., 
                term_unit: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dashboard.models.SystemData(_Model):
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


    class azure.mgmt.dashboard.models.TrackedResource(Resource):
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


    class azure.mgmt.dashboard.models.UnifiedAlertingScreenshots(_Model):
        capture_enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                capture_enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dashboard.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.dashboard.models.Users(_Model):
        editors_can_admin: Optional[bool]
        viewers_can_edit: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                editors_can_admin: Optional[bool] = ..., 
                viewers_can_edit: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dashboard.models.ZoneRedundancy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


namespace azure.mgmt.dashboard.operations

    class azure.mgmt.dashboard.operations.GrafanaOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                request_body_parameters: ManagedGrafana, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedGrafana]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                request_body_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedGrafana]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                request_body_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedGrafana]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                request_body_parameters: ManagedGrafanaUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedGrafana]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                request_body_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedGrafana]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                request_body_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedGrafana]: ...

        @distributed_trace
        def check_enterprise_details(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> EnterpriseDetails: ...

        @distributed_trace
        def fetch_available_plugins(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> GrafanaAvailablePluginListResponse: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> ManagedGrafana: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[ManagedGrafana]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ManagedGrafana]: ...


    class azure.mgmt.dashboard.operations.IntegrationFabricsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_fabric_name: str, 
                request_body_parameters: IntegrationFabric, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[IntegrationFabric]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_fabric_name: str, 
                request_body_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[IntegrationFabric]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_fabric_name: str, 
                request_body_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[IntegrationFabric]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_fabric_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_fabric_name: str, 
                request_body_parameters: IntegrationFabricUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[IntegrationFabric]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_fabric_name: str, 
                request_body_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[IntegrationFabric]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_fabric_name: str, 
                request_body_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[IntegrationFabric]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_fabric_name: str, 
                **kwargs: Any
            ) -> IntegrationFabric: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[IntegrationFabric]: ...


    class azure.mgmt.dashboard.operations.ManagedDashboardsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                dashboard_name: str, 
                request_body_parameters: ManagedDashboard, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedDashboard]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                dashboard_name: str, 
                request_body_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedDashboard]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                dashboard_name: str, 
                request_body_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedDashboard]: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                dashboard_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                dashboard_name: str, 
                **kwargs: Any
            ) -> ManagedDashboard: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ManagedDashboard]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[ManagedDashboard]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                dashboard_name: str, 
                request_body_parameters: ManagedDashboardUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagedDashboard: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                dashboard_name: str, 
                request_body_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagedDashboard: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                dashboard_name: str, 
                request_body_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagedDashboard: ...


    class azure.mgmt.dashboard.operations.ManagedPrivateEndpointsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                managed_private_endpoint_name: str, 
                request_body_parameters: ManagedPrivateEndpointModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedPrivateEndpointModel]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                managed_private_endpoint_name: str, 
                request_body_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedPrivateEndpointModel]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                managed_private_endpoint_name: str, 
                request_body_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedPrivateEndpointModel]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                managed_private_endpoint_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_refresh(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                managed_private_endpoint_name: str, 
                request_body_parameters: ManagedPrivateEndpointUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedPrivateEndpointModel]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                managed_private_endpoint_name: str, 
                request_body_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedPrivateEndpointModel]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                managed_private_endpoint_name: str, 
                request_body_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedPrivateEndpointModel]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                managed_private_endpoint_name: str, 
                **kwargs: Any
            ) -> ManagedPrivateEndpointModel: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ManagedPrivateEndpointModel]: ...


    class azure.mgmt.dashboard.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.dashboard.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_approve(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                private_endpoint_connection_name: str, 
                body: Optional[PrivateEndpointConnection] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @overload
        def begin_approve(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                private_endpoint_connection_name: str, 
                body: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @overload
        def begin_approve(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                private_endpoint_connection_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PrivateEndpointConnection]: ...


    class azure.mgmt.dashboard.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                private_link_resource_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PrivateLinkResource]: ...


```