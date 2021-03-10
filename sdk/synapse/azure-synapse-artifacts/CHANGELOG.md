# Release History

## 0.5.0 (2021-03-09)

** Features **

- Add library operations
- Change create_or_update_sql_script, delete_sql_script, rename_sql_script to long running operations

** Breaking changes **

- Stop Python 3.5 support

## 0.4.0 (2020-12-08)

** Features **

- Add Workspace git repo management operations
- Add rename method for data flow, dataset, linked service, notebook, pipeline, spark job definition, sql script operations

## 0.3.0 (2020-09-15)

** Features **

- Add Workspace operations
- Add SqlPools operations
- Add BigDataPools operations
- Add IntegrationRuntimes operations

** Breaking changes **

- Migrated most long running operation to polling mechanism (operation now starts with `begin`)

## 0.2.0 (2020-07-01)

* Initial Release
