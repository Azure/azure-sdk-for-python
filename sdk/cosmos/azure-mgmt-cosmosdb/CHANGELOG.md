# Release History

## 7.0.0 (2022-05-20)

**Features**

  - Added operation MongoDBResourcesOperations.begin_retrieve_continuous_backup_information
  - Added operation group CassandraClustersOperations
  - Added operation group CassandraDataCentersOperations
  - Added operation group LocationsOperations
  - Model DatabaseAccountCreateUpdateParameters has a new parameter capacity
  - Model DatabaseAccountGetResults has a new parameter capacity
  - Model DatabaseAccountUpdateParameters has a new parameter capacity
  - Model PeriodicModeProperties has a new parameter backup_storage_redundancy

## 7.0.0b5 (2022-04-28)

**Features**

  - Added operation DataTransferJobsOperations.cancel
  - Added operation DataTransferJobsOperations.pause
  - Added operation DataTransferJobsOperations.resume
  - Added operation MongoDBResourcesOperations.begin_mongo_db_container_redistribute_throughput
  - Added operation MongoDBResourcesOperations.begin_sql_container_retrieve_throughput_distribution
  - Added operation SqlResourcesOperations.begin_sql_container_redistribute_throughput
  - Added operation SqlResourcesOperations.begin_sql_container_retrieve_throughput_distribution
  - Model DataTransferJobGetResults has a new parameter processed_count
  - Model DataTransferJobGetResults has a new parameter total_count
  - Model DataTransferJobProperties has a new parameter processed_count
  - Model DataTransferJobProperties has a new parameter total_count

**Breaking changes**

  - Model DataTransferJobGetResults no longer has parameter percentage_complete
  - Model DataTransferJobProperties no longer has parameter percentage_complete

## 7.0.0b4 (2022-04-14)

**Features**

  - Added operation MongoDBResourcesOperations.begin_list_mongo_db_collection_partition_merge
  - Added operation SqlResourcesOperations.begin_list_sql_container_partition_merge
  - Model ContinuousModeBackupPolicy has a new parameter continuous_mode_properties
  - Model KeyWrapMetadata has a new parameter algorithm
  - Model RestorableDatabaseAccountGetResult has a new parameter oldest_restorable_time
  - Model RestorableSqlContainerPropertiesResourceContainer has a new parameter client_encryption_policy
  - Model SqlContainerGetPropertiesResource has a new parameter client_encryption_policy
  - Model SqlContainerResource has a new parameter client_encryption_policy

## 7.0.0b3 (2022-02-18)

**Features**

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
  - Added operation GremlinResourcesOperations.begin_retrieve_continuous_backup_information
  - Added operation MongoDBResourcesOperations.begin_create_update_mongo_role_definition
  - Added operation MongoDBResourcesOperations.begin_create_update_mongo_user_definition
  - Added operation MongoDBResourcesOperations.begin_delete_mongo_role_definition
  - Added operation MongoDBResourcesOperations.begin_delete_mongo_user_definition
  - Added operation MongoDBResourcesOperations.get_mongo_role_definition
  - Added operation MongoDBResourcesOperations.get_mongo_user_definition
  - Added operation MongoDBResourcesOperations.list_mongo_role_definitions
  - Added operation MongoDBResourcesOperations.list_mongo_user_definitions
  - Added operation SqlResourcesOperations.begin_create_update_client_encryption_key
  - Added operation SqlResourcesOperations.get_client_encryption_key
  - Added operation SqlResourcesOperations.list_client_encryption_keys
  - Added operation TableResourcesOperations.begin_retrieve_continuous_backup_information
  - Added operation group DataTransferJobsOperations
  - Added operation group GraphResourcesOperations
  - Added operation group RestorableGremlinDatabasesOperations
  - Added operation group RestorableGremlinGraphsOperations
  - Added operation group RestorableGremlinResourcesOperations
  - Added operation group RestorableTableResourcesOperations
  - Added operation group RestorableTablesOperations
  - Added operation group ServiceOperations
  - Model ARMResourceProperties has a new parameter identity
  - Model CassandraKeyspaceCreateUpdateParameters has a new parameter identity
  - Model CassandraKeyspaceGetResults has a new parameter identity
  - Model CassandraTableCreateUpdateParameters has a new parameter identity
  - Model CassandraTableGetResults has a new parameter identity
  - Model DataCenterResourceProperties has a new parameter authentication_method_ldap_properties
  - Model DatabaseAccountCreateUpdateParameters has a new parameter diagnostic_log_settings
  - Model DatabaseAccountCreateUpdateParameters has a new parameter enable_materialized_views
  - Model DatabaseAccountGetResults has a new parameter diagnostic_log_settings
  - Model DatabaseAccountGetResults has a new parameter enable_materialized_views
  - Model DatabaseAccountUpdateParameters has a new parameter diagnostic_log_settings
  - Model DatabaseAccountUpdateParameters has a new parameter enable_materialized_views
  - Model GremlinDatabaseCreateUpdateParameters has a new parameter identity
  - Model GremlinDatabaseGetResults has a new parameter identity
  - Model GremlinGraphCreateUpdateParameters has a new parameter identity
  - Model GremlinGraphGetResults has a new parameter identity
  - Model LocationProperties has a new parameter status
  - Model MongoDBCollectionCreateUpdateParameters has a new parameter identity
  - Model MongoDBCollectionGetResults has a new parameter identity
  - Model MongoDBDatabaseCreateUpdateParameters has a new parameter identity
  - Model MongoDBDatabaseGetResults has a new parameter identity
  - Model RestoreParameters has a new parameter gremlin_databases_to_restore
  - Model RestoreParameters has a new parameter tables_to_restore
  - Model SqlContainerCreateUpdateParameters has a new parameter identity
  - Model SqlContainerGetResults has a new parameter identity
  - Model SqlDatabaseCreateUpdateParameters has a new parameter identity
  - Model SqlDatabaseGetResults has a new parameter identity
  - Model SqlStoredProcedureCreateUpdateParameters has a new parameter identity
  - Model SqlStoredProcedureGetResults has a new parameter identity
  - Model SqlTriggerCreateUpdateParameters has a new parameter identity
  - Model SqlTriggerGetResults has a new parameter identity
  - Model SqlUserDefinedFunctionCreateUpdateParameters has a new parameter identity
  - Model SqlUserDefinedFunctionGetResults has a new parameter identity
  - Model TableCreateUpdateParameters has a new parameter identity
  - Model TableGetResults has a new parameter identity
  - Model ThroughputSettingsGetResults has a new parameter identity
  - Model ThroughputSettingsUpdateParameters has a new parameter identity

**Breaking changes**

  - Operation RestorableMongodbCollectionsOperations.list has a new signature
  - Operation RestorableMongodbCollectionsOperations.list has a new signature

## 7.0.0b2 (2021-10-26)

