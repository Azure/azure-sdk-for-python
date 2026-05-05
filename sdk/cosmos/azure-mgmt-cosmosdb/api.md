```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.cosmosdb

    class azure.mgmt.cosmosdb.CosmosDBManagementClient: implements ContextManager 
        cassandra_clusters: CassandraClustersOperations
        cassandra_data_centers: CassandraDataCentersOperations
        cassandra_resources: CassandraResourcesOperations
        collection: CollectionOperations
        collection_partition: CollectionPartitionOperations
        collection_partition_region: CollectionPartitionRegionOperations
        collection_region: CollectionRegionOperations
        database: DatabaseOperations
        database_account_region: DatabaseAccountRegionOperations
        database_accounts: DatabaseAccountsOperations
        fleet: FleetOperations
        fleetspace: FleetspaceOperations
        fleetspace_account: FleetspaceAccountOperations
        gremlin_resources: GremlinResourcesOperations
        locations: LocationsOperations
        mongo_db_resources: MongoDBResourcesOperations
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
        sql_resources: SqlResourcesOperations
        table_resources: TableResourcesOperations

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


namespace azure.mgmt.cosmosdb.aio

    class azure.mgmt.cosmosdb.aio.CosmosDBManagementClient: implements AsyncContextManager 
        cassandra_clusters: CassandraClustersOperations
        cassandra_data_centers: CassandraDataCentersOperations
        cassandra_resources: CassandraResourcesOperations
        collection: CollectionOperations
        collection_partition: CollectionPartitionOperations
        collection_partition_region: CollectionPartitionRegionOperations
        collection_region: CollectionRegionOperations
        database: DatabaseOperations
        database_account_region: DatabaseAccountRegionOperations
        database_accounts: DatabaseAccountsOperations
        fleet: FleetOperations
        fleetspace: FleetspaceOperations
        fleetspace_account: FleetspaceAccountOperations
        gremlin_resources: GremlinResourcesOperations
        locations: LocationsOperations
        mongo_db_resources: MongoDBResourcesOperations
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
        sql_resources: SqlResourcesOperations
        table_resources: TableResourcesOperations

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
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommandOutput]: ...

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

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ClusterResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[ClusterResource]: ...

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
                create_update_cassandra_keyspace_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CassandraKeyspaceGetResults]: ...

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

        @distributed_trace_async
        async def begin_delete_cassandra_keyspace(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
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

        @distributed_trace
        def list_cassandra_keyspaces(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[CassandraKeyspaceGetResults]: ...

        @distributed_trace
        def list_cassandra_tables(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[CassandraTableGetResults]: ...


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
                filter: Optional[str] = None, 
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
                filter: Optional[str] = None, 
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
                filter: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Metric]: ...


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
                filter: Optional[str] = None, 
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
                filter: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Metric]: ...

        @distributed_trace
        def list_usages(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_rid: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[Usage]: ...


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
                body: Optional[FleetResourceUpdate] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FleetResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                body: Optional[IO[bytes]] = None, 
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
                create_update_gremlin_graph_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GremlinGraphGetResults]: ...

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
                restorable_gremlin_database_rid: Optional[str] = None, 
                start_time: Optional[str] = None, 
                end_time: Optional[str] = None, 
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
                restore_location: Optional[str] = None, 
                restore_timestamp_in_utc: Optional[str] = None, 
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
                restorable_mongodb_database_rid: Optional[str] = None, 
                start_time: Optional[str] = None, 
                end_time: Optional[str] = None, 
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
                restore_location: Optional[str] = None, 
                restore_timestamp_in_utc: Optional[str] = None, 
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
                restorable_sql_database_rid: Optional[str] = None, 
                start_time: Optional[str] = None, 
                end_time: Optional[str] = None, 
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
                restore_location: Optional[str] = None, 
                restore_timestamp_in_utc: Optional[str] = None, 
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
                restore_location: Optional[str] = None, 
                restore_timestamp_in_utc: Optional[str] = None, 
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
                start_time: Optional[str] = None, 
                end_time: Optional[str] = None, 
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
                location: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BackupInformation]: ...

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
                create_update_table_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TableGetResults]: ...

        @distributed_trace_async
        async def begin_delete_table(
                self, 
                resource_group_name: str, 
                account_name: str, 
                table_name: str, 
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
        async def get_table_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                table_name: str, 
                **kwargs: Any
            ) -> ThroughputSettingsGetResults: ...

        @distributed_trace
        def list_tables(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[TableGetResults]: ...


namespace azure.mgmt.cosmosdb.models

    class azure.mgmt.cosmosdb.models.ARMProxyResource(Model):
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


    class azure.mgmt.cosmosdb.models.ARMResourceProperties(Model):
        id: str
        location: str
        name: str
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
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


    class azure.mgmt.cosmosdb.models.AccountKeyMetadata(Model):
        generation_time: datetime

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


    class azure.mgmt.cosmosdb.models.AnalyticalStorageConfiguration(Model):
        schema_type: Union[str, AnalyticalStorageSchemaType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                schema_type: Optional[Union[str, AnalyticalStorageSchemaType]] = ..., 
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


    class azure.mgmt.cosmosdb.models.AnalyticalStorageSchemaType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FULL_FIDELITY = "FullFidelity"
        WELL_DEFINED = "WellDefined"


    class azure.mgmt.cosmosdb.models.ApiProperties(Model):
        server_version: Union[str, ServerVersion]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                server_version: Optional[Union[str, ServerVersion]] = ..., 
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


    class azure.mgmt.cosmosdb.models.AuthenticationMethodLdapProperties(Model):
        connection_timeout_in_ms: int
        search_base_distinguished_name: str
        search_filter_template: str
        server_certificates: list[Certificate]
        server_hostname: str
        server_port: int
        service_user_distinguished_name: str
        service_user_password: str

        def __eq__(self, other: Any) -> bool: ...

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
                service_user_password: Optional[str] = ..., 
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


    class azure.mgmt.cosmosdb.models.AutoUpgradePolicyResource(Model):
        throughput_policy: ThroughputPolicyResource

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                throughput_policy: Optional[ThroughputPolicyResource] = ..., 
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


    class azure.mgmt.cosmosdb.models.AutoscaleSettings(Model):
        max_throughput: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                max_throughput: Optional[int] = ..., 
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


    class azure.mgmt.cosmosdb.models.AutoscaleSettingsResource(Model):
        auto_upgrade_policy: AutoUpgradePolicyResource
        max_throughput: int
        target_max_throughput: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                auto_upgrade_policy: Optional[AutoUpgradePolicyResource] = ..., 
                max_throughput: int, 
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


    class azure.mgmt.cosmosdb.models.AzureConnectionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        VPN = "VPN"


    class azure.mgmt.cosmosdb.models.BackupInformation(Model):
        continuous_backup_information: ContinuousBackupInformation

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


    class azure.mgmt.cosmosdb.models.BackupPolicy(Model):
        migration_state: BackupPolicyMigrationState
        type: Union[str, BackupPolicyType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                migration_state: Optional[BackupPolicyMigrationState] = ..., 
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


    class azure.mgmt.cosmosdb.models.BackupPolicyMigrationState(Model):
        start_time: datetime
        status: Union[str, BackupPolicyMigrationStatus]
        target_type: Union[str, BackupPolicyType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                start_time: Optional[datetime] = ..., 
                status: Optional[Union[str, BackupPolicyMigrationStatus]] = ..., 
                target_type: Optional[Union[str, BackupPolicyType]] = ..., 
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


    class azure.mgmt.cosmosdb.models.BackupPolicyMigrationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "Completed"
        FAILED = "Failed"
        INVALID = "Invalid"
        IN_PROGRESS = "InProgress"


    class azure.mgmt.cosmosdb.models.BackupPolicyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTINUOUS = "Continuous"
        PERIODIC = "Periodic"


    class azure.mgmt.cosmosdb.models.BackupStorageRedundancy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GEO = "Geo"
        LOCAL = "Local"
        ZONE = "Zone"


    class azure.mgmt.cosmosdb.models.Capability(Model):
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


    class azure.mgmt.cosmosdb.models.Capacity(Model):
        total_throughput_limit: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                total_throughput_limit: Optional[int] = ..., 
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


    class azure.mgmt.cosmosdb.models.CassandraClusterDataCenterNodeItem(Model):
        address: str
        cassandra_process_status: str
        cpu_usage: float
        disk_free_kb: int
        disk_used_kb: int
        host_id: str
        load: str
        memory_buffers_and_cached_kb: int
        memory_free_kb: int
        memory_total_kb: int
        memory_used_kb: int
        rack: str
        size: int
        state: Union[str, NodeState]
        status: str
        timestamp: str
        tokens: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                address: Optional[str] = ..., 
                cassandra_process_status: Optional[str] = ..., 
                cpu_usage: Optional[float] = ..., 
                disk_free_kb: Optional[int] = ..., 
                disk_used_kb: Optional[int] = ..., 
                host_id: Optional[str] = ..., 
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
                tokens: Optional[list[str]] = ..., 
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


    class azure.mgmt.cosmosdb.models.CassandraClusterPublicStatus(Model):
        connection_errors: list[ConnectionError]
        data_centers: list[CassandraClusterPublicStatusDataCentersItem]
        e_tag: str
        errors: list[CassandraError]
        reaper_status: ManagedCassandraReaperStatus

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                connection_errors: Optional[list[ConnectionError]] = ..., 
                data_centers: Optional[list[CassandraClusterPublicStatusDataCentersItem]] = ..., 
                e_tag: Optional[str] = ..., 
                errors: Optional[list[CassandraError]] = ..., 
                reaper_status: Optional[ManagedCassandraReaperStatus] = ..., 
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


    class azure.mgmt.cosmosdb.models.CassandraClusterPublicStatusDataCentersItem(Model):
        name: str
        nodes: list[CassandraClusterDataCenterNodeItem]
        seed_nodes: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                nodes: Optional[list[CassandraClusterDataCenterNodeItem]] = ..., 
                seed_nodes: Optional[list[str]] = ..., 
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


    class azure.mgmt.cosmosdb.models.CassandraError(Model):
        additional_error_info: str
        code: str
        message: str
        target: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_error_info: Optional[str] = ..., 
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


    class azure.mgmt.cosmosdb.models.CassandraKeyspaceCreateUpdateParameters(ARMResourceProperties):
        id: str
        location: str
        name: str
        options: CreateUpdateOptions
        resource: CassandraKeyspaceResource
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                options: Optional[CreateUpdateOptions] = ..., 
                resource: CassandraKeyspaceResource, 
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


    class azure.mgmt.cosmosdb.models.CassandraKeyspaceGetPropertiesOptions(OptionsResource):
        autoscale_settings: AutoscaleSettings
        throughput: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                autoscale_settings: Optional[AutoscaleSettings] = ..., 
                throughput: Optional[int] = ..., 
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


    class azure.mgmt.cosmosdb.models.CassandraKeyspaceGetPropertiesResource(CassandraKeyspaceResource, ExtendedResourceProperties):
        etag: str
        id: str
        rid: str
        ts: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
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


    class azure.mgmt.cosmosdb.models.CassandraKeyspaceGetResults(ARMResourceProperties):
        id: str
        location: str
        name: str
        options: CassandraKeyspaceGetPropertiesOptions
        resource: CassandraKeyspaceGetPropertiesResource
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                options: Optional[CassandraKeyspaceGetPropertiesOptions] = ..., 
                resource: Optional[CassandraKeyspaceGetPropertiesResource] = ..., 
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


    class azure.mgmt.cosmosdb.models.CassandraKeyspaceListResult(Model):
        value: list[CassandraKeyspaceGetResults]

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


    class azure.mgmt.cosmosdb.models.CassandraKeyspaceResource(Model):
        id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
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


    class azure.mgmt.cosmosdb.models.CassandraPartitionKey(Model):
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


    class azure.mgmt.cosmosdb.models.CassandraSchema(Model):
        cluster_keys: list[ClusterKey]
        columns: list[Column]
        partition_keys: list[CassandraPartitionKey]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cluster_keys: Optional[list[ClusterKey]] = ..., 
                columns: Optional[list[Column]] = ..., 
                partition_keys: Optional[list[CassandraPartitionKey]] = ..., 
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


    class azure.mgmt.cosmosdb.models.CassandraTableCreateUpdateParameters(ARMResourceProperties):
        id: str
        location: str
        name: str
        options: CreateUpdateOptions
        resource: CassandraTableResource
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                options: Optional[CreateUpdateOptions] = ..., 
                resource: CassandraTableResource, 
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


    class azure.mgmt.cosmosdb.models.CassandraTableGetPropertiesOptions(OptionsResource):
        autoscale_settings: AutoscaleSettings
        throughput: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                autoscale_settings: Optional[AutoscaleSettings] = ..., 
                throughput: Optional[int] = ..., 
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


    class azure.mgmt.cosmosdb.models.CassandraTableGetPropertiesResource(CassandraTableResource, ExtendedResourceProperties):
        analytical_storage_ttl: int
        default_ttl: int
        etag: str
        id: str
        rid: str
        schema: CassandraSchema
        ts: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                analytical_storage_ttl: Optional[int] = ..., 
                default_ttl: Optional[int] = ..., 
                id: str, 
                schema: Optional[CassandraSchema] = ..., 
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


    class azure.mgmt.cosmosdb.models.CassandraTableGetResults(ARMResourceProperties):
        id: str
        location: str
        name: str
        options: CassandraTableGetPropertiesOptions
        resource: CassandraTableGetPropertiesResource
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                options: Optional[CassandraTableGetPropertiesOptions] = ..., 
                resource: Optional[CassandraTableGetPropertiesResource] = ..., 
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


    class azure.mgmt.cosmosdb.models.CassandraTableListResult(Model):
        value: list[CassandraTableGetResults]

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


    class azure.mgmt.cosmosdb.models.CassandraTableResource(Model):
        analytical_storage_ttl: int
        default_ttl: int
        id: str
        schema: CassandraSchema

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                analytical_storage_ttl: Optional[int] = ..., 
                default_ttl: Optional[int] = ..., 
                id: str, 
                schema: Optional[CassandraSchema] = ..., 
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


    class azure.mgmt.cosmosdb.models.Certificate(Model):
        pem: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                pem: Optional[str] = ..., 
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


    class azure.mgmt.cosmosdb.models.ClientEncryptionIncludedPath(Model):
        client_encryption_key_id: str
        encryption_algorithm: str
        encryption_type: str
        path: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                client_encryption_key_id: str, 
                encryption_algorithm: str, 
                encryption_type: str, 
                path: str, 
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


    class azure.mgmt.cosmosdb.models.ClientEncryptionKeyCreateUpdateParameters(Model):
        resource: ClientEncryptionKeyResource

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                resource: ClientEncryptionKeyResource, 
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


    class azure.mgmt.cosmosdb.models.ClientEncryptionKeyGetPropertiesResource(ClientEncryptionKeyResource, ExtendedResourceProperties):
        encryption_algorithm: str
        etag: str
        id: str
        key_wrap_metadata: KeyWrapMetadata
        rid: str
        ts: float
        wrapped_data_encryption_key: bytes

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                encryption_algorithm: Optional[str] = ..., 
                id: Optional[str] = ..., 
                key_wrap_metadata: Optional[KeyWrapMetadata] = ..., 
                wrapped_data_encryption_key: Optional[bytes] = ..., 
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


    class azure.mgmt.cosmosdb.models.ClientEncryptionKeyGetResults(ARMProxyResource):
        id: str
        name: str
        resource: ClientEncryptionKeyGetPropertiesResource
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                resource: Optional[ClientEncryptionKeyGetPropertiesResource] = ..., 
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


    class azure.mgmt.cosmosdb.models.ClientEncryptionKeyResource(Model):
        encryption_algorithm: str
        id: str
        key_wrap_metadata: KeyWrapMetadata
        wrapped_data_encryption_key: bytes

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                encryption_algorithm: Optional[str] = ..., 
                id: Optional[str] = ..., 
                key_wrap_metadata: Optional[KeyWrapMetadata] = ..., 
                wrapped_data_encryption_key: Optional[bytes] = ..., 
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


    class azure.mgmt.cosmosdb.models.ClientEncryptionKeysListResult(Model):
        value: list[ClientEncryptionKeyGetResults]

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


    class azure.mgmt.cosmosdb.models.ClientEncryptionPolicy(Model):
        included_paths: list[ClientEncryptionIncludedPath]
        policy_format_version: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                included_paths: list[ClientEncryptionIncludedPath], 
                policy_format_version: int, 
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


    class azure.mgmt.cosmosdb.models.ClusterKey(Model):
        name: str
        order_by: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                order_by: Optional[str] = ..., 
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


    class azure.mgmt.cosmosdb.models.ClusterResource(ManagedCassandraARMResourceProperties):
        id: str
        identity: ManagedCassandraManagedServiceIdentity
        location: str
        name: str
        properties: ClusterResourceProperties
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                identity: Optional[ManagedCassandraManagedServiceIdentity] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[ClusterResourceProperties] = ..., 
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


    class azure.mgmt.cosmosdb.models.ClusterResourceProperties(Model):
        authentication_method: Union[str, AuthenticationMethod]
        azure_connection_method: Union[str, AzureConnectionType]
        cassandra_audit_logging_enabled: bool
        cassandra_version: str
        client_certificates: list[Certificate]
        cluster_name_override: str
        deallocated: bool
        delegated_management_subnet_id: str
        external_gossip_certificates: list[Certificate]
        external_seed_nodes: list[SeedNode]
        gossip_certificates: list[Certificate]
        hours_between_backups: int
        initial_cassandra_admin_password: str
        private_link_resource_id: str
        prometheus_endpoint: SeedNode
        provision_error: CassandraError
        provisioning_state: Union[str, ManagedCassandraProvisioningState]
        repair_enabled: bool
        restore_from_backup_id: str
        seed_nodes: list[SeedNode]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                authentication_method: Optional[Union[str, AuthenticationMethod]] = ..., 
                azure_connection_method: Optional[Union[str, AzureConnectionType]] = ..., 
                cassandra_audit_logging_enabled: Optional[bool] = ..., 
                cassandra_version: Optional[str] = ..., 
                client_certificates: Optional[list[Certificate]] = ..., 
                cluster_name_override: Optional[str] = ..., 
                deallocated: Optional[bool] = ..., 
                delegated_management_subnet_id: Optional[str] = ..., 
                external_gossip_certificates: Optional[list[Certificate]] = ..., 
                external_seed_nodes: Optional[list[SeedNode]] = ..., 
                hours_between_backups: Optional[int] = ..., 
                initial_cassandra_admin_password: Optional[str] = ..., 
                prometheus_endpoint: Optional[SeedNode] = ..., 
                provision_error: Optional[CassandraError] = ..., 
                provisioning_state: Optional[Union[str, ManagedCassandraProvisioningState]] = ..., 
                repair_enabled: Optional[bool] = ..., 
                restore_from_backup_id: Optional[str] = ..., 
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


    class azure.mgmt.cosmosdb.models.Column(Model):
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
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


    class azure.mgmt.cosmosdb.models.CommandOutput(Model):
        command_output: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                command_output: Optional[str] = ..., 
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


    class azure.mgmt.cosmosdb.models.CommandPostBody(Model):
        arguments: dict[str, str]
        cassandra_stop_start: bool
        command: str
        host: str
        readwrite: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                arguments: Optional[dict[str, str]] = ..., 
                cassandra_stop_start: Optional[bool] = ..., 
                command: str, 
                host: str, 
                readwrite: Optional[bool] = ..., 
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


    class azure.mgmt.cosmosdb.models.CompositePath(Model):
        order: Union[str, CompositePathSortOrder]
        path: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                order: Optional[Union[str, CompositePathSortOrder]] = ..., 
                path: Optional[str] = ..., 
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


    class azure.mgmt.cosmosdb.models.CompositePathSortOrder(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASCENDING = "ascending"
        DESCENDING = "descending"


    class azure.mgmt.cosmosdb.models.ComputedProperty(Model):
        name: str
        query: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                query: Optional[str] = ..., 
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


    class azure.mgmt.cosmosdb.models.ConflictResolutionMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM = "Custom"
        LAST_WRITER_WINS = "LastWriterWins"


    class azure.mgmt.cosmosdb.models.ConflictResolutionPolicy(Model):
        conflict_resolution_path: str
        conflict_resolution_procedure: str
        mode: Union[str, ConflictResolutionMode]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                conflict_resolution_path: Optional[str] = ..., 
                conflict_resolution_procedure: Optional[str] = ..., 
                mode: Union[str, ConflictResolutionMode] = "LastWriterWins", 
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


    class azure.mgmt.cosmosdb.models.ConnectionError(Model):
        connection_state: Union[str, ConnectionState]
        exception: str
        i_p_from: str
        i_p_to: str
        port: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                connection_state: Optional[Union[str, ConnectionState]] = ..., 
                exception: Optional[str] = ..., 
                i_p_from: Optional[str] = ..., 
                i_p_to: Optional[str] = ..., 
                port: Optional[int] = ..., 
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


    class azure.mgmt.cosmosdb.models.ConnectionState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DATACENTER_TO_DATACENTER_NETWORK_ERROR = "DatacenterToDatacenterNetworkError"
        INTERNAL_ERROR = "InternalError"
        INTERNAL_OPERATOR_TO_DATA_CENTER_CERTIFICATE_ERROR = "InternalOperatorToDataCenterCertificateError"
        OK = "OK"
        OPERATOR_TO_DATA_CENTER_NETWORK_ERROR = "OperatorToDataCenterNetworkError"
        UNKNOWN = "Unknown"


    class azure.mgmt.cosmosdb.models.ConnectorOffer(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SMALL = "Small"


    class azure.mgmt.cosmosdb.models.ConsistencyPolicy(Model):
        default_consistency_level: Union[str, DefaultConsistencyLevel]
        max_interval_in_seconds: int
        max_staleness_prefix: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                default_consistency_level: Union[str, DefaultConsistencyLevel], 
                max_interval_in_seconds: Optional[int] = ..., 
                max_staleness_prefix: Optional[int] = ..., 
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


    class azure.mgmt.cosmosdb.models.ContainerPartitionKey(Model):
        kind: Union[str, PartitionKind]
        paths: list[str]
        system_key: bool
        version: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                kind: Union[str, PartitionKind] = "Hash", 
                paths: Optional[list[str]] = ..., 
                version: Optional[int] = ..., 
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


    class azure.mgmt.cosmosdb.models.ContinuousBackupInformation(Model):
        latest_restorable_timestamp: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                latest_restorable_timestamp: Optional[str] = ..., 
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


    class azure.mgmt.cosmosdb.models.ContinuousBackupRestoreLocation(Model):
        location: str

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


    class azure.mgmt.cosmosdb.models.ContinuousModeBackupPolicy(BackupPolicy):
        continuous_mode_properties: ContinuousModeProperties
        migration_state: BackupPolicyMigrationState
        type: Union[str, BackupPolicyType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                continuous_mode_properties: Optional[ContinuousModeProperties] = ..., 
                migration_state: Optional[BackupPolicyMigrationState] = ..., 
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


    class azure.mgmt.cosmosdb.models.ContinuousModeProperties(Model):
        tier: Union[str, ContinuousTier]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                tier: Optional[Union[str, ContinuousTier]] = ..., 
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


    class azure.mgmt.cosmosdb.models.ContinuousTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTINUOUS30_DAYS = "Continuous30Days"
        CONTINUOUS7_DAYS = "Continuous7Days"


    class azure.mgmt.cosmosdb.models.CorsPolicy(Model):
        allowed_headers: str
        allowed_methods: str
        allowed_origins: str
        exposed_headers: str
        max_age_in_seconds: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                allowed_headers: Optional[str] = ..., 
                allowed_methods: Optional[str] = ..., 
                allowed_origins: str, 
                exposed_headers: Optional[str] = ..., 
                max_age_in_seconds: Optional[int] = ..., 
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


    class azure.mgmt.cosmosdb.models.CreateMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "Default"
        RESTORE = "Restore"


    class azure.mgmt.cosmosdb.models.CreateUpdateOptions(Model):
        autoscale_settings: AutoscaleSettings
        throughput: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                autoscale_settings: Optional[AutoscaleSettings] = ..., 
                throughput: Optional[int] = ..., 
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


    class azure.mgmt.cosmosdb.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.cosmosdb.models.DataCenterResource(ARMProxyResource):
        id: str
        name: str
        properties: DataCenterResourceProperties
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[DataCenterResourceProperties] = ..., 
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


    class azure.mgmt.cosmosdb.models.DataCenterResourceProperties(Model):
        authentication_method_ldap_properties: AuthenticationMethodLdapProperties
        availability_zone: bool
        backup_storage_customer_key_uri: str
        base64_encoded_cassandra_yaml_fragment: str
        data_center_location: str
        deallocated: bool
        delegated_subnet_id: str
        disk_capacity: int
        disk_sku: str
        managed_disk_customer_key_uri: str
        node_count: int
        private_endpoint_ip_address: str
        provision_error: CassandraError
        provisioning_state: Union[str, ManagedCassandraProvisioningState]
        seed_nodes: list[SeedNode]
        sku: str

        def __eq__(self, other: Any) -> bool: ...

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
                sku: Optional[str] = ..., 
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


    class azure.mgmt.cosmosdb.models.DataTransferRegionalServiceResource(RegionalServiceResource):
        location: str
        name: str
        status: Union[str, ServiceStatus]

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


    class azure.mgmt.cosmosdb.models.DataTransferServiceResource(Model):
        properties: DataTransferServiceResourceProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[DataTransferServiceResourceProperties] = ..., 
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


    class azure.mgmt.cosmosdb.models.DataTransferServiceResourceCreateUpdateProperties(ServiceResourceCreateUpdateProperties):
        instance_count: int
        instance_size: Union[str, ServiceSize]
        service_type: Union[str, ServiceType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                instance_count: Optional[int] = ..., 
                instance_size: Optional[Union[str, ServiceSize]] = ..., 
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


    class azure.mgmt.cosmosdb.models.DataTransferServiceResourceProperties(ServiceResourceProperties):
        additional_properties: dict[str, any]
        creation_time: datetime
        instance_count: int
        instance_size: Union[str, ServiceSize]
        locations: list[DataTransferRegionalServiceResource]
        service_type: Union[str, ServiceType]
        status: Union[str, ServiceStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_properties: Optional[dict[str, Any]] = ..., 
                instance_count: Optional[int] = ..., 
                instance_size: Optional[Union[str, ServiceSize]] = ..., 
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


    class azure.mgmt.cosmosdb.models.DataType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LINE_STRING = "LineString"
        MULTI_POLYGON = "MultiPolygon"
        NUMBER = "Number"
        POINT = "Point"
        POLYGON = "Polygon"
        STRING = "String"


    class azure.mgmt.cosmosdb.models.DatabaseAccountConnectionString(Model):
        connection_string: str
        description: str
        key_kind: Union[str, Kind]
        type: Union[str, Type]

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


    class azure.mgmt.cosmosdb.models.DatabaseAccountCreateUpdateParameters(ARMResourceProperties):
        analytical_storage_configuration: AnalyticalStorageConfiguration
        api_properties: ApiProperties
        backup_policy: BackupPolicy
        capabilities: list[Capability]
        capacity: Capacity
        connector_offer: Union[str, ConnectorOffer]
        consistency_policy: ConsistencyPolicy
        cors: list[CorsPolicy]
        create_mode: Union[str, CreateMode]
        customer_managed_key_status: str
        database_account_offer_type: str = "Standard"
        default_identity: str
        default_priority_level: Union[str, DefaultPriorityLevel]
        disable_key_based_metadata_write_access: bool
        disable_local_auth: bool
        enable_analytical_storage: bool
        enable_automatic_failover: bool
        enable_burst_capacity: bool
        enable_cassandra_connector: bool
        enable_free_tier: bool
        enable_multiple_write_locations: bool
        enable_partition_merge: bool
        enable_per_region_per_partition_autoscale: bool
        enable_priority_based_execution: bool
        id: str
        identity: ManagedServiceIdentity
        ip_rules: list[IpAddressOrRange]
        is_virtual_network_filter_enabled: bool
        key_vault_key_uri: str
        keys_metadata: DatabaseAccountKeysMetadata
        kind: Union[str, DatabaseAccountKind]
        location: str
        locations: list[Location]
        minimal_tls_version: Union[str, MinimalTlsVersion]
        name: str
        network_acl_bypass: Union[str, NetworkAclBypass]
        network_acl_bypass_resource_ids: list[str]
        public_network_access: Union[str, PublicNetworkAccess]
        restore_parameters: RestoreParameters
        tags: dict[str, str]
        type: str
        virtual_network_rules: list[VirtualNetworkRule]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                analytical_storage_configuration: Optional[AnalyticalStorageConfiguration] = ..., 
                api_properties: Optional[ApiProperties] = ..., 
                backup_policy: Optional[BackupPolicy] = ..., 
                capabilities: Optional[list[Capability]] = ..., 
                capacity: Optional[Capacity] = ..., 
                connector_offer: Optional[Union[str, ConnectorOffer]] = ..., 
                consistency_policy: Optional[ConsistencyPolicy] = ..., 
                cors: Optional[list[CorsPolicy]] = ..., 
                create_mode: Union[str, CreateMode] = "Default", 
                customer_managed_key_status: Optional[str] = ..., 
                default_identity: Optional[str] = ..., 
                default_priority_level: Optional[Union[str, DefaultPriorityLevel]] = ..., 
                disable_key_based_metadata_write_access: Optional[bool] = ..., 
                disable_local_auth: Optional[bool] = ..., 
                enable_analytical_storage: Optional[bool] = ..., 
                enable_automatic_failover: Optional[bool] = ..., 
                enable_burst_capacity: Optional[bool] = ..., 
                enable_cassandra_connector: Optional[bool] = ..., 
                enable_free_tier: Optional[bool] = ..., 
                enable_multiple_write_locations: Optional[bool] = ..., 
                enable_partition_merge: Optional[bool] = ..., 
                enable_per_region_per_partition_autoscale: Optional[bool] = ..., 
                enable_priority_based_execution: Optional[bool] = ..., 
                identity: Optional[ManagedServiceIdentity] = ..., 
                ip_rules: Optional[list[IpAddressOrRange]] = ..., 
                is_virtual_network_filter_enabled: Optional[bool] = ..., 
                key_vault_key_uri: Optional[str] = ..., 
                kind: Optional[Union[str, DatabaseAccountKind]] = ..., 
                location: Optional[str] = ..., 
                locations: list[Location], 
                minimal_tls_version: Optional[Union[str, MinimalTlsVersion]] = ..., 
                network_acl_bypass: Optional[Union[str, NetworkAclBypass]] = ..., 
                network_acl_bypass_resource_ids: Optional[list[str]] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                restore_parameters: Optional[RestoreParameters] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                virtual_network_rules: Optional[list[VirtualNetworkRule]] = ..., 
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


    class azure.mgmt.cosmosdb.models.DatabaseAccountGetResults(ARMResourceProperties):
        analytical_storage_configuration: AnalyticalStorageConfiguration
        api_properties: ApiProperties
        backup_policy: BackupPolicy
        capabilities: list[Capability]
        capacity: Capacity
        connector_offer: Union[str, ConnectorOffer]
        consistency_policy: ConsistencyPolicy
        cors: list[CorsPolicy]
        create_mode: Union[str, CreateMode]
        customer_managed_key_status: str
        database_account_offer_type: str
        default_identity: str
        default_priority_level: Union[str, DefaultPriorityLevel]
        disable_key_based_metadata_write_access: bool
        disable_local_auth: bool
        document_endpoint: str
        enable_analytical_storage: bool
        enable_automatic_failover: bool
        enable_burst_capacity: bool
        enable_cassandra_connector: bool
        enable_free_tier: bool
        enable_multiple_write_locations: bool
        enable_partition_merge: bool
        enable_per_region_per_partition_autoscale: bool
        enable_priority_based_execution: bool
        failover_policies: list[FailoverPolicy]
        id: str
        identity: ManagedServiceIdentity
        instance_id: str
        ip_rules: list[IpAddressOrRange]
        is_virtual_network_filter_enabled: bool
        key_vault_key_uri: str
        key_vault_key_uri_version: str
        keys_metadata: DatabaseAccountKeysMetadata
        kind: Union[str, DatabaseAccountKind]
        location: str
        locations: list[Location]
        minimal_tls_version: Union[str, MinimalTlsVersion]
        name: str
        network_acl_bypass: Union[str, NetworkAclBypass]
        network_acl_bypass_resource_ids: list[str]
        private_endpoint_connections: list[PrivateEndpointConnection]
        provisioning_state: str
        public_network_access: Union[str, PublicNetworkAccess]
        read_locations: list[Location]
        restore_parameters: RestoreParameters
        system_data: SystemData
        tags: dict[str, str]
        type: str
        virtual_network_rules: list[VirtualNetworkRule]
        write_locations: list[Location]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                analytical_storage_configuration: Optional[AnalyticalStorageConfiguration] = ..., 
                api_properties: Optional[ApiProperties] = ..., 
                backup_policy: Optional[BackupPolicy] = ..., 
                capabilities: Optional[list[Capability]] = ..., 
                capacity: Optional[Capacity] = ..., 
                connector_offer: Optional[Union[str, ConnectorOffer]] = ..., 
                consistency_policy: Optional[ConsistencyPolicy] = ..., 
                cors: Optional[list[CorsPolicy]] = ..., 
                create_mode: Union[str, CreateMode] = "Default", 
                customer_managed_key_status: Optional[str] = ..., 
                default_identity: Optional[str] = ..., 
                default_priority_level: Optional[Union[str, DefaultPriorityLevel]] = ..., 
                disable_key_based_metadata_write_access: Optional[bool] = ..., 
                disable_local_auth: Optional[bool] = ..., 
                enable_analytical_storage: Optional[bool] = ..., 
                enable_automatic_failover: Optional[bool] = ..., 
                enable_burst_capacity: Optional[bool] = ..., 
                enable_cassandra_connector: Optional[bool] = ..., 
                enable_free_tier: Optional[bool] = ..., 
                enable_multiple_write_locations: Optional[bool] = ..., 
                enable_partition_merge: Optional[bool] = ..., 
                enable_per_region_per_partition_autoscale: Optional[bool] = ..., 
                enable_priority_based_execution: Optional[bool] = ..., 
                identity: Optional[ManagedServiceIdentity] = ..., 
                ip_rules: Optional[list[IpAddressOrRange]] = ..., 
                is_virtual_network_filter_enabled: Optional[bool] = ..., 
                key_vault_key_uri: Optional[str] = ..., 
                kind: Optional[Union[str, DatabaseAccountKind]] = ..., 
                location: Optional[str] = ..., 
                minimal_tls_version: Optional[Union[str, MinimalTlsVersion]] = ..., 
                network_acl_bypass: Optional[Union[str, NetworkAclBypass]] = ..., 
                network_acl_bypass_resource_ids: Optional[list[str]] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                restore_parameters: Optional[RestoreParameters] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                virtual_network_rules: Optional[list[VirtualNetworkRule]] = ..., 
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


    class azure.mgmt.cosmosdb.models.DatabaseAccountKeysMetadata(Model):
        primary_master_key: AccountKeyMetadata
        primary_readonly_master_key: AccountKeyMetadata
        secondary_master_key: AccountKeyMetadata
        secondary_readonly_master_key: AccountKeyMetadata

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


    class azure.mgmt.cosmosdb.models.DatabaseAccountKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GLOBAL_DOCUMENT_DB = "GlobalDocumentDB"
        MONGO_DB = "MongoDB"
        PARSE = "Parse"


    class azure.mgmt.cosmosdb.models.DatabaseAccountListConnectionStringsResult(Model):
        connection_strings: list[DatabaseAccountConnectionString]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                connection_strings: Optional[list[DatabaseAccountConnectionString]] = ..., 
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


    class azure.mgmt.cosmosdb.models.DatabaseAccountListKeysResult(DatabaseAccountListReadOnlyKeysResult):
        primary_master_key: str
        primary_readonly_master_key: str
        secondary_master_key: str
        secondary_readonly_master_key: str

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


    class azure.mgmt.cosmosdb.models.DatabaseAccountListReadOnlyKeysResult(Model):
        primary_readonly_master_key: str
        secondary_readonly_master_key: str

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


    class azure.mgmt.cosmosdb.models.DatabaseAccountRegenerateKeyParameters(Model):
        key_kind: Union[str, KeyKind]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key_kind: Union[str, KeyKind], 
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


    class azure.mgmt.cosmosdb.models.DatabaseAccountUpdateParameters(Model):
        analytical_storage_configuration: AnalyticalStorageConfiguration
        api_properties: ApiProperties
        backup_policy: BackupPolicy
        capabilities: list[Capability]
        capacity: Capacity
        connector_offer: Union[str, ConnectorOffer]
        consistency_policy: ConsistencyPolicy
        cors: list[CorsPolicy]
        customer_managed_key_status: str
        default_identity: str
        default_priority_level: Union[str, DefaultPriorityLevel]
        disable_key_based_metadata_write_access: bool
        disable_local_auth: bool
        enable_analytical_storage: bool
        enable_automatic_failover: bool
        enable_burst_capacity: bool
        enable_cassandra_connector: bool
        enable_free_tier: bool
        enable_multiple_write_locations: bool
        enable_partition_merge: bool
        enable_per_region_per_partition_autoscale: bool
        enable_priority_based_execution: bool
        identity: ManagedServiceIdentity
        ip_rules: list[IpAddressOrRange]
        is_virtual_network_filter_enabled: bool
        key_vault_key_uri: str
        keys_metadata: DatabaseAccountKeysMetadata
        location: str
        locations: list[Location]
        minimal_tls_version: Union[str, MinimalTlsVersion]
        network_acl_bypass: Union[str, NetworkAclBypass]
        network_acl_bypass_resource_ids: list[str]
        public_network_access: Union[str, PublicNetworkAccess]
        tags: dict[str, str]
        virtual_network_rules: list[VirtualNetworkRule]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                analytical_storage_configuration: Optional[AnalyticalStorageConfiguration] = ..., 
                api_properties: Optional[ApiProperties] = ..., 
                backup_policy: Optional[BackupPolicy] = ..., 
                capabilities: Optional[list[Capability]] = ..., 
                capacity: Optional[Capacity] = ..., 
                connector_offer: Optional[Union[str, ConnectorOffer]] = ..., 
                consistency_policy: Optional[ConsistencyPolicy] = ..., 
                cors: Optional[list[CorsPolicy]] = ..., 
                customer_managed_key_status: Optional[str] = ..., 
                default_identity: Optional[str] = ..., 
                default_priority_level: Optional[Union[str, DefaultPriorityLevel]] = ..., 
                disable_key_based_metadata_write_access: Optional[bool] = ..., 
                disable_local_auth: Optional[bool] = ..., 
                enable_analytical_storage: Optional[bool] = ..., 
                enable_automatic_failover: Optional[bool] = ..., 
                enable_burst_capacity: Optional[bool] = ..., 
                enable_cassandra_connector: Optional[bool] = ..., 
                enable_free_tier: Optional[bool] = ..., 
                enable_multiple_write_locations: Optional[bool] = ..., 
                enable_partition_merge: Optional[bool] = ..., 
                enable_per_region_per_partition_autoscale: Optional[bool] = ..., 
                enable_priority_based_execution: Optional[bool] = ..., 
                identity: Optional[ManagedServiceIdentity] = ..., 
                ip_rules: Optional[list[IpAddressOrRange]] = ..., 
                is_virtual_network_filter_enabled: Optional[bool] = ..., 
                key_vault_key_uri: Optional[str] = ..., 
                location: Optional[str] = ..., 
                locations: Optional[list[Location]] = ..., 
                minimal_tls_version: Optional[Union[str, MinimalTlsVersion]] = ..., 
                network_acl_bypass: Optional[Union[str, NetworkAclBypass]] = ..., 
                network_acl_bypass_resource_ids: Optional[list[str]] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                virtual_network_rules: Optional[list[VirtualNetworkRule]] = ..., 
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


    class azure.mgmt.cosmosdb.models.DatabaseAccountsListResult(Model):
        value: list[DatabaseAccountGetResults]

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


    class azure.mgmt.cosmosdb.models.DatabaseRestoreResource(Model):
        collection_names: list[str]
        database_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                collection_names: Optional[list[str]] = ..., 
                database_name: Optional[str] = ..., 
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


    class azure.mgmt.cosmosdb.models.DistanceFunction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COSINE = "cosine"
        DOTPRODUCT = "dotproduct"
        EUCLIDEAN = "euclidean"


    class azure.mgmt.cosmosdb.models.ErrorAdditionalInfo(Model):
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


    class azure.mgmt.cosmosdb.models.ErrorDetail(Model):
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
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.cosmosdb.models.ErrorDetailAutoGenerated(Model):
        additional_info: list[ErrorAdditionalInfo]
        code: str
        details: list[ErrorDetailAutoGenerated]
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


    class azure.mgmt.cosmosdb.models.ErrorResponse(Model):
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


    class azure.mgmt.cosmosdb.models.ErrorResponseAutoGenerated(Model):
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
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.cosmosdb.models.ErrorResponseAutoGenerated2(Model):
        error: ErrorDetailAutoGenerated

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetailAutoGenerated] = ..., 
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


    class azure.mgmt.cosmosdb.models.ExcludedPath(Model):
        path: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                path: Optional[str] = ..., 
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


    class azure.mgmt.cosmosdb.models.ExtendedResourceProperties(Model):
        etag: str
        rid: str
        ts: float

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


    class azure.mgmt.cosmosdb.models.FailoverPolicies(Model):
        failover_policies: list[FailoverPolicy]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                failover_policies: list[FailoverPolicy], 
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


    class azure.mgmt.cosmosdb.models.FailoverPolicy(Model):
        failover_priority: int
        id: str
        location_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                failover_priority: Optional[int] = ..., 
                location_name: Optional[str] = ..., 
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


    class azure.mgmt.cosmosdb.models.FleetListResult(Model):
        next_link: str
        value: list[FleetResource]

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


    class azure.mgmt.cosmosdb.models.FleetResource(TrackedResource):
        id: str
        location: str
        name: str
        provisioning_state: Union[str, Status]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: str, 
                provisioning_state: Optional[Union[str, Status]] = ..., 
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


    class azure.mgmt.cosmosdb.models.FleetResourceUpdate(Model):
        provisioning_state: Union[str, Status]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                provisioning_state: Optional[Union[str, Status]] = ..., 
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


    class azure.mgmt.cosmosdb.models.FleetspaceAccountListResult(Model):
        next_link: str
        value: list[FleetspaceAccountResource]

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


    class azure.mgmt.cosmosdb.models.FleetspaceAccountPropertiesGlobalDatabaseAccountProperties(Model):
        arm_location: str
        resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                arm_location: Optional[str] = ..., 
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


    class azure.mgmt.cosmosdb.models.FleetspaceAccountResource(ProxyResourceAutoGenerated):
        global_database_account_properties: FleetspaceAccountPropertiesGlobalDatabaseAccountProperties
        id: str
        name: str
        provisioning_state: Union[str, Status]
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                global_database_account_properties: Optional[FleetspaceAccountPropertiesGlobalDatabaseAccountProperties] = ..., 
                provisioning_state: Optional[Union[str, Status]] = ..., 
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


    class azure.mgmt.cosmosdb.models.FleetspaceListResult(Model):
        next_link: str
        value: list[FleetspaceResource]

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


    class azure.mgmt.cosmosdb.models.FleetspacePropertiesFleetspaceApiKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NO_SQL = "NoSQL"


    class azure.mgmt.cosmosdb.models.FleetspacePropertiesServiceTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BUSINESS_CRITICAL = "BusinessCritical"
        GENERAL_PURPOSE = "GeneralPurpose"


    class azure.mgmt.cosmosdb.models.FleetspacePropertiesThroughputPoolConfiguration(Model):
        max_throughput: int
        min_throughput: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                max_throughput: Optional[int] = ..., 
                min_throughput: Optional[int] = ..., 
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


    class azure.mgmt.cosmosdb.models.FleetspaceResource(ProxyResourceAutoGenerated):
        data_regions: list[str]
        fleetspace_api_kind: Union[str, FleetspacePropertiesFleetspaceApiKind]
        id: str
        name: str
        provisioning_state: Union[str, Status]
        service_tier: Union[str, FleetspacePropertiesServiceTier]
        system_data: SystemData
        throughput_pool_configuration: FleetspacePropertiesThroughputPoolConfiguration
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                data_regions: Optional[list[str]] = ..., 
                fleetspace_api_kind: Optional[Union[str, FleetspacePropertiesFleetspaceApiKind]] = ..., 
                provisioning_state: Optional[Union[str, Status]] = ..., 
                service_tier: Optional[Union[str, FleetspacePropertiesServiceTier]] = ..., 
                throughput_pool_configuration: Optional[FleetspacePropertiesThroughputPoolConfiguration] = ..., 
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


    class azure.mgmt.cosmosdb.models.FleetspaceUpdate(Model):
        data_regions: list[str]
        fleetspace_api_kind: Union[str, FleetspacePropertiesFleetspaceApiKind]
        provisioning_state: Union[str, Status]
        service_tier: Union[str, FleetspacePropertiesServiceTier]
        throughput_pool_configuration: FleetspacePropertiesThroughputPoolConfiguration

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                data_regions: Optional[list[str]] = ..., 
                fleetspace_api_kind: Optional[Union[str, FleetspacePropertiesFleetspaceApiKind]] = ..., 
                provisioning_state: Optional[Union[str, Status]] = ..., 
                service_tier: Optional[Union[str, FleetspacePropertiesServiceTier]] = ..., 
                throughput_pool_configuration: Optional[FleetspacePropertiesThroughputPoolConfiguration] = ..., 
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


    class azure.mgmt.cosmosdb.models.FullTextIndexPath(Model):
        path: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                path: str, 
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


    class azure.mgmt.cosmosdb.models.FullTextPath(Model):
        language: str
        path: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                language: Optional[str] = ..., 
                path: str, 
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


    class azure.mgmt.cosmosdb.models.FullTextPolicy(Model):
        default_language: str
        full_text_paths: list[FullTextPath]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                default_language: Optional[str] = ..., 
                full_text_paths: Optional[list[FullTextPath]] = ..., 
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


    class azure.mgmt.cosmosdb.models.GraphAPIComputeRegionalServiceResource(RegionalServiceResource):
        graph_api_compute_endpoint: str
        location: str
        name: str
        status: Union[str, ServiceStatus]

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


    class azure.mgmt.cosmosdb.models.GraphAPIComputeServiceResource(Model):
        properties: GraphAPIComputeServiceResourceProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[GraphAPIComputeServiceResourceProperties] = ..., 
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


    class azure.mgmt.cosmosdb.models.GraphAPIComputeServiceResourceCreateUpdateProperties(ServiceResourceCreateUpdateProperties):
        instance_count: int
        instance_size: Union[str, ServiceSize]
        service_type: Union[str, ServiceType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                instance_count: Optional[int] = ..., 
                instance_size: Optional[Union[str, ServiceSize]] = ..., 
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


    class azure.mgmt.cosmosdb.models.GraphAPIComputeServiceResourceProperties(ServiceResourceProperties):
        additional_properties: dict[str, any]
        creation_time: datetime
        graph_api_compute_endpoint: str
        instance_count: int
        instance_size: Union[str, ServiceSize]
        locations: list[GraphAPIComputeRegionalServiceResource]
        service_type: Union[str, ServiceType]
        status: Union[str, ServiceStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_properties: Optional[dict[str, Any]] = ..., 
                graph_api_compute_endpoint: Optional[str] = ..., 
                instance_count: Optional[int] = ..., 
                instance_size: Optional[Union[str, ServiceSize]] = ..., 
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


    class azure.mgmt.cosmosdb.models.GremlinDatabaseCreateUpdateParameters(ARMResourceProperties):
        id: str
        location: str
        name: str
        options: CreateUpdateOptions
        resource: GremlinDatabaseResource
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                options: Optional[CreateUpdateOptions] = ..., 
                resource: GremlinDatabaseResource, 
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


    class azure.mgmt.cosmosdb.models.GremlinDatabaseGetPropertiesOptions(OptionsResource):
        autoscale_settings: AutoscaleSettings
        throughput: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                autoscale_settings: Optional[AutoscaleSettings] = ..., 
                throughput: Optional[int] = ..., 
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


    class azure.mgmt.cosmosdb.models.GremlinDatabaseGetPropertiesResource(GremlinDatabaseResource, ExtendedResourceProperties):
        create_mode: Union[str, CreateMode]
        etag: str
        id: str
        restore_parameters: ResourceRestoreParameters
        rid: str
        ts: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                create_mode: Union[str, CreateMode] = "Default", 
                id: str, 
                restore_parameters: Optional[ResourceRestoreParameters] = ..., 
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


    class azure.mgmt.cosmosdb.models.GremlinDatabaseGetResults(ARMResourceProperties):
        id: str
        location: str
        name: str
        options: GremlinDatabaseGetPropertiesOptions
        resource: GremlinDatabaseGetPropertiesResource
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                options: Optional[GremlinDatabaseGetPropertiesOptions] = ..., 
                resource: Optional[GremlinDatabaseGetPropertiesResource] = ..., 
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


    class azure.mgmt.cosmosdb.models.GremlinDatabaseListResult(Model):
        value: list[GremlinDatabaseGetResults]

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


    class azure.mgmt.cosmosdb.models.GremlinDatabaseResource(Model):
        create_mode: Union[str, CreateMode]
        id: str
        restore_parameters: ResourceRestoreParameters

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                create_mode: Union[str, CreateMode] = "Default", 
                id: str, 
                restore_parameters: Optional[ResourceRestoreParameters] = ..., 
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


    class azure.mgmt.cosmosdb.models.GremlinDatabaseRestoreResource(Model):
        database_name: str
        graph_names: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                database_name: Optional[str] = ..., 
                graph_names: Optional[list[str]] = ..., 
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


    class azure.mgmt.cosmosdb.models.GremlinGraphCreateUpdateParameters(ARMResourceProperties):
        id: str
        location: str
        name: str
        options: CreateUpdateOptions
        resource: GremlinGraphResource
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                options: Optional[CreateUpdateOptions] = ..., 
                resource: GremlinGraphResource, 
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


    class azure.mgmt.cosmosdb.models.GremlinGraphGetPropertiesOptions(OptionsResource):
        autoscale_settings: AutoscaleSettings
        throughput: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                autoscale_settings: Optional[AutoscaleSettings] = ..., 
                throughput: Optional[int] = ..., 
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


    class azure.mgmt.cosmosdb.models.GremlinGraphGetPropertiesResource(GremlinGraphResource, ExtendedResourceProperties):
        analytical_storage_ttl: int
        conflict_resolution_policy: ConflictResolutionPolicy
        create_mode: Union[str, CreateMode]
        default_ttl: int
        etag: str
        id: str
        indexing_policy: IndexingPolicy
        partition_key: ContainerPartitionKey
        restore_parameters: ResourceRestoreParameters
        rid: str
        ts: float
        unique_key_policy: UniqueKeyPolicy

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                analytical_storage_ttl: Optional[int] = ..., 
                conflict_resolution_policy: Optional[ConflictResolutionPolicy] = ..., 
                create_mode: Union[str, CreateMode] = "Default", 
                default_ttl: Optional[int] = ..., 
                id: str, 
                indexing_policy: Optional[IndexingPolicy] = ..., 
                partition_key: Optional[ContainerPartitionKey] = ..., 
                restore_parameters: Optional[ResourceRestoreParameters] = ..., 
                unique_key_policy: Optional[UniqueKeyPolicy] = ..., 
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


    class azure.mgmt.cosmosdb.models.GremlinGraphGetResults(ARMResourceProperties):
        id: str
        location: str
        name: str
        options: GremlinGraphGetPropertiesOptions
        resource: GremlinGraphGetPropertiesResource
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                options: Optional[GremlinGraphGetPropertiesOptions] = ..., 
                resource: Optional[GremlinGraphGetPropertiesResource] = ..., 
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


    class azure.mgmt.cosmosdb.models.GremlinGraphListResult(Model):
        value: list[GremlinGraphGetResults]

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


    class azure.mgmt.cosmosdb.models.GremlinGraphResource(Model):
        analytical_storage_ttl: int
        conflict_resolution_policy: ConflictResolutionPolicy
        create_mode: Union[str, CreateMode]
        default_ttl: int
        id: str
        indexing_policy: IndexingPolicy
        partition_key: ContainerPartitionKey
        restore_parameters: ResourceRestoreParameters
        unique_key_policy: UniqueKeyPolicy

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                analytical_storage_ttl: Optional[int] = ..., 
                conflict_resolution_policy: Optional[ConflictResolutionPolicy] = ..., 
                create_mode: Union[str, CreateMode] = "Default", 
                default_ttl: Optional[int] = ..., 
                id: str, 
                indexing_policy: Optional[IndexingPolicy] = ..., 
                partition_key: Optional[ContainerPartitionKey] = ..., 
                restore_parameters: Optional[ResourceRestoreParameters] = ..., 
                unique_key_policy: Optional[UniqueKeyPolicy] = ..., 
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


    class azure.mgmt.cosmosdb.models.IncludedPath(Model):
        indexes: list[Indexes]
        path: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                indexes: Optional[list[Indexes]] = ..., 
                path: Optional[str] = ..., 
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


    class azure.mgmt.cosmosdb.models.IndexKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HASH = "Hash"
        RANGE = "Range"
        SPATIAL = "Spatial"


    class azure.mgmt.cosmosdb.models.Indexes(Model):
        data_type: Union[str, DataType]
        kind: Union[str, IndexKind]
        precision: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                data_type: Union[str, DataType] = "String", 
                kind: Union[str, IndexKind] = "Hash", 
                precision: Optional[int] = ..., 
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


    class azure.mgmt.cosmosdb.models.IndexingMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONSISTENT = "consistent"
        LAZY = "lazy"
        NONE = "none"


    class azure.mgmt.cosmosdb.models.IndexingPolicy(Model):
        automatic: bool
        composite_indexes: list[list[CompositePath]]
        excluded_paths: list[ExcludedPath]
        full_text_indexes: list[FullTextIndexPath]
        included_paths: list[IncludedPath]
        indexing_mode: Union[str, IndexingMode]
        spatial_indexes: list[SpatialSpec]
        vector_indexes: list[VectorIndex]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                automatic: Optional[bool] = ..., 
                composite_indexes: Optional[list[list[CompositePath]]] = ..., 
                excluded_paths: Optional[list[ExcludedPath]] = ..., 
                full_text_indexes: Optional[list[FullTextIndexPath]] = ..., 
                included_paths: Optional[list[IncludedPath]] = ..., 
                indexing_mode: Union[str, IndexingMode] = "consistent", 
                spatial_indexes: Optional[list[SpatialSpec]] = ..., 
                vector_indexes: Optional[list[VectorIndex]] = ..., 
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


    class azure.mgmt.cosmosdb.models.IpAddressOrRange(Model):
        ip_address_or_range: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                ip_address_or_range: Optional[str] = ..., 
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


    class azure.mgmt.cosmosdb.models.KeyKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRIMARY = "primary"
        PRIMARY_READONLY = "primaryReadonly"
        SECONDARY = "secondary"
        SECONDARY_READONLY = "secondaryReadonly"


    class azure.mgmt.cosmosdb.models.KeyWrapMetadata(Model):
        algorithm: str
        name: str
        type: str
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                algorithm: Optional[str] = ..., 
                name: Optional[str] = ..., 
                type: Optional[str] = ..., 
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


    class azure.mgmt.cosmosdb.models.Kind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRIMARY = "Primary"
        PRIMARY_READONLY = "PrimaryReadonly"
        SECONDARY = "Secondary"
        SECONDARY_READONLY = "SecondaryReadonly"


    class azure.mgmt.cosmosdb.models.ListClusters(Model):
        value: list[ClusterResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[list[ClusterResource]] = ..., 
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


    class azure.mgmt.cosmosdb.models.ListDataCenters(Model):
        value: list[DataCenterResource]

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


    class azure.mgmt.cosmosdb.models.Location(Model):
        document_endpoint: str
        failover_priority: int
        id: str
        is_zone_redundant: bool
        location_name: str
        provisioning_state: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                failover_priority: Optional[int] = ..., 
                is_zone_redundant: Optional[bool] = ..., 
                location_name: Optional[str] = ..., 
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


    class azure.mgmt.cosmosdb.models.LocationGetResult(ARMProxyResource):
        id: str
        name: str
        properties: LocationProperties
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[LocationProperties] = ..., 
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


    class azure.mgmt.cosmosdb.models.LocationListResult(Model):
        value: list[LocationGetResult]

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


    class azure.mgmt.cosmosdb.models.LocationProperties(Model):
        backup_storage_redundancies: Union[list[str, BackupStorageRedundancy]]
        is_residency_restricted: bool
        is_subscription_region_access_allowed_for_az: bool
        is_subscription_region_access_allowed_for_regular: bool
        status: Union[str, Status]
        supports_availability_zone: bool

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


    class azure.mgmt.cosmosdb.models.ManagedCassandraARMResourceProperties(Model):
        id: str
        identity: ManagedCassandraManagedServiceIdentity
        location: str
        name: str
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                identity: Optional[ManagedCassandraManagedServiceIdentity] = ..., 
                location: Optional[str] = ..., 
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


    class azure.mgmt.cosmosdb.models.ManagedCassandraManagedServiceIdentity(Model):
        principal_id: str
        tenant_id: str
        type: Union[str, ManagedCassandraResourceIdentityType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                type: Optional[Union[str, ManagedCassandraResourceIdentityType]] = ..., 
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


    class azure.mgmt.cosmosdb.models.ManagedCassandraProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.cosmosdb.models.ManagedCassandraReaperStatus(Model):
        healthy: bool
        repair_run_ids: dict[str, str]
        repair_schedules: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                healthy: Optional[bool] = ..., 
                repair_run_ids: Optional[dict[str, str]] = ..., 
                repair_schedules: Optional[dict[str, str]] = ..., 
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


    class azure.mgmt.cosmosdb.models.ManagedCassandraResourceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"


    class azure.mgmt.cosmosdb.models.ManagedServiceIdentity(Model):
        principal_id: str
        tenant_id: str
        type: Union[str, ResourceIdentityType]
        user_assigned_identities: dict[str, ManagedServiceIdentityUserAssignedIdentity]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                type: Optional[Union[str, ResourceIdentityType]] = ..., 
                user_assigned_identities: Optional[dict[str, ManagedServiceIdentityUserAssignedIdentity]] = ..., 
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


    class azure.mgmt.cosmosdb.models.ManagedServiceIdentityUserAssignedIdentity(Model):
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


    class azure.mgmt.cosmosdb.models.MaterializedViewsBuilderRegionalServiceResource(RegionalServiceResource):
        location: str
        name: str
        status: Union[str, ServiceStatus]

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


    class azure.mgmt.cosmosdb.models.MaterializedViewsBuilderServiceResource(Model):
        properties: MaterializedViewsBuilderServiceResourceProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[MaterializedViewsBuilderServiceResourceProperties] = ..., 
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


    class azure.mgmt.cosmosdb.models.MaterializedViewsBuilderServiceResourceCreateUpdateProperties(ServiceResourceCreateUpdateProperties):
        instance_count: int
        instance_size: Union[str, ServiceSize]
        service_type: Union[str, ServiceType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                instance_count: Optional[int] = ..., 
                instance_size: Optional[Union[str, ServiceSize]] = ..., 
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


    class azure.mgmt.cosmosdb.models.MaterializedViewsBuilderServiceResourceProperties(ServiceResourceProperties):
        additional_properties: dict[str, any]
        creation_time: datetime
        instance_count: int
        instance_size: Union[str, ServiceSize]
        locations: list[MaterializedViewsBuilderRegionalServiceResource]
        service_type: Union[str, ServiceType]
        status: Union[str, ServiceStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_properties: Optional[dict[str, Any]] = ..., 
                instance_count: Optional[int] = ..., 
                instance_size: Optional[Union[str, ServiceSize]] = ..., 
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


    class azure.mgmt.cosmosdb.models.Metric(Model):
        end_time: datetime
        metric_values: list[MetricValue]
        name: MetricName
        start_time: datetime
        time_grain: str
        unit: Union[str, UnitType]

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


    class azure.mgmt.cosmosdb.models.MetricAvailability(Model):
        retention: str
        time_grain: str

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


    class azure.mgmt.cosmosdb.models.MetricDefinition(Model):
        metric_availabilities: list[MetricAvailability]
        name: MetricName
        primary_aggregation_type: Union[str, PrimaryAggregationType]
        resource_uri: str
        unit: Union[str, UnitType]

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


    class azure.mgmt.cosmosdb.models.MetricDefinitionsListResult(Model):
        value: list[MetricDefinition]

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


    class azure.mgmt.cosmosdb.models.MetricListResult(Model):
        value: list[Metric]

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


    class azure.mgmt.cosmosdb.models.MetricName(Model):
        localized_value: str
        value: str

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


    class azure.mgmt.cosmosdb.models.MetricValue(Model):
        average: float
        count: int
        maximum: float
        minimum: float
        timestamp: datetime
        total: float

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


    class azure.mgmt.cosmosdb.models.MinimalTlsVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        TLS = "Tls"
        TLS11 = "Tls11"
        TLS12 = "Tls12"


    class azure.mgmt.cosmosdb.models.MongoDBCollectionCreateUpdateParameters(ARMResourceProperties):
        id: str
        location: str
        name: str
        options: CreateUpdateOptions
        resource: MongoDBCollectionResource
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                options: Optional[CreateUpdateOptions] = ..., 
                resource: MongoDBCollectionResource, 
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


    class azure.mgmt.cosmosdb.models.MongoDBCollectionGetPropertiesOptions(OptionsResource):
        autoscale_settings: AutoscaleSettings
        throughput: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                autoscale_settings: Optional[AutoscaleSettings] = ..., 
                throughput: Optional[int] = ..., 
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


    class azure.mgmt.cosmosdb.models.MongoDBCollectionGetPropertiesResource(MongoDBCollectionResource, ExtendedResourceProperties):
        analytical_storage_ttl: int
        create_mode: Union[str, CreateMode]
        etag: str
        id: str
        indexes: list[MongoIndex]
        restore_parameters: ResourceRestoreParameters
        rid: str
        shard_key: dict[str, str]
        ts: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                analytical_storage_ttl: Optional[int] = ..., 
                create_mode: Union[str, CreateMode] = "Default", 
                id: str, 
                indexes: Optional[list[MongoIndex]] = ..., 
                restore_parameters: Optional[ResourceRestoreParameters] = ..., 
                shard_key: Optional[dict[str, str]] = ..., 
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


    class azure.mgmt.cosmosdb.models.MongoDBCollectionGetResults(ARMResourceProperties):
        id: str
        location: str
        name: str
        options: MongoDBCollectionGetPropertiesOptions
        resource: MongoDBCollectionGetPropertiesResource
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                options: Optional[MongoDBCollectionGetPropertiesOptions] = ..., 
                resource: Optional[MongoDBCollectionGetPropertiesResource] = ..., 
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


    class azure.mgmt.cosmosdb.models.MongoDBCollectionListResult(Model):
        value: list[MongoDBCollectionGetResults]

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


    class azure.mgmt.cosmosdb.models.MongoDBCollectionResource(Model):
        analytical_storage_ttl: int
        create_mode: Union[str, CreateMode]
        id: str
        indexes: list[MongoIndex]
        restore_parameters: ResourceRestoreParameters
        shard_key: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                analytical_storage_ttl: Optional[int] = ..., 
                create_mode: Union[str, CreateMode] = "Default", 
                id: str, 
                indexes: Optional[list[MongoIndex]] = ..., 
                restore_parameters: Optional[ResourceRestoreParameters] = ..., 
                shard_key: Optional[dict[str, str]] = ..., 
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


    class azure.mgmt.cosmosdb.models.MongoDBDatabaseCreateUpdateParameters(ARMResourceProperties):
        id: str
        location: str
        name: str
        options: CreateUpdateOptions
        resource: MongoDBDatabaseResource
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                options: Optional[CreateUpdateOptions] = ..., 
                resource: MongoDBDatabaseResource, 
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


    class azure.mgmt.cosmosdb.models.MongoDBDatabaseGetPropertiesOptions(OptionsResource):
        autoscale_settings: AutoscaleSettings
        throughput: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                autoscale_settings: Optional[AutoscaleSettings] = ..., 
                throughput: Optional[int] = ..., 
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


    class azure.mgmt.cosmosdb.models.MongoDBDatabaseGetPropertiesResource(MongoDBDatabaseResource, ExtendedResourceProperties):
        create_mode: Union[str, CreateMode]
        etag: str
        id: str
        restore_parameters: ResourceRestoreParameters
        rid: str
        ts: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                create_mode: Union[str, CreateMode] = "Default", 
                id: str, 
                restore_parameters: Optional[ResourceRestoreParameters] = ..., 
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


    class azure.mgmt.cosmosdb.models.MongoDBDatabaseGetResults(ARMResourceProperties):
        id: str
        location: str
        name: str
        options: MongoDBDatabaseGetPropertiesOptions
        resource: MongoDBDatabaseGetPropertiesResource
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                options: Optional[MongoDBDatabaseGetPropertiesOptions] = ..., 
                resource: Optional[MongoDBDatabaseGetPropertiesResource] = ..., 
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


    class azure.mgmt.cosmosdb.models.MongoDBDatabaseListResult(Model):
        value: list[MongoDBDatabaseGetResults]

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


    class azure.mgmt.cosmosdb.models.MongoDBDatabaseResource(Model):
        create_mode: Union[str, CreateMode]
        id: str
        restore_parameters: ResourceRestoreParameters

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                create_mode: Union[str, CreateMode] = "Default", 
                id: str, 
                restore_parameters: Optional[ResourceRestoreParameters] = ..., 
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


    class azure.mgmt.cosmosdb.models.MongoIndex(Model):
        key: MongoIndexKeys
        options: MongoIndexOptions

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key: Optional[MongoIndexKeys] = ..., 
                options: Optional[MongoIndexOptions] = ..., 
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


    class azure.mgmt.cosmosdb.models.MongoIndexKeys(Model):
        keys: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                keys: Optional[list[str]] = ..., 
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


    class azure.mgmt.cosmosdb.models.MongoIndexOptions(Model):
        expire_after_seconds: int
        unique: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                expire_after_seconds: Optional[int] = ..., 
                unique: Optional[bool] = ..., 
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


    class azure.mgmt.cosmosdb.models.MongoRoleDefinitionCreateUpdateParameters(Model):
        database_name: str
        privileges: list[Privilege]
        role_name: str
        roles: list[Role]
        type: Union[str, MongoRoleDefinitionType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                database_name: Optional[str] = ..., 
                privileges: Optional[list[Privilege]] = ..., 
                role_name: Optional[str] = ..., 
                roles: Optional[list[Role]] = ..., 
                type: Optional[Union[str, MongoRoleDefinitionType]] = ..., 
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


    class azure.mgmt.cosmosdb.models.MongoRoleDefinitionGetResults(ARMProxyResource):
        database_name: str
        id: str
        name: str
        privileges: list[Privilege]
        role_name: str
        roles: list[Role]
        type: str
        type_properties_type: Union[str, MongoRoleDefinitionType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                database_name: Optional[str] = ..., 
                privileges: Optional[list[Privilege]] = ..., 
                role_name: Optional[str] = ..., 
                roles: Optional[list[Role]] = ..., 
                type_properties_type: Optional[Union[str, MongoRoleDefinitionType]] = ..., 
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


    class azure.mgmt.cosmosdb.models.MongoRoleDefinitionListResult(Model):
        value: list[MongoRoleDefinitionGetResults]

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


    class azure.mgmt.cosmosdb.models.MongoRoleDefinitionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BUILT_IN_ROLE = "BuiltInRole"
        CUSTOM_ROLE = "CustomRole"


    class azure.mgmt.cosmosdb.models.MongoUserDefinitionCreateUpdateParameters(Model):
        custom_data: str
        database_name: str
        mechanisms: str
        password: str
        roles: list[Role]
        user_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                custom_data: Optional[str] = ..., 
                database_name: Optional[str] = ..., 
                mechanisms: Optional[str] = ..., 
                password: Optional[str] = ..., 
                roles: Optional[list[Role]] = ..., 
                user_name: Optional[str] = ..., 
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


    class azure.mgmt.cosmosdb.models.MongoUserDefinitionGetResults(ARMProxyResource):
        custom_data: str
        database_name: str
        id: str
        mechanisms: str
        name: str
        password: str
        roles: list[Role]
        type: str
        user_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                custom_data: Optional[str] = ..., 
                database_name: Optional[str] = ..., 
                mechanisms: Optional[str] = ..., 
                password: Optional[str] = ..., 
                roles: Optional[list[Role]] = ..., 
                user_name: Optional[str] = ..., 
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


    class azure.mgmt.cosmosdb.models.MongoUserDefinitionListResult(Model):
        value: list[MongoUserDefinitionGetResults]

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


    class azure.mgmt.cosmosdb.models.NetworkAclBypass(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_SERVICES = "AzureServices"
        NONE = "None"


    class azure.mgmt.cosmosdb.models.NodeState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        JOINING = "Joining"
        LEAVING = "Leaving"
        MOVING = "Moving"
        NORMAL = "Normal"
        STOPPED = "Stopped"


    class azure.mgmt.cosmosdb.models.NodeStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DOWN = "Down"
        UP = "Up"


    class azure.mgmt.cosmosdb.models.NotebookWorkspace(ARMProxyResource):
        id: str
        name: str
        notebook_server_endpoint: str
        status: str
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


    class azure.mgmt.cosmosdb.models.NotebookWorkspaceConnectionInfoResult(Model):
        auth_token: str
        notebook_server_endpoint: str

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


    class azure.mgmt.cosmosdb.models.NotebookWorkspaceCreateUpdateParameters(ARMProxyResource):
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


    class azure.mgmt.cosmosdb.models.NotebookWorkspaceListResult(Model):
        value: list[NotebookWorkspace]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[list[NotebookWorkspace]] = ..., 
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


    class azure.mgmt.cosmosdb.models.NotebookWorkspaceName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "default"


    class azure.mgmt.cosmosdb.models.Operation(Model):
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


    class azure.mgmt.cosmosdb.models.OperationDisplay(Model):
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
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.cosmosdb.models.OperationListResult(Model):
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


    class azure.mgmt.cosmosdb.models.OperationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATE = "Create"
        DELETE = "Delete"
        RECREATE = "Recreate"
        REPLACE = "Replace"
        SYSTEM_OPERATION = "SystemOperation"


    class azure.mgmt.cosmosdb.models.OptionsResource(Model):
        autoscale_settings: AutoscaleSettings
        throughput: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                autoscale_settings: Optional[AutoscaleSettings] = ..., 
                throughput: Optional[int] = ..., 
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


    class azure.mgmt.cosmosdb.models.PartitionKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HASH = "Hash"
        MULTI_HASH = "MultiHash"
        RANGE = "Range"


    class azure.mgmt.cosmosdb.models.PartitionMetric(Metric):
        end_time: datetime
        metric_values: list[MetricValue]
        name: MetricName
        partition_id: str
        partition_key_range_id: str
        start_time: datetime
        time_grain: str
        unit: Union[str, UnitType]

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


    class azure.mgmt.cosmosdb.models.PartitionMetricListResult(Model):
        value: list[PartitionMetric]

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


    class azure.mgmt.cosmosdb.models.PartitionUsage(Usage):
        current_value: int
        limit: int
        name: MetricName
        partition_id: str
        partition_key_range_id: str
        quota_period: str
        unit: Union[str, UnitType]

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


    class azure.mgmt.cosmosdb.models.PartitionUsagesResult(Model):
        value: list[PartitionUsage]

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


    class azure.mgmt.cosmosdb.models.PercentileMetric(Model):
        end_time: datetime
        metric_values: list[PercentileMetricValue]
        name: MetricName
        start_time: datetime
        time_grain: str
        unit: Union[str, UnitType]

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


    class azure.mgmt.cosmosdb.models.PercentileMetricListResult(Model):
        value: list[PercentileMetric]

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


    class azure.mgmt.cosmosdb.models.PercentileMetricValue(MetricValue):
        average: float
        count: int
        maximum: float
        minimum: float
        p10: float
        p25: float
        p50: float
        p75: float
        p90: float
        p95: float
        p99: float
        timestamp: datetime
        total: float

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


    class azure.mgmt.cosmosdb.models.PeriodicModeBackupPolicy(BackupPolicy):
        migration_state: BackupPolicyMigrationState
        periodic_mode_properties: PeriodicModeProperties
        type: Union[str, BackupPolicyType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                migration_state: Optional[BackupPolicyMigrationState] = ..., 
                periodic_mode_properties: Optional[PeriodicModeProperties] = ..., 
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


    class azure.mgmt.cosmosdb.models.PeriodicModeProperties(Model):
        backup_interval_in_minutes: int
        backup_retention_interval_in_hours: int
        backup_storage_redundancy: Union[str, BackupStorageRedundancy]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                backup_interval_in_minutes: Optional[int] = ..., 
                backup_retention_interval_in_hours: Optional[int] = ..., 
                backup_storage_redundancy: Optional[Union[str, BackupStorageRedundancy]] = ..., 
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


    class azure.mgmt.cosmosdb.models.Permission(Model):
        data_actions: list[str]
        not_data_actions: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                data_actions: Optional[list[str]] = ..., 
                not_data_actions: Optional[list[str]] = ..., 
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


    class azure.mgmt.cosmosdb.models.PrimaryAggregationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVERAGE = "Average"
        LAST = "Last"
        MAXIMUM = "Maximum"
        MINIMUM = "Minimum"
        NONE = "None"
        TOTAL = "Total"


    class azure.mgmt.cosmosdb.models.PrivateEndpointConnection(ProxyResource):
        group_id: str
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
                group_id: Optional[str] = ..., 
                private_endpoint: Optional[PrivateEndpointProperty] = ..., 
                private_link_service_connection_state: Optional[PrivateLinkServiceConnectionStateProperty] = ..., 
                provisioning_state: Optional[str] = ..., 
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


    class azure.mgmt.cosmosdb.models.PrivateEndpointConnectionListResult(Model):
        value: list[PrivateEndpointConnection]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[list[PrivateEndpointConnection]] = ..., 
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


    class azure.mgmt.cosmosdb.models.PrivateEndpointProperty(Model):
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


    class azure.mgmt.cosmosdb.models.PrivateLinkResource(ARMProxyResource):
        group_id: str
        id: str
        name: str
        required_members: list[str]
        required_zone_names: list[str]
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


    class azure.mgmt.cosmosdb.models.PrivateLinkResourceListResult(Model):
        value: list[PrivateLinkResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[list[PrivateLinkResource]] = ..., 
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


    class azure.mgmt.cosmosdb.models.PrivateLinkServiceConnectionStateProperty(Model):
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
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.cosmosdb.models.Privilege(Model):
        actions: list[str]
        resource: PrivilegeResource

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                actions: Optional[list[str]] = ..., 
                resource: Optional[PrivilegeResource] = ..., 
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


    class azure.mgmt.cosmosdb.models.PrivilegeResource(Model):
        collection: str
        db: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                collection: Optional[str] = ..., 
                db: Optional[str] = ..., 
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


    class azure.mgmt.cosmosdb.models.ProxyResource(Resource):
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


    class azure.mgmt.cosmosdb.models.ProxyResourceAutoGenerated(ResourceAutoGenerated):
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


    class azure.mgmt.cosmosdb.models.PublicNetworkAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        SECURED_BY_PERIMETER = "SecuredByPerimeter"


    class azure.mgmt.cosmosdb.models.RegionForOnlineOffline(Model):
        region: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                region: str, 
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


    class azure.mgmt.cosmosdb.models.RegionalServiceResource(Model):
        location: str
        name: str
        status: Union[str, ServiceStatus]

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


    class azure.mgmt.cosmosdb.models.Resource(Model):
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


    class azure.mgmt.cosmosdb.models.ResourceAutoGenerated(Model):
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


    class azure.mgmt.cosmosdb.models.ResourceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.cosmosdb.models.ResourceRestoreParameters(RestoreParametersBase):
        restore_source: str
        restore_timestamp_in_utc: datetime
        restore_with_ttl_disabled: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                restore_source: Optional[str] = ..., 
                restore_timestamp_in_utc: Optional[datetime] = ..., 
                restore_with_ttl_disabled: Optional[bool] = ..., 
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


    class azure.mgmt.cosmosdb.models.RestorableDatabaseAccountGetResult(Model):
        account_name: str
        api_type: Union[str, ApiType]
        creation_time: datetime
        deletion_time: datetime
        id: str
        location: str
        name: str
        oldest_restorable_time: datetime
        restorable_locations: list[RestorableLocationResource]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                account_name: Optional[str] = ..., 
                creation_time: Optional[datetime] = ..., 
                deletion_time: Optional[datetime] = ..., 
                location: Optional[str] = ..., 
                oldest_restorable_time: Optional[datetime] = ..., 
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


    class azure.mgmt.cosmosdb.models.RestorableDatabaseAccountsListResult(Model):
        value: list[RestorableDatabaseAccountGetResult]

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


    class azure.mgmt.cosmosdb.models.RestorableGremlinDatabaseGetResult(Model):
        id: str
        name: str
        resource: RestorableGremlinDatabasePropertiesResource
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                resource: Optional[RestorableGremlinDatabasePropertiesResource] = ..., 
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


    class azure.mgmt.cosmosdb.models.RestorableGremlinDatabasePropertiesResource(Model):
        can_undelete: str
        can_undelete_reason: str
        event_timestamp: str
        operation_type: Union[str, OperationType]
        owner_id: str
        owner_resource_id: str
        rid: str

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


    class azure.mgmt.cosmosdb.models.RestorableGremlinDatabasesListResult(Model):
        value: list[RestorableGremlinDatabaseGetResult]

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


    class azure.mgmt.cosmosdb.models.RestorableGremlinGraphGetResult(Model):
        id: str
        name: str
        resource: RestorableGremlinGraphPropertiesResource
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                resource: Optional[RestorableGremlinGraphPropertiesResource] = ..., 
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


    class azure.mgmt.cosmosdb.models.RestorableGremlinGraphPropertiesResource(Model):
        can_undelete: str
        can_undelete_reason: str
        event_timestamp: str
        operation_type: Union[str, OperationType]
        owner_id: str
        owner_resource_id: str
        rid: str

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


    class azure.mgmt.cosmosdb.models.RestorableGremlinGraphsListResult(Model):
        value: list[RestorableGremlinGraphGetResult]

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


    class azure.mgmt.cosmosdb.models.RestorableGremlinResourcesGetResult(Model):
        database_name: str
        graph_names: list[str]
        id: str
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                database_name: Optional[str] = ..., 
                graph_names: Optional[list[str]] = ..., 
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


    class azure.mgmt.cosmosdb.models.RestorableGremlinResourcesListResult(Model):
        value: list[RestorableGremlinResourcesGetResult]

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


    class azure.mgmt.cosmosdb.models.RestorableLocationResource(Model):
        creation_time: datetime
        deletion_time: datetime
        location_name: str
        regional_database_account_instance_id: str

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


    class azure.mgmt.cosmosdb.models.RestorableMongodbCollectionGetResult(Model):
        id: str
        name: str
        resource: RestorableMongodbCollectionPropertiesResource
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                resource: Optional[RestorableMongodbCollectionPropertiesResource] = ..., 
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


    class azure.mgmt.cosmosdb.models.RestorableMongodbCollectionPropertiesResource(Model):
        can_undelete: str
        can_undelete_reason: str
        event_timestamp: str
        operation_type: Union[str, OperationType]
        owner_id: str
        owner_resource_id: str
        rid: str

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


    class azure.mgmt.cosmosdb.models.RestorableMongodbCollectionsListResult(Model):
        value: list[RestorableMongodbCollectionGetResult]

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


    class azure.mgmt.cosmosdb.models.RestorableMongodbDatabaseGetResult(Model):
        id: str
        name: str
        resource: RestorableMongodbDatabasePropertiesResource
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                resource: Optional[RestorableMongodbDatabasePropertiesResource] = ..., 
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


    class azure.mgmt.cosmosdb.models.RestorableMongodbDatabasePropertiesResource(Model):
        can_undelete: str
        can_undelete_reason: str
        event_timestamp: str
        operation_type: Union[str, OperationType]
        owner_id: str
        owner_resource_id: str
        rid: str

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


    class azure.mgmt.cosmosdb.models.RestorableMongodbDatabasesListResult(Model):
        value: list[RestorableMongodbDatabaseGetResult]

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


    class azure.mgmt.cosmosdb.models.RestorableMongodbResourcesGetResult(Model):
        collection_names: list[str]
        database_name: str
        id: str
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                collection_names: Optional[list[str]] = ..., 
                database_name: Optional[str] = ..., 
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


    class azure.mgmt.cosmosdb.models.RestorableMongodbResourcesListResult(Model):
        value: list[RestorableMongodbResourcesGetResult]

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


    class azure.mgmt.cosmosdb.models.RestorableSqlContainerGetResult(Model):
        id: str
        name: str
        resource: RestorableSqlContainerPropertiesResource
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                resource: Optional[RestorableSqlContainerPropertiesResource] = ..., 
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


    class azure.mgmt.cosmosdb.models.RestorableSqlContainerPropertiesResource(Model):
        can_undelete: str
        can_undelete_reason: str
        container: RestorableSqlContainerPropertiesResourceContainer
        event_timestamp: str
        operation_type: Union[str, OperationType]
        owner_id: str
        owner_resource_id: str
        rid: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                container: Optional[RestorableSqlContainerPropertiesResourceContainer] = ..., 
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


    class azure.mgmt.cosmosdb.models.RestorableSqlContainerPropertiesResourceContainer(SqlContainerResource, ExtendedResourceProperties):
        analytical_storage_ttl: int
        client_encryption_policy: ClientEncryptionPolicy
        computed_properties: list[ComputedProperty]
        conflict_resolution_policy: ConflictResolutionPolicy
        create_mode: Union[str, CreateMode]
        default_ttl: int
        etag: str
        full_text_policy: FullTextPolicy
        id: str
        indexing_policy: IndexingPolicy
        partition_key: ContainerPartitionKey
        restore_parameters: ResourceRestoreParameters
        rid: str
        self_property: str
        ts: float
        unique_key_policy: UniqueKeyPolicy
        vector_embedding_policy: VectorEmbeddingPolicy

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                analytical_storage_ttl: Optional[int] = ..., 
                client_encryption_policy: Optional[ClientEncryptionPolicy] = ..., 
                computed_properties: Optional[list[ComputedProperty]] = ..., 
                conflict_resolution_policy: Optional[ConflictResolutionPolicy] = ..., 
                create_mode: Union[str, CreateMode] = "Default", 
                default_ttl: Optional[int] = ..., 
                full_text_policy: Optional[FullTextPolicy] = ..., 
                id: str, 
                indexing_policy: Optional[IndexingPolicy] = ..., 
                partition_key: Optional[ContainerPartitionKey] = ..., 
                restore_parameters: Optional[ResourceRestoreParameters] = ..., 
                unique_key_policy: Optional[UniqueKeyPolicy] = ..., 
                vector_embedding_policy: Optional[VectorEmbeddingPolicy] = ..., 
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


    class azure.mgmt.cosmosdb.models.RestorableSqlContainersListResult(Model):
        value: list[RestorableSqlContainerGetResult]

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


    class azure.mgmt.cosmosdb.models.RestorableSqlDatabaseGetResult(Model):
        id: str
        name: str
        resource: RestorableSqlDatabasePropertiesResource
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                resource: Optional[RestorableSqlDatabasePropertiesResource] = ..., 
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


    class azure.mgmt.cosmosdb.models.RestorableSqlDatabasePropertiesResource(Model):
        can_undelete: str
        can_undelete_reason: str
        database: RestorableSqlDatabasePropertiesResourceDatabase
        event_timestamp: str
        operation_type: Union[str, OperationType]
        owner_id: str
        owner_resource_id: str
        rid: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                database: Optional[RestorableSqlDatabasePropertiesResourceDatabase] = ..., 
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


    class azure.mgmt.cosmosdb.models.RestorableSqlDatabasePropertiesResourceDatabase(SqlDatabaseResource, ExtendedResourceProperties):
        colls: str
        create_mode: Union[str, CreateMode]
        etag: str
        id: str
        restore_parameters: ResourceRestoreParameters
        rid: str
        self_property: str
        ts: float
        users: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                create_mode: Union[str, CreateMode] = "Default", 
                id: str, 
                restore_parameters: Optional[ResourceRestoreParameters] = ..., 
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


    class azure.mgmt.cosmosdb.models.RestorableSqlDatabasesListResult(Model):
        value: list[RestorableSqlDatabaseGetResult]

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


    class azure.mgmt.cosmosdb.models.RestorableSqlResourcesGetResult(Model):
        collection_names: list[str]
        database_name: str
        id: str
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                collection_names: Optional[list[str]] = ..., 
                database_name: Optional[str] = ..., 
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


    class azure.mgmt.cosmosdb.models.RestorableSqlResourcesListResult(Model):
        value: list[RestorableSqlResourcesGetResult]

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


    class azure.mgmt.cosmosdb.models.RestorableTableGetResult(Model):
        id: str
        name: str
        resource: RestorableTablePropertiesResource
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                resource: Optional[RestorableTablePropertiesResource] = ..., 
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


    class azure.mgmt.cosmosdb.models.RestorableTablePropertiesResource(Model):
        can_undelete: str
        can_undelete_reason: str
        event_timestamp: str
        operation_type: Union[str, OperationType]
        owner_id: str
        owner_resource_id: str
        rid: str

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


    class azure.mgmt.cosmosdb.models.RestorableTableResourcesGetResult(Model):
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


    class azure.mgmt.cosmosdb.models.RestorableTableResourcesListResult(Model):
        value: list[RestorableTableResourcesGetResult]

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


    class azure.mgmt.cosmosdb.models.RestorableTablesListResult(Model):
        value: list[RestorableTableGetResult]

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


    class azure.mgmt.cosmosdb.models.RestoreMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        POINT_IN_TIME = "PointInTime"


    class azure.mgmt.cosmosdb.models.RestoreParameters(RestoreParametersBase):
        databases_to_restore: list[DatabaseRestoreResource]
        gremlin_databases_to_restore: list[GremlinDatabaseRestoreResource]
        restore_mode: Union[str, RestoreMode]
        restore_source: str
        restore_timestamp_in_utc: datetime
        restore_with_ttl_disabled: bool
        source_backup_location: str
        tables_to_restore: list[str]

        def __eq__(self, other: Any) -> bool: ...

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
                tables_to_restore: Optional[list[str]] = ..., 
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


    class azure.mgmt.cosmosdb.models.RestoreParametersBase(Model):
        restore_source: str
        restore_timestamp_in_utc: datetime
        restore_with_ttl_disabled: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                restore_source: Optional[str] = ..., 
                restore_timestamp_in_utc: Optional[datetime] = ..., 
                restore_with_ttl_disabled: Optional[bool] = ..., 
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


    class azure.mgmt.cosmosdb.models.Role(Model):
        db: str
        role: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                db: Optional[str] = ..., 
                role: Optional[str] = ..., 
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


    class azure.mgmt.cosmosdb.models.RoleDefinitionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BUILT_IN_ROLE = "BuiltInRole"
        CUSTOM_ROLE = "CustomRole"


    class azure.mgmt.cosmosdb.models.SeedNode(Model):
        ip_address: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                ip_address: Optional[str] = ..., 
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


    class azure.mgmt.cosmosdb.models.ServerVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FIVE0 = "5.0"
        FOUR0 = "4.0"
        FOUR2 = "4.2"
        SEVEN0 = "7.0"
        SIX0 = "6.0"
        THREE2 = "3.2"
        THREE6 = "3.6"


    class azure.mgmt.cosmosdb.models.ServiceResource(ARMProxyResource):
        id: str
        name: str
        properties: ServiceResourceProperties
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[ServiceResourceProperties] = ..., 
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


    class azure.mgmt.cosmosdb.models.ServiceResourceCreateUpdateParameters(Model):
        properties: ServiceResourceCreateUpdateProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[ServiceResourceCreateUpdateProperties] = ..., 
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


    class azure.mgmt.cosmosdb.models.ServiceResourceCreateUpdateProperties(Model):
        instance_count: int
        instance_size: Union[str, ServiceSize]
        service_type: Union[str, ServiceType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                instance_count: Optional[int] = ..., 
                instance_size: Optional[Union[str, ServiceSize]] = ..., 
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


    class azure.mgmt.cosmosdb.models.ServiceResourceListResult(Model):
        value: list[ServiceResource]

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


    class azure.mgmt.cosmosdb.models.ServiceResourceProperties(Model):
        additional_properties: dict[str, any]
        creation_time: datetime
        instance_count: int
        instance_size: Union[str, ServiceSize]
        service_type: Union[str, ServiceType]
        status: Union[str, ServiceStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_properties: Optional[dict[str, Any]] = ..., 
                instance_count: Optional[int] = ..., 
                instance_size: Optional[Union[str, ServiceSize]] = ..., 
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


    class azure.mgmt.cosmosdb.models.SpatialSpec(Model):
        path: str
        types: Union[list[str, SpatialType]]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                path: Optional[str] = ..., 
                types: Optional[list[Union[str, SpatialType]]] = ..., 
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


    class azure.mgmt.cosmosdb.models.SpatialType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LINE_STRING = "LineString"
        MULTI_POLYGON = "MultiPolygon"
        POINT = "Point"
        POLYGON = "Polygon"


    class azure.mgmt.cosmosdb.models.SqlContainerCreateUpdateParameters(ARMResourceProperties):
        id: str
        location: str
        name: str
        options: CreateUpdateOptions
        resource: SqlContainerResource
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                options: Optional[CreateUpdateOptions] = ..., 
                resource: SqlContainerResource, 
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


    class azure.mgmt.cosmosdb.models.SqlContainerGetPropertiesOptions(OptionsResource):
        autoscale_settings: AutoscaleSettings
        throughput: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                autoscale_settings: Optional[AutoscaleSettings] = ..., 
                throughput: Optional[int] = ..., 
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


    class azure.mgmt.cosmosdb.models.SqlContainerGetPropertiesResource(SqlContainerResource, ExtendedResourceProperties):
        analytical_storage_ttl: int
        client_encryption_policy: ClientEncryptionPolicy
        computed_properties: list[ComputedProperty]
        conflict_resolution_policy: ConflictResolutionPolicy
        create_mode: Union[str, CreateMode]
        default_ttl: int
        etag: str
        full_text_policy: FullTextPolicy
        id: str
        indexing_policy: IndexingPolicy
        partition_key: ContainerPartitionKey
        restore_parameters: ResourceRestoreParameters
        rid: str
        ts: float
        unique_key_policy: UniqueKeyPolicy
        vector_embedding_policy: VectorEmbeddingPolicy

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                analytical_storage_ttl: Optional[int] = ..., 
                client_encryption_policy: Optional[ClientEncryptionPolicy] = ..., 
                computed_properties: Optional[list[ComputedProperty]] = ..., 
                conflict_resolution_policy: Optional[ConflictResolutionPolicy] = ..., 
                create_mode: Union[str, CreateMode] = "Default", 
                default_ttl: Optional[int] = ..., 
                full_text_policy: Optional[FullTextPolicy] = ..., 
                id: str, 
                indexing_policy: Optional[IndexingPolicy] = ..., 
                partition_key: Optional[ContainerPartitionKey] = ..., 
                restore_parameters: Optional[ResourceRestoreParameters] = ..., 
                unique_key_policy: Optional[UniqueKeyPolicy] = ..., 
                vector_embedding_policy: Optional[VectorEmbeddingPolicy] = ..., 
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


    class azure.mgmt.cosmosdb.models.SqlContainerGetResults(ARMResourceProperties):
        id: str
        location: str
        name: str
        options: SqlContainerGetPropertiesOptions
        resource: SqlContainerGetPropertiesResource
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                options: Optional[SqlContainerGetPropertiesOptions] = ..., 
                resource: Optional[SqlContainerGetPropertiesResource] = ..., 
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


    class azure.mgmt.cosmosdb.models.SqlContainerListResult(Model):
        value: list[SqlContainerGetResults]

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


    class azure.mgmt.cosmosdb.models.SqlContainerResource(Model):
        analytical_storage_ttl: int
        client_encryption_policy: ClientEncryptionPolicy
        computed_properties: list[ComputedProperty]
        conflict_resolution_policy: ConflictResolutionPolicy
        create_mode: Union[str, CreateMode]
        default_ttl: int
        full_text_policy: FullTextPolicy
        id: str
        indexing_policy: IndexingPolicy
        partition_key: ContainerPartitionKey
        restore_parameters: ResourceRestoreParameters
        unique_key_policy: UniqueKeyPolicy
        vector_embedding_policy: VectorEmbeddingPolicy

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                analytical_storage_ttl: Optional[int] = ..., 
                client_encryption_policy: Optional[ClientEncryptionPolicy] = ..., 
                computed_properties: Optional[list[ComputedProperty]] = ..., 
                conflict_resolution_policy: Optional[ConflictResolutionPolicy] = ..., 
                create_mode: Union[str, CreateMode] = "Default", 
                default_ttl: Optional[int] = ..., 
                full_text_policy: Optional[FullTextPolicy] = ..., 
                id: str, 
                indexing_policy: Optional[IndexingPolicy] = ..., 
                partition_key: Optional[ContainerPartitionKey] = ..., 
                restore_parameters: Optional[ResourceRestoreParameters] = ..., 
                unique_key_policy: Optional[UniqueKeyPolicy] = ..., 
                vector_embedding_policy: Optional[VectorEmbeddingPolicy] = ..., 
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


    class azure.mgmt.cosmosdb.models.SqlDatabaseCreateUpdateParameters(ARMResourceProperties):
        id: str
        location: str
        name: str
        options: CreateUpdateOptions
        resource: SqlDatabaseResource
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                options: Optional[CreateUpdateOptions] = ..., 
                resource: SqlDatabaseResource, 
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


    class azure.mgmt.cosmosdb.models.SqlDatabaseGetPropertiesOptions(OptionsResource):
        autoscale_settings: AutoscaleSettings
        throughput: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                autoscale_settings: Optional[AutoscaleSettings] = ..., 
                throughput: Optional[int] = ..., 
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


    class azure.mgmt.cosmosdb.models.SqlDatabaseGetPropertiesResource(SqlDatabaseResource, ExtendedResourceProperties):
        colls: str
        create_mode: Union[str, CreateMode]
        etag: str
        id: str
        restore_parameters: ResourceRestoreParameters
        rid: str
        ts: float
        users: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                colls: Optional[str] = ..., 
                create_mode: Union[str, CreateMode] = "Default", 
                id: str, 
                restore_parameters: Optional[ResourceRestoreParameters] = ..., 
                users: Optional[str] = ..., 
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


    class azure.mgmt.cosmosdb.models.SqlDatabaseGetResults(ARMResourceProperties):
        id: str
        location: str
        name: str
        options: SqlDatabaseGetPropertiesOptions
        resource: SqlDatabaseGetPropertiesResource
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                options: Optional[SqlDatabaseGetPropertiesOptions] = ..., 
                resource: Optional[SqlDatabaseGetPropertiesResource] = ..., 
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


    class azure.mgmt.cosmosdb.models.SqlDatabaseListResult(Model):
        value: list[SqlDatabaseGetResults]

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


    class azure.mgmt.cosmosdb.models.SqlDatabaseResource(Model):
        create_mode: Union[str, CreateMode]
        id: str
        restore_parameters: ResourceRestoreParameters

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                create_mode: Union[str, CreateMode] = "Default", 
                id: str, 
                restore_parameters: Optional[ResourceRestoreParameters] = ..., 
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


    class azure.mgmt.cosmosdb.models.SqlDedicatedGatewayRegionalServiceResource(RegionalServiceResource):
        location: str
        name: str
        sql_dedicated_gateway_endpoint: str
        status: Union[str, ServiceStatus]

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


    class azure.mgmt.cosmosdb.models.SqlDedicatedGatewayServiceResource(Model):
        properties: SqlDedicatedGatewayServiceResourceProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[SqlDedicatedGatewayServiceResourceProperties] = ..., 
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


    class azure.mgmt.cosmosdb.models.SqlDedicatedGatewayServiceResourceCreateUpdateProperties(ServiceResourceCreateUpdateProperties):
        dedicated_gateway_type: Union[str, DedicatedGatewayType]
        instance_count: int
        instance_size: Union[str, ServiceSize]
        service_type: Union[str, ServiceType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                dedicated_gateway_type: Optional[Union[str, DedicatedGatewayType]] = ..., 
                instance_count: Optional[int] = ..., 
                instance_size: Optional[Union[str, ServiceSize]] = ..., 
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


    class azure.mgmt.cosmosdb.models.SqlDedicatedGatewayServiceResourceProperties(ServiceResourceProperties):
        additional_properties: dict[str, any]
        creation_time: datetime
        dedicated_gateway_type: Union[str, DedicatedGatewayType]
        instance_count: int
        instance_size: Union[str, ServiceSize]
        locations: list[SqlDedicatedGatewayRegionalServiceResource]
        service_type: Union[str, ServiceType]
        sql_dedicated_gateway_endpoint: str
        status: Union[str, ServiceStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_properties: Optional[dict[str, Any]] = ..., 
                dedicated_gateway_type: Optional[Union[str, DedicatedGatewayType]] = ..., 
                instance_count: Optional[int] = ..., 
                instance_size: Optional[Union[str, ServiceSize]] = ..., 
                sql_dedicated_gateway_endpoint: Optional[str] = ..., 
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


    class azure.mgmt.cosmosdb.models.SqlRoleAssignmentCreateUpdateParameters(Model):
        principal_id: str
        role_definition_id: str
        scope: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                principal_id: Optional[str] = ..., 
                role_definition_id: Optional[str] = ..., 
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


    class azure.mgmt.cosmosdb.models.SqlRoleAssignmentGetResults(ARMProxyResource):
        id: str
        name: str
        principal_id: str
        role_definition_id: str
        scope: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                principal_id: Optional[str] = ..., 
                role_definition_id: Optional[str] = ..., 
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


    class azure.mgmt.cosmosdb.models.SqlRoleAssignmentListResult(Model):
        value: list[SqlRoleAssignmentGetResults]

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


    class azure.mgmt.cosmosdb.models.SqlRoleDefinitionCreateUpdateParameters(Model):
        assignable_scopes: list[str]
        permissions: list[Permission]
        role_name: str
        type: Union[str, RoleDefinitionType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                assignable_scopes: Optional[list[str]] = ..., 
                permissions: Optional[list[Permission]] = ..., 
                role_name: Optional[str] = ..., 
                type: Optional[Union[str, RoleDefinitionType]] = ..., 
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


    class azure.mgmt.cosmosdb.models.SqlRoleDefinitionGetResults(ARMProxyResource):
        assignable_scopes: list[str]
        id: str
        name: str
        permissions: list[Permission]
        role_name: str
        type: str
        type_properties_type: Union[str, RoleDefinitionType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                assignable_scopes: Optional[list[str]] = ..., 
                permissions: Optional[list[Permission]] = ..., 
                role_name: Optional[str] = ..., 
                type_properties_type: Optional[Union[str, RoleDefinitionType]] = ..., 
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


    class azure.mgmt.cosmosdb.models.SqlRoleDefinitionListResult(Model):
        value: list[SqlRoleDefinitionGetResults]

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


    class azure.mgmt.cosmosdb.models.SqlStoredProcedureCreateUpdateParameters(ARMResourceProperties):
        id: str
        location: str
        name: str
        options: CreateUpdateOptions
        resource: SqlStoredProcedureResource
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                options: Optional[CreateUpdateOptions] = ..., 
                resource: SqlStoredProcedureResource, 
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


    class azure.mgmt.cosmosdb.models.SqlStoredProcedureGetPropertiesResource(SqlStoredProcedureResource, ExtendedResourceProperties):
        body: str
        etag: str
        id: str
        rid: str
        ts: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                body: Optional[str] = ..., 
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


    class azure.mgmt.cosmosdb.models.SqlStoredProcedureGetResults(ARMResourceProperties):
        id: str
        location: str
        name: str
        resource: SqlStoredProcedureGetPropertiesResource
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                resource: Optional[SqlStoredProcedureGetPropertiesResource] = ..., 
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


    class azure.mgmt.cosmosdb.models.SqlStoredProcedureListResult(Model):
        value: list[SqlStoredProcedureGetResults]

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


    class azure.mgmt.cosmosdb.models.SqlStoredProcedureResource(Model):
        body: str
        id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                body: Optional[str] = ..., 
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


    class azure.mgmt.cosmosdb.models.SqlTriggerCreateUpdateParameters(ARMResourceProperties):
        id: str
        location: str
        name: str
        options: CreateUpdateOptions
        resource: SqlTriggerResource
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                options: Optional[CreateUpdateOptions] = ..., 
                resource: SqlTriggerResource, 
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


    class azure.mgmt.cosmosdb.models.SqlTriggerGetPropertiesResource(SqlTriggerResource, ExtendedResourceProperties):
        body: str
        etag: str
        id: str
        rid: str
        trigger_operation: Union[str, TriggerOperation]
        trigger_type: Union[str, TriggerType]
        ts: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                body: Optional[str] = ..., 
                id: str, 
                trigger_operation: Optional[Union[str, TriggerOperation]] = ..., 
                trigger_type: Optional[Union[str, TriggerType]] = ..., 
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


    class azure.mgmt.cosmosdb.models.SqlTriggerGetResults(ARMResourceProperties):
        id: str
        location: str
        name: str
        resource: SqlTriggerGetPropertiesResource
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                resource: Optional[SqlTriggerGetPropertiesResource] = ..., 
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


    class azure.mgmt.cosmosdb.models.SqlTriggerListResult(Model):
        value: list[SqlTriggerGetResults]

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


    class azure.mgmt.cosmosdb.models.SqlTriggerResource(Model):
        body: str
        id: str
        trigger_operation: Union[str, TriggerOperation]
        trigger_type: Union[str, TriggerType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                body: Optional[str] = ..., 
                id: str, 
                trigger_operation: Optional[Union[str, TriggerOperation]] = ..., 
                trigger_type: Optional[Union[str, TriggerType]] = ..., 
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


    class azure.mgmt.cosmosdb.models.SqlUserDefinedFunctionCreateUpdateParameters(ARMResourceProperties):
        id: str
        location: str
        name: str
        options: CreateUpdateOptions
        resource: SqlUserDefinedFunctionResource
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                options: Optional[CreateUpdateOptions] = ..., 
                resource: SqlUserDefinedFunctionResource, 
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


    class azure.mgmt.cosmosdb.models.SqlUserDefinedFunctionGetPropertiesResource(SqlUserDefinedFunctionResource, ExtendedResourceProperties):
        body: str
        etag: str
        id: str
        rid: str
        ts: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                body: Optional[str] = ..., 
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


    class azure.mgmt.cosmosdb.models.SqlUserDefinedFunctionGetResults(ARMResourceProperties):
        id: str
        location: str
        name: str
        resource: SqlUserDefinedFunctionGetPropertiesResource
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                resource: Optional[SqlUserDefinedFunctionGetPropertiesResource] = ..., 
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


    class azure.mgmt.cosmosdb.models.SqlUserDefinedFunctionListResult(Model):
        value: list[SqlUserDefinedFunctionGetResults]

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


    class azure.mgmt.cosmosdb.models.SqlUserDefinedFunctionResource(Model):
        body: str
        id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                body: Optional[str] = ..., 
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


    class azure.mgmt.cosmosdb.models.SystemData(Model):
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


    class azure.mgmt.cosmosdb.models.TableCreateUpdateParameters(ARMResourceProperties):
        id: str
        location: str
        name: str
        options: CreateUpdateOptions
        resource: TableResource
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                options: Optional[CreateUpdateOptions] = ..., 
                resource: TableResource, 
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


    class azure.mgmt.cosmosdb.models.TableGetPropertiesOptions(OptionsResource):
        autoscale_settings: AutoscaleSettings
        throughput: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                autoscale_settings: Optional[AutoscaleSettings] = ..., 
                throughput: Optional[int] = ..., 
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


    class azure.mgmt.cosmosdb.models.TableGetPropertiesResource(TableResource, ExtendedResourceProperties):
        create_mode: Union[str, CreateMode]
        etag: str
        id: str
        restore_parameters: ResourceRestoreParameters
        rid: str
        ts: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                create_mode: Union[str, CreateMode] = "Default", 
                id: str, 
                restore_parameters: Optional[ResourceRestoreParameters] = ..., 
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


    class azure.mgmt.cosmosdb.models.TableGetResults(ARMResourceProperties):
        id: str
        location: str
        name: str
        options: TableGetPropertiesOptions
        resource: TableGetPropertiesResource
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                options: Optional[TableGetPropertiesOptions] = ..., 
                resource: Optional[TableGetPropertiesResource] = ..., 
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


    class azure.mgmt.cosmosdb.models.TableListResult(Model):
        value: list[TableGetResults]

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


    class azure.mgmt.cosmosdb.models.TableResource(Model):
        create_mode: Union[str, CreateMode]
        id: str
        restore_parameters: ResourceRestoreParameters

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                create_mode: Union[str, CreateMode] = "Default", 
                id: str, 
                restore_parameters: Optional[ResourceRestoreParameters] = ..., 
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


    class azure.mgmt.cosmosdb.models.ThroughputPolicyResource(Model):
        increment_percent: int
        is_enabled: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                increment_percent: Optional[int] = ..., 
                is_enabled: Optional[bool] = ..., 
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


    class azure.mgmt.cosmosdb.models.ThroughputSettingsGetPropertiesResource(ThroughputSettingsResource, ExtendedResourceProperties):
        autoscale_settings: AutoscaleSettingsResource
        etag: str
        instant_maximum_throughput: str
        minimum_throughput: str
        offer_replace_pending: str
        rid: str
        soft_allowed_maximum_throughput: str
        throughput: int
        ts: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                autoscale_settings: Optional[AutoscaleSettingsResource] = ..., 
                throughput: Optional[int] = ..., 
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


    class azure.mgmt.cosmosdb.models.ThroughputSettingsGetResults(ARMResourceProperties):
        id: str
        location: str
        name: str
        resource: ThroughputSettingsGetPropertiesResource
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                resource: Optional[ThroughputSettingsGetPropertiesResource] = ..., 
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


    class azure.mgmt.cosmosdb.models.ThroughputSettingsResource(Model):
        autoscale_settings: AutoscaleSettingsResource
        instant_maximum_throughput: str
        minimum_throughput: str
        offer_replace_pending: str
        soft_allowed_maximum_throughput: str
        throughput: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                autoscale_settings: Optional[AutoscaleSettingsResource] = ..., 
                throughput: Optional[int] = ..., 
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


    class azure.mgmt.cosmosdb.models.ThroughputSettingsUpdateParameters(ARMResourceProperties):
        id: str
        location: str
        name: str
        resource: ThroughputSettingsResource
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                resource: ThroughputSettingsResource, 
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


    class azure.mgmt.cosmosdb.models.TrackedResource(ResourceAutoGenerated):
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


    class azure.mgmt.cosmosdb.models.UniqueKey(Model):
        paths: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                paths: Optional[list[str]] = ..., 
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


    class azure.mgmt.cosmosdb.models.UniqueKeyPolicy(Model):
        unique_keys: list[UniqueKey]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                unique_keys: Optional[list[UniqueKey]] = ..., 
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


    class azure.mgmt.cosmosdb.models.UnitType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BYTES = "Bytes"
        BYTES_PER_SECOND = "BytesPerSecond"
        COUNT = "Count"
        COUNT_PER_SECOND = "CountPerSecond"
        MILLISECONDS = "Milliseconds"
        PERCENT = "Percent"
        SECONDS = "Seconds"


    class azure.mgmt.cosmosdb.models.Usage(Model):
        current_value: int
        limit: int
        name: MetricName
        quota_period: str
        unit: Union[str, UnitType]

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


    class azure.mgmt.cosmosdb.models.UsagesResult(Model):
        value: list[Usage]

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


    class azure.mgmt.cosmosdb.models.VectorDataType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FLOAT16 = "float16"
        FLOAT32 = "float32"
        INT8 = "int8"
        UINT8 = "uint8"


    class azure.mgmt.cosmosdb.models.VectorEmbedding(Model):
        data_type: Union[str, VectorDataType]
        dimensions: int
        distance_function: Union[str, DistanceFunction]
        path: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                data_type: Union[str, VectorDataType], 
                dimensions: int, 
                distance_function: Union[str, DistanceFunction], 
                path: str, 
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


    class azure.mgmt.cosmosdb.models.VectorEmbeddingPolicy(Model):
        vector_embeddings: list[VectorEmbedding]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                vector_embeddings: Optional[list[VectorEmbedding]] = ..., 
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


    class azure.mgmt.cosmosdb.models.VectorIndex(Model):
        indexing_search_list_size: int
        path: str
        quantization_byte_size: int
        type: Union[str, VectorIndexType]
        vector_index_shard_key: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                indexing_search_list_size: int = 100, 
                path: str, 
                quantization_byte_size: Optional[int] = ..., 
                type: Union[str, VectorIndexType], 
                vector_index_shard_key: Optional[list[str]] = ..., 
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


    class azure.mgmt.cosmosdb.models.VectorIndexType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISK_ANN = "diskANN"
        FLAT = "flat"
        QUANTIZED_FLAT = "quantizedFlat"


    class azure.mgmt.cosmosdb.models.VirtualNetworkRule(Model):
        id: str
        ignore_missing_v_net_service_endpoint: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                ignore_missing_v_net_service_endpoint: Optional[bool] = ..., 
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
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommandOutput]: ...

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
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ClusterResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[ClusterResource]: ...

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
                create_update_cassandra_keyspace_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CassandraKeyspaceGetResults]: ...

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

        @distributed_trace
        def begin_delete_cassandra_keyspace(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
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
        def list_cassandra_keyspaces(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[CassandraKeyspaceGetResults]: ...

        @distributed_trace
        def list_cassandra_tables(
                self, 
                resource_group_name: str, 
                account_name: str, 
                keyspace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[CassandraTableGetResults]: ...


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
                filter: Optional[str] = None, 
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
                filter: Optional[str] = None, 
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
                filter: str, 
                **kwargs: Any
            ) -> ItemPaged[Metric]: ...


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
                filter: Optional[str] = None, 
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
                filter: str, 
                **kwargs: Any
            ) -> ItemPaged[Metric]: ...

        @distributed_trace
        def list_usages(
                self, 
                resource_group_name: str, 
                account_name: str, 
                database_rid: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> ItemPaged[Usage]: ...


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
                body: Optional[FleetResourceUpdate] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FleetResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                body: Optional[IO[bytes]] = None, 
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
                create_update_gremlin_graph_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GremlinGraphGetResults]: ...

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
                restorable_gremlin_database_rid: Optional[str] = None, 
                start_time: Optional[str] = None, 
                end_time: Optional[str] = None, 
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
                restore_location: Optional[str] = None, 
                restore_timestamp_in_utc: Optional[str] = None, 
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
                restorable_mongodb_database_rid: Optional[str] = None, 
                start_time: Optional[str] = None, 
                end_time: Optional[str] = None, 
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
                restore_location: Optional[str] = None, 
                restore_timestamp_in_utc: Optional[str] = None, 
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
                restorable_sql_database_rid: Optional[str] = None, 
                start_time: Optional[str] = None, 
                end_time: Optional[str] = None, 
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
                restore_location: Optional[str] = None, 
                restore_timestamp_in_utc: Optional[str] = None, 
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
                restore_location: Optional[str] = None, 
                restore_timestamp_in_utc: Optional[str] = None, 
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
                start_time: Optional[str] = None, 
                end_time: Optional[str] = None, 
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
                location: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BackupInformation]: ...

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
                create_update_table_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TableGetResults]: ...

        @distributed_trace
        def begin_delete_table(
                self, 
                resource_group_name: str, 
                account_name: str, 
                table_name: str, 
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
        def get_table_throughput(
                self, 
                resource_group_name: str, 
                account_name: str, 
                table_name: str, 
                **kwargs: Any
            ) -> ThroughputSettingsGetResults: ...

        @distributed_trace
        def list_tables(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[TableGetResults]: ...


```