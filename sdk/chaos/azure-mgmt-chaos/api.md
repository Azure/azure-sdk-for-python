```py
namespace azure.mgmt.chaos

    class azure.mgmt.chaos.ChaosManagementClient: implements ContextManager 
        action_versions: ActionVersionsOperations
        actions: ActionsOperations
        capabilities: CapabilitiesOperations
        capability_types: CapabilityTypesOperations
        connections: ConnectionsOperations
        discovered_resources: DiscoveredResourcesOperations
        experiments: ExperimentsOperations
        operation_statuses: OperationStatusesOperations
        operations: Operations
        private_accesses: PrivateAccessesOperations
        scenario_configurations: ScenarioConfigurationsOperations
        scenario_runs: ScenarioRunsOperations
        scenarios: ScenariosOperations
        target_types: TargetTypesOperations
        targets: TargetsOperations
        workspaces: WorkspacesOperations

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


namespace azure.mgmt.chaos.aio

    class azure.mgmt.chaos.aio.ChaosManagementClient: implements AsyncContextManager 
        action_versions: ActionVersionsOperations
        actions: ActionsOperations
        capabilities: CapabilitiesOperations
        capability_types: CapabilityTypesOperations
        connections: ConnectionsOperations
        discovered_resources: DiscoveredResourcesOperations
        experiments: ExperimentsOperations
        operation_statuses: OperationStatusesOperations
        operations: Operations
        private_accesses: PrivateAccessesOperations
        scenario_configurations: ScenarioConfigurationsOperations
        scenario_runs: ScenarioRunsOperations
        scenarios: ScenariosOperations
        target_types: TargetTypesOperations
        targets: TargetsOperations
        workspaces: WorkspacesOperations

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


namespace azure.mgmt.chaos.aio.operations

    class azure.mgmt.chaos.aio.operations.ActionVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'location', 'action_name', 'version_name', 'accept']}, api_versions_list=['2026-05-01-preview', '2026-08-01-preview'])
        async def get(
                self, 
                location: str, 
                action_name: str, 
                version_name: str, 
                **kwargs: Any
            ) -> ActionVersion: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'location', 'action_name', 'continuation_token_parameter', 'accept']}, api_versions_list=['2026-05-01-preview', '2026-08-01-preview'])
        def list(
                self, 
                location: str, 
                action_name: str, 
                *, 
                continuation_token_parameter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ActionVersion]: ...


    class azure.mgmt.chaos.aio.operations.ActionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'location', 'action_name', 'accept']}, api_versions_list=['2026-05-01-preview', '2026-08-01-preview'])
        async def get(
                self, 
                location: str, 
                action_name: str, 
                **kwargs: Any
            ) -> Action: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'location', 'continuation_token_parameter', 'accept']}, api_versions_list=['2026-05-01-preview', '2026-08-01-preview'])
        def list(
                self, 
                location: str, 
                *, 
                continuation_token_parameter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Action]: ...


    class azure.mgmt.chaos.aio.operations.CapabilitiesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                parent_provider_namespace: str, 
                parent_resource_type: str, 
                parent_resource_name: str, 
                target_name: str, 
                capability_name: str, 
                resource: Capability, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Capability: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                parent_provider_namespace: str, 
                parent_resource_type: str, 
                parent_resource_name: str, 
                target_name: str, 
                capability_name: str, 
                resource: Capability, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Capability: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                parent_provider_namespace: str, 
                parent_resource_type: str, 
                parent_resource_name: str, 
                target_name: str, 
                capability_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Capability: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                parent_provider_namespace: str, 
                parent_resource_type: str, 
                parent_resource_name: str, 
                target_name: str, 
                capability_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                parent_provider_namespace: str, 
                parent_resource_type: str, 
                parent_resource_name: str, 
                target_name: str, 
                capability_name: str, 
                **kwargs: Any
            ) -> Capability: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                parent_provider_namespace: str, 
                parent_resource_type: str, 
                parent_resource_name: str, 
                target_name: str, 
                *, 
                continuation_token_parameter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Capability]: ...


    class azure.mgmt.chaos.aio.operations.CapabilityTypesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                location: str, 
                target_type_name: str, 
                capability_type_name: str, 
                **kwargs: Any
            ) -> CapabilityType: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                target_type_name: str, 
                *, 
                continuation_token_parameter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[CapabilityType]: ...


    class azure.mgmt.chaos.aio.operations.ConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                connection_name: str, 
                resource: Connection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Connection: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                connection_name: str, 
                resource: Connection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Connection: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                connection_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Connection: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-08-01-preview', params_added_on={'2026-08-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'connection_name']}, api_versions_list=['2026-08-01-preview'])
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                connection_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-08-01-preview', params_added_on={'2026-08-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'connection_name', 'accept']}, api_versions_list=['2026-08-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                connection_name: str, 
                **kwargs: Any
            ) -> Connection: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-08-01-preview', params_added_on={'2026-08-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'accept']}, api_versions_list=['2026-08-01-preview'])
        def list_all(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Connection]: ...


    class azure.mgmt.chaos.aio.operations.DiscoveredResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'discovered_resource_name', 'accept']}, api_versions_list=['2026-05-01-preview', '2026-08-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                discovered_resource_name: str, 
                **kwargs: Any
            ) -> DiscoveredResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'accept']}, api_versions_list=['2026-05-01-preview', '2026-08-01-preview'])
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DiscoveredResource]: ...


    class azure.mgmt.chaos.aio.operations.ExperimentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_cancel(
                self, 
                resource_group_name: str, 
                experiment_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                experiment_name: str, 
                resource: Experiment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Experiment]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                experiment_name: str, 
                resource: Experiment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Experiment]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                experiment_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Experiment]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                experiment_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_start(
                self, 
                resource_group_name: str, 
                experiment_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                experiment_name: str, 
                properties: ExperimentUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Experiment]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                experiment_name: str, 
                properties: ExperimentUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Experiment]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                experiment_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Experiment]: ...

        @distributed_trace_async
        async def execution_details(
                self, 
                resource_group_name: str, 
                experiment_name: str, 
                execution_id: str, 
                **kwargs: Any
            ) -> ExperimentExecutionDetails: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                experiment_name: str, 
                **kwargs: Any
            ) -> Experiment: ...

        @distributed_trace_async
        async def get_execution(
                self, 
                resource_group_name: str, 
                experiment_name: str, 
                execution_id: str, 
                **kwargs: Any
            ) -> ExperimentExecution: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                *, 
                continuation_token_parameter: Optional[str] = ..., 
                running: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Experiment]: ...

        @distributed_trace
        def list_all(
                self, 
                *, 
                continuation_token_parameter: Optional[str] = ..., 
                running: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Experiment]: ...

        @distributed_trace
        def list_all_executions(
                self, 
                resource_group_name: str, 
                experiment_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ExperimentExecution]: ...


    class azure.mgmt.chaos.aio.operations.OperationStatusesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                location: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationStatusResult: ...


    class azure.mgmt.chaos.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_all(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.chaos.aio.operations.PrivateAccessesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_access_name: str, 
                resource: PrivateAccess, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateAccess]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_access_name: str, 
                resource: PrivateAccess, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateAccess]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_access_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateAccess]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'private_access_name']}, api_versions_list=['2026-05-01-preview', '2026-08-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                private_access_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'private_access_name', 'private_endpoint_connection_name']}, api_versions_list=['2026-05-01-preview', '2026-08-01-preview'])
        async def begin_delete_a_private_endpoint_connection(
                self, 
                resource_group_name: str, 
                private_access_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                private_access_name: str, 
                properties: PrivateAccessPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateAccess]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                private_access_name: str, 
                properties: PrivateAccessPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateAccess]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                private_access_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateAccess]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'private_access_name', 'accept']}, api_versions_list=['2026-05-01-preview', '2026-08-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                private_access_name: str, 
                **kwargs: Any
            ) -> PrivateAccess: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'private_access_name', 'private_endpoint_connection_name', 'accept']}, api_versions_list=['2026-05-01-preview', '2026-08-01-preview'])
        async def get_a_private_endpoint_connection(
                self, 
                resource_group_name: str, 
                private_access_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'private_access_name', 'accept']}, api_versions_list=['2026-05-01-preview', '2026-08-01-preview'])
        async def get_private_link_resources(
                self, 
                resource_group_name: str, 
                private_access_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResourceListResult: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'continuation_token_parameter', 'accept']}, api_versions_list=['2026-05-01-preview', '2026-08-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                *, 
                continuation_token_parameter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateAccess]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'continuation_token_parameter', 'accept']}, api_versions_list=['2026-05-01-preview', '2026-08-01-preview'])
        def list_all(
                self, 
                *, 
                continuation_token_parameter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateAccess]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'private_access_name', 'accept']}, api_versions_list=['2026-05-01-preview', '2026-08-01-preview'])
        def list_private_endpoint_connections(
                self, 
                resource_group_name: str, 
                private_access_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateEndpointConnection]: ...


    class azure.mgmt.chaos.aio.operations.ScenarioConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                scenario_name: str, 
                scenario_configuration_name: str, 
                resource: ScenarioConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ScenarioConfiguration]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                scenario_name: str, 
                scenario_configuration_name: str, 
                resource: ScenarioConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ScenarioConfiguration]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                scenario_name: str, 
                scenario_configuration_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ScenarioConfiguration]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'scenario_name', 'scenario_configuration_name']}, api_versions_list=['2026-05-01-preview', '2026-08-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                scenario_name: str, 
                scenario_configuration_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'scenario_name', 'scenario_configuration_name']}, api_versions_list=['2026-05-01-preview', '2026-08-01-preview'])
        async def begin_execute(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                scenario_name: str, 
                scenario_configuration_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ScenarioRun]: ...

        @overload
        async def begin_fix_resource_permissions(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                scenario_name: str, 
                scenario_configuration_name: str, 
                body: Optional[FixResourcePermissionsRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PermissionsFix]: ...

        @overload
        async def begin_fix_resource_permissions(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                scenario_name: str, 
                scenario_configuration_name: str, 
                body: Optional[FixResourcePermissionsRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PermissionsFix]: ...

        @overload
        async def begin_fix_resource_permissions(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                scenario_name: str, 
                scenario_configuration_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PermissionsFix]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'scenario_name', 'scenario_configuration_name']}, api_versions_list=['2026-05-01-preview', '2026-08-01-preview'])
        async def begin_validate(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                scenario_name: str, 
                scenario_configuration_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[Validation]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'scenario_name', 'scenario_configuration_name', 'accept']}, api_versions_list=['2026-05-01-preview', '2026-08-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                scenario_name: str, 
                scenario_configuration_name: str, 
                **kwargs: Any
            ) -> ScenarioConfiguration: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'scenario_name', 'accept']}, api_versions_list=['2026-05-01-preview', '2026-08-01-preview'])
        def list_all(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                scenario_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ScenarioConfiguration]: ...


    class azure.mgmt.chaos.aio.operations.ScenarioRunsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'scenario_name', 'run_id']}, api_versions_list=['2026-05-01-preview', '2026-08-01-preview'])
        async def begin_cancel(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                scenario_name: str, 
                run_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ScenarioRun]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'scenario_name', 'run_id', 'accept']}, api_versions_list=['2026-05-01-preview', '2026-08-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                scenario_name: str, 
                run_id: str, 
                **kwargs: Any
            ) -> ScenarioRun: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'scenario_name', 'accept']}, api_versions_list=['2026-05-01-preview', '2026-08-01-preview'])
        def list_all(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                scenario_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ScenarioRun]: ...


    class azure.mgmt.chaos.aio.operations.ScenariosOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                scenario_name: str, 
                resource: Scenario, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Scenario: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                scenario_name: str, 
                resource: Scenario, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Scenario: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                scenario_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Scenario: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'scenario_name']}, api_versions_list=['2026-05-01-preview', '2026-08-01-preview'])
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                scenario_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'scenario_name', 'accept']}, api_versions_list=['2026-05-01-preview', '2026-08-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                scenario_name: str, 
                **kwargs: Any
            ) -> Scenario: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'accept']}, api_versions_list=['2026-05-01-preview', '2026-08-01-preview'])
        def list_all(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Scenario]: ...


    class azure.mgmt.chaos.aio.operations.TargetTypesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                location: str, 
                target_type_name: str, 
                **kwargs: Any
            ) -> TargetType: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                *, 
                continuation_token_parameter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[TargetType]: ...


    class azure.mgmt.chaos.aio.operations.TargetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                parent_provider_namespace: str, 
                parent_resource_type: str, 
                parent_resource_name: str, 
                target_name: str, 
                resource: Target, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Target: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                parent_provider_namespace: str, 
                parent_resource_type: str, 
                parent_resource_name: str, 
                target_name: str, 
                resource: Target, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Target: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                parent_provider_namespace: str, 
                parent_resource_type: str, 
                parent_resource_name: str, 
                target_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Target: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                parent_provider_namespace: str, 
                parent_resource_type: str, 
                parent_resource_name: str, 
                target_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                parent_provider_namespace: str, 
                parent_resource_type: str, 
                parent_resource_name: str, 
                target_name: str, 
                **kwargs: Any
            ) -> Target: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                parent_provider_namespace: str, 
                parent_resource_type: str, 
                parent_resource_name: str, 
                *, 
                continuation_token_parameter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Target]: ...


    class azure.mgmt.chaos.aio.operations.WorkspacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                resource: Workspace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Workspace]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                resource: Workspace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Workspace]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Workspace]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name']}, api_versions_list=['2026-05-01-preview', '2026-08-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-08-01-preview', params_added_on={'2026-08-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name']}, api_versions_list=['2026-08-01-preview'])
        async def begin_discover(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkspaceDiscovery]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-08-01-preview', params_added_on={'2026-08-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name']}, api_versions_list=['2026-08-01-preview'])
        async def begin_evaluate(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkspaceEvaluation]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                properties: WorkspaceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Workspace]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                properties: WorkspaceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Workspace]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Workspace]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'accept']}, api_versions_list=['2026-05-01-preview', '2026-08-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> Workspace: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'continuation_token_parameter', 'accept']}, api_versions_list=['2026-05-01-preview', '2026-08-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                *, 
                continuation_token_parameter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Workspace]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'continuation_token_parameter', 'accept']}, api_versions_list=['2026-05-01-preview', '2026-08-01-preview'])
        def list_all(
                self, 
                *, 
                continuation_token_parameter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Workspace]: ...


namespace azure.mgmt.chaos.models

    class azure.mgmt.chaos.models.Action(ProxyResource):
        id: str
        name: str
        properties: ActionProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: ActionProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.chaos.models.ActionDependency(_Model):
        name: str
        on_action_lifecycle: Optional[Union[str, ActionLifecycle]]
        type: Union[str, ActionDependencyType]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                on_action_lifecycle: Optional[Union[str, ActionLifecycle]] = ..., 
                type: Union[str, ActionDependencyType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.chaos.models.ActionDependencyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTION = "Action"


    class azure.mgmt.chaos.models.ActionKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELABLE = "Cancelable"
        CONTINUOUS = "Continuous"
        DISCRETE = "Discrete"


    class azure.mgmt.chaos.models.ActionLifecycle(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANY_TERMINAL = "AnyTerminal"
        FAILURE = "Failure"
        RUNNING = "Running"
        SKIPPED = "Skipped"
        START = "Start"
        SUCCESS = "Success"


    class azure.mgmt.chaos.models.ActionProperties(_Model):
        action_name: Optional[str]
        action_type: Optional[Union[str, ActionKind]]
        canonical_id: Optional[str]
        description: Optional[str]
        display_name: Optional[str]
        parameters_schema: Optional[Any]
        recommended_roles: Optional[list[str]]
        supported_target_types: Optional[list[ActionSupportedTargetType]]
        version: Optional[str]


    class azure.mgmt.chaos.models.ActionStatus(_Model):
        action_id: Optional[str]
        action_name: Optional[str]
        end_time: Optional[datetime]
        start_time: Optional[datetime]
        status: Optional[str]
        targets: Optional[list[ExperimentExecutionActionTargetDetailsProperties]]


    class azure.mgmt.chaos.models.ActionSupportedTargetType(_Model):
        required_permissions: Optional[list[str]]
        target_type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                required_permissions: Optional[list[str]] = ..., 
                target_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.chaos.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.chaos.models.ActionVersion(ProxyResource):
        id: str
        name: str
        properties: ActionProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: ActionProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.chaos.models.BranchStatus(_Model):
        actions: Optional[list[ActionStatus]]
        branch_id: Optional[str]
        branch_name: Optional[str]
        status: Optional[str]


    class azure.mgmt.chaos.models.Capability(ProxyResource):
        id: str
        name: str
        properties: Optional[CapabilityProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CapabilityProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.chaos.models.CapabilityProperties(_Model):
        description: Optional[str]
        parameters_schema: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        publisher: Optional[str]
        target_type: Optional[str]
        urn: Optional[str]


    class azure.mgmt.chaos.models.CapabilityType(ProxyResource):
        id: str
        name: str
        properties: Optional[CapabilityTypeProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CapabilityTypeProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.chaos.models.CapabilityTypeProperties(_Model):
        azure_rbac_actions: Optional[list[str]]
        azure_rbac_data_actions: Optional[list[str]]
        description: Optional[str]
        display_name: Optional[str]
        kind: Optional[str]
        parameters_schema: Optional[str]
        publisher: Optional[str]
        required_azure_role_definition_ids: Optional[list[str]]
        runtime_properties: Optional[CapabilityTypePropertiesRuntimeProperties]
        target_type: Optional[str]
        urn: Optional[str]


    class azure.mgmt.chaos.models.CapabilityTypePropertiesRuntimeProperties(_Model):
        kind: Optional[str]


    class azure.mgmt.chaos.models.ChaosExperimentAction(_Model):
        name: str
        type: str

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.chaos.models.ChaosExperimentBranch(_Model):
        actions: list[ChaosExperimentAction]
        name: str

        @overload
        def __init__(
                self, 
                *, 
                actions: list[ChaosExperimentAction], 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.chaos.models.ChaosExperimentStep(_Model):
        branches: list[ChaosExperimentBranch]
        name: str

        @overload
        def __init__(
                self, 
                *, 
                branches: list[ChaosExperimentBranch], 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.chaos.models.ChaosTargetFilter(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.chaos.models.ChaosTargetListSelector(ChaosTargetSelector, discriminator='List'):
        filter: ChaosTargetFilter
        id: str
        targets: list[TargetReference]
        type: Literal[SelectorType.LIST]

        @overload
        def __init__(
                self, 
                *, 
                filter: Optional[ChaosTargetFilter] = ..., 
                id: str, 
                targets: list[TargetReference]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.chaos.models.ChaosTargetQuerySelector(ChaosTargetSelector, discriminator='Query'):
        filter: ChaosTargetFilter
        id: str
        query_string: str
        subscription_ids: list[str]
        type: Literal[SelectorType.QUERY]

        @overload
        def __init__(
                self, 
                *, 
                filter: Optional[ChaosTargetFilter] = ..., 
                id: str, 
                query_string: str, 
                subscription_ids: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.chaos.models.ChaosTargetSelector(_Model):
        filter: Optional[ChaosTargetFilter]
        id: str
        type: str

        @overload
        def __init__(
                self, 
                *, 
                filter: Optional[ChaosTargetFilter] = ..., 
                id: str, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.chaos.models.ChaosTargetSimpleFilter(ChaosTargetFilter, discriminator='Simple'):
        parameters: Optional[ChaosTargetSimpleFilterParameters]
        type: Literal[FilterType.SIMPLE]

        @overload
        def __init__(
                self, 
                *, 
                parameters: Optional[ChaosTargetSimpleFilterParameters] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.chaos.models.ChaosTargetSimpleFilterParameters(_Model):
        zones: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                zones: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.chaos.models.Connection(ProxyResource):
        id: str
        name: str
        properties: Optional[ConnectionProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ConnectionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.chaos.models.ConnectionKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AKS_EXTENSION = "AksExtension"
        CHAOS_AGENT = "ChaosAgent"
        CSFI = "Csfi"


    class azure.mgmt.chaos.models.ConnectionProperties(_Model):
        certificate_issuer: Optional[str]
        certificate_subject_name: Optional[str]
        data_plane_endpoint: Optional[str]
        dsts_principal: Optional[str]
        kind: Union[str, ConnectionKind]
        principal_id: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        status: Optional[Union[str, ConnectionStatus]]
        target_resource_id: str
        tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                certificate_issuer: Optional[str] = ..., 
                certificate_subject_name: Optional[str] = ..., 
                dsts_principal: Optional[str] = ..., 
                kind: Union[str, ConnectionKind], 
                principal_id: Optional[str] = ..., 
                target_resource_id: str, 
                tenant_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.chaos.models.ConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONNECTED = "Connected"
        DISCONNECTED = "Disconnected"
        PENDING = "Pending"
        REVOKED = "Revoked"


    class azure.mgmt.chaos.models.ContinuousAction(ChaosExperimentAction, discriminator='continuous'):
        duration: timedelta
        name: str
        parameters: list[KeyValuePair]
        selector_id: str
        type: Literal[ExperimentActionType.CONTINUOUS]

        @overload
        def __init__(
                self, 
                *, 
                duration: timedelta, 
                name: str, 
                parameters: list[KeyValuePair], 
                selector_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.chaos.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.chaos.models.CustomerDataStorageProperties(_Model):
        blob_container_name: Optional[str]
        storage_account_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                blob_container_name: Optional[str] = ..., 
                storage_account_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.chaos.models.DelayAction(ChaosExperimentAction, discriminator='delay'):
        duration: timedelta
        name: str
        type: Literal[ExperimentActionType.DELAY]

        @overload
        def __init__(
                self, 
                *, 
                duration: timedelta, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.chaos.models.DiscoveredResource(ProxyResource):
        id: str
        name: str
        properties: Optional[DiscoveredResourceProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DiscoveredResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.chaos.models.DiscoveredResourceProperties(_Model):
        discovered_at: datetime
        fully_qualified_identifier: str
        resource_name: str
        resource_namespace: str
        resource_type: str
        scope: str


    class azure.mgmt.chaos.models.DiscreteAction(ChaosExperimentAction, discriminator='discrete'):
        name: str
        parameters: list[KeyValuePair]
        selector_id: str
        type: Literal[ExperimentActionType.DISCRETE]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                parameters: list[KeyValuePair], 
                selector_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.chaos.models.EntraIdentity(_Model):
        object_id: str
        tenant_id: str


    class azure.mgmt.chaos.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.chaos.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.chaos.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.chaos.models.Experiment(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: ExperimentProperties
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
                properties: ExperimentProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.chaos.models.ExperimentActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTINUOUS = "continuous"
        DELAY = "delay"
        DISCRETE = "discrete"


    class azure.mgmt.chaos.models.ExperimentExecution(ProxyResource):
        id: str
        name: str
        properties: Optional[ExperimentExecutionProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ExperimentExecutionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.chaos.models.ExperimentExecutionActionTargetDetailsError(_Model):
        code: Optional[str]
        message: Optional[str]


    class azure.mgmt.chaos.models.ExperimentExecutionActionTargetDetailsProperties(_Model):
        error: Optional[ExperimentExecutionActionTargetDetailsError]
        status: Optional[str]
        target: Optional[str]
        target_completed_time: Optional[datetime]
        target_failed_time: Optional[datetime]


    class azure.mgmt.chaos.models.ExperimentExecutionDetails(_Model):
        id: Optional[str]
        name: Optional[str]
        properties: Optional[ExperimentExecutionDetailsProperties]
        type: Optional[str]


    class azure.mgmt.chaos.models.ExperimentExecutionDetailsProperties(_Model):
        failure_reason: Optional[str]
        last_action_at: Optional[datetime]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        run_information: Optional[ExperimentExecutionDetailsPropertiesRunInformation]
        started_at: Optional[datetime]
        status: Optional[str]
        stopped_at: Optional[datetime]


    class azure.mgmt.chaos.models.ExperimentExecutionDetailsPropertiesRunInformation(_Model):
        steps: Optional[list[StepStatus]]


    class azure.mgmt.chaos.models.ExperimentExecutionProperties(_Model):
        provisioning_state: Optional[Union[str, ProvisioningState]]
        started_at: Optional[datetime]
        status: Optional[str]
        stopped_at: Optional[datetime]


    class azure.mgmt.chaos.models.ExperimentProperties(_Model):
        customer_data_storage: Optional[CustomerDataStorageProperties]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        selectors: list[ChaosTargetSelector]
        steps: list[ChaosExperimentStep]

        @overload
        def __init__(
                self, 
                *, 
                customer_data_storage: Optional[CustomerDataStorageProperties] = ..., 
                selectors: list[ChaosTargetSelector], 
                steps: list[ChaosExperimentStep]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.chaos.models.ExperimentUpdate(_Model):
        identity: Optional[ManagedServiceIdentity]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.chaos.models.ExternalResource(_Model):
        resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.chaos.models.FilterType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SIMPLE = "Simple"


    class azure.mgmt.chaos.models.FixResourcePermissionsRequest(_Model):
        what_if: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                what_if: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.chaos.models.KeyValuePair(_Model):
        key: str
        value: str

        @overload
        def __init__(
                self, 
                *, 
                key: str, 
                value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.chaos.models.ManagedServiceIdentity(_Model):
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


    class azure.mgmt.chaos.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.chaos.models.Operation(_Model):
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


    class azure.mgmt.chaos.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.chaos.models.OperationError(_Model):
        error_code: str
        error_message: str

        @overload
        def __init__(
                self, 
                *, 
                error_code: str, 
                error_message: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.chaos.models.OperationStatusResult(_Model):
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


    class azure.mgmt.chaos.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.chaos.models.ParameterType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARRAY = "array"
        BOOLEAN = "boolean"
        NUMBER = "number"
        OBJECT = "object"
        STRING = "string"


    class azure.mgmt.chaos.models.PermissionError(_Model):
        error_message: Optional[str]
        identity: Optional[EntraIdentity]
        missing_permissions: list[str]
        recommended_roles: list[str]
        required_permissions: list[str]
        resource_id: str


    class azure.mgmt.chaos.models.PermissionsFix(ProxyResource):
        id: str
        name: str
        properties: Optional[PermissionsFixProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PermissionsFixProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.chaos.models.PermissionsFixProperties(_Model):
        completed_at: Optional[datetime]
        role_assignments: list[RoleAssignmentResult]
        started_at: datetime
        state: Union[str, PermissionsFixState]
        summary: PermissionsFixSummary
        what_if_mode: bool


    class azure.mgmt.chaos.models.PermissionsFixState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        NOT_STARTED = "NotStarted"
        PARTIALLY_SUCCEEDED = "PartiallySucceeded"
        SUCCEEDED = "Succeeded"
        WHAT_IF_COMPLETED = "WhatIfCompleted"


    class azure.mgmt.chaos.models.PermissionsFixSummary(_Model):
        failed: int
        skipped: int
        succeeded: int
        total_required: int


    class azure.mgmt.chaos.models.PhysicalToLogicalZoneMapping(_Model):
        logical_zone: str
        physical_zone: str


    class azure.mgmt.chaos.models.PrivateAccess(TrackedResource):
        id: str
        location: str
        name: str
        properties: PrivateAccessProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: PrivateAccessProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.chaos.models.PrivateAccessPatch(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.chaos.models.PrivateAccessProperties(_Model):
        private_endpoint_connections: Optional[list[PrivateEndpointConnection]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        public_network_access: Optional[Union[str, PublicNetworkAccessOption]]

        @overload
        def __init__(
                self, 
                *, 
                public_network_access: Optional[Union[str, PublicNetworkAccessOption]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.chaos.models.PrivateEndpoint(_Model):
        id: Optional[str]


    class azure.mgmt.chaos.models.PrivateEndpointConnection(ProxyResource):
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


    class azure.mgmt.chaos.models.PrivateEndpointConnectionProperties(_Model):
        group_ids: Optional[list[str]]
        private_endpoint: Optional[PrivateEndpoint]
        private_link_service_connection_state: PrivateLinkServiceConnectionState
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                private_endpoint: Optional[PrivateEndpoint] = ..., 
                private_link_service_connection_state: PrivateLinkServiceConnectionState
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.chaos.models.PrivateEndpointServiceConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.chaos.models.PrivateLinkResource(TrackedResource):
        id: str
        location: str
        name: str
        properties: PrivateLinkResourceProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: PrivateLinkResourceProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.chaos.models.PrivateLinkResourceListResult(_Model):
        next_link: Optional[str]
        value: list[PrivateLinkResource]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[PrivateLinkResource]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.chaos.models.PrivateLinkResourceProperties(_Model):
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


    class azure.mgmt.chaos.models.PrivateLinkServiceConnectionState(_Model):
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


    class azure.mgmt.chaos.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        RUNNING = "Running"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.chaos.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.chaos.models.PublicNetworkAccessOption(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.chaos.models.Recommendation(_Model):
        evaluation_run_at: Optional[datetime]
        recommendation_status: Union[str, RecommendationStatus]


    class azure.mgmt.chaos.models.RecommendationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EVALUATING = "Evaluating"
        EVALUATION_CANCELLED = "EvaluationCancelled"
        EVALUATION_FAILED = "EvaluationFailed"
        NOT_APPLICABLE = "NotApplicable"
        NOT_EVALUATED = "NotEvaluated"
        RECOMMENDED = "Recommended"


    class azure.mgmt.chaos.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.chaos.models.ResourceStateError(_Model):
        error_code: int
        error_message: str
        remediation_uri: str
        resource_id: str


    class azure.mgmt.chaos.models.ResourceTargeting(_Model):
        exclude: Optional[ResourceTargetingCriteria]
        include: Optional[ResourceTargetingCriteria]

        @overload
        def __init__(
                self, 
                *, 
                exclude: Optional[ResourceTargetingCriteria] = ..., 
                include: Optional[ResourceTargetingCriteria] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.chaos.models.ResourceTargetingCriteria(_Model):
        locations: Optional[list[str]]
        physical_zones: Optional[list[str]]
        resources: Optional[list[str]]
        tags: Optional[list[KeyValuePair]]
        types: Optional[list[str]]
        zones: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                locations: Optional[list[str]] = ..., 
                physical_zones: Optional[list[str]] = ..., 
                resources: Optional[list[str]] = ..., 
                tags: Optional[list[KeyValuePair]] = ..., 
                types: Optional[list[str]] = ..., 
                zones: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.chaos.models.RoleAssignmentError(_Model):
        code: str
        message: str


    class azure.mgmt.chaos.models.RoleAssignmentResult(_Model):
        error: Optional[RoleAssignmentError]
        principal_id: str
        role_assignment_id: Optional[str]
        role_definition_id: str
        role_definition_name: str
        scope: str
        status: Union[str, RoleAssignmentStatus]
        target_resource_id: str


    class azure.mgmt.chaos.models.RoleAssignmentStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        PENDING = "Pending"
        SKIPPED = "Skipped"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.chaos.models.RunAfter(_Model):
        behavior: Optional[Union[str, RunAfterBehavior]]
        items_property: list[ActionDependency]

        @overload
        def __init__(
                self, 
                *, 
                behavior: Optional[Union[str, RunAfterBehavior]] = ..., 
                items_property: list[ActionDependency]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.chaos.models.RunAfterBehavior(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL = "All"
        ANY = "Any"
        AT_LEAST_ONE = "AtLeastOne"


    class azure.mgmt.chaos.models.Scenario(ProxyResource):
        id: str
        name: str
        properties: Optional[ScenarioProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ScenarioProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.chaos.models.ScenarioAction(_Model):
        action_id: str
        description: Optional[str]
        duration: str
        external_resource: Optional[ExternalResource]
        name: str
        parameters: Optional[list[KeyValuePair]]
        run_after: Optional[RunAfter]
        timeout: Optional[str]
        wait_before: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                action_id: str, 
                description: Optional[str] = ..., 
                duration: str, 
                external_resource: Optional[ExternalResource] = ..., 
                name: str, 
                parameters: Optional[list[KeyValuePair]] = ..., 
                run_after: Optional[RunAfter] = ..., 
                timeout: Optional[str] = ..., 
                wait_before: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.chaos.models.ScenarioConfiguration(ProxyResource):
        id: str
        name: str
        properties: Optional[ScenarioConfigurationProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ScenarioConfigurationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.chaos.models.ScenarioConfigurationProperties(_Model):
        parameters: Optional[list[KeyValuePair]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        resource_targeting: Optional[ResourceTargeting]
        scenario_id: str

        @overload
        def __init__(
                self, 
                *, 
                parameters: Optional[list[KeyValuePair]] = ..., 
                resource_targeting: Optional[ResourceTargeting] = ..., 
                scenario_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.chaos.models.ScenarioErrors(_Model):
        error_code: Optional[str]
        error_message: Optional[str]
        permission: list[PermissionError]
        resource: list[ResourceStateError]

        @overload
        def __init__(
                self, 
                *, 
                error_code: Optional[str] = ..., 
                error_message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.chaos.models.ScenarioParameter(_Model):
        default: Optional[str]
        description: Optional[str]
        name: str
        required: Optional[bool]
        type: Union[str, ParameterType]

        @overload
        def __init__(
                self, 
                *, 
                default: Optional[str] = ..., 
                description: Optional[str] = ..., 
                name: str, 
                required: Optional[bool] = ..., 
                type: Union[str, ParameterType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.chaos.models.ScenarioProperties(_Model):
        actions: list[ScenarioAction]
        created_from: Optional[str]
        description: Optional[str]
        parameters: list[ScenarioParameter]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        recommendation: Optional[Recommendation]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                actions: list[ScenarioAction], 
                description: Optional[str] = ..., 
                parameters: list[ScenarioParameter]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.chaos.models.ScenarioRun(ProxyResource):
        id: str
        name: str
        properties: Optional[ScenarioRunProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ScenarioRunProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.chaos.models.ScenarioRunProperties(_Model):
        end_time: Optional[datetime]
        errors: Optional[list[OperationError]]
        excluded_resources: Optional[list[ScenarioRunResource]]
        execution_errors: Optional[ScenarioErrors]
        managed_identity_principal_id: str
        resource_snapshot_id: Optional[str]
        resources: list[ScenarioRunResource]
        scenario_configuration_name: str
        scenario_name: str
        scenario_run_json: Optional[str]
        scenario_run_summary: Optional[list[ScenarioRunSummaryAction]]
        start_time: datetime
        status: Union[str, ScenarioRunState]
        workspace_name: str
        zone_resolution: Optional[ZoneResolutionInfo]


    class azure.mgmt.chaos.models.ScenarioRunResource(_Model):
        id: str


    class azure.mgmt.chaos.models.ScenarioRunState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CANCELING = "Canceling"
        CLEANING_UP = "CleaningUp"
        FAILED = "Failed"
        GENERATING = "Generating"
        PREPARING = "Preparing"
        QUEUED = "Queued"
        RESOLVING = "Resolving"
        RUNNING = "Running"
        STARTING = "Starting"
        SUCCEEDED = "Succeeded"
        VALIDATING = "Validating"
        VALIDATION_SUCCEEDED = "ValidationSucceeded"


    class azure.mgmt.chaos.models.ScenarioRunSummaryAction(_Model):
        action_urn: str
        completed_at: Optional[datetime]
        resources: list[ScenarioRunResource]
        started_at: Optional[datetime]
        state: Union[str, ScenarioSummaryState]


    class azure.mgmt.chaos.models.ScenarioSummaryState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CANCELING = "Canceling"
        FAILED = "Failed"
        FAILING_ON_ERROR = "FailingOnError"
        PENDING = "Pending"
        RUNNING = "Running"
        SKIPPED = "Skipped"
        STARTING = "Starting"
        STOPPING = "Stopping"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.chaos.models.ScenarioValidationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        GENERATING = "Generating"
        NOT_STARTED = "NotStarted"
        NO_RESOLVED_RESOURCES = "NoResolvedResources"
        REQUIRES_ATTENTION = "RequiresAttention"
        RESOLVING = "Resolving"
        SUCCEEDED = "Succeeded"
        VALIDATING = "Validating"


    class azure.mgmt.chaos.models.SelectorType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LIST = "List"
        QUERY = "Query"


    class azure.mgmt.chaos.models.StepStatus(_Model):
        branches: Optional[list[BranchStatus]]
        status: Optional[str]
        step_id: Optional[str]
        step_name: Optional[str]


    class azure.mgmt.chaos.models.SystemData(_Model):
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


    class azure.mgmt.chaos.models.Target(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: dict[str, Any]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: dict[str, Any]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.chaos.models.TargetReference(_Model):
        id: str
        type: Union[str, TargetReferenceType]

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                type: Union[str, TargetReferenceType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.chaos.models.TargetReferenceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CHAOS_TARGET = "ChaosTarget"


    class azure.mgmt.chaos.models.TargetType(ProxyResource):
        id: str
        name: str
        properties: TargetTypeProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: TargetTypeProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.chaos.models.TargetTypeProperties(_Model):
        description: Optional[str]
        display_name: Optional[str]
        properties_schema: Optional[str]
        resource_types: Optional[list[str]]


    class azure.mgmt.chaos.models.TemplateEvaluationResultItem(_Model):
        evaluation_result: Union[str, RecommendationStatus]
        template_id: Optional[str]
        template_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                evaluation_result: Union[str, RecommendationStatus], 
                template_id: Optional[str] = ..., 
                template_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.chaos.models.TrackedResource(Resource):
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


    class azure.mgmt.chaos.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.chaos.models.Validation(ProxyResource):
        id: str
        name: str
        properties: Optional[ValidationProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ValidationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.chaos.models.ValidationProperties(_Model):
        end_time: Optional[datetime]
        errors: Optional[list[OperationError]]
        excluded_resources: Optional[list[ScenarioRunResource]]
        execution_plan_json: Optional[str]
        resources: Optional[list[ScenarioRunResource]]
        start_time: datetime
        status: Union[str, ScenarioValidationState]
        validation_errors: Optional[ScenarioErrors]

        @overload
        def __init__(
                self, 
                *, 
                execution_plan_json: Optional[str] = ..., 
                validation_errors: Optional[ScenarioErrors] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.chaos.models.Workspace(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: WorkspaceProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: str, 
                properties: WorkspaceProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.chaos.models.WorkspaceDiscovery(ProxyResource):
        id: str
        name: str
        properties: Optional[WorkspaceDiscoveryProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[WorkspaceDiscoveryProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.chaos.models.WorkspaceDiscoveryProperties(_Model):
        end_time: Optional[datetime]
        errors: Optional[list[OperationError]]
        resource_snapshot_id: Optional[str]
        start_time: Optional[datetime]
        status: Union[str, WorkspaceDiscoveryStatus]
        workspace_id: str


    class azure.mgmt.chaos.models.WorkspaceDiscoveryStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        PENDING = "Pending"
        QUEUED = "Queued"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.chaos.models.WorkspaceEvaluation(ProxyResource):
        id: str
        name: str
        properties: Optional[WorkspaceEvaluationProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[WorkspaceEvaluationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.chaos.models.WorkspaceEvaluationProperties(_Model):
        end_time: Optional[datetime]
        errors: Optional[list[OperationError]]
        evaluation_result: Optional[Union[str, RecommendationStatus]]
        num_templates_evaluated_cancelled: Optional[int]
        num_templates_evaluated_failed: Optional[int]
        num_templates_evaluated_succeeded: Optional[int]
        num_templates_to_evaluate: Optional[int]
        resource_snapshot_id: Optional[str]
        results: Optional[list[TemplateEvaluationResultItem]]
        start_time: Optional[datetime]
        status: Union[str, WorkspaceEvaluationStatus]
        workspace_id: str


    class azure.mgmt.chaos.models.WorkspaceEvaluationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        PARTIALLY_SUCCEEDED = "PartiallySucceeded"
        PENDING = "Pending"
        QUEUED = "Queued"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.chaos.models.WorkspaceProperties(_Model):
        communication_endpoint: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        scopes: list[str]

        @overload
        def __init__(
                self, 
                *, 
                scopes: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.chaos.models.WorkspaceUpdate(_Model):
        identity: Optional[ManagedServiceIdentity]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.chaos.models.ZoneResolutionInfo(_Model):
        mode: Union[str, ZoneResolutionMode]
        requested_physical_zones: list[str]
        subscription_zone_mappings: list[ZoneResolutionMapping]


    class azure.mgmt.chaos.models.ZoneResolutionMapping(_Model):
        subscription_id: str
        zone_mappings: list[PhysicalToLogicalZoneMapping]


    class azure.mgmt.chaos.models.ZoneResolutionMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOGICAL = "logical"
        PHYSICAL = "physical"


namespace azure.mgmt.chaos.operations

    class azure.mgmt.chaos.operations.ActionVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'location', 'action_name', 'version_name', 'accept']}, api_versions_list=['2026-05-01-preview', '2026-08-01-preview'])
        def get(
                self, 
                location: str, 
                action_name: str, 
                version_name: str, 
                **kwargs: Any
            ) -> ActionVersion: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'location', 'action_name', 'continuation_token_parameter', 'accept']}, api_versions_list=['2026-05-01-preview', '2026-08-01-preview'])
        def list(
                self, 
                location: str, 
                action_name: str, 
                *, 
                continuation_token_parameter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ActionVersion]: ...


    class azure.mgmt.chaos.operations.ActionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'location', 'action_name', 'accept']}, api_versions_list=['2026-05-01-preview', '2026-08-01-preview'])
        def get(
                self, 
                location: str, 
                action_name: str, 
                **kwargs: Any
            ) -> Action: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'location', 'continuation_token_parameter', 'accept']}, api_versions_list=['2026-05-01-preview', '2026-08-01-preview'])
        def list(
                self, 
                location: str, 
                *, 
                continuation_token_parameter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Action]: ...


    class azure.mgmt.chaos.operations.CapabilitiesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                parent_provider_namespace: str, 
                parent_resource_type: str, 
                parent_resource_name: str, 
                target_name: str, 
                capability_name: str, 
                resource: Capability, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Capability: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                parent_provider_namespace: str, 
                parent_resource_type: str, 
                parent_resource_name: str, 
                target_name: str, 
                capability_name: str, 
                resource: Capability, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Capability: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                parent_provider_namespace: str, 
                parent_resource_type: str, 
                parent_resource_name: str, 
                target_name: str, 
                capability_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Capability: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                parent_provider_namespace: str, 
                parent_resource_type: str, 
                parent_resource_name: str, 
                target_name: str, 
                capability_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                parent_provider_namespace: str, 
                parent_resource_type: str, 
                parent_resource_name: str, 
                target_name: str, 
                capability_name: str, 
                **kwargs: Any
            ) -> Capability: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                parent_provider_namespace: str, 
                parent_resource_type: str, 
                parent_resource_name: str, 
                target_name: str, 
                *, 
                continuation_token_parameter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Capability]: ...


    class azure.mgmt.chaos.operations.CapabilityTypesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                target_type_name: str, 
                capability_type_name: str, 
                **kwargs: Any
            ) -> CapabilityType: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                target_type_name: str, 
                *, 
                continuation_token_parameter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[CapabilityType]: ...


    class azure.mgmt.chaos.operations.ConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                connection_name: str, 
                resource: Connection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Connection: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                connection_name: str, 
                resource: Connection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Connection: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                connection_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Connection: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-08-01-preview', params_added_on={'2026-08-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'connection_name']}, api_versions_list=['2026-08-01-preview'])
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                connection_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-08-01-preview', params_added_on={'2026-08-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'connection_name', 'accept']}, api_versions_list=['2026-08-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                connection_name: str, 
                **kwargs: Any
            ) -> Connection: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-08-01-preview', params_added_on={'2026-08-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'accept']}, api_versions_list=['2026-08-01-preview'])
        def list_all(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Connection]: ...


    class azure.mgmt.chaos.operations.DiscoveredResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'discovered_resource_name', 'accept']}, api_versions_list=['2026-05-01-preview', '2026-08-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                discovered_resource_name: str, 
                **kwargs: Any
            ) -> DiscoveredResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'accept']}, api_versions_list=['2026-05-01-preview', '2026-08-01-preview'])
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DiscoveredResource]: ...


    class azure.mgmt.chaos.operations.ExperimentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_cancel(
                self, 
                resource_group_name: str, 
                experiment_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                experiment_name: str, 
                resource: Experiment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Experiment]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                experiment_name: str, 
                resource: Experiment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Experiment]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                experiment_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Experiment]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                experiment_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_start(
                self, 
                resource_group_name: str, 
                experiment_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                experiment_name: str, 
                properties: ExperimentUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Experiment]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                experiment_name: str, 
                properties: ExperimentUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Experiment]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                experiment_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Experiment]: ...

        @distributed_trace
        def execution_details(
                self, 
                resource_group_name: str, 
                experiment_name: str, 
                execution_id: str, 
                **kwargs: Any
            ) -> ExperimentExecutionDetails: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                experiment_name: str, 
                **kwargs: Any
            ) -> Experiment: ...

        @distributed_trace
        def get_execution(
                self, 
                resource_group_name: str, 
                experiment_name: str, 
                execution_id: str, 
                **kwargs: Any
            ) -> ExperimentExecution: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                *, 
                continuation_token_parameter: Optional[str] = ..., 
                running: Optional[bool] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Experiment]: ...

        @distributed_trace
        def list_all(
                self, 
                *, 
                continuation_token_parameter: Optional[str] = ..., 
                running: Optional[bool] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Experiment]: ...

        @distributed_trace
        def list_all_executions(
                self, 
                resource_group_name: str, 
                experiment_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ExperimentExecution]: ...


    class azure.mgmt.chaos.operations.OperationStatusesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationStatusResult: ...


    class azure.mgmt.chaos.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_all(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.chaos.operations.PrivateAccessesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_access_name: str, 
                resource: PrivateAccess, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateAccess]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_access_name: str, 
                resource: PrivateAccess, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateAccess]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_access_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateAccess]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'private_access_name']}, api_versions_list=['2026-05-01-preview', '2026-08-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                private_access_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'private_access_name', 'private_endpoint_connection_name']}, api_versions_list=['2026-05-01-preview', '2026-08-01-preview'])
        def begin_delete_a_private_endpoint_connection(
                self, 
                resource_group_name: str, 
                private_access_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                private_access_name: str, 
                properties: PrivateAccessPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateAccess]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                private_access_name: str, 
                properties: PrivateAccessPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateAccess]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                private_access_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateAccess]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'private_access_name', 'accept']}, api_versions_list=['2026-05-01-preview', '2026-08-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                private_access_name: str, 
                **kwargs: Any
            ) -> PrivateAccess: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'private_access_name', 'private_endpoint_connection_name', 'accept']}, api_versions_list=['2026-05-01-preview', '2026-08-01-preview'])
        def get_a_private_endpoint_connection(
                self, 
                resource_group_name: str, 
                private_access_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'private_access_name', 'accept']}, api_versions_list=['2026-05-01-preview', '2026-08-01-preview'])
        def get_private_link_resources(
                self, 
                resource_group_name: str, 
                private_access_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResourceListResult: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'continuation_token_parameter', 'accept']}, api_versions_list=['2026-05-01-preview', '2026-08-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                *, 
                continuation_token_parameter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[PrivateAccess]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'continuation_token_parameter', 'accept']}, api_versions_list=['2026-05-01-preview', '2026-08-01-preview'])
        def list_all(
                self, 
                *, 
                continuation_token_parameter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[PrivateAccess]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'private_access_name', 'accept']}, api_versions_list=['2026-05-01-preview', '2026-08-01-preview'])
        def list_private_endpoint_connections(
                self, 
                resource_group_name: str, 
                private_access_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PrivateEndpointConnection]: ...


    class azure.mgmt.chaos.operations.ScenarioConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                scenario_name: str, 
                scenario_configuration_name: str, 
                resource: ScenarioConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ScenarioConfiguration]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                scenario_name: str, 
                scenario_configuration_name: str, 
                resource: ScenarioConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ScenarioConfiguration]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                scenario_name: str, 
                scenario_configuration_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ScenarioConfiguration]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'scenario_name', 'scenario_configuration_name']}, api_versions_list=['2026-05-01-preview', '2026-08-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                scenario_name: str, 
                scenario_configuration_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'scenario_name', 'scenario_configuration_name']}, api_versions_list=['2026-05-01-preview', '2026-08-01-preview'])
        def begin_execute(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                scenario_name: str, 
                scenario_configuration_name: str, 
                **kwargs: Any
            ) -> LROPoller[ScenarioRun]: ...

        @overload
        def begin_fix_resource_permissions(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                scenario_name: str, 
                scenario_configuration_name: str, 
                body: Optional[FixResourcePermissionsRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PermissionsFix]: ...

        @overload
        def begin_fix_resource_permissions(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                scenario_name: str, 
                scenario_configuration_name: str, 
                body: Optional[FixResourcePermissionsRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PermissionsFix]: ...

        @overload
        def begin_fix_resource_permissions(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                scenario_name: str, 
                scenario_configuration_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PermissionsFix]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'scenario_name', 'scenario_configuration_name']}, api_versions_list=['2026-05-01-preview', '2026-08-01-preview'])
        def begin_validate(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                scenario_name: str, 
                scenario_configuration_name: str, 
                **kwargs: Any
            ) -> LROPoller[Validation]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'scenario_name', 'scenario_configuration_name', 'accept']}, api_versions_list=['2026-05-01-preview', '2026-08-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                scenario_name: str, 
                scenario_configuration_name: str, 
                **kwargs: Any
            ) -> ScenarioConfiguration: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'scenario_name', 'accept']}, api_versions_list=['2026-05-01-preview', '2026-08-01-preview'])
        def list_all(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                scenario_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ScenarioConfiguration]: ...


    class azure.mgmt.chaos.operations.ScenarioRunsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'scenario_name', 'run_id']}, api_versions_list=['2026-05-01-preview', '2026-08-01-preview'])
        def begin_cancel(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                scenario_name: str, 
                run_id: str, 
                **kwargs: Any
            ) -> LROPoller[ScenarioRun]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'scenario_name', 'run_id', 'accept']}, api_versions_list=['2026-05-01-preview', '2026-08-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                scenario_name: str, 
                run_id: str, 
                **kwargs: Any
            ) -> ScenarioRun: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'scenario_name', 'accept']}, api_versions_list=['2026-05-01-preview', '2026-08-01-preview'])
        def list_all(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                scenario_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ScenarioRun]: ...


    class azure.mgmt.chaos.operations.ScenariosOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                scenario_name: str, 
                resource: Scenario, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Scenario: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                scenario_name: str, 
                resource: Scenario, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Scenario: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                scenario_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Scenario: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'scenario_name']}, api_versions_list=['2026-05-01-preview', '2026-08-01-preview'])
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                scenario_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'scenario_name', 'accept']}, api_versions_list=['2026-05-01-preview', '2026-08-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                scenario_name: str, 
                **kwargs: Any
            ) -> Scenario: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'accept']}, api_versions_list=['2026-05-01-preview', '2026-08-01-preview'])
        def list_all(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Scenario]: ...


    class azure.mgmt.chaos.operations.TargetTypesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                target_type_name: str, 
                **kwargs: Any
            ) -> TargetType: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                *, 
                continuation_token_parameter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[TargetType]: ...


    class azure.mgmt.chaos.operations.TargetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                parent_provider_namespace: str, 
                parent_resource_type: str, 
                parent_resource_name: str, 
                target_name: str, 
                resource: Target, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Target: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                parent_provider_namespace: str, 
                parent_resource_type: str, 
                parent_resource_name: str, 
                target_name: str, 
                resource: Target, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Target: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                parent_provider_namespace: str, 
                parent_resource_type: str, 
                parent_resource_name: str, 
                target_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Target: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                parent_provider_namespace: str, 
                parent_resource_type: str, 
                parent_resource_name: str, 
                target_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                parent_provider_namespace: str, 
                parent_resource_type: str, 
                parent_resource_name: str, 
                target_name: str, 
                **kwargs: Any
            ) -> Target: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                parent_provider_namespace: str, 
                parent_resource_type: str, 
                parent_resource_name: str, 
                *, 
                continuation_token_parameter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Target]: ...


    class azure.mgmt.chaos.operations.WorkspacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                resource: Workspace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Workspace]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                resource: Workspace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Workspace]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Workspace]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name']}, api_versions_list=['2026-05-01-preview', '2026-08-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-08-01-preview', params_added_on={'2026-08-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name']}, api_versions_list=['2026-08-01-preview'])
        def begin_discover(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> LROPoller[WorkspaceDiscovery]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-08-01-preview', params_added_on={'2026-08-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name']}, api_versions_list=['2026-08-01-preview'])
        def begin_evaluate(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> LROPoller[WorkspaceEvaluation]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                properties: WorkspaceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Workspace]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                properties: WorkspaceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Workspace]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Workspace]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'accept']}, api_versions_list=['2026-05-01-preview', '2026-08-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> Workspace: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'continuation_token_parameter', 'accept']}, api_versions_list=['2026-05-01-preview', '2026-08-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                *, 
                continuation_token_parameter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Workspace]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'continuation_token_parameter', 'accept']}, api_versions_list=['2026-05-01-preview', '2026-08-01-preview'])
        def list_all(
                self, 
                *, 
                continuation_token_parameter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Workspace]: ...


namespace azure.mgmt.chaos.types

    class azure.mgmt.chaos.types.ActionDependency(TypedDict, total=False):
        key "name": Required[str]
        key "onActionLifecycle": Union[str, ActionLifecycle]
        key "type": Required[Union[str, ActionDependencyType]]
        name: str
        on_action_lifecycle: Union[str, ActionLifecycle]
        type: Union[str, ActionDependencyType]


    class azure.mgmt.chaos.types.Capability(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('CapabilityProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: CapabilityProperties
        system_data: SystemData
        type: str


    class azure.mgmt.chaos.types.CapabilityProperties(TypedDict, total=False):
        key "description": str
        key "parametersSchema": str
        key "provisioningState": Union[str, ProvisioningState]
        key "publisher": str
        key "targetType": str
        key "urn": str
        description: str
        parameters_schema: str
        provisioning_state: Union[str, ProvisioningState]
        publisher: str
        target_type: str
        urn: str


    class azure.mgmt.chaos.types.ChaosExperimentBranch(TypedDict, total=False):
        key "actions": Required[list[ChaosExperimentAction]]
        key "name": Required[str]
        actions: list[ChaosExperimentAction]
        name: str


    class azure.mgmt.chaos.types.ChaosExperimentStep(TypedDict, total=False):
        key "branches": Required[list[ChaosExperimentBranch]]
        key "name": Required[str]
        branches: list[ChaosExperimentBranch]
        name: str


    class azure.mgmt.chaos.types.ChaosTargetFilter(TypedDict, total=False):
        key "parameters": ForwardRef('ChaosTargetSimpleFilterParameters', module='types')
        key "type": Required[Literal[FilterType.SIMPLE]]
        parameters: ChaosTargetSimpleFilterParameters
        type: Literal[FilterType.SIMPLE]


    class azure.mgmt.chaos.types.ChaosTargetListSelector(TypedDict, total=False):
        key "filter": ForwardRef('ChaosTargetFilter', module='types')
        key "id": Required[str]
        key "targets": Required[list[TargetReference]]
        key "type": Required[Literal[SelectorType.LIST]]
        filter: ChaosTargetFilter
        id: str
        targets: list[TargetReference]
        type: Literal[SelectorType.LIST]


    class azure.mgmt.chaos.types.ChaosTargetQuerySelector(TypedDict, total=False):
        key "filter": ForwardRef('ChaosTargetFilter', module='types')
        key "id": Required[str]
        key "queryString": Required[str]
        key "subscriptionIds": Required[list[str]]
        key "type": Required[Literal[SelectorType.QUERY]]
        filter: ChaosTargetFilter
        id: str
        query_string: str
        subscription_ids: list[str]
        type: Literal[SelectorType.QUERY]


    class azure.mgmt.chaos.types.ChaosTargetSimpleFilter(TypedDict, total=False):
        key "parameters": ForwardRef('ChaosTargetSimpleFilterParameters', module='types')
        key "type": Required[Literal[FilterType.SIMPLE]]
        parameters: ChaosTargetSimpleFilterParameters
        type: Literal[FilterType.SIMPLE]


    class azure.mgmt.chaos.types.ChaosTargetSimpleFilterParameters(TypedDict, total=False):
        zones: list[str]


    class azure.mgmt.chaos.types.Connection(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('ConnectionProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ConnectionProperties
        system_data: SystemData
        type: str


    class azure.mgmt.chaos.types.ConnectionProperties(TypedDict, total=False):
        key "certificateIssuer": str
        key "certificateSubjectName": str
        key "dataPlaneEndpoint": str
        key "dstsPrincipal": str
        key "kind": Required[Union[str, ConnectionKind]]
        key "principalId": str
        key "provisioningState": Union[str, ProvisioningState]
        key "status": Union[str, ConnectionStatus]
        key "targetResourceId": Required[str]
        key "tenantId": str
        certificate_issuer: str
        certificate_subject_name: str
        data_plane_endpoint: str
        dsts_principal: str
        kind: Union[str, ConnectionKind]
        principal_id: str
        provisioning_state: Union[str, ProvisioningState]
        status: Union[str, ConnectionStatus]
        target_resource_id: str
        tenant_id: str


    class azure.mgmt.chaos.types.ContinuousAction(TypedDict, total=False):
        key "duration": Required[str]
        key "name": Required[str]
        key "parameters": Required[list[KeyValuePair]]
        key "selectorId": Required[str]
        key "type": Required[Literal[ExperimentActionType.CONTINUOUS]]
        duration: str
        name: str
        parameters: list[KeyValuePair]
        selector_id: str
        type: Literal[ExperimentActionType.CONTINUOUS]


    class azure.mgmt.chaos.types.CustomerDataStorageProperties(TypedDict, total=False):
        key "blobContainerName": str
        key "storageAccountResourceId": str
        blob_container_name: str
        storage_account_resource_id: str


    class azure.mgmt.chaos.types.DelayAction(TypedDict, total=False):
        key "duration": Required[str]
        key "name": Required[str]
        key "type": Required[Literal[ExperimentActionType.DELAY]]
        duration: str
        name: str
        type: Literal[ExperimentActionType.DELAY]


    class azure.mgmt.chaos.types.DiscreteAction(TypedDict, total=False):
        key "name": Required[str]
        key "parameters": Required[list[KeyValuePair]]
        key "selectorId": Required[str]
        key "type": Required[Literal[ExperimentActionType.DISCRETE]]
        name: str
        parameters: list[KeyValuePair]
        selector_id: str
        type: Literal[ExperimentActionType.DISCRETE]


    class azure.mgmt.chaos.types.Experiment(TrackedResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": Required[ExperimentProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: ExperimentProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.chaos.types.ExperimentActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTINUOUS = "continuous"
        DELAY = "delay"
        DISCRETE = "discrete"


    class azure.mgmt.chaos.types.ExperimentProperties(TypedDict, total=False):
        key "customerDataStorage": ForwardRef('CustomerDataStorageProperties', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        key "selectors": Required[list[ChaosTargetSelector]]
        key "steps": Required[list[ChaosExperimentStep]]
        customer_data_storage: CustomerDataStorageProperties
        provisioning_state: Union[str, ProvisioningState]
        selectors: list[ChaosTargetSelector]
        steps: list[ChaosExperimentStep]


    class azure.mgmt.chaos.types.ExperimentUpdate(TypedDict, total=False):
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        identity: ManagedServiceIdentity
        tags: dict[str, str]


    class azure.mgmt.chaos.types.ExternalResource(TypedDict, total=False):
        key "resourceId": str
        resource_id: str


    class azure.mgmt.chaos.types.FilterType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SIMPLE = "Simple"


    class azure.mgmt.chaos.types.FixResourcePermissionsRequest(TypedDict, total=False):
        key "whatIf": bool
        what_if: bool


    class azure.mgmt.chaos.types.KeyValuePair(TypedDict, total=False):
        key "key": Required[str]
        key "value": Required[str]
        key: str
        value: str


    class azure.mgmt.chaos.types.ManagedServiceIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Required[Union[str, ManagedServiceIdentityType]]
        principal_id: str
        tenant_id: str
        type: Union[str, ManagedServiceIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentity]
        user_assigned_identities: dict[str, UserAssignedIdentity]


    class azure.mgmt.chaos.types.PrivateAccess(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": Required[PrivateAccessProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: PrivateAccessProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.chaos.types.PrivateAccessPatch(TypedDict, total=False):
        tags: dict[str, str]


    class azure.mgmt.chaos.types.PrivateAccessProperties(TypedDict, total=False):
        key "provisioningState": Union[str, ProvisioningState]
        key "publicNetworkAccess": Union[str, PublicNetworkAccessOption]
        privateEndpointConnections: list[PrivateEndpointConnection]
        private_endpoint_connections: list[PrivateEndpointConnection]
        provisioning_state: Union[str, ProvisioningState]
        public_network_access: Union[str, PublicNetworkAccessOption]


    class azure.mgmt.chaos.types.PrivateEndpoint(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.chaos.types.PrivateEndpointConnection(ProxyResource):
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


    class azure.mgmt.chaos.types.PrivateEndpointConnectionProperties(TypedDict, total=False):
        key "privateEndpoint": ForwardRef('PrivateEndpoint', module='types')
        key "privateLinkServiceConnectionState": Required[PrivateLinkServiceConnectionState]
        key "provisioningState": Union[str, ProvisioningState]
        groupIds: list[str]
        group_ids: list[str]
        private_endpoint: PrivateEndpoint
        private_link_service_connection_state: PrivateLinkServiceConnectionState
        provisioning_state: Union[str, ProvisioningState]


    class azure.mgmt.chaos.types.PrivateLinkServiceConnectionState(TypedDict, total=False):
        key "actionsRequired": str
        key "description": str
        key "status": Union[str, PrivateEndpointServiceConnectionStatus]
        actions_required: str
        description: str
        status: Union[str, PrivateEndpointServiceConnectionStatus]


    class azure.mgmt.chaos.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.chaos.types.Recommendation(TypedDict, total=False):
        key "evaluationRunAt": str
        key "recommendationStatus": Required[Union[str, RecommendationStatus]]
        evaluation_run_at: str
        recommendation_status: Union[str, RecommendationStatus]


    class azure.mgmt.chaos.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.chaos.types.ResourceTargeting(TypedDict, total=False):
        key "exclude": ForwardRef('ResourceTargetingCriteria', module='types')
        key "include": ForwardRef('ResourceTargetingCriteria', module='types')
        exclude: ResourceTargetingCriteria
        include: ResourceTargetingCriteria


    class azure.mgmt.chaos.types.ResourceTargetingCriteria(TypedDict, total=False):
        locations: list[str]
        physicalZones: list[str]
        physical_zones: list[str]
        resources: list[str]
        tags: list[KeyValuePair]
        types: list[str]
        zones: list[str]


    class azure.mgmt.chaos.types.RunAfter(TypedDict, total=False):
        key "behavior": Union[str, RunAfterBehavior]
        key "items": Required[list[ActionDependency]]
        behavior: Union[str, RunAfterBehavior]
        items_property: list[ActionDependency]


    class azure.mgmt.chaos.types.Scenario(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('ScenarioProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ScenarioProperties
        system_data: SystemData
        type: str


    class azure.mgmt.chaos.types.ScenarioAction(TypedDict, total=False):
        key "actionId": Required[str]
        key "description": str
        key "duration": Required[str]
        key "externalResource": ForwardRef('ExternalResource', module='types')
        key "name": Required[str]
        key "runAfter": ForwardRef('RunAfter', module='types')
        key "timeout": str
        key "waitBefore": str
        action_id: str
        description: str
        duration: str
        external_resource: ExternalResource
        name: str
        parameters: list[KeyValuePair]
        run_after: RunAfter
        timeout: str
        wait_before: str


    class azure.mgmt.chaos.types.ScenarioConfiguration(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('ScenarioConfigurationProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ScenarioConfigurationProperties
        system_data: SystemData
        type: str


    class azure.mgmt.chaos.types.ScenarioConfigurationProperties(TypedDict, total=False):
        key "provisioningState": Union[str, ProvisioningState]
        key "resourceTargeting": ForwardRef('ResourceTargeting', module='types')
        key "scenarioId": Required[str]
        parameters: list[KeyValuePair]
        provisioning_state: Union[str, ProvisioningState]
        resource_targeting: ResourceTargeting
        scenario_id: str


    class azure.mgmt.chaos.types.ScenarioParameter(TypedDict, total=False):
        key "default": str
        key "description": str
        key "name": Required[str]
        key "required": bool
        key "type": Required[Union[str, ParameterType]]
        default: str
        description: str
        name: str
        required: bool
        type: Union[str, ParameterType]


    class azure.mgmt.chaos.types.ScenarioProperties(TypedDict, total=False):
        key "actions": Required[list[ScenarioAction]]
        key "createdFrom": str
        key "description": str
        key "parameters": Required[list[ScenarioParameter]]
        key "provisioningState": Union[str, ProvisioningState]
        key "recommendation": ForwardRef('Recommendation', module='types')
        key "version": str
        actions: list[ScenarioAction]
        created_from: str
        description: str
        parameters: list[ScenarioParameter]
        provisioning_state: Union[str, ProvisioningState]
        recommendation: Recommendation
        version: str


    class azure.mgmt.chaos.types.SelectorType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LIST = "List"
        QUERY = "Query"


    class azure.mgmt.chaos.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.chaos.types.Target(ProxyResource):
        key "id": str
        key "location": str
        key "name": str
        key "properties": Required[dict[str, Any]]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: dict[str, Any]
        system_data: SystemData
        type: str


    class azure.mgmt.chaos.types.TargetReference(TypedDict, total=False):
        key "id": Required[str]
        key "type": Required[Union[str, TargetReferenceType]]
        id: str
        type: Union[str, TargetReferenceType]


    class azure.mgmt.chaos.types.TrackedResource(Resource):
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


    class azure.mgmt.chaos.types.UserAssignedIdentity(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        client_id: str
        principal_id: str


    class azure.mgmt.chaos.types.Workspace(TrackedResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": Required[WorkspaceProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: WorkspaceProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.chaos.types.WorkspaceProperties(TypedDict, total=False):
        key "communicationEndpoint": str
        key "provisioningState": Union[str, ProvisioningState]
        key "scopes": Required[list[str]]
        communication_endpoint: str
        provisioning_state: Union[str, ProvisioningState]
        scopes: list[str]


    class azure.mgmt.chaos.types.WorkspaceUpdate(TypedDict, total=False):
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        identity: ManagedServiceIdentity
        tags: dict[str, str]


```