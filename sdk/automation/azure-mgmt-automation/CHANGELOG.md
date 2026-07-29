# Release History

## 2.0.0 (2026-07-29)

### Features Added

  - Client `AutomationClient` added parameter `api_version` in method `__init__`
  - Client `AutomationClient` added method `convert_graph_runbook_content`
  - Client `AutomationClient` added method `send_request`
  - Client `AutomationClient` added operation group `deleted_automation_accounts`
  - Client `AutomationClient` added operation group `hybrid_runbook_workers`
  - Client `AutomationClient` added operation group `package`
  - Client `AutomationClient` added operation group `private_endpoint_connections`
  - Client `AutomationClient` added operation group `private_link_resources`
  - Client `AutomationClient` added operation group `python3_package`
  - Client `AutomationClient` added operation group `runtime_environments`
  - Model `AutomationAccount` added property `identity`
  - Model `AutomationAccount` added property `system_data`
  - Model `AutomationAccountCreateOrUpdateParameters` added property `identity`
  - Model `AutomationAccountUpdateParameters` added property `identity`
  - Model `Certificate` added property `system_data`
  - Model `Connection` added property `system_data`
  - Model `ConnectionType` added property `system_data`
  - Model `Credential` added property `system_data`
  - Model `DscConfiguration` added property `system_data`
  - Model `DscNode` added property `system_data`
  - Model `DscNodeConfiguration` added property `system_data`
  - Model `HybridRunbookWorker` added property `id`
  - Model `HybridRunbookWorker` added property `location`
  - Model `HybridRunbookWorker` added property `system_data`
  - Model `HybridRunbookWorker` added property `tags`
  - Model `HybridRunbookWorker` added property `type`
  - Model `HybridRunbookWorkerGroup` added property `location`
  - Model `HybridRunbookWorkerGroup` added property `system_data`
  - Model `HybridRunbookWorkerGroup` added property `tags`
  - Model `HybridRunbookWorkerGroup` added property `type`
  - Model `Job` added property `system_data`
  - Model `JobCollectionItem` added property `system_data`
  - Model `JobSchedule` added property `system_data`
  - Model `Module` added property `system_data`
  - Model `Operation` added property `origin`
  - Model `Operation` added property `properties`
  - Model `OperationDisplay` added property `description`
  - Model `ProxyResource` added property `system_data`
  - Model `Resource` added property `system_data`
  - Model `Runbook` added property `system_data`
  - Enum `RunbookTypeEnum` added member `POWER_SHELL72`
  - Enum `RunbookTypeEnum` added member `PYTHON`
  - Model `Schedule` added property `system_data`
  - Model `SoftwareUpdateConfiguration` added property `system_data`
  - Model `SourceControl` added property `system_data`
  - Model `TestJobCreateParameters` added property `runtime_environment`
  - Model `TrackedResource` added property `system_data`
  - Model `Variable` added property `system_data`
  - Model `Watcher` added property `system_data`
  - Model `Webhook` added property `system_data`
  - Added model `AutomationErrorResponse`
  - Added enum `CreatedByType`
  - Added model `DeletedAutomationAccount`
  - Added model `DeletedAutomationAccountListResult`
  - Added model `DeletedAutomationAccountProperties`
  - Added model `DeletedRunbook`
  - Added model `DeletedRunbookProperties`
  - Added model `Dimension`
  - Added enum `EncryptionKeySourceType`
  - Added model `EncryptionProperties`
  - Added model `EncryptionPropertiesIdentity`
  - Added model `ErrorAdditionalInfo`
  - Added enum `GraphRunbookType`
  - Added model `GraphicalRunbookContent`
  - Added model `HybridRunbookWorkerCreateOrUpdateParameters`
  - Added model `HybridRunbookWorkerCreateParameters`
  - Added model `HybridRunbookWorkerGroupCreateOrUpdateParameters`
  - Added model `HybridRunbookWorkerGroupCreateOrUpdateProperties`
  - Added model `HybridRunbookWorkerMoveParameters`
  - Added model `Identity`
  - Added model `JobRuntimeEnvironment`
  - Added model `KeyVaultProperties`
  - Added model `LogSpecification`
  - Added model `MetricSpecification`
  - Added model `OperationPropertiesFormat`
  - Added model `OperationPropertiesFormatServiceSpecification`
  - Added model `Package`
  - Added model `PackageCreateOrUpdateParameters`
  - Added model `PackageCreateOrUpdateProperties`
  - Added model `PackageErrorInfo`
  - Added model `PackageProperties`
  - Added enum `PackageProvisioningState`
  - Added model `PackageUpdateParameters`
  - Added model `PackageUpdateProperties`
  - Added model `PrivateEndpointConnection`
  - Added model `PrivateEndpointConnectionProperties`
  - Added model `PrivateEndpointProperty`
  - Added model `PrivateLinkResource`
  - Added model `PrivateLinkResourceProperties`
  - Added model `PrivateLinkServiceConnectionStateProperty`
  - Added model `RawGraphicalRunbookContent`
  - Added enum `ResourceIdentityType`
  - Added model `RuntimeEnvironment`
  - Added model `RuntimeEnvironmentProperties`
  - Added model `RuntimeEnvironmentUpdateParameters`
  - Added model `RuntimeEnvironmentUpdateProperties`
  - Added model `RuntimeProperties`
  - Added model `SUCScheduleProperties`
  - Added model `SoftwareUpdateConfigurationRunTaskProperties`
  - Added model `SoftwareUpdateConfigurationRunTasks`
  - Added model `SystemData`
  - Added model `UserAssignedIdentitiesProperties`
  - Added enum `WorkerType`
  - Operation group `AutomationAccountOperations` added method `list_deleted_runbooks`
  - Operation group `HybridRunbookWorkerGroupOperations` added method `create`
  - Added operation group `DeletedAutomationAccountsOperations`
  - Added operation group `HybridRunbookWorkersOperations`
  - Added operation group `PackageOperations`
  - Added operation group `PrivateEndpointConnectionsOperations`
  - Added operation group `PrivateLinkResourcesOperations`
  - Added operation group `Python3PackageOperations`
  - Added operation group `RuntimeEnvironmentsOperations`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. Please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - For the method breakings, please refer to https://aka.ms/azsdk/python/migrate/operations for migration.
  - Deleted operation group `AutomationClient.dsc_compilation_job`/`AutomationClient.dsc_compilation_job_stream` and their corresponding operation groups `DscCompilationJobOperations`/`DscCompilationJobStreamOperations`; corresponding models `DscCompilationJob`/`DscCompilationJobCreateParameters` were also deleted
  - Model `Activity` moved instance variable `creation_time`, `definition`, `description`, `last_modified_time`, `output_types` and `parameter_sets` under property `properties` whose type is `ActivityProperties`
  - Model `AgentRegistration` renamed its instance variable `keys` to `keys_property`
  - Model `AutomationAccount` moved instance variable `creation_time`, `description`, `last_modified_by`, `last_modified_time`, `sku` and `state` under property `properties` whose type is `AutomationAccountProperties`
  - Model `AutomationAccountCreateOrUpdateParameters` moved instance variable `sku` under property `properties` whose type is `AutomationAccountCreateOrUpdateProperties`
  - Model `AutomationAccountUpdateParameters` moved instance variable `sku` under property `properties` whose type is `AutomationAccountUpdateProperties`
  - Model `Certificate` moved instance variable `creation_time`, `description`, `expiry_time`, `is_exportable`, `last_modified_time` and `thumbprint` under property `properties` whose type is `CertificateProperties`
  - Model `CertificateCreateOrUpdateParameters` moved instance variable `base64_value`, `description`, `is_exportable` and `thumbprint` under property `properties` whose type is `CertificateCreateOrUpdateProperties`
  - Model `CertificateUpdateParameters` moved instance variable `description` under property `properties` whose type is `CertificateUpdateProperties`
  - Model `Connection` moved instance variable `connection_type`, `creation_time`, `description`, `field_definition_values` and `last_modified_time` under property `properties` whose type is `ConnectionProperties`
  - Model `ConnectionCreateOrUpdateParameters` moved instance variable `connection_type`, `description` and `field_definition_values` under property `properties` whose type is `ConnectionCreateOrUpdateProperties`
  - Model `ConnectionType` moved instance variable `creation_time`, `description`, `field_definitions`, `is_global` and `last_modified_time` under property `properties` whose type is `ConnectionTypeProperties`
  - Model `ConnectionTypeCreateOrUpdateParameters` moved instance variable `field_definitions` and `is_global` under property `properties` whose type is `ConnectionTypeCreateOrUpdateProperties`
  - Model `ConnectionUpdateParameters` moved instance variable `description` and `field_definition_values` under property `properties` whose type is `ConnectionUpdateProperties`
  - Model `Credential` moved instance variable `creation_time`, `description`, `last_modified_time` and `user_name` under property `properties` whose type is `CredentialProperties`
  - Model `CredentialCreateOrUpdateParameters` moved instance variable `description`, `password` and `user_name` under property `properties` whose type is `CredentialCreateOrUpdateProperties`
  - Model `CredentialUpdateParameters` moved instance variable `description`, `password` and `user_name` under property `properties` whose type is `CredentialUpdateProperties`
  - Model `DscConfiguration` moved instance variable `creation_time`, `description`, `job_count`, `last_modified_time`, `log_verbose`, `node_configuration_count`, `parameters`, `provisioning_state`, `source` and `state` under property `properties` whose type is `DscConfigurationProperties`
  - Model `DscConfigurationCreateOrUpdateParameters` moved instance variable `description`, `log_progress`, `log_verbose`, `parameters` and `source` under property `properties` whose type is `DscConfigurationCreateOrUpdateProperties`
  - Model `DscConfigurationUpdateParameters` moved instance variable `description`, `log_progress`, `log_verbose`, `parameters` and `source` under property `properties` whose type is `DscConfigurationCreateOrUpdateProperties`
  - Model `DscNode` moved instance variable `account_id`, `etag`, `extension_handler`, `ip`, `last_seen`, `name_properties_node_configuration_name`, `node_id`, `registration_time`, `status` and `total_count` under property `properties` whose type is `DscNodeProperties`
  - Model `DscNodeConfiguration` moved instance variable `configuration`, `creation_time`, `increment_node_configuration_build`, `last_modified_time`, `node_count` and `source` under property `properties` whose type is `DscNodeConfigurationProperties`
  - Model `DscNodeConfigurationCreateOrUpdateParameters` moved instance variable `configuration`, `increment_node_configuration_build` and `source` under property `properties` whose type is `DscNodeConfigurationCreateOrUpdateParametersProperties`
  - Model `DscNodeUpdateParametersProperties` moved instance variable `name` under property `node_configuration` whose type is `DscNodeConfigurationAssociationProperty`
  - Model `ErrorResponse` moved instance variable `code` and `message` under property `error` whose type is `ErrorDetail`
  - Model `HybridRunbookWorker` moved instance variable `ip` and `last_seen_date_time` under property `properties` whose type is `HybridRunbookWorkerProperties`
  - Model `HybridRunbookWorker` renamed its instance variable `registration_time` to `registered_date_time` under property `properties` whose type is `HybridRunbookWorkerProperties`
  - Model `HybridRunbookWorkerGroup` moved instance variable `credential` and `group_type` under property `properties` whose type is `HybridRunbookWorkerGroupProperties`
  - Model `HybridRunbookWorkerGroup` deleted or renamed its instance variable `hybrid_runbook_workers`
  - Model `Job` moved instance variable `creation_time`, `end_time`, `exception`, `job_id`, `last_modified_time`, `last_status_modified_time`, `parameters`, `provisioning_state`, `run_on`, `runbook`, `start_time`, `started_by`, `status` and `status_details` under property `properties` whose type is `JobProperties`
  - Model `JobCollectionItem` moved instance variable `creation_time`, `end_time`, `job_id`, `last_modified_time`, `provisioning_state`, `run_on`, `runbook`, `start_time` and `status` under property `properties` whose type is `JobCollectionItemProperties`
  - Model `JobCreateParameters` moved instance variable `parameters`, `run_on` and `runbook` under property `properties` whose type is `JobCreateProperties`
  - Model `JobSchedule` moved instance variable `job_schedule_id`, `parameters`, `run_on`, `runbook` and `schedule` under property `properties` whose type is `JobScheduleProperties`
  - Model `JobScheduleCreateParameters` moved instance variable `parameters`, `run_on`, `runbook` and `schedule` under property `properties` whose type is `JobScheduleCreateProperties`
  - Model `JobStream` moved instance variable `job_stream_id`, `stream_text`, `stream_type`, `summary`, `time` and `value` under property `properties` whose type is `JobStreamProperties`
  - Model `KeyListResult` renamed its instance variable `keys` to `keys_property`
  - Model `Module` moved instance variable `activity_count`, `content_link`, `creation_time`, `description`, `error`, `is_composite`, `is_global`, `last_modified_time`, `provisioning_state`, `size_in_bytes` and `version` under property `properties` whose type is `ModuleProperties`
  - Model `ModuleCreateOrUpdateParameters` moved instance variable `content_link` under property `properties` whose type is `ModuleCreateOrUpdateProperties`
  - Renamed enum value `ModuleProvisioningState.CANCELLED` to `ModuleProvisioningState.CANCELED`
  - Model `ModuleUpdateParameters` moved instance variable `content_link` under property `properties` whose type is `ModuleUpdateProperties`
  - Model `PythonPackageCreateParameters` moved instance variable `content_link` under property `properties` whose type is `PythonPackageCreateProperties`
  - Model `Runbook` moved instance variable `creation_time`, `description`, `draft`, `job_count`, `last_modified_by`, `last_modified_time`, `log_activity_trace`, `log_progress`, `log_verbose`, `output_types`, `parameters`, `provisioning_state`, `publish_content_link`, `runbook_type` and `state` under property `properties` whose type is `RunbookProperties`
  - Model `RunbookCreateOrUpdateParameters` moved instance variable `description`, `draft`, `log_activity_trace`, `log_progress`, `log_verbose`, `publish_content_link` and `runbook_type` under property `properties` whose type is `RunbookCreateOrUpdateProperties`
  - Model `RunbookUpdateParameters` moved instance variable `description`, `log_activity_trace`, `log_progress` and `log_verbose` under property `properties` whose type is `RunbookUpdateProperties`
  - Model `Schedule` moved instance variable `advanced_schedule`, `creation_time`, `description`, `expiry_time`, `expiry_time_offset_minutes`, `frequency`, `interval`, `is_enabled`, `last_modified_time`, `next_run`, `next_run_offset_minutes`, `start_time`, `start_time_offset_minutes` and `time_zone` under property `properties` whose type is `ScheduleProperties`
  - Model `ScheduleCreateOrUpdateParameters` moved instance variable `advanced_schedule`, `description`, `expiry_time`, `frequency`, `interval`, `start_time` and `time_zone` under property `properties` whose type is `ScheduleCreateOrUpdateProperties`
  - Model `ScheduleUpdateParameters` moved instance variable `description` and `is_enabled` under property `properties` whose type is `ScheduleUpdateProperties`
  - Model `SoftwareUpdateConfiguration` moved instance variable `created_by`, `creation_time`, `error`, `last_modified_by`, `last_modified_time`, `provisioning_state`, `schedule_info`, `tasks` and `update_configuration` under property `properties` whose type is `SoftwareUpdateConfigurationProperties`
  - Model `SoftwareUpdateConfigurationCollectionItem` moved instance variable `creation_time`, `frequency`, `last_modified_time`, `next_run`, `provisioning_state`, `start_time` and `update_configuration` under property `properties` whose type is `SoftwareUpdateConfigurationCollectionItemProperties`
  - Model `SoftwareUpdateConfigurationMachineRun` moved instance variable `configured_duration`, `correlation_id`, `created_by`, `creation_time`, `end_time`, `error`, `job`, `last_modified_by`, `last_modified_time`, `os_type`, `software_update_configuration`, `source_computer_id`, `start_time`, `status`, `target_computer` and `target_computer_type` under property `properties` whose type is `UpdateConfigurationMachineRunProperties`
  - Model `SoftwareUpdateConfigurationRun` moved instance variable `computer_count`, `configured_duration`, `created_by`, `creation_time`, `end_time`, `failed_count`, `last_modified_by`, `last_modified_time`, `os_type`, `software_update_configuration`, `start_time`, `status` and `tasks` under property `properties` whose type is `SoftwareUpdateConfigurationRunProperties`
  - Model `SourceControl` moved instance variable `auto_sync`, `branch`, `creation_time`, `description`, `folder_path`, `last_modified_time`, `publish_runbook`, `repo_url` and `source_type` under property `properties` whose type is `SourceControlProperties`
  - Model `SourceControlCreateOrUpdateParameters` moved instance variable `auto_sync`, `branch`, `description`, `folder_path`, `publish_runbook`, `repo_url`, `security_token` and `source_type` under property `properties` whose type is `SourceControlCreateOrUpdateProperties`
  - Model `SourceControlSyncJob` moved instance variable `creation_time`, `end_time`, `provisioning_state`, `source_control_sync_job_id`, `start_time` and `sync_type` under property `properties` whose type is `SourceControlSyncJobProperties`
  - Model `SourceControlSyncJobById` moved instance variable `creation_time`, `end_time`, `exception`, `provisioning_state`, `source_control_sync_job_id`, `start_time` and `sync_type` under property `properties` whose type is `SourceControlSyncJobByIdProperties`
  - Model `SourceControlSyncJobCreateParameters` moved instance variable `commit_id` under property `properties` whose type is `SourceControlSyncJobCreateProperties`
  - Model `SourceControlSyncJobStream` moved instance variable `source_control_sync_job_stream_id`, `stream_type`, `summary` and `time` under property `properties` whose type is `SourceControlSyncJobStreamProperties`
  - Model `SourceControlSyncJobStreamById` moved instance variable `source_control_sync_job_stream_id`, `stream_text`, `stream_type`, `summary`, `time` and `value` under property `properties` whose type is `SourceControlSyncJobStreamByIdProperties`
  - Model `SourceControlUpdateParameters` moved instance variable `auto_sync`, `branch`, `description`, `folder_path`, `publish_runbook` and `security_token` under property `properties` whose type is `SourceControlUpdateProperties`
  - Model `Variable` moved instance variable `creation_time`, `description`, `is_encrypted`, `last_modified_time` and `value` under property `properties` whose type is `VariableProperties`
  - Model `VariableCreateOrUpdateParameters` moved instance variable `description`, `is_encrypted` and `value` under property `properties` whose type is `VariableCreateOrUpdateProperties`
  - Model `VariableUpdateParameters` moved instance variable `description` and `value` under property `properties` whose type is `VariableUpdateProperties`
  - Model `Watcher` moved instance variable `creation_time`, `description`, `execution_frequency_in_seconds`, `last_modified_by`, `last_modified_time`, `script_name`, `script_parameters`, `script_run_on` and `status` under property `properties` whose type is `WatcherProperties`
  - Model `WatcherUpdateParameters` moved instance variable `execution_frequency_in_seconds` under property `properties` whose type is `WatcherUpdateProperties`
  - Model `Webhook` moved instance variable `creation_time`, `description`, `expiry_time`, `is_enabled`, `last_invoked_time`, `last_modified_by`, `last_modified_time`, `parameters`, `run_on`, `runbook` and `uri` under property `properties` whose type is `WebhookProperties`
  - Model `WebhookCreateOrUpdateParameters` moved instance variable `expiry_time`, `is_enabled`, `parameters`, `run_on`, `runbook` and `uri` under property `properties` whose type is `WebhookCreateOrUpdateProperties`
  - Model `WebhookUpdateParameters` moved instance variable `description`, `is_enabled`, `parameters` and `run_on` under property `properties` whose type is `WebhookUpdateProperties`
  - Method `DscConfigurationOperations.list_by_automation_account` changed its parameter `inlinecount` from `positional_or_keyword` to `keyword_only`
  - Method `DscNodeConfigurationOperations.list_by_automation_account` changed its parameter `inlinecount` from `positional_or_keyword` to `keyword_only`
  - Method `DscNodeOperations.list_by_automation_account` changed its parameter `inlinecount` from `positional_or_keyword` to `keyword_only`
  - Method `HybridRunbookWorkerGroupOperations.update` renamed its parameter `parameters` to `hybrid_runbook_worker_group_updation_parameters`
  - Method `JobOperations.create` changed its parameter `client_request_id` from `positional_or_keyword` to `keyword_only`
  - Method `JobOperations.get` changed its parameter `client_request_id` from `positional_or_keyword` to `keyword_only`
  - Method `JobOperations.get_output` changed its parameter `client_request_id` from `positional_or_keyword` to `keyword_only`
  - Method `JobOperations.get_runbook_content` changed its parameter `client_request_id` from `positional_or_keyword` to `keyword_only`
  - Method `JobOperations.list_by_automation_account` changed its parameter `client_request_id` from `positional_or_keyword` to `keyword_only`
  - Method `JobOperations.resume` changed its parameter `client_request_id` from `positional_or_keyword` to `keyword_only`
  - Method `JobOperations.stop` changed its parameter `client_request_id` from `positional_or_keyword` to `keyword_only`
  - Method `JobOperations.suspend` changed its parameter `client_request_id` from `positional_or_keyword` to `keyword_only`
  - Method `JobStreamOperations.get` changed its parameter `client_request_id` from `positional_or_keyword` to `keyword_only`
  - Method `JobStreamOperations.list_by_job` changed its parameter `client_request_id` from `positional_or_keyword` to `keyword_only`
  - Method `RunbookDraftOperations.begin_replace_content` changed type of its parameter `runbook_content` from `IO[bytes]` to `str`
  - Method `SoftwareUpdateConfigurationMachineRunsOperations.get_by_id` changed its parameter `client_request_id` from `positional_or_keyword` to `keyword_only`
  - Method `SoftwareUpdateConfigurationMachineRunsOperations.list` changed its parameter `client_request_id` from `positional_or_keyword` to `keyword_only`
  - Method `SoftwareUpdateConfigurationRunsOperations.get_by_id` changed its parameter `client_request_id` from `positional_or_keyword` to `keyword_only`
  - Method `SoftwareUpdateConfigurationRunsOperations.list` changed its parameter `client_request_id` from `positional_or_keyword` to `keyword_only`
  - Method `SoftwareUpdateConfigurationsOperations.create` changed its parameter `client_request_id` from `positional_or_keyword` to `keyword_only`
  - Method `SoftwareUpdateConfigurationsOperations.delete` changed its parameter `client_request_id` from `positional_or_keyword` to `keyword_only`
  - Method `SoftwareUpdateConfigurationsOperations.get_by_name` changed its parameter `client_request_id` from `positional_or_keyword` to `keyword_only`
  - Method `SoftwareUpdateConfigurationsOperations.list` changed its parameter `client_request_id` from `positional_or_keyword` to `keyword_only`
  - Method `ConnectionOperations.delete` changed return type from `Optional[Connection]` to `None`
  - Method `DscConfigurationOperations.get_content` changed return type from `Iterator[bytes]` to `str`
  - Method `DscNodeOperations.delete` changed return type from `DscNode` to `None`
  - Method `JobOperations.get_output` changed return type from `Iterator[bytes]` to `str`
  - Method `JobOperations.get_runbook_content` changed return type from `Iterator[bytes]` to `str`
  - Method `NodeReportsOperations.get_content` changed return type from `JSON` to `str`
  - Method `RunbookDraftOperations.begin_replace_content` changed return type from `LROPoller[Iterator[bytes]]` to `LROPoller[None]`
  - Method `RunbookDraftOperations.get_content` changed return type from `Iterator[bytes]` to `str`
  - Method `RunbookOperations.get_content` changed return type from `Iterator[bytes]` to `str`

