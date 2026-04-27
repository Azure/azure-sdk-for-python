# Release History

## 1.0.0b3 (2026-04-27)

### Features Added

  - Client `EducationManagementClient` added method `send_request`
  - Model `GrantDetails` added property `properties`
  - Model `JoinRequestDetails` added property `properties`
  - Model `LabDetails` added property `properties`
  - Model `StudentDetails` added property `properties`
  - Model `StudentLabDetails` added property `properties`
  - Added model `GrantDetailProperties`
  - Added model `JoinRequestProperties`
  - Added model `LabProperties`
  - Added model `ProxyResource`
  - Added model `StudentLabProperties`
  - Added model `StudentProperties`

### Breaking Changes

  - Model `GrantDetails` deleted or renamed its instance variable `offer_cap`
  - Model `GrantDetails` deleted or renamed its instance variable `effective_date`
  - Model `GrantDetails` deleted or renamed its instance variable `offer_type`
  - Model `GrantDetails` deleted or renamed its instance variable `expiration_date`
  - Model `GrantDetails` deleted or renamed its instance variable `status`
  - Model `GrantDetails` deleted or renamed its instance variable `allocated_budget`
  - Model `JoinRequestDetails` deleted or renamed its instance variable `first_name`
  - Model `JoinRequestDetails` deleted or renamed its instance variable `last_name`
  - Model `JoinRequestDetails` deleted or renamed its instance variable `email`
  - Model `JoinRequestDetails` deleted or renamed its instance variable `status`
  - Model `LabDetails` deleted or renamed its instance variable `display_name`
  - Model `LabDetails` deleted or renamed its instance variable `budget_per_student`
  - Model `LabDetails` deleted or renamed its instance variable `description`
  - Model `LabDetails` deleted or renamed its instance variable `expiration_date`
  - Model `LabDetails` deleted or renamed its instance variable `effective_date`
  - Model `LabDetails` deleted or renamed its instance variable `status`
  - Model `LabDetails` deleted or renamed its instance variable `max_student_count`
  - Model `LabDetails` deleted or renamed its instance variable `invitation_code`
  - Model `LabDetails` deleted or renamed its instance variable `currency_properties_total_allocated_budget_currency`
  - Model `LabDetails` deleted or renamed its instance variable `value_properties_total_allocated_budget_value`
  - Model `LabDetails` deleted or renamed its instance variable `currency_properties_total_budget_currency`
  - Model `LabDetails` deleted or renamed its instance variable `value_properties_total_budget_value`
  - Model `StudentDetails` deleted or renamed its instance variable `first_name`
  - Model `StudentDetails` deleted or renamed its instance variable `last_name`
  - Model `StudentDetails` deleted or renamed its instance variable `email`
  - Model `StudentDetails` deleted or renamed its instance variable `role`
  - Model `StudentDetails` deleted or renamed its instance variable `budget`
  - Model `StudentDetails` deleted or renamed its instance variable `subscription_id`
  - Model `StudentDetails` deleted or renamed its instance variable `expiration_date`
  - Model `StudentDetails` deleted or renamed its instance variable `status`
  - Model `StudentDetails` deleted or renamed its instance variable `effective_date`
  - Model `StudentDetails` deleted or renamed its instance variable `subscription_alias`
  - Model `StudentDetails` deleted or renamed its instance variable `subscription_invite_last_sent_date`
  - Model `StudentLabDetails` deleted or renamed its instance variable `display_name`
  - Model `StudentLabDetails` deleted or renamed its instance variable `description`
  - Model `StudentLabDetails` deleted or renamed its instance variable `expiration_date`
  - Model `StudentLabDetails` deleted or renamed its instance variable `role`
  - Model `StudentLabDetails` deleted or renamed its instance variable `budget`
  - Model `StudentLabDetails` deleted or renamed its instance variable `subscription_id`
  - Model `StudentLabDetails` deleted or renamed its instance variable `status`
  - Model `StudentLabDetails` deleted or renamed its instance variable `effective_date`
  - Model `StudentLabDetails` deleted or renamed its instance variable `lab_scope`
  - Deleted or renamed model `GrantListResponse`
  - Deleted or renamed model `JoinRequestList`
  - Method `GrantsOperations.get` changed its parameter `include_allocated_budget` from `positional_or_keyword` to `keyword_only`
  - Method `GrantsOperations.list` changed its parameter `include_allocated_budget` from `positional_or_keyword` to `keyword_only`
  - Method `GrantsOperations.list_all` changed its parameter `include_allocated_budget` from `positional_or_keyword` to `keyword_only`
  - Method `JoinRequestsOperations.list` changed its parameter `include_denied` from `positional_or_keyword` to `keyword_only`
  - Method `LabsOperations.generate_invite_code` changed its parameter `only_update_student_count_parameter` from `positional_or_keyword` to `keyword_only`
  - Method `LabsOperations.get` changed its parameter `include_budget` from `positional_or_keyword` to `keyword_only`
  - Method `LabsOperations.list` changed its parameter `include_budget` from `positional_or_keyword` to `keyword_only`
  - Method `LabsOperations.list_all` changed its parameter `include_budget` from `positional_or_keyword` to `keyword_only`
  - Method `LabsOperations.list_all` changed its parameter `include_deleted` from `positional_or_keyword` to `keyword_only`
  - Method `StudentsOperations.list` changed its parameter `include_deleted` from `positional_or_keyword` to `keyword_only`

## 1.0.0b2 (2022-12-12)

### Other Changes

  - Added generated samples in github repo
  - Drop support for python<3.7.0

## 1.0.0b1 (2022-07-07)

* Initial Release
