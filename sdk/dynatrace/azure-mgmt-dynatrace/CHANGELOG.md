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
  - Added model `MonitorProperties`
  - Added model `MonitorUpdateProperties`
  - Added model `MonitoredSubscription`
  - Added model `MonitoredSubscriptionProperties`
  - Added model `MonitoringTagRulesProperties`
  - Added enum `Status`
  - Added model `SubscriptionList`
  - Added enum `SubscriptionListOperation`
  - Added model `UpgradePlanRequest`
  - Model `MonitorsOperations` added method `begin_upgrade_plan`
  - Model `MonitorsOperations` added method `get_all_connected_resources_count`
  - Model `MonitorsOperations` added method `manage_agent_installation`
  - Added model `CreationSupportedOperations`
  - Added model `MonitoredSubscriptionsOperations`

### Breaking Changes

  - Model `DynatraceSingleSignOnResource` deleted or renamed its instance variable `single_sign_on_state`
  - Model `DynatraceSingleSignOnResource` deleted or renamed its instance variable `enterprise_app_id`
  - Model `DynatraceSingleSignOnResource` deleted or renamed its instance variable `single_sign_on_url`
  - Model `DynatraceSingleSignOnResource` deleted or renamed its instance variable `aad_domains`
  - Model `DynatraceSingleSignOnResource` deleted or renamed its instance variable `provisioning_state`
  - Model `MonitorResource` deleted or renamed its instance variable `monitoring_status`
  - Model `MonitorResource` deleted or renamed its instance variable `marketplace_subscription_status`
  - Model `MonitorResource` deleted or renamed its instance variable `dynatrace_environment_properties`
  - Model `MonitorResource` deleted or renamed its instance variable `user_info`
  - Model `MonitorResource` deleted or renamed its instance variable `plan_data`
  - Model `MonitorResource` deleted or renamed its instance variable `liftr_resource_category`
  - Model `MonitorResource` deleted or renamed its instance variable `liftr_resource_preference`
  - Model `MonitorResource` deleted or renamed its instance variable `provisioning_state`
  - Model `TagRule` deleted or renamed its instance variable `log_rules`
  - Model `TagRule` deleted or renamed its instance variable `metric_rules`
  - Model `TagRule` deleted or renamed its instance variable `provisioning_state`
  - Deleted or renamed model `AppServiceListResponse`
  - Deleted or renamed model `DynatraceSingleSignOnResourceListResult`
  - Deleted or renamed model `LinkableEnvironmentListResponse`
  - Deleted or renamed model `MonitorResourceListResult`
  - Deleted or renamed model `MonitoredResourceListResponse`
  - Deleted or renamed model `OperationListResult`
  - Deleted or renamed model `TagRuleListResult`
  - Deleted or renamed model `VMHostsListResponse`

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
