# Release History

## 1.0.0 (2026-01-28)

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
  - Added enum `DeploymentStacksResourcesWithoutDeleteSupportEnum`
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
  - Added enum `ValidationLevel`
  - Method `DeploymentStacksOperations.begin_delete_at_management_group` added parameter `unmanage_action_resources_without_delete_support`
  - Method `DeploymentStacksOperations.begin_delete_at_resource_group` added parameter `unmanage_action_resources_without_delete_support`
  - Method `DeploymentStacksOperations.begin_delete_at_subscription` added parameter `unmanage_action_resources_without_delete_support`
  - Added operation group `DeploymentStacksWhatIfResultsAtManagementGroupOperations`
  - Added operation group `DeploymentStacksWhatIfResultsAtResourceGroupOperations`
  - Added operation group `DeploymentStacksWhatIfResultsAtSubscriptionOperations`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. And please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration. 
  - For the method breakings, please refer to https://aka.ms/azsdk/python/migrate/operations for migration. 
  - Model `DeploymentStack` moved instance variable `error`/`template`/`template_link`/`parameters`/`parameters_link`/`action_on_unmanage`/`debug_setting`/`bypass_stack_out_of_sync_error`/`deployment_scope`/`description`/`deny_settings`/`provisioning_state`/`correlation_id`/`detached_resources`/`deleted_resources`/`failed_resources`/`resources`/`deployment_id`/`outputs`/`duration` under property `properties`
  - Method `DeploymentStacksOperations.begin_delete_at_management_group` changed its parameter `unmanage_action_resources`/`unmanage_action_resource_groups`/`unmanage_action_management_groups`/`bypass_stack_out_of_sync_error` from `positional_or_keyword` to `keyword_only`
  - Method `DeploymentStacksOperations.begin_delete_at_resource_group` changed its parameter `unmanage_action_resources`/`unmanage_action_resource_groups`/`unmanage_action_management_groups`/`bypass_stack_out_of_sync_error` from `positional_or_keyword` to `keyword_only`
  - Method `DeploymentStacksOperations.begin_delete_at_subscription` changed its parameter `unmanage_action_resources`/`unmanage_action_resource_groups`/`unmanage_action_management_groups`/`bypass_stack_out_of_sync_error` from `positional_or_keyword` to `keyword_only`
  - Replaced enum `UnmanageActionManagementGroupMode`/`UnmanageActionResourceGroupMode`/`UnmanageActionResourceMode` with enum `DeploymentStacksDeleteDetachEnum`

### Other Changes

  - Deleted model `AzureResourceBase`/`DeploymentStacksError` which actually were not used by SDK users

## 1.0.0b1 (2025-06-09)

### Other Changes

  - Initial version
