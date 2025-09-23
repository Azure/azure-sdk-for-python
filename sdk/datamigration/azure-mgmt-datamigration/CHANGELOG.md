# Release History

## 10.1.0 (2025-09-22)

### Features Added

  - Client `DataMigrationManagementClient` added operation group `database_migrations_mongo_to_cosmos_db_ru_mongo`
  - Client `DataMigrationManagementClient` added operation group `database_migrations_mongo_to_cosmos_dbv_core_mongo`
  - Client `DataMigrationManagementClient` added operation group `database_migrations_sql_db`
  - Client `DataMigrationManagementClient` added operation group `database_migrations_sql_mi`
  - Client `DataMigrationManagementClient` added operation group `database_migrations_sql_vm`
  - Client `DataMigrationManagementClient` added operation group `migration_services`
  - Client `DataMigrationManagementClient` added operation group `sql_migration_services`
  - Model `AzureActiveDirectoryApp` added property `ignore_azure_permissions`
  - Model `ConnectToSourceSqlServerTaskInput` added property `encrypted_key_for_secure_fields`
  - Model `ConnectToSourceSqlServerTaskProperties` added property `task_id`
  - Model `ConnectToTargetSqlDbTaskInput` added property `query_object_counts`
  - Model `ConnectToTargetSqlDbTaskProperties` added property `created_on`
  - Model `DataMigrationService` added property `auto_stop_delay`
  - Model `DataMigrationService` added property `delete_resources_on_stop`
  - Model `DataMigrationServiceStatusResponse` added property `agent_configuration`
  - Model `GetUserTablesSqlTaskInput` added property `encrypted_key_for_secure_fields`
  - Model `GetUserTablesSqlTaskProperties` added property `task_id`
  - Model `MigrateMySqlAzureDbForMySqlOfflineTaskInput` added property `encrypted_key_for_secure_fields`
  - Model `MigrateMySqlAzureDbForMySqlOfflineTaskProperties` added property `is_cloneable`
  - Model `MigrateMySqlAzureDbForMySqlOfflineTaskProperties` added property `task_id`
  - Model `MigratePostgreSqlAzureDbForPostgreSqlSyncDatabaseInput` added property `id`
  - Model `MigratePostgreSqlAzureDbForPostgreSqlSyncTaskInput` added property `encrypted_key_for_secure_fields`
  - Model `MigratePostgreSqlAzureDbForPostgreSqlSyncTaskInput` added property `started_on`
  - Model `MigratePostgreSqlAzureDbForPostgreSqlSyncTaskOutputError` added property `events`
  - Model `MigratePostgreSqlAzureDbForPostgreSqlSyncTaskOutputMigrationLevel` added property `database_count`
  - Model `MigratePostgreSqlAzureDbForPostgreSqlSyncTaskProperties` added property `task_id`
  - Model `MigratePostgreSqlAzureDbForPostgreSqlSyncTaskProperties` added property `created_on`
  - Model `MigratePostgreSqlAzureDbForPostgreSqlSyncTaskProperties` added property `is_cloneable`
  - Model `MigrateSchemaSqlServerSqlDbDatabaseInput` added property `id`
  - Model `MigrateSchemaSqlServerSqlDbTaskInput` added property `encrypted_key_for_secure_fields`
  - Model `MigrateSchemaSqlServerSqlDbTaskInput` added property `started_on`
  - Model `MigrateSchemaSqlServerSqlDbTaskProperties` added property `created_on`
  - Model `MigrateSchemaSqlServerSqlDbTaskProperties` added property `task_id`
  - Model `MigrateSchemaSqlServerSqlDbTaskProperties` added property `is_cloneable`
  - Model `MigrateSqlServerSqlDbDatabaseInput` added property `schema_setting`
  - Model `MigrateSqlServerSqlDbDatabaseInput` added property `id`
  - Model `MigrateSqlServerSqlDbTaskInput` added property `started_on`
  - Model `MigrateSqlServerSqlDbTaskInput` added property `encrypted_key_for_secure_fields`
  - Model `MigrateSqlServerSqlDbTaskProperties` added property `task_id`
  - Model `MigrateSqlServerSqlDbTaskProperties` added property `is_cloneable`
  - Model `MigrateSqlServerSqlDbTaskProperties` added property `created_on`
  - Model `MigrateSqlServerSqlMIDatabaseInput` added property `id`
  - Model `MigrateSqlServerSqlMISyncTaskInput` added property `number_of_parallel_database_migrations`
  - Model `MigrateSqlServerSqlMISyncTaskProperties` added property `created_on`
  - Model `MigrateSqlServerSqlMITaskInput` added property `started_on`
  - Model `MigrateSqlServerSqlMITaskInput` added property `encrypted_key_for_secure_fields`
  - Model `MigrateSqlServerSqlMITaskProperties` added property `task_id`
  - Model `MigrateSqlServerSqlMITaskProperties` added property `created_on`
  - Model `MigrateSqlServerSqlMITaskProperties` added property `parent_task_id`
  - Model `MigrateSqlServerSqlMITaskProperties` added property `is_cloneable`
  - Model `MigrateSyncCompleteCommandProperties` added property `command_id`
  - Model `MongoDbConnectionInfo` added property `data_source`
  - Model `MongoDbConnectionInfo` added property `encrypt_connection`
  - Model `MongoDbConnectionInfo` added property `server_brand_version`
  - Model `MongoDbConnectionInfo` added property `server_version`
  - Model `MongoDbConnectionInfo` added property `server_name`
  - Model `MongoDbConnectionInfo` added property `trust_server_certificate`
  - Model `MongoDbConnectionInfo` added property `enforce_ssl`
  - Model `MongoDbConnectionInfo` added property `port`
  - Model `MongoDbConnectionInfo` added property `additional_settings`
  - Model `MongoDbConnectionInfo` added property `authentication`
  - Model `MySqlConnectionInfo` added property `data_source`
  - Model `MySqlConnectionInfo` added property `authentication`
  - Model `MySqlConnectionInfo` added property `additional_settings`
  - Model `OracleConnectionInfo` added property `server_name`
  - Model `OracleConnectionInfo` added property `server_version`
  - Model `OracleConnectionInfo` added property `port`
  - Model `OracleConnectionInfo` added property `authentication`
  - Model `PostgreSqlConnectionInfo` added property `data_source`
  - Model `PostgreSqlConnectionInfo` added property `server_version`
  - Model `PostgreSqlConnectionInfo` added property `additional_settings`
  - Model `PostgreSqlConnectionInfo` added property `server_brand_version`
  - Model `PostgreSqlConnectionInfo` added property `authentication`
  - Model `Project` added property `etag`
  - Model `Project` added property `azure_authentication_info`
  - Model `Resource` added property `system_data`
  - Model `SchemaMigrationSetting` added property `file_name`
  - Enum `ServerLevelPermissionsGroup` added member `MIGRATION_FROM_SQL_SERVER_TO_AZURE_VM`
  - Model `SqlConnectionInfo` added property `server_name`
  - Model `SqlConnectionInfo` added property `port`
  - Model `SqlConnectionInfo` added property `server_version`
  - Model `SqlConnectionInfo` added property `server_brand_version`
  - Model `SqlConnectionInfo` added property `resource_id`
  - Added enum `AuthType`
  - Added model `AuthenticationKeys`
  - Added model `AzureBlob`
  - Added model `BackupConfiguration`
  - Added enum `CommandType`
  - Added model `CopyProgressDetails`
  - Added model `DatabaseMigration`
  - Added model `DatabaseMigrationBase`
  - Added model `DatabaseMigrationBaseListResult`
  - Added model `DatabaseMigrationBaseProperties`
  - Added model `DatabaseMigrationCosmosDbMongo`
  - Added model `DatabaseMigrationCosmosDbMongoListResult`
  - Added model `DatabaseMigrationListResult`
  - Added model `DatabaseMigrationProperties`
  - Added model `DatabaseMigrationPropertiesCosmosDbMongo`
  - Added model `DatabaseMigrationPropertiesSqlDb`
  - Added model `DatabaseMigrationPropertiesSqlMi`
  - Added model `DatabaseMigrationPropertiesSqlVm`
  - Added model `DatabaseMigrationSqlDb`
  - Added model `DatabaseMigrationSqlMi`
  - Added model `DatabaseMigrationSqlVm`
  - Added model `DeleteNode`
  - Added model `ErrorAdditionalInfo`
  - Added model `ErrorDetail`
  - Added model `ErrorInfo`
  - Added model `ErrorResponse`
  - Added model `IntegrationRuntimeMonitoringData`
  - Added model `ManagedServiceIdentity`
  - Added enum `ManagedServiceIdentityType`
  - Added model `MigrationOperationInput`
  - Added model `MigrationService`
  - Added model `MigrationServiceListResult`
  - Added model `MigrationServiceUpdate`
  - Added model `MigrationStatusDetails`
  - Added model `MongoConnectionInformation`
  - Added model `MongoMigrationCollection`
  - Added model `MongoMigrationProgressDetails`
  - Added enum `MongoMigrationStatus`
  - Added model `NodeMonitoringData`
  - Added model `OfflineConfiguration`
  - Added model `OperationListResult`
  - Added enum `OperationOrigin`
  - Added model `OperationsDefinition`
  - Added model `OperationsDisplayDefinition`
  - Added enum `ProvisioningState`
  - Added model `ProxyResource`
  - Added model `ProxyResourceAutoGenerated`
  - Added model `RegenAuthKeys`
  - Added model `ResourceAutoGenerated`
  - Added enum `ResourceType`
  - Added model `SourceLocation`
  - Added model `SqlBackupFileInfo`
  - Added model `SqlBackupSetInfo`
  - Added model `SqlConnectionInformation`
  - Added model `SqlDbMigrationStatusDetails`
  - Added model `SqlDbOfflineConfiguration`
  - Added model `SqlFileShare`
  - Added model `SqlMigrationListResult`
  - Added model `SqlMigrationService`
  - Added model `SqlMigrationServiceUpdate`
  - Added model `SystemDataAutoGenerated`
  - Added model `TargetLocation`
  - Added enum `TaskType`
  - Added model `TrackedResourceAutoGenerated`
  - Added model `UserAssignedIdentity`
  - Added operation group `DatabaseMigrationsMongoToCosmosDbRUMongoOperations`
  - Added operation group `DatabaseMigrationsMongoToCosmosDbvCoreMongoOperations`
  - Added operation group `DatabaseMigrationsSqlDbOperations`
  - Added operation group `DatabaseMigrationsSqlMiOperations`
  - Added operation group `DatabaseMigrationsSqlVmOperations`
  - Added operation group `MigrationServicesOperations`
  - Added operation group `SqlMigrationServicesOperations`

