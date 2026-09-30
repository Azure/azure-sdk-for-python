# Release History

## 10.0.0b6 (2026-05-06)

### Features Added

  - Client `CosmosDBManagementClient` added parameter `cloud_setting` in method `__init__`
  - Client `CosmosDBManagementClient` added method `send_request`
  - Client `CosmosDBManagementClient` added operation group `copy_jobs`
  - Client `CosmosDBManagementClient` added operation group `garnet_clusters`
  - Client `CosmosDBManagementClient` added operation group `mongo_mi_resources`
  - Client `CosmosDBManagementClient` added operation group `fleet`
  - Client `CosmosDBManagementClient` added operation group `fleet_analytics`
  - Client `CosmosDBManagementClient` added operation group `fleetspace`
  - Client `CosmosDBManagementClient` added operation group `fleetspace_account`
  - Model `CassandraKeyspaceGetResults` added property `system_data`
  - Model `CassandraTableGetResults` added property `system_data`
  - Model `CassandraViewGetResults` added property `system_data`
  - Model `ClientEncryptionKeyGetResults` added property `system_data`
  - Model `ClusterResource` added property `system_data`
  - Model `DataCenterResource` added property `system_data`
  - Enum `DataTransferComponent` added member `BASE_COSMOS_DATA_TRANSFER_DATA_SOURCE_SINK`
  - Model `DataTransferJobGetResults` added property `system_data`
  - Model `GraphResourceGetResults` added property `system_data`
  - Model `GremlinDatabaseGetResults` added property `system_data`
  - Model `GremlinGraphGetResults` added property `system_data`
  - Model `IndexingPolicy` added property `full_text_indexes`
  - Model `LocationGetResult` added property `system_data`
  - Model `MaterializedViewDefinition` added property `throughput_bucket_for_build`
  - Model `MongoDBCollectionGetResults` added property `system_data`
  - Model `MongoDBDatabaseGetResults` added property `system_data`
  - Model `MongoRoleDefinitionGetResults` added property `system_data`
  - Model `MongoUserDefinitionGetResults` added property `system_data`
  - Model `NotebookWorkspace` added property `system_data`
  - Model `Permission` added property `id`
  - Model `PhysicalPartitionThroughputInfoResource` added property `target_throughput`
  - Model `PrivateLinkResource` added property `system_data`
  - Model `RestorableDatabaseAccountGetResult` added property `system_data`
  - Model `RestorableSqlContainerPropertiesResourceContainer` added property `materialized_views`
  - Model `RestorableSqlContainerPropertiesResourceContainer` added property `materialized_views_properties`
  - Model `RestorableSqlContainerPropertiesResourceContainer` added property `full_text_policy`
  - Model `RestorableSqlContainerPropertiesResourceContainer` added property `data_masking_policy`
  - Model `ServiceResource` added property `system_data`
  - Model `SqlContainerGetPropertiesResource` added property `materialized_views`
  - Model `SqlContainerGetPropertiesResource` added property `materialized_views_properties`
  - Model `SqlContainerGetPropertiesResource` added property `full_text_policy`
  - Model `SqlContainerGetPropertiesResource` added property `data_masking_policy`
  - Model `SqlContainerGetResults` added property `system_data`
  - Model `SqlContainerResource` added property `materialized_views`
  - Model `SqlContainerResource` added property `materialized_views_properties`
  - Model `SqlContainerResource` added property `full_text_policy`
  - Model `SqlContainerResource` added property `data_masking_policy`
  - Model `SqlDatabaseGetResults` added property `system_data`
  - Model `SqlRoleAssignmentGetResults` added property `system_data`
  - Model `SqlRoleDefinitionGetResults` added property `system_data`
  - Model `SqlStoredProcedureGetResults` added property `system_data`
  - Model `SqlTriggerGetResults` added property `system_data`
  - Model `SqlUserDefinedFunctionGetResults` added property `system_data`
  - Enum `Status` added member `CREATING`
  - Model `TableGetResults` added property `system_data`
  - Model `ThroughputBucketResource` added property `is_default_bucket`
  - Model `ThroughputSettingsGetResults` added property `system_data`
  - Enum `VectorDataType` added member `FLOAT16`
  - Model `VectorIndex` added property `quantization_byte_size`
  - Model `VectorIndex` added property `indexing_search_list_size`
  - Model `VectorIndex` added property `vector_index_shard_key`
  - Added enum `AllocationState`
  - Added model `AzureBlobContainer`
  - Added model `AzureBlobSourceSinkDetails`
  - Added model `BaseCopyJobProperties`
  - Added model `BaseCopyJobTask`
  - Added model `BlobToCassandraRUCopyJobProperties`
  - Added model `BlobToCassandraRUCopyJobTask`
  - Added model `CassandraRUToBlobCopyJobProperties`
  - Added model `CassandraRUToBlobCopyJobTask`
  - Added model `CassandraRUToCassandraRUCopyJobProperties`
  - Added model `CassandraRUToCassandraRUCopyJobTask`
  - Added model `CassandraRoleAssignmentResource`
  - Added model `CassandraRoleAssignmentResourceProperties`
  - Added model `CassandraRoleDefinitionResource`
  - Added model `CassandraRoleDefinitionResourceProperties`
  - Added model `CloudError`
  - Added model `CopyJobGetResults`
  - Added enum `CopyJobMode`
  - Added model `CopyJobProperties`
  - Added enum `CopyJobStatus`
  - Added enum `CopyJobType`
  - Added model `CosmosDBCassandraTable`
  - Added model `CosmosDBMongoCollection`
  - Added model `CosmosDBMongoVCoreCollection`
  - Added model `CosmosDBNoSqlContainer`
  - Added model `CosmosDBSourceSinkDetails`
  - Added model `DataMaskingPolicy`
  - Added model `DataMaskingPolicyExcludedPathsItem`
  - Added model `DataMaskingPolicyIncludedPathsItem`
  - Added model `FleetAnalyticsProperties`
  - Added enum `FleetAnalyticsPropertiesStorageLocationType`
  - Added model `FleetAnalyticsResource`
  - Added model `FleetResource`
  - Added model `FleetResourceProperties`
  - Added model `FleetResourceUpdate`
  - Added model `FleetspaceAccountProperties`
  - Added model `FleetspaceAccountPropertiesGlobalDatabaseAccountProperties`
  - Added model `FleetspaceAccountResource`
  - Added model `FleetspaceProperties`
  - Added enum `FleetspacePropertiesFleetspaceApiKind`
  - Added enum `FleetspacePropertiesServiceTier`
  - Added model `FleetspacePropertiesThroughputPoolConfiguration`
  - Added model `FleetspaceResource`
  - Added model `FleetspaceUpdate`
  - Added model `FullTextIndexPath`
  - Added model `FullTextPath`
  - Added model `FullTextPolicy`
  - Added enum `GarnetCacheProvisioningState`
  - Added model `GarnetClusterResource`
  - Added model `GarnetClusterResourcePatch`
  - Added model `GarnetClusterResourcePatchProperties`
  - Added model `GarnetClusterResourceProperties`
  - Added model `GarnetClusterResourcePropertiesEndPointsItem`
  - Added model `GremlinRoleAssignmentResource`
  - Added model `GremlinRoleAssignmentResourceProperties`
  - Added model `GremlinRoleDefinitionResource`
  - Added model `GremlinRoleDefinitionResourceProperties`
  - Added model `MaterializedViewDetails`
  - Added model `MaterializedViewsProperties`
  - Added model `MongoMIRoleAssignmentResource`
  - Added model `MongoMIRoleAssignmentResourceProperties`
  - Added model `MongoMIRoleDefinitionResource`
  - Added model `MongoMIRoleDefinitionResourceProperties`
  - Added model `MongoRUToMongoRUCopyJobProperties`
  - Added model `MongoRUToMongoRUCopyJobTask`
  - Added model `MongoRUToMongoVCoreCopyJobProperties`
  - Added model `MongoRUToMongoVCoreCopyJobTask`
  - Added model `MongoRoleDefinitionResource`
  - Added model `MongoUserDefinitionResource`
  - Added model `MongoVCoreSourceSinkDetails`
  - Added model `NoSqlRUToNoSqlRUCopyJobProperties`
  - Added model `NoSqlRUToNoSqlRUCopyJobTask`
  - Added model `SqlRoleAssignmentResource`
  - Added model `SqlRoleDefinitionResource`
  - Operation group `CassandraResourcesOperations` added method `begin_create_update_cassandra_role_assignment`
  - Operation group `CassandraResourcesOperations` added method `begin_create_update_cassandra_role_definition`
  - Operation group `CassandraResourcesOperations` added method `begin_delete_cassandra_role_assignment`
  - Operation group `CassandraResourcesOperations` added method `begin_delete_cassandra_role_definition`
  - Operation group `CassandraResourcesOperations` added method `get_cassandra_role_assignment`
  - Operation group `CassandraResourcesOperations` added method `get_cassandra_role_definition`
  - Operation group `CassandraResourcesOperations` added method `list_cassandra_role_assignments`
  - Operation group `CassandraResourcesOperations` added method `list_cassandra_role_definitions`
  - Operation group `GremlinResourcesOperations` added method `begin_create_update_gremlin_role_assignment`
  - Operation group `GremlinResourcesOperations` added method `begin_create_update_gremlin_role_definition`
  - Operation group `GremlinResourcesOperations` added method `begin_delete_gremlin_role_assignment`
  - Operation group `GremlinResourcesOperations` added method `begin_delete_gremlin_role_definition`
  - Operation group `GremlinResourcesOperations` added method `get_gremlin_role_assignment`
  - Operation group `GremlinResourcesOperations` added method `get_gremlin_role_definition`
  - Operation group `GremlinResourcesOperations` added method `list_gremlin_role_assignments`
  - Operation group `GremlinResourcesOperations` added method `list_gremlin_role_definitions`
  - Added operation group `CopyJobsOperations`
  - Added operation group `FleetAnalyticsOperations`
  - Added operation group `FleetOperations`
  - Added operation group `FleetspaceAccountOperations`
  - Added operation group `FleetspaceOperations`
  - Added operation group `GarnetClustersOperations`
  - Added operation group `MongoMIResourcesOperations`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. Please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - For the method breakings, please refer to https://aka.ms/azsdk/python/migrate/operations for migration.
  - Model `CassandraKeyspaceCreateUpdateParameters` moved instance variable `resource`, `options` under property `properties` whose type is `CassandraKeyspaceCreateUpdateProperties`
  - Model `CassandraKeyspaceGetResults` moved instance variable `resource`, `options` under property `properties` whose type is `CassandraKeyspaceGetProperties`
  - Model `CassandraTableCreateUpdateParameters` moved instance variable `resource`, `options` under property `properties` whose type is `CassandraTableCreateUpdateProperties`
  - Model `CassandraTableGetResults` moved instance variable `resource`, `options` under property `properties` whose type is `CassandraTableGetProperties`
  - Model `CassandraViewCreateUpdateParameters` moved instance variable `resource`, `options` under property `properties` whose type is `CassandraViewCreateUpdateProperties`
  - Model `CassandraViewGetResults` moved instance variable `resource`, `options` under property `properties` whose type is `CassandraViewGetProperties`
  - Model `ChaosFaultResource` moved instance variable `action`, `region`, `database_name`, `container_name`, `provisioning_state` under property `properties` whose type is `ChaosFaultProperties`
  - Model `ClientEncryptionKeyCreateUpdateParameters` moved instance variable `resource` under property `properties` whose type is `ClientEncryptionKeyCreateUpdateProperties`
  - Model `ClientEncryptionKeyGetResults` moved instance variable `resource` under property `properties` whose type is `ClientEncryptionKeyGetProperties`
  - Model `DataTransferJobGetResults` moved instance variable `job_name`, `source`, `destination`, `status`, `processed_count`, `total_count`, `last_updated_utc_time`, `worker_count`, `error`, `duration`, `mode` under property `properties` whose type is `DataTransferJobProperties`
  - Model `DatabaseAccountCreateUpdateParameters` moved instance variable `consistency_policy`, `locations`, `ip_rules`, `is_virtual_network_filter_enabled`, `enable_automatic_failover`, `capabilities`, `virtual_network_rules`, `enable_multiple_write_locations`, `enable_cassandra_connector`, `connector_offer`, `disable_key_based_metadata_write_access`, `key_vault_key_uri`, `default_identity`, `public_network_access`, `enable_free_tier`, `api_properties`, `enable_analytical_storage`, `analytical_storage_configuration`, `create_mode`, `backup_policy`, `cors`, `network_acl_bypass`, `network_acl_bypass_resource_ids`, `diagnostic_log_settings`, `disable_local_auth`, `restore_parameters`, `capacity`, `capacity_mode`, `enable_materialized_views`, `keys_metadata`, `enable_partition_merge`, `enable_burst_capacity`, `minimal_tls_version`, `customer_managed_key_status`, `enable_priority_based_execution`, `default_priority_level`, `enable_per_region_per_partition_autoscale` under property `properties` whose type is `DatabaseAccountCreateUpdateProperties`
  - Model `DatabaseAccountGetResults` moved instance variable `provisioning_state`, `document_endpoint`, `database_account_offer_type`, `ip_rules`, `is_virtual_network_filter_enabled`, `enable_automatic_failover`, `consistency_policy`, `capabilities`, `write_locations`, `read_locations`, `locations`, `failover_policies`, `virtual_network_rules`, `private_endpoint_connections`, `enable_multiple_write_locations`, `enable_cassandra_connector`, `connector_offer`, `disable_key_based_metadata_write_access`, `key_vault_key_uri`, `default_identity`, `public_network_access`, `enable_free_tier`, `api_properties`, `enable_analytical_storage`, `analytical_storage_configuration`, `instance_id`, `create_mode`, `restore_parameters`, `backup_policy`, `cors`, `network_acl_bypass`, `network_acl_bypass_resource_ids`, `diagnostic_log_settings`, `disable_local_auth`, `capacity`, `capacity_mode`, `capacity_mode_change_transition_state`, `enable_materialized_views`, `keys_metadata`, `enable_partition_merge`, `enable_burst_capacity`, `minimal_tls_version`, `customer_managed_key_status`, `enable_priority_based_execution`, `default_priority_level`, `enable_per_region_per_partition_autoscale` under property `properties` whose type is `DatabaseAccountGetProperties`
  - Model `DatabaseAccountUpdateParameters` moved instance variable `consistency_policy`, `locations`, `ip_rules`, `is_virtual_network_filter_enabled`, `enable_automatic_failover`, `capabilities`, `virtual_network_rules`, `enable_multiple_write_locations`, `enable_cassandra_connector`, `connector_offer`, `disable_key_based_metadata_write_access`, `key_vault_key_uri`, `default_identity`, `public_network_access`, `enable_free_tier`, `api_properties`, `enable_analytical_storage`, `analytical_storage_configuration`, `backup_policy`, `cors`, `network_acl_bypass`, `network_acl_bypass_resource_ids`, `diagnostic_log_settings`, `disable_local_auth`, `capacity`, `capacity_mode`, `enable_materialized_views`, `keys_metadata`, `enable_partition_merge`, `enable_burst_capacity`, `minimal_tls_version`, `customer_managed_key_status`, `enable_priority_based_execution`, `default_priority_level`, `enable_per_region_per_partition_autoscale` under property `properties` whose type is `DatabaseAccountUpdateProperties`
  - Model `GraphResourceCreateUpdateParameters` moved instance variable `resource`, `options` under property `properties` whose type is `GraphResourceCreateUpdateProperties`
  - Model `GraphResourceGetResults` moved instance variable `resource`, `options` under property `properties` whose type is `GraphResourceGetProperties`
  - Model `GremlinDatabaseCreateUpdateParameters` moved instance variable `resource`, `options` under property `properties` whose type is `GremlinDatabaseCreateUpdateProperties`
  - Model `GremlinDatabaseGetResults` moved instance variable `resource`, `options` under property `properties` whose type is `GremlinDatabaseGetProperties`
  - Model `GremlinGraphCreateUpdateParameters` moved instance variable `resource`, `options` under property `properties` whose type is `GremlinGraphCreateUpdateProperties`
  - Model `GremlinGraphGetResults` moved instance variable `resource`, `options` under property `properties` whose type is `GremlinGraphGetProperties`
  - Model `MongoDBCollectionCreateUpdateParameters` moved instance variable `resource`, `options` under property `properties` whose type is `MongoDBCollectionCreateUpdateProperties`
  - Model `MongoDBCollectionGetResults` moved instance variable `resource`, `options` under property `properties` whose type is `MongoDBCollectionGetProperties`
  - Model `MongoDBDatabaseCreateUpdateParameters` moved instance variable `resource`, `options` under property `properties` whose type is `MongoDBDatabaseCreateUpdateProperties`
  - Model `MongoDBDatabaseGetResults` moved instance variable `resource`, `options` under property `properties` whose type is `MongoDBDatabaseGetProperties`
  - Model `MongoIndexKeys` deleted or renamed its instance variable `keys`
  - Model `MongoRoleDefinitionCreateUpdateParameters` moved instance variable `role_name`, `type`, `database_name`, `privileges`, `roles` under property `properties` whose type is `MongoRoleDefinitionResource`
  - Model `MongoRoleDefinitionGetResults` moved instance variable `role_name`, `type_properties_type`, `database_name`, `privileges`, `roles` under property `properties` whose type is `MongoRoleDefinitionResource`
  - Model `MongoUserDefinitionCreateUpdateParameters` moved instance variable `user_name`, `password`, `database_name`, `custom_data`, `roles`, `mechanisms` under property `properties` whose type is `MongoUserDefinitionResource`
  - Model `MongoUserDefinitionGetResults` moved instance variable `user_name`, `password`, `database_name`, `custom_data`, `roles`, `mechanisms` under property `properties` whose type is `MongoUserDefinitionResource`
  - Model `RedistributeThroughputParameters` moved instance variable `resource` under property `properties` whose type is `RedistributeThroughputProperties`
  - Model `RestorableDatabaseAccountGetResult` moved instance variable `account_name`, `creation_time`, `oldest_restorable_time`, `deletion_time`, `api_type`, `restorable_locations` under property `properties` whose type is `RestorableDatabaseAccountProperties`
  - Model `RestorableGremlinDatabaseGetResult` moved instance variable `resource` under property `properties` whose type is `RestorableGremlinDatabaseProperties`
  - Model `RestorableGremlinGraphGetResult` moved instance variable `resource` under property `properties` whose type is `RestorableGremlinGraphProperties`
  - Model `RestorableMongodbCollectionGetResult` moved instance variable `resource` under property `properties` whose type is `RestorableMongodbCollectionProperties`
  - Model `RestorableMongodbDatabaseGetResult` moved instance variable `resource` under property `properties` whose type is `RestorableMongodbDatabaseProperties`
  - Model `RestorableSqlContainerGetResult` moved instance variable `resource` under property `properties` whose type is `RestorableSqlContainerProperties`
  - Model `RestorableSqlDatabaseGetResult` moved instance variable `resource` under property `properties` whose type is `RestorableSqlDatabaseProperties`
  - Model `RestorableTableGetResult` moved instance variable `resource` under property `properties` whose type is `RestorableTableProperties`
  - Model `RetrieveThroughputParameters` moved instance variable `resource` under property `properties` whose type is `RetrieveThroughputProperties`
  - Model `SqlContainerCreateUpdateParameters` moved instance variable `resource`, `options` under property `properties` whose type is `SqlContainerCreateUpdateProperties`
  - Model `SqlContainerGetResults` moved instance variable `resource`, `options` under property `properties` whose type is `SqlContainerGetProperties`
  - Model `SqlDatabaseCreateUpdateParameters` moved instance variable `resource`, `options` under property `properties` whose type is `SqlDatabaseCreateUpdateProperties`
  - Model `SqlDatabaseGetResults` moved instance variable `resource`, `options` under property `properties` whose type is `SqlDatabaseGetProperties`
  - Model `SqlRoleAssignmentCreateUpdateParameters` moved instance variable `role_definition_id`, `scope`, `principal_id` under property `properties` whose type is `SqlRoleAssignmentResource`
  - Model `SqlRoleAssignmentGetResults` moved instance variable `role_definition_id`, `scope`, `principal_id` under property `properties` whose type is `SqlRoleAssignmentResource`
  - Model `SqlRoleDefinitionCreateUpdateParameters` moved instance variable `role_name`, `type`, `assignable_scopes`, `permissions` under property `properties` whose type is `SqlRoleDefinitionResource`
  - Model `SqlRoleDefinitionGetResults` moved instance variable `role_name`, `type_properties_type`, `assignable_scopes`, `permissions` under property `properties` whose type is `SqlRoleDefinitionResource`
  - Model `SqlStoredProcedureCreateUpdateParameters` moved instance variable `resource`, `options` under property `properties` whose type is `SqlStoredProcedureCreateUpdateProperties`
  - Model `SqlStoredProcedureGetResults` moved instance variable `resource` under property `properties` whose type is `SqlStoredProcedureGetProperties`
  - Model `SqlTriggerCreateUpdateParameters` moved instance variable `resource`, `options` under property `properties` whose type is `SqlTriggerCreateUpdateProperties`
  - Model `SqlTriggerGetResults` moved instance variable `resource` under property `properties` whose type is `SqlTriggerGetProperties`
  - Model `SqlUserDefinedFunctionCreateUpdateParameters` moved instance variable `resource`, `options` under property `properties` whose type is `SqlUserDefinedFunctionCreateUpdateProperties`
  - Model `SqlUserDefinedFunctionGetResults` moved instance variable `resource` under property `properties` whose type is `SqlUserDefinedFunctionGetProperties`
  - Model `TableCreateUpdateParameters` moved instance variable `resource`, `options` under property `properties` whose type is `TableCreateUpdateProperties`
  - Model `TableGetResults` moved instance variable `resource`, `options` under property `properties` whose type is `TableGetProperties`
  - Model `ThroughputPoolAccountResource` moved instance variable `provisioning_state`, `account_resource_identifier`, `account_location`, `account_instance_id` under property `properties` whose type is `ThroughputPoolAccountProperties`
  - Model `ThroughputPoolResource` moved instance variable `provisioning_state`, `max_throughput` under property `properties` whose type is `ThroughputPoolProperties`
  - Model `ThroughputPoolUpdate` moved instance variable `provisioning_state`, `max_throughput` under property `properties` whose type is `ThroughputPoolProperties`
  - Model `ThroughputSettingsGetResults` moved instance variable `resource` under property `properties` whose type is `ThroughputSettingsGetProperties`
  - Model `ThroughputSettingsUpdateParameters` moved instance variable `resource` under property `properties` whose type is `ThroughputSettingsUpdateProperties`
  - Deleted or renamed model `DataTransferServiceResource`
  - Deleted or renamed model `ExtendedResourceProperties`
  - Deleted or renamed model `GraphAPIComputeServiceResource`
  - Deleted or renamed model `ManagedCassandraARMResourceProperties`
  - Deleted or renamed model `MaterializedViewsBuilderServiceResource`
  - Deleted or renamed model `NodeStatus`
  - Deleted or renamed model `PermissionAutoGenerated`
  - Deleted or renamed model `SqlDedicatedGatewayServiceResource`
  - Deleted or renamed model `ThroughputPoolAccountCreateParameters`
  - Method `CassandraClustersOperations.begin_deallocate` changed its parameter `x_ms_force_deallocate` from `positional_or_keyword` to `keyword_only`
  - Method `RestorableGremlinGraphsOperations.list` changed its parameter `restorable_gremlin_database_rid`, `start_time`, `end_time` from `positional_or_keyword` to `keyword_only`
  - Method `RestorableGremlinResourcesOperations.list` changed its parameter `restore_location`, `restore_timestamp_in_utc` from `positional_or_keyword` to `keyword_only`
  - Method `RestorableMongodbCollectionsOperations.list` changed its parameter `restorable_mongodb_database_rid`, `start_time`, `end_time` from `positional_or_keyword` to `keyword_only`
  - Method `RestorableMongodbResourcesOperations.list` changed its parameter `restore_location`, `restore_timestamp_in_utc` from `positional_or_keyword` to `keyword_only`
  - Method `RestorableSqlContainersOperations.list` changed its parameter `restorable_sql_database_rid`, `start_time`, `end_time` from `positional_or_keyword` to `keyword_only`
  - Method `RestorableSqlResourcesOperations.list` changed its parameter `restore_location`, `restore_timestamp_in_utc` from `positional_or_keyword` to `keyword_only`
  - Method `RestorableTableResourcesOperations.list` changed its parameter `restore_location`, `restore_timestamp_in_utc` from `positional_or_keyword` to `keyword_only`
  - Method `RestorableTablesOperations.list` changed its parameter `start_time`, `end_time` from `positional_or_keyword` to `keyword_only`

