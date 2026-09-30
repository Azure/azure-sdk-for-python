# Release History

## 1.0.0b3 (2026-05-27)

### Features Added

  - Client `EducationManagementClient` added parameter `cloud_setting` in method `__init__`
  - Client `EducationManagementClient` added method `send_request`
  - Added model `ProxyResource`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. Please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - For the method breakings, please refer to https://aka.ms/azsdk/python/migrate/operations for migration.
  - Model `GrantDetails` moved instance variable `offer_cap`, `effective_date`, `offer_type`, `expiration_date`, `status` and `allocated_budget` under property `properties` whose type is `GrantDetailProperties`
  - Model `JoinRequestDetails` moved instance variable `first_name`, `last_name`, `email` and `status` under property `properties` whose type is `JoinRequestProperties`
  - Model `LabDetails` moved instance variable `display_name`, `budget_per_student`, `description`, `expiration_date`, `effective_date`, `status`, `max_student_count`, `invitation_code`, `currency_properties_total_allocated_budget_currency`, `value_properties_total_allocated_budget_value`, `currency_properties_total_budget_currency` and `value_properties_total_budget_value` under property `properties` whose type is `LabProperties`
  - Model `StudentDetails` moved instance variable `first_name`, `last_name`, `email`, `role`, `budget`, `subscription_id`, `expiration_date`, `status`, `effective_date`, `subscription_alias` and `subscription_invite_last_sent_date` under property `properties` whose type is `StudentProperties`
  - Model `StudentLabDetails` moved instance variable `display_name`, `description`, `expiration_date`, `role`, `budget`, `subscription_id`, `status`, `effective_date` and `lab_scope` under property `properties` whose type is `StudentLabProperties`
  - Method `GrantsOperations.get` changed its parameter `include_allocated_budget` from `positional_or_keyword` to `keyword_only`
  - Method `GrantsOperations.list` changed its parameter `include_allocated_budget` from `positional_or_keyword` to `keyword_only`
  - Method `GrantsOperations.list_all` changed its parameter `include_allocated_budget` from `positional_or_keyword` to `keyword_only`
  - Method `JoinRequestsOperations.list` changed its parameter `include_denied` from `positional_or_keyword` to `keyword_only`
  - Method `LabsOperations.generate_invite_code` changed its parameter `only_update_student_count_parameter` from `positional_or_keyword` to `keyword_only`
  - Method `LabsOperations.get` changed its parameter `include_budget` from `positional_or_keyword` to `keyword_only`
  - Method `LabsOperations.list` changed its parameter `include_budget` from `positional_or_keyword` to `keyword_only`
  - Method `LabsOperations.list_all` changed its parameter `include_budget`/`include_deleted` from `positional_or_keyword` to `keyword_only`
  - Method `StudentsOperations.list` changed its parameter `include_deleted` from `positional_or_keyword` to `keyword_only`
  - Renamed operation group `EducationManagementClientOperationsMixin` to `_EducationManagementClientOperationsMixin`

### Other Changes

  - Deleted model `GrantListResponse`/`JoinRequestList` which actually were not used by SDK users

## 1.0.0b2 (2022-12-12)

### Other Changes

  - Added generated samples in github repo
  - Drop support for python<3.7.0

## 1.0.0b1 (2022-07-07)

* Initial Release
