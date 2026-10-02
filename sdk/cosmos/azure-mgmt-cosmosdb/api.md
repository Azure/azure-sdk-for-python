```py
namespace azure.mgmt.cosmosdb

    class azure.mgmt.cosmosdb.CosmosDBManagementClient: implements ContextManager 
        cassandra_clusters: CassandraClustersOperations
        cassandra_data_centers: CassandraDataCentersOperations
        cassandra_resources: CassandraResourcesOperations
        chaos_fault: ChaosFaultOperations
        collection: CollectionOperations
        collection_partition: CollectionPartitionOperations
        collection_partition_region: CollectionPartitionRegionOperations
        collection_region: CollectionRegionOperations
        copy_jobs: CopyJobsOperations
        data_transfer_jobs: DataTransferJobsOperations
        database: DatabaseOperations
        database_account_region: DatabaseAccountRegionOperations
        database_accounts: DatabaseAccountsOperations
        fleet: FleetOperations
        fleet_analytics: FleetAnalyticsOperations
        fleetspace: FleetspaceOperations
        fleetspace_account: FleetspaceAccountOperations
        garnet_clusters: GarnetClustersOperations
        graph_resources: GraphResourcesOperations
        gremlin_resources: GremlinResourcesOperations
        locations: LocationsOperations
        mongo_db_resources: MongoDBResourcesOperations
        mongo_mi_resources: MongoMIResourcesOperations
        network_security_perimeter_configurations: NetworkSecurityPerimeterConfigurationsOperations
        notebook_workspaces: NotebookWorkspacesOperations
        operations: Operations
        partition_key_range_id: PartitionKeyRangeIdOperations
        partition_key_range_id_region: PartitionKeyRangeIdRegionOperations
        percentile: PercentileOperations
        percentile_source_target: PercentileSourceTargetOperations
        percentile_target: PercentileTargetOperations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        restorable_database_accounts: RestorableDatabaseAccountsOperations
        restorable_gremlin_databases: RestorableGremlinDatabasesOperations
        restorable_gremlin_graphs: RestorableGremlinGraphsOperations
        restorable_gremlin_resources: RestorableGremlinResourcesOperations
        restorable_mongodb_collections: RestorableMongodbCollectionsOperations
        restorable_mongodb_databases: RestorableMongodbDatabasesOperations
        restorable_mongodb_resources: RestorableMongodbResourcesOperations
        restorable_sql_containers: RestorableSqlContainersOperations
        restorable_sql_databases: RestorableSqlDatabasesOperations
        restorable_sql_resources: RestorableSqlResourcesOperations
        restorable_table_resources: RestorableTableResourcesOperations
        restorable_tables: RestorableTablesOperations
        service: ServiceOperations
        soft_deleted_database_accounts: SoftDeletedDatabaseAccountsOperations
        soft_deleted_sql_containers: SoftDeletedSqlContainersOperations
        soft_deleted_sql_databases: SoftDeletedSqlDatabasesOperations
        sql_resources: SqlResourcesOperations
        table_resources: TableResourcesOperations
        throughput_pool: ThroughputPoolOperations
        throughput_pool_account: ThroughputPoolAccountOperations
        throughput_pool_accounts: ThroughputPoolAccountsOperations
        throughput_pools: ThroughputPoolsOperations

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


namespace azure.mgmt.cosmosdb.aio

    class azure.mgmt.cosmosdb.aio.CosmosDBManagementClient: implements AsyncContextManager 
        cassandra_clusters: CassandraClustersOperations
        cassandra_data_centers: CassandraDataCentersOperations
        cassandra_resources: CassandraResourcesOperations
        chaos_fault: ChaosFaultOperations
        collection: CollectionOperations
        collection_partition: CollectionPartitionOperations
        collection_partition_region: CollectionPartitionRegionOperations
        collection_region: CollectionRegionOperations
        copy_jobs: CopyJobsOperations
        data_transfer_jobs: DataTransferJobsOperations
        database: DatabaseOperations
        database_account_region: DatabaseAccountRegionOperations
        database_accounts: DatabaseAccountsOperations
        fleet: FleetOperations
        fleet_analytics: FleetAnalyticsOperations
        fleetspace: FleetspaceOperations
        fleetspace_account: FleetspaceAccountOperations
        garnet_clusters: GarnetClustersOperations
        graph_resources: GraphResourcesOperations
        gremlin_resources: GremlinResourcesOperations
        locations: LocationsOperations
        mongo_db_resources: MongoDBResourcesOperations
        mongo_mi_resources: MongoMIResourcesOperations
        network_security_perimeter_configurations: NetworkSecurityPerimeterConfigurationsOperations
        notebook_workspaces: NotebookWorkspacesOperations
        operations: Operations
        partition_key_range_id: PartitionKeyRangeIdOperations
        partition_key_range_id_region: PartitionKeyRangeIdRegionOperations
        percentile: PercentileOperations
        percentile_source_target: PercentileSourceTargetOperations
        percentile_target: PercentileTargetOperations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        restorable_database_accounts: RestorableDatabaseAccountsOperations
        restorable_gremlin_databases: RestorableGremlinDatabasesOperations
        restorable_gremlin_graphs: RestorableGremlinGraphsOperations
        restorable_gremlin_resources: RestorableGremlinResourcesOperations
        restorable_mongodb_collections: RestorableMongodbCollectionsOperations
        restorable_mongodb_databases: RestorableMongodbDatabasesOperations
        restorable_mongodb_resources: RestorableMongodbResourcesOperations
        restorable_sql_containers: RestorableSqlContainersOperations
        restorable_sql_databases: RestorableSqlDatabasesOperations
        restorable_sql_resources: RestorableSqlResourcesOperations
        restorable_table_resources: RestorableTableResourcesOperations
        restorable_tables: RestorableTablesOperations
        service: ServiceOperations
        soft_deleted_database_accounts: SoftDeletedDatabaseAccountsOperations
        soft_deleted_sql_containers: SoftDeletedSqlContainersOperations
        soft_deleted_sql_databases: SoftDeletedSqlDatabasesOperations
        sql_resources: SqlResourcesOperations
        table_resources: TableResourcesOperations
        throughput_pool: ThroughputPoolOperations
        throughput_pool_account: ThroughputPoolAccountOperations
        throughput_pool_accounts: ThroughputPoolAccountsOperations
        throughput_pools: ThroughputPoolsOperations

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


namespace azure.mgmt.cosmosdb.aio.operations

    class azure.mgmt.cosmosdb.aio.operations.CassandraClustersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: ClusterResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ClusterResource]: ...

        @overload
        async def begin_create_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: ClusterResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ClusterResource]: ...

        @overload
        async def begin_create_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ClusterResource]: ...

        @distributed_trace_async
        async def begin_deallocate(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                *, 
                x_ms_force_deallocate: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_invoke_command(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: CommandPostBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommandOutput]: ...

        @overload
        async def begin_invoke_command(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: CommandPostBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommandOutput]: ...

        @overload
        async def begin_invoke_command(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommandOutput]: ...

        @overload
        async def begin_invoke_command_async(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: CommandAsyncPostBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommandPublicResource]: ...

        @overload
        async def begin_invoke_command_async(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: CommandAsyncPostBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommandPublicResource]: ...

        @overload
        async def begin_invoke_command_async(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommandPublicResource]: ...

        @distributed_trace_async
        async def begin_start(
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
                body: ClusterResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ClusterResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: ClusterResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ClusterResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ClusterResource]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ClusterResource: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'cluster_name', 'backup_id', 'accept']}, api_versions_list=['2026-04-01-preview'])
        async def get_backup(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                backup_id: str, 
                **kwargs: Any
            ) -> BackupResource: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'cluster_name', 'command_id', 'accept']}, api_versions_list=['2026-04-01-preview'])
        async def get_command_async(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                command_id: str, 
                **kwargs: Any
            ) -> CommandPublicResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'cluster_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        def list_backups(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[BackupResource]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ClusterResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[ClusterResource]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'cluster_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        def list_command(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[CommandPublicResource]: ...

        @distributed_trace_async
        async def status(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> CassandraClusterPublicStatus: ...


    class azure.mgmt.cosmosdb.aio.operations.CassandraDataCentersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                data_center_name: str, 
                body: DataCenterResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DataCenterResource]: ...

        @overload
        async def begin_create_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                data_center_name: str, 
                body: DataCenterResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DataCenterResource]: ...

        @overload
        async def begin_create_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                data_center_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DataCenterResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                data_center_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                data_center_name: str, 
                body: DataCenterResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DataCenterResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                data_center_name: str, 
                body: DataCenterResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DataCenterResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                data_center_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DataCenterResource]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                data_center_name: str, 
                **kwargs: Any
            ) -> DataCenterResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DataCenterResource]: ...


    class azure.mgmt.cosmosdb.aio.operations.CassandraResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_update_cassandra_keyspace(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                create_update_cassandra_keyspace_parameters: CassandraKeyspaceCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CassandraKeyspaceGetResults]: ...

        @overload
        async def begin_create_update_cassandra_keyspace(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                create_update_cassandra_keyspace_parameters: CassandraKeyspaceCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CassandraKeyspaceGetResults]: ...

        @overload
        async def begin_create_update_cassandra_keyspace(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                create_update_cassandra_keyspace_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CassandraKeyspaceGetResults]: ...

        @overload
        async def begin_create_update_cassandra_role_assignment(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_assignment_id: str, 
                create_update_cassandra_role_assignment_parameters: CassandraRoleAssignmentResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CassandraRoleAssignmentResource]: ...

        @overload
        async def begin_create_update_cassandra_role_assignment(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_assignment_id: str, 
                create_update_cassandra_role_assignment_parameters: CassandraRoleAssignmentResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CassandraRoleAssignmentResource]: ...

        @overload
        async def begin_create_update_cassandra_role_assignment(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_assignment_id: str, 
                create_update_cassandra_role_assignment_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CassandraRoleAssignmentResource]: ...

        @overload
        async def begin_create_update_cassandra_role_definition(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_definition_id: str, 
                create_update_cassandra_role_definition_parameters: CassandraRoleDefinitionResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CassandraRoleDefinitionResource]: ...

        @overload
        async def begin_create_update_cassandra_role_definition(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_definition_id: str, 
                create_update_cassandra_role_definition_parameters: CassandraRoleDefinitionResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CassandraRoleDefinitionResource]: ...

        @overload
        async def begin_create_update_cassandra_role_definition(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_definition_id: str, 
                create_update_cassandra_role_definition_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CassandraRoleDefinitionResource]: ...

        @overload
        async def begin_create_update_cassandra_table(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                table_name: str, 
                create_update_cassandra_table_parameters: CassandraTableCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CassandraTableGetResults]: ...

        @overload
        async def begin_create_update_cassandra_table(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                table_name: str, 
                create_update_cassandra_table_parameters: CassandraTableCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CassandraTableGetResults]: ...

        @overload
        async def begin_create_update_cassandra_table(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                table_name: str, 
                create_update_cassandra_table_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CassandraTableGetResults]: ...

        @overload
        async def begin_create_update_cassandra_view(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                view_name: str, 
                create_update_cassandra_view_parameters: CassandraViewCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CassandraViewGetResults]: ...

        @overload
        async def begin_create_update_cassandra_view(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                view_name: str, 
                create_update_cassandra_view_parameters: CassandraViewCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CassandraViewGetResults]: ...

        @overload
        async def begin_create_update_cassandra_view(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                view_name: str, 
                create_update_cassandra_view_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CassandraViewGetResults]: ...

        @distributed_trace_async
        async def begin_delete_cassandra_keyspace(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_delete_cassandra_role_assignment(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_assignment_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_delete_cassandra_role_definition(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_definition_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_delete_cassandra_table(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                table_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_delete_cassandra_view(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                view_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_migrate_cassandra_keyspace_to_autoscale(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ThroughputSettingsGetResults]: ...

        @distributed_trace_async
        async def begin_migrate_cassandra_keyspace_to_manual_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ThroughputSettingsGetResults]: ...

        @distributed_trace_async
        async def begin_migrate_cassandra_table_to_autoscale(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                table_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ThroughputSettingsGetResults]: ...

        @distributed_trace_async
        async def begin_migrate_cassandra_table_to_manual_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                table_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ThroughputSettingsGetResults]: ...

        @distributed_trace_async
        async def begin_migrate_cassandra_view_to_autoscale(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                view_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ThroughputSettingsGetResults]: ...

        @distributed_trace_async
        async def begin_migrate_cassandra_view_to_manual_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                view_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ThroughputSettingsGetResults]: ...

        @overload
        async def begin_update_cassandra_keyspace_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                update_throughput_parameters: ThroughputSettingsUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ThroughputSettingsGetResults]: ...

        @overload
        async def begin_update_cassandra_keyspace_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                update_throughput_parameters: ThroughputSettingsUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ThroughputSettingsGetResults]: ...

        @overload
        async def begin_update_cassandra_keyspace_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                update_throughput_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ThroughputSettingsGetResults]: ...

        @overload
        async def begin_update_cassandra_table_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                table_name: str, 
                update_throughput_parameters: ThroughputSettingsUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ThroughputSettingsGetResults]: ...

        @overload
        async def begin_update_cassandra_table_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                table_name: str, 
                update_throughput_parameters: ThroughputSettingsUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ThroughputSettingsGetResults]: ...

        @overload
        async def begin_update_cassandra_table_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                table_name: str, 
                update_throughput_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ThroughputSettingsGetResults]: ...

        @overload
        async def begin_update_cassandra_view_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                view_name: str, 
                update_throughput_parameters: ThroughputSettingsUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ThroughputSettingsGetResults]: ...

        @overload
        async def begin_update_cassandra_view_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                view_name: str, 
                update_throughput_parameters: ThroughputSettingsUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ThroughputSettingsGetResults]: ...

        @overload
        async def begin_update_cassandra_view_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                view_name: str, 
                update_throughput_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ThroughputSettingsGetResults]: ...

        @distributed_trace_async
        async def get_cassandra_keyspace(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                **kwargs: Any
            ) -> CassandraKeyspaceGetResults: ...

        @distributed_trace_async
        async def get_cassandra_keyspace_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                **kwargs: Any
            ) -> ThroughputSettingsGetResults: ...

        @distributed_trace_async
        async def get_cassandra_role_assignment(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_assignment_id: str, 
                **kwargs: Any
            ) -> CassandraRoleAssignmentResource: ...

        @distributed_trace_async
        async def get_cassandra_role_definition(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_definition_id: str, 
                **kwargs: Any
            ) -> CassandraRoleDefinitionResource: ...

        @distributed_trace_async
        async def get_cassandra_table(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                table_name: str, 
                **kwargs: Any
            ) -> CassandraTableGetResults: ...

        @distributed_trace_async
        async def get_cassandra_table_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                table_name: str, 
                **kwargs: Any
            ) -> ThroughputSettingsGetResults: ...

        @distributed_trace_async
        async def get_cassandra_view(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                view_name: str, 
                **kwargs: Any
            ) -> CassandraViewGetResults: ...

        @distributed_trace_async
        async def get_cassandra_view_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                view_name: str, 
                **kwargs: Any
            ) -> ThroughputSettingsGetResults: ...

        @distributed_trace
        def list_cassandra_keyspaces(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[CassandraKeyspaceGetResults]: ...

        @distributed_trace
        def list_cassandra_role_assignments(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[CassandraRoleAssignmentResource]: ...

        @distributed_trace
        def list_cassandra_role_definitions(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[CassandraRoleDefinitionResource]: ...

        @distributed_trace
        def list_cassandra_tables(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[CassandraTableGetResults]: ...

        @distributed_trace
        def list_cassandra_views(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[CassandraViewGetResults]: ...


    class azure.mgmt.cosmosdb.aio.operations.ChaosFaultOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_enable_disable(
                self, 
                resource_group_name: str, 
                account_name: str, 
                chaos_fault: str, 
                chaos_fault_request: ChaosFaultResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ChaosFaultResource]: ...

        @overload
        async def begin_enable_disable(
                self, 
                resource_group_name: str, 
                account_name: str, 
                chaos_fault: str, 
                chaos_fault_request: ChaosFaultResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ChaosFaultResource]: ...

        @overload
        async def begin_enable_disable(
                self, 
                resource_group_name: str, 
                account_name: str, 
                chaos_fault: str, 
                chaos_fault_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ChaosFaultResource]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                chaos_fault: str, 
                **kwargs: Any
            ) -> ChaosFaultResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ChaosFaultResource]: ...


    class azure.mgmt.cosmosdb.aio.operations.CollectionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_metric_definitions(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_rid: str, 
                collection_rid: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[MetricDefinition]: ...

        @distributed_trace
        def list_metrics(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_rid: str, 
                collection_rid: str, 
                *, 
                filter: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Metric]: ...

        @distributed_trace
        def list_usages(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_rid: str, 
                collection_rid: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Usage]: ...


    class azure.mgmt.cosmosdb.aio.operations.CollectionPartitionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_metrics(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_rid: str, 
                collection_rid: str, 
                *, 
                filter: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PartitionMetric]: ...

        @distributed_trace
        def list_usages(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_rid: str, 
                collection_rid: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[PartitionUsage]: ...


    class azure.mgmt.cosmosdb.aio.operations.CollectionPartitionRegionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_metrics(
                self, 
                resource_group_name: str, 
                account_name: str, 
                region: str, 
                database_rid: str, 
                collection_rid: str, 
                *, 
                filter: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PartitionMetric]: ...


    class azure.mgmt.cosmosdb.aio.operations.CollectionRegionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_metrics(
                self, 
                resource_group_name: str, 
                account_name: str, 
                region: str, 
                database_rid: str, 
                collection_rid: str, 
                *, 
                filter: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Metric]: ...


    class azure.mgmt.cosmosdb.aio.operations.CopyJobsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'job_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        async def cancel(
                self, 
                resource_group_name: str, 
                account_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> CopyJobGetResults: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'job_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        async def complete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> CopyJobGetResults: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                job_name: str, 
                job_create_parameters: CopyJobGetResults, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CopyJobGetResults: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                job_name: str, 
                job_create_parameters: CopyJobGetResults, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CopyJobGetResults: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                job_name: str, 
                job_create_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CopyJobGetResults: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'job_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> CopyJobGetResults: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        def list_by_database_account(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[CopyJobGetResults]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'job_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        async def pause(
                self, 
                resource_group_name: str, 
                account_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> CopyJobGetResults: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'job_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        async def resume(
                self, 
                resource_group_name: str, 
                account_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> CopyJobGetResults: ...


    class azure.mgmt.cosmosdb.aio.operations.DataTransferJobsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'job_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        async def cancel(
                self, 
                resource_group_name: str, 
                account_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> DataTransferJobGetResults: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'job_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        async def complete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> DataTransferJobGetResults: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                job_name: str, 
                job_create_parameters: CreateJobRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataTransferJobGetResults: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                job_name: str, 
                job_create_parameters: CreateJobRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataTransferJobGetResults: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                job_name: str, 
                job_create_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataTransferJobGetResults: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'job_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> DataTransferJobGetResults: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        def list_by_database_account(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DataTransferJobGetResults]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'job_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        async def pause(
                self, 
                resource_group_name: str, 
                account_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> DataTransferJobGetResults: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'job_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        async def resume(
                self, 
                resource_group_name: str, 
                account_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> DataTransferJobGetResults: ...


    class azure.mgmt.cosmosdb.aio.operations.DatabaseAccountRegionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_metrics(
                self, 
                resource_group_name: str, 
                account_name: str, 
                region: str, 
                *, 
                filter: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Metric]: ...


    class azure.mgmt.cosmosdb.aio.operations.DatabaseAccountsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                create_update_parameters: DatabaseAccountCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DatabaseAccountGetResults]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                create_update_parameters: DatabaseAccountCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DatabaseAccountGetResults]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                create_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DatabaseAccountGetResults]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_failover_priority_change(
                self, 
                resource_group_name: str, 
                account_name: str, 
                failover_parameters: FailoverPolicies, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_failover_priority_change(
                self, 
                resource_group_name: str, 
                account_name: str, 
                failover_parameters: FailoverPolicies, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_failover_priority_change(
                self, 
                resource_group_name: str, 
                account_name: str, 
                failover_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_offline_region(
                self, 
                resource_group_name: str, 
                account_name: str, 
                region_parameter_for_offline: RegionForOnlineOffline, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_offline_region(
                self, 
                resource_group_name: str, 
                account_name: str, 
                region_parameter_for_offline: RegionForOnlineOffline, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_offline_region(
                self, 
                resource_group_name: str, 
                account_name: str, 
                region_parameter_for_offline: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_online_region(
                self, 
                resource_group_name: str, 
                account_name: str, 
                region_parameter_for_online: RegionForOnlineOffline, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_online_region(
                self, 
                resource_group_name: str, 
                account_name: str, 
                region_parameter_for_online: RegionForOnlineOffline, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_online_region(
                self, 
                resource_group_name: str, 
                account_name: str, 
                region_parameter_for_online: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_regenerate_key(
                self, 
                resource_group_name: str, 
                account_name: str, 
                key_to_regenerate: DatabaseAccountRegenerateKeyParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_regenerate_key(
                self, 
                resource_group_name: str, 
                account_name: str, 
                key_to_regenerate: DatabaseAccountRegenerateKeyParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_regenerate_key(
                self, 
                resource_group_name: str, 
                account_name: str, 
                key_to_regenerate: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                update_parameters: DatabaseAccountUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DatabaseAccountGetResults]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                update_parameters: DatabaseAccountUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DatabaseAccountGetResults]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DatabaseAccountGetResults]: ...

        @distributed_trace_async
        async def check_name_exists(
                self, 
                account_name: str, 
                **kwargs: Any
            ) -> bool: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> DatabaseAccountGetResults: ...

        @distributed_trace_async
        async def get_read_only_keys(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> DatabaseAccountListReadOnlyKeysResult: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[DatabaseAccountGetResults]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DatabaseAccountGetResults]: ...

        @distributed_trace_async
        async def list_connection_strings(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> DatabaseAccountListConnectionStringsResult: ...

        @distributed_trace_async
        async def list_keys(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> DatabaseAccountListKeysResult: ...

        @distributed_trace
        def list_metric_definitions(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[MetricDefinition]: ...

        @distributed_trace
        def list_metrics(
                self, 
                resource_group_name: str, 
                account_name: str, 
                *, 
                filter: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Metric]: ...

        @distributed_trace_async
        async def list_read_only_keys(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> DatabaseAccountListReadOnlyKeysResult: ...

        @distributed_trace
        def list_usages(
                self, 
                resource_group_name: str, 
                account_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Usage]: ...


    class azure.mgmt.cosmosdb.aio.operations.DatabaseOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_metric_definitions(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_rid: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[MetricDefinition]: ...

        @distributed_trace
        def list_metrics(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_rid: str, 
                *, 
                filter: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Metric]: ...

        @distributed_trace
        def list_usages(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_rid: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Usage]: ...


    class azure.mgmt.cosmosdb.aio.operations.FleetAnalyticsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                fleet_analytics_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                fleet_analytics_name: str, 
                body: FleetAnalyticsResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FleetAnalyticsResource: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                fleet_analytics_name: str, 
                body: FleetAnalyticsResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FleetAnalyticsResource: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                fleet_analytics_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FleetAnalyticsResource: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                fleet_analytics_name: str, 
                **kwargs: Any
            ) -> FleetAnalyticsResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[FleetAnalyticsResource]: ...


    class azure.mgmt.cosmosdb.aio.operations.FleetOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                body: FleetResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FleetResource: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                body: FleetResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FleetResource: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FleetResource: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                **kwargs: Any
            ) -> FleetResource: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[FleetResource]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[FleetResource]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                body: FleetResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FleetResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                body: FleetResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FleetResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FleetResource: ...


    class azure.mgmt.cosmosdb.aio.operations.FleetspaceAccountOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                fleetspace_name: str, 
                fleetspace_account_name: str, 
                body: FleetspaceAccountResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FleetspaceAccountResource]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                fleetspace_name: str, 
                fleetspace_account_name: str, 
                body: FleetspaceAccountResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FleetspaceAccountResource]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                fleetspace_name: str, 
                fleetspace_account_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FleetspaceAccountResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                fleetspace_name: str, 
                fleetspace_account_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                fleetspace_name: str, 
                fleetspace_account_name: str, 
                **kwargs: Any
            ) -> FleetspaceAccountResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                fleetspace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[FleetspaceAccountResource]: ...


    class azure.mgmt.cosmosdb.aio.operations.FleetspaceOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                fleetspace_name: str, 
                body: FleetspaceResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FleetspaceResource]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                fleetspace_name: str, 
                body: FleetspaceResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FleetspaceResource]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                fleetspace_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FleetspaceResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                fleetspace_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                fleetspace_name: str, 
                body: Optional[FleetspaceUpdate] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FleetspaceResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                fleetspace_name: str, 
                body: Optional[FleetspaceUpdate] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FleetspaceResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                fleetspace_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FleetspaceResource]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                fleetspace_name: str, 
                **kwargs: Any
            ) -> FleetspaceResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[FleetspaceResource]: ...


    class azure.mgmt.cosmosdb.aio.operations.GarnetClustersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: GarnetClusterResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GarnetClusterResource]: ...

        @overload
        async def begin_create_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: GarnetClusterResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GarnetClusterResource]: ...

        @overload
        async def begin_create_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GarnetClusterResource]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'cluster_name']}, api_versions_list=['2026-04-01-preview'])
        async def begin_delete(
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
                body: GarnetClusterResourcePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GarnetClusterResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: GarnetClusterResourcePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GarnetClusterResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GarnetClusterResource]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'cluster_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> GarnetClusterResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[GarnetClusterResource]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2026-04-01-preview'])
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[GarnetClusterResource]: ...


    class azure.mgmt.cosmosdb.aio.operations.GraphResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_update_graph(
                self, 
                resource_group_name: str, 
                account_name: str, 
                graph_name: str, 
                create_update_graph_parameters: GraphResourceCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GraphResourceGetResults]: ...

        @overload
        async def begin_create_update_graph(
                self, 
                resource_group_name: str, 
                account_name: str, 
                graph_name: str, 
                create_update_graph_parameters: GraphResourceCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GraphResourceGetResults]: ...

        @overload
        async def begin_create_update_graph(
                self, 
                resource_group_name: str, 
                account_name: str, 
                graph_name: str, 
                create_update_graph_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GraphResourceGetResults]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'graph_name']}, api_versions_list=['2026-04-01-preview'])
        async def begin_delete_graph_resource(
                self, 
                resource_group_name: str, 
                account_name: str, 
                graph_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'graph_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        async def get_graph(
                self, 
                resource_group_name: str, 
                account_name: str, 
                graph_name: str, 
                **kwargs: Any
            ) -> GraphResourceGetResults: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        def list_graphs(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[GraphResourceGetResults]: ...


    class azure.mgmt.cosmosdb.aio.operations.GremlinResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_update_gremlin_database(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                create_update_gremlin_database_parameters: GremlinDatabaseCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GremlinDatabaseGetResults]: ...

        @overload
        async def begin_create_update_gremlin_database(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                create_update_gremlin_database_parameters: GremlinDatabaseCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GremlinDatabaseGetResults]: ...

        @overload
        async def begin_create_update_gremlin_database(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                create_update_gremlin_database_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GremlinDatabaseGetResults]: ...

        @overload
        async def begin_create_update_gremlin_graph(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                graph_name: str, 
                create_update_gremlin_graph_parameters: GremlinGraphCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GremlinGraphGetResults]: ...

        @overload
        async def begin_create_update_gremlin_graph(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                graph_name: str, 
                create_update_gremlin_graph_parameters: GremlinGraphCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GremlinGraphGetResults]: ...

        @overload
        async def begin_create_update_gremlin_graph(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                graph_name: str, 
                create_update_gremlin_graph_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GremlinGraphGetResults]: ...

        @overload
        async def begin_create_update_gremlin_role_assignment(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_assignment_id: str, 
                create_update_gremlin_role_assignment_parameters: GremlinRoleAssignmentResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GremlinRoleAssignmentResource]: ...

        @overload
        async def begin_create_update_gremlin_role_assignment(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_assignment_id: str, 
                create_update_gremlin_role_assignment_parameters: GremlinRoleAssignmentResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GremlinRoleAssignmentResource]: ...

        @overload
        async def begin_create_update_gremlin_role_assignment(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_assignment_id: str, 
                create_update_gremlin_role_assignment_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GremlinRoleAssignmentResource]: ...

        @overload
        async def begin_create_update_gremlin_role_definition(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_definition_id: str, 
                create_update_gremlin_role_definition_parameters: GremlinRoleDefinitionResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GremlinRoleDefinitionResource]: ...

        @overload
        async def begin_create_update_gremlin_role_definition(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_definition_id: str, 
                create_update_gremlin_role_definition_parameters: GremlinRoleDefinitionResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GremlinRoleDefinitionResource]: ...

        @overload
        async def begin_create_update_gremlin_role_definition(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_definition_id: str, 
                create_update_gremlin_role_definition_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GremlinRoleDefinitionResource]: ...

        @distributed_trace_async
        async def begin_delete_gremlin_database(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_delete_gremlin_graph(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                graph_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_delete_gremlin_role_assignment(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_assignment_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_delete_gremlin_role_definition(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_definition_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_migrate_gremlin_database_to_autoscale(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ThroughputSettingsGetResults]: ...

        @distributed_trace_async
        async def begin_migrate_gremlin_database_to_manual_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ThroughputSettingsGetResults]: ...

        @distributed_trace_async
        async def begin_migrate_gremlin_graph_to_autoscale(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                graph_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ThroughputSettingsGetResults]: ...

        @distributed_trace_async
        async def begin_migrate_gremlin_graph_to_manual_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                graph_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ThroughputSettingsGetResults]: ...

        @overload
        async def begin_retrieve_continuous_backup_information(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                graph_name: str, 
                location: ContinuousBackupRestoreLocation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BackupInformation]: ...

        @overload
        async def begin_retrieve_continuous_backup_information(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                graph_name: str, 
                location: ContinuousBackupRestoreLocation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BackupInformation]: ...

        @overload
        async def begin_retrieve_continuous_backup_information(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                graph_name: str, 
                location: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BackupInformation]: ...

        @overload
        async def begin_update_gremlin_database_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                update_throughput_parameters: ThroughputSettingsUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ThroughputSettingsGetResults]: ...

        @overload
        async def begin_update_gremlin_database_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                update_throughput_parameters: ThroughputSettingsUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ThroughputSettingsGetResults]: ...

        @overload
        async def begin_update_gremlin_database_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                update_throughput_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ThroughputSettingsGetResults]: ...

        @overload
        async def begin_update_gremlin_graph_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                graph_name: str, 
                update_throughput_parameters: ThroughputSettingsUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ThroughputSettingsGetResults]: ...

        @overload
        async def begin_update_gremlin_graph_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                graph_name: str, 
                update_throughput_parameters: ThroughputSettingsUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ThroughputSettingsGetResults]: ...

        @overload
        async def begin_update_gremlin_graph_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                graph_name: str, 
                update_throughput_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ThroughputSettingsGetResults]: ...

        @distributed_trace_async
        async def get_gremlin_database(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> GremlinDatabaseGetResults: ...

        @distributed_trace_async
        async def get_gremlin_database_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> ThroughputSettingsGetResults: ...

        @distributed_trace_async
        async def get_gremlin_graph(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                graph_name: str, 
                **kwargs: Any
            ) -> GremlinGraphGetResults: ...

        @distributed_trace_async
        async def get_gremlin_graph_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                graph_name: str, 
                **kwargs: Any
            ) -> ThroughputSettingsGetResults: ...

        @distributed_trace_async
        async def get_gremlin_role_assignment(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_assignment_id: str, 
                **kwargs: Any
            ) -> GremlinRoleAssignmentResource: ...

        @distributed_trace_async
        async def get_gremlin_role_definition(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_definition_id: str, 
                **kwargs: Any
            ) -> GremlinRoleDefinitionResource: ...

        @distributed_trace
        def list_gremlin_databases(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[GremlinDatabaseGetResults]: ...

        @distributed_trace
        def list_gremlin_graphs(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[GremlinGraphGetResults]: ...

        @distributed_trace
        def list_gremlin_role_assignments(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[GremlinRoleAssignmentResource]: ...

        @distributed_trace
        def list_gremlin_role_definitions(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[GremlinRoleDefinitionResource]: ...


    class azure.mgmt.cosmosdb.aio.operations.LocationsOperations:

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
            ) -> LocationGetResult: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[LocationGetResult]: ...


    class azure.mgmt.cosmosdb.aio.operations.MongoDBResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_update_mongo_db_collection(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                collection_name: str, 
                create_update_mongo_db_collection_parameters: MongoDBCollectionCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MongoDBCollectionGetResults]: ...

        @overload
        async def begin_create_update_mongo_db_collection(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                collection_name: str, 
                create_update_mongo_db_collection_parameters: MongoDBCollectionCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MongoDBCollectionGetResults]: ...

        @overload
        async def begin_create_update_mongo_db_collection(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                collection_name: str, 
                create_update_mongo_db_collection_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MongoDBCollectionGetResults]: ...

        @overload
        async def begin_create_update_mongo_db_database(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                create_update_mongo_db_database_parameters: MongoDBDatabaseCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MongoDBDatabaseGetResults]: ...

        @overload
        async def begin_create_update_mongo_db_database(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                create_update_mongo_db_database_parameters: MongoDBDatabaseCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MongoDBDatabaseGetResults]: ...

        @overload
        async def begin_create_update_mongo_db_database(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                create_update_mongo_db_database_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MongoDBDatabaseGetResults]: ...

        @overload
        async def begin_create_update_mongo_role_definition(
                self, 
                mongo_role_definition_id: str, 
                resource_group_name: str, 
                account_name: str, 
                create_update_mongo_role_definition_parameters: MongoRoleDefinitionCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MongoRoleDefinitionGetResults]: ...

        @overload
        async def begin_create_update_mongo_role_definition(
                self, 
                mongo_role_definition_id: str, 
                resource_group_name: str, 
                account_name: str, 
                create_update_mongo_role_definition_parameters: MongoRoleDefinitionCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MongoRoleDefinitionGetResults]: ...

        @overload
        async def begin_create_update_mongo_role_definition(
                self, 
                mongo_role_definition_id: str, 
                resource_group_name: str, 
                account_name: str, 
                create_update_mongo_role_definition_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MongoRoleDefinitionGetResults]: ...

        @overload
        async def begin_create_update_mongo_user_definition(
                self, 
                mongo_user_definition_id: str, 
                resource_group_name: str, 
                account_name: str, 
                create_update_mongo_user_definition_parameters: MongoUserDefinitionCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MongoUserDefinitionGetResults]: ...

        @overload
        async def begin_create_update_mongo_user_definition(
                self, 
                mongo_user_definition_id: str, 
                resource_group_name: str, 
                account_name: str, 
                create_update_mongo_user_definition_parameters: MongoUserDefinitionCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MongoUserDefinitionGetResults]: ...

        @overload
        async def begin_create_update_mongo_user_definition(
                self, 
                mongo_user_definition_id: str, 
                resource_group_name: str, 
                account_name: str, 
                create_update_mongo_user_definition_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MongoUserDefinitionGetResults]: ...

        @distributed_trace_async
        async def begin_delete_mongo_db_collection(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                collection_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_delete_mongo_db_database(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_delete_mongo_role_definition(
                self, 
                mongo_role_definition_id: str, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_delete_mongo_user_definition(
                self, 
                mongo_user_definition_id: str, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_list_mongo_db_collection_partition_merge(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                collection_name: str, 
                merge_parameters: MergeParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PhysicalPartitionStorageInfoCollection]: ...

        @overload
        async def begin_list_mongo_db_collection_partition_merge(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                collection_name: str, 
                merge_parameters: MergeParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PhysicalPartitionStorageInfoCollection]: ...

        @overload
        async def begin_list_mongo_db_collection_partition_merge(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                collection_name: str, 
                merge_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PhysicalPartitionStorageInfoCollection]: ...

        @distributed_trace_async
        async def begin_migrate_mongo_db_collection_to_autoscale(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                collection_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ThroughputSettingsGetResults]: ...

        @distributed_trace_async
        async def begin_migrate_mongo_db_collection_to_manual_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                collection_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ThroughputSettingsGetResults]: ...

        @distributed_trace_async
        async def begin_migrate_mongo_db_database_to_autoscale(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ThroughputSettingsGetResults]: ...

        @distributed_trace_async
        async def begin_migrate_mongo_db_database_to_manual_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ThroughputSettingsGetResults]: ...

        @overload
        async def begin_mongo_db_container_redistribute_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                collection_name: str, 
                redistribute_throughput_parameters: RedistributeThroughputParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PhysicalPartitionThroughputInfoResult]: ...

        @overload
        async def begin_mongo_db_container_redistribute_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                collection_name: str, 
                redistribute_throughput_parameters: RedistributeThroughputParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PhysicalPartitionThroughputInfoResult]: ...

        @overload
        async def begin_mongo_db_container_redistribute_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                collection_name: str, 
                redistribute_throughput_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PhysicalPartitionThroughputInfoResult]: ...

        @overload
        async def begin_mongo_db_container_retrieve_throughput_distribution(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                collection_name: str, 
                retrieve_throughput_parameters: RetrieveThroughputParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PhysicalPartitionThroughputInfoResult]: ...

        @overload
        async def begin_mongo_db_container_retrieve_throughput_distribution(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                collection_name: str, 
                retrieve_throughput_parameters: RetrieveThroughputParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PhysicalPartitionThroughputInfoResult]: ...

        @overload
        async def begin_mongo_db_container_retrieve_throughput_distribution(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                collection_name: str, 
                retrieve_throughput_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PhysicalPartitionThroughputInfoResult]: ...

        @overload
        async def begin_mongo_db_database_partition_merge(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                merge_parameters: MergeParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PhysicalPartitionStorageInfoCollection]: ...

        @overload
        async def begin_mongo_db_database_partition_merge(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                merge_parameters: MergeParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PhysicalPartitionStorageInfoCollection]: ...

        @overload
        async def begin_mongo_db_database_partition_merge(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                merge_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PhysicalPartitionStorageInfoCollection]: ...

        @overload
        async def begin_mongo_db_database_redistribute_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                redistribute_throughput_parameters: RedistributeThroughputParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PhysicalPartitionThroughputInfoResult]: ...

        @overload
        async def begin_mongo_db_database_redistribute_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                redistribute_throughput_parameters: RedistributeThroughputParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PhysicalPartitionThroughputInfoResult]: ...

        @overload
        async def begin_mongo_db_database_redistribute_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                redistribute_throughput_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PhysicalPartitionThroughputInfoResult]: ...

        @overload
        async def begin_mongo_db_database_retrieve_throughput_distribution(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                retrieve_throughput_parameters: RetrieveThroughputParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PhysicalPartitionThroughputInfoResult]: ...

        @overload
        async def begin_mongo_db_database_retrieve_throughput_distribution(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                retrieve_throughput_parameters: RetrieveThroughputParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PhysicalPartitionThroughputInfoResult]: ...

        @overload
        async def begin_mongo_db_database_retrieve_throughput_distribution(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                retrieve_throughput_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PhysicalPartitionThroughputInfoResult]: ...

        @overload
        async def begin_retrieve_continuous_backup_information(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                collection_name: str, 
                location: ContinuousBackupRestoreLocation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BackupInformation]: ...

        @overload
        async def begin_retrieve_continuous_backup_information(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                collection_name: str, 
                location: ContinuousBackupRestoreLocation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BackupInformation]: ...

        @overload
        async def begin_retrieve_continuous_backup_information(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                collection_name: str, 
                location: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BackupInformation]: ...

        @overload
        async def begin_update_mongo_db_collection_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                collection_name: str, 
                update_throughput_parameters: ThroughputSettingsUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ThroughputSettingsGetResults]: ...

        @overload
        async def begin_update_mongo_db_collection_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                collection_name: str, 
                update_throughput_parameters: ThroughputSettingsUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ThroughputSettingsGetResults]: ...

        @overload
        async def begin_update_mongo_db_collection_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                collection_name: str, 
                update_throughput_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ThroughputSettingsGetResults]: ...

        @overload
        async def begin_update_mongo_db_database_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                update_throughput_parameters: ThroughputSettingsUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ThroughputSettingsGetResults]: ...

        @overload
        async def begin_update_mongo_db_database_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                update_throughput_parameters: ThroughputSettingsUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ThroughputSettingsGetResults]: ...

        @overload
        async def begin_update_mongo_db_database_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                update_throughput_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ThroughputSettingsGetResults]: ...

        @distributed_trace_async
        async def get_mongo_db_collection(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                collection_name: str, 
                **kwargs: Any
            ) -> MongoDBCollectionGetResults: ...

        @distributed_trace_async
        async def get_mongo_db_collection_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                collection_name: str, 
                **kwargs: Any
            ) -> ThroughputSettingsGetResults: ...

        @distributed_trace_async
        async def get_mongo_db_database(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> MongoDBDatabaseGetResults: ...

        @distributed_trace_async
        async def get_mongo_db_database_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> ThroughputSettingsGetResults: ...

        @distributed_trace_async
        async def get_mongo_role_definition(
                self, 
                mongo_role_definition_id: str, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> MongoRoleDefinitionGetResults: ...

        @distributed_trace_async
        async def get_mongo_user_definition(
                self, 
                mongo_user_definition_id: str, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> MongoUserDefinitionGetResults: ...

        @distributed_trace
        def list_mongo_db_collections(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[MongoDBCollectionGetResults]: ...

        @distributed_trace
        def list_mongo_db_databases(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[MongoDBDatabaseGetResults]: ...

        @distributed_trace
        def list_mongo_role_definitions(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[MongoRoleDefinitionGetResults]: ...

        @distributed_trace
        def list_mongo_user_definitions(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[MongoUserDefinitionGetResults]: ...


    class azure.mgmt.cosmosdb.aio.operations.MongoMIResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_update_mongo_mi_role_assignment(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_assignment_id: str, 
                create_update_mongo_mi_role_assignment_parameters: MongoMIRoleAssignmentResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MongoMIRoleAssignmentResource]: ...

        @overload
        async def begin_create_update_mongo_mi_role_assignment(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_assignment_id: str, 
                create_update_mongo_mi_role_assignment_parameters: MongoMIRoleAssignmentResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MongoMIRoleAssignmentResource]: ...

        @overload
        async def begin_create_update_mongo_mi_role_assignment(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_assignment_id: str, 
                create_update_mongo_mi_role_assignment_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MongoMIRoleAssignmentResource]: ...

        @overload
        async def begin_create_update_mongo_mi_role_definition(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_definition_id: str, 
                create_update_mongo_mi_role_definition_parameters: MongoMIRoleDefinitionResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MongoMIRoleDefinitionResource]: ...

        @overload
        async def begin_create_update_mongo_mi_role_definition(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_definition_id: str, 
                create_update_mongo_mi_role_definition_parameters: MongoMIRoleDefinitionResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MongoMIRoleDefinitionResource]: ...

        @overload
        async def begin_create_update_mongo_mi_role_definition(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_definition_id: str, 
                create_update_mongo_mi_role_definition_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MongoMIRoleDefinitionResource]: ...

        @distributed_trace_async
        async def begin_delete_mongo_mi_role_assignment(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_assignment_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_delete_mongo_mi_role_definition(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_definition_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get_mongo_mi_role_assignment(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_assignment_id: str, 
                **kwargs: Any
            ) -> MongoMIRoleAssignmentResource: ...

        @distributed_trace_async
        async def get_mongo_mi_role_definition(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_definition_id: str, 
                **kwargs: Any
            ) -> MongoMIRoleDefinitionResource: ...

        @distributed_trace
        def list_mongo_mi_role_assignments(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[MongoMIRoleAssignmentResource]: ...

        @distributed_trace
        def list_mongo_mi_role_definitions(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[MongoMIRoleDefinitionResource]: ...


    class azure.mgmt.cosmosdb.aio.operations.NetworkSecurityPerimeterConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'network_security_perimeter_configuration_name']}, api_versions_list=['2026-04-01-preview'])
        async def begin_reconcile(
                self, 
                resource_group_name: str, 
                account_name: str, 
                network_security_perimeter_configuration_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'network_security_perimeter_configuration_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                network_security_perimeter_configuration_name: str, 
                **kwargs: Any
            ) -> NetworkSecurityPerimeterConfiguration: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[NetworkSecurityPerimeterConfiguration]: ...


    class azure.mgmt.cosmosdb.aio.operations.NotebookWorkspacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                notebook_workspace_name: Union[str, NotebookWorkspaceName], 
                notebook_create_update_parameters: NotebookWorkspaceCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NotebookWorkspace]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                notebook_workspace_name: Union[str, NotebookWorkspaceName], 
                notebook_create_update_parameters: NotebookWorkspaceCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NotebookWorkspace]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                notebook_workspace_name: Union[str, NotebookWorkspaceName], 
                notebook_create_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NotebookWorkspace]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                notebook_workspace_name: Union[str, NotebookWorkspaceName], 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_regenerate_auth_token(
                self, 
                resource_group_name: str, 
                account_name: str, 
                notebook_workspace_name: Union[str, NotebookWorkspaceName], 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_start(
                self, 
                resource_group_name: str, 
                account_name: str, 
                notebook_workspace_name: Union[str, NotebookWorkspaceName], 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                notebook_workspace_name: Union[str, NotebookWorkspaceName], 
                **kwargs: Any
            ) -> NotebookWorkspace: ...

        @distributed_trace
        def list_by_database_account(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[NotebookWorkspace]: ...

        @distributed_trace_async
        async def list_connection_info(
                self, 
                resource_group_name: str, 
                account_name: str, 
                notebook_workspace_name: Union[str, NotebookWorkspaceName], 
                **kwargs: Any
            ) -> NotebookWorkspaceConnectionInfoResult: ...


    class azure.mgmt.cosmosdb.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.cosmosdb.aio.operations.PartitionKeyRangeIdOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_metrics(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_rid: str, 
                collection_rid: str, 
                partition_key_range_id: str, 
                *, 
                filter: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PartitionMetric]: ...


    class azure.mgmt.cosmosdb.aio.operations.PartitionKeyRangeIdRegionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_metrics(
                self, 
                resource_group_name: str, 
                account_name: str, 
                region: str, 
                database_rid: str, 
                collection_rid: str, 
                partition_key_range_id: str, 
                *, 
                filter: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PartitionMetric]: ...


    class azure.mgmt.cosmosdb.aio.operations.PercentileOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_metrics(
                self, 
                resource_group_name: str, 
                account_name: str, 
                *, 
                filter: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PercentileMetric]: ...


    class azure.mgmt.cosmosdb.aio.operations.PercentileSourceTargetOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_metrics(
                self, 
                resource_group_name: str, 
                account_name: str, 
                source_region: str, 
                target_region: str, 
                *, 
                filter: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PercentileMetric]: ...


    class azure.mgmt.cosmosdb.aio.operations.PercentileTargetOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_metrics(
                self, 
                resource_group_name: str, 
                account_name: str, 
                target_region: str, 
                *, 
                filter: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PercentileMetric]: ...


    class azure.mgmt.cosmosdb.aio.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
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
                account_name: str, 
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
                account_name: str, 
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
                account_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list_by_database_account(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateEndpointConnection]: ...


    class azure.mgmt.cosmosdb.aio.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                group_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @distributed_trace
        def list_by_database_account(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateLinkResource]: ...


    class azure.mgmt.cosmosdb.aio.operations.RestorableDatabaseAccountsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get_by_location(
                self, 
                location: str, 
                instance_id: str, 
                **kwargs: Any
            ) -> RestorableDatabaseAccountGetResult: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[RestorableDatabaseAccountGetResult]: ...

        @distributed_trace
        def list_by_location(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[RestorableDatabaseAccountGetResult]: ...


    class azure.mgmt.cosmosdb.aio.operations.RestorableGremlinDatabasesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                instance_id: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[RestorableGremlinDatabaseGetResult]: ...


    class azure.mgmt.cosmosdb.aio.operations.RestorableGremlinGraphsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                instance_id: str, 
                *, 
                end_time: Optional[str] = ..., 
                restorable_gremlin_database_rid: Optional[str] = ..., 
                start_time: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[RestorableGremlinGraphGetResult]: ...


    class azure.mgmt.cosmosdb.aio.operations.RestorableGremlinResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                instance_id: str, 
                *, 
                restore_location: Optional[str] = ..., 
                restore_timestamp_in_utc: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[RestorableGremlinResourcesGetResult]: ...


    class azure.mgmt.cosmosdb.aio.operations.RestorableMongodbCollectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                instance_id: str, 
                *, 
                end_time: Optional[str] = ..., 
                restorable_mongodb_database_rid: Optional[str] = ..., 
                start_time: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[RestorableMongodbCollectionGetResult]: ...


    class azure.mgmt.cosmosdb.aio.operations.RestorableMongodbDatabasesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                instance_id: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[RestorableMongodbDatabaseGetResult]: ...


    class azure.mgmt.cosmosdb.aio.operations.RestorableMongodbResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                instance_id: str, 
                *, 
                restore_location: Optional[str] = ..., 
                restore_timestamp_in_utc: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[RestorableMongodbResourcesGetResult]: ...


    class azure.mgmt.cosmosdb.aio.operations.RestorableSqlContainersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                instance_id: str, 
                *, 
                end_time: Optional[str] = ..., 
                restorable_sql_database_rid: Optional[str] = ..., 
                start_time: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[RestorableSqlContainerGetResult]: ...


    class azure.mgmt.cosmosdb.aio.operations.RestorableSqlDatabasesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                instance_id: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[RestorableSqlDatabaseGetResult]: ...


    class azure.mgmt.cosmosdb.aio.operations.RestorableSqlResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                instance_id: str, 
                *, 
                restore_location: Optional[str] = ..., 
                restore_timestamp_in_utc: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[RestorableSqlResourcesGetResult]: ...


    class azure.mgmt.cosmosdb.aio.operations.RestorableTableResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                instance_id: str, 
                *, 
                restore_location: Optional[str] = ..., 
                restore_timestamp_in_utc: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[RestorableTableResourcesGetResult]: ...


    class azure.mgmt.cosmosdb.aio.operations.RestorableTablesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                instance_id: str, 
                *, 
                end_time: Optional[str] = ..., 
                start_time: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[RestorableTableGetResult]: ...


    class azure.mgmt.cosmosdb.aio.operations.ServiceOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                service_name: str, 
                create_update_parameters: ServiceResourceCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ServiceResource]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                service_name: str, 
                create_update_parameters: ServiceResourceCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ServiceResource]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                service_name: str, 
                create_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ServiceResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                service_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                service_name: str, 
                **kwargs: Any
            ) -> ServiceResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ServiceResource]: ...


    class azure.mgmt.cosmosdb.aio.operations.SoftDeletedDatabaseAccountsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['subscription_id', 'resource_group_name', 'location', 'account_name', 'api_version', 'soft_delete_action_kind']}, api_versions_list=['2026-04-01-preview'])
        async def begin_purge(
                self, 
                resource_group_name: str, 
                location: str, 
                account_name: str, 
                *, 
                soft_delete_action_kind: Optional[Union[str, SoftDeleteActionKind]] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['subscription_id', 'resource_group_name', 'location', 'account_name', 'api_version', 'soft_delete_action_kind']}, api_versions_list=['2026-04-01-preview'])
        async def begin_restore(
                self, 
                resource_group_name: str, 
                location: str, 
                account_name: str, 
                *, 
                soft_delete_action_kind: Optional[Union[str, SoftDeleteActionKind]] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'location', 'account_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                location: str, 
                account_name: str, 
                **kwargs: Any
            ) -> SoftDeletedDatabaseAccountGetResult: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'location', 'accept']}, api_versions_list=['2026-04-01-preview'])
        async def list_by_location(
                self, 
                location: str, 
                **kwargs: Any
            ) -> SoftDeletedDatabaseAccountsListResult: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['subscription_id', 'resource_group_name', 'location', 'api_version', 'accept']}, api_versions_list=['2026-04-01-preview'])
        async def list_by_resource_group_and_location(
                self, 
                resource_group_name: str, 
                location: str, 
                **kwargs: Any
            ) -> SoftDeletedDatabaseAccountsListResult: ...


    class azure.mgmt.cosmosdb.aio.operations.SoftDeletedSqlContainersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['subscription_id', 'resource_group_name', 'location', 'account_name', 'database_name', 'container_name', 'api_version', 'soft_delete_action_kind']}, api_versions_list=['2026-04-01-preview'])
        async def begin_purge(
                self, 
                resource_group_name: str, 
                location: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                *, 
                soft_delete_action_kind: Optional[Union[str, SoftDeleteActionKind]] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['subscription_id', 'resource_group_name', 'location', 'account_name', 'database_name', 'container_name', 'api_version', 'soft_delete_action_kind']}, api_versions_list=['2026-04-01-preview'])
        async def begin_restore(
                self, 
                resource_group_name: str, 
                location: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                *, 
                soft_delete_action_kind: Optional[Union[str, SoftDeleteActionKind]] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'location', 'account_name', 'database_name', 'container_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                location: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                **kwargs: Any
            ) -> SoftDeletedSqlContainerGetResult: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'location', 'account_name', 'database_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        async def list(
                self, 
                resource_group_name: str, 
                location: str, 
                account_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> SoftDeletedSqlContainersListResult: ...


    class azure.mgmt.cosmosdb.aio.operations.SoftDeletedSqlDatabasesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['subscription_id', 'resource_group_name', 'location', 'account_name', 'database_name', 'api_version', 'soft_delete_action_kind']}, api_versions_list=['2026-04-01-preview'])
        async def begin_purge(
                self, 
                resource_group_name: str, 
                location: str, 
                account_name: str, 
                database_name: str, 
                *, 
                soft_delete_action_kind: Optional[Union[str, SoftDeleteActionKind]] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['subscription_id', 'resource_group_name', 'location', 'account_name', 'database_name', 'api_version', 'soft_delete_action_kind']}, api_versions_list=['2026-04-01-preview'])
        async def begin_restore(
                self, 
                resource_group_name: str, 
                location: str, 
                account_name: str, 
                database_name: str, 
                *, 
                soft_delete_action_kind: Optional[Union[str, SoftDeleteActionKind]] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'location', 'account_name', 'database_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                location: str, 
                account_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> SoftDeletedSqlDatabaseGetResult: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'location', 'account_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        async def list(
                self, 
                resource_group_name: str, 
                location: str, 
                account_name: str, 
                **kwargs: Any
            ) -> SoftDeletedSqlDatabasesListResult: ...


    class azure.mgmt.cosmosdb.aio.operations.SqlResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_update_client_encryption_key(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                client_encryption_key_name: str, 
                create_update_client_encryption_key_parameters: ClientEncryptionKeyCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ClientEncryptionKeyGetResults]: ...

        @overload
        async def begin_create_update_client_encryption_key(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                client_encryption_key_name: str, 
                create_update_client_encryption_key_parameters: ClientEncryptionKeyCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ClientEncryptionKeyGetResults]: ...

        @overload
        async def begin_create_update_client_encryption_key(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                client_encryption_key_name: str, 
                create_update_client_encryption_key_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ClientEncryptionKeyGetResults]: ...

        @overload
        async def begin_create_update_sql_container(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                create_update_sql_container_parameters: SqlContainerCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlContainerGetResults]: ...

        @overload
        async def begin_create_update_sql_container(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                create_update_sql_container_parameters: SqlContainerCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlContainerGetResults]: ...

        @overload
        async def begin_create_update_sql_container(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                create_update_sql_container_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlContainerGetResults]: ...

        @overload
        async def begin_create_update_sql_database(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                create_update_sql_database_parameters: SqlDatabaseCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlDatabaseGetResults]: ...

        @overload
        async def begin_create_update_sql_database(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                create_update_sql_database_parameters: SqlDatabaseCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlDatabaseGetResults]: ...

        @overload
        async def begin_create_update_sql_database(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                create_update_sql_database_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlDatabaseGetResults]: ...

        @overload
        async def begin_create_update_sql_role_assignment(
                self, 
                role_assignment_id: str, 
                resource_group_name: str, 
                account_name: str, 
                create_update_sql_role_assignment_parameters: SqlRoleAssignmentCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlRoleAssignmentGetResults]: ...

        @overload
        async def begin_create_update_sql_role_assignment(
                self, 
                role_assignment_id: str, 
                resource_group_name: str, 
                account_name: str, 
                create_update_sql_role_assignment_parameters: SqlRoleAssignmentCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlRoleAssignmentGetResults]: ...

        @overload
        async def begin_create_update_sql_role_assignment(
                self, 
                role_assignment_id: str, 
                resource_group_name: str, 
                account_name: str, 
                create_update_sql_role_assignment_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlRoleAssignmentGetResults]: ...

        @overload
        async def begin_create_update_sql_role_definition(
                self, 
                role_definition_id: str, 
                resource_group_name: str, 
                account_name: str, 
                create_update_sql_role_definition_parameters: SqlRoleDefinitionCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlRoleDefinitionGetResults]: ...

        @overload
        async def begin_create_update_sql_role_definition(
                self, 
                role_definition_id: str, 
                resource_group_name: str, 
                account_name: str, 
                create_update_sql_role_definition_parameters: SqlRoleDefinitionCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlRoleDefinitionGetResults]: ...

        @overload
        async def begin_create_update_sql_role_definition(
                self, 
                role_definition_id: str, 
                resource_group_name: str, 
                account_name: str, 
                create_update_sql_role_definition_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlRoleDefinitionGetResults]: ...

        @overload
        async def begin_create_update_sql_stored_procedure(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                stored_procedure_name: str, 
                create_update_sql_stored_procedure_parameters: SqlStoredProcedureCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlStoredProcedureGetResults]: ...

        @overload
        async def begin_create_update_sql_stored_procedure(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                stored_procedure_name: str, 
                create_update_sql_stored_procedure_parameters: SqlStoredProcedureCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlStoredProcedureGetResults]: ...

        @overload
        async def begin_create_update_sql_stored_procedure(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                stored_procedure_name: str, 
                create_update_sql_stored_procedure_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlStoredProcedureGetResults]: ...

        @overload
        async def begin_create_update_sql_trigger(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                trigger_name: str, 
                create_update_sql_trigger_parameters: SqlTriggerCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlTriggerGetResults]: ...

        @overload
        async def begin_create_update_sql_trigger(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                trigger_name: str, 
                create_update_sql_trigger_parameters: SqlTriggerCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlTriggerGetResults]: ...

        @overload
        async def begin_create_update_sql_trigger(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                trigger_name: str, 
                create_update_sql_trigger_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlTriggerGetResults]: ...

        @overload
        async def begin_create_update_sql_user_defined_function(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                user_defined_function_name: str, 
                create_update_sql_user_defined_function_parameters: SqlUserDefinedFunctionCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlUserDefinedFunctionGetResults]: ...

        @overload
        async def begin_create_update_sql_user_defined_function(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                user_defined_function_name: str, 
                create_update_sql_user_defined_function_parameters: SqlUserDefinedFunctionCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlUserDefinedFunctionGetResults]: ...

        @overload
        async def begin_create_update_sql_user_defined_function(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                user_defined_function_name: str, 
                create_update_sql_user_defined_function_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlUserDefinedFunctionGetResults]: ...

        @distributed_trace_async
        async def begin_delete_sql_container(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_delete_sql_database(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_delete_sql_role_assignment(
                self, 
                role_assignment_id: str, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_delete_sql_role_definition(
                self, 
                role_definition_id: str, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_delete_sql_stored_procedure(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                stored_procedure_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_delete_sql_trigger(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                trigger_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_delete_sql_user_defined_function(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                user_defined_function_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_list_sql_container_partition_merge(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                merge_parameters: MergeParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PhysicalPartitionStorageInfoCollection]: ...

        @overload
        async def begin_list_sql_container_partition_merge(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                merge_parameters: MergeParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PhysicalPartitionStorageInfoCollection]: ...

        @overload
        async def begin_list_sql_container_partition_merge(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                merge_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PhysicalPartitionStorageInfoCollection]: ...

        @distributed_trace_async
        async def begin_migrate_sql_container_to_autoscale(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ThroughputSettingsGetResults]: ...

        @distributed_trace_async
        async def begin_migrate_sql_container_to_manual_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ThroughputSettingsGetResults]: ...

        @distributed_trace_async
        async def begin_migrate_sql_database_to_autoscale(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ThroughputSettingsGetResults]: ...

        @distributed_trace_async
        async def begin_migrate_sql_database_to_manual_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ThroughputSettingsGetResults]: ...

        @overload
        async def begin_retrieve_continuous_backup_information(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                location: ContinuousBackupRestoreLocation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BackupInformation]: ...

        @overload
        async def begin_retrieve_continuous_backup_information(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                location: ContinuousBackupRestoreLocation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BackupInformation]: ...

        @overload
        async def begin_retrieve_continuous_backup_information(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                location: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BackupInformation]: ...

        @overload
        async def begin_sql_container_redistribute_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                redistribute_throughput_parameters: RedistributeThroughputParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PhysicalPartitionThroughputInfoResult]: ...

        @overload
        async def begin_sql_container_redistribute_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                redistribute_throughput_parameters: RedistributeThroughputParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PhysicalPartitionThroughputInfoResult]: ...

        @overload
        async def begin_sql_container_redistribute_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                redistribute_throughput_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PhysicalPartitionThroughputInfoResult]: ...

        @overload
        async def begin_sql_container_retrieve_throughput_distribution(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                retrieve_throughput_parameters: RetrieveThroughputParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PhysicalPartitionThroughputInfoResult]: ...

        @overload
        async def begin_sql_container_retrieve_throughput_distribution(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                retrieve_throughput_parameters: RetrieveThroughputParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PhysicalPartitionThroughputInfoResult]: ...

        @overload
        async def begin_sql_container_retrieve_throughput_distribution(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                retrieve_throughput_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PhysicalPartitionThroughputInfoResult]: ...

        @overload
        async def begin_sql_database_partition_merge(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                merge_parameters: MergeParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PhysicalPartitionStorageInfoCollection]: ...

        @overload
        async def begin_sql_database_partition_merge(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                merge_parameters: MergeParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PhysicalPartitionStorageInfoCollection]: ...

        @overload
        async def begin_sql_database_partition_merge(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                merge_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PhysicalPartitionStorageInfoCollection]: ...

        @overload
        async def begin_sql_database_redistribute_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                redistribute_throughput_parameters: RedistributeThroughputParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PhysicalPartitionThroughputInfoResult]: ...

        @overload
        async def begin_sql_database_redistribute_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                redistribute_throughput_parameters: RedistributeThroughputParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PhysicalPartitionThroughputInfoResult]: ...

        @overload
        async def begin_sql_database_redistribute_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                redistribute_throughput_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PhysicalPartitionThroughputInfoResult]: ...

        @overload
        async def begin_sql_database_retrieve_throughput_distribution(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                retrieve_throughput_parameters: RetrieveThroughputParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PhysicalPartitionThroughputInfoResult]: ...

        @overload
        async def begin_sql_database_retrieve_throughput_distribution(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                retrieve_throughput_parameters: RetrieveThroughputParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PhysicalPartitionThroughputInfoResult]: ...

        @overload
        async def begin_sql_database_retrieve_throughput_distribution(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                retrieve_throughput_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PhysicalPartitionThroughputInfoResult]: ...

        @overload
        async def begin_update_sql_container_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                update_throughput_parameters: ThroughputSettingsUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ThroughputSettingsGetResults]: ...

        @overload
        async def begin_update_sql_container_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                update_throughput_parameters: ThroughputSettingsUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ThroughputSettingsGetResults]: ...

        @overload
        async def begin_update_sql_container_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                update_throughput_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ThroughputSettingsGetResults]: ...

        @overload
        async def begin_update_sql_database_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                update_throughput_parameters: ThroughputSettingsUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ThroughputSettingsGetResults]: ...

        @overload
        async def begin_update_sql_database_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                update_throughput_parameters: ThroughputSettingsUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ThroughputSettingsGetResults]: ...

        @overload
        async def begin_update_sql_database_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                update_throughput_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ThroughputSettingsGetResults]: ...

        @distributed_trace_async
        async def get_client_encryption_key(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                client_encryption_key_name: str, 
                **kwargs: Any
            ) -> ClientEncryptionKeyGetResults: ...

        @distributed_trace_async
        async def get_sql_container(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                **kwargs: Any
            ) -> SqlContainerGetResults: ...

        @distributed_trace_async
        async def get_sql_container_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                **kwargs: Any
            ) -> ThroughputSettingsGetResults: ...

        @distributed_trace_async
        async def get_sql_database(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> SqlDatabaseGetResults: ...

        @distributed_trace_async
        async def get_sql_database_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> ThroughputSettingsGetResults: ...

        @distributed_trace_async
        async def get_sql_role_assignment(
                self, 
                role_assignment_id: str, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> SqlRoleAssignmentGetResults: ...

        @distributed_trace_async
        async def get_sql_role_definition(
                self, 
                role_definition_id: str, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> SqlRoleDefinitionGetResults: ...

        @distributed_trace_async
        async def get_sql_stored_procedure(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                stored_procedure_name: str, 
                **kwargs: Any
            ) -> SqlStoredProcedureGetResults: ...

        @distributed_trace_async
        async def get_sql_trigger(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                trigger_name: str, 
                **kwargs: Any
            ) -> SqlTriggerGetResults: ...

        @distributed_trace_async
        async def get_sql_user_defined_function(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                user_defined_function_name: str, 
                **kwargs: Any
            ) -> SqlUserDefinedFunctionGetResults: ...

        @distributed_trace
        def list_client_encryption_keys(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ClientEncryptionKeyGetResults]: ...

        @distributed_trace
        def list_sql_containers(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SqlContainerGetResults]: ...

        @distributed_trace
        def list_sql_databases(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SqlDatabaseGetResults]: ...

        @distributed_trace
        def list_sql_role_assignments(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SqlRoleAssignmentGetResults]: ...

        @distributed_trace
        def list_sql_role_definitions(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SqlRoleDefinitionGetResults]: ...

        @distributed_trace
        def list_sql_stored_procedures(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SqlStoredProcedureGetResults]: ...

        @distributed_trace
        def list_sql_triggers(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SqlTriggerGetResults]: ...

        @distributed_trace
        def list_sql_user_defined_functions(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SqlUserDefinedFunctionGetResults]: ...


    class azure.mgmt.cosmosdb.aio.operations.TableResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_update_table(
                self, 
                resource_group_name: str, 
                account_name: str, 
                table_name: str, 
                create_update_table_parameters: TableCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TableGetResults]: ...

        @overload
        async def begin_create_update_table(
                self, 
                resource_group_name: str, 
                account_name: str, 
                table_name: str, 
                create_update_table_parameters: TableCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TableGetResults]: ...

        @overload
        async def begin_create_update_table(
                self, 
                resource_group_name: str, 
                account_name: str, 
                table_name: str, 
                create_update_table_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TableGetResults]: ...

        @overload
        async def begin_create_update_table_role_assignment(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_assignment_id: str, 
                create_update_table_role_assignment_parameters: TableRoleAssignmentResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TableRoleAssignmentResource]: ...

        @overload
        async def begin_create_update_table_role_assignment(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_assignment_id: str, 
                create_update_table_role_assignment_parameters: TableRoleAssignmentResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TableRoleAssignmentResource]: ...

        @overload
        async def begin_create_update_table_role_assignment(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_assignment_id: str, 
                create_update_table_role_assignment_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TableRoleAssignmentResource]: ...

        @overload
        async def begin_create_update_table_role_definition(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_definition_id: str, 
                create_update_table_role_definition_parameters: TableRoleDefinitionResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TableRoleDefinitionResource]: ...

        @overload
        async def begin_create_update_table_role_definition(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_definition_id: str, 
                create_update_table_role_definition_parameters: TableRoleDefinitionResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TableRoleDefinitionResource]: ...

        @overload
        async def begin_create_update_table_role_definition(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_definition_id: str, 
                create_update_table_role_definition_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TableRoleDefinitionResource]: ...

        @distributed_trace_async
        async def begin_delete_table(
                self, 
                resource_group_name: str, 
                account_name: str, 
                table_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_delete_table_role_assignment(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_assignment_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_delete_table_role_definition(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_definition_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_migrate_table_to_autoscale(
                self, 
                resource_group_name: str, 
                account_name: str, 
                table_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ThroughputSettingsGetResults]: ...

        @distributed_trace_async
        async def begin_migrate_table_to_manual_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                table_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ThroughputSettingsGetResults]: ...

        @overload
        async def begin_retrieve_continuous_backup_information(
                self, 
                resource_group_name: str, 
                account_name: str, 
                table_name: str, 
                location: ContinuousBackupRestoreLocation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BackupInformation]: ...

        @overload
        async def begin_retrieve_continuous_backup_information(
                self, 
                resource_group_name: str, 
                account_name: str, 
                table_name: str, 
                location: ContinuousBackupRestoreLocation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BackupInformation]: ...

        @overload
        async def begin_retrieve_continuous_backup_information(
                self, 
                resource_group_name: str, 
                account_name: str, 
                table_name: str, 
                location: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BackupInformation]: ...

        @overload
        async def begin_update_table_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                table_name: str, 
                update_throughput_parameters: ThroughputSettingsUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ThroughputSettingsGetResults]: ...

        @overload
        async def begin_update_table_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                table_name: str, 
                update_throughput_parameters: ThroughputSettingsUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ThroughputSettingsGetResults]: ...

        @overload
        async def begin_update_table_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                table_name: str, 
                update_throughput_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ThroughputSettingsGetResults]: ...

        @distributed_trace_async
        async def get_table(
                self, 
                resource_group_name: str, 
                account_name: str, 
                table_name: str, 
                **kwargs: Any
            ) -> TableGetResults: ...

        @distributed_trace_async
        async def get_table_role_assignment(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_assignment_id: str, 
                **kwargs: Any
            ) -> TableRoleAssignmentResource: ...

        @distributed_trace_async
        async def get_table_role_definition(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_definition_id: str, 
                **kwargs: Any
            ) -> TableRoleDefinitionResource: ...

        @distributed_trace_async
        async def get_table_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                table_name: str, 
                **kwargs: Any
            ) -> ThroughputSettingsGetResults: ...

        @distributed_trace
        def list_table_role_assignments(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[TableRoleAssignmentResource]: ...

        @distributed_trace
        def list_table_role_definitions(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[TableRoleDefinitionResource]: ...

        @distributed_trace
        def list_tables(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[TableGetResults]: ...


    class azure.mgmt.cosmosdb.aio.operations.ThroughputPoolAccountOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                throughput_pool_name: str, 
                throughput_pool_account_name: str, 
                body: ThroughputPoolAccountResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ThroughputPoolAccountResource]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                throughput_pool_name: str, 
                throughput_pool_account_name: str, 
                body: ThroughputPoolAccountResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ThroughputPoolAccountResource]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                throughput_pool_name: str, 
                throughput_pool_account_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ThroughputPoolAccountResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                throughput_pool_name: str, 
                throughput_pool_account_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                throughput_pool_name: str, 
                throughput_pool_account_name: str, 
                **kwargs: Any
            ) -> ThroughputPoolAccountResource: ...


    class azure.mgmt.cosmosdb.aio.operations.ThroughputPoolAccountsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                throughput_pool_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ThroughputPoolAccountResource]: ...


    class azure.mgmt.cosmosdb.aio.operations.ThroughputPoolOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                throughput_pool_name: str, 
                body: ThroughputPoolResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ThroughputPoolResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                throughput_pool_name: str, 
                body: ThroughputPoolResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ThroughputPoolResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                throughput_pool_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ThroughputPoolResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                throughput_pool_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                throughput_pool_name: str, 
                body: Optional[ThroughputPoolUpdate] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ThroughputPoolResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                throughput_pool_name: str, 
                body: Optional[ThroughputPoolUpdate] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ThroughputPoolResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                throughput_pool_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ThroughputPoolResource]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                throughput_pool_name: str, 
                **kwargs: Any
            ) -> ThroughputPoolResource: ...


    class azure.mgmt.cosmosdb.aio.operations.ThroughputPoolsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[ThroughputPoolResource]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ThroughputPoolResource]: ...


namespace azure.mgmt.cosmosdb.models

    class azure.mgmt.cosmosdb.models.ARMProxyResource(_Model):
        id: Optional[str]
        name: Optional[str]
        type: Optional[str]


    class azure.mgmt.cosmosdb.models.ARMResourceProperties(_Model):
        id: Optional[str]
        identity: Optional[ManagedServiceIdentity]
        location: Optional[str]
        name: Optional[str]
        tags: Optional[dict[str, str]]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: Optional[str] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.AccessRule(_Model):
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


    class azure.mgmt.cosmosdb.models.AccessRuleDirection(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INBOUND = "Inbound"
        OUTBOUND = "Outbound"


    class azure.mgmt.cosmosdb.models.AccessRuleProperties(_Model):
        address_prefixes: Optional[list[str]]
        direction: Optional[Union[str, AccessRuleDirection]]
        email_addresses: Optional[list[str]]
        fully_qualified_domain_names: Optional[list[str]]
        network_security_perimeters: Optional[list[NetworkSecurityPerimeter]]
        phone_numbers: Optional[list[str]]
        subscriptions: Optional[list[AccessRulePropertiesSubscriptionsItem]]

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
                subscriptions: Optional[list[AccessRulePropertiesSubscriptionsItem]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.AccessRulePropertiesSubscriptionsItem(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.AccountKeyMetadata(_Model):
        approximate_last_usage_time: Optional[datetime]
        generation_time: Optional[datetime]


    class azure.mgmt.cosmosdb.models.AllocationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        DEALLOCATED = "Deallocated"


    class azure.mgmt.cosmosdb.models.AnalyticalStorageConfiguration(_Model):
        schema_type: Optional[Union[str, AnalyticalStorageSchemaType]]

        @overload
        def __init__(
                self, 
                *, 
                schema_type: Optional[Union[str, AnalyticalStorageSchemaType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.AnalyticalStorageSchemaType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FULL_FIDELITY = "FullFidelity"
        WELL_DEFINED = "WellDefined"


    class azure.mgmt.cosmosdb.models.ApiProperties(_Model):
        server_version: Optional[Union[str, ServerVersion]]

        @overload
        def __init__(
                self, 
                *, 
                server_version: Optional[Union[str, ServerVersion]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.ApiType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CASSANDRA = "Cassandra"
        GREMLIN = "Gremlin"
        GREMLIN_V2 = "GremlinV2"
        MONGO_DB = "MongoDB"
        SQL = "Sql"
        TABLE = "Table"


    class azure.mgmt.cosmosdb.models.AuthenticationMethod(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CASSANDRA = "Cassandra"
        LDAP = "Ldap"
        NONE = "None"


    class azure.mgmt.cosmosdb.models.AuthenticationMethodLdapProperties(_Model):
        connection_timeout_in_ms: Optional[int]
        search_base_distinguished_name: Optional[str]
        search_filter_template: Optional[str]
        server_certificates: Optional[list[Certificate]]
        server_hostname: Optional[str]
        server_port: Optional[int]
        service_user_distinguished_name: Optional[str]
        service_user_password: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                connection_timeout_in_ms: Optional[int] = ..., 
                search_base_distinguished_name: Optional[str] = ..., 
                search_filter_template: Optional[str] = ..., 
                server_certificates: Optional[list[Certificate]] = ..., 
                server_hostname: Optional[str] = ..., 
                server_port: Optional[int] = ..., 
                service_user_distinguished_name: Optional[str] = ..., 
                service_user_password: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.AutoReplicate(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL_KEYSPACES = "AllKeyspaces"
        NONE = "None"
        SYSTEM_KEYSPACES = "SystemKeyspaces"


    class azure.mgmt.cosmosdb.models.AutoUpgradePolicyResource(_Model):
        throughput_policy: Optional[ThroughputPolicyResource]

        @overload
        def __init__(
                self, 
                *, 
                throughput_policy: Optional[ThroughputPolicyResource] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.AutoscaleSettings(_Model):
        max_throughput: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                max_throughput: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.AutoscaleSettingsResource(_Model):
        auto_upgrade_policy: Optional[AutoUpgradePolicyResource]
        max_throughput: int
        target_max_throughput: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                auto_upgrade_policy: Optional[AutoUpgradePolicyResource] = ..., 
                max_throughput: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.AzureBlobContainer(_Model):
        container_name: str

        @overload
        def __init__(
                self, 
                *, 
                container_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.AzureBlobDataTransferDataSourceSink(DataTransferDataSourceSink, discriminator='AzureBlobStorage'):
        component: Literal[DataTransferComponent.AZURE_BLOB_STORAGE]
        container_name: str
        endpoint_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                container_name: str, 
                endpoint_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.AzureBlobSourceSinkDetails(_Model):
        endpoint_url: str

        @overload
        def __init__(
                self, 
                *, 
                endpoint_url: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.AzureConnectionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        VPN = "VPN"


    class azure.mgmt.cosmosdb.models.BackupInformation(_Model):
        continuous_backup_information: Optional[ContinuousBackupInformation]

        @overload
        def __init__(
                self, 
                *, 
                continuous_backup_information: Optional[ContinuousBackupInformation] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.BackupPolicy(_Model):
        migration_state: Optional[BackupPolicyMigrationState]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                migration_state: Optional[BackupPolicyMigrationState] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.BackupPolicyMigrationState(_Model):
        start_time: Optional[datetime]
        status: Optional[Union[str, BackupPolicyMigrationStatus]]
        target_type: Optional[Union[str, BackupPolicyType]]

        @overload
        def __init__(
                self, 
                *, 
                start_time: Optional[datetime] = ..., 
                status: Optional[Union[str, BackupPolicyMigrationStatus]] = ..., 
                target_type: Optional[Union[str, BackupPolicyType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.BackupPolicyMigrationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "Completed"
        FAILED = "Failed"
        INVALID = "Invalid"
        IN_PROGRESS = "InProgress"


    class azure.mgmt.cosmosdb.models.BackupPolicyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTINUOUS = "Continuous"
        PERIODIC = "Periodic"


    class azure.mgmt.cosmosdb.models.BackupResource(_Model):
        backup_expiry_timestamp: Optional[datetime]
        backup_id: Optional[str]
        backup_start_timestamp: Optional[datetime]
        backup_state: Optional[Union[str, BackupState]]
        backup_stop_timestamp: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                backup_expiry_timestamp: Optional[datetime] = ..., 
                backup_id: Optional[str] = ..., 
                backup_start_timestamp: Optional[datetime] = ..., 
                backup_state: Optional[Union[str, BackupState]] = ..., 
                backup_stop_timestamp: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.BackupSchedule(_Model):
        cron_expression: Optional[str]
        retention_in_hours: Optional[int]
        schedule_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                cron_expression: Optional[str] = ..., 
                retention_in_hours: Optional[int] = ..., 
                schedule_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.BackupState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        INITIATED = "Initiated"
        IN_PROGRESS = "InProgress"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.cosmosdb.models.BackupStorageRedundancy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GEO = "Geo"
        LOCAL = "Local"
        ZONE = "Zone"


    class azure.mgmt.cosmosdb.models.BaseCopyJobProperties(_Model):
        job_type: str

        @overload
        def __init__(
                self, 
                *, 
                job_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.BaseCopyJobTask(_Model):
        processed_count: Optional[int]
        total_count: Optional[int]


    class azure.mgmt.cosmosdb.models.BaseCosmosDataTransferDataSourceSink(DataTransferDataSourceSink, discriminator='BaseCosmosDataTransferDataSourceSink'):
        component: Literal[DataTransferComponent.BASE_COSMOS_DATA_TRANSFER_DATA_SOURCE_SINK]
        remote_account_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                remote_account_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.BlobToCassandraRUCopyJobProperties(BaseCopyJobProperties, discriminator='AzureBlobStorageToCassandraRU'):
        destination_details: Optional[CosmosDBSourceSinkDetails]
        job_type: Literal[CopyJobType.AZURE_BLOB_STORAGE_TO_CASSANDRA_RU]
        source_details: AzureBlobSourceSinkDetails
        tasks: list[BlobToCassandraRUCopyJobTask]

        @overload
        def __init__(
                self, 
                *, 
                destination_details: Optional[CosmosDBSourceSinkDetails] = ..., 
                source_details: AzureBlobSourceSinkDetails, 
                tasks: list[BlobToCassandraRUCopyJobTask]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.BlobToCassandraRUCopyJobTask(BaseCopyJobTask):
        destination: CosmosDBCassandraTable
        processed_count: int
        source: AzureBlobContainer
        total_count: int

        @overload
        def __init__(
                self, 
                *, 
                destination: CosmosDBCassandraTable, 
                source: AzureBlobContainer
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.Capability(_Model):
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.Capacity(_Model):
        total_throughput_limit: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                total_throughput_limit: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.CapacityMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        PROVISIONED = "Provisioned"
        SERVERLESS = "Serverless"


    class azure.mgmt.cosmosdb.models.CapacityModeChangeTransitionState(_Model):
        capacity_mode_last_successful_transition_end_timestamp: Optional[datetime]
        capacity_mode_transition_begin_timestamp: Optional[datetime]
        capacity_mode_transition_end_timestamp: Optional[datetime]
        capacity_mode_transition_status: Optional[Union[str, CapacityModeTransitionStatus]]
        current_capacity_mode: Optional[Union[str, CapacityMode]]
        previous_capacity_mode: Optional[Union[str, CapacityMode]]

        @overload
        def __init__(
                self, 
                *, 
                capacity_mode_transition_status: Optional[Union[str, CapacityModeTransitionStatus]] = ..., 
                current_capacity_mode: Optional[Union[str, CapacityMode]] = ..., 
                previous_capacity_mode: Optional[Union[str, CapacityMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.CapacityModeTransitionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "Completed"
        FAILED = "Failed"
        INITIALIZED = "Initialized"
        INVALID = "Invalid"
        IN_PROGRESS = "InProgress"


    class azure.mgmt.cosmosdb.models.CassandraClusterDataCenterNodeItem(_Model):
        address: Optional[str]
        cassandra_process_status: Optional[str]
        cpu_usage: Optional[float]
        disk_free_kb: Optional[int]
        disk_used_kb: Optional[int]
        host_id: Optional[str]
        is_latest_model: Optional[bool]
        load: Optional[str]
        memory_buffers_and_cached_kb: Optional[int]
        memory_free_kb: Optional[int]
        memory_total_kb: Optional[int]
        memory_used_kb: Optional[int]
        rack: Optional[str]
        size: Optional[int]
        state: Optional[Union[str, NodeState]]
        status: Optional[str]
        timestamp: Optional[str]
        tokens: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                address: Optional[str] = ..., 
                cassandra_process_status: Optional[str] = ..., 
                cpu_usage: Optional[float] = ..., 
                disk_free_kb: Optional[int] = ..., 
                disk_used_kb: Optional[int] = ..., 
                host_id: Optional[str] = ..., 
                is_latest_model: Optional[bool] = ..., 
                load: Optional[str] = ..., 
                memory_buffers_and_cached_kb: Optional[int] = ..., 
                memory_free_kb: Optional[int] = ..., 
                memory_total_kb: Optional[int] = ..., 
                memory_used_kb: Optional[int] = ..., 
                rack: Optional[str] = ..., 
                size: Optional[int] = ..., 
                state: Optional[Union[str, NodeState]] = ..., 
                status: Optional[str] = ..., 
                timestamp: Optional[str] = ..., 
                tokens: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.CassandraClusterPublicStatus(_Model):
        connection_errors: Optional[list[ConnectionError]]
        data_centers: Optional[list[CassandraClusterPublicStatusDataCentersItem]]
        e_tag: Optional[str]
        errors: Optional[list[CassandraError]]
        reaper_status: Optional[ManagedCassandraReaperStatus]

        @overload
        def __init__(
                self, 
                *, 
                connection_errors: Optional[list[ConnectionError]] = ..., 
                data_centers: Optional[list[CassandraClusterPublicStatusDataCentersItem]] = ..., 
                e_tag: Optional[str] = ..., 
                errors: Optional[list[CassandraError]] = ..., 
                reaper_status: Optional[ManagedCassandraReaperStatus] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.CassandraClusterPublicStatusDataCentersItem(_Model):
        name: Optional[str]
        nodes: Optional[list[CassandraClusterDataCenterNodeItem]]
        seed_nodes: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                nodes: Optional[list[CassandraClusterDataCenterNodeItem]] = ..., 
                seed_nodes: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.CassandraError(_Model):
        additional_error_info: Optional[str]
        code: Optional[str]
        message: Optional[str]
        target: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                additional_error_info: Optional[str] = ..., 
                code: Optional[str] = ..., 
                message: Optional[str] = ..., 
                target: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.CassandraKeyspaceCreateUpdateParameters(ARMResourceProperties):
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: CassandraKeyspaceCreateUpdateProperties
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: Optional[str] = ..., 
                properties: CassandraKeyspaceCreateUpdateProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.CassandraKeyspaceCreateUpdateProperties(_Model):
        options: Optional[CreateUpdateOptions]
        resource: CassandraKeyspaceResource

        @overload
        def __init__(
                self, 
                *, 
                options: Optional[CreateUpdateOptions] = ..., 
                resource: CassandraKeyspaceResource
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.CassandraKeyspaceGetProperties(_Model):
        options: Optional[CassandraKeyspaceGetPropertiesOptions]
        resource: Optional[CassandraKeyspaceGetPropertiesResource]

        @overload
        def __init__(
                self, 
                *, 
                options: Optional[CassandraKeyspaceGetPropertiesOptions] = ..., 
                resource: Optional[CassandraKeyspaceGetPropertiesResource] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.CassandraKeyspaceGetPropertiesOptions(OptionsResource):
        autoscale_settings: AutoscaleSettings
        throughput: int

        @overload
        def __init__(
                self, 
                *, 
                autoscale_settings: Optional[AutoscaleSettings] = ..., 
                throughput: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.CassandraKeyspaceGetPropertiesResource(CassandraKeyspaceResource):
        etag: Optional[str]
        id: str
        rid: Optional[str]
        ts: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.CassandraKeyspaceGetResults(ProxyResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: Optional[str]
        name: str
        properties: Optional[CassandraKeyspaceGetProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[CassandraKeyspaceGetProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.CassandraKeyspaceResource(_Model):
        id: str

        @overload
        def __init__(
                self, 
                *, 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.CassandraPartitionKey(_Model):
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.CassandraRUToBlobCopyJobProperties(BaseCopyJobProperties, discriminator='CassandraRUToAzureBlobStorage'):
        destination_details: AzureBlobSourceSinkDetails
        job_type: Literal[CopyJobType.CASSANDRA_RU_TO_AZURE_BLOB_STORAGE]
        source_details: Optional[CosmosDBSourceSinkDetails]
        tasks: list[CassandraRUToBlobCopyJobTask]

        @overload
        def __init__(
                self, 
                *, 
                destination_details: AzureBlobSourceSinkDetails, 
                source_details: Optional[CosmosDBSourceSinkDetails] = ..., 
                tasks: list[CassandraRUToBlobCopyJobTask]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.CassandraRUToBlobCopyJobTask(BaseCopyJobTask):
        destination: AzureBlobContainer
        processed_count: int
        source: CosmosDBCassandraTable
        total_count: int

        @overload
        def __init__(
                self, 
                *, 
                destination: AzureBlobContainer, 
                source: CosmosDBCassandraTable
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.CassandraRUToCassandraRUCopyJobProperties(BaseCopyJobProperties, discriminator='CassandraRUToCassandraRU'):
        destination_details: Optional[CosmosDBSourceSinkDetails]
        job_type: Literal[CopyJobType.CASSANDRA_RU_TO_CASSANDRA_RU]
        source_details: Optional[CosmosDBSourceSinkDetails]
        tasks: list[CassandraRUToCassandraRUCopyJobTask]

        @overload
        def __init__(
                self, 
                *, 
                destination_details: Optional[CosmosDBSourceSinkDetails] = ..., 
                source_details: Optional[CosmosDBSourceSinkDetails] = ..., 
                tasks: list[CassandraRUToCassandraRUCopyJobTask]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.CassandraRUToCassandraRUCopyJobTask(BaseCopyJobTask):
        destination: CosmosDBCassandraTable
        processed_count: int
        source: CosmosDBCassandraTable
        total_count: int

        @overload
        def __init__(
                self, 
                *, 
                destination: CosmosDBCassandraTable, 
                source: CosmosDBCassandraTable
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.CassandraRoleAssignmentResource(ProxyResource):
        id: str
        name: str
        properties: Optional[CassandraRoleAssignmentResourceProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CassandraRoleAssignmentResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.CassandraRoleAssignmentResourceProperties(_Model):
        principal_id: Optional[str]
        provisioning_state: Optional[str]
        role_definition_id: Optional[str]
        scope: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                principal_id: Optional[str] = ..., 
                role_definition_id: Optional[str] = ..., 
                scope: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.CassandraRoleDefinitionResource(ProxyResource):
        id: str
        name: str
        properties: Optional[CassandraRoleDefinitionResourceProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CassandraRoleDefinitionResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.CassandraRoleDefinitionResourceProperties(_Model):
        assignable_scopes: Optional[list[str]]
        id: Optional[str]
        permissions: Optional[list[Permission]]
        role_name: Optional[str]
        type: Optional[Union[str, RoleDefinitionType]]

        @overload
        def __init__(
                self, 
                *, 
                assignable_scopes: Optional[list[str]] = ..., 
                id: Optional[str] = ..., 
                permissions: Optional[list[Permission]] = ..., 
                role_name: Optional[str] = ..., 
                type: Optional[Union[str, RoleDefinitionType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.CassandraSchema(_Model):
        cluster_keys: Optional[list[ClusterKey]]
        columns: Optional[list[Column]]
        partition_keys: Optional[list[CassandraPartitionKey]]

        @overload
        def __init__(
                self, 
                *, 
                cluster_keys: Optional[list[ClusterKey]] = ..., 
                columns: Optional[list[Column]] = ..., 
                partition_keys: Optional[list[CassandraPartitionKey]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.CassandraTableCreateUpdateParameters(ARMResourceProperties):
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: CassandraTableCreateUpdateProperties
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: Optional[str] = ..., 
                properties: CassandraTableCreateUpdateProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.CassandraTableCreateUpdateProperties(_Model):
        options: Optional[CreateUpdateOptions]
        resource: CassandraTableResource

        @overload
        def __init__(
                self, 
                *, 
                options: Optional[CreateUpdateOptions] = ..., 
                resource: CassandraTableResource
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.CassandraTableGetProperties(_Model):
        options: Optional[CassandraTableGetPropertiesOptions]
        resource: Optional[CassandraTableGetPropertiesResource]

        @overload
        def __init__(
                self, 
                *, 
                options: Optional[CassandraTableGetPropertiesOptions] = ..., 
                resource: Optional[CassandraTableGetPropertiesResource] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.CassandraTableGetPropertiesOptions(OptionsResource):
        autoscale_settings: AutoscaleSettings
        throughput: int

        @overload
        def __init__(
                self, 
                *, 
                autoscale_settings: Optional[AutoscaleSettings] = ..., 
                throughput: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.CassandraTableGetPropertiesResource(CassandraTableResource):
        analytical_storage_ttl: int
        default_ttl: int
        etag: Optional[str]
        id: str
        rid: Optional[str]
        schema: CassandraSchema
        ts: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                analytical_storage_ttl: Optional[int] = ..., 
                default_ttl: Optional[int] = ..., 
                id: str, 
                schema: Optional[CassandraSchema] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.CassandraTableGetResults(ProxyResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: Optional[str]
        name: str
        properties: Optional[CassandraTableGetProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[CassandraTableGetProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.CassandraTableResource(_Model):
        analytical_storage_ttl: Optional[int]
        default_ttl: Optional[int]
        id: str
        schema: Optional[CassandraSchema]

        @overload
        def __init__(
                self, 
                *, 
                analytical_storage_ttl: Optional[int] = ..., 
                default_ttl: Optional[int] = ..., 
                id: str, 
                schema: Optional[CassandraSchema] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.CassandraViewCreateUpdateParameters(ARMResourceProperties):
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: CassandraViewCreateUpdateProperties
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: Optional[str] = ..., 
                properties: CassandraViewCreateUpdateProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.CassandraViewCreateUpdateProperties(_Model):
        options: Optional[CreateUpdateOptions]
        resource: CassandraViewResource

        @overload
        def __init__(
                self, 
                *, 
                options: Optional[CreateUpdateOptions] = ..., 
                resource: CassandraViewResource
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.CassandraViewGetProperties(_Model):
        options: Optional[CassandraViewGetPropertiesOptions]
        resource: Optional[CassandraViewGetPropertiesResource]

        @overload
        def __init__(
                self, 
                *, 
                options: Optional[CassandraViewGetPropertiesOptions] = ..., 
                resource: Optional[CassandraViewGetPropertiesResource] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.CassandraViewGetPropertiesOptions(OptionsResource):
        autoscale_settings: AutoscaleSettings
        throughput: int

        @overload
        def __init__(
                self, 
                *, 
                autoscale_settings: Optional[AutoscaleSettings] = ..., 
                throughput: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.CassandraViewGetPropertiesResource(CassandraViewResource):
        etag: Optional[str]
        id: str
        rid: Optional[str]
        ts: Optional[float]
        view_definition: str

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                view_definition: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.CassandraViewGetResults(ProxyResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: Optional[str]
        name: str
        properties: Optional[CassandraViewGetProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[CassandraViewGetProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.CassandraViewResource(_Model):
        id: str
        view_definition: str

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                view_definition: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.Certificate(_Model):
        pem: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                pem: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.ChaosFaultProperties(_Model):
        action: Optional[Union[str, SupportedActions]]
        container_name: Optional[str]
        database_name: Optional[str]
        provisioning_state: Optional[str]
        region: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                action: Optional[Union[str, SupportedActions]] = ..., 
                container_name: Optional[str] = ..., 
                database_name: Optional[str] = ..., 
                region: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.ChaosFaultResource(ProxyResource):
        id: str
        name: str
        properties: Optional[ChaosFaultProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ChaosFaultProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.ClientEncryptionIncludedPath(_Model):
        client_encryption_key_id: str
        encryption_algorithm: str
        encryption_type: str
        path: str

        @overload
        def __init__(
                self, 
                *, 
                client_encryption_key_id: str, 
                encryption_algorithm: str, 
                encryption_type: str, 
                path: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.ClientEncryptionKeyCreateUpdateParameters(_Model):
        properties: ClientEncryptionKeyCreateUpdateProperties

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: ClientEncryptionKeyCreateUpdateProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.ClientEncryptionKeyCreateUpdateProperties(_Model):
        resource: ClientEncryptionKeyResource

        @overload
        def __init__(
                self, 
                *, 
                resource: ClientEncryptionKeyResource
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.ClientEncryptionKeyGetProperties(_Model):
        resource: Optional[ClientEncryptionKeyGetPropertiesResource]

        @overload
        def __init__(
                self, 
                *, 
                resource: Optional[ClientEncryptionKeyGetPropertiesResource] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.ClientEncryptionKeyGetPropertiesResource(ClientEncryptionKeyResource):
        encryption_algorithm: str
        etag: Optional[str]
        id: str
        key_wrap_metadata: KeyWrapMetadata
        rid: Optional[str]
        ts: Optional[float]
        wrapped_data_encryption_key: bytes

        @overload
        def __init__(
                self, 
                *, 
                encryption_algorithm: Optional[str] = ..., 
                id: Optional[str] = ..., 
                key_wrap_metadata: Optional[KeyWrapMetadata] = ..., 
                wrapped_data_encryption_key: Optional[bytes] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.ClientEncryptionKeyGetResults(ProxyResource):
        id: str
        name: str
        properties: Optional[ClientEncryptionKeyGetProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ClientEncryptionKeyGetProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.ClientEncryptionKeyResource(_Model):
        encryption_algorithm: Optional[str]
        id: Optional[str]
        key_wrap_metadata: Optional[KeyWrapMetadata]
        wrapped_data_encryption_key: Optional[bytes]

        @overload
        def __init__(
                self, 
                *, 
                encryption_algorithm: Optional[str] = ..., 
                id: Optional[str] = ..., 
                key_wrap_metadata: Optional[KeyWrapMetadata] = ..., 
                wrapped_data_encryption_key: Optional[bytes] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.ClientEncryptionPolicy(_Model):
        included_paths: list[ClientEncryptionIncludedPath]
        policy_format_version: int

        @overload
        def __init__(
                self, 
                *, 
                included_paths: list[ClientEncryptionIncludedPath], 
                policy_format_version: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.CloudError(_Model):
        error: Optional[ErrorResponseAutoGenerated]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorResponseAutoGenerated] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.ClusterKey(_Model):
        name: Optional[str]
        order_by: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                order_by: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.ClusterResource(ProxyResource):
        id: str
        identity: Optional[ManagedCassandraManagedServiceIdentity]
        location: Optional[str]
        name: str
        properties: Optional[ClusterResourceProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedCassandraManagedServiceIdentity] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[ClusterResourceProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.ClusterResourceProperties(_Model):
        authentication_method: Optional[Union[str, AuthenticationMethod]]
        auto_replicate: Optional[Union[str, AutoReplicate]]
        azure_connection_method: Optional[Union[str, AzureConnectionType]]
        backup_schedules: Optional[list[BackupSchedule]]
        cassandra_audit_logging_enabled: Optional[bool]
        cassandra_version: Optional[str]
        client_certificates: Optional[list[Certificate]]
        cluster_name_override: Optional[str]
        cluster_type: Optional[Union[str, ClusterType]]
        deallocated: Optional[bool]
        delegated_management_subnet_id: Optional[str]
        extensions: Optional[list[str]]
        external_data_centers: Optional[list[str]]
        external_gossip_certificates: Optional[list[Certificate]]
        external_seed_nodes: Optional[list[SeedNode]]
        gossip_certificates: Optional[list[Certificate]]
        hours_between_backups: Optional[int]
        initial_cassandra_admin_password: Optional[str]
        private_link_resource_id: Optional[str]
        prometheus_endpoint: Optional[SeedNode]
        provision_error: Optional[CassandraError]
        provisioning_state: Optional[Union[str, ManagedCassandraProvisioningState]]
        repair_enabled: Optional[bool]
        restore_from_backup_id: Optional[str]
        scheduled_event_strategy: Optional[Union[str, ScheduledEventStrategy]]
        seed_nodes: Optional[list[SeedNode]]

        @overload
        def __init__(
                self, 
                *, 
                authentication_method: Optional[Union[str, AuthenticationMethod]] = ..., 
                auto_replicate: Optional[Union[str, AutoReplicate]] = ..., 
                azure_connection_method: Optional[Union[str, AzureConnectionType]] = ..., 
                backup_schedules: Optional[list[BackupSchedule]] = ..., 
                cassandra_audit_logging_enabled: Optional[bool] = ..., 
                cassandra_version: Optional[str] = ..., 
                client_certificates: Optional[list[Certificate]] = ..., 
                cluster_name_override: Optional[str] = ..., 
                cluster_type: Optional[Union[str, ClusterType]] = ..., 
                deallocated: Optional[bool] = ..., 
                delegated_management_subnet_id: Optional[str] = ..., 
                extensions: Optional[list[str]] = ..., 
                external_data_centers: Optional[list[str]] = ..., 
                external_gossip_certificates: Optional[list[Certificate]] = ..., 
                external_seed_nodes: Optional[list[SeedNode]] = ..., 
                hours_between_backups: Optional[int] = ..., 
                initial_cassandra_admin_password: Optional[str] = ..., 
                prometheus_endpoint: Optional[SeedNode] = ..., 
                provision_error: Optional[CassandraError] = ..., 
                provisioning_state: Optional[Union[str, ManagedCassandraProvisioningState]] = ..., 
                repair_enabled: Optional[bool] = ..., 
                restore_from_backup_id: Optional[str] = ..., 
                scheduled_event_strategy: Optional[Union[str, ScheduledEventStrategy]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.ClusterType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NON_PRODUCTION = "NonProduction"
        PRODUCTION = "Production"


    class azure.mgmt.cosmosdb.models.Column(_Model):
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


    class azure.mgmt.cosmosdb.models.CommandAsyncPostBody(_Model):
        arguments: Optional[Any]
        cassandra_stop_start: Optional[bool]
        command: str
        host: str
        read_write: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                arguments: Optional[Any] = ..., 
                cassandra_stop_start: Optional[bool] = ..., 
                command: str, 
                host: str, 
                read_write: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.CommandOutput(_Model):
        command_output: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                command_output: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.CommandPostBody(_Model):
        arguments: Optional[dict[str, str]]
        cassandra_stop_start: Optional[bool]
        command: str
        host: str
        readwrite: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                arguments: Optional[dict[str, str]] = ..., 
                cassandra_stop_start: Optional[bool] = ..., 
                command: str, 
                host: str, 
                readwrite: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.CommandPublicResource(_Model):
        arguments: Optional[Any]
        cassandra_stop_start: Optional[bool]
        command: Optional[str]
        command_id: Optional[str]
        host: Optional[str]
        is_admin: Optional[bool]
        output_file: Optional[str]
        read_write: Optional[bool]
        result: Optional[str]
        status: Optional[Union[str, CommandStatus]]

        @overload
        def __init__(
                self, 
                *, 
                arguments: Optional[Any] = ..., 
                cassandra_stop_start: Optional[bool] = ..., 
                command: Optional[str] = ..., 
                command_id: Optional[str] = ..., 
                host: Optional[str] = ..., 
                is_admin: Optional[bool] = ..., 
                output_file: Optional[str] = ..., 
                read_write: Optional[bool] = ..., 
                result: Optional[str] = ..., 
                status: Optional[Union[str, CommandStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.CommandStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DONE = "Done"
        ENQUEUE = "Enqueue"
        FAILED = "Failed"
        FINISHED = "Finished"
        PROCESSING = "Processing"
        RUNNING = "Running"


    class azure.mgmt.cosmosdb.models.CompositePath(_Model):
        order: Optional[Union[str, CompositePathSortOrder]]
        path: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                order: Optional[Union[str, CompositePathSortOrder]] = ..., 
                path: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.CompositePathSortOrder(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASCENDING = "ascending"
        DESCENDING = "descending"


    class azure.mgmt.cosmosdb.models.ComputedProperty(_Model):
        name: Optional[str]
        query: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                query: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.ConflictResolutionMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM = "Custom"
        LAST_WRITER_WINS = "LastWriterWins"


    class azure.mgmt.cosmosdb.models.ConflictResolutionPolicy(_Model):
        conflict_resolution_path: Optional[str]
        conflict_resolution_procedure: Optional[str]
        mode: Optional[Union[str, ConflictResolutionMode]]

        @overload
        def __init__(
                self, 
                *, 
                conflict_resolution_path: Optional[str] = ..., 
                conflict_resolution_procedure: Optional[str] = ..., 
                mode: Optional[Union[str, ConflictResolutionMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.ConnectionError(_Model):
        connection_state: Optional[Union[str, ConnectionState]]
        exception: Optional[str]
        i_p_from: Optional[str]
        i_p_to: Optional[str]
        port: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                connection_state: Optional[Union[str, ConnectionState]] = ..., 
                exception: Optional[str] = ..., 
                i_p_from: Optional[str] = ..., 
                i_p_to: Optional[str] = ..., 
                port: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.ConnectionState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DATACENTER_TO_DATACENTER_NETWORK_ERROR = "DatacenterToDatacenterNetworkError"
        INTERNAL_ERROR = "InternalError"
        INTERNAL_OPERATOR_TO_DATA_CENTER_CERTIFICATE_ERROR = "InternalOperatorToDataCenterCertificateError"
        OK = "OK"
        OPERATOR_TO_DATA_CENTER_NETWORK_ERROR = "OperatorToDataCenterNetworkError"
        UNKNOWN = "Unknown"


    class azure.mgmt.cosmosdb.models.ConnectorOffer(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SMALL = "Small"


    class azure.mgmt.cosmosdb.models.ConsistencyPolicy(_Model):
        default_consistency_level: Union[str, DefaultConsistencyLevel]
        max_interval_in_seconds: Optional[int]
        max_staleness_prefix: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                default_consistency_level: Union[str, DefaultConsistencyLevel], 
                max_interval_in_seconds: Optional[int] = ..., 
                max_staleness_prefix: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.ContainerPartitionKey(_Model):
        kind: Optional[Union[str, PartitionKind]]
        paths: Optional[list[str]]
        system_key: Optional[bool]
        version: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                kind: Optional[Union[str, PartitionKind]] = ..., 
                paths: Optional[list[str]] = ..., 
                version: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.ContinuousBackupInformation(_Model):
        latest_restorable_timestamp: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                latest_restorable_timestamp: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.ContinuousBackupRestoreLocation(_Model):
        location: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.ContinuousModeBackupPolicy(BackupPolicy, discriminator='Continuous'):
        continuous_mode_properties: Optional[ContinuousModeProperties]
        migration_state: BackupPolicyMigrationState
        type: Literal[BackupPolicyType.CONTINUOUS]

        @overload
        def __init__(
                self, 
                *, 
                continuous_mode_properties: Optional[ContinuousModeProperties] = ..., 
                migration_state: Optional[BackupPolicyMigrationState] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.ContinuousModeProperties(_Model):
        tier: Optional[Union[str, ContinuousTier]]

        @overload
        def __init__(
                self, 
                *, 
                tier: Optional[Union[str, ContinuousTier]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.ContinuousTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTINUOUS30_DAYS = "Continuous30Days"
        CONTINUOUS35_DAYS = "Continuous35Days"
        CONTINUOUS7_DAYS = "Continuous7Days"


    class azure.mgmt.cosmosdb.models.CopyJobGetResults(ProxyResource):
        id: str
        name: str
        properties: CopyJobProperties
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: CopyJobProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.CopyJobMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OFFLINE = "Offline"
        ONLINE = "Online"


    class azure.mgmt.cosmosdb.models.CopyJobProperties(_Model):
        duration: Optional[str]
        error: Optional[ErrorResponse]
        job_properties: BaseCopyJobProperties
        last_updated_utc_time: Optional[datetime]
        mode: Optional[Union[str, CopyJobMode]]
        processed_count: Optional[int]
        status: Optional[Union[str, CopyJobStatus]]
        total_count: Optional[int]
        worker_count: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                job_properties: BaseCopyJobProperties, 
                mode: Optional[Union[str, CopyJobMode]] = ..., 
                worker_count: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.CopyJobStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELLED = "Cancelled"
        COMPLETED = "Completed"
        FAULTED = "Faulted"
        PARTITIONING = "Partitioning"
        PAUSED = "Paused"
        PENDING = "Pending"
        RUNNING = "Running"


    class azure.mgmt.cosmosdb.models.CopyJobType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_BLOB_STORAGE_TO_CASSANDRA_RU = "AzureBlobStorageToCassandraRU"
        CASSANDRA_RU_TO_AZURE_BLOB_STORAGE = "CassandraRUToAzureBlobStorage"
        CASSANDRA_RU_TO_CASSANDRA_RU = "CassandraRUToCassandraRU"
        MONGO_RU_TO_MONGO_RU = "MongoRUToMongoRU"
        MONGO_RU_TO_MONGO_V_CORE = "MongoRUToMongoVCore"
        NO_SQL_RU_TO_NO_SQL_RU = "NoSqlRUToNoSqlRU"


    class azure.mgmt.cosmosdb.models.CorsPolicy(_Model):
        allowed_headers: Optional[str]
        allowed_methods: Optional[str]
        allowed_origins: str
        exposed_headers: Optional[str]
        max_age_in_seconds: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                allowed_headers: Optional[str] = ..., 
                allowed_methods: Optional[str] = ..., 
                allowed_origins: str, 
                exposed_headers: Optional[str] = ..., 
                max_age_in_seconds: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.CosmosCassandraDataTransferDataSourceSink(BaseCosmosDataTransferDataSourceSink, discriminator='CosmosDBCassandra'):
        component: Literal[DataTransferComponent.COSMOS_DB_CASSANDRA]
        keyspace_name: str
        remote_account_name: str
        table_name: str

        @overload
        def __init__(
                self, 
                *, 
                keyspace_name: str, 
                remote_account_name: Optional[str] = ..., 
                table_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.CosmosDBCassandraTable(_Model):
        keyspace_name: str
        table_name: str

        @overload
        def __init__(
                self, 
                *, 
                keyspace_name: str, 
                table_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.CosmosDBMongoCollection(_Model):
        collection_name: str
        database_name: str

        @overload
        def __init__(
                self, 
                *, 
                collection_name: str, 
                database_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.CosmosDBMongoVCoreCollection(_Model):
        collection_name: str
        database_name: str

        @overload
        def __init__(
                self, 
                *, 
                collection_name: str, 
                database_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.CosmosDBNoSqlContainer(_Model):
        container_name: str
        database_name: str

        @overload
        def __init__(
                self, 
                *, 
                container_name: str, 
                database_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.CosmosDBSourceSinkDetails(_Model):
        remote_account_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                remote_account_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.CosmosMongoDataTransferDataSourceSink(BaseCosmosDataTransferDataSourceSink, discriminator='CosmosDBMongo'):
        collection_name: str
        component: Literal[DataTransferComponent.COSMOS_DB_MONGO]
        database_name: str
        remote_account_name: str

        @overload
        def __init__(
                self, 
                *, 
                collection_name: str, 
                database_name: str, 
                remote_account_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.CosmosMongoVCoreDataTransferDataSourceSink(DataTransferDataSourceSink, discriminator='CosmosDBMongoVCore'):
        collection_name: str
        component: Literal[DataTransferComponent.COSMOS_DB_MONGO_V_CORE]
        connection_string_key_vault_uri: Optional[str]
        database_name: str
        host_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                collection_name: str, 
                connection_string_key_vault_uri: Optional[str] = ..., 
                database_name: str, 
                host_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.CosmosSqlDataTransferDataSourceSink(BaseCosmosDataTransferDataSourceSink, discriminator='CosmosDBSql'):
        component: Literal[DataTransferComponent.COSMOS_DB_SQL]
        container_name: str
        database_name: str
        remote_account_name: str

        @overload
        def __init__(
                self, 
                *, 
                container_name: str, 
                database_name: str, 
                remote_account_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.CreateJobRequest(ARMProxyResource):
        id: str
        name: str
        properties: DataTransferJobProperties
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: DataTransferJobProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.CreateMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "Default"
        RESTORE = "Restore"


    class azure.mgmt.cosmosdb.models.CreateUpdateOptions(_Model):
        autoscale_settings: Optional[AutoscaleSettings]
        throughput: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                autoscale_settings: Optional[AutoscaleSettings] = ..., 
                throughput: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.cosmosdb.models.DataCenterResource(ProxyResource):
        id: str
        name: str
        properties: Optional[DataCenterResourceProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DataCenterResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.DataCenterResourceProperties(_Model):
        authentication_method_ldap_properties: Optional[AuthenticationMethodLdapProperties]
        availability_zone: Optional[bool]
        backup_storage_customer_key_uri: Optional[str]
        base64_encoded_cassandra_yaml_fragment: Optional[str]
        data_center_location: Optional[str]
        deallocated: Optional[bool]
        delegated_subnet_id: Optional[str]
        disk_capacity: Optional[int]
        disk_sku: Optional[str]
        managed_disk_customer_key_uri: Optional[str]
        node_count: Optional[int]
        private_endpoint_ip_address: Optional[str]
        provision_error: Optional[CassandraError]
        provisioning_state: Optional[Union[str, ManagedCassandraProvisioningState]]
        seed_nodes: Optional[list[SeedNode]]
        sku: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                authentication_method_ldap_properties: Optional[AuthenticationMethodLdapProperties] = ..., 
                availability_zone: Optional[bool] = ..., 
                backup_storage_customer_key_uri: Optional[str] = ..., 
                base64_encoded_cassandra_yaml_fragment: Optional[str] = ..., 
                data_center_location: Optional[str] = ..., 
                deallocated: Optional[bool] = ..., 
                delegated_subnet_id: Optional[str] = ..., 
                disk_capacity: Optional[int] = ..., 
                disk_sku: Optional[str] = ..., 
                managed_disk_customer_key_uri: Optional[str] = ..., 
                node_count: Optional[int] = ..., 
                private_endpoint_ip_address: Optional[str] = ..., 
                provision_error: Optional[CassandraError] = ..., 
                provisioning_state: Optional[Union[str, ManagedCassandraProvisioningState]] = ..., 
                sku: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.DataMaskingPolicy(_Model):
        excluded_paths: Optional[list[DataMaskingPolicyExcludedPathsItem]]
        included_paths: Optional[list[DataMaskingPolicyIncludedPathsItem]]
        is_policy_enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                excluded_paths: Optional[list[DataMaskingPolicyExcludedPathsItem]] = ..., 
                included_paths: Optional[list[DataMaskingPolicyIncludedPathsItem]] = ..., 
                is_policy_enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.DataMaskingPolicyExcludedPathsItem(_Model):
        path: str

        @overload
        def __init__(
                self, 
                *, 
                path: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.DataMaskingPolicyIncludedPathsItem(_Model):
        length: Optional[int]
        path: str
        start_position: Optional[int]
        strategy: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                length: Optional[int] = ..., 
                path: str, 
                start_position: Optional[int] = ..., 
                strategy: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.DataTransferComponent(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_BLOB_STORAGE = "AzureBlobStorage"
        BASE_COSMOS_DATA_TRANSFER_DATA_SOURCE_SINK = "BaseCosmosDataTransferDataSourceSink"
        COSMOS_DB_CASSANDRA = "CosmosDBCassandra"
        COSMOS_DB_MONGO = "CosmosDBMongo"
        COSMOS_DB_MONGO_V_CORE = "CosmosDBMongoVCore"
        COSMOS_DB_SQL = "CosmosDBSql"


    class azure.mgmt.cosmosdb.models.DataTransferDataSourceSink(_Model):
        component: str

        @overload
        def __init__(
                self, 
                *, 
                component: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.DataTransferJobGetResults(ProxyResource):
        id: str
        name: str
        properties: Optional[DataTransferJobProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DataTransferJobProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.DataTransferJobMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OFFLINE = "Offline"
        ONLINE = "Online"


    class azure.mgmt.cosmosdb.models.DataTransferJobProperties(_Model):
        destination: DataTransferDataSourceSink
        duration: Optional[str]
        error: Optional[ErrorResponseAutoGenerated]
        job_name: Optional[str]
        last_updated_utc_time: Optional[datetime]
        mode: Optional[Union[str, DataTransferJobMode]]
        processed_count: Optional[int]
        source: DataTransferDataSourceSink
        status: Optional[str]
        total_count: Optional[int]
        worker_count: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                destination: DataTransferDataSourceSink, 
                mode: Optional[Union[str, DataTransferJobMode]] = ..., 
                source: DataTransferDataSourceSink, 
                worker_count: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.DataTransferRegionalServiceResource(RegionalServiceResource):
        location: str
        name: str
        status: Union[str, ServiceStatus]


    class azure.mgmt.cosmosdb.models.DataTransferServiceResourceCreateUpdateProperties(ServiceResourceCreateUpdateProperties, discriminator='DataTransfer'):
        instance_count: int
        instance_size: Union[str, ServiceSize]
        service_type: Literal[ServiceType.DATA_TRANSFER]

        @overload
        def __init__(
                self, 
                *, 
                instance_count: Optional[int] = ..., 
                instance_size: Optional[Union[str, ServiceSize]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.DataTransferServiceResourceProperties(ServiceResourceProperties, discriminator='DataTransfer'):
        creation_time: datetime
        instance_count: int
        instance_size: Union[str, ServiceSize]
        locations: Optional[list[DataTransferRegionalServiceResource]]
        service_type: Literal[ServiceType.DATA_TRANSFER]
        status: Union[str, ServiceStatus]

        @overload
        def __init__(
                self, 
                *, 
                instance_count: Optional[int] = ..., 
                instance_size: Optional[Union[str, ServiceSize]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.DataType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LINE_STRING = "LineString"
        MULTI_POLYGON = "MultiPolygon"
        NUMBER = "Number"
        POINT = "Point"
        POLYGON = "Polygon"
        STRING = "String"


    class azure.mgmt.cosmosdb.models.DatabaseAccountConnectionString(_Model):
        connection_string: Optional[str]
        description: Optional[str]
        key_kind: Optional[Union[str, Kind]]
        type: Optional[Union[str, Type]]


    class azure.mgmt.cosmosdb.models.DatabaseAccountCreateUpdateParameters(ARMResourceProperties):
        id: str
        identity: ManagedServiceIdentity
        kind: Optional[Union[str, DatabaseAccountKind]]
        location: str
        name: str
        properties: DatabaseAccountCreateUpdateProperties
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                kind: Optional[Union[str, DatabaseAccountKind]] = ..., 
                location: Optional[str] = ..., 
                properties: DatabaseAccountCreateUpdateProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.DatabaseAccountCreateUpdateProperties(_Model):
        analytical_storage_configuration: Optional[AnalyticalStorageConfiguration]
        api_properties: Optional[ApiProperties]
        backup_policy: Optional[BackupPolicy]
        capabilities: Optional[list[Capability]]
        capacity: Optional[Capacity]
        capacity_mode: Optional[Union[str, CapacityMode]]
        connector_offer: Optional[Union[str, ConnectorOffer]]
        consistency_policy: Optional[ConsistencyPolicy]
        cors: Optional[list[CorsPolicy]]
        create_mode: Optional[Union[str, CreateMode]]
        customer_managed_key_status: Optional[str]
        database_account_offer_type: Literal["Standard"]
        default_identity: Optional[str]
        default_priority_level: Optional[Union[str, DefaultPriorityLevel]]
        diagnostic_log_settings: Optional[DiagnosticLogSettings]
        disable_key_based_metadata_write_access: Optional[bool]
        disable_local_auth: Optional[bool]
        enable_all_versions_and_deletes_change_feed: Optional[bool]
        enable_analytical_storage: Optional[bool]
        enable_automatic_failover: Optional[bool]
        enable_burst_capacity: Optional[bool]
        enable_cassandra_connector: Optional[bool]
        enable_free_tier: Optional[bool]
        enable_materialized_views: Optional[bool]
        enable_multiple_write_locations: Optional[bool]
        enable_partition_merge: Optional[bool]
        enable_per_region_per_partition_autoscale: Optional[bool]
        enable_priority_based_execution: Optional[bool]
        enforce_hierarchical_partition_key_id_last_level: Optional[bool]
        ip_rules: Optional[list[IpAddressOrRange]]
        is_virtual_network_filter_enabled: Optional[bool]
        key_vault_key_uri: Optional[str]
        keys_metadata: Optional[DatabaseAccountKeysMetadata]
        locations: list[Location]
        minimal_tls_version: Optional[Union[str, MinimalTlsVersion]]
        network_acl_bypass: Optional[Union[str, NetworkAclBypass]]
        network_acl_bypass_resource_ids: Optional[list[str]]
        public_network_access: Optional[Union[str, PublicNetworkAccess]]
        restore_parameters: Optional[RestoreParameters]
        soft_delete_configuration: Optional[SoftDeleteConfiguration]
        virtual_network_rules: Optional[list[VirtualNetworkRule]]

        @overload
        def __init__(
                self, 
                *, 
                analytical_storage_configuration: Optional[AnalyticalStorageConfiguration] = ..., 
                api_properties: Optional[ApiProperties] = ..., 
                backup_policy: Optional[BackupPolicy] = ..., 
                capabilities: Optional[list[Capability]] = ..., 
                capacity: Optional[Capacity] = ..., 
                capacity_mode: Optional[Union[str, CapacityMode]] = ..., 
                connector_offer: Optional[Union[str, ConnectorOffer]] = ..., 
                consistency_policy: Optional[ConsistencyPolicy] = ..., 
                cors: Optional[list[CorsPolicy]] = ..., 
                create_mode: Optional[Union[str, CreateMode]] = ..., 
                customer_managed_key_status: Optional[str] = ..., 
                default_identity: Optional[str] = ..., 
                default_priority_level: Optional[Union[str, DefaultPriorityLevel]] = ..., 
                diagnostic_log_settings: Optional[DiagnosticLogSettings] = ..., 
                disable_key_based_metadata_write_access: Optional[bool] = ..., 
                disable_local_auth: Optional[bool] = ..., 
                enable_all_versions_and_deletes_change_feed: Optional[bool] = ..., 
                enable_analytical_storage: Optional[bool] = ..., 
                enable_automatic_failover: Optional[bool] = ..., 
                enable_burst_capacity: Optional[bool] = ..., 
                enable_cassandra_connector: Optional[bool] = ..., 
                enable_free_tier: Optional[bool] = ..., 
                enable_materialized_views: Optional[bool] = ..., 
                enable_multiple_write_locations: Optional[bool] = ..., 
                enable_partition_merge: Optional[bool] = ..., 
                enable_per_region_per_partition_autoscale: Optional[bool] = ..., 
                enable_priority_based_execution: Optional[bool] = ..., 
                enforce_hierarchical_partition_key_id_last_level: Optional[bool] = ..., 
                ip_rules: Optional[list[IpAddressOrRange]] = ..., 
                is_virtual_network_filter_enabled: Optional[bool] = ..., 
                key_vault_key_uri: Optional[str] = ..., 
                locations: list[Location], 
                minimal_tls_version: Optional[Union[str, MinimalTlsVersion]] = ..., 
                network_acl_bypass: Optional[Union[str, NetworkAclBypass]] = ..., 
                network_acl_bypass_resource_ids: Optional[list[str]] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                restore_parameters: Optional[RestoreParameters] = ..., 
                soft_delete_configuration: Optional[SoftDeleteConfiguration] = ..., 
                virtual_network_rules: Optional[list[VirtualNetworkRule]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.DatabaseAccountGetProperties(_Model):
        analytical_storage_configuration: Optional[AnalyticalStorageConfiguration]
        api_properties: Optional[ApiProperties]
        backup_policy: Optional[BackupPolicy]
        capabilities: Optional[list[Capability]]
        capacity: Optional[Capacity]
        capacity_mode: Optional[Union[str, CapacityMode]]
        capacity_mode_change_transition_state: Optional[CapacityModeChangeTransitionState]
        connector_offer: Optional[Union[str, ConnectorOffer]]
        consistency_policy: Optional[ConsistencyPolicy]
        cors: Optional[list[CorsPolicy]]
        create_mode: Optional[Union[str, CreateMode]]
        customer_managed_key_status: Optional[str]
        database_account_offer_type: Optional[Literal["Standard"]]
        default_identity: Optional[str]
        default_priority_level: Optional[Union[str, DefaultPriorityLevel]]
        diagnostic_log_settings: Optional[DiagnosticLogSettings]
        disable_key_based_metadata_write_access: Optional[bool]
        disable_local_auth: Optional[bool]
        document_endpoint: Optional[str]
        enable_all_versions_and_deletes_change_feed: Optional[bool]
        enable_analytical_storage: Optional[bool]
        enable_automatic_failover: Optional[bool]
        enable_burst_capacity: Optional[bool]
        enable_cassandra_connector: Optional[bool]
        enable_free_tier: Optional[bool]
        enable_materialized_views: Optional[bool]
        enable_multiple_write_locations: Optional[bool]
        enable_partition_merge: Optional[bool]
        enable_per_region_per_partition_autoscale: Optional[bool]
        enable_priority_based_execution: Optional[bool]
        enforce_hierarchical_partition_key_id_last_level: Optional[bool]
        failover_policies: Optional[list[FailoverPolicy]]
        instance_id: Optional[str]
        ip_rules: Optional[list[IpAddressOrRange]]
        is_virtual_network_filter_enabled: Optional[bool]
        key_vault_key_uri: Optional[str]
        key_vault_key_uri_version: Optional[str]
        keys_metadata: Optional[DatabaseAccountKeysMetadata]
        locations: Optional[list[Location]]
        minimal_tls_version: Optional[Union[str, MinimalTlsVersion]]
        network_acl_bypass: Optional[Union[str, NetworkAclBypass]]
        network_acl_bypass_resource_ids: Optional[list[str]]
        private_endpoint_connections: Optional[list[PrivateEndpointConnection]]
        provisioning_state: Optional[str]
        public_network_access: Optional[Union[str, PublicNetworkAccess]]
        read_locations: Optional[list[Location]]
        restore_parameters: Optional[RestoreParameters]
        soft_delete_configuration: Optional[SoftDeleteConfiguration]
        throughput_pool_dedicated_r_us: Optional[int]
        throughput_pool_max_consumable_r_us: Optional[int]
        virtual_network_rules: Optional[list[VirtualNetworkRule]]
        write_locations: Optional[list[Location]]

        @overload
        def __init__(
                self, 
                *, 
                analytical_storage_configuration: Optional[AnalyticalStorageConfiguration] = ..., 
                api_properties: Optional[ApiProperties] = ..., 
                backup_policy: Optional[BackupPolicy] = ..., 
                capabilities: Optional[list[Capability]] = ..., 
                capacity: Optional[Capacity] = ..., 
                capacity_mode: Optional[Union[str, CapacityMode]] = ..., 
                capacity_mode_change_transition_state: Optional[CapacityModeChangeTransitionState] = ..., 
                connector_offer: Optional[Union[str, ConnectorOffer]] = ..., 
                consistency_policy: Optional[ConsistencyPolicy] = ..., 
                cors: Optional[list[CorsPolicy]] = ..., 
                create_mode: Optional[Union[str, CreateMode]] = ..., 
                customer_managed_key_status: Optional[str] = ..., 
                default_identity: Optional[str] = ..., 
                default_priority_level: Optional[Union[str, DefaultPriorityLevel]] = ..., 
                diagnostic_log_settings: Optional[DiagnosticLogSettings] = ..., 
                disable_key_based_metadata_write_access: Optional[bool] = ..., 
                disable_local_auth: Optional[bool] = ..., 
                enable_all_versions_and_deletes_change_feed: Optional[bool] = ..., 
                enable_analytical_storage: Optional[bool] = ..., 
                enable_automatic_failover: Optional[bool] = ..., 
                enable_burst_capacity: Optional[bool] = ..., 
                enable_cassandra_connector: Optional[bool] = ..., 
                enable_free_tier: Optional[bool] = ..., 
                enable_materialized_views: Optional[bool] = ..., 
                enable_multiple_write_locations: Optional[bool] = ..., 
                enable_partition_merge: Optional[bool] = ..., 
                enable_per_region_per_partition_autoscale: Optional[bool] = ..., 
                enable_priority_based_execution: Optional[bool] = ..., 
                enforce_hierarchical_partition_key_id_last_level: Optional[bool] = ..., 
                ip_rules: Optional[list[IpAddressOrRange]] = ..., 
                is_virtual_network_filter_enabled: Optional[bool] = ..., 
                key_vault_key_uri: Optional[str] = ..., 
                minimal_tls_version: Optional[Union[str, MinimalTlsVersion]] = ..., 
                network_acl_bypass: Optional[Union[str, NetworkAclBypass]] = ..., 
                network_acl_bypass_resource_ids: Optional[list[str]] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                restore_parameters: Optional[RestoreParameters] = ..., 
                soft_delete_configuration: Optional[SoftDeleteConfiguration] = ..., 
                throughput_pool_dedicated_r_us: Optional[int] = ..., 
                throughput_pool_max_consumable_r_us: Optional[int] = ..., 
                virtual_network_rules: Optional[list[VirtualNetworkRule]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.DatabaseAccountGetResults(ProxyResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        kind: Optional[Union[str, DatabaseAccountKind]]
        location: Optional[str]
        name: str
        properties: Optional[DatabaseAccountGetProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                kind: Optional[Union[str, DatabaseAccountKind]] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[DatabaseAccountGetProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.DatabaseAccountKeysMetadata(_Model):
        primary_master_key: Optional[AccountKeyMetadata]
        primary_readonly_master_key: Optional[AccountKeyMetadata]
        secondary_master_key: Optional[AccountKeyMetadata]
        secondary_readonly_master_key: Optional[AccountKeyMetadata]


    class azure.mgmt.cosmosdb.models.DatabaseAccountKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GLOBAL_DOCUMENT_DB = "GlobalDocumentDB"
        MONGO_DB = "MongoDB"
        PARSE = "Parse"


    class azure.mgmt.cosmosdb.models.DatabaseAccountListConnectionStringsResult(_Model):
        connection_strings: Optional[list[DatabaseAccountConnectionString]]

        @overload
        def __init__(
                self, 
                *, 
                connection_strings: Optional[list[DatabaseAccountConnectionString]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.DatabaseAccountListKeysResult(DatabaseAccountListReadOnlyKeysResult):
        primary_master_key: Optional[str]
        primary_readonly_master_key: str
        secondary_master_key: Optional[str]
        secondary_readonly_master_key: str


    class azure.mgmt.cosmosdb.models.DatabaseAccountListReadOnlyKeysResult(_Model):
        primary_readonly_master_key: Optional[str]
        secondary_readonly_master_key: Optional[str]


    class azure.mgmt.cosmosdb.models.DatabaseAccountRegenerateKeyParameters(_Model):
        key_kind: Union[str, KeyKind]
        skip_account_keys_last_usage_check: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                key_kind: Union[str, KeyKind], 
                skip_account_keys_last_usage_check: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.DatabaseAccountUpdateParameters(_Model):
        identity: Optional[ManagedServiceIdentity]
        location: Optional[str]
        properties: Optional[DatabaseAccountUpdateProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[DatabaseAccountUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.DatabaseAccountUpdateProperties(_Model):
        analytical_storage_configuration: Optional[AnalyticalStorageConfiguration]
        api_properties: Optional[ApiProperties]
        backup_policy: Optional[BackupPolicy]
        capabilities: Optional[list[Capability]]
        capacity: Optional[Capacity]
        capacity_mode: Optional[Union[str, CapacityMode]]
        connector_offer: Optional[Union[str, ConnectorOffer]]
        consistency_policy: Optional[ConsistencyPolicy]
        cors: Optional[list[CorsPolicy]]
        customer_managed_key_status: Optional[str]
        default_identity: Optional[str]
        default_priority_level: Optional[Union[str, DefaultPriorityLevel]]
        diagnostic_log_settings: Optional[DiagnosticLogSettings]
        disable_key_based_metadata_write_access: Optional[bool]
        disable_local_auth: Optional[bool]
        enable_all_versions_and_deletes_change_feed: Optional[bool]
        enable_analytical_storage: Optional[bool]
        enable_automatic_failover: Optional[bool]
        enable_burst_capacity: Optional[bool]
        enable_cassandra_connector: Optional[bool]
        enable_free_tier: Optional[bool]
        enable_materialized_views: Optional[bool]
        enable_multiple_write_locations: Optional[bool]
        enable_partition_merge: Optional[bool]
        enable_per_region_per_partition_autoscale: Optional[bool]
        enable_priority_based_execution: Optional[bool]
        enforce_hierarchical_partition_key_id_last_level: Optional[bool]
        ip_rules: Optional[list[IpAddressOrRange]]
        is_virtual_network_filter_enabled: Optional[bool]
        key_vault_key_uri: Optional[str]
        keys_metadata: Optional[DatabaseAccountKeysMetadata]
        locations: Optional[list[Location]]
        minimal_tls_version: Optional[Union[str, MinimalTlsVersion]]
        network_acl_bypass: Optional[Union[str, NetworkAclBypass]]
        network_acl_bypass_resource_ids: Optional[list[str]]
        public_network_access: Optional[Union[str, PublicNetworkAccess]]
        soft_delete_configuration: Optional[SoftDeleteConfiguration]
        virtual_network_rules: Optional[list[VirtualNetworkRule]]

        @overload
        def __init__(
                self, 
                *, 
                analytical_storage_configuration: Optional[AnalyticalStorageConfiguration] = ..., 
                api_properties: Optional[ApiProperties] = ..., 
                backup_policy: Optional[BackupPolicy] = ..., 
                capabilities: Optional[list[Capability]] = ..., 
                capacity: Optional[Capacity] = ..., 
                capacity_mode: Optional[Union[str, CapacityMode]] = ..., 
                connector_offer: Optional[Union[str, ConnectorOffer]] = ..., 
                consistency_policy: Optional[ConsistencyPolicy] = ..., 
                cors: Optional[list[CorsPolicy]] = ..., 
                customer_managed_key_status: Optional[str] = ..., 
                default_identity: Optional[str] = ..., 
                default_priority_level: Optional[Union[str, DefaultPriorityLevel]] = ..., 
                diagnostic_log_settings: Optional[DiagnosticLogSettings] = ..., 
                disable_key_based_metadata_write_access: Optional[bool] = ..., 
                disable_local_auth: Optional[bool] = ..., 
                enable_all_versions_and_deletes_change_feed: Optional[bool] = ..., 
                enable_analytical_storage: Optional[bool] = ..., 
                enable_automatic_failover: Optional[bool] = ..., 
                enable_burst_capacity: Optional[bool] = ..., 
                enable_cassandra_connector: Optional[bool] = ..., 
                enable_free_tier: Optional[bool] = ..., 
                enable_materialized_views: Optional[bool] = ..., 
                enable_multiple_write_locations: Optional[bool] = ..., 
                enable_partition_merge: Optional[bool] = ..., 
                enable_per_region_per_partition_autoscale: Optional[bool] = ..., 
                enable_priority_based_execution: Optional[bool] = ..., 
                enforce_hierarchical_partition_key_id_last_level: Optional[bool] = ..., 
                ip_rules: Optional[list[IpAddressOrRange]] = ..., 
                is_virtual_network_filter_enabled: Optional[bool] = ..., 
                key_vault_key_uri: Optional[str] = ..., 
                locations: Optional[list[Location]] = ..., 
                minimal_tls_version: Optional[Union[str, MinimalTlsVersion]] = ..., 
                network_acl_bypass: Optional[Union[str, NetworkAclBypass]] = ..., 
                network_acl_bypass_resource_ids: Optional[list[str]] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                soft_delete_configuration: Optional[SoftDeleteConfiguration] = ..., 
                virtual_network_rules: Optional[list[VirtualNetworkRule]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.DatabaseRestoreResource(_Model):
        collection_names: Optional[list[str]]
        database_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                collection_names: Optional[list[str]] = ..., 
                database_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.DedicatedGatewayType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISTRIBUTED_QUERY = "DistributedQuery"
        INTEGRATED_CACHE = "IntegratedCache"


    class azure.mgmt.cosmosdb.models.DefaultConsistencyLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BOUNDED_STALENESS = "BoundedStaleness"
        CONSISTENT_PREFIX = "ConsistentPrefix"
        EVENTUAL = "Eventual"
        SESSION = "Session"
        STRONG = "Strong"


    class azure.mgmt.cosmosdb.models.DefaultPriorityLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "High"
        LOW = "Low"


    class azure.mgmt.cosmosdb.models.DiagnosticLogSettings(_Model):
        enable_full_text_query: Optional[Union[str, EnableFullTextQuery]]

        @overload
        def __init__(
                self, 
                *, 
                enable_full_text_query: Optional[Union[str, EnableFullTextQuery]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.DistanceFunction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COSINE = "cosine"
        DOTPRODUCT = "dotproduct"
        EUCLIDEAN = "euclidean"


    class azure.mgmt.cosmosdb.models.EnableFullTextQuery(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "False"
        NONE = "None"
        TRUE = "True"


    class azure.mgmt.cosmosdb.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.cosmosdb.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.cosmosdb.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.ErrorResponseAutoGenerated(_Model):
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


    class azure.mgmt.cosmosdb.models.ExcludedPath(_Model):
        path: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                path: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.FailoverPolicies(_Model):
        failover_policies: list[FailoverPolicy]

        @overload
        def __init__(
                self, 
                *, 
                failover_policies: list[FailoverPolicy]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.FailoverPolicy(_Model):
        failover_priority: Optional[int]
        id: Optional[str]
        location_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                failover_priority: Optional[int] = ..., 
                location_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.FleetAnalyticsProperties(_Model):
        provisioning_state: Optional[Union[str, Status]]
        storage_location_type: Optional[Union[str, FleetAnalyticsPropertiesStorageLocationType]]
        storage_location_uri: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                storage_location_type: Optional[Union[str, FleetAnalyticsPropertiesStorageLocationType]] = ..., 
                storage_location_uri: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.FleetAnalyticsPropertiesStorageLocationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FABRIC_LAKEHOUSE = "FabricLakehouse"
        STORAGE_ACCOUNT = "StorageAccount"


    class azure.mgmt.cosmosdb.models.FleetAnalyticsResource(ProxyResource):
        id: str
        name: str
        properties: Optional[FleetAnalyticsProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[FleetAnalyticsProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.FleetResource(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[FleetResourceProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[FleetResourceProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.FleetResourceProperties(_Model):
        provisioning_state: Optional[Union[str, Status]]


    class azure.mgmt.cosmosdb.models.FleetResourceUpdate(_Model):
        properties: Optional[FleetResourceProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[FleetResourceProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.FleetspaceAccountProperties(_Model):
        global_database_account_properties: Optional[FleetspaceAccountPropertiesGlobalDatabaseAccountProperties]
        provisioning_state: Optional[Union[str, Status]]

        @overload
        def __init__(
                self, 
                *, 
                global_database_account_properties: Optional[FleetspaceAccountPropertiesGlobalDatabaseAccountProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.FleetspaceAccountPropertiesGlobalDatabaseAccountProperties(_Model):
        arm_location: Optional[str]
        resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                arm_location: Optional[str] = ..., 
                resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.FleetspaceAccountResource(ProxyResource):
        id: str
        name: str
        properties: Optional[FleetspaceAccountProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[FleetspaceAccountProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.FleetspaceProperties(_Model):
        data_regions: Optional[list[str]]
        fleetspace_api_kind: Optional[Union[str, FleetspacePropertiesFleetspaceApiKind]]
        provisioning_state: Optional[Union[str, Status]]
        service_tier: Optional[Union[str, FleetspacePropertiesServiceTier]]
        throughput_pool_configuration: Optional[FleetspacePropertiesThroughputPoolConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                data_regions: Optional[list[str]] = ..., 
                fleetspace_api_kind: Optional[Union[str, FleetspacePropertiesFleetspaceApiKind]] = ..., 
                service_tier: Optional[Union[str, FleetspacePropertiesServiceTier]] = ..., 
                throughput_pool_configuration: Optional[FleetspacePropertiesThroughputPoolConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.FleetspacePropertiesFleetspaceApiKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NO_SQL = "NoSQL"


    class azure.mgmt.cosmosdb.models.FleetspacePropertiesServiceTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BUSINESS_CRITICAL = "BusinessCritical"
        GENERAL_PURPOSE = "GeneralPurpose"


    class azure.mgmt.cosmosdb.models.FleetspacePropertiesThroughputPoolConfiguration(_Model):
        dedicated_r_us: Optional[int]
        max_consumable_r_us: Optional[int]
        max_throughput: Optional[int]
        min_throughput: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                dedicated_r_us: Optional[int] = ..., 
                max_consumable_r_us: Optional[int] = ..., 
                max_throughput: Optional[int] = ..., 
                min_throughput: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.FleetspaceResource(ProxyResource):
        id: str
        name: str
        properties: Optional[FleetspaceProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[FleetspaceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.FleetspaceUpdate(_Model):
        properties: Optional[FleetspaceProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[FleetspaceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.FullTextIndexPath(_Model):
        path: str

        @overload
        def __init__(
                self, 
                *, 
                path: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.FullTextPath(_Model):
        language: Optional[str]
        path: str

        @overload
        def __init__(
                self, 
                *, 
                language: Optional[str] = ..., 
                path: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.FullTextPolicy(_Model):
        default_language: Optional[str]
        full_text_paths: Optional[list[FullTextPath]]

        @overload
        def __init__(
                self, 
                *, 
                default_language: Optional[str] = ..., 
                full_text_paths: Optional[list[FullTextPath]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.GarnetAuthenticationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ENTRA = "Entra"


    class azure.mgmt.cosmosdb.models.GarnetCacheProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.cosmosdb.models.GarnetClusterResource(TrackedResource):
        id: str
        identity: Optional[ManagedCassandraManagedServiceIdentity]
        location: str
        name: str
        properties: Optional[GarnetClusterResourceProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedCassandraManagedServiceIdentity] = ..., 
                location: str, 
                properties: Optional[GarnetClusterResourceProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.GarnetClusterResourcePatch(_Model):
        properties: Optional[GarnetClusterResourcePatchProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[GarnetClusterResourcePatchProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.GarnetClusterResourcePatchProperties(_Model):
        authentication_method: Optional[Union[str, GarnetAuthenticationType]]
        cluster_type: Optional[Union[str, ClusterType]]
        extensions: Optional[list[str]]
        persistence: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                authentication_method: Optional[Union[str, GarnetAuthenticationType]] = ..., 
                cluster_type: Optional[Union[str, ClusterType]] = ..., 
                extensions: Optional[list[str]] = ..., 
                persistence: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.GarnetClusterResourceProperties(_Model):
        allocation_state: Optional[Union[str, AllocationState]]
        authentication_method: Optional[Union[str, GarnetAuthenticationType]]
        availability_zone: Optional[bool]
        cluster_type: Optional[Union[str, ClusterType]]
        end_points: Optional[list[GarnetClusterResourcePropertiesEndPointsItem]]
        extensions: Optional[list[str]]
        node_sku: Optional[str]
        persistence: Optional[bool]
        provision_error: Optional[ErrorDetail]
        provisioning_state: Optional[Union[str, GarnetCacheProvisioningState]]
        replication_factor: Optional[int]
        shard_count: Optional[int]
        subnet_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                allocation_state: Optional[Union[str, AllocationState]] = ..., 
                authentication_method: Optional[Union[str, GarnetAuthenticationType]] = ..., 
                availability_zone: Optional[bool] = ..., 
                cluster_type: Optional[Union[str, ClusterType]] = ..., 
                extensions: Optional[list[str]] = ..., 
                node_sku: Optional[str] = ..., 
                persistence: Optional[bool] = ..., 
                provision_error: Optional[ErrorDetail] = ..., 
                replication_factor: Optional[int] = ..., 
                shard_count: Optional[int] = ..., 
                subnet_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.GarnetClusterResourcePropertiesEndPointsItem(_Model):
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


    class azure.mgmt.cosmosdb.models.GraphAPIComputeRegionalServiceResource(RegionalServiceResource):
        graph_api_compute_endpoint: Optional[str]
        location: str
        name: str
        status: Union[str, ServiceStatus]


    class azure.mgmt.cosmosdb.models.GraphAPIComputeServiceResourceCreateUpdateProperties(ServiceResourceCreateUpdateProperties, discriminator='GraphAPICompute'):
        instance_count: int
        instance_size: Union[str, ServiceSize]
        service_type: Literal[ServiceType.GRAPH_API_COMPUTE]

        @overload
        def __init__(
                self, 
                *, 
                instance_count: Optional[int] = ..., 
                instance_size: Optional[Union[str, ServiceSize]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.GraphAPIComputeServiceResourceProperties(ServiceResourceProperties, discriminator='GraphAPICompute'):
        creation_time: datetime
        graph_api_compute_endpoint: Optional[str]
        instance_count: int
        instance_size: Union[str, ServiceSize]
        locations: Optional[list[GraphAPIComputeRegionalServiceResource]]
        service_type: Literal[ServiceType.GRAPH_API_COMPUTE]
        status: Union[str, ServiceStatus]

        @overload
        def __init__(
                self, 
                *, 
                graph_api_compute_endpoint: Optional[str] = ..., 
                instance_count: Optional[int] = ..., 
                instance_size: Optional[Union[str, ServiceSize]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.GraphResource(_Model):
        id: str

        @overload
        def __init__(
                self, 
                *, 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.GraphResourceCreateUpdateParameters(ARMResourceProperties):
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: GraphResourceCreateUpdateProperties
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: Optional[str] = ..., 
                properties: GraphResourceCreateUpdateProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.GraphResourceCreateUpdateProperties(_Model):
        options: Optional[CreateUpdateOptions]
        resource: GraphResource

        @overload
        def __init__(
                self, 
                *, 
                options: Optional[CreateUpdateOptions] = ..., 
                resource: GraphResource
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.GraphResourceGetProperties(_Model):
        options: Optional[GraphResourceGetPropertiesOptions]
        resource: Optional[GraphResourceGetPropertiesResource]

        @overload
        def __init__(
                self, 
                *, 
                options: Optional[GraphResourceGetPropertiesOptions] = ..., 
                resource: Optional[GraphResourceGetPropertiesResource] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.GraphResourceGetPropertiesOptions(OptionsResource):
        autoscale_settings: AutoscaleSettings
        throughput: int

        @overload
        def __init__(
                self, 
                *, 
                autoscale_settings: Optional[AutoscaleSettings] = ..., 
                throughput: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.GraphResourceGetPropertiesResource(GraphResource):
        id: str

        @overload
        def __init__(
                self, 
                *, 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.GraphResourceGetResults(ProxyResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: Optional[str]
        name: str
        properties: Optional[GraphResourceGetProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[GraphResourceGetProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.GremlinDatabaseCreateUpdateParameters(ARMResourceProperties):
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: GremlinDatabaseCreateUpdateProperties
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: Optional[str] = ..., 
                properties: GremlinDatabaseCreateUpdateProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.GremlinDatabaseCreateUpdateProperties(_Model):
        options: Optional[CreateUpdateOptions]
        resource: GremlinDatabaseResource

        @overload
        def __init__(
                self, 
                *, 
                options: Optional[CreateUpdateOptions] = ..., 
                resource: GremlinDatabaseResource
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.GremlinDatabaseGetProperties(_Model):
        options: Optional[GremlinDatabaseGetPropertiesOptions]
        resource: Optional[GremlinDatabaseGetPropertiesResource]

        @overload
        def __init__(
                self, 
                *, 
                options: Optional[GremlinDatabaseGetPropertiesOptions] = ..., 
                resource: Optional[GremlinDatabaseGetPropertiesResource] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.GremlinDatabaseGetPropertiesOptions(OptionsResource):
        autoscale_settings: AutoscaleSettings
        throughput: int

        @overload
        def __init__(
                self, 
                *, 
                autoscale_settings: Optional[AutoscaleSettings] = ..., 
                throughput: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.GremlinDatabaseGetPropertiesResource(GremlinDatabaseResource):
        create_mode: Union[str, CreateMode]
        etag: Optional[str]
        id: str
        restore_parameters: ResourceRestoreParameters
        rid: Optional[str]
        ts: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                create_mode: Optional[Union[str, CreateMode]] = ..., 
                id: str, 
                restore_parameters: Optional[ResourceRestoreParameters] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.GremlinDatabaseGetResults(ProxyResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: Optional[str]
        name: str
        properties: Optional[GremlinDatabaseGetProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[GremlinDatabaseGetProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.GremlinDatabaseResource(_Model):
        create_mode: Optional[Union[str, CreateMode]]
        id: str
        restore_parameters: Optional[ResourceRestoreParameters]

        @overload
        def __init__(
                self, 
                *, 
                create_mode: Optional[Union[str, CreateMode]] = ..., 
                id: str, 
                restore_parameters: Optional[ResourceRestoreParameters] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.GremlinDatabaseRestoreResource(_Model):
        database_name: Optional[str]
        graph_names: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                database_name: Optional[str] = ..., 
                graph_names: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.GremlinGraphCreateUpdateParameters(ARMResourceProperties):
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: GremlinGraphCreateUpdateProperties
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: Optional[str] = ..., 
                properties: GremlinGraphCreateUpdateProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.GremlinGraphCreateUpdateProperties(_Model):
        options: Optional[CreateUpdateOptions]
        resource: GremlinGraphResource

        @overload
        def __init__(
                self, 
                *, 
                options: Optional[CreateUpdateOptions] = ..., 
                resource: GremlinGraphResource
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.GremlinGraphGetProperties(_Model):
        options: Optional[GremlinGraphGetPropertiesOptions]
        resource: Optional[GremlinGraphGetPropertiesResource]

        @overload
        def __init__(
                self, 
                *, 
                options: Optional[GremlinGraphGetPropertiesOptions] = ..., 
                resource: Optional[GremlinGraphGetPropertiesResource] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.GremlinGraphGetPropertiesOptions(OptionsResource):
        autoscale_settings: AutoscaleSettings
        throughput: int

        @overload
        def __init__(
                self, 
                *, 
                autoscale_settings: Optional[AutoscaleSettings] = ..., 
                throughput: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.GremlinGraphGetPropertiesResource(GremlinGraphResource):
        analytical_storage_ttl: int
        conflict_resolution_policy: ConflictResolutionPolicy
        create_mode: Union[str, CreateMode]
        default_ttl: int
        etag: Optional[str]
        id: str
        indexing_policy: IndexingPolicy
        partition_key: ContainerPartitionKey
        restore_parameters: ResourceRestoreParameters
        rid: Optional[str]
        ts: Optional[float]
        unique_key_policy: UniqueKeyPolicy

        @overload
        def __init__(
                self, 
                *, 
                analytical_storage_ttl: Optional[int] = ..., 
                conflict_resolution_policy: Optional[ConflictResolutionPolicy] = ..., 
                create_mode: Optional[Union[str, CreateMode]] = ..., 
                default_ttl: Optional[int] = ..., 
                id: str, 
                indexing_policy: Optional[IndexingPolicy] = ..., 
                partition_key: Optional[ContainerPartitionKey] = ..., 
                restore_parameters: Optional[ResourceRestoreParameters] = ..., 
                unique_key_policy: Optional[UniqueKeyPolicy] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.GremlinGraphGetResults(ProxyResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: Optional[str]
        name: str
        properties: Optional[GremlinGraphGetProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[GremlinGraphGetProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.GremlinGraphResource(_Model):
        analytical_storage_ttl: Optional[int]
        conflict_resolution_policy: Optional[ConflictResolutionPolicy]
        create_mode: Optional[Union[str, CreateMode]]
        default_ttl: Optional[int]
        id: str
        indexing_policy: Optional[IndexingPolicy]
        partition_key: Optional[ContainerPartitionKey]
        restore_parameters: Optional[ResourceRestoreParameters]
        unique_key_policy: Optional[UniqueKeyPolicy]

        @overload
        def __init__(
                self, 
                *, 
                analytical_storage_ttl: Optional[int] = ..., 
                conflict_resolution_policy: Optional[ConflictResolutionPolicy] = ..., 
                create_mode: Optional[Union[str, CreateMode]] = ..., 
                default_ttl: Optional[int] = ..., 
                id: str, 
                indexing_policy: Optional[IndexingPolicy] = ..., 
                partition_key: Optional[ContainerPartitionKey] = ..., 
                restore_parameters: Optional[ResourceRestoreParameters] = ..., 
                unique_key_policy: Optional[UniqueKeyPolicy] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.GremlinRoleAssignmentResource(ProxyResource):
        id: str
        name: str
        properties: Optional[GremlinRoleAssignmentResourceProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[GremlinRoleAssignmentResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.GremlinRoleAssignmentResourceProperties(_Model):
        principal_id: Optional[str]
        provisioning_state: Optional[str]
        role_definition_id: Optional[str]
        scope: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                principal_id: Optional[str] = ..., 
                role_definition_id: Optional[str] = ..., 
                scope: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.GremlinRoleDefinitionResource(ProxyResource):
        id: str
        name: str
        properties: Optional[GremlinRoleDefinitionResourceProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[GremlinRoleDefinitionResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.GremlinRoleDefinitionResourceProperties(_Model):
        assignable_scopes: Optional[list[str]]
        id: Optional[str]
        permissions: Optional[list[Permission]]
        role_name: Optional[str]
        type: Optional[Union[str, RoleDefinitionType]]

        @overload
        def __init__(
                self, 
                *, 
                assignable_scopes: Optional[list[str]] = ..., 
                id: Optional[str] = ..., 
                permissions: Optional[list[Permission]] = ..., 
                role_name: Optional[str] = ..., 
                type: Optional[Union[str, RoleDefinitionType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.IncludedPath(_Model):
        indexes: Optional[list[Indexes]]
        path: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                indexes: Optional[list[Indexes]] = ..., 
                path: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.IndexKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HASH = "Hash"
        RANGE = "Range"
        SPATIAL = "Spatial"


    class azure.mgmt.cosmosdb.models.Indexes(_Model):
        data_type: Optional[Union[str, DataType]]
        kind: Optional[Union[str, IndexKind]]
        precision: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                data_type: Optional[Union[str, DataType]] = ..., 
                kind: Optional[Union[str, IndexKind]] = ..., 
                precision: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.IndexingMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONSISTENT = "consistent"
        LAZY = "lazy"
        NONE = "none"


    class azure.mgmt.cosmosdb.models.IndexingPolicy(_Model):
        automatic: Optional[bool]
        composite_indexes: Optional[list[list[CompositePath]]]
        excluded_paths: Optional[list[ExcludedPath]]
        full_text_indexes: Optional[list[FullTextIndexPath]]
        included_paths: Optional[list[IncludedPath]]
        indexing_mode: Optional[Union[str, IndexingMode]]
        spatial_indexes: Optional[list[SpatialSpec]]
        vector_indexes: Optional[list[VectorIndex]]

        @overload
        def __init__(
                self, 
                *, 
                automatic: Optional[bool] = ..., 
                composite_indexes: Optional[list[list[CompositePath]]] = ..., 
                excluded_paths: Optional[list[ExcludedPath]] = ..., 
                full_text_indexes: Optional[list[FullTextIndexPath]] = ..., 
                included_paths: Optional[list[IncludedPath]] = ..., 
                indexing_mode: Optional[Union[str, IndexingMode]] = ..., 
                spatial_indexes: Optional[list[SpatialSpec]] = ..., 
                vector_indexes: Optional[list[VectorIndex]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.IpAddressOrRange(_Model):
        ip_address_or_range: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                ip_address_or_range: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.IssueType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONFIGURATION_PROPAGATION_FAILURE = "ConfigurationPropagationFailure"
        MISSING_IDENTITY_CONFIGURATION = "MissingIdentityConfiguration"
        MISSING_PERIMETER_CONFIGURATION = "MissingPerimeterConfiguration"
        UNKNOWN = "Unknown"


    class azure.mgmt.cosmosdb.models.KeyKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRIMARY = "primary"
        PRIMARY_READONLY = "primaryReadonly"
        SECONDARY = "secondary"
        SECONDARY_READONLY = "secondaryReadonly"


    class azure.mgmt.cosmosdb.models.KeyWrapMetadata(_Model):
        algorithm: Optional[str]
        name: Optional[str]
        type: Optional[str]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                algorithm: Optional[str] = ..., 
                name: Optional[str] = ..., 
                type: Optional[str] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.Kind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRIMARY = "Primary"
        PRIMARY_READONLY = "PrimaryReadonly"
        SECONDARY = "Secondary"
        SECONDARY_READONLY = "SecondaryReadonly"


    class azure.mgmt.cosmosdb.models.Location(_Model):
        document_endpoint: Optional[str]
        failover_priority: Optional[int]
        id: Optional[str]
        is_zone_redundant: Optional[bool]
        location_name: Optional[str]
        provisioning_state: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                failover_priority: Optional[int] = ..., 
                is_zone_redundant: Optional[bool] = ..., 
                location_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.LocationGetResult(ProxyResource):
        id: str
        name: str
        properties: Optional[LocationProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[LocationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.LocationProperties(_Model):
        backup_storage_redundancies: Optional[list[Union[str, BackupStorageRedundancy]]]
        is_residency_restricted: Optional[bool]
        is_subscription_region_access_allowed_for_az: Optional[bool]
        is_subscription_region_access_allowed_for_regular: Optional[bool]
        status: Optional[Union[str, Status]]
        supports_availability_zone: Optional[bool]


    class azure.mgmt.cosmosdb.models.ManagedCassandraManagedServiceIdentity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Optional[Union[str, ManagedCassandraResourceIdentityType]]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, ManagedCassandraResourceIdentityType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.ManagedCassandraProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.cosmosdb.models.ManagedCassandraReaperStatus(_Model):
        healthy: Optional[bool]
        repair_run_ids: Optional[dict[str, str]]
        repair_schedules: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                healthy: Optional[bool] = ..., 
                repair_run_ids: Optional[dict[str, str]] = ..., 
                repair_schedules: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.ManagedCassandraResourceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"


    class azure.mgmt.cosmosdb.models.ManagedServiceIdentity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Optional[Union[str, ResourceIdentityType]]
        user_assigned_identities: Optional[dict[str, ManagedServiceIdentityUserAssignedIdentity]]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, ResourceIdentityType]] = ..., 
                user_assigned_identities: Optional[dict[str, ManagedServiceIdentityUserAssignedIdentity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.ManagedServiceIdentityUserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.cosmosdb.models.MaterializedViewDefinition(_Model):
        definition: str
        source_collection_id: str
        source_collection_rid: Optional[str]
        throughput_bucket_for_build: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                definition: str, 
                source_collection_id: str, 
                throughput_bucket_for_build: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.MaterializedViewDetails(_Model):
        id: Optional[str]
        rid: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                rid: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.MaterializedViewsBuilderRegionalServiceResource(RegionalServiceResource):
        location: str
        name: str
        status: Union[str, ServiceStatus]


    class azure.mgmt.cosmosdb.models.MaterializedViewsBuilderServiceResourceCreateUpdateProperties(ServiceResourceCreateUpdateProperties, discriminator='MaterializedViewsBuilder'):
        instance_count: int
        instance_size: Union[str, ServiceSize]
        service_type: Literal[ServiceType.MATERIALIZED_VIEWS_BUILDER]

        @overload
        def __init__(
                self, 
                *, 
                instance_count: Optional[int] = ..., 
                instance_size: Optional[Union[str, ServiceSize]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.MaterializedViewsBuilderServiceResourceProperties(ServiceResourceProperties, discriminator='MaterializedViewsBuilder'):
        creation_time: datetime
        instance_count: int
        instance_size: Union[str, ServiceSize]
        locations: Optional[list[MaterializedViewsBuilderRegionalServiceResource]]
        service_type: Literal[ServiceType.MATERIALIZED_VIEWS_BUILDER]
        status: Union[str, ServiceStatus]

        @overload
        def __init__(
                self, 
                *, 
                instance_count: Optional[int] = ..., 
                instance_size: Optional[Union[str, ServiceSize]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.MaterializedViewsProperties(_Model):
        throughput_bucket_for_build: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                throughput_bucket_for_build: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.MergeParameters(_Model):
        is_dry_run: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                is_dry_run: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.Metric(_Model):
        end_time: Optional[datetime]
        metric_values: Optional[list[MetricValue]]
        name: Optional[MetricName]
        start_time: Optional[datetime]
        time_grain: Optional[str]
        unit: Optional[Union[str, UnitType]]


    class azure.mgmt.cosmosdb.models.MetricAvailability(_Model):
        retention: Optional[str]
        time_grain: Optional[str]


    class azure.mgmt.cosmosdb.models.MetricDefinition(_Model):
        metric_availabilities: Optional[list[MetricAvailability]]
        name: Optional[MetricName]
        primary_aggregation_type: Optional[Union[str, PrimaryAggregationType]]
        resource_uri: Optional[str]
        unit: Optional[Union[str, UnitType]]


    class azure.mgmt.cosmosdb.models.MetricName(_Model):
        localized_value: Optional[str]
        value: Optional[str]


    class azure.mgmt.cosmosdb.models.MetricValue(_Model):
        average: Optional[float]
        count: Optional[int]
        maximum: Optional[float]
        minimum: Optional[float]
        timestamp: Optional[datetime]
        total: Optional[float]


    class azure.mgmt.cosmosdb.models.MinimalTlsVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        TLS = "Tls"
        TLS11 = "Tls11"
        TLS12 = "Tls12"


    class azure.mgmt.cosmosdb.models.MongoDBCollectionCreateUpdateParameters(ARMResourceProperties):
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: MongoDBCollectionCreateUpdateProperties
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: Optional[str] = ..., 
                properties: MongoDBCollectionCreateUpdateProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.MongoDBCollectionCreateUpdateProperties(_Model):
        options: Optional[CreateUpdateOptions]
        resource: MongoDBCollectionResource

        @overload
        def __init__(
                self, 
                *, 
                options: Optional[CreateUpdateOptions] = ..., 
                resource: MongoDBCollectionResource
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.MongoDBCollectionGetProperties(_Model):
        options: Optional[MongoDBCollectionGetPropertiesOptions]
        resource: Optional[MongoDBCollectionGetPropertiesResource]

        @overload
        def __init__(
                self, 
                *, 
                options: Optional[MongoDBCollectionGetPropertiesOptions] = ..., 
                resource: Optional[MongoDBCollectionGetPropertiesResource] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.MongoDBCollectionGetPropertiesOptions(OptionsResource):
        autoscale_settings: AutoscaleSettings
        throughput: int

        @overload
        def __init__(
                self, 
                *, 
                autoscale_settings: Optional[AutoscaleSettings] = ..., 
                throughput: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.MongoDBCollectionGetPropertiesResource(MongoDBCollectionResource):
        analytical_storage_ttl: int
        create_mode: Union[str, CreateMode]
        etag: Optional[str]
        id: str
        indexes: list[MongoIndex]
        restore_parameters: ResourceRestoreParameters
        rid: Optional[str]
        shard_key: dict[str, str]
        ts: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                analytical_storage_ttl: Optional[int] = ..., 
                create_mode: Optional[Union[str, CreateMode]] = ..., 
                id: str, 
                indexes: Optional[list[MongoIndex]] = ..., 
                restore_parameters: Optional[ResourceRestoreParameters] = ..., 
                shard_key: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.MongoDBCollectionGetResults(ProxyResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: Optional[str]
        name: str
        properties: Optional[MongoDBCollectionGetProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[MongoDBCollectionGetProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.MongoDBCollectionResource(_Model):
        analytical_storage_ttl: Optional[int]
        create_mode: Optional[Union[str, CreateMode]]
        id: str
        indexes: Optional[list[MongoIndex]]
        restore_parameters: Optional[ResourceRestoreParameters]
        shard_key: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                analytical_storage_ttl: Optional[int] = ..., 
                create_mode: Optional[Union[str, CreateMode]] = ..., 
                id: str, 
                indexes: Optional[list[MongoIndex]] = ..., 
                restore_parameters: Optional[ResourceRestoreParameters] = ..., 
                shard_key: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.MongoDBDatabaseCreateUpdateParameters(ARMResourceProperties):
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: MongoDBDatabaseCreateUpdateProperties
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: Optional[str] = ..., 
                properties: MongoDBDatabaseCreateUpdateProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.MongoDBDatabaseCreateUpdateProperties(_Model):
        options: Optional[CreateUpdateOptions]
        resource: MongoDBDatabaseResource

        @overload
        def __init__(
                self, 
                *, 
                options: Optional[CreateUpdateOptions] = ..., 
                resource: MongoDBDatabaseResource
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.MongoDBDatabaseGetProperties(_Model):
        options: Optional[MongoDBDatabaseGetPropertiesOptions]
        resource: Optional[MongoDBDatabaseGetPropertiesResource]

        @overload
        def __init__(
                self, 
                *, 
                options: Optional[MongoDBDatabaseGetPropertiesOptions] = ..., 
                resource: Optional[MongoDBDatabaseGetPropertiesResource] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.MongoDBDatabaseGetPropertiesOptions(OptionsResource):
        autoscale_settings: AutoscaleSettings
        throughput: int

        @overload
        def __init__(
                self, 
                *, 
                autoscale_settings: Optional[AutoscaleSettings] = ..., 
                throughput: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.MongoDBDatabaseGetPropertiesResource(MongoDBDatabaseResource):
        create_mode: Union[str, CreateMode]
        etag: Optional[str]
        id: str
        restore_parameters: ResourceRestoreParameters
        rid: Optional[str]
        ts: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                create_mode: Optional[Union[str, CreateMode]] = ..., 
                id: str, 
                restore_parameters: Optional[ResourceRestoreParameters] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.MongoDBDatabaseGetResults(ProxyResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: Optional[str]
        name: str
        properties: Optional[MongoDBDatabaseGetProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[MongoDBDatabaseGetProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.MongoDBDatabaseResource(_Model):
        create_mode: Optional[Union[str, CreateMode]]
        id: str
        restore_parameters: Optional[ResourceRestoreParameters]

        @overload
        def __init__(
                self, 
                *, 
                create_mode: Optional[Union[str, CreateMode]] = ..., 
                id: str, 
                restore_parameters: Optional[ResourceRestoreParameters] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.MongoIndex(_Model):
        key: Optional[MongoIndexKeys]
        options: Optional[MongoIndexOptions]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[MongoIndexKeys] = ..., 
                options: Optional[MongoIndexOptions] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.MongoIndexKeys(_Model):
        keys_property: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                keys_property: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.MongoIndexOptions(_Model):
        expire_after_seconds: Optional[int]
        unique: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                expire_after_seconds: Optional[int] = ..., 
                unique: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.MongoMIRoleAssignmentResource(ProxyResource):
        id: str
        name: str
        properties: Optional[MongoMIRoleAssignmentResourceProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[MongoMIRoleAssignmentResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.MongoMIRoleAssignmentResourceProperties(_Model):
        principal_id: Optional[str]
        provisioning_state: Optional[str]
        role_definition_id: Optional[str]
        scope: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                principal_id: Optional[str] = ..., 
                role_definition_id: Optional[str] = ..., 
                scope: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.MongoMIRoleDefinitionResource(ProxyResource):
        id: str
        name: str
        properties: Optional[MongoMIRoleDefinitionResourceProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[MongoMIRoleDefinitionResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.MongoMIRoleDefinitionResourceProperties(_Model):
        assignable_scopes: Optional[list[str]]
        id: Optional[str]
        permissions: Optional[list[Permission]]
        role_name: Optional[str]
        type: Optional[Union[str, RoleDefinitionType]]

        @overload
        def __init__(
                self, 
                *, 
                assignable_scopes: Optional[list[str]] = ..., 
                id: Optional[str] = ..., 
                permissions: Optional[list[Permission]] = ..., 
                role_name: Optional[str] = ..., 
                type: Optional[Union[str, RoleDefinitionType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.MongoRUToMongoRUCopyJobProperties(BaseCopyJobProperties, discriminator='MongoRUToMongoRU'):
        destination_details: Optional[CosmosDBSourceSinkDetails]
        job_type: Literal[CopyJobType.MONGO_RU_TO_MONGO_RU]
        source_details: Optional[CosmosDBSourceSinkDetails]
        tasks: list[MongoRUToMongoRUCopyJobTask]

        @overload
        def __init__(
                self, 
                *, 
                destination_details: Optional[CosmosDBSourceSinkDetails] = ..., 
                source_details: Optional[CosmosDBSourceSinkDetails] = ..., 
                tasks: list[MongoRUToMongoRUCopyJobTask]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.MongoRUToMongoRUCopyJobTask(BaseCopyJobTask):
        destination: CosmosDBMongoCollection
        processed_count: int
        source: CosmosDBMongoCollection
        total_count: int

        @overload
        def __init__(
                self, 
                *, 
                destination: CosmosDBMongoCollection, 
                source: CosmosDBMongoCollection
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.MongoRUToMongoVCoreCopyJobProperties(BaseCopyJobProperties, discriminator='MongoRUToMongoVCore'):
        destination_details: MongoVCoreSourceSinkDetails
        job_type: Literal[CopyJobType.MONGO_RU_TO_MONGO_V_CORE]
        source_details: Optional[CosmosDBSourceSinkDetails]
        tasks: list[MongoRUToMongoVCoreCopyJobTask]

        @overload
        def __init__(
                self, 
                *, 
                destination_details: MongoVCoreSourceSinkDetails, 
                source_details: Optional[CosmosDBSourceSinkDetails] = ..., 
                tasks: list[MongoRUToMongoVCoreCopyJobTask]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.MongoRUToMongoVCoreCopyJobTask(BaseCopyJobTask):
        destination: CosmosDBMongoVCoreCollection
        processed_count: int
        source: CosmosDBMongoCollection
        total_count: int

        @overload
        def __init__(
                self, 
                *, 
                destination: CosmosDBMongoVCoreCollection, 
                source: CosmosDBMongoCollection
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.MongoRoleDefinitionCreateUpdateParameters(_Model):
        properties: Optional[MongoRoleDefinitionResource]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[MongoRoleDefinitionResource] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.MongoRoleDefinitionGetResults(ProxyResource):
        id: str
        name: str
        properties: Optional[MongoRoleDefinitionResource]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[MongoRoleDefinitionResource] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.MongoRoleDefinitionResource(_Model):
        database_name: Optional[str]
        privileges: Optional[list[Privilege]]
        role_name: Optional[str]
        roles: Optional[list[Role]]
        type: Optional[Union[str, MongoRoleDefinitionType]]

        @overload
        def __init__(
                self, 
                *, 
                database_name: Optional[str] = ..., 
                privileges: Optional[list[Privilege]] = ..., 
                role_name: Optional[str] = ..., 
                roles: Optional[list[Role]] = ..., 
                type: Optional[Union[str, MongoRoleDefinitionType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.MongoRoleDefinitionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BUILT_IN_ROLE = "BuiltInRole"
        CUSTOM_ROLE = "CustomRole"


    class azure.mgmt.cosmosdb.models.MongoUserDefinitionCreateUpdateParameters(_Model):
        properties: Optional[MongoUserDefinitionResource]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[MongoUserDefinitionResource] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.MongoUserDefinitionGetResults(ProxyResource):
        id: str
        name: str
        properties: Optional[MongoUserDefinitionResource]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[MongoUserDefinitionResource] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.MongoUserDefinitionResource(_Model):
        custom_data: Optional[str]
        database_name: Optional[str]
        mechanisms: Optional[str]
        password: Optional[str]
        roles: Optional[list[Role]]
        user_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                custom_data: Optional[str] = ..., 
                database_name: Optional[str] = ..., 
                mechanisms: Optional[str] = ..., 
                password: Optional[str] = ..., 
                roles: Optional[list[Role]] = ..., 
                user_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.MongoVCoreSourceSinkDetails(_Model):
        connection_string_key_vault_uri: Optional[str]
        host_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                connection_string_key_vault_uri: Optional[str] = ..., 
                host_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.NetworkAclBypass(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_SERVICES = "AzureServices"
        NONE = "None"


    class azure.mgmt.cosmosdb.models.NetworkSecurityPerimeter(_Model):
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


    class azure.mgmt.cosmosdb.models.NetworkSecurityPerimeterConfiguration(ProxyResource):
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


    class azure.mgmt.cosmosdb.models.NetworkSecurityPerimeterConfigurationProperties(_Model):
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


    class azure.mgmt.cosmosdb.models.NetworkSecurityPerimeterConfigurationProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.cosmosdb.models.NetworkSecurityProfile(_Model):
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


    class azure.mgmt.cosmosdb.models.NoSqlRUToNoSqlRUCopyJobProperties(BaseCopyJobProperties, discriminator='NoSqlRUToNoSqlRU'):
        destination_details: Optional[CosmosDBSourceSinkDetails]
        job_type: Literal[CopyJobType.NO_SQL_RU_TO_NO_SQL_RU]
        source_details: Optional[CosmosDBSourceSinkDetails]
        tasks: list[NoSqlRUToNoSqlRUCopyJobTask]

        @overload
        def __init__(
                self, 
                *, 
                destination_details: Optional[CosmosDBSourceSinkDetails] = ..., 
                source_details: Optional[CosmosDBSourceSinkDetails] = ..., 
                tasks: list[NoSqlRUToNoSqlRUCopyJobTask]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.NoSqlRUToNoSqlRUCopyJobTask(BaseCopyJobTask):
        destination: CosmosDBNoSqlContainer
        processed_count: int
        source: CosmosDBNoSqlContainer
        total_count: int

        @overload
        def __init__(
                self, 
                *, 
                destination: CosmosDBNoSqlContainer, 
                source: CosmosDBNoSqlContainer
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.NodeState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        JOINING = "Joining"
        LEAVING = "Leaving"
        MOVING = "Moving"
        NORMAL = "Normal"
        STOPPED = "Stopped"


    class azure.mgmt.cosmosdb.models.NotebookWorkspace(ProxyResource):
        id: str
        name: str
        properties: Optional[NotebookWorkspaceProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[NotebookWorkspaceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.NotebookWorkspaceConnectionInfoResult(_Model):
        auth_token: Optional[str]
        notebook_server_endpoint: Optional[str]


    class azure.mgmt.cosmosdb.models.NotebookWorkspaceCreateUpdateParameters(ARMProxyResource):
        id: str
        name: str
        type: str


    class azure.mgmt.cosmosdb.models.NotebookWorkspaceName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "default"


    class azure.mgmt.cosmosdb.models.NotebookWorkspaceProperties(_Model):
        notebook_server_endpoint: Optional[str]
        status: Optional[str]


    class azure.mgmt.cosmosdb.models.Operation(_Model):
        display: Optional[OperationDisplay]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.OperationDisplay(_Model):
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


    class azure.mgmt.cosmosdb.models.OperationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATE = "Create"
        DELETE = "Delete"
        RECREATE = "Recreate"
        REPLACE = "Replace"
        SYSTEM_OPERATION = "SystemOperation"


    class azure.mgmt.cosmosdb.models.OptionsResource(_Model):
        autoscale_settings: Optional[AutoscaleSettings]
        throughput: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                autoscale_settings: Optional[AutoscaleSettings] = ..., 
                throughput: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.PartitionKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HASH = "Hash"
        MULTI_HASH = "MultiHash"
        RANGE = "Range"


    class azure.mgmt.cosmosdb.models.PartitionMetric(Metric):
        end_time: datetime
        metric_values: list[MetricValue]
        name: MetricName
        partition_id: Optional[str]
        partition_key_range_id: Optional[str]
        start_time: datetime
        time_grain: str
        unit: Union[str, UnitType]


    class azure.mgmt.cosmosdb.models.PartitionUsage(Usage):
        current_value: int
        limit: int
        name: MetricName
        partition_id: Optional[str]
        partition_key_range_id: Optional[str]
        quota_period: str
        unit: Union[str, UnitType]


    class azure.mgmt.cosmosdb.models.PercentileMetric(_Model):
        end_time: Optional[datetime]
        metric_values: Optional[list[PercentileMetricValue]]
        name: Optional[MetricName]
        start_time: Optional[datetime]
        time_grain: Optional[str]
        unit: Optional[Union[str, UnitType]]


    class azure.mgmt.cosmosdb.models.PercentileMetricValue(MetricValue):
        average: float
        count: int
        maximum: float
        minimum: float
        p10: Optional[float]
        p25: Optional[float]
        p50: Optional[float]
        p75: Optional[float]
        p90: Optional[float]
        p95: Optional[float]
        p99: Optional[float]
        timestamp: datetime
        total: float


    class azure.mgmt.cosmosdb.models.PeriodicModeBackupPolicy(BackupPolicy, discriminator='Periodic'):
        migration_state: BackupPolicyMigrationState
        periodic_mode_properties: Optional[PeriodicModeProperties]
        type: Literal[BackupPolicyType.PERIODIC]

        @overload
        def __init__(
                self, 
                *, 
                migration_state: Optional[BackupPolicyMigrationState] = ..., 
                periodic_mode_properties: Optional[PeriodicModeProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.PeriodicModeProperties(_Model):
        backup_interval_in_minutes: Optional[int]
        backup_retention_interval_in_hours: Optional[int]
        backup_storage_redundancy: Optional[Union[str, BackupStorageRedundancy]]

        @overload
        def __init__(
                self, 
                *, 
                backup_interval_in_minutes: Optional[int] = ..., 
                backup_retention_interval_in_hours: Optional[int] = ..., 
                backup_storage_redundancy: Optional[Union[str, BackupStorageRedundancy]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.Permission(_Model):
        data_actions: Optional[list[str]]
        id: Optional[str]
        not_data_actions: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                data_actions: Optional[list[str]] = ..., 
                id: Optional[str] = ..., 
                not_data_actions: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.PhysicalPartitionId(_Model):
        id: str

        @overload
        def __init__(
                self, 
                *, 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.PhysicalPartitionStorageInfo(_Model):
        id: Optional[str]
        storage_in_kb: Optional[float]


    class azure.mgmt.cosmosdb.models.PhysicalPartitionStorageInfoCollection(_Model):
        physical_partition_storage_info_collection: Optional[list[PhysicalPartitionStorageInfo]]


    class azure.mgmt.cosmosdb.models.PhysicalPartitionThroughputInfoProperties(_Model):
        physical_partition_throughput_info: Optional[list[PhysicalPartitionThroughputInfoResource]]

        @overload
        def __init__(
                self, 
                *, 
                physical_partition_throughput_info: Optional[list[PhysicalPartitionThroughputInfoResource]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.PhysicalPartitionThroughputInfoResource(_Model):
        id: str
        target_throughput: Optional[float]
        throughput: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                target_throughput: Optional[float] = ..., 
                throughput: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.PhysicalPartitionThroughputInfoResult(ARMResourceProperties):
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: Optional[PhysicalPartitionThroughputInfoResultProperties]
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[PhysicalPartitionThroughputInfoResultProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.PhysicalPartitionThroughputInfoResultProperties(_Model):
        resource: Optional[PhysicalPartitionThroughputInfoResultPropertiesResource]

        @overload
        def __init__(
                self, 
                *, 
                resource: Optional[PhysicalPartitionThroughputInfoResultPropertiesResource] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.PhysicalPartitionThroughputInfoResultPropertiesResource(PhysicalPartitionThroughputInfoProperties):
        physical_partition_throughput_info: list[PhysicalPartitionThroughputInfoResource]

        @overload
        def __init__(
                self, 
                *, 
                physical_partition_throughput_info: Optional[list[PhysicalPartitionThroughputInfoResource]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.PrimaryAggregationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVERAGE = "Average"
        LAST = "Last"
        MAXIMUM = "Maximum"
        MINIMUM = "Minimum"
        NONE = "None"
        TOTAL = "Total"


    class azure.mgmt.cosmosdb.models.PrivateEndpointConnection(ProxyResource):
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


    class azure.mgmt.cosmosdb.models.PrivateEndpointConnectionProperties(_Model):
        group_id: Optional[str]
        private_endpoint: Optional[PrivateEndpointProperty]
        private_link_service_connection_state: Optional[PrivateLinkServiceConnectionStateProperty]
        provisioning_state: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                group_id: Optional[str] = ..., 
                private_endpoint: Optional[PrivateEndpointProperty] = ..., 
                private_link_service_connection_state: Optional[PrivateLinkServiceConnectionStateProperty] = ..., 
                provisioning_state: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.PrivateEndpointProperty(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.PrivateLinkResource(ProxyResource):
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


    class azure.mgmt.cosmosdb.models.PrivateLinkResourceProperties(_Model):
        group_id: Optional[str]
        required_members: Optional[list[str]]
        required_zone_names: Optional[list[str]]


    class azure.mgmt.cosmosdb.models.PrivateLinkServiceConnectionStateProperty(_Model):
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


    class azure.mgmt.cosmosdb.models.Privilege(_Model):
        actions: Optional[list[str]]
        resource: Optional[PrivilegeResource]

        @overload
        def __init__(
                self, 
                *, 
                actions: Optional[list[str]] = ..., 
                resource: Optional[PrivilegeResource] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.PrivilegeResource(_Model):
        collection: Optional[str]
        db: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                collection: Optional[str] = ..., 
                db: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.ProvisioningIssue(_Model):
        name: Optional[str]
        properties: Optional[ProvisioningIssueProperties]


    class azure.mgmt.cosmosdb.models.ProvisioningIssueProperties(_Model):
        description: Optional[str]
        issue_type: Optional[Union[str, IssueType]]
        severity: Optional[Union[str, Severity]]
        suggested_access_rules: Optional[list[AccessRule]]
        suggested_resource_ids: Optional[list[str]]


    class azure.mgmt.cosmosdb.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.cosmosdb.models.PublicNetworkAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        SECURED_BY_PERIMETER = "SecuredByPerimeter"


    class azure.mgmt.cosmosdb.models.RedistributeThroughputParameters(ARMResourceProperties):
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: RedistributeThroughputProperties
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: Optional[str] = ..., 
                properties: RedistributeThroughputProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.RedistributeThroughputProperties(_Model):
        resource: RedistributeThroughputPropertiesResource

        @overload
        def __init__(
                self, 
                *, 
                resource: RedistributeThroughputPropertiesResource
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.RedistributeThroughputPropertiesResource(_Model):
        source_physical_partition_throughput_info: list[PhysicalPartitionThroughputInfoResource]
        target_physical_partition_throughput_info: list[PhysicalPartitionThroughputInfoResource]
        throughput_policy: Union[str, ThroughputPolicyType]

        @overload
        def __init__(
                self, 
                *, 
                source_physical_partition_throughput_info: list[PhysicalPartitionThroughputInfoResource], 
                target_physical_partition_throughput_info: list[PhysicalPartitionThroughputInfoResource], 
                throughput_policy: Union[str, ThroughputPolicyType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.RegionForOnlineOffline(_Model):
        region: str

        @overload
        def __init__(
                self, 
                *, 
                region: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.RegionalServiceResource(_Model):
        location: Optional[str]
        name: Optional[str]
        status: Optional[Union[str, ServiceStatus]]


    class azure.mgmt.cosmosdb.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.cosmosdb.models.ResourceAssociation(_Model):
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


    class azure.mgmt.cosmosdb.models.ResourceAssociationAccessMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUDIT = "Audit"
        ENFORCED = "Enforced"
        LEARNING = "Learning"


    class azure.mgmt.cosmosdb.models.ResourceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.cosmosdb.models.ResourceRestoreParameters(RestoreParametersBase):
        restore_source: str
        restore_timestamp_in_utc: datetime
        restore_with_ttl_disabled: bool

        @overload
        def __init__(
                self, 
                *, 
                restore_source: Optional[str] = ..., 
                restore_timestamp_in_utc: Optional[datetime] = ..., 
                restore_with_ttl_disabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.RestorableDatabaseAccountGetResult(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[RestorableDatabaseAccountProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[RestorableDatabaseAccountProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.RestorableDatabaseAccountProperties(_Model):
        account_name: Optional[str]
        api_type: Optional[Union[str, ApiType]]
        creation_time: Optional[datetime]
        deletion_time: Optional[datetime]
        oldest_restorable_time: Optional[datetime]
        restorable_locations: Optional[list[RestorableLocationResource]]

        @overload
        def __init__(
                self, 
                *, 
                account_name: Optional[str] = ..., 
                creation_time: Optional[datetime] = ..., 
                deletion_time: Optional[datetime] = ..., 
                oldest_restorable_time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.RestorableGremlinDatabaseGetResult(_Model):
        id: Optional[str]
        name: Optional[str]
        properties: Optional[RestorableGremlinDatabaseProperties]
        type: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RestorableGremlinDatabaseProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.RestorableGremlinDatabaseProperties(_Model):
        resource: Optional[RestorableGremlinDatabasePropertiesResource]

        @overload
        def __init__(
                self, 
                *, 
                resource: Optional[RestorableGremlinDatabasePropertiesResource] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.RestorableGremlinDatabasePropertiesResource(_Model):
        can_undelete: Optional[str]
        can_undelete_reason: Optional[str]
        event_timestamp: Optional[str]
        operation_type: Optional[Union[str, OperationType]]
        owner_id: Optional[str]
        owner_resource_id: Optional[str]
        rid: Optional[str]


    class azure.mgmt.cosmosdb.models.RestorableGremlinGraphGetResult(_Model):
        id: Optional[str]
        name: Optional[str]
        properties: Optional[RestorableGremlinGraphProperties]
        type: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RestorableGremlinGraphProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.RestorableGremlinGraphProperties(_Model):
        resource: Optional[RestorableGremlinGraphPropertiesResource]

        @overload
        def __init__(
                self, 
                *, 
                resource: Optional[RestorableGremlinGraphPropertiesResource] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.RestorableGremlinGraphPropertiesResource(_Model):
        can_undelete: Optional[str]
        can_undelete_reason: Optional[str]
        event_timestamp: Optional[str]
        operation_type: Optional[Union[str, OperationType]]
        owner_id: Optional[str]
        owner_resource_id: Optional[str]
        rid: Optional[str]


    class azure.mgmt.cosmosdb.models.RestorableGremlinResourcesGetResult(_Model):
        database_name: Optional[str]
        graph_names: Optional[list[str]]
        id: Optional[str]
        name: Optional[str]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                database_name: Optional[str] = ..., 
                graph_names: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.RestorableLocationResource(_Model):
        creation_time: Optional[datetime]
        deletion_time: Optional[datetime]
        location_name: Optional[str]
        regional_database_account_instance_id: Optional[str]


    class azure.mgmt.cosmosdb.models.RestorableMongodbCollectionGetResult(_Model):
        id: Optional[str]
        name: Optional[str]
        properties: Optional[RestorableMongodbCollectionProperties]
        type: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RestorableMongodbCollectionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.RestorableMongodbCollectionProperties(_Model):
        resource: Optional[RestorableMongodbCollectionPropertiesResource]

        @overload
        def __init__(
                self, 
                *, 
                resource: Optional[RestorableMongodbCollectionPropertiesResource] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.RestorableMongodbCollectionPropertiesResource(_Model):
        can_undelete: Optional[str]
        can_undelete_reason: Optional[str]
        event_timestamp: Optional[str]
        operation_type: Optional[Union[str, OperationType]]
        owner_id: Optional[str]
        owner_resource_id: Optional[str]
        rid: Optional[str]


    class azure.mgmt.cosmosdb.models.RestorableMongodbDatabaseGetResult(_Model):
        id: Optional[str]
        name: Optional[str]
        properties: Optional[RestorableMongodbDatabaseProperties]
        type: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RestorableMongodbDatabaseProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.RestorableMongodbDatabaseProperties(_Model):
        resource: Optional[RestorableMongodbDatabasePropertiesResource]

        @overload
        def __init__(
                self, 
                *, 
                resource: Optional[RestorableMongodbDatabasePropertiesResource] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.RestorableMongodbDatabasePropertiesResource(_Model):
        can_undelete: Optional[str]
        can_undelete_reason: Optional[str]
        event_timestamp: Optional[str]
        operation_type: Optional[Union[str, OperationType]]
        owner_id: Optional[str]
        owner_resource_id: Optional[str]
        rid: Optional[str]


    class azure.mgmt.cosmosdb.models.RestorableMongodbResourcesGetResult(_Model):
        collection_names: Optional[list[str]]
        database_name: Optional[str]
        id: Optional[str]
        name: Optional[str]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                collection_names: Optional[list[str]] = ..., 
                database_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.RestorableSqlContainerGetResult(_Model):
        id: Optional[str]
        name: Optional[str]
        properties: Optional[RestorableSqlContainerProperties]
        type: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RestorableSqlContainerProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.RestorableSqlContainerProperties(_Model):
        resource: Optional[RestorableSqlContainerPropertiesResource]

        @overload
        def __init__(
                self, 
                *, 
                resource: Optional[RestorableSqlContainerPropertiesResource] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.RestorableSqlContainerPropertiesResource(_Model):
        can_undelete: Optional[str]
        can_undelete_reason: Optional[str]
        container: Optional[RestorableSqlContainerPropertiesResourceContainer]
        event_timestamp: Optional[str]
        operation_type: Optional[Union[str, OperationType]]
        owner_id: Optional[str]
        owner_resource_id: Optional[str]
        rid: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                container: Optional[RestorableSqlContainerPropertiesResourceContainer] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.RestorableSqlContainerPropertiesResourceContainer(SqlContainerResource):
        analytical_storage_ttl: int
        client_encryption_policy: ClientEncryptionPolicy
        computed_properties: list[ComputedProperty]
        conflict_resolution_policy: ConflictResolutionPolicy
        create_mode: Union[str, CreateMode]
        data_masking_policy: DataMaskingPolicy
        default_ttl: int
        etag: Optional[str]
        full_text_policy: FullTextPolicy
        id: str
        indexing_policy: IndexingPolicy
        materialized_view_definition: MaterializedViewDefinition
        materialized_views: list[MaterializedViewDetails]
        materialized_views_properties: MaterializedViewsProperties
        partition_key: ContainerPartitionKey
        restore_parameters: ResourceRestoreParameters
        rid: Optional[str]
        self_property: Optional[str]
        ts: Optional[float]
        unique_key_policy: UniqueKeyPolicy
        vector_embedding_policy: VectorEmbeddingPolicy

        @overload
        def __init__(
                self, 
                *, 
                analytical_storage_ttl: Optional[int] = ..., 
                client_encryption_policy: Optional[ClientEncryptionPolicy] = ..., 
                computed_properties: Optional[list[ComputedProperty]] = ..., 
                conflict_resolution_policy: Optional[ConflictResolutionPolicy] = ..., 
                create_mode: Optional[Union[str, CreateMode]] = ..., 
                data_masking_policy: Optional[DataMaskingPolicy] = ..., 
                default_ttl: Optional[int] = ..., 
                full_text_policy: Optional[FullTextPolicy] = ..., 
                id: str, 
                indexing_policy: Optional[IndexingPolicy] = ..., 
                materialized_view_definition: Optional[MaterializedViewDefinition] = ..., 
                materialized_views: Optional[list[MaterializedViewDetails]] = ..., 
                materialized_views_properties: Optional[MaterializedViewsProperties] = ..., 
                partition_key: Optional[ContainerPartitionKey] = ..., 
                restore_parameters: Optional[ResourceRestoreParameters] = ..., 
                unique_key_policy: Optional[UniqueKeyPolicy] = ..., 
                vector_embedding_policy: Optional[VectorEmbeddingPolicy] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.RestorableSqlDatabaseGetResult(_Model):
        id: Optional[str]
        name: Optional[str]
        properties: Optional[RestorableSqlDatabaseProperties]
        type: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RestorableSqlDatabaseProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.RestorableSqlDatabaseProperties(_Model):
        resource: Optional[RestorableSqlDatabasePropertiesResource]

        @overload
        def __init__(
                self, 
                *, 
                resource: Optional[RestorableSqlDatabasePropertiesResource] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.RestorableSqlDatabasePropertiesResource(_Model):
        can_undelete: Optional[str]
        can_undelete_reason: Optional[str]
        database: Optional[RestorableSqlDatabasePropertiesResourceDatabase]
        event_timestamp: Optional[str]
        operation_type: Optional[Union[str, OperationType]]
        owner_id: Optional[str]
        owner_resource_id: Optional[str]
        rid: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                database: Optional[RestorableSqlDatabasePropertiesResourceDatabase] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.RestorableSqlDatabasePropertiesResourceDatabase(SqlDatabaseResource):
        colls: Optional[str]
        create_mode: Union[str, CreateMode]
        etag: Optional[str]
        id: str
        restore_parameters: ResourceRestoreParameters
        rid: Optional[str]
        self_property: Optional[str]
        ts: Optional[float]
        users: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                create_mode: Optional[Union[str, CreateMode]] = ..., 
                id: str, 
                restore_parameters: Optional[ResourceRestoreParameters] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.RestorableSqlResourcesGetResult(_Model):
        collection_names: Optional[list[str]]
        database_name: Optional[str]
        id: Optional[str]
        name: Optional[str]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                collection_names: Optional[list[str]] = ..., 
                database_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.RestorableTableGetResult(_Model):
        id: Optional[str]
        name: Optional[str]
        properties: Optional[RestorableTableProperties]
        type: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RestorableTableProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.RestorableTableProperties(_Model):
        resource: Optional[RestorableTablePropertiesResource]

        @overload
        def __init__(
                self, 
                *, 
                resource: Optional[RestorableTablePropertiesResource] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.RestorableTablePropertiesResource(_Model):
        can_undelete: Optional[str]
        can_undelete_reason: Optional[str]
        event_timestamp: Optional[str]
        operation_type: Optional[Union[str, OperationType]]
        owner_id: Optional[str]
        owner_resource_id: Optional[str]
        rid: Optional[str]


    class azure.mgmt.cosmosdb.models.RestorableTableResourcesGetResult(_Model):
        id: Optional[str]
        name: Optional[str]
        type: Optional[str]


    class azure.mgmt.cosmosdb.models.RestoreMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        POINT_IN_TIME = "PointInTime"


    class azure.mgmt.cosmosdb.models.RestoreParameters(RestoreParametersBase):
        databases_to_restore: Optional[list[DatabaseRestoreResource]]
        gremlin_databases_to_restore: Optional[list[GremlinDatabaseRestoreResource]]
        restore_mode: Optional[Union[str, RestoreMode]]
        restore_source: str
        restore_timestamp_in_utc: datetime
        restore_with_ttl_disabled: bool
        source_backup_location: Optional[str]
        tables_to_restore: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                databases_to_restore: Optional[list[DatabaseRestoreResource]] = ..., 
                gremlin_databases_to_restore: Optional[list[GremlinDatabaseRestoreResource]] = ..., 
                restore_mode: Optional[Union[str, RestoreMode]] = ..., 
                restore_source: Optional[str] = ..., 
                restore_timestamp_in_utc: Optional[datetime] = ..., 
                restore_with_ttl_disabled: Optional[bool] = ..., 
                source_backup_location: Optional[str] = ..., 
                tables_to_restore: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.RestoreParametersBase(_Model):
        restore_source: Optional[str]
        restore_timestamp_in_utc: Optional[datetime]
        restore_with_ttl_disabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                restore_source: Optional[str] = ..., 
                restore_timestamp_in_utc: Optional[datetime] = ..., 
                restore_with_ttl_disabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.RetrieveThroughputParameters(ARMResourceProperties):
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: RetrieveThroughputProperties
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: Optional[str] = ..., 
                properties: RetrieveThroughputProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.RetrieveThroughputProperties(_Model):
        resource: RetrieveThroughputPropertiesResource

        @overload
        def __init__(
                self, 
                *, 
                resource: RetrieveThroughputPropertiesResource
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.RetrieveThroughputPropertiesResource(_Model):
        physical_partition_ids: list[PhysicalPartitionId]

        @overload
        def __init__(
                self, 
                *, 
                physical_partition_ids: list[PhysicalPartitionId]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.Role(_Model):
        db: Optional[str]
        role: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                db: Optional[str] = ..., 
                role: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.RoleDefinitionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BUILT_IN_ROLE = "BuiltInRole"
        CUSTOM_ROLE = "CustomRole"


    class azure.mgmt.cosmosdb.models.ScheduledEventStrategy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IGNORE = "Ignore"
        STOP_ANY = "StopAny"
        STOP_BY_RACK = "StopByRack"


    class azure.mgmt.cosmosdb.models.SeedNode(_Model):
        ip_address: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                ip_address: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.ServerVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FIVE0 = "5.0"
        FOUR0 = "4.0"
        FOUR2 = "4.2"
        SEVEN0 = "7.0"
        SIX0 = "6.0"
        THREE2 = "3.2"
        THREE6 = "3.6"


    class azure.mgmt.cosmosdb.models.ServiceResource(ProxyResource):
        id: str
        name: str
        properties: Optional[ServiceResourceProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ServiceResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.ServiceResourceCreateUpdateParameters(_Model):
        properties: Optional[ServiceResourceCreateUpdateProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ServiceResourceCreateUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.ServiceResourceCreateUpdateProperties(_Model):
        instance_count: Optional[int]
        instance_size: Optional[Union[str, ServiceSize]]
        service_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_count: Optional[int] = ..., 
                instance_size: Optional[Union[str, ServiceSize]] = ..., 
                service_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.ServiceResourceProperties(_Model):
        creation_time: Optional[datetime]
        instance_count: Optional[int]
        instance_size: Optional[Union[str, ServiceSize]]
        service_type: str
        status: Optional[Union[str, ServiceStatus]]

        @overload
        def __init__(
                self, 
                *, 
                instance_count: Optional[int] = ..., 
                instance_size: Optional[Union[str, ServiceSize]] = ..., 
                service_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.ServiceSize(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COSMOS_D16_S = "Cosmos.D16s"
        COSMOS_D4_S = "Cosmos.D4s"
        COSMOS_D8_S = "Cosmos.D8s"


    class azure.mgmt.cosmosdb.models.ServiceStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "Creating"
        DELETING = "Deleting"
        ERROR = "Error"
        RUNNING = "Running"
        STOPPED = "Stopped"
        UPDATING = "Updating"


    class azure.mgmt.cosmosdb.models.ServiceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DATA_TRANSFER = "DataTransfer"
        GRAPH_API_COMPUTE = "GraphAPICompute"
        MATERIALIZED_VIEWS_BUILDER = "MaterializedViewsBuilder"
        SQL_DEDICATED_GATEWAY = "SqlDedicatedGateway"


    class azure.mgmt.cosmosdb.models.Severity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ERROR = "Error"
        WARNING = "Warning"


    class azure.mgmt.cosmosdb.models.SoftDeleteActionKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PERMANENT_DELETE_RESOURCE = "PermanentDeleteResource"
        RESTORE_SOFT_DELETED_RESOURCE = "RestoreSoftDeletedResource"


    class azure.mgmt.cosmosdb.models.SoftDeleteConfiguration(_Model):
        min_minutes_before_permanent_deletion_allowed: Optional[int]
        soft_delete_retention_period_in_minutes: Optional[int]
        soft_deletion_enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                min_minutes_before_permanent_deletion_allowed: Optional[int] = ..., 
                soft_delete_retention_period_in_minutes: Optional[int] = ..., 
                soft_deletion_enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.SoftDeletedDatabaseAccountGetResult(ProxyResource):
        id: str
        name: str
        properties: Optional[SoftDeletedDatabaseAccountProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SoftDeletedDatabaseAccountProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.SoftDeletedDatabaseAccountProperties(_Model):
        account_name: Optional[str]
        resource: Optional[SoftDeletedDatabaseAccountResource]
        soft_delete_configuration: Optional[SoftDeleteConfiguration]
        soft_deletion_metadata: Optional[SoftDeletionMetadata]

        @overload
        def __init__(
                self, 
                *, 
                account_name: Optional[str] = ..., 
                resource: Optional[SoftDeletedDatabaseAccountResource] = ..., 
                soft_delete_configuration: Optional[SoftDeleteConfiguration] = ..., 
                soft_deletion_metadata: Optional[SoftDeletionMetadata] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.SoftDeletedDatabaseAccountResource(_Model):
        locations: Optional[list[Location]]
        read_locations: Optional[list[Location]]
        write_locations: Optional[list[Location]]

        @overload
        def __init__(
                self, 
                *, 
                locations: Optional[list[Location]] = ..., 
                read_locations: Optional[list[Location]] = ..., 
                write_locations: Optional[list[Location]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.SoftDeletedDatabaseAccountsListResult(_Model):
        next_link: Optional[str]
        value: list[SoftDeletedDatabaseAccountGetResult]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[SoftDeletedDatabaseAccountGetResult]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.SoftDeletedSqlContainerGetResult(ProxyResource):
        id: str
        name: str
        properties: Optional[SoftDeletedSqlContainerProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SoftDeletedSqlContainerProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.SoftDeletedSqlContainerProperties(_Model):
        resource: Optional[SoftDeletedSqlContainerResource]
        soft_deletion_metadata: Optional[SoftDeletionMetadata]

        @overload
        def __init__(
                self, 
                *, 
                resource: Optional[SoftDeletedSqlContainerResource] = ..., 
                soft_deletion_metadata: Optional[SoftDeletionMetadata] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.SoftDeletedSqlContainerResource(_Model):
        default_ttl: Optional[int]
        id: str
        partition_key: Optional[ContainerPartitionKey]
        rid: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                default_ttl: Optional[int] = ..., 
                id: str, 
                partition_key: Optional[ContainerPartitionKey] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.SoftDeletedSqlContainersListResult(_Model):
        next_link: Optional[str]
        value: list[SoftDeletedSqlContainerGetResult]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[SoftDeletedSqlContainerGetResult]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.SoftDeletedSqlDatabaseGetResult(ProxyResource):
        id: str
        name: str
        properties: Optional[SoftDeletedSqlDatabaseProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SoftDeletedSqlDatabaseProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.SoftDeletedSqlDatabaseProperties(_Model):
        resource: Optional[SoftDeletedSqlDatabaseResource]
        soft_deletion_metadata: Optional[SoftDeletionMetadata]

        @overload
        def __init__(
                self, 
                *, 
                resource: Optional[SoftDeletedSqlDatabaseResource] = ..., 
                soft_deletion_metadata: Optional[SoftDeletionMetadata] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.SoftDeletedSqlDatabaseResource(_Model):
        id: str
        rid: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.SoftDeletedSqlDatabasesListResult(_Model):
        next_link: Optional[str]
        value: list[SoftDeletedSqlDatabaseGetResult]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[SoftDeletedSqlDatabaseGetResult]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.SoftDeletionMetadata(_Model):
        is_soft_deleted: Optional[bool]
        soft_deletion_resource_expiration_timestamp: Optional[int]
        soft_deletion_start_timestamp: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                is_soft_deleted: Optional[bool] = ..., 
                soft_deletion_resource_expiration_timestamp: Optional[int] = ..., 
                soft_deletion_start_timestamp: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.SpatialSpec(_Model):
        path: Optional[str]
        types: Optional[list[Union[str, SpatialType]]]

        @overload
        def __init__(
                self, 
                *, 
                path: Optional[str] = ..., 
                types: Optional[list[Union[str, SpatialType]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.SpatialType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LINE_STRING = "LineString"
        MULTI_POLYGON = "MultiPolygon"
        POINT = "Point"
        POLYGON = "Polygon"


    class azure.mgmt.cosmosdb.models.SqlContainerCreateUpdateParameters(ARMResourceProperties):
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: SqlContainerCreateUpdateProperties
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: Optional[str] = ..., 
                properties: SqlContainerCreateUpdateProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.SqlContainerCreateUpdateProperties(_Model):
        options: Optional[CreateUpdateOptions]
        resource: SqlContainerResource

        @overload
        def __init__(
                self, 
                *, 
                options: Optional[CreateUpdateOptions] = ..., 
                resource: SqlContainerResource
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.SqlContainerGetProperties(_Model):
        options: Optional[SqlContainerGetPropertiesOptions]
        resource: Optional[SqlContainerGetPropertiesResource]

        @overload
        def __init__(
                self, 
                *, 
                options: Optional[SqlContainerGetPropertiesOptions] = ..., 
                resource: Optional[SqlContainerGetPropertiesResource] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.SqlContainerGetPropertiesOptions(OptionsResource):
        autoscale_settings: AutoscaleSettings
        throughput: int

        @overload
        def __init__(
                self, 
                *, 
                autoscale_settings: Optional[AutoscaleSettings] = ..., 
                throughput: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.SqlContainerGetPropertiesResource(SqlContainerResource):
        analytical_storage_ttl: int
        client_encryption_policy: ClientEncryptionPolicy
        computed_properties: list[ComputedProperty]
        conflict_resolution_policy: ConflictResolutionPolicy
        create_mode: Union[str, CreateMode]
        data_masking_policy: DataMaskingPolicy
        default_ttl: int
        etag: Optional[str]
        full_text_policy: FullTextPolicy
        id: str
        indexing_policy: IndexingPolicy
        materialized_view_definition: MaterializedViewDefinition
        materialized_views: list[MaterializedViewDetails]
        materialized_views_properties: MaterializedViewsProperties
        partition_key: ContainerPartitionKey
        restore_parameters: ResourceRestoreParameters
        rid: Optional[str]
        ts: Optional[float]
        unique_key_policy: UniqueKeyPolicy
        vector_embedding_policy: VectorEmbeddingPolicy

        @overload
        def __init__(
                self, 
                *, 
                analytical_storage_ttl: Optional[int] = ..., 
                client_encryption_policy: Optional[ClientEncryptionPolicy] = ..., 
                computed_properties: Optional[list[ComputedProperty]] = ..., 
                conflict_resolution_policy: Optional[ConflictResolutionPolicy] = ..., 
                create_mode: Optional[Union[str, CreateMode]] = ..., 
                data_masking_policy: Optional[DataMaskingPolicy] = ..., 
                default_ttl: Optional[int] = ..., 
                full_text_policy: Optional[FullTextPolicy] = ..., 
                id: str, 
                indexing_policy: Optional[IndexingPolicy] = ..., 
                materialized_view_definition: Optional[MaterializedViewDefinition] = ..., 
                materialized_views: Optional[list[MaterializedViewDetails]] = ..., 
                materialized_views_properties: Optional[MaterializedViewsProperties] = ..., 
                partition_key: Optional[ContainerPartitionKey] = ..., 
                restore_parameters: Optional[ResourceRestoreParameters] = ..., 
                unique_key_policy: Optional[UniqueKeyPolicy] = ..., 
                vector_embedding_policy: Optional[VectorEmbeddingPolicy] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.SqlContainerGetResults(ProxyResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: Optional[str]
        name: str
        properties: Optional[SqlContainerGetProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[SqlContainerGetProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.SqlContainerResource(_Model):
        analytical_storage_ttl: Optional[int]
        client_encryption_policy: Optional[ClientEncryptionPolicy]
        computed_properties: Optional[list[ComputedProperty]]
        conflict_resolution_policy: Optional[ConflictResolutionPolicy]
        create_mode: Optional[Union[str, CreateMode]]
        data_masking_policy: Optional[DataMaskingPolicy]
        default_ttl: Optional[int]
        full_text_policy: Optional[FullTextPolicy]
        id: str
        indexing_policy: Optional[IndexingPolicy]
        materialized_view_definition: Optional[MaterializedViewDefinition]
        materialized_views: Optional[list[MaterializedViewDetails]]
        materialized_views_properties: Optional[MaterializedViewsProperties]
        partition_key: Optional[ContainerPartitionKey]
        restore_parameters: Optional[ResourceRestoreParameters]
        unique_key_policy: Optional[UniqueKeyPolicy]
        vector_embedding_policy: Optional[VectorEmbeddingPolicy]

        @overload
        def __init__(
                self, 
                *, 
                analytical_storage_ttl: Optional[int] = ..., 
                client_encryption_policy: Optional[ClientEncryptionPolicy] = ..., 
                computed_properties: Optional[list[ComputedProperty]] = ..., 
                conflict_resolution_policy: Optional[ConflictResolutionPolicy] = ..., 
                create_mode: Optional[Union[str, CreateMode]] = ..., 
                data_masking_policy: Optional[DataMaskingPolicy] = ..., 
                default_ttl: Optional[int] = ..., 
                full_text_policy: Optional[FullTextPolicy] = ..., 
                id: str, 
                indexing_policy: Optional[IndexingPolicy] = ..., 
                materialized_view_definition: Optional[MaterializedViewDefinition] = ..., 
                materialized_views: Optional[list[MaterializedViewDetails]] = ..., 
                materialized_views_properties: Optional[MaterializedViewsProperties] = ..., 
                partition_key: Optional[ContainerPartitionKey] = ..., 
                restore_parameters: Optional[ResourceRestoreParameters] = ..., 
                unique_key_policy: Optional[UniqueKeyPolicy] = ..., 
                vector_embedding_policy: Optional[VectorEmbeddingPolicy] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.SqlDatabaseCreateUpdateParameters(ARMResourceProperties):
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: SqlDatabaseCreateUpdateProperties
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: Optional[str] = ..., 
                properties: SqlDatabaseCreateUpdateProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.SqlDatabaseCreateUpdateProperties(_Model):
        options: Optional[CreateUpdateOptions]
        resource: SqlDatabaseResource

        @overload
        def __init__(
                self, 
                *, 
                options: Optional[CreateUpdateOptions] = ..., 
                resource: SqlDatabaseResource
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.SqlDatabaseGetProperties(_Model):
        options: Optional[SqlDatabaseGetPropertiesOptions]
        resource: Optional[SqlDatabaseGetPropertiesResource]

        @overload
        def __init__(
                self, 
                *, 
                options: Optional[SqlDatabaseGetPropertiesOptions] = ..., 
                resource: Optional[SqlDatabaseGetPropertiesResource] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.SqlDatabaseGetPropertiesOptions(OptionsResource):
        autoscale_settings: AutoscaleSettings
        throughput: int

        @overload
        def __init__(
                self, 
                *, 
                autoscale_settings: Optional[AutoscaleSettings] = ..., 
                throughput: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.SqlDatabaseGetPropertiesResource(SqlDatabaseResource):
        colls: Optional[str]
        create_mode: Union[str, CreateMode]
        etag: Optional[str]
        id: str
        restore_parameters: ResourceRestoreParameters
        rid: Optional[str]
        ts: Optional[float]
        users: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                colls: Optional[str] = ..., 
                create_mode: Optional[Union[str, CreateMode]] = ..., 
                id: str, 
                restore_parameters: Optional[ResourceRestoreParameters] = ..., 
                users: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.SqlDatabaseGetResults(ProxyResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: Optional[str]
        name: str
        properties: Optional[SqlDatabaseGetProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[SqlDatabaseGetProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.SqlDatabaseResource(_Model):
        create_mode: Optional[Union[str, CreateMode]]
        id: str
        restore_parameters: Optional[ResourceRestoreParameters]

        @overload
        def __init__(
                self, 
                *, 
                create_mode: Optional[Union[str, CreateMode]] = ..., 
                id: str, 
                restore_parameters: Optional[ResourceRestoreParameters] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.SqlDedicatedGatewayRegionalServiceResource(RegionalServiceResource):
        location: str
        name: str
        sql_dedicated_gateway_endpoint: Optional[str]
        status: Union[str, ServiceStatus]


    class azure.mgmt.cosmosdb.models.SqlDedicatedGatewayServiceResourceCreateUpdateProperties(ServiceResourceCreateUpdateProperties, discriminator='SqlDedicatedGateway'):
        dedicated_gateway_type: Optional[Union[str, DedicatedGatewayType]]
        instance_count: int
        instance_size: Union[str, ServiceSize]
        service_type: Literal[ServiceType.SQL_DEDICATED_GATEWAY]

        @overload
        def __init__(
                self, 
                *, 
                dedicated_gateway_type: Optional[Union[str, DedicatedGatewayType]] = ..., 
                instance_count: Optional[int] = ..., 
                instance_size: Optional[Union[str, ServiceSize]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.SqlDedicatedGatewayServiceResourceProperties(ServiceResourceProperties, discriminator='SqlDedicatedGateway'):
        creation_time: datetime
        dedicated_gateway_type: Optional[Union[str, DedicatedGatewayType]]
        instance_count: int
        instance_size: Union[str, ServiceSize]
        locations: Optional[list[SqlDedicatedGatewayRegionalServiceResource]]
        service_type: Literal[ServiceType.SQL_DEDICATED_GATEWAY]
        sql_dedicated_gateway_endpoint: Optional[str]
        status: Union[str, ServiceStatus]

        @overload
        def __init__(
                self, 
                *, 
                dedicated_gateway_type: Optional[Union[str, DedicatedGatewayType]] = ..., 
                instance_count: Optional[int] = ..., 
                instance_size: Optional[Union[str, ServiceSize]] = ..., 
                sql_dedicated_gateway_endpoint: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.SqlRoleAssignmentCreateUpdateParameters(_Model):
        properties: Optional[SqlRoleAssignmentResource]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SqlRoleAssignmentResource] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.SqlRoleAssignmentGetResults(ProxyResource):
        id: str
        name: str
        properties: Optional[SqlRoleAssignmentResource]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SqlRoleAssignmentResource] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.SqlRoleAssignmentResource(_Model):
        principal_id: Optional[str]
        role_definition_id: Optional[str]
        scope: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                principal_id: Optional[str] = ..., 
                role_definition_id: Optional[str] = ..., 
                scope: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.SqlRoleDefinitionCreateUpdateParameters(_Model):
        properties: Optional[SqlRoleDefinitionResource]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SqlRoleDefinitionResource] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.SqlRoleDefinitionGetResults(ProxyResource):
        id: str
        name: str
        properties: Optional[SqlRoleDefinitionResource]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SqlRoleDefinitionResource] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.SqlRoleDefinitionResource(_Model):
        assignable_scopes: Optional[list[str]]
        permissions: Optional[list[Permission]]
        role_name: Optional[str]
        type: Optional[Union[str, RoleDefinitionType]]

        @overload
        def __init__(
                self, 
                *, 
                assignable_scopes: Optional[list[str]] = ..., 
                permissions: Optional[list[Permission]] = ..., 
                role_name: Optional[str] = ..., 
                type: Optional[Union[str, RoleDefinitionType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.SqlStoredProcedureCreateUpdateParameters(ARMResourceProperties):
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: SqlStoredProcedureCreateUpdateProperties
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: Optional[str] = ..., 
                properties: SqlStoredProcedureCreateUpdateProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.SqlStoredProcedureCreateUpdateProperties(_Model):
        options: Optional[CreateUpdateOptions]
        resource: SqlStoredProcedureResource

        @overload
        def __init__(
                self, 
                *, 
                options: Optional[CreateUpdateOptions] = ..., 
                resource: SqlStoredProcedureResource
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.SqlStoredProcedureGetProperties(_Model):
        resource: Optional[SqlStoredProcedureGetPropertiesResource]

        @overload
        def __init__(
                self, 
                *, 
                resource: Optional[SqlStoredProcedureGetPropertiesResource] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.SqlStoredProcedureGetPropertiesResource(SqlStoredProcedureResource):
        body: str
        etag: Optional[str]
        id: str
        rid: Optional[str]
        ts: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                body: Optional[str] = ..., 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.SqlStoredProcedureGetResults(ProxyResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: Optional[str]
        name: str
        properties: Optional[SqlStoredProcedureGetProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[SqlStoredProcedureGetProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.SqlStoredProcedureResource(_Model):
        body: Optional[str]
        id: str

        @overload
        def __init__(
                self, 
                *, 
                body: Optional[str] = ..., 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.SqlTriggerCreateUpdateParameters(ARMResourceProperties):
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: SqlTriggerCreateUpdateProperties
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: Optional[str] = ..., 
                properties: SqlTriggerCreateUpdateProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.SqlTriggerCreateUpdateProperties(_Model):
        options: Optional[CreateUpdateOptions]
        resource: SqlTriggerResource

        @overload
        def __init__(
                self, 
                *, 
                options: Optional[CreateUpdateOptions] = ..., 
                resource: SqlTriggerResource
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.SqlTriggerGetProperties(_Model):
        resource: Optional[SqlTriggerGetPropertiesResource]

        @overload
        def __init__(
                self, 
                *, 
                resource: Optional[SqlTriggerGetPropertiesResource] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.SqlTriggerGetPropertiesResource(SqlTriggerResource):
        body: str
        etag: Optional[str]
        id: str
        rid: Optional[str]
        trigger_operation: Union[str, TriggerOperation]
        trigger_type: Union[str, TriggerType]
        ts: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                body: Optional[str] = ..., 
                id: str, 
                trigger_operation: Optional[Union[str, TriggerOperation]] = ..., 
                trigger_type: Optional[Union[str, TriggerType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.SqlTriggerGetResults(ProxyResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: Optional[str]
        name: str
        properties: Optional[SqlTriggerGetProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[SqlTriggerGetProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.SqlTriggerResource(_Model):
        body: Optional[str]
        id: str
        trigger_operation: Optional[Union[str, TriggerOperation]]
        trigger_type: Optional[Union[str, TriggerType]]

        @overload
        def __init__(
                self, 
                *, 
                body: Optional[str] = ..., 
                id: str, 
                trigger_operation: Optional[Union[str, TriggerOperation]] = ..., 
                trigger_type: Optional[Union[str, TriggerType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.SqlUserDefinedFunctionCreateUpdateParameters(ARMResourceProperties):
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: SqlUserDefinedFunctionCreateUpdateProperties
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: Optional[str] = ..., 
                properties: SqlUserDefinedFunctionCreateUpdateProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.SqlUserDefinedFunctionCreateUpdateProperties(_Model):
        options: Optional[CreateUpdateOptions]
        resource: SqlUserDefinedFunctionResource

        @overload
        def __init__(
                self, 
                *, 
                options: Optional[CreateUpdateOptions] = ..., 
                resource: SqlUserDefinedFunctionResource
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.SqlUserDefinedFunctionGetProperties(_Model):
        resource: Optional[SqlUserDefinedFunctionGetPropertiesResource]

        @overload
        def __init__(
                self, 
                *, 
                resource: Optional[SqlUserDefinedFunctionGetPropertiesResource] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.SqlUserDefinedFunctionGetPropertiesResource(SqlUserDefinedFunctionResource):
        body: str
        etag: Optional[str]
        id: str
        rid: Optional[str]
        ts: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                body: Optional[str] = ..., 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.SqlUserDefinedFunctionGetResults(ProxyResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: Optional[str]
        name: str
        properties: Optional[SqlUserDefinedFunctionGetProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[SqlUserDefinedFunctionGetProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.SqlUserDefinedFunctionResource(_Model):
        body: Optional[str]
        id: str

        @overload
        def __init__(
                self, 
                *, 
                body: Optional[str] = ..., 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.Status(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        INITIALIZING = "Initializing"
        INTERNALLY_READY = "InternallyReady"
        ONLINE = "Online"
        SUCCEEDED = "Succeeded"
        UNINITIALIZED = "Uninitialized"
        UPDATING = "Updating"


    class azure.mgmt.cosmosdb.models.SupportedActions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLE = "Disable"
        ENABLE = "Enable"


    class azure.mgmt.cosmosdb.models.SystemData(_Model):
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


    class azure.mgmt.cosmosdb.models.TableCreateUpdateParameters(ARMResourceProperties):
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: TableCreateUpdateProperties
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: Optional[str] = ..., 
                properties: TableCreateUpdateProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.TableCreateUpdateProperties(_Model):
        options: Optional[CreateUpdateOptions]
        resource: TableResource

        @overload
        def __init__(
                self, 
                *, 
                options: Optional[CreateUpdateOptions] = ..., 
                resource: TableResource
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.TableGetProperties(_Model):
        options: Optional[TableGetPropertiesOptions]
        resource: Optional[TableGetPropertiesResource]

        @overload
        def __init__(
                self, 
                *, 
                options: Optional[TableGetPropertiesOptions] = ..., 
                resource: Optional[TableGetPropertiesResource] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.TableGetPropertiesOptions(OptionsResource):
        autoscale_settings: AutoscaleSettings
        throughput: int

        @overload
        def __init__(
                self, 
                *, 
                autoscale_settings: Optional[AutoscaleSettings] = ..., 
                throughput: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.TableGetPropertiesResource(TableResource):
        create_mode: Union[str, CreateMode]
        etag: Optional[str]
        id: str
        restore_parameters: ResourceRestoreParameters
        rid: Optional[str]
        ts: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                create_mode: Optional[Union[str, CreateMode]] = ..., 
                id: str, 
                restore_parameters: Optional[ResourceRestoreParameters] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.TableGetResults(ProxyResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: Optional[str]
        name: str
        properties: Optional[TableGetProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[TableGetProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.TableResource(_Model):
        create_mode: Optional[Union[str, CreateMode]]
        id: str
        restore_parameters: Optional[ResourceRestoreParameters]

        @overload
        def __init__(
                self, 
                *, 
                create_mode: Optional[Union[str, CreateMode]] = ..., 
                id: str, 
                restore_parameters: Optional[ResourceRestoreParameters] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.TableRoleAssignmentResource(ProxyResource):
        id: str
        name: str
        properties: Optional[TableRoleAssignmentResourceProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[TableRoleAssignmentResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.TableRoleAssignmentResourceProperties(_Model):
        principal_id: Optional[str]
        provisioning_state: Optional[str]
        role_definition_id: Optional[str]
        scope: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                principal_id: Optional[str] = ..., 
                role_definition_id: Optional[str] = ..., 
                scope: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.TableRoleDefinitionResource(ProxyResource):
        id: str
        name: str
        properties: Optional[TableRoleDefinitionResourceProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[TableRoleDefinitionResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.TableRoleDefinitionResourceProperties(_Model):
        assignable_scopes: Optional[list[str]]
        id: Optional[str]
        permissions: Optional[list[Permission]]
        role_name: Optional[str]
        type: Optional[Union[str, RoleDefinitionType]]

        @overload
        def __init__(
                self, 
                *, 
                assignable_scopes: Optional[list[str]] = ..., 
                id: Optional[str] = ..., 
                permissions: Optional[list[Permission]] = ..., 
                role_name: Optional[str] = ..., 
                type: Optional[Union[str, RoleDefinitionType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.ThroughputBucketResource(_Model):
        id: int
        is_default_bucket: Optional[bool]
        max_throughput_percentage: int

        @overload
        def __init__(
                self, 
                *, 
                id: int, 
                is_default_bucket: Optional[bool] = ..., 
                max_throughput_percentage: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.ThroughputPolicyResource(_Model):
        increment_percent: Optional[int]
        is_enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                increment_percent: Optional[int] = ..., 
                is_enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.ThroughputPolicyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM = "custom"
        EQUAL = "equal"
        NONE = "none"


    class azure.mgmt.cosmosdb.models.ThroughputPoolAccountProperties(_Model):
        account_instance_id: Optional[str]
        account_location: Optional[str]
        account_resource_identifier: Optional[str]
        provisioning_state: Optional[Union[str, Status]]

        @overload
        def __init__(
                self, 
                *, 
                account_location: Optional[str] = ..., 
                account_resource_identifier: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.ThroughputPoolAccountResource(ProxyResource):
        id: str
        name: str
        properties: Optional[ThroughputPoolAccountProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ThroughputPoolAccountProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.ThroughputPoolProperties(_Model):
        max_throughput: Optional[int]
        provisioning_state: Optional[Union[str, Status]]

        @overload
        def __init__(
                self, 
                *, 
                max_throughput: Optional[int] = ..., 
                provisioning_state: Optional[Union[str, Status]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.ThroughputPoolResource(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[ThroughputPoolProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[ThroughputPoolProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.ThroughputPoolUpdate(_Model):
        properties: Optional[ThroughputPoolProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ThroughputPoolProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.ThroughputSettingsGetProperties(_Model):
        resource: Optional[ThroughputSettingsGetPropertiesResource]

        @overload
        def __init__(
                self, 
                *, 
                resource: Optional[ThroughputSettingsGetPropertiesResource] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.ThroughputSettingsGetPropertiesResource(ThroughputSettingsResource):
        autoscale_settings: AutoscaleSettingsResource
        etag: Optional[str]
        instant_maximum_throughput: str
        minimum_throughput: str
        offer_replace_pending: str
        rid: Optional[str]
        soft_allowed_maximum_throughput: str
        throughput: int
        throughput_buckets: list[ThroughputBucketResource]
        ts: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                autoscale_settings: Optional[AutoscaleSettingsResource] = ..., 
                throughput: Optional[int] = ..., 
                throughput_buckets: Optional[list[ThroughputBucketResource]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.ThroughputSettingsGetResults(ProxyResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: Optional[str]
        name: str
        properties: Optional[ThroughputSettingsGetProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[ThroughputSettingsGetProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.ThroughputSettingsResource(_Model):
        autoscale_settings: Optional[AutoscaleSettingsResource]
        instant_maximum_throughput: Optional[str]
        minimum_throughput: Optional[str]
        offer_replace_pending: Optional[str]
        soft_allowed_maximum_throughput: Optional[str]
        throughput: Optional[int]
        throughput_buckets: Optional[list[ThroughputBucketResource]]

        @overload
        def __init__(
                self, 
                *, 
                autoscale_settings: Optional[AutoscaleSettingsResource] = ..., 
                throughput: Optional[int] = ..., 
                throughput_buckets: Optional[list[ThroughputBucketResource]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.ThroughputSettingsUpdateParameters(ARMResourceProperties):
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: ThroughputSettingsUpdateProperties
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: Optional[str] = ..., 
                properties: ThroughputSettingsUpdateProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cosmosdb.models.ThroughputSettingsUpdateProperties(_Model):
        resource: ThroughputSettingsResource

        @overload
        def __init__(
                self, 
                *, 
                resource: ThroughputSettingsResource
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.TrackedResource(Resource):
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


    class azure.mgmt.cosmosdb.models.TriggerOperation(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL = "All"
        CREATE = "Create"
        DELETE = "Delete"
        REPLACE = "Replace"
        UPDATE = "Update"


    class azure.mgmt.cosmosdb.models.TriggerType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        POST = "Post"
        PRE = "Pre"


    class azure.mgmt.cosmosdb.models.Type(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CASSANDRA = "Cassandra"
        CASSANDRA_CONNECTOR_METADATA = "CassandraConnectorMetadata"
        GREMLIN = "Gremlin"
        GREMLIN_V2 = "GremlinV2"
        MONGO_DB = "MongoDB"
        SQL = "Sql"
        SQL_DEDICATED_GATEWAY = "SqlDedicatedGateway"
        TABLE = "Table"
        UNDEFINED = "Undefined"


    class azure.mgmt.cosmosdb.models.UniqueKey(_Model):
        paths: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                paths: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.UniqueKeyPolicy(_Model):
        unique_keys: Optional[list[UniqueKey]]

        @overload
        def __init__(
                self, 
                *, 
                unique_keys: Optional[list[UniqueKey]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.UnitType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BYTES = "Bytes"
        BYTES_PER_SECOND = "BytesPerSecond"
        COUNT = "Count"
        COUNT_PER_SECOND = "CountPerSecond"
        MILLISECONDS = "Milliseconds"
        PERCENT = "Percent"
        SECONDS = "Seconds"


    class azure.mgmt.cosmosdb.models.Usage(_Model):
        current_value: Optional[int]
        limit: Optional[int]
        name: Optional[MetricName]
        quota_period: Optional[str]
        unit: Optional[Union[str, UnitType]]


    class azure.mgmt.cosmosdb.models.VectorDataType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FLOAT16 = "float16"
        FLOAT32 = "float32"
        INT8 = "int8"
        UINT8 = "uint8"


    class azure.mgmt.cosmosdb.models.VectorEmbedding(_Model):
        data_type: Union[str, VectorDataType]
        dimensions: int
        distance_function: Union[str, DistanceFunction]
        path: str

        @overload
        def __init__(
                self, 
                *, 
                data_type: Union[str, VectorDataType], 
                dimensions: int, 
                distance_function: Union[str, DistanceFunction], 
                path: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.VectorEmbeddingPolicy(_Model):
        vector_embeddings: Optional[list[VectorEmbedding]]

        @overload
        def __init__(
                self, 
                *, 
                vector_embeddings: Optional[list[VectorEmbedding]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.VectorIndex(_Model):
        indexing_search_list_size: Optional[int]
        path: str
        quantization_byte_size: Optional[int]
        type: Union[str, VectorIndexType]
        vector_index_shard_key: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                indexing_search_list_size: Optional[int] = ..., 
                path: str, 
                quantization_byte_size: Optional[int] = ..., 
                type: Union[str, VectorIndexType], 
                vector_index_shard_key: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cosmosdb.models.VectorIndexType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISK_ANN = "diskANN"
        FLAT = "flat"
        QUANTIZED_FLAT = "quantizedFlat"


    class azure.mgmt.cosmosdb.models.VirtualNetworkRule(_Model):
        id: Optional[str]
        ignore_missing_v_net_service_endpoint: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                ignore_missing_v_net_service_endpoint: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.cosmosdb.operations

    class azure.mgmt.cosmosdb.operations.CassandraClustersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: ClusterResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ClusterResource]: ...

        @overload
        def begin_create_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: ClusterResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ClusterResource]: ...

        @overload
        def begin_create_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ClusterResource]: ...

        @distributed_trace
        def begin_deallocate(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                *, 
                x_ms_force_deallocate: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_invoke_command(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: CommandPostBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommandOutput]: ...

        @overload
        def begin_invoke_command(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: CommandPostBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommandOutput]: ...

        @overload
        def begin_invoke_command(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommandOutput]: ...

        @overload
        def begin_invoke_command_async(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: CommandAsyncPostBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommandPublicResource]: ...

        @overload
        def begin_invoke_command_async(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: CommandAsyncPostBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommandPublicResource]: ...

        @overload
        def begin_invoke_command_async(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommandPublicResource]: ...

        @distributed_trace
        def begin_start(
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
                body: ClusterResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ClusterResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: ClusterResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ClusterResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ClusterResource]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ClusterResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'cluster_name', 'backup_id', 'accept']}, api_versions_list=['2026-04-01-preview'])
        def get_backup(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                backup_id: str, 
                **kwargs: Any
            ) -> BackupResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'cluster_name', 'command_id', 'accept']}, api_versions_list=['2026-04-01-preview'])
        def get_command_async(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                command_id: str, 
                **kwargs: Any
            ) -> CommandPublicResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'cluster_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        def list_backups(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ItemPaged[BackupResource]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ClusterResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[ClusterResource]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'cluster_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        def list_command(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ItemPaged[CommandPublicResource]: ...

        @distributed_trace
        def status(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> CassandraClusterPublicStatus: ...


    class azure.mgmt.cosmosdb.operations.CassandraDataCentersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                data_center_name: str, 
                body: DataCenterResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DataCenterResource]: ...

        @overload
        def begin_create_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                data_center_name: str, 
                body: DataCenterResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DataCenterResource]: ...

        @overload
        def begin_create_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                data_center_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DataCenterResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                data_center_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                data_center_name: str, 
                body: DataCenterResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DataCenterResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                data_center_name: str, 
                body: DataCenterResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DataCenterResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                data_center_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DataCenterResource]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                data_center_name: str, 
                **kwargs: Any
            ) -> DataCenterResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DataCenterResource]: ...


    class azure.mgmt.cosmosdb.operations.CassandraResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_update_cassandra_keyspace(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                create_update_cassandra_keyspace_parameters: CassandraKeyspaceCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CassandraKeyspaceGetResults]: ...

        @overload
        def begin_create_update_cassandra_keyspace(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                create_update_cassandra_keyspace_parameters: CassandraKeyspaceCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CassandraKeyspaceGetResults]: ...

        @overload
        def begin_create_update_cassandra_keyspace(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                create_update_cassandra_keyspace_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CassandraKeyspaceGetResults]: ...

        @overload
        def begin_create_update_cassandra_role_assignment(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_assignment_id: str, 
                create_update_cassandra_role_assignment_parameters: CassandraRoleAssignmentResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CassandraRoleAssignmentResource]: ...

        @overload
        def begin_create_update_cassandra_role_assignment(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_assignment_id: str, 
                create_update_cassandra_role_assignment_parameters: CassandraRoleAssignmentResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CassandraRoleAssignmentResource]: ...

        @overload
        def begin_create_update_cassandra_role_assignment(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_assignment_id: str, 
                create_update_cassandra_role_assignment_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CassandraRoleAssignmentResource]: ...

        @overload
        def begin_create_update_cassandra_role_definition(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_definition_id: str, 
                create_update_cassandra_role_definition_parameters: CassandraRoleDefinitionResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CassandraRoleDefinitionResource]: ...

        @overload
        def begin_create_update_cassandra_role_definition(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_definition_id: str, 
                create_update_cassandra_role_definition_parameters: CassandraRoleDefinitionResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CassandraRoleDefinitionResource]: ...

        @overload
        def begin_create_update_cassandra_role_definition(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_definition_id: str, 
                create_update_cassandra_role_definition_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CassandraRoleDefinitionResource]: ...

        @overload
        def begin_create_update_cassandra_table(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                table_name: str, 
                create_update_cassandra_table_parameters: CassandraTableCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CassandraTableGetResults]: ...

        @overload
        def begin_create_update_cassandra_table(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                table_name: str, 
                create_update_cassandra_table_parameters: CassandraTableCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CassandraTableGetResults]: ...

        @overload
        def begin_create_update_cassandra_table(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                table_name: str, 
                create_update_cassandra_table_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CassandraTableGetResults]: ...

        @overload
        def begin_create_update_cassandra_view(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                view_name: str, 
                create_update_cassandra_view_parameters: CassandraViewCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CassandraViewGetResults]: ...

        @overload
        def begin_create_update_cassandra_view(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                view_name: str, 
                create_update_cassandra_view_parameters: CassandraViewCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CassandraViewGetResults]: ...

        @overload
        def begin_create_update_cassandra_view(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                view_name: str, 
                create_update_cassandra_view_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CassandraViewGetResults]: ...

        @distributed_trace
        def begin_delete_cassandra_keyspace(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_delete_cassandra_role_assignment(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_assignment_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_delete_cassandra_role_definition(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_definition_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_delete_cassandra_table(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                table_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_delete_cassandra_view(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                view_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_migrate_cassandra_keyspace_to_autoscale(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                **kwargs: Any
            ) -> LROPoller[ThroughputSettingsGetResults]: ...

        @distributed_trace
        def begin_migrate_cassandra_keyspace_to_manual_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                **kwargs: Any
            ) -> LROPoller[ThroughputSettingsGetResults]: ...

        @distributed_trace
        def begin_migrate_cassandra_table_to_autoscale(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                table_name: str, 
                **kwargs: Any
            ) -> LROPoller[ThroughputSettingsGetResults]: ...

        @distributed_trace
        def begin_migrate_cassandra_table_to_manual_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                table_name: str, 
                **kwargs: Any
            ) -> LROPoller[ThroughputSettingsGetResults]: ...

        @distributed_trace
        def begin_migrate_cassandra_view_to_autoscale(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                view_name: str, 
                **kwargs: Any
            ) -> LROPoller[ThroughputSettingsGetResults]: ...

        @distributed_trace
        def begin_migrate_cassandra_view_to_manual_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                view_name: str, 
                **kwargs: Any
            ) -> LROPoller[ThroughputSettingsGetResults]: ...

        @overload
        def begin_update_cassandra_keyspace_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                update_throughput_parameters: ThroughputSettingsUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ThroughputSettingsGetResults]: ...

        @overload
        def begin_update_cassandra_keyspace_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                update_throughput_parameters: ThroughputSettingsUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ThroughputSettingsGetResults]: ...

        @overload
        def begin_update_cassandra_keyspace_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                update_throughput_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ThroughputSettingsGetResults]: ...

        @overload
        def begin_update_cassandra_table_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                table_name: str, 
                update_throughput_parameters: ThroughputSettingsUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ThroughputSettingsGetResults]: ...

        @overload
        def begin_update_cassandra_table_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                table_name: str, 
                update_throughput_parameters: ThroughputSettingsUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ThroughputSettingsGetResults]: ...

        @overload
        def begin_update_cassandra_table_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                table_name: str, 
                update_throughput_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ThroughputSettingsGetResults]: ...

        @overload
        def begin_update_cassandra_view_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                view_name: str, 
                update_throughput_parameters: ThroughputSettingsUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ThroughputSettingsGetResults]: ...

        @overload
        def begin_update_cassandra_view_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                view_name: str, 
                update_throughput_parameters: ThroughputSettingsUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ThroughputSettingsGetResults]: ...

        @overload
        def begin_update_cassandra_view_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                view_name: str, 
                update_throughput_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ThroughputSettingsGetResults]: ...

        @distributed_trace
        def get_cassandra_keyspace(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                **kwargs: Any
            ) -> CassandraKeyspaceGetResults: ...

        @distributed_trace
        def get_cassandra_keyspace_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                **kwargs: Any
            ) -> ThroughputSettingsGetResults: ...

        @distributed_trace
        def get_cassandra_role_assignment(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_assignment_id: str, 
                **kwargs: Any
            ) -> CassandraRoleAssignmentResource: ...

        @distributed_trace
        def get_cassandra_role_definition(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_definition_id: str, 
                **kwargs: Any
            ) -> CassandraRoleDefinitionResource: ...

        @distributed_trace
        def get_cassandra_table(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                table_name: str, 
                **kwargs: Any
            ) -> CassandraTableGetResults: ...

        @distributed_trace
        def get_cassandra_table_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                table_name: str, 
                **kwargs: Any
            ) -> ThroughputSettingsGetResults: ...

        @distributed_trace
        def get_cassandra_view(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                view_name: str, 
                **kwargs: Any
            ) -> CassandraViewGetResults: ...

        @distributed_trace
        def get_cassandra_view_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                view_name: str, 
                **kwargs: Any
            ) -> ThroughputSettingsGetResults: ...

        @distributed_trace
        def list_cassandra_keyspaces(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[CassandraKeyspaceGetResults]: ...

        @distributed_trace
        def list_cassandra_role_assignments(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[CassandraRoleAssignmentResource]: ...

        @distributed_trace
        def list_cassandra_role_definitions(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[CassandraRoleDefinitionResource]: ...

        @distributed_trace
        def list_cassandra_tables(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[CassandraTableGetResults]: ...

        @distributed_trace
        def list_cassandra_views(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[CassandraViewGetResults]: ...


    class azure.mgmt.cosmosdb.operations.ChaosFaultOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_enable_disable(
                self, 
                resource_group_name: str, 
                account_name: str, 
                chaos_fault: str, 
                chaos_fault_request: ChaosFaultResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ChaosFaultResource]: ...

        @overload
        def begin_enable_disable(
                self, 
                resource_group_name: str, 
                account_name: str, 
                chaos_fault: str, 
                chaos_fault_request: ChaosFaultResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ChaosFaultResource]: ...

        @overload
        def begin_enable_disable(
                self, 
                resource_group_name: str, 
                account_name: str, 
                chaos_fault: str, 
                chaos_fault_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ChaosFaultResource]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                chaos_fault: str, 
                **kwargs: Any
            ) -> ChaosFaultResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ChaosFaultResource]: ...


    class azure.mgmt.cosmosdb.operations.CollectionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_metric_definitions(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_rid: str, 
                collection_rid: str, 
                **kwargs: Any
            ) -> ItemPaged[MetricDefinition]: ...

        @distributed_trace
        def list_metrics(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_rid: str, 
                collection_rid: str, 
                *, 
                filter: str, 
                **kwargs: Any
            ) -> ItemPaged[Metric]: ...

        @distributed_trace
        def list_usages(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_rid: str, 
                collection_rid: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Usage]: ...


    class azure.mgmt.cosmosdb.operations.CollectionPartitionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_metrics(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_rid: str, 
                collection_rid: str, 
                *, 
                filter: str, 
                **kwargs: Any
            ) -> ItemPaged[PartitionMetric]: ...

        @distributed_trace
        def list_usages(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_rid: str, 
                collection_rid: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[PartitionUsage]: ...


    class azure.mgmt.cosmosdb.operations.CollectionPartitionRegionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_metrics(
                self, 
                resource_group_name: str, 
                account_name: str, 
                region: str, 
                database_rid: str, 
                collection_rid: str, 
                *, 
                filter: str, 
                **kwargs: Any
            ) -> ItemPaged[PartitionMetric]: ...


    class azure.mgmt.cosmosdb.operations.CollectionRegionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_metrics(
                self, 
                resource_group_name: str, 
                account_name: str, 
                region: str, 
                database_rid: str, 
                collection_rid: str, 
                *, 
                filter: str, 
                **kwargs: Any
            ) -> ItemPaged[Metric]: ...


    class azure.mgmt.cosmosdb.operations.CopyJobsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'job_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        def cancel(
                self, 
                resource_group_name: str, 
                account_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> CopyJobGetResults: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'job_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        def complete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> CopyJobGetResults: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                job_name: str, 
                job_create_parameters: CopyJobGetResults, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CopyJobGetResults: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                job_name: str, 
                job_create_parameters: CopyJobGetResults, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CopyJobGetResults: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                job_name: str, 
                job_create_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CopyJobGetResults: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'job_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> CopyJobGetResults: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        def list_by_database_account(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[CopyJobGetResults]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'job_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        def pause(
                self, 
                resource_group_name: str, 
                account_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> CopyJobGetResults: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'job_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        def resume(
                self, 
                resource_group_name: str, 
                account_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> CopyJobGetResults: ...


    class azure.mgmt.cosmosdb.operations.DataTransferJobsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'job_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        def cancel(
                self, 
                resource_group_name: str, 
                account_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> DataTransferJobGetResults: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'job_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        def complete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> DataTransferJobGetResults: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                job_name: str, 
                job_create_parameters: CreateJobRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataTransferJobGetResults: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                job_name: str, 
                job_create_parameters: CreateJobRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataTransferJobGetResults: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                job_name: str, 
                job_create_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataTransferJobGetResults: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'job_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> DataTransferJobGetResults: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        def list_by_database_account(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DataTransferJobGetResults]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'job_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        def pause(
                self, 
                resource_group_name: str, 
                account_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> DataTransferJobGetResults: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'job_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        def resume(
                self, 
                resource_group_name: str, 
                account_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> DataTransferJobGetResults: ...


    class azure.mgmt.cosmosdb.operations.DatabaseAccountRegionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_metrics(
                self, 
                resource_group_name: str, 
                account_name: str, 
                region: str, 
                *, 
                filter: str, 
                **kwargs: Any
            ) -> ItemPaged[Metric]: ...


    class azure.mgmt.cosmosdb.operations.DatabaseAccountsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                create_update_parameters: DatabaseAccountCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DatabaseAccountGetResults]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                create_update_parameters: DatabaseAccountCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DatabaseAccountGetResults]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                create_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DatabaseAccountGetResults]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_failover_priority_change(
                self, 
                resource_group_name: str, 
                account_name: str, 
                failover_parameters: FailoverPolicies, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_failover_priority_change(
                self, 
                resource_group_name: str, 
                account_name: str, 
                failover_parameters: FailoverPolicies, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_failover_priority_change(
                self, 
                resource_group_name: str, 
                account_name: str, 
                failover_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_offline_region(
                self, 
                resource_group_name: str, 
                account_name: str, 
                region_parameter_for_offline: RegionForOnlineOffline, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_offline_region(
                self, 
                resource_group_name: str, 
                account_name: str, 
                region_parameter_for_offline: RegionForOnlineOffline, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_offline_region(
                self, 
                resource_group_name: str, 
                account_name: str, 
                region_parameter_for_offline: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_online_region(
                self, 
                resource_group_name: str, 
                account_name: str, 
                region_parameter_for_online: RegionForOnlineOffline, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_online_region(
                self, 
                resource_group_name: str, 
                account_name: str, 
                region_parameter_for_online: RegionForOnlineOffline, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_online_region(
                self, 
                resource_group_name: str, 
                account_name: str, 
                region_parameter_for_online: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_regenerate_key(
                self, 
                resource_group_name: str, 
                account_name: str, 
                key_to_regenerate: DatabaseAccountRegenerateKeyParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_regenerate_key(
                self, 
                resource_group_name: str, 
                account_name: str, 
                key_to_regenerate: DatabaseAccountRegenerateKeyParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_regenerate_key(
                self, 
                resource_group_name: str, 
                account_name: str, 
                key_to_regenerate: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                update_parameters: DatabaseAccountUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DatabaseAccountGetResults]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                update_parameters: DatabaseAccountUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DatabaseAccountGetResults]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DatabaseAccountGetResults]: ...

        @distributed_trace
        def check_name_exists(
                self, 
                account_name: str, 
                **kwargs: Any
            ) -> bool: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> DatabaseAccountGetResults: ...

        @distributed_trace
        def get_read_only_keys(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> DatabaseAccountListReadOnlyKeysResult: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[DatabaseAccountGetResults]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DatabaseAccountGetResults]: ...

        @distributed_trace
        def list_connection_strings(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> DatabaseAccountListConnectionStringsResult: ...

        @distributed_trace
        def list_keys(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> DatabaseAccountListKeysResult: ...

        @distributed_trace
        def list_metric_definitions(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[MetricDefinition]: ...

        @distributed_trace
        def list_metrics(
                self, 
                resource_group_name: str, 
                account_name: str, 
                *, 
                filter: str, 
                **kwargs: Any
            ) -> ItemPaged[Metric]: ...

        @distributed_trace
        def list_read_only_keys(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> DatabaseAccountListReadOnlyKeysResult: ...

        @distributed_trace
        def list_usages(
                self, 
                resource_group_name: str, 
                account_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Usage]: ...


    class azure.mgmt.cosmosdb.operations.DatabaseOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_metric_definitions(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_rid: str, 
                **kwargs: Any
            ) -> ItemPaged[MetricDefinition]: ...

        @distributed_trace
        def list_metrics(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_rid: str, 
                *, 
                filter: str, 
                **kwargs: Any
            ) -> ItemPaged[Metric]: ...

        @distributed_trace
        def list_usages(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_rid: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Usage]: ...


    class azure.mgmt.cosmosdb.operations.FleetAnalyticsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                fleet_analytics_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                fleet_analytics_name: str, 
                body: FleetAnalyticsResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FleetAnalyticsResource: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                fleet_analytics_name: str, 
                body: FleetAnalyticsResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FleetAnalyticsResource: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                fleet_analytics_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FleetAnalyticsResource: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                fleet_analytics_name: str, 
                **kwargs: Any
            ) -> FleetAnalyticsResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                **kwargs: Any
            ) -> ItemPaged[FleetAnalyticsResource]: ...


    class azure.mgmt.cosmosdb.operations.FleetOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                body: FleetResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FleetResource: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                body: FleetResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FleetResource: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FleetResource: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                **kwargs: Any
            ) -> FleetResource: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[FleetResource]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[FleetResource]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                body: FleetResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FleetResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                body: FleetResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FleetResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FleetResource: ...


    class azure.mgmt.cosmosdb.operations.FleetspaceAccountOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                fleetspace_name: str, 
                fleetspace_account_name: str, 
                body: FleetspaceAccountResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FleetspaceAccountResource]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                fleetspace_name: str, 
                fleetspace_account_name: str, 
                body: FleetspaceAccountResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FleetspaceAccountResource]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                fleetspace_name: str, 
                fleetspace_account_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FleetspaceAccountResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                fleetspace_name: str, 
                fleetspace_account_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                fleetspace_name: str, 
                fleetspace_account_name: str, 
                **kwargs: Any
            ) -> FleetspaceAccountResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                fleetspace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[FleetspaceAccountResource]: ...


    class azure.mgmt.cosmosdb.operations.FleetspaceOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                fleetspace_name: str, 
                body: FleetspaceResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FleetspaceResource]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                fleetspace_name: str, 
                body: FleetspaceResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FleetspaceResource]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                fleetspace_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FleetspaceResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                fleetspace_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                fleetspace_name: str, 
                body: Optional[FleetspaceUpdate] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FleetspaceResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                fleetspace_name: str, 
                body: Optional[FleetspaceUpdate] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FleetspaceResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                fleetspace_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FleetspaceResource]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                fleetspace_name: str, 
                **kwargs: Any
            ) -> FleetspaceResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                **kwargs: Any
            ) -> ItemPaged[FleetspaceResource]: ...


    class azure.mgmt.cosmosdb.operations.GarnetClustersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: GarnetClusterResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GarnetClusterResource]: ...

        @overload
        def begin_create_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: GarnetClusterResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GarnetClusterResource]: ...

        @overload
        def begin_create_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GarnetClusterResource]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'cluster_name']}, api_versions_list=['2026-04-01-preview'])
        def begin_delete(
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
                body: GarnetClusterResourcePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GarnetClusterResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: GarnetClusterResourcePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GarnetClusterResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GarnetClusterResource]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'cluster_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> GarnetClusterResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[GarnetClusterResource]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2026-04-01-preview'])
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[GarnetClusterResource]: ...


    class azure.mgmt.cosmosdb.operations.GraphResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_update_graph(
                self, 
                resource_group_name: str, 
                account_name: str, 
                graph_name: str, 
                create_update_graph_parameters: GraphResourceCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GraphResourceGetResults]: ...

        @overload
        def begin_create_update_graph(
                self, 
                resource_group_name: str, 
                account_name: str, 
                graph_name: str, 
                create_update_graph_parameters: GraphResourceCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GraphResourceGetResults]: ...

        @overload
        def begin_create_update_graph(
                self, 
                resource_group_name: str, 
                account_name: str, 
                graph_name: str, 
                create_update_graph_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GraphResourceGetResults]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'graph_name']}, api_versions_list=['2026-04-01-preview'])
        def begin_delete_graph_resource(
                self, 
                resource_group_name: str, 
                account_name: str, 
                graph_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'graph_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        def get_graph(
                self, 
                resource_group_name: str, 
                account_name: str, 
                graph_name: str, 
                **kwargs: Any
            ) -> GraphResourceGetResults: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        def list_graphs(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[GraphResourceGetResults]: ...


    class azure.mgmt.cosmosdb.operations.GremlinResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_update_gremlin_database(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                create_update_gremlin_database_parameters: GremlinDatabaseCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GremlinDatabaseGetResults]: ...

        @overload
        def begin_create_update_gremlin_database(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                create_update_gremlin_database_parameters: GremlinDatabaseCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GremlinDatabaseGetResults]: ...

        @overload
        def begin_create_update_gremlin_database(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                create_update_gremlin_database_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GremlinDatabaseGetResults]: ...

        @overload
        def begin_create_update_gremlin_graph(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                graph_name: str, 
                create_update_gremlin_graph_parameters: GremlinGraphCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GremlinGraphGetResults]: ...

        @overload
        def begin_create_update_gremlin_graph(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                graph_name: str, 
                create_update_gremlin_graph_parameters: GremlinGraphCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GremlinGraphGetResults]: ...

        @overload
        def begin_create_update_gremlin_graph(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                graph_name: str, 
                create_update_gremlin_graph_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GremlinGraphGetResults]: ...

        @overload
        def begin_create_update_gremlin_role_assignment(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_assignment_id: str, 
                create_update_gremlin_role_assignment_parameters: GremlinRoleAssignmentResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GremlinRoleAssignmentResource]: ...

        @overload
        def begin_create_update_gremlin_role_assignment(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_assignment_id: str, 
                create_update_gremlin_role_assignment_parameters: GremlinRoleAssignmentResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GremlinRoleAssignmentResource]: ...

        @overload
        def begin_create_update_gremlin_role_assignment(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_assignment_id: str, 
                create_update_gremlin_role_assignment_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GremlinRoleAssignmentResource]: ...

        @overload
        def begin_create_update_gremlin_role_definition(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_definition_id: str, 
                create_update_gremlin_role_definition_parameters: GremlinRoleDefinitionResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GremlinRoleDefinitionResource]: ...

        @overload
        def begin_create_update_gremlin_role_definition(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_definition_id: str, 
                create_update_gremlin_role_definition_parameters: GremlinRoleDefinitionResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GremlinRoleDefinitionResource]: ...

        @overload
        def begin_create_update_gremlin_role_definition(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_definition_id: str, 
                create_update_gremlin_role_definition_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GremlinRoleDefinitionResource]: ...

        @distributed_trace
        def begin_delete_gremlin_database(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_delete_gremlin_graph(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                graph_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_delete_gremlin_role_assignment(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_assignment_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_delete_gremlin_role_definition(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_definition_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_migrate_gremlin_database_to_autoscale(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> LROPoller[ThroughputSettingsGetResults]: ...

        @distributed_trace
        def begin_migrate_gremlin_database_to_manual_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> LROPoller[ThroughputSettingsGetResults]: ...

        @distributed_trace
        def begin_migrate_gremlin_graph_to_autoscale(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                graph_name: str, 
                **kwargs: Any
            ) -> LROPoller[ThroughputSettingsGetResults]: ...

        @distributed_trace
        def begin_migrate_gremlin_graph_to_manual_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                graph_name: str, 
                **kwargs: Any
            ) -> LROPoller[ThroughputSettingsGetResults]: ...

        @overload
        def begin_retrieve_continuous_backup_information(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                graph_name: str, 
                location: ContinuousBackupRestoreLocation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BackupInformation]: ...

        @overload
        def begin_retrieve_continuous_backup_information(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                graph_name: str, 
                location: ContinuousBackupRestoreLocation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BackupInformation]: ...

        @overload
        def begin_retrieve_continuous_backup_information(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                graph_name: str, 
                location: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BackupInformation]: ...

        @overload
        def begin_update_gremlin_database_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                update_throughput_parameters: ThroughputSettingsUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ThroughputSettingsGetResults]: ...

        @overload
        def begin_update_gremlin_database_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                update_throughput_parameters: ThroughputSettingsUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ThroughputSettingsGetResults]: ...

        @overload
        def begin_update_gremlin_database_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                update_throughput_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ThroughputSettingsGetResults]: ...

        @overload
        def begin_update_gremlin_graph_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                graph_name: str, 
                update_throughput_parameters: ThroughputSettingsUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ThroughputSettingsGetResults]: ...

        @overload
        def begin_update_gremlin_graph_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                graph_name: str, 
                update_throughput_parameters: ThroughputSettingsUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ThroughputSettingsGetResults]: ...

        @overload
        def begin_update_gremlin_graph_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                graph_name: str, 
                update_throughput_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ThroughputSettingsGetResults]: ...

        @distributed_trace
        def get_gremlin_database(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> GremlinDatabaseGetResults: ...

        @distributed_trace
        def get_gremlin_database_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> ThroughputSettingsGetResults: ...

        @distributed_trace
        def get_gremlin_graph(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                graph_name: str, 
                **kwargs: Any
            ) -> GremlinGraphGetResults: ...

        @distributed_trace
        def get_gremlin_graph_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                graph_name: str, 
                **kwargs: Any
            ) -> ThroughputSettingsGetResults: ...

        @distributed_trace
        def get_gremlin_role_assignment(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_assignment_id: str, 
                **kwargs: Any
            ) -> GremlinRoleAssignmentResource: ...

        @distributed_trace
        def get_gremlin_role_definition(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_definition_id: str, 
                **kwargs: Any
            ) -> GremlinRoleDefinitionResource: ...

        @distributed_trace
        def list_gremlin_databases(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[GremlinDatabaseGetResults]: ...

        @distributed_trace
        def list_gremlin_graphs(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> ItemPaged[GremlinGraphGetResults]: ...

        @distributed_trace
        def list_gremlin_role_assignments(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[GremlinRoleAssignmentResource]: ...

        @distributed_trace
        def list_gremlin_role_definitions(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[GremlinRoleDefinitionResource]: ...


    class azure.mgmt.cosmosdb.operations.LocationsOperations:

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
            ) -> LocationGetResult: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[LocationGetResult]: ...


    class azure.mgmt.cosmosdb.operations.MongoDBResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_update_mongo_db_collection(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                collection_name: str, 
                create_update_mongo_db_collection_parameters: MongoDBCollectionCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MongoDBCollectionGetResults]: ...

        @overload
        def begin_create_update_mongo_db_collection(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                collection_name: str, 
                create_update_mongo_db_collection_parameters: MongoDBCollectionCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MongoDBCollectionGetResults]: ...

        @overload
        def begin_create_update_mongo_db_collection(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                collection_name: str, 
                create_update_mongo_db_collection_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MongoDBCollectionGetResults]: ...

        @overload
        def begin_create_update_mongo_db_database(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                create_update_mongo_db_database_parameters: MongoDBDatabaseCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MongoDBDatabaseGetResults]: ...

        @overload
        def begin_create_update_mongo_db_database(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                create_update_mongo_db_database_parameters: MongoDBDatabaseCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MongoDBDatabaseGetResults]: ...

        @overload
        def begin_create_update_mongo_db_database(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                create_update_mongo_db_database_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MongoDBDatabaseGetResults]: ...

        @overload
        def begin_create_update_mongo_role_definition(
                self, 
                mongo_role_definition_id: str, 
                resource_group_name: str, 
                account_name: str, 
                create_update_mongo_role_definition_parameters: MongoRoleDefinitionCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MongoRoleDefinitionGetResults]: ...

        @overload
        def begin_create_update_mongo_role_definition(
                self, 
                mongo_role_definition_id: str, 
                resource_group_name: str, 
                account_name: str, 
                create_update_mongo_role_definition_parameters: MongoRoleDefinitionCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MongoRoleDefinitionGetResults]: ...

        @overload
        def begin_create_update_mongo_role_definition(
                self, 
                mongo_role_definition_id: str, 
                resource_group_name: str, 
                account_name: str, 
                create_update_mongo_role_definition_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MongoRoleDefinitionGetResults]: ...

        @overload
        def begin_create_update_mongo_user_definition(
                self, 
                mongo_user_definition_id: str, 
                resource_group_name: str, 
                account_name: str, 
                create_update_mongo_user_definition_parameters: MongoUserDefinitionCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MongoUserDefinitionGetResults]: ...

        @overload
        def begin_create_update_mongo_user_definition(
                self, 
                mongo_user_definition_id: str, 
                resource_group_name: str, 
                account_name: str, 
                create_update_mongo_user_definition_parameters: MongoUserDefinitionCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MongoUserDefinitionGetResults]: ...

        @overload
        def begin_create_update_mongo_user_definition(
                self, 
                mongo_user_definition_id: str, 
                resource_group_name: str, 
                account_name: str, 
                create_update_mongo_user_definition_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MongoUserDefinitionGetResults]: ...

        @distributed_trace
        def begin_delete_mongo_db_collection(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                collection_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_delete_mongo_db_database(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_delete_mongo_role_definition(
                self, 
                mongo_role_definition_id: str, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_delete_mongo_user_definition(
                self, 
                mongo_user_definition_id: str, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_list_mongo_db_collection_partition_merge(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                collection_name: str, 
                merge_parameters: MergeParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PhysicalPartitionStorageInfoCollection]: ...

        @overload
        def begin_list_mongo_db_collection_partition_merge(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                collection_name: str, 
                merge_parameters: MergeParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PhysicalPartitionStorageInfoCollection]: ...

        @overload
        def begin_list_mongo_db_collection_partition_merge(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                collection_name: str, 
                merge_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PhysicalPartitionStorageInfoCollection]: ...

        @distributed_trace
        def begin_migrate_mongo_db_collection_to_autoscale(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                collection_name: str, 
                **kwargs: Any
            ) -> LROPoller[ThroughputSettingsGetResults]: ...

        @distributed_trace
        def begin_migrate_mongo_db_collection_to_manual_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                collection_name: str, 
                **kwargs: Any
            ) -> LROPoller[ThroughputSettingsGetResults]: ...

        @distributed_trace
        def begin_migrate_mongo_db_database_to_autoscale(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> LROPoller[ThroughputSettingsGetResults]: ...

        @distributed_trace
        def begin_migrate_mongo_db_database_to_manual_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> LROPoller[ThroughputSettingsGetResults]: ...

        @overload
        def begin_mongo_db_container_redistribute_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                collection_name: str, 
                redistribute_throughput_parameters: RedistributeThroughputParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PhysicalPartitionThroughputInfoResult]: ...

        @overload
        def begin_mongo_db_container_redistribute_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                collection_name: str, 
                redistribute_throughput_parameters: RedistributeThroughputParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PhysicalPartitionThroughputInfoResult]: ...

        @overload
        def begin_mongo_db_container_redistribute_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                collection_name: str, 
                redistribute_throughput_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PhysicalPartitionThroughputInfoResult]: ...

        @overload
        def begin_mongo_db_container_retrieve_throughput_distribution(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                collection_name: str, 
                retrieve_throughput_parameters: RetrieveThroughputParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PhysicalPartitionThroughputInfoResult]: ...

        @overload
        def begin_mongo_db_container_retrieve_throughput_distribution(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                collection_name: str, 
                retrieve_throughput_parameters: RetrieveThroughputParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PhysicalPartitionThroughputInfoResult]: ...

        @overload
        def begin_mongo_db_container_retrieve_throughput_distribution(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                collection_name: str, 
                retrieve_throughput_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PhysicalPartitionThroughputInfoResult]: ...

        @overload
        def begin_mongo_db_database_partition_merge(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                merge_parameters: MergeParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PhysicalPartitionStorageInfoCollection]: ...

        @overload
        def begin_mongo_db_database_partition_merge(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                merge_parameters: MergeParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PhysicalPartitionStorageInfoCollection]: ...

        @overload
        def begin_mongo_db_database_partition_merge(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                merge_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PhysicalPartitionStorageInfoCollection]: ...

        @overload
        def begin_mongo_db_database_redistribute_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                redistribute_throughput_parameters: RedistributeThroughputParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PhysicalPartitionThroughputInfoResult]: ...

        @overload
        def begin_mongo_db_database_redistribute_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                redistribute_throughput_parameters: RedistributeThroughputParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PhysicalPartitionThroughputInfoResult]: ...

        @overload
        def begin_mongo_db_database_redistribute_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                redistribute_throughput_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PhysicalPartitionThroughputInfoResult]: ...

        @overload
        def begin_mongo_db_database_retrieve_throughput_distribution(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                retrieve_throughput_parameters: RetrieveThroughputParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PhysicalPartitionThroughputInfoResult]: ...

        @overload
        def begin_mongo_db_database_retrieve_throughput_distribution(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                retrieve_throughput_parameters: RetrieveThroughputParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PhysicalPartitionThroughputInfoResult]: ...

        @overload
        def begin_mongo_db_database_retrieve_throughput_distribution(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                retrieve_throughput_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PhysicalPartitionThroughputInfoResult]: ...

        @overload
        def begin_retrieve_continuous_backup_information(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                collection_name: str, 
                location: ContinuousBackupRestoreLocation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BackupInformation]: ...

        @overload
        def begin_retrieve_continuous_backup_information(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                collection_name: str, 
                location: ContinuousBackupRestoreLocation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BackupInformation]: ...

        @overload
        def begin_retrieve_continuous_backup_information(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                collection_name: str, 
                location: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BackupInformation]: ...

        @overload
        def begin_update_mongo_db_collection_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                collection_name: str, 
                update_throughput_parameters: ThroughputSettingsUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ThroughputSettingsGetResults]: ...

        @overload
        def begin_update_mongo_db_collection_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                collection_name: str, 
                update_throughput_parameters: ThroughputSettingsUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ThroughputSettingsGetResults]: ...

        @overload
        def begin_update_mongo_db_collection_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                collection_name: str, 
                update_throughput_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ThroughputSettingsGetResults]: ...

        @overload
        def begin_update_mongo_db_database_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                update_throughput_parameters: ThroughputSettingsUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ThroughputSettingsGetResults]: ...

        @overload
        def begin_update_mongo_db_database_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                update_throughput_parameters: ThroughputSettingsUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ThroughputSettingsGetResults]: ...

        @overload
        def begin_update_mongo_db_database_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                update_throughput_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ThroughputSettingsGetResults]: ...

        @distributed_trace
        def get_mongo_db_collection(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                collection_name: str, 
                **kwargs: Any
            ) -> MongoDBCollectionGetResults: ...

        @distributed_trace
        def get_mongo_db_collection_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                collection_name: str, 
                **kwargs: Any
            ) -> ThroughputSettingsGetResults: ...

        @distributed_trace
        def get_mongo_db_database(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> MongoDBDatabaseGetResults: ...

        @distributed_trace
        def get_mongo_db_database_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> ThroughputSettingsGetResults: ...

        @distributed_trace
        def get_mongo_role_definition(
                self, 
                mongo_role_definition_id: str, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> MongoRoleDefinitionGetResults: ...

        @distributed_trace
        def get_mongo_user_definition(
                self, 
                mongo_user_definition_id: str, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> MongoUserDefinitionGetResults: ...

        @distributed_trace
        def list_mongo_db_collections(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> ItemPaged[MongoDBCollectionGetResults]: ...

        @distributed_trace
        def list_mongo_db_databases(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[MongoDBDatabaseGetResults]: ...

        @distributed_trace
        def list_mongo_role_definitions(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[MongoRoleDefinitionGetResults]: ...

        @distributed_trace
        def list_mongo_user_definitions(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[MongoUserDefinitionGetResults]: ...


    class azure.mgmt.cosmosdb.operations.MongoMIResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_update_mongo_mi_role_assignment(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_assignment_id: str, 
                create_update_mongo_mi_role_assignment_parameters: MongoMIRoleAssignmentResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MongoMIRoleAssignmentResource]: ...

        @overload
        def begin_create_update_mongo_mi_role_assignment(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_assignment_id: str, 
                create_update_mongo_mi_role_assignment_parameters: MongoMIRoleAssignmentResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MongoMIRoleAssignmentResource]: ...

        @overload
        def begin_create_update_mongo_mi_role_assignment(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_assignment_id: str, 
                create_update_mongo_mi_role_assignment_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MongoMIRoleAssignmentResource]: ...

        @overload
        def begin_create_update_mongo_mi_role_definition(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_definition_id: str, 
                create_update_mongo_mi_role_definition_parameters: MongoMIRoleDefinitionResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MongoMIRoleDefinitionResource]: ...

        @overload
        def begin_create_update_mongo_mi_role_definition(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_definition_id: str, 
                create_update_mongo_mi_role_definition_parameters: MongoMIRoleDefinitionResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MongoMIRoleDefinitionResource]: ...

        @overload
        def begin_create_update_mongo_mi_role_definition(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_definition_id: str, 
                create_update_mongo_mi_role_definition_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MongoMIRoleDefinitionResource]: ...

        @distributed_trace
        def begin_delete_mongo_mi_role_assignment(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_assignment_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_delete_mongo_mi_role_definition(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_definition_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get_mongo_mi_role_assignment(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_assignment_id: str, 
                **kwargs: Any
            ) -> MongoMIRoleAssignmentResource: ...

        @distributed_trace
        def get_mongo_mi_role_definition(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_definition_id: str, 
                **kwargs: Any
            ) -> MongoMIRoleDefinitionResource: ...

        @distributed_trace
        def list_mongo_mi_role_assignments(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[MongoMIRoleAssignmentResource]: ...

        @distributed_trace
        def list_mongo_mi_role_definitions(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[MongoMIRoleDefinitionResource]: ...


    class azure.mgmt.cosmosdb.operations.NetworkSecurityPerimeterConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'network_security_perimeter_configuration_name']}, api_versions_list=['2026-04-01-preview'])
        def begin_reconcile(
                self, 
                resource_group_name: str, 
                account_name: str, 
                network_security_perimeter_configuration_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'network_security_perimeter_configuration_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                network_security_perimeter_configuration_name: str, 
                **kwargs: Any
            ) -> NetworkSecurityPerimeterConfiguration: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[NetworkSecurityPerimeterConfiguration]: ...


    class azure.mgmt.cosmosdb.operations.NotebookWorkspacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                notebook_workspace_name: Union[str, NotebookWorkspaceName], 
                notebook_create_update_parameters: NotebookWorkspaceCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NotebookWorkspace]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                notebook_workspace_name: Union[str, NotebookWorkspaceName], 
                notebook_create_update_parameters: NotebookWorkspaceCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NotebookWorkspace]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                notebook_workspace_name: Union[str, NotebookWorkspaceName], 
                notebook_create_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NotebookWorkspace]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                notebook_workspace_name: Union[str, NotebookWorkspaceName], 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_regenerate_auth_token(
                self, 
                resource_group_name: str, 
                account_name: str, 
                notebook_workspace_name: Union[str, NotebookWorkspaceName], 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_start(
                self, 
                resource_group_name: str, 
                account_name: str, 
                notebook_workspace_name: Union[str, NotebookWorkspaceName], 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                notebook_workspace_name: Union[str, NotebookWorkspaceName], 
                **kwargs: Any
            ) -> NotebookWorkspace: ...

        @distributed_trace
        def list_by_database_account(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[NotebookWorkspace]: ...

        @distributed_trace
        def list_connection_info(
                self, 
                resource_group_name: str, 
                account_name: str, 
                notebook_workspace_name: Union[str, NotebookWorkspaceName], 
                **kwargs: Any
            ) -> NotebookWorkspaceConnectionInfoResult: ...


    class azure.mgmt.cosmosdb.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.cosmosdb.operations.PartitionKeyRangeIdOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_metrics(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_rid: str, 
                collection_rid: str, 
                partition_key_range_id: str, 
                *, 
                filter: str, 
                **kwargs: Any
            ) -> ItemPaged[PartitionMetric]: ...


    class azure.mgmt.cosmosdb.operations.PartitionKeyRangeIdRegionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_metrics(
                self, 
                resource_group_name: str, 
                account_name: str, 
                region: str, 
                database_rid: str, 
                collection_rid: str, 
                partition_key_range_id: str, 
                *, 
                filter: str, 
                **kwargs: Any
            ) -> ItemPaged[PartitionMetric]: ...


    class azure.mgmt.cosmosdb.operations.PercentileOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_metrics(
                self, 
                resource_group_name: str, 
                account_name: str, 
                *, 
                filter: str, 
                **kwargs: Any
            ) -> ItemPaged[PercentileMetric]: ...


    class azure.mgmt.cosmosdb.operations.PercentileSourceTargetOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_metrics(
                self, 
                resource_group_name: str, 
                account_name: str, 
                source_region: str, 
                target_region: str, 
                *, 
                filter: str, 
                **kwargs: Any
            ) -> ItemPaged[PercentileMetric]: ...


    class azure.mgmt.cosmosdb.operations.PercentileTargetOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_metrics(
                self, 
                resource_group_name: str, 
                account_name: str, 
                target_region: str, 
                *, 
                filter: str, 
                **kwargs: Any
            ) -> ItemPaged[PercentileMetric]: ...


    class azure.mgmt.cosmosdb.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
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
                account_name: str, 
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
                account_name: str, 
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
                account_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list_by_database_account(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PrivateEndpointConnection]: ...


    class azure.mgmt.cosmosdb.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                group_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @distributed_trace
        def list_by_database_account(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PrivateLinkResource]: ...


    class azure.mgmt.cosmosdb.operations.RestorableDatabaseAccountsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get_by_location(
                self, 
                location: str, 
                instance_id: str, 
                **kwargs: Any
            ) -> RestorableDatabaseAccountGetResult: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[RestorableDatabaseAccountGetResult]: ...

        @distributed_trace
        def list_by_location(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[RestorableDatabaseAccountGetResult]: ...


    class azure.mgmt.cosmosdb.operations.RestorableGremlinDatabasesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                instance_id: str, 
                **kwargs: Any
            ) -> ItemPaged[RestorableGremlinDatabaseGetResult]: ...


    class azure.mgmt.cosmosdb.operations.RestorableGremlinGraphsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                instance_id: str, 
                *, 
                end_time: Optional[str] = ..., 
                restorable_gremlin_database_rid: Optional[str] = ..., 
                start_time: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[RestorableGremlinGraphGetResult]: ...


    class azure.mgmt.cosmosdb.operations.RestorableGremlinResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                instance_id: str, 
                *, 
                restore_location: Optional[str] = ..., 
                restore_timestamp_in_utc: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[RestorableGremlinResourcesGetResult]: ...


    class azure.mgmt.cosmosdb.operations.RestorableMongodbCollectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                instance_id: str, 
                *, 
                end_time: Optional[str] = ..., 
                restorable_mongodb_database_rid: Optional[str] = ..., 
                start_time: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[RestorableMongodbCollectionGetResult]: ...


    class azure.mgmt.cosmosdb.operations.RestorableMongodbDatabasesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                instance_id: str, 
                **kwargs: Any
            ) -> ItemPaged[RestorableMongodbDatabaseGetResult]: ...


    class azure.mgmt.cosmosdb.operations.RestorableMongodbResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                instance_id: str, 
                *, 
                restore_location: Optional[str] = ..., 
                restore_timestamp_in_utc: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[RestorableMongodbResourcesGetResult]: ...


    class azure.mgmt.cosmosdb.operations.RestorableSqlContainersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                instance_id: str, 
                *, 
                end_time: Optional[str] = ..., 
                restorable_sql_database_rid: Optional[str] = ..., 
                start_time: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[RestorableSqlContainerGetResult]: ...


    class azure.mgmt.cosmosdb.operations.RestorableSqlDatabasesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                instance_id: str, 
                **kwargs: Any
            ) -> ItemPaged[RestorableSqlDatabaseGetResult]: ...


    class azure.mgmt.cosmosdb.operations.RestorableSqlResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                instance_id: str, 
                *, 
                restore_location: Optional[str] = ..., 
                restore_timestamp_in_utc: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[RestorableSqlResourcesGetResult]: ...


    class azure.mgmt.cosmosdb.operations.RestorableTableResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                instance_id: str, 
                *, 
                restore_location: Optional[str] = ..., 
                restore_timestamp_in_utc: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[RestorableTableResourcesGetResult]: ...


    class azure.mgmt.cosmosdb.operations.RestorableTablesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                instance_id: str, 
                *, 
                end_time: Optional[str] = ..., 
                start_time: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[RestorableTableGetResult]: ...


    class azure.mgmt.cosmosdb.operations.ServiceOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                service_name: str, 
                create_update_parameters: ServiceResourceCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ServiceResource]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                service_name: str, 
                create_update_parameters: ServiceResourceCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ServiceResource]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                service_name: str, 
                create_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ServiceResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                service_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                service_name: str, 
                **kwargs: Any
            ) -> ServiceResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ServiceResource]: ...


    class azure.mgmt.cosmosdb.operations.SoftDeletedDatabaseAccountsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['subscription_id', 'resource_group_name', 'location', 'account_name', 'api_version', 'soft_delete_action_kind']}, api_versions_list=['2026-04-01-preview'])
        def begin_purge(
                self, 
                resource_group_name: str, 
                location: str, 
                account_name: str, 
                *, 
                soft_delete_action_kind: Optional[Union[str, SoftDeleteActionKind]] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['subscription_id', 'resource_group_name', 'location', 'account_name', 'api_version', 'soft_delete_action_kind']}, api_versions_list=['2026-04-01-preview'])
        def begin_restore(
                self, 
                resource_group_name: str, 
                location: str, 
                account_name: str, 
                *, 
                soft_delete_action_kind: Optional[Union[str, SoftDeleteActionKind]] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'location', 'account_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                location: str, 
                account_name: str, 
                **kwargs: Any
            ) -> SoftDeletedDatabaseAccountGetResult: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'location', 'accept']}, api_versions_list=['2026-04-01-preview'])
        def list_by_location(
                self, 
                location: str, 
                **kwargs: Any
            ) -> SoftDeletedDatabaseAccountsListResult: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['subscription_id', 'resource_group_name', 'location', 'api_version', 'accept']}, api_versions_list=['2026-04-01-preview'])
        def list_by_resource_group_and_location(
                self, 
                resource_group_name: str, 
                location: str, 
                **kwargs: Any
            ) -> SoftDeletedDatabaseAccountsListResult: ...


    class azure.mgmt.cosmosdb.operations.SoftDeletedSqlContainersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['subscription_id', 'resource_group_name', 'location', 'account_name', 'database_name', 'container_name', 'api_version', 'soft_delete_action_kind']}, api_versions_list=['2026-04-01-preview'])
        def begin_purge(
                self, 
                resource_group_name: str, 
                location: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                *, 
                soft_delete_action_kind: Optional[Union[str, SoftDeleteActionKind]] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['subscription_id', 'resource_group_name', 'location', 'account_name', 'database_name', 'container_name', 'api_version', 'soft_delete_action_kind']}, api_versions_list=['2026-04-01-preview'])
        def begin_restore(
                self, 
                resource_group_name: str, 
                location: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                *, 
                soft_delete_action_kind: Optional[Union[str, SoftDeleteActionKind]] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'location', 'account_name', 'database_name', 'container_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                location: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                **kwargs: Any
            ) -> SoftDeletedSqlContainerGetResult: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'location', 'account_name', 'database_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                location: str, 
                account_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> SoftDeletedSqlContainersListResult: ...


    class azure.mgmt.cosmosdb.operations.SoftDeletedSqlDatabasesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['subscription_id', 'resource_group_name', 'location', 'account_name', 'database_name', 'api_version', 'soft_delete_action_kind']}, api_versions_list=['2026-04-01-preview'])
        def begin_purge(
                self, 
                resource_group_name: str, 
                location: str, 
                account_name: str, 
                database_name: str, 
                *, 
                soft_delete_action_kind: Optional[Union[str, SoftDeleteActionKind]] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['subscription_id', 'resource_group_name', 'location', 'account_name', 'database_name', 'api_version', 'soft_delete_action_kind']}, api_versions_list=['2026-04-01-preview'])
        def begin_restore(
                self, 
                resource_group_name: str, 
                location: str, 
                account_name: str, 
                database_name: str, 
                *, 
                soft_delete_action_kind: Optional[Union[str, SoftDeleteActionKind]] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'location', 'account_name', 'database_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                location: str, 
                account_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> SoftDeletedSqlDatabaseGetResult: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'location', 'account_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                location: str, 
                account_name: str, 
                **kwargs: Any
            ) -> SoftDeletedSqlDatabasesListResult: ...


    class azure.mgmt.cosmosdb.operations.SqlResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_update_client_encryption_key(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                client_encryption_key_name: str, 
                create_update_client_encryption_key_parameters: ClientEncryptionKeyCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ClientEncryptionKeyGetResults]: ...

        @overload
        def begin_create_update_client_encryption_key(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                client_encryption_key_name: str, 
                create_update_client_encryption_key_parameters: ClientEncryptionKeyCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ClientEncryptionKeyGetResults]: ...

        @overload
        def begin_create_update_client_encryption_key(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                client_encryption_key_name: str, 
                create_update_client_encryption_key_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ClientEncryptionKeyGetResults]: ...

        @overload
        def begin_create_update_sql_container(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                create_update_sql_container_parameters: SqlContainerCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlContainerGetResults]: ...

        @overload
        def begin_create_update_sql_container(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                create_update_sql_container_parameters: SqlContainerCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlContainerGetResults]: ...

        @overload
        def begin_create_update_sql_container(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                create_update_sql_container_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlContainerGetResults]: ...

        @overload
        def begin_create_update_sql_database(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                create_update_sql_database_parameters: SqlDatabaseCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlDatabaseGetResults]: ...

        @overload
        def begin_create_update_sql_database(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                create_update_sql_database_parameters: SqlDatabaseCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlDatabaseGetResults]: ...

        @overload
        def begin_create_update_sql_database(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                create_update_sql_database_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlDatabaseGetResults]: ...

        @overload
        def begin_create_update_sql_role_assignment(
                self, 
                role_assignment_id: str, 
                resource_group_name: str, 
                account_name: str, 
                create_update_sql_role_assignment_parameters: SqlRoleAssignmentCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlRoleAssignmentGetResults]: ...

        @overload
        def begin_create_update_sql_role_assignment(
                self, 
                role_assignment_id: str, 
                resource_group_name: str, 
                account_name: str, 
                create_update_sql_role_assignment_parameters: SqlRoleAssignmentCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlRoleAssignmentGetResults]: ...

        @overload
        def begin_create_update_sql_role_assignment(
                self, 
                role_assignment_id: str, 
                resource_group_name: str, 
                account_name: str, 
                create_update_sql_role_assignment_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlRoleAssignmentGetResults]: ...

        @overload
        def begin_create_update_sql_role_definition(
                self, 
                role_definition_id: str, 
                resource_group_name: str, 
                account_name: str, 
                create_update_sql_role_definition_parameters: SqlRoleDefinitionCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlRoleDefinitionGetResults]: ...

        @overload
        def begin_create_update_sql_role_definition(
                self, 
                role_definition_id: str, 
                resource_group_name: str, 
                account_name: str, 
                create_update_sql_role_definition_parameters: SqlRoleDefinitionCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlRoleDefinitionGetResults]: ...

        @overload
        def begin_create_update_sql_role_definition(
                self, 
                role_definition_id: str, 
                resource_group_name: str, 
                account_name: str, 
                create_update_sql_role_definition_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlRoleDefinitionGetResults]: ...

        @overload
        def begin_create_update_sql_stored_procedure(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                stored_procedure_name: str, 
                create_update_sql_stored_procedure_parameters: SqlStoredProcedureCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlStoredProcedureGetResults]: ...

        @overload
        def begin_create_update_sql_stored_procedure(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                stored_procedure_name: str, 
                create_update_sql_stored_procedure_parameters: SqlStoredProcedureCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlStoredProcedureGetResults]: ...

        @overload
        def begin_create_update_sql_stored_procedure(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                stored_procedure_name: str, 
                create_update_sql_stored_procedure_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlStoredProcedureGetResults]: ...

        @overload
        def begin_create_update_sql_trigger(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                trigger_name: str, 
                create_update_sql_trigger_parameters: SqlTriggerCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlTriggerGetResults]: ...

        @overload
        def begin_create_update_sql_trigger(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                trigger_name: str, 
                create_update_sql_trigger_parameters: SqlTriggerCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlTriggerGetResults]: ...

        @overload
        def begin_create_update_sql_trigger(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                trigger_name: str, 
                create_update_sql_trigger_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlTriggerGetResults]: ...

        @overload
        def begin_create_update_sql_user_defined_function(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                user_defined_function_name: str, 
                create_update_sql_user_defined_function_parameters: SqlUserDefinedFunctionCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlUserDefinedFunctionGetResults]: ...

        @overload
        def begin_create_update_sql_user_defined_function(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                user_defined_function_name: str, 
                create_update_sql_user_defined_function_parameters: SqlUserDefinedFunctionCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlUserDefinedFunctionGetResults]: ...

        @overload
        def begin_create_update_sql_user_defined_function(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                user_defined_function_name: str, 
                create_update_sql_user_defined_function_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlUserDefinedFunctionGetResults]: ...

        @distributed_trace
        def begin_delete_sql_container(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_delete_sql_database(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_delete_sql_role_assignment(
                self, 
                role_assignment_id: str, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_delete_sql_role_definition(
                self, 
                role_definition_id: str, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_delete_sql_stored_procedure(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                stored_procedure_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_delete_sql_trigger(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                trigger_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_delete_sql_user_defined_function(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                user_defined_function_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_list_sql_container_partition_merge(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                merge_parameters: MergeParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PhysicalPartitionStorageInfoCollection]: ...

        @overload
        def begin_list_sql_container_partition_merge(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                merge_parameters: MergeParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PhysicalPartitionStorageInfoCollection]: ...

        @overload
        def begin_list_sql_container_partition_merge(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                merge_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PhysicalPartitionStorageInfoCollection]: ...

        @distributed_trace
        def begin_migrate_sql_container_to_autoscale(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                **kwargs: Any
            ) -> LROPoller[ThroughputSettingsGetResults]: ...

        @distributed_trace
        def begin_migrate_sql_container_to_manual_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                **kwargs: Any
            ) -> LROPoller[ThroughputSettingsGetResults]: ...

        @distributed_trace
        def begin_migrate_sql_database_to_autoscale(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> LROPoller[ThroughputSettingsGetResults]: ...

        @distributed_trace
        def begin_migrate_sql_database_to_manual_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> LROPoller[ThroughputSettingsGetResults]: ...

        @overload
        def begin_retrieve_continuous_backup_information(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                location: ContinuousBackupRestoreLocation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BackupInformation]: ...

        @overload
        def begin_retrieve_continuous_backup_information(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                location: ContinuousBackupRestoreLocation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BackupInformation]: ...

        @overload
        def begin_retrieve_continuous_backup_information(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                location: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BackupInformation]: ...

        @overload
        def begin_sql_container_redistribute_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                redistribute_throughput_parameters: RedistributeThroughputParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PhysicalPartitionThroughputInfoResult]: ...

        @overload
        def begin_sql_container_redistribute_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                redistribute_throughput_parameters: RedistributeThroughputParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PhysicalPartitionThroughputInfoResult]: ...

        @overload
        def begin_sql_container_redistribute_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                redistribute_throughput_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PhysicalPartitionThroughputInfoResult]: ...

        @overload
        def begin_sql_container_retrieve_throughput_distribution(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                retrieve_throughput_parameters: RetrieveThroughputParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PhysicalPartitionThroughputInfoResult]: ...

        @overload
        def begin_sql_container_retrieve_throughput_distribution(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                retrieve_throughput_parameters: RetrieveThroughputParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PhysicalPartitionThroughputInfoResult]: ...

        @overload
        def begin_sql_container_retrieve_throughput_distribution(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                retrieve_throughput_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PhysicalPartitionThroughputInfoResult]: ...

        @overload
        def begin_sql_database_partition_merge(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                merge_parameters: MergeParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PhysicalPartitionStorageInfoCollection]: ...

        @overload
        def begin_sql_database_partition_merge(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                merge_parameters: MergeParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PhysicalPartitionStorageInfoCollection]: ...

        @overload
        def begin_sql_database_partition_merge(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                merge_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PhysicalPartitionStorageInfoCollection]: ...

        @overload
        def begin_sql_database_redistribute_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                redistribute_throughput_parameters: RedistributeThroughputParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PhysicalPartitionThroughputInfoResult]: ...

        @overload
        def begin_sql_database_redistribute_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                redistribute_throughput_parameters: RedistributeThroughputParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PhysicalPartitionThroughputInfoResult]: ...

        @overload
        def begin_sql_database_redistribute_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                redistribute_throughput_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PhysicalPartitionThroughputInfoResult]: ...

        @overload
        def begin_sql_database_retrieve_throughput_distribution(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                retrieve_throughput_parameters: RetrieveThroughputParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PhysicalPartitionThroughputInfoResult]: ...

        @overload
        def begin_sql_database_retrieve_throughput_distribution(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                retrieve_throughput_parameters: RetrieveThroughputParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PhysicalPartitionThroughputInfoResult]: ...

        @overload
        def begin_sql_database_retrieve_throughput_distribution(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                retrieve_throughput_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PhysicalPartitionThroughputInfoResult]: ...

        @overload
        def begin_update_sql_container_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                update_throughput_parameters: ThroughputSettingsUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ThroughputSettingsGetResults]: ...

        @overload
        def begin_update_sql_container_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                update_throughput_parameters: ThroughputSettingsUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ThroughputSettingsGetResults]: ...

        @overload
        def begin_update_sql_container_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                update_throughput_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ThroughputSettingsGetResults]: ...

        @overload
        def begin_update_sql_database_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                update_throughput_parameters: ThroughputSettingsUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ThroughputSettingsGetResults]: ...

        @overload
        def begin_update_sql_database_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                update_throughput_parameters: ThroughputSettingsUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ThroughputSettingsGetResults]: ...

        @overload
        def begin_update_sql_database_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                update_throughput_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ThroughputSettingsGetResults]: ...

        @distributed_trace
        def get_client_encryption_key(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                client_encryption_key_name: str, 
                **kwargs: Any
            ) -> ClientEncryptionKeyGetResults: ...

        @distributed_trace
        def get_sql_container(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                **kwargs: Any
            ) -> SqlContainerGetResults: ...

        @distributed_trace
        def get_sql_container_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                **kwargs: Any
            ) -> ThroughputSettingsGetResults: ...

        @distributed_trace
        def get_sql_database(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> SqlDatabaseGetResults: ...

        @distributed_trace
        def get_sql_database_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> ThroughputSettingsGetResults: ...

        @distributed_trace
        def get_sql_role_assignment(
                self, 
                role_assignment_id: str, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> SqlRoleAssignmentGetResults: ...

        @distributed_trace
        def get_sql_role_definition(
                self, 
                role_definition_id: str, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> SqlRoleDefinitionGetResults: ...

        @distributed_trace
        def get_sql_stored_procedure(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                stored_procedure_name: str, 
                **kwargs: Any
            ) -> SqlStoredProcedureGetResults: ...

        @distributed_trace
        def get_sql_trigger(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                trigger_name: str, 
                **kwargs: Any
            ) -> SqlTriggerGetResults: ...

        @distributed_trace
        def get_sql_user_defined_function(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                user_defined_function_name: str, 
                **kwargs: Any
            ) -> SqlUserDefinedFunctionGetResults: ...

        @distributed_trace
        def list_client_encryption_keys(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ClientEncryptionKeyGetResults]: ...

        @distributed_trace
        def list_sql_containers(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SqlContainerGetResults]: ...

        @distributed_trace
        def list_sql_databases(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SqlDatabaseGetResults]: ...

        @distributed_trace
        def list_sql_role_assignments(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SqlRoleAssignmentGetResults]: ...

        @distributed_trace
        def list_sql_role_definitions(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SqlRoleDefinitionGetResults]: ...

        @distributed_trace
        def list_sql_stored_procedures(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SqlStoredProcedureGetResults]: ...

        @distributed_trace
        def list_sql_triggers(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SqlTriggerGetResults]: ...

        @distributed_trace
        def list_sql_user_defined_functions(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_name: str, 
                container_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SqlUserDefinedFunctionGetResults]: ...


    class azure.mgmt.cosmosdb.operations.TableResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_update_table(
                self, 
                resource_group_name: str, 
                account_name: str, 
                table_name: str, 
                create_update_table_parameters: TableCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TableGetResults]: ...

        @overload
        def begin_create_update_table(
                self, 
                resource_group_name: str, 
                account_name: str, 
                table_name: str, 
                create_update_table_parameters: TableCreateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TableGetResults]: ...

        @overload
        def begin_create_update_table(
                self, 
                resource_group_name: str, 
                account_name: str, 
                table_name: str, 
                create_update_table_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TableGetResults]: ...

        @overload
        def begin_create_update_table_role_assignment(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_assignment_id: str, 
                create_update_table_role_assignment_parameters: TableRoleAssignmentResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TableRoleAssignmentResource]: ...

        @overload
        def begin_create_update_table_role_assignment(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_assignment_id: str, 
                create_update_table_role_assignment_parameters: TableRoleAssignmentResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TableRoleAssignmentResource]: ...

        @overload
        def begin_create_update_table_role_assignment(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_assignment_id: str, 
                create_update_table_role_assignment_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TableRoleAssignmentResource]: ...

        @overload
        def begin_create_update_table_role_definition(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_definition_id: str, 
                create_update_table_role_definition_parameters: TableRoleDefinitionResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TableRoleDefinitionResource]: ...

        @overload
        def begin_create_update_table_role_definition(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_definition_id: str, 
                create_update_table_role_definition_parameters: TableRoleDefinitionResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TableRoleDefinitionResource]: ...

        @overload
        def begin_create_update_table_role_definition(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_definition_id: str, 
                create_update_table_role_definition_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TableRoleDefinitionResource]: ...

        @distributed_trace
        def begin_delete_table(
                self, 
                resource_group_name: str, 
                account_name: str, 
                table_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_delete_table_role_assignment(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_assignment_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_delete_table_role_definition(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_definition_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_migrate_table_to_autoscale(
                self, 
                resource_group_name: str, 
                account_name: str, 
                table_name: str, 
                **kwargs: Any
            ) -> LROPoller[ThroughputSettingsGetResults]: ...

        @distributed_trace
        def begin_migrate_table_to_manual_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                table_name: str, 
                **kwargs: Any
            ) -> LROPoller[ThroughputSettingsGetResults]: ...

        @overload
        def begin_retrieve_continuous_backup_information(
                self, 
                resource_group_name: str, 
                account_name: str, 
                table_name: str, 
                location: ContinuousBackupRestoreLocation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BackupInformation]: ...

        @overload
        def begin_retrieve_continuous_backup_information(
                self, 
                resource_group_name: str, 
                account_name: str, 
                table_name: str, 
                location: ContinuousBackupRestoreLocation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BackupInformation]: ...

        @overload
        def begin_retrieve_continuous_backup_information(
                self, 
                resource_group_name: str, 
                account_name: str, 
                table_name: str, 
                location: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BackupInformation]: ...

        @overload
        def begin_update_table_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                table_name: str, 
                update_throughput_parameters: ThroughputSettingsUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ThroughputSettingsGetResults]: ...

        @overload
        def begin_update_table_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                table_name: str, 
                update_throughput_parameters: ThroughputSettingsUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ThroughputSettingsGetResults]: ...

        @overload
        def begin_update_table_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                table_name: str, 
                update_throughput_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ThroughputSettingsGetResults]: ...

        @distributed_trace
        def get_table(
                self, 
                resource_group_name: str, 
                account_name: str, 
                table_name: str, 
                **kwargs: Any
            ) -> TableGetResults: ...

        @distributed_trace
        def get_table_role_assignment(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_assignment_id: str, 
                **kwargs: Any
            ) -> TableRoleAssignmentResource: ...

        @distributed_trace
        def get_table_role_definition(
                self, 
                resource_group_name: str, 
                account_name: str, 
                role_definition_id: str, 
                **kwargs: Any
            ) -> TableRoleDefinitionResource: ...

        @distributed_trace
        def get_table_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                table_name: str, 
                **kwargs: Any
            ) -> ThroughputSettingsGetResults: ...

        @distributed_trace
        def list_table_role_assignments(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[TableRoleAssignmentResource]: ...

        @distributed_trace
        def list_table_role_definitions(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[TableRoleDefinitionResource]: ...

        @distributed_trace
        def list_tables(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[TableGetResults]: ...


    class azure.mgmt.cosmosdb.operations.ThroughputPoolAccountOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                throughput_pool_name: str, 
                throughput_pool_account_name: str, 
                body: ThroughputPoolAccountResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ThroughputPoolAccountResource]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                throughput_pool_name: str, 
                throughput_pool_account_name: str, 
                body: ThroughputPoolAccountResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ThroughputPoolAccountResource]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                throughput_pool_name: str, 
                throughput_pool_account_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ThroughputPoolAccountResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                throughput_pool_name: str, 
                throughput_pool_account_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                throughput_pool_name: str, 
                throughput_pool_account_name: str, 
                **kwargs: Any
            ) -> ThroughputPoolAccountResource: ...


    class azure.mgmt.cosmosdb.operations.ThroughputPoolAccountsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                throughput_pool_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ThroughputPoolAccountResource]: ...


    class azure.mgmt.cosmosdb.operations.ThroughputPoolOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                throughput_pool_name: str, 
                body: ThroughputPoolResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ThroughputPoolResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                throughput_pool_name: str, 
                body: ThroughputPoolResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ThroughputPoolResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                throughput_pool_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ThroughputPoolResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                throughput_pool_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                throughput_pool_name: str, 
                body: Optional[ThroughputPoolUpdate] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ThroughputPoolResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                throughput_pool_name: str, 
                body: Optional[ThroughputPoolUpdate] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ThroughputPoolResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                throughput_pool_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ThroughputPoolResource]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                throughput_pool_name: str, 
                **kwargs: Any
            ) -> ThroughputPoolResource: ...


    class azure.mgmt.cosmosdb.operations.ThroughputPoolsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[ThroughputPoolResource]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ThroughputPoolResource]: ...


namespace azure.mgmt.cosmosdb.types

    class azure.mgmt.cosmosdb.types.ARMProxyResource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "type": str
        id: str
        name: str
        type: str


    class azure.mgmt.cosmosdb.types.ARMResourceProperties(TypedDict, total=False):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": str
        key "name": str
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        tags: dict[str, str]
        type: str


    class azure.mgmt.cosmosdb.types.AccountKeyMetadata(TypedDict, total=False):
        key "approximateLastUsageTime": str
        key "generationTime": str
        approximateLastUsageTime: str
        generationTime: str


    class azure.mgmt.cosmosdb.types.AnalyticalStorageConfiguration(TypedDict, total=False):
        key "schemaType": Union[str, AnalyticalStorageSchemaType]
        schemaType: Union[str, AnalyticalStorageSchemaType]


    class azure.mgmt.cosmosdb.types.ApiProperties(TypedDict, total=False):
        key "serverVersion": Union[str, ServerVersion]
        serverVersion: Union[str, ServerVersion]


    class azure.mgmt.cosmosdb.types.AuthenticationMethodLdapProperties(TypedDict, total=False):
        key "connectionTimeoutInMs": int
        key "searchBaseDistinguishedName": str
        key "searchFilterTemplate": str
        key "serverHostname": str
        key "serverPort": int
        key "serviceUserDistinguishedName": str
        key "serviceUserPassword": str
        connectionTimeoutInMs: int
        searchBaseDistinguishedName: str
        searchFilterTemplate: str
        serverCertificates: list[Certificate]
        serverHostname: str
        serverPort: int
        serviceUserDistinguishedName: str
        serviceUserPassword: str


    class azure.mgmt.cosmosdb.types.AutoUpgradePolicyResource(TypedDict, total=False):
        key "throughputPolicy": ForwardRef('ThroughputPolicyResource', module='types')
        throughputPolicy: ThroughputPolicyResource


    class azure.mgmt.cosmosdb.types.AutoscaleSettings(TypedDict, total=False):
        key "maxThroughput": int
        maxThroughput: int


    class azure.mgmt.cosmosdb.types.AutoscaleSettingsResource(TypedDict, total=False):
        key "autoUpgradePolicy": ForwardRef('AutoUpgradePolicyResource', module='types')
        key "maxThroughput": Required[int]
        key "targetMaxThroughput": int
        autoUpgradePolicy: AutoUpgradePolicyResource
        maxThroughput: int
        targetMaxThroughput: int


    class azure.mgmt.cosmosdb.types.AzureBlobContainer(TypedDict, total=False):
        key "containerName": Required[str]
        containerName: str


    class azure.mgmt.cosmosdb.types.AzureBlobDataTransferDataSourceSink(TypedDict, total=False):
        key "component": Required[Literal[DataTransferComponent.AZURE_BLOB_STORAGE]]
        key "containerName": Required[str]
        key "endpointUrl": str
        component: Literal[DataTransferComponent.AZURE_BLOB_STORAGE]
        containerName: str
        endpointUrl: str


    class azure.mgmt.cosmosdb.types.AzureBlobSourceSinkDetails(TypedDict, total=False):
        key "endpointUrl": Required[str]
        endpointUrl: str


    class azure.mgmt.cosmosdb.types.BackupPolicyMigrationState(TypedDict, total=False):
        key "startTime": str
        key "status": Union[str, BackupPolicyMigrationStatus]
        key "targetType": Union[str, BackupPolicyType]
        startTime: str
        status: Union[str, BackupPolicyMigrationStatus]
        targetType: Union[str, BackupPolicyType]


    class azure.mgmt.cosmosdb.types.BackupPolicyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTINUOUS = "Continuous"
        PERIODIC = "Periodic"


    class azure.mgmt.cosmosdb.types.BackupSchedule(TypedDict, total=False):
        key "cronExpression": str
        key "retentionInHours": int
        key "scheduleName": str
        cronExpression: str
        retentionInHours: int
        scheduleName: str


    class azure.mgmt.cosmosdb.types.BaseCopyJobTask(TypedDict, total=False):
        key "processedCount": int
        key "totalCount": int
        processedCount: int
        totalCount: int


    class azure.mgmt.cosmosdb.types.BlobToCassandraRUCopyJobProperties(TypedDict, total=False):
        key "destinationDetails": ForwardRef('CosmosDBSourceSinkDetails', module='types')
        key "jobType": Required[Literal[CopyJobType.AZURE_BLOB_STORAGE_TO_CASSANDRA_RU]]
        key "sourceDetails": Required[AzureBlobSourceSinkDetails]
        key "tasks": Required[list[BlobToCassandraRUCopyJobTask]]
        destinationDetails: CosmosDBSourceSinkDetails
        jobType: Literal[CopyJobType.AZURE_BLOB_STORAGE_TO_CASSANDRA_RU]
        sourceDetails: AzureBlobSourceSinkDetails
        tasks: list[BlobToCassandraRUCopyJobTask]


    class azure.mgmt.cosmosdb.types.BlobToCassandraRUCopyJobTask(BaseCopyJobTask):
        key "destination": Required[CosmosDBCassandraTable]
        key "processedCount": int
        key "source": Required[AzureBlobContainer]
        key "totalCount": int
        destination: CosmosDBCassandraTable
        processedCount: int
        source: AzureBlobContainer
        totalCount: int


    class azure.mgmt.cosmosdb.types.Capability(TypedDict, total=False):
        key "name": str
        name: str


    class azure.mgmt.cosmosdb.types.Capacity(TypedDict, total=False):
        key "totalThroughputLimit": int
        totalThroughputLimit: int


    class azure.mgmt.cosmosdb.types.CassandraError(TypedDict, total=False):
        key "additionalErrorInfo": str
        key "code": str
        key "message": str
        key "target": str
        additionalErrorInfo: str
        code: str
        message: str
        target: str


    class azure.mgmt.cosmosdb.types.CassandraKeyspaceCreateUpdateParameters(ARMResourceProperties):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": str
        key "name": str
        key "properties": Required[CassandraKeyspaceCreateUpdateProperties]
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: CassandraKeyspaceCreateUpdateProperties
        tags: dict[str, str]
        type: str


    class azure.mgmt.cosmosdb.types.CassandraKeyspaceCreateUpdateProperties(TypedDict, total=False):
        key "options": ForwardRef('CreateUpdateOptions', module='types')
        key "resource": Required[CassandraKeyspaceResource]
        options: CreateUpdateOptions
        resource: CassandraKeyspaceResource


    class azure.mgmt.cosmosdb.types.CassandraKeyspaceResource(TypedDict, total=False):
        key "id": Required[str]
        id: str


    class azure.mgmt.cosmosdb.types.CassandraPartitionKey(TypedDict, total=False):
        key "name": str
        name: str


    class azure.mgmt.cosmosdb.types.CassandraRUToBlobCopyJobProperties(TypedDict, total=False):
        key "destinationDetails": Required[AzureBlobSourceSinkDetails]
        key "jobType": Required[Literal[CopyJobType.CASSANDRA_RU_TO_AZURE_BLOB_STORAGE]]
        key "sourceDetails": ForwardRef('CosmosDBSourceSinkDetails', module='types')
        key "tasks": Required[list[CassandraRUToBlobCopyJobTask]]
        destinationDetails: AzureBlobSourceSinkDetails
        jobType: Literal[CopyJobType.CASSANDRA_RU_TO_AZURE_BLOB_STORAGE]
        sourceDetails: CosmosDBSourceSinkDetails
        tasks: list[CassandraRUToBlobCopyJobTask]


    class azure.mgmt.cosmosdb.types.CassandraRUToBlobCopyJobTask(BaseCopyJobTask):
        key "destination": Required[AzureBlobContainer]
        key "processedCount": int
        key "source": Required[CosmosDBCassandraTable]
        key "totalCount": int
        destination: AzureBlobContainer
        processedCount: int
        source: CosmosDBCassandraTable
        totalCount: int


    class azure.mgmt.cosmosdb.types.CassandraRUToCassandraRUCopyJobProperties(TypedDict, total=False):
        key "destinationDetails": ForwardRef('CosmosDBSourceSinkDetails', module='types')
        key "jobType": Required[Literal[CopyJobType.CASSANDRA_RU_TO_CASSANDRA_RU]]
        key "sourceDetails": ForwardRef('CosmosDBSourceSinkDetails', module='types')
        key "tasks": Required[list[CassandraRUToCassandraRUCopyJobTask]]
        destinationDetails: CosmosDBSourceSinkDetails
        jobType: Literal[CopyJobType.CASSANDRA_RU_TO_CASSANDRA_RU]
        sourceDetails: CosmosDBSourceSinkDetails
        tasks: list[CassandraRUToCassandraRUCopyJobTask]


    class azure.mgmt.cosmosdb.types.CassandraRUToCassandraRUCopyJobTask(BaseCopyJobTask):
        key "destination": Required[CosmosDBCassandraTable]
        key "processedCount": int
        key "source": Required[CosmosDBCassandraTable]
        key "totalCount": int
        destination: CosmosDBCassandraTable
        processedCount: int
        source: CosmosDBCassandraTable
        totalCount: int


    class azure.mgmt.cosmosdb.types.CassandraRoleAssignmentResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('CassandraRoleAssignmentResourceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: CassandraRoleAssignmentResourceProperties
        systemData: SystemData
        type: str


    class azure.mgmt.cosmosdb.types.CassandraRoleAssignmentResourceProperties(TypedDict, total=False):
        key "principalId": str
        key "provisioningState": str
        key "roleDefinitionId": str
        key "scope": str
        principalId: str
        provisioningState: str
        roleDefinitionId: str
        scope: str


    class azure.mgmt.cosmosdb.types.CassandraRoleDefinitionResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('CassandraRoleDefinitionResourceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: CassandraRoleDefinitionResourceProperties
        systemData: SystemData
        type: str


    class azure.mgmt.cosmosdb.types.CassandraRoleDefinitionResourceProperties(TypedDict, total=False):
        key "id": str
        key "roleName": str
        key "type": Union[str, RoleDefinitionType]
        assignableScopes: list[str]
        id: str
        permissions: list[Permission]
        roleName: str
        type: Union[str, RoleDefinitionType]


    class azure.mgmt.cosmosdb.types.CassandraSchema(TypedDict, total=False):
        clusterKeys: list[ClusterKey]
        columns: list[Column]
        partitionKeys: list[CassandraPartitionKey]


    class azure.mgmt.cosmosdb.types.CassandraTableCreateUpdateParameters(ARMResourceProperties):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": str
        key "name": str
        key "properties": Required[CassandraTableCreateUpdateProperties]
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: CassandraTableCreateUpdateProperties
        tags: dict[str, str]
        type: str


    class azure.mgmt.cosmosdb.types.CassandraTableCreateUpdateProperties(TypedDict, total=False):
        key "options": ForwardRef('CreateUpdateOptions', module='types')
        key "resource": Required[CassandraTableResource]
        options: CreateUpdateOptions
        resource: CassandraTableResource


    class azure.mgmt.cosmosdb.types.CassandraTableResource(TypedDict, total=False):
        key "analyticalStorageTtl": int
        key "defaultTtl": int
        key "id": Required[str]
        key "schema": ForwardRef('CassandraSchema', module='types')
        analyticalStorageTtl: int
        defaultTtl: int
        id: str
        schema: CassandraSchema


    class azure.mgmt.cosmosdb.types.CassandraViewCreateUpdateParameters(ARMResourceProperties):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": str
        key "name": str
        key "properties": Required[CassandraViewCreateUpdateProperties]
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: CassandraViewCreateUpdateProperties
        tags: dict[str, str]
        type: str


    class azure.mgmt.cosmosdb.types.CassandraViewCreateUpdateProperties(TypedDict, total=False):
        key "options": ForwardRef('CreateUpdateOptions', module='types')
        key "resource": Required[CassandraViewResource]
        options: CreateUpdateOptions
        resource: CassandraViewResource


    class azure.mgmt.cosmosdb.types.CassandraViewResource(TypedDict, total=False):
        key "id": Required[str]
        key "viewDefinition": Required[str]
        id: str
        viewDefinition: str


    class azure.mgmt.cosmosdb.types.Certificate(TypedDict, total=False):
        key "pem": str
        pem: str


    class azure.mgmt.cosmosdb.types.ChaosFaultProperties(TypedDict, total=False):
        key "action": Union[str, SupportedActions]
        key "containerName": str
        key "databaseName": str
        key "provisioningState": str
        key "region": str
        action: Union[str, SupportedActions]
        containerName: str
        databaseName: str
        provisioningState: str
        region: str


    class azure.mgmt.cosmosdb.types.ChaosFaultResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('ChaosFaultProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ChaosFaultProperties
        systemData: SystemData
        type: str


    class azure.mgmt.cosmosdb.types.ClientEncryptionIncludedPath(TypedDict, total=False):
        key "clientEncryptionKeyId": Required[str]
        key "encryptionAlgorithm": Required[str]
        key "encryptionType": Required[str]
        key "path": Required[str]
        clientEncryptionKeyId: str
        encryptionAlgorithm: str
        encryptionType: str
        path: str


    class azure.mgmt.cosmosdb.types.ClientEncryptionKeyCreateUpdateParameters(TypedDict, total=False):
        key "properties": Required[ClientEncryptionKeyCreateUpdateProperties]
        properties: ClientEncryptionKeyCreateUpdateProperties


    class azure.mgmt.cosmosdb.types.ClientEncryptionKeyCreateUpdateProperties(TypedDict, total=False):
        key "resource": Required[ClientEncryptionKeyResource]
        resource: ClientEncryptionKeyResource


    class azure.mgmt.cosmosdb.types.ClientEncryptionKeyResource(TypedDict, total=False):
        key "encryptionAlgorithm": str
        key "id": str
        key "keyWrapMetadata": ForwardRef('KeyWrapMetadata', module='types')
        key "wrappedDataEncryptionKey": str
        encryptionAlgorithm: str
        id: str
        keyWrapMetadata: KeyWrapMetadata
        wrappedDataEncryptionKey: str


    class azure.mgmt.cosmosdb.types.ClientEncryptionPolicy(TypedDict, total=False):
        key "includedPaths": Required[list[ClientEncryptionIncludedPath]]
        key "policyFormatVersion": Required[int]
        includedPaths: list[ClientEncryptionIncludedPath]
        policyFormatVersion: int


    class azure.mgmt.cosmosdb.types.ClusterKey(TypedDict, total=False):
        key "name": str
        key "orderBy": str
        name: str
        orderBy: str


    class azure.mgmt.cosmosdb.types.ClusterResource(ProxyResource):
        key "id": str
        key "identity": ForwardRef('ManagedCassandraManagedServiceIdentity', module='types')
        key "location": str
        key "name": str
        key "properties": ForwardRef('ClusterResourceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedCassandraManagedServiceIdentity
        location: str
        name: str
        properties: ClusterResourceProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.cosmosdb.types.ClusterResourceProperties(TypedDict, total=False):
        key "authenticationMethod": Union[str, AuthenticationMethod]
        key "autoReplicate": Union[str, AutoReplicate]
        key "azureConnectionMethod": Union[str, AzureConnectionType]
        key "cassandraAuditLoggingEnabled": bool
        key "cassandraVersion": str
        key "clusterNameOverride": str
        key "clusterType": Union[str, ClusterType]
        key "deallocated": bool
        key "delegatedManagementSubnetId": str
        key "hoursBetweenBackups": int
        key "initialCassandraAdminPassword": str
        key "privateLinkResourceId": str
        key "prometheusEndpoint": ForwardRef('SeedNode', module='types')
        key "provisionError": ForwardRef('CassandraError', module='types')
        key "provisioningState": Union[str, ManagedCassandraProvisioningState]
        key "repairEnabled": bool
        key "restoreFromBackupId": str
        key "scheduledEventStrategy": Union[str, ScheduledEventStrategy]
        authenticationMethod: Union[str, AuthenticationMethod]
        autoReplicate: Union[str, AutoReplicate]
        azureConnectionMethod: Union[str, AzureConnectionType]
        backupSchedules: list[BackupSchedule]
        cassandraAuditLoggingEnabled: bool
        cassandraVersion: str
        clientCertificates: list[Certificate]
        clusterNameOverride: str
        clusterType: Union[str, ClusterType]
        deallocated: bool
        delegatedManagementSubnetId: str
        extensions: list[str]
        externalDataCenters: list[str]
        externalGossipCertificates: list[Certificate]
        externalSeedNodes: list[SeedNode]
        gossipCertificates: list[Certificate]
        hoursBetweenBackups: int
        initialCassandraAdminPassword: str
        privateLinkResourceId: str
        prometheusEndpoint: SeedNode
        provisionError: CassandraError
        provisioningState: Union[str, ManagedCassandraProvisioningState]
        repairEnabled: bool
        restoreFromBackupId: str
        scheduledEventStrategy: Union[str, ScheduledEventStrategy]
        seedNodes: list[SeedNode]


    class azure.mgmt.cosmosdb.types.Column(TypedDict, total=False):
        key "name": str
        key "type": str
        name: str
        type: str


    class azure.mgmt.cosmosdb.types.CommandAsyncPostBody(TypedDict):
        key "arguments": Any
        key "cassandra-stop-start": bool
        key "command": Required[str]
        key "host": Required[str]
        key "readWrite": bool
        arguments: Any
        cassandra-stop-start: bool
        command: str
        host: str
        readWrite: bool


    class azure.mgmt.cosmosdb.types.CommandPostBody(TypedDict):
        key "cassandra-stop-start": bool
        key "command": Required[str]
        key "host": Required[str]
        key "readwrite": bool
        arguments: dict[str, str]
        cassandra-stop-start: bool
        command: str
        host: str
        readwrite: bool


    class azure.mgmt.cosmosdb.types.CompositePath(TypedDict, total=False):
        key "order": Union[str, CompositePathSortOrder]
        key "path": str
        order: Union[str, CompositePathSortOrder]
        path: str


    class azure.mgmt.cosmosdb.types.ComputedProperty(TypedDict, total=False):
        key "name": str
        key "query": str
        name: str
        query: str


    class azure.mgmt.cosmosdb.types.ConflictResolutionPolicy(TypedDict, total=False):
        key "conflictResolutionPath": str
        key "conflictResolutionProcedure": str
        key "mode": Union[str, ConflictResolutionMode]
        conflictResolutionPath: str
        conflictResolutionProcedure: str
        mode: Union[str, ConflictResolutionMode]


    class azure.mgmt.cosmosdb.types.ConsistencyPolicy(TypedDict, total=False):
        key "defaultConsistencyLevel": Required[Union[str, DefaultConsistencyLevel]]
        key "maxIntervalInSeconds": int
        key "maxStalenessPrefix": int
        defaultConsistencyLevel: Union[str, DefaultConsistencyLevel]
        maxIntervalInSeconds: int
        maxStalenessPrefix: int


    class azure.mgmt.cosmosdb.types.ContainerPartitionKey(TypedDict, total=False):
        key "kind": Union[str, PartitionKind]
        key "systemKey": bool
        key "version": int
        kind: Union[str, PartitionKind]
        paths: list[str]
        systemKey: bool
        version: int


    class azure.mgmt.cosmosdb.types.ContinuousBackupRestoreLocation(TypedDict, total=False):
        key "location": str
        location: str


    class azure.mgmt.cosmosdb.types.ContinuousModeBackupPolicy(TypedDict, total=False):
        key "continuousModeProperties": ForwardRef('ContinuousModeProperties', module='types')
        key "migrationState": ForwardRef('BackupPolicyMigrationState', module='types')
        key "type": Required[Literal[BackupPolicyType.CONTINUOUS]]
        continuousModeProperties: ContinuousModeProperties
        migrationState: BackupPolicyMigrationState
        type: Literal[BackupPolicyType.CONTINUOUS]


    class azure.mgmt.cosmosdb.types.ContinuousModeProperties(TypedDict, total=False):
        key "tier": Union[str, ContinuousTier]
        tier: Union[str, ContinuousTier]


    class azure.mgmt.cosmosdb.types.CopyJobGetResults(ProxyResource):
        key "id": str
        key "name": str
        key "properties": Required[CopyJobProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: CopyJobProperties
        systemData: SystemData
        type: str


    class azure.mgmt.cosmosdb.types.CopyJobProperties(TypedDict, total=False):
        key "duration": str
        key "error": ForwardRef('ErrorResponse', module='types')
        key "jobProperties": Required[BaseCopyJobProperties]
        key "lastUpdatedUtcTime": str
        key "mode": Union[str, CopyJobMode]
        key "processedCount": int
        key "status": Union[str, CopyJobStatus]
        key "totalCount": int
        key "workerCount": int
        duration: str
        error: ErrorResponse
        jobProperties: BaseCopyJobProperties
        lastUpdatedUtcTime: str
        mode: Union[str, CopyJobMode]
        processedCount: int
        status: Union[str, CopyJobStatus]
        totalCount: int
        workerCount: int


    class azure.mgmt.cosmosdb.types.CopyJobType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_BLOB_STORAGE_TO_CASSANDRA_RU = "AzureBlobStorageToCassandraRU"
        CASSANDRA_RU_TO_AZURE_BLOB_STORAGE = "CassandraRUToAzureBlobStorage"
        CASSANDRA_RU_TO_CASSANDRA_RU = "CassandraRUToCassandraRU"
        MONGO_RU_TO_MONGO_RU = "MongoRUToMongoRU"
        MONGO_RU_TO_MONGO_V_CORE = "MongoRUToMongoVCore"
        NO_SQL_RU_TO_NO_SQL_RU = "NoSqlRUToNoSqlRU"


    class azure.mgmt.cosmosdb.types.CorsPolicy(TypedDict, total=False):
        key "allowedHeaders": str
        key "allowedMethods": str
        key "allowedOrigins": Required[str]
        key "exposedHeaders": str
        key "maxAgeInSeconds": int
        allowedHeaders: str
        allowedMethods: str
        allowedOrigins: str
        exposedHeaders: str
        maxAgeInSeconds: int


    class azure.mgmt.cosmosdb.types.CosmosCassandraDataTransferDataSourceSink(TypedDict, total=False):
        key "component": Required[Literal[DataTransferComponent.COSMOS_DB_CASSANDRA]]
        key "keyspaceName": Required[str]
        key "remoteAccountName": str
        key "tableName": Required[str]
        component: Literal[DataTransferComponent.COSMOS_DB_CASSANDRA]
        keyspaceName: str
        remoteAccountName: str
        tableName: str


    class azure.mgmt.cosmosdb.types.CosmosDBCassandraTable(TypedDict, total=False):
        key "keyspaceName": Required[str]
        key "tableName": Required[str]
        keyspaceName: str
        tableName: str


    class azure.mgmt.cosmosdb.types.CosmosDBMongoCollection(TypedDict, total=False):
        key "collectionName": Required[str]
        key "databaseName": Required[str]
        collectionName: str
        databaseName: str


    class azure.mgmt.cosmosdb.types.CosmosDBMongoVCoreCollection(TypedDict, total=False):
        key "collectionName": Required[str]
        key "databaseName": Required[str]
        collectionName: str
        databaseName: str


    class azure.mgmt.cosmosdb.types.CosmosDBNoSqlContainer(TypedDict, total=False):
        key "containerName": Required[str]
        key "databaseName": Required[str]
        containerName: str
        databaseName: str


    class azure.mgmt.cosmosdb.types.CosmosDBSourceSinkDetails(TypedDict, total=False):
        key "remoteAccountName": str
        remoteAccountName: str


    class azure.mgmt.cosmosdb.types.CosmosMongoDataTransferDataSourceSink(TypedDict, total=False):
        key "collectionName": Required[str]
        key "component": Required[Literal[DataTransferComponent.COSMOS_DB_MONGO]]
        key "databaseName": Required[str]
        key "remoteAccountName": str
        collectionName: str
        component: Literal[DataTransferComponent.COSMOS_DB_MONGO]
        databaseName: str
        remoteAccountName: str


    class azure.mgmt.cosmosdb.types.CosmosMongoVCoreDataTransferDataSourceSink(TypedDict, total=False):
        key "collectionName": Required[str]
        key "component": Required[Literal[DataTransferComponent.COSMOS_DB_MONGO_V_CORE]]
        key "connectionStringKeyVaultUri": str
        key "databaseName": Required[str]
        key "hostName": str
        collectionName: str
        component: Literal[DataTransferComponent.COSMOS_DB_MONGO_V_CORE]
        connectionStringKeyVaultUri: str
        databaseName: str
        hostName: str


    class azure.mgmt.cosmosdb.types.CosmosSqlDataTransferDataSourceSink(TypedDict, total=False):
        key "component": Required[Literal[DataTransferComponent.COSMOS_DB_SQL]]
        key "containerName": Required[str]
        key "databaseName": Required[str]
        key "remoteAccountName": str
        component: Literal[DataTransferComponent.COSMOS_DB_SQL]
        containerName: str
        databaseName: str
        remoteAccountName: str


    class azure.mgmt.cosmosdb.types.CreateJobRequest(ARMProxyResource):
        key "id": str
        key "name": str
        key "properties": Required[DataTransferJobProperties]
        key "type": str
        id: str
        name: str
        properties: DataTransferJobProperties
        type: str


    class azure.mgmt.cosmosdb.types.CreateUpdateOptions(TypedDict, total=False):
        key "autoscaleSettings": ForwardRef('AutoscaleSettings', module='types')
        key "throughput": int
        autoscaleSettings: AutoscaleSettings
        throughput: int


    class azure.mgmt.cosmosdb.types.DataCenterResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('DataCenterResourceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: DataCenterResourceProperties
        systemData: SystemData
        type: str


    class azure.mgmt.cosmosdb.types.DataCenterResourceProperties(TypedDict, total=False):
        key "authenticationMethodLdapProperties": ForwardRef('AuthenticationMethodLdapProperties', module='types')
        key "availabilityZone": bool
        key "backupStorageCustomerKeyUri": str
        key "base64EncodedCassandraYamlFragment": str
        key "dataCenterLocation": str
        key "deallocated": bool
        key "delegatedSubnetId": str
        key "diskCapacity": int
        key "diskSku": str
        key "managedDiskCustomerKeyUri": str
        key "nodeCount": int
        key "privateEndpointIpAddress": str
        key "provisionError": ForwardRef('CassandraError', module='types')
        key "provisioningState": Union[str, ManagedCassandraProvisioningState]
        key "sku": str
        authenticationMethodLdapProperties: AuthenticationMethodLdapProperties
        availabilityZone: bool
        backupStorageCustomerKeyUri: str
        base64EncodedCassandraYamlFragment: str
        dataCenterLocation: str
        deallocated: bool
        delegatedSubnetId: str
        diskCapacity: int
        diskSku: str
        managedDiskCustomerKeyUri: str
        nodeCount: int
        privateEndpointIpAddress: str
        provisionError: CassandraError
        provisioningState: Union[str, ManagedCassandraProvisioningState]
        seedNodes: list[SeedNode]
        sku: str


    class azure.mgmt.cosmosdb.types.DataMaskingPolicy(TypedDict, total=False):
        key "isPolicyEnabled": bool
        excludedPaths: list[DataMaskingPolicyExcludedPathsItem]
        includedPaths: list[DataMaskingPolicyIncludedPathsItem]
        isPolicyEnabled: bool


    class azure.mgmt.cosmosdb.types.DataMaskingPolicyExcludedPathsItem(TypedDict, total=False):
        key "path": Required[str]
        path: str


    class azure.mgmt.cosmosdb.types.DataMaskingPolicyIncludedPathsItem(TypedDict, total=False):
        key "length": int
        key "path": Required[str]
        key "startPosition": int
        key "strategy": str
        length: int
        path: str
        startPosition: int
        strategy: str


    class azure.mgmt.cosmosdb.types.DataTransferComponent(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_BLOB_STORAGE = "AzureBlobStorage"
        BASE_COSMOS_DATA_TRANSFER_DATA_SOURCE_SINK = "BaseCosmosDataTransferDataSourceSink"
        COSMOS_DB_CASSANDRA = "CosmosDBCassandra"
        COSMOS_DB_MONGO = "CosmosDBMongo"
        COSMOS_DB_MONGO_V_CORE = "CosmosDBMongoVCore"
        COSMOS_DB_SQL = "CosmosDBSql"


    class azure.mgmt.cosmosdb.types.DataTransferJobProperties(TypedDict, total=False):
        key "destination": Required[DataTransferDataSourceSink]
        key "duration": str
        key "error": ForwardRef('ErrorResponseAutoGenerated', module='types')
        key "jobName": str
        key "lastUpdatedUtcTime": str
        key "mode": Union[str, DataTransferJobMode]
        key "processedCount": int
        key "source": Required[DataTransferDataSourceSink]
        key "status": str
        key "totalCount": int
        key "workerCount": int
        destination: DataTransferDataSourceSink
        duration: str
        error: ErrorResponseAutoGenerated
        jobName: str
        lastUpdatedUtcTime: str
        mode: Union[str, DataTransferJobMode]
        processedCount: int
        source: DataTransferDataSourceSink
        status: str
        totalCount: int
        workerCount: int


    class azure.mgmt.cosmosdb.types.DataTransferServiceResourceCreateUpdateProperties(TypedDict, total=False):
        key "instanceCount": int
        key "instanceSize": Union[str, ServiceSize]
        key "serviceType": Required[Literal[ServiceType.DATA_TRANSFER]]
        instanceCount: int
        instanceSize: Union[str, ServiceSize]
        serviceType: Literal[ServiceType.DATA_TRANSFER]


    class azure.mgmt.cosmosdb.types.DatabaseAccountCreateUpdateParameters(ARMResourceProperties):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "kind": Union[str, DatabaseAccountKind]
        key "location": str
        key "name": str
        key "properties": Required[DatabaseAccountCreateUpdateProperties]
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        kind: Union[str, DatabaseAccountKind]
        location: str
        name: str
        properties: DatabaseAccountCreateUpdateProperties
        tags: dict[str, str]
        type: str


    class azure.mgmt.cosmosdb.types.DatabaseAccountCreateUpdateProperties(TypedDict, total=False):
        key "analyticalStorageConfiguration": ForwardRef('AnalyticalStorageConfiguration', module='types')
        key "apiProperties": ForwardRef('ApiProperties', module='types')
        key "backupPolicy": ForwardRef('BackupPolicy', module='types')
        key "capacity": ForwardRef('Capacity', module='types')
        key "capacityMode": Union[str, CapacityMode]
        key "connectorOffer": Union[str, ConnectorOffer]
        key "consistencyPolicy": ForwardRef('ConsistencyPolicy', module='types')
        key "createMode": Union[str, CreateMode]
        key "customerManagedKeyStatus": str
        key "databaseAccountOfferType": Required[Literal["Standard"]]
        key "defaultIdentity": str
        key "defaultPriorityLevel": Union[str, DefaultPriorityLevel]
        key "diagnosticLogSettings": ForwardRef('DiagnosticLogSettings', module='types')
        key "disableKeyBasedMetadataWriteAccess": bool
        key "disableLocalAuth": bool
        key "enableAllVersionsAndDeletesChangeFeed": bool
        key "enableAnalyticalStorage": bool
        key "enableAutomaticFailover": bool
        key "enableBurstCapacity": bool
        key "enableCassandraConnector": bool
        key "enableFreeTier": bool
        key "enableMaterializedViews": bool
        key "enableMultipleWriteLocations": bool
        key "enablePartitionMerge": bool
        key "enablePerRegionPerPartitionAutoscale": bool
        key "enablePriorityBasedExecution": bool
        key "enforceHierarchicalPartitionKeyIdLastLevel": bool
        key "isVirtualNetworkFilterEnabled": bool
        key "keyVaultKeyUri": str
        key "keysMetadata": ForwardRef('DatabaseAccountKeysMetadata', module='types')
        key "locations": Required[list[Location]]
        key "minimalTlsVersion": Union[str, MinimalTlsVersion]
        key "networkAclBypass": Union[str, NetworkAclBypass]
        key "publicNetworkAccess": Union[str, PublicNetworkAccess]
        key "restoreParameters": ForwardRef('RestoreParameters', module='types')
        key "softDeleteConfiguration": ForwardRef('SoftDeleteConfiguration', module='types')
        analyticalStorageConfiguration: AnalyticalStorageConfiguration
        apiProperties: ApiProperties
        backupPolicy: BackupPolicy
        capabilities: list[Capability]
        capacity: Capacity
        capacityMode: Union[str, CapacityMode]
        connectorOffer: Union[str, ConnectorOffer]
        consistencyPolicy: ConsistencyPolicy
        cors: list[CorsPolicy]
        createMode: Union[str, CreateMode]
        customerManagedKeyStatus: str
        databaseAccountOfferType: Literal[Standard]
        defaultIdentity: str
        defaultPriorityLevel: Union[str, DefaultPriorityLevel]
        diagnosticLogSettings: DiagnosticLogSettings
        disableKeyBasedMetadataWriteAccess: bool
        disableLocalAuth: bool
        enableAllVersionsAndDeletesChangeFeed: bool
        enableAnalyticalStorage: bool
        enableAutomaticFailover: bool
        enableBurstCapacity: bool
        enableCassandraConnector: bool
        enableFreeTier: bool
        enableMaterializedViews: bool
        enableMultipleWriteLocations: bool
        enablePartitionMerge: bool
        enablePerRegionPerPartitionAutoscale: bool
        enablePriorityBasedExecution: bool
        enforceHierarchicalPartitionKeyIdLastLevel: bool
        ipRules: list[IpAddressOrRange]
        isVirtualNetworkFilterEnabled: bool
        keyVaultKeyUri: str
        keysMetadata: DatabaseAccountKeysMetadata
        locations: list[Location]
        minimalTlsVersion: Union[str, MinimalTlsVersion]
        networkAclBypass: Union[str, NetworkAclBypass]
        networkAclBypassResourceIds: list[str]
        publicNetworkAccess: Union[str, PublicNetworkAccess]
        restoreParameters: RestoreParameters
        softDeleteConfiguration: SoftDeleteConfiguration
        virtualNetworkRules: list[VirtualNetworkRule]


    class azure.mgmt.cosmosdb.types.DatabaseAccountKeysMetadata(TypedDict, total=False):
        key "primaryMasterKey": ForwardRef('AccountKeyMetadata', module='types')
        key "primaryReadonlyMasterKey": ForwardRef('AccountKeyMetadata', module='types')
        key "secondaryMasterKey": ForwardRef('AccountKeyMetadata', module='types')
        key "secondaryReadonlyMasterKey": ForwardRef('AccountKeyMetadata', module='types')
        primaryMasterKey: AccountKeyMetadata
        primaryReadonlyMasterKey: AccountKeyMetadata
        secondaryMasterKey: AccountKeyMetadata
        secondaryReadonlyMasterKey: AccountKeyMetadata


    class azure.mgmt.cosmosdb.types.DatabaseAccountRegenerateKeyParameters(TypedDict, total=False):
        key "keyKind": Required[Union[str, KeyKind]]
        key "skipAccountKeysLastUsageCheck": bool
        keyKind: Union[str, KeyKind]
        skipAccountKeysLastUsageCheck: bool


    class azure.mgmt.cosmosdb.types.DatabaseAccountUpdateParameters(TypedDict, total=False):
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": str
        key "properties": ForwardRef('DatabaseAccountUpdateProperties', module='types')
        identity: ManagedServiceIdentity
        location: str
        properties: DatabaseAccountUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.cosmosdb.types.DatabaseAccountUpdateProperties(TypedDict, total=False):
        key "analyticalStorageConfiguration": ForwardRef('AnalyticalStorageConfiguration', module='types')
        key "apiProperties": ForwardRef('ApiProperties', module='types')
        key "backupPolicy": ForwardRef('BackupPolicy', module='types')
        key "capacity": ForwardRef('Capacity', module='types')
        key "capacityMode": Union[str, CapacityMode]
        key "connectorOffer": Union[str, ConnectorOffer]
        key "consistencyPolicy": ForwardRef('ConsistencyPolicy', module='types')
        key "customerManagedKeyStatus": str
        key "defaultIdentity": str
        key "defaultPriorityLevel": Union[str, DefaultPriorityLevel]
        key "diagnosticLogSettings": ForwardRef('DiagnosticLogSettings', module='types')
        key "disableKeyBasedMetadataWriteAccess": bool
        key "disableLocalAuth": bool
        key "enableAllVersionsAndDeletesChangeFeed": bool
        key "enableAnalyticalStorage": bool
        key "enableAutomaticFailover": bool
        key "enableBurstCapacity": bool
        key "enableCassandraConnector": bool
        key "enableFreeTier": bool
        key "enableMaterializedViews": bool
        key "enableMultipleWriteLocations": bool
        key "enablePartitionMerge": bool
        key "enablePerRegionPerPartitionAutoscale": bool
        key "enablePriorityBasedExecution": bool
        key "enforceHierarchicalPartitionKeyIdLastLevel": bool
        key "isVirtualNetworkFilterEnabled": bool
        key "keyVaultKeyUri": str
        key "keysMetadata": ForwardRef('DatabaseAccountKeysMetadata', module='types')
        key "minimalTlsVersion": Union[str, MinimalTlsVersion]
        key "networkAclBypass": Union[str, NetworkAclBypass]
        key "publicNetworkAccess": Union[str, PublicNetworkAccess]
        key "softDeleteConfiguration": ForwardRef('SoftDeleteConfiguration', module='types')
        analyticalStorageConfiguration: AnalyticalStorageConfiguration
        apiProperties: ApiProperties
        backupPolicy: BackupPolicy
        capabilities: list[Capability]
        capacity: Capacity
        capacityMode: Union[str, CapacityMode]
        connectorOffer: Union[str, ConnectorOffer]
        consistencyPolicy: ConsistencyPolicy
        cors: list[CorsPolicy]
        customerManagedKeyStatus: str
        defaultIdentity: str
        defaultPriorityLevel: Union[str, DefaultPriorityLevel]
        diagnosticLogSettings: DiagnosticLogSettings
        disableKeyBasedMetadataWriteAccess: bool
        disableLocalAuth: bool
        enableAllVersionsAndDeletesChangeFeed: bool
        enableAnalyticalStorage: bool
        enableAutomaticFailover: bool
        enableBurstCapacity: bool
        enableCassandraConnector: bool
        enableFreeTier: bool
        enableMaterializedViews: bool
        enableMultipleWriteLocations: bool
        enablePartitionMerge: bool
        enablePerRegionPerPartitionAutoscale: bool
        enablePriorityBasedExecution: bool
        enforceHierarchicalPartitionKeyIdLastLevel: bool
        ipRules: list[IpAddressOrRange]
        isVirtualNetworkFilterEnabled: bool
        keyVaultKeyUri: str
        keysMetadata: DatabaseAccountKeysMetadata
        locations: list[Location]
        minimalTlsVersion: Union[str, MinimalTlsVersion]
        networkAclBypass: Union[str, NetworkAclBypass]
        networkAclBypassResourceIds: list[str]
        publicNetworkAccess: Union[str, PublicNetworkAccess]
        softDeleteConfiguration: SoftDeleteConfiguration
        virtualNetworkRules: list[VirtualNetworkRule]


    class azure.mgmt.cosmosdb.types.DatabaseRestoreResource(TypedDict, total=False):
        key "databaseName": str
        collectionNames: list[str]
        databaseName: str


    class azure.mgmt.cosmosdb.types.DiagnosticLogSettings(TypedDict, total=False):
        key "enableFullTextQuery": Union[str, EnableFullTextQuery]
        enableFullTextQuery: Union[str, EnableFullTextQuery]


    class azure.mgmt.cosmosdb.types.ErrorAdditionalInfo(TypedDict, total=False):
        key "info": Any
        key "type": str
        info: Any
        type: str


    class azure.mgmt.cosmosdb.types.ErrorDetail(TypedDict, total=False):
        key "code": str
        key "message": str
        key "target": str
        additionalInfo: list[ErrorAdditionalInfo]
        code: str
        details: list[ErrorDetail]
        message: str
        target: str


    class azure.mgmt.cosmosdb.types.ErrorResponse(TypedDict, total=False):
        key "error": ForwardRef('ErrorDetail', module='types')
        error: ErrorDetail


    class azure.mgmt.cosmosdb.types.ErrorResponseAutoGenerated(TypedDict, total=False):
        key "code": str
        key "message": str
        code: str
        message: str


    class azure.mgmt.cosmosdb.types.ExcludedPath(TypedDict, total=False):
        key "path": str
        path: str


    class azure.mgmt.cosmosdb.types.FailoverPolicies(TypedDict, total=False):
        key "failoverPolicies": Required[list[FailoverPolicy]]
        failoverPolicies: list[FailoverPolicy]


    class azure.mgmt.cosmosdb.types.FailoverPolicy(TypedDict, total=False):
        key "failoverPriority": int
        key "id": str
        key "locationName": str
        failoverPriority: int
        id: str
        locationName: str


    class azure.mgmt.cosmosdb.types.FleetAnalyticsProperties(TypedDict, total=False):
        key "provisioningState": Union[str, Status]
        key "storageLocationType": Union[str, FleetAnalyticsPropertiesStorageLocationType]
        key "storageLocationUri": str
        provisioningState: Union[str, Status]
        storageLocationType: Union[str, FleetAnalyticsPropertiesStorageLocationType]
        storageLocationUri: str


    class azure.mgmt.cosmosdb.types.FleetAnalyticsResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('FleetAnalyticsProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: FleetAnalyticsProperties
        systemData: SystemData
        type: str


    class azure.mgmt.cosmosdb.types.FleetResource(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('FleetResourceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: FleetResourceProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.cosmosdb.types.FleetResourceProperties(TypedDict, total=False):
        key "provisioningState": Union[str, Status]
        provisioningState: Union[str, Status]


    class azure.mgmt.cosmosdb.types.FleetResourceUpdate(TypedDict, total=False):
        key "properties": ForwardRef('FleetResourceProperties', module='types')
        properties: FleetResourceProperties
        tags: dict[str, str]


    class azure.mgmt.cosmosdb.types.FleetspaceAccountProperties(TypedDict, total=False):
        key "globalDatabaseAccountProperties": ForwardRef('FleetspaceAccountPropertiesGlobalDatabaseAccountProperties', module='types')
        key "provisioningState": Union[str, Status]
        globalDatabaseAccountProperties: FleetspaceAccountPropertiesGlobalDatabaseAccountProperties
        provisioningState: Union[str, Status]


    class azure.mgmt.cosmosdb.types.FleetspaceAccountPropertiesGlobalDatabaseAccountProperties(TypedDict, total=False):
        key "armLocation": str
        key "resourceId": str
        armLocation: str
        resourceId: str


    class azure.mgmt.cosmosdb.types.FleetspaceAccountResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('FleetspaceAccountProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: FleetspaceAccountProperties
        systemData: SystemData
        type: str


    class azure.mgmt.cosmosdb.types.FleetspaceProperties(TypedDict, total=False):
        key "fleetspaceApiKind": Union[str, FleetspacePropertiesFleetspaceApiKind]
        key "provisioningState": Union[str, Status]
        key "serviceTier": Union[str, FleetspacePropertiesServiceTier]
        key "throughputPoolConfiguration": ForwardRef('FleetspacePropertiesThroughputPoolConfiguration', module='types')
        dataRegions: list[str]
        fleetspaceApiKind: Union[str, FleetspacePropertiesFleetspaceApiKind]
        provisioningState: Union[str, Status]
        serviceTier: Union[str, FleetspacePropertiesServiceTier]
        throughputPoolConfiguration: FleetspacePropertiesThroughputPoolConfiguration


    class azure.mgmt.cosmosdb.types.FleetspacePropertiesThroughputPoolConfiguration(TypedDict, total=False):
        key "dedicatedRUs": int
        key "maxConsumableRUs": int
        key "maxThroughput": int
        key "minThroughput": int
        dedicatedRUs: int
        maxConsumableRUs: int
        maxThroughput: int
        minThroughput: int


    class azure.mgmt.cosmosdb.types.FleetspaceResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('FleetspaceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: FleetspaceProperties
        systemData: SystemData
        type: str


    class azure.mgmt.cosmosdb.types.FleetspaceUpdate(TypedDict, total=False):
        key "properties": ForwardRef('FleetspaceProperties', module='types')
        properties: FleetspaceProperties


    class azure.mgmt.cosmosdb.types.FullTextIndexPath(TypedDict, total=False):
        key "path": Required[str]
        path: str


    class azure.mgmt.cosmosdb.types.FullTextPath(TypedDict, total=False):
        key "language": str
        key "path": Required[str]
        language: str
        path: str


    class azure.mgmt.cosmosdb.types.FullTextPolicy(TypedDict, total=False):
        key "defaultLanguage": str
        defaultLanguage: str
        fullTextPaths: list[FullTextPath]


    class azure.mgmt.cosmosdb.types.GarnetClusterResource(TrackedResource):
        key "id": str
        key "identity": ForwardRef('ManagedCassandraManagedServiceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('GarnetClusterResourceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedCassandraManagedServiceIdentity
        location: str
        name: str
        properties: GarnetClusterResourceProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.cosmosdb.types.GarnetClusterResourcePatch(TypedDict, total=False):
        key "properties": ForwardRef('GarnetClusterResourcePatchProperties', module='types')
        properties: GarnetClusterResourcePatchProperties


    class azure.mgmt.cosmosdb.types.GarnetClusterResourcePatchProperties(TypedDict, total=False):
        key "authenticationMethod": Union[str, GarnetAuthenticationType]
        key "clusterType": Union[str, ClusterType]
        key "persistence": bool
        authenticationMethod: Union[str, GarnetAuthenticationType]
        clusterType: Union[str, ClusterType]
        extensions: list[str]
        persistence: bool


    class azure.mgmt.cosmosdb.types.GarnetClusterResourceProperties(TypedDict, total=False):
        key "allocationState": Union[str, AllocationState]
        key "authenticationMethod": Union[str, GarnetAuthenticationType]
        key "availabilityZone": bool
        key "clusterType": Union[str, ClusterType]
        key "nodeSku": str
        key "persistence": bool
        key "provisionError": ForwardRef('ErrorDetail', module='types')
        key "provisioningState": Union[str, GarnetCacheProvisioningState]
        key "replicationFactor": int
        key "shardCount": int
        key "subnetId": str
        allocationState: Union[str, AllocationState]
        authenticationMethod: Union[str, GarnetAuthenticationType]
        availabilityZone: bool
        clusterType: Union[str, ClusterType]
        endPoints: list[GarnetClusterResourcePropertiesEndPointsItem]
        extensions: list[str]
        nodeSku: str
        persistence: bool
        provisionError: ErrorDetail
        provisioningState: Union[str, GarnetCacheProvisioningState]
        replicationFactor: int
        shardCount: int
        subnetId: str


    class azure.mgmt.cosmosdb.types.GarnetClusterResourcePropertiesEndPointsItem(TypedDict, total=False):
        key "ipAddress": str
        key "port": int
        ipAddress: str
        port: int


    class azure.mgmt.cosmosdb.types.GraphAPIComputeServiceResourceCreateUpdateProperties(TypedDict, total=False):
        key "instanceCount": int
        key "instanceSize": Union[str, ServiceSize]
        key "serviceType": Required[Literal[ServiceType.GRAPH_API_COMPUTE]]
        instanceCount: int
        instanceSize: Union[str, ServiceSize]
        serviceType: Literal[ServiceType.GRAPH_API_COMPUTE]


    class azure.mgmt.cosmosdb.types.GraphResource(TypedDict, total=False):
        key "id": Required[str]
        id: str


    class azure.mgmt.cosmosdb.types.GraphResourceCreateUpdateParameters(ARMResourceProperties):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": str
        key "name": str
        key "properties": Required[GraphResourceCreateUpdateProperties]
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: GraphResourceCreateUpdateProperties
        tags: dict[str, str]
        type: str


    class azure.mgmt.cosmosdb.types.GraphResourceCreateUpdateProperties(TypedDict, total=False):
        key "options": ForwardRef('CreateUpdateOptions', module='types')
        key "resource": Required[GraphResource]
        options: CreateUpdateOptions
        resource: GraphResource


    class azure.mgmt.cosmosdb.types.GremlinDatabaseCreateUpdateParameters(ARMResourceProperties):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": str
        key "name": str
        key "properties": Required[GremlinDatabaseCreateUpdateProperties]
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: GremlinDatabaseCreateUpdateProperties
        tags: dict[str, str]
        type: str


    class azure.mgmt.cosmosdb.types.GremlinDatabaseCreateUpdateProperties(TypedDict, total=False):
        key "options": ForwardRef('CreateUpdateOptions', module='types')
        key "resource": Required[GremlinDatabaseResource]
        options: CreateUpdateOptions
        resource: GremlinDatabaseResource


    class azure.mgmt.cosmosdb.types.GremlinDatabaseResource(TypedDict, total=False):
        key "createMode": Union[str, CreateMode]
        key "id": Required[str]
        key "restoreParameters": ForwardRef('ResourceRestoreParameters', module='types')
        createMode: Union[str, CreateMode]
        id: str
        restoreParameters: ResourceRestoreParameters


    class azure.mgmt.cosmosdb.types.GremlinDatabaseRestoreResource(TypedDict, total=False):
        key "databaseName": str
        databaseName: str
        graphNames: list[str]


    class azure.mgmt.cosmosdb.types.GremlinGraphCreateUpdateParameters(ARMResourceProperties):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": str
        key "name": str
        key "properties": Required[GremlinGraphCreateUpdateProperties]
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: GremlinGraphCreateUpdateProperties
        tags: dict[str, str]
        type: str


    class azure.mgmt.cosmosdb.types.GremlinGraphCreateUpdateProperties(TypedDict, total=False):
        key "options": ForwardRef('CreateUpdateOptions', module='types')
        key "resource": Required[GremlinGraphResource]
        options: CreateUpdateOptions
        resource: GremlinGraphResource


    class azure.mgmt.cosmosdb.types.GremlinGraphResource(TypedDict, total=False):
        key "analyticalStorageTtl": int
        key "conflictResolutionPolicy": ForwardRef('ConflictResolutionPolicy', module='types')
        key "createMode": Union[str, CreateMode]
        key "defaultTtl": int
        key "id": Required[str]
        key "indexingPolicy": ForwardRef('IndexingPolicy', module='types')
        key "partitionKey": ForwardRef('ContainerPartitionKey', module='types')
        key "restoreParameters": ForwardRef('ResourceRestoreParameters', module='types')
        key "uniqueKeyPolicy": ForwardRef('UniqueKeyPolicy', module='types')
        analyticalStorageTtl: int
        conflictResolutionPolicy: ConflictResolutionPolicy
        createMode: Union[str, CreateMode]
        defaultTtl: int
        id: str
        indexingPolicy: IndexingPolicy
        partitionKey: ContainerPartitionKey
        restoreParameters: ResourceRestoreParameters
        uniqueKeyPolicy: UniqueKeyPolicy


    class azure.mgmt.cosmosdb.types.GremlinRoleAssignmentResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('GremlinRoleAssignmentResourceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: GremlinRoleAssignmentResourceProperties
        systemData: SystemData
        type: str


    class azure.mgmt.cosmosdb.types.GremlinRoleAssignmentResourceProperties(TypedDict, total=False):
        key "principalId": str
        key "provisioningState": str
        key "roleDefinitionId": str
        key "scope": str
        principalId: str
        provisioningState: str
        roleDefinitionId: str
        scope: str


    class azure.mgmt.cosmosdb.types.GremlinRoleDefinitionResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('GremlinRoleDefinitionResourceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: GremlinRoleDefinitionResourceProperties
        systemData: SystemData
        type: str


    class azure.mgmt.cosmosdb.types.GremlinRoleDefinitionResourceProperties(TypedDict, total=False):
        key "id": str
        key "roleName": str
        key "type": Union[str, RoleDefinitionType]
        assignableScopes: list[str]
        id: str
        permissions: list[Permission]
        roleName: str
        type: Union[str, RoleDefinitionType]


    class azure.mgmt.cosmosdb.types.IncludedPath(TypedDict, total=False):
        key "path": str
        indexes: list[Indexes]
        path: str


    class azure.mgmt.cosmosdb.types.Indexes(TypedDict, total=False):
        key "dataType": Union[str, DataType]
        key "kind": Union[str, IndexKind]
        key "precision": int
        dataType: Union[str, DataType]
        kind: Union[str, IndexKind]
        precision: int


    class azure.mgmt.cosmosdb.types.IndexingPolicy(TypedDict, total=False):
        key "automatic": bool
        key "indexingMode": Union[str, IndexingMode]
        automatic: bool
        compositeIndexes: list[list[CompositePath]]
        excludedPaths: list[ExcludedPath]
        fullTextIndexes: list[FullTextIndexPath]
        includedPaths: list[IncludedPath]
        indexingMode: Union[str, IndexingMode]
        spatialIndexes: list[SpatialSpec]
        vectorIndexes: list[VectorIndex]


    class azure.mgmt.cosmosdb.types.IpAddressOrRange(TypedDict, total=False):
        key "ipAddressOrRange": str
        ipAddressOrRange: str


    class azure.mgmt.cosmosdb.types.KeyWrapMetadata(TypedDict, total=False):
        key "algorithm": str
        key "name": str
        key "type": str
        key "value": str
        algorithm: str
        name: str
        type: str
        value: str


    class azure.mgmt.cosmosdb.types.Location(TypedDict, total=False):
        key "documentEndpoint": str
        key "failoverPriority": int
        key "id": str
        key "isZoneRedundant": bool
        key "locationName": str
        key "provisioningState": str
        documentEndpoint: str
        failoverPriority: int
        id: str
        isZoneRedundant: bool
        locationName: str
        provisioningState: str


    class azure.mgmt.cosmosdb.types.ManagedCassandraManagedServiceIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Union[str, ManagedCassandraResourceIdentityType]
        principalId: str
        tenantId: str
        type: Union[str, ManagedCassandraResourceIdentityType]


    class azure.mgmt.cosmosdb.types.ManagedServiceIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Union[str, ResourceIdentityType]
        principalId: str
        tenantId: str
        type: Union[str, ResourceIdentityType]
        userAssignedIdentities: dict[str, ManagedServiceIdentityUserAssignedIdentity]


    class azure.mgmt.cosmosdb.types.ManagedServiceIdentityUserAssignedIdentity(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        clientId: str
        principalId: str


    class azure.mgmt.cosmosdb.types.MaterializedViewDefinition(TypedDict, total=False):
        key "definition": Required[str]
        key "sourceCollectionId": Required[str]
        key "sourceCollectionRid": str
        key "throughputBucketForBuild": int
        definition: str
        sourceCollectionId: str
        sourceCollectionRid: str
        throughputBucketForBuild: int


    class azure.mgmt.cosmosdb.types.MaterializedViewDetails(TypedDict, total=False):
        key "id": str
        _rid: str
        id: str


    class azure.mgmt.cosmosdb.types.MaterializedViewsBuilderServiceResourceCreateUpdateProperties(TypedDict, total=False):
        key "instanceCount": int
        key "instanceSize": Union[str, ServiceSize]
        key "serviceType": Required[Literal[ServiceType.MATERIALIZED_VIEWS_BUILDER]]
        instanceCount: int
        instanceSize: Union[str, ServiceSize]
        serviceType: Literal[ServiceType.MATERIALIZED_VIEWS_BUILDER]


    class azure.mgmt.cosmosdb.types.MaterializedViewsProperties(TypedDict, total=False):
        key "throughputBucketForBuild": int
        throughputBucketForBuild: int


    class azure.mgmt.cosmosdb.types.MergeParameters(TypedDict, total=False):
        key "isDryRun": bool
        isDryRun: bool


    class azure.mgmt.cosmosdb.types.MongoDBCollectionCreateUpdateParameters(ARMResourceProperties):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": str
        key "name": str
        key "properties": Required[MongoDBCollectionCreateUpdateProperties]
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: MongoDBCollectionCreateUpdateProperties
        tags: dict[str, str]
        type: str


    class azure.mgmt.cosmosdb.types.MongoDBCollectionCreateUpdateProperties(TypedDict, total=False):
        key "options": ForwardRef('CreateUpdateOptions', module='types')
        key "resource": Required[MongoDBCollectionResource]
        options: CreateUpdateOptions
        resource: MongoDBCollectionResource


    class azure.mgmt.cosmosdb.types.MongoDBCollectionResource(TypedDict, total=False):
        key "analyticalStorageTtl": int
        key "createMode": Union[str, CreateMode]
        key "id": Required[str]
        key "restoreParameters": ForwardRef('ResourceRestoreParameters', module='types')
        analyticalStorageTtl: int
        createMode: Union[str, CreateMode]
        id: str
        indexes: list[MongoIndex]
        restoreParameters: ResourceRestoreParameters
        shardKey: dict[str, str]


    class azure.mgmt.cosmosdb.types.MongoDBDatabaseCreateUpdateParameters(ARMResourceProperties):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": str
        key "name": str
        key "properties": Required[MongoDBDatabaseCreateUpdateProperties]
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: MongoDBDatabaseCreateUpdateProperties
        tags: dict[str, str]
        type: str


    class azure.mgmt.cosmosdb.types.MongoDBDatabaseCreateUpdateProperties(TypedDict, total=False):
        key "options": ForwardRef('CreateUpdateOptions', module='types')
        key "resource": Required[MongoDBDatabaseResource]
        options: CreateUpdateOptions
        resource: MongoDBDatabaseResource


    class azure.mgmt.cosmosdb.types.MongoDBDatabaseResource(TypedDict, total=False):
        key "createMode": Union[str, CreateMode]
        key "id": Required[str]
        key "restoreParameters": ForwardRef('ResourceRestoreParameters', module='types')
        createMode: Union[str, CreateMode]
        id: str
        restoreParameters: ResourceRestoreParameters


    class azure.mgmt.cosmosdb.types.MongoIndex(TypedDict, total=False):
        key "key": ForwardRef('MongoIndexKeys', module='types')
        key "options": ForwardRef('MongoIndexOptions', module='types')
        key: MongoIndexKeys
        options: MongoIndexOptions


    class azure.mgmt.cosmosdb.types.MongoIndexKeys(TypedDict, total=False):
        keys: list[str]


    class azure.mgmt.cosmosdb.types.MongoIndexOptions(TypedDict, total=False):
        key "expireAfterSeconds": int
        key "unique": bool
        expireAfterSeconds: int
        unique: bool


    class azure.mgmt.cosmosdb.types.MongoMIRoleAssignmentResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('MongoMIRoleAssignmentResourceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: MongoMIRoleAssignmentResourceProperties
        systemData: SystemData
        type: str


    class azure.mgmt.cosmosdb.types.MongoMIRoleAssignmentResourceProperties(TypedDict, total=False):
        key "principalId": str
        key "provisioningState": str
        key "roleDefinitionId": str
        key "scope": str
        principalId: str
        provisioningState: str
        roleDefinitionId: str
        scope: str


    class azure.mgmt.cosmosdb.types.MongoMIRoleDefinitionResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('MongoMIRoleDefinitionResourceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: MongoMIRoleDefinitionResourceProperties
        systemData: SystemData
        type: str


    class azure.mgmt.cosmosdb.types.MongoMIRoleDefinitionResourceProperties(TypedDict, total=False):
        key "id": str
        key "roleName": str
        key "type": Union[str, RoleDefinitionType]
        assignableScopes: list[str]
        id: str
        permissions: list[Permission]
        roleName: str
        type: Union[str, RoleDefinitionType]


    class azure.mgmt.cosmosdb.types.MongoRUToMongoRUCopyJobProperties(TypedDict, total=False):
        key "destinationDetails": ForwardRef('CosmosDBSourceSinkDetails', module='types')
        key "jobType": Required[Literal[CopyJobType.MONGO_RU_TO_MONGO_RU]]
        key "sourceDetails": ForwardRef('CosmosDBSourceSinkDetails', module='types')
        key "tasks": Required[list[MongoRUToMongoRUCopyJobTask]]
        destinationDetails: CosmosDBSourceSinkDetails
        jobType: Literal[CopyJobType.MONGO_RU_TO_MONGO_RU]
        sourceDetails: CosmosDBSourceSinkDetails
        tasks: list[MongoRUToMongoRUCopyJobTask]


    class azure.mgmt.cosmosdb.types.MongoRUToMongoRUCopyJobTask(BaseCopyJobTask):
        key "destination": Required[CosmosDBMongoCollection]
        key "processedCount": int
        key "source": Required[CosmosDBMongoCollection]
        key "totalCount": int
        destination: CosmosDBMongoCollection
        processedCount: int
        source: CosmosDBMongoCollection
        totalCount: int


    class azure.mgmt.cosmosdb.types.MongoRUToMongoVCoreCopyJobProperties(TypedDict, total=False):
        key "destinationDetails": Required[MongoVCoreSourceSinkDetails]
        key "jobType": Required[Literal[CopyJobType.MONGO_RU_TO_MONGO_V_CORE]]
        key "sourceDetails": ForwardRef('CosmosDBSourceSinkDetails', module='types')
        key "tasks": Required[list[MongoRUToMongoVCoreCopyJobTask]]
        destinationDetails: MongoVCoreSourceSinkDetails
        jobType: Literal[CopyJobType.MONGO_RU_TO_MONGO_V_CORE]
        sourceDetails: CosmosDBSourceSinkDetails
        tasks: list[MongoRUToMongoVCoreCopyJobTask]


    class azure.mgmt.cosmosdb.types.MongoRUToMongoVCoreCopyJobTask(BaseCopyJobTask):
        key "destination": Required[CosmosDBMongoVCoreCollection]
        key "processedCount": int
        key "source": Required[CosmosDBMongoCollection]
        key "totalCount": int
        destination: CosmosDBMongoVCoreCollection
        processedCount: int
        source: CosmosDBMongoCollection
        totalCount: int


    class azure.mgmt.cosmosdb.types.MongoRoleDefinitionCreateUpdateParameters(TypedDict, total=False):
        key "properties": ForwardRef('MongoRoleDefinitionResource', module='types')
        properties: MongoRoleDefinitionResource


    class azure.mgmt.cosmosdb.types.MongoRoleDefinitionResource(TypedDict, total=False):
        key "databaseName": str
        key "roleName": str
        key "type": Union[str, MongoRoleDefinitionType]
        databaseName: str
        privileges: list[Privilege]
        roleName: str
        roles: list[Role]
        type: Union[str, MongoRoleDefinitionType]


    class azure.mgmt.cosmosdb.types.MongoUserDefinitionCreateUpdateParameters(TypedDict, total=False):
        key "properties": ForwardRef('MongoUserDefinitionResource', module='types')
        properties: MongoUserDefinitionResource


    class azure.mgmt.cosmosdb.types.MongoUserDefinitionResource(TypedDict, total=False):
        key "customData": str
        key "databaseName": str
        key "mechanisms": str
        key "password": str
        key "userName": str
        customData: str
        databaseName: str
        mechanisms: str
        password: str
        roles: list[Role]
        userName: str


    class azure.mgmt.cosmosdb.types.MongoVCoreSourceSinkDetails(TypedDict, total=False):
        key "connectionStringKeyVaultUri": str
        key "hostName": str
        connectionStringKeyVaultUri: str
        hostName: str


    class azure.mgmt.cosmosdb.types.NoSqlRUToNoSqlRUCopyJobProperties(TypedDict, total=False):
        key "destinationDetails": ForwardRef('CosmosDBSourceSinkDetails', module='types')
        key "jobType": Required[Literal[CopyJobType.NO_SQL_RU_TO_NO_SQL_RU]]
        key "sourceDetails": ForwardRef('CosmosDBSourceSinkDetails', module='types')
        key "tasks": Required[list[NoSqlRUToNoSqlRUCopyJobTask]]
        destinationDetails: CosmosDBSourceSinkDetails
        jobType: Literal[CopyJobType.NO_SQL_RU_TO_NO_SQL_RU]
        sourceDetails: CosmosDBSourceSinkDetails
        tasks: list[NoSqlRUToNoSqlRUCopyJobTask]


    class azure.mgmt.cosmosdb.types.NoSqlRUToNoSqlRUCopyJobTask(BaseCopyJobTask):
        key "destination": Required[CosmosDBNoSqlContainer]
        key "processedCount": int
        key "source": Required[CosmosDBNoSqlContainer]
        key "totalCount": int
        destination: CosmosDBNoSqlContainer
        processedCount: int
        source: CosmosDBNoSqlContainer
        totalCount: int


    class azure.mgmt.cosmosdb.types.NotebookWorkspaceCreateUpdateParameters(ARMProxyResource):
        key "id": str
        key "name": str
        key "type": str
        id: str
        name: str
        type: str


    class azure.mgmt.cosmosdb.types.PeriodicModeBackupPolicy(TypedDict, total=False):
        key "migrationState": ForwardRef('BackupPolicyMigrationState', module='types')
        key "periodicModeProperties": ForwardRef('PeriodicModeProperties', module='types')
        key "type": Required[Literal[BackupPolicyType.PERIODIC]]
        migrationState: BackupPolicyMigrationState
        periodicModeProperties: PeriodicModeProperties
        type: Literal[BackupPolicyType.PERIODIC]


    class azure.mgmt.cosmosdb.types.PeriodicModeProperties(TypedDict, total=False):
        key "backupIntervalInMinutes": int
        key "backupRetentionIntervalInHours": int
        key "backupStorageRedundancy": Union[str, BackupStorageRedundancy]
        backupIntervalInMinutes: int
        backupRetentionIntervalInHours: int
        backupStorageRedundancy: Union[str, BackupStorageRedundancy]


    class azure.mgmt.cosmosdb.types.Permission(TypedDict, total=False):
        key "id": str
        dataActions: list[str]
        id: str
        notDataActions: list[str]


    class azure.mgmt.cosmosdb.types.PhysicalPartitionId(TypedDict, total=False):
        key "id": Required[str]
        id: str


    class azure.mgmt.cosmosdb.types.PhysicalPartitionThroughputInfoResource(TypedDict, total=False):
        key "id": Required[str]
        key "targetThroughput": float
        key "throughput": float
        id: str
        targetThroughput: float
        throughput: float


    class azure.mgmt.cosmosdb.types.PrivateEndpointConnection(ProxyResource):
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


    class azure.mgmt.cosmosdb.types.PrivateEndpointConnectionProperties(TypedDict, total=False):
        key "groupId": str
        key "privateEndpoint": ForwardRef('PrivateEndpointProperty', module='types')
        key "privateLinkServiceConnectionState": ForwardRef('PrivateLinkServiceConnectionStateProperty', module='types')
        key "provisioningState": str
        groupId: str
        privateEndpoint: PrivateEndpointProperty
        privateLinkServiceConnectionState: PrivateLinkServiceConnectionStateProperty
        provisioningState: str


    class azure.mgmt.cosmosdb.types.PrivateEndpointProperty(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.cosmosdb.types.PrivateLinkServiceConnectionStateProperty(TypedDict, total=False):
        key "actionsRequired": str
        key "description": str
        key "status": str
        actionsRequired: str
        description: str
        status: str


    class azure.mgmt.cosmosdb.types.Privilege(TypedDict, total=False):
        key "resource": ForwardRef('PrivilegeResource', module='types')
        actions: list[str]
        resource: PrivilegeResource


    class azure.mgmt.cosmosdb.types.PrivilegeResource(TypedDict, total=False):
        key "collection": str
        key "db": str
        collection: str
        db: str


    class azure.mgmt.cosmosdb.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.cosmosdb.types.RedistributeThroughputParameters(ARMResourceProperties):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": str
        key "name": str
        key "properties": Required[RedistributeThroughputProperties]
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: RedistributeThroughputProperties
        tags: dict[str, str]
        type: str


    class azure.mgmt.cosmosdb.types.RedistributeThroughputProperties(TypedDict, total=False):
        key "resource": Required[RedistributeThroughputPropertiesResource]
        resource: RedistributeThroughputPropertiesResource


    class azure.mgmt.cosmosdb.types.RedistributeThroughputPropertiesResource(TypedDict, total=False):
        key "sourcePhysicalPartitionThroughputInfo": Required[list[PhysicalPartitionThroughputInfoResource]]
        key "targetPhysicalPartitionThroughputInfo": Required[list[PhysicalPartitionThroughputInfoResource]]
        key "throughputPolicy": Required[Union[str, ThroughputPolicyType]]
        sourcePhysicalPartitionThroughputInfo: list[PhysicalPartitionThroughputInfoResource]
        targetPhysicalPartitionThroughputInfo: list[PhysicalPartitionThroughputInfoResource]
        throughputPolicy: Union[str, ThroughputPolicyType]


    class azure.mgmt.cosmosdb.types.RegionForOnlineOffline(TypedDict, total=False):
        key "region": Required[str]
        region: str


    class azure.mgmt.cosmosdb.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.cosmosdb.types.ResourceRestoreParameters(RestoreParametersBase):
        key "restoreSource": str
        key "restoreTimestampInUtc": str
        key "restoreWithTtlDisabled": bool
        restoreSource: str
        restoreTimestampInUtc: str
        restoreWithTtlDisabled: bool


    class azure.mgmt.cosmosdb.types.RestoreParameters(RestoreParametersBase):
        key "restoreMode": Union[str, RestoreMode]
        key "restoreSource": str
        key "restoreTimestampInUtc": str
        key "restoreWithTtlDisabled": bool
        key "sourceBackupLocation": str
        databasesToRestore: list[DatabaseRestoreResource]
        gremlinDatabasesToRestore: list[GremlinDatabaseRestoreResource]
        restoreMode: Union[str, RestoreMode]
        restoreSource: str
        restoreTimestampInUtc: str
        restoreWithTtlDisabled: bool
        sourceBackupLocation: str
        tablesToRestore: list[str]


    class azure.mgmt.cosmosdb.types.RestoreParametersBase(TypedDict, total=False):
        key "restoreSource": str
        key "restoreTimestampInUtc": str
        key "restoreWithTtlDisabled": bool
        restoreSource: str
        restoreTimestampInUtc: str
        restoreWithTtlDisabled: bool


    class azure.mgmt.cosmosdb.types.RetrieveThroughputParameters(ARMResourceProperties):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": str
        key "name": str
        key "properties": Required[RetrieveThroughputProperties]
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: RetrieveThroughputProperties
        tags: dict[str, str]
        type: str


    class azure.mgmt.cosmosdb.types.RetrieveThroughputProperties(TypedDict, total=False):
        key "resource": Required[RetrieveThroughputPropertiesResource]
        resource: RetrieveThroughputPropertiesResource


    class azure.mgmt.cosmosdb.types.RetrieveThroughputPropertiesResource(TypedDict, total=False):
        key "physicalPartitionIds": Required[list[PhysicalPartitionId]]
        physicalPartitionIds: list[PhysicalPartitionId]


    class azure.mgmt.cosmosdb.types.Role(TypedDict, total=False):
        key "db": str
        key "role": str
        db: str
        role: str


    class azure.mgmt.cosmosdb.types.SeedNode(TypedDict, total=False):
        key "ipAddress": str
        ipAddress: str


    class azure.mgmt.cosmosdb.types.ServiceResourceCreateUpdateParameters(TypedDict, total=False):
        key "properties": ForwardRef('ServiceResourceCreateUpdateProperties', module='types')
        properties: ServiceResourceCreateUpdateProperties


    class azure.mgmt.cosmosdb.types.ServiceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DATA_TRANSFER = "DataTransfer"
        GRAPH_API_COMPUTE = "GraphAPICompute"
        MATERIALIZED_VIEWS_BUILDER = "MaterializedViewsBuilder"
        SQL_DEDICATED_GATEWAY = "SqlDedicatedGateway"


    class azure.mgmt.cosmosdb.types.SoftDeleteConfiguration(TypedDict, total=False):
        key "minMinutesBeforePermanentDeletionAllowed": int
        key "softDeleteRetentionPeriodInMinutes": int
        key "softDeletionEnabled": bool
        minMinutesBeforePermanentDeletionAllowed: int
        softDeleteRetentionPeriodInMinutes: int
        softDeletionEnabled: bool


    class azure.mgmt.cosmosdb.types.SpatialSpec(TypedDict, total=False):
        key "path": str
        path: str
        types: list[Union[str, SpatialType]]


    class azure.mgmt.cosmosdb.types.SqlContainerCreateUpdateParameters(ARMResourceProperties):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": str
        key "name": str
        key "properties": Required[SqlContainerCreateUpdateProperties]
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: SqlContainerCreateUpdateProperties
        tags: dict[str, str]
        type: str


    class azure.mgmt.cosmosdb.types.SqlContainerCreateUpdateProperties(TypedDict, total=False):
        key "options": ForwardRef('CreateUpdateOptions', module='types')
        key "resource": Required[SqlContainerResource]
        options: CreateUpdateOptions
        resource: SqlContainerResource


    class azure.mgmt.cosmosdb.types.SqlContainerResource(TypedDict, total=False):
        key "analyticalStorageTtl": int
        key "clientEncryptionPolicy": ForwardRef('ClientEncryptionPolicy', module='types')
        key "conflictResolutionPolicy": ForwardRef('ConflictResolutionPolicy', module='types')
        key "createMode": Union[str, CreateMode]
        key "dataMaskingPolicy": ForwardRef('DataMaskingPolicy', module='types')
        key "defaultTtl": int
        key "fullTextPolicy": ForwardRef('FullTextPolicy', module='types')
        key "id": Required[str]
        key "indexingPolicy": ForwardRef('IndexingPolicy', module='types')
        key "materializedViewDefinition": ForwardRef('MaterializedViewDefinition', module='types')
        key "materializedViewsProperties": ForwardRef('MaterializedViewsProperties', module='types')
        key "partitionKey": ForwardRef('ContainerPartitionKey', module='types')
        key "restoreParameters": ForwardRef('ResourceRestoreParameters', module='types')
        key "uniqueKeyPolicy": ForwardRef('UniqueKeyPolicy', module='types')
        key "vectorEmbeddingPolicy": ForwardRef('VectorEmbeddingPolicy', module='types')
        analyticalStorageTtl: int
        clientEncryptionPolicy: ClientEncryptionPolicy
        computedProperties: list[ComputedProperty]
        conflictResolutionPolicy: ConflictResolutionPolicy
        createMode: Union[str, CreateMode]
        dataMaskingPolicy: DataMaskingPolicy
        defaultTtl: int
        fullTextPolicy: FullTextPolicy
        id: str
        indexingPolicy: IndexingPolicy
        materializedViewDefinition: MaterializedViewDefinition
        materializedViews: list[MaterializedViewDetails]
        materializedViewsProperties: MaterializedViewsProperties
        partitionKey: ContainerPartitionKey
        restoreParameters: ResourceRestoreParameters
        uniqueKeyPolicy: UniqueKeyPolicy
        vectorEmbeddingPolicy: VectorEmbeddingPolicy


    class azure.mgmt.cosmosdb.types.SqlDatabaseCreateUpdateParameters(ARMResourceProperties):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": str
        key "name": str
        key "properties": Required[SqlDatabaseCreateUpdateProperties]
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: SqlDatabaseCreateUpdateProperties
        tags: dict[str, str]
        type: str


    class azure.mgmt.cosmosdb.types.SqlDatabaseCreateUpdateProperties(TypedDict, total=False):
        key "options": ForwardRef('CreateUpdateOptions', module='types')
        key "resource": Required[SqlDatabaseResource]
        options: CreateUpdateOptions
        resource: SqlDatabaseResource


    class azure.mgmt.cosmosdb.types.SqlDatabaseResource(TypedDict, total=False):
        key "createMode": Union[str, CreateMode]
        key "id": Required[str]
        key "restoreParameters": ForwardRef('ResourceRestoreParameters', module='types')
        createMode: Union[str, CreateMode]
        id: str
        restoreParameters: ResourceRestoreParameters


    class azure.mgmt.cosmosdb.types.SqlDedicatedGatewayServiceResourceCreateUpdateProperties(TypedDict, total=False):
        key "dedicatedGatewayType": Union[str, DedicatedGatewayType]
        key "instanceCount": int
        key "instanceSize": Union[str, ServiceSize]
        key "serviceType": Required[Literal[ServiceType.SQL_DEDICATED_GATEWAY]]
        dedicatedGatewayType: Union[str, DedicatedGatewayType]
        instanceCount: int
        instanceSize: Union[str, ServiceSize]
        serviceType: Literal[ServiceType.SQL_DEDICATED_GATEWAY]


    class azure.mgmt.cosmosdb.types.SqlRoleAssignmentCreateUpdateParameters(TypedDict, total=False):
        key "properties": ForwardRef('SqlRoleAssignmentResource', module='types')
        properties: SqlRoleAssignmentResource


    class azure.mgmt.cosmosdb.types.SqlRoleAssignmentResource(TypedDict, total=False):
        key "principalId": str
        key "roleDefinitionId": str
        key "scope": str
        principalId: str
        roleDefinitionId: str
        scope: str


    class azure.mgmt.cosmosdb.types.SqlRoleDefinitionCreateUpdateParameters(TypedDict, total=False):
        key "properties": ForwardRef('SqlRoleDefinitionResource', module='types')
        properties: SqlRoleDefinitionResource


    class azure.mgmt.cosmosdb.types.SqlRoleDefinitionResource(TypedDict, total=False):
        key "roleName": str
        key "type": Union[str, RoleDefinitionType]
        assignableScopes: list[str]
        permissions: list[Permission]
        roleName: str
        type: Union[str, RoleDefinitionType]


    class azure.mgmt.cosmosdb.types.SqlStoredProcedureCreateUpdateParameters(ARMResourceProperties):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": str
        key "name": str
        key "properties": Required[SqlStoredProcedureCreateUpdateProperties]
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: SqlStoredProcedureCreateUpdateProperties
        tags: dict[str, str]
        type: str


    class azure.mgmt.cosmosdb.types.SqlStoredProcedureCreateUpdateProperties(TypedDict, total=False):
        key "options": ForwardRef('CreateUpdateOptions', module='types')
        key "resource": Required[SqlStoredProcedureResource]
        options: CreateUpdateOptions
        resource: SqlStoredProcedureResource


    class azure.mgmt.cosmosdb.types.SqlStoredProcedureResource(TypedDict, total=False):
        key "body": str
        key "id": Required[str]
        body: str
        id: str


    class azure.mgmt.cosmosdb.types.SqlTriggerCreateUpdateParameters(ARMResourceProperties):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": str
        key "name": str
        key "properties": Required[SqlTriggerCreateUpdateProperties]
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: SqlTriggerCreateUpdateProperties
        tags: dict[str, str]
        type: str


    class azure.mgmt.cosmosdb.types.SqlTriggerCreateUpdateProperties(TypedDict, total=False):
        key "options": ForwardRef('CreateUpdateOptions', module='types')
        key "resource": Required[SqlTriggerResource]
        options: CreateUpdateOptions
        resource: SqlTriggerResource


    class azure.mgmt.cosmosdb.types.SqlTriggerResource(TypedDict, total=False):
        key "body": str
        key "id": Required[str]
        key "triggerOperation": Union[str, TriggerOperation]
        key "triggerType": Union[str, TriggerType]
        body: str
        id: str
        triggerOperation: Union[str, TriggerOperation]
        triggerType: Union[str, TriggerType]


    class azure.mgmt.cosmosdb.types.SqlUserDefinedFunctionCreateUpdateParameters(ARMResourceProperties):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": str
        key "name": str
        key "properties": Required[SqlUserDefinedFunctionCreateUpdateProperties]
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: SqlUserDefinedFunctionCreateUpdateProperties
        tags: dict[str, str]
        type: str


    class azure.mgmt.cosmosdb.types.SqlUserDefinedFunctionCreateUpdateProperties(TypedDict, total=False):
        key "options": ForwardRef('CreateUpdateOptions', module='types')
        key "resource": Required[SqlUserDefinedFunctionResource]
        options: CreateUpdateOptions
        resource: SqlUserDefinedFunctionResource


    class azure.mgmt.cosmosdb.types.SqlUserDefinedFunctionResource(TypedDict, total=False):
        key "body": str
        key "id": Required[str]
        body: str
        id: str


    class azure.mgmt.cosmosdb.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.cosmosdb.types.TableCreateUpdateParameters(ARMResourceProperties):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": str
        key "name": str
        key "properties": Required[TableCreateUpdateProperties]
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: TableCreateUpdateProperties
        tags: dict[str, str]
        type: str


    class azure.mgmt.cosmosdb.types.TableCreateUpdateProperties(TypedDict, total=False):
        key "options": ForwardRef('CreateUpdateOptions', module='types')
        key "resource": Required[TableResource]
        options: CreateUpdateOptions
        resource: TableResource


    class azure.mgmt.cosmosdb.types.TableResource(TypedDict, total=False):
        key "createMode": Union[str, CreateMode]
        key "id": Required[str]
        key "restoreParameters": ForwardRef('ResourceRestoreParameters', module='types')
        createMode: Union[str, CreateMode]
        id: str
        restoreParameters: ResourceRestoreParameters


    class azure.mgmt.cosmosdb.types.TableRoleAssignmentResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('TableRoleAssignmentResourceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: TableRoleAssignmentResourceProperties
        systemData: SystemData
        type: str


    class azure.mgmt.cosmosdb.types.TableRoleAssignmentResourceProperties(TypedDict, total=False):
        key "principalId": str
        key "provisioningState": str
        key "roleDefinitionId": str
        key "scope": str
        principalId: str
        provisioningState: str
        roleDefinitionId: str
        scope: str


    class azure.mgmt.cosmosdb.types.TableRoleDefinitionResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('TableRoleDefinitionResourceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: TableRoleDefinitionResourceProperties
        systemData: SystemData
        type: str


    class azure.mgmt.cosmosdb.types.TableRoleDefinitionResourceProperties(TypedDict, total=False):
        key "id": str
        key "roleName": str
        key "type": Union[str, RoleDefinitionType]
        assignableScopes: list[str]
        id: str
        permissions: list[Permission]
        roleName: str
        type: Union[str, RoleDefinitionType]


    class azure.mgmt.cosmosdb.types.ThroughputBucketResource(TypedDict, total=False):
        key "id": Required[int]
        key "isDefaultBucket": bool
        key "maxThroughputPercentage": Required[int]
        id: int
        isDefaultBucket: bool
        maxThroughputPercentage: int


    class azure.mgmt.cosmosdb.types.ThroughputPolicyResource(TypedDict, total=False):
        key "incrementPercent": int
        key "isEnabled": bool
        incrementPercent: int
        isEnabled: bool


    class azure.mgmt.cosmosdb.types.ThroughputPoolAccountProperties(TypedDict, total=False):
        key "accountInstanceId": str
        key "accountLocation": str
        key "accountResourceIdentifier": str
        key "provisioningState": Union[str, Status]
        accountInstanceId: str
        accountLocation: str
        accountResourceIdentifier: str
        provisioningState: Union[str, Status]


    class azure.mgmt.cosmosdb.types.ThroughputPoolAccountResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('ThroughputPoolAccountProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ThroughputPoolAccountProperties
        systemData: SystemData
        type: str


    class azure.mgmt.cosmosdb.types.ThroughputPoolProperties(TypedDict, total=False):
        key "maxThroughput": int
        key "provisioningState": Union[str, Status]
        maxThroughput: int
        provisioningState: Union[str, Status]


    class azure.mgmt.cosmosdb.types.ThroughputPoolResource(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('ThroughputPoolProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: ThroughputPoolProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.cosmosdb.types.ThroughputPoolUpdate(TypedDict, total=False):
        key "properties": ForwardRef('ThroughputPoolProperties', module='types')
        properties: ThroughputPoolProperties


    class azure.mgmt.cosmosdb.types.ThroughputSettingsResource(TypedDict, total=False):
        key "autoscaleSettings": ForwardRef('AutoscaleSettingsResource', module='types')
        key "instantMaximumThroughput": str
        key "minimumThroughput": str
        key "offerReplacePending": str
        key "softAllowedMaximumThroughput": str
        key "throughput": int
        autoscaleSettings: AutoscaleSettingsResource
        instantMaximumThroughput: str
        minimumThroughput: str
        offerReplacePending: str
        softAllowedMaximumThroughput: str
        throughput: int
        throughputBuckets: list[ThroughputBucketResource]


    class azure.mgmt.cosmosdb.types.ThroughputSettingsUpdateParameters(ARMResourceProperties):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": str
        key "name": str
        key "properties": Required[ThroughputSettingsUpdateProperties]
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: ThroughputSettingsUpdateProperties
        tags: dict[str, str]
        type: str


    class azure.mgmt.cosmosdb.types.ThroughputSettingsUpdateProperties(TypedDict, total=False):
        key "resource": Required[ThroughputSettingsResource]
        resource: ThroughputSettingsResource


    class azure.mgmt.cosmosdb.types.TrackedResource(Resource):
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


    class azure.mgmt.cosmosdb.types.UniqueKey(TypedDict, total=False):
        paths: list[str]


    class azure.mgmt.cosmosdb.types.UniqueKeyPolicy(TypedDict, total=False):
        uniqueKeys: list[UniqueKey]


    class azure.mgmt.cosmosdb.types.VectorEmbedding(TypedDict, total=False):
        key "dataType": Required[Union[str, VectorDataType]]
        key "dimensions": Required[int]
        key "distanceFunction": Required[Union[str, DistanceFunction]]
        key "path": Required[str]
        dataType: Union[str, VectorDataType]
        dimensions: int
        distanceFunction: Union[str, DistanceFunction]
        path: str


    class azure.mgmt.cosmosdb.types.VectorEmbeddingPolicy(TypedDict, total=False):
        vectorEmbeddings: list[VectorEmbedding]


    class azure.mgmt.cosmosdb.types.VectorIndex(TypedDict, total=False):
        key "indexingSearchListSize": int
        key "path": Required[str]
        key "quantizationByteSize": int
        key "type": Required[Union[str, VectorIndexType]]
        indexingSearchListSize: int
        path: str
        quantizationByteSize: int
        type: Union[str, VectorIndexType]
        vectorIndexShardKey: list[str]


    class azure.mgmt.cosmosdb.types.VirtualNetworkRule(TypedDict, total=False):
        key "id": str
        key "ignoreMissingVNetServiceEndpoint": bool
        id: str
        ignoreMissingVNetServiceEndpoint: bool


```