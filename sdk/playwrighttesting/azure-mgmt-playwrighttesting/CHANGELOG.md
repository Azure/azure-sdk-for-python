# Release History

## 1.0.0 (2024-12-16)

### Features Added

  - Client `PlaywrightTestingMgmtClient` added operation group `account_quotas`
  - Model `AccountProperties` added property `local_auth`
  - Model `AccountUpdateProperties` added property `local_auth`
  - Enum `FreeTrialState` added member `NOT_ELIGIBLE`
  - Enum `FreeTrialState` added member `NOT_REGISTERED`
  - Enum `ProvisioningState` added member `CREATING`
  - Enum `QuotaNames` added member `REPORTING`
  - Model `QuotaProperties` added property `offering_type`
  - Added model `AccountFreeTrialProperties`
  - Added model `AccountQuota`
  - Added model `AccountQuotaListResult`
  - Added model `AccountQuotaProperties`
  - Added enum `CheckNameAvailabilityReason`
  - Added model `CheckNameAvailabilityRequest`
  - Added model `CheckNameAvailabilityResponse`
  - Added enum `OfferingType`
  - Operation group `AccountsOperations` added method `check_name_availability`
  - Added operation group `AccountQuotasOperations`

### Breaking Changes

  - Model `FreeTrialProperties` deleted or renamed its instance variable `created_at`
  - Model `FreeTrialProperties` deleted or renamed its instance variable `expiry_at`
  - Model `FreeTrialProperties` deleted or renamed its instance variable `allocated_value`
  - Model `FreeTrialProperties` deleted or renamed its instance variable `used_value`
  - Model `FreeTrialProperties` deleted or renamed its instance variable `percentage_used`
  - Method `AccountsOperations.begin_create_or_update` renamed its parameter `name` to `account_name`
  - Method `AccountsOperations.begin_delete` renamed its parameter `name` to `account_name`
  - Method `AccountsOperations.get` renamed its parameter `name` to `account_name`
  - Method `AccountsOperations.update` renamed its parameter `name` to `account_name`
  - Method `QuotasOperations.get` renamed its parameter `name` to `quota_name`

## 1.0.0b2 (2024-03-04)

### Features Added

  - Model Account has a new parameter properties
  - Model AccountUpdate has a new parameter properties
  - Model Quota has a new parameter properties

### Breaking Changes

  - Model Account no longer has parameter dashboard_uri
  - Model Account no longer has parameter provisioning_state
  - Model Account no longer has parameter regional_affinity
  - Model Account no longer has parameter reporting
  - Model Account no longer has parameter scalable_execution
  - Model AccountUpdate no longer has parameter regional_affinity
  - Model AccountUpdate no longer has parameter reporting
  - Model AccountUpdate no longer has parameter scalable_execution
  - Model Quota no longer has parameter free_trial
  - Model Quota no longer has parameter provisioning_state

## 1.0.0b1 (2023-09-27)

* Initial Release