### Other Changes

  - Deleted model `ActivityListResult`/`AutomationAccountListResult`/`CertificateListResult`/`CollectionItemUpdateConfiguration`/`ConnectionListResult`/`ConnectionTypeListResult`/`CredentialListResult`/`DscCompilationJobListResult`/`DscConfigurationListResult`/`DscNodeConfigurationListResult`/`DscNodeListResult`/`DscNodeReportListResult`/`HybridRunbookWorkerGroupUpdateParameters`/`HybridRunbookWorkerGroupsListResult`/`JobListResultV2`/`JobScheduleListResult`/`JobStreamListResult`/`ModuleListResult`/`OperationListResult`/`RunbookCreateOrUpdateDraftParameters`/`RunbookCreateOrUpdateDraftProperties`/`RunbookListResult`/`ScheduleListResult`/`SoftareUpdateConfigurationRunTaskProperties`/`SoftareUpdateConfigurationRunTasks`/`SourceControlListResult`/`SourceControlSyncJobListResult`/`SourceControlSyncJobStreamsListBySyncJob`/`StatisticsListResult`/`TypeFieldListResult`/`UsageListResult`/`VariableListResult`/`WatcherListResult`/`WebhookListResult` which actually were not used by SDK users

## 1.1.0b5 (2026-05-27)

