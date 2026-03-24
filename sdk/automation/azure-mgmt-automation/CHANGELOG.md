# Release History

## 1.1.0b5 (2026-03-24)

### Features Added

  - Client `AutomationClient` added method `send_request`
  - Model `AgentRegistration` added property `keys_property`
  - Model `AutomationAccountCreateOrUpdateParameters` added property `properties`
  - Model `AutomationAccountUpdateParameters` added property `properties`
  - Model `CertificateCreateOrUpdateParameters` added property `properties`
  - Model `CertificateUpdateParameters` added property `properties`
  - Model `ConnectionCreateOrUpdateParameters` added property `properties`
  - Model `ConnectionType` added property `system_data`
  - Model `ConnectionTypeCreateOrUpdateParameters` added property `properties`
  - Model `ConnectionUpdateParameters` added property `properties`
  - Model `CredentialCreateOrUpdateParameters` added property `properties`
  - Model `CredentialUpdateParameters` added property `properties`
  - Model `DscConfigurationCreateOrUpdateParameters` added property `properties`
  - Model `DscConfigurationUpdateParameters` added property `properties`
  - Model `HybridRunbookWorkerCreateParameters` added property `properties`
  - Model `HybridRunbookWorkerGroupCreateOrUpdateParameters` added property `properties`
  - Model `JobSchedule` added property `system_data`
  - Model `ModuleCreateOrUpdateParameters` added property `properties`
  - Model `ModuleUpdateParameters` added property `properties`
  - Model `Operation` added property `properties`
  - Model `PackageCreateOrUpdateParameters` added property `properties`
  - Model `PackageUpdateParameters` added property `properties`
  - Model `PythonPackageCreateParameters` added property `properties`
  - Model `RunbookCreateOrUpdateParameters` added property `properties`
  - Model `RunbookUpdateParameters` added property `properties`
  - Model `RuntimeEnvironmentUpdateParameters` added property `properties`
  - Model `ScheduleCreateOrUpdateParameters` added property `properties`
  - Model `ScheduleUpdateParameters` added property `properties`
  - Model `SoftwareUpdateConfiguration` added property `system_data`
  - Model `SoftwareUpdateConfigurationMachineRun` added property `properties`
  - Model `VariableCreateOrUpdateParameters` added property `properties`
  - Model `VariableUpdateParameters` added property `properties`
  - Model `WatcherUpdateParameters` added property `properties`
  - Model `WebhookCreateOrUpdateParameters` added property `properties`
  - Model `WebhookUpdateParameters` added property `properties`
  - Added model `AutomationAccountCreateOrUpdateProperties`
  - Added model `AutomationAccountUpdateProperties`
  - Added model `AutomationErrorResponse`
  - Added model `CertificateCreateOrUpdateProperties`
  - Added model `CertificateUpdateProperties`
  - Added model `ConnectionCreateOrUpdateProperties`
  - Added model `ConnectionTypeCreateOrUpdateProperties`
  - Added model `ConnectionUpdateProperties`
  - Added model `CredentialCreateOrUpdateProperties`
  - Added model `CredentialUpdateProperties`
  - Added model `DscConfigurationCreateOrUpdateProperties`
  - Added model `DscNodeConfigurationAssociationProperty`
  - Added model `ErrorAdditionalInfo`
  - Added model `ErrorDetail`
  - Added model `HybridRunbookWorkerCreateOrUpdateParameters`
  - Added model `HybridRunbookWorkerGroupCreateOrUpdateProperties`
  - Added model `JobCreateProperties`
  - Added model `JobScheduleCreateProperties`
  - Added model `ModuleCreateOrUpdateProperties`
  - Added model `ModuleUpdateProperties`
  - Added model `OperationPropertiesFormat`
  - Added model `PackageCreateOrUpdateProperties`
  - Added model `PackageUpdateProperties`
  - Added model `PythonPackageCreateProperties`
  - Added model `ReplaceContentFinalResult`
  - Added model `RunbookCreateOrUpdateProperties`
  - Added model `RunbookUpdateProperties`
  - Added model `RuntimeEnvironmentUpdateProperties`
  - Added model `RuntimeProperties`
  - Added model `ScheduleCreateOrUpdateProperties`
  - Added model `ScheduleUpdateProperties`
  - Added model `SourceControlCreateOrUpdateProperties`
  - Added model `SourceControlSyncJobCreateProperties`
  - Added model `SourceControlUpdateProperties`
  - Added model `UpdateConfigurationMachineRunProperties`
  - Added model `VariableCreateOrUpdateProperties`
  - Added model `VariableUpdateProperties`
  - Added model `WatcherUpdateProperties`
  - Added model `WebhookCreateOrUpdateProperties`
  - Added model `WebhookUpdateProperties`

