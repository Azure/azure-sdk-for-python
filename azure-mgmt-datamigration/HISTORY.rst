.. :changelog:

Release History
===============

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