## 10.1.0b2 (2025-06-17)

### Features Added

  - Client `DataMigrationManagementClient` added operation group `database_migrations_mongo_to_cosmos_db_ru_mongo`
  - Client `DataMigrationManagementClient` added operation group `database_migrations_mongo_to_cosmos_dbv_core_mongo`
  - Client `DataMigrationManagementClient` added operation group `migration_services`
  - Model `AzureBlob` added property `auth_type`
  - Model `AzureBlob` added property `identity`
  - Model `ProxyResource` added property `system_data`
  - Model `Resource` added property `system_data`
  - Enum `ResourceType` added member `MONGO_TO_COSMOS_DB_MONGO`
  - Added enum `AuthType`
  - Added model `DatabaseMigrationBase`
  - Added model `DatabaseMigrationBaseListResult`
  - Added model `DatabaseMigrationBaseProperties`
  - Added model `DatabaseMigrationCosmosDbMongo`
  - Added model `DatabaseMigrationCosmosDbMongoListResult`
  - Added model `DatabaseMigrationPropertiesCosmosDbMongo`
  - Added model `ErrorAdditionalInfo`
  - Added model `ErrorDetail`
  - Added model `ErrorResponse`
  - Added model `ManagedServiceIdentity`
  - Added enum `ManagedServiceIdentityType`
  - Added model `MigrationService`
  - Added model `MigrationServiceListResult`
  - Added model `MigrationServiceUpdate`
  - Added model `MongoConnectionInformation`
  - Added model `MongoMigrationCollection`
  - Added model `MongoMigrationProgressDetails`
  - Added enum `MongoMigrationStatus`
  - Added enum `ProvisioningState`
  - Added model `ProxyResourceAutoGenerated`
  - Added model `ResourceAutoGenerated`
  - Added model `SystemDataAutoGenerated`
  - Added model `TrackedResourceAutoGenerated`
  - Added model `UserAssignedIdentity`
  - Added operation group `DatabaseMigrationsMongoToCosmosDbRUMongoOperations`
  - Added operation group `DatabaseMigrationsMongoToCosmosDbvCoreMongoOperations`
  - Added operation group `MigrationServicesOperations`