### Other Changes

  - Deleted model `ChaosFaultListResponse`/`DataTransferJobFeedResults`/`ListBackups`/`ListClusters`/`ListCommands`/`ListDataCenters`/`PartitionUsagesResult`/`UsagesResult` which actually were not used by SDK users

## 9.9.0 (2025-11-14)

### Features Added

  - Model `CosmosDBManagementClient` added parameter `cloud_setting` in method `__init__`
  - Client `CosmosDBManagementClient` added operation group `fleet`
  - Client `CosmosDBManagementClient` added operation group `fleetspace`
  - Client `CosmosDBManagementClient` added operation group `fleetspace_account`
  - Model `DatabaseAccountCreateUpdateParameters` added property `enable_priority_based_execution`
  - Model `DatabaseAccountCreateUpdateParameters` added property `default_priority_level`
  - Model `DatabaseAccountGetResults` added property `key_vault_key_uri_version`
  - Model `DatabaseAccountGetResults` added property `enable_priority_based_execution`
  - Model `DatabaseAccountGetResults` added property `default_priority_level`
  - Model `DatabaseAccountUpdateParameters` added property `enable_priority_based_execution`
  - Model `DatabaseAccountUpdateParameters` added property `default_priority_level`
  - Model `IndexingPolicy` added property `full_text_indexes`
  - Model `RestoreParameters` added property `source_backup_location`
  - Enum `Status` added member `CANCELED`
  - Enum `Status` added member `CREATING`
  - Enum `Status` added member `FAILED`
  - Enum `Status` added member `SUCCEEDED`
  - Enum `Status` added member `UPDATING`
  - Enum `VectorDataType` added member `FLOAT16`
  - Model `VectorIndex` added property `quantization_byte_size`
  - Model `VectorIndex` added property `indexing_search_list_size`
  - Model `VectorIndex` added property `vector_index_shard_key`
  - Added enum `DefaultPriorityLevel`
  - Added model `ErrorDetailAutoGenerated`
  - Added model `ErrorResponseAutoGenerated2`
  - Added model `FleetListResult`
  - Added model `FleetResource`
  - Added model `FleetResourceUpdate`
  - Added model `FleetspaceAccountListResult`
  - Added model `FleetspaceAccountPropertiesGlobalDatabaseAccountProperties`
  - Added model `FleetspaceAccountResource`
  - Added model `FleetspaceListResult`
  - Added enum `FleetspacePropertiesFleetspaceApiKind`
  - Added enum `FleetspacePropertiesServiceTier`
  - Added model `FleetspacePropertiesThroughputPoolConfiguration`
  - Added model `FleetspaceResource`
  - Added model `FleetspaceUpdate`
  - Added model `FullTextIndexPath`
  - Added model `ProxyResourceAutoGenerated`
  - Added model `ResourceAutoGenerated`
  - Added model `TrackedResource`
  - Added operation group `FleetOperations`
  - Added operation group `FleetspaceAccountOperations`
  - Added operation group `FleetspaceOperations`

