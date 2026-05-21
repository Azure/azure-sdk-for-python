# Release History

## 2.0.0b1 (2026-05-21)

### Breaking Changes

  - Deleted or renamed client operation group `DeploymentStacksClient.deployment_stacks_what_if_results_at_resource_group`
  - Deleted or renamed client operation group `DeploymentStacksClient.deployment_stacks_what_if_results_at_subscription`
  - Deleted or renamed client operation group `DeploymentStacksClient.deployment_stacks_what_if_results_at_management_group`
  - Model `ActionOnUnmanage` deleted or renamed its instance variable `resources_without_delete_support`
  - Deleted or renamed enum value `DenyStatusMode.UNKNOWN`
  - Model `DeploymentParameter` deleted or renamed its instance variable `expression`
  - Model `DeploymentStackProperties` deleted or renamed its instance variable `extension_configs`
  - Model `DeploymentStackProperties` deleted or renamed its instance variable `external_inputs`
  - Model `DeploymentStackProperties` deleted or renamed its instance variable `external_input_definitions`
  - Model `DeploymentStackProperties` deleted or renamed its instance variable `validation_level`
  - Model `DeploymentStackProperties` deleted or renamed its instance variable `deployment_extensions`
  - Deleted or renamed enum value `DeploymentStackProvisioningState.INITIALIZING`
  - Deleted or renamed enum value `DeploymentStackProvisioningState.RUNNING`
  - Model `DeploymentStackValidateProperties` deleted or renamed its instance variable `deployment_extensions`
  - Model `DeploymentStackValidateProperties` deleted or renamed its instance variable `validation_level`
  - Model `ManagedResourceReference` deleted or renamed its instance variable `extension`
  - Model `ManagedResourceReference` deleted or renamed its instance variable `type`
  - Model `ManagedResourceReference` deleted or renamed its instance variable `identifiers`
  - Model `ManagedResourceReference` deleted or renamed its instance variable `api_version`
  - Model `ResourceReference` deleted or renamed its instance variable `extension`
  - Model `ResourceReference` deleted or renamed its instance variable `type`
  - Model `ResourceReference` deleted or renamed its instance variable `identifiers`
  - Model `ResourceReference` deleted or renamed its instance variable `api_version`
  - Model `ResourceReferenceExtended` deleted or renamed its instance variable `extension`
  - Model `ResourceReferenceExtended` deleted or renamed its instance variable `type`
  - Model `ResourceReferenceExtended` deleted or renamed its instance variable `identifiers`
  - Model `ResourceReferenceExtended` deleted or renamed its instance variable `api_version`
  - Deleted or renamed model `DeploymentExtension`
  - Deleted or renamed model `DeploymentExtensionConfig`
  - Deleted or renamed model `DeploymentExtensionConfigItem`
  - Deleted or renamed model `DeploymentExternalInput`
  - Deleted or renamed model `DeploymentExternalInputDefinition`
  - Deleted or renamed model `DeploymentStacksChangeBase`
  - Deleted or renamed model `DeploymentStacksChangeBaseDenyStatusMode`
  - Deleted or renamed model `DeploymentStacksChangeBaseDeploymentStacksManagementStatus`
  - Deleted or renamed model `DeploymentStacksChangeDeltaDenySettings`
  - Deleted or renamed model `DeploymentStacksChangeDeltaRecord`
  - Deleted or renamed model `DeploymentStacksDiagnostic`
  - Deleted or renamed model `DeploymentStacksDiagnosticLevel`
  - Deleted or renamed model `DeploymentStacksManagementStatus`
  - Deleted or renamed model `DeploymentStacksWhatIfChange`
  - Deleted or renamed model `DeploymentStacksWhatIfChangeCertainty`
  - Deleted or renamed model `DeploymentStacksWhatIfChangeType`
  - Deleted or renamed model `DeploymentStacksWhatIfPropertyChange`
  - Deleted or renamed model `DeploymentStacksWhatIfPropertyChangeType`
  - Deleted or renamed model `DeploymentStacksWhatIfResourceChange`
  - Deleted or renamed model `DeploymentStacksWhatIfResult`
  - Deleted or renamed model `DeploymentStacksWhatIfResultProperties`
  - Deleted or renamed model `ResourcesWithoutDeleteSupportAction`
  - Deleted or renamed model `ValidationLevel`
  - Deleted or renamed model `DeploymentStacksWhatIfResultsAtManagementGroupOperations`
  - Deleted or renamed model `DeploymentStacksWhatIfResultsAtResourceGroupOperations`
  - Deleted or renamed model `DeploymentStacksWhatIfResultsAtSubscriptionOperations`

## 1.0.0 (2026-02-10)

