# Release History

## 1.0.0b2 (2026-07-08)

### Features Added

  - Client `ManagedApplicationsMgmtClient` added parameter `cloud_setting` in method `__init__`
  - Client `ManagedApplicationsMgmtClient` added method `portal_registry_package`
  - Client `ManagedApplicationsMgmtClient` added method `send_request`
  - Added model `RegistryPackage`
  - Added model `RegistryPackageLinks`
  - Added model `RegistryPackagePlan`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. Please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - Model `Application` moved instance variable `managed_resource_group_id`, `application_definition_id`, `parameters`, `outputs`, `provisioning_state`, `billing_details`, `jit_access_policy`, `publisher_tenant_id`, `authorizations`, `management_mode`, `customer_support`, `support_urls`, `artifacts`, `created_by` and `updated_by` under property `properties` whose type is `ApplicationProperties`
  - Model `ApplicationDefinition` moved instance variable `lock_level`, `display_name`, `is_enabled`, `authorizations`, `artifacts`, `description`, `package_file_uri`, `storage_account_id`, `main_template`, `create_ui_definition`, `notification_policy`, `locking_policy`, `deployment_policy`, `management_policy` and `policies` under property `properties` whose type is `ApplicationDefinitionProperties`
  - Model `ApplicationPatchable` moved instance variable `managed_resource_group_id`, `application_definition_id`, `parameters`, `outputs`, `provisioning_state`, `billing_details`, `jit_access_policy`, `publisher_tenant_id`, `authorizations`, `management_mode`, `customer_support`, `support_urls`, `artifacts`, `created_by` and `updated_by` under property `properties` whose type is `ApplicationProperties`
  - Model `JitRequestDefinition` moved instance variable `application_resource_id`, `publisher_tenant_id`, `jit_authorization_policies`, `jit_scheduling_policy`, `provisioning_state`, `jit_request_state`, `created_by` and `updated_by` under property `properties` whose type is `JitRequestProperties`
  - Deleted or renamed operation group `ManagedApplicationsMgmtClientOperationsMixin`
  - Method `ApplicationsOperations.begin_update` changed return type from `LROPoller[ApplicationPatchable]` to `LROPoller[Application]`
  - Method `ApplicationsOperations.begin_update_by_id` changed return type from `LROPoller[ApplicationPatchable]` to `LROPoller[Application]`

### Other Changes

  - Deleted model `ApplicationDefinitionListResult`/`ApplicationListResult`/`OperationListResult` which actually were not used by SDK users

## 1.0.0b1 (2023-09-20)

* Initial Release
