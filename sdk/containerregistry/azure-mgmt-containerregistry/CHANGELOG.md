# Release History

## 14.1.0b4 (2025-12-05)

### Other Changes

  - Regular update

## 14.1.0b3 (2025-11-05)

### Features Added

  - Model `ContainerRegistryManagementClient` added parameter `cloud_setting` in method `__init__`
  - Model `PrivateLinkResource` added property `system_data`
  - Added model `TrackedResource`

### Breaking Changes

  - Deleted or renamed client operation group `ContainerRegistryManagementClient.archives`
  - Deleted or renamed client operation group `ContainerRegistryManagementClient.archive_versions`
  - Deleted or renamed client operation group `ContainerRegistryManagementClient.export_pipelines`
  - Deleted or renamed client operation group `ContainerRegistryManagementClient.import_pipelines`
  - Deleted or renamed client operation group `ContainerRegistryManagementClient.pipeline_runs`
  - Model `Policies` deleted or renamed its instance variable `soft_delete_policy`
  - Model `Registry` deleted or renamed its instance variable `metadata_search`
  - Model `RegistryUpdateParameters` deleted or renamed its instance variable `metadata_search`
  - Model `Resource` deleted or renamed its instance variable `location`
  - Model `Resource` deleted or renamed its instance variable `tags`
  - Deleted or renamed model `ActiveDirectoryObject`
  - Deleted or renamed model `Archive`
  - Deleted or renamed model `ArchivePackageSourceProperties`
  - Deleted or renamed model `ArchiveProperties`
  - Deleted or renamed model `ArchiveUpdateParameters`
  - Deleted or renamed model `ArchiveVersion`
  - Deleted or renamed model `DebianArchivePackageSourceProperties`
  - Deleted or renamed model `DebianArchiveProperties`
  - Deleted or renamed model `ExportPipeline`
  - Deleted or renamed model `ExportPipelineTargetProperties`
  - Deleted or renamed model `ImportPipeline`
  - Deleted or renamed model `ImportPipelineSourceProperties`
  - Deleted or renamed model `LastModifiedByType`
  - Deleted or renamed model `MetadataSearch`
  - Deleted or renamed model `PackageSourceType`
  - Deleted or renamed model `PackageType`
  - Deleted or renamed model `PipelineOptions`
  - Deleted or renamed model `PipelineRun`
  - Deleted or renamed model `PipelineRunRequest`
  - Deleted or renamed model `PipelineRunResponse`
  - Deleted or renamed model `PipelineRunSourceProperties`
  - Deleted or renamed model `PipelineRunSourceType`
  - Deleted or renamed model `PipelineRunTargetProperties`
  - Deleted or renamed model `PipelineRunTargetType`
  - Deleted or renamed model `PipelineSourceTriggerDescriptor`
  - Deleted or renamed model `PipelineSourceTriggerProperties`
  - Deleted or renamed model `PipelineSourceType`
  - Deleted or renamed model `PipelineTriggerDescriptor`
  - Deleted or renamed model `PipelineTriggerProperties`
  - Deleted or renamed model `ProgressProperties`
  - Deleted or renamed model `RunFilter`
  - Deleted or renamed model `SoftDeletePolicy`
  - Deleted or renamed model `StorageAccountProperties`

## 14.1.0b2 (2025-08-15)

