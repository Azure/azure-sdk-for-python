# Release History

## 1.1.0b1 (2026-07-23)

### Features Added

  - Client `DevOpsInfrastructureMgmtClient` added parameter `cloud_setting` in method `__init__`
  - Model `AzureDevOpsOrganizationProfile` added property `description`
  - Model `AzureDevOpsOrganizationProfile` added property `update_description`
  - Model `AzureDevOpsOrganizationProfile` added property `alias`
  - Model `DevOpsAzureSku` added property `windows_nvme_drive`
  - Model `DevOpsAzureSku` added property `linux_nvme_path`
  - Model `DevOpsAzureSku` added property `vm_sizes`
  - Model `NetworkProfile` added property `static_ip_address_count`
  - Model `NetworkProfile` added property `ip_addresses`
  - Model `Organization` added property `open_access`
  - Model `Organization` added property `alias`
  - Model `PoolImage` added property `ephemeral_type`
  - Model `PoolImage` added property `is_ephemeral`
  - Model `PoolImage` added property `provisioning_script_storage_account_resource_id`
  - Model `PoolImage` added property `provisioning_script_managed_identity_client_id`
  - Model `PoolImage` added property `provisioning_script_should_restart`
  - Model `PoolImage` added property `provisioning_script_entry_point`
  - Model `PoolProperties` added property `runtime_configuration`
  - Model `PoolUpdateProperties` added property `runtime_configuration`
  - Model `SecretsManagementSettings` added property `certificate_store_name`
  - Added enum `ActionType`
  - Added enum `AvailabilityStatus`
  - Added enum `CertificateStoreNameOption`
  - Added model `CheckNameAvailability`
  - Added enum `CheckNameAvailabilityReason`
  - Added model `CheckNameAvailabilityResult`
  - Added model `DeleteResourcesDetails`
  - Added enum `DevOpsInfrastructureResourceType`
  - Added enum `EphemeralType`
  - Added model `Operation`
  - Added model `OperationDisplay`
  - Added enum `Origin`
  - Added model `RuntimeConfiguration`
  - Added model `VmSize`
  - Operation group `PoolsOperations` added method `check_name_availability`
  - Operation group `PoolsOperations` added method `delete_resources`

## 1.0.0 (2024-11-21)

### Features Added

  - Model `Quota` added property `unit`
  - Model `Quota` added property `current_value`
  - Model `Quota` added property `limit`
  - Operation group `SubscriptionUsagesOperations` added method `usages`

### Breaking Changes

  - Enum `ManagedServiceIdentityType` renamed its value `SYSTEM_AND_USER_ASSIGNED` to `SYSTEM_ASSIGNED_USER_ASSIGNED`
  - Enum `OsDiskStorageAccountType` renamed its value `STANDARD_S_S_D` to `STANDARD_SSD`
  - Model `Quota` deleted or renamed its instance variable `properties`
  - Model `Quota` deleted or renamed its instance variable `type`
  - Model `Quota` deleted or renamed its instance variable `system_data`
  - Deleted or renamed enum value `StorageAccountType.PREMIUM_L_R_S`
  - Deleted or renamed enum value `StorageAccountType.PREMIUM_Z_R_S`
  - Deleted or renamed enum value `StorageAccountType.STANDARD_L_R_S`
  - Deleted or renamed enum value `StorageAccountType.STANDARD_S_S_D_L_R_S`
  - Deleted or renamed enum value `StorageAccountType.STANDARD_S_S_D_Z_R_S`
  - Deleted or renamed model `ActionType`
  - Deleted or renamed model `Operation`
  - Deleted or renamed model `OperationDisplay`
  - Deleted or renamed model `Origin`
  - Deleted or renamed model `QuotaProperties`
  - Deleted or renamed method `SubscriptionUsagesOperations.list_by_location`

## 1.0.0b1 (2024-05-29)

- Initial version
