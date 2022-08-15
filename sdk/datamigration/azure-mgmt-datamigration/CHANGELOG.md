# Release History

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
