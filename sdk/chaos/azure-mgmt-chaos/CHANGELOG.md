# Release History

## 2.0.0 (2025-05-19)

### Features Added

  - Model `CapabilityType` added property `required_azure_role_definition_ids`
  - Model `ExperimentExecution` added property `system_data`
  - Model `ExperimentExecutionDetails` added property `properties`
  - Model `Resource` added property `system_data`
  - Model `TrackedResource` added property `system_data`
  - Added enum `ExperimentActionType`
  - Added model `ManagedServiceIdentity`
  - Added enum `ManagedServiceIdentityType`
  - Added model `OperationStatusResult`
  - Added model `ProxyResource`

### Breaking Changes

  - Model `CapabilityType` deleted or renamed its instance variable `location`
  - Model `ExperimentExecutionDetails` deleted or renamed its instance variable `status`
  - Model `ExperimentExecutionDetails` deleted or renamed its instance variable `started_at`
  - Model `ExperimentExecutionDetails` deleted or renamed its instance variable `stopped_at`
  - Model `ExperimentExecutionDetails` deleted or renamed its instance variable `failure_reason`
  - Model `ExperimentExecutionDetails` deleted or renamed its instance variable `last_action_at`
  - Model `ExperimentExecutionDetails` deleted or renamed its instance variable `run_information`
  - Model `TargetType` deleted or renamed its instance variable `location`
  - Deleted or renamed model `ExperimentExecutionProperties`
  - Deleted or renamed model `OperationStatus`
  - Deleted or renamed model `ResourceIdentity`
  - Deleted or renamed model `ResourceIdentityType`
  - Method `CapabilitiesOperations.create_or_update` inserted a `positional_or_keyword` parameter `resource`
  - Method `CapabilitiesOperations.create_or_update` deleted or renamed its parameter `capability` of kind `positional_or_keyword`
  - Method `CapabilityTypesOperations.get` inserted a `positional_or_keyword` parameter `location`
  - Method `CapabilityTypesOperations.get` deleted or renamed its parameter `location_name` of kind `positional_or_keyword`
  - Method `CapabilityTypesOperations.list` inserted a `positional_or_keyword` parameter `location`
  - Method `CapabilityTypesOperations.list` deleted or renamed its parameter `location_name` of kind `positional_or_keyword`
  - Method `ExperimentsOperations.begin_create_or_update` inserted a `positional_or_keyword` parameter `resource`
  - Method `ExperimentsOperations.begin_create_or_update` deleted or renamed its parameter `experiment` of kind `positional_or_keyword`
  - Method `ExperimentsOperations.begin_update` inserted a `positional_or_keyword` parameter `properties`
  - Method `ExperimentsOperations.begin_update` deleted or renamed its parameter `experiment` of kind `positional_or_keyword`
  - Method `OperationStatusesOperations.get` inserted a `positional_or_keyword` parameter `operation_id`
  - Method `OperationStatusesOperations.get` deleted or renamed its parameter `async_operation_id` of kind `positional_or_keyword`
  - Method `TargetTypesOperations.get` inserted a `positional_or_keyword` parameter `location`
  - Method `TargetTypesOperations.get` deleted or renamed its parameter `location_name` of kind `positional_or_keyword`
  - Method `TargetTypesOperations.list` inserted a `positional_or_keyword` parameter `location`
  - Method `TargetTypesOperations.list` deleted or renamed its parameter `location_name` of kind `positional_or_keyword`
  - Method `TargetsOperations.create_or_update` inserted a `positional_or_keyword` parameter `resource`
  - Method `TargetsOperations.create_or_update` deleted or renamed its parameter `target` of kind `positional_or_keyword`
  - Method `CapabilitiesOperations.create_or_update` re-ordered its parameters from `['self', 'resource_group_name', 'parent_provider_namespace', 'parent_resource_type', 'parent_resource_name', 'target_name', 'capability_name', 'capability', 'kwargs']` to `['self', 'resource_group_name', 'parent_provider_namespace', 'parent_resource_type', 'parent_resource_name', 'target_name', 'capability_name', 'resource', 'kwargs']`
  - Method `TargetTypesOperations.get` re-ordered its parameters from `['self', 'location_name', 'target_type_name', 'kwargs']` to `['self', 'location', 'target_type_name', 'kwargs']`
  - Method `TargetTypesOperations.list` re-ordered its parameters from `['self', 'location_name', 'continuation_token_parameter', 'kwargs']` to `['self', 'location', 'continuation_token_parameter', 'kwargs']`
  - Method `OperationStatusesOperations.get` re-ordered its parameters from `['self', 'location', 'async_operation_id', 'kwargs']` to `['self', 'location', 'operation_id', 'kwargs']`
  - Method `TargetsOperations.create_or_update` re-ordered its parameters from `['self', 'resource_group_name', 'parent_provider_namespace', 'parent_resource_type', 'parent_resource_name', 'target_name', 'target', 'kwargs']` to `['self', 'resource_group_name', 'parent_provider_namespace', 'parent_resource_type', 'parent_resource_name', 'target_name', 'resource', 'kwargs']`
  - Method `ExperimentsOperations.begin_update` re-ordered its parameters from `['self', 'resource_group_name', 'experiment_name', 'experiment', 'kwargs']` to `['self', 'resource_group_name', 'experiment_name', 'properties', 'kwargs']`
  - Method `ExperimentsOperations.begin_create_or_update` re-ordered its parameters from `['self', 'resource_group_name', 'experiment_name', 'experiment', 'kwargs']` to `['self', 'resource_group_name', 'experiment_name', 'resource', 'kwargs']`
  - Method `CapabilityTypesOperations.get` re-ordered its parameters from `['self', 'location_name', 'target_type_name', 'capability_type_name', 'kwargs']` to `['self', 'location', 'target_type_name', 'capability_type_name', 'kwargs']`
  - Method `CapabilityTypesOperations.list` re-ordered its parameters from `['self', 'location_name', 'target_type_name', 'continuation_token_parameter', 'kwargs']` to `['self', 'location', 'target_type_name', 'continuation_token_parameter', 'kwargs']`

