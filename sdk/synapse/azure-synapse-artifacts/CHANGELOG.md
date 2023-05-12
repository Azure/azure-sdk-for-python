# Release History

## 0.16.1 (Unreleased)

### Features Added

### Breaking Changes

### Bugs Fixed

### Other Changes

## 0.16.0 (2023-05-12)

### Bugs Fixed

  - Fix to support IO input  #29615

## 0.15.0 (2023-01-09)

### Features Added

  - Model AzureSynapseArtifactsLinkedService has a new parameter workspace_resource_id
  - Model RestServiceLinkedService has a new parameter auth_headers
  - Model SynapseSparkJobDefinitionActivity has a new parameter configuration_type
  - Model SynapseSparkJobDefinitionActivity has a new parameter files_v2
  - Model SynapseSparkJobDefinitionActivity has a new parameter python_code_reference
  - Model SynapseSparkJobDefinitionActivity has a new parameter scan_folder
  - Model SynapseSparkJobDefinitionActivity has a new parameter spark_config
  - Model SynapseSparkJobDefinitionActivity has a new parameter target_spark_configuration 

### Breaking Changes

  - Parameter export_settings of model SnowflakeSource is now required
  - Renamed operation LinkConnectionOperations.create_or_update_link_connection to LinkConnectionOperations.create_or_update
  - Renamed operation LinkConnectionOperations.delete_link_connection to LinkConnectionOperations.delete
  - Renamed operation LinkConnectionOperations.get_link_connection to LinkConnectionOperations.get
  - Renamed operation LinkConnectionOperations.list_link_connections_by_workspace to LinkConnectionOperations.list_by_workspace

## 0.14.0 (2022-09-19)

### Features Added

  - Upgraded api-version for some operation group

### Other Changes
  
  - Drop support for python3.6

## 0.13.0 (2022-04-21)

### Features

  - Added operation group LinkConnectionOperations

## 0.12.0 (2022-03-07)

### Features Added

- re-generated based on tag package-artifacts-composite-v3

## 0.11.0 (2022-01-11)

### Features Added

- Added `MetastoreOperations`

### Other Changes

- Python 2.7 and 3.6 are no longer supported. Please use Python version 3.7 or later.

## 0.10.0 (2021-11-09)

### Other Changes

- Internal bugfixes (re-generated with latest generator)

## 0.9.0 (2021-10-05)

### Features Added

- re-generated based on tag package-artifacts-composite-v1

## 0.8.0 (2021-08-10)

- Updated API version to "2020-12-01" which is the default API version
- Added `NotebookOperationResultOperations`, `OperationResultOperations`, `OperationStatusOperations`
- Added API version "2021-06-01-preview" support

## 0.7.0 (2021-05-11)

### Bug fixes

- Enable poller when starting a long running operation    #18184

## 0.6.0 (2021-04-06)

### New Features

- Add ADF support

## 0.5.0 (2021-03-09)

### New Features

- Add library operations
- Change create_or_update_sql_script, delete_sql_script, rename_sql_script to long running operations

### Breaking changes

- Stop Python 3.5 support

## 0.4.0 (2020-12-08)

### New Features

- Add Workspace git repo management operations
- Add rename method for data flow, dataset, linked service, notebook, pipeline, spark job definition, sql script operations

## 0.3.0 (2020-09-15)

### New Features

- Add Workspace operations
- Add SqlPools operations
- Add BigDataPools operations
- Add IntegrationRuntimes operations

### Breaking changes

- Migrated most long running operation to polling mechanism (operation now starts with `begin`)

## 0.2.0 (2020-07-01)

* Initial Release