### Features Added

  - Client `AutomationClient` added parameter `cloud_setting` in method `__init__`
  - Client `AutomationClient` added method `send_request`
  - Client `AutomationClient` added operation group `runtime_environments`
  - Client `AutomationClient` added operation group `package`
  - Model `Certificate` added property `system_data`
  - Model `Connection` added property `system_data`
  - Model `ConnectionType` added property `system_data`
  - Model `Credential` added property `system_data`
  - Model `DscConfiguration` added property `system_data`
  - Model `DscNode` added property `system_data`
  - Model `DscNodeConfiguration` added property `system_data`
  - Model `HybridRunbookWorker` added property `tags`
  - Model `HybridRunbookWorker` added property `location`
  - Model `HybridRunbookWorkerGroup` added property `tags`
  - Model `HybridRunbookWorkerGroup` added property `location`
  - Model `Job` added property `system_data`
  - Model `JobCollectionItem` added property `system_data`
  - Model `JobSchedule` added property `system_data`
  - Model `Module` added property `system_data`
  - Model `PrivateEndpointConnection` added property `system_data`
  - Model `PrivateLinkResource` added property `system_data`
  - Model `ProxyResource` added property `system_data`
  - Model `Resource` added property `system_data`
  - Model `Runbook` added property `system_data`
  - Enum `RunbookTypeEnum` added member `POWER_SHELL72`
  - Enum `RunbookTypeEnum` added member `PYTHON`
  - Model `Schedule` added property `system_data`
  - Model `SoftwareUpdateConfiguration` added property `system_data`
  - Model `SourceControl` added property `system_data`
  - Model `TestJobCreateParameters` added property `runtime_environment`
  - Model `TrackedResource` added property `system_data`
  - Model `Variable` added property `system_data`
  - Model `Watcher` added property `system_data`
  - Model `Webhook` added property `system_data`
  - Added model `AutomationErrorResponse`
  - Added model `DeletedRunbook`
  - Added model `DeletedRunbookProperties`
  - Added model `ErrorAdditionalInfo`
  - Added model `JobRuntimeEnvironment`
  - Added model `Package`
  - Added model `PackageCreateOrUpdateParameters`
  - Added model `PackageCreateOrUpdateProperties`
  - Added model `PackageErrorInfo`
  - Added model `PackageProperties`
  - Added enum `PackageProvisioningState`
  - Added model `PackageUpdateParameters`
  - Added model `PackageUpdateProperties`
  - Added model `RuntimeEnvironment`
  - Added model `RuntimeEnvironmentProperties`
  - Added model `RuntimeEnvironmentUpdateParameters`
  - Added model `RuntimeEnvironmentUpdateProperties`
  - Added model `RuntimeProperties`
  - Operation group `AutomationAccountOperations` added method `list_deleted_runbooks`
  - Operation group `HybridRunbookWorkersOperations` added method `patch`
  - Added operation group `PackageOperations`
  - Added operation group `RuntimeEnvironmentsOperations`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. Please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - For the method breakings, please refer to https://aka.ms/azsdk/python/migrate/operations for migration.
  - Model `AgentRegistration` renamed its instance variable `keys` to `keys_property`
  - Model `AutomationAccountCreateOrUpdateParameters` moved instance variable `sku`, `encryption`, `public_network_access` and `disable_local_auth` under property `properties` whose type is `AutomationAccountCreateOrUpdateProperties`
  - Model `AutomationAccountUpdateParameters` moved instance variable `sku`, `encryption`, `public_network_access` and `disable_local_auth` under property `properties` whose type is `AutomationAccountUpdateProperties`
  - Model `CertificateCreateOrUpdateParameters` moved instance variable `base64_value`, `description`, `thumbprint` and `is_exportable` under property `properties` whose type is `CertificateCreateOrUpdateProperties`
  - Model `CertificateUpdateParameters` moved instance variable `description` under property `properties` whose type is `CertificateUpdateProperties`
  - Model `ConnectionCreateOrUpdateParameters` moved instance variable `description`, `connection_type` and `field_definition_values` under property `properties` whose type is `ConnectionCreateOrUpdateProperties`
  - Model `ConnectionTypeCreateOrUpdateParameters` moved instance variable `is_global` and `field_definitions` under property `properties` whose type is `ConnectionTypeCreateOrUpdateProperties`
  - Model `ConnectionUpdateParameters` moved instance variable `description` and `field_definition_values` under property `properties` whose type is `ConnectionUpdateProperties`
  - Model `CredentialCreateOrUpdateParameters` moved instance variable `user_name`, `password` and `description` under property `properties` whose type is `CredentialCreateOrUpdateProperties`
  - Model `CredentialUpdateParameters` moved instance variable `user_name`, `password` and `description` under property `properties` whose type is `CredentialUpdateProperties`
  - Model `DscConfigurationCreateOrUpdateParameters` moved instance variable `log_verbose`, `log_progress`, `source`, `parameters` and `description` under property `properties` whose type is `DscConfigurationCreateOrUpdateProperties`
  - Model `DscConfigurationUpdateParameters` moved instance variable `log_verbose`, `log_progress`, `source`, `parameters` and `description` under property `properties` whose type is `DscConfigurationCreateOrUpdateProperties`
  - Model `DscNodeUpdateParametersProperties` moved instance variable `name` under property `node_configuration` whose type is `DscNodeConfigurationAssociationProperty`
  - Model `ErrorResponse` moved instance variable `code` and `message` under property `error` whose type is `ErrorDetail`
  - Model `HybridRunbookWorkerCreateParameters` moved instance variable `vm_resource_id` under property `properties` whose type is `HybridRunbookWorkerCreateOrUpdateParameters`
  - Model `HybridRunbookWorkerGroupCreateOrUpdateParameters` moved instance variable `credential` under property `properties` whose type is `HybridRunbookWorkerGroupCreateOrUpdateProperties`
  - Model `JobCreateParameters` moved instance variable `runbook`, `parameters` and `run_on` under property `properties` whose type is `JobCreateProperties`
  - Model `JobScheduleCreateParameters` moved instance variable `schedule`, `runbook`, `run_on` and `parameters` under property `properties` whose type is `JobScheduleCreateProperties`
  - Model `KeyListResult` renamed its instance variable `keys` to `keys_property`
  - Model `ModuleCreateOrUpdateParameters` moved instance variable `content_link` under property `properties` whose type is `ModuleCreateOrUpdateProperties`
  - Renamed enum value `ModuleProvisioningState.CANCELLED` to `ModuleProvisioningState.CANCELED`
  - Model `ModuleUpdateParameters` moved instance variable `content_link` under property `properties` whose type is `ModuleUpdateProperties`
  - Model `Operation` moved instance variable `service_specification` under property `properties` whose type is `OperationPropertiesFormat`
  - Model `PythonPackageCreateParameters` moved instance variable `content_link` under property `properties` whose type is `PythonPackageCreateProperties`
  - Model `RunbookCreateOrUpdateParameters` moved instance variable `log_verbose`, `log_progress`, `runbook_type`, `draft`, `publish_content_link`, `description` and `log_activity_trace` under property `properties` whose type is `RunbookCreateOrUpdateProperties`
  - Model `RunbookUpdateParameters` moved instance variable `description`, `log_verbose`, `log_progress` and `log_activity_trace` under property `properties` whose type is `RunbookUpdateProperties`
  - Model `ScheduleCreateOrUpdateParameters` moved instance variable `description`, `start_time`, `expiry_time`, `interval`, `frequency`, `time_zone` and `advanced_schedule` under property `properties` whose type is `ScheduleCreateOrUpdateProperties`
  - Model `ScheduleUpdateParameters` moved instance variable `description` and `is_enabled` under property `properties` whose type is `ScheduleUpdateProperties`
  - Model `SoftwareUpdateConfigurationMachineRun` moved instance variable `target_computer`, `target_computer_type`, `software_update_configuration`, `status`, `os_type`, `correlation_id`, `source_computer_id`, `start_time`, `end_time`, `configured_duration`, `job`, `creation_time`, `created_by`, `last_modified_time`, `last_modified_by` and `error` under property `properties` whose type is `UpdateConfigurationMachineRunProperties`
  - Model `SourceControlCreateOrUpdateParameters` moved instance variable `repo_url`, `branch`, `folder_path`, `auto_sync`, `publish_runbook`, `source_type`, `security_token` and `description` under property `properties` whose type is `SourceControlCreateOrUpdateProperties`
  - Model `SourceControlSyncJobCreateParameters` moved instance variable `commit_id` under property `properties` whose type is `SourceControlSyncJobCreateProperties`
  - Model `SourceControlUpdateParameters` moved instance variable `branch`, `folder_path`, `auto_sync`, `publish_runbook`, `security_token` and `description` under property `properties` whose type is `SourceControlUpdateProperties`
  - Model `VariableCreateOrUpdateParameters` moved instance variable `value`, `description` and `is_encrypted` under property `properties` whose type is `VariableCreateOrUpdateProperties`
  - Model `VariableUpdateParameters` moved instance variable `value` and `description` under property `properties` whose type is `VariableUpdateProperties`
  - Model `WatcherUpdateParameters` moved instance variable `execution_frequency_in_seconds` under property `properties` whose type is `WatcherUpdateProperties`
  - Model `WebhookCreateOrUpdateParameters` moved instance variable `is_enabled`, `uri`, `expiry_time`, `parameters`, `runbook` and `run_on` under property `properties` whose type is `WebhookCreateOrUpdateProperties`
  - Model `WebhookUpdateParameters` moved instance variable `is_enabled`, `run_on`, `parameters` and `description` under property `properties` whose type is `WebhookUpdateProperties`
  - Deleted operation group `AutomationClient.dsc_compilation_job`/`AutomationClient.dsc_compilation_job_stream` and their corresponding models `DscCompilationJob`/`DscCompilationJobCreateParameters` were also deleted
  - Method `DscConfigurationOperations.list_by_automation_account` changed its parameter `inlinecount` from `positional_or_keyword` to `keyword_only`
  - Method `DscNodeConfigurationOperations.list_by_automation_account` changed its parameter `inlinecount` from `positional_or_keyword` to `keyword_only`
  - Method `DscNodeOperations.list_by_automation_account` changed its parameter `inlinecount` from `positional_or_keyword` to `keyword_only`
  - Method `JobOperations.create` changed its parameter `client_request_id` from `positional_or_keyword` to `keyword_only`
  - Method `JobOperations.get` changed its parameter `client_request_id` from `positional_or_keyword` to `keyword_only`
  - Method `JobOperations.get_output` changed its parameter `client_request_id` from `positional_or_keyword` to `keyword_only`
  - Method `JobOperations.get_runbook_content` changed its parameter `client_request_id` from `positional_or_keyword` to `keyword_only`
  - Method `JobOperations.list_by_automation_account` changed its parameter `client_request_id` from `positional_or_keyword` to `keyword_only`
  - Method `JobOperations.resume` changed its parameter `client_request_id` from `positional_or_keyword` to `keyword_only`
  - Method `JobOperations.stop` changed its parameter `client_request_id` from `positional_or_keyword` to `keyword_only`
  - Method `JobOperations.suspend` changed its parameter `client_request_id` from `positional_or_keyword` to `keyword_only`
  - Method `JobStreamOperations.get` changed its parameter `client_request_id` from `positional_or_keyword` to `keyword_only`
  - Method `JobStreamOperations.list_by_job` changed its parameter `client_request_id` from `positional_or_keyword` to `keyword_only`
  - Method `SoftwareUpdateConfigurationMachineRunsOperations.get_by_id` changed its parameter `client_request_id` from `positional_or_keyword` to `keyword_only`
  - Method `SoftwareUpdateConfigurationMachineRunsOperations.list` changed its parameter `client_request_id` from `positional_or_keyword` to `keyword_only`
  - Method `SoftwareUpdateConfigurationRunsOperations.get_by_id` changed its parameter `client_request_id` from `positional_or_keyword` to `keyword_only`
  - Method `SoftwareUpdateConfigurationRunsOperations.list` changed its parameter `client_request_id` from `positional_or_keyword` to `keyword_only`
  - Method `SoftwareUpdateConfigurationsOperations.create` changed its parameter `client_request_id` from `positional_or_keyword` to `keyword_only`
  - Method `SoftwareUpdateConfigurationsOperations.delete` changed its parameter `client_request_id` from `positional_or_keyword` to `keyword_only`
  - Method `SoftwareUpdateConfigurationsOperations.get_by_name` changed its parameter `client_request_id` from `positional_or_keyword` to `keyword_only`
  - Method `SoftwareUpdateConfigurationsOperations.list` changed its parameter `client_request_id` from `positional_or_keyword` to `keyword_only`
  - Method `DscConfigurationOperations.get_content` changed return type from `Iterator[bytes]` to `str`
  - Method `NodeReportsOperations.get_content` changed return type from `JSON` to `str`
  - Method `RunbookDraftOperations.begin_replace_content` changed return type from `LROPoller[Iterator[bytes]]` to `LROPoller[None]`
  - Method `RunbookDraftOperations.get_content` changed return type from `Iterator[bytes]` to `str`
  - Method `RunbookOperations.get_content` changed return type from `Iterator[bytes]` to `str`