### Breaking Changes
  - Parameter `location` of method `TrackedResource.__init__` is now required

## 10.1.0b1 (2022-11-18)

### Features Added

  - Added operation group DatabaseMigrationsSqlDbOperations
  - Added operation group DatabaseMigrationsSqlMiOperations
  - Added operation group DatabaseMigrationsSqlVmOperations
  - Added operation group SqlMigrationServicesOperations
  - Model AzureActiveDirectoryApp has a new parameter ignore_azure_permissions
  - Model ConnectToSourceSqlServerTaskInput has a new parameter encrypted_key_for_secure_fields
  - Model ConnectToSourceSqlServerTaskProperties has a new parameter task_id
  - Model ConnectToTargetSqlDbTaskInput has a new parameter query_object_counts
  - Model ConnectToTargetSqlDbTaskProperties has a new parameter created_on
  - Model DataMigrationService has a new parameter auto_stop_delay
  - Model DataMigrationService has a new parameter delete_resources_on_stop
  - Model DataMigrationServiceStatusResponse has a new parameter agent_configuration
  - Model GetUserTablesSqlTaskInput has a new parameter encrypted_key_for_secure_fields
  - Model GetUserTablesSqlTaskProperties has a new parameter task_id
  - Model MigrateMySqlAzureDbForMySqlOfflineTaskInput has a new parameter encrypted_key_for_secure_fields
  - Model MigrateMySqlAzureDbForMySqlOfflineTaskProperties has a new parameter is_cloneable
  - Model MigrateMySqlAzureDbForMySqlOfflineTaskProperties has a new parameter task_id
  - Model MigratePostgreSqlAzureDbForPostgreSqlSyncDatabaseInput has a new parameter id
  - Model MigratePostgreSqlAzureDbForPostgreSqlSyncTaskInput has a new parameter encrypted_key_for_secure_fields
  - Model MigratePostgreSqlAzureDbForPostgreSqlSyncTaskInput has a new parameter started_on
  - Model MigratePostgreSqlAzureDbForPostgreSqlSyncTaskOutputError has a new parameter events
  - Model MigratePostgreSqlAzureDbForPostgreSqlSyncTaskOutputMigrationLevel has a new parameter database_count
  - Model MigratePostgreSqlAzureDbForPostgreSqlSyncTaskProperties has a new parameter created_on
  - Model MigratePostgreSqlAzureDbForPostgreSqlSyncTaskProperties has a new parameter is_cloneable
  - Model MigratePostgreSqlAzureDbForPostgreSqlSyncTaskProperties has a new parameter task_id
  - Model MigrateSchemaSqlServerSqlDbDatabaseInput has a new parameter id
  - Model MigrateSchemaSqlServerSqlDbTaskInput has a new parameter encrypted_key_for_secure_fields
  - Model MigrateSchemaSqlServerSqlDbTaskInput has a new parameter started_on
  - Model MigrateSchemaSqlServerSqlDbTaskProperties has a new parameter created_on
  - Model MigrateSchemaSqlServerSqlDbTaskProperties has a new parameter is_cloneable
  - Model MigrateSchemaSqlServerSqlDbTaskProperties has a new parameter task_id
  - Model MigrateSqlServerSqlDbDatabaseInput has a new parameter id
  - Model MigrateSqlServerSqlDbDatabaseInput has a new parameter schema_setting
  - Model MigrateSqlServerSqlDbTaskInput has a new parameter encrypted_key_for_secure_fields
  - Model MigrateSqlServerSqlDbTaskInput has a new parameter started_on
  - Model MigrateSqlServerSqlDbTaskProperties has a new parameter created_on
  - Model MigrateSqlServerSqlDbTaskProperties has a new parameter is_cloneable
  - Model MigrateSqlServerSqlDbTaskProperties has a new parameter task_id
  - Model MigrateSqlServerSqlMIDatabaseInput has a new parameter id
  - Model MigrateSqlServerSqlMISyncTaskInput has a new parameter number_of_parallel_database_migrations
  - Model MigrateSqlServerSqlMISyncTaskProperties has a new parameter created_on
  - Model MigrateSqlServerSqlMITaskInput has a new parameter encrypted_key_for_secure_fields
  - Model MigrateSqlServerSqlMITaskInput has a new parameter started_on
  - Model MigrateSqlServerSqlMITaskProperties has a new parameter created_on
  - Model MigrateSqlServerSqlMITaskProperties has a new parameter is_cloneable
  - Model MigrateSqlServerSqlMITaskProperties has a new parameter parent_task_id
  - Model MigrateSqlServerSqlMITaskProperties has a new parameter task_id
  - Model MigrateSyncCompleteCommandProperties has a new parameter command_id
  - Model MongoDbConnectionInfo has a new parameter additional_settings
  - Model MongoDbConnectionInfo has a new parameter authentication
  - Model MongoDbConnectionInfo has a new parameter data_source
  - Model MongoDbConnectionInfo has a new parameter encrypt_connection
  - Model MongoDbConnectionInfo has a new parameter enforce_ssl
  - Model MongoDbConnectionInfo has a new parameter port
  - Model MongoDbConnectionInfo has a new parameter server_brand_version
  - Model MongoDbConnectionInfo has a new parameter server_name
  - Model MongoDbConnectionInfo has a new parameter server_version
  - Model MongoDbConnectionInfo has a new parameter trust_server_certificate
  - Model MySqlConnectionInfo has a new parameter additional_settings
  - Model MySqlConnectionInfo has a new parameter authentication
  - Model MySqlConnectionInfo has a new parameter data_source
  - Model OracleConnectionInfo has a new parameter authentication
  - Model OracleConnectionInfo has a new parameter port
  - Model OracleConnectionInfo has a new parameter server_name
  - Model OracleConnectionInfo has a new parameter server_version
  - Model PostgreSqlConnectionInfo has a new parameter additional_settings
  - Model PostgreSqlConnectionInfo has a new parameter authentication
  - Model PostgreSqlConnectionInfo has a new parameter data_source
  - Model PostgreSqlConnectionInfo has a new parameter server_brand_version
  - Model PostgreSqlConnectionInfo has a new parameter server_version
  - Model Project has a new parameter azure_authentication_info
  - Model Project has a new parameter etag
  - Model SchemaMigrationSetting has a new parameter file_name
  - Model SqlConnectionInfo has a new parameter port
  - Model SqlConnectionInfo has a new parameter resource_id
  - Model SqlConnectionInfo has a new parameter server_brand_version
  - Model SqlConnectionInfo has a new parameter server_name
  - Model SqlConnectionInfo has a new parameter server_version