**Features**

  - Model DataCenterResourceProperties has a new parameter disk_capacity
  - Model DataCenterResourceProperties has a new parameter disk_sku
  - Model DataCenterResourceProperties has a new parameter managed_disk_customer_key_uri
  - Model DataCenterResourceProperties has a new parameter sku
  - Model DataCenterResourceProperties has a new parameter availability_zone
  - Model DataCenterResourceProperties has a new parameter backup_storage_customer_key_uri
  - Model DatabaseAccountCreateUpdateParameters has a new parameter capacity
  - Model DatabaseAccountUpdateParameters has a new parameter capacity
  - Model ClusterResourceProperties has a new parameter cassandra_audit_logging_enabled
  - Model ClusterResourceProperties has a new parameter deallocated
  - Model DatabaseAccountGetResults has a new parameter capacity
  - Added operation MongoDBResourcesOperations.begin_retrieve_continuous_backup_information
  - Added operation CassandraClustersOperations.begin_invoke_command
  - Added operation CassandraClustersOperations.begin_start
  - Added operation CassandraClustersOperations.begin_deallocate
  - Added operation CassandraClustersOperations.status
  - Added operation group LocationsOperations

**Breaking changes**

  - Model MongoDBDatabaseGetResults no longer has parameter identity
  - Model MongoDBDatabaseCreateUpdateParameters no longer has parameter identity
  - Model SqlContainerGetResults no longer has parameter identity
  - Model SqlUserDefinedFunctionGetResults no longer has parameter identity
  - Model GremlinDatabaseGetResults no longer has parameter identity
  - Model SqlTriggerCreateUpdateParameters no longer has parameter identity
  - Model SqlContainerCreateUpdateParameters no longer has parameter identity
  - Model SqlDatabaseCreateUpdateParameters no longer has parameter identity
  - Model LocationProperties no longer has parameter status
  - Model DatabaseAccountCreateUpdateParameters no longer has parameter diagnostic_log_settings
  - Model ThroughputSettingsGetResults no longer has parameter identity
  - Model DatabaseAccountUpdateParameters no longer has parameter diagnostic_log_settings
  - Model ARMResourceProperties no longer has parameter identity
  - Model CassandraTableGetResults no longer has parameter identity
  - Model GremlinGraphGetResults no longer has parameter identity
  - Model CassandraKeyspaceCreateUpdateParameters no longer has parameter identity
  - Model GremlinDatabaseCreateUpdateParameters no longer has parameter identity
  - Model SqlTriggerGetResults no longer has parameter identity
  - Model GremlinGraphCreateUpdateParameters no longer has parameter identity
  - Model MongoDBCollectionGetResults no longer has parameter identity
  - Model TableGetResults no longer has parameter identity
  - Model CassandraKeyspaceGetResults no longer has parameter identity
  - Model MongoDBCollectionCreateUpdateParameters no longer has parameter identity
  - Model SqlStoredProcedureGetResults no longer has parameter identity
  - Model SqlStoredProcedureCreateUpdateParameters no longer has parameter identity
  - Model ThroughputSettingsUpdateParameters no longer has parameter identity
  - Model SqlUserDefinedFunctionCreateUpdateParameters no longer has parameter identity
  - Model TableCreateUpdateParameters no longer has parameter identity
  - Model DatabaseAccountGetResults no longer has parameter diagnostic_log_settings
  - Model SqlDatabaseGetResults no longer has parameter identity
  - Model CassandraTableCreateUpdateParameters no longer has parameter identity
  - Removed operation CassandraResourcesOperations.begin_create_update_cassandra_view
  - Removed operation CassandraResourcesOperations.get_cassandra_view
  - Removed operation CassandraResourcesOperations.list_cassandra_views
  - Removed operation CassandraResourcesOperations.begin_migrate_cassandra_view_to_autoscale
  - Removed operation CassandraResourcesOperations.begin_update_cassandra_view_throughput
  - Removed operation CassandraResourcesOperations.get_cassandra_view_throughput
  - Removed operation CassandraResourcesOperations.begin_delete_cassandra_view
  - Removed operation CassandraResourcesOperations.begin_migrate_cassandra_view_to_manual_throughput
  - Removed operation CassandraClustersOperations.begin_request_repair
  - Removed operation CassandraClustersOperations.begin_fetch_node_status
  - Removed operation CassandraClustersOperations.get_backup
  - Removed operation CassandraClustersOperations.list_backups
  - Removed operation group ServiceOperations
  - Removed operation group CosmosDBManagementClientOperationsMixin
  - Removed operation group GraphResourcesOperations

## 7.0.0b1 (2021-09-17)

**Features**

  - Model SqlContainerCreateUpdateParameters has a new parameter identity
  - Model TableGetResults has a new parameter identity
  - Model SqlTriggerCreateUpdateParameters has a new parameter identity
  - Model DatabaseAccountCreateUpdateParameters has a new parameter diagnostic_log_settings
  - Model SqlTriggerGetResults has a new parameter identity
  - Model SqlDatabaseGetResults has a new parameter identity
  - Model GremlinGraphGetResults has a new parameter identity
  - Model SqlStoredProcedureGetResults has a new parameter identity
  - Model TableCreateUpdateParameters has a new parameter identity
  - Model PeriodicModeProperties has a new parameter backup_storage_redundancy
  - Model CassandraKeyspaceCreateUpdateParameters has a new parameter identity
  - Model SqlContainerGetResults has a new parameter identity
  - Model DatabaseAccountGetResults has a new parameter diagnostic_log_settings
  - Model SqlStoredProcedureCreateUpdateParameters has a new parameter identity
  - Model CassandraKeyspaceGetResults has a new parameter identity
  - Model ThroughputSettingsUpdateParameters has a new parameter identity
  - Model GremlinDatabaseCreateUpdateParameters has a new parameter identity
  - Model ThroughputSettingsGetResults has a new parameter identity
  - Model MongoDBCollectionGetResults has a new parameter identity
  - Model SqlDatabaseCreateUpdateParameters has a new parameter identity
  - Model ARMResourceProperties has a new parameter identity
  - Model SqlUserDefinedFunctionCreateUpdateParameters has a new parameter identity
  - Model GremlinDatabaseGetResults has a new parameter identity
  - Model GremlinGraphCreateUpdateParameters has a new parameter identity
  - Model MongoDBCollectionCreateUpdateParameters has a new parameter identity
  - Model CassandraTableCreateUpdateParameters has a new parameter identity
  - Model CassandraTableGetResults has a new parameter identity
  - Model MongoDBDatabaseGetResults has a new parameter identity
  - Model SqlUserDefinedFunctionGetResults has a new parameter identity
  - Model MongoDBDatabaseCreateUpdateParameters has a new parameter identity
  - Model DatabaseAccountUpdateParameters has a new parameter diagnostic_log_settings
  - Added operation CassandraResourcesOperations.begin_create_update_cassandra_view
  - Added operation CassandraResourcesOperations.get_cassandra_view_throughput
  - Added operation CassandraResourcesOperations.get_cassandra_view
  - Added operation CassandraResourcesOperations.list_cassandra_views
  - Added operation CassandraResourcesOperations.begin_migrate_cassandra_view_to_manual_throughput
  - Added operation CassandraResourcesOperations.begin_migrate_cassandra_view_to_autoscale
  - Added operation CassandraResourcesOperations.begin_delete_cassandra_view
  - Added operation CassandraResourcesOperations.begin_update_cassandra_view_throughput
  - Added operation group CassandraClustersOperations
  - Added operation group CassandraDataCentersOperations
  - Added operation group ServiceOperations
  - Added operation group CosmosDBManagementClientOperationsMixin
  - Added operation group GraphResourcesOperations