### Other Changes

  - Deleted model `JobListResultV2`/`SourceControlSyncJobStreamsListBySyncJob`/`RunbookCreateOrUpdateDraftParameters`/`RunbookCreateOrUpdateDraftProperties` which actually were not used by SDK users

## 1.0.1 (2026-05-14)

### Other Changes

  - Regenerated with latest code generator tool

## 1.1.0b4 (2024-11-05)

### Other Changes

  - Update dependencies

## 1.1.0b3 (2022-12-12)

### Features Added

  - Added operation group DeletedAutomationAccountsOperations
  - Added operation group Python3PackageOperations
  - Model HybridRunbookWorkerGroupCreateOrUpdateParameters has a new parameter name
  - Model Operation has a new parameter origin
  - Model Operation has a new parameter service_specification
  - Model OperationDisplay has a new parameter description

### Breaking Changes

  - Model HybridRunbookWorkerGroup no longer has parameter hybrid_runbook_workers
  - Operation DscConfigurationOperations.create_or_update no longer has parameter content_type
  - Operation DscConfigurationOperations.update no longer has parameter content_type
  - Operation HybridRunbookWorkerGroupOperations.update has a new required parameter hybrid_runbook_worker_group_updation_parameters
  - Operation HybridRunbookWorkerGroupOperations.update no longer has parameter parameters

