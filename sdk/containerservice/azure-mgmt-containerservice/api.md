```py
namespace azure.mgmt.containerservice

    class azure.mgmt.containerservice.ContainerServiceClient: implements ContextManager 
        agent_pools: AgentPoolsOperations
        alert_configurations: AlertConfigurationsOperations
        container_service: ContainerServiceOperations
        identity_bindings: IdentityBindingsOperations
        jwt_authenticators: JWTAuthenticatorsOperations
        load_balancers: LoadBalancersOperations
        machines: MachinesOperations
        maintenance_configurations: MaintenanceConfigurationsOperations
        maintenance_windows: MaintenanceWindowsOperations
        managed_cluster_snapshots: ManagedClusterSnapshotsOperations
        managed_clusters: ManagedClustersOperations
        managed_namespaces: ManagedNamespacesOperations
        mesh_memberships: MeshMembershipsOperations
        operation_status_result: OperationStatusResultOperations
        operations: Operations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        resolve_private_link_service_id: ResolvePrivateLinkServiceIdOperations
        snapshots: SnapshotsOperations
        trusted_access_role_bindings: TrustedAccessRoleBindingsOperations
        trusted_access_roles: TrustedAccessRolesOperations
        vm_skus: VmSkusOperations

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


namespace azure.mgmt.containerservice.aio

    class azure.mgmt.containerservice.aio.ContainerServiceClient: implements AsyncContextManager 
        agent_pools: AgentPoolsOperations
        alert_configurations: AlertConfigurationsOperations
        container_service: ContainerServiceOperations
        identity_bindings: IdentityBindingsOperations
        jwt_authenticators: JWTAuthenticatorsOperations
        load_balancers: LoadBalancersOperations
        machines: MachinesOperations
        maintenance_configurations: MaintenanceConfigurationsOperations
        maintenance_windows: MaintenanceWindowsOperations
        managed_cluster_snapshots: ManagedClusterSnapshotsOperations
        managed_clusters: ManagedClustersOperations
        managed_namespaces: ManagedNamespacesOperations
        mesh_memberships: MeshMembershipsOperations
        operation_status_result: OperationStatusResultOperations
        operations: Operations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        resolve_private_link_service_id: ResolvePrivateLinkServiceIdOperations
        snapshots: SnapshotsOperations
        trusted_access_role_bindings: TrustedAccessRoleBindingsOperations
        trusted_access_roles: TrustedAccessRolesOperations
        vm_skus: VmSkusOperations

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


namespace azure.mgmt.containerservice.aio.operations

    class azure.mgmt.containerservice.aio.operations.AgentPoolsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_abort_latest_operation(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                agent_pool_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'resource_name', 'agent_pool_name']}, api_versions_list=['2026-05-02-preview'])
        async def begin_complete_upgrade(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                agent_pool_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                agent_pool_name: str, 
                parameters: AgentPool, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[AgentPool]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                agent_pool_name: str, 
                parameters: AgentPool, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[AgentPool]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                agent_pool_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[AgentPool]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                agent_pool_name: str, 
                *, 
                etag: Optional[str] = ..., 
                ignore_pod_disruption_budget: Optional[bool] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_delete_machines(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                agent_pool_name: str, 
                machines: AgentPoolDeleteMachinesParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_delete_machines(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                agent_pool_name: str, 
                machines: AgentPoolDeleteMachinesParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_delete_machines(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                agent_pool_name: str, 
                machines: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_upgrade_node_image_version(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                agent_pool_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                agent_pool_name: str, 
                **kwargs: Any
            ) -> AgentPool: ...

        @distributed_trace_async
        async def get_available_agent_pool_versions(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AgentPoolAvailableVersions: ...

        @distributed_trace_async
        async def get_upgrade_profile(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                agent_pool_name: str, 
                **kwargs: Any
            ) -> AgentPoolUpgradeProfile: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AgentPool]: ...

        @overload
        async def list_bootstrap_data(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                agent_pool_name: str, 
                body: ListBootstrapDataRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PoolBootstrapData: ...

        @overload
        async def list_bootstrap_data(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                agent_pool_name: str, 
                body: ListBootstrapDataRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PoolBootstrapData: ...

        @overload
        async def list_bootstrap_data(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                agent_pool_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PoolBootstrapData: ...


    class azure.mgmt.containerservice.aio.operations.AlertConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                configuration_name: str, 
                resource: AlertConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AlertConfiguration]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                configuration_name: str, 
                resource: AlertConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AlertConfiguration]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                configuration_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AlertConfiguration]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'resource_name', 'configuration_name']}, api_versions_list=['2026-05-02-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                configuration_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'resource_name', 'configuration_name', 'accept']}, api_versions_list=['2026-05-02-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                configuration_name: str, 
                **kwargs: Any
            ) -> AlertConfiguration: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'resource_name', 'accept']}, api_versions_list=['2026-05-02-preview'])
        def list_by_managed_cluster(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AlertConfiguration]: ...


    class azure.mgmt.containerservice.aio.operations.ContainerServiceOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_node_image_versions(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[NodeImageVersion]: ...


    class azure.mgmt.containerservice.aio.operations.IdentityBindingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                identity_binding_name: str, 
                parameters: IdentityBinding, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[IdentityBinding]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                identity_binding_name: str, 
                parameters: IdentityBinding, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[IdentityBinding]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                identity_binding_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[IdentityBinding]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-04-01', params_added_on={'2026-04-01': ['api_version', 'subscription_id', 'resource_group_name', 'resource_name', 'identity_binding_name']}, api_versions_list=['2026-04-01', '2026-05-01', '2026-05-02-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                identity_binding_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-04-01', params_added_on={'2026-04-01': ['api_version', 'subscription_id', 'resource_group_name', 'resource_name', 'identity_binding_name', 'accept']}, api_versions_list=['2026-04-01', '2026-05-01', '2026-05-02-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                identity_binding_name: str, 
                **kwargs: Any
            ) -> IdentityBinding: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01', params_added_on={'2026-04-01': ['api_version', 'subscription_id', 'resource_group_name', 'resource_name', 'accept']}, api_versions_list=['2026-04-01', '2026-05-01', '2026-05-02-preview'])
        def list_by_managed_cluster(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[IdentityBinding]: ...


    class azure.mgmt.containerservice.aio.operations.JWTAuthenticatorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                jwt_authenticator_name: str, 
                parameters: JWTAuthenticator, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[JWTAuthenticator]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                jwt_authenticator_name: str, 
                parameters: JWTAuthenticator, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[JWTAuthenticator]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                jwt_authenticator_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[JWTAuthenticator]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'resource_name', 'jwt_authenticator_name']}, api_versions_list=['2026-05-02-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                jwt_authenticator_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'resource_name', 'jwt_authenticator_name', 'accept']}, api_versions_list=['2026-05-02-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                jwt_authenticator_name: str, 
                **kwargs: Any
            ) -> JWTAuthenticator: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'resource_name', 'accept']}, api_versions_list=['2026-05-02-preview'])
        def list_by_managed_cluster(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[JWTAuthenticator]: ...


    class azure.mgmt.containerservice.aio.operations.LoadBalancersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'resource_name', 'load_balancer_name']}, api_versions_list=['2026-05-02-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                load_balancer_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                load_balancer_name: str, 
                parameters: LoadBalancer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LoadBalancer: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                load_balancer_name: str, 
                parameters: LoadBalancer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LoadBalancer: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                load_balancer_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LoadBalancer: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'resource_name', 'load_balancer_name', 'accept']}, api_versions_list=['2026-05-02-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                load_balancer_name: str, 
                **kwargs: Any
            ) -> LoadBalancer: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'resource_name', 'accept']}, api_versions_list=['2026-05-02-preview'])
        def list_by_managed_cluster(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[LoadBalancer]: ...


    class azure.mgmt.containerservice.aio.operations.MachinesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                agent_pool_name: str, 
                machine_name: str, 
                parameters: Machine, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[Machine]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                agent_pool_name: str, 
                machine_name: str, 
                parameters: Machine, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[Machine]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                agent_pool_name: str, 
                machine_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[Machine]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                agent_pool_name: str, 
                machine_name: str, 
                **kwargs: Any
            ) -> Machine: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                agent_pool_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Machine]: ...


    class azure.mgmt.containerservice.aio.operations.MaintenanceConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                config_name: str, 
                parameters: MaintenanceConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MaintenanceConfiguration: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                config_name: str, 
                parameters: MaintenanceConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MaintenanceConfiguration: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                config_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MaintenanceConfiguration: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                config_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                config_name: str, 
                **kwargs: Any
            ) -> MaintenanceConfiguration: ...

        @distributed_trace
        def list_by_managed_cluster(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[MaintenanceConfiguration]: ...


    class azure.mgmt.containerservice.aio.operations.MaintenanceWindowsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                maintenance_window_name: str, 
                resource: MaintenanceWindowResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MaintenanceWindowResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                maintenance_window_name: str, 
                resource: MaintenanceWindowResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MaintenanceWindowResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                maintenance_window_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MaintenanceWindowResource]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'maintenance_window_name']}, api_versions_list=['2026-05-02-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                maintenance_window_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'maintenance_window_name', 'accept']}, api_versions_list=['2026-05-02-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                maintenance_window_name: str, 
                **kwargs: Any
            ) -> MaintenanceWindowResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2026-05-02-preview'])
        def list(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[MaintenanceWindowResource]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2026-05-02-preview'])
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[MaintenanceWindowResource]: ...

        @overload
        async def update_tags(
                self, 
                resource_group_name: str, 
                maintenance_window_name: str, 
                properties: TagsObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MaintenanceWindowResource: ...

        @overload
        async def update_tags(
                self, 
                resource_group_name: str, 
                maintenance_window_name: str, 
                properties: TagsObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MaintenanceWindowResource: ...

        @overload
        async def update_tags(
                self, 
                resource_group_name: str, 
                maintenance_window_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MaintenanceWindowResource: ...


    class azure.mgmt.containerservice.aio.operations.ManagedClusterSnapshotsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: ManagedClusterSnapshot, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagedClusterSnapshot: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: ManagedClusterSnapshot, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagedClusterSnapshot: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagedClusterSnapshot: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'resource_name']}, api_versions_list=['2026-05-02-preview'])
        async def delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'resource_name', 'accept']}, api_versions_list=['2026-05-02-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ManagedClusterSnapshot: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2026-05-02-preview'])
        def list(self, **kwargs: Any) -> AsyncItemPaged[ManagedClusterSnapshot]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2026-05-02-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ManagedClusterSnapshot]: ...

        @overload
        async def update_tags(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: TagsObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagedClusterSnapshot: ...

        @overload
        async def update_tags(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: TagsObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagedClusterSnapshot: ...

        @overload
        async def update_tags(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagedClusterSnapshot: ...


    class azure.mgmt.containerservice.aio.operations.ManagedClustersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_abort_latest_operation(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: ManagedCluster, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedCluster]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: ManagedCluster, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedCluster]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedCluster]: ...

        @distributed_trace_async
        @api_version_validation(params_added_on={'2026-05-02-preview': ['ignore_pod_disruption_budget']}, api_versions_list=['2025-10-01', '2026-01-01', '2026-02-01', '2026-03-01', '2026-04-01', '2026-05-01', '2026-05-02-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                *, 
                etag: Optional[str] = ..., 
                ignore_pod_disruption_budget: Optional[bool] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_rebalance_load_balancers(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: RebalanceLoadBalancersRequestBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_rebalance_load_balancers(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: RebalanceLoadBalancersRequestBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_rebalance_load_balancers(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_reset_aad_profile(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: ManagedClusterAADProfile, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_reset_aad_profile(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: ManagedClusterAADProfile, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_reset_aad_profile(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_reset_service_principal_profile(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: ManagedClusterServicePrincipalProfile, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_reset_service_principal_profile(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: ManagedClusterServicePrincipalProfile, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_reset_service_principal_profile(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_rotate_cluster_certificates(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_rotate_service_account_signing_keys(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_run_command(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                request_payload: RunCommandRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RunCommandResult]: ...

        @overload
        async def begin_run_command(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                request_payload: RunCommandRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RunCommandResult]: ...

        @overload
        async def begin_run_command(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                request_payload: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RunCommandResult]: ...

        @distributed_trace_async
        async def begin_start(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_stop(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update_tags(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: TagsObject, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedCluster]: ...

        @overload
        async def begin_update_tags(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: TagsObject, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedCluster]: ...

        @overload
        async def begin_update_tags(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedCluster]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ManagedCluster: ...

        @distributed_trace_async
        async def get_access_profile(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                role_name: str, 
                **kwargs: Any
            ) -> ManagedClusterAccessProfile: ...

        @distributed_trace_async
        async def get_command_result(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                command_id: str, 
                **kwargs: Any
            ) -> Optional[RunCommandResult]: ...

        @distributed_trace_async
        async def get_guardrails_versions(
                self, 
                location: str, 
                version: str, 
                **kwargs: Any
            ) -> GuardrailsAvailableVersion: ...

        @distributed_trace_async
        async def get_mesh_revision_profile(
                self, 
                location: str, 
                mode: str, 
                **kwargs: Any
            ) -> MeshRevisionProfile: ...

        @distributed_trace_async
        async def get_mesh_upgrade_profile(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                mode: str, 
                **kwargs: Any
            ) -> MeshUpgradeProfile: ...

        @distributed_trace_async
        async def get_safeguards_versions(
                self, 
                location: str, 
                version: str, 
                **kwargs: Any
            ) -> SafeguardsAvailableVersion: ...

        @distributed_trace_async
        async def get_upgrade_profile(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ManagedClusterUpgradeProfile: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[ManagedCluster]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ManagedCluster]: ...

        @distributed_trace_async
        async def list_cluster_admin_credentials(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                *, 
                server_fqdn: Optional[str] = ..., 
                **kwargs: Any
            ) -> CredentialResults: ...

        @distributed_trace_async
        async def list_cluster_monitoring_user_credentials(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                *, 
                server_fqdn: Optional[str] = ..., 
                **kwargs: Any
            ) -> CredentialResults: ...

        @distributed_trace_async
        async def list_cluster_user_credentials(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                *, 
                format: Optional[Union[str, Format]] = ..., 
                server_fqdn: Optional[str] = ..., 
                **kwargs: Any
            ) -> CredentialResults: ...

        @distributed_trace
        def list_guardrails_versions(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[GuardrailsAvailableVersion]: ...

        @distributed_trace_async
        async def list_kubernetes_versions(
                self, 
                location: str, 
                **kwargs: Any
            ) -> KubernetesVersionListResult: ...

        @distributed_trace
        def list_mesh_revision_profiles(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[MeshRevisionProfile]: ...

        @distributed_trace
        def list_mesh_upgrade_profiles(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[MeshUpgradeProfile]: ...

        @distributed_trace
        def list_outbound_network_dependencies_endpoints(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[OutboundEnvironmentEndpoint]: ...

        @distributed_trace
        def list_safeguards_versions(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SafeguardsAvailableVersion]: ...


    class azure.mgmt.containerservice.aio.operations.ManagedNamespacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                managed_namespace_name: str, 
                parameters: ManagedNamespace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedNamespace]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                managed_namespace_name: str, 
                parameters: ManagedNamespace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedNamespace]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                managed_namespace_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedNamespace]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                managed_namespace_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                managed_namespace_name: str, 
                **kwargs: Any
            ) -> ManagedNamespace: ...

        @distributed_trace
        def list_by_managed_cluster(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ManagedNamespace]: ...

        @distributed_trace_async
        async def list_credential(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                managed_namespace_name: str, 
                **kwargs: Any
            ) -> CredentialResults: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                managed_namespace_name: str, 
                parameters: TagsObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagedNamespace: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                managed_namespace_name: str, 
                parameters: TagsObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagedNamespace: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                managed_namespace_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagedNamespace: ...


    class azure.mgmt.containerservice.aio.operations.MeshMembershipsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                mesh_membership_name: str, 
                parameters: MeshMembership, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MeshMembership]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                mesh_membership_name: str, 
                parameters: MeshMembership, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MeshMembership]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                mesh_membership_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MeshMembership]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'resource_name', 'mesh_membership_name']}, api_versions_list=['2026-05-02-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                mesh_membership_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'resource_name', 'mesh_membership_name', 'accept']}, api_versions_list=['2026-05-02-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                mesh_membership_name: str, 
                **kwargs: Any
            ) -> MeshMembership: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'resource_name', 'accept']}, api_versions_list=['2026-05-02-preview'])
        def list_by_managed_cluster(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[MeshMembership]: ...


    class azure.mgmt.containerservice.aio.operations.OperationStatusResultOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'resource_name', 'operation_id', 'accept']}, api_versions_list=['2026-05-02-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationStatusResult: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'resource_name', 'agent_pool_name', 'operation_id', 'accept']}, api_versions_list=['2026-05-02-preview'])
        async def get_by_agent_pool(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                agent_pool_name: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationStatusResult: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'resource_name', 'accept']}, api_versions_list=['2026-05-02-preview'])
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[OperationStatusResult]: ...


    class azure.mgmt.containerservice.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[OperationValue]: ...


    class azure.mgmt.containerservice.aio.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace_async
        async def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnectionListResult: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                private_endpoint_connection_name: str, 
                parameters: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                private_endpoint_connection_name: str, 
                parameters: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                private_endpoint_connection_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...


    class azure.mgmt.containerservice.aio.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResourcesListResult: ...


    class azure.mgmt.containerservice.aio.operations.ResolvePrivateLinkServiceIdOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def post(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: PrivateLinkResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @overload
        async def post(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: PrivateLinkResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @overload
        async def post(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateLinkResource: ...


    class azure.mgmt.containerservice.aio.operations.SnapshotsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: Snapshot, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Snapshot: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: Snapshot, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Snapshot: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Snapshot: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> Snapshot: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Snapshot]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Snapshot]: ...

        @overload
        async def update_tags(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: TagsObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Snapshot: ...

        @overload
        async def update_tags(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: TagsObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Snapshot: ...

        @overload
        async def update_tags(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Snapshot: ...


    class azure.mgmt.containerservice.aio.operations.TrustedAccessRoleBindingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                trusted_access_role_binding_name: str, 
                trusted_access_role_binding: TrustedAccessRoleBinding, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TrustedAccessRoleBinding]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                trusted_access_role_binding_name: str, 
                trusted_access_role_binding: TrustedAccessRoleBinding, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TrustedAccessRoleBinding]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                trusted_access_role_binding_name: str, 
                trusted_access_role_binding: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TrustedAccessRoleBinding]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                trusted_access_role_binding_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                trusted_access_role_binding_name: str, 
                **kwargs: Any
            ) -> TrustedAccessRoleBinding: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[TrustedAccessRoleBinding]: ...


    class azure.mgmt.containerservice.aio.operations.TrustedAccessRolesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[TrustedAccessRole]: ...


    class azure.mgmt.containerservice.aio.operations.VmSkusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                *, 
                include_extended_locations: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ResourceSku]: ...


namespace azure.mgmt.containerservice.models

    class azure.mgmt.containerservice.models.AbsoluteMonthlySchedule(_Model):
        day_of_month: int
        interval_months: int

        @overload
        def __init__(
                self, 
                *, 
                day_of_month: int, 
                interval_months: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.AccelerationMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BPF_VETH = "BpfVeth"
        NONE = "None"


    class azure.mgmt.containerservice.models.AccessProfile(_Model):
        kube_config: Optional[bytes]

        @overload
        def __init__(
                self, 
                *, 
                kube_config: Optional[bytes] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.AddonAutoscaling(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.containerservice.models.AdoptionPolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALWAYS = "Always"
        IF_IDENTICAL = "IfIdentical"
        NEVER = "Never"


    class azure.mgmt.containerservice.models.AdvancedNetworkPolicies(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FQDN = "FQDN"
        L7 = "L7"
        NONE = "None"


    class azure.mgmt.containerservice.models.AdvancedNetworking(_Model):
        enabled: Optional[bool]
        observability: Optional[AdvancedNetworkingObservability]
        performance: Optional[AdvancedNetworkingPerformance]
        security: Optional[AdvancedNetworkingSecurity]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                observability: Optional[AdvancedNetworkingObservability] = ..., 
                performance: Optional[AdvancedNetworkingPerformance] = ..., 
                security: Optional[AdvancedNetworkingSecurity] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.AdvancedNetworkingObservability(_Model):
        enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.AdvancedNetworkingPerformance(_Model):
        acceleration_mode: Optional[Union[str, AccelerationMode]]

        @overload
        def __init__(
                self, 
                *, 
                acceleration_mode: Optional[Union[str, AccelerationMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.AdvancedNetworkingSecurity(_Model):
        advanced_network_policies: Optional[Union[str, AdvancedNetworkPolicies]]
        enabled: Optional[bool]
        transit_encryption: Optional[AdvancedNetworkingSecurityTransitEncryption]

        @overload
        def __init__(
                self, 
                *, 
                advanced_network_policies: Optional[Union[str, AdvancedNetworkPolicies]] = ..., 
                enabled: Optional[bool] = ..., 
                transit_encryption: Optional[AdvancedNetworkingSecurityTransitEncryption] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.AdvancedNetworkingSecurityTransitEncryption(_Model):
        type: Optional[Union[str, TransitEncryptionType]]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, TransitEncryptionType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.AgentPool(ProxyResource):
        id: str
        name: str
        properties: Optional[AgentPoolManagedClusterAgentPoolProfileProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AgentPoolManagedClusterAgentPoolProfileProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.containerservice.models.AgentPoolArtifactStreamingProfile(_Model):
        enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.AgentPoolAvailableVersions(_Model):
        id: Optional[str]
        name: Optional[str]
        properties: AgentPoolAvailableVersionsProperties
        type: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: AgentPoolAvailableVersionsProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.containerservice.models.AgentPoolAvailableVersionsProperties(_Model):
        agent_pool_versions: Optional[list[AgentPoolAvailableVersionsPropertiesAgentPoolVersionsItem]]

        @overload
        def __init__(
                self, 
                *, 
                agent_pool_versions: Optional[list[AgentPoolAvailableVersionsPropertiesAgentPoolVersionsItem]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.AgentPoolAvailableVersionsPropertiesAgentPoolVersionsItem(_Model):
        default: Optional[bool]
        is_preview: Optional[bool]
        kubernetes_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                default: Optional[bool] = ..., 
                is_preview: Optional[bool] = ..., 
                kubernetes_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.AgentPoolBlueGreenUpgradeSettings(_Model):
        batch_soak_duration_in_minutes: Optional[int]
        drain_batch_size: Optional[str]
        drain_timeout_in_minutes: Optional[int]
        final_soak_duration_in_minutes: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                batch_soak_duration_in_minutes: Optional[int] = ..., 
                drain_batch_size: Optional[str] = ..., 
                drain_timeout_in_minutes: Optional[int] = ..., 
                final_soak_duration_in_minutes: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.AgentPoolDeleteMachinesParameter(_Model):
        machine_names: list[str]

        @overload
        def __init__(
                self, 
                *, 
                machine_names: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.AgentPoolGatewayProfile(_Model):
        public_ip_prefix_size: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                public_ip_prefix_size: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.AgentPoolManagedClusterAgentPoolProfileProperties(_Model):
        artifact_streaming_profile: Optional[AgentPoolArtifactStreamingProfile]
        availability_zones: Optional[list[str]]
        capacity_reservation_group_id: Optional[str]
        count: Optional[int]
        creation_data: Optional[CreationData]
        current_orchestrator_version: Optional[str]
        e_tag: Optional[str]
        enable_auto_scaling: Optional[bool]
        enable_encryption_at_host: Optional[bool]
        enable_fips: Optional[bool]
        enable_node_public_ip: Optional[bool]
        enable_os_disk_full_caching: Optional[bool]
        enable_ultra_ssd: Optional[bool]
        gateway_profile: Optional[AgentPoolGatewayProfile]
        gpu_instance_profile: Optional[Union[str, GPUInstanceProfile]]
        gpu_profile: Optional[GPUProfile]
        host_group_id: Optional[str]
        kubelet_config: Optional[KubeletConfig]
        kubelet_disk_type: Optional[Union[str, KubeletDiskType]]
        linux_os_config: Optional[LinuxOSConfig]
        local_dns_profile: Optional[LocalDNSProfile]
        max_count: Optional[int]
        max_pods: Optional[int]
        message_of_the_day: Optional[str]
        min_count: Optional[int]
        mode: Optional[Union[str, AgentPoolMode]]
        network_profile: Optional[AgentPoolNetworkProfile]
        node_image_version: Optional[str]
        node_initialization_taints: Optional[list[str]]
        node_labels: Optional[dict[str, str]]
        node_public_ip_prefix_id: Optional[str]
        node_taints: Optional[list[str]]
        orchestrator_version: Optional[str]
        os_disk_size_gb: Optional[int]
        os_disk_type: Optional[Union[str, OSDiskType]]
        os_sku: Optional[Union[str, _models.OSSKU]]
        os_type: Optional[Union[str, OSType]]
        pod_ip_allocation_mode: Optional[Union[str, PodIPAllocationMode]]
        pod_subnet_id: Optional[str]
        power_state: Optional[PowerState]
        prepared_image_specification_profile: Optional[PreparedImageSpecificationProfile]
        provisioning_state: Optional[str]
        proximity_placement_group_id: Optional[str]
        scale_down_mode: Optional[Union[str, ScaleDownMode]]
        scale_set_eviction_policy: Optional[Union[str, ScaleSetEvictionPolicy]]
        scale_set_priority: Optional[Union[str, ScaleSetPriority]]
        security_profile: Optional[AgentPoolSecurityProfile]
        spot_max_price: Optional[float]
        status: Optional[AgentPoolStatus]
        tags: Optional[dict[str, str]]
        type_properties_type: Optional[Union[str, AgentPoolType]]
        upgrade_settings: Optional[AgentPoolUpgradeSettings]
        upgrade_settings_blue_green: Optional[AgentPoolBlueGreenUpgradeSettings]
        upgrade_strategy: Optional[Union[str, UpgradeStrategy]]
        virtual_machine_nodes_status: Optional[list[VirtualMachineNodes]]
        virtual_machines_profile: Optional[VirtualMachinesProfile]
        vm_size: Optional[str]
        vnet_subnet_id: Optional[str]
        windows_profile: Optional[AgentPoolWindowsProfile]
        workload_runtime: Optional[Union[str, WorkloadRuntime]]

        @overload
        def __init__(
                self, 
                *, 
                artifact_streaming_profile: Optional[AgentPoolArtifactStreamingProfile] = ..., 
                availability_zones: Optional[list[str]] = ..., 
                capacity_reservation_group_id: Optional[str] = ..., 
                count: Optional[int] = ..., 
                creation_data: Optional[CreationData] = ..., 
                enable_auto_scaling: Optional[bool] = ..., 
                enable_encryption_at_host: Optional[bool] = ..., 
                enable_fips: Optional[bool] = ..., 
                enable_node_public_ip: Optional[bool] = ..., 
                enable_os_disk_full_caching: Optional[bool] = ..., 
                enable_ultra_ssd: Optional[bool] = ..., 
                gateway_profile: Optional[AgentPoolGatewayProfile] = ..., 
                gpu_instance_profile: Optional[Union[str, GPUInstanceProfile]] = ..., 
                gpu_profile: Optional[GPUProfile] = ..., 
                host_group_id: Optional[str] = ..., 
                kubelet_config: Optional[KubeletConfig] = ..., 
                kubelet_disk_type: Optional[Union[str, KubeletDiskType]] = ..., 
                linux_os_config: Optional[LinuxOSConfig] = ..., 
                local_dns_profile: Optional[LocalDNSProfile] = ..., 
                max_count: Optional[int] = ..., 
                max_pods: Optional[int] = ..., 
                message_of_the_day: Optional[str] = ..., 
                min_count: Optional[int] = ..., 
                mode: Optional[Union[str, AgentPoolMode]] = ..., 
                network_profile: Optional[AgentPoolNetworkProfile] = ..., 
                node_image_version: Optional[str] = ..., 
                node_initialization_taints: Optional[list[str]] = ..., 
                node_labels: Optional[dict[str, str]] = ..., 
                node_public_ip_prefix_id: Optional[str] = ..., 
                node_taints: Optional[list[str]] = ..., 
                orchestrator_version: Optional[str] = ..., 
                os_disk_size_gb: Optional[int] = ..., 
                os_disk_type: Optional[Union[str, OSDiskType]] = ..., 
                os_sku: Optional[Union[str, _models.OSSKU]] = ..., 
                os_type: Optional[Union[str, OSType]] = ..., 
                pod_ip_allocation_mode: Optional[Union[str, PodIPAllocationMode]] = ..., 
                pod_subnet_id: Optional[str] = ..., 
                power_state: Optional[PowerState] = ..., 
                prepared_image_specification_profile: Optional[PreparedImageSpecificationProfile] = ..., 
                proximity_placement_group_id: Optional[str] = ..., 
                scale_down_mode: Optional[Union[str, ScaleDownMode]] = ..., 
                scale_set_eviction_policy: Optional[Union[str, ScaleSetEvictionPolicy]] = ..., 
                scale_set_priority: Optional[Union[str, ScaleSetPriority]] = ..., 
                security_profile: Optional[AgentPoolSecurityProfile] = ..., 
                spot_max_price: Optional[float] = ..., 
                status: Optional[AgentPoolStatus] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                type_properties_type: Optional[Union[str, AgentPoolType]] = ..., 
                upgrade_settings: Optional[AgentPoolUpgradeSettings] = ..., 
                upgrade_settings_blue_green: Optional[AgentPoolBlueGreenUpgradeSettings] = ..., 
                upgrade_strategy: Optional[Union[str, UpgradeStrategy]] = ..., 
                virtual_machine_nodes_status: Optional[list[VirtualMachineNodes]] = ..., 
                virtual_machines_profile: Optional[VirtualMachinesProfile] = ..., 
                vm_size: Optional[str] = ..., 
                vnet_subnet_id: Optional[str] = ..., 
                windows_profile: Optional[AgentPoolWindowsProfile] = ..., 
                workload_runtime: Optional[Union[str, WorkloadRuntime]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.AgentPoolMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GATEWAY = "Gateway"
        MACHINES = "Machines"
        MANAGED_SYSTEM = "ManagedSystem"
        SYSTEM = "System"
        USER = "User"


    class azure.mgmt.containerservice.models.AgentPoolNetworkInterface(_Model):
        enable_accelerated_networking: Optional[bool]
        type: Optional[Union[str, AgentPoolNetworkInterfaceType]]
        vnet_subnet_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                enable_accelerated_networking: Optional[bool] = ..., 
                type: Optional[Union[str, AgentPoolNetworkInterfaceType]] = ..., 
                vnet_subnet_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.AgentPoolNetworkInterfaceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DYNAMIC = "Dynamic"
        STANDARD = "Standard"


    class azure.mgmt.containerservice.models.AgentPoolNetworkProfile(_Model):
        allowed_host_ports: Optional[list[PortRange]]
        application_security_groups: Optional[list[str]]
        node_public_ip_prefix_i_ds: Optional[list[str]]
        node_public_ip_tags: Optional[list[IPTag]]
        secondary_network_interfaces: Optional[list[AgentPoolNetworkInterface]]

        @overload
        def __init__(
                self, 
                *, 
                allowed_host_ports: Optional[list[PortRange]] = ..., 
                application_security_groups: Optional[list[str]] = ..., 
                node_public_ip_prefix_i_ds: Optional[list[str]] = ..., 
                node_public_ip_tags: Optional[list[IPTag]] = ..., 
                secondary_network_interfaces: Optional[list[AgentPoolNetworkInterface]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.AgentPoolRecentlyUsedVersion(_Model):
        node_image_version: Optional[str]
        orchestrator_version: Optional[str]
        timestamp: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                node_image_version: Optional[str] = ..., 
                orchestrator_version: Optional[str] = ..., 
                timestamp: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.AgentPoolSSHAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENTRA_ID = "EntraId"
        LOCAL_USER = "LocalUser"


    class azure.mgmt.containerservice.models.AgentPoolSecurityProfile(_Model):
        enable_secure_boot: Optional[bool]
        enable_vtpm: Optional[bool]
        ssh_access: Optional[Union[str, AgentPoolSSHAccess]]

        @overload
        def __init__(
                self, 
                *, 
                enable_secure_boot: Optional[bool] = ..., 
                enable_vtpm: Optional[bool] = ..., 
                ssh_access: Optional[Union[str, AgentPoolSSHAccess]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.AgentPoolStatus(_Model):
        provisioning_error: Optional[ErrorDetail]


    class azure.mgmt.containerservice.models.AgentPoolType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABILITY_SET = "AvailabilitySet"
        FLEX_NODES = "FlexNodes"
        VIRTUAL_MACHINES = "VirtualMachines"
        VIRTUAL_MACHINE_SCALE_SETS = "VirtualMachineScaleSets"


    class azure.mgmt.containerservice.models.AgentPoolUpgradeProfile(ProxyResource):
        id: str
        name: str
        properties: AgentPoolUpgradeProfileProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: AgentPoolUpgradeProfileProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.containerservice.models.AgentPoolUpgradeProfileProperties(_Model):
        components_by_releases: Optional[list[ComponentsByRelease]]
        kubernetes_version: str
        latest_node_image_version: Optional[str]
        os_type: Union[str, OSType]
        recently_used_versions: Optional[list[AgentPoolRecentlyUsedVersion]]
        upgrades: Optional[list[AgentPoolUpgradeProfilePropertiesUpgradesItem]]

        @overload
        def __init__(
                self, 
                *, 
                components_by_releases: Optional[list[ComponentsByRelease]] = ..., 
                kubernetes_version: str, 
                latest_node_image_version: Optional[str] = ..., 
                os_type: Union[str, OSType], 
                upgrades: Optional[list[AgentPoolUpgradeProfilePropertiesUpgradesItem]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.AgentPoolUpgradeProfilePropertiesUpgradesItem(_Model):
        is_out_of_support: Optional[bool]
        is_preview: Optional[bool]
        kubernetes_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                is_out_of_support: Optional[bool] = ..., 
                is_preview: Optional[bool] = ..., 
                kubernetes_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.AgentPoolUpgradeSettings(_Model):
        drain_timeout_in_minutes: Optional[int]
        max_blocked_nodes: Optional[str]
        max_surge: Optional[str]
        max_unavailable: Optional[str]
        node_soak_duration_in_minutes: Optional[int]
        undrainable_node_behavior: Optional[Union[str, UndrainableNodeBehavior]]

        @overload
        def __init__(
                self, 
                *, 
                drain_timeout_in_minutes: Optional[int] = ..., 
                max_blocked_nodes: Optional[str] = ..., 
                max_surge: Optional[str] = ..., 
                max_unavailable: Optional[str] = ..., 
                node_soak_duration_in_minutes: Optional[int] = ..., 
                undrainable_node_behavior: Optional[Union[str, UndrainableNodeBehavior]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.AgentPoolWindowsProfile(_Model):
        disable_outbound_nat: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                disable_outbound_nat: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.AlertConfiguration(ProxyResource):
        id: str
        name: str
        properties: Optional[AlertConfigurationProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AlertConfigurationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.AlertConfigurationMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        MANAGED = "Managed"


    class azure.mgmt.containerservice.models.AlertConfigurationProperties(_Model):
        mode: Union[str, AlertConfigurationMode]
        notification: AlertNotification
        provisioning_state: Optional[Union[str, AlertConfigurationProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                mode: Union[str, AlertConfigurationMode], 
                notification: AlertNotification
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.AlertConfigurationProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.containerservice.models.AlertNotification(_Model):
        action_group_id: str

        @overload
        def __init__(
                self, 
                *, 
                action_group_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.AllowedSubject(_Model):
        namespace_selector: LabelSelector
        service_account_selector: Optional[LabelSelector]

        @overload
        def __init__(
                self, 
                *, 
                namespace_selector: LabelSelector, 
                service_account_selector: Optional[LabelSelector] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ArtifactSource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CACHE = "Cache"
        DIRECT = "Direct"


    class azure.mgmt.containerservice.models.AutoScaleProfile(_Model):
        max_count: Optional[int]
        min_count: Optional[int]
        size: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                max_count: Optional[int] = ..., 
                min_count: Optional[int] = ..., 
                size: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.AzureKeyVaultKms(_Model):
        enabled: Optional[bool]
        key_id: Optional[str]
        key_vault_network_access: Optional[Union[str, KeyVaultNetworkAccessTypes]]
        key_vault_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                key_id: Optional[str] = ..., 
                key_vault_network_access: Optional[Union[str, KeyVaultNetworkAccessTypes]] = ..., 
                key_vault_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.BackendPoolType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NODE_IP = "NodeIP"
        NODE_IP_CONFIGURATION = "NodeIPConfiguration"
        POD_IP = "PodIP"


    class azure.mgmt.containerservice.models.BastionProfile(_Model):
        bastion_id: Optional[str]
        enabled: Optional[bool]
        public_ip_address_id: Optional[str]
        scale_units: Optional[int]
        sku: Optional[Union[str, BastionSku]]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                public_ip_address_id: Optional[str] = ..., 
                scale_units: Optional[int] = ..., 
                sku: Optional[Union[str, BastionSku]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.BastionSku(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PREMIUM = "Premium"
        STANDARD = "Standard"


    class azure.mgmt.containerservice.models.BootstrapAzureConfig(_Model):
        bootstrap_token: Optional[BootstrapTokenInfo]
        resource_manager_endpoint: Optional[str]
        target_agent_pool_name: Optional[str]
        target_cluster: Optional[BootstrapTargetCluster]


    class azure.mgmt.containerservice.models.BootstrapComponentVersions(_Model):
        containerd: Optional[str]
        kubernetes: Optional[str]
        runc: Optional[str]


    class azure.mgmt.containerservice.models.BootstrapKubeletConfig(_Model):
        ca_cert_data: Optional[str]
        cluster_fqdn: Optional[str]


    class azure.mgmt.containerservice.models.BootstrapNetworkingConfig(_Model):
        cni_version: Optional[str]
        dns_service_ip: Optional[str]


    class azure.mgmt.containerservice.models.BootstrapNodeConfig(_Model):
        kubelet: Optional[BootstrapKubeletConfig]
        labels: Optional[dict[str, str]]
        max_pods: Optional[int]
        taints: Optional[list[str]]


    class azure.mgmt.containerservice.models.BootstrapTargetCluster(_Model):
        resource_id: Optional[str]


    class azure.mgmt.containerservice.models.BootstrapTokenInfo(_Model):
        token: Optional[str]


    class azure.mgmt.containerservice.models.ClusterServiceLoadBalancerHealthProbeMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SERVICE_NODE_PORT = "ServiceNodePort"
        SHARED = "Shared"


    class azure.mgmt.containerservice.models.ClusterUpgradeSettings(_Model):
        override_settings: Optional[UpgradeOverrideSettings]

        @overload
        def __init__(
                self, 
                *, 
                override_settings: Optional[UpgradeOverrideSettings] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.Code(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        RUNNING = "Running"
        STOPPED = "Stopped"


    class azure.mgmt.containerservice.models.CommandResultProperties(_Model):
        exit_code: Optional[int]
        finished_at: Optional[datetime]
        logs: Optional[str]
        provisioning_state: Optional[str]
        reason: Optional[str]
        started_at: Optional[datetime]


    class azure.mgmt.containerservice.models.CompatibleVersions(_Model):
        name: Optional[str]
        versions: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                versions: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.Component(_Model):
        has_breaking_changes: Optional[bool]
        name: Optional[str]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                has_breaking_changes: Optional[bool] = ..., 
                name: Optional[str] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ComponentsByRelease(_Model):
        components: Optional[list[Component]]
        kubernetes_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                components: Optional[list[Component]] = ..., 
                kubernetes_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        DISCONNECTED = "Disconnected"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.containerservice.models.ContainerNetworkLogs(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.containerservice.models.ContainerServiceLinuxProfile(_Model):
        admin_username: str
        ssh: ContainerServiceSshConfiguration

        @overload
        def __init__(
                self, 
                *, 
                admin_username: str, 
                ssh: ContainerServiceSshConfiguration
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ContainerServiceNetworkProfile(_Model):
        advanced_networking: Optional[AdvancedNetworking]
        bastion_profile: Optional[BastionProfile]
        dns_service_ip: Optional[str]
        ip_families: Optional[list[Union[str, IPFamily]]]
        kube_proxy_config: Optional[ContainerServiceNetworkProfileKubeProxyConfig]
        load_balancer_profile: Optional[ManagedClusterLoadBalancerProfile]
        load_balancer_sku: Optional[Union[str, LoadBalancerSku]]
        nat_gateway_id: Optional[str]
        nat_gateway_profile: Optional[ManagedClusterNATGatewayProfile]
        network_dataplane: Optional[Union[str, NetworkDataplane]]
        network_mode: Optional[Union[str, NetworkMode]]
        network_plugin: Optional[Union[str, NetworkPlugin]]
        network_plugin_mode: Optional[Union[str, NetworkPluginMode]]
        network_policy: Optional[Union[str, NetworkPolicy]]
        outbound_type: Optional[Union[str, OutboundType]]
        pod_cidr: Optional[str]
        pod_cidrs: Optional[list[str]]
        pod_link_local_access: Optional[Union[str, PodLinkLocalAccess]]
        service_cidr: Optional[str]
        service_cidrs: Optional[list[str]]
        static_egress_gateway_profile: Optional[ManagedClusterStaticEgressGatewayProfile]

        @overload
        def __init__(
                self, 
                *, 
                advanced_networking: Optional[AdvancedNetworking] = ..., 
                bastion_profile: Optional[BastionProfile] = ..., 
                dns_service_ip: Optional[str] = ..., 
                ip_families: Optional[list[Union[str, IPFamily]]] = ..., 
                kube_proxy_config: Optional[ContainerServiceNetworkProfileKubeProxyConfig] = ..., 
                load_balancer_profile: Optional[ManagedClusterLoadBalancerProfile] = ..., 
                load_balancer_sku: Optional[Union[str, LoadBalancerSku]] = ..., 
                nat_gateway_id: Optional[str] = ..., 
                nat_gateway_profile: Optional[ManagedClusterNATGatewayProfile] = ..., 
                network_dataplane: Optional[Union[str, NetworkDataplane]] = ..., 
                network_mode: Optional[Union[str, NetworkMode]] = ..., 
                network_plugin: Optional[Union[str, NetworkPlugin]] = ..., 
                network_plugin_mode: Optional[Union[str, NetworkPluginMode]] = ..., 
                network_policy: Optional[Union[str, NetworkPolicy]] = ..., 
                outbound_type: Optional[Union[str, OutboundType]] = ..., 
                pod_cidr: Optional[str] = ..., 
                pod_cidrs: Optional[list[str]] = ..., 
                pod_link_local_access: Optional[Union[str, PodLinkLocalAccess]] = ..., 
                service_cidr: Optional[str] = ..., 
                service_cidrs: Optional[list[str]] = ..., 
                static_egress_gateway_profile: Optional[ManagedClusterStaticEgressGatewayProfile] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ContainerServiceNetworkProfileKubeProxyConfig(_Model):
        enabled: Optional[bool]
        ipvs_config: Optional[ContainerServiceNetworkProfileKubeProxyConfigIpvsConfig]
        mode: Optional[Union[str, Mode]]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                ipvs_config: Optional[ContainerServiceNetworkProfileKubeProxyConfigIpvsConfig] = ..., 
                mode: Optional[Union[str, Mode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ContainerServiceNetworkProfileKubeProxyConfigIpvsConfig(_Model):
        scheduler: Optional[Union[str, IpvsScheduler]]
        tcp_fin_timeout_seconds: Optional[int]
        tcp_timeout_seconds: Optional[int]
        udp_timeout_seconds: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                scheduler: Optional[Union[str, IpvsScheduler]] = ..., 
                tcp_fin_timeout_seconds: Optional[int] = ..., 
                tcp_timeout_seconds: Optional[int] = ..., 
                udp_timeout_seconds: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ContainerServiceSshConfiguration(_Model):
        public_keys: list[ContainerServiceSshPublicKey]

        @overload
        def __init__(
                self, 
                *, 
                public_keys: list[ContainerServiceSshPublicKey]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ContainerServiceSshPublicKey(_Model):
        key_data: str

        @overload
        def __init__(
                self, 
                *, 
                key_data: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ControlPlaneScalingSize(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        H2 = "H2"
        H4 = "H4"
        H8 = "H8"


    class azure.mgmt.containerservice.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.containerservice.models.CreationData(_Model):
        source_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                source_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.CredentialResult(_Model):
        name: Optional[str]
        value: Optional[bytes]


    class azure.mgmt.containerservice.models.CredentialResults(_Model):
        kubeconfigs: Optional[list[CredentialResult]]


    class azure.mgmt.containerservice.models.DailySchedule(_Model):
        interval_days: int

        @overload
        def __init__(
                self, 
                *, 
                interval_days: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.DateSpan(_Model):
        end: date
        start: date

        @overload
        def __init__(
                self, 
                *, 
                end: date, 
                start: date
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.DelegatedResource(_Model):
        location: Optional[str]
        referral_resource: Optional[str]
        resource_id: Optional[str]
        tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                referral_resource: Optional[str] = ..., 
                resource_id: Optional[str] = ..., 
                tenant_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.DeletePolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETE = "Delete"
        KEEP = "Keep"


    class azure.mgmt.containerservice.models.DriftAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        RECREATE = "Recreate"
        SYNCED = "Synced"


    class azure.mgmt.containerservice.models.DriverType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUDA = "CUDA"
        GRID = "GRID"


    class azure.mgmt.containerservice.models.EndpointDependency(_Model):
        domain_name: Optional[str]
        endpoint_details: Optional[list[EndpointDetail]]

        @overload
        def __init__(
                self, 
                *, 
                domain_name: Optional[str] = ..., 
                endpoint_details: Optional[list[EndpointDetail]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.EndpointDetail(_Model):
        description: Optional[str]
        ip_address: Optional[str]
        port: Optional[int]
        protocol: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                ip_address: Optional[str] = ..., 
                port: Optional[int] = ..., 
                protocol: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.containerservice.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.containerservice.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.Expander(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LEAST_WASTE = "least-waste"
        MOST_PODS = "most-pods"
        PRIORITY = "priority"
        RANDOM = "random"


    class azure.mgmt.containerservice.models.ExtendedLocation(_Model):
        name: Optional[str]
        type: Optional[Union[str, ExtendedLocationTypes]]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                type: Optional[Union[str, ExtendedLocationTypes]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ExtendedLocationTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EDGE_ZONE = "EdgeZone"


    class azure.mgmt.containerservice.models.Format(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE = "azure"
        EXEC = "exec"


    class azure.mgmt.containerservice.models.GPUDriver(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INSTALL = "Install"
        NONE = "None"


    class azure.mgmt.containerservice.models.GPUInstanceProfile(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MIG1_G = "MIG1g"
        MIG2_G = "MIG2g"
        MIG3_G = "MIG3g"
        MIG4_G = "MIG4g"
        MIG7_G = "MIG7g"


    class azure.mgmt.containerservice.models.GPUProfile(_Model):
        driver: Optional[Union[str, GPUDriver]]
        driver_type: Optional[Union[str, DriverType]]
        nvidia: Optional[NvidiaGPUProfile]

        @overload
        def __init__(
                self, 
                *, 
                driver: Optional[Union[str, GPUDriver]] = ..., 
                driver_type: Optional[Union[str, DriverType]] = ..., 
                nvidia: Optional[NvidiaGPUProfile] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.GatewayAPIIstioEnabled(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.containerservice.models.GuardrailsAvailableVersion(ProxyResource):
        id: str
        name: str
        properties: GuardrailsAvailableVersionsProperties
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: GuardrailsAvailableVersionsProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.GuardrailsAvailableVersionsProperties(_Model):
        is_default_version: Optional[bool]
        support: Optional[Union[str, GuardrailsSupport]]


    class azure.mgmt.containerservice.models.GuardrailsSupport(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PREVIEW = "Preview"
        STABLE = "Stable"


    class azure.mgmt.containerservice.models.HardEvictionThreshold(_Model):
        memory_available: Optional[str]
        node_fs_available: Optional[str]
        node_fs_inodes_free: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                memory_available: Optional[str] = ..., 
                node_fs_available: Optional[str] = ..., 
                node_fs_inodes_free: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.IPFamily(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        I_PV4 = "IPv4"
        I_PV6 = "IPv6"


    class azure.mgmt.containerservice.models.IPTag(_Model):
        ip_tag_type: Optional[str]
        tag: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                ip_tag_type: Optional[str] = ..., 
                tag: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.IdentityBinding(ProxyResource):
        e_tag: Optional[str]
        id: str
        name: str
        properties: Optional[IdentityBindingProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[IdentityBindingProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.IdentityBindingManagedIdentityProfile(_Model):
        client_id: Optional[str]
        object_id: Optional[str]
        resource_id: str
        tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.IdentityBindingOidcIssuerProfile(_Model):
        oidc_issuer_url: Optional[str]


    class azure.mgmt.containerservice.models.IdentityBindingProperties(_Model):
        allowed_subjects: Optional[list[AllowedSubject]]
        managed_identity: IdentityBindingManagedIdentityProfile
        oidc_issuer: Optional[IdentityBindingOidcIssuerProfile]
        provisioning_state: Optional[Union[str, IdentityBindingProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                allowed_subjects: Optional[list[AllowedSubject]] = ..., 
                managed_identity: IdentityBindingManagedIdentityProfile
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.IdentityBindingProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.containerservice.models.InfrastructureEncryption(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.containerservice.models.IpvsScheduler(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LEAST_CONNECTION = "LeastConnection"
        ROUND_ROBIN = "RoundRobin"


    class azure.mgmt.containerservice.models.IstioCertificateAuthority(_Model):
        plugin: Optional[IstioPluginCertificateAuthority]

        @overload
        def __init__(
                self, 
                *, 
                plugin: Optional[IstioPluginCertificateAuthority] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.IstioComponents(_Model):
        egress_gateways: Optional[list[IstioEgressGateway]]
        ingress_gateways: Optional[list[IstioIngressGateway]]
        proxy_redirection_mechanism: Optional[Union[str, ProxyRedirectionMechanism]]

        @overload
        def __init__(
                self, 
                *, 
                egress_gateways: Optional[list[IstioEgressGateway]] = ..., 
                ingress_gateways: Optional[list[IstioIngressGateway]] = ..., 
                proxy_redirection_mechanism: Optional[Union[str, ProxyRedirectionMechanism]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.IstioEgressGateway(_Model):
        enabled: bool
        gateway_configuration_name: Optional[str]
        name: str
        namespace: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                enabled: bool, 
                gateway_configuration_name: Optional[str] = ..., 
                name: str, 
                namespace: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.IstioIngressGateway(_Model):
        enabled: bool
        mode: Union[str, IstioIngressGatewayMode]

        @overload
        def __init__(
                self, 
                *, 
                enabled: bool, 
                mode: Union[str, IstioIngressGatewayMode]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.IstioIngressGatewayMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXTERNAL = "External"
        INTERNAL = "Internal"


    class azure.mgmt.containerservice.models.IstioPluginCertificateAuthority(_Model):
        cert_chain_object_name: Optional[str]
        cert_object_name: Optional[str]
        key_object_name: Optional[str]
        key_vault_id: Optional[str]
        root_cert_object_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                cert_chain_object_name: Optional[str] = ..., 
                cert_object_name: Optional[str] = ..., 
                key_object_name: Optional[str] = ..., 
                key_vault_id: Optional[str] = ..., 
                root_cert_object_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.IstioServiceMesh(_Model):
        certificate_authority: Optional[IstioCertificateAuthority]
        components: Optional[IstioComponents]
        revisions: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                certificate_authority: Optional[IstioCertificateAuthority] = ..., 
                components: Optional[IstioComponents] = ..., 
                revisions: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.JWTAuthenticator(ProxyResource):
        id: str
        name: str
        properties: JWTAuthenticatorProperties
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: JWTAuthenticatorProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.JWTAuthenticatorClaimMappingExpression(_Model):
        expression: str

        @overload
        def __init__(
                self, 
                *, 
                expression: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.JWTAuthenticatorClaimMappings(_Model):
        extra: Optional[list[JWTAuthenticatorExtraClaimMappingExpression]]
        groups: Optional[JWTAuthenticatorClaimMappingExpression]
        uid: Optional[JWTAuthenticatorClaimMappingExpression]
        username: JWTAuthenticatorClaimMappingExpression

        @overload
        def __init__(
                self, 
                *, 
                extra: Optional[list[JWTAuthenticatorExtraClaimMappingExpression]] = ..., 
                groups: Optional[JWTAuthenticatorClaimMappingExpression] = ..., 
                uid: Optional[JWTAuthenticatorClaimMappingExpression] = ..., 
                username: JWTAuthenticatorClaimMappingExpression
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.JWTAuthenticatorExtraClaimMappingExpression(_Model):
        key: str
        value_expression: str

        @overload
        def __init__(
                self, 
                *, 
                key: str, 
                value_expression: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.JWTAuthenticatorIssuer(_Model):
        audiences: list[str]
        url: str

        @overload
        def __init__(
                self, 
                *, 
                audiences: list[str], 
                url: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.JWTAuthenticatorProperties(_Model):
        claim_mappings: JWTAuthenticatorClaimMappings
        claim_validation_rules: Optional[list[JWTAuthenticatorValidationRule]]
        issuer: JWTAuthenticatorIssuer
        provisioning_state: Optional[Union[str, JWTAuthenticatorProvisioningState]]
        user_validation_rules: Optional[list[JWTAuthenticatorValidationRule]]

        @overload
        def __init__(
                self, 
                *, 
                claim_mappings: JWTAuthenticatorClaimMappings, 
                claim_validation_rules: Optional[list[JWTAuthenticatorValidationRule]] = ..., 
                issuer: JWTAuthenticatorIssuer, 
                user_validation_rules: Optional[list[JWTAuthenticatorValidationRule]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.JWTAuthenticatorProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.containerservice.models.JWTAuthenticatorValidationRule(_Model):
        expression: str
        message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                expression: str, 
                message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.KeyVaultNetworkAccessTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRIVATE = "Private"
        PUBLIC = "Public"


    class azure.mgmt.containerservice.models.KubeReserved(_Model):
        cpu_millicores: Optional[int]
        memory_mb: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                cpu_millicores: Optional[int] = ..., 
                memory_mb: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.KubeletConfig(_Model):
        allowed_unsafe_sysctls: Optional[list[str]]
        container_log_max_files: Optional[int]
        container_log_max_size_mb: Optional[int]
        cpu_cfs_quota: Optional[bool]
        cpu_cfs_quota_period: Optional[str]
        cpu_manager_policy: Optional[str]
        fail_swap_on: Optional[bool]
        hard_eviction_threshold: Optional[HardEvictionThreshold]
        image_gc_high_threshold: Optional[int]
        image_gc_low_threshold: Optional[int]
        kube_reserved: Optional[KubeReserved]
        pod_max_pids: Optional[int]
        seccomp_default: Optional[Union[str, SeccompDefault]]
        topology_manager_policy: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                allowed_unsafe_sysctls: Optional[list[str]] = ..., 
                container_log_max_files: Optional[int] = ..., 
                container_log_max_size_mb: Optional[int] = ..., 
                cpu_cfs_quota: Optional[bool] = ..., 
                cpu_cfs_quota_period: Optional[str] = ..., 
                cpu_manager_policy: Optional[str] = ..., 
                fail_swap_on: Optional[bool] = ..., 
                hard_eviction_threshold: Optional[HardEvictionThreshold] = ..., 
                image_gc_high_threshold: Optional[int] = ..., 
                image_gc_low_threshold: Optional[int] = ..., 
                kube_reserved: Optional[KubeReserved] = ..., 
                pod_max_pids: Optional[int] = ..., 
                seccomp_default: Optional[Union[str, SeccompDefault]] = ..., 
                topology_manager_policy: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.KubeletDiskType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OS = "OS"
        TEMPORARY = "Temporary"


    class azure.mgmt.containerservice.models.KubernetesPatchVersion(_Model):
        upgrades: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                upgrades: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.KubernetesResourceObjectEncryptionProfile(_Model):
        infrastructure_encryption: Optional[Union[str, InfrastructureEncryption]]

        @overload
        def __init__(
                self, 
                *, 
                infrastructure_encryption: Optional[Union[str, InfrastructureEncryption]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.KubernetesSupportPlan(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AKS_LONG_TERM_SUPPORT = "AKSLongTermSupport"
        KUBERNETES_OFFICIAL = "KubernetesOfficial"


    class azure.mgmt.containerservice.models.KubernetesVersion(_Model):
        capabilities: Optional[KubernetesVersionCapabilities]
        is_default: Optional[bool]
        is_preview: Optional[bool]
        patch_versions: Optional[dict[str, KubernetesPatchVersion]]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                capabilities: Optional[KubernetesVersionCapabilities] = ..., 
                is_default: Optional[bool] = ..., 
                is_preview: Optional[bool] = ..., 
                patch_versions: Optional[dict[str, KubernetesPatchVersion]] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.KubernetesVersionCapabilities(_Model):
        support_plan: Optional[list[Union[str, KubernetesSupportPlan]]]

        @overload
        def __init__(
                self, 
                *, 
                support_plan: Optional[list[Union[str, KubernetesSupportPlan]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.KubernetesVersionListResult(_Model):
        values_property: Optional[list[KubernetesVersion]]

        @overload
        def __init__(
                self, 
                *, 
                values_property: Optional[list[KubernetesVersion]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.LabelSelector(_Model):
        match_expressions: Optional[list[LabelSelectorRequirement]]
        match_labels: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                match_expressions: Optional[list[LabelSelectorRequirement]] = ..., 
                match_labels: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.LabelSelectorRequirement(_Model):
        key: Optional[str]
        operator: Optional[Union[str, Operator]]
        values_property: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                operator: Optional[Union[str, Operator]] = ..., 
                values_property: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.LicenseType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        WINDOWS_SERVER = "Windows_Server"


    class azure.mgmt.containerservice.models.LinuxOSConfig(_Model):
        swap_file_size_mb: Optional[int]
        sysctls: Optional[SysctlConfig]
        transparent_huge_page_defrag: Optional[str]
        transparent_huge_page_enabled: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                swap_file_size_mb: Optional[int] = ..., 
                sysctls: Optional[SysctlConfig] = ..., 
                transparent_huge_page_defrag: Optional[str] = ..., 
                transparent_huge_page_enabled: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ListBootstrapDataRequest(_Model):


    class azure.mgmt.containerservice.models.LoadBalancer(ProxyResource):
        id: str
        name: str
        properties: Optional[LoadBalancerProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[LoadBalancerProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.containerservice.models.LoadBalancerProperties(_Model):
        allow_service_placement: Optional[bool]
        node_selector: Optional[LabelSelector]
        primary_agent_pool_name: str
        provisioning_state: Optional[str]
        service_label_selector: Optional[LabelSelector]
        service_namespace_selector: Optional[LabelSelector]

        @overload
        def __init__(
                self, 
                *, 
                allow_service_placement: Optional[bool] = ..., 
                node_selector: Optional[LabelSelector] = ..., 
                primary_agent_pool_name: str, 
                service_label_selector: Optional[LabelSelector] = ..., 
                service_namespace_selector: Optional[LabelSelector] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.LoadBalancerSku(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC = "basic"
        SERVICE = "service"
        STANDARD = "standard"


    class azure.mgmt.containerservice.models.LocalDNSForwardDestination(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLUSTER_CORE_DNS = "ClusterCoreDNS"
        VNET_DNS = "VnetDNS"


    class azure.mgmt.containerservice.models.LocalDNSForwardPolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        RANDOM = "Random"
        ROUND_ROBIN = "RoundRobin"
        SEQUENTIAL = "Sequential"


    class azure.mgmt.containerservice.models.LocalDNSMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        PREFERRED = "Preferred"
        REQUIRED = "Required"


    class azure.mgmt.containerservice.models.LocalDNSOverride(_Model):
        cache_duration_in_seconds: Optional[int]
        forward_destination: Optional[Union[str, LocalDNSForwardDestination]]
        forward_policy: Optional[Union[str, LocalDNSForwardPolicy]]
        max_concurrent: Optional[int]
        protocol: Optional[Union[str, LocalDNSProtocol]]
        query_logging: Optional[Union[str, LocalDNSQueryLogging]]
        serve_stale: Optional[Union[str, LocalDNSServeStale]]
        serve_stale_duration_in_seconds: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                cache_duration_in_seconds: Optional[int] = ..., 
                forward_destination: Optional[Union[str, LocalDNSForwardDestination]] = ..., 
                forward_policy: Optional[Union[str, LocalDNSForwardPolicy]] = ..., 
                max_concurrent: Optional[int] = ..., 
                protocol: Optional[Union[str, LocalDNSProtocol]] = ..., 
                query_logging: Optional[Union[str, LocalDNSQueryLogging]] = ..., 
                serve_stale: Optional[Union[str, LocalDNSServeStale]] = ..., 
                serve_stale_duration_in_seconds: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.LocalDNSProfile(_Model):
        kube_dns_overrides: Optional[dict[str, LocalDNSOverride]]
        mode: Optional[Union[str, LocalDNSMode]]
        state: Optional[Union[str, LocalDNSState]]
        vnet_dns_overrides: Optional[dict[str, LocalDNSOverride]]

        @overload
        def __init__(
                self, 
                *, 
                kube_dns_overrides: Optional[dict[str, LocalDNSOverride]] = ..., 
                mode: Optional[Union[str, LocalDNSMode]] = ..., 
                vnet_dns_overrides: Optional[dict[str, LocalDNSOverride]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.LocalDNSProtocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FORCE_TCP = "ForceTCP"
        PREFER_UDP = "PreferUDP"


    class azure.mgmt.containerservice.models.LocalDNSQueryLogging(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ERROR = "Error"
        LOG = "Log"


    class azure.mgmt.containerservice.models.LocalDNSServeStale(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLE = "Disable"
        IMMEDIATE = "Immediate"
        VERIFY = "Verify"


    class azure.mgmt.containerservice.models.LocalDNSState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.containerservice.models.Machine(ProxyResource):
        id: str
        name: str
        properties: Optional[MachineProperties]
        system_data: SystemData
        type: str
        zones: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[MachineProperties] = ..., 
                zones: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.MachineBillingProfile(_Model):
        spot_max_price: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                spot_max_price: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.MachineHardwareProfile(_Model):
        gpu_instance_profile: Optional[Union[str, GPUInstanceProfile]]
        gpu_profile: Optional[GPUProfile]
        ultra_ssd_enabled: Optional[bool]
        vm_size: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                gpu_instance_profile: Optional[Union[str, GPUInstanceProfile]] = ..., 
                gpu_profile: Optional[GPUProfile] = ..., 
                ultra_ssd_enabled: Optional[bool] = ..., 
                vm_size: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.MachineIpAddress(_Model):
        family: Optional[Union[str, IPFamily]]
        ip: Optional[str]


    class azure.mgmt.containerservice.models.MachineKubernetesProfile(_Model):
        artifact_streaming_profile: Optional[AgentPoolArtifactStreamingProfile]
        current_orchestrator_version: Optional[str]
        kubelet_config: Optional[KubeletConfig]
        kubelet_disk_type: Optional[Union[str, KubeletDiskType]]
        max_pods: Optional[int]
        node_initialization_taints: Optional[list[str]]
        node_labels: Optional[dict[str, str]]
        node_name: Optional[str]
        node_taints: Optional[list[str]]
        orchestrator_version: Optional[str]
        workload_runtime: Optional[Union[str, WorkloadRuntime]]

        @overload
        def __init__(
                self, 
                *, 
                artifact_streaming_profile: Optional[AgentPoolArtifactStreamingProfile] = ..., 
                kubelet_config: Optional[KubeletConfig] = ..., 
                kubelet_disk_type: Optional[Union[str, KubeletDiskType]] = ..., 
                max_pods: Optional[int] = ..., 
                node_initialization_taints: Optional[list[str]] = ..., 
                node_labels: Optional[dict[str, str]] = ..., 
                node_taints: Optional[list[str]] = ..., 
                orchestrator_version: Optional[str] = ..., 
                workload_runtime: Optional[Union[str, WorkloadRuntime]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.MachineNetworkProperties(_Model):
        enable_node_public_ip: Optional[bool]
        ip_addresses: Optional[list[MachineIpAddress]]
        node_public_ip_prefix_id: Optional[str]
        node_public_ip_tags: Optional[list[IPTag]]
        pod_subnet_id: Optional[str]
        vnet_subnet_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                enable_node_public_ip: Optional[bool] = ..., 
                node_public_ip_prefix_id: Optional[str] = ..., 
                node_public_ip_tags: Optional[list[IPTag]] = ..., 
                pod_subnet_id: Optional[str] = ..., 
                vnet_subnet_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.MachineOSProfile(_Model):
        enable_fips: Optional[bool]
        linux_profile: Optional[MachineOSProfileLinuxProfile]
        os_disk_size_gb: Optional[int]
        os_disk_type: Optional[Union[str, OSDiskType]]
        os_sku: Optional[Union[str, _models.OSSKU]]
        os_type: Optional[Union[str, OSType]]
        windows_profile: Optional[AgentPoolWindowsProfile]

        @overload
        def __init__(
                self, 
                *, 
                enable_fips: Optional[bool] = ..., 
                linux_profile: Optional[MachineOSProfileLinuxProfile] = ..., 
                os_disk_size_gb: Optional[int] = ..., 
                os_disk_type: Optional[Union[str, OSDiskType]] = ..., 
                os_sku: Optional[Union[str, _models.OSSKU]] = ..., 
                os_type: Optional[Union[str, OSType]] = ..., 
                windows_profile: Optional[AgentPoolWindowsProfile] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.MachineOSProfileLinuxProfile(_Model):
        linux_os_config: Optional[LinuxOSConfig]
        message_of_the_day: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                linux_os_config: Optional[LinuxOSConfig] = ..., 
                message_of_the_day: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.MachineProperties(_Model):
        billing: Optional[MachineBillingProfile]
        e_tag: Optional[str]
        eviction_policy: Optional[Union[str, ScaleSetEvictionPolicy]]
        hardware: Optional[MachineHardwareProfile]
        kubernetes: Optional[MachineKubernetesProfile]
        local_dns_profile: Optional[LocalDNSProfile]
        mode: Optional[Union[str, AgentPoolMode]]
        network: Optional[MachineNetworkProperties]
        node_image_version: Optional[str]
        operating_system: Optional[MachineOSProfile]
        priority: Optional[Union[str, ScaleSetPriority]]
        provisioning_state: Optional[str]
        resource_id: Optional[str]
        security: Optional[MachineSecurityProfile]
        status: Optional[MachineStatus]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                billing: Optional[MachineBillingProfile] = ..., 
                eviction_policy: Optional[Union[str, ScaleSetEvictionPolicy]] = ..., 
                hardware: Optional[MachineHardwareProfile] = ..., 
                kubernetes: Optional[MachineKubernetesProfile] = ..., 
                local_dns_profile: Optional[LocalDNSProfile] = ..., 
                mode: Optional[Union[str, AgentPoolMode]] = ..., 
                network: Optional[MachineNetworkProperties] = ..., 
                operating_system: Optional[MachineOSProfile] = ..., 
                priority: Optional[Union[str, ScaleSetPriority]] = ..., 
                security: Optional[MachineSecurityProfile] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.MachineSecurityProfile(_Model):
        enable_encryption_at_host: Optional[bool]
        enable_secure_boot: Optional[bool]
        enable_vtpm: Optional[bool]
        ssh_access: Optional[Union[str, AgentPoolSSHAccess]]

        @overload
        def __init__(
                self, 
                *, 
                enable_encryption_at_host: Optional[bool] = ..., 
                enable_secure_boot: Optional[bool] = ..., 
                enable_vtpm: Optional[bool] = ..., 
                ssh_access: Optional[Union[str, AgentPoolSSHAccess]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.MachineStatus(_Model):
        creation_timestamp: Optional[datetime]
        drift_action: Optional[Union[str, DriftAction]]
        drift_reason: Optional[str]
        provisioning_error: Optional[ErrorDetail]
        vm_state: Optional[Union[str, VmState]]


    class azure.mgmt.containerservice.models.MaintenanceConfiguration(ProxyResource):
        id: str
        name: str
        properties: Optional[MaintenanceConfigurationProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[MaintenanceConfigurationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.containerservice.models.MaintenanceConfigurationProperties(_Model):
        maintenance_window: Optional[MaintenanceWindow]
        maintenance_window_id: Optional[str]
        not_allowed_time: Optional[list[TimeSpan]]
        time_in_week: Optional[list[TimeInWeek]]

        @overload
        def __init__(
                self, 
                *, 
                maintenance_window: Optional[MaintenanceWindow] = ..., 
                maintenance_window_id: Optional[str] = ..., 
                not_allowed_time: Optional[list[TimeSpan]] = ..., 
                time_in_week: Optional[list[TimeInWeek]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.MaintenanceWindow(_Model):
        duration_hours: int
        not_allowed_dates: Optional[list[DateSpan]]
        schedule: Schedule
        start_date: Optional[date]
        start_time: str
        utc_offset: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                duration_hours: int, 
                not_allowed_dates: Optional[list[DateSpan]] = ..., 
                schedule: Schedule, 
                start_date: Optional[date] = ..., 
                start_time: str, 
                utc_offset: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.MaintenanceWindowResource(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[MaintenanceWindowResourceProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[MaintenanceWindowResourceProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.MaintenanceWindowResourceProperties(_Model):
        duration_hours: int
        not_allowed_dates: Optional[list[DateSpan]]
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]
        schedule: Schedule
        start_date: Optional[date]
        start_time: str
        utc_offset: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                duration_hours: int, 
                not_allowed_dates: Optional[list[DateSpan]] = ..., 
                schedule: Schedule, 
                start_date: Optional[date] = ..., 
                start_time: str, 
                utc_offset: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedCluster(TrackedResource):
        e_tag: Optional[str]
        extended_location: Optional[ExtendedLocation]
        id: str
        identity: Optional[ManagedClusterIdentity]
        kind: Optional[str]
        location: str
        name: str
        properties: Optional[ManagedClusterProperties]
        sku: Optional[ManagedClusterSKU]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                identity: Optional[ManagedClusterIdentity] = ..., 
                kind: Optional[str] = ..., 
                location: str, 
                properties: Optional[ManagedClusterProperties] = ..., 
                sku: Optional[ManagedClusterSKU] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterAADProfile(_Model):
        admin_group_object_i_ds: Optional[list[str]]
        client_app_id: Optional[str]
        enable_azure_rbac: Optional[bool]
        managed: Optional[bool]
        server_app_id: Optional[str]
        server_app_secret: Optional[str]
        tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                admin_group_object_i_ds: Optional[list[str]] = ..., 
                client_app_id: Optional[str] = ..., 
                enable_azure_rbac: Optional[bool] = ..., 
                managed: Optional[bool] = ..., 
                server_app_id: Optional[str] = ..., 
                server_app_secret: Optional[str] = ..., 
                tenant_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterAIToolchainOperatorProfile(_Model):
        enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterAPIServerAccessProfile(_Model):
        authorized_ip_ranges: Optional[list[str]]
        disable_run_command: Optional[bool]
        enable_private_cluster: Optional[bool]
        enable_private_cluster_public_fqdn: Optional[bool]
        enable_vnet_integration: Optional[bool]
        private_dns_zone: Optional[str]
        subnet_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                authorized_ip_ranges: Optional[list[str]] = ..., 
                disable_run_command: Optional[bool] = ..., 
                enable_private_cluster: Optional[bool] = ..., 
                enable_private_cluster_public_fqdn: Optional[bool] = ..., 
                enable_vnet_integration: Optional[bool] = ..., 
                private_dns_zone: Optional[str] = ..., 
                subnet_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterAccessProfile(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[AccessProfile]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[AccessProfile] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterAddonProfile(_Model):
        config: Optional[dict[str, str]]
        enabled: bool
        identity: Optional[ManagedClusterAddonProfileIdentity]

        @overload
        def __init__(
                self, 
                *, 
                config: Optional[dict[str, str]] = ..., 
                enabled: bool
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterAddonProfileIdentity(UserAssignedIdentity):
        client_id: str
        object_id: str
        resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                client_id: Optional[str] = ..., 
                object_id: Optional[str] = ..., 
                resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterAgentPoolProfile(ManagedClusterAgentPoolProfileProperties):
        artifact_streaming_profile: AgentPoolArtifactStreamingProfile
        availability_zones: list[str]
        capacity_reservation_group_id: str
        count: int
        creation_data: CreationData
        current_orchestrator_version: str
        e_tag: str
        enable_auto_scaling: bool
        enable_encryption_at_host: bool
        enable_fips: bool
        enable_node_public_ip: bool
        enable_os_disk_full_caching: bool
        enable_ultra_ssd: bool
        gateway_profile: AgentPoolGatewayProfile
        gpu_instance_profile: Union[str, GPUInstanceProfile]
        gpu_profile: GPUProfile
        host_group_id: str
        kubelet_config: KubeletConfig
        kubelet_disk_type: Union[str, KubeletDiskType]
        linux_os_config: LinuxOSConfig
        local_dns_profile: LocalDNSProfile
        max_count: int
        max_pods: int
        message_of_the_day: str
        min_count: int
        mode: Union[str, AgentPoolMode]
        name: str
        network_profile: AgentPoolNetworkProfile
        node_image_version: str
        node_initialization_taints: list[str]
        node_labels: dict[str, str]
        node_public_ip_prefix_id: str
        node_taints: list[str]
        orchestrator_version: str
        os_disk_size_gb: int
        os_disk_type: Union[str, OSDiskType]
        os_sku: Union[str, azure.mgmt.containerservice.models.OSSKU]
        os_type: Union[str, OSType]
        pod_ip_allocation_mode: Union[str, PodIPAllocationMode]
        pod_subnet_id: str
        power_state: PowerState
        prepared_image_specification_profile: PreparedImageSpecificationProfile
        provisioning_state: str
        proximity_placement_group_id: str
        scale_down_mode: Union[str, ScaleDownMode]
        scale_set_eviction_policy: Union[str, ScaleSetEvictionPolicy]
        scale_set_priority: Union[str, ScaleSetPriority]
        security_profile: AgentPoolSecurityProfile
        spot_max_price: float
        status: AgentPoolStatus
        tags: dict[str, str]
        type: Union[str, AgentPoolType]
        upgrade_settings: AgentPoolUpgradeSettings
        upgrade_settings_blue_green: AgentPoolBlueGreenUpgradeSettings
        upgrade_strategy: Union[str, UpgradeStrategy]
        virtual_machine_nodes_status: list[VirtualMachineNodes]
        virtual_machines_profile: VirtualMachinesProfile
        vm_size: str
        vnet_subnet_id: str
        windows_profile: AgentPoolWindowsProfile
        workload_runtime: Union[str, WorkloadRuntime]

        @overload
        def __init__(
                self, 
                *, 
                artifact_streaming_profile: Optional[AgentPoolArtifactStreamingProfile] = ..., 
                availability_zones: Optional[list[str]] = ..., 
                capacity_reservation_group_id: Optional[str] = ..., 
                count: Optional[int] = ..., 
                creation_data: Optional[CreationData] = ..., 
                enable_auto_scaling: Optional[bool] = ..., 
                enable_encryption_at_host: Optional[bool] = ..., 
                enable_fips: Optional[bool] = ..., 
                enable_node_public_ip: Optional[bool] = ..., 
                enable_os_disk_full_caching: Optional[bool] = ..., 
                enable_ultra_ssd: Optional[bool] = ..., 
                gateway_profile: Optional[AgentPoolGatewayProfile] = ..., 
                gpu_instance_profile: Optional[Union[str, GPUInstanceProfile]] = ..., 
                gpu_profile: Optional[GPUProfile] = ..., 
                host_group_id: Optional[str] = ..., 
                kubelet_config: Optional[KubeletConfig] = ..., 
                kubelet_disk_type: Optional[Union[str, KubeletDiskType]] = ..., 
                linux_os_config: Optional[LinuxOSConfig] = ..., 
                local_dns_profile: Optional[LocalDNSProfile] = ..., 
                max_count: Optional[int] = ..., 
                max_pods: Optional[int] = ..., 
                message_of_the_day: Optional[str] = ..., 
                min_count: Optional[int] = ..., 
                mode: Optional[Union[str, AgentPoolMode]] = ..., 
                name: str, 
                network_profile: Optional[AgentPoolNetworkProfile] = ..., 
                node_image_version: Optional[str] = ..., 
                node_initialization_taints: Optional[list[str]] = ..., 
                node_labels: Optional[dict[str, str]] = ..., 
                node_public_ip_prefix_id: Optional[str] = ..., 
                node_taints: Optional[list[str]] = ..., 
                orchestrator_version: Optional[str] = ..., 
                os_disk_size_gb: Optional[int] = ..., 
                os_disk_type: Optional[Union[str, OSDiskType]] = ..., 
                os_sku: Optional[Union[str, _models.OSSKU]] = ..., 
                os_type: Optional[Union[str, OSType]] = ..., 
                pod_ip_allocation_mode: Optional[Union[str, PodIPAllocationMode]] = ..., 
                pod_subnet_id: Optional[str] = ..., 
                power_state: Optional[PowerState] = ..., 
                prepared_image_specification_profile: Optional[PreparedImageSpecificationProfile] = ..., 
                proximity_placement_group_id: Optional[str] = ..., 
                scale_down_mode: Optional[Union[str, ScaleDownMode]] = ..., 
                scale_set_eviction_policy: Optional[Union[str, ScaleSetEvictionPolicy]] = ..., 
                scale_set_priority: Optional[Union[str, ScaleSetPriority]] = ..., 
                security_profile: Optional[AgentPoolSecurityProfile] = ..., 
                spot_max_price: Optional[float] = ..., 
                status: Optional[AgentPoolStatus] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                type: Optional[Union[str, AgentPoolType]] = ..., 
                upgrade_settings: Optional[AgentPoolUpgradeSettings] = ..., 
                upgrade_settings_blue_green: Optional[AgentPoolBlueGreenUpgradeSettings] = ..., 
                upgrade_strategy: Optional[Union[str, UpgradeStrategy]] = ..., 
                virtual_machine_nodes_status: Optional[list[VirtualMachineNodes]] = ..., 
                virtual_machines_profile: Optional[VirtualMachinesProfile] = ..., 
                vm_size: Optional[str] = ..., 
                vnet_subnet_id: Optional[str] = ..., 
                windows_profile: Optional[AgentPoolWindowsProfile] = ..., 
                workload_runtime: Optional[Union[str, WorkloadRuntime]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterAgentPoolProfileProperties(_Model):
        artifact_streaming_profile: Optional[AgentPoolArtifactStreamingProfile]
        availability_zones: Optional[list[str]]
        capacity_reservation_group_id: Optional[str]
        count: Optional[int]
        creation_data: Optional[CreationData]
        current_orchestrator_version: Optional[str]
        e_tag: Optional[str]
        enable_auto_scaling: Optional[bool]
        enable_encryption_at_host: Optional[bool]
        enable_fips: Optional[bool]
        enable_node_public_ip: Optional[bool]
        enable_os_disk_full_caching: Optional[bool]
        enable_ultra_ssd: Optional[bool]
        gateway_profile: Optional[AgentPoolGatewayProfile]
        gpu_instance_profile: Optional[Union[str, GPUInstanceProfile]]
        gpu_profile: Optional[GPUProfile]
        host_group_id: Optional[str]
        kubelet_config: Optional[KubeletConfig]
        kubelet_disk_type: Optional[Union[str, KubeletDiskType]]
        linux_os_config: Optional[LinuxOSConfig]
        local_dns_profile: Optional[LocalDNSProfile]
        max_count: Optional[int]
        max_pods: Optional[int]
        message_of_the_day: Optional[str]
        min_count: Optional[int]
        mode: Optional[Union[str, AgentPoolMode]]
        network_profile: Optional[AgentPoolNetworkProfile]
        node_image_version: Optional[str]
        node_initialization_taints: Optional[list[str]]
        node_labels: Optional[dict[str, str]]
        node_public_ip_prefix_id: Optional[str]
        node_taints: Optional[list[str]]
        orchestrator_version: Optional[str]
        os_disk_size_gb: Optional[int]
        os_disk_type: Optional[Union[str, OSDiskType]]
        os_sku: Optional[Union[str, _models.OSSKU]]
        os_type: Optional[Union[str, OSType]]
        pod_ip_allocation_mode: Optional[Union[str, PodIPAllocationMode]]
        pod_subnet_id: Optional[str]
        power_state: Optional[PowerState]
        prepared_image_specification_profile: Optional[PreparedImageSpecificationProfile]
        provisioning_state: Optional[str]
        proximity_placement_group_id: Optional[str]
        scale_down_mode: Optional[Union[str, ScaleDownMode]]
        scale_set_eviction_policy: Optional[Union[str, ScaleSetEvictionPolicy]]
        scale_set_priority: Optional[Union[str, ScaleSetPriority]]
        security_profile: Optional[AgentPoolSecurityProfile]
        spot_max_price: Optional[float]
        status: Optional[AgentPoolStatus]
        tags: Optional[dict[str, str]]
        type: Optional[Union[str, AgentPoolType]]
        upgrade_settings: Optional[AgentPoolUpgradeSettings]
        upgrade_settings_blue_green: Optional[AgentPoolBlueGreenUpgradeSettings]
        upgrade_strategy: Optional[Union[str, UpgradeStrategy]]
        virtual_machine_nodes_status: Optional[list[VirtualMachineNodes]]
        virtual_machines_profile: Optional[VirtualMachinesProfile]
        vm_size: Optional[str]
        vnet_subnet_id: Optional[str]
        windows_profile: Optional[AgentPoolWindowsProfile]
        workload_runtime: Optional[Union[str, WorkloadRuntime]]

        @overload
        def __init__(
                self, 
                *, 
                artifact_streaming_profile: Optional[AgentPoolArtifactStreamingProfile] = ..., 
                availability_zones: Optional[list[str]] = ..., 
                capacity_reservation_group_id: Optional[str] = ..., 
                count: Optional[int] = ..., 
                creation_data: Optional[CreationData] = ..., 
                enable_auto_scaling: Optional[bool] = ..., 
                enable_encryption_at_host: Optional[bool] = ..., 
                enable_fips: Optional[bool] = ..., 
                enable_node_public_ip: Optional[bool] = ..., 
                enable_os_disk_full_caching: Optional[bool] = ..., 
                enable_ultra_ssd: Optional[bool] = ..., 
                gateway_profile: Optional[AgentPoolGatewayProfile] = ..., 
                gpu_instance_profile: Optional[Union[str, GPUInstanceProfile]] = ..., 
                gpu_profile: Optional[GPUProfile] = ..., 
                host_group_id: Optional[str] = ..., 
                kubelet_config: Optional[KubeletConfig] = ..., 
                kubelet_disk_type: Optional[Union[str, KubeletDiskType]] = ..., 
                linux_os_config: Optional[LinuxOSConfig] = ..., 
                local_dns_profile: Optional[LocalDNSProfile] = ..., 
                max_count: Optional[int] = ..., 
                max_pods: Optional[int] = ..., 
                message_of_the_day: Optional[str] = ..., 
                min_count: Optional[int] = ..., 
                mode: Optional[Union[str, AgentPoolMode]] = ..., 
                network_profile: Optional[AgentPoolNetworkProfile] = ..., 
                node_image_version: Optional[str] = ..., 
                node_initialization_taints: Optional[list[str]] = ..., 
                node_labels: Optional[dict[str, str]] = ..., 
                node_public_ip_prefix_id: Optional[str] = ..., 
                node_taints: Optional[list[str]] = ..., 
                orchestrator_version: Optional[str] = ..., 
                os_disk_size_gb: Optional[int] = ..., 
                os_disk_type: Optional[Union[str, OSDiskType]] = ..., 
                os_sku: Optional[Union[str, _models.OSSKU]] = ..., 
                os_type: Optional[Union[str, OSType]] = ..., 
                pod_ip_allocation_mode: Optional[Union[str, PodIPAllocationMode]] = ..., 
                pod_subnet_id: Optional[str] = ..., 
                power_state: Optional[PowerState] = ..., 
                prepared_image_specification_profile: Optional[PreparedImageSpecificationProfile] = ..., 
                proximity_placement_group_id: Optional[str] = ..., 
                scale_down_mode: Optional[Union[str, ScaleDownMode]] = ..., 
                scale_set_eviction_policy: Optional[Union[str, ScaleSetEvictionPolicy]] = ..., 
                scale_set_priority: Optional[Union[str, ScaleSetPriority]] = ..., 
                security_profile: Optional[AgentPoolSecurityProfile] = ..., 
                spot_max_price: Optional[float] = ..., 
                status: Optional[AgentPoolStatus] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                type: Optional[Union[str, AgentPoolType]] = ..., 
                upgrade_settings: Optional[AgentPoolUpgradeSettings] = ..., 
                upgrade_settings_blue_green: Optional[AgentPoolBlueGreenUpgradeSettings] = ..., 
                upgrade_strategy: Optional[Union[str, UpgradeStrategy]] = ..., 
                virtual_machine_nodes_status: Optional[list[VirtualMachineNodes]] = ..., 
                virtual_machines_profile: Optional[VirtualMachinesProfile] = ..., 
                vm_size: Optional[str] = ..., 
                vnet_subnet_id: Optional[str] = ..., 
                windows_profile: Optional[AgentPoolWindowsProfile] = ..., 
                workload_runtime: Optional[Union[str, WorkloadRuntime]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterAppRoutingIstio(_Model):
        mode: Optional[Union[str, GatewayAPIIstioEnabled]]

        @overload
        def __init__(
                self, 
                *, 
                mode: Optional[Union[str, GatewayAPIIstioEnabled]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterAutoUpgradeProfile(_Model):
        node_os_upgrade_channel: Optional[Union[str, NodeOSUpgradeChannel]]
        upgrade_channel: Optional[Union[str, UpgradeChannel]]

        @overload
        def __init__(
                self, 
                *, 
                node_os_upgrade_channel: Optional[Union[str, NodeOSUpgradeChannel]] = ..., 
                upgrade_channel: Optional[Union[str, UpgradeChannel]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterAzureMonitorProfile(_Model):
        app_monitoring: Optional[ManagedClusterAzureMonitorProfileAppMonitoring]
        container_insights: Optional[ManagedClusterAzureMonitorProfileContainerInsights]
        metrics: Optional[ManagedClusterAzureMonitorProfileMetrics]

        @overload
        def __init__(
                self, 
                *, 
                app_monitoring: Optional[ManagedClusterAzureMonitorProfileAppMonitoring] = ..., 
                container_insights: Optional[ManagedClusterAzureMonitorProfileContainerInsights] = ..., 
                metrics: Optional[ManagedClusterAzureMonitorProfileMetrics] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterAzureMonitorProfileAppMonitoring(_Model):
        auto_instrumentation: Optional[ManagedClusterAzureMonitorProfileAppMonitoringAutoInstrumentation]
        open_telemetry_logs_and_traces: Optional[ManagedClusterAzureMonitorProfileAppMonitoringOpenTelemetryLogsAndTraces]
        open_telemetry_metrics: Optional[ManagedClusterAzureMonitorProfileAppMonitoringOpenTelemetryMetrics]

        @overload
        def __init__(
                self, 
                *, 
                auto_instrumentation: Optional[ManagedClusterAzureMonitorProfileAppMonitoringAutoInstrumentation] = ..., 
                open_telemetry_logs_and_traces: Optional[ManagedClusterAzureMonitorProfileAppMonitoringOpenTelemetryLogsAndTraces] = ..., 
                open_telemetry_metrics: Optional[ManagedClusterAzureMonitorProfileAppMonitoringOpenTelemetryMetrics] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterAzureMonitorProfileAppMonitoringAutoInstrumentation(_Model):
        enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterAzureMonitorProfileAppMonitoringOpenTelemetryLogsAndTraces(_Model):
        enabled: Optional[bool]
        grpc_port: Optional[int]
        http_port: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                grpc_port: Optional[int] = ..., 
                http_port: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterAzureMonitorProfileAppMonitoringOpenTelemetryMetrics(_Model):
        enabled: Optional[bool]
        grpc_port: Optional[int]
        http_port: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                grpc_port: Optional[int] = ..., 
                http_port: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterAzureMonitorProfileContainerInsights(_Model):
        container_network_logs: Optional[Union[str, ContainerNetworkLogs]]
        disable_custom_metrics: Optional[bool]
        disable_prometheus_metrics_scraping: Optional[bool]
        enabled: Optional[bool]
        log_analytics_workspace_resource_id: Optional[str]
        syslog_port: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                container_network_logs: Optional[Union[str, ContainerNetworkLogs]] = ..., 
                disable_custom_metrics: Optional[bool] = ..., 
                disable_prometheus_metrics_scraping: Optional[bool] = ..., 
                enabled: Optional[bool] = ..., 
                log_analytics_workspace_resource_id: Optional[str] = ..., 
                syslog_port: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterAzureMonitorProfileKubeStateMetrics(_Model):
        metric_annotations_allow_list: Optional[str]
        metric_labels_allowlist: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                metric_annotations_allow_list: Optional[str] = ..., 
                metric_labels_allowlist: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterAzureMonitorProfileMetrics(_Model):
        control_plane: Optional[ManagedClusterAzureMonitorProfileMetricsControlPlane]
        enabled: bool
        kube_state_metrics: Optional[ManagedClusterAzureMonitorProfileKubeStateMetrics]

        @overload
        def __init__(
                self, 
                *, 
                control_plane: Optional[ManagedClusterAzureMonitorProfileMetricsControlPlane] = ..., 
                enabled: bool, 
                kube_state_metrics: Optional[ManagedClusterAzureMonitorProfileKubeStateMetrics] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterAzureMonitorProfileMetricsControlPlane(_Model):
        enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterBootstrapProfile(_Model):
        artifact_source: Optional[Union[str, ArtifactSource]]
        container_registry_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                artifact_source: Optional[Union[str, ArtifactSource]] = ..., 
                container_registry_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterControlPlaneScalingProfile(_Model):
        scaling_size: Union[str, ControlPlaneScalingSize]

        @overload
        def __init__(
                self, 
                *, 
                scaling_size: Union[str, ControlPlaneScalingSize]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterCostAnalysis(_Model):
        enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterHTTPProxyConfig(_Model):
        effective_no_proxy: Optional[list[str]]
        enabled: Optional[bool]
        http_proxy: Optional[str]
        https_proxy: Optional[str]
        no_proxy: Optional[list[str]]
        trusted_ca: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                http_proxy: Optional[str] = ..., 
                https_proxy: Optional[str] = ..., 
                no_proxy: Optional[list[str]] = ..., 
                trusted_ca: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterHealthMonitorProfile(_Model):
        enable_continuous_control_plane_and_addon_monitor: Optional[bool]
        enable_on_demand_monitor: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                enable_continuous_control_plane_and_addon_monitor: Optional[bool] = ..., 
                enable_on_demand_monitor: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterHostedSystemProfile(_Model):
        enabled: Optional[bool]
        node_subnet_id: Optional[str]
        system_node_subnet_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                node_subnet_id: Optional[str] = ..., 
                system_node_subnet_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterIdentity(_Model):
        delegated_resources: Optional[dict[str, DelegatedResource]]
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Optional[Union[str, ResourceIdentityType]]
        user_assigned_identities: Optional[dict[str, ManagedServiceIdentityUserAssignedIdentitiesValue]]

        @overload
        def __init__(
                self, 
                *, 
                delegated_resources: Optional[dict[str, DelegatedResource]] = ..., 
                type: Optional[Union[str, ResourceIdentityType]] = ..., 
                user_assigned_identities: Optional[dict[str, ManagedServiceIdentityUserAssignedIdentitiesValue]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterIngressDefaultDomainProfile(_Model):
        domain_name: Optional[str]
        enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterIngressProfile(_Model):
        application_load_balancer: Optional[ManagedClusterIngressProfileApplicationLoadBalancer]
        gateway_api: Optional[ManagedClusterIngressProfileGatewayConfiguration]
        web_app_routing: Optional[ManagedClusterIngressProfileWebAppRouting]

        @overload
        def __init__(
                self, 
                *, 
                application_load_balancer: Optional[ManagedClusterIngressProfileApplicationLoadBalancer] = ..., 
                gateway_api: Optional[ManagedClusterIngressProfileGatewayConfiguration] = ..., 
                web_app_routing: Optional[ManagedClusterIngressProfileWebAppRouting] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterIngressProfileApplicationLoadBalancer(_Model):
        enabled: Optional[bool]
        identity: Optional[UserAssignedIdentity]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterIngressProfileGatewayConfiguration(_Model):
        installation: Optional[Union[str, ManagedGatewayType]]

        @overload
        def __init__(
                self, 
                *, 
                installation: Optional[Union[str, ManagedGatewayType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterIngressProfileNginx(_Model):
        default_ingress_controller_type: Optional[Union[str, NginxIngressControllerType]]

        @overload
        def __init__(
                self, 
                *, 
                default_ingress_controller_type: Optional[Union[str, NginxIngressControllerType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterIngressProfileWebAppRouting(_Model):
        default_domain: Optional[ManagedClusterIngressDefaultDomainProfile]
        dns_zone_resource_ids: Optional[list[str]]
        enabled: Optional[bool]
        gateway_api_implementations: Optional[ManagedClusterWebAppRoutingGatewayAPIImplementations]
        identity: Optional[UserAssignedIdentity]
        nginx: Optional[ManagedClusterIngressProfileNginx]

        @overload
        def __init__(
                self, 
                *, 
                default_domain: Optional[ManagedClusterIngressDefaultDomainProfile] = ..., 
                dns_zone_resource_ids: Optional[list[str]] = ..., 
                enabled: Optional[bool] = ..., 
                gateway_api_implementations: Optional[ManagedClusterWebAppRoutingGatewayAPIImplementations] = ..., 
                nginx: Optional[ManagedClusterIngressProfileNginx] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterLoadBalancerProfile(_Model):
        allocated_outbound_ports: Optional[int]
        backend_pool_type: Optional[Union[str, BackendPoolType]]
        cluster_service_load_balancer_health_probe_mode: Optional[Union[str, ClusterServiceLoadBalancerHealthProbeMode]]
        effective_outbound_i_ps: Optional[list[ResourceReference]]
        enable_multiple_standard_load_balancers: Optional[bool]
        idle_timeout_in_minutes: Optional[int]
        managed_outbound_i_ps: Optional[ManagedClusterLoadBalancerProfileManagedOutboundIPs]
        outbound_i_ps: Optional[ManagedClusterLoadBalancerProfileOutboundIPs]
        outbound_ip_prefixes: Optional[ManagedClusterLoadBalancerProfileOutboundIPPrefixes]

        @overload
        def __init__(
                self, 
                *, 
                allocated_outbound_ports: Optional[int] = ..., 
                backend_pool_type: Optional[Union[str, BackendPoolType]] = ..., 
                cluster_service_load_balancer_health_probe_mode: Optional[Union[str, ClusterServiceLoadBalancerHealthProbeMode]] = ..., 
                enable_multiple_standard_load_balancers: Optional[bool] = ..., 
                idle_timeout_in_minutes: Optional[int] = ..., 
                managed_outbound_i_ps: Optional[ManagedClusterLoadBalancerProfileManagedOutboundIPs] = ..., 
                outbound_i_ps: Optional[ManagedClusterLoadBalancerProfileOutboundIPs] = ..., 
                outbound_ip_prefixes: Optional[ManagedClusterLoadBalancerProfileOutboundIPPrefixes] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterLoadBalancerProfileManagedOutboundIPs(_Model):
        count: Optional[int]
        count_ipv6: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                count: Optional[int] = ..., 
                count_ipv6: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterLoadBalancerProfileOutboundIPPrefixes(_Model):
        public_ip_prefixes: Optional[list[ResourceReference]]

        @overload
        def __init__(
                self, 
                *, 
                public_ip_prefixes: Optional[list[ResourceReference]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterLoadBalancerProfileOutboundIPs(_Model):
        public_i_ps: Optional[list[ResourceReference]]

        @overload
        def __init__(
                self, 
                *, 
                public_i_ps: Optional[list[ResourceReference]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterManagedOutboundIPProfile(_Model):
        count: Optional[int]
        count_i_pv6: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                count: Optional[int] = ..., 
                count_i_pv6: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterMetricsProfile(_Model):
        cost_analysis: Optional[ManagedClusterCostAnalysis]

        @overload
        def __init__(
                self, 
                *, 
                cost_analysis: Optional[ManagedClusterCostAnalysis] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterNATGatewayProfile(_Model):
        effective_outbound_i_ps: Optional[list[ResourceReference]]
        idle_timeout_in_minutes: Optional[int]
        managed_outbound_ip_profile: Optional[ManagedClusterManagedOutboundIPProfile]
        outbound_i_ps: Optional[ManagedClusterNATGatewayProfileOutboundIPs]
        outbound_ip_prefixes: Optional[ManagedClusterNATGatewayProfileOutboundIpPrefixes]

        @overload
        def __init__(
                self, 
                *, 
                idle_timeout_in_minutes: Optional[int] = ..., 
                managed_outbound_ip_profile: Optional[ManagedClusterManagedOutboundIPProfile] = ..., 
                outbound_i_ps: Optional[ManagedClusterNATGatewayProfileOutboundIPs] = ..., 
                outbound_ip_prefixes: Optional[ManagedClusterNATGatewayProfileOutboundIpPrefixes] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterNATGatewayProfileOutboundIPs(_Model):
        public_i_ps: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                public_i_ps: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterNATGatewayProfileOutboundIpPrefixes(_Model):
        public_ip_prefixes: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                public_ip_prefixes: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterNodeProvisioningProfile(_Model):
        default_node_pools: Optional[Union[str, NodeProvisioningDefaultNodePools]]
        mode: Optional[Union[str, NodeProvisioningMode]]

        @overload
        def __init__(
                self, 
                *, 
                default_node_pools: Optional[Union[str, NodeProvisioningDefaultNodePools]] = ..., 
                mode: Optional[Union[str, NodeProvisioningMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterNodeResourceGroupProfile(_Model):
        restriction_level: Optional[Union[str, RestrictionLevel]]

        @overload
        def __init__(
                self, 
                *, 
                restriction_level: Optional[Union[str, RestrictionLevel]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterOIDCIssuerProfile(_Model):
        enabled: Optional[bool]
        issuer_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterPodIdentity(_Model):
        binding_selector: Optional[str]
        identity: UserAssignedIdentity
        name: str
        namespace: str
        provisioning_info: Optional[ManagedClusterPodIdentityProvisioningInfo]
        provisioning_state: Optional[Union[str, ManagedClusterPodIdentityProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                binding_selector: Optional[str] = ..., 
                identity: UserAssignedIdentity, 
                name: str, 
                namespace: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterPodIdentityException(_Model):
        name: str
        namespace: str
        pod_labels: dict[str, str]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                namespace: str, 
                pod_labels: dict[str, str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterPodIdentityProfile(_Model):
        allow_network_plugin_kubenet: Optional[bool]
        enabled: Optional[bool]
        user_assigned_identities: Optional[list[ManagedClusterPodIdentity]]
        user_assigned_identity_exceptions: Optional[list[ManagedClusterPodIdentityException]]

        @overload
        def __init__(
                self, 
                *, 
                allow_network_plugin_kubenet: Optional[bool] = ..., 
                enabled: Optional[bool] = ..., 
                user_assigned_identities: Optional[list[ManagedClusterPodIdentity]] = ..., 
                user_assigned_identity_exceptions: Optional[list[ManagedClusterPodIdentityException]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterPodIdentityProvisioningError(_Model):
        error: Optional[ManagedClusterPodIdentityProvisioningErrorBody]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ManagedClusterPodIdentityProvisioningErrorBody] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterPodIdentityProvisioningErrorBody(_Model):
        code: Optional[str]
        details: Optional[list[ManagedClusterPodIdentityProvisioningErrorBody]]
        message: Optional[str]
        target: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                details: Optional[list[ManagedClusterPodIdentityProvisioningErrorBody]] = ..., 
                message: Optional[str] = ..., 
                target: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterPodIdentityProvisioningInfo(_Model):
        error: Optional[ManagedClusterPodIdentityProvisioningError]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ManagedClusterPodIdentityProvisioningError] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterPodIdentityProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASSIGNED = "Assigned"
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.containerservice.models.ManagedClusterPoolUpgradeProfile(_Model):
        components_by_releases: Optional[list[ComponentsByRelease]]
        kubernetes_version: str
        name: Optional[str]
        os_type: Union[str, OSType]
        upgrades: Optional[list[ManagedClusterPoolUpgradeProfileUpgradesItem]]

        @overload
        def __init__(
                self, 
                *, 
                components_by_releases: Optional[list[ComponentsByRelease]] = ..., 
                kubernetes_version: str, 
                name: Optional[str] = ..., 
                os_type: Union[str, OSType], 
                upgrades: Optional[list[ManagedClusterPoolUpgradeProfileUpgradesItem]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterPoolUpgradeProfileUpgradesItem(_Model):
        is_out_of_support: Optional[bool]
        is_preview: Optional[bool]
        kubernetes_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                is_out_of_support: Optional[bool] = ..., 
                is_preview: Optional[bool] = ..., 
                kubernetes_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterProperties(_Model):
        aad_profile: Optional[ManagedClusterAADProfile]
        addon_profiles: Optional[dict[str, ManagedClusterAddonProfile]]
        agent_pool_profiles: Optional[list[ManagedClusterAgentPoolProfile]]
        ai_toolchain_operator_profile: Optional[ManagedClusterAIToolchainOperatorProfile]
        api_server_access_profile: Optional[ManagedClusterAPIServerAccessProfile]
        auto_scaler_profile: Optional[ManagedClusterPropertiesAutoScalerProfile]
        auto_upgrade_profile: Optional[ManagedClusterAutoUpgradeProfile]
        azure_monitor_profile: Optional[ManagedClusterAzureMonitorProfile]
        azure_portal_fqdn: Optional[str]
        bootstrap_profile: Optional[ManagedClusterBootstrapProfile]
        control_plane_scaling_profile: Optional[ManagedClusterControlPlaneScalingProfile]
        creation_data: Optional[CreationData]
        current_kubernetes_version: Optional[str]
        disable_local_accounts: Optional[bool]
        disk_encryption_set_id: Optional[str]
        dns_prefix: Optional[str]
        enable_fips: Optional[bool]
        enable_namespace_resources: Optional[bool]
        enable_rbac: Optional[bool]
        fqdn: Optional[str]
        fqdn_subdomain: Optional[str]
        health_monitor_profile: Optional[ManagedClusterHealthMonitorProfile]
        hosted_system_profile: Optional[ManagedClusterHostedSystemProfile]
        http_proxy_config: Optional[ManagedClusterHTTPProxyConfig]
        identity_profile: Optional[dict[str, UserAssignedIdentity]]
        ingress_profile: Optional[ManagedClusterIngressProfile]
        kubernetes_version: Optional[str]
        linux_profile: Optional[ContainerServiceLinuxProfile]
        max_agent_pools: Optional[int]
        metrics_profile: Optional[ManagedClusterMetricsProfile]
        network_profile: Optional[ContainerServiceNetworkProfile]
        node_disruption_profile: Optional[NodeDisruptionProfile]
        node_provisioning_profile: Optional[ManagedClusterNodeProvisioningProfile]
        node_resource_group: Optional[str]
        node_resource_group_profile: Optional[ManagedClusterNodeResourceGroupProfile]
        oidc_issuer_profile: Optional[ManagedClusterOIDCIssuerProfile]
        pod_identity_profile: Optional[ManagedClusterPodIdentityProfile]
        power_state: Optional[PowerState]
        private_fqdn: Optional[str]
        private_link_resources: Optional[list[PrivateLinkResource]]
        provisioning_state: Optional[str]
        public_network_access: Optional[Union[str, PublicNetworkAccess]]
        resource_uid: Optional[str]
        scheduler_profile: Optional[SchedulerProfile]
        security_profile: Optional[ManagedClusterSecurityProfile]
        service_mesh_profile: Optional[ServiceMeshProfile]
        service_principal_profile: Optional[ManagedClusterServicePrincipalProfile]
        status: Optional[ManagedClusterStatus]
        storage_profile: Optional[ManagedClusterStorageProfile]
        support_plan: Optional[Union[str, KubernetesSupportPlan]]
        upgrade_settings: Optional[ClusterUpgradeSettings]
        windows_profile: Optional[ManagedClusterWindowsProfile]
        workload_auto_scaler_profile: Optional[ManagedClusterWorkloadAutoScalerProfile]

        @overload
        def __init__(
                self, 
                *, 
                aad_profile: Optional[ManagedClusterAADProfile] = ..., 
                addon_profiles: Optional[dict[str, ManagedClusterAddonProfile]] = ..., 
                agent_pool_profiles: Optional[list[ManagedClusterAgentPoolProfile]] = ..., 
                ai_toolchain_operator_profile: Optional[ManagedClusterAIToolchainOperatorProfile] = ..., 
                api_server_access_profile: Optional[ManagedClusterAPIServerAccessProfile] = ..., 
                auto_scaler_profile: Optional[ManagedClusterPropertiesAutoScalerProfile] = ..., 
                auto_upgrade_profile: Optional[ManagedClusterAutoUpgradeProfile] = ..., 
                azure_monitor_profile: Optional[ManagedClusterAzureMonitorProfile] = ..., 
                bootstrap_profile: Optional[ManagedClusterBootstrapProfile] = ..., 
                control_plane_scaling_profile: Optional[ManagedClusterControlPlaneScalingProfile] = ..., 
                creation_data: Optional[CreationData] = ..., 
                disable_local_accounts: Optional[bool] = ..., 
                disk_encryption_set_id: Optional[str] = ..., 
                dns_prefix: Optional[str] = ..., 
                enable_fips: Optional[bool] = ..., 
                enable_namespace_resources: Optional[bool] = ..., 
                enable_rbac: Optional[bool] = ..., 
                fqdn_subdomain: Optional[str] = ..., 
                health_monitor_profile: Optional[ManagedClusterHealthMonitorProfile] = ..., 
                hosted_system_profile: Optional[ManagedClusterHostedSystemProfile] = ..., 
                http_proxy_config: Optional[ManagedClusterHTTPProxyConfig] = ..., 
                identity_profile: Optional[dict[str, UserAssignedIdentity]] = ..., 
                ingress_profile: Optional[ManagedClusterIngressProfile] = ..., 
                kubernetes_version: Optional[str] = ..., 
                linux_profile: Optional[ContainerServiceLinuxProfile] = ..., 
                metrics_profile: Optional[ManagedClusterMetricsProfile] = ..., 
                network_profile: Optional[ContainerServiceNetworkProfile] = ..., 
                node_disruption_profile: Optional[NodeDisruptionProfile] = ..., 
                node_provisioning_profile: Optional[ManagedClusterNodeProvisioningProfile] = ..., 
                node_resource_group: Optional[str] = ..., 
                node_resource_group_profile: Optional[ManagedClusterNodeResourceGroupProfile] = ..., 
                oidc_issuer_profile: Optional[ManagedClusterOIDCIssuerProfile] = ..., 
                pod_identity_profile: Optional[ManagedClusterPodIdentityProfile] = ..., 
                private_link_resources: Optional[list[PrivateLinkResource]] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                scheduler_profile: Optional[SchedulerProfile] = ..., 
                security_profile: Optional[ManagedClusterSecurityProfile] = ..., 
                service_mesh_profile: Optional[ServiceMeshProfile] = ..., 
                service_principal_profile: Optional[ManagedClusterServicePrincipalProfile] = ..., 
                status: Optional[ManagedClusterStatus] = ..., 
                storage_profile: Optional[ManagedClusterStorageProfile] = ..., 
                support_plan: Optional[Union[str, KubernetesSupportPlan]] = ..., 
                upgrade_settings: Optional[ClusterUpgradeSettings] = ..., 
                windows_profile: Optional[ManagedClusterWindowsProfile] = ..., 
                workload_auto_scaler_profile: Optional[ManagedClusterWorkloadAutoScalerProfile] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterPropertiesAutoScalerProfile(_Model):
        balance_similar_node_groups: Optional[str]
        daemonset_eviction_for_empty_nodes: Optional[bool]
        daemonset_eviction_for_occupied_nodes: Optional[bool]
        expander: Optional[Union[str, Expander]]
        ignore_daemonsets_utilization: Optional[bool]
        max_empty_bulk_delete: Optional[str]
        max_graceful_termination_sec: Optional[str]
        max_node_provision_time: Optional[str]
        max_total_unready_percentage: Optional[str]
        new_pod_scale_up_delay: Optional[str]
        ok_total_unready_count: Optional[str]
        scale_down_delay_after_add: Optional[str]
        scale_down_delay_after_delete: Optional[str]
        scale_down_delay_after_failure: Optional[str]
        scale_down_unneeded_time: Optional[str]
        scale_down_unready_time: Optional[str]
        scale_down_utilization_threshold: Optional[str]
        scan_interval: Optional[str]
        skip_nodes_with_local_storage: Optional[str]
        skip_nodes_with_system_pods: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                balance_similar_node_groups: Optional[str] = ..., 
                daemonset_eviction_for_empty_nodes: Optional[bool] = ..., 
                daemonset_eviction_for_occupied_nodes: Optional[bool] = ..., 
                expander: Optional[Union[str, Expander]] = ..., 
                ignore_daemonsets_utilization: Optional[bool] = ..., 
                max_empty_bulk_delete: Optional[str] = ..., 
                max_graceful_termination_sec: Optional[str] = ..., 
                max_node_provision_time: Optional[str] = ..., 
                max_total_unready_percentage: Optional[str] = ..., 
                new_pod_scale_up_delay: Optional[str] = ..., 
                ok_total_unready_count: Optional[str] = ..., 
                scale_down_delay_after_add: Optional[str] = ..., 
                scale_down_delay_after_delete: Optional[str] = ..., 
                scale_down_delay_after_failure: Optional[str] = ..., 
                scale_down_unneeded_time: Optional[str] = ..., 
                scale_down_unready_time: Optional[str] = ..., 
                scale_down_utilization_threshold: Optional[str] = ..., 
                scan_interval: Optional[str] = ..., 
                skip_nodes_with_local_storage: Optional[str] = ..., 
                skip_nodes_with_system_pods: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterPropertiesForSnapshot(_Model):
        enable_rbac: Optional[bool]
        kubernetes_version: Optional[str]
        network_profile: Optional[NetworkProfileForSnapshot]
        sku: Optional[ManagedClusterSKU]


    class azure.mgmt.containerservice.models.ManagedClusterSKU(_Model):
        name: Optional[Union[str, ManagedClusterSKUName]]
        tier: Optional[Union[str, ManagedClusterSKUTier]]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[Union[str, ManagedClusterSKUName]] = ..., 
                tier: Optional[Union[str, ManagedClusterSKUTier]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterSKUName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC = "Automatic"
        BASE = "Base"


    class azure.mgmt.containerservice.models.ManagedClusterSKUTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FREE = "Free"
        PREMIUM = "Premium"
        STANDARD = "Standard"


    class azure.mgmt.containerservice.models.ManagedClusterSecurityProfile(_Model):
        azure_key_vault_kms: Optional[AzureKeyVaultKms]
        custom_ca_trust_certificates: Optional[list[bytes]]
        defender: Optional[ManagedClusterSecurityProfileDefender]
        image_cleaner: Optional[ManagedClusterSecurityProfileImageCleaner]
        image_integrity: Optional[ManagedClusterSecurityProfileImageIntegrity]
        kubernetes_resource_object_encryption_profile: Optional[KubernetesResourceObjectEncryptionProfile]
        node_restriction: Optional[ManagedClusterSecurityProfileNodeRestriction]
        service_account_image_pull_profile: Optional[ServiceAccountImagePullProfile]
        workload_identity: Optional[ManagedClusterSecurityProfileWorkloadIdentity]

        @overload
        def __init__(
                self, 
                *, 
                azure_key_vault_kms: Optional[AzureKeyVaultKms] = ..., 
                custom_ca_trust_certificates: Optional[list[bytes]] = ..., 
                defender: Optional[ManagedClusterSecurityProfileDefender] = ..., 
                image_cleaner: Optional[ManagedClusterSecurityProfileImageCleaner] = ..., 
                image_integrity: Optional[ManagedClusterSecurityProfileImageIntegrity] = ..., 
                kubernetes_resource_object_encryption_profile: Optional[KubernetesResourceObjectEncryptionProfile] = ..., 
                node_restriction: Optional[ManagedClusterSecurityProfileNodeRestriction] = ..., 
                service_account_image_pull_profile: Optional[ServiceAccountImagePullProfile] = ..., 
                workload_identity: Optional[ManagedClusterSecurityProfileWorkloadIdentity] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterSecurityProfileDefender(_Model):
        log_analytics_workspace_resource_id: Optional[str]
        security_gating: Optional[ManagedClusterSecurityProfileDefenderSecurityGating]
        security_monitoring: Optional[ManagedClusterSecurityProfileDefenderSecurityMonitoring]

        @overload
        def __init__(
                self, 
                *, 
                log_analytics_workspace_resource_id: Optional[str] = ..., 
                security_gating: Optional[ManagedClusterSecurityProfileDefenderSecurityGating] = ..., 
                security_monitoring: Optional[ManagedClusterSecurityProfileDefenderSecurityMonitoring] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterSecurityProfileDefenderSecurityGating(_Model):
        allow_secret_access: Optional[bool]
        enabled: Optional[bool]
        identities: Optional[list[ManagedClusterSecurityProfileDefenderSecurityGatingIdentity]]

        @overload
        def __init__(
                self, 
                *, 
                allow_secret_access: Optional[bool] = ..., 
                enabled: Optional[bool] = ..., 
                identities: Optional[list[ManagedClusterSecurityProfileDefenderSecurityGatingIdentity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterSecurityProfileDefenderSecurityGatingIdentity(_Model):
        azure_container_registry: Optional[str]
        identity: Optional[UserAssignedIdentity]

        @overload
        def __init__(
                self, 
                *, 
                azure_container_registry: Optional[str] = ..., 
                identity: Optional[UserAssignedIdentity] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterSecurityProfileDefenderSecurityMonitoring(_Model):
        enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterSecurityProfileImageCleaner(_Model):
        enabled: Optional[bool]
        interval_hours: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                interval_hours: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterSecurityProfileImageIntegrity(_Model):
        enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterSecurityProfileNodeRestriction(_Model):
        enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterSecurityProfileWorkloadIdentity(_Model):
        enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterServicePrincipalProfile(_Model):
        client_id: str
        secret: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                client_id: str, 
                secret: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterSnapshot(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[ManagedClusterSnapshotProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[ManagedClusterSnapshotProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterSnapshotProperties(_Model):
        creation_data: Optional[CreationData]
        managed_cluster_properties_read_only: Optional[ManagedClusterPropertiesForSnapshot]
        snapshot_type: Optional[Union[str, SnapshotType]]

        @overload
        def __init__(
                self, 
                *, 
                creation_data: Optional[CreationData] = ..., 
                snapshot_type: Optional[Union[str, SnapshotType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterStaticEgressGatewayProfile(_Model):
        enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterStatus(_Model):
        provisioning_error: Optional[ErrorDetail]


    class azure.mgmt.containerservice.models.ManagedClusterStorageProfile(_Model):
        blob_csi_driver: Optional[ManagedClusterStorageProfileBlobCSIDriver]
        disk_csi_driver: Optional[ManagedClusterStorageProfileDiskCSIDriver]
        file_csi_driver: Optional[ManagedClusterStorageProfileFileCSIDriver]
        snapshot_controller: Optional[ManagedClusterStorageProfileSnapshotController]

        @overload
        def __init__(
                self, 
                *, 
                blob_csi_driver: Optional[ManagedClusterStorageProfileBlobCSIDriver] = ..., 
                disk_csi_driver: Optional[ManagedClusterStorageProfileDiskCSIDriver] = ..., 
                file_csi_driver: Optional[ManagedClusterStorageProfileFileCSIDriver] = ..., 
                snapshot_controller: Optional[ManagedClusterStorageProfileSnapshotController] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterStorageProfileBlobCSIDriver(_Model):
        enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterStorageProfileDiskCSIDriver(_Model):
        enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterStorageProfileFileCSIDriver(_Model):
        enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterStorageProfileSnapshotController(_Model):
        enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterUpgradeProfile(ProxyResource):
        id: str
        name: str
        properties: ManagedClusterUpgradeProfileProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: ManagedClusterUpgradeProfileProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterUpgradeProfileProperties(_Model):
        agent_pool_profiles: list[ManagedClusterPoolUpgradeProfile]
        control_plane_profile: ManagedClusterPoolUpgradeProfile

        @overload
        def __init__(
                self, 
                *, 
                agent_pool_profiles: list[ManagedClusterPoolUpgradeProfile], 
                control_plane_profile: ManagedClusterPoolUpgradeProfile
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterWebAppRoutingGatewayAPIImplementations(_Model):
        app_routing_istio: Optional[ManagedClusterAppRoutingIstio]

        @overload
        def __init__(
                self, 
                *, 
                app_routing_istio: Optional[ManagedClusterAppRoutingIstio] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterWindowsProfile(_Model):
        admin_password: Optional[str]
        admin_username: str
        enable_csi_proxy: Optional[bool]
        gmsa_profile: Optional[WindowsGmsaProfile]
        license_type: Optional[Union[str, LicenseType]]

        @overload
        def __init__(
                self, 
                *, 
                admin_password: Optional[str] = ..., 
                admin_username: str, 
                enable_csi_proxy: Optional[bool] = ..., 
                gmsa_profile: Optional[WindowsGmsaProfile] = ..., 
                license_type: Optional[Union[str, LicenseType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterWorkloadAutoScalerProfile(_Model):
        keda: Optional[ManagedClusterWorkloadAutoScalerProfileKeda]
        vertical_pod_autoscaler: Optional[ManagedClusterWorkloadAutoScalerProfileVerticalPodAutoscaler]

        @overload
        def __init__(
                self, 
                *, 
                keda: Optional[ManagedClusterWorkloadAutoScalerProfileKeda] = ..., 
                vertical_pod_autoscaler: Optional[ManagedClusterWorkloadAutoScalerProfileVerticalPodAutoscaler] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterWorkloadAutoScalerProfileKeda(_Model):
        enabled: bool

        @overload
        def __init__(
                self, 
                *, 
                enabled: bool
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedClusterWorkloadAutoScalerProfileVerticalPodAutoscaler(_Model):
        addon_autoscaling: Optional[Union[str, AddonAutoscaling]]
        enabled: bool

        @overload
        def __init__(
                self, 
                *, 
                addon_autoscaling: Optional[Union[str, AddonAutoscaling]] = ..., 
                enabled: bool
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedGatewayType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        STANDARD = "Standard"


    class azure.mgmt.containerservice.models.ManagedNamespace(TrackedResource):
        e_tag: Optional[str]
        id: str
        location: str
        name: str
        properties: Optional[NamespaceProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[NamespaceProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ManagedServiceIdentityUserAssignedIdentitiesValue(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.containerservice.models.ManagementMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MANAGED = "Managed"
        UNMANAGED = "Unmanaged"


    class azure.mgmt.containerservice.models.ManualScaleProfile(_Model):
        count: Optional[int]
        size: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                count: Optional[int] = ..., 
                size: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.MeshMembership(ProxyResource):
        e_tag: Optional[str]
        id: str
        managed_by: Optional[str]
        name: str
        properties: Optional[MeshMembershipProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                managed_by: Optional[str] = ..., 
                properties: Optional[MeshMembershipProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.MeshMembershipPrivateConnectProfile(_Model):
        private_ip_address: Optional[str]
        subnet_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                subnet_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.MeshMembershipProperties(_Model):
        managed_mesh_id: str
        private_connect_profile: Optional[MeshMembershipPrivateConnectProfile]
        provisioning_state: Optional[Union[str, MeshMembershipProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                managed_mesh_id: str, 
                private_connect_profile: Optional[MeshMembershipPrivateConnectProfile] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.MeshMembershipProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.containerservice.models.MeshRevision(_Model):
        compatible_with: Optional[list[CompatibleVersions]]
        revision: Optional[str]
        upgrades: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                compatible_with: Optional[list[CompatibleVersions]] = ..., 
                revision: Optional[str] = ..., 
                upgrades: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.MeshRevisionProfile(ProxyResource):
        id: str
        name: str
        properties: Optional[MeshRevisionProfileProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[MeshRevisionProfileProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.MeshRevisionProfileProperties(_Model):
        mesh_revisions: Optional[list[MeshRevision]]

        @overload
        def __init__(
                self, 
                *, 
                mesh_revisions: Optional[list[MeshRevision]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.MeshUpgradeProfile(ProxyResource):
        id: str
        name: str
        properties: Optional[MeshUpgradeProfileProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[MeshUpgradeProfileProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.MeshUpgradeProfileProperties(MeshRevision):
        compatible_with: list[CompatibleVersions]
        revision: str
        upgrades: list[str]

        @overload
        def __init__(
                self, 
                *, 
                compatible_with: Optional[list[CompatibleVersions]] = ..., 
                revision: Optional[str] = ..., 
                upgrades: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.MigStrategy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MIXED = "Mixed"
        NONE = "None"
        SINGLE = "Single"


    class azure.mgmt.containerservice.models.Mode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IPTABLES = "IPTABLES"
        IPVS = "IPVS"
        NFTABLES = "NFTABLES"


    class azure.mgmt.containerservice.models.NamespaceProperties(_Model):
        adoption_policy: Optional[Union[str, AdoptionPolicy]]
        annotations: Optional[dict[str, str]]
        default_network_policy: Optional[NetworkPolicies]
        default_resource_quota: Optional[ResourceQuota]
        delete_policy: Optional[Union[str, DeletePolicy]]
        labels: Optional[dict[str, str]]
        portal_fqdn: Optional[str]
        provisioning_state: Optional[Union[str, NamespaceProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                adoption_policy: Optional[Union[str, AdoptionPolicy]] = ..., 
                annotations: Optional[dict[str, str]] = ..., 
                default_network_policy: Optional[NetworkPolicies] = ..., 
                default_resource_quota: Optional[ResourceQuota] = ..., 
                delete_policy: Optional[Union[str, DeletePolicy]] = ..., 
                labels: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.NamespaceProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.containerservice.models.NetworkDataplane(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE = "azure"
        CILIUM = "cilium"


    class azure.mgmt.containerservice.models.NetworkMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BRIDGE = "bridge"
        TRANSPARENT = "transparent"


    class azure.mgmt.containerservice.models.NetworkPlugin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE = "azure"
        KUBENET = "kubenet"
        NONE = "none"


    class azure.mgmt.containerservice.models.NetworkPluginMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OVERLAY = "overlay"


    class azure.mgmt.containerservice.models.NetworkPolicies(_Model):
        egress: Optional[Union[str, PolicyRule]]
        ingress: Optional[Union[str, PolicyRule]]

        @overload
        def __init__(
                self, 
                *, 
                egress: Optional[Union[str, PolicyRule]] = ..., 
                ingress: Optional[Union[str, PolicyRule]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.NetworkPolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE = "azure"
        CALICO = "calico"
        CILIUM = "cilium"
        NONE = "none"


    class azure.mgmt.containerservice.models.NetworkProfileForSnapshot(_Model):
        load_balancer_sku: Optional[Union[str, LoadBalancerSku]]
        network_mode: Optional[Union[str, NetworkMode]]
        network_plugin: Optional[Union[str, NetworkPlugin]]
        network_plugin_mode: Optional[Union[str, NetworkPluginMode]]
        network_policy: Optional[Union[str, NetworkPolicy]]

        @overload
        def __init__(
                self, 
                *, 
                load_balancer_sku: Optional[Union[str, LoadBalancerSku]] = ..., 
                network_mode: Optional[Union[str, NetworkMode]] = ..., 
                network_plugin: Optional[Union[str, NetworkPlugin]] = ..., 
                network_plugin_mode: Optional[Union[str, NetworkPluginMode]] = ..., 
                network_policy: Optional[Union[str, NetworkPolicy]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.NginxIngressControllerType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANNOTATION_CONTROLLED = "AnnotationControlled"
        EXTERNAL = "External"
        INTERNAL = "Internal"
        NONE = "None"


    class azure.mgmt.containerservice.models.NodeDisruptionPolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW = "Allow"
        ALLOW_DURING_MAINTENANCE_WINDOW = "AllowDuringMaintenanceWindow"
        BLOCK = "Block"


    class azure.mgmt.containerservice.models.NodeDisruptionProfile(_Model):
        node_disruption_policy: Optional[Union[str, NodeDisruptionPolicy]]

        @overload
        def __init__(
                self, 
                *, 
                node_disruption_policy: Optional[Union[str, NodeDisruptionPolicy]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.NodeImageVersion(_Model):
        full_name: Optional[str]
        os: Optional[str]
        sku: Optional[str]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                full_name: Optional[str] = ..., 
                os: Optional[str] = ..., 
                sku: Optional[str] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.NodeOSUpgradeChannel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NODE_IMAGE = "NodeImage"
        NONE = "None"
        SECURITY_PATCH = "SecurityPatch"
        UNMANAGED = "Unmanaged"


    class azure.mgmt.containerservice.models.NodeProvisioningDefaultNodePools(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO = "Auto"
        NONE = "None"


    class azure.mgmt.containerservice.models.NodeProvisioningMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO = "Auto"
        MANUAL = "Manual"


    class azure.mgmt.containerservice.models.NvidiaGPUProfile(_Model):
        management_mode: Optional[Union[str, ManagementMode]]
        mig_strategy: Optional[Union[str, MigStrategy]]

        @overload
        def __init__(
                self, 
                *, 
                management_mode: Optional[Union[str, ManagementMode]] = ..., 
                mig_strategy: Optional[Union[str, MigStrategy]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.OSDiskType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EPHEMERAL = "Ephemeral"
        MANAGED = "Managed"


    class azure.mgmt.containerservice.models.OSSKU(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_CONTAINER_LINUX = "AzureContainerLinux"
        AZURE_LINUX = "AzureLinux"
        AZURE_LINUX3 = "AzureLinux3"
        CBL_MARINER = "CBLMariner"
        FLATCAR = "Flatcar"
        MARINER = "Mariner"
        UBUNTU = "Ubuntu"
        UBUNTU2204 = "Ubuntu2204"
        UBUNTU2404 = "Ubuntu2404"
        WINDOWS2019 = "Windows2019"
        WINDOWS2022 = "Windows2022"
        WINDOWS2025 = "Windows2025"
        WINDOWS_ANNUAL = "WindowsAnnual"


    class azure.mgmt.containerservice.models.OSType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LINUX = "Linux"
        WINDOWS = "Windows"


    class azure.mgmt.containerservice.models.OperationStatusResult(_Model):
        end_time: Optional[datetime]
        error: Optional[ErrorDetail]
        id: Optional[str]
        name: Optional[str]
        operations: Optional[list[OperationStatusResult]]
        percent_complete: Optional[float]
        resource_id: Optional[str]
        start_time: Optional[datetime]
        status: str

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                error: Optional[ErrorDetail] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                operations: Optional[list[OperationStatusResult]] = ..., 
                percent_complete: Optional[float] = ..., 
                start_time: Optional[datetime] = ..., 
                status: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.OperationValue(_Model):
        display: Optional[OperationValueDisplay]
        name: Optional[str]
        origin: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[OperationValueDisplay] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.containerservice.models.OperationValueDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.containerservice.models.Operator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DOES_NOT_EXIST = "DoesNotExist"
        EXISTS = "Exists"
        IN = "In"
        NOT_IN = "NotIn"


    class azure.mgmt.containerservice.models.OutboundEnvironmentEndpoint(_Model):
        category: Optional[str]
        endpoints: Optional[list[EndpointDependency]]

        @overload
        def __init__(
                self, 
                *, 
                category: Optional[str] = ..., 
                endpoints: Optional[list[EndpointDependency]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.OutboundType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOAD_BALANCER = "loadBalancer"
        MANAGED_NAT_GATEWAY = "managedNATGateway"
        MANAGED_NAT_GATEWAY_V2 = "managedNATGatewayV2"
        NONE = "none"
        USER_ASSIGNED_NAT_GATEWAY = "userAssignedNATGateway"
        USER_DEFINED_ROUTING = "userDefinedRouting"


    class azure.mgmt.containerservice.models.PodIPAllocationMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DYNAMIC_INDIVIDUAL = "DynamicIndividual"
        STATIC_BLOCK = "StaticBlock"


    class azure.mgmt.containerservice.models.PodLinkLocalAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IMDS = "IMDS"
        NONE = "None"


    class azure.mgmt.containerservice.models.PolicyRule(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW_ALL = "AllowAll"
        ALLOW_SAME_NAMESPACE = "AllowSameNamespace"
        DENY_ALL = "DenyAll"


    class azure.mgmt.containerservice.models.PoolBootstrapData(_Model):
        azure: Optional[BootstrapAzureConfig]
        components: Optional[BootstrapComponentVersions]
        networking: Optional[BootstrapNetworkingConfig]
        node: Optional[BootstrapNodeConfig]


    class azure.mgmt.containerservice.models.PortRange(_Model):
        port_end: Optional[int]
        port_start: Optional[int]
        protocol: Optional[Union[str, Protocol]]

        @overload
        def __init__(
                self, 
                *, 
                port_end: Optional[int] = ..., 
                port_start: Optional[int] = ..., 
                protocol: Optional[Union[str, Protocol]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.PowerState(_Model):
        code: Optional[Union[str, Code]]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[Union[str, Code]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.PreparedImageSpecificationProfile(_Model):
        prepared_image_specification_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                prepared_image_specification_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.PrivateEndpoint(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.PrivateEndpointConnection(ProxyResource):
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


    class azure.mgmt.containerservice.models.PrivateEndpointConnectionListResult(_Model):
        value: Optional[list[PrivateEndpointConnection]]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[list[PrivateEndpointConnection]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.PrivateEndpointConnectionProperties(_Model):
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


    class azure.mgmt.containerservice.models.PrivateEndpointConnectionProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.containerservice.models.PrivateLinkResource(_Model):
        group_id: Optional[str]
        id: Optional[str]
        name: Optional[str]
        private_link_service_id: Optional[str]
        required_members: Optional[list[str]]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                group_id: Optional[str] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                required_members: Optional[list[str]] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.PrivateLinkResourcesListResult(_Model):
        value: Optional[list[PrivateLinkResource]]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[list[PrivateLinkResource]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.PrivateLinkServiceConnectionState(_Model):
        description: Optional[str]
        status: Optional[Union[str, ConnectionStatus]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                status: Optional[Union[str, ConnectionStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.Protocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        TCP = "TCP"
        UDP = "UDP"


    class azure.mgmt.containerservice.models.ProxyRedirectionMechanism(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CNI_CHAINING = "CNIChaining"
        INIT_CONTAINERS = "InitContainers"


    class azure.mgmt.containerservice.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.containerservice.models.PublicNetworkAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        SECURED_BY_PERIMETER = "SecuredByPerimeter"


    class azure.mgmt.containerservice.models.RebalanceLoadBalancersRequestBody(_Model):
        load_balancer_names: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                load_balancer_names: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.RelativeMonthlySchedule(_Model):
        day_of_week: Union[str, WeekDay]
        interval_months: int
        week_index: Union[str, Type]

        @overload
        def __init__(
                self, 
                *, 
                day_of_week: Union[str, WeekDay], 
                interval_months: int, 
                week_index: Union[str, Type]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.containerservice.models.ResourceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.containerservice.models.ResourceProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.containerservice.models.ResourceQuota(_Model):
        cpu_limit: Optional[str]
        cpu_request: Optional[str]
        memory_limit: Optional[str]
        memory_request: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                cpu_limit: Optional[str] = ..., 
                cpu_request: Optional[str] = ..., 
                memory_limit: Optional[str] = ..., 
                memory_request: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ResourceReference(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ResourceSku(_Model):
        api_versions: Optional[list[str]]
        capabilities: Optional[list[ResourceSkuCapabilities]]
        capacity: Optional[ResourceSkuCapacity]
        costs: Optional[list[ResourceSkuCosts]]
        family: Optional[str]
        kind: Optional[str]
        location_info: Optional[list[ResourceSkuLocationInfo]]
        locations: Optional[list[str]]
        name: Optional[str]
        resource_type: Optional[str]
        restrictions: Optional[list[ResourceSkuRestrictions]]
        size: Optional[str]
        tier: Optional[str]


    class azure.mgmt.containerservice.models.ResourceSkuCapabilities(_Model):
        name: Optional[str]
        value: Optional[str]


    class azure.mgmt.containerservice.models.ResourceSkuCapacity(_Model):
        default: Optional[int]
        maximum: Optional[int]
        minimum: Optional[int]
        scale_type: Optional[Union[str, ResourceSkuCapacityScaleType]]


    class azure.mgmt.containerservice.models.ResourceSkuCapacityScaleType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC = "Automatic"
        MANUAL = "Manual"
        NONE = "None"


    class azure.mgmt.containerservice.models.ResourceSkuCosts(_Model):
        extended_unit: Optional[str]
        meter_id: Optional[str]
        quantity: Optional[int]


    class azure.mgmt.containerservice.models.ResourceSkuLocationInfo(_Model):
        extended_locations: Optional[list[str]]
        location: Optional[str]
        type: Optional[Union[str, ExtendedLocationTypes]]
        zone_details: Optional[list[ResourceSkuZoneDetails]]
        zones: Optional[list[str]]


    class azure.mgmt.containerservice.models.ResourceSkuRestrictionInfo(_Model):
        locations: Optional[list[str]]
        zones: Optional[list[str]]


    class azure.mgmt.containerservice.models.ResourceSkuRestrictions(_Model):
        reason_code: Optional[Union[str, ResourceSkuRestrictionsReasonCode]]
        restriction_info: Optional[ResourceSkuRestrictionInfo]
        type: Optional[Union[str, ResourceSkuRestrictionsType]]
        values_property: Optional[list[str]]


    class azure.mgmt.containerservice.models.ResourceSkuRestrictionsReasonCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_AVAILABLE_FOR_SUBSCRIPTION = "NotAvailableForSubscription"
        QUOTA_ID = "QuotaId"


    class azure.mgmt.containerservice.models.ResourceSkuRestrictionsType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOCATION = "Location"
        ZONE = "Zone"


    class azure.mgmt.containerservice.models.ResourceSkuZoneDetails(_Model):
        capabilities: Optional[list[ResourceSkuCapabilities]]
        name: Optional[list[str]]


    class azure.mgmt.containerservice.models.RestrictionLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        READ_ONLY = "ReadOnly"
        UNRESTRICTED = "Unrestricted"


    class azure.mgmt.containerservice.models.RunCommandRequest(_Model):
        cluster_token: Optional[str]
        command: str
        context: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                cluster_token: Optional[str] = ..., 
                command: str, 
                context: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.RunCommandResult(_Model):
        id: Optional[str]
        properties: Optional[CommandResultProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CommandResultProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.containerservice.models.SafeguardsAvailableVersion(ProxyResource):
        id: str
        name: str
        properties: SafeguardsAvailableVersionsProperties
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: SafeguardsAvailableVersionsProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.SafeguardsAvailableVersionsProperties(_Model):
        is_default_version: Optional[bool]
        support: Optional[Union[str, SafeguardsSupport]]


    class azure.mgmt.containerservice.models.SafeguardsSupport(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PREVIEW = "Preview"
        STABLE = "Stable"


    class azure.mgmt.containerservice.models.ScaleDownMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEALLOCATE = "Deallocate"
        DELETE = "Delete"


    class azure.mgmt.containerservice.models.ScaleProfile(_Model):
        autoscale: Optional[list[AutoScaleProfile]]
        manual: Optional[list[ManualScaleProfile]]

        @overload
        def __init__(
                self, 
                *, 
                autoscale: Optional[list[AutoScaleProfile]] = ..., 
                manual: Optional[list[ManualScaleProfile]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ScaleSetEvictionPolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEALLOCATE = "Deallocate"
        DELETE = "Delete"


    class azure.mgmt.containerservice.models.ScaleSetPriority(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        REGULAR = "Regular"
        SPOT = "Spot"


    class azure.mgmt.containerservice.models.Schedule(_Model):
        absolute_monthly: Optional[AbsoluteMonthlySchedule]
        daily: Optional[DailySchedule]
        relative_monthly: Optional[RelativeMonthlySchedule]
        weekly: Optional[WeeklySchedule]

        @overload
        def __init__(
                self, 
                *, 
                absolute_monthly: Optional[AbsoluteMonthlySchedule] = ..., 
                daily: Optional[DailySchedule] = ..., 
                relative_monthly: Optional[RelativeMonthlySchedule] = ..., 
                weekly: Optional[WeeklySchedule] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.SchedulerConfigMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "Default"
        MANAGED_BY_CRD = "ManagedByCRD"


    class azure.mgmt.containerservice.models.SchedulerInstanceProfile(_Model):
        scheduler_config_mode: Optional[Union[str, SchedulerConfigMode]]

        @overload
        def __init__(
                self, 
                *, 
                scheduler_config_mode: Optional[Union[str, SchedulerConfigMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.SchedulerProfile(_Model):
        upstream: Optional[SchedulerInstanceProfile]

        @overload
        def __init__(
                self, 
                *, 
                upstream: Optional[SchedulerInstanceProfile] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.SeccompDefault(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        RUNTIME_DEFAULT = "RuntimeDefault"
        UNCONFINED = "Unconfined"


    class azure.mgmt.containerservice.models.ServiceAccountImagePullProfile(_Model):
        default_managed_identity_id: Optional[str]
        enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                default_managed_identity_id: Optional[str] = ..., 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.ServiceMeshMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ISTIO = "Istio"


    class azure.mgmt.containerservice.models.ServiceMeshProfile(_Model):
        istio: Optional[IstioServiceMesh]
        mode: Union[str, ServiceMeshMode]

        @overload
        def __init__(
                self, 
                *, 
                istio: Optional[IstioServiceMesh] = ..., 
                mode: Union[str, ServiceMeshMode]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.Snapshot(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[SnapshotProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[SnapshotProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.containerservice.models.SnapshotProperties(_Model):
        creation_data: Optional[CreationData]
        enable_fips: Optional[bool]
        kubernetes_version: Optional[str]
        node_image_version: Optional[str]
        os_sku: Optional[Union[str, _models.OSSKU]]
        os_type: Optional[Union[str, OSType]]
        snapshot_type: Optional[Union[str, SnapshotType]]
        vm_size: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                creation_data: Optional[CreationData] = ..., 
                snapshot_type: Optional[Union[str, SnapshotType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.SnapshotType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MANAGED_CLUSTER = "ManagedCluster"
        NODE_POOL = "NodePool"


    class azure.mgmt.containerservice.models.SysctlConfig(_Model):
        fs_aio_max_nr: Optional[int]
        fs_file_max: Optional[int]
        fs_inotify_max_user_watches: Optional[int]
        fs_nr_open: Optional[int]
        kernel_threads_max: Optional[int]
        net_core_netdev_max_backlog: Optional[int]
        net_core_optmem_max: Optional[int]
        net_core_rmem_default: Optional[int]
        net_core_rmem_max: Optional[int]
        net_core_somaxconn: Optional[int]
        net_core_wmem_default: Optional[int]
        net_core_wmem_max: Optional[int]
        net_ipv4_ip_local_port_range: Optional[str]
        net_ipv4_neigh_default_gc_thresh1: Optional[int]
        net_ipv4_neigh_default_gc_thresh2: Optional[int]
        net_ipv4_neigh_default_gc_thresh3: Optional[int]
        net_ipv4_tcp_fin_timeout: Optional[int]
        net_ipv4_tcp_keepalive_probes: Optional[int]
        net_ipv4_tcp_keepalive_time: Optional[int]
        net_ipv4_tcp_max_syn_backlog: Optional[int]
        net_ipv4_tcp_max_tw_buckets: Optional[int]
        net_ipv4_tcp_tw_reuse: Optional[bool]
        net_ipv4_tcpkeepalive_intvl: Optional[int]
        net_netfilter_nf_conntrack_buckets: Optional[int]
        net_netfilter_nf_conntrack_max: Optional[int]
        vm_max_map_count: Optional[int]
        vm_swappiness: Optional[int]
        vm_vfs_cache_pressure: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                fs_aio_max_nr: Optional[int] = ..., 
                fs_file_max: Optional[int] = ..., 
                fs_inotify_max_user_watches: Optional[int] = ..., 
                fs_nr_open: Optional[int] = ..., 
                kernel_threads_max: Optional[int] = ..., 
                net_core_netdev_max_backlog: Optional[int] = ..., 
                net_core_optmem_max: Optional[int] = ..., 
                net_core_rmem_default: Optional[int] = ..., 
                net_core_rmem_max: Optional[int] = ..., 
                net_core_somaxconn: Optional[int] = ..., 
                net_core_wmem_default: Optional[int] = ..., 
                net_core_wmem_max: Optional[int] = ..., 
                net_ipv4_ip_local_port_range: Optional[str] = ..., 
                net_ipv4_neigh_default_gc_thresh1: Optional[int] = ..., 
                net_ipv4_neigh_default_gc_thresh2: Optional[int] = ..., 
                net_ipv4_neigh_default_gc_thresh3: Optional[int] = ..., 
                net_ipv4_tcp_fin_timeout: Optional[int] = ..., 
                net_ipv4_tcp_keepalive_probes: Optional[int] = ..., 
                net_ipv4_tcp_keepalive_time: Optional[int] = ..., 
                net_ipv4_tcp_max_syn_backlog: Optional[int] = ..., 
                net_ipv4_tcp_max_tw_buckets: Optional[int] = ..., 
                net_ipv4_tcp_tw_reuse: Optional[bool] = ..., 
                net_ipv4_tcpkeepalive_intvl: Optional[int] = ..., 
                net_netfilter_nf_conntrack_buckets: Optional[int] = ..., 
                net_netfilter_nf_conntrack_max: Optional[int] = ..., 
                vm_max_map_count: Optional[int] = ..., 
                vm_swappiness: Optional[int] = ..., 
                vm_vfs_cache_pressure: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.SystemData(_Model):
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


    class azure.mgmt.containerservice.models.TagsObject(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.TimeInWeek(_Model):
        day: Optional[Union[str, WeekDay]]
        hour_slots: Optional[list[int]]

        @overload
        def __init__(
                self, 
                *, 
                day: Optional[Union[str, WeekDay]] = ..., 
                hour_slots: Optional[list[int]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.TimeSpan(_Model):
        end: Optional[datetime]
        start: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                end: Optional[datetime] = ..., 
                start: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.TrackedResource(Resource):
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


    class azure.mgmt.containerservice.models.TransitEncryptionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        M_TLS = "mTLS"
        NONE = "None"
        WIRE_GUARD = "WireGuard"


    class azure.mgmt.containerservice.models.TrustedAccessRole(_Model):
        name: Optional[str]
        rules: Optional[list[TrustedAccessRoleRule]]
        source_resource_type: Optional[str]


    class azure.mgmt.containerservice.models.TrustedAccessRoleBinding(ProxyResource):
        id: str
        name: str
        properties: TrustedAccessRoleBindingProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: TrustedAccessRoleBindingProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.containerservice.models.TrustedAccessRoleBindingProperties(_Model):
        provisioning_state: Optional[Union[str, TrustedAccessRoleBindingProvisioningState]]
        roles: list[str]
        source_resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                roles: list[str], 
                source_resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.TrustedAccessRoleBindingProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.containerservice.models.TrustedAccessRoleRule(_Model):
        api_groups: Optional[list[str]]
        non_resource_ur_ls: Optional[list[str]]
        resource_names: Optional[list[str]]
        resources: Optional[list[str]]
        verbs: Optional[list[str]]


    class azure.mgmt.containerservice.models.Type(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FIRST = "First"
        FOURTH = "Fourth"
        LAST = "Last"
        SECOND = "Second"
        THIRD = "Third"


    class azure.mgmt.containerservice.models.UndrainableNodeBehavior(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CORDON = "Cordon"
        SCHEDULE = "Schedule"


    class azure.mgmt.containerservice.models.UpgradeChannel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NODE_IMAGE = "node-image"
        NONE = "none"
        PATCH = "patch"
        RAPID = "rapid"
        STABLE = "stable"


    class azure.mgmt.containerservice.models.UpgradeOverrideSettings(_Model):
        force_upgrade: Optional[bool]
        until: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                force_upgrade: Optional[bool] = ..., 
                until: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.UpgradeStrategy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BLUE_GREEN = "BlueGreen"
        ROLLING = "Rolling"


    class azure.mgmt.containerservice.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        object_id: Optional[str]
        resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                client_id: Optional[str] = ..., 
                object_id: Optional[str] = ..., 
                resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.VirtualMachineNodes(_Model):
        count: Optional[int]
        size: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                count: Optional[int] = ..., 
                size: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.VirtualMachinesProfile(_Model):
        scale: Optional[ScaleProfile]

        @overload
        def __init__(
                self, 
                *, 
                scale: Optional[ScaleProfile] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.VmState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETED = "Deleted"
        RUNNING = "Running"


    class azure.mgmt.containerservice.models.WeekDay(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FRIDAY = "Friday"
        MONDAY = "Monday"
        SATURDAY = "Saturday"
        SUNDAY = "Sunday"
        THURSDAY = "Thursday"
        TUESDAY = "Tuesday"
        WEDNESDAY = "Wednesday"


    class azure.mgmt.containerservice.models.WeeklySchedule(_Model):
        day_of_week: Union[str, WeekDay]
        interval_weeks: int

        @overload
        def __init__(
                self, 
                *, 
                day_of_week: Union[str, WeekDay], 
                interval_weeks: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.WindowsGmsaProfile(_Model):
        dns_server: Optional[str]
        enabled: Optional[bool]
        root_domain_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                dns_server: Optional[str] = ..., 
                enabled: Optional[bool] = ..., 
                root_domain_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservice.models.WorkloadRuntime(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        KATA_MSHV_VM_ISOLATION = "KataMshvVmIsolation"
        KATA_VM_ISOLATION = "KataVmIsolation"
        OCI_CONTAINER = "OCIContainer"
        WASM_WASI = "WasmWasi"


namespace azure.mgmt.containerservice.operations

    class azure.mgmt.containerservice.operations.AgentPoolsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_abort_latest_operation(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                agent_pool_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'resource_name', 'agent_pool_name']}, api_versions_list=['2026-05-02-preview'])
        def begin_complete_upgrade(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                agent_pool_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                agent_pool_name: str, 
                parameters: AgentPool, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[AgentPool]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                agent_pool_name: str, 
                parameters: AgentPool, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[AgentPool]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                agent_pool_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[AgentPool]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                agent_pool_name: str, 
                *, 
                etag: Optional[str] = ..., 
                ignore_pod_disruption_budget: Optional[bool] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_delete_machines(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                agent_pool_name: str, 
                machines: AgentPoolDeleteMachinesParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_delete_machines(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                agent_pool_name: str, 
                machines: AgentPoolDeleteMachinesParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_delete_machines(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                agent_pool_name: str, 
                machines: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_upgrade_node_image_version(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                agent_pool_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                agent_pool_name: str, 
                **kwargs: Any
            ) -> AgentPool: ...

        @distributed_trace
        def get_available_agent_pool_versions(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AgentPoolAvailableVersions: ...

        @distributed_trace
        def get_upgrade_profile(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                agent_pool_name: str, 
                **kwargs: Any
            ) -> AgentPoolUpgradeProfile: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AgentPool]: ...

        @overload
        def list_bootstrap_data(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                agent_pool_name: str, 
                body: ListBootstrapDataRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PoolBootstrapData: ...

        @overload
        def list_bootstrap_data(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                agent_pool_name: str, 
                body: ListBootstrapDataRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PoolBootstrapData: ...

        @overload
        def list_bootstrap_data(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                agent_pool_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PoolBootstrapData: ...


    class azure.mgmt.containerservice.operations.AlertConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                configuration_name: str, 
                resource: AlertConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AlertConfiguration]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                configuration_name: str, 
                resource: AlertConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AlertConfiguration]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                configuration_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AlertConfiguration]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'resource_name', 'configuration_name']}, api_versions_list=['2026-05-02-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                configuration_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'resource_name', 'configuration_name', 'accept']}, api_versions_list=['2026-05-02-preview'])
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                configuration_name: str, 
                **kwargs: Any
            ) -> AlertConfiguration: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'resource_name', 'accept']}, api_versions_list=['2026-05-02-preview'])
        def list_by_managed_cluster(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AlertConfiguration]: ...


    class azure.mgmt.containerservice.operations.ContainerServiceOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_node_image_versions(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[NodeImageVersion]: ...


    class azure.mgmt.containerservice.operations.IdentityBindingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                identity_binding_name: str, 
                parameters: IdentityBinding, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[IdentityBinding]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                identity_binding_name: str, 
                parameters: IdentityBinding, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[IdentityBinding]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                identity_binding_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[IdentityBinding]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01', params_added_on={'2026-04-01': ['api_version', 'subscription_id', 'resource_group_name', 'resource_name', 'identity_binding_name']}, api_versions_list=['2026-04-01', '2026-05-01', '2026-05-02-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                identity_binding_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01', params_added_on={'2026-04-01': ['api_version', 'subscription_id', 'resource_group_name', 'resource_name', 'identity_binding_name', 'accept']}, api_versions_list=['2026-04-01', '2026-05-01', '2026-05-02-preview'])
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                identity_binding_name: str, 
                **kwargs: Any
            ) -> IdentityBinding: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01', params_added_on={'2026-04-01': ['api_version', 'subscription_id', 'resource_group_name', 'resource_name', 'accept']}, api_versions_list=['2026-04-01', '2026-05-01', '2026-05-02-preview'])
        def list_by_managed_cluster(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ItemPaged[IdentityBinding]: ...


    class azure.mgmt.containerservice.operations.JWTAuthenticatorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                jwt_authenticator_name: str, 
                parameters: JWTAuthenticator, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[JWTAuthenticator]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                jwt_authenticator_name: str, 
                parameters: JWTAuthenticator, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[JWTAuthenticator]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                jwt_authenticator_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[JWTAuthenticator]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'resource_name', 'jwt_authenticator_name']}, api_versions_list=['2026-05-02-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                jwt_authenticator_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'resource_name', 'jwt_authenticator_name', 'accept']}, api_versions_list=['2026-05-02-preview'])
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                jwt_authenticator_name: str, 
                **kwargs: Any
            ) -> JWTAuthenticator: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'resource_name', 'accept']}, api_versions_list=['2026-05-02-preview'])
        def list_by_managed_cluster(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ItemPaged[JWTAuthenticator]: ...


    class azure.mgmt.containerservice.operations.LoadBalancersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'resource_name', 'load_balancer_name']}, api_versions_list=['2026-05-02-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                load_balancer_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                load_balancer_name: str, 
                parameters: LoadBalancer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LoadBalancer: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                load_balancer_name: str, 
                parameters: LoadBalancer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LoadBalancer: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                load_balancer_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LoadBalancer: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'resource_name', 'load_balancer_name', 'accept']}, api_versions_list=['2026-05-02-preview'])
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                load_balancer_name: str, 
                **kwargs: Any
            ) -> LoadBalancer: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'resource_name', 'accept']}, api_versions_list=['2026-05-02-preview'])
        def list_by_managed_cluster(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ItemPaged[LoadBalancer]: ...


    class azure.mgmt.containerservice.operations.MachinesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                agent_pool_name: str, 
                machine_name: str, 
                parameters: Machine, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[Machine]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                agent_pool_name: str, 
                machine_name: str, 
                parameters: Machine, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[Machine]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                agent_pool_name: str, 
                machine_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[Machine]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                agent_pool_name: str, 
                machine_name: str, 
                **kwargs: Any
            ) -> Machine: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                agent_pool_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Machine]: ...


    class azure.mgmt.containerservice.operations.MaintenanceConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                config_name: str, 
                parameters: MaintenanceConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MaintenanceConfiguration: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                config_name: str, 
                parameters: MaintenanceConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MaintenanceConfiguration: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                config_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MaintenanceConfiguration: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                config_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                config_name: str, 
                **kwargs: Any
            ) -> MaintenanceConfiguration: ...

        @distributed_trace
        def list_by_managed_cluster(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ItemPaged[MaintenanceConfiguration]: ...


    class azure.mgmt.containerservice.operations.MaintenanceWindowsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                maintenance_window_name: str, 
                resource: MaintenanceWindowResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MaintenanceWindowResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                maintenance_window_name: str, 
                resource: MaintenanceWindowResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MaintenanceWindowResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                maintenance_window_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MaintenanceWindowResource]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'maintenance_window_name']}, api_versions_list=['2026-05-02-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                maintenance_window_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'maintenance_window_name', 'accept']}, api_versions_list=['2026-05-02-preview'])
        def get(
                self, 
                resource_group_name: str, 
                maintenance_window_name: str, 
                **kwargs: Any
            ) -> MaintenanceWindowResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2026-05-02-preview'])
        def list(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[MaintenanceWindowResource]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2026-05-02-preview'])
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[MaintenanceWindowResource]: ...

        @overload
        def update_tags(
                self, 
                resource_group_name: str, 
                maintenance_window_name: str, 
                properties: TagsObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MaintenanceWindowResource: ...

        @overload
        def update_tags(
                self, 
                resource_group_name: str, 
                maintenance_window_name: str, 
                properties: TagsObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MaintenanceWindowResource: ...

        @overload
        def update_tags(
                self, 
                resource_group_name: str, 
                maintenance_window_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MaintenanceWindowResource: ...


    class azure.mgmt.containerservice.operations.ManagedClusterSnapshotsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: ManagedClusterSnapshot, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagedClusterSnapshot: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: ManagedClusterSnapshot, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagedClusterSnapshot: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagedClusterSnapshot: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'resource_name']}, api_versions_list=['2026-05-02-preview'])
        def delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'resource_name', 'accept']}, api_versions_list=['2026-05-02-preview'])
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ManagedClusterSnapshot: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2026-05-02-preview'])
        def list(self, **kwargs: Any) -> ItemPaged[ManagedClusterSnapshot]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2026-05-02-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ManagedClusterSnapshot]: ...

        @overload
        def update_tags(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: TagsObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagedClusterSnapshot: ...

        @overload
        def update_tags(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: TagsObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagedClusterSnapshot: ...

        @overload
        def update_tags(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagedClusterSnapshot: ...


    class azure.mgmt.containerservice.operations.ManagedClustersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_abort_latest_operation(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: ManagedCluster, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[ManagedCluster]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: ManagedCluster, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[ManagedCluster]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[ManagedCluster]: ...

        @distributed_trace
        @api_version_validation(params_added_on={'2026-05-02-preview': ['ignore_pod_disruption_budget']}, api_versions_list=['2025-10-01', '2026-01-01', '2026-02-01', '2026-03-01', '2026-04-01', '2026-05-01', '2026-05-02-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                *, 
                etag: Optional[str] = ..., 
                ignore_pod_disruption_budget: Optional[bool] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_rebalance_load_balancers(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: RebalanceLoadBalancersRequestBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_rebalance_load_balancers(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: RebalanceLoadBalancersRequestBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_rebalance_load_balancers(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_reset_aad_profile(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: ManagedClusterAADProfile, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_reset_aad_profile(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: ManagedClusterAADProfile, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_reset_aad_profile(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_reset_service_principal_profile(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: ManagedClusterServicePrincipalProfile, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_reset_service_principal_profile(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: ManagedClusterServicePrincipalProfile, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_reset_service_principal_profile(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_rotate_cluster_certificates(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_rotate_service_account_signing_keys(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_run_command(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                request_payload: RunCommandRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RunCommandResult]: ...

        @overload
        def begin_run_command(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                request_payload: RunCommandRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RunCommandResult]: ...

        @overload
        def begin_run_command(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                request_payload: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RunCommandResult]: ...

        @distributed_trace
        def begin_start(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_stop(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update_tags(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: TagsObject, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[ManagedCluster]: ...

        @overload
        def begin_update_tags(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: TagsObject, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[ManagedCluster]: ...

        @overload
        def begin_update_tags(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[ManagedCluster]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ManagedCluster: ...

        @distributed_trace
        def get_access_profile(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                role_name: str, 
                **kwargs: Any
            ) -> ManagedClusterAccessProfile: ...

        @distributed_trace
        def get_command_result(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                command_id: str, 
                **kwargs: Any
            ) -> Optional[RunCommandResult]: ...

        @distributed_trace
        def get_guardrails_versions(
                self, 
                location: str, 
                version: str, 
                **kwargs: Any
            ) -> GuardrailsAvailableVersion: ...

        @distributed_trace
        def get_mesh_revision_profile(
                self, 
                location: str, 
                mode: str, 
                **kwargs: Any
            ) -> MeshRevisionProfile: ...

        @distributed_trace
        def get_mesh_upgrade_profile(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                mode: str, 
                **kwargs: Any
            ) -> MeshUpgradeProfile: ...

        @distributed_trace
        def get_safeguards_versions(
                self, 
                location: str, 
                version: str, 
                **kwargs: Any
            ) -> SafeguardsAvailableVersion: ...

        @distributed_trace
        def get_upgrade_profile(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ManagedClusterUpgradeProfile: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[ManagedCluster]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ManagedCluster]: ...

        @distributed_trace
        def list_cluster_admin_credentials(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                *, 
                server_fqdn: Optional[str] = ..., 
                **kwargs: Any
            ) -> CredentialResults: ...

        @distributed_trace
        def list_cluster_monitoring_user_credentials(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                *, 
                server_fqdn: Optional[str] = ..., 
                **kwargs: Any
            ) -> CredentialResults: ...

        @distributed_trace
        def list_cluster_user_credentials(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                *, 
                format: Optional[Union[str, Format]] = ..., 
                server_fqdn: Optional[str] = ..., 
                **kwargs: Any
            ) -> CredentialResults: ...

        @distributed_trace
        def list_guardrails_versions(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[GuardrailsAvailableVersion]: ...

        @distributed_trace
        def list_kubernetes_versions(
                self, 
                location: str, 
                **kwargs: Any
            ) -> KubernetesVersionListResult: ...

        @distributed_trace
        def list_mesh_revision_profiles(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[MeshRevisionProfile]: ...

        @distributed_trace
        def list_mesh_upgrade_profiles(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ItemPaged[MeshUpgradeProfile]: ...

        @distributed_trace
        def list_outbound_network_dependencies_endpoints(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ItemPaged[OutboundEnvironmentEndpoint]: ...

        @distributed_trace
        def list_safeguards_versions(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[SafeguardsAvailableVersion]: ...


    class azure.mgmt.containerservice.operations.ManagedNamespacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                managed_namespace_name: str, 
                parameters: ManagedNamespace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedNamespace]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                managed_namespace_name: str, 
                parameters: ManagedNamespace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedNamespace]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                managed_namespace_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedNamespace]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                managed_namespace_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                managed_namespace_name: str, 
                **kwargs: Any
            ) -> ManagedNamespace: ...

        @distributed_trace
        def list_by_managed_cluster(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ManagedNamespace]: ...

        @distributed_trace
        def list_credential(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                managed_namespace_name: str, 
                **kwargs: Any
            ) -> CredentialResults: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                managed_namespace_name: str, 
                parameters: TagsObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagedNamespace: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                managed_namespace_name: str, 
                parameters: TagsObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagedNamespace: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                managed_namespace_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagedNamespace: ...


    class azure.mgmt.containerservice.operations.MeshMembershipsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                mesh_membership_name: str, 
                parameters: MeshMembership, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MeshMembership]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                mesh_membership_name: str, 
                parameters: MeshMembership, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MeshMembership]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                mesh_membership_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MeshMembership]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'resource_name', 'mesh_membership_name']}, api_versions_list=['2026-05-02-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                mesh_membership_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'resource_name', 'mesh_membership_name', 'accept']}, api_versions_list=['2026-05-02-preview'])
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                mesh_membership_name: str, 
                **kwargs: Any
            ) -> MeshMembership: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'resource_name', 'accept']}, api_versions_list=['2026-05-02-preview'])
        def list_by_managed_cluster(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ItemPaged[MeshMembership]: ...


    class azure.mgmt.containerservice.operations.OperationStatusResultOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'resource_name', 'operation_id', 'accept']}, api_versions_list=['2026-05-02-preview'])
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationStatusResult: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'resource_name', 'agent_pool_name', 'operation_id', 'accept']}, api_versions_list=['2026-05-02-preview'])
        def get_by_agent_pool(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                agent_pool_name: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationStatusResult: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'resource_name', 'accept']}, api_versions_list=['2026-05-02-preview'])
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ItemPaged[OperationStatusResult]: ...


    class azure.mgmt.containerservice.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[OperationValue]: ...


    class azure.mgmt.containerservice.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnectionListResult: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                private_endpoint_connection_name: str, 
                parameters: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                private_endpoint_connection_name: str, 
                parameters: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                private_endpoint_connection_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...


    class azure.mgmt.containerservice.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResourcesListResult: ...


    class azure.mgmt.containerservice.operations.ResolvePrivateLinkServiceIdOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def post(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: PrivateLinkResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @overload
        def post(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: PrivateLinkResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @overload
        def post(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateLinkResource: ...


    class azure.mgmt.containerservice.operations.SnapshotsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: Snapshot, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Snapshot: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: Snapshot, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Snapshot: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Snapshot: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> Snapshot: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Snapshot]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Snapshot]: ...

        @overload
        def update_tags(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: TagsObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Snapshot: ...

        @overload
        def update_tags(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: TagsObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Snapshot: ...

        @overload
        def update_tags(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Snapshot: ...


    class azure.mgmt.containerservice.operations.TrustedAccessRoleBindingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                trusted_access_role_binding_name: str, 
                trusted_access_role_binding: TrustedAccessRoleBinding, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TrustedAccessRoleBinding]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                trusted_access_role_binding_name: str, 
                trusted_access_role_binding: TrustedAccessRoleBinding, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TrustedAccessRoleBinding]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                trusted_access_role_binding_name: str, 
                trusted_access_role_binding: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TrustedAccessRoleBinding]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                trusted_access_role_binding_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                trusted_access_role_binding_name: str, 
                **kwargs: Any
            ) -> TrustedAccessRoleBinding: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ItemPaged[TrustedAccessRoleBinding]: ...


    class azure.mgmt.containerservice.operations.TrustedAccessRolesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[TrustedAccessRole]: ...


    class azure.mgmt.containerservice.operations.VmSkusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                *, 
                include_extended_locations: Optional[bool] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ResourceSku]: ...


namespace azure.mgmt.containerservice.types

    class azure.mgmt.containerservice.types.AbsoluteMonthlySchedule(TypedDict, total=False):
        key "dayOfMonth": Required[int]
        key "intervalMonths": Required[int]
        day_of_month: int
        interval_months: int


    class azure.mgmt.containerservice.types.AdvancedNetworking(TypedDict, total=False):
        key "enabled": bool
        key "observability": ForwardRef('AdvancedNetworkingObservability', module='types')
        key "performance": ForwardRef('AdvancedNetworkingPerformance', module='types')
        key "security": ForwardRef('AdvancedNetworkingSecurity', module='types')
        enabled: bool
        observability: AdvancedNetworkingObservability
        performance: AdvancedNetworkingPerformance
        security: AdvancedNetworkingSecurity


    class azure.mgmt.containerservice.types.AdvancedNetworkingObservability(TypedDict, total=False):
        key "enabled": bool
        enabled: bool


    class azure.mgmt.containerservice.types.AdvancedNetworkingPerformance(TypedDict, total=False):
        key "accelerationMode": Union[str, AccelerationMode]
        acceleration_mode: Union[str, AccelerationMode]


    class azure.mgmt.containerservice.types.AdvancedNetworkingSecurity(TypedDict, total=False):
        key "advancedNetworkPolicies": Union[str, AdvancedNetworkPolicies]
        key "enabled": bool
        key "transitEncryption": ForwardRef('AdvancedNetworkingSecurityTransitEncryption', module='types')
        advanced_network_policies: Union[str, AdvancedNetworkPolicies]
        enabled: bool
        transit_encryption: AdvancedNetworkingSecurityTransitEncryption


    class azure.mgmt.containerservice.types.AdvancedNetworkingSecurityTransitEncryption(TypedDict, total=False):
        key "type": Union[str, TransitEncryptionType]
        type: Union[str, TransitEncryptionType]


    class azure.mgmt.containerservice.types.AgentPool(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('AgentPoolManagedClusterAgentPoolProfileProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: AgentPoolManagedClusterAgentPoolProfileProperties
        system_data: SystemData
        type: str


    class azure.mgmt.containerservice.types.AgentPoolArtifactStreamingProfile(TypedDict, total=False):
        key "enabled": bool
        enabled: bool


    class azure.mgmt.containerservice.types.AgentPoolBlueGreenUpgradeSettings(TypedDict, total=False):
        key "batchSoakDurationInMinutes": int
        key "drainBatchSize": str
        key "drainTimeoutInMinutes": int
        key "finalSoakDurationInMinutes": int
        batch_soak_duration_in_minutes: int
        drain_batch_size: str
        drain_timeout_in_minutes: int
        final_soak_duration_in_minutes: int


    class azure.mgmt.containerservice.types.AgentPoolDeleteMachinesParameter(TypedDict, total=False):
        key "machineNames": Required[list[str]]
        machine_names: list[str]


    class azure.mgmt.containerservice.types.AgentPoolGatewayProfile(TypedDict, total=False):
        key "publicIPPrefixSize": int
        public_ip_prefix_size: int


    class azure.mgmt.containerservice.types.AgentPoolManagedClusterAgentPoolProfileProperties(TypedDict, total=False):
        key "artifactStreamingProfile": ForwardRef('AgentPoolArtifactStreamingProfile', module='types')
        key "capacityReservationGroupID": str
        key "count": int
        key "creationData": ForwardRef('CreationData', module='types')
        key "currentOrchestratorVersion": str
        key "eTag": str
        key "enableAutoScaling": bool
        key "enableEncryptionAtHost": bool
        key "enableFIPS": bool
        key "enableNodePublicIP": bool
        key "enableOSDiskFullCaching": bool
        key "enableUltraSSD": bool
        key "gatewayProfile": ForwardRef('AgentPoolGatewayProfile', module='types')
        key "gpuInstanceProfile": Union[str, GPUInstanceProfile]
        key "gpuProfile": ForwardRef('GPUProfile', module='types')
        key "hostGroupID": str
        key "kubeletConfig": ForwardRef('KubeletConfig', module='types')
        key "kubeletDiskType": Union[str, KubeletDiskType]
        key "linuxOSConfig": ForwardRef('LinuxOSConfig', module='types')
        key "localDNSProfile": ForwardRef('LocalDNSProfile', module='types')
        key "maxCount": int
        key "maxPods": int
        key "messageOfTheDay": str
        key "minCount": int
        key "mode": Union[str, AgentPoolMode]
        key "networkProfile": ForwardRef('AgentPoolNetworkProfile', module='types')
        key "nodeImageVersion": str
        key "nodePublicIPPrefixID": str
        key "orchestratorVersion": str
        key "osDiskSizeGB": int
        key "osDiskType": Union[str, OSDiskType]
        key "osSKU": Union[str, OSSKU]
        key "osType": Union[str, OSType]
        key "podIPAllocationMode": Union[str, PodIPAllocationMode]
        key "podSubnetID": str
        key "powerState": ForwardRef('PowerState', module='types')
        key "preparedImageSpecificationProfile": ForwardRef('PreparedImageSpecificationProfile', module='types')
        key "provisioningState": str
        key "proximityPlacementGroupID": str
        key "scaleDownMode": Union[str, ScaleDownMode]
        key "scaleSetEvictionPolicy": Union[str, ScaleSetEvictionPolicy]
        key "scaleSetPriority": Union[str, ScaleSetPriority]
        key "securityProfile": ForwardRef('AgentPoolSecurityProfile', module='types')
        key "spotMaxPrice": float
        key "status": ForwardRef('AgentPoolStatus', module='types')
        key "type": Union[str, AgentPoolType]
        key "upgradeSettings": ForwardRef('AgentPoolUpgradeSettings', module='types')
        key "upgradeSettingsBlueGreen": ForwardRef('AgentPoolBlueGreenUpgradeSettings', module='types')
        key "upgradeStrategy": Union[str, UpgradeStrategy]
        key "virtualMachinesProfile": ForwardRef('VirtualMachinesProfile', module='types')
        key "vmSize": str
        key "vnetSubnetID": str
        key "windowsProfile": ForwardRef('AgentPoolWindowsProfile', module='types')
        key "workloadRuntime": Union[str, WorkloadRuntime]
        artifact_streaming_profile: AgentPoolArtifactStreamingProfile
        availabilityZones: list[str]
        availability_zones: list[str]
        capacity_reservation_group_id: str
        count: int
        creation_data: CreationData
        current_orchestrator_version: str
        e_tag: str
        enable_auto_scaling: bool
        enable_encryption_at_host: bool
        enable_fips: bool
        enable_node_public_ip: bool
        enable_os_disk_full_caching: bool
        enable_ultra_ssd: bool
        gateway_profile: AgentPoolGatewayProfile
        gpu_instance_profile: Union[str, GPUInstanceProfile]
        gpu_profile: GPUProfile
        host_group_id: str
        kubelet_config: KubeletConfig
        kubelet_disk_type: Union[str, KubeletDiskType]
        linux_os_config: LinuxOSConfig
        local_dns_profile: LocalDNSProfile
        max_count: int
        max_pods: int
        message_of_the_day: str
        min_count: int
        mode: Union[str, AgentPoolMode]
        network_profile: AgentPoolNetworkProfile
        nodeInitializationTaints: list[str]
        nodeLabels: dict[str, str]
        nodeTaints: list[str]
        node_image_version: str
        node_initialization_taints: list[str]
        node_labels: dict[str, str]
        node_public_ip_prefix_id: str
        node_taints: list[str]
        orchestrator_version: str
        os_disk_size_gb: int
        os_disk_type: Union[str, OSDiskType]
        os_sku: Union[str, OSSKU]
        os_type: Union[str, OSType]
        pod_ip_allocation_mode: Union[str, PodIPAllocationMode]
        pod_subnet_id: str
        power_state: PowerState
        prepared_image_specification_profile: PreparedImageSpecificationProfile
        provisioning_state: str
        proximity_placement_group_id: str
        scale_down_mode: Union[str, ScaleDownMode]
        scale_set_eviction_policy: Union[str, ScaleSetEvictionPolicy]
        scale_set_priority: Union[str, ScaleSetPriority]
        security_profile: AgentPoolSecurityProfile
        spot_max_price: float
        status: AgentPoolStatus
        tags: dict[str, str]
        type_properties_type: Union[str, AgentPoolType]
        upgrade_settings: AgentPoolUpgradeSettings
        upgrade_settings_blue_green: AgentPoolBlueGreenUpgradeSettings
        upgrade_strategy: Union[str, UpgradeStrategy]
        virtualMachineNodesStatus: list[VirtualMachineNodes]
        virtual_machine_nodes_status: list[VirtualMachineNodes]
        virtual_machines_profile: VirtualMachinesProfile
        vm_size: str
        vnet_subnet_id: str
        windows_profile: AgentPoolWindowsProfile
        workload_runtime: Union[str, WorkloadRuntime]


    class azure.mgmt.containerservice.types.AgentPoolNetworkInterface(TypedDict, total=False):
        key "enableAcceleratedNetworking": bool
        key "type": Union[str, AgentPoolNetworkInterfaceType]
        key "vnetSubnetId": str
        enable_accelerated_networking: bool
        type: Union[str, AgentPoolNetworkInterfaceType]
        vnet_subnet_id: str


    class azure.mgmt.containerservice.types.AgentPoolNetworkProfile(TypedDict, total=False):
        allowedHostPorts: list[PortRange]
        allowed_host_ports: list[PortRange]
        applicationSecurityGroups: list[str]
        application_security_groups: list[str]
        nodePublicIPPrefixIDs: list[str]
        nodePublicIPTags: list[IPTag]
        node_public_ip_prefix_i_ds: list[str]
        node_public_ip_tags: list[IPTag]
        secondaryNetworkInterfaces: list[AgentPoolNetworkInterface]
        secondary_network_interfaces: list[AgentPoolNetworkInterface]


    class azure.mgmt.containerservice.types.AgentPoolSecurityProfile(TypedDict, total=False):
        key "enableSecureBoot": bool
        key "enableVTPM": bool
        key "sshAccess": Union[str, AgentPoolSSHAccess]
        enable_secure_boot: bool
        enable_vtpm: bool
        ssh_access: Union[str, AgentPoolSSHAccess]


    class azure.mgmt.containerservice.types.AgentPoolStatus(TypedDict, total=False):
        key "provisioningError": ForwardRef('ErrorDetail', module='types')
        provisioning_error: ErrorDetail


    class azure.mgmt.containerservice.types.AgentPoolUpgradeSettings(TypedDict, total=False):
        key "drainTimeoutInMinutes": int
        key "maxBlockedNodes": str
        key "maxSurge": str
        key "maxUnavailable": str
        key "nodeSoakDurationInMinutes": int
        key "undrainableNodeBehavior": Union[str, UndrainableNodeBehavior]
        drain_timeout_in_minutes: int
        max_blocked_nodes: str
        max_surge: str
        max_unavailable: str
        node_soak_duration_in_minutes: int
        undrainable_node_behavior: Union[str, UndrainableNodeBehavior]


    class azure.mgmt.containerservice.types.AgentPoolWindowsProfile(TypedDict, total=False):
        key "disableOutboundNat": bool
        disable_outbound_nat: bool


    class azure.mgmt.containerservice.types.AlertConfiguration(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('AlertConfigurationProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: AlertConfigurationProperties
        system_data: SystemData
        type: str


    class azure.mgmt.containerservice.types.AlertConfigurationProperties(TypedDict, total=False):
        key "mode": Required[Union[str, AlertConfigurationMode]]
        key "notification": Required[AlertNotification]
        key "provisioningState": Union[str, AlertConfigurationProvisioningState]
        mode: Union[str, AlertConfigurationMode]
        notification: AlertNotification
        provisioning_state: Union[str, AlertConfigurationProvisioningState]


    class azure.mgmt.containerservice.types.AlertNotification(TypedDict, total=False):
        key "actionGroupId": Required[str]
        action_group_id: str


    class azure.mgmt.containerservice.types.AllowedSubject(TypedDict, total=False):
        key "namespaceSelector": Required[LabelSelector]
        key "serviceAccountSelector": ForwardRef('LabelSelector', module='types')
        namespace_selector: LabelSelector
        service_account_selector: LabelSelector


    class azure.mgmt.containerservice.types.AutoScaleProfile(TypedDict, total=False):
        key "maxCount": int
        key "minCount": int
        key "size": str
        max_count: int
        min_count: int
        size: str


    class azure.mgmt.containerservice.types.AzureKeyVaultKms(TypedDict, total=False):
        key "enabled": bool
        key "keyId": str
        key "keyVaultNetworkAccess": Union[str, KeyVaultNetworkAccessTypes]
        key "keyVaultResourceId": str
        enabled: bool
        key_id: str
        key_vault_network_access: Union[str, KeyVaultNetworkAccessTypes]
        key_vault_resource_id: str


    class azure.mgmt.containerservice.types.BastionProfile(TypedDict, total=False):
        key "bastionId": str
        key "enabled": bool
        key "publicIpAddressId": str
        key "scaleUnits": int
        key "sku": Union[str, BastionSku]
        bastion_id: str
        enabled: bool
        public_ip_address_id: str
        scale_units: int
        sku: Union[str, BastionSku]


    class azure.mgmt.containerservice.types.ClusterUpgradeSettings(TypedDict, total=False):
        key "overrideSettings": ForwardRef('UpgradeOverrideSettings', module='types')
        override_settings: UpgradeOverrideSettings


    class azure.mgmt.containerservice.types.ContainerServiceLinuxProfile(TypedDict, total=False):
        key "adminUsername": Required[str]
        key "ssh": Required[ContainerServiceSshConfiguration]
        admin_username: str
        ssh: ContainerServiceSshConfiguration


    class azure.mgmt.containerservice.types.ContainerServiceNetworkProfile(TypedDict, total=False):
        key "advancedNetworking": ForwardRef('AdvancedNetworking', module='types')
        key "bastionProfile": ForwardRef('BastionProfile', module='types')
        key "dnsServiceIP": str
        key "kubeProxyConfig": ForwardRef('ContainerServiceNetworkProfileKubeProxyConfig', module='types')
        key "loadBalancerProfile": ForwardRef('ManagedClusterLoadBalancerProfile', module='types')
        key "loadBalancerSku": Union[str, LoadBalancerSku]
        key "natGatewayId": str
        key "natGatewayProfile": ForwardRef('ManagedClusterNATGatewayProfile', module='types')
        key "networkDataplane": Union[str, NetworkDataplane]
        key "networkMode": Union[str, NetworkMode]
        key "networkPlugin": Union[str, NetworkPlugin]
        key "networkPluginMode": Union[str, NetworkPluginMode]
        key "networkPolicy": Union[str, NetworkPolicy]
        key "outboundType": Union[str, OutboundType]
        key "podCidr": str
        key "podLinkLocalAccess": Union[str, PodLinkLocalAccess]
        key "serviceCidr": str
        key "staticEgressGatewayProfile": ForwardRef('ManagedClusterStaticEgressGatewayProfile', module='types')
        advanced_networking: AdvancedNetworking
        bastion_profile: BastionProfile
        dns_service_ip: str
        ipFamilies: list[Union[str, IPFamily]]
        ip_families: list[Union[str, IPFamily]]
        kube_proxy_config: ContainerServiceNetworkProfileKubeProxyConfig
        load_balancer_profile: ManagedClusterLoadBalancerProfile
        load_balancer_sku: Union[str, LoadBalancerSku]
        nat_gateway_id: str
        nat_gateway_profile: ManagedClusterNATGatewayProfile
        network_dataplane: Union[str, NetworkDataplane]
        network_mode: Union[str, NetworkMode]
        network_plugin: Union[str, NetworkPlugin]
        network_plugin_mode: Union[str, NetworkPluginMode]
        network_policy: Union[str, NetworkPolicy]
        outbound_type: Union[str, OutboundType]
        podCidrs: list[str]
        pod_cidr: str
        pod_cidrs: list[str]
        pod_link_local_access: Union[str, PodLinkLocalAccess]
        serviceCidrs: list[str]
        service_cidr: str
        service_cidrs: list[str]
        static_egress_gateway_profile: ManagedClusterStaticEgressGatewayProfile


    class azure.mgmt.containerservice.types.ContainerServiceNetworkProfileKubeProxyConfig(TypedDict, total=False):
        key "enabled": bool
        key "ipvsConfig": ForwardRef('ContainerServiceNetworkProfileKubeProxyConfigIpvsConfig', module='types')
        key "mode": Union[str, Mode]
        enabled: bool
        ipvs_config: ContainerServiceNetworkProfileKubeProxyConfigIpvsConfig
        mode: Union[str, Mode]


    class azure.mgmt.containerservice.types.ContainerServiceNetworkProfileKubeProxyConfigIpvsConfig(TypedDict, total=False):
        key "scheduler": Union[str, IpvsScheduler]
        key "tcpFinTimeoutSeconds": int
        key "tcpTimeoutSeconds": int
        key "udpTimeoutSeconds": int
        scheduler: Union[str, IpvsScheduler]
        tcp_fin_timeout_seconds: int
        tcp_timeout_seconds: int
        udp_timeout_seconds: int


    class azure.mgmt.containerservice.types.ContainerServiceSshConfiguration(TypedDict, total=False):
        key "publicKeys": Required[list[ContainerServiceSshPublicKey]]
        public_keys: list[ContainerServiceSshPublicKey]


    class azure.mgmt.containerservice.types.ContainerServiceSshPublicKey(TypedDict, total=False):
        key "keyData": Required[str]
        key_data: str


    class azure.mgmt.containerservice.types.CreationData(TypedDict, total=False):
        key "sourceResourceId": str
        source_resource_id: str


    class azure.mgmt.containerservice.types.DailySchedule(TypedDict, total=False):
        key "intervalDays": Required[int]
        interval_days: int


    class azure.mgmt.containerservice.types.DateSpan(TypedDict, total=False):
        key "end": Required[str]
        key "start": Required[str]
        end: str
        start: str


    class azure.mgmt.containerservice.types.DelegatedResource(TypedDict, total=False):
        key "location": str
        key "referralResource": str
        key "resourceId": str
        key "tenantId": str
        location: str
        referral_resource: str
        resource_id: str
        tenant_id: str


    class azure.mgmt.containerservice.types.ErrorAdditionalInfo(TypedDict, total=False):
        key "info": Any
        key "type": str
        info: Any
        type: str


    class azure.mgmt.containerservice.types.ErrorDetail(TypedDict, total=False):
        key "code": str
        key "message": str
        key "target": str
        additionalInfo: list[ErrorAdditionalInfo]
        additional_info: list[ErrorAdditionalInfo]
        code: str
        details: list[ErrorDetail]
        message: str
        target: str


    class azure.mgmt.containerservice.types.ExtendedLocation(TypedDict, total=False):
        key "name": str
        key "type": Union[str, ExtendedLocationTypes]
        name: str
        type: Union[str, ExtendedLocationTypes]


    class azure.mgmt.containerservice.types.GPUProfile(TypedDict, total=False):
        key "driver": Union[str, GPUDriver]
        key "driverType": Union[str, DriverType]
        key "nvidia": ForwardRef('NvidiaGPUProfile', module='types')
        driver: Union[str, GPUDriver]
        driver_type: Union[str, DriverType]
        nvidia: NvidiaGPUProfile


    class azure.mgmt.containerservice.types.HardEvictionThreshold(TypedDict, total=False):
        key "memoryAvailable": str
        key "nodeFsAvailable": str
        key "nodeFsInodesFree": str
        memory_available: str
        node_fs_available: str
        node_fs_inodes_free: str


    class azure.mgmt.containerservice.types.IPTag(TypedDict, total=False):
        key "ipTagType": str
        key "tag": str
        ip_tag_type: str
        tag: str


    class azure.mgmt.containerservice.types.IdentityBinding(ProxyResource):
        key "eTag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('IdentityBindingProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        e_tag: str
        id: str
        name: str
        properties: IdentityBindingProperties
        system_data: SystemData
        type: str


    class azure.mgmt.containerservice.types.IdentityBindingManagedIdentityProfile(TypedDict, total=False):
        key "clientId": str
        key "objectId": str
        key "resourceId": Required[str]
        key "tenantId": str
        client_id: str
        object_id: str
        resource_id: str
        tenant_id: str


    class azure.mgmt.containerservice.types.IdentityBindingOidcIssuerProfile(TypedDict, total=False):
        key "oidcIssuerUrl": str
        oidc_issuer_url: str


    class azure.mgmt.containerservice.types.IdentityBindingProperties(TypedDict, total=False):
        key "managedIdentity": Required[IdentityBindingManagedIdentityProfile]
        key "oidcIssuer": ForwardRef('IdentityBindingOidcIssuerProfile', module='types')
        key "provisioningState": Union[str, IdentityBindingProvisioningState]
        allowedSubjects: list[AllowedSubject]
        allowed_subjects: list[AllowedSubject]
        managed_identity: IdentityBindingManagedIdentityProfile
        oidc_issuer: IdentityBindingOidcIssuerProfile
        provisioning_state: Union[str, IdentityBindingProvisioningState]


    class azure.mgmt.containerservice.types.IstioCertificateAuthority(TypedDict, total=False):
        key "plugin": ForwardRef('IstioPluginCertificateAuthority', module='types')
        plugin: IstioPluginCertificateAuthority


    class azure.mgmt.containerservice.types.IstioComponents(TypedDict, total=False):
        key "proxyRedirectionMechanism": Union[str, ProxyRedirectionMechanism]
        egressGateways: list[IstioEgressGateway]
        egress_gateways: list[IstioEgressGateway]
        ingressGateways: list[IstioIngressGateway]
        ingress_gateways: list[IstioIngressGateway]
        proxy_redirection_mechanism: Union[str, ProxyRedirectionMechanism]


    class azure.mgmt.containerservice.types.IstioEgressGateway(TypedDict, total=False):
        key "enabled": Required[bool]
        key "gatewayConfigurationName": str
        key "name": Required[str]
        key "namespace": str
        enabled: bool
        gateway_configuration_name: str
        name: str
        namespace: str


    class azure.mgmt.containerservice.types.IstioIngressGateway(TypedDict, total=False):
        key "enabled": Required[bool]
        key "mode": Required[Union[str, IstioIngressGatewayMode]]
        enabled: bool
        mode: Union[str, IstioIngressGatewayMode]


    class azure.mgmt.containerservice.types.IstioPluginCertificateAuthority(TypedDict, total=False):
        key "certChainObjectName": str
        key "certObjectName": str
        key "keyObjectName": str
        key "keyVaultId": str
        key "rootCertObjectName": str
        cert_chain_object_name: str
        cert_object_name: str
        key_object_name: str
        key_vault_id: str
        root_cert_object_name: str


    class azure.mgmt.containerservice.types.IstioServiceMesh(TypedDict, total=False):
        key "certificateAuthority": ForwardRef('IstioCertificateAuthority', module='types')
        key "components": ForwardRef('IstioComponents', module='types')
        certificate_authority: IstioCertificateAuthority
        components: IstioComponents
        revisions: list[str]


    class azure.mgmt.containerservice.types.JWTAuthenticator(ProxyResource):
        key "id": str
        key "name": str
        key "properties": Required[JWTAuthenticatorProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: JWTAuthenticatorProperties
        system_data: SystemData
        type: str


    class azure.mgmt.containerservice.types.JWTAuthenticatorClaimMappingExpression(TypedDict, total=False):
        key "expression": Required[str]
        expression: str


    class azure.mgmt.containerservice.types.JWTAuthenticatorClaimMappings(TypedDict, total=False):
        key "groups": ForwardRef('JWTAuthenticatorClaimMappingExpression', module='types')
        key "uid": ForwardRef('JWTAuthenticatorClaimMappingExpression', module='types')
        key "username": Required[JWTAuthenticatorClaimMappingExpression]
        extra: list[JWTAuthenticatorExtraClaimMappingExpression]
        groups: JWTAuthenticatorClaimMappingExpression
        uid: JWTAuthenticatorClaimMappingExpression
        username: JWTAuthenticatorClaimMappingExpression


    class azure.mgmt.containerservice.types.JWTAuthenticatorExtraClaimMappingExpression(TypedDict, total=False):
        key "key": Required[str]
        key "valueExpression": Required[str]
        key: str
        value_expression: str


    class azure.mgmt.containerservice.types.JWTAuthenticatorIssuer(TypedDict, total=False):
        key "audiences": Required[list[str]]
        key "url": Required[str]
        audiences: list[str]
        url: str


    class azure.mgmt.containerservice.types.JWTAuthenticatorProperties(TypedDict, total=False):
        key "claimMappings": Required[JWTAuthenticatorClaimMappings]
        key "issuer": Required[JWTAuthenticatorIssuer]
        key "provisioningState": Union[str, JWTAuthenticatorProvisioningState]
        claimValidationRules: list[JWTAuthenticatorValidationRule]
        claim_mappings: JWTAuthenticatorClaimMappings
        claim_validation_rules: list[JWTAuthenticatorValidationRule]
        issuer: JWTAuthenticatorIssuer
        provisioning_state: Union[str, JWTAuthenticatorProvisioningState]
        userValidationRules: list[JWTAuthenticatorValidationRule]
        user_validation_rules: list[JWTAuthenticatorValidationRule]


    class azure.mgmt.containerservice.types.JWTAuthenticatorValidationRule(TypedDict, total=False):
        key "expression": Required[str]
        key "message": str
        expression: str
        message: str


    class azure.mgmt.containerservice.types.KubeReserved(TypedDict, total=False):
        key "cpuMillicores": int
        key "memoryMB": int
        cpu_millicores: int
        memory_mb: int


    class azure.mgmt.containerservice.types.KubeletConfig(TypedDict, total=False):
        key "containerLogMaxFiles": int
        key "containerLogMaxSizeMB": int
        key "cpuCfsQuota": bool
        key "cpuCfsQuotaPeriod": str
        key "cpuManagerPolicy": str
        key "failSwapOn": bool
        key "hardEvictionThreshold": ForwardRef('HardEvictionThreshold', module='types')
        key "imageGcHighThreshold": int
        key "imageGcLowThreshold": int
        key "kubeReserved": ForwardRef('KubeReserved', module='types')
        key "podMaxPids": int
        key "seccompDefault": Union[str, SeccompDefault]
        key "topologyManagerPolicy": str
        allowedUnsafeSysctls: list[str]
        allowed_unsafe_sysctls: list[str]
        container_log_max_files: int
        container_log_max_size_mb: int
        cpu_cfs_quota: bool
        cpu_cfs_quota_period: str
        cpu_manager_policy: str
        fail_swap_on: bool
        hard_eviction_threshold: HardEvictionThreshold
        image_gc_high_threshold: int
        image_gc_low_threshold: int
        kube_reserved: KubeReserved
        pod_max_pids: int
        seccomp_default: Union[str, SeccompDefault]
        topology_manager_policy: str


    class azure.mgmt.containerservice.types.KubernetesResourceObjectEncryptionProfile(TypedDict, total=False):
        key "infrastructureEncryption": Union[str, InfrastructureEncryption]
        infrastructure_encryption: Union[str, InfrastructureEncryption]


    class azure.mgmt.containerservice.types.LabelSelector(TypedDict, total=False):
        matchExpressions: list[LabelSelectorRequirement]
        matchLabels: list[str]
        match_expressions: list[LabelSelectorRequirement]
        match_labels: list[str]


    class azure.mgmt.containerservice.types.LabelSelectorRequirement(TypedDict, total=False):
        key "key": str
        key "operator": Union[str, Operator]
        key: str
        operator: Union[str, Operator]
        values: list[str]
        values_property: list[str]


    class azure.mgmt.containerservice.types.LinuxOSConfig(TypedDict, total=False):
        key "swapFileSizeMB": int
        key "sysctls": ForwardRef('SysctlConfig', module='types')
        key "transparentHugePageDefrag": str
        key "transparentHugePageEnabled": str
        swap_file_size_mb: int
        sysctls: SysctlConfig
        transparent_huge_page_defrag: str
        transparent_huge_page_enabled: str


    class azure.mgmt.containerservice.types.ListBootstrapDataRequest(TypedDict, total=False):


    class azure.mgmt.containerservice.types.LoadBalancer(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('LoadBalancerProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: LoadBalancerProperties
        system_data: SystemData
        type: str


    class azure.mgmt.containerservice.types.LoadBalancerProperties(TypedDict, total=False):
        key "allowServicePlacement": bool
        key "nodeSelector": ForwardRef('LabelSelector', module='types')
        key "primaryAgentPoolName": Required[str]
        key "provisioningState": str
        key "serviceLabelSelector": ForwardRef('LabelSelector', module='types')
        key "serviceNamespaceSelector": ForwardRef('LabelSelector', module='types')
        allow_service_placement: bool
        node_selector: LabelSelector
        primary_agent_pool_name: str
        provisioning_state: str
        service_label_selector: LabelSelector
        service_namespace_selector: LabelSelector


    class azure.mgmt.containerservice.types.LocalDNSOverride(TypedDict, total=False):
        key "cacheDurationInSeconds": int
        key "forwardDestination": Union[str, LocalDNSForwardDestination]
        key "forwardPolicy": Union[str, LocalDNSForwardPolicy]
        key "maxConcurrent": int
        key "protocol": Union[str, LocalDNSProtocol]
        key "queryLogging": Union[str, LocalDNSQueryLogging]
        key "serveStale": Union[str, LocalDNSServeStale]
        key "serveStaleDurationInSeconds": int
        cache_duration_in_seconds: int
        forward_destination: Union[str, LocalDNSForwardDestination]
        forward_policy: Union[str, LocalDNSForwardPolicy]
        max_concurrent: int
        protocol: Union[str, LocalDNSProtocol]
        query_logging: Union[str, LocalDNSQueryLogging]
        serve_stale: Union[str, LocalDNSServeStale]
        serve_stale_duration_in_seconds: int


    class azure.mgmt.containerservice.types.LocalDNSProfile(TypedDict, total=False):
        key "mode": Union[str, LocalDNSMode]
        key "state": Union[str, LocalDNSState]
        kubeDNSOverrides: dict[str, LocalDNSOverride]
        kube_dns_overrides: dict[str, LocalDNSOverride]
        mode: Union[str, LocalDNSMode]
        state: Union[str, LocalDNSState]
        vnetDNSOverrides: dict[str, LocalDNSOverride]
        vnet_dns_overrides: dict[str, LocalDNSOverride]


    class azure.mgmt.containerservice.types.Machine(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('MachineProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: MachineProperties
        system_data: SystemData
        type: str
        zones: list[str]


    class azure.mgmt.containerservice.types.MachineBillingProfile(TypedDict, total=False):
        key "spotMaxPrice": float
        spot_max_price: float


    class azure.mgmt.containerservice.types.MachineHardwareProfile(TypedDict, total=False):
        key "gpuInstanceProfile": Union[str, GPUInstanceProfile]
        key "gpuProfile": ForwardRef('GPUProfile', module='types')
        key "ultraSsdEnabled": bool
        key "vmSize": str
        gpu_instance_profile: Union[str, GPUInstanceProfile]
        gpu_profile: GPUProfile
        ultra_ssd_enabled: bool
        vm_size: str


    class azure.mgmt.containerservice.types.MachineIpAddress(TypedDict, total=False):
        key "family": Union[str, IPFamily]
        key "ip": str
        family: Union[str, IPFamily]
        ip: str


    class azure.mgmt.containerservice.types.MachineKubernetesProfile(TypedDict, total=False):
        key "artifactStreamingProfile": ForwardRef('AgentPoolArtifactStreamingProfile', module='types')
        key "currentOrchestratorVersion": str
        key "kubeletConfig": ForwardRef('KubeletConfig', module='types')
        key "kubeletDiskType": Union[str, KubeletDiskType]
        key "maxPods": int
        key "nodeName": str
        key "orchestratorVersion": str
        key "workloadRuntime": Union[str, WorkloadRuntime]
        artifact_streaming_profile: AgentPoolArtifactStreamingProfile
        current_orchestrator_version: str
        kubelet_config: KubeletConfig
        kubelet_disk_type: Union[str, KubeletDiskType]
        max_pods: int
        nodeInitializationTaints: list[str]
        nodeLabels: dict[str, str]
        nodeTaints: list[str]
        node_initialization_taints: list[str]
        node_labels: dict[str, str]
        node_name: str
        node_taints: list[str]
        orchestrator_version: str
        workload_runtime: Union[str, WorkloadRuntime]


    class azure.mgmt.containerservice.types.MachineNetworkProperties(TypedDict, total=False):
        key "enableNodePublicIP": bool
        key "nodePublicIPPrefixID": str
        key "podSubnetID": str
        key "vnetSubnetID": str
        enable_node_public_ip: bool
        ipAddresses: list[MachineIpAddress]
        ip_addresses: list[MachineIpAddress]
        nodePublicIPTags: list[IPTag]
        node_public_ip_prefix_id: str
        node_public_ip_tags: list[IPTag]
        pod_subnet_id: str
        vnet_subnet_id: str


    class azure.mgmt.containerservice.types.MachineOSProfile(TypedDict, total=False):
        key "enableFIPS": bool
        key "linuxProfile": ForwardRef('MachineOSProfileLinuxProfile', module='types')
        key "osDiskSizeGB": int
        key "osDiskType": Union[str, OSDiskType]
        key "osSKU": Union[str, OSSKU]
        key "osType": Union[str, OSType]
        key "windowsProfile": ForwardRef('AgentPoolWindowsProfile', module='types')
        enable_fips: bool
        linux_profile: MachineOSProfileLinuxProfile
        os_disk_size_gb: int
        os_disk_type: Union[str, OSDiskType]
        os_sku: Union[str, OSSKU]
        os_type: Union[str, OSType]
        windows_profile: AgentPoolWindowsProfile


    class azure.mgmt.containerservice.types.MachineOSProfileLinuxProfile(TypedDict, total=False):
        key "linuxOSConfig": ForwardRef('LinuxOSConfig', module='types')
        key "messageOfTheDay": str
        linux_os_config: LinuxOSConfig
        message_of_the_day: str


    class azure.mgmt.containerservice.types.MachineProperties(TypedDict, total=False):
        key "billing": ForwardRef('MachineBillingProfile', module='types')
        key "eTag": str
        key "evictionPolicy": Union[str, ScaleSetEvictionPolicy]
        key "hardware": ForwardRef('MachineHardwareProfile', module='types')
        key "kubernetes": ForwardRef('MachineKubernetesProfile', module='types')
        key "localDNSProfile": ForwardRef('LocalDNSProfile', module='types')
        key "mode": Union[str, AgentPoolMode]
        key "network": ForwardRef('MachineNetworkProperties', module='types')
        key "nodeImageVersion": str
        key "operatingSystem": ForwardRef('MachineOSProfile', module='types')
        key "priority": Union[str, ScaleSetPriority]
        key "provisioningState": str
        key "resourceId": str
        key "security": ForwardRef('MachineSecurityProfile', module='types')
        key "status": ForwardRef('MachineStatus', module='types')
        billing: MachineBillingProfile
        e_tag: str
        eviction_policy: Union[str, ScaleSetEvictionPolicy]
        hardware: MachineHardwareProfile
        kubernetes: MachineKubernetesProfile
        local_dns_profile: LocalDNSProfile
        mode: Union[str, AgentPoolMode]
        network: MachineNetworkProperties
        node_image_version: str
        operating_system: MachineOSProfile
        priority: Union[str, ScaleSetPriority]
        provisioning_state: str
        resource_id: str
        security: MachineSecurityProfile
        status: MachineStatus
        tags: dict[str, str]


    class azure.mgmt.containerservice.types.MachineSecurityProfile(TypedDict, total=False):
        key "enableEncryptionAtHost": bool
        key "enableSecureBoot": bool
        key "enableVTPM": bool
        key "sshAccess": Union[str, AgentPoolSSHAccess]
        enable_encryption_at_host: bool
        enable_secure_boot: bool
        enable_vtpm: bool
        ssh_access: Union[str, AgentPoolSSHAccess]


    class azure.mgmt.containerservice.types.MachineStatus(TypedDict, total=False):
        key "creationTimestamp": str
        key "driftAction": Union[str, DriftAction]
        key "driftReason": str
        key "provisioningError": ForwardRef('ErrorDetail', module='types')
        key "vmState": Union[str, VmState]
        creation_timestamp: str
        drift_action: Union[str, DriftAction]
        drift_reason: str
        provisioning_error: ErrorDetail
        vm_state: Union[str, VmState]


    class azure.mgmt.containerservice.types.MaintenanceConfiguration(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('MaintenanceConfigurationProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: MaintenanceConfigurationProperties
        system_data: SystemData
        type: str


    class azure.mgmt.containerservice.types.MaintenanceConfigurationProperties(TypedDict, total=False):
        key "maintenanceWindow": ForwardRef('MaintenanceWindow', module='types')
        key "maintenanceWindowId": str
        maintenance_window: MaintenanceWindow
        maintenance_window_id: str
        notAllowedTime: list[TimeSpan]
        not_allowed_time: list[TimeSpan]
        timeInWeek: list[TimeInWeek]
        time_in_week: list[TimeInWeek]


    class azure.mgmt.containerservice.types.MaintenanceWindow(TypedDict, total=False):
        key "durationHours": Required[int]
        key "schedule": Required[Schedule]
        key "startDate": str
        key "startTime": Required[str]
        key "utcOffset": str
        duration_hours: int
        notAllowedDates: list[DateSpan]
        not_allowed_dates: list[DateSpan]
        schedule: Schedule
        start_date: str
        start_time: str
        utc_offset: str


    class azure.mgmt.containerservice.types.MaintenanceWindowResource(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('MaintenanceWindowResourceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: MaintenanceWindowResourceProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.containerservice.types.MaintenanceWindowResourceProperties(TypedDict, total=False):
        key "durationHours": Required[int]
        key "provisioningState": Union[str, ResourceProvisioningState]
        key "schedule": Required[Schedule]
        key "startDate": str
        key "startTime": Required[str]
        key "utcOffset": str
        duration_hours: int
        notAllowedDates: list[DateSpan]
        not_allowed_dates: list[DateSpan]
        provisioning_state: Union[str, ResourceProvisioningState]
        schedule: Schedule
        start_date: str
        start_time: str
        utc_offset: str


    class azure.mgmt.containerservice.types.ManagedCluster(TrackedResource):
        key "eTag": str
        key "extendedLocation": ForwardRef('ExtendedLocation', module='types')
        key "id": str
        key "identity": ForwardRef('ManagedClusterIdentity', module='types')
        key "kind": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('ManagedClusterProperties', module='types')
        key "sku": ForwardRef('ManagedClusterSKU', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        e_tag: str
        extended_location: ExtendedLocation
        id: str
        identity: ManagedClusterIdentity
        kind: str
        location: str
        name: str
        properties: ManagedClusterProperties
        sku: ManagedClusterSKU
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.containerservice.types.ManagedClusterAADProfile(TypedDict, total=False):
        key "clientAppID": str
        key "enableAzureRBAC": bool
        key "managed": bool
        key "serverAppID": str
        key "serverAppSecret": str
        key "tenantID": str
        adminGroupObjectIDs: list[str]
        admin_group_object_i_ds: list[str]
        client_app_id: str
        enable_azure_rbac: bool
        managed: bool
        server_app_id: str
        server_app_secret: str
        tenant_id: str


    class azure.mgmt.containerservice.types.ManagedClusterAIToolchainOperatorProfile(TypedDict, total=False):
        key "enabled": bool
        enabled: bool


    class azure.mgmt.containerservice.types.ManagedClusterAPIServerAccessProfile(TypedDict, total=False):
        key "disableRunCommand": bool
        key "enablePrivateCluster": bool
        key "enablePrivateClusterPublicFQDN": bool
        key "enableVnetIntegration": bool
        key "privateDNSZone": str
        key "subnetId": str
        authorizedIPRanges: list[str]
        authorized_ip_ranges: list[str]
        disable_run_command: bool
        enable_private_cluster: bool
        enable_private_cluster_public_fqdn: bool
        enable_vnet_integration: bool
        private_dns_zone: str
        subnet_id: str


    class azure.mgmt.containerservice.types.ManagedClusterAddonProfile(TypedDict, total=False):
        key "enabled": Required[bool]
        key "identity": ForwardRef('ManagedClusterAddonProfileIdentity', module='types')
        config: dict[str, str]
        enabled: bool
        identity: ManagedClusterAddonProfileIdentity


    class azure.mgmt.containerservice.types.ManagedClusterAddonProfileIdentity(UserAssignedIdentity):
        key "clientId": str
        key "objectId": str
        key "resourceId": str
        client_id: str
        object_id: str
        resource_id: str


    class azure.mgmt.containerservice.types.ManagedClusterAgentPoolProfile(ManagedClusterAgentPoolProfileProperties):
        key "artifactStreamingProfile": ForwardRef('AgentPoolArtifactStreamingProfile', module='types')
        key "capacityReservationGroupID": str
        key "count": int
        key "creationData": ForwardRef('CreationData', module='types')
        key "currentOrchestratorVersion": str
        key "eTag": str
        key "enableAutoScaling": bool
        key "enableEncryptionAtHost": bool
        key "enableFIPS": bool
        key "enableNodePublicIP": bool
        key "enableOSDiskFullCaching": bool
        key "enableUltraSSD": bool
        key "gatewayProfile": ForwardRef('AgentPoolGatewayProfile', module='types')
        key "gpuInstanceProfile": Union[str, GPUInstanceProfile]
        key "gpuProfile": ForwardRef('GPUProfile', module='types')
        key "hostGroupID": str
        key "kubeletConfig": ForwardRef('KubeletConfig', module='types')
        key "kubeletDiskType": Union[str, KubeletDiskType]
        key "linuxOSConfig": ForwardRef('LinuxOSConfig', module='types')
        key "localDNSProfile": ForwardRef('LocalDNSProfile', module='types')
        key "maxCount": int
        key "maxPods": int
        key "messageOfTheDay": str
        key "minCount": int
        key "mode": Union[str, AgentPoolMode]
        key "name": Required[str]
        key "networkProfile": ForwardRef('AgentPoolNetworkProfile', module='types')
        key "nodeImageVersion": str
        key "nodePublicIPPrefixID": str
        key "orchestratorVersion": str
        key "osDiskSizeGB": int
        key "osDiskType": Union[str, OSDiskType]
        key "osSKU": Union[str, OSSKU]
        key "osType": Union[str, OSType]
        key "podIPAllocationMode": Union[str, PodIPAllocationMode]
        key "podSubnetID": str
        key "powerState": ForwardRef('PowerState', module='types')
        key "preparedImageSpecificationProfile": ForwardRef('PreparedImageSpecificationProfile', module='types')
        key "provisioningState": str
        key "proximityPlacementGroupID": str
        key "scaleDownMode": Union[str, ScaleDownMode]
        key "scaleSetEvictionPolicy": Union[str, ScaleSetEvictionPolicy]
        key "scaleSetPriority": Union[str, ScaleSetPriority]
        key "securityProfile": ForwardRef('AgentPoolSecurityProfile', module='types')
        key "spotMaxPrice": float
        key "status": ForwardRef('AgentPoolStatus', module='types')
        key "type": Union[str, AgentPoolType]
        key "upgradeSettings": ForwardRef('AgentPoolUpgradeSettings', module='types')
        key "upgradeSettingsBlueGreen": ForwardRef('AgentPoolBlueGreenUpgradeSettings', module='types')
        key "upgradeStrategy": Union[str, UpgradeStrategy]
        key "virtualMachinesProfile": ForwardRef('VirtualMachinesProfile', module='types')
        key "vmSize": str
        key "vnetSubnetID": str
        key "windowsProfile": ForwardRef('AgentPoolWindowsProfile', module='types')
        key "workloadRuntime": Union[str, WorkloadRuntime]
        artifact_streaming_profile: AgentPoolArtifactStreamingProfile
        availabilityZones: list[str]
        availability_zones: list[str]
        capacity_reservation_group_id: str
        count: int
        creation_data: CreationData
        current_orchestrator_version: str
        e_tag: str
        enable_auto_scaling: bool
        enable_encryption_at_host: bool
        enable_fips: bool
        enable_node_public_ip: bool
        enable_os_disk_full_caching: bool
        enable_ultra_ssd: bool
        gateway_profile: AgentPoolGatewayProfile
        gpu_instance_profile: Union[str, GPUInstanceProfile]
        gpu_profile: GPUProfile
        host_group_id: str
        kubelet_config: KubeletConfig
        kubelet_disk_type: Union[str, KubeletDiskType]
        linux_os_config: LinuxOSConfig
        local_dns_profile: LocalDNSProfile
        max_count: int
        max_pods: int
        message_of_the_day: str
        min_count: int
        mode: Union[str, AgentPoolMode]
        name: str
        network_profile: AgentPoolNetworkProfile
        nodeInitializationTaints: list[str]
        nodeLabels: dict[str, str]
        nodeTaints: list[str]
        node_image_version: str
        node_initialization_taints: list[str]
        node_labels: dict[str, str]
        node_public_ip_prefix_id: str
        node_taints: list[str]
        orchestrator_version: str
        os_disk_size_gb: int
        os_disk_type: Union[str, OSDiskType]
        os_sku: Union[str, OSSKU]
        os_type: Union[str, OSType]
        pod_ip_allocation_mode: Union[str, PodIPAllocationMode]
        pod_subnet_id: str
        power_state: PowerState
        prepared_image_specification_profile: PreparedImageSpecificationProfile
        provisioning_state: str
        proximity_placement_group_id: str
        scale_down_mode: Union[str, ScaleDownMode]
        scale_set_eviction_policy: Union[str, ScaleSetEvictionPolicy]
        scale_set_priority: Union[str, ScaleSetPriority]
        security_profile: AgentPoolSecurityProfile
        spot_max_price: float
        status: AgentPoolStatus
        tags: dict[str, str]
        type: Union[str, AgentPoolType]
        upgrade_settings: AgentPoolUpgradeSettings
        upgrade_settings_blue_green: AgentPoolBlueGreenUpgradeSettings
        upgrade_strategy: Union[str, UpgradeStrategy]
        virtualMachineNodesStatus: list[VirtualMachineNodes]
        virtual_machine_nodes_status: list[VirtualMachineNodes]
        virtual_machines_profile: VirtualMachinesProfile
        vm_size: str
        vnet_subnet_id: str
        windows_profile: AgentPoolWindowsProfile
        workload_runtime: Union[str, WorkloadRuntime]


    class azure.mgmt.containerservice.types.ManagedClusterAgentPoolProfileProperties(TypedDict, total=False):
        key "artifactStreamingProfile": ForwardRef('AgentPoolArtifactStreamingProfile', module='types')
        key "capacityReservationGroupID": str
        key "count": int
        key "creationData": ForwardRef('CreationData', module='types')
        key "currentOrchestratorVersion": str
        key "eTag": str
        key "enableAutoScaling": bool
        key "enableEncryptionAtHost": bool
        key "enableFIPS": bool
        key "enableNodePublicIP": bool
        key "enableOSDiskFullCaching": bool
        key "enableUltraSSD": bool
        key "gatewayProfile": ForwardRef('AgentPoolGatewayProfile', module='types')
        key "gpuInstanceProfile": Union[str, GPUInstanceProfile]
        key "gpuProfile": ForwardRef('GPUProfile', module='types')
        key "hostGroupID": str
        key "kubeletConfig": ForwardRef('KubeletConfig', module='types')
        key "kubeletDiskType": Union[str, KubeletDiskType]
        key "linuxOSConfig": ForwardRef('LinuxOSConfig', module='types')
        key "localDNSProfile": ForwardRef('LocalDNSProfile', module='types')
        key "maxCount": int
        key "maxPods": int
        key "messageOfTheDay": str
        key "minCount": int
        key "mode": Union[str, AgentPoolMode]
        key "networkProfile": ForwardRef('AgentPoolNetworkProfile', module='types')
        key "nodeImageVersion": str
        key "nodePublicIPPrefixID": str
        key "orchestratorVersion": str
        key "osDiskSizeGB": int
        key "osDiskType": Union[str, OSDiskType]
        key "osSKU": Union[str, OSSKU]
        key "osType": Union[str, OSType]
        key "podIPAllocationMode": Union[str, PodIPAllocationMode]
        key "podSubnetID": str
        key "powerState": ForwardRef('PowerState', module='types')
        key "preparedImageSpecificationProfile": ForwardRef('PreparedImageSpecificationProfile', module='types')
        key "provisioningState": str
        key "proximityPlacementGroupID": str
        key "scaleDownMode": Union[str, ScaleDownMode]
        key "scaleSetEvictionPolicy": Union[str, ScaleSetEvictionPolicy]
        key "scaleSetPriority": Union[str, ScaleSetPriority]
        key "securityProfile": ForwardRef('AgentPoolSecurityProfile', module='types')
        key "spotMaxPrice": float
        key "status": ForwardRef('AgentPoolStatus', module='types')
        key "type": Union[str, AgentPoolType]
        key "upgradeSettings": ForwardRef('AgentPoolUpgradeSettings', module='types')
        key "upgradeSettingsBlueGreen": ForwardRef('AgentPoolBlueGreenUpgradeSettings', module='types')
        key "upgradeStrategy": Union[str, UpgradeStrategy]
        key "virtualMachinesProfile": ForwardRef('VirtualMachinesProfile', module='types')
        key "vmSize": str
        key "vnetSubnetID": str
        key "windowsProfile": ForwardRef('AgentPoolWindowsProfile', module='types')
        key "workloadRuntime": Union[str, WorkloadRuntime]
        artifact_streaming_profile: AgentPoolArtifactStreamingProfile
        availabilityZones: list[str]
        availability_zones: list[str]
        capacity_reservation_group_id: str
        count: int
        creation_data: CreationData
        current_orchestrator_version: str
        e_tag: str
        enable_auto_scaling: bool
        enable_encryption_at_host: bool
        enable_fips: bool
        enable_node_public_ip: bool
        enable_os_disk_full_caching: bool
        enable_ultra_ssd: bool
        gateway_profile: AgentPoolGatewayProfile
        gpu_instance_profile: Union[str, GPUInstanceProfile]
        gpu_profile: GPUProfile
        host_group_id: str
        kubelet_config: KubeletConfig
        kubelet_disk_type: Union[str, KubeletDiskType]
        linux_os_config: LinuxOSConfig
        local_dns_profile: LocalDNSProfile
        max_count: int
        max_pods: int
        message_of_the_day: str
        min_count: int
        mode: Union[str, AgentPoolMode]
        network_profile: AgentPoolNetworkProfile
        nodeInitializationTaints: list[str]
        nodeLabels: dict[str, str]
        nodeTaints: list[str]
        node_image_version: str
        node_initialization_taints: list[str]
        node_labels: dict[str, str]
        node_public_ip_prefix_id: str
        node_taints: list[str]
        orchestrator_version: str
        os_disk_size_gb: int
        os_disk_type: Union[str, OSDiskType]
        os_sku: Union[str, OSSKU]
        os_type: Union[str, OSType]
        pod_ip_allocation_mode: Union[str, PodIPAllocationMode]
        pod_subnet_id: str
        power_state: PowerState
        prepared_image_specification_profile: PreparedImageSpecificationProfile
        provisioning_state: str
        proximity_placement_group_id: str
        scale_down_mode: Union[str, ScaleDownMode]
        scale_set_eviction_policy: Union[str, ScaleSetEvictionPolicy]
        scale_set_priority: Union[str, ScaleSetPriority]
        security_profile: AgentPoolSecurityProfile
        spot_max_price: float
        status: AgentPoolStatus
        tags: dict[str, str]
        type: Union[str, AgentPoolType]
        upgrade_settings: AgentPoolUpgradeSettings
        upgrade_settings_blue_green: AgentPoolBlueGreenUpgradeSettings
        upgrade_strategy: Union[str, UpgradeStrategy]
        virtualMachineNodesStatus: list[VirtualMachineNodes]
        virtual_machine_nodes_status: list[VirtualMachineNodes]
        virtual_machines_profile: VirtualMachinesProfile
        vm_size: str
        vnet_subnet_id: str
        windows_profile: AgentPoolWindowsProfile
        workload_runtime: Union[str, WorkloadRuntime]


    class azure.mgmt.containerservice.types.ManagedClusterAppRoutingIstio(TypedDict, total=False):
        key "mode": Union[str, GatewayAPIIstioEnabled]
        mode: Union[str, GatewayAPIIstioEnabled]


    class azure.mgmt.containerservice.types.ManagedClusterAutoUpgradeProfile(TypedDict, total=False):
        key "nodeOSUpgradeChannel": Union[str, NodeOSUpgradeChannel]
        key "upgradeChannel": Union[str, UpgradeChannel]
        node_os_upgrade_channel: Union[str, NodeOSUpgradeChannel]
        upgrade_channel: Union[str, UpgradeChannel]


    class azure.mgmt.containerservice.types.ManagedClusterAzureMonitorProfile(TypedDict, total=False):
        key "appMonitoring": ForwardRef('ManagedClusterAzureMonitorProfileAppMonitoring', module='types')
        key "containerInsights": ForwardRef('ManagedClusterAzureMonitorProfileContainerInsights', module='types')
        key "metrics": ForwardRef('ManagedClusterAzureMonitorProfileMetrics', module='types')
        app_monitoring: ManagedClusterAzureMonitorProfileAppMonitoring
        container_insights: ManagedClusterAzureMonitorProfileContainerInsights
        metrics: ManagedClusterAzureMonitorProfileMetrics


    class azure.mgmt.containerservice.types.ManagedClusterAzureMonitorProfileAppMonitoring(TypedDict, total=False):
        key "autoInstrumentation": ForwardRef('ManagedClusterAzureMonitorProfileAppMonitoringAutoInstrumentation', module='types')
        key "openTelemetryLogsAndTraces": ForwardRef('ManagedClusterAzureMonitorProfileAppMonitoringOpenTelemetryLogsAndTraces', module='types')
        key "openTelemetryMetrics": ForwardRef('ManagedClusterAzureMonitorProfileAppMonitoringOpenTelemetryMetrics', module='types')
        auto_instrumentation: ManagedClusterAzureMonitorProfileAppMonitoringAutoInstrumentation
        open_telemetry_logs_and_traces: ManagedClusterAzureMonitorProfileAppMonitoringOpenTelemetryLogsAndTraces
        open_telemetry_metrics: ManagedClusterAzureMonitorProfileAppMonitoringOpenTelemetryMetrics


    class azure.mgmt.containerservice.types.ManagedClusterAzureMonitorProfileAppMonitoringAutoInstrumentation(TypedDict, total=False):
        key "enabled": bool
        enabled: bool


    class azure.mgmt.containerservice.types.ManagedClusterAzureMonitorProfileAppMonitoringOpenTelemetryLogsAndTraces(TypedDict, total=False):
        key "enabled": bool
        key "grpcPort": int
        key "httpPort": int
        enabled: bool
        grpc_port: int
        http_port: int


    class azure.mgmt.containerservice.types.ManagedClusterAzureMonitorProfileAppMonitoringOpenTelemetryMetrics(TypedDict, total=False):
        key "enabled": bool
        key "grpcPort": int
        key "httpPort": int
        enabled: bool
        grpc_port: int
        http_port: int


    class azure.mgmt.containerservice.types.ManagedClusterAzureMonitorProfileContainerInsights(TypedDict, total=False):
        key "containerNetworkLogs": Union[str, ContainerNetworkLogs]
        key "disableCustomMetrics": bool
        key "disablePrometheusMetricsScraping": bool
        key "enabled": bool
        key "logAnalyticsWorkspaceResourceId": str
        key "syslogPort": int
        container_network_logs: Union[str, ContainerNetworkLogs]
        disable_custom_metrics: bool
        disable_prometheus_metrics_scraping: bool
        enabled: bool
        log_analytics_workspace_resource_id: str
        syslog_port: int


    class azure.mgmt.containerservice.types.ManagedClusterAzureMonitorProfileKubeStateMetrics(TypedDict, total=False):
        key "metricAnnotationsAllowList": str
        key "metricLabelsAllowlist": str
        metric_annotations_allow_list: str
        metric_labels_allowlist: str


    class azure.mgmt.containerservice.types.ManagedClusterAzureMonitorProfileMetrics(TypedDict, total=False):
        key "controlPlane": ForwardRef('ManagedClusterAzureMonitorProfileMetricsControlPlane', module='types')
        key "enabled": Required[bool]
        key "kubeStateMetrics": ForwardRef('ManagedClusterAzureMonitorProfileKubeStateMetrics', module='types')
        control_plane: ManagedClusterAzureMonitorProfileMetricsControlPlane
        enabled: bool
        kube_state_metrics: ManagedClusterAzureMonitorProfileKubeStateMetrics


    class azure.mgmt.containerservice.types.ManagedClusterAzureMonitorProfileMetricsControlPlane(TypedDict, total=False):
        key "enabled": bool
        enabled: bool


    class azure.mgmt.containerservice.types.ManagedClusterBootstrapProfile(TypedDict, total=False):
        key "artifactSource": Union[str, ArtifactSource]
        key "containerRegistryId": str
        artifact_source: Union[str, ArtifactSource]
        container_registry_id: str


    class azure.mgmt.containerservice.types.ManagedClusterControlPlaneScalingProfile(TypedDict, total=False):
        key "scalingSize": Required[Union[str, ControlPlaneScalingSize]]
        scaling_size: Union[str, ControlPlaneScalingSize]


    class azure.mgmt.containerservice.types.ManagedClusterCostAnalysis(TypedDict, total=False):
        key "enabled": bool
        enabled: bool


    class azure.mgmt.containerservice.types.ManagedClusterHTTPProxyConfig(TypedDict, total=False):
        key "enabled": bool
        key "httpProxy": str
        key "httpsProxy": str
        key "trustedCa": str
        effectiveNoProxy: list[str]
        effective_no_proxy: list[str]
        enabled: bool
        http_proxy: str
        https_proxy: str
        noProxy: list[str]
        no_proxy: list[str]
        trusted_ca: str


    class azure.mgmt.containerservice.types.ManagedClusterHealthMonitorProfile(TypedDict, total=False):
        key "enableContinuousControlPlaneAndAddonMonitor": bool
        key "enableOnDemandMonitor": bool
        enable_continuous_control_plane_and_addon_monitor: bool
        enable_on_demand_monitor: bool


    class azure.mgmt.containerservice.types.ManagedClusterHostedSystemProfile(TypedDict, total=False):
        key "enabled": bool
        key "nodeSubnetID": str
        key "systemNodeSubnetID": str
        enabled: bool
        node_subnet_id: str
        system_node_subnet_id: str


    class azure.mgmt.containerservice.types.ManagedClusterIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Union[str, ResourceIdentityType]
        delegatedResources: dict[str, DelegatedResource]
        delegated_resources: dict[str, DelegatedResource]
        principal_id: str
        tenant_id: str
        type: Union[str, ResourceIdentityType]
        userAssignedIdentities: dict[str, ManagedServiceIdentityUserAssignedIdentitiesValue]
        user_assigned_identities: dict[str, ManagedServiceIdentityUserAssignedIdentitiesValue]


    class azure.mgmt.containerservice.types.ManagedClusterIngressDefaultDomainProfile(TypedDict, total=False):
        key "domainName": str
        key "enabled": bool
        domain_name: str
        enabled: bool


    class azure.mgmt.containerservice.types.ManagedClusterIngressProfile(TypedDict, total=False):
        key "applicationLoadBalancer": ForwardRef('ManagedClusterIngressProfileApplicationLoadBalancer', module='types')
        key "gatewayAPI": ForwardRef('ManagedClusterIngressProfileGatewayConfiguration', module='types')
        key "webAppRouting": ForwardRef('ManagedClusterIngressProfileWebAppRouting', module='types')
        application_load_balancer: ManagedClusterIngressProfileApplicationLoadBalancer
        gateway_api: ManagedClusterIngressProfileGatewayConfiguration
        web_app_routing: ManagedClusterIngressProfileWebAppRouting


    class azure.mgmt.containerservice.types.ManagedClusterIngressProfileApplicationLoadBalancer(TypedDict, total=False):
        key "enabled": bool
        key "identity": ForwardRef('UserAssignedIdentity', module='types')
        enabled: bool
        identity: UserAssignedIdentity


    class azure.mgmt.containerservice.types.ManagedClusterIngressProfileGatewayConfiguration(TypedDict, total=False):
        key "installation": Union[str, ManagedGatewayType]
        installation: Union[str, ManagedGatewayType]


    class azure.mgmt.containerservice.types.ManagedClusterIngressProfileNginx(TypedDict, total=False):
        key "defaultIngressControllerType": Union[str, NginxIngressControllerType]
        default_ingress_controller_type: Union[str, NginxIngressControllerType]


    class azure.mgmt.containerservice.types.ManagedClusterIngressProfileWebAppRouting(TypedDict, total=False):
        key "defaultDomain": ForwardRef('ManagedClusterIngressDefaultDomainProfile', module='types')
        key "enabled": bool
        key "gatewayAPIImplementations": ForwardRef('ManagedClusterWebAppRoutingGatewayAPIImplementations', module='types')
        key "identity": ForwardRef('UserAssignedIdentity', module='types')
        key "nginx": ForwardRef('ManagedClusterIngressProfileNginx', module='types')
        default_domain: ManagedClusterIngressDefaultDomainProfile
        dnsZoneResourceIds: list[str]
        dns_zone_resource_ids: list[str]
        enabled: bool
        gateway_api_implementations: ManagedClusterWebAppRoutingGatewayAPIImplementations
        identity: UserAssignedIdentity
        nginx: ManagedClusterIngressProfileNginx


    class azure.mgmt.containerservice.types.ManagedClusterLoadBalancerProfile(TypedDict, total=False):
        key "allocatedOutboundPorts": int
        key "backendPoolType": Union[str, BackendPoolType]
        key "clusterServiceLoadBalancerHealthProbeMode": Union[str, ClusterServiceLoadBalancerHealthProbeMode]
        key "enableMultipleStandardLoadBalancers": bool
        key "idleTimeoutInMinutes": int
        key "managedOutboundIPs": ForwardRef('ManagedClusterLoadBalancerProfileManagedOutboundIPs', module='types')
        key "outboundIPPrefixes": ForwardRef('ManagedClusterLoadBalancerProfileOutboundIPPrefixes', module='types')
        key "outboundIPs": ForwardRef('ManagedClusterLoadBalancerProfileOutboundIPs', module='types')
        allocated_outbound_ports: int
        backend_pool_type: Union[str, BackendPoolType]
        cluster_service_load_balancer_health_probe_mode: Union[str, ClusterServiceLoadBalancerHealthProbeMode]
        effectiveOutboundIPs: list[ResourceReference]
        effective_outbound_i_ps: list[ResourceReference]
        enable_multiple_standard_load_balancers: bool
        idle_timeout_in_minutes: int
        managed_outbound_i_ps: ManagedClusterLoadBalancerProfileManagedOutboundIPs
        outbound_i_ps: ManagedClusterLoadBalancerProfileOutboundIPs
        outbound_ip_prefixes: ManagedClusterLoadBalancerProfileOutboundIPPrefixes


    class azure.mgmt.containerservice.types.ManagedClusterLoadBalancerProfileManagedOutboundIPs(TypedDict, total=False):
        key "count": int
        key "countIPv6": int
        count: int
        count_ipv6: int


    class azure.mgmt.containerservice.types.ManagedClusterLoadBalancerProfileOutboundIPPrefixes(TypedDict, total=False):
        publicIPPrefixes: list[ResourceReference]
        public_ip_prefixes: list[ResourceReference]


    class azure.mgmt.containerservice.types.ManagedClusterLoadBalancerProfileOutboundIPs(TypedDict, total=False):
        publicIPs: list[ResourceReference]
        public_i_ps: list[ResourceReference]


    class azure.mgmt.containerservice.types.ManagedClusterManagedOutboundIPProfile(TypedDict, total=False):
        key "count": int
        key "countIPv6": int
        count: int
        count_i_pv6: int


    class azure.mgmt.containerservice.types.ManagedClusterMetricsProfile(TypedDict, total=False):
        key "costAnalysis": ForwardRef('ManagedClusterCostAnalysis', module='types')
        cost_analysis: ManagedClusterCostAnalysis


    class azure.mgmt.containerservice.types.ManagedClusterNATGatewayProfile(TypedDict, total=False):
        key "idleTimeoutInMinutes": int
        key "managedOutboundIPProfile": ForwardRef('ManagedClusterManagedOutboundIPProfile', module='types')
        key "outboundIPPrefixes": ForwardRef('ManagedClusterNATGatewayProfileOutboundIpPrefixes', module='types')
        key "outboundIPs": ForwardRef('ManagedClusterNATGatewayProfileOutboundIPs', module='types')
        effectiveOutboundIPs: list[ResourceReference]
        effective_outbound_i_ps: list[ResourceReference]
        idle_timeout_in_minutes: int
        managed_outbound_ip_profile: ManagedClusterManagedOutboundIPProfile
        outbound_i_ps: ManagedClusterNATGatewayProfileOutboundIPs
        outbound_ip_prefixes: ManagedClusterNATGatewayProfileOutboundIpPrefixes


    class azure.mgmt.containerservice.types.ManagedClusterNATGatewayProfileOutboundIPs(TypedDict, total=False):
        publicIPs: list[str]
        public_i_ps: list[str]


    class azure.mgmt.containerservice.types.ManagedClusterNATGatewayProfileOutboundIpPrefixes(TypedDict, total=False):
        publicIPPrefixes: list[str]
        public_ip_prefixes: list[str]


    class azure.mgmt.containerservice.types.ManagedClusterNodeProvisioningProfile(TypedDict, total=False):
        key "defaultNodePools": Union[str, NodeProvisioningDefaultNodePools]
        key "mode": Union[str, NodeProvisioningMode]
        default_node_pools: Union[str, NodeProvisioningDefaultNodePools]
        mode: Union[str, NodeProvisioningMode]


    class azure.mgmt.containerservice.types.ManagedClusterNodeResourceGroupProfile(TypedDict, total=False):
        key "restrictionLevel": Union[str, RestrictionLevel]
        restriction_level: Union[str, RestrictionLevel]


    class azure.mgmt.containerservice.types.ManagedClusterOIDCIssuerProfile(TypedDict, total=False):
        key "enabled": bool
        key "issuerURL": str
        enabled: bool
        issuer_url: str


    class azure.mgmt.containerservice.types.ManagedClusterPodIdentity(TypedDict, total=False):
        key "bindingSelector": str
        key "identity": Required[UserAssignedIdentity]
        key "name": Required[str]
        key "namespace": Required[str]
        key "provisioningInfo": ForwardRef('ManagedClusterPodIdentityProvisioningInfo', module='types')
        key "provisioningState": Union[str, ManagedClusterPodIdentityProvisioningState]
        binding_selector: str
        identity: UserAssignedIdentity
        name: str
        namespace: str
        provisioning_info: ManagedClusterPodIdentityProvisioningInfo
        provisioning_state: Union[str, ManagedClusterPodIdentityProvisioningState]


    class azure.mgmt.containerservice.types.ManagedClusterPodIdentityException(TypedDict, total=False):
        key "name": Required[str]
        key "namespace": Required[str]
        key "podLabels": Required[dict[str, str]]
        name: str
        namespace: str
        pod_labels: dict[str, str]


    class azure.mgmt.containerservice.types.ManagedClusterPodIdentityProfile(TypedDict, total=False):
        key "allowNetworkPluginKubenet": bool
        key "enabled": bool
        allow_network_plugin_kubenet: bool
        enabled: bool
        userAssignedIdentities: list[ManagedClusterPodIdentity]
        userAssignedIdentityExceptions: list[ManagedClusterPodIdentityException]
        user_assigned_identities: list[ManagedClusterPodIdentity]
        user_assigned_identity_exceptions: list[ManagedClusterPodIdentityException]


    class azure.mgmt.containerservice.types.ManagedClusterPodIdentityProvisioningError(TypedDict, total=False):
        key "error": ForwardRef('ManagedClusterPodIdentityProvisioningErrorBody', module='types')
        error: ManagedClusterPodIdentityProvisioningErrorBody


    class azure.mgmt.containerservice.types.ManagedClusterPodIdentityProvisioningErrorBody(TypedDict, total=False):
        key "code": str
        key "message": str
        key "target": str
        code: str
        details: list[ManagedClusterPodIdentityProvisioningErrorBody]
        message: str
        target: str


    class azure.mgmt.containerservice.types.ManagedClusterPodIdentityProvisioningInfo(TypedDict, total=False):
        key "error": ForwardRef('ManagedClusterPodIdentityProvisioningError', module='types')
        error: ManagedClusterPodIdentityProvisioningError


    class azure.mgmt.containerservice.types.ManagedClusterProperties(TypedDict, total=False):
        key "aadProfile": ForwardRef('ManagedClusterAADProfile', module='types')
        key "aiToolchainOperatorProfile": ForwardRef('ManagedClusterAIToolchainOperatorProfile', module='types')
        key "apiServerAccessProfile": ForwardRef('ManagedClusterAPIServerAccessProfile', module='types')
        key "autoScalerProfile": ForwardRef('ManagedClusterPropertiesAutoScalerProfile', module='types')
        key "autoUpgradeProfile": ForwardRef('ManagedClusterAutoUpgradeProfile', module='types')
        key "azureMonitorProfile": ForwardRef('ManagedClusterAzureMonitorProfile', module='types')
        key "azurePortalFQDN": str
        key "bootstrapProfile": ForwardRef('ManagedClusterBootstrapProfile', module='types')
        key "controlPlaneScalingProfile": ForwardRef('ManagedClusterControlPlaneScalingProfile', module='types')
        key "creationData": ForwardRef('CreationData', module='types')
        key "currentKubernetesVersion": str
        key "disableLocalAccounts": bool
        key "diskEncryptionSetID": str
        key "dnsPrefix": str
        key "enableFIPS": bool
        key "enableNamespaceResources": bool
        key "enableRBAC": bool
        key "fqdn": str
        key "fqdnSubdomain": str
        key "healthMonitorProfile": ForwardRef('ManagedClusterHealthMonitorProfile', module='types')
        key "hostedSystemProfile": ForwardRef('ManagedClusterHostedSystemProfile', module='types')
        key "httpProxyConfig": ForwardRef('ManagedClusterHTTPProxyConfig', module='types')
        key "ingressProfile": ForwardRef('ManagedClusterIngressProfile', module='types')
        key "kubernetesVersion": str
        key "linuxProfile": ForwardRef('ContainerServiceLinuxProfile', module='types')
        key "maxAgentPools": int
        key "metricsProfile": ForwardRef('ManagedClusterMetricsProfile', module='types')
        key "networkProfile": ForwardRef('ContainerServiceNetworkProfile', module='types')
        key "nodeDisruptionProfile": ForwardRef('NodeDisruptionProfile', module='types')
        key "nodeProvisioningProfile": ForwardRef('ManagedClusterNodeProvisioningProfile', module='types')
        key "nodeResourceGroup": str
        key "nodeResourceGroupProfile": ForwardRef('ManagedClusterNodeResourceGroupProfile', module='types')
        key "oidcIssuerProfile": ForwardRef('ManagedClusterOIDCIssuerProfile', module='types')
        key "podIdentityProfile": ForwardRef('ManagedClusterPodIdentityProfile', module='types')
        key "powerState": ForwardRef('PowerState', module='types')
        key "privateFQDN": str
        key "provisioningState": str
        key "publicNetworkAccess": Union[str, PublicNetworkAccess]
        key "resourceUID": str
        key "schedulerProfile": ForwardRef('SchedulerProfile', module='types')
        key "securityProfile": ForwardRef('ManagedClusterSecurityProfile', module='types')
        key "serviceMeshProfile": ForwardRef('ServiceMeshProfile', module='types')
        key "servicePrincipalProfile": ForwardRef('ManagedClusterServicePrincipalProfile', module='types')
        key "status": ForwardRef('ManagedClusterStatus', module='types')
        key "storageProfile": ForwardRef('ManagedClusterStorageProfile', module='types')
        key "supportPlan": Union[str, KubernetesSupportPlan]
        key "upgradeSettings": ForwardRef('ClusterUpgradeSettings', module='types')
        key "windowsProfile": ForwardRef('ManagedClusterWindowsProfile', module='types')
        key "workloadAutoScalerProfile": ForwardRef('ManagedClusterWorkloadAutoScalerProfile', module='types')
        aad_profile: ManagedClusterAADProfile
        addonProfiles: dict[str, ManagedClusterAddonProfile]
        addon_profiles: dict[str, ManagedClusterAddonProfile]
        agentPoolProfiles: list[ManagedClusterAgentPoolProfile]
        agent_pool_profiles: list[ManagedClusterAgentPoolProfile]
        ai_toolchain_operator_profile: ManagedClusterAIToolchainOperatorProfile
        api_server_access_profile: ManagedClusterAPIServerAccessProfile
        auto_scaler_profile: ManagedClusterPropertiesAutoScalerProfile
        auto_upgrade_profile: ManagedClusterAutoUpgradeProfile
        azure_monitor_profile: ManagedClusterAzureMonitorProfile
        azure_portal_fqdn: str
        bootstrap_profile: ManagedClusterBootstrapProfile
        control_plane_scaling_profile: ManagedClusterControlPlaneScalingProfile
        creation_data: CreationData
        current_kubernetes_version: str
        disable_local_accounts: bool
        disk_encryption_set_id: str
        dns_prefix: str
        enable_fips: bool
        enable_namespace_resources: bool
        enable_rbac: bool
        fqdn: str
        fqdn_subdomain: str
        health_monitor_profile: ManagedClusterHealthMonitorProfile
        hosted_system_profile: ManagedClusterHostedSystemProfile
        http_proxy_config: ManagedClusterHTTPProxyConfig
        identityProfile: dict[str, UserAssignedIdentity]
        identity_profile: dict[str, UserAssignedIdentity]
        ingress_profile: ManagedClusterIngressProfile
        kubernetes_version: str
        linux_profile: ContainerServiceLinuxProfile
        max_agent_pools: int
        metrics_profile: ManagedClusterMetricsProfile
        network_profile: ContainerServiceNetworkProfile
        node_disruption_profile: NodeDisruptionProfile
        node_provisioning_profile: ManagedClusterNodeProvisioningProfile
        node_resource_group: str
        node_resource_group_profile: ManagedClusterNodeResourceGroupProfile
        oidc_issuer_profile: ManagedClusterOIDCIssuerProfile
        pod_identity_profile: ManagedClusterPodIdentityProfile
        power_state: PowerState
        privateLinkResources: list[PrivateLinkResource]
        private_fqdn: str
        private_link_resources: list[PrivateLinkResource]
        provisioning_state: str
        public_network_access: Union[str, PublicNetworkAccess]
        resource_uid: str
        scheduler_profile: SchedulerProfile
        security_profile: ManagedClusterSecurityProfile
        service_mesh_profile: ServiceMeshProfile
        service_principal_profile: ManagedClusterServicePrincipalProfile
        status: ManagedClusterStatus
        storage_profile: ManagedClusterStorageProfile
        support_plan: Union[str, KubernetesSupportPlan]
        upgrade_settings: ClusterUpgradeSettings
        windows_profile: ManagedClusterWindowsProfile
        workload_auto_scaler_profile: ManagedClusterWorkloadAutoScalerProfile


    class azure.mgmt.containerservice.types.ManagedClusterPropertiesAutoScalerProfile(TypedDict):
        key "balance-similar-node-groups": str
        key "daemonset-eviction-for-empty-nodes": bool
        key "daemonset-eviction-for-occupied-nodes": bool
        key "expander": Union[str, Expander]
        key "ignore-daemonsets-utilization": bool
        key "max-empty-bulk-delete": str
        key "max-graceful-termination-sec": str
        key "max-node-provision-time": str
        key "max-total-unready-percentage": str
        key "new-pod-scale-up-delay": str
        key "ok-total-unready-count": str
        key "scale-down-delay-after-add": str
        key "scale-down-delay-after-delete": str
        key "scale-down-delay-after-failure": str
        key "scale-down-unneeded-time": str
        key "scale-down-unready-time": str
        key "scale-down-utilization-threshold": str
        key "scan-interval": str
        key "skip-nodes-with-local-storage": str
        key "skip-nodes-with-system-pods": str
        balance_similar_node_groups: str
        daemonset_eviction_for_empty_nodes: bool
        daemonset_eviction_for_occupied_nodes: bool
        expander: Union[str, Expander]
        ignore_daemonsets_utilization: bool
        max_empty_bulk_delete: str
        max_graceful_termination_sec: str
        max_node_provision_time: str
        max_total_unready_percentage: str
        new_pod_scale_up_delay: str
        ok_total_unready_count: str
        scale_down_delay_after_add: str
        scale_down_delay_after_delete: str
        scale_down_delay_after_failure: str
        scale_down_unneeded_time: str
        scale_down_unready_time: str
        scale_down_utilization_threshold: str
        scan_interval: str
        skip_nodes_with_local_storage: str
        skip_nodes_with_system_pods: str


    class azure.mgmt.containerservice.types.ManagedClusterPropertiesForSnapshot(TypedDict, total=False):
        key "enableRbac": bool
        key "kubernetesVersion": str
        key "networkProfile": ForwardRef('NetworkProfileForSnapshot', module='types')
        key "sku": ForwardRef('ManagedClusterSKU', module='types')
        enable_rbac: bool
        kubernetes_version: str
        network_profile: NetworkProfileForSnapshot
        sku: ManagedClusterSKU


    class azure.mgmt.containerservice.types.ManagedClusterSKU(TypedDict, total=False):
        key "name": Union[str, ManagedClusterSKUName]
        key "tier": Union[str, ManagedClusterSKUTier]
        name: Union[str, ManagedClusterSKUName]
        tier: Union[str, ManagedClusterSKUTier]


    class azure.mgmt.containerservice.types.ManagedClusterSecurityProfile(TypedDict, total=False):
        key "azureKeyVaultKms": ForwardRef('AzureKeyVaultKms', module='types')
        key "defender": ForwardRef('ManagedClusterSecurityProfileDefender', module='types')
        key "imageCleaner": ForwardRef('ManagedClusterSecurityProfileImageCleaner', module='types')
        key "imageIntegrity": ForwardRef('ManagedClusterSecurityProfileImageIntegrity', module='types')
        key "kubernetesResourceObjectEncryptionProfile": ForwardRef('KubernetesResourceObjectEncryptionProfile', module='types')
        key "nodeRestriction": ForwardRef('ManagedClusterSecurityProfileNodeRestriction', module='types')
        key "serviceAccountImagePullProfile": ForwardRef('ServiceAccountImagePullProfile', module='types')
        key "workloadIdentity": ForwardRef('ManagedClusterSecurityProfileWorkloadIdentity', module='types')
        azure_key_vault_kms: AzureKeyVaultKms
        customCATrustCertificates: list[str]
        custom_ca_trust_certificates: list[str]
        defender: ManagedClusterSecurityProfileDefender
        image_cleaner: ManagedClusterSecurityProfileImageCleaner
        image_integrity: ManagedClusterSecurityProfileImageIntegrity
        kubernetes_resource_object_encryption_profile: KubernetesResourceObjectEncryptionProfile
        node_restriction: ManagedClusterSecurityProfileNodeRestriction
        service_account_image_pull_profile: ServiceAccountImagePullProfile
        workload_identity: ManagedClusterSecurityProfileWorkloadIdentity


    class azure.mgmt.containerservice.types.ManagedClusterSecurityProfileDefender(TypedDict, total=False):
        key "logAnalyticsWorkspaceResourceId": str
        key "securityGating": ForwardRef('ManagedClusterSecurityProfileDefenderSecurityGating', module='types')
        key "securityMonitoring": ForwardRef('ManagedClusterSecurityProfileDefenderSecurityMonitoring', module='types')
        log_analytics_workspace_resource_id: str
        security_gating: ManagedClusterSecurityProfileDefenderSecurityGating
        security_monitoring: ManagedClusterSecurityProfileDefenderSecurityMonitoring


    class azure.mgmt.containerservice.types.ManagedClusterSecurityProfileDefenderSecurityGating(TypedDict, total=False):
        key "allowSecretAccess": bool
        key "enabled": bool
        allow_secret_access: bool
        enabled: bool
        identities: list[ManagedClusterSecurityProfileDefenderSecurityGatingIdentity]


    class azure.mgmt.containerservice.types.ManagedClusterSecurityProfileDefenderSecurityGatingIdentity(TypedDict, total=False):
        key "azureContainerRegistry": str
        key "identity": ForwardRef('UserAssignedIdentity', module='types')
        azure_container_registry: str
        identity: UserAssignedIdentity


    class azure.mgmt.containerservice.types.ManagedClusterSecurityProfileDefenderSecurityMonitoring(TypedDict, total=False):
        key "enabled": bool
        enabled: bool


    class azure.mgmt.containerservice.types.ManagedClusterSecurityProfileImageCleaner(TypedDict, total=False):
        key "enabled": bool
        key "intervalHours": int
        enabled: bool
        interval_hours: int


    class azure.mgmt.containerservice.types.ManagedClusterSecurityProfileImageIntegrity(TypedDict, total=False):
        key "enabled": bool
        enabled: bool


    class azure.mgmt.containerservice.types.ManagedClusterSecurityProfileNodeRestriction(TypedDict, total=False):
        key "enabled": bool
        enabled: bool


    class azure.mgmt.containerservice.types.ManagedClusterSecurityProfileWorkloadIdentity(TypedDict, total=False):
        key "enabled": bool
        enabled: bool


    class azure.mgmt.containerservice.types.ManagedClusterServicePrincipalProfile(TypedDict, total=False):
        key "clientId": Required[str]
        key "secret": str
        client_id: str
        secret: str


    class azure.mgmt.containerservice.types.ManagedClusterSnapshot(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('ManagedClusterSnapshotProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: ManagedClusterSnapshotProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.containerservice.types.ManagedClusterSnapshotProperties(TypedDict, total=False):
        key "creationData": ForwardRef('CreationData', module='types')
        key "managedClusterPropertiesReadOnly": ForwardRef('ManagedClusterPropertiesForSnapshot', module='types')
        key "snapshotType": Union[str, SnapshotType]
        creation_data: CreationData
        managed_cluster_properties_read_only: ManagedClusterPropertiesForSnapshot
        snapshot_type: Union[str, SnapshotType]


    class azure.mgmt.containerservice.types.ManagedClusterStaticEgressGatewayProfile(TypedDict, total=False):
        key "enabled": bool
        enabled: bool


    class azure.mgmt.containerservice.types.ManagedClusterStatus(TypedDict, total=False):
        key "provisioningError": ForwardRef('ErrorDetail', module='types')
        provisioning_error: ErrorDetail


    class azure.mgmt.containerservice.types.ManagedClusterStorageProfile(TypedDict, total=False):
        key "blobCSIDriver": ForwardRef('ManagedClusterStorageProfileBlobCSIDriver', module='types')
        key "diskCSIDriver": ForwardRef('ManagedClusterStorageProfileDiskCSIDriver', module='types')
        key "fileCSIDriver": ForwardRef('ManagedClusterStorageProfileFileCSIDriver', module='types')
        key "snapshotController": ForwardRef('ManagedClusterStorageProfileSnapshotController', module='types')
        blob_csi_driver: ManagedClusterStorageProfileBlobCSIDriver
        disk_csi_driver: ManagedClusterStorageProfileDiskCSIDriver
        file_csi_driver: ManagedClusterStorageProfileFileCSIDriver
        snapshot_controller: ManagedClusterStorageProfileSnapshotController


    class azure.mgmt.containerservice.types.ManagedClusterStorageProfileBlobCSIDriver(TypedDict, total=False):
        key "enabled": bool
        enabled: bool


    class azure.mgmt.containerservice.types.ManagedClusterStorageProfileDiskCSIDriver(TypedDict, total=False):
        key "enabled": bool
        enabled: bool


    class azure.mgmt.containerservice.types.ManagedClusterStorageProfileFileCSIDriver(TypedDict, total=False):
        key "enabled": bool
        enabled: bool


    class azure.mgmt.containerservice.types.ManagedClusterStorageProfileSnapshotController(TypedDict, total=False):
        key "enabled": bool
        enabled: bool


    class azure.mgmt.containerservice.types.ManagedClusterWebAppRoutingGatewayAPIImplementations(TypedDict, total=False):
        key "appRoutingIstio": ForwardRef('ManagedClusterAppRoutingIstio', module='types')
        app_routing_istio: ManagedClusterAppRoutingIstio


    class azure.mgmt.containerservice.types.ManagedClusterWindowsProfile(TypedDict, total=False):
        key "adminPassword": str
        key "adminUsername": Required[str]
        key "enableCSIProxy": bool
        key "gmsaProfile": ForwardRef('WindowsGmsaProfile', module='types')
        key "licenseType": Union[str, LicenseType]
        admin_password: str
        admin_username: str
        enable_csi_proxy: bool
        gmsa_profile: WindowsGmsaProfile
        license_type: Union[str, LicenseType]


    class azure.mgmt.containerservice.types.ManagedClusterWorkloadAutoScalerProfile(TypedDict, total=False):
        key "keda": ForwardRef('ManagedClusterWorkloadAutoScalerProfileKeda', module='types')
        key "verticalPodAutoscaler": ForwardRef('ManagedClusterWorkloadAutoScalerProfileVerticalPodAutoscaler', module='types')
        keda: ManagedClusterWorkloadAutoScalerProfileKeda
        vertical_pod_autoscaler: ManagedClusterWorkloadAutoScalerProfileVerticalPodAutoscaler


    class azure.mgmt.containerservice.types.ManagedClusterWorkloadAutoScalerProfileKeda(TypedDict, total=False):
        key "enabled": Required[bool]
        enabled: bool


    class azure.mgmt.containerservice.types.ManagedClusterWorkloadAutoScalerProfileVerticalPodAutoscaler(TypedDict, total=False):
        key "addonAutoscaling": Union[str, AddonAutoscaling]
        key "enabled": Required[bool]
        addon_autoscaling: Union[str, AddonAutoscaling]
        enabled: bool


    class azure.mgmt.containerservice.types.ManagedNamespace(TrackedResource):
        key "eTag": str
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('NamespaceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        e_tag: str
        id: str
        location: str
        name: str
        properties: NamespaceProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.containerservice.types.ManagedServiceIdentityUserAssignedIdentitiesValue(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        client_id: str
        principal_id: str


    class azure.mgmt.containerservice.types.ManualScaleProfile(TypedDict, total=False):
        key "count": int
        key "size": str
        count: int
        size: str


    class azure.mgmt.containerservice.types.MeshMembership(ProxyResource):
        key "eTag": str
        key "id": str
        key "managedBy": str
        key "name": str
        key "properties": ForwardRef('MeshMembershipProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        e_tag: str
        id: str
        managed_by: str
        name: str
        properties: MeshMembershipProperties
        system_data: SystemData
        type: str


    class azure.mgmt.containerservice.types.MeshMembershipPrivateConnectProfile(TypedDict, total=False):
        key "privateIpAddress": str
        key "subnetResourceId": str
        private_ip_address: str
        subnet_resource_id: str


    class azure.mgmt.containerservice.types.MeshMembershipProperties(TypedDict, total=False):
        key "managedMeshID": Required[str]
        key "privateConnectProfile": ForwardRef('MeshMembershipPrivateConnectProfile', module='types')
        key "provisioningState": Union[str, MeshMembershipProvisioningState]
        managed_mesh_id: str
        private_connect_profile: MeshMembershipPrivateConnectProfile
        provisioning_state: Union[str, MeshMembershipProvisioningState]


    class azure.mgmt.containerservice.types.NamespaceProperties(TypedDict, total=False):
        key "adoptionPolicy": Union[str, AdoptionPolicy]
        key "defaultNetworkPolicy": ForwardRef('NetworkPolicies', module='types')
        key "defaultResourceQuota": ForwardRef('ResourceQuota', module='types')
        key "deletePolicy": Union[str, DeletePolicy]
        key "portalFqdn": str
        key "provisioningState": Union[str, NamespaceProvisioningState]
        adoption_policy: Union[str, AdoptionPolicy]
        annotations: dict[str, str]
        default_network_policy: NetworkPolicies
        default_resource_quota: ResourceQuota
        delete_policy: Union[str, DeletePolicy]
        labels: dict[str, str]
        portal_fqdn: str
        provisioning_state: Union[str, NamespaceProvisioningState]


    class azure.mgmt.containerservice.types.NetworkPolicies(TypedDict, total=False):
        key "egress": Union[str, PolicyRule]
        key "ingress": Union[str, PolicyRule]
        egress: Union[str, PolicyRule]
        ingress: Union[str, PolicyRule]


    class azure.mgmt.containerservice.types.NetworkProfileForSnapshot(TypedDict, total=False):
        key "loadBalancerSku": Union[str, LoadBalancerSku]
        key "networkMode": Union[str, NetworkMode]
        key "networkPlugin": Union[str, NetworkPlugin]
        key "networkPluginMode": Union[str, NetworkPluginMode]
        key "networkPolicy": Union[str, NetworkPolicy]
        load_balancer_sku: Union[str, LoadBalancerSku]
        network_mode: Union[str, NetworkMode]
        network_plugin: Union[str, NetworkPlugin]
        network_plugin_mode: Union[str, NetworkPluginMode]
        network_policy: Union[str, NetworkPolicy]


    class azure.mgmt.containerservice.types.NodeDisruptionProfile(TypedDict, total=False):
        key "nodeDisruptionPolicy": Union[str, NodeDisruptionPolicy]
        node_disruption_policy: Union[str, NodeDisruptionPolicy]


    class azure.mgmt.containerservice.types.NvidiaGPUProfile(TypedDict, total=False):
        key "managementMode": Union[str, ManagementMode]
        key "migStrategy": Union[str, MigStrategy]
        management_mode: Union[str, ManagementMode]
        mig_strategy: Union[str, MigStrategy]


    class azure.mgmt.containerservice.types.PortRange(TypedDict, total=False):
        key "portEnd": int
        key "portStart": int
        key "protocol": Union[str, Protocol]
        port_end: int
        port_start: int
        protocol: Union[str, Protocol]


    class azure.mgmt.containerservice.types.PowerState(TypedDict, total=False):
        key "code": Union[str, Code]
        code: Union[str, Code]


    class azure.mgmt.containerservice.types.PreparedImageSpecificationProfile(TypedDict, total=False):
        key "preparedImageSpecificationId": str
        prepared_image_specification_id: str


    class azure.mgmt.containerservice.types.PrivateEndpoint(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.containerservice.types.PrivateEndpointConnection(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('PrivateEndpointConnectionProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: PrivateEndpointConnectionProperties
        system_data: SystemData
        type: str


    class azure.mgmt.containerservice.types.PrivateEndpointConnectionProperties(TypedDict, total=False):
        key "privateEndpoint": ForwardRef('PrivateEndpoint', module='types')
        key "privateLinkServiceConnectionState": Required[PrivateLinkServiceConnectionState]
        key "provisioningState": Union[str, PrivateEndpointConnectionProvisioningState]
        private_endpoint: PrivateEndpoint
        private_link_service_connection_state: PrivateLinkServiceConnectionState
        provisioning_state: Union[str, PrivateEndpointConnectionProvisioningState]


    class azure.mgmt.containerservice.types.PrivateLinkResource(TypedDict, total=False):
        key "groupId": str
        key "id": str
        key "name": str
        key "privateLinkServiceID": str
        key "type": str
        group_id: str
        id: str
        name: str
        private_link_service_id: str
        requiredMembers: list[str]
        required_members: list[str]
        type: str


    class azure.mgmt.containerservice.types.PrivateLinkServiceConnectionState(TypedDict, total=False):
        key "description": str
        key "status": Union[str, ConnectionStatus]
        description: str
        status: Union[str, ConnectionStatus]


    class azure.mgmt.containerservice.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.containerservice.types.RebalanceLoadBalancersRequestBody(TypedDict, total=False):
        loadBalancerNames: list[str]
        load_balancer_names: list[str]


    class azure.mgmt.containerservice.types.RelativeMonthlySchedule(TypedDict, total=False):
        key "dayOfWeek": Required[Union[str, WeekDay]]
        key "intervalMonths": Required[int]
        key "weekIndex": Required[Union[str, Type]]
        day_of_week: Union[str, WeekDay]
        interval_months: int
        week_index: Union[str, Type]


    class azure.mgmt.containerservice.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.containerservice.types.ResourceQuota(TypedDict, total=False):
        key "cpuLimit": str
        key "cpuRequest": str
        key "memoryLimit": str
        key "memoryRequest": str
        cpu_limit: str
        cpu_request: str
        memory_limit: str
        memory_request: str


    class azure.mgmt.containerservice.types.ResourceReference(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.containerservice.types.RunCommandRequest(TypedDict, total=False):
        key "clusterToken": str
        key "command": Required[str]
        key "context": str
        cluster_token: str
        command: str
        context: str


    class azure.mgmt.containerservice.types.ScaleProfile(TypedDict, total=False):
        autoscale: list[AutoScaleProfile]
        manual: list[ManualScaleProfile]


    class azure.mgmt.containerservice.types.Schedule(TypedDict, total=False):
        key "absoluteMonthly": ForwardRef('AbsoluteMonthlySchedule', module='types')
        key "daily": ForwardRef('DailySchedule', module='types')
        key "relativeMonthly": ForwardRef('RelativeMonthlySchedule', module='types')
        key "weekly": ForwardRef('WeeklySchedule', module='types')
        absolute_monthly: AbsoluteMonthlySchedule
        daily: DailySchedule
        relative_monthly: RelativeMonthlySchedule
        weekly: WeeklySchedule


    class azure.mgmt.containerservice.types.SchedulerInstanceProfile(TypedDict, total=False):
        key "schedulerConfigMode": Union[str, SchedulerConfigMode]
        scheduler_config_mode: Union[str, SchedulerConfigMode]


    class azure.mgmt.containerservice.types.SchedulerProfile(TypedDict, total=False):
        key "upstream": ForwardRef('SchedulerInstanceProfile', module='types')
        upstream: SchedulerInstanceProfile


    class azure.mgmt.containerservice.types.ServiceAccountImagePullProfile(TypedDict, total=False):
        key "defaultManagedIdentityId": str
        key "enabled": bool
        default_managed_identity_id: str
        enabled: bool


    class azure.mgmt.containerservice.types.ServiceMeshProfile(TypedDict, total=False):
        key "istio": ForwardRef('IstioServiceMesh', module='types')
        key "mode": Required[Union[str, ServiceMeshMode]]
        istio: IstioServiceMesh
        mode: Union[str, ServiceMeshMode]


    class azure.mgmt.containerservice.types.Snapshot(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('SnapshotProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: SnapshotProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.containerservice.types.SnapshotProperties(TypedDict, total=False):
        key "creationData": ForwardRef('CreationData', module='types')
        key "enableFIPS": bool
        key "kubernetesVersion": str
        key "nodeImageVersion": str
        key "osSku": Union[str, OSSKU]
        key "osType": Union[str, OSType]
        key "snapshotType": Union[str, SnapshotType]
        key "vmSize": str
        creation_data: CreationData
        enable_fips: bool
        kubernetes_version: str
        node_image_version: str
        os_sku: Union[str, OSSKU]
        os_type: Union[str, OSType]
        snapshot_type: Union[str, SnapshotType]
        vm_size: str


    class azure.mgmt.containerservice.types.SysctlConfig(TypedDict, total=False):
        key "fsAioMaxNr": int
        key "fsFileMax": int
        key "fsInotifyMaxUserWatches": int
        key "fsNrOpen": int
        key "kernelThreadsMax": int
        key "netCoreNetdevMaxBacklog": int
        key "netCoreOptmemMax": int
        key "netCoreRmemDefault": int
        key "netCoreRmemMax": int
        key "netCoreSomaxconn": int
        key "netCoreWmemDefault": int
        key "netCoreWmemMax": int
        key "netIpv4IpLocalPortRange": str
        key "netIpv4NeighDefaultGcThresh1": int
        key "netIpv4NeighDefaultGcThresh2": int
        key "netIpv4NeighDefaultGcThresh3": int
        key "netIpv4TcpFinTimeout": int
        key "netIpv4TcpKeepaliveProbes": int
        key "netIpv4TcpKeepaliveTime": int
        key "netIpv4TcpMaxSynBacklog": int
        key "netIpv4TcpMaxTwBuckets": int
        key "netIpv4TcpTwReuse": bool
        key "netIpv4TcpkeepaliveIntvl": int
        key "netNetfilterNfConntrackBuckets": int
        key "netNetfilterNfConntrackMax": int
        key "vmMaxMapCount": int
        key "vmSwappiness": int
        key "vmVfsCachePressure": int
        fs_aio_max_nr: int
        fs_file_max: int
        fs_inotify_max_user_watches: int
        fs_nr_open: int
        kernel_threads_max: int
        net_core_netdev_max_backlog: int
        net_core_optmem_max: int
        net_core_rmem_default: int
        net_core_rmem_max: int
        net_core_somaxconn: int
        net_core_wmem_default: int
        net_core_wmem_max: int
        net_ipv4_ip_local_port_range: str
        net_ipv4_neigh_default_gc_thresh1: int
        net_ipv4_neigh_default_gc_thresh2: int
        net_ipv4_neigh_default_gc_thresh3: int
        net_ipv4_tcp_fin_timeout: int
        net_ipv4_tcp_keepalive_probes: int
        net_ipv4_tcp_keepalive_time: int
        net_ipv4_tcp_max_syn_backlog: int
        net_ipv4_tcp_max_tw_buckets: int
        net_ipv4_tcp_tw_reuse: bool
        net_ipv4_tcpkeepalive_intvl: int
        net_netfilter_nf_conntrack_buckets: int
        net_netfilter_nf_conntrack_max: int
        vm_max_map_count: int
        vm_swappiness: int
        vm_vfs_cache_pressure: int


    class azure.mgmt.containerservice.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.containerservice.types.TagsObject(TypedDict, total=False):
        tags: dict[str, str]


    class azure.mgmt.containerservice.types.TimeInWeek(TypedDict, total=False):
        key "day": Union[str, WeekDay]
        day: Union[str, WeekDay]
        hourSlots: list[int]
        hour_slots: list[int]


    class azure.mgmt.containerservice.types.TimeSpan(TypedDict, total=False):
        key "end": str
        key "start": str
        end: str
        start: str


    class azure.mgmt.containerservice.types.TrackedResource(Resource):
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


    class azure.mgmt.containerservice.types.TrustedAccessRoleBinding(ProxyResource):
        key "id": str
        key "name": str
        key "properties": Required[TrustedAccessRoleBindingProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: TrustedAccessRoleBindingProperties
        system_data: SystemData
        type: str


    class azure.mgmt.containerservice.types.TrustedAccessRoleBindingProperties(TypedDict, total=False):
        key "provisioningState": Union[str, TrustedAccessRoleBindingProvisioningState]
        key "roles": Required[list[str]]
        key "sourceResourceId": Required[str]
        provisioning_state: Union[str, TrustedAccessRoleBindingProvisioningState]
        roles: list[str]
        source_resource_id: str


    class azure.mgmt.containerservice.types.UpgradeOverrideSettings(TypedDict, total=False):
        key "forceUpgrade": bool
        key "until": str
        force_upgrade: bool
        until: str


    class azure.mgmt.containerservice.types.UserAssignedIdentity(TypedDict, total=False):
        key "clientId": str
        key "objectId": str
        key "resourceId": str
        client_id: str
        object_id: str
        resource_id: str


    class azure.mgmt.containerservice.types.VirtualMachineNodes(TypedDict, total=False):
        key "count": int
        key "size": str
        count: int
        size: str


    class azure.mgmt.containerservice.types.VirtualMachinesProfile(TypedDict, total=False):
        key "scale": ForwardRef('ScaleProfile', module='types')
        scale: ScaleProfile


    class azure.mgmt.containerservice.types.WeeklySchedule(TypedDict, total=False):
        key "dayOfWeek": Required[Union[str, WeekDay]]
        key "intervalWeeks": Required[int]
        day_of_week: Union[str, WeekDay]
        interval_weeks: int


    class azure.mgmt.containerservice.types.WindowsGmsaProfile(TypedDict, total=False):
        key "dnsServer": str
        key "enabled": bool
        key "rootDomainName": str
        dns_server: str
        enabled: bool
        root_domain_name: str


```