```py
namespace azure.mgmt.appcontainers

    class azure.mgmt.appcontainers.ContainerAppsAPIClient(_ContainerAppsAPIClientOperationsMixin): implements ContextManager 
        available_environment_modes: AvailableEnvironmentModesOperations
        available_workload_profiles: AvailableWorkloadProfilesOperations
        billing_meters: BillingMetersOperations
        certificates: CertificatesOperations
        connected_environments: ConnectedEnvironmentsOperations
        connected_environments_certificates: ConnectedEnvironmentsCertificatesOperations
        connected_environments_dapr_components: ConnectedEnvironmentsDaprComponentsOperations
        connected_environments_storages: ConnectedEnvironmentsStoragesOperations
        container_app_private_endpoint_connections: ContainerAppPrivateEndpointConnectionsOperations
        container_app_private_link_resources: ContainerAppPrivateLinkResourcesOperations
        container_apps: ContainerAppsOperations
        container_apps_auth_configs: ContainerAppsAuthConfigsOperations
        container_apps_diagnostics: ContainerAppsDiagnosticsOperations
        container_apps_functions: ContainerAppsFunctionsOperations
        container_apps_label_history: ContainerAppsLabelHistoryOperations
        container_apps_revision_functions: ContainerAppsRevisionFunctionsOperations
        container_apps_revision_replicas: ContainerAppsRevisionReplicasOperations
        container_apps_revisions: ContainerAppsRevisionsOperations
        container_apps_session_pools: ContainerAppsSessionPoolsOperations
        container_apps_source_controls: ContainerAppsSourceControlsOperations
        dapr_component_resiliency_policies: DaprComponentResiliencyPoliciesOperations
        dapr_components: DaprComponentsOperations
        dot_net_components: DotNetComponentsOperations
        functions_extension: FunctionsExtensionOperations
        http_route_config: HttpRouteConfigOperations
        java_components: JavaComponentsOperations
        jobs: JobsOperations
        jobs_executions: JobsExecutionsOperations
        logic_apps: LogicAppsOperations
        maintenance_configurations: MaintenanceConfigurationsOperations
        managed_certificates: ManagedCertificatesOperations
        managed_environment_diagnostics: ManagedEnvironmentDiagnosticsOperations
        managed_environment_private_endpoint_connections: ManagedEnvironmentPrivateEndpointConnectionsOperations
        managed_environment_private_link_resources: ManagedEnvironmentPrivateLinkResourcesOperations
        managed_environment_usages: ManagedEnvironmentUsagesOperations
        managed_environments: ManagedEnvironmentsOperations
        managed_environments_diagnostics: ManagedEnvironmentsDiagnosticsOperations
        managed_environments_storages: ManagedEnvironmentsStoragesOperations
        namespaces: NamespacesOperations
        operations: Operations
        sandbox_groups: SandboxGroupsOperations
        usages: UsagesOperations
        vnet_connections: VnetConnectionsOperations

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

        @distributed_trace
        def get_custom_domain_verification_id(self, **kwargs: Any) -> str: ...

        @distributed_trace
        def job_execution(
                self, 
                resource_group_name: str, 
                job_name: str, 
                job_execution_name: str, 
                **kwargs: Any
            ) -> JobExecution: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


namespace azure.mgmt.appcontainers.aio

    class azure.mgmt.appcontainers.aio.ContainerAppsAPIClient(_ContainerAppsAPIClientOperationsMixin): implements AsyncContextManager 
        available_environment_modes: AvailableEnvironmentModesOperations
        available_workload_profiles: AvailableWorkloadProfilesOperations
        billing_meters: BillingMetersOperations
        certificates: CertificatesOperations
        connected_environments: ConnectedEnvironmentsOperations
        connected_environments_certificates: ConnectedEnvironmentsCertificatesOperations
        connected_environments_dapr_components: ConnectedEnvironmentsDaprComponentsOperations
        connected_environments_storages: ConnectedEnvironmentsStoragesOperations
        container_app_private_endpoint_connections: ContainerAppPrivateEndpointConnectionsOperations
        container_app_private_link_resources: ContainerAppPrivateLinkResourcesOperations
        container_apps: ContainerAppsOperations
        container_apps_auth_configs: ContainerAppsAuthConfigsOperations
        container_apps_diagnostics: ContainerAppsDiagnosticsOperations
        container_apps_functions: ContainerAppsFunctionsOperations
        container_apps_label_history: ContainerAppsLabelHistoryOperations
        container_apps_revision_functions: ContainerAppsRevisionFunctionsOperations
        container_apps_revision_replicas: ContainerAppsRevisionReplicasOperations
        container_apps_revisions: ContainerAppsRevisionsOperations
        container_apps_session_pools: ContainerAppsSessionPoolsOperations
        container_apps_source_controls: ContainerAppsSourceControlsOperations
        dapr_component_resiliency_policies: DaprComponentResiliencyPoliciesOperations
        dapr_components: DaprComponentsOperations
        dot_net_components: DotNetComponentsOperations
        functions_extension: FunctionsExtensionOperations
        http_route_config: HttpRouteConfigOperations
        java_components: JavaComponentsOperations
        jobs: JobsOperations
        jobs_executions: JobsExecutionsOperations
        logic_apps: LogicAppsOperations
        maintenance_configurations: MaintenanceConfigurationsOperations
        managed_certificates: ManagedCertificatesOperations
        managed_environment_diagnostics: ManagedEnvironmentDiagnosticsOperations
        managed_environment_private_endpoint_connections: ManagedEnvironmentPrivateEndpointConnectionsOperations
        managed_environment_private_link_resources: ManagedEnvironmentPrivateLinkResourcesOperations
        managed_environment_usages: ManagedEnvironmentUsagesOperations
        managed_environments: ManagedEnvironmentsOperations
        managed_environments_diagnostics: ManagedEnvironmentsDiagnosticsOperations
        managed_environments_storages: ManagedEnvironmentsStoragesOperations
        namespaces: NamespacesOperations
        operations: Operations
        sandbox_groups: SandboxGroupsOperations
        usages: UsagesOperations
        vnet_connections: VnetConnectionsOperations

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

        @distributed_trace_async
        async def get_custom_domain_verification_id(self, **kwargs: Any) -> str: ...

        @distributed_trace_async
        async def job_execution(
                self, 
                resource_group_name: str, 
                job_name: str, 
                job_execution_name: str, 
                **kwargs: Any
            ) -> JobExecution: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


namespace azure.mgmt.appcontainers.aio.operations

    class azure.mgmt.appcontainers.aio.operations.AvailableEnvironmentModesOperations:

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
            ) -> AsyncItemPaged[AvailableEnvironmentMode]: ...


    class azure.mgmt.appcontainers.aio.operations.AvailableWorkloadProfilesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AvailableWorkloadProfile]: ...


    class azure.mgmt.appcontainers.aio.operations.BillingMetersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                location: str, 
                **kwargs: Any
            ) -> BillingMeterCollection: ...


    class azure.mgmt.appcontainers.aio.operations.CertificatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                certificate_name: str, 
                certificate_envelope: Optional[Certificate] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Certificate: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                certificate_name: str, 
                certificate_envelope: Optional[Certificate] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Certificate: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                certificate_name: str, 
                certificate_envelope: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Certificate: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                certificate_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                certificate_name: str, 
                **kwargs: Any
            ) -> Certificate: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Certificate]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                certificate_name: str, 
                certificate_envelope: CertificatePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Certificate: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                certificate_name: str, 
                certificate_envelope: CertificatePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Certificate: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                certificate_name: str, 
                certificate_envelope: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Certificate: ...


    class azure.mgmt.appcontainers.aio.operations.ConnectedEnvironmentsCertificatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                certificate_name: str, 
                certificate_envelope: Optional[Certificate] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Certificate]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                certificate_name: str, 
                certificate_envelope: Optional[Certificate] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Certificate]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                certificate_name: str, 
                certificate_envelope: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Certificate]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                certificate_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                certificate_name: str, 
                certificate_envelope: CertificatePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Certificate]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                certificate_name: str, 
                certificate_envelope: CertificatePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Certificate]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                certificate_name: str, 
                certificate_envelope: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Certificate]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                certificate_name: str, 
                **kwargs: Any
            ) -> Certificate: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Certificate]: ...


    class azure.mgmt.appcontainers.aio.operations.ConnectedEnvironmentsDaprComponentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                component_name: str, 
                dapr_component_envelope: DaprComponent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DaprComponent]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                component_name: str, 
                dapr_component_envelope: DaprComponent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DaprComponent]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                component_name: str, 
                dapr_component_envelope: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DaprComponent]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                component_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                component_name: str, 
                **kwargs: Any
            ) -> DaprComponent: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DaprComponent]: ...

        @distributed_trace_async
        async def list_secrets(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                component_name: str, 
                **kwargs: Any
            ) -> DaprSecretsCollection: ...


    class azure.mgmt.appcontainers.aio.operations.ConnectedEnvironmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                environment_envelope: ConnectedEnvironment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ConnectedEnvironment]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                environment_envelope: ConnectedEnvironment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ConnectedEnvironment]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                environment_envelope: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ConnectedEnvironment]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def check_name_availability(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                check_name_availability_request: CheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        async def check_name_availability(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                check_name_availability_request: CheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        async def check_name_availability(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                check_name_availability_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                **kwargs: Any
            ) -> ConnectedEnvironment: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ConnectedEnvironment]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[ConnectedEnvironment]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                environment_envelope: ConnectedEnvironmentPatchResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectedEnvironment: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                environment_envelope: ConnectedEnvironmentPatchResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectedEnvironment: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                environment_envelope: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectedEnvironment: ...


    class azure.mgmt.appcontainers.aio.operations.ConnectedEnvironmentsStoragesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                storage_name: str, 
                storage_envelope: ConnectedEnvironmentStorage, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ConnectedEnvironmentStorage]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                storage_name: str, 
                storage_envelope: ConnectedEnvironmentStorage, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ConnectedEnvironmentStorage]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                storage_name: str, 
                storage_envelope: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ConnectedEnvironmentStorage]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                storage_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                storage_name: str, 
                **kwargs: Any
            ) -> ConnectedEnvironmentStorage: ...

        @distributed_trace_async
        async def list(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                **kwargs: Any
            ) -> ConnectedEnvironmentStoragesCollection: ...


    class azure.mgmt.appcontainers.aio.operations.ContainerAppPrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                private_endpoint_connection_name: str, 
                private_endpoint_connection_envelope: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                private_endpoint_connection_name: str, 
                private_endpoint_connection_envelope: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                private_endpoint_connection_name: str, 
                private_endpoint_connection_envelope: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-07-01', params_added_on={'2026-07-01': ['api_version', 'subscription_id', 'resource_group_name', 'container_app_name', 'private_endpoint_connection_name']}, api_versions_list=['2026-07-01'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-07-01', params_added_on={'2026-07-01': ['api_version', 'subscription_id', 'resource_group_name', 'container_app_name', 'private_endpoint_connection_name', 'accept']}, api_versions_list=['2026-07-01'])
        async def get(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-01', params_added_on={'2026-07-01': ['api_version', 'subscription_id', 'resource_group_name', 'container_app_name', 'accept']}, api_versions_list=['2026-07-01'])
        def list(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateEndpointConnection]: ...


    class azure.mgmt.appcontainers.aio.operations.ContainerAppPrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-07-01', params_added_on={'2026-07-01': ['api_version', 'subscription_id', 'resource_group_name', 'container_app_name', 'private_link_resource_name', 'accept']}, api_versions_list=['2026-07-01'])
        async def get(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                private_link_resource_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-01', params_added_on={'2026-07-01': ['api_version', 'subscription_id', 'resource_group_name', 'container_app_name', 'accept']}, api_versions_list=['2026-07-01'])
        def list(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateLinkResource]: ...


    class azure.mgmt.appcontainers.aio.operations.ContainerAppsAuthConfigsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                auth_config_name: str, 
                auth_config_envelope: AuthConfig, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AuthConfig: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                auth_config_name: str, 
                auth_config_envelope: AuthConfig, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AuthConfig: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                auth_config_name: str, 
                auth_config_envelope: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AuthConfig: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                auth_config_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                auth_config_name: str, 
                **kwargs: Any
            ) -> AuthConfig: ...

        @distributed_trace
        def list_by_container_app(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AuthConfig]: ...


    class azure.mgmt.appcontainers.aio.operations.ContainerAppsDiagnosticsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get_detector(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                detector_name: str, 
                **kwargs: Any
            ) -> Diagnostics: ...

        @distributed_trace_async
        async def get_revision(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                revision_name: str, 
                **kwargs: Any
            ) -> Revision: ...

        @distributed_trace_async
        async def get_root(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                **kwargs: Any
            ) -> ContainerApp: ...

        @distributed_trace
        def list_detectors(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Diagnostics]: ...

        @distributed_trace
        def list_revisions(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Revision]: ...


    class azure.mgmt.appcontainers.aio.operations.ContainerAppsFunctionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-03-02-preview', params_added_on={'2026-03-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'container_app_name', 'function_name', 'accept']}, api_versions_list=['2026-03-02-preview', '2026-07-01'])
        async def get(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                function_name: str, 
                **kwargs: Any
            ) -> ContainerAppsFunction: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-02-preview', params_added_on={'2026-03-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'container_app_name', 'accept']}, api_versions_list=['2026-03-02-preview', '2026-07-01'])
        def list(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ContainerAppsFunction]: ...


    class azure.mgmt.appcontainers.aio.operations.ContainerAppsLabelHistoryOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-07-01', params_added_on={'2026-07-01': ['api_version', 'subscription_id', 'resource_group_name', 'container_app_name', 'label_name']}, api_versions_list=['2026-07-01'])
        async def delete_label_history(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                label_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-07-01', params_added_on={'2026-07-01': ['api_version', 'subscription_id', 'resource_group_name', 'container_app_name', 'label_name', 'accept']}, api_versions_list=['2026-07-01'])
        async def get_label_history(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                label_name: str, 
                **kwargs: Any
            ) -> LabelHistory: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-01', params_added_on={'2026-07-01': ['api_version', 'subscription_id', 'resource_group_name', 'container_app_name', 'filter', 'accept']}, api_versions_list=['2026-07-01'])
        def list_label_history(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[LabelHistory]: ...


    class azure.mgmt.appcontainers.aio.operations.ContainerAppsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                container_app_envelope: ContainerApp, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ContainerApp]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                container_app_envelope: ContainerApp, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ContainerApp]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                container_app_envelope: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ContainerApp]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_start(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ContainerApp]: ...

        @distributed_trace_async
        async def begin_stop(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ContainerApp]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                container_app_envelope: ContainerApp, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ContainerApp]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                container_app_envelope: ContainerApp, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ContainerApp]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                container_app_envelope: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ContainerApp]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                **kwargs: Any
            ) -> ContainerApp: ...

        @distributed_trace_async
        async def get_auth_token(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                **kwargs: Any
            ) -> ContainerAppAuthToken: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ContainerApp]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[ContainerApp]: ...

        @distributed_trace_async
        async def list_custom_host_name_analysis(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                *, 
                custom_hostname: Optional[str] = ..., 
                **kwargs: Any
            ) -> CustomHostnameAnalysisResult: ...

        @distributed_trace_async
        async def list_secrets(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                **kwargs: Any
            ) -> SecretsCollection: ...


    class azure.mgmt.appcontainers.aio.operations.ContainerAppsRevisionFunctionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                revision_name: str, 
                function_name: str, 
                **kwargs: Any
            ) -> ContainerAppsFunction: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                revision_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ContainerAppsFunction]: ...


    class azure.mgmt.appcontainers.aio.operations.ContainerAppsRevisionReplicasOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get_replica(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                revision_name: str, 
                replica_name: str, 
                **kwargs: Any
            ) -> Replica: ...

        @distributed_trace_async
        async def list_replicas(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                revision_name: str, 
                **kwargs: Any
            ) -> ReplicaCollection: ...


    class azure.mgmt.appcontainers.aio.operations.ContainerAppsRevisionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def activate_revision(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                revision_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def deactivate_revision(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                revision_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get_revision(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                revision_name: str, 
                **kwargs: Any
            ) -> Revision: ...

        @distributed_trace
        def list_revisions(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Revision]: ...

        @distributed_trace_async
        async def restart_revision(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                revision_name: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.appcontainers.aio.operations.ContainerAppsSessionPoolsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                session_pool_name: str, 
                session_pool_envelope: SessionPool, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SessionPool]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                session_pool_name: str, 
                session_pool_envelope: SessionPool, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SessionPool]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                session_pool_name: str, 
                session_pool_envelope: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SessionPool]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                session_pool_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                session_pool_name: str, 
                session_pool_envelope: SessionPoolUpdatableProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SessionPool]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                session_pool_name: str, 
                session_pool_envelope: SessionPoolUpdatableProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SessionPool]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                session_pool_name: str, 
                session_pool_envelope: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SessionPool]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                session_pool_name: str, 
                **kwargs: Any
            ) -> SessionPool: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SessionPool]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[SessionPool]: ...


    class azure.mgmt.appcontainers.aio.operations.ContainerAppsSourceControlsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                source_control_name: str, 
                source_control_envelope: SourceControl, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SourceControl]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                source_control_name: str, 
                source_control_envelope: SourceControl, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SourceControl]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                source_control_name: str, 
                source_control_envelope: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SourceControl]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                source_control_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                source_control_name: str, 
                **kwargs: Any
            ) -> SourceControl: ...

        @distributed_trace
        def list_by_container_app(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SourceControl]: ...


    class azure.mgmt.appcontainers.aio.operations.DaprComponentResiliencyPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                component_name: str, 
                name: str, 
                dapr_component_resiliency_policy_envelope: DaprComponentResiliencyPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DaprComponentResiliencyPolicy: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                component_name: str, 
                name: str, 
                dapr_component_resiliency_policy_envelope: DaprComponentResiliencyPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DaprComponentResiliencyPolicy: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                component_name: str, 
                name: str, 
                dapr_component_resiliency_policy_envelope: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DaprComponentResiliencyPolicy: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-07-01', params_added_on={'2026-07-01': ['api_version', 'subscription_id', 'resource_group_name', 'environment_name', 'component_name', 'name']}, api_versions_list=['2026-07-01'])
        async def delete(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                component_name: str, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-07-01', params_added_on={'2026-07-01': ['api_version', 'subscription_id', 'resource_group_name', 'environment_name', 'component_name', 'name', 'accept']}, api_versions_list=['2026-07-01'])
        async def get(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                component_name: str, 
                name: str, 
                **kwargs: Any
            ) -> DaprComponentResiliencyPolicy: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-01', params_added_on={'2026-07-01': ['api_version', 'subscription_id', 'resource_group_name', 'environment_name', 'component_name', 'accept']}, api_versions_list=['2026-07-01'])
        def list(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                component_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DaprComponentResiliencyPolicy]: ...


    class azure.mgmt.appcontainers.aio.operations.DaprComponentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                component_name: str, 
                dapr_component_envelope: DaprComponent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DaprComponent: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                component_name: str, 
                dapr_component_envelope: DaprComponent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DaprComponent: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                component_name: str, 
                dapr_component_envelope: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DaprComponent: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                component_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                component_name: str, 
                **kwargs: Any
            ) -> DaprComponent: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DaprComponent]: ...

        @distributed_trace_async
        async def list_secrets(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                component_name: str, 
                **kwargs: Any
            ) -> DaprSecretsCollection: ...


    class azure.mgmt.appcontainers.aio.operations.DotNetComponentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                name: str, 
                dot_net_component_envelope: DotNetComponent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DotNetComponent]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                name: str, 
                dot_net_component_envelope: DotNetComponent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DotNetComponent]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                name: str, 
                dot_net_component_envelope: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DotNetComponent]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-03-02-preview', params_added_on={'2026-03-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'environment_name', 'name']}, api_versions_list=['2026-03-02-preview', '2026-07-01'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                name: str, 
                dot_net_component_envelope: DotNetComponent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DotNetComponent]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                name: str, 
                dot_net_component_envelope: DotNetComponent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DotNetComponent]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                name: str, 
                dot_net_component_envelope: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DotNetComponent]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-03-02-preview', params_added_on={'2026-03-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'environment_name', 'name', 'accept']}, api_versions_list=['2026-03-02-preview', '2026-07-01'])
        async def get(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                name: str, 
                **kwargs: Any
            ) -> DotNetComponent: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-02-preview', params_added_on={'2026-03-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'environment_name', 'accept']}, api_versions_list=['2026-03-02-preview', '2026-07-01'])
        def list(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DotNetComponent]: ...


    class azure.mgmt.appcontainers.aio.operations.FunctionsExtensionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-07-01', params_added_on={'2026-07-01': ['api_version', 'subscription_id', 'resource_group_name', 'container_app_name', 'revision_name', 'function_app_name', 'accept']}, api_versions_list=['2026-07-01'])
        async def invoke_functions_host(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                revision_name: str, 
                function_app_name: str, 
                **kwargs: Any
            ) -> str: ...


    class azure.mgmt.appcontainers.aio.operations.HttpRouteConfigOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                http_route_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                http_route_name: str, 
                http_route_config_envelope: Optional[HttpRouteConfig] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HttpRouteConfig: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                http_route_name: str, 
                http_route_config_envelope: Optional[HttpRouteConfig] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HttpRouteConfig: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                http_route_name: str, 
                http_route_config_envelope: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HttpRouteConfig: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                http_route_name: str, 
                **kwargs: Any
            ) -> HttpRouteConfig: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[HttpRouteConfig]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                http_route_name: str, 
                http_route_config_envelope: HttpRouteConfig, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HttpRouteConfig: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                http_route_name: str, 
                http_route_config_envelope: HttpRouteConfig, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HttpRouteConfig: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                http_route_name: str, 
                http_route_config_envelope: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HttpRouteConfig: ...


    class azure.mgmt.appcontainers.aio.operations.JavaComponentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                name: str, 
                java_component_envelope: JavaComponent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[JavaComponent]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                name: str, 
                java_component_envelope: JavaComponent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[JavaComponent]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                name: str, 
                java_component_envelope: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[JavaComponent]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                name: str, 
                java_component_envelope: JavaComponent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[JavaComponent]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                name: str, 
                java_component_envelope: JavaComponent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[JavaComponent]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                name: str, 
                java_component_envelope: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[JavaComponent]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                name: str, 
                **kwargs: Any
            ) -> JavaComponent: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[JavaComponent]: ...


    class azure.mgmt.appcontainers.aio.operations.JobsExecutionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                job_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[JobExecution]: ...


    class azure.mgmt.appcontainers.aio.operations.JobsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                job_name: str, 
                job_envelope: Job, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Job]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                job_name: str, 
                job_envelope: Job, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Job]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                job_name: str, 
                job_envelope: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Job]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-03-02-preview', params_added_on={'2026-03-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'job_name', 'accept']}, api_versions_list=['2026-03-02-preview', '2026-07-01'])
        async def begin_resume(
                self, 
                resource_group_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[Job]: ...

        @overload
        async def begin_start(
                self, 
                resource_group_name: str, 
                job_name: str, 
                template: Optional[JobExecutionTemplate] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[JobExecutionBase]: ...

        @overload
        async def begin_start(
                self, 
                resource_group_name: str, 
                job_name: str, 
                template: Optional[JobExecutionTemplate] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[JobExecutionBase]: ...

        @overload
        async def begin_start(
                self, 
                resource_group_name: str, 
                job_name: str, 
                template: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[JobExecutionBase]: ...

        @distributed_trace_async
        async def begin_stop_execution(
                self, 
                resource_group_name: str, 
                job_name: str, 
                job_execution_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_stop_multiple_executions(
                self, 
                resource_group_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ContainerAppJobExecutions]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-03-02-preview', params_added_on={'2026-03-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'job_name', 'accept']}, api_versions_list=['2026-03-02-preview', '2026-07-01'])
        async def begin_suspend(
                self, 
                resource_group_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[Job]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                job_name: str, 
                job_envelope: JobPatchProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Job]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                job_name: str, 
                job_envelope: JobPatchProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Job]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                job_name: str, 
                job_envelope: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Job]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> Job: ...

        @distributed_trace_async
        async def get_detector(
                self, 
                resource_group_name: str, 
                job_name: str, 
                detector_name: str, 
                **kwargs: Any
            ) -> Diagnostics: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Job]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[Job]: ...

        @distributed_trace
        def list_detectors(
                self, 
                resource_group_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Diagnostics]: ...

        @distributed_trace_async
        async def list_secrets(
                self, 
                resource_group_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> JobSecretsCollection: ...

        @distributed_trace_async
        async def proxy_get(
                self, 
                resource_group_name: str, 
                job_name: str, 
                api_name: str, 
                **kwargs: Any
            ) -> Job: ...


    class azure.mgmt.appcontainers.aio.operations.LogicAppsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                logic_app_name: str, 
                resource: Optional[LogicApp] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LogicApp: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                logic_app_name: str, 
                resource: Optional[LogicApp] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LogicApp: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                logic_app_name: str, 
                resource: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LogicApp: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                logic_app_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                logic_app_name: str, 
                **kwargs: Any
            ) -> LogicApp: ...

        @distributed_trace_async
        async def get_workflow(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                logic_app_name: str, 
                workflow_name: str, 
                **kwargs: Any
            ) -> WorkflowEnvelope: ...

        @distributed_trace
        def list_workflows(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                logic_app_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[WorkflowEnvelope]: ...

        @distributed_trace_async
        async def list_workflows_connections(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                logic_app_name: str, 
                **kwargs: Any
            ) -> WorkflowEnvelope: ...


    class azure.mgmt.appcontainers.aio.operations.MaintenanceConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                config_name: str, 
                maintenance_configuration_envelope: MaintenanceConfigurationResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MaintenanceConfigurationResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                config_name: str, 
                maintenance_configuration_envelope: MaintenanceConfigurationResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MaintenanceConfigurationResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                config_name: str, 
                maintenance_configuration_envelope: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MaintenanceConfigurationResource: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                config_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                config_name: str, 
                **kwargs: Any
            ) -> MaintenanceConfigurationResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[MaintenanceConfigurationResource]: ...


    class azure.mgmt.appcontainers.aio.operations.ManagedCertificatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                managed_certificate_name: str, 
                managed_certificate_envelope: Optional[ManagedCertificate] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedCertificate]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                managed_certificate_name: str, 
                managed_certificate_envelope: Optional[ManagedCertificate] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedCertificate]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                managed_certificate_name: str, 
                managed_certificate_envelope: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedCertificate]: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                managed_certificate_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                managed_certificate_name: str, 
                **kwargs: Any
            ) -> ManagedCertificate: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ManagedCertificate]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                managed_certificate_name: str, 
                managed_certificate_envelope: ManagedCertificatePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagedCertificate: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                managed_certificate_name: str, 
                managed_certificate_envelope: ManagedCertificatePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagedCertificate: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                managed_certificate_name: str, 
                managed_certificate_envelope: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagedCertificate: ...


    class azure.mgmt.appcontainers.aio.operations.ManagedEnvironmentDiagnosticsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get_detector(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                detector_name: str, 
                **kwargs: Any
            ) -> Diagnostics: ...

        @distributed_trace_async
        async def list_detectors(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                **kwargs: Any
            ) -> DiagnosticsCollection: ...


    class azure.mgmt.appcontainers.aio.operations.ManagedEnvironmentPrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                private_endpoint_connection_name: str, 
                private_endpoint_connection_envelope: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                private_endpoint_connection_name: str, 
                private_endpoint_connection_envelope: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                private_endpoint_connection_name: str, 
                private_endpoint_connection_envelope: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateEndpointConnection]: ...


    class azure.mgmt.appcontainers.aio.operations.ManagedEnvironmentPrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-07-01', params_added_on={'2026-07-01': ['api_version', 'subscription_id', 'resource_group_name', 'environment_name', 'private_link_resource_name', 'accept']}, api_versions_list=['2026-07-01'])
        async def get(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                private_link_resource_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-01', params_added_on={'2026-07-01': ['api_version', 'subscription_id', 'resource_group_name', 'environment_name', 'accept']}, api_versions_list=['2026-07-01'])
        def list(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateLinkResource]: ...


    class azure.mgmt.appcontainers.aio.operations.ManagedEnvironmentUsagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Usage]: ...


    class azure.mgmt.appcontainers.aio.operations.ManagedEnvironmentsDiagnosticsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get_root(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                **kwargs: Any
            ) -> ManagedEnvironment: ...


    class azure.mgmt.appcontainers.aio.operations.ManagedEnvironmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                environment_envelope: ManagedEnvironment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedEnvironment]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                environment_envelope: ManagedEnvironment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedEnvironment]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                environment_envelope: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedEnvironment]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                environment_envelope: ManagedEnvironment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedEnvironment]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                environment_envelope: ManagedEnvironment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedEnvironment]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                environment_envelope: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedEnvironment]: ...

        @overload
        async def check_migration_eligibility(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                body: CheckMigrationEligibilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckMigrationEligibilityResponse: ...

        @overload
        async def check_migration_eligibility(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                body: CheckMigrationEligibilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckMigrationEligibilityResponse: ...

        @overload
        async def check_migration_eligibility(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckMigrationEligibilityResponse: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                **kwargs: Any
            ) -> ManagedEnvironment: ...

        @distributed_trace_async
        async def get_auth_token(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                **kwargs: Any
            ) -> EnvironmentAuthToken: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ManagedEnvironment]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[ManagedEnvironment]: ...

        @distributed_trace
        def list_workload_profile_states(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[WorkloadProfileStates]: ...


    class azure.mgmt.appcontainers.aio.operations.ManagedEnvironmentsStoragesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                storage_name: str, 
                storage_envelope: ManagedEnvironmentStorage, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagedEnvironmentStorage: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                storage_name: str, 
                storage_envelope: ManagedEnvironmentStorage, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagedEnvironmentStorage: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                storage_name: str, 
                storage_envelope: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagedEnvironmentStorage: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                storage_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                storage_name: str, 
                **kwargs: Any
            ) -> ManagedEnvironmentStorage: ...

        @distributed_trace_async
        async def list(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                **kwargs: Any
            ) -> ManagedEnvironmentStoragesCollection: ...


    class azure.mgmt.appcontainers.aio.operations.NamespacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def check_name_availability(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                check_name_availability_request: CheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        async def check_name_availability(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                check_name_availability_request: CheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        async def check_name_availability(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                check_name_availability_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...


    class azure.mgmt.appcontainers.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[OperationDetail]: ...


    class azure.mgmt.appcontainers.aio.operations.SandboxGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                sandbox_group_name: str, 
                resource: SandboxGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SandboxGroup]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                sandbox_group_name: str, 
                resource: SandboxGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SandboxGroup]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                sandbox_group_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SandboxGroup]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-07-01', params_added_on={'2026-07-01': ['api_version', 'subscription_id', 'resource_group_name', 'sandbox_group_name']}, api_versions_list=['2026-07-01'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                sandbox_group_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                sandbox_group_name: str, 
                properties: SandboxGroupPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                sandbox_group_name: str, 
                properties: SandboxGroupPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                sandbox_group_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-07-01', params_added_on={'2026-07-01': ['api_version', 'subscription_id', 'resource_group_name', 'sandbox_group_name', 'accept']}, api_versions_list=['2026-07-01'])
        async def get(
                self, 
                resource_group_name: str, 
                sandbox_group_name: str, 
                **kwargs: Any
            ) -> SandboxGroup: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-01', params_added_on={'2026-07-01': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2026-07-01'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SandboxGroup]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-01', params_added_on={'2026-07-01': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2026-07-01'])
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[SandboxGroup]: ...


    class azure.mgmt.appcontainers.aio.operations.UsagesOperations:

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
            ) -> AsyncItemPaged[Usage]: ...


    class azure.mgmt.appcontainers.aio.operations.VnetConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-07-01', params_added_on={'2026-07-01': ['api_version', 'subscription_id', 'resource_group_name', 'sandbox_group_name', 'vnet_connection_name']}, api_versions_list=['2026-07-01'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                sandbox_group_name: str, 
                vnet_connection_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                sandbox_group_name: str, 
                vnet_connection_name: str, 
                resource: VnetConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VnetConnection: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                sandbox_group_name: str, 
                vnet_connection_name: str, 
                resource: VnetConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VnetConnection: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                sandbox_group_name: str, 
                vnet_connection_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VnetConnection: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-07-01', params_added_on={'2026-07-01': ['api_version', 'subscription_id', 'resource_group_name', 'sandbox_group_name', 'vnet_connection_name', 'accept']}, api_versions_list=['2026-07-01'])
        async def get(
                self, 
                resource_group_name: str, 
                sandbox_group_name: str, 
                vnet_connection_name: str, 
                **kwargs: Any
            ) -> VnetConnection: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-01', params_added_on={'2026-07-01': ['api_version', 'subscription_id', 'resource_group_name', 'sandbox_group_name', 'accept']}, api_versions_list=['2026-07-01'])
        def list_by_sandbox_group(
                self, 
                resource_group_name: str, 
                sandbox_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[VnetConnection]: ...


namespace azure.mgmt.appcontainers.models

    class azure.mgmt.appcontainers.models.AccessMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        READ_ONLY = "ReadOnly"
        READ_WRITE = "ReadWrite"


    class azure.mgmt.appcontainers.models.Action(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW = "Allow"
        DENY = "Deny"


    class azure.mgmt.appcontainers.models.ActiveRevisionsMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MULTIPLE = "Multiple"
        SINGLE = "Single"


    class azure.mgmt.appcontainers.models.Affinity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "none"
        STICKY = "sticky"


    class azure.mgmt.appcontainers.models.AllowedAudiencesValidation(_Model):
        allowed_audiences: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                allowed_audiences: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.AllowedPrincipals(_Model):
        groups: Optional[list[str]]
        identities: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                groups: Optional[list[str]] = ..., 
                identities: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.AppInsightsConfiguration(_Model):
        connection_string: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                connection_string: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.AppLogsConfiguration(_Model):
        destination: Optional[str]
        log_analytics_configuration: Optional[LogAnalyticsConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                destination: Optional[str] = ..., 
                log_analytics_configuration: Optional[LogAnalyticsConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.AppProtocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GRPC = "grpc"
        HTTP = "http"


    class azure.mgmt.appcontainers.models.AppRegistration(_Model):
        app_id: Optional[str]
        app_secret_setting_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                app_id: Optional[str] = ..., 
                app_secret_setting_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.Apple(_Model):
        enabled: Optional[bool]
        login: Optional[LoginScopes]
        registration: Optional[AppleRegistration]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                login: Optional[LoginScopes] = ..., 
                registration: Optional[AppleRegistration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.AppleRegistration(_Model):
        client_id: Optional[str]
        client_secret_setting_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                client_id: Optional[str] = ..., 
                client_secret_setting_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.Applicability(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM = "Custom"
        LOCATION_DEFAULT = "LocationDefault"


    class azure.mgmt.appcontainers.models.AuthConfig(ProxyResource):
        id: str
        name: str
        properties: Optional[AuthConfigProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AuthConfigProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.appcontainers.models.AuthConfigProperties(_Model):
        encryption_settings: Optional[EncryptionSettings]
        global_validation: Optional[GlobalValidation]
        http_settings: Optional[HttpSettings]
        identity_providers: Optional[IdentityProviders]
        login: Optional[Login]
        platform: Optional[AuthPlatform]

        @overload
        def __init__(
                self, 
                *, 
                encryption_settings: Optional[EncryptionSettings] = ..., 
                global_validation: Optional[GlobalValidation] = ..., 
                http_settings: Optional[HttpSettings] = ..., 
                identity_providers: Optional[IdentityProviders] = ..., 
                login: Optional[Login] = ..., 
                platform: Optional[AuthPlatform] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.AuthPlatform(_Model):
        enabled: Optional[bool]
        runtime_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                runtime_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.AvailableEnvironmentMode(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[AvailableEnvironmentModeProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[AvailableEnvironmentModeProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.AvailableEnvironmentModeProperties(_Model):
        description: Optional[str]
        display_name: Optional[str]


    class azure.mgmt.appcontainers.models.AvailableWorkloadProfile(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[AvailableWorkloadProfileProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[AvailableWorkloadProfileProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.AvailableWorkloadProfileProperties(_Model):
        applicability: Optional[Union[str, Applicability]]
        category: Optional[str]
        cores: Optional[int]
        display_name: Optional[str]
        gpus: Optional[int]
        memory_gi_b: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                applicability: Optional[Union[str, Applicability]] = ..., 
                category: Optional[str] = ..., 
                cores: Optional[int] = ..., 
                display_name: Optional[str] = ..., 
                gpus: Optional[int] = ..., 
                memory_gi_b: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.AzureActiveDirectory(_Model):
        enabled: Optional[bool]
        is_auto_provisioned: Optional[bool]
        login: Optional[AzureActiveDirectoryLogin]
        registration: Optional[AzureActiveDirectoryRegistration]
        validation: Optional[AzureActiveDirectoryValidation]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                is_auto_provisioned: Optional[bool] = ..., 
                login: Optional[AzureActiveDirectoryLogin] = ..., 
                registration: Optional[AzureActiveDirectoryRegistration] = ..., 
                validation: Optional[AzureActiveDirectoryValidation] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.AzureActiveDirectoryLogin(_Model):
        disable_www_authenticate: Optional[bool]
        login_parameters: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                disable_www_authenticate: Optional[bool] = ..., 
                login_parameters: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.AzureActiveDirectoryRegistration(_Model):
        client_id: Optional[str]
        client_secret_certificate_issuer: Optional[str]
        client_secret_certificate_subject_alternative_name: Optional[str]
        client_secret_certificate_thumbprint: Optional[str]
        client_secret_setting_name: Optional[str]
        open_id_issuer: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                client_id: Optional[str] = ..., 
                client_secret_certificate_issuer: Optional[str] = ..., 
                client_secret_certificate_subject_alternative_name: Optional[str] = ..., 
                client_secret_certificate_thumbprint: Optional[str] = ..., 
                client_secret_setting_name: Optional[str] = ..., 
                open_id_issuer: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.AzureActiveDirectoryValidation(_Model):
        allowed_audiences: Optional[list[str]]
        default_authorization_policy: Optional[DefaultAuthorizationPolicy]
        jwt_claim_checks: Optional[JwtClaimChecks]

        @overload
        def __init__(
                self, 
                *, 
                allowed_audiences: Optional[list[str]] = ..., 
                default_authorization_policy: Optional[DefaultAuthorizationPolicy] = ..., 
                jwt_claim_checks: Optional[JwtClaimChecks] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.AzureCredentials(_Model):
        client_id: Optional[str]
        client_secret: Optional[str]
        kind: Optional[str]
        subscription_id: Optional[str]
        tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                client_id: Optional[str] = ..., 
                client_secret: Optional[str] = ..., 
                kind: Optional[str] = ..., 
                subscription_id: Optional[str] = ..., 
                tenant_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.AzureFileProperties(_Model):
        access_mode: Optional[Union[str, AccessMode]]
        account_key: Optional[str]
        account_key_vault_properties: Optional[SecretKeyVaultProperties]
        account_name: Optional[str]
        share_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                access_mode: Optional[Union[str, AccessMode]] = ..., 
                account_key: Optional[str] = ..., 
                account_key_vault_properties: Optional[SecretKeyVaultProperties] = ..., 
                account_name: Optional[str] = ..., 
                share_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.AzureStaticWebApps(_Model):
        enabled: Optional[bool]
        registration: Optional[AzureStaticWebAppsRegistration]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                registration: Optional[AzureStaticWebAppsRegistration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.AzureStaticWebAppsRegistration(_Model):
        client_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                client_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.BaseContainer(_Model):
        args: Optional[list[str]]
        command: Optional[list[str]]
        env: Optional[list[EnvironmentVar]]
        image: Optional[str]
        name: Optional[str]
        resources: Optional[ContainerResources]
        volume_mounts: Optional[list[VolumeMount]]

        @overload
        def __init__(
                self, 
                *, 
                args: Optional[list[str]] = ..., 
                command: Optional[list[str]] = ..., 
                env: Optional[list[EnvironmentVar]] = ..., 
                image: Optional[str] = ..., 
                name: Optional[str] = ..., 
                resources: Optional[ContainerResources] = ..., 
                volume_mounts: Optional[list[VolumeMount]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.BillingMeter(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[BillingMeterProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[BillingMeterProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.BillingMeterCollection(_Model):
        value: list[BillingMeter]

        @overload
        def __init__(
                self, 
                *, 
                value: list[BillingMeter]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.BillingMeterProperties(_Model):
        category: Optional[str]
        display_name: Optional[str]
        meter_type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                category: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                meter_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.BindingType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO = "Auto"
        DISABLED = "Disabled"
        SNI_ENABLED = "SniEnabled"


    class azure.mgmt.appcontainers.models.BlobStorageTokenStore(_Model):
        blob_container_uri: Optional[str]
        client_id: Optional[str]
        managed_identity_resource_id: Optional[str]
        sas_url_setting_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                blob_container_uri: Optional[str] = ..., 
                client_id: Optional[str] = ..., 
                managed_identity_resource_id: Optional[str] = ..., 
                sas_url_setting_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.Certificate(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[CertificateProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[CertificateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.CertificateKeyVaultProperties(_Model):
        identity: Optional[str]
        key_vault_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[str] = ..., 
                key_vault_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.CertificatePatch(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.CertificateProperties(_Model):
        certificate_key_vault_properties: Optional[CertificateKeyVaultProperties]
        deployment_errors: Optional[str]
        expiration_date: Optional[datetime]
        issue_date: Optional[datetime]
        issuer: Optional[str]
        password: Optional[str]
        provisioning_state: Optional[Union[str, CertificateProvisioningState]]
        public_key_hash: Optional[str]
        subject_alternative_names: Optional[list[str]]
        subject_name: Optional[str]
        thumbprint: Optional[str]
        valid: Optional[bool]
        value: Optional[bytes]

        @overload
        def __init__(
                self, 
                *, 
                certificate_key_vault_properties: Optional[CertificateKeyVaultProperties] = ..., 
                password: Optional[str] = ..., 
                value: Optional[bytes] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.CertificateProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        DELETE_FAILED = "DeleteFailed"
        DELETING = "Deleting"
        FAILED = "Failed"
        PENDING = "Pending"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.appcontainers.models.CheckMigrationEligibilityRequest(_Model):
        target_mode: str

        @overload
        def __init__(
                self, 
                *, 
                target_mode: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.CheckMigrationEligibilityResponse(_Model):
        current_mode: str
        environment_name: str
        failure_reasons: list[MigrationEligibilityFailureReason]
        is_eligible: bool
        target_mode: str

        @overload
        def __init__(
                self, 
                *, 
                current_mode: str, 
                environment_name: str, 
                failure_reasons: list[MigrationEligibilityFailureReason], 
                is_eligible: bool, 
                target_mode: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.CheckNameAvailabilityReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALREADY_EXISTS = "AlreadyExists"
        INVALID = "Invalid"


    class azure.mgmt.appcontainers.models.CheckNameAvailabilityRequest(_Model):
        name: Optional[str]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.CheckNameAvailabilityResponse(_Model):
        message: Optional[str]
        name_available: Optional[bool]
        reason: Optional[Union[str, CheckNameAvailabilityReason]]

        @overload
        def __init__(
                self, 
                *, 
                message: Optional[str] = ..., 
                name_available: Optional[bool] = ..., 
                reason: Optional[Union[str, CheckNameAvailabilityReason]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.ClientRegistration(_Model):
        client_id: Optional[str]
        client_secret_setting_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                client_id: Optional[str] = ..., 
                client_secret_setting_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.Configuration(_Model):
        active_revisions_mode: Optional[Union[str, ActiveRevisionsMode]]
        dapr: Optional[Dapr]
        identity_settings: Optional[list[IdentitySettings]]
        ingress: Optional[Ingress]
        max_inactive_revisions: Optional[int]
        registries: Optional[list[RegistryCredentials]]
        runtime: Optional[Runtime]
        secrets: Optional[list[Secret]]
        service: Optional[Service]

        @overload
        def __init__(
                self, 
                *, 
                active_revisions_mode: Optional[Union[str, ActiveRevisionsMode]] = ..., 
                dapr: Optional[Dapr] = ..., 
                identity_settings: Optional[list[IdentitySettings]] = ..., 
                ingress: Optional[Ingress] = ..., 
                max_inactive_revisions: Optional[int] = ..., 
                registries: Optional[list[RegistryCredentials]] = ..., 
                runtime: Optional[Runtime] = ..., 
                secrets: Optional[list[Secret]] = ..., 
                service: Optional[Service] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.ConnectedEnvironment(TrackedResource):
        extended_location: Optional[ExtendedLocation]
        id: str
        location: str
        name: str
        properties: Optional[ConnectedEnvironmentProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                location: str, 
                properties: Optional[ConnectedEnvironmentProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.appcontainers.models.ConnectedEnvironmentPatchResource(ResourceTags):
        tags: dict[str, str]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.ConnectedEnvironmentProperties(_Model):
        custom_domain_configuration: Optional[CustomDomainConfiguration]
        dapr_ai_connection_string: Optional[str]
        default_domain: Optional[str]
        deployment_errors: Optional[str]
        provisioning_state: Optional[Union[str, ConnectedEnvironmentProvisioningState]]
        static_ip: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                custom_domain_configuration: Optional[CustomDomainConfiguration] = ..., 
                dapr_ai_connection_string: Optional[str] = ..., 
                static_ip: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.ConnectedEnvironmentProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        INFRASTRUCTURE_SETUP_COMPLETE = "InfrastructureSetupComplete"
        INFRASTRUCTURE_SETUP_IN_PROGRESS = "InfrastructureSetupInProgress"
        INITIALIZATION_IN_PROGRESS = "InitializationInProgress"
        SCHEDULED_FOR_DELETE = "ScheduledForDelete"
        SUCCEEDED = "Succeeded"
        WAITING = "Waiting"


    class azure.mgmt.appcontainers.models.ConnectedEnvironmentStorage(ProxyResource):
        id: str
        name: str
        properties: Optional[ConnectedEnvironmentStorageProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ConnectedEnvironmentStorageProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.ConnectedEnvironmentStorageProperties(_Model):
        azure_file: Optional[AzureFileProperties]
        deployment_errors: Optional[str]
        provisioning_state: Optional[Union[str, ConnectedEnvironmentStorageProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                azure_file: Optional[AzureFileProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.ConnectedEnvironmentStorageProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.appcontainers.models.ConnectedEnvironmentStoragesCollection(_Model):
        value: list[ConnectedEnvironmentStorage]

        @overload
        def __init__(
                self, 
                *, 
                value: list[ConnectedEnvironmentStorage]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.Container(BaseContainer):
        args: list[str]
        command: list[str]
        env: list[EnvironmentVar]
        image: str
        name: str
        probes: Optional[list[ContainerAppProbe]]
        resources: ContainerResources
        volume_mounts: list[VolumeMount]

        @overload
        def __init__(
                self, 
                *, 
                args: Optional[list[str]] = ..., 
                command: Optional[list[str]] = ..., 
                env: Optional[list[EnvironmentVar]] = ..., 
                image: Optional[str] = ..., 
                name: Optional[str] = ..., 
                probes: Optional[list[ContainerAppProbe]] = ..., 
                resources: Optional[ContainerResources] = ..., 
                volume_mounts: Optional[list[VolumeMount]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.ContainerApp(TrackedResource):
        extended_location: Optional[ExtendedLocation]
        id: str
        identity: Optional[ManagedServiceIdentity]
        kind: Optional[Union[str, Kind]]
        location: str
        managed_by: Optional[str]
        name: str
        properties: Optional[ContainerAppProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                identity: Optional[ManagedServiceIdentity] = ..., 
                kind: Optional[Union[str, Kind]] = ..., 
                location: str, 
                managed_by: Optional[str] = ..., 
                properties: Optional[ContainerAppProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.appcontainers.models.ContainerAppAuthToken(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[ContainerAppAuthTokenProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[ContainerAppAuthTokenProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.appcontainers.models.ContainerAppAuthTokenProperties(_Model):
        expires: Optional[datetime]
        token: Optional[str]


    class azure.mgmt.appcontainers.models.ContainerAppContainerRunningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        RUNNING = "Running"
        TERMINATED = "Terminated"
        WAITING = "Waiting"


    class azure.mgmt.appcontainers.models.ContainerAppJobExecutions(_Model):
        next_link: Optional[str]
        value: list[JobExecution]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[JobExecution]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.ContainerAppNetworkingConfiguration(_Model):
        outbound_vnet_subnet_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                outbound_vnet_subnet_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.ContainerAppProbe(_Model):
        failure_threshold: Optional[int]
        http_get: Optional[ContainerAppProbeHttpGet]
        initial_delay_seconds: Optional[int]
        period_seconds: Optional[int]
        success_threshold: Optional[int]
        tcp_socket: Optional[ContainerAppProbeTcpSocket]
        termination_grace_period_seconds: Optional[int]
        timeout_seconds: Optional[int]
        type: Optional[Union[str, Type]]

        @overload
        def __init__(
                self, 
                *, 
                failure_threshold: Optional[int] = ..., 
                http_get: Optional[ContainerAppProbeHttpGet] = ..., 
                initial_delay_seconds: Optional[int] = ..., 
                period_seconds: Optional[int] = ..., 
                success_threshold: Optional[int] = ..., 
                tcp_socket: Optional[ContainerAppProbeTcpSocket] = ..., 
                termination_grace_period_seconds: Optional[int] = ..., 
                timeout_seconds: Optional[int] = ..., 
                type: Optional[Union[str, Type]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.ContainerAppProbeHttpGet(_Model):
        host: Optional[str]
        http_headers: Optional[list[ContainerAppProbeHttpGetHttpHeadersItem]]
        path: Optional[str]
        port: int
        scheme: Optional[Union[str, Scheme]]

        @overload
        def __init__(
                self, 
                *, 
                host: Optional[str] = ..., 
                http_headers: Optional[list[ContainerAppProbeHttpGetHttpHeadersItem]] = ..., 
                path: Optional[str] = ..., 
                port: int, 
                scheme: Optional[Union[str, Scheme]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.ContainerAppProbeHttpGetHttpHeadersItem(_Model):
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


    class azure.mgmt.appcontainers.models.ContainerAppProbeTcpSocket(_Model):
        host: Optional[str]
        port: int

        @overload
        def __init__(
                self, 
                *, 
                host: Optional[str] = ..., 
                port: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.ContainerAppProperties(_Model):
        configuration: Optional[Configuration]
        custom_domain_verification_id: Optional[str]
        environment_id: Optional[str]
        event_stream_endpoint: Optional[str]
        latest_ready_revision_name: Optional[str]
        latest_revision_fqdn: Optional[str]
        latest_revision_name: Optional[str]
        managed_environment_id: Optional[str]
        networking: Optional[ContainerAppNetworkingConfiguration]
        outbound_ip_addresses: Optional[list[str]]
        provisioning_state: Optional[Union[str, ContainerAppProvisioningState]]
        running_status: Optional[Union[str, ContainerAppRunningStatus]]
        template: Optional[Template]
        workload_profile_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                configuration: Optional[Configuration] = ..., 
                environment_id: Optional[str] = ..., 
                managed_environment_id: Optional[str] = ..., 
                networking: Optional[ContainerAppNetworkingConfiguration] = ..., 
                template: Optional[Template] = ..., 
                workload_profile_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.ContainerAppProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.appcontainers.models.ContainerAppReplicaRunningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_RUNNING = "NotRunning"
        RUNNING = "Running"
        UNKNOWN = "Unknown"


    class azure.mgmt.appcontainers.models.ContainerAppRunningStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PROGRESSING = "Progressing"
        READY = "Ready"
        RUNNING = "Running"
        STOPPED = "Stopped"
        SUSPENDED = "Suspended"


    class azure.mgmt.appcontainers.models.ContainerAppSecret(_Model):
        identity: Optional[str]
        key_vault_url: Optional[str]
        name: Optional[str]
        value: Optional[str]


    class azure.mgmt.appcontainers.models.ContainerAppsFunction(ProxyResource):
        id: str
        name: str
        properties: Optional[ContainerAppsFunctionProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ContainerAppsFunctionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.appcontainers.models.ContainerAppsFunctionProperties(_Model):
        invoke_url_template: Optional[str]
        is_disabled: Optional[bool]
        language: Optional[str]
        state: Optional[Union[str, ContainerAppsFunctionState]]
        trigger_type: Optional[str]


    class azure.mgmt.appcontainers.models.ContainerAppsFunctionState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.appcontainers.models.ContainerExecutionStatus(_Model):
        additional_information: Optional[str]
        code: Optional[int]
        name: Optional[str]
        status: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                additional_information: Optional[str] = ..., 
                code: Optional[int] = ..., 
                name: Optional[str] = ..., 
                status: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.ContainerResources(_Model):
        cpu: Optional[float]
        ephemeral_storage: Optional[str]
        memory: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                cpu: Optional[float] = ..., 
                memory: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.ContainerType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM_CONTAINER = "CustomContainer"
        PYTHON_LTS = "PythonLTS"


    class azure.mgmt.appcontainers.models.CookieExpiration(_Model):
        convention: Optional[Union[str, CookieExpirationConvention]]
        time_to_expiration: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                convention: Optional[Union[str, CookieExpirationConvention]] = ..., 
                time_to_expiration: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.CookieExpirationConvention(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FIXED_TIME = "FixedTime"
        IDENTITY_PROVIDER_DERIVED = "IdentityProviderDerived"


    class azure.mgmt.appcontainers.models.CorsPolicy(_Model):
        allow_credentials: Optional[bool]
        allowed_headers: Optional[list[str]]
        allowed_methods: Optional[list[str]]
        allowed_origins: list[str]
        expose_headers: Optional[list[str]]
        max_age: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                allow_credentials: Optional[bool] = ..., 
                allowed_headers: Optional[list[str]] = ..., 
                allowed_methods: Optional[list[str]] = ..., 
                allowed_origins: list[str], 
                expose_headers: Optional[list[str]] = ..., 
                max_age: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.appcontainers.models.CustomContainerTemplate(_Model):
        containers: Optional[list[SessionContainer]]
        ingress: Optional[SessionIngress]
        registry_credentials: Optional[SessionRegistryCredentials]

        @overload
        def __init__(
                self, 
                *, 
                containers: Optional[list[SessionContainer]] = ..., 
                ingress: Optional[SessionIngress] = ..., 
                registry_credentials: Optional[SessionRegistryCredentials] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.CustomDomain(_Model):
        binding_type: Optional[Union[str, BindingType]]
        certificate_id: Optional[str]
        name: str

        @overload
        def __init__(
                self, 
                *, 
                binding_type: Optional[Union[str, BindingType]] = ..., 
                certificate_id: Optional[str] = ..., 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.CustomDomainConfiguration(_Model):
        certificate_key_vault_properties: Optional[CertificateKeyVaultProperties]
        certificate_password: Optional[str]
        certificate_value: Optional[bytes]
        custom_domain_verification_id: Optional[str]
        dns_suffix: Optional[str]
        expiration_date: Optional[datetime]
        subject_name: Optional[str]
        thumbprint: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                certificate_key_vault_properties: Optional[CertificateKeyVaultProperties] = ..., 
                certificate_password: Optional[str] = ..., 
                certificate_value: Optional[bytes] = ..., 
                dns_suffix: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.CustomHostnameAnalysisResult(_Model):
        a_records: Optional[list[str]]
        alternate_c_name_records: Optional[list[str]]
        alternate_txt_records: Optional[list[str]]
        c_name_records: Optional[list[str]]
        conflict_with_environment_custom_domain: Optional[bool]
        conflicting_container_app_resource_id: Optional[str]
        custom_domain_verification_failure_info: Optional[CustomHostnameAnalysisResultCustomDomainVerificationFailureInfo]
        custom_domain_verification_test: Optional[Union[str, DnsVerificationTestResult]]
        has_conflict_on_managed_environment: Optional[bool]
        host_name: Optional[str]
        is_hostname_already_verified: Optional[bool]
        txt_records: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                a_records: Optional[list[str]] = ..., 
                alternate_c_name_records: Optional[list[str]] = ..., 
                alternate_txt_records: Optional[list[str]] = ..., 
                c_name_records: Optional[list[str]] = ..., 
                txt_records: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.CustomHostnameAnalysisResultCustomDomainVerificationFailureInfo(_Model):
        code: Optional[str]
        details: Optional[list[CustomHostnameAnalysisResultCustomDomainVerificationFailureInfoDetailsItem]]
        message: Optional[str]
        target: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                details: Optional[list[CustomHostnameAnalysisResultCustomDomainVerificationFailureInfoDetailsItem]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.CustomHostnameAnalysisResultCustomDomainVerificationFailureInfoDetailsItem(_Model):
        code: Optional[str]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.appcontainers.models.CustomOpenIdConnectProvider(_Model):
        enabled: Optional[bool]
        login: Optional[OpenIdConnectLogin]
        registration: Optional[OpenIdConnectRegistration]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                login: Optional[OpenIdConnectLogin] = ..., 
                registration: Optional[OpenIdConnectRegistration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.CustomScaleRule(_Model):
        auth: Optional[list[ScaleRuleAuth]]
        identity: Optional[str]
        metadata: Optional[dict[str, str]]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                auth: Optional[list[ScaleRuleAuth]] = ..., 
                identity: Optional[str] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.Dapr(_Model):
        app_health: Optional[DaprAppHealth]
        app_id: Optional[str]
        app_port: Optional[int]
        app_protocol: Optional[Union[str, AppProtocol]]
        enable_api_logging: Optional[bool]
        enabled: Optional[bool]
        http_max_request_size: Optional[int]
        http_read_buffer_size: Optional[int]
        log_level: Optional[Union[str, LogLevel]]
        max_concurrency: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                app_health: Optional[DaprAppHealth] = ..., 
                app_id: Optional[str] = ..., 
                app_port: Optional[int] = ..., 
                app_protocol: Optional[Union[str, AppProtocol]] = ..., 
                enable_api_logging: Optional[bool] = ..., 
                enabled: Optional[bool] = ..., 
                http_max_request_size: Optional[int] = ..., 
                http_read_buffer_size: Optional[int] = ..., 
                log_level: Optional[Union[str, LogLevel]] = ..., 
                max_concurrency: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.DaprAppHealth(_Model):
        enabled: Optional[bool]
        path: Optional[str]
        probe_interval_seconds: Optional[int]
        probe_timeout_milliseconds: Optional[int]
        threshold: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                path: Optional[str] = ..., 
                probe_interval_seconds: Optional[int] = ..., 
                probe_timeout_milliseconds: Optional[int] = ..., 
                threshold: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.DaprComponent(ProxyResource):
        id: str
        name: str
        properties: Optional[DaprComponentProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DaprComponentProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.appcontainers.models.DaprComponentProperties(_Model):
        component_type: Optional[str]
        deployment_errors: Optional[str]
        ignore_errors: Optional[bool]
        init_timeout: Optional[str]
        metadata: Optional[list[DaprMetadata]]
        provisioning_state: Optional[Union[str, DaprComponentProvisioningState]]
        scopes: Optional[list[str]]
        secret_store_component: Optional[str]
        secrets: Optional[list[Secret]]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                component_type: Optional[str] = ..., 
                ignore_errors: Optional[bool] = ..., 
                init_timeout: Optional[str] = ..., 
                metadata: Optional[list[DaprMetadata]] = ..., 
                scopes: Optional[list[str]] = ..., 
                secret_store_component: Optional[str] = ..., 
                secrets: Optional[list[Secret]] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.DaprComponentProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.appcontainers.models.DaprComponentResiliencyPolicy(ProxyResource):
        id: str
        name: str
        properties: Optional[DaprComponentResiliencyPolicyProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DaprComponentResiliencyPolicyProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.appcontainers.models.DaprComponentResiliencyPolicyCircuitBreakerPolicyConfiguration(_Model):
        consecutive_errors: Optional[int]
        interval_in_seconds: Optional[int]
        timeout_in_seconds: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                consecutive_errors: Optional[int] = ..., 
                interval_in_seconds: Optional[int] = ..., 
                timeout_in_seconds: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.DaprComponentResiliencyPolicyConfiguration(_Model):
        circuit_breaker_policy: Optional[DaprComponentResiliencyPolicyCircuitBreakerPolicyConfiguration]
        http_retry_policy: Optional[DaprComponentResiliencyPolicyHttpRetryPolicyConfiguration]
        timeout_policy: Optional[DaprComponentResiliencyPolicyTimeoutPolicyConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                circuit_breaker_policy: Optional[DaprComponentResiliencyPolicyCircuitBreakerPolicyConfiguration] = ..., 
                http_retry_policy: Optional[DaprComponentResiliencyPolicyHttpRetryPolicyConfiguration] = ..., 
                timeout_policy: Optional[DaprComponentResiliencyPolicyTimeoutPolicyConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.DaprComponentResiliencyPolicyHttpRetryBackOffConfiguration(_Model):
        initial_delay_in_milliseconds: Optional[int]
        max_interval_in_milliseconds: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                initial_delay_in_milliseconds: Optional[int] = ..., 
                max_interval_in_milliseconds: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.DaprComponentResiliencyPolicyHttpRetryPolicyConfiguration(_Model):
        max_retries: Optional[int]
        retry_back_off: Optional[DaprComponentResiliencyPolicyHttpRetryBackOffConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                max_retries: Optional[int] = ..., 
                retry_back_off: Optional[DaprComponentResiliencyPolicyHttpRetryBackOffConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.DaprComponentResiliencyPolicyProperties(_Model):
        inbound_policy: Optional[DaprComponentResiliencyPolicyConfiguration]
        outbound_policy: Optional[DaprComponentResiliencyPolicyConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                inbound_policy: Optional[DaprComponentResiliencyPolicyConfiguration] = ..., 
                outbound_policy: Optional[DaprComponentResiliencyPolicyConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.DaprComponentResiliencyPolicyTimeoutPolicyConfiguration(_Model):
        response_timeout_in_seconds: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                response_timeout_in_seconds: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.DaprConfiguration(_Model):
        version: Optional[str]


    class azure.mgmt.appcontainers.models.DaprMetadata(_Model):
        name: Optional[str]
        secret_ref: Optional[str]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                secret_ref: Optional[str] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.DaprSecret(_Model):
        name: Optional[str]
        value: Optional[str]


    class azure.mgmt.appcontainers.models.DaprSecretsCollection(_Model):
        value: list[DaprSecret]

        @overload
        def __init__(
                self, 
                *, 
                value: list[DaprSecret]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.DataDogConfiguration(_Model):
        key: Optional[str]
        site: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                site: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.DefaultAuthorizationPolicy(_Model):
        allowed_applications: Optional[list[str]]
        allowed_principals: Optional[AllowedPrincipals]

        @overload
        def __init__(
                self, 
                *, 
                allowed_applications: Optional[list[str]] = ..., 
                allowed_principals: Optional[AllowedPrincipals] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.DefaultErrorResponse(_Model):
        error: Optional[DefaultErrorResponseError]


    class azure.mgmt.appcontainers.models.DefaultErrorResponseError(_Model):
        code: Optional[str]
        details: Optional[list[DefaultErrorResponseErrorDetailsItem]]
        innererror: Optional[str]
        message: Optional[str]
        target: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                details: Optional[list[DefaultErrorResponseErrorDetailsItem]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.DefaultErrorResponseErrorDetailsItem(_Model):
        code: Optional[str]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.appcontainers.models.DestinationsConfiguration(_Model):
        data_dog_configuration: Optional[DataDogConfiguration]
        otlp_configurations: Optional[list[OtlpConfiguration]]

        @overload
        def __init__(
                self, 
                *, 
                data_dog_configuration: Optional[DataDogConfiguration] = ..., 
                otlp_configurations: Optional[list[OtlpConfiguration]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.DiagnosticDataProviderMetadata(_Model):
        property_bag: Optional[list[DiagnosticDataProviderMetadataPropertyBagItem]]
        provider_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                property_bag: Optional[list[DiagnosticDataProviderMetadataPropertyBagItem]] = ..., 
                provider_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.DiagnosticDataProviderMetadataPropertyBagItem(_Model):
        name: Optional[str]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.DiagnosticDataTableResponseColumn(_Model):
        column_name: Optional[str]
        column_type: Optional[str]
        data_type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                column_name: Optional[str] = ..., 
                column_type: Optional[str] = ..., 
                data_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.DiagnosticDataTableResponseObject(_Model):
        columns: Optional[list[DiagnosticDataTableResponseColumn]]
        rows: Optional[list[Any]]
        table_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                columns: Optional[list[DiagnosticDataTableResponseColumn]] = ..., 
                rows: Optional[list[Any]] = ..., 
                table_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.DiagnosticRendering(_Model):
        description: Optional[str]
        is_visible: Optional[bool]
        title: Optional[str]
        type: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                is_visible: Optional[bool] = ..., 
                title: Optional[str] = ..., 
                type: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.DiagnosticSupportTopic(_Model):
        id: Optional[str]
        pes_id: Optional[str]


    class azure.mgmt.appcontainers.models.Diagnostics(ProxyResource):
        id: str
        name: str
        properties: Optional[DiagnosticsProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DiagnosticsProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.DiagnosticsCollection(_Model):
        next_link: Optional[str]
        value: list[Diagnostics]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[Diagnostics]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.DiagnosticsDataApiResponse(_Model):
        rendering_properties: Optional[DiagnosticRendering]
        table: Optional[DiagnosticDataTableResponseObject]

        @overload
        def __init__(
                self, 
                *, 
                rendering_properties: Optional[DiagnosticRendering] = ..., 
                table: Optional[DiagnosticDataTableResponseObject] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.DiagnosticsDefinition(_Model):
        analysis_types: Optional[list[str]]
        author: Optional[str]
        category: Optional[str]
        description: Optional[str]
        id: Optional[str]
        name: Optional[str]
        score: Optional[float]
        support_topic_list: Optional[list[DiagnosticSupportTopic]]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                analysis_types: Optional[list[str]] = ..., 
                support_topic_list: Optional[list[DiagnosticSupportTopic]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.DiagnosticsProperties(_Model):
        data_provider_metadata: Optional[DiagnosticDataProviderMetadata]
        dataset: Optional[list[DiagnosticsDataApiResponse]]
        metadata: Optional[DiagnosticsDefinition]
        status: Optional[DiagnosticsStatus]

        @overload
        def __init__(
                self, 
                *, 
                data_provider_metadata: Optional[DiagnosticDataProviderMetadata] = ..., 
                dataset: Optional[list[DiagnosticsDataApiResponse]] = ..., 
                metadata: Optional[DiagnosticsDefinition] = ..., 
                status: Optional[DiagnosticsStatus] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.DiagnosticsStatus(_Model):
        message: Optional[str]
        status_id: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                message: Optional[str] = ..., 
                status_id: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.DnsVerificationTestResult(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        PASSED = "Passed"
        SKIPPED = "Skipped"


    class azure.mgmt.appcontainers.models.DotNetComponent(ProxyResource):
        id: str
        name: str
        properties: Optional[DotNetComponentProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DotNetComponentProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.appcontainers.models.DotNetComponentConfigurationProperty(_Model):
        property_name: Optional[str]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                property_name: Optional[str] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.DotNetComponentProperties(_Model):
        component_type: Optional[Union[str, DotNetComponentType]]
        configurations: Optional[list[DotNetComponentConfigurationProperty]]
        provisioning_state: Optional[Union[str, DotNetComponentProvisioningState]]
        service_binds: Optional[list[DotNetComponentServiceBind]]

        @overload
        def __init__(
                self, 
                *, 
                component_type: Optional[Union[str, DotNetComponentType]] = ..., 
                configurations: Optional[list[DotNetComponentConfigurationProperty]] = ..., 
                service_binds: Optional[list[DotNetComponentServiceBind]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.DotNetComponentProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.appcontainers.models.DotNetComponentServiceBind(_Model):
        name: Optional[str]
        service_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                service_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.DotNetComponentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASPIRE_DASHBOARD = "AspireDashboard"


    class azure.mgmt.appcontainers.models.DynamicPoolConfiguration(_Model):
        lifecycle_configuration: Optional[LifecycleConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                lifecycle_configuration: Optional[LifecycleConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.EncryptionSettings(_Model):
        container_app_auth_encryption_secret_name: Optional[str]
        container_app_auth_signing_secret_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                container_app_auth_encryption_secret_name: Optional[str] = ..., 
                container_app_auth_signing_secret_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.EnvironmentAuthToken(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[EnvironmentAuthTokenProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[EnvironmentAuthTokenProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.appcontainers.models.EnvironmentAuthTokenProperties(_Model):
        expires: Optional[datetime]
        token: Optional[str]


    class azure.mgmt.appcontainers.models.EnvironmentProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        INFRASTRUCTURE_SETUP_COMPLETE = "InfrastructureSetupComplete"
        INFRASTRUCTURE_SETUP_IN_PROGRESS = "InfrastructureSetupInProgress"
        INITIALIZATION_IN_PROGRESS = "InitializationInProgress"
        SCHEDULED_FOR_DELETE = "ScheduledForDelete"
        SUCCEEDED = "Succeeded"
        UPGRADE_FAILED = "UpgradeFailed"
        UPGRADE_REQUESTED = "UpgradeRequested"
        WAITING = "Waiting"


    class azure.mgmt.appcontainers.models.EnvironmentVar(_Model):
        name: Optional[str]
        secret_ref: Optional[str]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                secret_ref: Optional[str] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.appcontainers.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.appcontainers.models.ErrorEntity(_Model):
        code: Optional[str]
        details: Optional[list[ErrorEntity]]
        extended_code: Optional[str]
        inner_errors: Optional[list[ErrorEntity]]
        message: Optional[str]
        message_template: Optional[str]
        parameters: Optional[list[str]]
        target: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                details: Optional[list[ErrorEntity]] = ..., 
                extended_code: Optional[str] = ..., 
                inner_errors: Optional[list[ErrorEntity]] = ..., 
                message: Optional[str] = ..., 
                message_template: Optional[str] = ..., 
                parameters: Optional[list[str]] = ..., 
                target: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.ExecutionStatus(_Model):
        replicas: Optional[list[ReplicaExecutionStatus]]

        @overload
        def __init__(
                self, 
                *, 
                replicas: Optional[list[ReplicaExecutionStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.ExtendedLocation(_Model):
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


    class azure.mgmt.appcontainers.models.ExtendedLocationTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM_LOCATION = "CustomLocation"


    class azure.mgmt.appcontainers.models.Facebook(_Model):
        enabled: Optional[bool]
        graph_api_version: Optional[str]
        login: Optional[LoginScopes]
        registration: Optional[AppRegistration]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                graph_api_version: Optional[str] = ..., 
                login: Optional[LoginScopes] = ..., 
                registration: Optional[AppRegistration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.ForwardProxy(_Model):
        convention: Optional[Union[str, ForwardProxyConvention]]
        custom_host_header_name: Optional[str]
        custom_proto_header_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                convention: Optional[Union[str, ForwardProxyConvention]] = ..., 
                custom_host_header_name: Optional[str] = ..., 
                custom_proto_header_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.ForwardProxyConvention(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM = "Custom"
        NO_PROXY = "NoProxy"
        STANDARD = "Standard"


    class azure.mgmt.appcontainers.models.GitHub(_Model):
        enabled: Optional[bool]
        login: Optional[LoginScopes]
        registration: Optional[ClientRegistration]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                login: Optional[LoginScopes] = ..., 
                registration: Optional[ClientRegistration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.GithubActionConfiguration(_Model):
        azure_credentials: Optional[AzureCredentials]
        context_path: Optional[str]
        github_personal_access_token: Optional[str]
        image: Optional[str]
        os: Optional[str]
        publish_type: Optional[str]
        registry_info: Optional[RegistryInfo]
        runtime_stack: Optional[str]
        runtime_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                azure_credentials: Optional[AzureCredentials] = ..., 
                context_path: Optional[str] = ..., 
                github_personal_access_token: Optional[str] = ..., 
                image: Optional[str] = ..., 
                os: Optional[str] = ..., 
                publish_type: Optional[str] = ..., 
                registry_info: Optional[RegistryInfo] = ..., 
                runtime_stack: Optional[str] = ..., 
                runtime_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.GlobalValidation(_Model):
        excluded_paths: Optional[list[str]]
        redirect_to_provider: Optional[str]
        unauthenticated_client_action: Optional[Union[str, UnauthenticatedClientActionV2]]

        @overload
        def __init__(
                self, 
                *, 
                excluded_paths: Optional[list[str]] = ..., 
                redirect_to_provider: Optional[str] = ..., 
                unauthenticated_client_action: Optional[Union[str, UnauthenticatedClientActionV2]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.Google(_Model):
        enabled: Optional[bool]
        login: Optional[LoginScopes]
        registration: Optional[ClientRegistration]
        validation: Optional[AllowedAudiencesValidation]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                login: Optional[LoginScopes] = ..., 
                registration: Optional[ClientRegistration] = ..., 
                validation: Optional[AllowedAudiencesValidation] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.Header(_Model):
        key: Optional[str]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.HttpRoute(_Model):
        action: Optional[HttpRouteAction]
        match: Optional[HttpRouteMatch]

        @overload
        def __init__(
                self, 
                *, 
                action: Optional[HttpRouteAction] = ..., 
                match: Optional[HttpRouteMatch] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.HttpRouteAction(_Model):
        prefix_rewrite: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                prefix_rewrite: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.HttpRouteConfig(ProxyResource):
        id: str
        name: str
        properties: Optional[HttpRouteConfigProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[HttpRouteConfigProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.HttpRouteConfigProperties(_Model):
        custom_domains: Optional[list[CustomDomain]]
        fqdn: Optional[str]
        provisioning_errors: Optional[list[HttpRouteProvisioningErrors]]
        provisioning_state: Optional[Union[str, HttpRouteProvisioningState]]
        rules: Optional[list[HttpRouteRule]]

        @overload
        def __init__(
                self, 
                *, 
                custom_domains: Optional[list[CustomDomain]] = ..., 
                rules: Optional[list[HttpRouteRule]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.HttpRouteMatch(_Model):
        case_sensitive: Optional[bool]
        path: Optional[str]
        path_separated_prefix: Optional[str]
        prefix: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                case_sensitive: Optional[bool] = ..., 
                path: Optional[str] = ..., 
                path_separated_prefix: Optional[str] = ..., 
                prefix: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.HttpRouteProvisioningErrors(_Model):
        message: Optional[str]
        timestamp: Optional[datetime]


    class azure.mgmt.appcontainers.models.HttpRouteProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        PENDING = "Pending"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"
        WAITING = "Waiting"


    class azure.mgmt.appcontainers.models.HttpRouteRule(_Model):
        description: Optional[str]
        routes: Optional[list[HttpRoute]]
        targets: Optional[list[HttpRouteTarget]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                routes: Optional[list[HttpRoute]] = ..., 
                targets: Optional[list[HttpRouteTarget]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.HttpRouteTarget(_Model):
        container_app: str
        label: Optional[str]
        revision: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                container_app: str, 
                label: Optional[str] = ..., 
                revision: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.HttpScaleRule(_Model):
        auth: Optional[list[ScaleRuleAuth]]
        identity: Optional[str]
        metadata: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                auth: Optional[list[ScaleRuleAuth]] = ..., 
                identity: Optional[str] = ..., 
                metadata: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.HttpSettings(_Model):
        forward_proxy: Optional[ForwardProxy]
        require_https: Optional[bool]
        routes: Optional[HttpSettingsRoutes]

        @overload
        def __init__(
                self, 
                *, 
                forward_proxy: Optional[ForwardProxy] = ..., 
                require_https: Optional[bool] = ..., 
                routes: Optional[HttpSettingsRoutes] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.HttpSettingsRoutes(_Model):
        api_prefix: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                api_prefix: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.IdentityProviders(_Model):
        apple: Optional[Apple]
        azure_active_directory: Optional[AzureActiveDirectory]
        azure_static_web_apps: Optional[AzureStaticWebApps]
        custom_open_id_connect_providers: Optional[dict[str, CustomOpenIdConnectProvider]]
        facebook: Optional[Facebook]
        git_hub: Optional[GitHub]
        google: Optional[Google]
        twitter: Optional[Twitter]

        @overload
        def __init__(
                self, 
                *, 
                apple: Optional[Apple] = ..., 
                azure_active_directory: Optional[AzureActiveDirectory] = ..., 
                azure_static_web_apps: Optional[AzureStaticWebApps] = ..., 
                custom_open_id_connect_providers: Optional[dict[str, CustomOpenIdConnectProvider]] = ..., 
                facebook: Optional[Facebook] = ..., 
                git_hub: Optional[GitHub] = ..., 
                google: Optional[Google] = ..., 
                twitter: Optional[Twitter] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.IdentitySettings(_Model):
        identity: str
        lifecycle: Optional[Union[str, IdentitySettingsLifeCycle]]

        @overload
        def __init__(
                self, 
                *, 
                identity: str, 
                lifecycle: Optional[Union[str, IdentitySettingsLifeCycle]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.IdentitySettingsLifeCycle(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL = "All"
        INIT = "Init"
        MAIN = "Main"
        NONE = "None"


    class azure.mgmt.appcontainers.models.Ingress(_Model):
        additional_port_mappings: Optional[list[IngressPortMapping]]
        allow_insecure: Optional[bool]
        client_certificate_mode: Optional[Union[str, IngressClientCertificateMode]]
        cors_policy: Optional[CorsPolicy]
        custom_domains: Optional[list[CustomDomain]]
        exposed_port: Optional[int]
        external: Optional[bool]
        fqdn: Optional[str]
        ip_security_restrictions: Optional[list[IpSecurityRestrictionRule]]
        sticky_sessions: Optional[IngressStickySessions]
        target_port: Optional[int]
        traffic: Optional[list[TrafficWeight]]
        transport: Optional[Union[str, IngressTransportMethod]]

        @overload
        def __init__(
                self, 
                *, 
                additional_port_mappings: Optional[list[IngressPortMapping]] = ..., 
                allow_insecure: Optional[bool] = ..., 
                client_certificate_mode: Optional[Union[str, IngressClientCertificateMode]] = ..., 
                cors_policy: Optional[CorsPolicy] = ..., 
                custom_domains: Optional[list[CustomDomain]] = ..., 
                exposed_port: Optional[int] = ..., 
                external: Optional[bool] = ..., 
                ip_security_restrictions: Optional[list[IpSecurityRestrictionRule]] = ..., 
                sticky_sessions: Optional[IngressStickySessions] = ..., 
                target_port: Optional[int] = ..., 
                traffic: Optional[list[TrafficWeight]] = ..., 
                transport: Optional[Union[str, IngressTransportMethod]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.IngressClientCertificateMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPT = "accept"
        IGNORE = "ignore"
        REQUIRE = "require"


    class azure.mgmt.appcontainers.models.IngressConfiguration(_Model):
        header_count_limit: Optional[int]
        request_idle_timeout: Optional[int]
        termination_grace_period_seconds: Optional[int]
        workload_profile_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                header_count_limit: Optional[int] = ..., 
                request_idle_timeout: Optional[int] = ..., 
                termination_grace_period_seconds: Optional[int] = ..., 
                workload_profile_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.IngressPortMapping(_Model):
        exposed_port: Optional[int]
        external: bool
        target_port: int

        @overload
        def __init__(
                self, 
                *, 
                exposed_port: Optional[int] = ..., 
                external: bool, 
                target_port: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.IngressStickySessions(_Model):
        affinity: Optional[Union[str, Affinity]]

        @overload
        def __init__(
                self, 
                *, 
                affinity: Optional[Union[str, Affinity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.IngressTransportMethod(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO = "auto"
        HTTP = "http"
        HTTP2 = "http2"
        TCP = "tcp"


    class azure.mgmt.appcontainers.models.InitContainer(BaseContainer):
        args: list[str]
        command: list[str]
        env: list[EnvironmentVar]
        image: str
        name: str
        resources: ContainerResources
        volume_mounts: list[VolumeMount]

        @overload
        def __init__(
                self, 
                *, 
                args: Optional[list[str]] = ..., 
                command: Optional[list[str]] = ..., 
                env: Optional[list[EnvironmentVar]] = ..., 
                image: Optional[str] = ..., 
                name: Optional[str] = ..., 
                resources: Optional[ContainerResources] = ..., 
                volume_mounts: Optional[list[VolumeMount]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.IpSecurityRestrictionRule(_Model):
        action: Union[str, Action]
        description: Optional[str]
        ip_address_range: str
        name: str

        @overload
        def __init__(
                self, 
                *, 
                action: Union[str, Action], 
                description: Optional[str] = ..., 
                ip_address_range: str, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.JavaComponent(ProxyResource):
        id: str
        name: str
        properties: Optional[JavaComponentProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[JavaComponentProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.JavaComponentConfigurationProperty(_Model):
        property_name: Optional[str]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                property_name: Optional[str] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.JavaComponentIngress(_Model):
        fqdn: Optional[str]


    class azure.mgmt.appcontainers.models.JavaComponentProperties(_Model):
        component_type: str
        configurations: Optional[list[JavaComponentConfigurationProperty]]
        provisioning_state: Optional[Union[str, JavaComponentProvisioningState]]
        scale: Optional[JavaComponentPropertiesScale]
        service_binds: Optional[list[JavaComponentServiceBind]]

        @overload
        def __init__(
                self, 
                *, 
                component_type: str, 
                configurations: Optional[list[JavaComponentConfigurationProperty]] = ..., 
                scale: Optional[JavaComponentPropertiesScale] = ..., 
                service_binds: Optional[list[JavaComponentServiceBind]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.JavaComponentPropertiesScale(_Model):
        max_replicas: Optional[int]
        min_replicas: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                max_replicas: Optional[int] = ..., 
                min_replicas: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.JavaComponentProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.appcontainers.models.JavaComponentServiceBind(_Model):
        name: Optional[str]
        service_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                service_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.JavaComponentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SPRING_BOOT_ADMIN = "SpringBootAdmin"
        SPRING_CLOUD_CONFIG = "SpringCloudConfig"
        SPRING_CLOUD_EUREKA = "SpringCloudEureka"


    class azure.mgmt.appcontainers.models.Job(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: Optional[JobProperties]
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
                properties: Optional[JobProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.appcontainers.models.JobConfiguration(_Model):
        event_trigger_config: Optional[JobConfigurationEventTriggerConfig]
        identity_settings: Optional[list[IdentitySettings]]
        manual_trigger_config: Optional[JobConfigurationManualTriggerConfig]
        registries: Optional[list[RegistryCredentials]]
        replica_retry_limit: Optional[int]
        replica_timeout: int
        schedule_trigger_config: Optional[JobConfigurationScheduleTriggerConfig]
        secrets: Optional[list[Secret]]
        trigger_type: Union[str, TriggerType]

        @overload
        def __init__(
                self, 
                *, 
                event_trigger_config: Optional[JobConfigurationEventTriggerConfig] = ..., 
                identity_settings: Optional[list[IdentitySettings]] = ..., 
                manual_trigger_config: Optional[JobConfigurationManualTriggerConfig] = ..., 
                registries: Optional[list[RegistryCredentials]] = ..., 
                replica_retry_limit: Optional[int] = ..., 
                replica_timeout: int, 
                schedule_trigger_config: Optional[JobConfigurationScheduleTriggerConfig] = ..., 
                secrets: Optional[list[Secret]] = ..., 
                trigger_type: Union[str, TriggerType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.JobConfigurationEventTriggerConfig(_Model):
        parallelism: Optional[int]
        replica_completion_count: Optional[int]
        scale: Optional[JobScale]

        @overload
        def __init__(
                self, 
                *, 
                parallelism: Optional[int] = ..., 
                replica_completion_count: Optional[int] = ..., 
                scale: Optional[JobScale] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.JobConfigurationManualTriggerConfig(_Model):
        parallelism: Optional[int]
        replica_completion_count: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                parallelism: Optional[int] = ..., 
                replica_completion_count: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.JobConfigurationScheduleTriggerConfig(_Model):
        cron_expression: str
        parallelism: Optional[int]
        replica_completion_count: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                cron_expression: str, 
                parallelism: Optional[int] = ..., 
                replica_completion_count: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.JobExecution(ProxyResource):
        id: str
        name: str
        properties: Optional[JobExecutionProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[JobExecutionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.appcontainers.models.JobExecutionBase(_Model):
        id: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.JobExecutionContainer(_Model):
        args: Optional[list[str]]
        command: Optional[list[str]]
        env: Optional[list[EnvironmentVar]]
        image: Optional[str]
        name: Optional[str]
        resources: Optional[ContainerResources]

        @overload
        def __init__(
                self, 
                *, 
                args: Optional[list[str]] = ..., 
                command: Optional[list[str]] = ..., 
                env: Optional[list[EnvironmentVar]] = ..., 
                image: Optional[str] = ..., 
                name: Optional[str] = ..., 
                resources: Optional[ContainerResources] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.JobExecutionProperties(_Model):
        detailed_status: Optional[ExecutionStatus]
        end_time: Optional[datetime]
        message: Optional[str]
        reason: Optional[str]
        start_time: Optional[datetime]
        status: Optional[Union[str, JobExecutionRunningState]]
        template: Optional[JobExecutionTemplate]

        @overload
        def __init__(
                self, 
                *, 
                detailed_status: Optional[ExecutionStatus] = ..., 
                end_time: Optional[datetime] = ..., 
                start_time: Optional[datetime] = ..., 
                template: Optional[JobExecutionTemplate] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.JobExecutionRunningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEGRADED = "Degraded"
        FAILED = "Failed"
        PROCESSING = "Processing"
        RUNNING = "Running"
        STOPPED = "Stopped"
        SUCCEEDED = "Succeeded"
        UNKNOWN = "Unknown"


    class azure.mgmt.appcontainers.models.JobExecutionTemplate(_Model):
        containers: Optional[list[JobExecutionContainer]]
        init_containers: Optional[list[JobExecutionContainer]]

        @overload
        def __init__(
                self, 
                *, 
                containers: Optional[list[JobExecutionContainer]] = ..., 
                init_containers: Optional[list[JobExecutionContainer]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.JobPatchProperties(_Model):
        identity: Optional[ManagedServiceIdentity]
        properties: Optional[JobPatchPropertiesProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                properties: Optional[JobPatchPropertiesProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.JobPatchPropertiesProperties(_Model):
        configuration: Optional[JobConfiguration]
        environment_id: Optional[str]
        event_stream_endpoint: Optional[str]
        outbound_ip_addresses: Optional[list[str]]
        template: Optional[JobTemplate]

        @overload
        def __init__(
                self, 
                *, 
                configuration: Optional[JobConfiguration] = ..., 
                environment_id: Optional[str] = ..., 
                event_stream_endpoint: Optional[str] = ..., 
                outbound_ip_addresses: Optional[list[str]] = ..., 
                template: Optional[JobTemplate] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.JobProperties(_Model):
        configuration: Optional[JobConfiguration]
        environment_id: Optional[str]
        event_stream_endpoint: Optional[str]
        outbound_ip_addresses: Optional[list[str]]
        provisioning_state: Optional[Union[str, JobProvisioningState]]
        running_state: Optional[Union[str, JobRunningState]]
        template: Optional[JobTemplate]
        workload_profile_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                configuration: Optional[JobConfiguration] = ..., 
                environment_id: Optional[str] = ..., 
                template: Optional[JobTemplate] = ..., 
                workload_profile_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.JobProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.appcontainers.models.JobRunningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PROGRESSING = "Progressing"
        READY = "Ready"
        SUSPENDED = "Suspended"


    class azure.mgmt.appcontainers.models.JobScale(_Model):
        max_executions: Optional[int]
        min_executions: Optional[int]
        polling_interval: Optional[int]
        rules: Optional[list[JobScaleRule]]

        @overload
        def __init__(
                self, 
                *, 
                max_executions: Optional[int] = ..., 
                min_executions: Optional[int] = ..., 
                polling_interval: Optional[int] = ..., 
                rules: Optional[list[JobScaleRule]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.JobScaleRule(_Model):
        auth: Optional[list[ScaleRuleAuth]]
        identity: Optional[str]
        metadata: Optional[Any]
        name: Optional[str]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                auth: Optional[list[ScaleRuleAuth]] = ..., 
                identity: Optional[str] = ..., 
                metadata: Optional[Any] = ..., 
                name: Optional[str] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.JobSecretsCollection(_Model):
        value: list[Secret]

        @overload
        def __init__(
                self, 
                *, 
                value: list[Secret]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.JobTemplate(_Model):
        containers: Optional[list[Container]]
        init_containers: Optional[list[InitContainer]]
        volumes: Optional[list[Volume]]

        @overload
        def __init__(
                self, 
                *, 
                containers: Optional[list[Container]] = ..., 
                init_containers: Optional[list[InitContainer]] = ..., 
                volumes: Optional[list[Volume]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.JwtClaimChecks(_Model):
        allowed_client_applications: Optional[list[str]]
        allowed_groups: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                allowed_client_applications: Optional[list[str]] = ..., 
                allowed_groups: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.KedaConfiguration(_Model):
        version: Optional[str]


    class azure.mgmt.appcontainers.models.Kind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FUNCTIONAPP = "functionapp"
        WORKFLOWAPP = "workflowapp"


    class azure.mgmt.appcontainers.models.LabelHistory(ProxyResource):
        id: str
        name: str
        properties: Optional[LabelHistoryProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[LabelHistoryProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.LabelHistoryProperties(_Model):
        records: Optional[list[LabelHistoryRecordItem]]


    class azure.mgmt.appcontainers.models.LabelHistoryRecordItem(_Model):
        revision: Optional[str]
        start: Optional[datetime]
        status: Optional[Union[str, Status]]
        stop: Optional[datetime]


    class azure.mgmt.appcontainers.models.LifecycleConfiguration(_Model):
        cooldown_period_in_seconds: Optional[int]
        lifecycle_type: Optional[Union[str, LifecycleType]]
        max_alive_period_in_seconds: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                cooldown_period_in_seconds: Optional[int] = ..., 
                lifecycle_type: Optional[Union[str, LifecycleType]] = ..., 
                max_alive_period_in_seconds: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.LifecycleType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ON_CONTAINER_EXIT = "OnContainerExit"
        TIMED = "Timed"


    class azure.mgmt.appcontainers.models.LogAnalyticsConfiguration(_Model):
        customer_id: Optional[str]
        shared_key: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                customer_id: Optional[str] = ..., 
                shared_key: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.LogLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEBUG = "debug"
        ERROR = "error"
        INFO = "info"
        WARN = "warn"


    class azure.mgmt.appcontainers.models.LogicApp(ProxyResource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.appcontainers.models.Login(_Model):
        allowed_external_redirect_urls: Optional[list[str]]
        cookie_expiration: Optional[CookieExpiration]
        nonce: Optional[Nonce]
        preserve_url_fragments_for_logins: Optional[bool]
        routes: Optional[LoginRoutes]
        token_store: Optional[TokenStore]

        @overload
        def __init__(
                self, 
                *, 
                allowed_external_redirect_urls: Optional[list[str]] = ..., 
                cookie_expiration: Optional[CookieExpiration] = ..., 
                nonce: Optional[Nonce] = ..., 
                preserve_url_fragments_for_logins: Optional[bool] = ..., 
                routes: Optional[LoginRoutes] = ..., 
                token_store: Optional[TokenStore] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.LoginRoutes(_Model):
        logout_endpoint: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                logout_endpoint: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.LoginScopes(_Model):
        scopes: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                scopes: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.LogsConfiguration(_Model):
        destinations: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                destinations: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.MaintenanceConfigurationResource(ProxyResource):
        id: str
        name: str
        properties: Optional[ScheduledEntries]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ScheduledEntries] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.appcontainers.models.ManagedCertificate(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[ManagedCertificateProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[ManagedCertificateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.ManagedCertificateDomainControlValidation(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CNAME = "CNAME"
        HTTP = "HTTP"
        TXT = "TXT"


    class azure.mgmt.appcontainers.models.ManagedCertificatePatch(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.ManagedCertificateProperties(_Model):
        domain_control_validation: Optional[Union[str, ManagedCertificateDomainControlValidation]]
        error: Optional[str]
        provisioning_state: Optional[Union[str, CertificateProvisioningState]]
        subject_name: Optional[str]
        validation_token: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                domain_control_validation: Optional[Union[str, ManagedCertificateDomainControlValidation]] = ..., 
                subject_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.ManagedEnvironment(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        kind: Optional[str]
        location: str
        name: str
        properties: Optional[ManagedEnvironmentProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                kind: Optional[str] = ..., 
                location: str, 
                properties: Optional[ManagedEnvironmentProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.appcontainers.models.ManagedEnvironmentMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARCHIVED = "Archived"
        CONSUMPTION_ONLY = "ConsumptionOnly"
        EXPRESS = "Express"
        WORKLOAD_PROFILES = "WorkloadProfiles"


    class azure.mgmt.appcontainers.models.ManagedEnvironmentProperties(_Model):
        app_insights_configuration: Optional[AppInsightsConfiguration]
        app_logs_configuration: Optional[AppLogsConfiguration]
        custom_domain_configuration: Optional[CustomDomainConfiguration]
        dapr_ai_connection_string: Optional[str]
        dapr_ai_instrumentation_key: Optional[str]
        dapr_configuration: Optional[DaprConfiguration]
        default_domain: Optional[str]
        deployment_errors: Optional[str]
        environment_mode: Optional[Union[str, ManagedEnvironmentMode]]
        event_stream_endpoint: Optional[str]
        infrastructure_resource_group: Optional[str]
        ingress_configuration: Optional[IngressConfiguration]
        keda_configuration: Optional[KedaConfiguration]
        open_telemetry_configuration: Optional[OpenTelemetryConfiguration]
        peer_authentication: Optional[ManagedEnvironmentPropertiesPeerAuthentication]
        peer_traffic_configuration: Optional[ManagedEnvironmentPropertiesPeerTrafficConfiguration]
        private_endpoint_connections: Optional[list[PrivateEndpointConnection]]
        provisioning_state: Optional[Union[str, EnvironmentProvisioningState]]
        public_network_access: Optional[Union[str, PublicNetworkAccess]]
        static_ip: Optional[str]
        vnet_configuration: Optional[VnetConfiguration]
        workload_profiles: Optional[list[WorkloadProfile]]
        zone_redundant: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                app_insights_configuration: Optional[AppInsightsConfiguration] = ..., 
                app_logs_configuration: Optional[AppLogsConfiguration] = ..., 
                custom_domain_configuration: Optional[CustomDomainConfiguration] = ..., 
                dapr_ai_connection_string: Optional[str] = ..., 
                dapr_ai_instrumentation_key: Optional[str] = ..., 
                dapr_configuration: Optional[DaprConfiguration] = ..., 
                environment_mode: Optional[Union[str, ManagedEnvironmentMode]] = ..., 
                infrastructure_resource_group: Optional[str] = ..., 
                ingress_configuration: Optional[IngressConfiguration] = ..., 
                keda_configuration: Optional[KedaConfiguration] = ..., 
                open_telemetry_configuration: Optional[OpenTelemetryConfiguration] = ..., 
                peer_authentication: Optional[ManagedEnvironmentPropertiesPeerAuthentication] = ..., 
                peer_traffic_configuration: Optional[ManagedEnvironmentPropertiesPeerTrafficConfiguration] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                vnet_configuration: Optional[VnetConfiguration] = ..., 
                workload_profiles: Optional[list[WorkloadProfile]] = ..., 
                zone_redundant: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.ManagedEnvironmentPropertiesPeerAuthentication(_Model):
        mtls: Optional[Mtls]

        @overload
        def __init__(
                self, 
                *, 
                mtls: Optional[Mtls] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.ManagedEnvironmentPropertiesPeerTrafficConfiguration(_Model):
        encryption: Optional[ManagedEnvironmentPropertiesPeerTrafficConfigurationEncryption]

        @overload
        def __init__(
                self, 
                *, 
                encryption: Optional[ManagedEnvironmentPropertiesPeerTrafficConfigurationEncryption] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.ManagedEnvironmentPropertiesPeerTrafficConfigurationEncryption(_Model):
        enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.ManagedEnvironmentStorage(ProxyResource):
        id: str
        name: str
        properties: Optional[ManagedEnvironmentStorageProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ManagedEnvironmentStorageProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.ManagedEnvironmentStorageProperties(_Model):
        azure_file: Optional[AzureFileProperties]
        nfs_azure_file: Optional[NfsAzureFileProperties]

        @overload
        def __init__(
                self, 
                *, 
                azure_file: Optional[AzureFileProperties] = ..., 
                nfs_azure_file: Optional[NfsAzureFileProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.ManagedEnvironmentStoragesCollection(_Model):
        value: list[ManagedEnvironmentStorage]

        @overload
        def __init__(
                self, 
                *, 
                value: list[ManagedEnvironmentStorage]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.ManagedIdentitySetting(_Model):
        identity: str
        lifecycle: Optional[Union[str, SessionPoolIdentityLifeCycle]]

        @overload
        def __init__(
                self, 
                *, 
                identity: str, 
                lifecycle: Optional[Union[str, SessionPoolIdentityLifeCycle]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.ManagedServiceIdentity(_Model):
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


    class azure.mgmt.appcontainers.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.appcontainers.models.MetricsConfiguration(_Model):
        destinations: Optional[list[str]]
        include_keda: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                destinations: Optional[list[str]] = ..., 
                include_keda: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.MigrationEligibilityFailureReason(_Model):
        code: str
        message: str

        @overload
        def __init__(
                self, 
                *, 
                code: str, 
                message: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.Mtls(_Model):
        enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.NfsAzureFileProperties(_Model):
        access_mode: Optional[Union[str, AccessMode]]
        server: Optional[str]
        share_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                access_mode: Optional[Union[str, AccessMode]] = ..., 
                server: Optional[str] = ..., 
                share_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.Nonce(_Model):
        nonce_expiration_interval: Optional[str]
        validate_nonce: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                nonce_expiration_interval: Optional[str] = ..., 
                validate_nonce: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.OpenIdConnectClientCredential(_Model):
        client_secret_setting_name: Optional[str]
        method: Optional[Literal["ClientSecretPost"]]

        @overload
        def __init__(
                self, 
                *, 
                client_secret_setting_name: Optional[str] = ..., 
                method: Optional[Literal[ClientSecretPost]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.OpenIdConnectConfig(_Model):
        authorization_endpoint: Optional[str]
        certification_uri: Optional[str]
        issuer: Optional[str]
        token_endpoint: Optional[str]
        well_known_open_id_configuration: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                authorization_endpoint: Optional[str] = ..., 
                certification_uri: Optional[str] = ..., 
                issuer: Optional[str] = ..., 
                token_endpoint: Optional[str] = ..., 
                well_known_open_id_configuration: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.OpenIdConnectLogin(_Model):
        name_claim_type: Optional[str]
        scopes: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                name_claim_type: Optional[str] = ..., 
                scopes: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.OpenIdConnectRegistration(_Model):
        client_credential: Optional[OpenIdConnectClientCredential]
        client_id: Optional[str]
        open_id_connect_configuration: Optional[OpenIdConnectConfig]

        @overload
        def __init__(
                self, 
                *, 
                client_credential: Optional[OpenIdConnectClientCredential] = ..., 
                client_id: Optional[str] = ..., 
                open_id_connect_configuration: Optional[OpenIdConnectConfig] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.OpenTelemetryConfiguration(_Model):
        destinations_configuration: Optional[DestinationsConfiguration]
        logs_configuration: Optional[LogsConfiguration]
        metrics_configuration: Optional[MetricsConfiguration]
        traces_configuration: Optional[TracesConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                destinations_configuration: Optional[DestinationsConfiguration] = ..., 
                logs_configuration: Optional[LogsConfiguration] = ..., 
                metrics_configuration: Optional[MetricsConfiguration] = ..., 
                traces_configuration: Optional[TracesConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.OperationDetail(_Model):
        display: Optional[OperationDisplay]
        is_data_action: Optional[bool]
        name: Optional[str]
        origin: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
                is_data_action: Optional[bool] = ..., 
                name: Optional[str] = ..., 
                origin: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.OperationDisplay(_Model):
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


    class azure.mgmt.appcontainers.models.OtlpConfiguration(_Model):
        endpoint: Optional[str]
        headers: Optional[list[Header]]
        insecure: Optional[bool]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                endpoint: Optional[str] = ..., 
                headers: Optional[list[Header]] = ..., 
                insecure: Optional[bool] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.PoolManagementType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DYNAMIC = "Dynamic"
        MANUAL = "Manual"


    class azure.mgmt.appcontainers.models.PrivateEndpoint(_Model):
        id: Optional[str]


    class azure.mgmt.appcontainers.models.PrivateEndpointConnection(ProxyResource):
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


    class azure.mgmt.appcontainers.models.PrivateEndpointConnectionProperties(_Model):
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


    class azure.mgmt.appcontainers.models.PrivateEndpointConnectionProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        PENDING = "Pending"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"
        WAITING = "Waiting"


    class azure.mgmt.appcontainers.models.PrivateEndpointServiceConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        DISCONNECTED = "Disconnected"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.appcontainers.models.PrivateLinkResource(Resource):
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


    class azure.mgmt.appcontainers.models.PrivateLinkResourceProperties(_Model):
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


    class azure.mgmt.appcontainers.models.PrivateLinkServiceConnectionState(_Model):
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


    class azure.mgmt.appcontainers.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.appcontainers.models.PublicNetworkAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.appcontainers.models.QueueScaleRule(_Model):
        account_name: Optional[str]
        auth: Optional[list[ScaleRuleAuth]]
        identity: Optional[str]
        queue_length: Optional[int]
        queue_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                account_name: Optional[str] = ..., 
                auth: Optional[list[ScaleRuleAuth]] = ..., 
                identity: Optional[str] = ..., 
                queue_length: Optional[int] = ..., 
                queue_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.RegistryCredentials(_Model):
        identity: Optional[str]
        password_secret_ref: Optional[str]
        server: Optional[str]
        username: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[str] = ..., 
                password_secret_ref: Optional[str] = ..., 
                server: Optional[str] = ..., 
                username: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.RegistryInfo(_Model):
        registry_password: Optional[str]
        registry_url: Optional[str]
        registry_user_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                registry_password: Optional[str] = ..., 
                registry_url: Optional[str] = ..., 
                registry_user_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.Replica(ProxyResource):
        id: str
        name: str
        properties: Optional[ReplicaProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ReplicaProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.appcontainers.models.ReplicaCollection(_Model):
        value: list[Replica]

        @overload
        def __init__(
                self, 
                *, 
                value: list[Replica]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.ReplicaContainer(_Model):
        container_id: Optional[str]
        debug_endpoint: Optional[str]
        exec_endpoint: Optional[str]
        log_stream_endpoint: Optional[str]
        name: Optional[str]
        ready: Optional[bool]
        restart_count: Optional[int]
        running_state: Optional[Union[str, ContainerAppContainerRunningState]]
        running_state_details: Optional[str]
        started: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                container_id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                ready: Optional[bool] = ..., 
                restart_count: Optional[int] = ..., 
                started: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.ReplicaExecutionStatus(_Model):
        containers: Optional[list[ContainerExecutionStatus]]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                containers: Optional[list[ContainerExecutionStatus]] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.ReplicaProperties(_Model):
        containers: Optional[list[ReplicaContainer]]
        created_time: Optional[datetime]
        init_containers: Optional[list[ReplicaContainer]]
        running_state: Optional[Union[str, ContainerAppReplicaRunningState]]
        running_state_details: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                containers: Optional[list[ReplicaContainer]] = ..., 
                init_containers: Optional[list[ReplicaContainer]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.appcontainers.models.ResourceTags(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.Revision(ProxyResource):
        id: str
        name: str
        properties: Optional[RevisionProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RevisionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.appcontainers.models.RevisionHealthState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HEALTHY = "Healthy"
        NONE = "None"
        UNHEALTHY = "Unhealthy"


    class azure.mgmt.appcontainers.models.RevisionProperties(_Model):
        active: Optional[bool]
        created_time: Optional[datetime]
        fqdn: Optional[str]
        health_state: Optional[Union[str, RevisionHealthState]]
        last_active_time: Optional[datetime]
        provisioning_error: Optional[str]
        provisioning_state: Optional[Union[str, RevisionProvisioningState]]
        replicas: Optional[int]
        running_state: Optional[Union[str, RevisionRunningState]]
        template: Optional[Template]
        traffic_weight: Optional[int]


    class azure.mgmt.appcontainers.models.RevisionProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEPROVISIONED = "Deprovisioned"
        DEPROVISIONING = "Deprovisioning"
        FAILED = "Failed"
        PROVISIONED = "Provisioned"
        PROVISIONING = "Provisioning"


    class azure.mgmt.appcontainers.models.RevisionRunningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEGRADED = "Degraded"
        FAILED = "Failed"
        PROCESSING = "Processing"
        RUNNING = "Running"
        STOPPED = "Stopped"
        UNKNOWN = "Unknown"


    class azure.mgmt.appcontainers.models.Runtime(_Model):
        java: Optional[RuntimeJava]

        @overload
        def __init__(
                self, 
                *, 
                java: Optional[RuntimeJava] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.RuntimeJava(_Model):
        enable_metrics: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                enable_metrics: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.SandboxGroup(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[SandboxGroupProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[SandboxGroupProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.SandboxGroupPatch(_Model):
        properties: Optional[SandboxGroupPatchProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SandboxGroupPatchProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.SandboxGroupPatchProperties(_Model):
        environment_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                environment_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.SandboxGroupProperties(_Model):
        default_domain: Optional[str]
        environment_id: Optional[str]
        provisioning_state: Optional[Union[str, SandboxGroupProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                environment_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.SandboxGroupProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.appcontainers.models.Scale(_Model):
        allow_scaling_rule_override: Optional[bool]
        cooldown_period: Optional[int]
        max_replicas: Optional[int]
        min_replicas: Optional[int]
        polling_interval: Optional[int]
        rules: Optional[list[ScaleRule]]

        @overload
        def __init__(
                self, 
                *, 
                allow_scaling_rule_override: Optional[bool] = ..., 
                cooldown_period: Optional[int] = ..., 
                max_replicas: Optional[int] = ..., 
                min_replicas: Optional[int] = ..., 
                polling_interval: Optional[int] = ..., 
                rules: Optional[list[ScaleRule]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.ScaleConfiguration(_Model):
        max_concurrent_sessions: Optional[int]
        ready_session_instances: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                max_concurrent_sessions: Optional[int] = ..., 
                ready_session_instances: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.ScaleRule(_Model):
        azure_queue: Optional[QueueScaleRule]
        custom: Optional[CustomScaleRule]
        http: Optional[HttpScaleRule]
        name: Optional[str]
        tcp: Optional[TcpScaleRule]

        @overload
        def __init__(
                self, 
                *, 
                azure_queue: Optional[QueueScaleRule] = ..., 
                custom: Optional[CustomScaleRule] = ..., 
                http: Optional[HttpScaleRule] = ..., 
                name: Optional[str] = ..., 
                tcp: Optional[TcpScaleRule] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.ScaleRuleAuth(_Model):
        secret_ref: Optional[str]
        trigger_parameter: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                secret_ref: Optional[str] = ..., 
                trigger_parameter: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.ScheduledEntries(_Model):
        scheduled_entries: list[ScheduledEntry]

        @overload
        def __init__(
                self, 
                *, 
                scheduled_entries: list[ScheduledEntry]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.ScheduledEntry(_Model):
        duration_hours: int
        start_hour_utc: int
        week_day: Union[str, WeekDay]

        @overload
        def __init__(
                self, 
                *, 
                duration_hours: int, 
                start_hour_utc: int, 
                week_day: Union[str, WeekDay]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.Scheme(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HTTP = "HTTP"
        HTTPS = "HTTPS"


    class azure.mgmt.appcontainers.models.Secret(_Model):
        identity: Optional[str]
        key_vault_url: Optional[str]
        name: Optional[str]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[str] = ..., 
                key_vault_url: Optional[str] = ..., 
                name: Optional[str] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.SecretKeyVaultProperties(_Model):
        identity: Optional[str]
        key_vault_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[str] = ..., 
                key_vault_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.SecretVolumeItem(_Model):
        path: Optional[str]
        secret_ref: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                path: Optional[str] = ..., 
                secret_ref: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.SecretsCollection(_Model):
        value: list[ContainerAppSecret]

        @overload
        def __init__(
                self, 
                *, 
                value: list[ContainerAppSecret]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.Service(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.ServiceBind(_Model):
        name: Optional[str]
        service_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                service_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.SessionContainer(_Model):
        args: Optional[list[str]]
        command: Optional[list[str]]
        env: Optional[list[EnvironmentVar]]
        image: Optional[str]
        name: Optional[str]
        probes: Optional[list[SessionProbe]]
        resources: Optional[SessionContainerResources]

        @overload
        def __init__(
                self, 
                *, 
                args: Optional[list[str]] = ..., 
                command: Optional[list[str]] = ..., 
                env: Optional[list[EnvironmentVar]] = ..., 
                image: Optional[str] = ..., 
                name: Optional[str] = ..., 
                probes: Optional[list[SessionProbe]] = ..., 
                resources: Optional[SessionContainerResources] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.SessionContainerResources(_Model):
        cpu: Optional[float]
        memory: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                cpu: Optional[float] = ..., 
                memory: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.SessionIngress(_Model):
        target_port: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                target_port: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.SessionNetworkConfiguration(_Model):
        status: Optional[Union[str, SessionNetworkStatus]]

        @overload
        def __init__(
                self, 
                *, 
                status: Optional[Union[str, SessionNetworkStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.SessionNetworkStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EGRESS_DISABLED = "EgressDisabled"
        EGRESS_ENABLED = "EgressEnabled"


    class azure.mgmt.appcontainers.models.SessionPool(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: Optional[SessionPoolProperties]
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
                properties: Optional[SessionPoolProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.appcontainers.models.SessionPoolIdentityLifeCycle(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MAIN = "Main"
        NONE = "None"


    class azure.mgmt.appcontainers.models.SessionPoolProperties(_Model):
        container_type: Optional[Union[str, ContainerType]]
        custom_container_template: Optional[CustomContainerTemplate]
        dynamic_pool_configuration: Optional[DynamicPoolConfiguration]
        environment_id: Optional[str]
        managed_identity_settings: Optional[list[ManagedIdentitySetting]]
        node_count: Optional[int]
        pool_management_endpoint: Optional[str]
        pool_management_type: Optional[Union[str, PoolManagementType]]
        provisioning_state: Optional[Union[str, SessionPoolProvisioningState]]
        scale_configuration: Optional[ScaleConfiguration]
        secrets: Optional[list[SessionPoolSecret]]
        session_network_configuration: Optional[SessionNetworkConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                container_type: Optional[Union[str, ContainerType]] = ..., 
                custom_container_template: Optional[CustomContainerTemplate] = ..., 
                dynamic_pool_configuration: Optional[DynamicPoolConfiguration] = ..., 
                environment_id: Optional[str] = ..., 
                managed_identity_settings: Optional[list[ManagedIdentitySetting]] = ..., 
                pool_management_type: Optional[Union[str, PoolManagementType]] = ..., 
                scale_configuration: Optional[ScaleConfiguration] = ..., 
                secrets: Optional[list[SessionPoolSecret]] = ..., 
                session_network_configuration: Optional[SessionNetworkConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.SessionPoolProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.appcontainers.models.SessionPoolSecret(_Model):
        name: Optional[str]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.SessionPoolUpdatableProperties(_Model):
        identity: Optional[ManagedServiceIdentity]
        properties: Optional[SessionPoolUpdatablePropertiesProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                properties: Optional[SessionPoolUpdatablePropertiesProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.appcontainers.models.SessionPoolUpdatablePropertiesProperties(_Model):
        custom_container_template: Optional[CustomContainerTemplate]
        dynamic_pool_configuration: Optional[DynamicPoolConfiguration]
        scale_configuration: Optional[ScaleConfiguration]
        secrets: Optional[list[SessionPoolSecret]]
        session_network_configuration: Optional[SessionNetworkConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                custom_container_template: Optional[CustomContainerTemplate] = ..., 
                dynamic_pool_configuration: Optional[DynamicPoolConfiguration] = ..., 
                scale_configuration: Optional[ScaleConfiguration] = ..., 
                secrets: Optional[list[SessionPoolSecret]] = ..., 
                session_network_configuration: Optional[SessionNetworkConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.SessionProbe(_Model):
        failure_threshold: Optional[int]
        http_get: Optional[SessionProbeHttpGet]
        initial_delay_seconds: Optional[int]
        period_seconds: Optional[int]
        success_threshold: Optional[int]
        tcp_socket: Optional[SessionProbeTcpSocket]
        termination_grace_period_seconds: Optional[int]
        timeout_seconds: Optional[int]
        type: Optional[Union[str, SessionProbeType]]

        @overload
        def __init__(
                self, 
                *, 
                failure_threshold: Optional[int] = ..., 
                http_get: Optional[SessionProbeHttpGet] = ..., 
                initial_delay_seconds: Optional[int] = ..., 
                period_seconds: Optional[int] = ..., 
                success_threshold: Optional[int] = ..., 
                tcp_socket: Optional[SessionProbeTcpSocket] = ..., 
                termination_grace_period_seconds: Optional[int] = ..., 
                timeout_seconds: Optional[int] = ..., 
                type: Optional[Union[str, SessionProbeType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.SessionProbeHttpGet(_Model):
        host: Optional[str]
        http_headers: Optional[list[SessionProbeHttpGetHttpHeadersItem]]
        path: Optional[str]
        port: int
        scheme: Optional[Union[str, Scheme]]

        @overload
        def __init__(
                self, 
                *, 
                host: Optional[str] = ..., 
                http_headers: Optional[list[SessionProbeHttpGetHttpHeadersItem]] = ..., 
                path: Optional[str] = ..., 
                port: int, 
                scheme: Optional[Union[str, Scheme]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.SessionProbeHttpGetHttpHeadersItem(_Model):
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


    class azure.mgmt.appcontainers.models.SessionProbeTcpSocket(_Model):
        host: Optional[str]
        port: int

        @overload
        def __init__(
                self, 
                *, 
                host: Optional[str] = ..., 
                port: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.SessionProbeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LIVENESS = "Liveness"
        STARTUP = "Startup"


    class azure.mgmt.appcontainers.models.SessionRegistryCredentials(_Model):
        identity: Optional[str]
        password_secret_ref: Optional[str]
        server: Optional[str]
        username: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[str] = ..., 
                password_secret_ref: Optional[str] = ..., 
                server: Optional[str] = ..., 
                username: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.SourceControl(ProxyResource):
        id: str
        name: str
        properties: Optional[SourceControlProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SourceControlProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.appcontainers.models.SourceControlOperationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.appcontainers.models.SourceControlProperties(_Model):
        branch: Optional[str]
        github_action_configuration: Optional[GithubActionConfiguration]
        operation_state: Optional[Union[str, SourceControlOperationState]]
        repo_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                branch: Optional[str] = ..., 
                github_action_configuration: Optional[GithubActionConfiguration] = ..., 
                repo_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.SpringBootAdminComponent(JavaComponentProperties, discriminator='SpringBootAdmin'):
        component_type: Literal[JavaComponentType.SPRING_BOOT_ADMIN]
        configurations: list[JavaComponentConfigurationProperty]
        ingress: Optional[JavaComponentIngress]
        provisioning_state: Union[str, JavaComponentProvisioningState]
        scale: JavaComponentPropertiesScale
        service_binds: list[JavaComponentServiceBind]

        @overload
        def __init__(
                self, 
                *, 
                configurations: Optional[list[JavaComponentConfigurationProperty]] = ..., 
                ingress: Optional[JavaComponentIngress] = ..., 
                scale: Optional[JavaComponentPropertiesScale] = ..., 
                service_binds: Optional[list[JavaComponentServiceBind]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.SpringCloudConfigComponent(JavaComponentProperties, discriminator='SpringCloudConfig'):
        component_type: Literal[JavaComponentType.SPRING_CLOUD_CONFIG]
        configurations: list[JavaComponentConfigurationProperty]
        provisioning_state: Union[str, JavaComponentProvisioningState]
        scale: JavaComponentPropertiesScale
        service_binds: list[JavaComponentServiceBind]

        @overload
        def __init__(
                self, 
                *, 
                configurations: Optional[list[JavaComponentConfigurationProperty]] = ..., 
                scale: Optional[JavaComponentPropertiesScale] = ..., 
                service_binds: Optional[list[JavaComponentServiceBind]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.SpringCloudEurekaComponent(JavaComponentProperties, discriminator='SpringCloudEureka'):
        component_type: Literal[JavaComponentType.SPRING_CLOUD_EUREKA]
        configurations: list[JavaComponentConfigurationProperty]
        ingress: Optional[JavaComponentIngress]
        provisioning_state: Union[str, JavaComponentProvisioningState]
        scale: JavaComponentPropertiesScale
        service_binds: list[JavaComponentServiceBind]

        @overload
        def __init__(
                self, 
                *, 
                configurations: Optional[list[JavaComponentConfigurationProperty]] = ..., 
                ingress: Optional[JavaComponentIngress] = ..., 
                scale: Optional[JavaComponentPropertiesScale] = ..., 
                service_binds: Optional[list[JavaComponentServiceBind]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.Status(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        STARTING = "Starting"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.appcontainers.models.StorageType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_FILE = "AzureFile"
        EMPTY_DIR = "EmptyDir"
        NFS_AZURE_FILE = "NfsAzureFile"
        SECRET = "Secret"


    class azure.mgmt.appcontainers.models.SystemData(_Model):
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


    class azure.mgmt.appcontainers.models.TcpScaleRule(_Model):
        auth: Optional[list[ScaleRuleAuth]]
        identity: Optional[str]
        metadata: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                auth: Optional[list[ScaleRuleAuth]] = ..., 
                identity: Optional[str] = ..., 
                metadata: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.Template(_Model):
        containers: Optional[list[Container]]
        init_containers: Optional[list[InitContainer]]
        revision_suffix: Optional[str]
        scale: Optional[Scale]
        service_binds: Optional[list[ServiceBind]]
        termination_grace_period_seconds: Optional[int]
        volumes: Optional[list[Volume]]

        @overload
        def __init__(
                self, 
                *, 
                containers: Optional[list[Container]] = ..., 
                init_containers: Optional[list[InitContainer]] = ..., 
                revision_suffix: Optional[str] = ..., 
                scale: Optional[Scale] = ..., 
                service_binds: Optional[list[ServiceBind]] = ..., 
                termination_grace_period_seconds: Optional[int] = ..., 
                volumes: Optional[list[Volume]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.TokenStore(_Model):
        azure_blob_storage: Optional[BlobStorageTokenStore]
        enabled: Optional[bool]
        token_refresh_extension_hours: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                azure_blob_storage: Optional[BlobStorageTokenStore] = ..., 
                enabled: Optional[bool] = ..., 
                token_refresh_extension_hours: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.TracesConfiguration(_Model):
        destinations: Optional[list[str]]
        include_dapr: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                destinations: Optional[list[str]] = ..., 
                include_dapr: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.TrackedResource(Resource):
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


    class azure.mgmt.appcontainers.models.TrafficWeight(_Model):
        label: Optional[str]
        latest_revision: Optional[bool]
        revision_name: Optional[str]
        weight: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                label: Optional[str] = ..., 
                latest_revision: Optional[bool] = ..., 
                revision_name: Optional[str] = ..., 
                weight: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.TriggerType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EVENT = "Event"
        MANUAL = "Manual"
        SCHEDULE = "Schedule"


    class azure.mgmt.appcontainers.models.Twitter(_Model):
        enabled: Optional[bool]
        registration: Optional[TwitterRegistration]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                registration: Optional[TwitterRegistration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.TwitterRegistration(_Model):
        consumer_key: Optional[str]
        consumer_secret_setting_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                consumer_key: Optional[str] = ..., 
                consumer_secret_setting_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.Type(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LIVENESS = "Liveness"
        READINESS = "Readiness"
        STARTUP = "Startup"


    class azure.mgmt.appcontainers.models.UnauthenticatedClientActionV2(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW_ANONYMOUS = "AllowAnonymous"
        REDIRECT_TO_LOGIN_PAGE = "RedirectToLoginPage"
        RETURN401 = "Return401"
        RETURN403 = "Return403"


    class azure.mgmt.appcontainers.models.Usage(_Model):
        current_value: float
        limit: float
        name: UsageName
        unit: Literal["Count"]

        @overload
        def __init__(
                self, 
                *, 
                current_value: float, 
                limit: float, 
                name: UsageName
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.UsageName(_Model):
        localized_value: Optional[str]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                localized_value: Optional[str] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.appcontainers.models.VnetConfiguration(_Model):
        docker_bridge_cidr: Optional[str]
        infrastructure_subnet_id: Optional[str]
        internal: Optional[bool]
        platform_reserved_cidr: Optional[str]
        platform_reserved_dns_ip: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                docker_bridge_cidr: Optional[str] = ..., 
                infrastructure_subnet_id: Optional[str] = ..., 
                internal: Optional[bool] = ..., 
                platform_reserved_cidr: Optional[str] = ..., 
                platform_reserved_dns_ip: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.VnetConnection(ProxyResource):
        id: str
        name: str
        properties: Optional[VnetConnectionProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[VnetConnectionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.VnetConnectionProperties(_Model):
        provisioning_state: Optional[Union[str, VnetConnectionProvisioningState]]
        subnet_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                subnet_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.VnetConnectionProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.appcontainers.models.Volume(_Model):
        mount_options: Optional[str]
        name: Optional[str]
        secrets: Optional[list[SecretVolumeItem]]
        storage_name: Optional[str]
        storage_type: Optional[Union[str, StorageType]]

        @overload
        def __init__(
                self, 
                *, 
                mount_options: Optional[str] = ..., 
                name: Optional[str] = ..., 
                secrets: Optional[list[SecretVolumeItem]] = ..., 
                storage_name: Optional[str] = ..., 
                storage_type: Optional[Union[str, StorageType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.VolumeMount(_Model):
        mount_path: Optional[str]
        sub_path: Optional[str]
        volume_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                mount_path: Optional[str] = ..., 
                sub_path: Optional[str] = ..., 
                volume_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.WeekDay(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FRIDAY = "Friday"
        MONDAY = "Monday"
        SATURDAY = "Saturday"
        SUNDAY = "Sunday"
        THURSDAY = "Thursday"
        TUESDAY = "Tuesday"
        WEDNESDAY = "Wednesday"


    class azure.mgmt.appcontainers.models.WorkflowEnvelope(ProxyResource):
        id: str
        kind: Optional[Union[str, WorkflowKind]]
        name: str
        properties: Optional[WorkflowEnvelopeProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                kind: Optional[Union[str, WorkflowKind]] = ..., 
                properties: Optional[WorkflowEnvelopeProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.WorkflowEnvelopeProperties(_Model):
        files: Optional[Any]
        flow_state: Optional[Union[str, WorkflowState]]
        health: Optional[WorkflowHealth]

        @overload
        def __init__(
                self, 
                *, 
                files: Optional[Any] = ..., 
                flow_state: Optional[Union[str, WorkflowState]] = ..., 
                health: Optional[WorkflowHealth] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.WorkflowHealth(_Model):
        error: Optional[ErrorEntity]
        state: Union[str, WorkflowHealthState]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorEntity] = ..., 
                state: Union[str, WorkflowHealthState]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.WorkflowHealthState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HEALTHY = "Healthy"
        NOT_SPECIFIED = "NotSpecified"
        UNHEALTHY = "Unhealthy"
        UNKNOWN = "Unknown"


    class azure.mgmt.appcontainers.models.WorkflowKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AGENTIC = "Agentic"
        STATEFUL = "Stateful"
        STATELESS = "Stateless"


    class azure.mgmt.appcontainers.models.WorkflowState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "Completed"
        DELETED = "Deleted"
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        NOT_SPECIFIED = "NotSpecified"
        SUSPENDED = "Suspended"


    class azure.mgmt.appcontainers.models.WorkloadProfile(_Model):
        maximum_count: Optional[int]
        minimum_count: Optional[int]
        name: str
        workload_profile_type: str

        @overload
        def __init__(
                self, 
                *, 
                maximum_count: Optional[int] = ..., 
                minimum_count: Optional[int] = ..., 
                name: str, 
                workload_profile_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.WorkloadProfileStates(ProxyResource):
        id: str
        name: str
        properties: Optional[WorkloadProfileStatesProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[WorkloadProfileStatesProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appcontainers.models.WorkloadProfileStatesProperties(_Model):
        current_count: Optional[int]
        maximum_count: Optional[int]
        minimum_count: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                current_count: Optional[int] = ..., 
                maximum_count: Optional[int] = ..., 
                minimum_count: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.appcontainers.operations

    class azure.mgmt.appcontainers.operations.AvailableEnvironmentModesOperations:

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
            ) -> ItemPaged[AvailableEnvironmentMode]: ...


    class azure.mgmt.appcontainers.operations.AvailableWorkloadProfilesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[AvailableWorkloadProfile]: ...


    class azure.mgmt.appcontainers.operations.BillingMetersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                **kwargs: Any
            ) -> BillingMeterCollection: ...


    class azure.mgmt.appcontainers.operations.CertificatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                certificate_name: str, 
                certificate_envelope: Optional[Certificate] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Certificate: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                certificate_name: str, 
                certificate_envelope: Optional[Certificate] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Certificate: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                certificate_name: str, 
                certificate_envelope: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Certificate: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                certificate_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                certificate_name: str, 
                **kwargs: Any
            ) -> Certificate: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Certificate]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                certificate_name: str, 
                certificate_envelope: CertificatePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Certificate: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                certificate_name: str, 
                certificate_envelope: CertificatePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Certificate: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                certificate_name: str, 
                certificate_envelope: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Certificate: ...


    class azure.mgmt.appcontainers.operations.ConnectedEnvironmentsCertificatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                certificate_name: str, 
                certificate_envelope: Optional[Certificate] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Certificate]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                certificate_name: str, 
                certificate_envelope: Optional[Certificate] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Certificate]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                certificate_name: str, 
                certificate_envelope: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Certificate]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                certificate_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                certificate_name: str, 
                certificate_envelope: CertificatePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Certificate]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                certificate_name: str, 
                certificate_envelope: CertificatePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Certificate]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                certificate_name: str, 
                certificate_envelope: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Certificate]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                certificate_name: str, 
                **kwargs: Any
            ) -> Certificate: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Certificate]: ...


    class azure.mgmt.appcontainers.operations.ConnectedEnvironmentsDaprComponentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                component_name: str, 
                dapr_component_envelope: DaprComponent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DaprComponent]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                component_name: str, 
                dapr_component_envelope: DaprComponent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DaprComponent]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                component_name: str, 
                dapr_component_envelope: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DaprComponent]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                component_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                component_name: str, 
                **kwargs: Any
            ) -> DaprComponent: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DaprComponent]: ...

        @distributed_trace
        def list_secrets(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                component_name: str, 
                **kwargs: Any
            ) -> DaprSecretsCollection: ...


    class azure.mgmt.appcontainers.operations.ConnectedEnvironmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                environment_envelope: ConnectedEnvironment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ConnectedEnvironment]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                environment_envelope: ConnectedEnvironment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ConnectedEnvironment]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                environment_envelope: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ConnectedEnvironment]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def check_name_availability(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                check_name_availability_request: CheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        def check_name_availability(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                check_name_availability_request: CheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        def check_name_availability(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                check_name_availability_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                **kwargs: Any
            ) -> ConnectedEnvironment: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ConnectedEnvironment]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[ConnectedEnvironment]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                environment_envelope: ConnectedEnvironmentPatchResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectedEnvironment: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                environment_envelope: ConnectedEnvironmentPatchResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectedEnvironment: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                environment_envelope: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectedEnvironment: ...


    class azure.mgmt.appcontainers.operations.ConnectedEnvironmentsStoragesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                storage_name: str, 
                storage_envelope: ConnectedEnvironmentStorage, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ConnectedEnvironmentStorage]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                storage_name: str, 
                storage_envelope: ConnectedEnvironmentStorage, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ConnectedEnvironmentStorage]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                storage_name: str, 
                storage_envelope: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ConnectedEnvironmentStorage]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                storage_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                storage_name: str, 
                **kwargs: Any
            ) -> ConnectedEnvironmentStorage: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                connected_environment_name: str, 
                **kwargs: Any
            ) -> ConnectedEnvironmentStoragesCollection: ...


    class azure.mgmt.appcontainers.operations.ContainerAppPrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                private_endpoint_connection_name: str, 
                private_endpoint_connection_envelope: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                private_endpoint_connection_name: str, 
                private_endpoint_connection_envelope: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                private_endpoint_connection_name: str, 
                private_endpoint_connection_envelope: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-01', params_added_on={'2026-07-01': ['api_version', 'subscription_id', 'resource_group_name', 'container_app_name', 'private_endpoint_connection_name']}, api_versions_list=['2026-07-01'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-01', params_added_on={'2026-07-01': ['api_version', 'subscription_id', 'resource_group_name', 'container_app_name', 'private_endpoint_connection_name', 'accept']}, api_versions_list=['2026-07-01'])
        def get(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-01', params_added_on={'2026-07-01': ['api_version', 'subscription_id', 'resource_group_name', 'container_app_name', 'accept']}, api_versions_list=['2026-07-01'])
        def list(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PrivateEndpointConnection]: ...


    class azure.mgmt.appcontainers.operations.ContainerAppPrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-01', params_added_on={'2026-07-01': ['api_version', 'subscription_id', 'resource_group_name', 'container_app_name', 'private_link_resource_name', 'accept']}, api_versions_list=['2026-07-01'])
        def get(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                private_link_resource_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-01', params_added_on={'2026-07-01': ['api_version', 'subscription_id', 'resource_group_name', 'container_app_name', 'accept']}, api_versions_list=['2026-07-01'])
        def list(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PrivateLinkResource]: ...


    class azure.mgmt.appcontainers.operations.ContainerAppsAuthConfigsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                auth_config_name: str, 
                auth_config_envelope: AuthConfig, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AuthConfig: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                auth_config_name: str, 
                auth_config_envelope: AuthConfig, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AuthConfig: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                auth_config_name: str, 
                auth_config_envelope: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AuthConfig: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                auth_config_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                auth_config_name: str, 
                **kwargs: Any
            ) -> AuthConfig: ...

        @distributed_trace
        def list_by_container_app(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AuthConfig]: ...


    class azure.mgmt.appcontainers.operations.ContainerAppsDiagnosticsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get_detector(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                detector_name: str, 
                **kwargs: Any
            ) -> Diagnostics: ...

        @distributed_trace
        def get_revision(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                revision_name: str, 
                **kwargs: Any
            ) -> Revision: ...

        @distributed_trace
        def get_root(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                **kwargs: Any
            ) -> ContainerApp: ...

        @distributed_trace
        def list_detectors(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Diagnostics]: ...

        @distributed_trace
        def list_revisions(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Revision]: ...


    class azure.mgmt.appcontainers.operations.ContainerAppsFunctionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-02-preview', params_added_on={'2026-03-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'container_app_name', 'function_name', 'accept']}, api_versions_list=['2026-03-02-preview', '2026-07-01'])
        def get(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                function_name: str, 
                **kwargs: Any
            ) -> ContainerAppsFunction: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-02-preview', params_added_on={'2026-03-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'container_app_name', 'accept']}, api_versions_list=['2026-03-02-preview', '2026-07-01'])
        def list(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ContainerAppsFunction]: ...


    class azure.mgmt.appcontainers.operations.ContainerAppsLabelHistoryOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-01', params_added_on={'2026-07-01': ['api_version', 'subscription_id', 'resource_group_name', 'container_app_name', 'label_name']}, api_versions_list=['2026-07-01'])
        def delete_label_history(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                label_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-01', params_added_on={'2026-07-01': ['api_version', 'subscription_id', 'resource_group_name', 'container_app_name', 'label_name', 'accept']}, api_versions_list=['2026-07-01'])
        def get_label_history(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                label_name: str, 
                **kwargs: Any
            ) -> LabelHistory: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-01', params_added_on={'2026-07-01': ['api_version', 'subscription_id', 'resource_group_name', 'container_app_name', 'filter', 'accept']}, api_versions_list=['2026-07-01'])
        def list_label_history(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[LabelHistory]: ...


    class azure.mgmt.appcontainers.operations.ContainerAppsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                container_app_envelope: ContainerApp, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ContainerApp]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                container_app_envelope: ContainerApp, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ContainerApp]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                container_app_envelope: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ContainerApp]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_start(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                **kwargs: Any
            ) -> LROPoller[ContainerApp]: ...

        @distributed_trace
        def begin_stop(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                **kwargs: Any
            ) -> LROPoller[ContainerApp]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                container_app_envelope: ContainerApp, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ContainerApp]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                container_app_envelope: ContainerApp, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ContainerApp]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                container_app_envelope: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ContainerApp]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                **kwargs: Any
            ) -> ContainerApp: ...

        @distributed_trace
        def get_auth_token(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                **kwargs: Any
            ) -> ContainerAppAuthToken: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ContainerApp]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[ContainerApp]: ...

        @distributed_trace
        def list_custom_host_name_analysis(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                *, 
                custom_hostname: Optional[str] = ..., 
                **kwargs: Any
            ) -> CustomHostnameAnalysisResult: ...

        @distributed_trace
        def list_secrets(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                **kwargs: Any
            ) -> SecretsCollection: ...


    class azure.mgmt.appcontainers.operations.ContainerAppsRevisionFunctionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                revision_name: str, 
                function_name: str, 
                **kwargs: Any
            ) -> ContainerAppsFunction: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                revision_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ContainerAppsFunction]: ...


    class azure.mgmt.appcontainers.operations.ContainerAppsRevisionReplicasOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get_replica(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                revision_name: str, 
                replica_name: str, 
                **kwargs: Any
            ) -> Replica: ...

        @distributed_trace
        def list_replicas(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                revision_name: str, 
                **kwargs: Any
            ) -> ReplicaCollection: ...


    class azure.mgmt.appcontainers.operations.ContainerAppsRevisionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def activate_revision(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                revision_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def deactivate_revision(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                revision_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get_revision(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                revision_name: str, 
                **kwargs: Any
            ) -> Revision: ...

        @distributed_trace
        def list_revisions(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Revision]: ...

        @distributed_trace
        def restart_revision(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                revision_name: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.appcontainers.operations.ContainerAppsSessionPoolsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                session_pool_name: str, 
                session_pool_envelope: SessionPool, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SessionPool]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                session_pool_name: str, 
                session_pool_envelope: SessionPool, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SessionPool]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                session_pool_name: str, 
                session_pool_envelope: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SessionPool]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                session_pool_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                session_pool_name: str, 
                session_pool_envelope: SessionPoolUpdatableProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SessionPool]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                session_pool_name: str, 
                session_pool_envelope: SessionPoolUpdatableProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SessionPool]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                session_pool_name: str, 
                session_pool_envelope: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SessionPool]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                session_pool_name: str, 
                **kwargs: Any
            ) -> SessionPool: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SessionPool]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[SessionPool]: ...


    class azure.mgmt.appcontainers.operations.ContainerAppsSourceControlsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                source_control_name: str, 
                source_control_envelope: SourceControl, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SourceControl]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                source_control_name: str, 
                source_control_envelope: SourceControl, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SourceControl]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                source_control_name: str, 
                source_control_envelope: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SourceControl]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                source_control_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                source_control_name: str, 
                **kwargs: Any
            ) -> SourceControl: ...

        @distributed_trace
        def list_by_container_app(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SourceControl]: ...


    class azure.mgmt.appcontainers.operations.DaprComponentResiliencyPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                component_name: str, 
                name: str, 
                dapr_component_resiliency_policy_envelope: DaprComponentResiliencyPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DaprComponentResiliencyPolicy: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                component_name: str, 
                name: str, 
                dapr_component_resiliency_policy_envelope: DaprComponentResiliencyPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DaprComponentResiliencyPolicy: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                component_name: str, 
                name: str, 
                dapr_component_resiliency_policy_envelope: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DaprComponentResiliencyPolicy: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-01', params_added_on={'2026-07-01': ['api_version', 'subscription_id', 'resource_group_name', 'environment_name', 'component_name', 'name']}, api_versions_list=['2026-07-01'])
        def delete(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                component_name: str, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-01', params_added_on={'2026-07-01': ['api_version', 'subscription_id', 'resource_group_name', 'environment_name', 'component_name', 'name', 'accept']}, api_versions_list=['2026-07-01'])
        def get(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                component_name: str, 
                name: str, 
                **kwargs: Any
            ) -> DaprComponentResiliencyPolicy: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-01', params_added_on={'2026-07-01': ['api_version', 'subscription_id', 'resource_group_name', 'environment_name', 'component_name', 'accept']}, api_versions_list=['2026-07-01'])
        def list(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                component_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DaprComponentResiliencyPolicy]: ...


    class azure.mgmt.appcontainers.operations.DaprComponentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                component_name: str, 
                dapr_component_envelope: DaprComponent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DaprComponent: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                component_name: str, 
                dapr_component_envelope: DaprComponent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DaprComponent: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                component_name: str, 
                dapr_component_envelope: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DaprComponent: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                component_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                component_name: str, 
                **kwargs: Any
            ) -> DaprComponent: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DaprComponent]: ...

        @distributed_trace
        def list_secrets(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                component_name: str, 
                **kwargs: Any
            ) -> DaprSecretsCollection: ...


    class azure.mgmt.appcontainers.operations.DotNetComponentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                name: str, 
                dot_net_component_envelope: DotNetComponent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DotNetComponent]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                name: str, 
                dot_net_component_envelope: DotNetComponent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DotNetComponent]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                name: str, 
                dot_net_component_envelope: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DotNetComponent]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-02-preview', params_added_on={'2026-03-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'environment_name', 'name']}, api_versions_list=['2026-03-02-preview', '2026-07-01'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                name: str, 
                dot_net_component_envelope: DotNetComponent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DotNetComponent]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                name: str, 
                dot_net_component_envelope: DotNetComponent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DotNetComponent]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                name: str, 
                dot_net_component_envelope: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DotNetComponent]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-02-preview', params_added_on={'2026-03-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'environment_name', 'name', 'accept']}, api_versions_list=['2026-03-02-preview', '2026-07-01'])
        def get(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                name: str, 
                **kwargs: Any
            ) -> DotNetComponent: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-02-preview', params_added_on={'2026-03-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'environment_name', 'accept']}, api_versions_list=['2026-03-02-preview', '2026-07-01'])
        def list(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DotNetComponent]: ...


    class azure.mgmt.appcontainers.operations.FunctionsExtensionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-01', params_added_on={'2026-07-01': ['api_version', 'subscription_id', 'resource_group_name', 'container_app_name', 'revision_name', 'function_app_name', 'accept']}, api_versions_list=['2026-07-01'])
        def invoke_functions_host(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                revision_name: str, 
                function_app_name: str, 
                **kwargs: Any
            ) -> str: ...


    class azure.mgmt.appcontainers.operations.HttpRouteConfigOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                http_route_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                http_route_name: str, 
                http_route_config_envelope: Optional[HttpRouteConfig] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HttpRouteConfig: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                http_route_name: str, 
                http_route_config_envelope: Optional[HttpRouteConfig] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HttpRouteConfig: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                http_route_name: str, 
                http_route_config_envelope: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HttpRouteConfig: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                http_route_name: str, 
                **kwargs: Any
            ) -> HttpRouteConfig: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                **kwargs: Any
            ) -> ItemPaged[HttpRouteConfig]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                http_route_name: str, 
                http_route_config_envelope: HttpRouteConfig, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HttpRouteConfig: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                http_route_name: str, 
                http_route_config_envelope: HttpRouteConfig, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HttpRouteConfig: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                http_route_name: str, 
                http_route_config_envelope: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HttpRouteConfig: ...


    class azure.mgmt.appcontainers.operations.JavaComponentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                name: str, 
                java_component_envelope: JavaComponent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[JavaComponent]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                name: str, 
                java_component_envelope: JavaComponent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[JavaComponent]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                name: str, 
                java_component_envelope: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[JavaComponent]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                name: str, 
                java_component_envelope: JavaComponent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[JavaComponent]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                name: str, 
                java_component_envelope: JavaComponent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[JavaComponent]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                name: str, 
                java_component_envelope: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[JavaComponent]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                name: str, 
                **kwargs: Any
            ) -> JavaComponent: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                **kwargs: Any
            ) -> ItemPaged[JavaComponent]: ...


    class azure.mgmt.appcontainers.operations.JobsExecutionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                job_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[JobExecution]: ...


    class azure.mgmt.appcontainers.operations.JobsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                job_name: str, 
                job_envelope: Job, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Job]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                job_name: str, 
                job_envelope: Job, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Job]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                job_name: str, 
                job_envelope: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Job]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-02-preview', params_added_on={'2026-03-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'job_name', 'accept']}, api_versions_list=['2026-03-02-preview', '2026-07-01'])
        def begin_resume(
                self, 
                resource_group_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> LROPoller[Job]: ...

        @overload
        def begin_start(
                self, 
                resource_group_name: str, 
                job_name: str, 
                template: Optional[JobExecutionTemplate] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[JobExecutionBase]: ...

        @overload
        def begin_start(
                self, 
                resource_group_name: str, 
                job_name: str, 
                template: Optional[JobExecutionTemplate] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[JobExecutionBase]: ...

        @overload
        def begin_start(
                self, 
                resource_group_name: str, 
                job_name: str, 
                template: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[JobExecutionBase]: ...

        @distributed_trace
        def begin_stop_execution(
                self, 
                resource_group_name: str, 
                job_name: str, 
                job_execution_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_stop_multiple_executions(
                self, 
                resource_group_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> LROPoller[ContainerAppJobExecutions]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-02-preview', params_added_on={'2026-03-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'job_name', 'accept']}, api_versions_list=['2026-03-02-preview', '2026-07-01'])
        def begin_suspend(
                self, 
                resource_group_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> LROPoller[Job]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                job_name: str, 
                job_envelope: JobPatchProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Job]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                job_name: str, 
                job_envelope: JobPatchProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Job]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                job_name: str, 
                job_envelope: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Job]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> Job: ...

        @distributed_trace
        def get_detector(
                self, 
                resource_group_name: str, 
                job_name: str, 
                detector_name: str, 
                **kwargs: Any
            ) -> Diagnostics: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Job]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[Job]: ...

        @distributed_trace
        def list_detectors(
                self, 
                resource_group_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Diagnostics]: ...

        @distributed_trace
        def list_secrets(
                self, 
                resource_group_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> JobSecretsCollection: ...

        @distributed_trace
        def proxy_get(
                self, 
                resource_group_name: str, 
                job_name: str, 
                api_name: str, 
                **kwargs: Any
            ) -> Job: ...


    class azure.mgmt.appcontainers.operations.LogicAppsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                logic_app_name: str, 
                resource: Optional[LogicApp] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LogicApp: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                logic_app_name: str, 
                resource: Optional[LogicApp] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LogicApp: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                logic_app_name: str, 
                resource: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LogicApp: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                logic_app_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                logic_app_name: str, 
                **kwargs: Any
            ) -> LogicApp: ...

        @distributed_trace
        def get_workflow(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                logic_app_name: str, 
                workflow_name: str, 
                **kwargs: Any
            ) -> WorkflowEnvelope: ...

        @distributed_trace
        def list_workflows(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                logic_app_name: str, 
                **kwargs: Any
            ) -> ItemPaged[WorkflowEnvelope]: ...

        @distributed_trace
        def list_workflows_connections(
                self, 
                resource_group_name: str, 
                container_app_name: str, 
                logic_app_name: str, 
                **kwargs: Any
            ) -> WorkflowEnvelope: ...


    class azure.mgmt.appcontainers.operations.MaintenanceConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                config_name: str, 
                maintenance_configuration_envelope: MaintenanceConfigurationResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MaintenanceConfigurationResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                config_name: str, 
                maintenance_configuration_envelope: MaintenanceConfigurationResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MaintenanceConfigurationResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                config_name: str, 
                maintenance_configuration_envelope: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MaintenanceConfigurationResource: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                config_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                config_name: str, 
                **kwargs: Any
            ) -> MaintenanceConfigurationResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                **kwargs: Any
            ) -> ItemPaged[MaintenanceConfigurationResource]: ...


    class azure.mgmt.appcontainers.operations.ManagedCertificatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                managed_certificate_name: str, 
                managed_certificate_envelope: Optional[ManagedCertificate] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedCertificate]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                managed_certificate_name: str, 
                managed_certificate_envelope: Optional[ManagedCertificate] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedCertificate]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                managed_certificate_name: str, 
                managed_certificate_envelope: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedCertificate]: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                managed_certificate_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                managed_certificate_name: str, 
                **kwargs: Any
            ) -> ManagedCertificate: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ManagedCertificate]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                managed_certificate_name: str, 
                managed_certificate_envelope: ManagedCertificatePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagedCertificate: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                managed_certificate_name: str, 
                managed_certificate_envelope: ManagedCertificatePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagedCertificate: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                managed_certificate_name: str, 
                managed_certificate_envelope: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagedCertificate: ...


    class azure.mgmt.appcontainers.operations.ManagedEnvironmentDiagnosticsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get_detector(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                detector_name: str, 
                **kwargs: Any
            ) -> Diagnostics: ...

        @distributed_trace
        def list_detectors(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                **kwargs: Any
            ) -> DiagnosticsCollection: ...


    class azure.mgmt.appcontainers.operations.ManagedEnvironmentPrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                private_endpoint_connection_name: str, 
                private_endpoint_connection_envelope: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                private_endpoint_connection_name: str, 
                private_endpoint_connection_envelope: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                private_endpoint_connection_name: str, 
                private_endpoint_connection_envelope: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PrivateEndpointConnection]: ...


    class azure.mgmt.appcontainers.operations.ManagedEnvironmentPrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-01', params_added_on={'2026-07-01': ['api_version', 'subscription_id', 'resource_group_name', 'environment_name', 'private_link_resource_name', 'accept']}, api_versions_list=['2026-07-01'])
        def get(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                private_link_resource_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-01', params_added_on={'2026-07-01': ['api_version', 'subscription_id', 'resource_group_name', 'environment_name', 'accept']}, api_versions_list=['2026-07-01'])
        def list(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PrivateLinkResource]: ...


    class azure.mgmt.appcontainers.operations.ManagedEnvironmentUsagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Usage]: ...


    class azure.mgmt.appcontainers.operations.ManagedEnvironmentsDiagnosticsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get_root(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                **kwargs: Any
            ) -> ManagedEnvironment: ...


    class azure.mgmt.appcontainers.operations.ManagedEnvironmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                environment_envelope: ManagedEnvironment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedEnvironment]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                environment_envelope: ManagedEnvironment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedEnvironment]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                environment_envelope: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedEnvironment]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                environment_envelope: ManagedEnvironment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedEnvironment]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                environment_envelope: ManagedEnvironment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedEnvironment]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                environment_envelope: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedEnvironment]: ...

        @overload
        def check_migration_eligibility(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                body: CheckMigrationEligibilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckMigrationEligibilityResponse: ...

        @overload
        def check_migration_eligibility(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                body: CheckMigrationEligibilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckMigrationEligibilityResponse: ...

        @overload
        def check_migration_eligibility(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckMigrationEligibilityResponse: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                **kwargs: Any
            ) -> ManagedEnvironment: ...

        @distributed_trace
        def get_auth_token(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                **kwargs: Any
            ) -> EnvironmentAuthToken: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ManagedEnvironment]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[ManagedEnvironment]: ...

        @distributed_trace
        def list_workload_profile_states(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                **kwargs: Any
            ) -> ItemPaged[WorkloadProfileStates]: ...


    class azure.mgmt.appcontainers.operations.ManagedEnvironmentsStoragesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                storage_name: str, 
                storage_envelope: ManagedEnvironmentStorage, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagedEnvironmentStorage: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                storage_name: str, 
                storage_envelope: ManagedEnvironmentStorage, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagedEnvironmentStorage: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                storage_name: str, 
                storage_envelope: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagedEnvironmentStorage: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                storage_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                storage_name: str, 
                **kwargs: Any
            ) -> ManagedEnvironmentStorage: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                **kwargs: Any
            ) -> ManagedEnvironmentStoragesCollection: ...


    class azure.mgmt.appcontainers.operations.NamespacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def check_name_availability(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                check_name_availability_request: CheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        def check_name_availability(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                check_name_availability_request: CheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        def check_name_availability(
                self, 
                resource_group_name: str, 
                environment_name: str, 
                check_name_availability_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...


    class azure.mgmt.appcontainers.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[OperationDetail]: ...


    class azure.mgmt.appcontainers.operations.SandboxGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                sandbox_group_name: str, 
                resource: SandboxGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SandboxGroup]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                sandbox_group_name: str, 
                resource: SandboxGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SandboxGroup]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                sandbox_group_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SandboxGroup]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-01', params_added_on={'2026-07-01': ['api_version', 'subscription_id', 'resource_group_name', 'sandbox_group_name']}, api_versions_list=['2026-07-01'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                sandbox_group_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                sandbox_group_name: str, 
                properties: SandboxGroupPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                sandbox_group_name: str, 
                properties: SandboxGroupPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                sandbox_group_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-01', params_added_on={'2026-07-01': ['api_version', 'subscription_id', 'resource_group_name', 'sandbox_group_name', 'accept']}, api_versions_list=['2026-07-01'])
        def get(
                self, 
                resource_group_name: str, 
                sandbox_group_name: str, 
                **kwargs: Any
            ) -> SandboxGroup: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-01', params_added_on={'2026-07-01': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2026-07-01'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SandboxGroup]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-01', params_added_on={'2026-07-01': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2026-07-01'])
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[SandboxGroup]: ...


    class azure.mgmt.appcontainers.operations.UsagesOperations:

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
            ) -> ItemPaged[Usage]: ...


    class azure.mgmt.appcontainers.operations.VnetConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-01', params_added_on={'2026-07-01': ['api_version', 'subscription_id', 'resource_group_name', 'sandbox_group_name', 'vnet_connection_name']}, api_versions_list=['2026-07-01'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                sandbox_group_name: str, 
                vnet_connection_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                sandbox_group_name: str, 
                vnet_connection_name: str, 
                resource: VnetConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VnetConnection: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                sandbox_group_name: str, 
                vnet_connection_name: str, 
                resource: VnetConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VnetConnection: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                sandbox_group_name: str, 
                vnet_connection_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VnetConnection: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-01', params_added_on={'2026-07-01': ['api_version', 'subscription_id', 'resource_group_name', 'sandbox_group_name', 'vnet_connection_name', 'accept']}, api_versions_list=['2026-07-01'])
        def get(
                self, 
                resource_group_name: str, 
                sandbox_group_name: str, 
                vnet_connection_name: str, 
                **kwargs: Any
            ) -> VnetConnection: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-01', params_added_on={'2026-07-01': ['api_version', 'subscription_id', 'resource_group_name', 'sandbox_group_name', 'accept']}, api_versions_list=['2026-07-01'])
        def list_by_sandbox_group(
                self, 
                resource_group_name: str, 
                sandbox_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[VnetConnection]: ...


namespace azure.mgmt.appcontainers.types

    class azure.mgmt.appcontainers.types.AllowedAudiencesValidation(TypedDict, total=False):
        allowedAudiences: list[str]


    class azure.mgmt.appcontainers.types.AllowedPrincipals(TypedDict, total=False):
        groups: list[str]
        identities: list[str]


    class azure.mgmt.appcontainers.types.AppInsightsConfiguration(TypedDict, total=False):
        key "connectionString": str
        connectionString: str


    class azure.mgmt.appcontainers.types.AppLogsConfiguration(TypedDict, total=False):
        key "destination": str
        key "logAnalyticsConfiguration": ForwardRef('LogAnalyticsConfiguration', module='types')
        destination: str
        logAnalyticsConfiguration: LogAnalyticsConfiguration


    class azure.mgmt.appcontainers.types.AppRegistration(TypedDict, total=False):
        key "appId": str
        key "appSecretSettingName": str
        appId: str
        appSecretSettingName: str


    class azure.mgmt.appcontainers.types.Apple(TypedDict, total=False):
        key "enabled": bool
        key "login": ForwardRef('LoginScopes', module='types')
        key "registration": ForwardRef('AppleRegistration', module='types')
        enabled: bool
        login: LoginScopes
        registration: AppleRegistration


    class azure.mgmt.appcontainers.types.AppleRegistration(TypedDict, total=False):
        key "clientId": str
        key "clientSecretSettingName": str
        clientId: str
        clientSecretSettingName: str


    class azure.mgmt.appcontainers.types.AuthConfig(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('AuthConfigProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: AuthConfigProperties
        systemData: SystemData
        type: str


    class azure.mgmt.appcontainers.types.AuthConfigProperties(TypedDict, total=False):
        key "encryptionSettings": ForwardRef('EncryptionSettings', module='types')
        key "globalValidation": ForwardRef('GlobalValidation', module='types')
        key "httpSettings": ForwardRef('HttpSettings', module='types')
        key "identityProviders": ForwardRef('IdentityProviders', module='types')
        key "login": ForwardRef('Login', module='types')
        key "platform": ForwardRef('AuthPlatform', module='types')
        encryptionSettings: EncryptionSettings
        globalValidation: GlobalValidation
        httpSettings: HttpSettings
        identityProviders: IdentityProviders
        login: Login
        platform: AuthPlatform


    class azure.mgmt.appcontainers.types.AuthPlatform(TypedDict, total=False):
        key "enabled": bool
        key "runtimeVersion": str
        enabled: bool
        runtimeVersion: str


    class azure.mgmt.appcontainers.types.AzureActiveDirectory(TypedDict, total=False):
        key "enabled": bool
        key "isAutoProvisioned": bool
        key "login": ForwardRef('AzureActiveDirectoryLogin', module='types')
        key "registration": ForwardRef('AzureActiveDirectoryRegistration', module='types')
        key "validation": ForwardRef('AzureActiveDirectoryValidation', module='types')
        enabled: bool
        isAutoProvisioned: bool
        login: AzureActiveDirectoryLogin
        registration: AzureActiveDirectoryRegistration
        validation: AzureActiveDirectoryValidation


    class azure.mgmt.appcontainers.types.AzureActiveDirectoryLogin(TypedDict, total=False):
        key "disableWWWAuthenticate": bool
        disableWWWAuthenticate: bool
        loginParameters: list[str]


    class azure.mgmt.appcontainers.types.AzureActiveDirectoryRegistration(TypedDict, total=False):
        key "clientId": str
        key "clientSecretCertificateIssuer": str
        key "clientSecretCertificateSubjectAlternativeName": str
        key "clientSecretCertificateThumbprint": str
        key "clientSecretSettingName": str
        key "openIdIssuer": str
        clientId: str
        clientSecretCertificateIssuer: str
        clientSecretCertificateSubjectAlternativeName: str
        clientSecretCertificateThumbprint: str
        clientSecretSettingName: str
        openIdIssuer: str


    class azure.mgmt.appcontainers.types.AzureActiveDirectoryValidation(TypedDict, total=False):
        key "defaultAuthorizationPolicy": ForwardRef('DefaultAuthorizationPolicy', module='types')
        key "jwtClaimChecks": ForwardRef('JwtClaimChecks', module='types')
        allowedAudiences: list[str]
        defaultAuthorizationPolicy: DefaultAuthorizationPolicy
        jwtClaimChecks: JwtClaimChecks


    class azure.mgmt.appcontainers.types.AzureCredentials(TypedDict, total=False):
        key "clientId": str
        key "clientSecret": str
        key "kind": str
        key "subscriptionId": str
        key "tenantId": str
        clientId: str
        clientSecret: str
        kind: str
        subscriptionId: str
        tenantId: str


    class azure.mgmt.appcontainers.types.AzureFileProperties(TypedDict, total=False):
        key "accessMode": Union[str, AccessMode]
        key "accountKey": str
        key "accountKeyVaultProperties": ForwardRef('SecretKeyVaultProperties', module='types')
        key "accountName": str
        key "shareName": str
        accessMode: Union[str, AccessMode]
        accountKey: str
        accountKeyVaultProperties: SecretKeyVaultProperties
        accountName: str
        shareName: str


    class azure.mgmt.appcontainers.types.AzureStaticWebApps(TypedDict, total=False):
        key "enabled": bool
        key "registration": ForwardRef('AzureStaticWebAppsRegistration', module='types')
        enabled: bool
        registration: AzureStaticWebAppsRegistration


    class azure.mgmt.appcontainers.types.AzureStaticWebAppsRegistration(TypedDict, total=False):
        key "clientId": str
        clientId: str


    class azure.mgmt.appcontainers.types.BaseContainer(TypedDict, total=False):
        key "image": str
        key "name": str
        key "resources": ForwardRef('ContainerResources', module='types')
        args: list[str]
        command: list[str]
        env: list[EnvironmentVar]
        image: str
        name: str
        resources: ContainerResources
        volumeMounts: list[VolumeMount]


    class azure.mgmt.appcontainers.types.BlobStorageTokenStore(TypedDict, total=False):
        key "blobContainerUri": str
        key "clientId": str
        key "managedIdentityResourceId": str
        key "sasUrlSettingName": str
        blobContainerUri: str
        clientId: str
        managedIdentityResourceId: str
        sasUrlSettingName: str


    class azure.mgmt.appcontainers.types.Certificate(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('CertificateProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: CertificateProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.appcontainers.types.CertificateKeyVaultProperties(TypedDict, total=False):
        key "identity": str
        key "keyVaultUrl": str
        identity: str
        keyVaultUrl: str


    class azure.mgmt.appcontainers.types.CertificatePatch(TypedDict, total=False):
        tags: dict[str, str]


    class azure.mgmt.appcontainers.types.CertificateProperties(TypedDict, total=False):
        key "certificateKeyVaultProperties": ForwardRef('CertificateKeyVaultProperties', module='types')
        key "deploymentErrors": str
        key "expirationDate": str
        key "issueDate": str
        key "issuer": str
        key "password": str
        key "provisioningState": Union[str, CertificateProvisioningState]
        key "publicKeyHash": str
        key "subjectName": str
        key "thumbprint": str
        key "valid": bool
        key "value": str
        certificateKeyVaultProperties: CertificateKeyVaultProperties
        deploymentErrors: str
        expirationDate: str
        issueDate: str
        issuer: str
        password: str
        provisioningState: Union[str, CertificateProvisioningState]
        publicKeyHash: str
        subjectAlternativeNames: list[str]
        subjectName: str
        thumbprint: str
        valid: bool
        value: str


    class azure.mgmt.appcontainers.types.CheckMigrationEligibilityRequest(TypedDict, total=False):
        key "targetMode": Required[str]
        targetMode: str


    class azure.mgmt.appcontainers.types.CheckNameAvailabilityRequest(TypedDict, total=False):
        key "name": str
        key "type": str
        name: str
        type: str


    class azure.mgmt.appcontainers.types.ClientRegistration(TypedDict, total=False):
        key "clientId": str
        key "clientSecretSettingName": str
        clientId: str
        clientSecretSettingName: str


    class azure.mgmt.appcontainers.types.Configuration(TypedDict, total=False):
        key "activeRevisionsMode": Union[str, ActiveRevisionsMode]
        key "dapr": ForwardRef('Dapr', module='types')
        key "ingress": ForwardRef('Ingress', module='types')
        key "maxInactiveRevisions": int
        key "runtime": ForwardRef('Runtime', module='types')
        key "service": ForwardRef('Service', module='types')
        activeRevisionsMode: Union[str, ActiveRevisionsMode]
        dapr: Dapr
        identitySettings: list[IdentitySettings]
        ingress: Ingress
        maxInactiveRevisions: int
        registries: list[RegistryCredentials]
        runtime: Runtime
        secrets: list[Secret]
        service: Service


    class azure.mgmt.appcontainers.types.ConnectedEnvironment(TrackedResource):
        key "extendedLocation": ForwardRef('ExtendedLocation', module='types')
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('ConnectedEnvironmentProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        extendedLocation: ExtendedLocation
        id: str
        location: str
        name: str
        properties: ConnectedEnvironmentProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.appcontainers.types.ConnectedEnvironmentPatchResource(ResourceTags):
        tags: dict[str, str]


    class azure.mgmt.appcontainers.types.ConnectedEnvironmentProperties(TypedDict, total=False):
        key "customDomainConfiguration": ForwardRef('CustomDomainConfiguration', module='types')
        key "daprAIConnectionString": str
        key "defaultDomain": str
        key "deploymentErrors": str
        key "provisioningState": Union[str, ConnectedEnvironmentProvisioningState]
        key "staticIp": str
        customDomainConfiguration: CustomDomainConfiguration
        daprAIConnectionString: str
        defaultDomain: str
        deploymentErrors: str
        provisioningState: Union[str, ConnectedEnvironmentProvisioningState]
        staticIp: str


    class azure.mgmt.appcontainers.types.ConnectedEnvironmentStorage(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('ConnectedEnvironmentStorageProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ConnectedEnvironmentStorageProperties
        systemData: SystemData
        type: str


    class azure.mgmt.appcontainers.types.ConnectedEnvironmentStorageProperties(TypedDict, total=False):
        key "azureFile": ForwardRef('AzureFileProperties', module='types')
        key "deploymentErrors": str
        key "provisioningState": Union[str, ConnectedEnvironmentStorageProvisioningState]
        azureFile: AzureFileProperties
        deploymentErrors: str
        provisioningState: Union[str, ConnectedEnvironmentStorageProvisioningState]


    class azure.mgmt.appcontainers.types.Container(BaseContainer):
        key "image": str
        key "name": str
        key "resources": ForwardRef('ContainerResources', module='types')
        args: list[str]
        command: list[str]
        env: list[EnvironmentVar]
        image: str
        name: str
        probes: list[ContainerAppProbe]
        resources: ContainerResources
        volumeMounts: list[VolumeMount]


    class azure.mgmt.appcontainers.types.ContainerApp(TrackedResource):
        key "extendedLocation": ForwardRef('ExtendedLocation', module='types')
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "kind": Union[str, Kind]
        key "location": Required[str]
        key "managedBy": str
        key "name": str
        key "properties": ForwardRef('ContainerAppProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        extendedLocation: ExtendedLocation
        id: str
        identity: ManagedServiceIdentity
        kind: Union[str, Kind]
        location: str
        managedBy: str
        name: str
        properties: ContainerAppProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.appcontainers.types.ContainerAppNetworkingConfiguration(TypedDict, total=False):
        key "outboundVnetSubnetId": str
        outboundVnetSubnetId: str


    class azure.mgmt.appcontainers.types.ContainerAppProbe(TypedDict, total=False):
        key "failureThreshold": int
        key "httpGet": ForwardRef('ContainerAppProbeHttpGet', module='types')
        key "initialDelaySeconds": int
        key "periodSeconds": int
        key "successThreshold": int
        key "tcpSocket": ForwardRef('ContainerAppProbeTcpSocket', module='types')
        key "terminationGracePeriodSeconds": int
        key "timeoutSeconds": int
        key "type": Union[str, Type]
        failureThreshold: int
        httpGet: ContainerAppProbeHttpGet
        initialDelaySeconds: int
        periodSeconds: int
        successThreshold: int
        tcpSocket: ContainerAppProbeTcpSocket
        terminationGracePeriodSeconds: int
        timeoutSeconds: int
        type: Union[str, Type]


    class azure.mgmt.appcontainers.types.ContainerAppProbeHttpGet(TypedDict, total=False):
        key "host": str
        key "path": str
        key "port": Required[int]
        key "scheme": Union[str, Scheme]
        host: str
        httpHeaders: list[ContainerAppProbeHttpGetHttpHeadersItem]
        path: str
        port: int
        scheme: Union[str, Scheme]


    class azure.mgmt.appcontainers.types.ContainerAppProbeHttpGetHttpHeadersItem(TypedDict, total=False):
        key "name": Required[str]
        key "value": Required[str]
        name: str
        value: str


    class azure.mgmt.appcontainers.types.ContainerAppProbeTcpSocket(TypedDict, total=False):
        key "host": str
        key "port": Required[int]
        host: str
        port: int


    class azure.mgmt.appcontainers.types.ContainerAppProperties(TypedDict, total=False):
        key "configuration": ForwardRef('Configuration', module='types')
        key "customDomainVerificationId": str
        key "environmentId": str
        key "eventStreamEndpoint": str
        key "latestReadyRevisionName": str
        key "latestRevisionFqdn": str
        key "latestRevisionName": str
        key "managedEnvironmentId": str
        key "networking": ForwardRef('ContainerAppNetworkingConfiguration', module='types')
        key "provisioningState": Union[str, ContainerAppProvisioningState]
        key "runningStatus": Union[str, ContainerAppRunningStatus]
        key "template": ForwardRef('Template', module='types')
        key "workloadProfileName": str
        configuration: Configuration
        customDomainVerificationId: str
        environmentId: str
        eventStreamEndpoint: str
        latestReadyRevisionName: str
        latestRevisionFqdn: str
        latestRevisionName: str
        managedEnvironmentId: str
        networking: ContainerAppNetworkingConfiguration
        outboundIpAddresses: list[str]
        provisioningState: Union[str, ContainerAppProvisioningState]
        runningStatus: Union[str, ContainerAppRunningStatus]
        template: Template
        workloadProfileName: str


    class azure.mgmt.appcontainers.types.ContainerResources(TypedDict, total=False):
        key "cpu": float
        key "ephemeralStorage": str
        key "memory": str
        cpu: float
        ephemeralStorage: str
        memory: str


    class azure.mgmt.appcontainers.types.CookieExpiration(TypedDict, total=False):
        key "convention": Union[str, CookieExpirationConvention]
        key "timeToExpiration": str
        convention: Union[str, CookieExpirationConvention]
        timeToExpiration: str


    class azure.mgmt.appcontainers.types.CorsPolicy(TypedDict, total=False):
        key "allowCredentials": bool
        key "allowedOrigins": Required[list[str]]
        key "maxAge": int
        allowCredentials: bool
        allowedHeaders: list[str]
        allowedMethods: list[str]
        allowedOrigins: list[str]
        exposeHeaders: list[str]
        maxAge: int


    class azure.mgmt.appcontainers.types.CustomContainerTemplate(TypedDict, total=False):
        key "ingress": ForwardRef('SessionIngress', module='types')
        key "registryCredentials": ForwardRef('SessionRegistryCredentials', module='types')
        containers: list[SessionContainer]
        ingress: SessionIngress
        registryCredentials: SessionRegistryCredentials


    class azure.mgmt.appcontainers.types.CustomDomain(TypedDict, total=False):
        key "bindingType": Union[str, BindingType]
        key "certificateId": str
        key "name": Required[str]
        bindingType: Union[str, BindingType]
        certificateId: str
        name: str


    class azure.mgmt.appcontainers.types.CustomDomainConfiguration(TypedDict, total=False):
        key "certificateKeyVaultProperties": ForwardRef('CertificateKeyVaultProperties', module='types')
        key "certificatePassword": str
        key "certificateValue": str
        key "customDomainVerificationId": str
        key "dnsSuffix": str
        key "expirationDate": str
        key "subjectName": str
        key "thumbprint": str
        certificateKeyVaultProperties: CertificateKeyVaultProperties
        certificatePassword: str
        certificateValue: str
        customDomainVerificationId: str
        dnsSuffix: str
        expirationDate: str
        subjectName: str
        thumbprint: str


    class azure.mgmt.appcontainers.types.CustomOpenIdConnectProvider(TypedDict, total=False):
        key "enabled": bool
        key "login": ForwardRef('OpenIdConnectLogin', module='types')
        key "registration": ForwardRef('OpenIdConnectRegistration', module='types')
        enabled: bool
        login: OpenIdConnectLogin
        registration: OpenIdConnectRegistration


    class azure.mgmt.appcontainers.types.CustomScaleRule(TypedDict, total=False):
        key "identity": str
        key "type": str
        auth: list[ScaleRuleAuth]
        identity: str
        metadata: dict[str, str]
        type: str


    class azure.mgmt.appcontainers.types.Dapr(TypedDict, total=False):
        key "appHealth": ForwardRef('DaprAppHealth', module='types')
        key "appId": str
        key "appPort": int
        key "appProtocol": Union[str, AppProtocol]
        key "enableApiLogging": bool
        key "enabled": bool
        key "httpMaxRequestSize": int
        key "httpReadBufferSize": int
        key "logLevel": Union[str, LogLevel]
        key "maxConcurrency": int
        appHealth: DaprAppHealth
        appId: str
        appPort: int
        appProtocol: Union[str, AppProtocol]
        enableApiLogging: bool
        enabled: bool
        httpMaxRequestSize: int
        httpReadBufferSize: int
        logLevel: Union[str, LogLevel]
        maxConcurrency: int


    class azure.mgmt.appcontainers.types.DaprAppHealth(TypedDict, total=False):
        key "enabled": bool
        key "path": str
        key "probeIntervalSeconds": int
        key "probeTimeoutMilliseconds": int
        key "threshold": int
        enabled: bool
        path: str
        probeIntervalSeconds: int
        probeTimeoutMilliseconds: int
        threshold: int


    class azure.mgmt.appcontainers.types.DaprComponent(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('DaprComponentProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: DaprComponentProperties
        systemData: SystemData
        type: str


    class azure.mgmt.appcontainers.types.DaprComponentProperties(TypedDict, total=False):
        key "componentType": str
        key "deploymentErrors": str
        key "ignoreErrors": bool
        key "initTimeout": str
        key "provisioningState": Union[str, DaprComponentProvisioningState]
        key "secretStoreComponent": str
        key "version": str
        componentType: str
        deploymentErrors: str
        ignoreErrors: bool
        initTimeout: str
        metadata: list[DaprMetadata]
        provisioningState: Union[str, DaprComponentProvisioningState]
        scopes: list[str]
        secretStoreComponent: str
        secrets: list[Secret]
        version: str


    class azure.mgmt.appcontainers.types.DaprComponentResiliencyPolicy(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('DaprComponentResiliencyPolicyProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: DaprComponentResiliencyPolicyProperties
        systemData: SystemData
        type: str


    class azure.mgmt.appcontainers.types.DaprComponentResiliencyPolicyCircuitBreakerPolicyConfiguration(TypedDict, total=False):
        key "consecutiveErrors": int
        key "intervalInSeconds": int
        key "timeoutInSeconds": int
        consecutiveErrors: int
        intervalInSeconds: int
        timeoutInSeconds: int


    class azure.mgmt.appcontainers.types.DaprComponentResiliencyPolicyConfiguration(TypedDict, total=False):
        key "circuitBreakerPolicy": ForwardRef('DaprComponentResiliencyPolicyCircuitBreakerPolicyConfiguration', module='types')
        key "httpRetryPolicy": ForwardRef('DaprComponentResiliencyPolicyHttpRetryPolicyConfiguration', module='types')
        key "timeoutPolicy": ForwardRef('DaprComponentResiliencyPolicyTimeoutPolicyConfiguration', module='types')
        circuitBreakerPolicy: DaprComponentResiliencyPolicyCircuitBreakerPolicyConfiguration
        httpRetryPolicy: DaprComponentResiliencyPolicyHttpRetryPolicyConfiguration
        timeoutPolicy: DaprComponentResiliencyPolicyTimeoutPolicyConfiguration


    class azure.mgmt.appcontainers.types.DaprComponentResiliencyPolicyHttpRetryBackOffConfiguration(TypedDict, total=False):
        key "initialDelayInMilliseconds": int
        key "maxIntervalInMilliseconds": int
        initialDelayInMilliseconds: int
        maxIntervalInMilliseconds: int


    class azure.mgmt.appcontainers.types.DaprComponentResiliencyPolicyHttpRetryPolicyConfiguration(TypedDict, total=False):
        key "maxRetries": int
        key "retryBackOff": ForwardRef('DaprComponentResiliencyPolicyHttpRetryBackOffConfiguration', module='types')
        maxRetries: int
        retryBackOff: DaprComponentResiliencyPolicyHttpRetryBackOffConfiguration


    class azure.mgmt.appcontainers.types.DaprComponentResiliencyPolicyProperties(TypedDict, total=False):
        key "inboundPolicy": ForwardRef('DaprComponentResiliencyPolicyConfiguration', module='types')
        key "outboundPolicy": ForwardRef('DaprComponentResiliencyPolicyConfiguration', module='types')
        inboundPolicy: DaprComponentResiliencyPolicyConfiguration
        outboundPolicy: DaprComponentResiliencyPolicyConfiguration


    class azure.mgmt.appcontainers.types.DaprComponentResiliencyPolicyTimeoutPolicyConfiguration(TypedDict, total=False):
        key "responseTimeoutInSeconds": int
        responseTimeoutInSeconds: int


    class azure.mgmt.appcontainers.types.DaprConfiguration(TypedDict, total=False):
        key "version": str
        version: str


    class azure.mgmt.appcontainers.types.DaprMetadata(TypedDict, total=False):
        key "name": str
        key "secretRef": str
        key "value": str
        name: str
        secretRef: str
        value: str


    class azure.mgmt.appcontainers.types.DataDogConfiguration(TypedDict, total=False):
        key "key": str
        key "site": str
        key: str
        site: str


    class azure.mgmt.appcontainers.types.DefaultAuthorizationPolicy(TypedDict, total=False):
        key "allowedPrincipals": ForwardRef('AllowedPrincipals', module='types')
        allowedApplications: list[str]
        allowedPrincipals: AllowedPrincipals


    class azure.mgmt.appcontainers.types.DestinationsConfiguration(TypedDict, total=False):
        key "dataDogConfiguration": ForwardRef('DataDogConfiguration', module='types')
        dataDogConfiguration: DataDogConfiguration
        otlpConfigurations: list[OtlpConfiguration]


    class azure.mgmt.appcontainers.types.DotNetComponent(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('DotNetComponentProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: DotNetComponentProperties
        systemData: SystemData
        type: str


    class azure.mgmt.appcontainers.types.DotNetComponentConfigurationProperty(TypedDict, total=False):
        key "propertyName": str
        key "value": str
        propertyName: str
        value: str


    class azure.mgmt.appcontainers.types.DotNetComponentProperties(TypedDict, total=False):
        key "componentType": Union[str, DotNetComponentType]
        key "provisioningState": Union[str, DotNetComponentProvisioningState]
        componentType: Union[str, DotNetComponentType]
        configurations: list[DotNetComponentConfigurationProperty]
        provisioningState: Union[str, DotNetComponentProvisioningState]
        serviceBinds: list[DotNetComponentServiceBind]


    class azure.mgmt.appcontainers.types.DotNetComponentServiceBind(TypedDict, total=False):
        key "name": str
        key "serviceId": str
        name: str
        serviceId: str


    class azure.mgmt.appcontainers.types.DynamicPoolConfiguration(TypedDict, total=False):
        key "lifecycleConfiguration": ForwardRef('LifecycleConfiguration', module='types')
        lifecycleConfiguration: LifecycleConfiguration


    class azure.mgmt.appcontainers.types.EncryptionSettings(TypedDict, total=False):
        key "containerAppAuthEncryptionSecretName": str
        key "containerAppAuthSigningSecretName": str
        containerAppAuthEncryptionSecretName: str
        containerAppAuthSigningSecretName: str


    class azure.mgmt.appcontainers.types.EnvironmentVar(TypedDict, total=False):
        key "name": str
        key "secretRef": str
        key "value": str
        name: str
        secretRef: str
        value: str


    class azure.mgmt.appcontainers.types.ExtendedLocation(TypedDict, total=False):
        key "name": str
        key "type": Union[str, ExtendedLocationTypes]
        name: str
        type: Union[str, ExtendedLocationTypes]


    class azure.mgmt.appcontainers.types.Facebook(TypedDict, total=False):
        key "enabled": bool
        key "graphApiVersion": str
        key "login": ForwardRef('LoginScopes', module='types')
        key "registration": ForwardRef('AppRegistration', module='types')
        enabled: bool
        graphApiVersion: str
        login: LoginScopes
        registration: AppRegistration


    class azure.mgmt.appcontainers.types.ForwardProxy(TypedDict, total=False):
        key "convention": Union[str, ForwardProxyConvention]
        key "customHostHeaderName": str
        key "customProtoHeaderName": str
        convention: Union[str, ForwardProxyConvention]
        customHostHeaderName: str
        customProtoHeaderName: str


    class azure.mgmt.appcontainers.types.GitHub(TypedDict, total=False):
        key "enabled": bool
        key "login": ForwardRef('LoginScopes', module='types')
        key "registration": ForwardRef('ClientRegistration', module='types')
        enabled: bool
        login: LoginScopes
        registration: ClientRegistration


    class azure.mgmt.appcontainers.types.GithubActionConfiguration(TypedDict, total=False):
        key "azureCredentials": ForwardRef('AzureCredentials', module='types')
        key "contextPath": str
        key "githubPersonalAccessToken": str
        key "image": str
        key "os": str
        key "publishType": str
        key "registryInfo": ForwardRef('RegistryInfo', module='types')
        key "runtimeStack": str
        key "runtimeVersion": str
        azureCredentials: AzureCredentials
        contextPath: str
        githubPersonalAccessToken: str
        image: str
        os: str
        publishType: str
        registryInfo: RegistryInfo
        runtimeStack: str
        runtimeVersion: str


    class azure.mgmt.appcontainers.types.GlobalValidation(TypedDict, total=False):
        key "redirectToProvider": str
        key "unauthenticatedClientAction": Union[str, UnauthenticatedClientActionV2]
        excludedPaths: list[str]
        redirectToProvider: str
        unauthenticatedClientAction: Union[str, UnauthenticatedClientActionV2]


    class azure.mgmt.appcontainers.types.Google(TypedDict, total=False):
        key "enabled": bool
        key "login": ForwardRef('LoginScopes', module='types')
        key "registration": ForwardRef('ClientRegistration', module='types')
        key "validation": ForwardRef('AllowedAudiencesValidation', module='types')
        enabled: bool
        login: LoginScopes
        registration: ClientRegistration
        validation: AllowedAudiencesValidation


    class azure.mgmt.appcontainers.types.Header(TypedDict, total=False):
        key "key": str
        key "value": str
        key: str
        value: str


    class azure.mgmt.appcontainers.types.HttpRoute(TypedDict, total=False):
        key "action": ForwardRef('HttpRouteAction', module='types')
        key "match": ForwardRef('HttpRouteMatch', module='types')
        action: HttpRouteAction
        match: HttpRouteMatch


    class azure.mgmt.appcontainers.types.HttpRouteAction(TypedDict, total=False):
        key "prefixRewrite": str
        prefixRewrite: str


    class azure.mgmt.appcontainers.types.HttpRouteConfig(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('HttpRouteConfigProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: HttpRouteConfigProperties
        systemData: SystemData
        type: str


    class azure.mgmt.appcontainers.types.HttpRouteConfigProperties(TypedDict, total=False):
        key "fqdn": str
        key "provisioningState": Union[str, HttpRouteProvisioningState]
        customDomains: list[CustomDomain]
        fqdn: str
        provisioningErrors: list[HttpRouteProvisioningErrors]
        provisioningState: Union[str, HttpRouteProvisioningState]
        rules: list[HttpRouteRule]


    class azure.mgmt.appcontainers.types.HttpRouteMatch(TypedDict, total=False):
        key "caseSensitive": bool
        key "path": str
        key "pathSeparatedPrefix": str
        key "prefix": str
        caseSensitive: bool
        path: str
        pathSeparatedPrefix: str
        prefix: str


    class azure.mgmt.appcontainers.types.HttpRouteProvisioningErrors(TypedDict, total=False):
        key "message": str
        key "timestamp": str
        message: str
        timestamp: str


    class azure.mgmt.appcontainers.types.HttpRouteRule(TypedDict, total=False):
        key "description": str
        description: str
        routes: list[HttpRoute]
        targets: list[HttpRouteTarget]


    class azure.mgmt.appcontainers.types.HttpRouteTarget(TypedDict, total=False):
        key "containerApp": Required[str]
        key "label": str
        key "revision": str
        containerApp: str
        label: str
        revision: str


    class azure.mgmt.appcontainers.types.HttpScaleRule(TypedDict, total=False):
        key "identity": str
        auth: list[ScaleRuleAuth]
        identity: str
        metadata: dict[str, str]


    class azure.mgmt.appcontainers.types.HttpSettings(TypedDict, total=False):
        key "forwardProxy": ForwardRef('ForwardProxy', module='types')
        key "requireHttps": bool
        key "routes": ForwardRef('HttpSettingsRoutes', module='types')
        forwardProxy: ForwardProxy
        requireHttps: bool
        routes: HttpSettingsRoutes


    class azure.mgmt.appcontainers.types.HttpSettingsRoutes(TypedDict, total=False):
        key "apiPrefix": str
        apiPrefix: str


    class azure.mgmt.appcontainers.types.IdentityProviders(TypedDict, total=False):
        key "apple": ForwardRef('Apple', module='types')
        key "azureActiveDirectory": ForwardRef('AzureActiveDirectory', module='types')
        key "azureStaticWebApps": ForwardRef('AzureStaticWebApps', module='types')
        key "facebook": ForwardRef('Facebook', module='types')
        key "gitHub": ForwardRef('GitHub', module='types')
        key "google": ForwardRef('Google', module='types')
        key "twitter": ForwardRef('Twitter', module='types')
        apple: Apple
        azureActiveDirectory: AzureActiveDirectory
        azureStaticWebApps: AzureStaticWebApps
        customOpenIdConnectProviders: dict[str, CustomOpenIdConnectProvider]
        facebook: Facebook
        gitHub: GitHub
        google: Google
        twitter: Twitter


    class azure.mgmt.appcontainers.types.IdentitySettings(TypedDict, total=False):
        key "identity": Required[str]
        key "lifecycle": Union[str, IdentitySettingsLifeCycle]
        identity: str
        lifecycle: Union[str, IdentitySettingsLifeCycle]


    class azure.mgmt.appcontainers.types.Ingress(TypedDict, total=False):
        key "allowInsecure": bool
        key "clientCertificateMode": Union[str, IngressClientCertificateMode]
        key "corsPolicy": ForwardRef('CorsPolicy', module='types')
        key "exposedPort": int
        key "external": bool
        key "fqdn": str
        key "stickySessions": ForwardRef('IngressStickySessions', module='types')
        key "targetPort": int
        key "transport": Union[str, IngressTransportMethod]
        additionalPortMappings: list[IngressPortMapping]
        allowInsecure: bool
        clientCertificateMode: Union[str, IngressClientCertificateMode]
        corsPolicy: CorsPolicy
        customDomains: list[CustomDomain]
        exposedPort: int
        external: bool
        fqdn: str
        ipSecurityRestrictions: list[IpSecurityRestrictionRule]
        stickySessions: IngressStickySessions
        targetPort: int
        traffic: list[TrafficWeight]
        transport: Union[str, IngressTransportMethod]


    class azure.mgmt.appcontainers.types.IngressConfiguration(TypedDict, total=False):
        key "headerCountLimit": int
        key "requestIdleTimeout": int
        key "terminationGracePeriodSeconds": int
        key "workloadProfileName": str
        headerCountLimit: int
        requestIdleTimeout: int
        terminationGracePeriodSeconds: int
        workloadProfileName: str


    class azure.mgmt.appcontainers.types.IngressPortMapping(TypedDict, total=False):
        key "exposedPort": int
        key "external": Required[bool]
        key "targetPort": Required[int]
        exposedPort: int
        external: bool
        targetPort: int


    class azure.mgmt.appcontainers.types.IngressStickySessions(TypedDict, total=False):
        key "affinity": Union[str, Affinity]
        affinity: Union[str, Affinity]


    class azure.mgmt.appcontainers.types.InitContainer(BaseContainer):
        key "image": str
        key "name": str
        key "resources": ForwardRef('ContainerResources', module='types')
        args: list[str]
        command: list[str]
        env: list[EnvironmentVar]
        image: str
        name: str
        resources: ContainerResources
        volumeMounts: list[VolumeMount]


    class azure.mgmt.appcontainers.types.IpSecurityRestrictionRule(TypedDict, total=False):
        key "action": Required[Union[str, Action]]
        key "description": str
        key "ipAddressRange": Required[str]
        key "name": Required[str]
        action: Union[str, Action]
        description: str
        ipAddressRange: str
        name: str


    class azure.mgmt.appcontainers.types.JavaComponent(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('JavaComponentProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: JavaComponentProperties
        systemData: SystemData
        type: str


    class azure.mgmt.appcontainers.types.JavaComponentConfigurationProperty(TypedDict, total=False):
        key "propertyName": str
        key "value": str
        propertyName: str
        value: str


    class azure.mgmt.appcontainers.types.JavaComponentIngress(TypedDict, total=False):
        key "fqdn": str
        fqdn: str


    class azure.mgmt.appcontainers.types.JavaComponentPropertiesScale(TypedDict, total=False):
        key "maxReplicas": int
        key "minReplicas": int
        maxReplicas: int
        minReplicas: int


    class azure.mgmt.appcontainers.types.JavaComponentServiceBind(TypedDict, total=False):
        key "name": str
        key "serviceId": str
        name: str
        serviceId: str


    class azure.mgmt.appcontainers.types.JavaComponentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SPRING_BOOT_ADMIN = "SpringBootAdmin"
        SPRING_CLOUD_CONFIG = "SpringCloudConfig"
        SPRING_CLOUD_EUREKA = "SpringCloudEureka"


    class azure.mgmt.appcontainers.types.Job(TrackedResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('JobProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: JobProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.appcontainers.types.JobConfiguration(TypedDict, total=False):
        key "eventTriggerConfig": ForwardRef('JobConfigurationEventTriggerConfig', module='types')
        key "manualTriggerConfig": ForwardRef('JobConfigurationManualTriggerConfig', module='types')
        key "replicaRetryLimit": int
        key "replicaTimeout": Required[int]
        key "scheduleTriggerConfig": ForwardRef('JobConfigurationScheduleTriggerConfig', module='types')
        key "triggerType": Required[Union[str, TriggerType]]
        eventTriggerConfig: JobConfigurationEventTriggerConfig
        identitySettings: list[IdentitySettings]
        manualTriggerConfig: JobConfigurationManualTriggerConfig
        registries: list[RegistryCredentials]
        replicaRetryLimit: int
        replicaTimeout: int
        scheduleTriggerConfig: JobConfigurationScheduleTriggerConfig
        secrets: list[Secret]
        triggerType: Union[str, TriggerType]


    class azure.mgmt.appcontainers.types.JobConfigurationEventTriggerConfig(TypedDict, total=False):
        key "parallelism": int
        key "replicaCompletionCount": int
        key "scale": ForwardRef('JobScale', module='types')
        parallelism: int
        replicaCompletionCount: int
        scale: JobScale


    class azure.mgmt.appcontainers.types.JobConfigurationManualTriggerConfig(TypedDict, total=False):
        key "parallelism": int
        key "replicaCompletionCount": int
        parallelism: int
        replicaCompletionCount: int


    class azure.mgmt.appcontainers.types.JobConfigurationScheduleTriggerConfig(TypedDict, total=False):
        key "cronExpression": Required[str]
        key "parallelism": int
        key "replicaCompletionCount": int
        cronExpression: str
        parallelism: int
        replicaCompletionCount: int


    class azure.mgmt.appcontainers.types.JobExecutionContainer(TypedDict, total=False):
        key "image": str
        key "name": str
        key "resources": ForwardRef('ContainerResources', module='types')
        args: list[str]
        command: list[str]
        env: list[EnvironmentVar]
        image: str
        name: str
        resources: ContainerResources


    class azure.mgmt.appcontainers.types.JobExecutionTemplate(TypedDict, total=False):
        containers: list[JobExecutionContainer]
        initContainers: list[JobExecutionContainer]


    class azure.mgmt.appcontainers.types.JobPatchProperties(TypedDict, total=False):
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "properties": ForwardRef('JobPatchPropertiesProperties', module='types')
        identity: ManagedServiceIdentity
        properties: JobPatchPropertiesProperties
        tags: dict[str, str]


    class azure.mgmt.appcontainers.types.JobPatchPropertiesProperties(TypedDict, total=False):
        key "configuration": ForwardRef('JobConfiguration', module='types')
        key "environmentId": str
        key "eventStreamEndpoint": str
        key "template": ForwardRef('JobTemplate', module='types')
        configuration: JobConfiguration
        environmentId: str
        eventStreamEndpoint: str
        outboundIpAddresses: list[str]
        template: JobTemplate


    class azure.mgmt.appcontainers.types.JobProperties(TypedDict, total=False):
        key "configuration": ForwardRef('JobConfiguration', module='types')
        key "environmentId": str
        key "eventStreamEndpoint": str
        key "provisioningState": Union[str, JobProvisioningState]
        key "runningState": Union[str, JobRunningState]
        key "template": ForwardRef('JobTemplate', module='types')
        key "workloadProfileName": str
        configuration: JobConfiguration
        environmentId: str
        eventStreamEndpoint: str
        outboundIpAddresses: list[str]
        provisioningState: Union[str, JobProvisioningState]
        runningState: Union[str, JobRunningState]
        template: JobTemplate
        workloadProfileName: str


    class azure.mgmt.appcontainers.types.JobScale(TypedDict, total=False):
        key "maxExecutions": int
        key "minExecutions": int
        key "pollingInterval": int
        maxExecutions: int
        minExecutions: int
        pollingInterval: int
        rules: list[JobScaleRule]


    class azure.mgmt.appcontainers.types.JobScaleRule(TypedDict, total=False):
        key "identity": str
        key "metadata": Any
        key "name": str
        key "type": str
        auth: list[ScaleRuleAuth]
        identity: str
        metadata: Any
        name: str
        type: str


    class azure.mgmt.appcontainers.types.JobTemplate(TypedDict, total=False):
        containers: list[Container]
        initContainers: list[InitContainer]
        volumes: list[Volume]


    class azure.mgmt.appcontainers.types.JwtClaimChecks(TypedDict, total=False):
        allowedClientApplications: list[str]
        allowedGroups: list[str]


    class azure.mgmt.appcontainers.types.KedaConfiguration(TypedDict, total=False):
        key "version": str
        version: str


    class azure.mgmt.appcontainers.types.LifecycleConfiguration(TypedDict, total=False):
        key "cooldownPeriodInSeconds": int
        key "lifecycleType": Union[str, LifecycleType]
        key "maxAlivePeriodInSeconds": int
        cooldownPeriodInSeconds: int
        lifecycleType: Union[str, LifecycleType]
        maxAlivePeriodInSeconds: int


    class azure.mgmt.appcontainers.types.LogAnalyticsConfiguration(TypedDict, total=False):
        key "customerId": str
        key "sharedKey": str
        customerId: str
        sharedKey: str


    class azure.mgmt.appcontainers.types.LogicApp(ProxyResource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.appcontainers.types.Login(TypedDict, total=False):
        key "cookieExpiration": ForwardRef('CookieExpiration', module='types')
        key "nonce": ForwardRef('Nonce', module='types')
        key "preserveUrlFragmentsForLogins": bool
        key "routes": ForwardRef('LoginRoutes', module='types')
        key "tokenStore": ForwardRef('TokenStore', module='types')
        allowedExternalRedirectUrls: list[str]
        cookieExpiration: CookieExpiration
        nonce: Nonce
        preserveUrlFragmentsForLogins: bool
        routes: LoginRoutes
        tokenStore: TokenStore


    class azure.mgmt.appcontainers.types.LoginRoutes(TypedDict, total=False):
        key "logoutEndpoint": str
        logoutEndpoint: str


    class azure.mgmt.appcontainers.types.LoginScopes(TypedDict, total=False):
        scopes: list[str]


    class azure.mgmt.appcontainers.types.LogsConfiguration(TypedDict, total=False):
        destinations: list[str]


    class azure.mgmt.appcontainers.types.MaintenanceConfigurationResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('ScheduledEntries', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ScheduledEntries
        systemData: SystemData
        type: str


    class azure.mgmt.appcontainers.types.ManagedCertificate(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('ManagedCertificateProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: ManagedCertificateProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.appcontainers.types.ManagedCertificatePatch(TypedDict, total=False):
        tags: dict[str, str]


    class azure.mgmt.appcontainers.types.ManagedCertificateProperties(TypedDict, total=False):
        key "domainControlValidation": Union[str, ManagedCertificateDomainControlValidation]
        key "error": str
        key "provisioningState": Union[str, CertificateProvisioningState]
        key "subjectName": str
        key "validationToken": str
        domainControlValidation: Union[str, ManagedCertificateDomainControlValidation]
        error: str
        provisioningState: Union[str, CertificateProvisioningState]
        subjectName: str
        validationToken: str


    class azure.mgmt.appcontainers.types.ManagedEnvironment(TrackedResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "kind": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('ManagedEnvironmentProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        kind: str
        location: str
        name: str
        properties: ManagedEnvironmentProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.appcontainers.types.ManagedEnvironmentProperties(TypedDict, total=False):
        key "appInsightsConfiguration": ForwardRef('AppInsightsConfiguration', module='types')
        key "appLogsConfiguration": ForwardRef('AppLogsConfiguration', module='types')
        key "customDomainConfiguration": ForwardRef('CustomDomainConfiguration', module='types')
        key "daprAIConnectionString": str
        key "daprAIInstrumentationKey": str
        key "daprConfiguration": ForwardRef('DaprConfiguration', module='types')
        key "defaultDomain": str
        key "deploymentErrors": str
        key "environmentMode": Union[str, ManagedEnvironmentMode]
        key "eventStreamEndpoint": str
        key "infrastructureResourceGroup": str
        key "ingressConfiguration": ForwardRef('IngressConfiguration', module='types')
        key "kedaConfiguration": ForwardRef('KedaConfiguration', module='types')
        key "openTelemetryConfiguration": ForwardRef('OpenTelemetryConfiguration', module='types')
        key "peerAuthentication": ForwardRef('ManagedEnvironmentPropertiesPeerAuthentication', module='types')
        key "peerTrafficConfiguration": ForwardRef('ManagedEnvironmentPropertiesPeerTrafficConfiguration', module='types')
        key "provisioningState": Union[str, EnvironmentProvisioningState]
        key "publicNetworkAccess": Union[str, PublicNetworkAccess]
        key "staticIp": str
        key "vnetConfiguration": ForwardRef('VnetConfiguration', module='types')
        key "zoneRedundant": bool
        appInsightsConfiguration: AppInsightsConfiguration
        appLogsConfiguration: AppLogsConfiguration
        customDomainConfiguration: CustomDomainConfiguration
        daprAIConnectionString: str
        daprAIInstrumentationKey: str
        daprConfiguration: DaprConfiguration
        defaultDomain: str
        deploymentErrors: str
        environmentMode: Union[str, ManagedEnvironmentMode]
        eventStreamEndpoint: str
        infrastructureResourceGroup: str
        ingressConfiguration: IngressConfiguration
        kedaConfiguration: KedaConfiguration
        openTelemetryConfiguration: OpenTelemetryConfiguration
        peerAuthentication: ManagedEnvironmentPropertiesPeerAuthentication
        peerTrafficConfiguration: ManagedEnvironmentPropertiesPeerTrafficConfiguration
        privateEndpointConnections: list[PrivateEndpointConnection]
        provisioningState: Union[str, EnvironmentProvisioningState]
        publicNetworkAccess: Union[str, PublicNetworkAccess]
        staticIp: str
        vnetConfiguration: VnetConfiguration
        workloadProfiles: list[WorkloadProfile]
        zoneRedundant: bool


    class azure.mgmt.appcontainers.types.ManagedEnvironmentPropertiesPeerAuthentication(TypedDict, total=False):
        key "mtls": ForwardRef('Mtls', module='types')
        mtls: Mtls


    class azure.mgmt.appcontainers.types.ManagedEnvironmentPropertiesPeerTrafficConfiguration(TypedDict, total=False):
        key "encryption": ForwardRef('ManagedEnvironmentPropertiesPeerTrafficConfigurationEncryption', module='types')
        encryption: ManagedEnvironmentPropertiesPeerTrafficConfigurationEncryption


    class azure.mgmt.appcontainers.types.ManagedEnvironmentPropertiesPeerTrafficConfigurationEncryption(TypedDict, total=False):
        key "enabled": bool
        enabled: bool


    class azure.mgmt.appcontainers.types.ManagedEnvironmentStorage(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('ManagedEnvironmentStorageProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ManagedEnvironmentStorageProperties
        systemData: SystemData
        type: str


    class azure.mgmt.appcontainers.types.ManagedEnvironmentStorageProperties(TypedDict, total=False):
        key "azureFile": ForwardRef('AzureFileProperties', module='types')
        key "nfsAzureFile": ForwardRef('NfsAzureFileProperties', module='types')
        azureFile: AzureFileProperties
        nfsAzureFile: NfsAzureFileProperties


    class azure.mgmt.appcontainers.types.ManagedIdentitySetting(TypedDict, total=False):
        key "identity": Required[str]
        key "lifecycle": Union[str, SessionPoolIdentityLifeCycle]
        identity: str
        lifecycle: Union[str, SessionPoolIdentityLifeCycle]


    class azure.mgmt.appcontainers.types.ManagedServiceIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Required[Union[str, ManagedServiceIdentityType]]
        principalId: str
        tenantId: str
        type: Union[str, ManagedServiceIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentity]


    class azure.mgmt.appcontainers.types.MetricsConfiguration(TypedDict, total=False):
        key "includeKeda": bool
        destinations: list[str]
        includeKeda: bool


    class azure.mgmt.appcontainers.types.Mtls(TypedDict, total=False):
        key "enabled": bool
        enabled: bool


    class azure.mgmt.appcontainers.types.NfsAzureFileProperties(TypedDict, total=False):
        key "accessMode": Union[str, AccessMode]
        key "server": str
        key "shareName": str
        accessMode: Union[str, AccessMode]
        server: str
        shareName: str


    class azure.mgmt.appcontainers.types.Nonce(TypedDict, total=False):
        key "nonceExpirationInterval": str
        key "validateNonce": bool
        nonceExpirationInterval: str
        validateNonce: bool


    class azure.mgmt.appcontainers.types.OpenIdConnectClientCredential(TypedDict, total=False):
        key "clientSecretSettingName": str
        key "method": Literal["ClientSecretPost"]
        clientSecretSettingName: str
        method: Literal[ClientSecretPost]


    class azure.mgmt.appcontainers.types.OpenIdConnectConfig(TypedDict, total=False):
        key "authorizationEndpoint": str
        key "certificationUri": str
        key "issuer": str
        key "tokenEndpoint": str
        key "wellKnownOpenIdConfiguration": str
        authorizationEndpoint: str
        certificationUri: str
        issuer: str
        tokenEndpoint: str
        wellKnownOpenIdConfiguration: str


    class azure.mgmt.appcontainers.types.OpenIdConnectLogin(TypedDict, total=False):
        key "nameClaimType": str
        nameClaimType: str
        scopes: list[str]


    class azure.mgmt.appcontainers.types.OpenIdConnectRegistration(TypedDict, total=False):
        key "clientCredential": ForwardRef('OpenIdConnectClientCredential', module='types')
        key "clientId": str
        key "openIdConnectConfiguration": ForwardRef('OpenIdConnectConfig', module='types')
        clientCredential: OpenIdConnectClientCredential
        clientId: str
        openIdConnectConfiguration: OpenIdConnectConfig


    class azure.mgmt.appcontainers.types.OpenTelemetryConfiguration(TypedDict, total=False):
        key "destinationsConfiguration": ForwardRef('DestinationsConfiguration', module='types')
        key "logsConfiguration": ForwardRef('LogsConfiguration', module='types')
        key "metricsConfiguration": ForwardRef('MetricsConfiguration', module='types')
        key "tracesConfiguration": ForwardRef('TracesConfiguration', module='types')
        destinationsConfiguration: DestinationsConfiguration
        logsConfiguration: LogsConfiguration
        metricsConfiguration: MetricsConfiguration
        tracesConfiguration: TracesConfiguration


    class azure.mgmt.appcontainers.types.OtlpConfiguration(TypedDict, total=False):
        key "endpoint": str
        key "insecure": bool
        key "name": str
        endpoint: str
        headers: list[Header]
        insecure: bool
        name: str


    class azure.mgmt.appcontainers.types.PrivateEndpoint(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.appcontainers.types.PrivateEndpointConnection(ProxyResource):
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


    class azure.mgmt.appcontainers.types.PrivateEndpointConnectionProperties(TypedDict, total=False):
        key "privateEndpoint": ForwardRef('PrivateEndpoint', module='types')
        key "privateLinkServiceConnectionState": Required[PrivateLinkServiceConnectionState]
        key "provisioningState": Union[str, PrivateEndpointConnectionProvisioningState]
        groupIds: list[str]
        privateEndpoint: PrivateEndpoint
        privateLinkServiceConnectionState: PrivateLinkServiceConnectionState
        provisioningState: Union[str, PrivateEndpointConnectionProvisioningState]


    class azure.mgmt.appcontainers.types.PrivateLinkServiceConnectionState(TypedDict, total=False):
        key "actionsRequired": str
        key "description": str
        key "status": Union[str, PrivateEndpointServiceConnectionStatus]
        actionsRequired: str
        description: str
        status: Union[str, PrivateEndpointServiceConnectionStatus]


    class azure.mgmt.appcontainers.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.appcontainers.types.QueueScaleRule(TypedDict, total=False):
        key "accountName": str
        key "identity": str
        key "queueLength": int
        key "queueName": str
        accountName: str
        auth: list[ScaleRuleAuth]
        identity: str
        queueLength: int
        queueName: str


    class azure.mgmt.appcontainers.types.RegistryCredentials(TypedDict, total=False):
        key "identity": str
        key "passwordSecretRef": str
        key "server": str
        key "username": str
        identity: str
        passwordSecretRef: str
        server: str
        username: str


    class azure.mgmt.appcontainers.types.RegistryInfo(TypedDict, total=False):
        key "registryPassword": str
        key "registryUrl": str
        key "registryUserName": str
        registryPassword: str
        registryUrl: str
        registryUserName: str


    class azure.mgmt.appcontainers.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.appcontainers.types.ResourceTags(TypedDict, total=False):
        tags: dict[str, str]


    class azure.mgmt.appcontainers.types.Runtime(TypedDict, total=False):
        key "java": ForwardRef('RuntimeJava', module='types')
        java: RuntimeJava


    class azure.mgmt.appcontainers.types.RuntimeJava(TypedDict, total=False):
        key "enableMetrics": bool
        enableMetrics: bool


    class azure.mgmt.appcontainers.types.SandboxGroup(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('SandboxGroupProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: SandboxGroupProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.appcontainers.types.SandboxGroupPatch(TypedDict, total=False):
        key "properties": ForwardRef('SandboxGroupPatchProperties', module='types')
        properties: SandboxGroupPatchProperties
        tags: dict[str, str]


    class azure.mgmt.appcontainers.types.SandboxGroupPatchProperties(TypedDict, total=False):
        key "environmentId": str
        environmentId: str


    class azure.mgmt.appcontainers.types.SandboxGroupProperties(TypedDict, total=False):
        key "defaultDomain": str
        key "environmentId": str
        key "provisioningState": Union[str, SandboxGroupProvisioningState]
        defaultDomain: str
        environmentId: str
        provisioningState: Union[str, SandboxGroupProvisioningState]


    class azure.mgmt.appcontainers.types.Scale(TypedDict, total=False):
        key "allowScalingRuleOverride": bool
        key "cooldownPeriod": int
        key "maxReplicas": int
        key "minReplicas": int
        key "pollingInterval": int
        allowScalingRuleOverride: bool
        cooldownPeriod: int
        maxReplicas: int
        minReplicas: int
        pollingInterval: int
        rules: list[ScaleRule]


    class azure.mgmt.appcontainers.types.ScaleConfiguration(TypedDict, total=False):
        key "maxConcurrentSessions": int
        key "readySessionInstances": int
        maxConcurrentSessions: int
        readySessionInstances: int


    class azure.mgmt.appcontainers.types.ScaleRule(TypedDict, total=False):
        key "azureQueue": ForwardRef('QueueScaleRule', module='types')
        key "custom": ForwardRef('CustomScaleRule', module='types')
        key "http": ForwardRef('HttpScaleRule', module='types')
        key "name": str
        key "tcp": ForwardRef('TcpScaleRule', module='types')
        azureQueue: QueueScaleRule
        custom: CustomScaleRule
        http: HttpScaleRule
        name: str
        tcp: TcpScaleRule


    class azure.mgmt.appcontainers.types.ScaleRuleAuth(TypedDict, total=False):
        key "secretRef": str
        key "triggerParameter": str
        secretRef: str
        triggerParameter: str


    class azure.mgmt.appcontainers.types.ScheduledEntries(TypedDict, total=False):
        key "scheduledEntries": Required[list[ScheduledEntry]]
        scheduledEntries: list[ScheduledEntry]


    class azure.mgmt.appcontainers.types.ScheduledEntry(TypedDict, total=False):
        key "durationHours": Required[int]
        key "startHourUtc": Required[int]
        key "weekDay": Required[Union[str, WeekDay]]
        durationHours: int
        startHourUtc: int
        weekDay: Union[str, WeekDay]


    class azure.mgmt.appcontainers.types.Secret(TypedDict, total=False):
        key "identity": str
        key "keyVaultUrl": str
        key "name": str
        key "value": str
        identity: str
        keyVaultUrl: str
        name: str
        value: str


    class azure.mgmt.appcontainers.types.SecretKeyVaultProperties(TypedDict, total=False):
        key "identity": str
        key "keyVaultUrl": str
        identity: str
        keyVaultUrl: str


    class azure.mgmt.appcontainers.types.SecretVolumeItem(TypedDict, total=False):
        key "path": str
        key "secretRef": str
        path: str
        secretRef: str


    class azure.mgmt.appcontainers.types.Service(TypedDict, total=False):
        key "type": Required[str]
        type: str


    class azure.mgmt.appcontainers.types.ServiceBind(TypedDict, total=False):
        key "name": str
        key "serviceId": str
        name: str
        serviceId: str


    class azure.mgmt.appcontainers.types.SessionContainer(TypedDict, total=False):
        key "image": str
        key "name": str
        key "resources": ForwardRef('SessionContainerResources', module='types')
        args: list[str]
        command: list[str]
        env: list[EnvironmentVar]
        image: str
        name: str
        probes: list[SessionProbe]
        resources: SessionContainerResources


    class azure.mgmt.appcontainers.types.SessionContainerResources(TypedDict, total=False):
        key "cpu": float
        key "memory": str
        cpu: float
        memory: str


    class azure.mgmt.appcontainers.types.SessionIngress(TypedDict, total=False):
        key "targetPort": int
        targetPort: int


    class azure.mgmt.appcontainers.types.SessionNetworkConfiguration(TypedDict, total=False):
        key "status": Union[str, SessionNetworkStatus]
        status: Union[str, SessionNetworkStatus]


    class azure.mgmt.appcontainers.types.SessionPool(TrackedResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('SessionPoolProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: SessionPoolProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.appcontainers.types.SessionPoolProperties(TypedDict, total=False):
        key "containerType": Union[str, ContainerType]
        key "customContainerTemplate": ForwardRef('CustomContainerTemplate', module='types')
        key "dynamicPoolConfiguration": ForwardRef('DynamicPoolConfiguration', module='types')
        key "environmentId": str
        key "nodeCount": int
        key "poolManagementEndpoint": str
        key "poolManagementType": Union[str, PoolManagementType]
        key "provisioningState": Union[str, SessionPoolProvisioningState]
        key "scaleConfiguration": ForwardRef('ScaleConfiguration', module='types')
        key "sessionNetworkConfiguration": ForwardRef('SessionNetworkConfiguration', module='types')
        containerType: Union[str, ContainerType]
        customContainerTemplate: CustomContainerTemplate
        dynamicPoolConfiguration: DynamicPoolConfiguration
        environmentId: str
        managedIdentitySettings: list[ManagedIdentitySetting]
        nodeCount: int
        poolManagementEndpoint: str
        poolManagementType: Union[str, PoolManagementType]
        provisioningState: Union[str, SessionPoolProvisioningState]
        scaleConfiguration: ScaleConfiguration
        secrets: list[SessionPoolSecret]
        sessionNetworkConfiguration: SessionNetworkConfiguration


    class azure.mgmt.appcontainers.types.SessionPoolSecret(TypedDict, total=False):
        key "name": str
        key "value": str
        name: str
        value: str


    class azure.mgmt.appcontainers.types.SessionPoolUpdatableProperties(TypedDict, total=False):
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "properties": ForwardRef('SessionPoolUpdatablePropertiesProperties', module='types')
        identity: ManagedServiceIdentity
        properties: SessionPoolUpdatablePropertiesProperties
        tags: dict[str, str]


    class azure.mgmt.appcontainers.types.SessionPoolUpdatablePropertiesProperties(TypedDict, total=False):
        key "customContainerTemplate": ForwardRef('CustomContainerTemplate', module='types')
        key "dynamicPoolConfiguration": ForwardRef('DynamicPoolConfiguration', module='types')
        key "scaleConfiguration": ForwardRef('ScaleConfiguration', module='types')
        key "sessionNetworkConfiguration": ForwardRef('SessionNetworkConfiguration', module='types')
        customContainerTemplate: CustomContainerTemplate
        dynamicPoolConfiguration: DynamicPoolConfiguration
        scaleConfiguration: ScaleConfiguration
        secrets: list[SessionPoolSecret]
        sessionNetworkConfiguration: SessionNetworkConfiguration


    class azure.mgmt.appcontainers.types.SessionProbe(TypedDict, total=False):
        key "failureThreshold": int
        key "httpGet": ForwardRef('SessionProbeHttpGet', module='types')
        key "initialDelaySeconds": int
        key "periodSeconds": int
        key "successThreshold": int
        key "tcpSocket": ForwardRef('SessionProbeTcpSocket', module='types')
        key "terminationGracePeriodSeconds": int
        key "timeoutSeconds": int
        key "type": Union[str, SessionProbeType]
        failureThreshold: int
        httpGet: SessionProbeHttpGet
        initialDelaySeconds: int
        periodSeconds: int
        successThreshold: int
        tcpSocket: SessionProbeTcpSocket
        terminationGracePeriodSeconds: int
        timeoutSeconds: int
        type: Union[str, SessionProbeType]


    class azure.mgmt.appcontainers.types.SessionProbeHttpGet(TypedDict, total=False):
        key "host": str
        key "path": str
        key "port": Required[int]
        key "scheme": Union[str, Scheme]
        host: str
        httpHeaders: list[SessionProbeHttpGetHttpHeadersItem]
        path: str
        port: int
        scheme: Union[str, Scheme]


    class azure.mgmt.appcontainers.types.SessionProbeHttpGetHttpHeadersItem(TypedDict, total=False):
        key "name": Required[str]
        key "value": Required[str]
        name: str
        value: str


    class azure.mgmt.appcontainers.types.SessionProbeTcpSocket(TypedDict, total=False):
        key "host": str
        key "port": Required[int]
        host: str
        port: int


    class azure.mgmt.appcontainers.types.SessionRegistryCredentials(TypedDict, total=False):
        key "identity": str
        key "passwordSecretRef": str
        key "server": str
        key "username": str
        identity: str
        passwordSecretRef: str
        server: str
        username: str


    class azure.mgmt.appcontainers.types.SourceControl(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('SourceControlProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: SourceControlProperties
        systemData: SystemData
        type: str


    class azure.mgmt.appcontainers.types.SourceControlProperties(TypedDict, total=False):
        key "branch": str
        key "githubActionConfiguration": ForwardRef('GithubActionConfiguration', module='types')
        key "operationState": Union[str, SourceControlOperationState]
        key "repoUrl": str
        branch: str
        githubActionConfiguration: GithubActionConfiguration
        operationState: Union[str, SourceControlOperationState]
        repoUrl: str


    class azure.mgmt.appcontainers.types.SpringBootAdminComponent(TypedDict, total=False):
        key "componentType": Required[Literal[JavaComponentType.SPRING_BOOT_ADMIN]]
        key "ingress": ForwardRef('JavaComponentIngress', module='types')
        key "provisioningState": Union[str, JavaComponentProvisioningState]
        key "scale": ForwardRef('JavaComponentPropertiesScale', module='types')
        componentType: Literal[JavaComponentType.SPRING_BOOT_ADMIN]
        configurations: list[JavaComponentConfigurationProperty]
        ingress: JavaComponentIngress
        provisioningState: Union[str, JavaComponentProvisioningState]
        scale: JavaComponentPropertiesScale
        serviceBinds: list[JavaComponentServiceBind]


    class azure.mgmt.appcontainers.types.SpringCloudConfigComponent(TypedDict, total=False):
        key "componentType": Required[Literal[JavaComponentType.SPRING_CLOUD_CONFIG]]
        key "provisioningState": Union[str, JavaComponentProvisioningState]
        key "scale": ForwardRef('JavaComponentPropertiesScale', module='types')
        componentType: Literal[JavaComponentType.SPRING_CLOUD_CONFIG]
        configurations: list[JavaComponentConfigurationProperty]
        provisioningState: Union[str, JavaComponentProvisioningState]
        scale: JavaComponentPropertiesScale
        serviceBinds: list[JavaComponentServiceBind]


    class azure.mgmt.appcontainers.types.SpringCloudEurekaComponent(TypedDict, total=False):
        key "componentType": Required[Literal[JavaComponentType.SPRING_CLOUD_EUREKA]]
        key "ingress": ForwardRef('JavaComponentIngress', module='types')
        key "provisioningState": Union[str, JavaComponentProvisioningState]
        key "scale": ForwardRef('JavaComponentPropertiesScale', module='types')
        componentType: Literal[JavaComponentType.SPRING_CLOUD_EUREKA]
        configurations: list[JavaComponentConfigurationProperty]
        ingress: JavaComponentIngress
        provisioningState: Union[str, JavaComponentProvisioningState]
        scale: JavaComponentPropertiesScale
        serviceBinds: list[JavaComponentServiceBind]


    class azure.mgmt.appcontainers.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.appcontainers.types.TcpScaleRule(TypedDict, total=False):
        key "identity": str
        auth: list[ScaleRuleAuth]
        identity: str
        metadata: dict[str, str]


    class azure.mgmt.appcontainers.types.Template(TypedDict, total=False):
        key "revisionSuffix": str
        key "scale": ForwardRef('Scale', module='types')
        key "terminationGracePeriodSeconds": int
        containers: list[Container]
        initContainers: list[InitContainer]
        revisionSuffix: str
        scale: Scale
        serviceBinds: list[ServiceBind]
        terminationGracePeriodSeconds: int
        volumes: list[Volume]


    class azure.mgmt.appcontainers.types.TokenStore(TypedDict, total=False):
        key "azureBlobStorage": ForwardRef('BlobStorageTokenStore', module='types')
        key "enabled": bool
        key "tokenRefreshExtensionHours": float
        azureBlobStorage: BlobStorageTokenStore
        enabled: bool
        tokenRefreshExtensionHours: float


    class azure.mgmt.appcontainers.types.TracesConfiguration(TypedDict, total=False):
        key "includeDapr": bool
        destinations: list[str]
        includeDapr: bool


    class azure.mgmt.appcontainers.types.TrackedResource(Resource):
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


    class azure.mgmt.appcontainers.types.TrafficWeight(TypedDict, total=False):
        key "label": str
        key "latestRevision": bool
        key "revisionName": str
        key "weight": int
        label: str
        latestRevision: bool
        revisionName: str
        weight: int


    class azure.mgmt.appcontainers.types.Twitter(TypedDict, total=False):
        key "enabled": bool
        key "registration": ForwardRef('TwitterRegistration', module='types')
        enabled: bool
        registration: TwitterRegistration


    class azure.mgmt.appcontainers.types.TwitterRegistration(TypedDict, total=False):
        key "consumerKey": str
        key "consumerSecretSettingName": str
        consumerKey: str
        consumerSecretSettingName: str


    class azure.mgmt.appcontainers.types.UserAssignedIdentity(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        clientId: str
        principalId: str


    class azure.mgmt.appcontainers.types.VnetConfiguration(TypedDict, total=False):
        key "dockerBridgeCidr": str
        key "infrastructureSubnetId": str
        key "internal": bool
        key "platformReservedCidr": str
        key "platformReservedDnsIP": str
        dockerBridgeCidr: str
        infrastructureSubnetId: str
        internal: bool
        platformReservedCidr: str
        platformReservedDnsIP: str


    class azure.mgmt.appcontainers.types.VnetConnection(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('VnetConnectionProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: VnetConnectionProperties
        systemData: SystemData
        type: str


    class azure.mgmt.appcontainers.types.VnetConnectionProperties(TypedDict, total=False):
        key "provisioningState": Union[str, VnetConnectionProvisioningState]
        key "subnetId": str
        provisioningState: Union[str, VnetConnectionProvisioningState]
        subnetId: str


    class azure.mgmt.appcontainers.types.Volume(TypedDict, total=False):
        key "mountOptions": str
        key "name": str
        key "storageName": str
        key "storageType": Union[str, StorageType]
        mountOptions: str
        name: str
        secrets: list[SecretVolumeItem]
        storageName: str
        storageType: Union[str, StorageType]


    class azure.mgmt.appcontainers.types.VolumeMount(TypedDict, total=False):
        key "mountPath": str
        key "subPath": str
        key "volumeName": str
        mountPath: str
        subPath: str
        volumeName: str


    class azure.mgmt.appcontainers.types.WorkloadProfile(TypedDict, total=False):
        key "maximumCount": int
        key "minimumCount": int
        key "name": Required[str]
        key "workloadProfileType": Required[str]
        maximumCount: int
        minimumCount: int
        name: str
        workloadProfileType: str


```