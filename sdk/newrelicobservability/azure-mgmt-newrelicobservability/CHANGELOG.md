# Release History

## 2.0.0b2 (2026-07-07)

### Features Added

  - Client `NewRelicObservabilityMgmtClient` added method `send_request`
  - Model `AccountResource` added property `properties`
  - Model `MonitoredSubscriptionProperties` added property `system_data`
  - Model `NewRelicMonitorResource` added property `properties`
  - Model `NewRelicMonitorResourceUpdate` added property `properties`
  - Model `OrganizationResource` added property `properties`
  - Model `PlanDataResource` added property `properties`
  - Model `TagRule` added property `properties`
  - Added model `AccountProperties`
  - Added model `MonitorProperties`
  - Added model `NewRelicMonitorResourceUpdateProperties`
  - Added model `OrganizationProperties`
  - Added model `PlanDataProperties`
  - Added model `TagRuleUpdateProperties`

### Breaking Changes

  - Model `AccountResource` deleted or renamed its instance variable `organization_id`
  - Model `AccountResource` deleted or renamed its instance variable `account_id`
  - Model `AccountResource` deleted or renamed its instance variable `account_name`
  - Model `AccountResource` deleted or renamed its instance variable `region`
  - Model `NewRelicMonitorResource` deleted or renamed its instance variable `provisioning_state`
  - Model `NewRelicMonitorResource` deleted or renamed its instance variable `monitoring_status`
  - Model `NewRelicMonitorResource` deleted or renamed its instance variable `marketplace_subscription_status`
  - Model `NewRelicMonitorResource` deleted or renamed its instance variable `marketplace_subscription_id`
  - Model `NewRelicMonitorResource` deleted or renamed its instance variable `new_relic_account_properties`
  - Model `NewRelicMonitorResource` deleted or renamed its instance variable `user_info`
  - Model `NewRelicMonitorResource` deleted or renamed its instance variable `plan_data`
  - Model `NewRelicMonitorResource` deleted or renamed its instance variable `saa_s_data`
  - Model `NewRelicMonitorResource` deleted or renamed its instance variable `liftr_resource_category`
  - Model `NewRelicMonitorResource` deleted or renamed its instance variable `liftr_resource_preference`
  - Model `NewRelicMonitorResource` deleted or renamed its instance variable `org_creation_source`
  - Model `NewRelicMonitorResource` deleted or renamed its instance variable `account_creation_source`
  - Model `NewRelicMonitorResource` deleted or renamed its instance variable `subscription_state`
  - Model `NewRelicMonitorResource` deleted or renamed its instance variable `saa_s_azure_subscription_status`
  - Model `NewRelicMonitorResourceUpdate` deleted or renamed its instance variable `new_relic_account_properties`
  - Model `NewRelicMonitorResourceUpdate` deleted or renamed its instance variable `user_info`
  - Model `NewRelicMonitorResourceUpdate` deleted or renamed its instance variable `plan_data`
  - Model `NewRelicMonitorResourceUpdate` deleted or renamed its instance variable `saa_s_data`
  - Model `NewRelicMonitorResourceUpdate` deleted or renamed its instance variable `org_creation_source`
  - Model `NewRelicMonitorResourceUpdate` deleted or renamed its instance variable `account_creation_source`
  - Model `OrganizationResource` deleted or renamed its instance variable `organization_id`
  - Model `OrganizationResource` deleted or renamed its instance variable `organization_name`
  - Model `OrganizationResource` deleted or renamed its instance variable `billing_source`
  - Model `PlanDataResource` deleted or renamed its instance variable `plan_data`
  - Model `PlanDataResource` deleted or renamed its instance variable `org_creation_source`
  - Model `PlanDataResource` deleted or renamed its instance variable `account_creation_source`
  - Model `TagRule` deleted or renamed its instance variable `provisioning_state`
  - Model `TagRule` deleted or renamed its instance variable `log_rules`
  - Model `TagRule` deleted or renamed its instance variable `metric_rules`
  - Model `TagRuleUpdate` deleted or renamed its instance variable `log_rules`
  - Model `TagRuleUpdate` deleted or renamed its instance variable `metric_rules`
  - Deleted or renamed model `AccountsListResponse`
  - Deleted or renamed model `AppServicesGetParameter`
  - Deleted or renamed model `AppServicesListResponse`
  - Deleted or renamed model `ConnectedPartnerResourcesListResponse`
  - Deleted or renamed model `HostsGetParameter`
  - Deleted or renamed model `LinkedResourceListResponse`
  - Deleted or renamed model `MetricsRequestParameter`
  - Deleted or renamed model `MetricsStatusRequestParameter`
  - Deleted or renamed model `MonitoredResourceListResponse`
  - Deleted or renamed model `MonitoredSubscriptionPropertiesList`
  - Deleted or renamed model `NewRelicMonitorResourceListResult`
  - Deleted or renamed model `OperationListResult`
  - Deleted or renamed model `OrganizationsListResponse`
  - Deleted or renamed model `PlanDataListResponse`
  - Deleted or renamed model `SwitchBillingParameter`
  - Deleted or renamed model `TagRuleListResult`
  - Deleted or renamed model `VMHostsListResponse`
  - Method `AccountsOperations.list` changed its parameter `user_email` from `positional_or_keyword` to `keyword_only`
  - Method `AccountsOperations.list` changed its parameter `location` from `positional_or_keyword` to `keyword_only`
  - Method `MonitorsOperations.begin_delete` changed its parameter `user_email` from `positional_or_keyword` to `keyword_only`
  - Method `OrganizationsOperations.list` changed its parameter `user_email` from `positional_or_keyword` to `keyword_only`
  - Method `OrganizationsOperations.list` changed its parameter `location` from `positional_or_keyword` to `keyword_only`
  - Method `PlansOperations.list` changed its parameter `account_id` from `positional_or_keyword` to `keyword_only`
  - Method `PlansOperations.list` changed its parameter `organization_id` from `positional_or_keyword` to `keyword_only`
  - Method `MonitorsOperations.begin_delete` re-ordered its parameters from `['self', 'resource_group_name', 'user_email', 'monitor_name', 'kwargs']` to `['self', 'resource_group_name', 'monitor_name', 'user_email', 'kwargs']`