### Features Added

  - Model `DeploymentStacksClient` added parameter `cloud_setting` in method `__init__`
  - Client `DeploymentStacksClient` added method `send_request`
  - Client `DeploymentStacksClient` added operation group `deployment_stacks_what_if_results_at_resource_group`
  - Client `DeploymentStacksClient` added operation group `deployment_stacks_what_if_results_at_subscription`
  - Client `DeploymentStacksClient` added operation group `deployment_stacks_what_if_results_at_management_group`
  - Model `ActionOnUnmanage` added property `resources_without_delete_support`
  - Enum `DenyStatusMode` added member `UNKNOWN`
  - Model `DeploymentParameter` added property `expression`
  - Model `DeploymentStack` added property `properties`
  - Model `DeploymentStackProperties` added property `extension_configs`
  - Model `DeploymentStackProperties` added property `external_inputs`
  - Model `DeploymentStackProperties` added property `external_input_definitions`
  - Model `DeploymentStackProperties` added property `validation_level`
  - Model `DeploymentStackProperties` added property `deployment_extensions`
  - Enum `DeploymentStackProvisioningState` added member `INITIALIZING`
  - Enum `DeploymentStackProvisioningState` added member `RUNNING`
  - Model `DeploymentStackValidateProperties` added property `deployment_extensions`
  - Model `DeploymentStackValidateProperties` added property `validation_level`
  - Model `ManagedResourceReference` added property `extension`
  - Model `ManagedResourceReference` added property `type`
  - Model `ManagedResourceReference` added property `identifiers`
  - Model `ManagedResourceReference` added property `api_version`
  - Model `ResourceReference` added property `extension`
  - Model `ResourceReference` added property `type`
  - Model `ResourceReference` added property `identifiers`
  - Model `ResourceReference` added property `api_version`
  - Model `ResourceReferenceExtended` added property `extension`
  - Model `ResourceReferenceExtended` added property `type`
  - Model `ResourceReferenceExtended` added property `identifiers`
  - Model `ResourceReferenceExtended` added property `api_version`
  - Added model `DeploymentExtension`
  - Added model `DeploymentExtensionConfig`
  - Added model `DeploymentExtensionConfigItem`
  - Added model `DeploymentExternalInput`
  - Added model `DeploymentExternalInputDefinition`
  - Added model `DeploymentStacksChangeBase`
  - Added model `DeploymentStacksChangeBaseDenyStatusMode`
  - Added model `DeploymentStacksChangeBaseDeploymentStacksManagementStatus`
  - Added model `DeploymentStacksChangeDeltaDenySettings`
  - Added model `DeploymentStacksChangeDeltaRecord`
  - Added model `DeploymentStacksDiagnostic`
  - Added enum `DeploymentStacksDiagnosticLevel`
  - Added enum `DeploymentStacksManagementStatus`
  - Added model `DeploymentStacksWhatIfChange`
  - Added enum `DeploymentStacksWhatIfChangeCertainty`
  - Added enum `DeploymentStacksWhatIfChangeType`
  - Added model `DeploymentStacksWhatIfPropertyChange`
  - Added enum `DeploymentStacksWhatIfPropertyChangeType`
  - Added model `DeploymentStacksWhatIfResourceChange`
  - Added model `DeploymentStacksWhatIfResult`
  - Added model `DeploymentStacksWhatIfResultProperties`
  - Added model `ErrorResponse`
  - Added model `ProxyResource`
  - Added model `Resource`
  - Added enum `ResourcesWithoutDeleteSupportAction`
  - Added enum `ValidationLevel`
  - Method `DeploymentStacksOperations.begin_delete_at_management_group` added parameter `unmanage_action_resources_without_delete_support`
  - Method `DeploymentStacksOperations.begin_delete_at_resource_group` added parameter `unmanage_action_resources_without_delete_support`
  - Method `DeploymentStacksOperations.begin_delete_at_subscription` added parameter `unmanage_action_resources_without_delete_support`
  - Added operation group `DeploymentStacksWhatIfResultsAtManagementGroupOperations`
  - Added operation group `DeploymentStacksWhatIfResultsAtResourceGroupOperations`
  - Added operation group `DeploymentStacksWhatIfResultsAtSubscriptionOperations`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. Please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - For the method breakings, please refer to https://aka.ms/azsdk/python/migrate/operations for migration.
  - Deleted or renamed model `DeploymentStacksDeleteDetachEnum`
  - Model `DeploymentStack` moved instance variable `error`, `template`, `template_link`, `parameters`, `parameters_link`, `action_on_unmanage`, `debug_setting`, `bypass_stack_out_of_sync_error`, `deployment_scope`, `description`, `deny_settings`, `provisioning_state`, `correlation_id`, `detached_resources`, `deleted_resources`, `failed_resources`, `resources`, `deployment_id`, `outputs` and `duration` under property `properties`
  - Method `DeploymentStacksOperations.begin_delete_at_management_group` changed its parameter `unmanage_action_resources`/`unmanage_action_resource_groups`/`unmanage_action_management_groups`/`bypass_stack_out_of_sync_error` from `positional_or_keyword` to `keyword_only`
  - Method `DeploymentStacksOperations.begin_delete_at_resource_group` changed its parameter `unmanage_action_resources`/`unmanage_action_resource_groups`/`unmanage_action_management_groups`/`bypass_stack_out_of_sync_error` from `positional_or_keyword` to `keyword_only`
  - Method `DeploymentStacksOperations.begin_delete_at_subscription` changed its parameter `unmanage_action_resources`/`unmanage_action_resource_groups`/`unmanage_action_management_groups`/`bypass_stack_out_of_sync_error` from `positional_or_keyword` to `keyword_only`

### Other Changes

  - Deleted model `AzureResourceBase`/`DeploymentStacksError` which actually were not used by SDK users

## 1.0.0b1 (2025-06-09)

### Other Changes

  - Initial version