## 1.1.0b2 (2022-07-18)

**Features**

  - Added operation HybridRunbookWorkerGroupOperations.create
  - Added operation group AutomationClientOperationsMixin
  - Added operation group HybridRunbookWorkersOperations
  - Added operation group PrivateEndpointConnectionsOperations
  - Added operation group PrivateLinkResourcesOperations
  - Model AutomationAccount has a new parameter automation_hybrid_service_url
  - Model AutomationAccount has a new parameter disable_local_auth
  - Model AutomationAccount has a new parameter encryption
  - Model AutomationAccount has a new parameter identity
  - Model AutomationAccount has a new parameter private_endpoint_connections
  - Model AutomationAccount has a new parameter public_network_access
  - Model AutomationAccount has a new parameter system_data
  - Model AutomationAccountCreateOrUpdateParameters has a new parameter disable_local_auth
  - Model AutomationAccountCreateOrUpdateParameters has a new parameter encryption
  - Model AutomationAccountCreateOrUpdateParameters has a new parameter identity
  - Model AutomationAccountCreateOrUpdateParameters has a new parameter public_network_access
  - Model AutomationAccountUpdateParameters has a new parameter disable_local_auth
  - Model AutomationAccountUpdateParameters has a new parameter encryption
  - Model AutomationAccountUpdateParameters has a new parameter identity
  - Model AutomationAccountUpdateParameters has a new parameter public_network_access
  - Model HybridRunbookWorker has a new parameter id
  - Model HybridRunbookWorker has a new parameter registered_date_time
  - Model HybridRunbookWorker has a new parameter system_data
  - Model HybridRunbookWorker has a new parameter type
  - Model HybridRunbookWorker has a new parameter vm_resource_id
  - Model HybridRunbookWorker has a new parameter worker_name
  - Model HybridRunbookWorker has a new parameter worker_type
  - Model HybridRunbookWorkerGroup has a new parameter system_data
  - Model HybridRunbookWorkerGroup has a new parameter type
  - Operation DscConfigurationOperations.create_or_update has a new optional and keyword-only parameter content_type
  - Operation DscConfigurationOperations.update has a new optional and keyword-only parameter content_type

**Breaking changes**

  - Model HybridRunbookWorker no longer has parameter registration_time

## 1.1.0b1 (2021-03-16)

**Features**

  - Model SoftwareUpdateConfigurationCollectionItem has a new parameter tasks

## 1.0.0 (2020-12-17)

- GA release

## 1.0.0b1 (2020-11-11)

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

## 0.1.1 (2019-05-13)

**Bugfixes**

  - Remove incorrect "count_type1" parameter from client signature
    #4965

## 0.1.0 (2019-04-16)

  - Initial Release