### Features Added

  - Client `ContainerRegistryManagementClient` added operation group `archives`
  - Client `ContainerRegistryManagementClient` added operation group `archive_versions`
  - Client `ContainerRegistryManagementClient` added operation group `export_pipelines`
  - Client `ContainerRegistryManagementClient` added operation group `import_pipelines`
  - Client `ContainerRegistryManagementClient` added operation group `pipeline_runs`
  - Client `ContainerRegistryManagementClient` added operation group `agent_pools`
  - Client `ContainerRegistryManagementClient` added operation group `runs`
  - Client `ContainerRegistryManagementClient` added operation group `task_runs`
  - Client `ContainerRegistryManagementClient` added operation group `tasks`
  - Model `Policies` added property `soft_delete_policy`
  - Model `Registry` added property `network_rule_bypass_allowed_for_tasks`
  - Model `Registry` added property `metadata_search`
  - Model `Registry` added property `auto_generated_domain_name_label_scope`
  - Model `Registry` added property `role_assignment_mode`
  - Model `RegistryNameCheckRequest` added property `resource_group_name`
  - Model `RegistryNameCheckRequest` added property `auto_generated_domain_name_label_scope`
  - Model `RegistryNameStatus` added property `available_login_server_name`
  - Model `RegistryUpdateParameters` added property `network_rule_bypass_allowed_for_tasks`
  - Model `RegistryUpdateParameters` added property `metadata_search`
  - Model `RegistryUpdateParameters` added property `role_assignment_mode`
  - Added model `AgentPool`
  - Added model `AgentPoolListResult`
  - Added model `AgentPoolQueueStatus`
  - Added model `AgentPoolUpdateParameters`
  - Added model `AgentProperties`
  - Added enum `Architecture`
  - Added model `Archive`
  - Added model `ArchiveListResult`
  - Added model `ArchivePackageSourceProperties`
  - Added model `ArchiveProperties`
  - Added model `ArchiveUpdateParameters`
  - Added model `ArchiveVersion`
  - Added model `ArchiveVersionListResult`
  - Added model `Argument`
  - Added model `AuthInfo`
  - Added model `AuthInfoUpdateParameters`
  - Added enum `AutoGeneratedDomainNameLabelScope`
  - Added model `BaseImageDependency`
  - Added enum `BaseImageDependencyType`
  - Added model `BaseImageTrigger`
  - Added enum `BaseImageTriggerType`
  - Added model `BaseImageTriggerUpdateParameters`
  - Added model `Credentials`
  - Added model `CustomRegistryCredentials`
  - Added model `DebianArchivePackageSourceProperties`
  - Added model `DebianArchiveProperties`
  - Added model `DockerBuildRequest`
  - Added model `DockerBuildStep`
  - Added model `DockerBuildStepUpdateParameters`
  - Added model `EncodedTaskRunRequest`
  - Added model `EncodedTaskStep`
  - Added model `EncodedTaskStepUpdateParameters`
  - Added model `ExportPipeline`
  - Added model `ExportPipelineListResult`
  - Added model `ExportPipelineTargetProperties`
  - Added model `FileTaskRunRequest`
  - Added model `FileTaskStep`
  - Added model `FileTaskStepUpdateParameters`
  - Added model `ImageDescriptor`
  - Added model `ImageUpdateTrigger`
  - Added model `ImportPipeline`
  - Added model `ImportPipelineListResult`
  - Added model `ImportPipelineSourceProperties`
  - Added enum `MetadataSearch`
  - Added enum `OS`
  - Added model `OverrideTaskStepProperties`
  - Added enum `PackageSourceType`
  - Added enum `PipelineOptions`
  - Added model `PipelineRun`
  - Added model `PipelineRunListResult`
  - Added model `PipelineRunRequest`
  - Added model `PipelineRunResponse`
  - Added model `PipelineRunSourceProperties`
  - Added enum `PipelineRunSourceType`
  - Added model `PipelineRunTargetProperties`
  - Added enum `PipelineRunTargetType`
  - Added model `PipelineSourceTriggerDescriptor`
  - Added model `PipelineSourceTriggerProperties`
  - Added enum `PipelineSourceType`
  - Added model `PipelineTriggerDescriptor`
  - Added model `PipelineTriggerProperties`
  - Added model `PlatformProperties`
  - Added model `PlatformUpdateParameters`
  - Added model `ProgressProperties`
  - Added enum `RoleAssignmentMode`
  - Added model `Run`
  - Added model `RunFilter`
  - Added model `RunGetLogResult`
  - Added model `RunListResult`
  - Added model `RunRequest`
  - Added enum `RunStatus`
  - Added enum `RunType`
  - Added model `RunUpdateParameters`
  - Added model `SecretObject`
  - Added enum `SecretObjectType`
  - Added model `SetValue`
  - Added model `SoftDeletePolicy`
  - Added enum `SourceControlType`
  - Added model `SourceProperties`
  - Added model `SourceRegistryCredentials`
  - Added enum `SourceRegistryLoginMode`
  - Added model `SourceTrigger`
  - Added model `SourceTriggerDescriptor`
  - Added enum `SourceTriggerEvent`
  - Added model `SourceTriggerUpdateParameters`
  - Added model `SourceUpdateParameters`
  - Added model `SourceUploadDefinition`
  - Added enum `StepType`
  - Added model `Task`
  - Added model `TaskListResult`
  - Added model `TaskRun`
  - Added model `TaskRunListResult`
  - Added model `TaskRunRequest`
  - Added model `TaskRunUpdateParameters`
  - Added enum `TaskStatus`
  - Added model `TaskStepProperties`
  - Added model `TaskStepUpdateParameters`
  - Added model `TaskUpdateParameters`
  - Added model `TimerTrigger`
  - Added model `TimerTriggerDescriptor`
  - Added model `TimerTriggerUpdateParameters`
  - Added enum `TokenType`
  - Added model `TriggerProperties`
  - Added enum `TriggerStatus`
  - Added model `TriggerUpdateParameters`
  - Added enum `UpdateTriggerPayloadType`
  - Added enum `Variant`
  - Operation group `RegistriesOperations` added method `get_build_source_upload_url`
  - Operation group `RegistriesOperations` added method `schedule_run`
  - Added operation group `AgentPoolsOperations`
  - Added operation group `ArchiveVersionsOperations`
  - Added operation group `ArchivesOperations`
  - Added operation group `ExportPipelinesOperations`
  - Added operation group `ImportPipelinesOperations`
  - Added operation group `PipelineRunsOperations`
  - Added operation group `RunsOperations`
  - Added operation group `TaskRunsOperations`
  - Added operation group `TasksOperations`

