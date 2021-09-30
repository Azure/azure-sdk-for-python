# Release History

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