## 9.8.0 (2025-05-07)

### Features Added

  - Model `RestorableSqlContainerPropertiesResourceContainer` added property `full_text_policy`
  - Model `SqlContainerGetPropertiesResource` added property `full_text_policy`
  - Model `SqlContainerResource` added property `full_text_policy`
  - Added model `FullTextPath`
  - Added model `FullTextPolicy`

## 10.0.0b5 (2024-12-23)

### Features Added

  - Model `CommandPostBody` added property `readwrite`
  - Model `ErrorResponse` added property `error`
  - Model `ErrorResponseAutoGenerated` added property `code`
  - Model `ErrorResponseAutoGenerated` added property `message`
  - Model `IndexingPolicy` added property `vector_indexes`
  - Model `RestorableSqlContainerPropertiesResourceContainer` added property `vector_embedding_policy`
  - Model `SqlContainerGetPropertiesResource` added property `vector_embedding_policy`
  - Model `SqlContainerResource` added property `vector_embedding_policy`
  - Model `ThroughputSettingsGetPropertiesResource` added property `throughput_buckets`
  - Model `ThroughputSettingsResource` added property `throughput_buckets`
  - Added model `CommandAsyncPostBody`
  - Added enum `DistanceFunction`
  - Added model `PermissionAutoGenerated`
  - Added model `TableRoleAssignmentListResult`
  - Added model `TableRoleAssignmentResource`
  - Added model `TableRoleDefinitionListResult`
  - Added model `TableRoleDefinitionResource`
  - Added model `ThroughputBucketResource`
  - Added enum `VectorDataType`
  - Added model `VectorEmbedding`
  - Added model `VectorEmbeddingPolicy`
  - Added model `VectorIndex`
  - Added enum `VectorIndexType`
  - Operation group `TableResourcesOperations` added method `begin_create_update_table_role_assignment`
  - Operation group `TableResourcesOperations` added method `begin_create_update_table_role_definition`
  - Operation group `TableResourcesOperations` added method `begin_delete_table_role_assignment`
  - Operation group `TableResourcesOperations` added method `begin_delete_table_role_definition`
  - Operation group `TableResourcesOperations` added method `get_table_role_assignment`
  - Operation group `TableResourcesOperations` added method `get_table_role_definition`
  - Operation group `TableResourcesOperations` added method `list_table_role_assignments`
  - Operation group `TableResourcesOperations` added method `list_table_role_definitions`