### Breaking Changes

  - This package now only targets the latest Api-Version available on Azure and removes APIs of other Api-Version. After this change, the package can have much smaller size. If your application requires a specific and non-latest Api-Version, it's recommended to pin this package to the previous released version; If your application always only use latest Api-Version, please ignore this change.
  - Deleted or renamed model `ConnectedRegistryProperties`
  - Deleted or renamed model `ConnectedRegistryPropertiesActivation`
  - Deleted or renamed model `ConnectedRegistryPropertiesAutoGenerated`
  - Deleted or renamed model `ConnectedRegistryUpdateParametersProperties`
  - Deleted or renamed model `ConnectedRegistryUpdateProperties`

## 14.1.0b1 (2025-05-15)

### Other Changes

  - Internal package structure change

## 14.0.0 (2025-04-27)

### Breaking Changes

  - Model Policies no longer has parameter soft_delete_policy
  - Model Registry no longer has parameter auto_generated_domain_name_label_scope
  - Model Registry no longer has parameter metadata_search
  - Model Registry no longer has parameter role_assignment_mode
  - Model RegistryNameCheckRequest no longer has parameter auto_generated_domain_name_label_scope
  - Model RegistryNameCheckRequest no longer has parameter resource_group_name
  - Model RegistryNameStatus no longer has parameter available_login_server_name
  - Model RegistryUpdateParameters no longer has parameter metadata_search
  - Model RegistryUpdateParameters no longer has parameter role_assignment_mode
  - Removed operation RegistriesOperations.get_build_source_upload_url
  - Removed operation RegistriesOperations.schedule_run

## 13.0.0 (2025-04-21)