## 10.0.0 (2021-08-19)

**Features**

  - Model ConnectToTargetAzureDbForMySqlTaskInput has a new parameter is_offline_migration
  - Model MySqlConnectionInfo has a new parameter encrypt_connection
  - Model TrackedResource has a new parameter system_data
  - Model Project has a new parameter system_data
  - Model ApiError has a new parameter system_data
  - Model ProjectFile has a new parameter system_data
  - Model DataMigrationService has a new parameter system_data
  - Model ConnectToSourceMySqlTaskInput has a new parameter is_offline_migration
  - Model ProjectTask has a new parameter system_data

**Breaking changes**

  - Parameter result_type of model MigrateSchemaSqlServerSqlDbTaskOutputError is now required
  - Parameter result_type of model MigrateSchemaSqlServerSqlDbTaskOutput is now required
  - Parameter result_type of model MigrateSchemaSqlServerSqlDbTaskOutputMigrationLevel is now required
  - Parameter result_type of model MigrateSchemaSqlServerSqlDbTaskOutputDatabaseLevel is now required
  - Parameter result_type of model MigrateSchemaSqlTaskOutputError is now required

## 9.0.0 (2021-04-07)

**Features**

  - Model AvailableServiceSku has a new parameter sku

**Breaking changes**

  - Operation ServiceTasksOperations.update has a new signature
  - Operation TasksOperations.create_or_update has a new signature
  - Operation TasksOperations.update has a new signature
  - Operation FilesOperations.create_or_update has a new signature
  - Operation FilesOperations.update has a new signature
  - Operation TasksOperations.update has a new signature
  - Operation TasksOperations.create_or_update has a new signature
  - Operation ServiceTasksOperations.update has a new signature
  - Operation FilesOperations.update has a new signature
  - Operation FilesOperations.create_or_update has a new signature
  - Operation ServicesOperations.check_children_name_availability has a new signature
  - Operation ServicesOperations.check_name_availability has a new signature
  - Operation ServiceTasksOperations.create_or_update has a new signature
  - Model AvailableServiceSku no longer has parameter available_service_sku

