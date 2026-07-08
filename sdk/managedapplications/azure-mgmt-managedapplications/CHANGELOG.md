# Release History

## 1.0.0b2 (2026-07-08)

### Features Added

  - Client `ManagedApplicationsMgmtClient` added parameter `cloud_setting` in method `__init__`
  - Client `ManagedApplicationsMgmtClient` added method `portal_registry_package`
  - Client `ManagedApplicationsMgmtClient` added method `send_request`
  - Model `Application` added property `properties`
  - Model `ApplicationDefinition` added property `properties`
  - Model `ApplicationPatchable` added property `properties`
  - Model `JitRequestDefinition` added property `properties`
  - Added model `ApplicationDefinitionProperties`
  - Added model `ApplicationProperties`
  - Added model `JitRequestProperties`
  - Added model `RegistryPackage`
  - Added model `RegistryPackageLinks`
  - Added model `RegistryPackagePlan`

### Breaking Changes

  - Model `Application` deleted or renamed its instance variable `managed_resource_group_id`
  - Model `Application` deleted or renamed its instance variable `application_definition_id`
  - Model `Application` deleted or renamed its instance variable `parameters`
  - Model `Application` deleted or renamed its instance variable `outputs`
  - Model `Application` deleted or renamed its instance variable `provisioning_state`
  - Model `Application` deleted or renamed its instance variable `billing_details`
  - Model `Application` deleted or renamed its instance variable `jit_access_policy`
  - Model `Application` deleted or renamed its instance variable `publisher_tenant_id`
  - Model `Application` deleted or renamed its instance variable `authorizations`
  - Model `Application` deleted or renamed its instance variable `management_mode`
  - Model `Application` deleted or renamed its instance variable `customer_support`
  - Model `Application` deleted or renamed its instance variable `support_urls`
  - Model `Application` deleted or renamed its instance variable `artifacts`
  - Model `Application` deleted or renamed its instance variable `created_by`
  - Model `Application` deleted or renamed its instance variable `updated_by`
  - Model `ApplicationDefinition` deleted or renamed its instance variable `lock_level`
  - Model `ApplicationDefinition` deleted or renamed its instance variable `display_name`
  - Model `ApplicationDefinition` deleted or renamed its instance variable `is_enabled`
  - Model `ApplicationDefinition` deleted or renamed its instance variable `authorizations`
  - Model `ApplicationDefinition` deleted or renamed its instance variable `artifacts`
  - Model `ApplicationDefinition` deleted or renamed its instance variable `description`
  - Model `ApplicationDefinition` deleted or renamed its instance variable `package_file_uri`
  - Model `ApplicationDefinition` deleted or renamed its instance variable `storage_account_id`
  - Model `ApplicationDefinition` deleted or renamed its instance variable `main_template`
  - Model `ApplicationDefinition` deleted or renamed its instance variable `create_ui_definition`
  - Model `ApplicationDefinition` deleted or renamed its instance variable `notification_policy`
  - Model `ApplicationDefinition` deleted or renamed its instance variable `locking_policy`
  - Model `ApplicationDefinition` deleted or renamed its instance variable `deployment_policy`
  - Model `ApplicationDefinition` deleted or renamed its instance variable `management_policy`
  - Model `ApplicationDefinition` deleted or renamed its instance variable `policies`
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
  - Deleted or renamed model `ApplicationDefinitionListResult`
  - Deleted or renamed model `ApplicationListResult`
  - Deleted or renamed model `OperationListResult`
  - Deleted or renamed model `ManagedApplicationsMgmtClientOperationsMixin`
  - Method `ApplicationsOperations.begin_update` changed return type from `AsyncLROPoller[ApplicationPatchable]` to `AsyncLROPoller[Application]`
  - Method `ApplicationsOperations.begin_update_by_id` changed return type from `AsyncLROPoller[ApplicationPatchable]` to `AsyncLROPoller[Application]`
  - Method `ApplicationsOperations.begin_update` changed return type from `LROPoller[ApplicationPatchable]` to `LROPoller[Application]`
  - Method `ApplicationsOperations.begin_update_by_id` changed return type from `LROPoller[ApplicationPatchable]` to `LROPoller[Application]`

## 1.0.0b1 (2023-09-20)

* Initial Release