### Breaking Changes

  - Model `CommandPostBody` deleted or renamed its instance variable `read_write`
  - Model `ErrorResponse` deleted or renamed its instance variable `code`
  - Model `ErrorResponse` deleted or renamed its instance variable `message`
  - Model `ErrorResponseAutoGenerated` deleted or renamed its instance variable `error`

## 9.7.0 (2024-11-18)

### Features Added

  - Model `DatabaseAccountCreateUpdateParameters` added property `enable_per_region_per_partition_autoscale`
  - Model `DatabaseAccountGetResults` added property `enable_per_region_per_partition_autoscale`
  - Model `DatabaseAccountUpdateParameters` added property `enable_per_region_per_partition_autoscale`
  - Model `IndexingPolicy` added property `vector_indexes`
  - Model `RestorableSqlContainerPropertiesResourceContainer` added property `vector_embedding_policy`
  - Model `SqlContainerGetPropertiesResource` added property `vector_embedding_policy`
  - Model `SqlContainerResource` added property `vector_embedding_policy`
  - Added enum `DistanceFunction`
  - Added enum `VectorDataType`
  - Added model `VectorEmbedding`
  - Added model `VectorEmbeddingPolicy`
  - Added model `VectorIndex`
  - Added enum `VectorIndexType`

## 10.0.0b4 (2024-09-23)