## 9.0.0b1 (2020-12-21)

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

## 4.0.0 (2019-10-24)

**Features**

  - Model MigrationEligibilityInfo has a new parameter
    is_eligible_for_migration
  - Model ConnectToTargetSqlMITaskInput has a new parameter
    validate_ssis_catalog_only
  - Model ConnectToTargetSqlMITaskInput has a new parameter
    collect_logins
  - Model ConnectToTargetSqlMITaskInput has a new parameter
    collect_agent_jobs
  - Model ConnectToSourceSqlServerTaskInput has a new parameter
    collect_databases
  - Model ConnectToSourceSqlServerTaskInput has a new parameter
    validate_ssis_catalog_only
  - Model MigrateSqlServerSqlMITaskInput has a new parameter
    aad_domain_name
  - Model MigrateOracleAzureDbPostgreSqlSyncDatabaseInput has a new
    parameter case_manipulation

**Breaking changes**

  - Model MigrationEligibilityInfo no longer has parameter
    is_eligibile_for_migration

## 3.0.0 (2019-07-12)

**Features**

  - Added operation group ServiceTasksOperations

**General Breaking changes**

This version uses a next-generation code generator that might introduce
breaking changes if from some import. In summary, some modules were
incorrectly visible/importable and have been renamed. This fixed several
issues caused by usage of classes that were not supposed to be used in
the first place. DataMigrationServiceManagementClient cannot be imported
from azure.mgmt.datamigration.data_migration_service_client anymore
(import from azure.mgmt.datamigration works like before)
DataMigrationServiceManagementClientConfiguration import has been moved
from
azure.mgmt.datamigration.data_migration_service_management_client to
azure.mgmt.datamigration A model MyClass from a "models" sub-module
cannot be imported anymore using
azure.mgmt.datamigration.models.my_class (import from
azure.mgmt.datamigration.models works like before) An operation class
MyClassOperations from an operations sub-module cannot be imported
anymore using azure.mgmt.datamigration.operations.my_class_operations
(import from azure.mgmt.datamigration.operations works like before) Last
but not least, HTTP connection pooling is now enabled by default. You
should always use a client as a context manager, or call close(), or use
no more than one client per process.