### Features Added

  - Added operation RegistriesOperations.get_build_source_upload_url
  - Added operation RegistriesOperations.schedule_run
  - Added operation RunsOperations.cancel
  - Added operation RunsOperations.update
  - Added operation TaskRunsOperations.delete
  - Added operation TasksOperations.create
  - Added operation TasksOperations.delete
  - Added operation TasksOperations.update
  - Model Registry has a new parameter role_assignment_mode
  - Model RegistryUpdateParameters has a new parameter role_assignment_mode
  - Model SourceRegistryCredentials has a new parameter identity

### Breaking Changes

  - Removed operation RunsOperations.begin_cancel
  - Removed operation RunsOperations.begin_update
  - Removed operation TaskRunsOperations.begin_delete
  - Removed operation TasksOperations.begin_create
  - Removed operation TasksOperations.begin_delete
  - Removed operation TasksOperations.begin_update

## 12.0.0 (2025-02-24)

### Breaking Changes
  - Removed subfolders of some unused Api-Versions for smaller package size. If your application requires a specific and non-latest Api-Version, it's recommended to pin this package to the previous released version; If your application always only use latest Api-Version, please ignore this change.

## 11.0.0 (2024-02-19)

### Features Added

  - Model ConnectedRegistry has a new parameter garbage_collection
  - Model ConnectedRegistryUpdateParameters has a new parameter garbage_collection
  - Model Registry has a new parameter auto_generated_domain_name_label_scope
  - Model RegistryNameCheckRequest has a new parameter auto_generated_domain_name_label_scope
  - Model RegistryNameCheckRequest has a new parameter resource_group_name
  - Model RegistryNameStatus has a new parameter available_login_server_name

### Breaking Changes

  - Removed operation group BuildStepsOperations
  - Removed operation group BuildTasksOperations
  - Removed operation group BuildsOperations

## 10.3.0 (2023-11-20)

### Features Added

  - Model Registry has a new parameter metadata_search
  - Model RegistryUpdateParameters has a new parameter metadata_search

## 10.2.0 (2023-09-21)

### Features Added

  - Added operation group ArchiveVersionsOperations
  - Added operation group ArchivesOperations

## 10.1.0 (2023-02-15)

### Features Added

  - Added operation group CacheRulesOperations
  - Added operation group CredentialSetsOperations

## 10.0.0 (2022-05-26)

**Features**

  - Model Policies has a new parameter azure_ad_authentication_as_arm_policy
  - Model Policies has a new parameter soft_delete_policy

**Breaking changes**

  - Model NetworkRuleSet no longer has parameter virtual_network_rules

## 9.1.0 (2022-03-03)

**Features**

  - Added operation RegistriesOperations.begin_generate_credentials
  - Model NetworkRuleSet has a new parameter virtual_network_rules
  - Model Registry has a new parameter anonymous_pull_enabled
  - Model RegistryUpdateParameters has a new parameter anonymous_pull_enabled

## 9.0.0 (2022-01-19)

**Features**

  - Added operation RegistriesOperations.get_private_link_resource

**Breaking changes**

  - Model NetworkRuleSet no longer has parameter virtual_network_rules
  - Model Registry no longer has parameter anonymous_pull_enabled
  - Model RegistryUpdateParameters no longer has parameter anonymous_pull_enabled
  - Removed operation RegistriesOperations.begin_generate_credentials

## 8.2.0 (2021-10-26)

**Features**

  - Model ConnectedRegistryUpdateParameters has a new parameter notifications_list
  - Model ConnectedRegistry has a new parameter notifications_list

## 8.1.0 (2021-07-22)

**Features**

  - Model Policies has a new parameter export_policy
  - Model OperationDefinition has a new parameter is_data_action

## 8.0.0 (2021-05-25)

