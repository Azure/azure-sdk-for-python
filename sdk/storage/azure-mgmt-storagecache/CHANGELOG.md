# Release History

## 4.0.0 (2026-07-08)

### Features Added

  - Client `StorageCacheManagementClient` added method `send_request`
  - Client `StorageCacheManagementClient` added operation group `expansion_jobs`
  - Enum `AmlFilesystemHealthStateType` added member `EXPANDING`
  - Added model `AutoExportJobPropertiesStatus`
  - Added model `AutoImportJobPropertiesStatus`
  - Added model `CloudError`
  - Added model `ExpansionJob`
  - Added model `ExpansionJobProperties`
  - Added enum `ExpansionJobPropertiesProvisioningState`
  - Added model `ExpansionJobPropertiesStatus`
  - Added enum `ExpansionJobStatusType`
  - Added model `ExpansionJobUpdate`
  - Added model `ImportJobPropertiesStatus`
  - Added model `ProxyResource`
  - Added operation group `ExpansionJobsOperations`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. Please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - For the method breakings, please refer to https://aka.ms/azsdk/python/migrate/operations for migration.
  - Model `AmlFilesystem` moved instance variable `storage_capacity_ti_b`, `health`, `provisioning_state`, `filesystem_subnet`, `client_info`, `throughput_provisioned_m_bps`, `encryption_settings`, `maintenance_window`, `hsm` and `root_squash_settings` under property `properties` whose type is `AmlFilesystemProperties`
  - Model `AmlFilesystemUpdate` moved instance variable `encryption_settings`, `maintenance_window` and `root_squash_settings` under property `properties` whose type is `AmlFilesystemUpdateProperties`
  - Model `ApiOperation` moved instance variable `service_specification` under property `properties` whose type is `ApiOperationProperties`
  - Model `AscOperation` moved instance variable `output` under property `properties` whose type is `AscOperationProperties`
  - Model `AutoExportJob` moved instance variable `provisioning_state`, `admin_status`, `auto_export_prefixes`, `state`, `status_code`, `status_message`, `total_files_exported`, `total_mi_b_exported`, `total_files_failed`, `export_iteration_count`, `last_successful_iteration_completion_time_utc`, `current_iteration_files_discovered`, `current_iteration_mi_b_discovered`, `current_iteration_files_exported`, `current_iteration_mi_b_exported`, `current_iteration_files_failed`, `last_started_time_utc` and `last_completion_time_utc` under property `properties` whose type is `AutoExportJobProperties`
  - Model `AutoExportJobUpdate` moved instance variable `admin_status` under property `properties` whose type is `AutoExportJobUpdateProperties`
  - Model `AutoImportJob` moved instance variable `provisioning_state`, `admin_status`, `auto_import_prefixes`, `conflict_resolution_mode`, `enable_deletions`, `maximum_errors`, `state`, `status_code`, `status_message`, `scan_start_time`, `scan_end_time`, `total_blobs_walked`, `rate_of_blob_walk`, `total_blobs_imported`, `rate_of_blob_import`, `imported_files`, `imported_directories`, `imported_symlinks`, `preexisting_files`, `preexisting_directories`, `preexisting_symlinks`, `total_errors`, `total_conflicts`, `blob_sync_events`, `last_started_time_utc` and `last_completion_time_utc` under property `properties` whose type is `AutoImportJobProperties`
  - Model `AutoImportJobUpdate` moved instance variable `admin_status` under property `properties` whose type is `AutoImportJobUpdateProperties`
  - Model `Cache` moved instance variable `cache_size_gb`, `health`, `mount_addresses`, `provisioning_state`, `subnet`, `upgrade_status`, `upgrade_settings`, `network_settings`, `encryption_settings`, `security_settings`, `directory_services_settings`, `zones`, `priming_jobs` and `space_allocation` under property `properties` whose type is `CacheProperties`
  - Model `ImportJob` moved instance variable `provisioning_state`, `admin_status`, `import_prefixes`, `conflict_resolution_mode`, `maximum_errors`, `state`, `status_message`, `total_blobs_walked`, `blobs_walked_per_second`, `total_blobs_imported`, `imported_files`, `imported_directories`, `imported_symlinks`, `preexisting_files`, `preexisting_directories`, `preexisting_symlinks`, `blobs_imported_per_second`, `last_completion_time`, `last_started_time`, `total_errors` and `total_conflicts` under property `properties` whose type is `ImportJobProperties`
  - Model `ImportJobUpdate` moved instance variable `admin_status` under property `properties` whose type is `ImportJobUpdateProperties`
  - Model `Restriction` renamed its instance variable `values` to `values_property`
  - Model `StorageTarget` moved instance variable `junctions`, `target_type`, `provisioning_state`, `state`, `nfs3`, `clfs`, `unknown`, `blob_nfs` and `allocation_percentage` under property `properties` whose type is `StorageTargetProperties`
  - Method `StorageTargetsOperations.begin_delete` changed its parameter `force` from `positional_or_keyword` to `keyword_only`