## 2.0.0b1 (2025-11-17)

### Features Added

  - Model `NewRelicObservabilityMgmtClient` added parameter `cloud_setting` in method `__init__`
  - Client `NewRelicObservabilityMgmtClient` added operation group `saa_s`
  - Model `MarketplaceSaaSInfo` added property `publisher_id`
  - Model `MarketplaceSaaSInfo` added property `offer_id`
  - Model `NewRelicMonitorResource` added property `saa_s_data`
  - Model `NewRelicMonitorResourceUpdate` added property `saa_s_data`
  - Added model `ActivateSaaSParameterRequest`
  - Added model `LatestLinkedSaaSResponse`
  - Added model `ResubscribeProperties`
  - Added model `SaaSData`
  - Added model `SaaSResourceDetailsResponse`
  - Operation group `MonitorsOperations` added method `begin_link_saa_s`
  - Operation group `MonitorsOperations` added method `begin_resubscribe`
  - Operation group `MonitorsOperations` added method `latest_linked_saa_s`
  - Operation group `MonitorsOperations` added method `refresh_ingestion_key`
  - Added operation group `SaaSOperations`

### Breaking Changes

  - Deleted or renamed model `BillingCycle`
  - Operation group `MonitoredSubscriptionsOperations` renamed method `begin_createor_update` to `begin_create_or_update`
  - Operation group `MonitorsOperations` renamed method `update` to `begin_update`

## 1.1.0 (2024-03-18)

### Features Added

  - Added operation MonitorsOperations.list_linked_resources
  - Added operation group BillingInfoOperations
  - Added operation group ConnectedPartnerResourcesOperations
  - Added operation group MonitoredSubscriptionsOperations
  - Model NewRelicMonitorResource has a new parameter saa_s_azure_subscription_status
  - Model NewRelicMonitorResource has a new parameter subscription_state

## 1.0.0 (2023-05-20)

### Other Changes

  - First GA

## 1.0.0b1 (2023-03-24)

* Initial Release