**Breaking changes**

  - Parameter create_mode of model DatabaseAccountCreateUpdateParameters is now required

## 6.4.0 (2021-06-22)

**Features**

  - Model ContinuousModeBackupPolicy has a new parameter migration_state
  - Model DatabaseAccountGetResults has a new parameter restore_parameters
  - Model DatabaseAccountGetResults has a new parameter analytical_storage_configuration
  - Model DatabaseAccountGetResults has a new parameter system_data
  - Model DatabaseAccountGetResults has a new parameter instance_id
  - Model DatabaseAccountGetResults has a new parameter disable_local_auth
  - Model DatabaseAccountGetResults has a new parameter create_mode
  - Model BackupPolicy has a new parameter migration_state
  - Model DatabaseAccountCreateUpdateParameters has a new parameter analytical_storage_configuration
  - Model DatabaseAccountCreateUpdateParameters has a new parameter restore_parameters
  - Model DatabaseAccountCreateUpdateParameters has a new parameter disable_local_auth
  - Model DatabaseAccountCreateUpdateParameters has a new parameter create_mode
  - Model PeriodicModeBackupPolicy has a new parameter migration_state
  - Model DatabaseAccountUpdateParameters has a new parameter analytical_storage_configuration
  - Model DatabaseAccountUpdateParameters has a new parameter disable_local_auth
  - Added operation SqlResourcesOperations.begin_retrieve_continuous_backup_information
  - Added operation group RestorableMongodbDatabasesOperations
  - Added operation group RestorableDatabaseAccountsOperations
  - Added operation group RestorableSqlDatabasesOperations
  - Added operation group RestorableSqlContainersOperations
  - Added operation group RestorableMongodbResourcesOperations
  - Added operation group RestorableMongodbCollectionsOperations
  - Added operation group RestorableSqlResourcesOperations

## 6.3.0 (2021-05-14)

**Breaking changes**

  - Model CassandraKeyspaceCreateUpdateParameters no longer has parameter identity
  - Model ARMResourceProperties no longer has parameter identity
  - Model MongoDBCollectionCreateUpdateParameters no longer has parameter identity
  - Model SqlDatabaseCreateUpdateParameters no longer has parameter identity
  - Model SqlStoredProcedureCreateUpdateParameters no longer has parameter identity
  - Model SqlTriggerGetResults no longer has parameter identity
  - Model MongoDBDatabaseCreateUpdateParameters no longer has parameter identity
  - Model SqlDatabaseGetResults no longer has parameter identity
  - Model TableGetResults no longer has parameter identity
  - Model CassandraTableCreateUpdateParameters no longer has parameter identity
  - Model GremlinGraphCreateUpdateParameters no longer has parameter identity
  - Model GremlinDatabaseGetResults no longer has parameter identity
  - Model ThroughputSettingsUpdateParameters no longer has parameter identity
  - Model CassandraKeyspaceGetResults no longer has parameter identity
  - Model SqlContainerGetResults no longer has parameter identity
  - Model SqlUserDefinedFunctionGetResults no longer has parameter identity
  - Model SqlTriggerCreateUpdateParameters no longer has parameter identity
  - Model MongoDBCollectionGetResults no longer has parameter identity
  - Model MongoDBDatabaseGetResults no longer has parameter identity
  - Model PeriodicModeProperties no longer has parameter backup_storage_redundancy
  - Model ThroughputSettingsGetResults no longer has parameter identity
  - Model GremlinGraphGetResults no longer has parameter identity
  - Model GremlinDatabaseCreateUpdateParameters no longer has parameter identity
  - Model CassandraTableGetResults no longer has parameter identity
  - Model SqlStoredProcedureGetResults no longer has parameter identity
  - Model TableCreateUpdateParameters no longer has parameter identity
  - Model DatabaseAccountGetResults no longer has parameter create_mode
  - Model DatabaseAccountGetResults no longer has parameter restore_parameters
  - Model DatabaseAccountGetResults no longer has parameter instance_id
  - Model DatabaseAccountGetResults no longer has parameter system_data
  - Model SqlUserDefinedFunctionCreateUpdateParameters no longer has parameter identity
  - Model SqlContainerCreateUpdateParameters no longer has parameter identity
  - Removed operation SqlResourcesOperations.begin_retrieve_continuous_backup_information
  - Model DatabaseAccountCreateUpdateParameters has a new signature
  - Removed operation group RestorableDatabaseAccountsOperations
  - Removed operation group RestorableMongodbCollectionsOperations
  - Removed operation group CosmosDBManagementClientOperationsMixin
  - Removed operation group RestorableSqlResourcesOperations
  - Removed operation group RestorableMongodbDatabasesOperations
  - Removed operation group CassandraClustersOperations
  - Removed operation group RestorableMongodbResourcesOperations
  - Removed operation group RestorableSqlContainersOperations
  - Removed operation group CassandraDataCentersOperations
  - Removed operation group RestorableSqlDatabasesOperations
  - Removed operation group ServiceOperations

## 6.3.0b1 (2021-05-10)

**Features**

  - Model CassandraKeyspaceGetResults has a new parameter identity
  - Model TableCreateUpdateParameters has a new parameter identity
  - Model CassandraTableGetResults has a new parameter identity
  - Model MongoDBDatabaseGetResults has a new parameter identity
  - Model SqlStoredProcedureGetResults has a new parameter identity
  - Model TableGetResults has a new parameter identity
  - Model SqlTriggerGetResults has a new parameter identity
  - Model SqlTriggerCreateUpdateParameters has a new parameter identity
  - Model SqlContainerGetResults has a new parameter identity
  - Model SqlUserDefinedFunctionCreateUpdateParameters has a new parameter identity
  - Model SqlContainerCreateUpdateParameters has a new parameter identity
  - Model PeriodicModeProperties has a new parameter backup_storage_redundancy
  - Model MongoDBCollectionCreateUpdateParameters has a new parameter identity
  - Model SqlDatabaseCreateUpdateParameters has a new parameter identity
  - Model GremlinGraphCreateUpdateParameters has a new parameter identity
  - Model GremlinGraphGetResults has a new parameter identity
  - Model GremlinDatabaseCreateUpdateParameters has a new parameter identity
  - Model ThroughputSettingsUpdateParameters has a new parameter identity
  - Model MongoDBDatabaseCreateUpdateParameters has a new parameter identity
  - Model ThroughputSettingsGetResults has a new parameter identity
  - Model CassandraKeyspaceCreateUpdateParameters has a new parameter identity
  - Model SqlStoredProcedureCreateUpdateParameters has a new parameter identity
  - Model MongoDBCollectionGetResults has a new parameter identity
  - Model CassandraTableCreateUpdateParameters has a new parameter identity
  - Model SqlUserDefinedFunctionGetResults has a new parameter identity
  - Model SqlDatabaseGetResults has a new parameter identity
  - Model ARMResourceProperties has a new parameter identity
  - Model GremlinDatabaseGetResults has a new parameter identity
  - Model DatabaseAccountGetResults has a new parameter instance_id
  - Model DatabaseAccountGetResults has a new parameter restore_parameters
  - Model DatabaseAccountGetResults has a new parameter system_data
  - Model DatabaseAccountGetResults has a new parameter create_mode
  - Added operation SqlResourcesOperations.begin_create_update_sql_role_assignment
  - Added operation SqlResourcesOperations.begin_retrieve_continuous_backup_information
  - Added operation SqlResourcesOperations.begin_delete_sql_role_assignment
  - Added operation SqlResourcesOperations.begin_create_update_sql_role_definition
  - Added operation SqlResourcesOperations.list_sql_role_definitions
  - Added operation SqlResourcesOperations.begin_delete_sql_role_definition
  - Added operation SqlResourcesOperations.list_sql_role_assignments
  - Added operation SqlResourcesOperations.get_sql_role_assignment
  - Added operation SqlResourcesOperations.get_sql_role_definition
  - Added operation group CassandraDataCentersOperations
  - Added operation group RestorableSqlContainersOperations
  - Added operation group CassandraClustersOperations
  - Added operation group RestorableMongodbResourcesOperations
  - Added operation group RestorableMongodbDatabasesOperations
  - Added operation group RestorableDatabaseAccountsOperations
  - Added operation group RestorableMongodbCollectionsOperations
  - Added operation group CosmosDBManagementClientOperationsMixin
  - Added operation group RestorableSqlResourcesOperations
  - Added operation group ServiceOperations
  - Added operation group RestorableSqlDatabasesOperations

