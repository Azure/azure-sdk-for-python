.. :changelog:

Release History
===============

2.2.0 (2019-05-21)
++++++++++++++++++

**Features**

- Model ValidateMigrationInputSqlServerSqlDbSyncTaskProperties has a new parameter client_data
- Model ValidateMongoDbTaskProperties has a new parameter client_data
- Model MigrateMySqlAzureDbForMySqlSyncTaskProperties has a new parameter client_data
- Model MigrateSqlServerSqlDbTaskProperties has a new parameter client_data
- Model ConnectToSourceMySqlTaskProperties has a new parameter client_data
- Model MigrateMongoDbTaskProperties has a new parameter client_data
- Model MigrateMySqlAzureDbForMySqlSyncDatabaseInput has a new parameter target_setting
- Model MigrateMySqlAzureDbForMySqlSyncDatabaseInput has a new parameter source_setting
- Model MigrateMySqlAzureDbForMySqlSyncDatabaseInput has a new parameter migration_setting
- Model MigrateSqlServerSqlMITaskProperties has a new parameter client_data
- Model MigrateSqlServerSqlDbSyncTaskProperties has a new parameter client_data
- Model ValidateMigrationInputSqlServerSqlMITaskProperties has a new parameter client_data
- Model ConnectToTargetSqlMITaskProperties has a new parameter client_data
- Model MigrateSqlServerSqlMITaskOutputMigrationLevel has a new parameter orphaned_users_info
- Model GetTdeCertificatesSqlTaskProperties has a new parameter client_data
- Model ConnectToSourceSqlServerSyncTaskProperties has a new parameter client_data
- Model MigratePostgreSqlAzureDbForPostgreSqlSyncTaskProperties has a new parameter client_data
- Model ConnectToSourceSqlServerTaskProperties has a new parameter client_data
- Model ConnectToTargetAzureDbForMySqlTaskProperties has a new parameter client_data
- Model GetUserTablesSqlTaskProperties has a new parameter client_data
- Model ProjectTaskProperties has a new parameter client_data
- Model MigratePostgreSqlAzureDbForPostgreSqlSyncDatabaseInput has a new parameter target_setting
- Model MigratePostgreSqlAzureDbForPostgreSqlSyncDatabaseInput has a new parameter source_setting
- Model MigratePostgreSqlAzureDbForPostgreSqlSyncDatabaseInput has a new parameter migration_setting
- Model GetUserTablesSqlSyncTaskProperties has a new parameter client_data
- Model MigrateSchemaSqlServerSqlDbTaskProperties has a new parameter client_data
- Model ConnectToTargetSqlDbTaskProperties has a new parameter client_data
- Model MigrateSyncCompleteCommandOutput has a new parameter id
- Model ConnectToMongoDbTaskProperties has a new parameter client_data
- Model ConnectToTargetSqlSqlDbSyncTaskProperties has a new parameter client_data
- Model MigrateSqlServerSqlMITaskOutputMigrationLevel no longer has parameter orphaned_users

2.1.0 (2018-11-05)
++++++++++++++++++

**Features**

- Model MigrateSchemaSqlServerSqlDbDatabaseInput has a new parameter name
- Added operation group FilesOperations
- Add MongoDB support

2.0.0 (2018-09-07)
++++++++++++++++++

**Features**

- Model ConnectToSourceSqlServerTaskInput has a new parameter collect_tde_certificate_info
- Model ConnectToTargetSqlDbTaskProperties has a new parameter commands
- Model ConnectToSourceSqlServerTaskProperties has a new parameter commands
- Model MigrateSqlServerSqlDbTaskProperties has a new parameter commands
- Model ConnectToSourceSqlServerTaskOutputTaskLevel has a new parameter database_tde_certificate_mapping
- Model ProjectTaskProperties has a new parameter commands
- Model ConnectToSourceSqlServerTaskOutputAgentJobLevel has a new parameter validation_errors
- Model SqlConnectionInfo has a new parameter platform
- Model GetUserTablesSqlTaskProperties has a new parameter commands
- Model MigrateSqlServerSqlDbTaskOutputMigrationLevel has a new parameter migration_validation_result
- Model MigrateSqlServerSqlDbTaskOutputMigrationLevel has a new parameter migration_report_result
- Model MigrateSqlServerSqlServerDatabaseInput has a new parameter backup_and_restore_folder
- Added operation ServicesOperations.check_children_name_availability
- Added operation TasksOperations.command
- Added operation ProjectsOperations.list

**Breaking changes**

- Model MigrateSqlServerSqlDbTaskOutputMigrationLevel no longer has parameter migration_report
- Model MigrateSqlServerSqlServerDatabaseInput no longer has parameter backup_file_share
- Model ReportableException has a new signature
- Removed operation ServicesOperations.nested_check_name_availability
- Removed operation ProjectsOperations.list_by_resource_group

1.0.0 (2018-06-05)
++++++++++++++++++

* Initial stable release

0.1.0 (2018-04-20)
++++++++++++++++++

* Initial Release
