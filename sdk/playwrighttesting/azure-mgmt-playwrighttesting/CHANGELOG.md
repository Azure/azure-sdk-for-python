# Release History

## 1.0.0 (2024-12-22)

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
  - Model `AccountsOperations` added method `check_name_availability`
  - Added model `AccountQuotasOperations`
  - Method `AccountsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, account_name: str, resource: Account, content_type: str)`
  - Method `AccountsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, account_name: str, resource: IO[bytes], content_type: str)`
  - Method `AccountsOperations.update` has a new overload `def update(self: None, resource_group_name: str, account_name: str, properties: AccountUpdate, content_type: str)`
  - Method `AccountsOperations.update` has a new overload `def update(self: None, resource_group_name: str, account_name: str, properties: IO[bytes], content_type: str)`
  - Method `AccountsOperations.check_name_availability` has a new overload `def check_name_availability(self: None, body: CheckNameAvailabilityRequest, content_type: str)`
  - Method `AccountsOperations.check_name_availability` has a new overload `def check_name_availability(self: None, body: IO[bytes], content_type: str)`

### Breaking Changes

  - Model `FreeTrialProperties` deleted or renamed its instance variable `created_at`
  - Model `FreeTrialProperties` deleted or renamed its instance variable `expiry_at`
  - Model `FreeTrialProperties` deleted or renamed its instance variable `allocated_value`
  - Model `FreeTrialProperties` deleted or renamed its instance variable `used_value`
  - Model `FreeTrialProperties` deleted or renamed its instance variable `percentage_used`
  - Method `AccountsOperations.begin_create_or_update` inserted a `positional_or_keyword` parameter `account_name`
  - Method `AccountsOperations.begin_create_or_update` deleted or renamed its parameter `name` of kind `positional_or_keyword`
  - Method `AccountsOperations.begin_delete` inserted a `positional_or_keyword` parameter `account_name`
  - Method `AccountsOperations.begin_delete` deleted or renamed its parameter `name` of kind `positional_or_keyword`
  - Method `AccountsOperations.get` inserted a `positional_or_keyword` parameter `account_name`
  - Method `AccountsOperations.get` deleted or renamed its parameter `name` of kind `positional_or_keyword`
  - Method `AccountsOperations.update` inserted a `positional_or_keyword` parameter `account_name`
  - Method `AccountsOperations.update` deleted or renamed its parameter `name` of kind `positional_or_keyword`
  - Method `QuotasOperations.get` inserted a `positional_or_keyword` parameter `quota_name`
  - Method `QuotasOperations.get` deleted or renamed its parameter `name` of kind `positional_or_keyword`
  - Method `QuotasOperations.get` re-ordered its parameters from `['self', 'location', 'name', 'kwargs']` to `['self', 'location', 'quota_name', 'kwargs']`
  - Method `AccountsOperations.update` re-ordered its parameters from `['self', 'resource_group_name', 'name', 'properties', 'kwargs']` to `['self', 'resource_group_name', 'account_name', 'properties', 'kwargs']`
  - Method `AccountsOperations.begin_create_or_update` re-ordered its parameters from `['self', 'resource_group_name', 'name', 'resource', 'kwargs']` to `['self', 'resource_group_name', 'account_name', 'resource', 'kwargs']`
  - Method `AccountsOperations.get` re-ordered its parameters from `['self', 'resource_group_name', 'name', 'kwargs']` to `['self', 'resource_group_name', 'account_name', 'kwargs']`
  - Method `AccountsOperations.begin_delete` re-ordered its parameters from `['self', 'resource_group_name', 'name', 'kwargs']` to `['self', 'resource_group_name', 'account_name', 'kwargs']`

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
