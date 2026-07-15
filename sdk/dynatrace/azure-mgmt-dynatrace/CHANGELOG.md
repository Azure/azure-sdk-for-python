# Release History

## 3.0.0b1 (2026-07-06)

### Features Added

  - Client `DynatraceObservabilityMgmtClient` added parameter `cloud_setting` in method `__init__`
  - Client `DynatraceObservabilityMgmtClient` added method `send_request`
  - Client `DynatraceObservabilityMgmtClient` added operation group `monitored_subscriptions`
  - Client `DynatraceObservabilityMgmtClient` added operation group `creation_supported`
  - Model `AccountInfo` added property `company_name`
  - Model `DynatraceSingleSignOnResource` added property `properties`
  - Model `MarketplaceSaaSResourceDetailsResponse` added property `marketplace_saa_s_resource_name`
  - Enum `MarketplaceSubscriptionStatus` added member `UNSUBSCRIBED`
  - Model `MonitorResource` added property `properties`
  - Model `MonitorResourceUpdate` added property `properties`
  - Model `MonitorResourceUpdate` added property `identity`
  - Enum `MonitoringType` added member `DISCOVERY`
  - Model `ProxyResource` added property `system_data`
  - Model `Resource` added property `system_data`
  - Model `TagRule` added property `properties`
  - Model `TrackedResource` added property `system_data`
  - Added enum `Action`
  - Added model `ConnectedResourcesCountResponse`
  - Added model `CreateResourceSupportedProperties`
  - Added model `CreateResourceSupportedResponse`
  - Added model `LogStatusRequest`
  - Added model `ManageAgentInstallationRequest`
  - Added model `ManageAgentList`
  - Added model `ManagedServiceIdentity`
  - Added enum `ManagedServiceIdentityType`
  - Added enum `MarketplaceSaasAutoRenew`
  - Added model `MarketplaceSubscriptionIdRequest`
  - Added model `MetricStatusRequest`
  - Added model `MonitorUpdateProperties`
  - Added model `MonitoredSubscription`
  - Added model `MonitoredSubscriptionProperties`
  - Added enum `Status`
  - Added model `SubscriptionList`
  - Added enum `SubscriptionListOperation`
  - Added model `UpgradePlanRequest`
  - Operation group `MonitorsOperations` added method `begin_upgrade_plan`
  - Operation group `MonitorsOperations` added method `get_all_connected_resources_count`
  - Operation group `MonitorsOperations` added method `manage_agent_installation`
  - Added operation group `CreationSupportedOperations`
  - Added operation group `MonitoredSubscriptionsOperations`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. Please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - Model `DynatraceSingleSignOnResource` moved instance variable `single_sign_on_state`, `enterprise_app_id`, `single_sign_on_url`, `aad_domains` and `provisioning_state` under property `properties` whose type is `DynatraceSingleSignOnProperties`
  - Model `MonitorResource` moved instance variable `monitoring_status`, `marketplace_subscription_status`, `dynatrace_environment_properties`, `user_info`, `plan_data`, `liftr_resource_category`, `liftr_resource_preference` and `provisioning_state` under property `properties` whose type is `MonitorProperties`
  - Model `TagRule` moved instance variable `log_rules`, `metric_rules` and `provisioning_state` under property `properties` whose type is `MonitoringTagRulesProperties`

### Other Changes

  - Deleted model `AppServiceListResponse`/`DynatraceSingleSignOnResourceListResult`/`LinkableEnvironmentListResponse`/`MonitorResourceListResult`/`MonitoredResourceListResponse`/`OperationListResult`/`TagRuleListResult`/`VMHostsListResponse` which actually were not used by SDK users

## 2.0.0 (2023-08-18)

### Features Added

  - Added operation MonitorsOperations.get_marketplace_saa_s_resource_details
  - Added operation MonitorsOperations.get_metric_status
  - Model MetricRules has a new parameter sending_metrics

### Breaking Changes

  - Model MonitorResourceUpdate no longer has parameter dynatrace_environment_properties
  - Model MonitorResourceUpdate no longer has parameter marketplace_subscription_status
  - Model MonitorResourceUpdate no longer has parameter monitoring_status
  - Model MonitorResourceUpdate no longer has parameter plan_data
  - Model MonitorResourceUpdate no longer has parameter user_info
  - Parameter region of model LinkableEnvironmentRequest is now required
  - Parameter tenant_id of model LinkableEnvironmentRequest is now required
  - Parameter user_principal of model LinkableEnvironmentRequest is now required
  - Parameter user_principal of model SSODetailsRequest is now required
  - Removed operation MonitorsOperations.get_account_credentials
  - Removed operation TagRulesOperations.update

## 1.1.0b1 (2022-12-27)

### Other Changes

  - Added generated samples in github repo
  - Drop support for python<3.7.0

## 1.0.0 (2022-09-16)

### Breaking Changes

  - Client name is changed from `DynatraceObservability` to `DynatraceObservabilityMgmtClient`

## 1.0.0b1 (2022-05-19)

* Initial Release
