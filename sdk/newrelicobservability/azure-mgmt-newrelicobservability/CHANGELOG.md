# Release History

## 2.0.0 (2026-08-11)

### Features Added

  - Client `NewRelicObservabilityMgmtClient` added parameter `cloud_setting` in method `__init__`
  - Client `NewRelicObservabilityMgmtClient` added method `send_request`
  - Client `NewRelicObservabilityMgmtClient` added operation group `saa_s`
  - Model `MarketplaceSaaSInfo` added property `offer_id`
  - Model `MarketplaceSaaSInfo` added property `publisher_id`
  - Model `MonitoredSubscriptionProperties` added property `system_data`
  - Added model `ActivateSaaSParameterRequest`
  - Added model `LatestLinkedSaaSResponse`
  - Added model `ResubscribeProperties`
  - Added model `SaaSData`
  - Added model `SaaSResourceDetailsResponse`
  - Operation group `MonitoredSubscriptionsOperations` added method `begin_create_or_update`
  - Operation group `MonitorsOperations` added method `begin_link_saa_s`
  - Operation group `MonitorsOperations` added method `begin_resubscribe`
  - Operation group `MonitorsOperations` added method `begin_update`
  - Operation group `MonitorsOperations` added method `latest_linked_saa_s`
  - Operation group `MonitorsOperations` added method `refresh_ingestion_key`
  - Added operation group `SaaSOperations`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. Please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - For the method breakings, please refer to https://aka.ms/azsdk/python/migrate/operations for migration.
  - Model `AccountResource` moved instance variable `account_id`, `account_name`, `organization_id` and `region` under property `properties` whose type is `AccountProperties`
  - Model `NewRelicMonitorResource` moved instance variable `account_creation_source`, `liftr_resource_category`, `liftr_resource_preference`, `marketplace_subscription_id`, `marketplace_subscription_status`, `monitoring_status`, `new_relic_account_properties`, `org_creation_source`, `plan_data`, `provisioning_state`, `saa_s_azure_subscription_status`, `subscription_state` and `user_info` under property `properties` whose type is `MonitorProperties`
  - Model `NewRelicMonitorResourceUpdate` moved instance variable `account_creation_source`, `new_relic_account_properties`, `org_creation_source`, `plan_data` and `user_info` under property `properties` whose type is `NewRelicMonitorResourceUpdateProperties`
  - Model `OrganizationResource` moved instance variable `billing_source`, `organization_id` and `organization_name` under property `properties` whose type is `OrganizationProperties`
  - Model `PlanDataResource` moved instance variable `account_creation_source`, `org_creation_source` and `plan_data` under property `properties` whose type is `PlanDataProperties`
  - Model `TagRule` moved instance variable `log_rules`, `metric_rules` and `provisioning_state` under property `properties` whose type is `MonitoringTagRulesProperties`
  - Model `TagRuleUpdate` moved instance variable `log_rules` and `metric_rules` under property `properties` whose type is `TagRuleUpdateProperties`
  - Deleted or renamed model `BillingCycle`
  - Method `AccountsOperations.list` changed its parameter `location`/`user_email` from `positional_or_keyword` to `keyword_only`
  - Operation group `MonitoredSubscriptionsOperations` renamed method `begin_createor_update` to `begin_create_or_update`
  - Method `MonitorsOperations.begin_delete` changed its parameter `user_email` from `positional_or_keyword` to `keyword_only`
  - Operation group `MonitorsOperations` renamed method `update` to `begin_update`
  - Method `OrganizationsOperations.list` changed its parameter `location`/`user_email` from `positional_or_keyword` to `keyword_only`
  - Method `PlansOperations.list` changed its parameter `account_id`/`organization_id` from `positional_or_keyword` to `keyword_only`

### Other Changes

  - Deleted model `AccountsListResponse`/`AppServicesListResponse`/`ConnectedPartnerResourcesListResponse`/`LinkedResourceListResponse`/`MonitoredResourceListResponse`/`MonitoredSubscriptionPropertiesList`/`NewRelicMonitorResourceListResult`/`OperationListResult`/`OrganizationsListResponse`/`PlanDataListResponse`/`TagRuleListResult`/`VMHostsListResponse` which actually were not used by SDK users
  - Deleted model `AppServicesGetParameter`/`HostsGetParameter`/`MetricsRequestParameter`/`MetricsStatusRequestParameter`/`SwitchBillingParameter` which actually were not used by SDK users

## 2.0.0b2 (2026-07-07)

### Features Added

  - Client `NewRelicObservabilityMgmtClient` added method `send_request`
  - Model `MonitoredSubscriptionProperties` added property `system_data`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. Please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - For the method breakings, please refer to https://aka.ms/azsdk/python/migrate/operations for migration.
  - Model `AccountResource` moved instance variable `organization_id`, `account_id`, `account_name` and `region` under property `properties` whose type is `AccountProperties`
  - Model `NewRelicMonitorResource` moved instance variable `provisioning_state`, `monitoring_status`, `marketplace_subscription_status`, `marketplace_subscription_id`, `new_relic_account_properties`, `user_info`, `plan_data`, `saa_s_data`, `liftr_resource_category`, `liftr_resource_preference`, `org_creation_source`, `account_creation_source`, `subscription_state` and `saa_s_azure_subscription_status` under property `properties` whose type is `MonitorProperties`
  - Model `NewRelicMonitorResourceUpdate` moved instance variable `new_relic_account_properties`, `user_info`, `plan_data`, `saa_s_data`, `org_creation_source` and `account_creation_source` under property `properties` whose type is `NewRelicMonitorResourceUpdateProperties`
  - Model `OrganizationResource` moved instance variable `organization_id`, `organization_name` and `billing_source` under property `properties` whose type is `OrganizationProperties`
  - Model `PlanDataResource` moved instance variable `plan_data`, `org_creation_source` and `account_creation_source` under property `properties` whose type is `PlanDataProperties`
  - Model `TagRule` moved instance variable `provisioning_state`, `log_rules` and `metric_rules` under property `properties` whose type is `MonitoringTagRulesProperties`
  - Model `TagRuleUpdate` moved instance variable `log_rules` and `metric_rules` under property `properties` whose type is `TagRuleUpdateProperties`
  - Method `AccountsOperations.list` changed its parameter `user_email`/`location` from `positional_or_keyword` to `keyword_only`
  - Method `MonitorsOperations.begin_delete` changed its parameter `user_email` from `positional_or_keyword` to `keyword_only`
  - Method `OrganizationsOperations.list` changed its parameter `user_email`/`location` from `positional_or_keyword` to `keyword_only`
  - Method `PlansOperations.list` changed its parameter `account_id`/`organization_id` from `positional_or_keyword` to `keyword_only`

### Other Changes

  - Deleted model `AccountsListResponse`/`AppServicesListResponse`/`ConnectedPartnerResourcesListResponse`/`LinkedResourceListResponse`/`MonitoredResourceListResponse`/`MonitoredSubscriptionPropertiesList`/`NewRelicMonitorResourceListResult`/`OperationListResult`/`OrganizationsListResponse`/`PlanDataListResponse`/`TagRuleListResult`/`VMHostsListResponse` which actually were not used by SDK users
  - Deleted model `AppServicesGetParameter`/`HostsGetParameter`/`MetricsRequestParameter`/`MetricsStatusRequestParameter`/`SwitchBillingParameter` which actually were not used by SDK users

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
