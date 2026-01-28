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
  - Model `DeploymentStacksOperations` added parameter `unmanage_action_resources_without_delete_support` in method `begin_delete_at_management_group`
  - Model `DeploymentStacksOperations` added parameter `unmanage_action_resources_without_delete_support` in method `begin_delete_at_resource_group`
  - Model `DeploymentStacksOperations` added parameter `unmanage_action_resources_without_delete_support` in method `begin_delete_at_subscription`
  - Added model `DeploymentStacksWhatIfResultsAtManagementGroupOperations`
  - Added model `DeploymentStacksWhatIfResultsAtResourceGroupOperations`
  - Added model `DeploymentStacksWhatIfResultsAtSubscriptionOperations`

### Breaking Changes

  - Model `DeploymentStack` deleted or renamed its instance variable `error`
  - Model `DeploymentStack` deleted or renamed its instance variable `template`
  - Model `DeploymentStack` deleted or renamed its instance variable `template_link`
  - Model `DeploymentStack` deleted or renamed its instance variable `parameters`
  - Model `DeploymentStack` deleted or renamed its instance variable `parameters_link`
  - Model `DeploymentStack` deleted or renamed its instance variable `action_on_unmanage`
  - Model `DeploymentStack` deleted or renamed its instance variable `debug_setting`
  - Model `DeploymentStack` deleted or renamed its instance variable `bypass_stack_out_of_sync_error`
  - Model `DeploymentStack` deleted or renamed its instance variable `deployment_scope`
  - Model `DeploymentStack` deleted or renamed its instance variable `description`
  - Model `DeploymentStack` deleted or renamed its instance variable `deny_settings`
  - Model `DeploymentStack` deleted or renamed its instance variable `provisioning_state`
  - Model `DeploymentStack` deleted or renamed its instance variable `correlation_id`
  - Model `DeploymentStack` deleted or renamed its instance variable `detached_resources`
  - Model `DeploymentStack` deleted or renamed its instance variable `deleted_resources`
  - Model `DeploymentStack` deleted or renamed its instance variable `failed_resources`
  - Model `DeploymentStack` deleted or renamed its instance variable `resources`
  - Model `DeploymentStack` deleted or renamed its instance variable `deployment_id`
  - Model `DeploymentStack` deleted or renamed its instance variable `outputs`
  - Model `DeploymentStack` deleted or renamed its instance variable `duration`
  - Deleted or renamed model `AzureResourceBase`
  - Deleted or renamed model `DeploymentStacksError`
  - Deleted or renamed model `UnmanageActionManagementGroupMode`
  - Deleted or renamed model `UnmanageActionResourceGroupMode`
  - Deleted or renamed model `UnmanageActionResourceMode`
  - Method `DeploymentStacksOperations.begin_delete_at_management_group` changed its parameter `unmanage_action_resources` from `positional_or_keyword` to `keyword_only`
  - Method `DeploymentStacksOperations.begin_delete_at_management_group` changed its parameter `unmanage_action_resource_groups` from `positional_or_keyword` to `keyword_only`
  - Method `DeploymentStacksOperations.begin_delete_at_management_group` changed its parameter `unmanage_action_management_groups` from `positional_or_keyword` to `keyword_only`
  - Method `DeploymentStacksOperations.begin_delete_at_management_group` changed its parameter `bypass_stack_out_of_sync_error` from `positional_or_keyword` to `keyword_only`
  - Method `DeploymentStacksOperations.begin_delete_at_resource_group` changed its parameter `unmanage_action_resources` from `positional_or_keyword` to `keyword_only`
  - Method `DeploymentStacksOperations.begin_delete_at_resource_group` changed its parameter `unmanage_action_resource_groups` from `positional_or_keyword` to `keyword_only`
  - Method `DeploymentStacksOperations.begin_delete_at_resource_group` changed its parameter `unmanage_action_management_groups` from `positional_or_keyword` to `keyword_only`
  - Method `DeploymentStacksOperations.begin_delete_at_resource_group` changed its parameter `bypass_stack_out_of_sync_error` from `positional_or_keyword` to `keyword_only`
  - Method `DeploymentStacksOperations.begin_delete_at_subscription` changed its parameter `unmanage_action_resources` from `positional_or_keyword` to `keyword_only`
  - Method `DeploymentStacksOperations.begin_delete_at_subscription` changed its parameter `unmanage_action_resource_groups` from `positional_or_keyword` to `keyword_only`
  - Method `DeploymentStacksOperations.begin_delete_at_subscription` changed its parameter `unmanage_action_management_groups` from `positional_or_keyword` to `keyword_only`
  - Method `DeploymentStacksOperations.begin_delete_at_subscription` changed its parameter `bypass_stack_out_of_sync_error` from `positional_or_keyword` to `keyword_only`

## 1.0.0b1 (2025-06-09)

### Other Changes

  - Initial version
