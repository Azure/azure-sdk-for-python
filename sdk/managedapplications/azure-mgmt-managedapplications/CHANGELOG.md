# Release History

## 1.0.0b2 (2026-04-02)

### Features Added

  - Client `ApplicationClient` added method `portal_registry_package`
  - Client `ApplicationClient` added method `send_request`
  - Client `ApplicationClient` added operation group `operations`
  - Model `ApplicationPatchable` added property `properties`
  - Model `JitRequestDefinition` added property `properties`
  - Added model `JitRequestProperties`
  - Added model `RegistryPackage`
  - Added model `RegistryPackageLinks`
  - Added model `RegistryPackagePlan`
  - Added model `Operations`
  - Added model `jitRequestsOperations`

### Breaking Changes

  - Deleted or renamed client method `ApplicationClient.list_operations`
  - Method `ApplicationsOperations.list_allowed_upgrade_plans` changed from `asynchronous` to `synchronous`
  - Method `ApplicationsOperations.list_tokens` changed from `asynchronous` to `synchronous`
  - Model `ApplicationPatchable` deleted or renamed its instance variable `managed_resource_group_id`
  - Model `ApplicationPatchable` deleted or renamed its instance variable `application_definition_id`
  - Model `ApplicationPatchable` deleted or renamed its instance variable `parameters`
  - Model `ApplicationPatchable` deleted or renamed its instance variable `outputs`
  - Model `ApplicationPatchable` deleted or renamed its instance variable `provisioning_state`
  - Model `ApplicationPatchable` deleted or renamed its instance variable `billing_details`
  - Model `ApplicationPatchable` deleted or renamed its instance variable `jit_access_policy`
  - Model `ApplicationPatchable` deleted or renamed its instance variable `publisher_tenant_id`
  - Model `ApplicationPatchable` deleted or renamed its instance variable `authorizations`
  - Model `ApplicationPatchable` deleted or renamed its instance variable `management_mode`
  - Model `ApplicationPatchable` deleted or renamed its instance variable `customer_support`
  - Model `ApplicationPatchable` deleted or renamed its instance variable `support_urls`
  - Model `ApplicationPatchable` deleted or renamed its instance variable `artifacts`
  - Model `ApplicationPatchable` deleted or renamed its instance variable `created_by`
  - Model `ApplicationPatchable` deleted or renamed its instance variable `updated_by`
  - Model `JitRequestDefinition` deleted or renamed its instance variable `application_resource_id`
  - Model `JitRequestDefinition` deleted or renamed its instance variable `publisher_tenant_id`
  - Model `JitRequestDefinition` deleted or renamed its instance variable `jit_authorization_policies`
  - Model `JitRequestDefinition` deleted or renamed its instance variable `jit_scheduling_policy`
  - Model `JitRequestDefinition` deleted or renamed its instance variable `provisioning_state`
  - Model `JitRequestDefinition` deleted or renamed its instance variable `jit_request_state`
  - Model `JitRequestDefinition` deleted or renamed its instance variable `created_by`
  - Model `JitRequestDefinition` deleted or renamed its instance variable `updated_by`
  - Deleted or renamed model `AllowedUpgradePlansResult`
  - Deleted or renamed model `ManagedIdentityTokenResult`
  - Deleted or renamed method `ApplicationDefinitionsOperations.create_or_update_by_id`
  - Deleted or renamed method `ApplicationDefinitionsOperations.delete_by_id`
  - Deleted or renamed method `ApplicationDefinitionsOperations.get_by_id`
  - Deleted or renamed method `ApplicationDefinitionsOperations.update_by_id`
  - Deleted or renamed model `JitRequestsOperations`

## 1.0.0b1 (2023-09-20)

* Initial Release