### Features Added

  - Client `CosmosDBManagementClient` added operation group `network_security_perimeter_configurations`
  - Client `CosmosDBManagementClient` added operation group `chaos_fault`
  - Enum `DataTransferComponent` added member `COSMOS_DB_MONGO_V_CORE`
  - Model `DatabaseAccountCreateUpdateParameters` added property `capacity_mode`
  - Model `DatabaseAccountGetResults` added property `capacity_mode`
  - Model `DatabaseAccountGetResults` added property `capacity_mode_change_transition_state`
  - Model `DatabaseAccountUpdateParameters` added property `capacity_mode`
  - Enum `ServerVersion` added member `FIVE0`
  - Enum `ServerVersion` added member `SEVEN0`
  - Enum `ServerVersion` added member `SIX0`
  - Model `ServiceResourceCreateUpdateParameters` added parameter `properties` in method `__init__`
  - Model `SqlDedicatedGatewayServiceResourceProperties` added property `dedicated_gateway_type`
  - Added model `AccessRule`
  - Added enum `AccessRuleDirection`
  - Added model `AccessRuleProperties`
  - Added model `AccessRulePropertiesSubscriptionsItem`
  - Added enum `CapacityMode`
  - Added model `CapacityModeChangeTransitionState`
  - Added enum `CapacityModeTransitionStatus`
  - Added model `ChaosFaultListResponse`
  - Added model `ChaosFaultResource`
  - Added model `CosmosMongoVCoreDataTransferDataSourceSink`
  - Added model `DataTransferServiceResourceCreateUpdateProperties`
  - Added enum `DedicatedGatewayType`
  - Added model `GraphAPIComputeServiceResourceCreateUpdateProperties`
  - Added enum `IssueType`
  - Added model `MaterializedViewsBuilderServiceResourceCreateUpdateProperties`
  - Added model `NetworkSecurityPerimeter`
  - Added model `NetworkSecurityPerimeterConfiguration`
  - Added model `NetworkSecurityPerimeterConfigurationListResult`
  - Added model `NetworkSecurityPerimeterConfigurationProperties`
  - Added enum `NetworkSecurityPerimeterConfigurationProvisioningState`
  - Added model `NetworkSecurityProfile`
  - Added model `ProvisioningIssue`
  - Added model `ProvisioningIssueProperties`
  - Added model `ResourceAssociation`
  - Added enum `ResourceAssociationAccessMode`
  - Added model `ServiceResourceCreateUpdateProperties`
  - Added enum `Severity`
  - Added model `SqlDedicatedGatewayServiceResourceCreateUpdateProperties`
  - Added enum `SupportedActions`
  - Added model `ChaosFaultOperations`
  - Added model `NetworkSecurityPerimeterConfigurationsOperations`

### Breaking Changes

  - Deleted or renamed client operation group `CosmosDBManagementClient.mongo_clusters`
  - Deleted or renamed enum value `CreateMode.POINT_IN_TIME_RESTORE`
  - Model `ServiceResourceCreateUpdateParameters` deleted or renamed its instance variable `instance_size`
  - Model `ServiceResourceCreateUpdateParameters` deleted or renamed its instance variable `instance_count`
  - Model `ServiceResourceCreateUpdateParameters` deleted or renamed its instance variable `service_type`
  - Deleted or renamed model `CheckNameAvailabilityReason`
  - Deleted or renamed model `CheckNameAvailabilityRequest`
  - Deleted or renamed model `CheckNameAvailabilityResponse`
  - Deleted or renamed model `ConnectionString`
  - Deleted or renamed model `FirewallRule`
  - Deleted or renamed model `ListConnectionStringsResult`
  - Deleted or renamed model `MongoCluster`
  - Deleted or renamed model `MongoClusterRestoreParameters`
  - Deleted or renamed model `MongoClusterStatus`
  - Deleted or renamed model `MongoClusterUpdate`
  - Deleted or renamed model `NodeGroupProperties`
  - Deleted or renamed model `NodeGroupSpec`
  - Deleted or renamed model `NodeKind`
  - Deleted or renamed model `ProvisioningState`
  - Deleted or renamed model `MongoClustersOperations`

## 9.6.0 (2024-09-18)

### Features Added

  - Model `ResourceRestoreParameters` added property `restore_with_ttl_disabled`
  - Model `RestoreParameters` added parameter `restore_with_ttl_disabled` in method `__init__`
  - Model `RestoreParametersBase` added property `restore_with_ttl_disabled`
  - Enum `ServerVersion` added member `SEVEN0`
  - Added model `ErrorAdditionalInfo`
  - Added model `ErrorDetail`
  - Added model `ErrorResponseAutoGenerated`

## 9.5.1 (2024-06-19)

### Features Added

  - Model ServiceResourceCreateUpdateParameters has a new parameter properties

### Breaking Changes

  - Model ServiceResourceCreateUpdateParameters no longer has parameter instance_count
  - Model ServiceResourceCreateUpdateParameters no longer has parameter instance_size
  - Model ServiceResourceCreateUpdateParameters no longer has parameter service_type

### Bugs Fixed

  - Disable parameter flatten for Model ServiceResourceCreateUpdateParameters to avoid deserializatin

## 9.5.0 (2024-05-20)

### Features Added

  - Model ClusterResourceProperties has a new parameter azure_connection_method
  - Model ClusterResourceProperties has a new parameter private_link_resource_id
  - Model DataCenterResourceProperties has a new parameter private_endpoint_ip_address
  - Model SqlDedicatedGatewayServiceResourceProperties has a new parameter dedicated_gateway_type

## 10.0.0b3 (2024-03-18)

### Features Added

  - Added operation DataTransferJobsOperations.complete
  - Model DatabaseAccountCreateUpdateParameters has a new parameter enable_per_region_per_partition_autoscale
  - Model DatabaseAccountGetResults has a new parameter enable_per_region_per_partition_autoscale
  - Model DatabaseAccountUpdateParameters has a new parameter enable_per_region_per_partition_autoscale
  - Model PrivateEndpointConnection has a new parameter system_data
  - Model ProxyResource has a new parameter system_data
  - Model Resource has a new parameter system_data
  - Model ResourceRestoreParameters has a new parameter restore_with_ttl_disabled
  - Model RestoreParameters has a new parameter restore_with_ttl_disabled
  - Model RestoreParametersBase has a new parameter restore_with_ttl_disabled

## 10.0.0b2 (2024-01-26)