**Breaking changes**

  - Model DatabaseAccountCreateUpdateParameters has a new signature

## 6.2.0 (2021-04-06)

**Features**

  - Model DatabaseAccountUpdateParameters has a new parameter default_identity
  - Model DatabaseAccountCreateUpdateParameters has a new parameter default_identity
  - Model DatabaseAccountGetResults has a new parameter default_identity

## 6.1.0 (2021-03-02)

**Features**

  - Model DatabaseAccountGetResults has a new parameter network_acl_bypass
  - Model DatabaseAccountGetResults has a new parameter backup_policy
  - Model DatabaseAccountGetResults has a new parameter identity
  - Model DatabaseAccountGetResults has a new parameter network_acl_bypass_resource_ids
  - Model PrivateEndpointConnection has a new parameter group_id
  - Model PrivateEndpointConnection has a new parameter provisioning_state
  - Model ContainerPartitionKey has a new parameter system_key
  - Model DatabaseAccountUpdateParameters has a new parameter network_acl_bypass
  - Model DatabaseAccountUpdateParameters has a new parameter backup_policy
  - Model DatabaseAccountUpdateParameters has a new parameter identity
  - Model DatabaseAccountUpdateParameters has a new parameter network_acl_bypass_resource_ids
  - Model PrivateLinkServiceConnectionStateProperty has a new parameter description
  - Model DatabaseAccountCreateUpdateParameters has a new parameter network_acl_bypass
  - Model DatabaseAccountCreateUpdateParameters has a new parameter backup_policy
  - Model DatabaseAccountCreateUpdateParameters has a new parameter identity
  - Model DatabaseAccountCreateUpdateParameters has a new parameter network_acl_bypass_resource_ids

## 6.0.0 (2020-11-24)

- GA release

## 6.0.0b1 (2020-10-12)

This is beta preview version.

This version uses a next-generation code generator that introduces important breaking changes, but also important new features (like unified authentication and async programming).

**General breaking changes**

- Credential system has been completly revamped:

  - `azure.common.credentials` or `msrestazure.azure_active_directory` instances are no longer supported, use the `azure-identity` classes instead: https://pypi.org/project/azure-identity/
  - `credentials` parameter has been renamed `credential`