### Other Changes

  - Deleted model `AmlFilesystemsListResult`/`ApiOperationListResult`/`AutoExportJobsListResult`/`AutoImportJobsListResult`/`CachesListResult`/`ImportJobsListResult`/`ResourceSkusResult`/`ResourceUsagesListResult`/`StorageTargetsResult`/`UsageModelsResult` which actually were not used by SDK users
  - Deleted model `StorageTargetResource`/`UserAssignedIdentitiesValueAutoGenerated` which actually were not used by SDK users

## 4.0.0b1 (2026-05-27)

### Features Added

  - Client `StorageCacheManagementClient` added method `send_request`
  - Client `StorageCacheManagementClient` added operation group `expansion_jobs`
  - Enum `AmlFilesystemHealthStateType` added member `EXPANDING`
  - Added model `AutoExportJobPropertiesStatus`
  - Added model `AutoImportJobPropertiesStatus`
  - Added model `CloudError`
  - Added model `ExpansionJob`
  - Added model `ExpansionJobProperties`
  - Added enum `ExpansionJobPropertiesProvisioningState`
  - Added model `ExpansionJobPropertiesStatus`
  - Added enum `ExpansionJobStatusType`
  - Added model `ExpansionJobUpdate`
  - Added model `ImportJobPropertiesStatus`
  - Added model `ProxyResource`
  - Added operation group `ExpansionJobsOperations`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. Please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - For the method breakings, please refer to https://aka.ms/azsdk/python/migrate/operations for migration.
  - Model `Restriction` renamed its instance variable `values` to `values_property`
  - Method `StorageTargetsOperations.begin_delete` changed its parameter `force` from `positional_or_keyword` to `keyword_only`

### Other Changes

  - Deleted model `ResourceSkusResult`/`StorageTargetsResult`/`UsageModelsResult`/`UserAssignedIdentitiesValueAutoGenerated`/`StorageTargetResource` which actually were not used by SDK users

## 3.0.1 (2025-10-09)

### Bugs Fixed

- Exclude `generated_samples` and `generated_tests` from wheel

## 3.0.0 (2025-09-25)

### Features Added

  - Model `StorageCacheManagementClient` added parameter `cloud_setting` in method `__init__`
  - Client `StorageCacheManagementClient` added operation group `auto_export_jobs`
  - Client `StorageCacheManagementClient` added operation group `auto_import_jobs`
  - Model `ImportJob` added property `admin_status`
  - Model `ImportJob` added property `imported_files`
  - Model `ImportJob` added property `imported_directories`
  - Model `ImportJob` added property `imported_symlinks`
  - Model `ImportJob` added property `preexisting_files`
  - Model `ImportJob` added property `preexisting_directories`
  - Model `ImportJob` added property `preexisting_symlinks`
  - Model `ImportJobUpdate` added property `admin_status`
  - Added model `AutoExportJob`
  - Added enum `AutoExportJobAdminStatus`
  - Added enum `AutoExportJobProvisioningStateType`
  - Added model `AutoExportJobUpdate`
  - Added model `AutoExportJobsListResult`
  - Added enum `AutoExportStatusType`
  - Added model `AutoImportJob`
  - Added enum `AutoImportJobPropertiesAdminStatus`
  - Added enum `AutoImportJobPropertiesProvisioningState`
  - Added model `AutoImportJobPropertiesStatusBlobSyncEvents`
  - Added enum `AutoImportJobState`
  - Added model `AutoImportJobUpdate`
  - Added enum `AutoImportJobUpdatePropertiesAdminStatus`
  - Added model `AutoImportJobsListResult`
  - Added enum `ImportJobAdminStatus`
  - Added operation group `AutoExportJobsOperations`
  - Added operation group `AutoImportJobsOperations`