### Features Added

  - Added operation CassandraClustersOperations.begin_invoke_command_async
  - Added operation CassandraClustersOperations.get_command_async
  - Added operation CassandraClustersOperations.list_command
  - Added operation group ThroughputPoolAccountOperations
  - Added operation group ThroughputPoolAccountsOperations
  - Added operation group ThroughputPoolOperations
  - Added operation group ThroughputPoolsOperations
  - Model BackupResource has a new parameter backup_expiry_timestamp
  - Model BackupResource has a new parameter backup_id
  - Model BackupResource has a new parameter backup_start_timestamp
  - Model BackupResource has a new parameter backup_state
  - Model BackupResource has a new parameter backup_stop_timestamp
  - Model CassandraClusterDataCenterNodeItem has a new parameter is_latest_model
  - Model ClusterResourceProperties has a new parameter auto_replicate
  - Model ClusterResourceProperties has a new parameter azure_connection_method
  - Model ClusterResourceProperties has a new parameter backup_schedules
  - Model ClusterResourceProperties has a new parameter cluster_type
  - Model ClusterResourceProperties has a new parameter extensions
  - Model ClusterResourceProperties has a new parameter external_data_centers
  - Model ClusterResourceProperties has a new parameter private_link_resource_id
  - Model ClusterResourceProperties has a new parameter scheduled_event_strategy
  - Model CommandPostBody has a new parameter read_write
  - Model CosmosCassandraDataTransferDataSourceSink has a new parameter remote_account_name
  - Model CosmosMongoDataTransferDataSourceSink has a new parameter remote_account_name
  - Model CosmosSqlDataTransferDataSourceSink has a new parameter remote_account_name
  - Model DataCenterResourceProperties has a new parameter private_endpoint_ip_address
  - Model DataTransferJobGetResults has a new parameter duration
  - Model DataTransferJobGetResults has a new parameter mode
  - Model DataTransferJobProperties has a new parameter duration
  - Model DataTransferJobProperties has a new parameter mode
  - Model DatabaseAccountCreateUpdateParameters has a new parameter customer_managed_key_status
  - Model DatabaseAccountCreateUpdateParameters has a new parameter default_priority_level
  - Model DatabaseAccountCreateUpdateParameters has a new parameter enable_priority_based_execution
  - Model DatabaseAccountGetResults has a new parameter customer_managed_key_status
  - Model DatabaseAccountGetResults has a new parameter default_priority_level
  - Model DatabaseAccountGetResults has a new parameter enable_priority_based_execution
  - Model DatabaseAccountUpdateParameters has a new parameter customer_managed_key_status
  - Model DatabaseAccountUpdateParameters has a new parameter default_priority_level
  - Model DatabaseAccountUpdateParameters has a new parameter enable_priority_based_execution
  - Model RestorableGremlinDatabasePropertiesResource has a new parameter can_undelete
  - Model RestorableGremlinDatabasePropertiesResource has a new parameter can_undelete_reason
  - Model RestorableGremlinGraphPropertiesResource has a new parameter can_undelete
  - Model RestorableGremlinGraphPropertiesResource has a new parameter can_undelete_reason
  - Model RestorableMongodbCollectionPropertiesResource has a new parameter can_undelete
  - Model RestorableMongodbCollectionPropertiesResource has a new parameter can_undelete_reason
  - Model RestorableMongodbDatabasePropertiesResource has a new parameter can_undelete
  - Model RestorableMongodbDatabasePropertiesResource has a new parameter can_undelete_reason
  - Model RestorableSqlContainerPropertiesResource has a new parameter can_undelete
  - Model RestorableSqlContainerPropertiesResource has a new parameter can_undelete_reason
  - Model RestorableSqlContainerPropertiesResourceContainer has a new parameter computed_properties
  - Model RestorableSqlDatabasePropertiesResource has a new parameter can_undelete
  - Model RestorableSqlDatabasePropertiesResource has a new parameter can_undelete_reason
  - Model RestorableTablePropertiesResource has a new parameter can_undelete
  - Model RestorableTablePropertiesResource has a new parameter can_undelete_reason
  - Model SqlContainerGetPropertiesResource has a new parameter computed_properties
  - Model SqlContainerResource has a new parameter computed_properties
  - Model ThroughputSettingsGetPropertiesResource has a new parameter instant_maximum_throughput
  - Model ThroughputSettingsGetPropertiesResource has a new parameter soft_allowed_maximum_throughput
  - Model ThroughputSettingsResource has a new parameter instant_maximum_throughput
  - Model ThroughputSettingsResource has a new parameter soft_allowed_maximum_throughput
  - Operation CassandraClustersOperations.begin_deallocate has a new optional parameter x_ms_force_deallocate

### Breaking Changes

  - Model BackupResource no longer has parameter id
  - Model BackupResource no longer has parameter name
  - Model BackupResource no longer has parameter properties
  - Model BackupResource no longer has parameter type
  - Model CommandPostBody no longer has parameter readwrite

## 9.4.0 (2023-12-19)

### Features Added

  - Model GremlinDatabaseGetPropertiesResource has a new parameter create_mode
  - Model GremlinDatabaseGetPropertiesResource has a new parameter restore_parameters
  - Model GremlinDatabaseResource has a new parameter create_mode
  - Model GremlinDatabaseResource has a new parameter restore_parameters
  - Model GremlinGraphGetPropertiesResource has a new parameter create_mode
  - Model GremlinGraphGetPropertiesResource has a new parameter restore_parameters
  - Model GremlinGraphResource has a new parameter create_mode
  - Model GremlinGraphResource has a new parameter restore_parameters
  - Model MongoDBCollectionGetPropertiesResource has a new parameter create_mode
  - Model MongoDBCollectionGetPropertiesResource has a new parameter restore_parameters
  - Model MongoDBCollectionResource has a new parameter create_mode
  - Model MongoDBCollectionResource has a new parameter restore_parameters
  - Model MongoDBDatabaseGetPropertiesResource has a new parameter create_mode
  - Model MongoDBDatabaseGetPropertiesResource has a new parameter restore_parameters
  - Model MongoDBDatabaseResource has a new parameter create_mode
  - Model MongoDBDatabaseResource has a new parameter restore_parameters
  - Model RestorableGremlinDatabasePropertiesResource has a new parameter can_undelete
  - Model RestorableGremlinDatabasePropertiesResource has a new parameter can_undelete_reason
  - Model RestorableGremlinGraphPropertiesResource has a new parameter can_undelete
  - Model RestorableGremlinGraphPropertiesResource has a new parameter can_undelete_reason
  - Model RestorableMongodbCollectionPropertiesResource has a new parameter can_undelete
  - Model RestorableMongodbCollectionPropertiesResource has a new parameter can_undelete_reason
  - Model RestorableMongodbDatabasePropertiesResource has a new parameter can_undelete
  - Model RestorableMongodbDatabasePropertiesResource has a new parameter can_undelete_reason
  - Model RestorableSqlContainerPropertiesResource has a new parameter can_undelete
  - Model RestorableSqlContainerPropertiesResource has a new parameter can_undelete_reason
  - Model RestorableSqlContainerPropertiesResourceContainer has a new parameter computed_properties
  - Model RestorableSqlContainerPropertiesResourceContainer has a new parameter create_mode
  - Model RestorableSqlContainerPropertiesResourceContainer has a new parameter restore_parameters
  - Model RestorableSqlDatabasePropertiesResource has a new parameter can_undelete
  - Model RestorableSqlDatabasePropertiesResource has a new parameter can_undelete_reason
  - Model RestorableSqlDatabasePropertiesResourceDatabase has a new parameter create_mode
  - Model RestorableSqlDatabasePropertiesResourceDatabase has a new parameter restore_parameters
  - Model RestorableTablePropertiesResource has a new parameter can_undelete
  - Model RestorableTablePropertiesResource has a new parameter can_undelete_reason
  - Model SqlContainerGetPropertiesResource has a new parameter computed_properties
  - Model SqlContainerGetPropertiesResource has a new parameter create_mode
  - Model SqlContainerGetPropertiesResource has a new parameter restore_parameters
  - Model SqlContainerResource has a new parameter computed_properties
  - Model SqlContainerResource has a new parameter create_mode
  - Model SqlContainerResource has a new parameter restore_parameters
  - Model SqlDatabaseGetPropertiesResource has a new parameter create_mode
  - Model SqlDatabaseGetPropertiesResource has a new parameter restore_parameters
  - Model SqlDatabaseResource has a new parameter create_mode
  - Model SqlDatabaseResource has a new parameter restore_parameters
  - Model TableGetPropertiesResource has a new parameter create_mode
  - Model TableGetPropertiesResource has a new parameter restore_parameters
  - Model TableResource has a new parameter create_mode
  - Model TableResource has a new parameter restore_parameters

## 9.3.0 (2023-10-23)

### Features Added

  - Model DatabaseAccountCreateUpdateParameters has a new parameter customer_managed_key_status
  - Model DatabaseAccountCreateUpdateParameters has a new parameter enable_burst_capacity
  - Model DatabaseAccountGetResults has a new parameter customer_managed_key_status
  - Model DatabaseAccountGetResults has a new parameter enable_burst_capacity
  - Model DatabaseAccountUpdateParameters has a new parameter customer_managed_key_status
  - Model DatabaseAccountUpdateParameters has a new parameter enable_burst_capacity

## 10.0.0b1 (2023-06-16)