**Features**

  - Model PipelineRun has a new parameter system_data
  - Model TaskRunRequest has a new parameter log_template
  - Model TaskUpdateParameters has a new parameter log_template
  - Model Token has a new parameter system_data
  - Model EncodedTaskRunRequest has a new parameter log_template
  - Model ScopeMap has a new parameter system_data
  - Model AgentPool has a new parameter system_data
  - Model RegistryUpdateParameters has a new parameter anonymous_pull_enabled
  - Model RegistryUpdateParameters has a new parameter network_rule_bypass_options
  - Model ExportPipeline has a new parameter system_data
  - Model KeyVaultProperties has a new parameter key_rotation_enabled
  - Model KeyVaultProperties has a new parameter last_key_rotation_timestamp
  - Model Run has a new parameter log_artifact
  - Model Run has a new parameter system_data
  - Model FileTaskRunRequest has a new parameter log_template
  - Model RunRequest has a new parameter log_template
  - Model OperationServiceSpecificationDefinition has a new parameter log_specifications
  - Model Webhook has a new parameter system_data
  - Model ProxyResource has a new parameter system_data
  - Model TaskRun has a new parameter system_data
  - Model DockerBuildRequest has a new parameter log_template
  - Model Task has a new parameter is_system_task
  - Model Task has a new parameter system_data
  - Model Task has a new parameter log_template
  - Model Registry has a new parameter zone_redundancy
  - Model Registry has a new parameter anonymous_pull_enabled
  - Model Registry has a new parameter system_data
  - Model Registry has a new parameter network_rule_bypass_options
  - Model ImportPipeline has a new parameter system_data
  - Model Resource has a new parameter system_data
  - Model PrivateEndpointConnection has a new parameter system_data
  - Model Replication has a new parameter zone_redundancy
  - Model Replication has a new parameter system_data
  - Added operation group ConnectedRegistriesOperations

**Breaking changes**

  - Parameter type of model QuickBuildRequest is now required
  - Parameter type of model BuildStepProperties is now required
  - Parameter type of model BuildStepPropertiesUpdateParameters is now required
  - Parameter type of model QueueBuildRequest is now required
  - Parameter type of model BuildTaskBuildRequest is now required
  - Model TokenCredentialsProperties no longer has parameter active_directory_object
  - Model Registry no longer has parameter storage_account
  - Removed operation RegistriesOperations.get_build_source_upload_url
  - Removed operation RegistriesOperations.begin_schedule_run

## 8.0.0b1 (2020-10-12)

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

## 3.0.0rc15(2020-9-16)
**Features**

  - Model FileTaskRunRequest has a new parameter log_template
  - Model Run has a new parameter log_artifact
  - Model EncodedTaskRunRequest has a new parameter log_template
  - Model ImportPipeline has a new parameter location
  - Model TaskRunRequest has a new parameter log_template
  - Model Task has a new parameter log_template
  - Model Task has a new parameter is_system_task
  - Model RunRequest has a new parameter log_template
  - Model ExportPipeline has a new parameter location
  - Model TaskUpdateParameters has a new parameter log_template
  - Model TaskRunUpdateParameters has a new parameter location
  - Model DockerBuildRequest has a new parameter log_template

**Breaking changes**

  - Model TaskRun no longer has parameter tags

## 3.0.0rc14(2020-06-15)

**Features**

  - Model RunGetLogResult has a new parameter log_artifact_link

## 3.0.0rc13 (2020-05-15)

**Features**

  - Model Replication has a new parameter region_endpoint_enabled
  - Model ReplicationUpdateParameters has a new parameter region_endpoint_enabled

**Breaking changes**

  - Operation ReplicationsOperations.create has a new signature
  - Operation ReplicationsOperations.update has a new signature
  - Operation ReplicationsOperations.create has a new signature

## 3.0.0rc12(2020-05-06)