### Breaking Changes

  - Model `AgentRegistration` deleted or renamed its instance variable `keys`
  - Model `AutomationAccountCreateOrUpdateParameters` deleted or renamed its instance variable `sku`
  - Model `AutomationAccountCreateOrUpdateParameters` deleted or renamed its instance variable `encryption`
  - Model `AutomationAccountCreateOrUpdateParameters` deleted or renamed its instance variable `public_network_access`
  - Model `AutomationAccountCreateOrUpdateParameters` deleted or renamed its instance variable `disable_local_auth`
  - Model `AutomationAccountUpdateParameters` deleted or renamed its instance variable `sku`
  - Model `AutomationAccountUpdateParameters` deleted or renamed its instance variable `encryption`
  - Model `AutomationAccountUpdateParameters` deleted or renamed its instance variable `public_network_access`
  - Model `AutomationAccountUpdateParameters` deleted or renamed its instance variable `disable_local_auth`
  - Model `CertificateCreateOrUpdateParameters` deleted or renamed its instance variable `base64_value`
  - Model `CertificateCreateOrUpdateParameters` deleted or renamed its instance variable `description`
  - Model `CertificateCreateOrUpdateParameters` deleted or renamed its instance variable `thumbprint`
  - Model `CertificateCreateOrUpdateParameters` deleted or renamed its instance variable `is_exportable`
  - Model `CertificateUpdateParameters` deleted or renamed its instance variable `description`
  - Model `ConnectionCreateOrUpdateParameters` deleted or renamed its instance variable `description`
  - Model `ConnectionCreateOrUpdateParameters` deleted or renamed its instance variable `connection_type`
  - Model `ConnectionCreateOrUpdateParameters` deleted or renamed its instance variable `field_definition_values`
  - Model `ConnectionTypeCreateOrUpdateParameters` deleted or renamed its instance variable `is_global`
  - Model `ConnectionTypeCreateOrUpdateParameters` deleted or renamed its instance variable `field_definitions`
  - Model `ConnectionUpdateParameters` deleted or renamed its instance variable `description`
  - Model `ConnectionUpdateParameters` deleted or renamed its instance variable `field_definition_values`
  - Model `CredentialCreateOrUpdateParameters` deleted or renamed its instance variable `user_name`
  - Model `CredentialCreateOrUpdateParameters` deleted or renamed its instance variable `password`
  - Model `CredentialCreateOrUpdateParameters` deleted or renamed its instance variable `description`
  - Model `CredentialUpdateParameters` deleted or renamed its instance variable `user_name`
  - Model `CredentialUpdateParameters` deleted or renamed its instance variable `password`
  - Model `CredentialUpdateParameters` deleted or renamed its instance variable `description`
  - Model `DscConfigurationCreateOrUpdateParameters` deleted or renamed its instance variable `log_verbose`
  - Model `DscConfigurationCreateOrUpdateParameters` deleted or renamed its instance variable `log_progress`
  - Model `DscConfigurationCreateOrUpdateParameters` deleted or renamed its instance variable `source`
  - Model `DscConfigurationCreateOrUpdateParameters` deleted or renamed its instance variable `parameters`
  - Model `DscConfigurationCreateOrUpdateParameters` deleted or renamed its instance variable `description`
  - Model `DscConfigurationUpdateParameters` deleted or renamed its instance variable `log_verbose`
  - Model `DscConfigurationUpdateParameters` deleted or renamed its instance variable `log_progress`
  - Model `DscConfigurationUpdateParameters` deleted or renamed its instance variable `source`
  - Model `DscConfigurationUpdateParameters` deleted or renamed its instance variable `parameters`
  - Model `DscConfigurationUpdateParameters` deleted or renamed its instance variable `description`
  - Model `DscNodeUpdateParametersProperties` deleted or renamed its instance variable `name`
  - Model `ErrorResponse` deleted or renamed its instance variable `code`
  - Model `ErrorResponse` deleted or renamed its instance variable `message`
  - Model `HybridRunbookWorkerCreateParameters` deleted or renamed its instance variable `vm_resource_id`
  - Model `HybridRunbookWorkerGroupCreateOrUpdateParameters` deleted or renamed its instance variable `credential`
  - Model `JobCreateParameters` deleted or renamed its instance variable `runbook`
  - Model `JobCreateParameters` deleted or renamed its instance variable `parameters`
  - Model `JobCreateParameters` deleted or renamed its instance variable `run_on`
  - Model `JobScheduleCreateParameters` deleted or renamed its instance variable `schedule`
  - Model `JobScheduleCreateParameters` deleted or renamed its instance variable `runbook`
  - Model `JobScheduleCreateParameters` deleted or renamed its instance variable `run_on`
  - Model `JobScheduleCreateParameters` deleted or renamed its instance variable `parameters`
  - Model `KeyListResult` deleted or renamed its instance variable `keys`
  - Model `ModuleCreateOrUpdateParameters` deleted or renamed its instance variable `content_link`
  - Model `ModuleUpdateParameters` deleted or renamed its instance variable `content_link`
  - Model `Operation` deleted or renamed its instance variable `service_specification`
  - Model `PackageCreateOrUpdateParameters` deleted or renamed its instance variable `content_link`
  - Model `PackageUpdateParameters` deleted or renamed its instance variable `content_link`
  - Model `PythonPackageCreateParameters` deleted or renamed its instance variable `content_link`
  - Model `RunbookCreateOrUpdateParameters` deleted or renamed its instance variable `log_verbose`
  - Model `RunbookCreateOrUpdateParameters` deleted or renamed its instance variable `log_progress`
  - Model `RunbookCreateOrUpdateParameters` deleted or renamed its instance variable `runtime_environment`
  - Model `RunbookCreateOrUpdateParameters` deleted or renamed its instance variable `runbook_type`
  - Model `RunbookCreateOrUpdateParameters` deleted or renamed its instance variable `draft`
  - Model `RunbookCreateOrUpdateParameters` deleted or renamed its instance variable `publish_content_link`
  - Model `RunbookCreateOrUpdateParameters` deleted or renamed its instance variable `description`
  - Model `RunbookCreateOrUpdateParameters` deleted or renamed its instance variable `log_activity_trace`
  - Model `RunbookUpdateParameters` deleted or renamed its instance variable `description`
  - Model `RunbookUpdateParameters` deleted or renamed its instance variable `log_verbose`
  - Model `RunbookUpdateParameters` deleted or renamed its instance variable `log_progress`
  - Model `RunbookUpdateParameters` deleted or renamed its instance variable `log_activity_trace`
  - Model `RuntimeEnvironmentUpdateParameters` deleted or renamed its instance variable `default_packages`
  - Model `ScheduleCreateOrUpdateParameters` deleted or renamed its instance variable `description`
  - Model `ScheduleCreateOrUpdateParameters` deleted or renamed its instance variable `start_time`
  - Model `ScheduleCreateOrUpdateParameters` deleted or renamed its instance variable `expiry_time`
  - Model `ScheduleCreateOrUpdateParameters` deleted or renamed its instance variable `interval`
  - Model `ScheduleCreateOrUpdateParameters` deleted or renamed its instance variable `frequency`
  - Model `ScheduleCreateOrUpdateParameters` deleted or renamed its instance variable `time_zone`
  - Model `ScheduleCreateOrUpdateParameters` deleted or renamed its instance variable `advanced_schedule`
  - Model `ScheduleUpdateParameters` deleted or renamed its instance variable `description`
  - Model `ScheduleUpdateParameters` deleted or renamed its instance variable `is_enabled`
  - Model `SoftwareUpdateConfigurationMachineRun` deleted or renamed its instance variable `target_computer`
  - Model `SoftwareUpdateConfigurationMachineRun` deleted or renamed its instance variable `target_computer_type`
  - Model `SoftwareUpdateConfigurationMachineRun` deleted or renamed its instance variable `software_update_configuration`
  - Model `SoftwareUpdateConfigurationMachineRun` deleted or renamed its instance variable `status`
  - Model `SoftwareUpdateConfigurationMachineRun` deleted or renamed its instance variable `os_type`
  - Model `SoftwareUpdateConfigurationMachineRun` deleted or renamed its instance variable `correlation_id`
  - Model `SoftwareUpdateConfigurationMachineRun` deleted or renamed its instance variable `source_computer_id`
  - Model `SoftwareUpdateConfigurationMachineRun` deleted or renamed its instance variable `start_time`
  - Model `SoftwareUpdateConfigurationMachineRun` deleted or renamed its instance variable `end_time`
  - Model `SoftwareUpdateConfigurationMachineRun` deleted or renamed its instance variable `configured_duration`
  - Model `SoftwareUpdateConfigurationMachineRun` deleted or renamed its instance variable `job`
  - Model `SoftwareUpdateConfigurationMachineRun` deleted or renamed its instance variable `creation_time`
  - Model `SoftwareUpdateConfigurationMachineRun` deleted or renamed its instance variable `created_by`
  - Model `SoftwareUpdateConfigurationMachineRun` deleted or renamed its instance variable `last_modified_time`
  - Model `SoftwareUpdateConfigurationMachineRun` deleted or renamed its instance variable `last_modified_by`
  - Model `SoftwareUpdateConfigurationMachineRun` deleted or renamed its instance variable `error`
  - Model `SourceControlCreateOrUpdateParameters` deleted or renamed its instance variable `repo_url`
  - Model `SourceControlCreateOrUpdateParameters` deleted or renamed its instance variable `branch`
  - Model `SourceControlCreateOrUpdateParameters` deleted or renamed its instance variable `folder_path`
  - Model `SourceControlCreateOrUpdateParameters` deleted or renamed its instance variable `auto_sync`
  - Model `SourceControlCreateOrUpdateParameters` deleted or renamed its instance variable `publish_runbook`
  - Model `SourceControlCreateOrUpdateParameters` deleted or renamed its instance variable `source_type`
  - Model `SourceControlCreateOrUpdateParameters` deleted or renamed its instance variable `security_token`
  - Model `SourceControlCreateOrUpdateParameters` deleted or renamed its instance variable `description`
  - Model `SourceControlSyncJobCreateParameters` deleted or renamed its instance variable `commit_id`
  - Model `SourceControlUpdateParameters` deleted or renamed its instance variable `branch`
  - Model `SourceControlUpdateParameters` deleted or renamed its instance variable `folder_path`
  - Model `SourceControlUpdateParameters` deleted or renamed its instance variable `auto_sync`
  - Model `SourceControlUpdateParameters` deleted or renamed its instance variable `publish_runbook`
  - Model `SourceControlUpdateParameters` deleted or renamed its instance variable `security_token`
  - Model `SourceControlUpdateParameters` deleted or renamed its instance variable `description`
  - Model `VariableCreateOrUpdateParameters` deleted or renamed its instance variable `value`
  - Model `VariableCreateOrUpdateParameters` deleted or renamed its instance variable `description`
  - Model `VariableCreateOrUpdateParameters` deleted or renamed its instance variable `is_encrypted`
  - Model `VariableUpdateParameters` deleted or renamed its instance variable `value`
  - Model `VariableUpdateParameters` deleted or renamed its instance variable `description`
  - Model `WatcherUpdateParameters` deleted or renamed its instance variable `execution_frequency_in_seconds`
  - Model `WebhookCreateOrUpdateParameters` deleted or renamed its instance variable `is_enabled`
  - Model `WebhookCreateOrUpdateParameters` deleted or renamed its instance variable `uri`
  - Model `WebhookCreateOrUpdateParameters` deleted or renamed its instance variable `expiry_time`
  - Model `WebhookCreateOrUpdateParameters` deleted or renamed its instance variable `parameters`
  - Model `WebhookCreateOrUpdateParameters` deleted or renamed its instance variable `runbook`
  - Model `WebhookCreateOrUpdateParameters` deleted or renamed its instance variable `run_on`
  - Model `WebhookUpdateParameters` deleted or renamed its instance variable `is_enabled`
  - Model `WebhookUpdateParameters` deleted or renamed its instance variable `run_on`
  - Model `WebhookUpdateParameters` deleted or renamed its instance variable `parameters`
  - Model `WebhookUpdateParameters` deleted or renamed its instance variable `description`
  - Deleted or renamed model `JobListResultV2`
  - Deleted or renamed model `RunbookCreateOrUpdateDraftParameters`
  - Deleted or renamed model `RunbookCreateOrUpdateDraftProperties`
  - Deleted or renamed model `SourceControlSyncJobStreamsListBySyncJob`
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

## 1.1.0 (2026-03-24)

skip changelog generation

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
