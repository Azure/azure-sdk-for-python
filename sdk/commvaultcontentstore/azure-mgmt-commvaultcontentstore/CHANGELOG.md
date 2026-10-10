# Release History

## 1.0.0b2 (2026-10-07)

### Features Added

  - Model `CloudAccountProperties` added property `company`
  - Model `CloudAccountProperties` added property `role_assignments_on_cca_create`
  - Model `StorageProperties` added property `compliance_lock_status`
  - Added model `ActivateSaaSRequestParam`
  - Added model `CompanyProfile`
  - Added enum `ComplianceLockStatus`
  - Operation group `StoragesOperations` added method `disable_compliance_lock`
  - Operation group `StoragesOperations` added method `enable_compliance_lock`
  - Operation group `StoragesOperations` added method `refresh`

### Breaking Changes

  - Model `ActivateSaaSParameterRequest` renamed its instance variable `saa_s_guid` to `saas_guid`
  - Model `CloudAccountProperties` deleted or renamed its instance variable `backup_admin_on_cca_create`
  - Model `CloudAccountProperties` deleted or renamed its instance variable `multi_person_authorization_on_cca_create`
  - `ProtectionGroupProperties.last_back_up_time` is now required.
  - `ProtectionGroupProperties.number_of_protected_items` is now required.
  - `ProtectionGroupProperties.protection_status` is now required.
  - `RoleAssignment.entities` is now required.
  - `RoleAssignment.role_name` is now required.
  - Deleted or renamed model `CloudAccountUpdate`
  - Deleted or renamed model `CloudAccountUpdateProperties`
  - Method `CloudAccountsOperations.begin_update` changed type of its parameter `properties` from `CloudAccountUpdate` to `CloudAccount`

## 1.0.0b1 (2026-06-25)

### Other Changes

  - Initial version