**Features**

  - Model Registry has a new parameter public_network_access
  - Model ErrorResponseBody has a new parameter details
  - Model ErrorResponseBody has a new parameter target
  - Model RegistryUpdateParameters has a new parameter public_network_access
  - Added operation group PipelineRunsOperations
  - Added operation group ImportPipelinesOperations
  - Added operation group ExportPipelinesOperations

## 3.0.0rc11 (2020-03-25)

**Breaking changes**

  - Operation PrivateEndpointConnectionsOperations.create_or_update has a new signature
  - Operation PrivateEndpointConnectionsOperations.create_or_update has a new signature

## 3.0.0rc10 (2020-03-11)

**Features**

- Model FileTaskRunRequest has a new parameter agent_pool_name
- Model RunRequest has a new parameter agent_pool_name
- Model RunFilter has a new parameter agent_pool_name
- Model DockerBuildRequest has a new parameter agent_pool_name
- Model TaskRunRequest has a new parameter agent_pool_name
- Model EncodedTaskRunRequest has a new parameter agent_pool_name
- Model TaskUpdateParameters has a new parameter agent_pool_name
- Model Run has a new parameter agent_pool_name
- Model Task has a new parameter agent_pool_name
- Added operation TaskRunsOperations.get_details
- Added operation group AgentPoolsOperations

## 3.0.0rc9 (2020-03-02)

**Features**

  - Model Registry has a new parameter encryption
  - Model Registry has a new parameter data_endpoint_host_names
  - Model Registry has a new parameter private_endpoint_connections
  - Model Registry has a new parameter identity
  - Model Registry has a new parameter data_endpoint_enabled
  - Model TokenCredentialsProperties has a new parameter active_directory_object
  - Model RegistryUpdateParameters has a new parameter identity
  - Model RegistryUpdateParameters has a new parameter data_endpoint_enabled
  - Model RegistryUpdateParameters has a new parameter encryption
  - Added operation RegistriesOperations.list_private_link_resources
  - Added operation group PrivateEndpointConnectionsOperations

**Breaking changes**

  - Model Token no longer has parameter object_id

## 3.0.0rc8 (2020-01-10)

**Features**

  - Added operation group TaskRunsOperations

## 3.0.0rc7 (2019-10-23)

**Bugfixes**

  - Minor fixes in ScopeMaps

## 3.0.0rc6 (2019-10-03)

**Features**

  - Added operation RegistriesOperations.generate_credentials

## 3.0.0rc5 (2019-08-02)

**Bugfixes**

  - Reverting API version back to 2019-05-01

## 3.0.0rc4 (2019-07-10)

**Bugfixes**

  - Fix incorrect default API version from 2019-05-01 to 2017-10-01

## 3.0.0rc3 (2019-07-01)

New preview API version 2019-06-01-preview contains:

**Features**

  - Model BaseImageTriggerUpdateParameters has a new parameter
    update_trigger_payload_type
  - Model BaseImageTriggerUpdateParameters has a new parameter
    update_trigger_endpoint
  - Model RegistryUpdateParameters has a new parameter policies
  - Model Registry has a new parameter policies
  - Model TaskRunRequest has a new parameter
    override_task_step_properties
  - Model BaseImageTrigger has a new parameter
    update_trigger_payload_type
  - Model BaseImageTrigger has a new parameter update_trigger_endpoint
  - Model Run has a new parameter update_trigger_token
  - Added operation RegistriesOperations.get_build_source_upload_url
  - Added operation RegistriesOperations.schedule_run

**Breaking changes**

  - Model RegistryUpdateParameters no longer has parameter
    storage_account
  - Model TaskRunRequest no longer has parameter task_name
  - Model TaskRunRequest no longer has parameter values
  - Model TaskRunRequest has a new required parameter task_id
  - Removed operation RegistriesOperations.list_policies
  - Removed operation RegistriesOperations.generate_credentials
  - Removed operation RegistriesOperations.update_policies

## 3.0.0rc2 (2019-06-12)

**Features**

  - Model Run has a new parameter timer_trigger