### Features Added

  - Added operation CassandraClustersOperations.get_backup
  - Added operation CassandraClustersOperations.list_backups
  - Added operation CassandraResourcesOperations.begin_create_update_cassandra_view
  - Added operation CassandraResourcesOperations.begin_delete_cassandra_view
  - Added operation CassandraResourcesOperations.begin_migrate_cassandra_view_to_autoscale
  - Added operation CassandraResourcesOperations.begin_migrate_cassandra_view_to_manual_throughput
  - Added operation CassandraResourcesOperations.begin_update_cassandra_view_throughput
  - Added operation CassandraResourcesOperations.get_cassandra_view
  - Added operation CassandraResourcesOperations.get_cassandra_view_throughput
  - Added operation CassandraResourcesOperations.list_cassandra_views
  - Added operation MongoDBResourcesOperations.begin_list_mongo_db_collection_partition_merge
  - Added operation MongoDBResourcesOperations.begin_mongo_db_container_redistribute_throughput
  - Added operation MongoDBResourcesOperations.begin_mongo_db_container_retrieve_throughput_distribution
  - Added operation MongoDBResourcesOperations.begin_mongo_db_database_partition_merge
  - Added operation MongoDBResourcesOperations.begin_mongo_db_database_redistribute_throughput
  - Added operation MongoDBResourcesOperations.begin_mongo_db_database_retrieve_throughput_distribution
  - Added operation SqlResourcesOperations.begin_list_sql_container_partition_merge
  - Added operation SqlResourcesOperations.begin_sql_container_redistribute_throughput
  - Added operation SqlResourcesOperations.begin_sql_container_retrieve_throughput_distribution
  - Added operation SqlResourcesOperations.begin_sql_database_partition_merge
  - Added operation SqlResourcesOperations.begin_sql_database_redistribute_throughput
  - Added operation SqlResourcesOperations.begin_sql_database_retrieve_throughput_distribution
  - Added operation group DataTransferJobsOperations
  - Added operation group GraphResourcesOperations
  - Added operation group MongoClustersOperations
  - Model ARMResourceProperties has a new parameter identity
  - Model CassandraKeyspaceCreateUpdateParameters has a new parameter identity
  - Model CassandraKeyspaceGetResults has a new parameter identity
  - Model CassandraTableCreateUpdateParameters has a new parameter identity
  - Model CassandraTableGetResults has a new parameter identity
  - Model DatabaseAccountCreateUpdateParameters has a new parameter diagnostic_log_settings
  - Model DatabaseAccountCreateUpdateParameters has a new parameter enable_burst_capacity
  - Model DatabaseAccountCreateUpdateParameters has a new parameter enable_materialized_views
  - Model DatabaseAccountGetResults has a new parameter diagnostic_log_settings
  - Model DatabaseAccountGetResults has a new parameter enable_burst_capacity
  - Model DatabaseAccountGetResults has a new parameter enable_materialized_views
  - Model DatabaseAccountUpdateParameters has a new parameter diagnostic_log_settings
  - Model DatabaseAccountUpdateParameters has a new parameter enable_burst_capacity
  - Model DatabaseAccountUpdateParameters has a new parameter enable_materialized_views
  - Model GremlinDatabaseCreateUpdateParameters has a new parameter identity
  - Model GremlinDatabaseGetPropertiesResource has a new parameter create_mode
  - Model GremlinDatabaseGetPropertiesResource has a new parameter restore_parameters
  - Model GremlinDatabaseGetResults has a new parameter identity
  - Model GremlinDatabaseResource has a new parameter create_mode
  - Model GremlinDatabaseResource has a new parameter restore_parameters
  - Model GremlinGraphCreateUpdateParameters has a new parameter identity
  - Model GremlinGraphGetPropertiesResource has a new parameter create_mode
  - Model GremlinGraphGetPropertiesResource has a new parameter restore_parameters
  - Model GremlinGraphGetResults has a new parameter identity
  - Model GremlinGraphResource has a new parameter create_mode
  - Model GremlinGraphResource has a new parameter restore_parameters
  - Model MongoDBCollectionCreateUpdateParameters has a new parameter identity
  - Model MongoDBCollectionGetPropertiesResource has a new parameter create_mode
  - Model MongoDBCollectionGetPropertiesResource has a new parameter restore_parameters
  - Model MongoDBCollectionGetResults has a new parameter identity
  - Model MongoDBCollectionResource has a new parameter create_mode
  - Model MongoDBCollectionResource has a new parameter restore_parameters
  - Model MongoDBDatabaseCreateUpdateParameters has a new parameter identity
  - Model MongoDBDatabaseGetPropertiesResource has a new parameter create_mode
  - Model MongoDBDatabaseGetPropertiesResource has a new parameter restore_parameters
  - Model MongoDBDatabaseGetResults has a new parameter identity
  - Model MongoDBDatabaseResource has a new parameter create_mode
  - Model MongoDBDatabaseResource has a new parameter restore_parameters
  - Model RestorableSqlContainerPropertiesResourceContainer has a new parameter create_mode
  - Model RestorableSqlContainerPropertiesResourceContainer has a new parameter materialized_view_definition
  - Model RestorableSqlContainerPropertiesResourceContainer has a new parameter restore_parameters
  - Model RestorableSqlDatabasePropertiesResourceDatabase has a new parameter create_mode
  - Model RestorableSqlDatabasePropertiesResourceDatabase has a new parameter restore_parameters
  - Model RestoreParameters has a new parameter source_backup_location
  - Model SqlContainerCreateUpdateParameters has a new parameter identity
  - Model SqlContainerGetPropertiesResource has a new parameter create_mode
  - Model SqlContainerGetPropertiesResource has a new parameter materialized_view_definition
  - Model SqlContainerGetPropertiesResource has a new parameter restore_parameters
  - Model SqlContainerGetResults has a new parameter identity
  - Model SqlContainerResource has a new parameter create_mode
  - Model SqlContainerResource has a new parameter materialized_view_definition
  - Model SqlContainerResource has a new parameter restore_parameters
  - Model SqlDatabaseCreateUpdateParameters has a new parameter identity
  - Model SqlDatabaseGetPropertiesResource has a new parameter create_mode
  - Model SqlDatabaseGetPropertiesResource has a new parameter restore_parameters
  - Model SqlDatabaseGetResults has a new parameter identity
  - Model SqlDatabaseResource has a new parameter create_mode
  - Model SqlDatabaseResource has a new parameter restore_parameters
  - Model SqlStoredProcedureCreateUpdateParameters has a new parameter identity
  - Model SqlStoredProcedureGetResults has a new parameter identity
  - Model SqlTriggerCreateUpdateParameters has a new parameter identity
  - Model SqlTriggerGetResults has a new parameter identity
  - Model SqlUserDefinedFunctionCreateUpdateParameters has a new parameter identity
  - Model SqlUserDefinedFunctionGetResults has a new parameter identity
  - Model TableCreateUpdateParameters has a new parameter identity
  - Model TableGetPropertiesResource has a new parameter create_mode
  - Model TableGetPropertiesResource has a new parameter restore_parameters
  - Model TableGetResults has a new parameter identity
  - Model TableResource has a new parameter create_mode
  - Model TableResource has a new parameter restore_parameters
  - Model ThroughputSettingsGetResults has a new parameter identity
  - Model ThroughputSettingsUpdateParameters has a new parameter identity

### Breaking Changes

  - Model ThroughputSettingsGetPropertiesResource no longer has parameter instant_maximum_throughput
  - Model ThroughputSettingsGetPropertiesResource no longer has parameter soft_allowed_maximum_throughput
  - Model ThroughputSettingsResource no longer has parameter instant_maximum_throughput
  - Model ThroughputSettingsResource no longer has parameter soft_allowed_maximum_throughput

## 9.2.0 (2023-05-08)

### Features Added

  - Model ContinuousModeBackupPolicy has a new parameter continuous_mode_properties
  - Model RestorableDatabaseAccountGetResult has a new parameter oldest_restorable_time
  - Model ThroughputSettingsGetPropertiesResource has a new parameter instant_maximum_throughput
  - Model ThroughputSettingsGetPropertiesResource has a new parameter soft_allowed_maximum_throughput
  - Model ThroughputSettingsResource has a new parameter instant_maximum_throughput
  - Model ThroughputSettingsResource has a new parameter soft_allowed_maximum_throughput
  - Added new enum type `ContinuousTier`
  - Enum `PublicNetworkAccess` has a new value `SECURED_BY_PERIMETER`

## 9.1.0 (2023-04-21)