### Breaking Changes

  - Parameter `conflict_resolution_mode` of method `ImportJob.__init__` is now optional
  - Deleted or renamed operation group `StorageCacheManagementClientOperationsMixin`

## 2.0.0 (2024-05-20)

### Features Added

  - Added operation group ImportJobsOperations
  - Model AmlFilesystem has a new parameter root_squash_settings
  - Model AmlFilesystemHsmSettings has a new parameter import_prefixes_initial
  - Model AmlFilesystemUpdate has a new parameter root_squash_settings
  - Model ErrorResponse has a new parameter error
  - Model AscOperation.error changes type from ErrorResponse to AscOperationErrorResponse

### Breaking Changes

  - Model ErrorResponse no longer has parameter code
  - Model ErrorResponse no longer has parameter message

## 1.6.0b1 (2024-02-22)

### Features Added

  - Model AmlFilesystem has a new parameter root_squash_settings
  - Model AmlFilesystemUpdate has a new parameter root_squash_settings

## 1.5.0 (2023-06-16)

### Features Added

  - Added operation group AmlFilesystemsOperations
  - Added operation group StorageCacheManagementClientOperationsMixin

## 1.4.0 (2023-02-15)

### Features Added

  - Added operation StorageTargetsOperations.begin_restore_defaults
  - Model BlobNfsTarget has a new parameter verification_timer
  - Model BlobNfsTarget has a new parameter write_back_timer
  - Model Nfs3Target has a new parameter verification_timer
  - Model Nfs3Target has a new parameter write_back_timer

### Breaking Changes

  - Renamed operation CachesOperations.update to CachesOperations.begin_update

## 1.4.0b1 (2022-12-12)

### Other Changes

  - Added generated samples in github repo
  - Drop support for python<3.7.0

## 1.3.0 (2022-07-07)

**Features**

  - Added operation CachesOperations.begin_pause_priming_job
  - Added operation CachesOperations.begin_resume_priming_job
  - Added operation CachesOperations.begin_space_allocation
  - Added operation CachesOperations.begin_start_priming_job
  - Added operation CachesOperations.begin_stop_priming_job
  - Model ApiOperationPropertiesServiceSpecification has a new parameter log_specifications
  - Model Cache has a new parameter priming_jobs
  - Model Cache has a new parameter space_allocation
  - Model Cache has a new parameter upgrade_settings
  - Model StorageTarget has a new parameter allocation_percentage

## 1.2.0 (2022-03-22)

**Features**

  - Added operation StorageTargetOperations.begin_invalidate
  - Added operation group AscUsagesOperations
  - Model Cache has a new parameter zones

## 1.1.0 (2021-09-30)

**Features**

  - Model StorageTarget has a new parameter state

## 1.0.0 (2021-07-29)

**Features**

  - Model CacheEncryptionSettings has a new parameter rotation_to_latest_key_version_enabled
  - Model CacheIdentity has a new parameter user_assigned_identities
  - Added operation group StorageTargetOperations

**Breaking changes**

  - Operation StorageTargetsOperations.begin_delete has a new signature

## 1.0.0b1 (2021-05-13)

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

## 0.3.0 (2020-03-01)

**Features**

  - Model Cache has a new parameter security_settings
  - Model Cache has a new parameter network_settings
  - Model Cache has a new parameter identity
  - Model Cache has a new parameter encryption_settings

## 0.2.0 (2019-11-12)

**Features**

  - Added operation CachesOperations.create_or_update
  - Added operation StorageTargetsOperations.create_or_update

**Breaking changes**

  - Removed operation CachesOperations.create
  - Removed operation StorageTargetsOperations.create
  - Removed operation StorageTargetsOperations.update

## 0.1.0rc1 (2019-09-03)

  - Initial Release