## 2.2.0 (2019-05-21)

**Features**

  - Model ValidateMigrationInputSqlServerSqlDbSyncTaskProperties has a
    new parameter client_data
  - Model ValidateMongoDbTaskProperties has a new parameter client_data
  - Model MigrateMySqlAzureDbForMySqlSyncTaskProperties has a new
    parameter client_data
  - Model MigrateSqlServerSqlDbTaskProperties has a new parameter
    client_data
  - Model ConnectToSourceMySqlTaskProperties has a new parameter
    client_data
  - Model MigrateMongoDbTaskProperties has a new parameter client_data
  - Model MigrateMySqlAzureDbForMySqlSyncDatabaseInput has a new
    parameter target_setting
  - Model MigrateMySqlAzureDbForMySqlSyncDatabaseInput has a new
    parameter source_setting
  - Model MigrateMySqlAzureDbForMySqlSyncDatabaseInput has a new
    parameter migration_setting
  - Model MigrateSqlServerSqlMITaskProperties has a new parameter
    client_data
  - Model MigrateSqlServerSqlDbSyncTaskProperties has a new parameter
    client_data
  - Model ValidateMigrationInputSqlServerSqlMITaskProperties has a new
    parameter client_data
  - Model ConnectToTargetSqlMITaskProperties has a new parameter
    client_data
  - Model MigrateSqlServerSqlMITaskOutputMigrationLevel has a new
    parameter orphaned_users_info
  - Model GetTdeCertificatesSqlTaskProperties has a new parameter
    client_data
  - Model ConnectToSourceSqlServerSyncTaskProperties has a new parameter
    client_data
  - Model MigratePostgreSqlAzureDbForPostgreSqlSyncTaskProperties has a
    new parameter client_data
  - Model ConnectToSourceSqlServerTaskProperties has a new parameter
    client_data
  - Model ConnectToTargetAzureDbForMySqlTaskProperties has a new
    parameter client_data
  - Model GetUserTablesSqlTaskProperties has a new parameter
    client_data
  - Model ProjectTaskProperties has a new parameter client_data
  - Model MigratePostgreSqlAzureDbForPostgreSqlSyncDatabaseInput has a
    new parameter target_setting
  - Model MigratePostgreSqlAzureDbForPostgreSqlSyncDatabaseInput has a
    new parameter source_setting
  - Model MigratePostgreSqlAzureDbForPostgreSqlSyncDatabaseInput has a
    new parameter migration_setting
  - Model GetUserTablesSqlSyncTaskProperties has a new parameter
    client_data
  - Model MigrateSchemaSqlServerSqlDbTaskProperties has a new parameter
    client_data
  - Model ConnectToTargetSqlDbTaskProperties has a new parameter
    client_data
  - Model MigrateSyncCompleteCommandOutput has a new parameter id
  - Model ConnectToMongoDbTaskProperties has a new parameter
    client_data
  - Model ConnectToTargetSqlSqlDbSyncTaskProperties has a new parameter
    client_data
  - Model MigrateSqlServerSqlMITaskOutputMigrationLevel no longer has
    parameter orphaned_users