**General Breaking changes**

This version uses a next-generation code generator that *might*
introduce breaking changes while using imports. In summary, some modules
were incorrectly visible/importable and have been renamed. This fixed
several issues caused by usage of classes that were not supposed to be
used in the first place.

  - ContainerRegistryManagementClient cannot be imported from
    `azure.mgmt.containerregistry.containerregistry_management_client`
    anymore (import from `azure.mgmt.containerregistry` works like
    before)
  - ContainerRegistryManagementClientConfiguration import has been moved
    from
    `azure.mgmt.containerregistry.containerregistry_management_client`
    to `azure.mgmt.containerregistry`
  - ContainerRegistryManagementClient cannot be imported from
    `azure.mgmt.containerregistry.v20xx_yy_zz.containerregistry_management_client`
    anymore (import from `azure.mgmt.containerregistry.v20xx_yy_zz`
    works like before)
  - ContainerRegistryManagementClientConfiguration import has been moved
    from
    `azure.mgmt.containerregistry.v20xx_yy_zz.containerregistry_management_client`
    to `azure.mgmt.containerregistry.v20xx_yy_zz`
  - A model `MyClass` from a "models" sub-module cannot be imported
    anymore using
    `azure.mgmt.containerregistry.v20xx_yy_zz.models.my_class`
    (import from `azure.mgmt.containerregistry.v20xx_yy_zz.models`
    works like before)
  - An operation class `MyClassOperations` from an `operations`
    sub-module cannot be imported anymore using
    `azure.mgmt.containerregistry.v20xx_yy_zz.operations.my_class_operations`
    (import from
    `azure.mgmt.containerregistry.v20xx_yy_zz.operations` works like
    before)

Last but not least, HTTP connection pooling is now enabled by default.
You should always use a client as a context manager, or call close(), or
use no more than one containerregistry mgmt client per process.

## 3.0.0rc1 (2019-05-24)

**Features**

  - Model Registry has a new parameter policies
  - Model RegistryUpdateParameters has a new parameter policies
  - Add preview ScopeMaps (2019-05-01-preview API version)

**Breaking changes**

  - Model RegistryUpdateParameters no longer has parameter
    storage_account
  - Removed operation RegistriesOperations.update_policies
  - Removed operation RegistriesOperations.list_policies

## 2.8.0 (2019-04-30)

**Features**

  - Model CustomRegistryCredentials has a new parameter identity
  - Model Run has a new parameter run_error_message
  - Model Task has a new parameter identity
  - Model TaskUpdateParameters has a new parameter identity
  - Model Target has a new parameter name
  - Model Target has a new parameter version
  - Model TriggerProperties has a new parameter timer_triggers
  - Model TriggerUpdateParameters has a new parameter timer_triggers

## 2.7.0 (2019-01-25)

**Features**

  - Model Run has a new parameter custom_registries
  - Model Run has a new parameter source_registry_auth
  - Model DockerBuildStepUpdateParameters has a new parameter target
  - Model FileTaskRunRequest has a new parameter credentials
  - Model DockerBuildRequest has a new parameter credentials
  - Model DockerBuildRequest has a new parameter target
  - Model TaskUpdateParameters has a new parameter credentials
  - Model Task has a new parameter credentials
  - Model EncodedTaskRunRequest has a new parameter credentials
  - Model DockerBuildStep has a new parameter target

## 2.6.0 (2019-01-02)

**Features**

  - Add IP rules

**Bugfixes**

  - Rename incorrect "id" to "virtual_network_resource_id"

## 2.5.0 (2018-12-10)

**Features**

  - Add network rule set to registry properties

## 2.4.0 (2018-11-05)

**Features**

  - Add context token to task step

## 2.3.0 (2018-10-17)

  - Support context path, source location URL, and pull request based
    triggers for task/run.
  - Allow specifying credentials for source registry on import image.

## 2.2.0 (2018-09-11)

