```py
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
                parameters: JSON, 
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
                resource_name: JSON, 
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
            ) -> AsyncItemPaged[AttachedDatabaseConfiguration]: ...


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
                parameters: JSON, 
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
                principal_assignment_name: JSON, 
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
            ) -> AsyncItemPaged[ClusterPrincipalAssignment]: ...


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
                callout_policies: JSON, 
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
                language_extensions_to_add: JSON, 
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
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
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
                follower_database_to_remove: JSON, 
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
                cluster_migrate_request: JSON, 
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
                callout_policy: JSON, 
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
                language_extensions_to_remove: JSON, 
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
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
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
                cluster_name: JSON, 
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
        def list(self, **kwargs: Any) -> AsyncItemPaged[Cluster]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Cluster]: ...

        @distributed_trace
        def list_callout_policies(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[CalloutPolicy]: ...

        @distributed_trace
        def list_follower_databases(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[FollowerDatabaseDefinition]: ...

        @distributed_trace
        def list_follower_databases_get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[FollowerDatabaseDefinitionGet]: ...

        @distributed_trace
        def list_language_extensions(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[LanguageExtension]: ...

        @distributed_trace
        def list_outbound_network_dependencies_endpoints(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[OutboundNetworkDependenciesEndpoint]: ...

        @distributed_trace
        def list_skus(self, **kwargs: Any) -> AsyncItemPaged[SkuDescription]: ...

        @distributed_trace
        def list_skus_by_resource(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AzureResourceSku]: ...


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
                parameters: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                data_connection_name: JSON, 
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
            ) -> AsyncItemPaged[DataConnection]: ...


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
                parameters: JSON, 
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
                parameters: JSON, 
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
                principal_assignment_name: JSON, 
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
            ) -> AsyncItemPaged[DatabasePrincipalAssignment]: ...


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
                database_principals_to_add: JSON, 
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
                *, 
                caller_role: Optional[Union[str, CallerRole]] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Database]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                parameters: JSON, 
                *, 
                caller_role: Optional[Union[str, CallerRole]] = ..., 
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
                *, 
                caller_role: Optional[Union[str, CallerRole]] = ..., 
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
                *, 
                caller_role: Optional[Union[str, CallerRole]] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Database]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                parameters: JSON, 
                *, 
                caller_role: Optional[Union[str, CallerRole]] = ..., 
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
                *, 
                caller_role: Optional[Union[str, CallerRole]] = ..., 
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
                resource_name: JSON, 
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
                *, 
                skiptoken: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Database]: ...

        @distributed_trace
        def list_principals(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DatabasePrincipal]: ...

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
                database_principals_to_remove: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                resource_name: JSON, 
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
            ) -> AsyncItemPaged[ManagedPrivateEndpoint]: ...


    class azure.mgmt.kusto.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


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
                parameters: JSON, 
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
            ) -> AsyncItemPaged[PrivateEndpointConnection]: ...


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
            ) -> AsyncItemPaged[PrivateLinkResource]: ...


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
                parameters: JSON, 
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
                parameters: JSON, 
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
                resource_name: JSON, 
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
            ) -> AsyncItemPaged[SandboxCustomImage]: ...


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
                parameters: JSON, 
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
                parameters: JSON, 
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
                script_name: JSON, 
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
            ) -> AsyncItemPaged[Script]: ...


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
            ) -> AsyncItemPaged[SkuDescription]: ...


namespace azure.mgmt.kusto.models

    class azure.mgmt.kusto.models.AcceptedAudiences(_Model):
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kusto.models.AttachedDatabaseConfiguration(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[AttachedDatabaseConfigurationProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[AttachedDatabaseConfigurationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.kusto.models.AttachedDatabaseConfigurationProperties(_Model):
        attached_database_names: Optional[list[str]]
        cluster_resource_id: str
        database_name: str
        database_name_override: Optional[str]
        database_name_prefix: Optional[str]
        default_principals_modification_kind: Union[str, DefaultPrincipalsModificationKind]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        table_level_sharing_properties: Optional[TableLevelSharingProperties]

        @overload
        def __init__(
                self, 
                *, 
                cluster_resource_id: str, 
                database_name: str, 
                database_name_override: Optional[str] = ..., 
                database_name_prefix: Optional[str] = ..., 
                default_principals_modification_kind: Union[str, DefaultPrincipalsModificationKind], 
                table_level_sharing_properties: Optional[TableLevelSharingProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kusto.models.AttachedDatabaseConfigurationsCheckNameRequest(_Model):
        name: str
        type: Literal["Kusto/clusters/attachedDatabaseConfigurations"]

        @overload
        def __init__(
                self, 
                *, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kusto.models.AzureCapacity(_Model):
        default: int
        maximum: int
        minimum: int
        scale_type: Union[str, AzureScaleType]

        @overload
        def __init__(
                self, 
                *, 
                default: int, 
                maximum: int, 
                minimum: int, 
                scale_type: Union[str, AzureScaleType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kusto.models.AzureResourceSku(_Model):
        capacity: Optional[AzureCapacity]
        resource_type: Optional[str]
        sku: Optional[AzureSku]

        @overload
        def __init__(
                self, 
                *, 
                capacity: Optional[AzureCapacity] = ..., 
                resource_type: Optional[str] = ..., 
                sku: Optional[AzureSku] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kusto.models.AzureScaleType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC = "automatic"
        MANUAL = "manual"
        NONE = "none"


    class azure.mgmt.kusto.models.AzureSku(_Model):
        capacity: Optional[int]
        name: Union[str, AzureSkuName]
        tier: Union[str, AzureSkuTier]

        @overload
        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                name: Union[str, AzureSkuName], 
                tier: Union[str, AzureSkuTier]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.kusto.models.CalloutPoliciesList(_Model):
        next_link: Optional[str]
        value: list[CalloutPolicy]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[CalloutPolicy]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kusto.models.CalloutPolicy(_Model):
        callout_id: Optional[str]
        callout_type: Optional[Union[str, CalloutType]]
        callout_uri_regex: Optional[str]
        outbound_access: Optional[Union[str, OutboundAccess]]

        @overload
        def __init__(
                self, 
                *, 
                callout_type: Optional[Union[str, CalloutType]] = ..., 
                callout_uri_regex: Optional[str] = ..., 
                outbound_access: Optional[Union[str, OutboundAccess]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kusto.models.CalloutPolicyToRemove(_Model):
        callout_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                callout_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.kusto.models.CheckNameRequest(_Model):
        name: str
        type: Union[str, Type]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                type: Union[str, Type]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kusto.models.CheckNameResult(_Model):
        message: Optional[str]
        name: Optional[str]
        name_available: Optional[bool]
        reason: Optional[Union[str, Reason]]

        @overload
        def __init__(
                self, 
                *, 
                message: Optional[str] = ..., 
                name: Optional[str] = ..., 
                name_available: Optional[bool] = ..., 
                reason: Optional[Union[str, Reason]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kusto.models.Cluster(TrackedResource):
        etag: Optional[str]
        id: str
        identity: Optional[Identity]
        location: str
        name: str
        properties: Optional[ClusterProperties]
        sku: AzureSku
        system_data: SystemData
        tags: dict[str, str]
        type: str
        zones: Optional[list[str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[Identity] = ..., 
                location: str, 
                properties: Optional[ClusterProperties] = ..., 
                sku: AzureSku, 
                tags: Optional[dict[str, str]] = ..., 
                zones: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.kusto.models.ClusterCheckNameRequest(_Model):
        name: str
        type: Literal["Kusto/clusters"]

        @overload
        def __init__(
                self, 
                *, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kusto.models.ClusterMigrateRequest(_Model):
        cluster_resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                cluster_resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kusto.models.ClusterNetworkAccessFlag(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.kusto.models.ClusterPrincipalAssignment(ProxyResource):
        id: str
        name: str
        properties: Optional[ClusterPrincipalProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ClusterPrincipalProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.kusto.models.ClusterPrincipalAssignmentCheckNameRequest(_Model):
        name: str
        type: Literal["Kusto/clusters/principalAssignments"]

        @overload
        def __init__(
                self, 
                *, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kusto.models.ClusterPrincipalProperties(_Model):
        aad_object_id: Optional[str]
        principal_id: str
        principal_name: Optional[str]
        principal_type: Union[str, PrincipalType]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        role: Union[str, ClusterPrincipalRole]
        tenant_id: Optional[str]
        tenant_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                principal_id: str, 
                principal_type: Union[str, PrincipalType], 
                role: Union[str, ClusterPrincipalRole], 
                tenant_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kusto.models.ClusterPrincipalRole(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL_DATABASES_ADMIN = "AllDatabasesAdmin"
        ALL_DATABASES_MONITOR = "AllDatabasesMonitor"
        ALL_DATABASES_VIEWER = "AllDatabasesViewer"


    class azure.mgmt.kusto.models.ClusterProperties(_Model):
        accepted_audiences: Optional[list[AcceptedAudiences]]
        allowed_fqdn_list: Optional[list[str]]
        allowed_ip_range_list: Optional[list[str]]
        callout_policies: Optional[list[CalloutPolicy]]
        data_ingestion_uri: Optional[str]
        enable_auto_stop: Optional[bool]
        enable_disk_encryption: Optional[bool]
        enable_double_encryption: Optional[bool]
        enable_purge: Optional[bool]
        enable_streaming_ingest: Optional[bool]
        engine_type: Optional[Union[str, EngineType]]
        key_vault_properties: Optional[KeyVaultProperties]
        language_extensions: Optional[LanguageExtensionsList]
        migration_cluster: Optional[MigrationClusterProperties]
        optimized_autoscale: Optional[OptimizedAutoscale]
        private_endpoint_connections: Optional[list[PrivateEndpointConnection]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        public_ip_type: Optional[Union[str, PublicIPType]]
        public_network_access: Optional[Union[str, PublicNetworkAccess]]
        restrict_outbound_network_access: Optional[Union[str, ClusterNetworkAccessFlag]]
        state: Optional[Union[str, State]]
        state_reason: Optional[str]
        trusted_external_tenants: Optional[list[TrustedExternalTenant]]
        uri: Optional[str]
        virtual_cluster_graduation_properties: Optional[str]
        virtual_network_configuration: Optional[VirtualNetworkConfiguration]
        zone_status: Optional[Union[str, ZoneStatus]]

        @overload
        def __init__(
                self, 
                *, 
                accepted_audiences: Optional[list[AcceptedAudiences]] = ..., 
                allowed_fqdn_list: Optional[list[str]] = ..., 
                allowed_ip_range_list: Optional[list[str]] = ..., 
                callout_policies: Optional[list[CalloutPolicy]] = ..., 
                enable_auto_stop: Optional[bool] = ..., 
                enable_disk_encryption: Optional[bool] = ..., 
                enable_double_encryption: Optional[bool] = ..., 
                enable_purge: Optional[bool] = ..., 
                enable_streaming_ingest: Optional[bool] = ..., 
                engine_type: Optional[Union[str, EngineType]] = ..., 
                key_vault_properties: Optional[KeyVaultProperties] = ..., 
                language_extensions: Optional[LanguageExtensionsList] = ..., 
                optimized_autoscale: Optional[OptimizedAutoscale] = ..., 
                public_ip_type: Optional[Union[str, PublicIPType]] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                restrict_outbound_network_access: Optional[Union[str, ClusterNetworkAccessFlag]] = ..., 
                trusted_external_tenants: Optional[list[TrustedExternalTenant]] = ..., 
                virtual_cluster_graduation_properties: Optional[str] = ..., 
                virtual_network_configuration: Optional[VirtualNetworkConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kusto.models.ClusterUpdate(Resource):
        id: str
        identity: Optional[Identity]
        location: Optional[str]
        name: str
        properties: Optional[ClusterProperties]
        sku: Optional[AzureSku]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str
        zones: Optional[list[str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[Identity] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[ClusterProperties] = ..., 
                sku: Optional[AzureSku] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                zones: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.kusto.models.ComponentsSgqdofSchemasIdentityPropertiesUserassignedidentitiesAdditionalproperties(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.kusto.models.Compression(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        G_ZIP = "GZip"
        NONE = "None"


    class azure.mgmt.kusto.models.CosmosDbDataConnection(DataConnection, discriminator='CosmosDb'):
        id: str
        kind: Literal[DataConnectionKind.COSMOS_DB]
        location: str
        name: str
        properties: Optional[CosmosDbDataConnectionProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[CosmosDbDataConnectionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.kusto.models.CosmosDbDataConnectionProperties(_Model):
        cosmos_db_account_resource_id: str
        cosmos_db_container: str
        cosmos_db_database: str
        managed_identity_object_id: Optional[str]
        managed_identity_resource_id: str
        mapping_rule_name: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        retrieval_start_date: Optional[datetime]
        table_name: str

        @overload
        def __init__(
                self, 
                *, 
                cosmos_db_account_resource_id: str, 
                cosmos_db_container: str, 
                cosmos_db_database: str, 
                managed_identity_resource_id: str, 
                mapping_rule_name: Optional[str] = ..., 
                retrieval_start_date: Optional[datetime] = ..., 
                table_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kusto.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.kusto.models.DataConnection(ProxyResource):
        id: str
        kind: str
        location: Optional[str]
        name: str
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str, 
                location: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kusto.models.DataConnectionCheckNameRequest(_Model):
        name: str
        type: Literal["Kusto/clusters/databases/dataConnections"]

        @overload
        def __init__(
                self, 
                *, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kusto.models.DataConnectionKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COSMOS_DB = "CosmosDb"
        EVENT_GRID = "EventGrid"
        EVENT_GRID_WITH_MANAGED_IDENTITY = "EventGridWithManagedIdentity"
        EVENT_HUB = "EventHub"
        EVENT_HUB_WITH_MANAGED_IDENTITY = "EventHubWithManagedIdentity"
        IOT_HUB = "IotHub"


    class azure.mgmt.kusto.models.DataConnectionValidation(_Model):
        data_connection_name: Optional[str]
        properties: Optional[DataConnection]

        @overload
        def __init__(
                self, 
                *, 
                data_connection_name: Optional[str] = ..., 
                properties: Optional[DataConnection] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kusto.models.DataConnectionValidationListResult(_Model):
        value: Optional[list[DataConnectionValidationResult]]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[list[DataConnectionValidationResult]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kusto.models.DataConnectionValidationResult(_Model):
        error_message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                error_message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kusto.models.Database(ProxyResource):
        id: str
        kind: str
        location: Optional[str]
        name: str
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str, 
                location: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kusto.models.DatabaseInviteFollowerRequest(_Model):
        invitee_email: str
        table_level_sharing_properties: Optional[TableLevelSharingProperties]

        @overload
        def __init__(
                self, 
                *, 
                invitee_email: str, 
                table_level_sharing_properties: Optional[TableLevelSharingProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kusto.models.DatabaseInviteFollowerResult(_Model):
        generated_invitation: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                generated_invitation: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kusto.models.DatabasePrincipal(_Model):
        app_id: Optional[str]
        email: Optional[str]
        fqn: Optional[str]
        name: str
        role: Union[str, DatabasePrincipalRole]
        tenant_name: Optional[str]
        type: Union[str, DatabasePrincipalType]

        @overload
        def __init__(
                self, 
                *, 
                app_id: Optional[str] = ..., 
                email: Optional[str] = ..., 
                fqn: Optional[str] = ..., 
                name: str, 
                role: Union[str, DatabasePrincipalRole], 
                type: Union[str, DatabasePrincipalType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kusto.models.DatabasePrincipalAssignment(ProxyResource):
        id: str
        name: str
        properties: Optional[DatabasePrincipalProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DatabasePrincipalProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.kusto.models.DatabasePrincipalAssignmentCheckNameRequest(_Model):
        name: str
        type: Literal["Kusto/clusters/databases/principalAssignments"]

        @overload
        def __init__(
                self, 
                *, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kusto.models.DatabasePrincipalListRequest(_Model):
        value: Optional[list[DatabasePrincipal]]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[list[DatabasePrincipal]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kusto.models.DatabasePrincipalListResult(_Model):
        next_link: Optional[str]
        value: Optional[list[DatabasePrincipal]]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[list[DatabasePrincipal]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kusto.models.DatabasePrincipalProperties(_Model):
        aad_object_id: Optional[str]
        principal_id: str
        principal_name: Optional[str]
        principal_type: Union[str, PrincipalType]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        role: Union[str, DatabasePrincipalRole]
        tenant_id: Optional[str]
        tenant_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                principal_id: str, 
                principal_type: Union[str, PrincipalType], 
                role: Union[str, DatabasePrincipalRole], 
                tenant_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.kusto.models.DatabaseStatistics(_Model):
        size: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                size: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kusto.models.DefaultPrincipalsModificationKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        REPLACE = "Replace"
        UNION = "Union"


    class azure.mgmt.kusto.models.DiagnoseVirtualNetworkResult(_Model):
        findings: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                findings: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kusto.models.EndpointDependency(_Model):
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


    class azure.mgmt.kusto.models.EndpointDetail(_Model):
        ip_address: Optional[str]
        port: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                ip_address: Optional[str] = ..., 
                port: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kusto.models.EngineType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        V2 = "V2"
        V3 = "V3"


    class azure.mgmt.kusto.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.kusto.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.kusto.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kusto.models.EventGridConnectionProperties(_Model):
        blob_storage_event_type: Optional[Union[str, BlobStorageEventType]]
        consumer_group: str
        data_format: Optional[Union[str, EventGridDataFormat]]
        database_routing: Optional[Union[str, DatabaseRouting]]
        event_grid_resource_id: Optional[str]
        event_hub_resource_id: str
        ignore_first_record: Optional[bool]
        managed_identity_object_id: Optional[str]
        managed_identity_resource_id: Optional[str]
        mapping_rule_name: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        storage_account_resource_id: str
        table_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                blob_storage_event_type: Optional[Union[str, BlobStorageEventType]] = ..., 
                consumer_group: str, 
                data_format: Optional[Union[str, EventGridDataFormat]] = ..., 
                database_routing: Optional[Union[str, DatabaseRouting]] = ..., 
                event_grid_resource_id: Optional[str] = ..., 
                event_hub_resource_id: str, 
                ignore_first_record: Optional[bool] = ..., 
                managed_identity_resource_id: Optional[str] = ..., 
                mapping_rule_name: Optional[str] = ..., 
                storage_account_resource_id: str, 
                table_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kusto.models.EventGridConnectionWithManagedIdentityProperties(_Model):
        blob_storage_event_type: Optional[Union[str, BlobStorageEventType]]
        consumer_group: str
        data_format: Optional[Union[str, EventGridDataFormat]]
        database_routing: Optional[Union[str, DatabaseRouting]]
        event_grid_resource_id: Optional[str]
        event_hub_resource_id_for_managed_identity: str
        ignore_first_record: Optional[bool]
        managed_identity_object_id: Optional[str]
        managed_identity_resource_id: str
        mapping_rule_name: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        storage_account_resource_id_for_managed_identity: str
        table_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                blob_storage_event_type: Optional[Union[str, BlobStorageEventType]] = ..., 
                consumer_group: str, 
                data_format: Optional[Union[str, EventGridDataFormat]] = ..., 
                database_routing: Optional[Union[str, DatabaseRouting]] = ..., 
                event_grid_resource_id: Optional[str] = ..., 
                event_hub_resource_id_for_managed_identity: str, 
                ignore_first_record: Optional[bool] = ..., 
                managed_identity_resource_id: str, 
                mapping_rule_name: Optional[str] = ..., 
                storage_account_resource_id_for_managed_identity: str, 
                table_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kusto.models.EventGridDataConnection(DataConnection, discriminator='EventGrid'):
        id: str
        kind: Literal[DataConnectionKind.EVENT_GRID]
        location: str
        name: str
        properties: Optional[EventGridConnectionProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[EventGridConnectionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.kusto.models.EventGridDataConnectionWithManagedIdentity(DataConnection, discriminator='EventGridWithManagedIdentity'):
        id: str
        kind: Literal[DataConnectionKind.EVENT_GRID_WITH_MANAGED_IDENTITY]
        location: str
        name: str
        properties: Optional[EventGridConnectionWithManagedIdentityProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[EventGridConnectionWithManagedIdentityProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.kusto.models.EventGridDataFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APACHEAVRO = "APACHEAVRO"
        AVRO = "AVRO"
        AZMONSTREAM = "AZMONSTREAM"
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


    class azure.mgmt.kusto.models.EventHubConnectionProperties(_Model):
        compression: Optional[Union[str, Compression]]
        consumer_group: str
        data_format: Optional[Union[str, EventHubDataFormat]]
        database_routing: Optional[Union[str, DatabaseRouting]]
        event_hub_resource_id: str
        event_system_properties: Optional[list[str]]
        managed_identity_object_id: Optional[str]
        managed_identity_resource_id: Optional[str]
        mapping_rule_name: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        retrieval_start_date: Optional[datetime]
        table_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                compression: Optional[Union[str, Compression]] = ..., 
                consumer_group: str, 
                data_format: Optional[Union[str, EventHubDataFormat]] = ..., 
                database_routing: Optional[Union[str, DatabaseRouting]] = ..., 
                event_hub_resource_id: str, 
                event_system_properties: Optional[list[str]] = ..., 
                managed_identity_resource_id: Optional[str] = ..., 
                mapping_rule_name: Optional[str] = ..., 
                retrieval_start_date: Optional[datetime] = ..., 
                table_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kusto.models.EventHubConnectionWithManagedIdentityProperties(_Model):
        compression: Optional[Union[str, Compression]]
        consumer_group: str
        data_format: Optional[Union[str, EventHubDataFormat]]
        database_routing: Optional[Union[str, DatabaseRouting]]
        event_hub_resource_id_for_managed_identity: str
        event_system_properties: Optional[list[str]]
        managed_identity_object_id: Optional[str]
        managed_identity_resource_id: str
        mapping_rule_name: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        retrieval_start_date: Optional[datetime]
        table_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                compression: Optional[Union[str, Compression]] = ..., 
                consumer_group: str, 
                data_format: Optional[Union[str, EventHubDataFormat]] = ..., 
                database_routing: Optional[Union[str, DatabaseRouting]] = ..., 
                event_hub_resource_id_for_managed_identity: str, 
                event_system_properties: Optional[list[str]] = ..., 
                managed_identity_resource_id: str, 
                mapping_rule_name: Optional[str] = ..., 
                retrieval_start_date: Optional[datetime] = ..., 
                table_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kusto.models.EventHubDataConnection(DataConnection, discriminator='EventHub'):
        id: str
        kind: Literal[DataConnectionKind.EVENT_HUB]
        location: str
        name: str
        properties: Optional[EventHubConnectionProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[EventHubConnectionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.kusto.models.EventHubDataConnectionWithManagedIdentity(DataConnection, discriminator='EventHubWithManagedIdentity'):
        id: str
        kind: Literal[DataConnectionKind.EVENT_HUB_WITH_MANAGED_IDENTITY]
        location: str
        name: str
        properties: Optional[EventHubConnectionWithManagedIdentityProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[EventHubConnectionWithManagedIdentityProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.kusto.models.EventHubDataFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APACHEAVRO = "APACHEAVRO"
        AVRO = "AVRO"
        AZMONSTREAM = "AZMONSTREAM"
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


    class azure.mgmt.kusto.models.FollowerDatabaseDefinition(_Model):
        attached_database_configuration_name: str
        cluster_resource_id: str
        database_name: Optional[str]
        database_share_origin: Optional[Union[str, DatabaseShareOrigin]]
        table_level_sharing_properties: Optional[TableLevelSharingProperties]

        @overload
        def __init__(
                self, 
                *, 
                attached_database_configuration_name: str, 
                cluster_resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kusto.models.FollowerDatabaseDefinitionGet(_Model):
        properties: Optional[FollowerDatabaseProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[FollowerDatabaseProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.kusto.models.FollowerDatabaseProperties(_Model):
        attached_database_configuration_name: str
        cluster_resource_id: str
        database_name: Optional[str]
        database_share_origin: Optional[Union[str, DatabaseShareOrigin]]
        table_level_sharing_properties: Optional[TableLevelSharingProperties]

        @overload
        def __init__(
                self, 
                *, 
                attached_database_configuration_name: str, 
                cluster_resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kusto.models.Identity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Union[str, IdentityType]
        user_assigned_identities: Optional[dict[str, ComponentsSgqdofSchemasIdentityPropertiesUserassignedidentitiesAdditionalproperties]]

        @overload
        def __init__(
                self, 
                *, 
                type: Union[str, IdentityType], 
                user_assigned_identities: Optional[dict[str, ComponentsSgqdofSchemasIdentityPropertiesUserassignedidentitiesAdditionalproperties]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kusto.models.IdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned, UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.kusto.models.IotHubConnectionProperties(_Model):
        consumer_group: str
        data_format: Optional[Union[str, IotHubDataFormat]]
        database_routing: Optional[Union[str, DatabaseRouting]]
        event_system_properties: Optional[list[str]]
        iot_hub_resource_id: str
        mapping_rule_name: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        retrieval_start_date: Optional[datetime]
        shared_access_policy_name: str
        table_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                consumer_group: str, 
                data_format: Optional[Union[str, IotHubDataFormat]] = ..., 
                database_routing: Optional[Union[str, DatabaseRouting]] = ..., 
                event_system_properties: Optional[list[str]] = ..., 
                iot_hub_resource_id: str, 
                mapping_rule_name: Optional[str] = ..., 
                retrieval_start_date: Optional[datetime] = ..., 
                shared_access_policy_name: str, 
                table_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kusto.models.IotHubDataConnection(DataConnection, discriminator='IotHub'):
        id: str
        kind: Literal[DataConnectionKind.IOT_HUB]
        location: str
        name: str
        properties: Optional[IotHubConnectionProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[IotHubConnectionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.kusto.models.IotHubDataFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APACHEAVRO = "APACHEAVRO"
        AVRO = "AVRO"
        AZMONSTREAM = "AZMONSTREAM"
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


    class azure.mgmt.kusto.models.KeyVaultProperties(_Model):
        federated_identity_client_id: Optional[str]
        key_name: Optional[str]
        key_vault_uri: Optional[str]
        key_version: Optional[str]
        user_identity: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                federated_identity_client_id: Optional[str] = ..., 
                key_name: Optional[str] = ..., 
                key_vault_uri: Optional[str] = ..., 
                key_version: Optional[str] = ..., 
                user_identity: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kusto.models.Kind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        READ_ONLY_FOLLOWING = "ReadOnlyFollowing"
        READ_WRITE = "ReadWrite"


    class azure.mgmt.kusto.models.Language(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PYTHON = "Python"


    class azure.mgmt.kusto.models.LanguageExtension(_Model):
        language_extension_custom_image_name: Optional[str]
        language_extension_image_name: Optional[Union[str, LanguageExtensionImageName]]
        language_extension_name: Optional[Union[str, LanguageExtensionName]]

        @overload
        def __init__(
                self, 
                *, 
                language_extension_custom_image_name: Optional[str] = ..., 
                language_extension_image_name: Optional[Union[str, LanguageExtensionImageName]] = ..., 
                language_extension_name: Optional[Union[str, LanguageExtensionName]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.kusto.models.LanguageExtensionsList(_Model):
        next_link: Optional[str]
        value: Optional[list[LanguageExtension]]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[list[LanguageExtension]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kusto.models.ManagedPrivateEndpoint(ProxyResource):
        id: str
        name: str
        properties: Optional[ManagedPrivateEndpointProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ManagedPrivateEndpointProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.kusto.models.ManagedPrivateEndpointProperties(_Model):
        group_id: str
        private_link_resource_id: str
        private_link_resource_region: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        request_message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                group_id: str, 
                private_link_resource_id: str, 
                private_link_resource_region: Optional[str] = ..., 
                request_message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kusto.models.ManagedPrivateEndpointsCheckNameRequest(_Model):
        name: str
        type: Literal["Kusto/clusters/managedPrivateEndpoints"]

        @overload
        def __init__(
                self, 
                *, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kusto.models.MigrationClusterProperties(_Model):
        data_ingestion_uri: Optional[str]
        id: Optional[str]
        role: Optional[Union[str, MigrationClusterRole]]
        uri: Optional[str]


    class azure.mgmt.kusto.models.MigrationClusterRole(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DESTINATION = "Destination"
        SOURCE = "Source"


    class azure.mgmt.kusto.models.Operation(_Model):
        display: Optional[OperationDisplay]
        name: Optional[str]
        origin: Optional[str]
        properties: Optional[Any]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
                name: Optional[str] = ..., 
                origin: Optional[str] = ..., 
                properties: Optional[Any] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.kusto.models.OperationDisplay(_Model):
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


    class azure.mgmt.kusto.models.OperationResult(_Model):
        end_time: Optional[datetime]
        error: Optional[OperationResultErrorProperties]
        id: Optional[str]
        name: Optional[str]
        percent_complete: Optional[float]
        properties: Optional[OperationResultProperties]
        start_time: Optional[datetime]
        status: Optional[Union[str, Status]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                error: Optional[OperationResultErrorProperties] = ..., 
                percent_complete: Optional[float] = ..., 
                properties: Optional[OperationResultProperties] = ..., 
                start_time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.kusto.models.OperationResultErrorProperties(_Model):
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


    class azure.mgmt.kusto.models.OperationResultProperties(_Model):
        operation_kind: Optional[str]
        operation_state: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                operation_kind: Optional[str] = ..., 
                operation_state: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kusto.models.OptimizedAutoscale(_Model):
        is_enabled: bool
        maximum: int
        minimum: int
        version: int

        @overload
        def __init__(
                self, 
                *, 
                is_enabled: bool, 
                maximum: int, 
                minimum: int, 
                version: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kusto.models.OutboundAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW = "Allow"
        DENY = "Deny"


    class azure.mgmt.kusto.models.OutboundNetworkDependenciesEndpoint(ProxyResource):
        etag: Optional[str]
        id: str
        name: str
        properties: Optional[OutboundNetworkDependenciesEndpointProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[OutboundNetworkDependenciesEndpointProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.kusto.models.OutboundNetworkDependenciesEndpointProperties(_Model):
        category: Optional[str]
        endpoints: Optional[list[EndpointDependency]]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                category: Optional[str] = ..., 
                endpoints: Optional[list[EndpointDependency]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.kusto.models.PrivateEndpointConnectionProperties(_Model):
        group_id: Optional[str]
        private_endpoint: Optional[PrivateEndpointProperty]
        private_link_service_connection_state: PrivateLinkServiceConnectionStateProperty
        provisioning_state: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                private_link_service_connection_state: PrivateLinkServiceConnectionStateProperty
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kusto.models.PrivateEndpointProperty(_Model):
        id: Optional[str]


    class azure.mgmt.kusto.models.PrivateLinkResource(ProxyResource):
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


    class azure.mgmt.kusto.models.PrivateLinkResourceProperties(_Model):
        group_id: Optional[str]
        required_members: Optional[list[str]]
        required_zone_names: Optional[list[str]]


    class azure.mgmt.kusto.models.PrivateLinkServiceConnectionStateProperty(_Model):
        actions_required: Optional[str]
        description: Optional[str]
        status: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                status: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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
        system_data: SystemData
        type: str


    class azure.mgmt.kusto.models.PublicIPType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DUAL_STACK = "DualStack"
        I_PV4 = "IPv4"


    class azure.mgmt.kusto.models.PublicNetworkAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        SECURED_BY_PERIMETER = "SecuredByPerimeter"


    class azure.mgmt.kusto.models.ReadOnlyFollowingDatabase(Database, discriminator='ReadOnlyFollowing'):
        id: str
        kind: Literal[Kind.READ_ONLY_FOLLOWING]
        location: str
        name: str
        properties: Optional[ReadOnlyFollowingDatabaseProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[ReadOnlyFollowingDatabaseProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.kusto.models.ReadOnlyFollowingDatabaseProperties(_Model):
        attached_database_configuration_name: Optional[str]
        database_share_origin: Optional[Union[str, DatabaseShareOrigin]]
        hot_cache_period: Optional[timedelta]
        leader_cluster_resource_id: Optional[str]
        original_database_name: Optional[str]
        principals_modification_kind: Optional[Union[str, PrincipalsModificationKind]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        soft_delete_period: Optional[timedelta]
        statistics: Optional[DatabaseStatistics]
        suspension_details: Optional[SuspensionDetails]
        table_level_sharing_properties: Optional[TableLevelSharingProperties]

        @overload
        def __init__(
                self, 
                *, 
                hot_cache_period: Optional[timedelta] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kusto.models.ReadWriteDatabase(Database, discriminator='ReadWrite'):
        id: str
        kind: Literal[Kind.READ_WRITE]
        location: str
        name: str
        properties: Optional[ReadWriteDatabaseProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[ReadWriteDatabaseProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.kusto.models.ReadWriteDatabaseProperties(_Model):
        hot_cache_period: Optional[timedelta]
        is_followed: Optional[bool]
        key_vault_properties: Optional[KeyVaultProperties]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        soft_delete_period: Optional[timedelta]
        statistics: Optional[DatabaseStatistics]
        suspension_details: Optional[SuspensionDetails]

        @overload
        def __init__(
                self, 
                *, 
                hot_cache_period: Optional[timedelta] = ..., 
                key_vault_properties: Optional[KeyVaultProperties] = ..., 
                soft_delete_period: Optional[timedelta] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kusto.models.Reason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALREADY_EXISTS = "AlreadyExists"
        INVALID = "Invalid"


    class azure.mgmt.kusto.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.kusto.models.ResourceSkuCapabilities(_Model):
        name: Optional[str]
        value: Optional[str]


    class azure.mgmt.kusto.models.ResourceSkuZoneDetails(_Model):
        capabilities: Optional[list[ResourceSkuCapabilities]]
        name: Optional[list[str]]


    class azure.mgmt.kusto.models.SandboxCustomImage(ProxyResource):
        id: str
        name: str
        properties: Optional[SandboxCustomImageProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SandboxCustomImageProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.kusto.models.SandboxCustomImageProperties(_Model):
        base_image_name: Optional[str]
        language: Union[str, Language]
        language_version: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        requirements_file_content: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                base_image_name: Optional[str] = ..., 
                language: Union[str, Language], 
                language_version: Optional[str] = ..., 
                requirements_file_content: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kusto.models.SandboxCustomImagesCheckNameRequest(_Model):
        name: str
        type: Literal["Kusto/clusters/sandboxCustomImages"]

        @overload
        def __init__(
                self, 
                *, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kusto.models.Script(ProxyResource):
        id: str
        name: str
        properties: Optional[ScriptProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ScriptProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.kusto.models.ScriptCheckNameRequest(_Model):
        name: str
        type: Literal["Kusto/clusters/databases/scripts"]

        @overload
        def __init__(
                self, 
                *, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kusto.models.ScriptLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLUSTER = "Cluster"
        DATABASE = "Database"


    class azure.mgmt.kusto.models.ScriptProperties(_Model):
        continue_on_errors: Optional[bool]
        force_update_tag: Optional[str]
        managed_identity_resource_id: Optional[str]
        principal_permissions_action: Optional[Union[str, PrincipalPermissionsAction]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        script_content: Optional[str]
        script_level: Optional[Union[str, ScriptLevel]]
        script_url: Optional[str]
        script_url_sas_token: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                continue_on_errors: Optional[bool] = ..., 
                force_update_tag: Optional[str] = ..., 
                managed_identity_resource_id: Optional[str] = ..., 
                principal_permissions_action: Optional[Union[str, PrincipalPermissionsAction]] = ..., 
                script_content: Optional[str] = ..., 
                script_level: Optional[Union[str, ScriptLevel]] = ..., 
                script_url: Optional[str] = ..., 
                script_url_sas_token: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kusto.models.SkuDescription(_Model):
        location_info: Optional[list[SkuLocationInfoItem]]
        locations: Optional[list[str]]
        name: Optional[str]
        resource_type: Optional[str]
        restrictions: Optional[list[Any]]
        tier: Optional[str]


    class azure.mgmt.kusto.models.SkuLocationInfoItem(_Model):
        location: str
        zone_details: Optional[list[ResourceSkuZoneDetails]]
        zones: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                zone_details: Optional[list[ResourceSkuZoneDetails]] = ..., 
                zones: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.kusto.models.SuspensionDetails(_Model):
        suspension_start_date: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                suspension_start_date: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kusto.models.SystemData(_Model):
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


    class azure.mgmt.kusto.models.TableLevelSharingProperties(_Model):
        external_tables_to_exclude: Optional[list[str]]
        external_tables_to_include: Optional[list[str]]
        functions_to_exclude: Optional[list[str]]
        functions_to_include: Optional[list[str]]
        materialized_views_to_exclude: Optional[list[str]]
        materialized_views_to_include: Optional[list[str]]
        tables_to_exclude: Optional[list[str]]
        tables_to_include: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                external_tables_to_exclude: Optional[list[str]] = ..., 
                external_tables_to_include: Optional[list[str]] = ..., 
                functions_to_exclude: Optional[list[str]] = ..., 
                functions_to_include: Optional[list[str]] = ..., 
                materialized_views_to_exclude: Optional[list[str]] = ..., 
                materialized_views_to_include: Optional[list[str]] = ..., 
                tables_to_exclude: Optional[list[str]] = ..., 
                tables_to_include: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kusto.models.TrackedResource(Resource):
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


    class azure.mgmt.kusto.models.TrustedExternalTenant(_Model):
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kusto.models.Type(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MICROSOFT_KUSTO_CLUSTERS_ATTACHED_DATABASE_CONFIGURATIONS = "Microsoft.Kusto/clusters/attachedDatabaseConfigurations"
        MICROSOFT_KUSTO_CLUSTERS_DATABASES = "Microsoft.Kusto/clusters/databases"


    class azure.mgmt.kusto.models.VirtualNetworkConfiguration(_Model):
        data_management_public_ip_id: str
        engine_public_ip_id: str
        state: Optional[Union[str, VnetState]]
        subnet_id: str

        @overload
        def __init__(
                self, 
                *, 
                data_management_public_ip_id: str, 
                engine_public_ip_id: str, 
                state: Optional[Union[str, VnetState]] = ..., 
                subnet_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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
            ) -> None: ...

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
                parameters: JSON, 
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
                resource_name: JSON, 
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
            ) -> ItemPaged[AttachedDatabaseConfiguration]: ...


    class azure.mgmt.kusto.operations.ClusterPrincipalAssignmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                parameters: JSON, 
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
                principal_assignment_name: JSON, 
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
            ) -> ItemPaged[ClusterPrincipalAssignment]: ...


    class azure.mgmt.kusto.operations.ClustersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                callout_policies: JSON, 
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
                language_extensions_to_add: JSON, 
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
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
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
                follower_database_to_remove: JSON, 
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
                cluster_migrate_request: JSON, 
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
                callout_policy: JSON, 
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
                language_extensions_to_remove: JSON, 
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
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
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
                cluster_name: JSON, 
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
        def list(self, **kwargs: Any) -> ItemPaged[Cluster]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Cluster]: ...

        @distributed_trace
        def list_callout_policies(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ItemPaged[CalloutPolicy]: ...

        @distributed_trace
        def list_follower_databases(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ItemPaged[FollowerDatabaseDefinition]: ...

        @distributed_trace
        def list_follower_databases_get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ItemPaged[FollowerDatabaseDefinitionGet]: ...

        @distributed_trace
        def list_language_extensions(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ItemPaged[LanguageExtension]: ...

        @distributed_trace
        def list_outbound_network_dependencies_endpoints(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ItemPaged[OutboundNetworkDependenciesEndpoint]: ...

        @distributed_trace
        def list_skus(self, **kwargs: Any) -> ItemPaged[SkuDescription]: ...

        @distributed_trace
        def list_skus_by_resource(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AzureResourceSku]: ...


    class azure.mgmt.kusto.operations.DataConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                parameters: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                data_connection_name: JSON, 
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
            ) -> ItemPaged[DataConnection]: ...


    class azure.mgmt.kusto.operations.DatabaseOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                parameters: JSON, 
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
            ) -> None: ...

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
                parameters: JSON, 
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
                principal_assignment_name: JSON, 
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
            ) -> ItemPaged[DatabasePrincipalAssignment]: ...


    class azure.mgmt.kusto.operations.DatabasesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                database_principals_to_add: JSON, 
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
                *, 
                caller_role: Optional[Union[str, CallerRole]] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Database]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                parameters: JSON, 
                *, 
                caller_role: Optional[Union[str, CallerRole]] = ..., 
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
                *, 
                caller_role: Optional[Union[str, CallerRole]] = ..., 
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
                *, 
                caller_role: Optional[Union[str, CallerRole]] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Database]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                parameters: JSON, 
                *, 
                caller_role: Optional[Union[str, CallerRole]] = ..., 
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
                *, 
                caller_role: Optional[Union[str, CallerRole]] = ..., 
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
                resource_name: JSON, 
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
                *, 
                skiptoken: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Database]: ...

        @distributed_trace
        def list_principals(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DatabasePrincipal]: ...

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
                database_principals_to_remove: JSON, 
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
            ) -> None: ...

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
                parameters: JSON, 
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
                parameters: JSON, 
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
                resource_name: JSON, 
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
            ) -> ItemPaged[ManagedPrivateEndpoint]: ...


    class azure.mgmt.kusto.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.kusto.operations.OperationsResultsLocationOperations:

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
            ) -> None: ...


    class azure.mgmt.kusto.operations.OperationsResultsOperations:

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
            ) -> OperationResult: ...


    class azure.mgmt.kusto.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                parameters: JSON, 
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
            ) -> ItemPaged[PrivateEndpointConnection]: ...


    class azure.mgmt.kusto.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
            ) -> ItemPaged[PrivateLinkResource]: ...


    class azure.mgmt.kusto.operations.SandboxCustomImagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                parameters: JSON, 
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
                parameters: JSON, 
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
                resource_name: JSON, 
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
            ) -> ItemPaged[SandboxCustomImage]: ...


    class azure.mgmt.kusto.operations.ScriptsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                parameters: JSON, 
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
                parameters: JSON, 
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
                script_name: JSON, 
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
            ) -> ItemPaged[Script]: ...


    class azure.mgmt.kusto.operations.SkusOperations:

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
            ) -> ItemPaged[SkuDescription]: ...


```