### Features Added

  - Model CassandraClusterDataCenterNodeItem has a new parameter cassandra_process_status
  - Model CassandraClusterPublicStatus has a new parameter errors
  - Model ClusterResourceProperties has a new parameter provision_error
  - Model DataCenterResourceProperties has a new parameter authentication_method_ldap_properties
  - Model DataCenterResourceProperties has a new parameter deallocated
  - Model DataCenterResourceProperties has a new parameter provision_error
  - Model DatabaseAccountConnectionString has a new parameter key_kind
  - Model DatabaseAccountConnectionString has a new parameter type
  - Model LocationProperties has a new parameter is_subscription_region_access_allowed_for_az
  - Model LocationProperties has a new parameter is_subscription_region_access_allowed_for_regular
  - Model LocationProperties has a new parameter status

## 9.1.0b2 (2023-04-20)

### Features Added

  - Added operation group MongoClustersOperations

## 9.1.0b1 (2023-03-20)

### Features Added

  - Added operation CassandraClustersOperations.get_backup
  - Added operation CassandraClustersOperations.list_backups
  - Added operation CassandraResourcesOperations.begin_create_update_cassandra_view
  - Added operation CassandraResourcesOperations.begin_delete_cassandra_view
  - Added operation CassandraResourcesOperations.begin_migrate_cassandra_view_to_autoscale
  - Added operation CassandraResourcesOperations.begin_migrate_cassandra_view_to_manual_throughput
  - Added operation CassandraResourcesOperations.begin_update_cassandra_view_throughput
  - Added operation CassandraResourcesOperations.get_cassandra_view
  - Added operation CassandraResourcesOperations.get_cassandra_view_throughput
  - Added operation CassandraResourcesOperations.list_cassandra_views
  - Added operation MongoDBResourcesOperations.begin_list_mongo_db_collection_partition_merge
  - Added operation MongoDBResourcesOperations.begin_mongo_db_container_redistribute_throughput
  - Added operation MongoDBResourcesOperations.begin_mongo_db_container_retrieve_throughput_distribution
  - Added operation MongoDBResourcesOperations.begin_mongo_db_database_redistribute_throughput
  - Added operation MongoDBResourcesOperations.begin_mongo_db_database_retrieve_throughput_distribution
  - Added operation SqlResourcesOperations.begin_list_sql_container_partition_merge
  - Added operation SqlResourcesOperations.begin_sql_container_redistribute_throughput
  - Added operation SqlResourcesOperations.begin_sql_container_retrieve_throughput_distribution
  - Added operation SqlResourcesOperations.begin_sql_database_redistribute_throughput
  - Added operation SqlResourcesOperations.begin_sql_database_retrieve_throughput_distribution
  - Added operation group DataTransferJobsOperations
  - Added operation group GraphResourcesOperations
  - Model ARMResourceProperties has a new parameter identity
  - Model CassandraKeyspaceCreateUpdateParameters has a new parameter identity
  - Model CassandraKeyspaceGetResults has a new parameter identity
  - Model CassandraTableCreateUpdateParameters has a new parameter identity
  - Model CassandraTableGetResults has a new parameter identity
  - Model ContinuousModeBackupPolicy has a new parameter continuous_mode_properties
  - Model DataCenterResourceProperties has a new parameter authentication_method_ldap_properties
  - Model DatabaseAccountCreateUpdateParameters has a new parameter diagnostic_log_settings
  - Model DatabaseAccountCreateUpdateParameters has a new parameter enable_burst_capacity
  - Model DatabaseAccountCreateUpdateParameters has a new parameter enable_materialized_views
  - Model DatabaseAccountGetResults has a new parameter diagnostic_log_settings
  - Model DatabaseAccountGetResults has a new parameter enable_burst_capacity
  - Model DatabaseAccountGetResults has a new parameter enable_materialized_views
  - Model DatabaseAccountUpdateParameters has a new parameter diagnostic_log_settings
  - Model DatabaseAccountUpdateParameters has a new parameter enable_burst_capacity
  - Model DatabaseAccountUpdateParameters has a new parameter enable_materialized_views
  - Model GremlinDatabaseCreateUpdateParameters has a new parameter identity
  - Model GremlinDatabaseGetPropertiesResource has a new parameter create_mode
  - Model GremlinDatabaseGetPropertiesResource has a new parameter restore_parameters
  - Model GremlinDatabaseGetResults has a new parameter identity
  - Model GremlinDatabaseResource has a new parameter create_mode
  - Model GremlinDatabaseResource has a new parameter restore_parameters
  - Model GremlinGraphCreateUpdateParameters has a new parameter identity
  - Model GremlinGraphGetPropertiesResource has a new parameter create_mode
  - Model GremlinGraphGetPropertiesResource has a new parameter restore_parameters
  - Model GremlinGraphGetResults has a new parameter identity
  - Model GremlinGraphResource has a new parameter create_mode
  - Model GremlinGraphResource has a new parameter restore_parameters
  - Model LocationProperties has a new parameter status
  - Model MongoDBCollectionCreateUpdateParameters has a new parameter identity
  - Model MongoDBCollectionGetPropertiesResource has a new parameter create_mode
  - Model MongoDBCollectionGetPropertiesResource has a new parameter restore_parameters
  - Model MongoDBCollectionGetResults has a new parameter identity
  - Model MongoDBCollectionResource has a new parameter create_mode
  - Model MongoDBCollectionResource has a new parameter restore_parameters
  - Model MongoDBDatabaseCreateUpdateParameters has a new parameter identity
  - Model MongoDBDatabaseGetPropertiesResource has a new parameter create_mode
  - Model MongoDBDatabaseGetPropertiesResource has a new parameter restore_parameters
  - Model MongoDBDatabaseGetResults has a new parameter identity
  - Model MongoDBDatabaseResource has a new parameter create_mode
  - Model MongoDBDatabaseResource has a new parameter restore_parameters
  - Model RestorableDatabaseAccountGetResult has a new parameter oldest_restorable_time
  - Model RestorableSqlContainerPropertiesResourceContainer has a new parameter create_mode
  - Model RestorableSqlContainerPropertiesResourceContainer has a new parameter restore_parameters
  - Model RestorableSqlDatabasePropertiesResourceDatabase has a new parameter create_mode
  - Model RestorableSqlDatabasePropertiesResourceDatabase has a new parameter restore_parameters
  - Model RestoreParameters has a new parameter source_backup_location
  - Model SqlContainerCreateUpdateParameters has a new parameter identity
  - Model SqlContainerGetPropertiesResource has a new parameter create_mode
  - Model SqlContainerGetPropertiesResource has a new parameter restore_parameters
  - Model SqlContainerGetResults has a new parameter identity
  - Model SqlContainerResource has a new parameter create_mode
  - Model SqlContainerResource has a new parameter restore_parameters
  - Model SqlDatabaseCreateUpdateParameters has a new parameter identity
  - Model SqlDatabaseGetPropertiesResource has a new parameter create_mode
  - Model SqlDatabaseGetPropertiesResource has a new parameter restore_parameters
  - Model SqlDatabaseGetResults has a new parameter identity
  - Model SqlDatabaseResource has a new parameter create_mode
  - Model SqlDatabaseResource has a new parameter restore_parameters
  - Model SqlStoredProcedureCreateUpdateParameters has a new parameter identity
  - Model SqlStoredProcedureGetResults has a new parameter identity
  - Model SqlTriggerCreateUpdateParameters has a new parameter identity
  - Model SqlTriggerGetResults has a new parameter identity
  - Model SqlUserDefinedFunctionCreateUpdateParameters has a new parameter identity
  - Model SqlUserDefinedFunctionGetResults has a new parameter identity
  - Model TableCreateUpdateParameters has a new parameter identity
  - Model TableGetPropertiesResource has a new parameter create_mode
  - Model TableGetPropertiesResource has a new parameter restore_parameters
  - Model TableGetResults has a new parameter identity
  - Model TableResource has a new parameter create_mode
  - Model TableResource has a new parameter restore_parameters
  - Model ThroughputSettingsGetResults has a new parameter identity
  - Model ThroughputSettingsUpdateParameters has a new parameter identity

> Changelog entries prior to 9.1.0b1 were removed to reduce file size. See https://pypi.org/project/azure-mgmt-cosmosdb/9.1.0b1/ for the older history.
