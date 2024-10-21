# Release History

## 1.0.0 (2024-11-18)

### Features Added

  - Enum `ManagedServiceIdentityType` added member `SYSTEM_ASSIGNED_USER_ASSIGNED`
  - Enum `OsDiskStorageAccountType` added member `STANDARD_SSD`
  - Model `Quota` added property `unit`
  - Model `Quota` added property `current_value`
  - Model `Quota` added property `limit`
  - Model `SubscriptionUsagesOperations` added method `usages`

### Breaking Changes

  - Deleted or renamed enum value `ManagedServiceIdentityType.SYSTEM_AND_USER_ASSIGNED`
  - Deleted or renamed enum value `OsDiskStorageAccountType.STANDARD_S_S_D`
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