- The `config` attribute no longer exists on a client, configuration should be passed as kwarg. Example: `MyClient(credential, subscription_id, enable_logging=True)`. For a complete set of
  supported options, see the [parameters accept in init documentation of azure-core](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#available-policies)
- You can't import a `version` module anymore, use `__version__` instead
- Operations that used to return a `msrest.polling.LROPoller` now returns a `azure.core.polling.LROPoller` and are prefixed with `begin_`.
- Exceptions tree have been simplified and most exceptions are now `azure.core.exceptions.HttpResponseError` (`CloudError` has been removed).
- Most of the operation kwarg have changed. Some of the most noticeable:

  - `raw` has been removed. Equivalent feature can be found using `cls`, a callback that will give access to internal HTTP response for advanced user
  - For a complete set of
  supported options, see the [parameters accept in Request documentation of azure-core](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#available-policies)

**General new features**

- Type annotations support using `typing`. SDKs are mypy ready.
- This client has now stable and official support for async. Check the `aio` namespace of your package to find the async client.
- This client now support natively tracing library like OpenCensus or OpenTelemetry. See this [tracing quickstart](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/core/azure-core-tracing-opentelemetry) for an overview.

## 1.0.0 (2020-08-17)

**Features**

  - Model SqlContainerGetPropertiesResource has a new parameter analytical_storage_ttl
  - Model DatabaseAccountUpdateParameters has a new parameter cors
  - Model SqlContainerResource has a new parameter analytical_storage_ttl
  - Model DatabaseAccountGetResults has a new parameter cors
  - Added operation MongoDBResourcesOperations.migrate_mongo_db_collection_to_manual_throughput
  - Added operation MongoDBResourcesOperations.migrate_mongo_db_database_to_manual_throughput
  - Added operation MongoDBResourcesOperations.migrate_mongo_db_database_to_autoscale
  - Added operation MongoDBResourcesOperations.migrate_mongo_db_collection_to_autoscale
  - Added operation GremlinResourcesOperations.migrate_gremlin_database_to_manual_throughput
  - Added operation GremlinResourcesOperations.migrate_gremlin_graph_to_autoscale
  - Added operation GremlinResourcesOperations.migrate_gremlin_graph_to_manual_throughput
  - Added operation GremlinResourcesOperations.migrate_gremlin_database_to_autoscale
  - Added operation TableResourcesOperations.migrate_table_to_autoscale
  - Added operation TableResourcesOperations.migrate_table_to_manual_throughput
  - Added operation CassandraResourcesOperations.migrate_cassandra_keyspace_to_autoscale
  - Added operation CassandraResourcesOperations.migrate_cassandra_keyspace_to_manual_throughput
  - Added operation CassandraResourcesOperations.migrate_cassandra_table_to_manual_throughput
  - Added operation CassandraResourcesOperations.migrate_cassandra_table_to_autoscale
  - Added operation SqlResourcesOperations.migrate_sql_database_to_manual_throughput
  - Added operation SqlResourcesOperations.migrate_sql_database_to_autoscale
  - Added operation SqlResourcesOperations.migrate_sql_container_to_autoscale
  - Added operation SqlResourcesOperations.migrate_sql_container_to_manual_throughput

**Breaking changes**

  - Model ThroughputSettingsUpdateParameters no longer has parameter identity
  - Model CassandraKeyspaceCreateUpdateParameters no longer has parameter identity
  - Model SqlTriggerCreateUpdateParameters no longer has parameter identity
  - Model SqlContainerGetResults no longer has parameter identity
  - Model MongoDBDatabaseGetResults no longer has parameter identity
  - Model GremlinGraphGetResults no longer has parameter identity
  - Model SqlUserDefinedFunctionGetResults no longer has parameter identity
  - Model CassandraTableGetResults no longer has parameter identity
  - Model SqlUserDefinedFunctionCreateUpdateParameters no longer has parameter identity
  - Model SqlDatabaseGetResults no longer has parameter identity
  - Model MongoDBCollectionGetResults no longer has parameter identity
  - Model SqlStoredProcedureGetResults no longer has parameter identity
  - Model GremlinDatabaseGetResults no longer has parameter identity
  - Model MongoDBDatabaseCreateUpdateParameters no longer has parameter identity
  - Model SqlTriggerGetResults no longer has parameter identity
  - Model CassandraKeyspaceGetResults no longer has parameter identity
  - Model DatabaseAccountUpdateParameters no longer has parameter backup_policy
  - Model SqlStoredProcedureCreateUpdateParameters no longer has parameter identity
  - Model TableCreateUpdateParameters no longer has parameter identity
  - Model GremlinDatabaseCreateUpdateParameters no longer has parameter identity
  - Model SqlDatabaseCreateUpdateParameters no longer has parameter identity
  - Model MongoDBCollectionCreateUpdateParameters no longer has parameter identity
  - Model DatabaseAccountGetResults no longer has parameter instance_id
  - Model DatabaseAccountGetResults no longer has parameter system_data
  - Model DatabaseAccountGetResults no longer has parameter backup_policy
  - Model DatabaseAccountGetResults no longer has parameter identity
  - Model DatabaseAccountGetResults no longer has parameter create_mode
  - Model DatabaseAccountGetResults no longer has parameter restore_parameters
  - Model SqlContainerCreateUpdateParameters no longer has parameter identity
  - Model GremlinGraphCreateUpdateParameters no longer has parameter identity
  - Model ARMResourceProperties no longer has parameter identity
  - Model CassandraTableCreateUpdateParameters no longer has parameter identity
  - Model ThroughputSettingsGetResults no longer has parameter identity
  - Model TableGetResults no longer has parameter identity
  - Model DatabaseAccountCreateUpdateParameters has a new signature
  - Removed operation group RestorableDatabaseAccountsOperations

## 0.16.0 (2020-07-31)

**Features**

  - Model SqlUserDefinedFunctionGetResults has a new parameter identity
  - Model CassandraKeyspaceCreateUpdateParameters has a new parameter identity
  - Model MongoDBCollectionGetResults has a new parameter identity
  - Model TableGetResults has a new parameter identity
  - Model SqlTriggerGetResults has a new parameter identity
  - Model SqlStoredProcedureCreateUpdateParameters has a new parameter identity
  - Model SqlDatabaseCreateUpdateParameters has a new parameter identity
  - Model CassandraTableGetResults has a new parameter identity
  - Model MongoDBDatabaseCreateUpdateParameters has a new parameter identity
  - Model ThroughputSettingsGetResults has a new parameter identity
  - Model TableCreateUpdateParameters has a new parameter identity
  - Model SqlContainerCreateUpdateParameters has a new parameter identity
  - Model DatabaseAccountUpdateParameters has a new parameter backup_policy
  - Model SqlDatabaseGetResults has a new parameter identity
  - Model MongoDBDatabaseGetResults has a new parameter identity
  - Model SqlUserDefinedFunctionCreateUpdateParameters has a new parameter identity
  - Model CassandraTableCreateUpdateParameters has a new parameter identity
  - Model MongoDBCollectionCreateUpdateParameters has a new parameter identity
  - Model SqlStoredProcedureGetResults has a new parameter identity
  - Model ThroughputSettingsUpdateParameters has a new parameter identity
  - Model GremlinDatabaseCreateUpdateParameters has a new parameter identity
  - Model GremlinDatabaseGetResults has a new parameter identity
  - Model ARMResourceProperties has a new parameter identity
  - Model CassandraKeyspaceGetResults has a new parameter identity
  - Model SqlContainerGetResults has a new parameter identity
  - Model GremlinGraphCreateUpdateParameters has a new parameter identity
  - Model GremlinGraphGetResults has a new parameter identity
  - Model SqlTriggerCreateUpdateParameters has a new parameter identity
  - Model DatabaseAccountGetResults has a new parameter system_data
  - Model DatabaseAccountGetResults has a new parameter backup_policy
  - Model DatabaseAccountGetResults has a new parameter create_mode
  - Model DatabaseAccountGetResults has a new parameter instance_id
  - Model DatabaseAccountGetResults has a new parameter identity
  - Model DatabaseAccountGetResults has a new parameter restore_parameters
  - Added operation group RestorableDatabaseAccountsOperations

**Breaking changes**

  - Model DatabaseAccountCreateUpdateParameters has a new signature

## 0.15.0 (2020-06-11)

**Features**

  - Model MongoDBCollectionResource has a new parameter analytical_storage_ttl
  - Model MongoDBDatabaseGetPropertiesOptions has a new parameter autoscale_settings
  - Model ThroughputSettingsGetPropertiesResource has a new parameter autoscale_settings
  - Model SqlContainerGetPropertiesOptions has a new parameter autoscale_settings
  - Model CassandraTableGetPropertiesResource has a new parameter analytical_storage_ttl
  - Model CassandraTableResource has a new parameter analytical_storage_ttl
  - Model OptionsResource has a new parameter autoscale_settings
  - Model TableGetPropertiesOptions has a new parameter autoscale_settings
  - Model ThroughputSettingsResource has a new parameter autoscale_settings
  - Model CassandraTableGetPropertiesOptions has a new parameter autoscale_settings
  - Model GremlinDatabaseGetPropertiesOptions has a new parameter autoscale_settings
  - Model DatabaseAccountGetResults has a new parameter api_properties
  - Model DatabaseAccountGetResults has a new parameter ip_rules
  - Model DatabaseAccountGetResults has a new parameter enable_free_tier
  - Model DatabaseAccountGetResults has a new parameter enable_analytical_storage
  - Model GremlinGraphGetPropertiesOptions has a new parameter autoscale_settings
  - Model DatabaseAccountCreateUpdateParameters has a new parameter api_properties
  - Model DatabaseAccountCreateUpdateParameters has a new parameter ip_rules
  - Model DatabaseAccountCreateUpdateParameters has a new parameter enable_free_tier
  - Model DatabaseAccountCreateUpdateParameters has a new parameter enable_analytical_storage
  - Model MongoDBCollectionGetPropertiesOptions has a new parameter autoscale_settings
  - Model CassandraKeyspaceGetPropertiesOptions has a new parameter autoscale_settings
  - Model SqlDatabaseGetPropertiesOptions has a new parameter autoscale_settings
  - Model DatabaseAccountUpdateParameters has a new parameter api_properties
  - Model DatabaseAccountUpdateParameters has a new parameter ip_rules
  - Model DatabaseAccountUpdateParameters has a new parameter enable_free_tier
  - Model DatabaseAccountUpdateParameters has a new parameter enable_analytical_storage
  - Model MongoDBCollectionGetPropertiesResource has a new parameter analytical_storage_ttl

**Breaking changes**

  - Model ThroughputSettingsGetPropertiesResource no longer has parameter provisioned_throughput_settings
  - Model ThroughputSettingsResource no longer has parameter provisioned_throughput_settings
  - Model DatabaseAccountGetResults no longer has parameter ip_range_filter
  - Model DatabaseAccountCreateUpdateParameters no longer has parameter ip_range_filter
  - Model DatabaseAccountUpdateParameters no longer has parameter ip_range_filter
  - Model CreateUpdateOptions has a new signature

## 0.14.0 (2020-05-05)

**Features**

  - Model DatabaseAccountGetResults has a new parameter private_endpoint_connections

## 0.13.0 (2020-04-18)

**Features**

  - Model DatabaseAccountUpdateParameters has a new parameter public_network_access
  - Model DatabaseAccountCreateUpdateParameters has a new parameter public_network_access
  - Model GremlinGraphGetResults has a new parameter options
  - Model PrivateLinkResource has a new parameter required_zone_names
  - Model ThroughputSettingsGetPropertiesResource has a new parameter provisioned_throughput_settings
  - Model PrivateEndpointConnection has a new parameter group_id
  - Model PrivateEndpointConnection has a new parameter provisioning_state
  - Model MongoDBDatabaseGetResults has a new parameter options
  - Model SqlContainerGetResults has a new parameter options
  - Model TableGetResults has a new parameter options
  - Model SqlDatabaseGetResults has a new parameter options
  - Model CassandraKeyspaceGetResults has a new parameter options
  - Model ThroughputSettingsResource has a new parameter provisioned_throughput_settings
  - Model DatabaseAccountGetResults has a new parameter public_network_access
  - Model GremlinDatabaseGetResults has a new parameter options
  - Model MongoDBCollectionGetResults has a new parameter options
  - Model CassandraTableGetResults has a new parameter options
  - Added operation group NotebookWorkspacesOperations

**Breaking changes**

  - Model ThroughputSettingsGetPropertiesResource no longer has parameter autopilot_settings
  - Model ThroughputSettingsResource no longer has parameter autopilot_settings
  - Operation PrivateEndpointConnectionsOperations.create_or_update has a new signature

## 0.12.0 (2020-02-27)

**Features**

  - Model DatabaseAccountGetResults has a new parameter key_vault_key_uri
  - Model ThroughputSettingsResource has a new parameter autopilot_settings
  - Model ThroughputSettingsGetPropertiesResource has a new parameter autopilot_settings
  - Model DatabaseAccountCreateUpdateParameters has a new parameter key_vault_key_uri
  - Model DatabaseAccountUpdateParameters has a new parameter key_vault_key_uri

## 0.11.0 (2019-12-07)

**Features**

  - Model GremlinDatabaseGetResults has a new parameter resource
  - Model ThroughputSettingsGetResults has a new parameter resource
  - Model SqlStoredProcedureGetResults has a new parameter resource
  - Model MongoDBDatabaseGetResults has a new parameter resource
  - Model SqlUserDefinedFunctionGetResults has a new parameter resource
  - Model TableGetResults has a new parameter resource
  - Model IndexingPolicy has a new parameter composite_indexes
  - Model IndexingPolicy has a new parameter spatial_indexes
  - Model CassandraKeyspaceGetResults has a new parameter resource
  - Model SqlDatabaseGetResults has a new parameter resource

**Breaking changes**

  - Model GremlinDatabaseGetResults no longer has parameter _etag
  - Model GremlinDatabaseGetResults no longer has parameter
    gremlin_database_get_results_id
  - Model GremlinDatabaseGetResults no longer has parameter _ts
  - Model GremlinDatabaseGetResults no longer has parameter _rid
  - Model ThroughputSettingsGetResults no longer has parameter
    minimum_throughput
  - Model ThroughputSettingsGetResults no longer has parameter
    offer_replace_pending
  - Model ThroughputSettingsGetResults no longer has parameter
    throughput
  - Model SqlStoredProcedureGetResults no longer has parameter _etag
  - Model SqlStoredProcedureGetResults no longer has parameter _ts
  - Model SqlStoredProcedureGetResults no longer has parameter _rid
  - Model SqlStoredProcedureGetResults no longer has parameter body
  - Model SqlStoredProcedureGetResults no longer has parameter
    sql_stored_procedure_get_results_id
  - Model MongoDBDatabaseGetResults no longer has parameter _etag
  - Model MongoDBDatabaseGetResults no longer has parameter
    mongo_db_database_get_results_id
  - Model MongoDBDatabaseGetResults no longer has parameter _ts
  - Model MongoDBDatabaseGetResults no longer has parameter _rid
  - Model SqlUserDefinedFunctionGetResults no longer has parameter
    _etag
  - Model SqlUserDefinedFunctionGetResults no longer has parameter
    sql_user_defined_function_get_results_id
  - Model SqlUserDefinedFunctionGetResults no longer has parameter _ts
  - Model SqlUserDefinedFunctionGetResults no longer has parameter _rid
  - Model SqlUserDefinedFunctionGetResults no longer has parameter body
  - Model TableGetResults no longer has parameter _etag
  - Model TableGetResults no longer has parameter
    table_get_results_id
  - Model TableGetResults no longer has parameter _ts
  - Model TableGetResults no longer has parameter _rid
  - Model CassandraKeyspaceGetResults no longer has parameter _etag
  - Model CassandraKeyspaceGetResults no longer has parameter
    cassandra_keyspace_get_results_id
  - Model CassandraKeyspaceGetResults no longer has parameter _ts
  - Model CassandraKeyspaceGetResults no longer has parameter _rid
  - Model SqlDatabaseGetResults no longer has parameter _colls
  - Model SqlDatabaseGetResults no longer has parameter _etag
  - Model SqlDatabaseGetResults no longer has parameter _users
  - Model SqlDatabaseGetResults no longer has parameter
    sql_database_get_results_id
  - Model SqlDatabaseGetResults no longer has parameter _rid
  - Model SqlDatabaseGetResults no longer has parameter _ts
  - Model GremlinGraphGetResults has a new signature
  - Model CassandraTableGetResults has a new signature
  - Model SqlTriggerGetResults has a new signature
  - Model SqlContainerGetResults has a new signature
  - Model MongoDBCollectionGetResults has a new signature

## 0.10.0 (2019-11-13)

**Features**

  - Model DatabaseAccountCreateUpdateParameters has a new parameter
    disable_key_based_metadata_write_access
  - Model ContainerPartitionKey has a new parameter version
  - Added operation DatabaseAccountsOperations.update
  - Added operation group SqlResourcesOperations
  - Added operation group MongoDBResourcesOperations
  - Added operation group TableResourcesOperations
  - Added operation group GremlinResourcesOperations
  - Added operation group CassandraResourcesOperations

**Breaking changes**

  - CosmosDB has been renamed to CosmosDBManagementClient
  - CosmosDBConfiguration was renamed to
    CosmodDBManagementClientConfiguration
  - Model MongoDBCollectionCreateUpdateParameters has a new signature
  - Model GremlinGraphCreateUpdateParameters has a new signature
  - Model CassandraKeyspaceCreateUpdateParameters has a new signature
  - Model GremlinDatabaseCreateUpdateParameters has a new signature
  - Model SqlContainerCreateUpdateParameters has a new signature
  - Model CassandraTableCreateUpdateParameters has a new signature
  - Model TableCreateUpdateParameters has a new signature
  - Model MongoDBDatabaseCreateUpdateParameters has a new signature
  - Model SqlDatabaseCreateUpdateParameters has a new signature
  - Removed operation
    DatabaseAccountsOperations.get_gremlin_graph_throughput
  - Removed operation
    DatabaseAccountsOperations.update_cassandra_keyspace_throughput
  - Removed operation DatabaseAccountsOperations.delete_sql_database
  - Removed operation
    DatabaseAccountsOperations.update_sql_database_throughput
  - Removed operation
    DatabaseAccountsOperations.update_mongo_db_database_throughput
  - Removed operation
    DatabaseAccountsOperations.delete_mongo_db_collection
  - Removed operation
    DatabaseAccountsOperations.list_mongo_db_databases
  - Removed operation
    DatabaseAccountsOperations.create_update_mongo_db_database
  - Removed operation
    DatabaseAccountsOperations.create_update_gremlin_graph
  - Removed operation
    DatabaseAccountsOperations.update_gremlin_database_throughput
  - Removed operation
    DatabaseAccountsOperations.get_mongo_db_collection
  - Removed operation
    DatabaseAccountsOperations.delete_gremlin_database
  - Removed operation
    DatabaseAccountsOperations.create_update_cassandra_keyspace
  - Removed operation DatabaseAccountsOperations.get_sql_database
  - Removed operation DatabaseAccountsOperations.get_table
  - Removed operation
    DatabaseAccountsOperations.update_table_throughput
  - Removed operation
    DatabaseAccountsOperations.create_update_mongo_db_collection
  - Removed operation DatabaseAccountsOperations.get_gremlin_database
  - Removed operation
    DatabaseAccountsOperations.create_update_sql_container
  - Removed operation
    DatabaseAccountsOperations.create_update_gremlin_database
  - Removed operation DatabaseAccountsOperations.get_table_throughput
  - Removed operation
    DatabaseAccountsOperations.delete_mongo_db_database
  - Removed operation
    DatabaseAccountsOperations.get_cassandra_table_throughput
  - Removed operation
    DatabaseAccountsOperations.update_sql_container_throughput
  - Removed operation DatabaseAccountsOperations.get_cassandra_table
  - Removed operation
    DatabaseAccountsOperations.list_gremlin_databases
  - Removed operation DatabaseAccountsOperations.list_gremlin_graphs
  - Removed operation
    DatabaseAccountsOperations.list_mongo_db_collections
  - Removed operation
    DatabaseAccountsOperations.create_update_cassandra_table
  - Removed operation
    DatabaseAccountsOperations.delete_cassandra_keyspace
  - Removed operation
    DatabaseAccountsOperations.update_cassandra_table_throughput
  - Removed operation
    DatabaseAccountsOperations.update_gremlin_graph_throughput
  - Removed operation DatabaseAccountsOperations.create_update_table
  - Removed operation
    DatabaseAccountsOperations.get_mongo_db_database_throughput
  - Removed operation DatabaseAccountsOperations.get_sql_container
  - Removed operation
    DatabaseAccountsOperations.get_gremlin_database_throughput
  - Removed operation
    DatabaseAccountsOperations.get_mongo_db_collection_throughput
  - Removed operation DatabaseAccountsOperations.list_cassandra_tables
  - Removed operation
    DatabaseAccountsOperations.get_sql_database_throughput
  - Removed operation DatabaseAccountsOperations.list_sql_databases
  - Removed operation DatabaseAccountsOperations.list_tables
  - Removed operation
    DatabaseAccountsOperations.get_cassandra_keyspace
  - Removed operation DatabaseAccountsOperations.get_gremlin_graph
  - Removed operation
    DatabaseAccountsOperations.get_mongo_db_database
  - Removed operation DatabaseAccountsOperations.delete_table
  - Removed operation
    DatabaseAccountsOperations.list_cassandra_keyspaces
  - Removed operation DatabaseAccountsOperations.list_sql_containers
  - Removed operation DatabaseAccountsOperations.delete_sql_container
  - Removed operation DatabaseAccountsOperations.delete_gremlin_graph
  - Removed operation
    DatabaseAccountsOperations.get_cassandra_keyspace_throughput
  - Removed operation
    DatabaseAccountsOperations.get_sql_container_throughput
  - Removed operation
    DatabaseAccountsOperations.delete_cassandra_table
  - Removed operation DatabaseAccountsOperations.patch
  - Removed operation
    DatabaseAccountsOperations.create_update_sql_database
  - Removed operation
    DatabaseAccountsOperations.update_mongo_db_collection_throughput

## 0.9.0 (2019-11-09)

**Features**

  - Added operation group PrivateLinkResourcesOperations
  - Added operation group PrivateEndpointConnectionsOperations

## 0.8.0 (2019-08-15)

**Features**

  - Model DatabaseAccount has a new parameter
    enable_cassandra_connector
  - Model DatabaseAccount has a new parameter connector_offer
  - Model DatabaseAccountCreateUpdateParameters has a new parameter
    enable_cassandra_connector
  - Model DatabaseAccountCreateUpdateParameters has a new parameter
    connector_offer

**General breaking changes**

This version uses a next-generation code generator that *might*
introduce breaking changes if from some import. In summary, some modules
were incorrectly visible/importable and have been renamed. This fixed
several issues caused by usage of classes that were not supposed to be
used in the first place.

  - CosmosDB cannot be imported from `azure.mgmt.cosmosdb.cosmos_db`
    anymore (import from `azure.mgmt.cosmosdb` works like before)
  - CosmosDBConfiguration import has been moved from
    `azure.mgmt.cosmosdb.cosmos_db` to `azure.mgmt.cosmosdb`
  - A model `MyClass` from a "models" sub-module cannot be imported
    anymore using `azure.mgmt.cosmosdb.models.my_class` (import from
    `azure.mgmt.cosmosdb.models` works like before)
  - An operation class `MyClassOperations` from an `operations`
    sub-module cannot be imported anymore using
    `azure.mgmt.cosmosdb.operations.my_class_operations` (import
    from `azure.mgmt.cosmosdb.operations` works like before)

Last but not least, HTTP connection pooling is now enabled by default.
You should always use a client as a context manager, or call close(), or
use no more than one client per process.

## 0.7.0 (2019-06-07)

**Features**

  - Added operation
    DatabaseAccountsOperations.get_gremlin_graph_throughput
  - Added operation
    DatabaseAccountsOperations.get_sql_database_throughput
  - Added operation
    DatabaseAccountsOperations.update_gremlin_database_throughput
  - Added operation
    DatabaseAccountsOperations.get_sql_container_throughput
  - Added operation
    DatabaseAccountsOperations.update_sql_container_throughput
  - Added operation
    DatabaseAccountsOperations.get_gremlin_database_throughput
  - Added operation
    DatabaseAccountsOperations.get_cassandra_table_throughput
  - Added operation
    DatabaseAccountsOperations.update_cassandra_keyspace_throughput
  - Added operation
    DatabaseAccountsOperations.update_mongo_db_collection_throughput
  - Added operation
    DatabaseAccountsOperations.update_cassandra_table_throughput
  - Added operation DatabaseAccountsOperations.update_table_throughput
  - Added operation
    DatabaseAccountsOperations.update_mongo_db_database_throughput
  - Added operation
    DatabaseAccountsOperations.get_mongo_db_database_throughput
  - Added operation
    DatabaseAccountsOperations.update_sql_database_throughput
  - Added operation DatabaseAccountsOperations.get_table_throughput
  - Added operation
    DatabaseAccountsOperations.get_mongo_db_collection_throughput
  - Added operation
    DatabaseAccountsOperations.update_gremlin_graph_throughput
  - Added operation
    DatabaseAccountsOperations.get_cassandra_keyspace_throughput

## 0.6.1 (2019-05-31)

**Features**

  - Add is_zone_redundant attribute

**Bugfix**

  - Fix some incorrect type from int to long (Python 2)

## 0.6.0 (2019-05-03)

**Features**

  - Added operation DatabaseAccountsOperations.list_sql_databases
  - Added operation DatabaseAccountsOperations.delete_gremlin_graph
  - Added operation DatabaseAccountsOperations.get_sql_database
  - Added operation DatabaseAccountsOperations.delete_table
  - Added operation DatabaseAccountsOperations.get_cassandra_keyspace
  - Added operation DatabaseAccountsOperations.list_sql_containers
  - Added operation
    DatabaseAccountsOperations.create_update_sql_container
  - Added operation DatabaseAccountsOperations.get_table
  - Added operation DatabaseAccountsOperations.list_cassandra_tables
  - Added operation DatabaseAccountsOperations.create_update_table
  - Added operation
    DatabaseAccountsOperations.delete_mongo_db_collection
  - Added operation DatabaseAccountsOperations.get_gremlin_graph
  - Added operation DatabaseAccountsOperations.get_gremlin_database
  - Added operation
    DatabaseAccountsOperations.list_cassandra_keyspaces
  - Added operation
    DatabaseAccountsOperations.create_update_mongo_db_collection
  - Added operation
    DatabaseAccountsOperations.create_update_cassandra_keyspace
  - Added operation
    DatabaseAccountsOperations.create_update_cassandra_table
  - Added operation DatabaseAccountsOperations.get_mongo_db_database
  - Added operation DatabaseAccountsOperations.list_gremlin_databases
  - Added operation
    DatabaseAccountsOperations.create_update_sql_database
  - Added operation
    DatabaseAccountsOperations.get_mongo_db_collection
  - Added operation
    DatabaseAccountsOperations.list_mongo_db_collections
  - Added operation DatabaseAccountsOperations.get_sql_container
  - Added operation
    DatabaseAccountsOperations.delete_cassandra_keyspace
  - Added operation
    DatabaseAccountsOperations.delete_mongo_db_database
  - Added operation DatabaseAccountsOperations.get_cassandra_table
  - Added operation DatabaseAccountsOperations.delete_cassandra_table
  - Added operation
    DatabaseAccountsOperations.list_mongo_db_databases
  - Added operation DatabaseAccountsOperations.list_gremlin_graphs
  - Added operation
    DatabaseAccountsOperations.create_update_mongo_db_database
  - Added operation DatabaseAccountsOperations.delete_sql_container
  - Added operation
    DatabaseAccountsOperations.create_update_gremlin_graph
  - Added operation
    DatabaseAccountsOperations.create_update_gremlin_database
  - Added operation DatabaseAccountsOperations.list_tables
  - Added operation DatabaseAccountsOperations.delete_gremlin_database
  - Added operation DatabaseAccountsOperations.delete_sql_database

## 0.5.2 (2018-11-05)

**Features**

  - Add ignore_missing_vnet_service_endpoint support

## 0.5.1 (2018-10-16)

**Bugfix**

  - Fix sdist broken in 0.5.0. No code change.

## 0.5.0 (2018-10-08)

**Features**

  - Add enable_multiple_write_locations support

**Note**

  - `database_accounts.list_read_only_keys` is now doing a POST
    call, and not GET anymore. This should not impact anything. Old
    behavior be can found with the
    `database_accounts.get_read_only_keys` **deprecated** method.
  - azure-mgmt-nspkg is not installed anymore on Python 3 (PEP420-based
    namespace package)

## 0.4.1 (2018-05-15)

**Features**

  - Add database_accounts.offline_region
  - Add database_accounts.online_region
  - Client class can be used as a context manager to keep the underlying
    HTTP session open for performance

## 0.4.0 (2018-04-17)

**General Breaking changes**

This version uses a next-generation code generator that *might*
introduce breaking changes.

  - Model signatures now use only keyword-argument syntax. All
    positional arguments must be re-written as keyword-arguments. To
    keep auto-completion in most cases, models are now generated for
    Python 2 and Python 3. Python 3 uses the "*" syntax for
    keyword-only arguments.
  - Enum types now use the "str" mixin (class AzureEnum(str, Enum)) to
    improve the behavior when unrecognized enum values are encountered.
    While this is not a breaking change, the distinctions are important,
    and are documented here:
    <https://docs.python.org/3/library/enum.html#others> At a glance:
      - "is" should not be used at all.
      - "format" will return the string value, where "%s" string
        formatting will return `NameOfEnum.stringvalue`. Format syntax
        should be prefered.
  - New Long Running Operation:
      - Return type changes from
        `msrestazure.azure_operation.AzureOperationPoller` to
        `msrest.polling.LROPoller`. External API is the same.
      - Return type is now **always** a `msrest.polling.LROPoller`,
        regardless of the optional parameters used.
      - The behavior has changed when using `raw=True`. Instead of
        returning the initial call result as `ClientRawResponse`,
        without polling, now this returns an LROPoller. After polling,
        the final resource will be returned as a `ClientRawResponse`.
      - New `polling` parameter. The default behavior is
        `Polling=True` which will poll using ARM algorithm. When
        `Polling=False`, the response of the initial call will be
        returned without polling.
      - `polling` parameter accepts instances of subclasses of
        `msrest.polling.PollingMethod`.
      - `add_done_callback` will no longer raise if called after
        polling is finished, but will instead execute the callback right
        away.

**Bugfixes**

  - Compatibility of the sdist with wheel 0.31.0

**Features**

  - Add VNet related properties to CosmosDB

## 0.3.1 (2018-02-01)

**Bugfixes**

  - Fix capabilities model definition

## 0.3.0 (2018-01-30)

**Features**

  - Add capability
  - Add metrics operation groups

## 0.2.1 (2017-10-18)

**Bugfixes**

  - Fix max_interval_in_seconds interval values from 1/100 to 5/86400
  - Tags is now optional

**Features**

  - Add operation list

## 0.2.0 (2017-06-26)

  - Creation on this package based on azure-mgmt-documentdb 0.1.3
    content
