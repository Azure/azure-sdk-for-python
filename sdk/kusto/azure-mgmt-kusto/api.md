```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.kusto

    class azure.mgmt.kusto.KustoManagementClient: implements ContextManager 
        attached_database_configurations: AttachedDatabaseConfigurationsOperations
        cluster_principal_assignments: ClusterPrincipalAssignmentsOperations
        clusters: ClustersOperations
        data_connections: DataConnectionsOperations
        database: DatabaseOperations
        database_principal_assignments: DatabasePrincipalAssignmentsOperations
        databases: DatabasesOperations
        managed_private_endpoints: ManagedPrivateEndpointsOperations
        operations: Operations
        operations_results: OperationsResultsOperations
        operations_results_location: OperationsResultsLocationOperations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        sandbox_custom_images: SandboxCustomImagesOperations
        scripts: ScriptsOperations
        skus: SkusOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
                base_url: str = "https://management.azure.com", 
                *, 
                api_version: str = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...


namespace azure.mgmt.kusto.aio

    class azure.mgmt.kusto.aio.KustoManagementClient: implements AsyncContextManager 
        attached_database_configurations: AttachedDatabaseConfigurationsOperations
        cluster_principal_assignments: ClusterPrincipalAssignmentsOperations
        clusters: ClustersOperations
        data_connections: DataConnectionsOperations
        database: DatabaseOperations
        database_principal_assignments: DatabasePrincipalAssignmentsOperations
        databases: DatabasesOperations
        managed_private_endpoints: ManagedPrivateEndpointsOperations
        operations: Operations
        operations_results: OperationsResultsOperations
        operations_results_location: OperationsResultsLocationOperations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        sandbox_custom_images: SandboxCustomImagesOperations
        scripts: ScriptsOperations
        skus: SkusOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                subscription_id: str, 
                base_url: str = "https://management.azure.com", 
                *, 
                api_version: str = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...


namespace azure.mgmt.kusto.aio.operations

    class azure.mgmt.kusto.aio.operations.AttachedDatabaseConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                attached_database_configuration_name: str, 
                parameters: AttachedDatabaseConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AttachedDatabaseConfiguration]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                attached_database_configuration_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AttachedDatabaseConfiguration]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                attached_database_configuration_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def check_name_availability(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                resource_name: AttachedDatabaseConfigurationsCheckNameRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameResult: ...

        @overload
        async def check_name_availability(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                resource_name: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameResult: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                attached_database_configuration_name: str, 
                **kwargs: Any
            ) -> AttachedDatabaseConfiguration: ...

        @distributed_trace
        def list_by_cluster(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[AttachedDatabaseConfiguration]: ...


    class azure.mgmt.kusto.aio.operations.ClusterPrincipalAssignmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                principal_assignment_name: str, 
                parameters: ClusterPrincipalAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ClusterPrincipalAssignment]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                principal_assignment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ClusterPrincipalAssignment]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                principal_assignment_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def check_name_availability(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                principal_assignment_name: ClusterPrincipalAssignmentCheckNameRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameResult: ...

        @overload
        async def check_name_availability(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                principal_assignment_name: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameResult: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                principal_assignment_name: str, 
                **kwargs: Any
            ) -> ClusterPrincipalAssignment: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[ClusterPrincipalAssignment]: ...


    class azure.mgmt.kusto.aio.operations.ClustersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_add_callout_policies(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                callout_policies: CalloutPoliciesList, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_add_callout_policies(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                callout_policies: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_add_language_extensions(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                language_extensions_to_add: LanguageExtensionsList, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_add_language_extensions(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                language_extensions_to_add: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: Cluster, 
                if_match: Optional[str] = None, 
                if_none_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: IO[bytes], 
                if_match: Optional[str] = None, 
                if_none_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_detach_follower_databases(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                follower_database_to_remove: FollowerDatabaseDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_detach_follower_databases(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                follower_database_to_remove: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_diagnose_virtual_network(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[DiagnoseVirtualNetworkResult]: ...

        @overload
        async def begin_migrate(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                cluster_migrate_request: ClusterMigrateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_migrate(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                cluster_migrate_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_remove_callout_policy(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                callout_policy: CalloutPolicyToRemove, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_remove_callout_policy(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                callout_policy: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_remove_language_extensions(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                language_extensions_to_remove: LanguageExtensionsList, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_remove_language_extensions(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                language_extensions_to_remove: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_start(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_stop(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: ClusterUpdate, 
                if_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: IO[bytes], 
                if_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @overload
        async def check_name_availability(
                self, 
                location: str, 
                cluster_name: ClusterCheckNameRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameResult: ...

        @overload
        async def check_name_availability(
                self, 
                location: str, 
                cluster_name: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameResult: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> Cluster: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncIterable[Cluster]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[Cluster]: ...

        @distributed_trace
        def list_callout_policies(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[CalloutPolicy]: ...

        @distributed_trace
        def list_follower_databases(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[FollowerDatabaseDefinition]: ...

        @distributed_trace
        def list_follower_databases_get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[FollowerDatabaseDefinitionGet]: ...

        @distributed_trace
        def list_language_extensions(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[LanguageExtension]: ...

        @distributed_trace
        def list_outbound_network_dependencies_endpoints(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[OutboundNetworkDependenciesEndpoint]: ...

        @distributed_trace
        def list_skus(self, **kwargs: Any) -> AsyncIterable[SkuDescription]: ...

        @distributed_trace
        def list_skus_by_resource(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[AzureResourceSku]: ...


    class azure.mgmt.kusto.aio.operations.DataConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                data_connection_name: str, 
                parameters: DataConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DataConnection]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                data_connection_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DataConnection]: ...

        @overload
        async def begin_data_connection_validation(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                parameters: DataConnectionValidation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DataConnectionValidationListResult]: ...

        @overload
        async def begin_data_connection_validation(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DataConnectionValidationListResult]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                data_connection_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                data_connection_name: str, 
                parameters: DataConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DataConnection]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                data_connection_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DataConnection]: ...

        @overload
        async def check_name_availability(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                data_connection_name: DataConnectionCheckNameRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameResult: ...

        @overload
        async def check_name_availability(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                data_connection_name: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameResult: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                data_connection_name: str, 
                **kwargs: Any
            ) -> DataConnection: ...

        @distributed_trace
        def list_by_database(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[DataConnection]: ...


    class azure.mgmt.kusto.aio.operations.DatabaseOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def invite_follower(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                parameters: DatabaseInviteFollowerRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DatabaseInviteFollowerResult: ...

        @overload
        async def invite_follower(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DatabaseInviteFollowerResult: ...


    class azure.mgmt.kusto.aio.operations.DatabasePrincipalAssignmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                principal_assignment_name: str, 
                parameters: DatabasePrincipalAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DatabasePrincipalAssignment]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                principal_assignment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DatabasePrincipalAssignment]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                principal_assignment_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def check_name_availability(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                principal_assignment_name: DatabasePrincipalAssignmentCheckNameRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameResult: ...

        @overload
        async def check_name_availability(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                principal_assignment_name: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameResult: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                principal_assignment_name: str, 
                **kwargs: Any
            ) -> DatabasePrincipalAssignment: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[DatabasePrincipalAssignment]: ...


    class azure.mgmt.kusto.aio.operations.DatabasesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def add_principals(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                database_principals_to_add: DatabasePrincipalListRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DatabasePrincipalListResult: ...

        @overload
        async def add_principals(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                database_principals_to_add: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DatabasePrincipalListResult: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                parameters: Database, 
                caller_role: Union[str, CallerRole] = "Admin", 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Database]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                parameters: IO[bytes], 
                caller_role: Union[str, CallerRole] = "Admin", 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Database]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                parameters: Database, 
                caller_role: Union[str, CallerRole] = "Admin", 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Database]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                parameters: IO[bytes], 
                caller_role: Union[str, CallerRole] = "Admin", 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Database]: ...

        @overload
        async def check_name_availability(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                resource_name: CheckNameRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameResult: ...

        @overload
        async def check_name_availability(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                resource_name: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameResult: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> Database: ...

        @distributed_trace
        def list_by_cluster(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                top: Optional[int] = None, 
                skiptoken: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[Database]: ...

        @distributed_trace
        def list_principals(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[DatabasePrincipal]: ...

        @overload
        async def remove_principals(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                database_principals_to_remove: DatabasePrincipalListRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DatabasePrincipalListResult: ...

        @overload
        async def remove_principals(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                database_principals_to_remove: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DatabasePrincipalListResult: ...


    class azure.mgmt.kusto.aio.operations.ManagedPrivateEndpointsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                managed_private_endpoint_name: str, 
                parameters: ManagedPrivateEndpoint, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedPrivateEndpoint]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                managed_private_endpoint_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedPrivateEndpoint]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                managed_private_endpoint_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                managed_private_endpoint_name: str, 
                parameters: ManagedPrivateEndpoint, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedPrivateEndpoint]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                managed_private_endpoint_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedPrivateEndpoint]: ...

        @overload
        async def check_name_availability(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                resource_name: ManagedPrivateEndpointsCheckNameRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameResult: ...

        @overload
        async def check_name_availability(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                resource_name: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameResult: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                managed_private_endpoint_name: str, 
                **kwargs: Any
            ) -> ManagedPrivateEndpoint: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[ManagedPrivateEndpoint]: ...


    class azure.mgmt.kusto.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncIterable[Operation]: ...


    class azure.mgmt.kusto.aio.operations.OperationsResultsLocationOperations:

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
            ) -> None: ...


    class azure.mgmt.kusto.aio.operations.OperationsResultsOperations:

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
            ) -> OperationResult: ...


    class azure.mgmt.kusto.aio.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
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
                cluster_name: str, 
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
                cluster_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[PrivateEndpointConnection]: ...


    class azure.mgmt.kusto.aio.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                private_link_resource_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[PrivateLinkResource]: ...


    class azure.mgmt.kusto.aio.operations.SandboxCustomImagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                sandbox_custom_image_name: str, 
                parameters: SandboxCustomImage, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SandboxCustomImage]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                sandbox_custom_image_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SandboxCustomImage]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                sandbox_custom_image_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                sandbox_custom_image_name: str, 
                parameters: SandboxCustomImage, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SandboxCustomImage]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                sandbox_custom_image_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SandboxCustomImage]: ...

        @overload
        async def check_name_availability(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                resource_name: SandboxCustomImagesCheckNameRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameResult: ...

        @overload
        async def check_name_availability(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                resource_name: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameResult: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                sandbox_custom_image_name: str, 
                **kwargs: Any
            ) -> SandboxCustomImage: ...

        @distributed_trace
        def list_by_cluster(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[SandboxCustomImage]: ...


    class azure.mgmt.kusto.aio.operations.ScriptsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                script_name: str, 
                parameters: Script, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Script]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                script_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Script]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                script_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                script_name: str, 
                parameters: Script, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Script]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                script_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Script]: ...

        @overload
        async def check_name_availability(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                script_name: ScriptCheckNameRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameResult: ...

        @overload
        async def check_name_availability(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                script_name: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameResult: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                script_name: str, 
                **kwargs: Any
            ) -> Script: ...

        @distributed_trace
        def list_by_database(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[Script]: ...


    class azure.mgmt.kusto.aio.operations.SkusOperations:

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
            ) -> AsyncIterable[SkuDescription]: ...


namespace azure.mgmt.kusto.models

    class azure.mgmt.kusto.models.AcceptedAudiences(Model):
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.AttachedDatabaseConfiguration(ProxyResource):
        attached_database_names: list[str]
        cluster_resource_id: str
        database_name: str
        database_name_override: str
        database_name_prefix: str
        default_principals_modification_kind: Union[str, DefaultPrincipalsModificationKind]
        id: str
        location: str
        name: str
        provisioning_state: Union[str, ProvisioningState]
        table_level_sharing_properties: TableLevelSharingProperties
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cluster_resource_id: Optional[str] = ..., 
                database_name: Optional[str] = ..., 
                database_name_override: Optional[str] = ..., 
                database_name_prefix: Optional[str] = ..., 
                default_principals_modification_kind: Optional[Union[str, DefaultPrincipalsModificationKind]] = ..., 
                location: Optional[str] = ..., 
                table_level_sharing_properties: Optional[TableLevelSharingProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.AttachedDatabaseConfigurationListResult(Model):
        value: list[AttachedDatabaseConfiguration]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[AttachedDatabaseConfiguration]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.AttachedDatabaseConfigurationsCheckNameRequest(Model):
        name: str
        type: str = "Microsoft.Kusto/clusters/attachedDatabaseConfigurations"

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.AzureCapacity(Model):
        default: int
        maximum: int
        minimum: int
        scale_type: Union[str, AzureScaleType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                default: int, 
                maximum: int, 
                minimum: int, 
                scale_type: Union[str, AzureScaleType], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.AzureResourceSku(Model):
        capacity: AzureCapacity
        resource_type: str
        sku: AzureSku

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                capacity: Optional[AzureCapacity] = ..., 
                resource_type: Optional[str] = ..., 
                sku: Optional[AzureSku] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.AzureScaleType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC = "automatic"
        MANUAL = "manual"
        NONE = "none"


    class azure.mgmt.kusto.models.AzureSku(Model):
        capacity: int
        name: Union[str, AzureSkuName]
        tier: Union[str, AzureSkuTier]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                name: Union[str, AzureSkuName], 
                tier: Union[str, AzureSkuTier], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.AzureSkuName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEV_NO_SLA_STANDARD_D11_V2 = "Dev(No SLA)_Standard_D11_v2"
        DEV_NO_SLA_STANDARD_E2_A_V4 = "Dev(No SLA)_Standard_E2a_v4"
        STANDARD_D11_V2 = "Standard_D11_v2"
        STANDARD_D12_V2 = "Standard_D12_v2"
        STANDARD_D13_V2 = "Standard_D13_v2"
        STANDARD_D14_V2 = "Standard_D14_v2"
        STANDARD_D16_D_V5 = "Standard_D16d_v5"
        STANDARD_D32_D_V4 = "Standard_D32d_v4"
        STANDARD_D32_D_V5 = "Standard_D32d_v5"
        STANDARD_DS13_V2_1_TB_PS = "Standard_DS13_v2+1TB_PS"
        STANDARD_DS13_V2_2_TB_PS = "Standard_DS13_v2+2TB_PS"
        STANDARD_DS14_V2_3_TB_PS = "Standard_DS14_v2+3TB_PS"
        STANDARD_DS14_V2_4_TB_PS = "Standard_DS14_v2+4TB_PS"
        STANDARD_E16_ADS_V5 = "Standard_E16ads_v5"
        STANDARD_E16_AS_V4_3_TB_PS = "Standard_E16as_v4+3TB_PS"
        STANDARD_E16_AS_V4_4_TB_PS = "Standard_E16as_v4+4TB_PS"
        STANDARD_E16_AS_V5_3_TB_PS = "Standard_E16as_v5+3TB_PS"
        STANDARD_E16_AS_V5_4_TB_PS = "Standard_E16as_v5+4TB_PS"
        STANDARD_E16_A_V4 = "Standard_E16a_v4"
        STANDARD_E16_D_V4 = "Standard_E16d_v4"
        STANDARD_E16_D_V5 = "Standard_E16d_v5"
        STANDARD_E16_S_V4_3_TB_PS = "Standard_E16s_v4+3TB_PS"
        STANDARD_E16_S_V4_4_TB_PS = "Standard_E16s_v4+4TB_PS"
        STANDARD_E16_S_V5_3_TB_PS = "Standard_E16s_v5+3TB_PS"
        STANDARD_E16_S_V5_4_TB_PS = "Standard_E16s_v5+4TB_PS"
        STANDARD_E2_ADS_V5 = "Standard_E2ads_v5"
        STANDARD_E2_A_V4 = "Standard_E2a_v4"
        STANDARD_E2_D_V4 = "Standard_E2d_v4"
        STANDARD_E2_D_V5 = "Standard_E2d_v5"
        STANDARD_E4_ADS_V5 = "Standard_E4ads_v5"
        STANDARD_E4_A_V4 = "Standard_E4a_v4"
        STANDARD_E4_D_V4 = "Standard_E4d_v4"
        STANDARD_E4_D_V5 = "Standard_E4d_v5"
        STANDARD_E64_I_V3 = "Standard_E64i_v3"
        STANDARD_E80_IDS_V4 = "Standard_E80ids_v4"
        STANDARD_E8_ADS_V5 = "Standard_E8ads_v5"
        STANDARD_E8_AS_V4_1_TB_PS = "Standard_E8as_v4+1TB_PS"
        STANDARD_E8_AS_V4_2_TB_PS = "Standard_E8as_v4+2TB_PS"
        STANDARD_E8_AS_V5_1_TB_PS = "Standard_E8as_v5+1TB_PS"
        STANDARD_E8_AS_V5_2_TB_PS = "Standard_E8as_v5+2TB_PS"
        STANDARD_E8_A_V4 = "Standard_E8a_v4"
        STANDARD_E8_D_V4 = "Standard_E8d_v4"
        STANDARD_E8_D_V5 = "Standard_E8d_v5"
        STANDARD_E8_S_V4_1_TB_PS = "Standard_E8s_v4+1TB_PS"
        STANDARD_E8_S_V4_2_TB_PS = "Standard_E8s_v4+2TB_PS"
        STANDARD_E8_S_V5_1_TB_PS = "Standard_E8s_v5+1TB_PS"
        STANDARD_E8_S_V5_2_TB_PS = "Standard_E8s_v5+2TB_PS"
        STANDARD_EC16_ADS_V5 = "Standard_EC16ads_v5"
        STANDARD_EC16_AS_V5_3_TB_PS = "Standard_EC16as_v5+3TB_PS"
        STANDARD_EC16_AS_V5_4_TB_PS = "Standard_EC16as_v5+4TB_PS"
        STANDARD_EC8_ADS_V5 = "Standard_EC8ads_v5"
        STANDARD_EC8_AS_V5_1_TB_PS = "Standard_EC8as_v5+1TB_PS"
        STANDARD_EC8_AS_V5_2_TB_PS = "Standard_EC8as_v5+2TB_PS"
        STANDARD_L16_AS_V3 = "Standard_L16as_v3"
        STANDARD_L16_S = "Standard_L16s"
        STANDARD_L16_S_V2 = "Standard_L16s_v2"
        STANDARD_L16_S_V3 = "Standard_L16s_v3"
        STANDARD_L32_AS_V3 = "Standard_L32as_v3"
        STANDARD_L32_S_V3 = "Standard_L32s_v3"
        STANDARD_L4_S = "Standard_L4s"
        STANDARD_L8_AS_V3 = "Standard_L8as_v3"
        STANDARD_L8_S = "Standard_L8s"
        STANDARD_L8_S_V2 = "Standard_L8s_v2"
        STANDARD_L8_S_V3 = "Standard_L8s_v3"


    class azure.mgmt.kusto.models.AzureSkuTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC = "Basic"
        STANDARD = "Standard"


    class azure.mgmt.kusto.models.BlobStorageEventType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MICROSOFT_STORAGE_BLOB_CREATED = "Microsoft.Storage.BlobCreated"
        MICROSOFT_STORAGE_BLOB_RENAMED = "Microsoft.Storage.BlobRenamed"


    class azure.mgmt.kusto.models.CallerRole(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADMIN = "Admin"
        NONE = "None"


    class azure.mgmt.kusto.models.CalloutPoliciesList(Model):
        next_link: str
        value: list[CalloutPolicy]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[CalloutPolicy]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.CalloutPolicy(Model):
        callout_id: str
        callout_type: Union[str, CalloutType]
        callout_uri_regex: str
        outbound_access: Union[str, OutboundAccess]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                callout_type: Optional[Union[str, CalloutType]] = ..., 
                callout_uri_regex: Optional[str] = ..., 
                outbound_access: Optional[Union[str, OutboundAccess]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.CalloutPolicyToRemove(Model):
        callout_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                callout_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.CalloutType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_DIGITAL_TWINS = "azure_digital_twins"
        AZURE_OPENAI = "azure_openai"
        COSMOSDB = "cosmosdb"
        EXTERNAL_DATA = "external_data"
        GENEVAMETRICS = "genevametrics"
        KUSTO = "kusto"
        MYSQL = "mysql"
        POSTGRESQL = "postgresql"
        SANDBOX_ARTIFACTS = "sandbox_artifacts"
        SQL = "sql"
        WEBAPI = "webapi"


    class azure.mgmt.kusto.models.CheckNameRequest(Model):
        name: str
        type: Union[str, Type]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: str, 
                type: Union[str, Type], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.CheckNameResult(Model):
        message: str
        name: str
        name_available: bool
        reason: Union[str, Reason]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                message: Optional[str] = ..., 
                name: Optional[str] = ..., 
                name_available: Optional[bool] = ..., 
                reason: Optional[Union[str, Reason]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.Cluster(TrackedResource):
        accepted_audiences: list[AcceptedAudiences]
        allowed_fqdn_list: list[str]
        allowed_ip_range_list: list[str]
        callout_policies: list[CalloutPolicy]
        data_ingestion_uri: str
        enable_auto_stop: bool
        enable_disk_encryption: bool
        enable_double_encryption: bool
        enable_purge: bool
        enable_streaming_ingest: bool
        engine_type: Union[str, EngineType]
        etag: str
        id: str
        identity: Identity
        key_vault_properties: KeyVaultProperties
        language_extensions: LanguageExtensionsList
        location: str
        migration_cluster: MigrationClusterProperties
        name: str
        optimized_autoscale: OptimizedAutoscale
        private_endpoint_connections: list[PrivateEndpointConnection]
        provisioning_state: Union[str, ProvisioningState]
        public_ip_type: Union[str, PublicIPType]
        public_network_access: Union[str, PublicNetworkAccess]
        restrict_outbound_network_access: Union[str, ClusterNetworkAccessFlag]
        sku: AzureSku
        state: Union[str, State]
        state_reason: str
        system_data: SystemData
        tags: dict[str, str]
        trusted_external_tenants: list[TrustedExternalTenant]
        type: str
        uri: str
        virtual_cluster_graduation_properties: str
        virtual_network_configuration: VirtualNetworkConfiguration
        zone_status: Union[str, ZoneStatus]
        zones: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                accepted_audiences: Optional[List[AcceptedAudiences]] = ..., 
                allowed_fqdn_list: Optional[List[str]] = ..., 
                allowed_ip_range_list: Optional[List[str]] = ..., 
                callout_policies: Optional[List[CalloutPolicy]] = ..., 
                enable_auto_stop: bool = True, 
                enable_disk_encryption: bool = False, 
                enable_double_encryption: bool = False, 
                enable_purge: bool = False, 
                enable_streaming_ingest: bool = False, 
                engine_type: Union[str, EngineType] = "V3", 
                identity: Optional[Identity] = ..., 
                key_vault_properties: Optional[KeyVaultProperties] = ..., 
                language_extensions: Optional[LanguageExtensionsList] = ..., 
                location: str, 
                optimized_autoscale: Optional[OptimizedAutoscale] = ..., 
                public_ip_type: Union[str, PublicIPType] = "IPv4", 
                public_network_access: Union[str, PublicNetworkAccess] = "Enabled", 
                restrict_outbound_network_access: Union[str, ClusterNetworkAccessFlag] = "Disabled", 
                sku: AzureSku, 
                tags: Optional[Dict[str, str]] = ..., 
                trusted_external_tenants: Optional[List[TrustedExternalTenant]] = ..., 
                virtual_cluster_graduation_properties: Optional[str] = ..., 
                virtual_network_configuration: Optional[VirtualNetworkConfiguration] = ..., 
                zones: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.ClusterCheckNameRequest(Model):
        name: str
        type: str = "Microsoft.Kusto/clusters"

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.ClusterListResult(Model):
        value: list[Cluster]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[Cluster]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.ClusterMigrateRequest(Model):
        cluster_resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cluster_resource_id: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.ClusterNetworkAccessFlag(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.kusto.models.ClusterPrincipalAssignment(ProxyResource):
        aad_object_id: str
        id: str
        name: str
        principal_id: str
        principal_name: str
        principal_type: Union[str, PrincipalType]
        provisioning_state: Union[str, ProvisioningState]
        role: Union[str, ClusterPrincipalRole]
        tenant_id: str
        tenant_name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                principal_id: Optional[str] = ..., 
                principal_type: Optional[Union[str, PrincipalType]] = ..., 
                role: Optional[Union[str, ClusterPrincipalRole]] = ..., 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.ClusterPrincipalAssignmentCheckNameRequest(Model):
        name: str
        type: str = "Microsoft.Kusto/clusters/principalAssignments"

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.ClusterPrincipalAssignmentListResult(Model):
        value: list[ClusterPrincipalAssignment]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[ClusterPrincipalAssignment]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.ClusterPrincipalRole(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL_DATABASES_ADMIN = "AllDatabasesAdmin"
        ALL_DATABASES_MONITOR = "AllDatabasesMonitor"
        ALL_DATABASES_VIEWER = "AllDatabasesViewer"


    class azure.mgmt.kusto.models.ClusterUpdate(Resource):
        accepted_audiences: list[AcceptedAudiences]
        allowed_fqdn_list: list[str]
        allowed_ip_range_list: list[str]
        callout_policies: list[CalloutPolicy]
        data_ingestion_uri: str
        enable_auto_stop: bool
        enable_disk_encryption: bool
        enable_double_encryption: bool
        enable_purge: bool
        enable_streaming_ingest: bool
        engine_type: Union[str, EngineType]
        id: str
        identity: Identity
        key_vault_properties: KeyVaultProperties
        language_extensions: LanguageExtensionsList
        location: str
        migration_cluster: MigrationClusterProperties
        name: str
        optimized_autoscale: OptimizedAutoscale
        private_endpoint_connections: list[PrivateEndpointConnection]
        provisioning_state: Union[str, ProvisioningState]
        public_ip_type: Union[str, PublicIPType]
        public_network_access: Union[str, PublicNetworkAccess]
        restrict_outbound_network_access: Union[str, ClusterNetworkAccessFlag]
        sku: AzureSku
        state: Union[str, State]
        state_reason: str
        tags: dict[str, str]
        trusted_external_tenants: list[TrustedExternalTenant]
        type: str
        uri: str
        virtual_cluster_graduation_properties: str
        virtual_network_configuration: VirtualNetworkConfiguration
        zone_status: Union[str, ZoneStatus]
        zones: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                accepted_audiences: Optional[List[AcceptedAudiences]] = ..., 
                allowed_fqdn_list: Optional[List[str]] = ..., 
                allowed_ip_range_list: Optional[List[str]] = ..., 
                callout_policies: Optional[List[CalloutPolicy]] = ..., 
                enable_auto_stop: bool = True, 
                enable_disk_encryption: bool = False, 
                enable_double_encryption: bool = False, 
                enable_purge: bool = False, 
                enable_streaming_ingest: bool = False, 
                engine_type: Union[str, EngineType] = "V3", 
                identity: Optional[Identity] = ..., 
                key_vault_properties: Optional[KeyVaultProperties] = ..., 
                language_extensions: Optional[LanguageExtensionsList] = ..., 
                location: Optional[str] = ..., 
                optimized_autoscale: Optional[OptimizedAutoscale] = ..., 
                public_ip_type: Union[str, PublicIPType] = "IPv4", 
                public_network_access: Union[str, PublicNetworkAccess] = "Enabled", 
                restrict_outbound_network_access: Union[str, ClusterNetworkAccessFlag] = "Disabled", 
                sku: Optional[AzureSku] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                trusted_external_tenants: Optional[List[TrustedExternalTenant]] = ..., 
                virtual_cluster_graduation_properties: Optional[str] = ..., 
                virtual_network_configuration: Optional[VirtualNetworkConfiguration] = ..., 
                zones: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.ComponentsSgqdofSchemasIdentityPropertiesUserassignedidentitiesAdditionalproperties(Model):
        client_id: str
        principal_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.Compression(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        G_ZIP = "GZip"
        NONE = "None"


    class azure.mgmt.kusto.models.CosmosDbDataConnection(DataConnection):
        cosmos_db_account_resource_id: str
        cosmos_db_container: str
        cosmos_db_database: str
        id: str
        kind: Union[str, DataConnectionKind]
        location: str
        managed_identity_object_id: str
        managed_identity_resource_id: str
        mapping_rule_name: str
        name: str
        provisioning_state: Union[str, ProvisioningState]
        retrieval_start_date: datetime
        table_name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cosmos_db_account_resource_id: Optional[str] = ..., 
                cosmos_db_container: Optional[str] = ..., 
                cosmos_db_database: Optional[str] = ..., 
                location: Optional[str] = ..., 
                managed_identity_resource_id: Optional[str] = ..., 
                mapping_rule_name: Optional[str] = ..., 
                retrieval_start_date: Optional[datetime] = ..., 
                table_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.kusto.models.DataConnection(ProxyResource):
        id: str
        kind: Union[str, DataConnectionKind]
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
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.DataConnectionCheckNameRequest(Model):
        name: str
        type: str = "Microsoft.Kusto/clusters/databases/dataConnections"

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.DataConnectionKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COSMOS_DB = "CosmosDb"
        EVENT_GRID = "EventGrid"
        EVENT_HUB = "EventHub"
        IOT_HUB = "IotHub"


    class azure.mgmt.kusto.models.DataConnectionListResult(Model):
        value: list[DataConnection]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[DataConnection]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.DataConnectionValidation(Model):
        data_connection_name: str
        properties: DataConnection

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                data_connection_name: Optional[str] = ..., 
                properties: Optional[DataConnection] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.DataConnectionValidationListResult(Model):
        value: list[DataConnectionValidationResult]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[DataConnectionValidationResult]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.DataConnectionValidationResult(Model):
        error_message: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error_message: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.Database(ProxyResource):
        id: str
        kind: Union[str, Kind]
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
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.DatabaseInviteFollowerRequest(Model):
        invitee_email: str
        table_level_sharing_properties: TableLevelSharingProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                invitee_email: str, 
                table_level_sharing_properties: Optional[TableLevelSharingProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.DatabaseInviteFollowerResult(Model):
        generated_invitation: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                generated_invitation: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.DatabaseListResult(Model):
        next_link: str
        value: list[Database]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[Database]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.DatabasePrincipal(Model):
        app_id: str
        email: str
        fqn: str
        name: str
        role: Union[str, DatabasePrincipalRole]
        tenant_name: str
        type: Union[str, DatabasePrincipalType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                app_id: Optional[str] = ..., 
                email: Optional[str] = ..., 
                fqn: Optional[str] = ..., 
                name: str, 
                role: Union[str, DatabasePrincipalRole], 
                type: Union[str, DatabasePrincipalType], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.DatabasePrincipalAssignment(ProxyResource):
        aad_object_id: str
        id: str
        name: str
        principal_id: str
        principal_name: str
        principal_type: Union[str, PrincipalType]
        provisioning_state: Union[str, ProvisioningState]
        role: Union[str, DatabasePrincipalRole]
        tenant_id: str
        tenant_name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                principal_id: Optional[str] = ..., 
                principal_type: Optional[Union[str, PrincipalType]] = ..., 
                role: Optional[Union[str, DatabasePrincipalRole]] = ..., 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.DatabasePrincipalAssignmentCheckNameRequest(Model):
        name: str
        type: str = "Microsoft.Kusto/clusters/databases/principalAssignments"

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.DatabasePrincipalAssignmentListResult(Model):
        value: list[DatabasePrincipalAssignment]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[DatabasePrincipalAssignment]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.DatabasePrincipalListRequest(Model):
        value: list[DatabasePrincipal]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[DatabasePrincipal]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.DatabasePrincipalListResult(Model):
        value: list[DatabasePrincipal]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[DatabasePrincipal]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.DatabasePrincipalRole(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADMIN = "Admin"
        INGESTOR = "Ingestor"
        MONITOR = "Monitor"
        UNRESTRICTED_VIEWER = "UnrestrictedViewer"
        USER = "User"
        VIEWER = "Viewer"


    class azure.mgmt.kusto.models.DatabasePrincipalType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APP = "App"
        GROUP = "Group"
        USER = "User"


    class azure.mgmt.kusto.models.DatabaseRouting(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MULTI = "Multi"
        SINGLE = "Single"


    class azure.mgmt.kusto.models.DatabaseShareOrigin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DATA_SHARE = "DataShare"
        DIRECT = "Direct"
        OTHER = "Other"


    class azure.mgmt.kusto.models.DatabaseStatistics(Model):
        size: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                size: Optional[float] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.DefaultPrincipalsModificationKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        REPLACE = "Replace"
        UNION = "Union"


    class azure.mgmt.kusto.models.DiagnoseVirtualNetworkResult(Model):
        findings: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                findings: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.EndpointDependency(Model):
        domain_name: str
        endpoint_details: list[EndpointDetail]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                domain_name: Optional[str] = ..., 
                endpoint_details: Optional[List[EndpointDetail]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.EndpointDetail(Model):
        ip_address: str
        port: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                ip_address: Optional[str] = ..., 
                port: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.EngineType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        V2 = "V2"
        V3 = "V3"


    class azure.mgmt.kusto.models.ErrorAdditionalInfo(Model):
        info: JSON
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.ErrorDetail(Model):
        additional_info: list[ErrorAdditionalInfo]
        code: str
        details: list[ErrorDetail]
        message: str
        target: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.ErrorResponse(Model):
        error: ErrorDetail

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.EventGridDataConnection(DataConnection):
        blob_storage_event_type: Union[str, BlobStorageEventType]
        consumer_group: str
        data_format: Union[str, EventGridDataFormat]
        database_routing: Union[str, DatabaseRouting]
        event_grid_resource_id: str
        event_hub_resource_id: str
        id: str
        ignore_first_record: bool
        kind: Union[str, DataConnectionKind]
        location: str
        managed_identity_object_id: str
        managed_identity_resource_id: str
        mapping_rule_name: str
        name: str
        provisioning_state: Union[str, ProvisioningState]
        storage_account_resource_id: str
        table_name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                blob_storage_event_type: Optional[Union[str, BlobStorageEventType]] = ..., 
                consumer_group: Optional[str] = ..., 
                data_format: Optional[Union[str, EventGridDataFormat]] = ..., 
                database_routing: Optional[Union[str, DatabaseRouting]] = ..., 
                event_grid_resource_id: Optional[str] = ..., 
                event_hub_resource_id: Optional[str] = ..., 
                ignore_first_record: Optional[bool] = ..., 
                location: Optional[str] = ..., 
                managed_identity_resource_id: Optional[str] = ..., 
                mapping_rule_name: Optional[str] = ..., 
                storage_account_resource_id: Optional[str] = ..., 
                table_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.EventGridDataFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APACHEAVRO = "APACHEAVRO"
        AVRO = "AVRO"
        CSV = "CSV"
        JSON = "JSON"
        MULTIJSON = "MULTIJSON"
        ORC = "ORC"
        PARQUET = "PARQUET"
        PSV = "PSV"
        RAW = "RAW"
        SCSV = "SCSV"
        SINGLEJSON = "SINGLEJSON"
        SOHSV = "SOHSV"
        TSV = "TSV"
        TSVE = "TSVE"
        TXT = "TXT"
        W3_CLOGFILE = "W3CLOGFILE"


    class azure.mgmt.kusto.models.EventHubDataConnection(DataConnection):
        compression: Union[str, Compression]
        consumer_group: str
        data_format: Union[str, EventHubDataFormat]
        database_routing: Union[str, DatabaseRouting]
        event_hub_resource_id: str
        event_system_properties: list[str]
        id: str
        kind: Union[str, DataConnectionKind]
        location: str
        managed_identity_object_id: str
        managed_identity_resource_id: str
        mapping_rule_name: str
        name: str
        provisioning_state: Union[str, ProvisioningState]
        retrieval_start_date: datetime
        table_name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                compression: Union[str, Compression] = None, 
                consumer_group: Optional[str] = ..., 
                data_format: Optional[Union[str, EventHubDataFormat]] = ..., 
                database_routing: Optional[Union[str, DatabaseRouting]] = ..., 
                event_hub_resource_id: Optional[str] = ..., 
                event_system_properties: Optional[List[str]] = ..., 
                location: Optional[str] = ..., 
                managed_identity_resource_id: Optional[str] = ..., 
                mapping_rule_name: Optional[str] = ..., 
                retrieval_start_date: Optional[datetime] = ..., 
                table_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.EventHubDataFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APACHEAVRO = "APACHEAVRO"
        AVRO = "AVRO"
        CSV = "CSV"
        JSON = "JSON"
        MULTIJSON = "MULTIJSON"
        ORC = "ORC"
        PARQUET = "PARQUET"
        PSV = "PSV"
        RAW = "RAW"
        SCSV = "SCSV"
        SINGLEJSON = "SINGLEJSON"
        SOHSV = "SOHSV"
        TSV = "TSV"
        TSVE = "TSVE"
        TXT = "TXT"
        W3_CLOGFILE = "W3CLOGFILE"


    class azure.mgmt.kusto.models.FollowerDatabaseDefinition(Model):
        attached_database_configuration_name: str
        cluster_resource_id: str
        database_name: str
        database_share_origin: Union[str, DatabaseShareOrigin]
        table_level_sharing_properties: TableLevelSharingProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                attached_database_configuration_name: str, 
                cluster_resource_id: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.FollowerDatabaseDefinitionGet(Model):
        attached_database_configuration_name: str
        cluster_resource_id: str
        database_name: str
        database_share_origin: Union[str, DatabaseShareOrigin]
        table_level_sharing_properties: TableLevelSharingProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                attached_database_configuration_name: Optional[str] = ..., 
                cluster_resource_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.FollowerDatabaseListResult(Model):
        value: list[FollowerDatabaseDefinition]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[FollowerDatabaseDefinition]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.FollowerDatabaseListResultGet(Model):
        next_link: str
        value: list[FollowerDatabaseDefinitionGet]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[FollowerDatabaseDefinitionGet]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.Identity(Model):
        principal_id: str
        tenant_id: str
        type: Union[str, IdentityType]
        user_assigned_identities: dict[str, ComponentsSgqdofSchemasIdentityPropertiesUserassignedidentitiesAdditionalproperties]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                type: Union[str, IdentityType], 
                user_assigned_identities: Optional[Dict[str, ComponentsSgqdofSchemasIdentityPropertiesUserassignedidentitiesAdditionalproperties]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.IdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned, UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.kusto.models.IotHubDataConnection(DataConnection):
        consumer_group: str
        data_format: Union[str, IotHubDataFormat]
        database_routing: Union[str, DatabaseRouting]
        event_system_properties: list[str]
        id: str
        iot_hub_resource_id: str
        kind: Union[str, DataConnectionKind]
        location: str
        mapping_rule_name: str
        name: str
        provisioning_state: Union[str, ProvisioningState]
        retrieval_start_date: datetime
        shared_access_policy_name: str
        table_name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                consumer_group: Optional[str] = ..., 
                data_format: Optional[Union[str, IotHubDataFormat]] = ..., 
                database_routing: Optional[Union[str, DatabaseRouting]] = ..., 
                event_system_properties: Optional[List[str]] = ..., 
                iot_hub_resource_id: Optional[str] = ..., 
                location: Optional[str] = ..., 
                mapping_rule_name: Optional[str] = ..., 
                retrieval_start_date: Optional[datetime] = ..., 
                shared_access_policy_name: Optional[str] = ..., 
                table_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.IotHubDataFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APACHEAVRO = "APACHEAVRO"
        AVRO = "AVRO"
        CSV = "CSV"
        JSON = "JSON"
        MULTIJSON = "MULTIJSON"
        ORC = "ORC"
        PARQUET = "PARQUET"
        PSV = "PSV"
        RAW = "RAW"
        SCSV = "SCSV"
        SINGLEJSON = "SINGLEJSON"
        SOHSV = "SOHSV"
        TSV = "TSV"
        TSVE = "TSVE"
        TXT = "TXT"
        W3_CLOGFILE = "W3CLOGFILE"


    class azure.mgmt.kusto.models.KeyVaultProperties(Model):
        key_name: str
        key_vault_uri: str
        key_version: str
        user_identity: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key_name: Optional[str] = ..., 
                key_vault_uri: Optional[str] = ..., 
                key_version: Optional[str] = ..., 
                user_identity: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.Kind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        READ_ONLY_FOLLOWING = "ReadOnlyFollowing"
        READ_WRITE = "ReadWrite"


    class azure.mgmt.kusto.models.Language(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PYTHON = "Python"


    class azure.mgmt.kusto.models.LanguageExtension(Model):
        language_extension_custom_image_name: str
        language_extension_image_name: Union[str, LanguageExtensionImageName]
        language_extension_name: Union[str, LanguageExtensionName]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                language_extension_custom_image_name: Optional[str] = ..., 
                language_extension_image_name: Optional[Union[str, LanguageExtensionImageName]] = ..., 
                language_extension_name: Optional[Union[str, LanguageExtensionName]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.LanguageExtensionImageName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PYTHON3_10_8 = "Python3_10_8"
        PYTHON3_10_8_DL = "Python3_10_8_DL"
        PYTHON3_11_7 = "Python3_11_7"
        PYTHON3_11_7_DL = "Python3_11_7_DL"
        PYTHON3_6_5 = "Python3_6_5"
        PYTHON_CUSTOM_IMAGE = "PythonCustomImage"
        R = "R"


    class azure.mgmt.kusto.models.LanguageExtensionName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PYTHON = "PYTHON"
        R = "R"


    class azure.mgmt.kusto.models.LanguageExtensionsList(Model):
        value: list[LanguageExtension]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[LanguageExtension]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.ListResourceSkusResult(Model):
        value: list[AzureResourceSku]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[AzureResourceSku]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.ManagedPrivateEndpoint(ProxyResource):
        group_id: str
        id: str
        name: str
        private_link_resource_id: str
        private_link_resource_region: str
        provisioning_state: Union[str, ProvisioningState]
        request_message: str
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                group_id: Optional[str] = ..., 
                private_link_resource_id: Optional[str] = ..., 
                private_link_resource_region: Optional[str] = ..., 
                request_message: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.ManagedPrivateEndpointListResult(Model):
        value: list[ManagedPrivateEndpoint]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[ManagedPrivateEndpoint]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.ManagedPrivateEndpointsCheckNameRequest(Model):
        name: str
        type: str = "Microsoft.Kusto/clusters/managedPrivateEndpoints"

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.MigrationClusterProperties(Model):
        data_ingestion_uri: str
        id: str
        role: Union[str, MigrationClusterRole]
        uri: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.MigrationClusterRole(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DESTINATION = "Destination"
        SOURCE = "Source"


    class azure.mgmt.kusto.models.Operation(Model):
        display: OperationDisplay
        name: str
        origin: str
        properties: JSON

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
                name: Optional[str] = ..., 
                origin: Optional[str] = ..., 
                properties: Optional[JSON] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.OperationDisplay(Model):
        description: str
        operation: str
        provider: str
        resource: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                operation: Optional[str] = ..., 
                provider: Optional[str] = ..., 
                resource: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.OperationListResult(Model):
        next_link: str
        value: list[Operation]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[Operation]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.OperationResult(Model):
        code: str
        end_time: datetime
        id: str
        message: str
        name: str
        operation_kind: str
        operation_state: str
        percent_complete: float
        provisioning_state: Union[str, ProvisioningState]
        start_time: datetime
        status: Union[str, Status]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                end_time: Optional[datetime] = ..., 
                message: Optional[str] = ..., 
                operation_kind: Optional[str] = ..., 
                operation_state: Optional[str] = ..., 
                percent_complete: Optional[float] = ..., 
                start_time: Optional[datetime] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.OptimizedAutoscale(Model):
        is_enabled: bool
        maximum: int
        minimum: int
        version: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                is_enabled: bool, 
                maximum: int, 
                minimum: int, 
                version: int, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.OutboundAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW = "Allow"
        DENY = "Deny"


    class azure.mgmt.kusto.models.OutboundNetworkDependenciesEndpoint(ProxyResource):
        category: str
        endpoints: list[EndpointDependency]
        etag: str
        id: str
        name: str
        provisioning_state: Union[str, ProvisioningState]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                category: Optional[str] = ..., 
                endpoints: Optional[List[EndpointDependency]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.OutboundNetworkDependenciesEndpointListResult(Model):
        next_link: str
        value: list[OutboundNetworkDependenciesEndpoint]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: List[OutboundNetworkDependenciesEndpoint], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.PrincipalPermissionsAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        REMOVE_PERMISSION_ON_SCRIPT_COMPLETION = "RemovePermissionOnScriptCompletion"
        RETAIN_PERMISSION_ON_SCRIPT_COMPLETION = "RetainPermissionOnScriptCompletion"


    class azure.mgmt.kusto.models.PrincipalType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APP = "App"
        GROUP = "Group"
        USER = "User"


    class azure.mgmt.kusto.models.PrincipalsModificationKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        REPLACE = "Replace"
        UNION = "Union"


    class azure.mgmt.kusto.models.PrivateEndpointConnection(ProxyResource):
        group_id: str
        id: str
        name: str
        private_endpoint: PrivateEndpointProperty
        private_link_service_connection_state: PrivateLinkServiceConnectionStateProperty
        provisioning_state: str
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                private_link_service_connection_state: Optional[PrivateLinkServiceConnectionStateProperty] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.PrivateEndpointConnectionListResult(Model):
        value: list[PrivateEndpointConnection]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[PrivateEndpointConnection]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.PrivateEndpointProperty(Model):
        id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.PrivateLinkResource(Resource):
        group_id: str
        id: str
        name: str
        required_members: list[str]
        required_zone_names: list[str]
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.PrivateLinkResourceListResult(Model):
        value: list[PrivateLinkResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[PrivateLinkResource]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.PrivateLinkServiceConnectionStateProperty(Model):
        actions_required: str
        description: str
        status: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                status: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        MOVING = "Moving"
        RUNNING = "Running"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.kusto.models.ProxyResource(Resource):
        id: str
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.PublicIPType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DUAL_STACK = "DualStack"
        I_PV4 = "IPv4"


    class azure.mgmt.kusto.models.PublicNetworkAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.kusto.models.ReadOnlyFollowingDatabase(Database):
        attached_database_configuration_name: str
        database_share_origin: Union[str, DatabaseShareOrigin]
        hot_cache_period: timedelta
        id: str
        kind: Union[str, Kind]
        leader_cluster_resource_id: str
        location: str
        name: str
        original_database_name: str
        principals_modification_kind: Union[str, PrincipalsModificationKind]
        provisioning_state: Union[str, ProvisioningState]
        soft_delete_period: timedelta
        statistics: DatabaseStatistics
        suspension_details: SuspensionDetails
        table_level_sharing_properties: TableLevelSharingProperties
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                hot_cache_period: Optional[timedelta] = ..., 
                location: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.ReadWriteDatabase(Database):
        hot_cache_period: timedelta
        id: str
        is_followed: bool
        key_vault_properties: KeyVaultProperties
        kind: Union[str, Kind]
        location: str
        name: str
        provisioning_state: Union[str, ProvisioningState]
        soft_delete_period: timedelta
        statistics: DatabaseStatistics
        suspension_details: SuspensionDetails
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                hot_cache_period: Optional[timedelta] = ..., 
                key_vault_properties: Optional[KeyVaultProperties] = ..., 
                location: Optional[str] = ..., 
                soft_delete_period: Optional[timedelta] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.Reason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALREADY_EXISTS = "AlreadyExists"
        INVALID = "Invalid"


    class azure.mgmt.kusto.models.Resource(Model):
        id: str
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.ResourceSkuCapabilities(Model):
        name: str
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.ResourceSkuZoneDetails(Model):
        capabilities: list[ResourceSkuCapabilities]
        name: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.SandboxCustomImage(ProxyResource):
        base_image_name: str
        id: str
        language: Union[str, Language]
        language_version: str
        name: str
        provisioning_state: Union[str, ProvisioningState]
        requirements_file_content: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                base_image_name: Optional[str] = ..., 
                language: Optional[Union[str, Language]] = ..., 
                language_version: Optional[str] = ..., 
                requirements_file_content: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.SandboxCustomImagesCheckNameRequest(Model):
        name: str
        type: str = "Microsoft.Kusto/clusters/sandboxCustomImages"

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.SandboxCustomImagesListResult(Model):
        next_link: str
        value: list[SandboxCustomImage]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[SandboxCustomImage]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.Script(ProxyResource):
        continue_on_errors: bool
        force_update_tag: str
        id: str
        name: str
        principal_permissions_action: Union[str, PrincipalPermissionsAction]
        provisioning_state: Union[str, ProvisioningState]
        script_content: str
        script_level: Union[str, ScriptLevel]
        script_url: str
        script_url_sas_token: str
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                continue_on_errors: bool = False, 
                force_update_tag: Optional[str] = ..., 
                principal_permissions_action: Optional[Union[str, PrincipalPermissionsAction]] = ..., 
                script_content: Optional[str] = ..., 
                script_level: Optional[Union[str, ScriptLevel]] = ..., 
                script_url: Optional[str] = ..., 
                script_url_sas_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.ScriptCheckNameRequest(Model):
        name: str
        type: str = "Microsoft.Kusto/clusters/databases/scripts"

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.ScriptLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLUSTER = "Cluster"
        DATABASE = "Database"


    class azure.mgmt.kusto.models.ScriptListResult(Model):
        value: list[Script]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[Script]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.SkuDescription(Model):
        location_info: list[SkuLocationInfoItem]
        locations: list[str]
        name: str
        resource_type: str
        restrictions: list[JSON]
        tier: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.SkuDescriptionList(Model):
        value: list[SkuDescription]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.SkuLocationInfoItem(Model):
        location: str
        zone_details: list[ResourceSkuZoneDetails]
        zones: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: str, 
                zone_details: Optional[List[ResourceSkuZoneDetails]] = ..., 
                zones: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.State(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "Creating"
        DELETED = "Deleted"
        DELETING = "Deleting"
        MIGRATED = "Migrated"
        RUNNING = "Running"
        STARTING = "Starting"
        STOPPED = "Stopped"
        STOPPING = "Stopping"
        UNAVAILABLE = "Unavailable"
        UPDATING = "Updating"


    class azure.mgmt.kusto.models.Status(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        RUNNING = "Running"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.kusto.models.SuspensionDetails(Model):
        suspension_start_date: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                suspension_start_date: Optional[datetime] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.SystemData(Model):
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
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.TableLevelSharingProperties(Model):
        external_tables_to_exclude: list[str]
        external_tables_to_include: list[str]
        functions_to_exclude: list[str]
        functions_to_include: list[str]
        materialized_views_to_exclude: list[str]
        materialized_views_to_include: list[str]
        tables_to_exclude: list[str]
        tables_to_include: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                external_tables_to_exclude: Optional[List[str]] = ..., 
                external_tables_to_include: Optional[List[str]] = ..., 
                functions_to_exclude: Optional[List[str]] = ..., 
                functions_to_include: Optional[List[str]] = ..., 
                materialized_views_to_exclude: Optional[List[str]] = ..., 
                materialized_views_to_include: Optional[List[str]] = ..., 
                tables_to_exclude: Optional[List[str]] = ..., 
                tables_to_include: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.TrackedResource(Resource):
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
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.TrustedExternalTenant(Model):
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.Type(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MICROSOFT_KUSTO_CLUSTERS_ATTACHED_DATABASE_CONFIGURATIONS = "Microsoft.Kusto/clusters/attachedDatabaseConfigurations"
        MICROSOFT_KUSTO_CLUSTERS_DATABASES = "Microsoft.Kusto/clusters/databases"


    class azure.mgmt.kusto.models.VirtualNetworkConfiguration(Model):
        data_management_public_ip_id: str
        engine_public_ip_id: str
        state: Union[str, VnetState]
        subnet_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                data_management_public_ip_id: str, 
                engine_public_ip_id: str, 
                state: Union[str, VnetState] = "Enabled", 
                subnet_id: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.kusto.models.VnetState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.kusto.models.ZoneStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NON_ZONAL = "NonZonal"
        ZONAL = "Zonal"
        ZONAL_INCONSISTENCY = "ZonalInconsistency"


namespace azure.mgmt.kusto.operations

    class azure.mgmt.kusto.operations.AttachedDatabaseConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                attached_database_configuration_name: str, 
                parameters: AttachedDatabaseConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AttachedDatabaseConfiguration]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                attached_database_configuration_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AttachedDatabaseConfiguration]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                attached_database_configuration_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def check_name_availability(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                resource_name: AttachedDatabaseConfigurationsCheckNameRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameResult: ...

        @overload
        def check_name_availability(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                resource_name: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameResult: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                attached_database_configuration_name: str, 
                **kwargs: Any
            ) -> AttachedDatabaseConfiguration: ...

        @distributed_trace
        def list_by_cluster(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> Iterable[AttachedDatabaseConfiguration]: ...


    class azure.mgmt.kusto.operations.ClusterPrincipalAssignmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                principal_assignment_name: str, 
                parameters: ClusterPrincipalAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ClusterPrincipalAssignment]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                principal_assignment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ClusterPrincipalAssignment]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                principal_assignment_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def check_name_availability(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                principal_assignment_name: ClusterPrincipalAssignmentCheckNameRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameResult: ...

        @overload
        def check_name_availability(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                principal_assignment_name: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameResult: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                principal_assignment_name: str, 
                **kwargs: Any
            ) -> ClusterPrincipalAssignment: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> Iterable[ClusterPrincipalAssignment]: ...


    class azure.mgmt.kusto.operations.ClustersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_add_callout_policies(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                callout_policies: CalloutPoliciesList, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_add_callout_policies(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                callout_policies: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_add_language_extensions(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                language_extensions_to_add: LanguageExtensionsList, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_add_language_extensions(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                language_extensions_to_add: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: Cluster, 
                if_match: Optional[str] = None, 
                if_none_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: IO[bytes], 
                if_match: Optional[str] = None, 
                if_none_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_detach_follower_databases(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                follower_database_to_remove: FollowerDatabaseDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_detach_follower_databases(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                follower_database_to_remove: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_diagnose_virtual_network(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> LROPoller[DiagnoseVirtualNetworkResult]: ...

        @overload
        def begin_migrate(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                cluster_migrate_request: ClusterMigrateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_migrate(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                cluster_migrate_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_remove_callout_policy(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                callout_policy: CalloutPolicyToRemove, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_remove_callout_policy(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                callout_policy: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_remove_language_extensions(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                language_extensions_to_remove: LanguageExtensionsList, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_remove_language_extensions(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                language_extensions_to_remove: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_start(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_stop(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: ClusterUpdate, 
                if_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: IO[bytes], 
                if_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @overload
        def check_name_availability(
                self, 
                location: str, 
                cluster_name: ClusterCheckNameRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameResult: ...

        @overload
        def check_name_availability(
                self, 
                location: str, 
                cluster_name: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameResult: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> Cluster: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> Iterable[Cluster]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> Iterable[Cluster]: ...

        @distributed_trace
        def list_callout_policies(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> Iterable[CalloutPolicy]: ...

        @distributed_trace
        def list_follower_databases(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> Iterable[FollowerDatabaseDefinition]: ...

        @distributed_trace
        def list_follower_databases_get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> Iterable[FollowerDatabaseDefinitionGet]: ...

        @distributed_trace
        def list_language_extensions(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> Iterable[LanguageExtension]: ...

        @distributed_trace
        def list_outbound_network_dependencies_endpoints(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> Iterable[OutboundNetworkDependenciesEndpoint]: ...

        @distributed_trace
        def list_skus(self, **kwargs: Any) -> Iterable[SkuDescription]: ...

        @distributed_trace
        def list_skus_by_resource(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> Iterable[AzureResourceSku]: ...


    class azure.mgmt.kusto.operations.DataConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                data_connection_name: str, 
                parameters: DataConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DataConnection]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                data_connection_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DataConnection]: ...

        @overload
        def begin_data_connection_validation(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                parameters: DataConnectionValidation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DataConnectionValidationListResult]: ...

        @overload
        def begin_data_connection_validation(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DataConnectionValidationListResult]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                data_connection_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                data_connection_name: str, 
                parameters: DataConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DataConnection]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                data_connection_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DataConnection]: ...

        @overload
        def check_name_availability(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                data_connection_name: DataConnectionCheckNameRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameResult: ...

        @overload
        def check_name_availability(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                data_connection_name: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameResult: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                data_connection_name: str, 
                **kwargs: Any
            ) -> DataConnection: ...

        @distributed_trace
        def list_by_database(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> Iterable[DataConnection]: ...


    class azure.mgmt.kusto.operations.DatabaseOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def invite_follower(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                parameters: DatabaseInviteFollowerRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DatabaseInviteFollowerResult: ...

        @overload
        def invite_follower(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DatabaseInviteFollowerResult: ...


    class azure.mgmt.kusto.operations.DatabasePrincipalAssignmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                principal_assignment_name: str, 
                parameters: DatabasePrincipalAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DatabasePrincipalAssignment]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                principal_assignment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DatabasePrincipalAssignment]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                principal_assignment_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def check_name_availability(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                principal_assignment_name: DatabasePrincipalAssignmentCheckNameRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameResult: ...

        @overload
        def check_name_availability(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                principal_assignment_name: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameResult: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                principal_assignment_name: str, 
                **kwargs: Any
            ) -> DatabasePrincipalAssignment: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> Iterable[DatabasePrincipalAssignment]: ...


    class azure.mgmt.kusto.operations.DatabasesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def add_principals(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                database_principals_to_add: DatabasePrincipalListRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DatabasePrincipalListResult: ...

        @overload
        def add_principals(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                database_principals_to_add: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DatabasePrincipalListResult: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                parameters: Database, 
                caller_role: Union[str, CallerRole] = "Admin", 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Database]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                parameters: IO[bytes], 
                caller_role: Union[str, CallerRole] = "Admin", 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Database]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                parameters: Database, 
                caller_role: Union[str, CallerRole] = "Admin", 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Database]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                parameters: IO[bytes], 
                caller_role: Union[str, CallerRole] = "Admin", 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Database]: ...

        @overload
        def check_name_availability(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                resource_name: CheckNameRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameResult: ...

        @overload
        def check_name_availability(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                resource_name: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameResult: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> Database: ...

        @distributed_trace
        def list_by_cluster(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                top: Optional[int] = None, 
                skiptoken: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[Database]: ...

        @distributed_trace
        def list_principals(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> Iterable[DatabasePrincipal]: ...

        @overload
        def remove_principals(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                database_principals_to_remove: DatabasePrincipalListRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DatabasePrincipalListResult: ...

        @overload
        def remove_principals(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                database_principals_to_remove: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DatabasePrincipalListResult: ...


    class azure.mgmt.kusto.operations.ManagedPrivateEndpointsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                managed_private_endpoint_name: str, 
                parameters: ManagedPrivateEndpoint, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedPrivateEndpoint]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                managed_private_endpoint_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedPrivateEndpoint]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                managed_private_endpoint_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                managed_private_endpoint_name: str, 
                parameters: ManagedPrivateEndpoint, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedPrivateEndpoint]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                managed_private_endpoint_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedPrivateEndpoint]: ...

        @overload
        def check_name_availability(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                resource_name: ManagedPrivateEndpointsCheckNameRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameResult: ...

        @overload
        def check_name_availability(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                resource_name: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameResult: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                managed_private_endpoint_name: str, 
                **kwargs: Any
            ) -> ManagedPrivateEndpoint: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> Iterable[ManagedPrivateEndpoint]: ...


    class azure.mgmt.kusto.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(self, **kwargs: Any) -> Iterable[Operation]: ...


    class azure.mgmt.kusto.operations.OperationsResultsLocationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.kusto.operations.OperationsResultsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationResult: ...


    class azure.mgmt.kusto.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
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
                cluster_name: str, 
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
                cluster_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> Iterable[PrivateEndpointConnection]: ...


    class azure.mgmt.kusto.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                private_link_resource_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> Iterable[PrivateLinkResource]: ...


    class azure.mgmt.kusto.operations.SandboxCustomImagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                sandbox_custom_image_name: str, 
                parameters: SandboxCustomImage, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SandboxCustomImage]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                sandbox_custom_image_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SandboxCustomImage]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                sandbox_custom_image_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                sandbox_custom_image_name: str, 
                parameters: SandboxCustomImage, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SandboxCustomImage]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                sandbox_custom_image_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SandboxCustomImage]: ...

        @overload
        def check_name_availability(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                resource_name: SandboxCustomImagesCheckNameRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameResult: ...

        @overload
        def check_name_availability(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                resource_name: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameResult: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                sandbox_custom_image_name: str, 
                **kwargs: Any
            ) -> SandboxCustomImage: ...

        @distributed_trace
        def list_by_cluster(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> Iterable[SandboxCustomImage]: ...


    class azure.mgmt.kusto.operations.ScriptsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                script_name: str, 
                parameters: Script, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Script]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                script_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Script]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                script_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                script_name: str, 
                parameters: Script, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Script]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                script_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Script]: ...

        @overload
        def check_name_availability(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                script_name: ScriptCheckNameRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameResult: ...

        @overload
        def check_name_availability(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                script_name: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameResult: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                script_name: str, 
                **kwargs: Any
            ) -> Script: ...

        @distributed_trace
        def list_by_database(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> Iterable[Script]: ...


    class azure.mgmt.kusto.operations.SkusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                **kwargs: Any
            ) -> Iterable[SkuDescription]: ...


```