## 2.1.0 (2018-11-05)

**Features**

  - Model MigrateSchemaSqlServerSqlDbDatabaseInput has a new parameter
    name
  - Added operation group FilesOperations
  - Add MongoDB support

## 2.0.0 (2018-09-07)

**Features**

  - Model ConnectToSourceSqlServerTaskInput has a new parameter
    collect_tde_certificate_info
  - Model ConnectToTargetSqlDbTaskProperties has a new parameter
    commands
  - Model ConnectToSourceSqlServerTaskProperties has a new parameter
    commands
  - Model MigrateSqlServerSqlDbTaskProperties has a new parameter
    commands
  - Model ConnectToSourceSqlServerTaskOutputTaskLevel has a new
    parameter database_tde_certificate_mapping
  - Model ProjectTaskProperties has a new parameter commands
  - Model ConnectToSourceSqlServerTaskOutputAgentJobLevel has a new
    parameter validation_errors
  - Model SqlConnectionInfo has a new parameter platform
  - Model GetUserTablesSqlTaskProperties has a new parameter commands
  - Model MigrateSqlServerSqlDbTaskOutputMigrationLevel has a new
    parameter migration_validation_result
  - Model MigrateSqlServerSqlDbTaskOutputMigrationLevel has a new
    parameter migration_report_result
  - Model MigrateSqlServerSqlServerDatabaseInput has a new parameter
    backup_and_restore_folder
  - Added operation
    ServicesOperations.check_children_name_availability
  - Added operation TasksOperations.command
  - Added operation ProjectsOperations.list

**Breaking changes**

  - Model MigrateSqlServerSqlDbTaskOutputMigrationLevel no longer has
    parameter migration_report
  - Model MigrateSqlServerSqlServerDatabaseInput no longer has parameter
    backup_file_share
  - Model ReportableException has a new signature
  - Removed operation
    ServicesOperations.nested_check_name_availability
  - Removed operation ProjectsOperations.list_by_resource_group

## 1.0.0 (2018-06-05)

  - Initial stable release

## 0.1.0 (2018-04-20)

  - Initial Release