**Features**

  - Added operation RegistriesOperations.get_build_source_upload_url
  - Added operation RegistriesOperations.schedule_run
  - Added operation group RunsOperations
  - Added operation group TasksOperations

Default API version is now 2018-09-01

## 2.1.0 (2018-07-26)

**Features**

  - Model OperationDefinition has a new parameter service_specification
  - Model OperationDefinition has a new parameter origin
  - Added operation RegistriesOperations.list_policies
  - Added operation RegistriesOperations.update_policies

## 2.0.0 (2018-04-30)

**Features**

  - Support for build steps/taks (ApiVersion 2018-02-01-preview)
  - Support for Azure Profiles
  - Client class can be used as a context manager to keep the underlying
    HTTP session open for performance

**General Breaking changes**

This version uses a next-generation code generator that *might*
introduce breaking changes.

  - Model signatures now use only keyword-argument syntax. All
    positional arguments must be re-written as keyword-arguments. To
    keep auto-completion in most cases, models are now generated for
    Python 2 and Python 3. Python 3 uses the "*" syntax for
    keyword-only arguments.
  - Enum types now use the "str" mixin (class AzureEnum(str, Enum)) to
    improve the behavior when unrecognized enum values are encountered.
    While this is not a breaking change, the distinctions are important,
    and are documented here:
    <https://docs.python.org/3/library/enum.html#others> At a glance:
      - "is" should not be used at all.
      - "format" will return the string value, where "%s" string
        formatting will return `NameOfEnum.stringvalue`. Format syntax
        should be prefered.
  - New Long Running Operation:
      - Return type changes from
        `msrestazure.azure_operation.AzureOperationPoller` to
        `msrest.polling.LROPoller`. External API is the same.
      - Return type is now **always** a `msrest.polling.LROPoller`,
        regardless of the optional parameters used.
      - The behavior has changed when using `raw=True`. Instead of
        returning the initial call result as `ClientRawResponse`,
        without polling, now this returns an LROPoller. After polling,
        the final resource will be returned as a `ClientRawResponse`.
      - New `polling` parameter. The default behavior is
        `Polling=True` which will poll using ARM algorithm. When
        `Polling=False`, the response of the initial call will be
        returned without polling.
      - `polling` parameter accepts instances of subclasses of
        `msrest.polling.PollingMethod`.
      - `add_done_callback` will no longer raise if called after
        polling is finished, but will instead execute the callback right
        away.

**Bugfixes**

  - Compatibility of the sdist with wheel 0.31.0

## 1.0.1 (2017-10-09)

  - Rename Managed_Basic, Managed_Standard, Managed_Premium to Basic,
    Standard, Premium.

## 1.0.0 (2017-09-22)

  - New default API version 2017-10-01.
  - Remove support for API Version 2017-06-01-preview
  - New support for managed registries with three Managed SKUs.
  - New support for registry webhooks and replications.
  - Rename Basic SKU to Classic SKU.

## 0.3.1 (2017-06-30)

  - Support for registry SKU update (2017-06-01-preview)
  - New listUsages API to get the quota usages for a container registry
    (2017-06-01-preview)

## 0.3.0 (2017-06-15)

  - This package now supports an additional ApiVersion
    2017-06-01-preview

## 0.2.1 (2017-04-20)

This wheel package is now built with the azure wheel extension

## 0.2.0 (2017-03-20)

  - New ApiVersion 2017-03-01
  - Update getCredentials to listCredentials to support multiple login
    credentials.
  - Refine regenerateCredential to support regenerate the specified
    login credential.
  - Add Sku to registry properties as a required property.
  - Rename GetProperties to Get.
  - Change CreateOrUpdate to Create, add registry create parameters.

## 0.1.1 (2016-12-12)

**Bugfixes**

  - Fix random error on Create and Delete operation

## 0.1.0 (2016-11-04)

  - Initial Release