## 1.1.0 (2024-03-04)

### Features Added

  - Model ExperimentUpdate has a new parameter tags

## 1.0.0 (2023-11-20)

### Features Added

  - Added operation ExperimentsOperations.execution_details
  - Added operation ExperimentsOperations.get_execution
  - Added operation ExperimentsOperations.list_all_executions
  - Added operation group OperationStatusesOperations
  - Model Experiment has a new parameter provisioning_state
  - Model ExperimentExecutionDetails has a new parameter last_action_at
  - Model ExperimentExecutionDetails has a new parameter started_at
  - Model ExperimentExecutionDetails has a new parameter stopped_at

### Breaking Changes

  - Model Experiment no longer has parameter start_on_creation
  - Model ExperimentExecutionDetails no longer has parameter created_date_time
  - Model ExperimentExecutionDetails no longer has parameter experiment_id
  - Model ExperimentExecutionDetails no longer has parameter last_action_date_time
  - Model ExperimentExecutionDetails no longer has parameter start_date_time
  - Model ExperimentExecutionDetails no longer has parameter stop_date_time
  - Removed operation ExperimentsOperations.get_execution_details
  - Removed operation ExperimentsOperations.get_status
  - Removed operation ExperimentsOperations.list_all_statuses
  - Removed operation ExperimentsOperations.list_execution_details
  - Renamed operation ExperimentsOperations.cancel to ExperimentsOperations.begin_cancel
  - Renamed operation ExperimentsOperations.create_or_update to ExperimentsOperations.begin_create_or_update
  - Renamed operation ExperimentsOperations.delete to ExperimentsOperations.begin_delete
  - Renamed operation ExperimentsOperations.start to ExperimentsOperations.begin_start
  - Renamed operation ExperimentsOperations.update to ExperimentsOperations.begin_update

## 1.0.0b7 (2023-08-18)

### Features Added

  - Added operation ExperimentsOperations.update
  - Model CapabilityType has a new parameter azure_rbac_actions
  - Model CapabilityType has a new parameter azure_rbac_data_actions
  - Model ResourceIdentity has a new parameter user_assigned_identities
  - Model Selector has a new parameter additional_properties

### Breaking Changes

  - Model Selector no longer has parameter targets

## 1.0.0b6 (2022-12-14)

### Features Added

  - Model Selector has a new parameter filter

## 1.0.0b5 (2022-08-01)

**Features**

  - Added operation ExperimentsOperations.cancel
  - Added operation ExperimentsOperations.create_or_update
  - Model CapabilityType has a new parameter kind
  - Model CapabilityType has a new parameter runtime_properties

**Breaking changes**

  - Removed operation ExperimentsOperations.begin_cancel
  - Removed operation ExperimentsOperations.begin_create_or_update

## 1.0.0b4 (2022-06-28)

**Features**

  - Model ActionStatus has a new parameter action_id
  - Model ActionStatus has a new parameter action_name
  - Model BranchStatus has a new parameter branch_id
  - Model BranchStatus has a new parameter branch_name
  - Model ExperimentExecutionActionTargetDetailsProperties has a new parameter target_completed_time
  - Model ExperimentExecutionActionTargetDetailsProperties has a new parameter target_failed_time
  - Model ExperimentExecutionDetails has a new parameter created_date_time
  - Model ExperimentExecutionDetails has a new parameter last_action_date_time
  - Model ExperimentExecutionDetails has a new parameter start_date_time
  - Model ExperimentExecutionDetails has a new parameter stop_date_time
  - Model StepStatus has a new parameter step_id
  - Model StepStatus has a new parameter step_name

**Breaking changes**

  - Model ActionStatus no longer has parameter id
  - Model ActionStatus no longer has parameter name
  - Model BranchStatus no longer has parameter id
  - Model BranchStatus no longer has parameter name
  - Model ExperimentExecutionActionTargetDetailsProperties no longer has parameter completed_date_utc
  - Model ExperimentExecutionActionTargetDetailsProperties no longer has parameter failed_date_utc
  - Model ExperimentExecutionDetails no longer has parameter created_date_utc
  - Model ExperimentExecutionDetails no longer has parameter last_action_date_utc
  - Model ExperimentExecutionDetails no longer has parameter start_date_utc
  - Model ExperimentExecutionDetails no longer has parameter stop_date_utc
  - Model StepStatus no longer has parameter id
  - Model StepStatus no longer has parameter name

## 1.0.0b3 (2022-05-07)

**Features**

  - Model ActionStatus has a new parameter end_time
  - Model ActionStatus has a new parameter start_time

## 1.0.0b2 (2021-10-25)

**Features**

  - Modified client name

## 1.0.0b1 (2021-10-21)

* Initial Release
