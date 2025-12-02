# Release History

## 3.0.1 (2025-10-09)

### Bugs Fixed

- Exclude `generated_samples` and `generated_tests` from wheel

## 3.0.0 (2025-09-22)

### Features Added

  - Model `QuotaMgmtClient` added parameter `cloud_setting` in method `__init__`
  - Client `QuotaMgmtClient` added method `send_request`
  - Client `QuotaMgmtClient` added operation group `group_quota_usages`
  - Client `QuotaMgmtClient` added operation group `group_quota_location_settings`
  - Model `CurrentQuotaLimitBase` added property `system_data`
  - Model `CurrentUsagesBase` added property `system_data`
  - Model `GroupQuotasEntityBase` added property `group_type`
  - Model `GroupQuotasEntityProperties` added property `group_type`
  - Model `QuotaRequestDetails` added property `system_data`
  - Enum `RequestState` added member `ESCALATED`
  - Added enum `EnforcementState`
  - Added model `ExtensionResource`
  - Added model `GroupQuotasEnforcementStatus`
  - Added model `GroupQuotasEnforcementStatusProperties`
  - Added enum `GroupType`
  - Added operation group `GroupQuotaLocationSettingsOperations`
  - Added operation group `GroupQuotaUsagesOperations`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. And please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - Deleted or renamed model `CommonResourceProperties`
  - Deleted or renamed model `CreateGenericQuotaRequestParameters`
  - Deleted or renamed model `GroupQuotaList`
  - Deleted or renamed model `GroupQuotaSubscriptionIdList`
  - Deleted or renamed model `GroupQuotaSubscriptionRequestStatusList`
  - Deleted or renamed model `LROResponse`
  - Deleted or renamed model `LROResponseProperties`
  - Deleted or renamed model `OperationList`
  - Deleted or renamed model `QuotaAllocationRequestStatusList`
  - Deleted or renamed model `QuotaLimits`
  - Deleted or renamed model `QuotaLimitsResponse`
  - Deleted or renamed model `QuotaRequestDetailsList`
  - Deleted or renamed model `QuotaRequestOneResourceProperties`
  - Deleted or renamed model `QuotaRequestOneResourceSubmitResponse`
  - Deleted or renamed model `QuotaRequestStatusDetails`
  - Deleted or renamed model `QuotaRequestSubmitResponse`
  - Deleted or renamed model `QuotaRequestSubmitResponse202`
  - Deleted or renamed model `ResourceBaseRequest`
  - Deleted or renamed model `ResourceUsageList`
  - Deleted or renamed model `SubmittedResourceRequestStatusList`
  - Deleted or renamed model `SubscriptionGroupQuotaAssignment`
  - Deleted or renamed model `SubscriptionQuotaAllocationRequestList`
  - Deleted or renamed model `SubscriptionQuotaAllocationsStatusList`
  - Deleted or renamed model `UsagesLimits`
  - Method `QuotaRequestStatusOperations.list` changed its parameter `skiptoken` from `positional_or_keyword` to `keyword_only`

## 2.0.0 (2025-02-26)

### Features Added

  - Client `QuotaMgmtClient` added operation group `group_quotas`
  - Client `QuotaMgmtClient` added operation group `group_quota_subscriptions`
  - Client `QuotaMgmtClient` added operation group `group_quota_subscription_requests`
  - Client `QuotaMgmtClient` added operation group `group_quota_limits_request`
  - Client `QuotaMgmtClient` added operation group `group_quota_limits`
  - Client `QuotaMgmtClient` added operation group `group_quota_subscription_allocation_request`
  - Client `QuotaMgmtClient` added operation group `group_quota_subscription_allocation`
  - Model `QuotaRequestDetails` added property `properties`
  - Added model `AllocatedQuotaToSubscriptionList`
  - Added model `AllocatedToSubscription`
  - Added enum `CreatedByType`
  - Added model `ErrorAdditionalInfo`
  - Added model `ErrorDetail`
  - Added model `ErrorResponse`
  - Added model `GroupQuotaDetails`
  - Added model `GroupQuotaDetailsName`
  - Added model `GroupQuotaLimit`
  - Added model `GroupQuotaLimitList`
  - Added model `GroupQuotaLimitListProperties`
  - Added model `GroupQuotaLimitProperties`
  - Added model `GroupQuotaList`
  - Added model `GroupQuotaRequestBase`
  - Added model `GroupQuotaRequestBaseProperties`
  - Added model `GroupQuotaRequestBasePropertiesName`
  - Added model `GroupQuotaSubscriptionId`
  - Added model `GroupQuotaSubscriptionIdList`
  - Added model `GroupQuotaSubscriptionIdProperties`
  - Added model `GroupQuotaSubscriptionRequestStatus`
  - Added model `GroupQuotaSubscriptionRequestStatusList`
  - Added model `GroupQuotaSubscriptionRequestStatusProperties`
  - Added model `GroupQuotaUsagesBase`
  - Added model `GroupQuotaUsagesBaseName`
  - Added model `GroupQuotasEntity`
  - Added model `GroupQuotasEntityBase`
  - Added model `GroupQuotasEntityBasePatch`
  - Added model `GroupQuotasEntityPatch`
  - Added model `GroupQuotasEntityPatchProperties`
  - Added model `GroupQuotasEntityProperties`
  - Added model `LROResponse`
  - Added model `LROResponseProperties`
  - Added model `ProxyResource`
  - Added model `QuotaAllocationRequestBase`
  - Added model `QuotaAllocationRequestBaseProperties`
  - Added model `QuotaAllocationRequestBasePropertiesName`
  - Added model `QuotaAllocationRequestStatus`
  - Added model `QuotaAllocationRequestStatusList`
  - Added model `QuotaAllocationRequestStatusProperties`
  - Added model `QuotaRequestOneResourceProperties`
  - Added model `QuotaRequestStatusDetails`
  - Added enum `RequestState`
  - Added model `Resource`
  - Added model `ResourceBaseRequest`
  - Added model `ResourceUsageList`
  - Added model `ResourceUsages`
  - Added model `SubmittedResourceRequestStatus`
  - Added model `SubmittedResourceRequestStatusList`
  - Added model `SubmittedResourceRequestStatusProperties`
  - Added model `SubscriptionGroupQuotaAssignment`
  - Added model `SubscriptionQuotaAllocationRequestList`
  - Added model `SubscriptionQuotaAllocations`
  - Added model `SubscriptionQuotaAllocationsList`
  - Added model `SubscriptionQuotaAllocationsListProperties`
  - Added model `SubscriptionQuotaAllocationsProperties`
  - Added model `SubscriptionQuotaAllocationsStatusList`
  - Added model `SubscriptionQuotaDetails`
  - Added model `SubscriptionQuotaDetailsName`
  - Added model `SystemData`
  - Added operation group `GroupQuotaLimitsOperations`
  - Added operation group `GroupQuotaLimitsRequestOperations`
  - Added operation group `GroupQuotaSubscriptionAllocationOperations`
  - Added operation group `GroupQuotaSubscriptionAllocationRequestOperations`
  - Added operation group `GroupQuotaSubscriptionRequestsOperations`
  - Added operation group `GroupQuotaSubscriptionsOperations`
  - Added operation group `GroupQuotasOperations`

### Breaking Changes

  - Model `QuotaRequestDetails` deleted or renamed its instance variable `provisioning_state`
  - Model `QuotaRequestDetails` deleted or renamed its instance variable `message`
  - Model `QuotaRequestDetails` deleted or renamed its instance variable `error`
  - Model `QuotaRequestDetails` deleted or renamed its instance variable `request_submit_time`
  - Model `QuotaRequestDetails` deleted or renamed its instance variable `value`
  - Model `QuotaRequestOneResourceSubmitResponse` deleted or renamed its instance variable `provisioning_state`
  - Model `QuotaRequestOneResourceSubmitResponse` deleted or renamed its instance variable `message`
  - Model `QuotaRequestOneResourceSubmitResponse` deleted or renamed its instance variable `request_submit_time`
  - Model `QuotaRequestOneResourceSubmitResponse` deleted or renamed its instance variable `limit`
  - Model `QuotaRequestOneResourceSubmitResponse` deleted or renamed its instance variable `current_value`
  - Model `QuotaRequestOneResourceSubmitResponse` deleted or renamed its instance variable `unit`
  - Model `QuotaRequestOneResourceSubmitResponse` deleted or renamed its instance variable `name_properties_name`
  - Model `QuotaRequestOneResourceSubmitResponse` deleted or renamed its instance variable `resource_type`
  - Model `QuotaRequestOneResourceSubmitResponse` deleted or renamed its instance variable `quota_period`
  - Model `QuotaRequestOneResourceSubmitResponse` deleted or renamed its instance variable `is_quota_applicable`
  - Model `QuotaRequestOneResourceSubmitResponse` deleted or renamed its instance variable `error`
  - Model `QuotaRequestSubmitResponse202` deleted or renamed its instance variable `provisioning_state`
  - Model `QuotaRequestSubmitResponse202` deleted or renamed its instance variable `message`
  - Model `QuotaRequestSubmitResponse202` deleted or renamed its instance variable `limit`
  - Model `QuotaRequestSubmitResponse202` deleted or renamed its instance variable `unit`
  - Model `QuotaRequestSubmitResponse202` deleted or renamed its instance variable `name_properties_name`
  - Model `QuotaRequestSubmitResponse202` deleted or renamed its instance variable `resource_type`
  - Model `QuotaRequestSubmitResponse202` deleted or renamed its instance variable `quota_period`

## 2.0.0b2 (2025-01-22)

### Features Added

  - Model `GroupQuotaDetails` added property `resource_name`
  - Model `GroupQuotaLimitList` added property `properties`
  - Model `GroupQuotaLimitList` added property `id`
  - Model `GroupQuotaLimitList` added property `name`
  - Model `GroupQuotaLimitList` added property `type`
  - Model `GroupQuotaLimitList` added property `system_data`
  - Model `SubscriptionQuotaAllocationsList` added property `properties`
  - Model `SubscriptionQuotaAllocationsList` added property `id`
  - Model `SubscriptionQuotaAllocationsList` added property `name`
  - Model `SubscriptionQuotaAllocationsList` added property `type`
  - Model `SubscriptionQuotaAllocationsList` added property `system_data`
  - Model `SubscriptionQuotaDetails` added property `resource_name`
  - Added model `GroupQuotaLimitListProperties`
  - Added model `GroupQuotaLimitProperties`
  - Added model `GroupQuotasEntityPatchProperties`
  - Added model `GroupQuotasEntityProperties`
  - Added model `SubscriptionQuotaAllocationsListProperties`
  - Added model `SubscriptionQuotaAllocationsProperties`

### Breaking Changes

  - Deleted or renamed client operation group `QuotaMgmtClient.group_quota_usages`
  - Deleted or renamed client operation group `QuotaMgmtClient.group_quota_location_settings`
  - Model `GroupQuotaDetails` deleted or renamed its instance variable `region`
  - Model `GroupQuotaLimit` deleted or renamed its instance variable `id`
  - Model `GroupQuotaLimit` deleted or renamed its instance variable `name`
  - Model `GroupQuotaLimit` deleted or renamed its instance variable `type`
  - Model `GroupQuotaLimit` deleted or renamed its instance variable `system_data`
  - Model `GroupQuotaLimitList` deleted or renamed its instance variable `value`
  - Model `GroupQuotaLimitList` deleted or renamed its instance variable `next_link`
  - Model `GroupQuotasEntityBase` deleted or renamed its instance variable `additional_attributes`
  - Model `GroupQuotasEntityBasePatch` deleted or renamed its instance variable `additional_attributes`
  - Model `SubscriptionQuotaAllocations` deleted or renamed its instance variable `id`
  - Model `SubscriptionQuotaAllocations` deleted or renamed its instance variable `name`
  - Model `SubscriptionQuotaAllocations` deleted or renamed its instance variable `type`
  - Model `SubscriptionQuotaAllocations` deleted or renamed its instance variable `system_data`
  - Model `SubscriptionQuotaAllocationsList` deleted or renamed its instance variable `value`
  - Model `SubscriptionQuotaAllocationsList` deleted or renamed its instance variable `next_link`
  - Model `SubscriptionQuotaDetails` deleted or renamed its instance variable `region`
  - Deleted or renamed model `AdditionalAttributes`
  - Deleted or renamed model `AdditionalAttributesPatch`
  - Deleted or renamed model `BillingAccountId`
  - Deleted or renamed model `EnforcementState`
  - Deleted or renamed model `EnvironmentType`
  - Deleted or renamed model `GroupQuotasEnforcementListResponse`
  - Deleted or renamed model `GroupQuotasEnforcementResponse`
  - Deleted or renamed model `GroupQuotasEnforcementResponseProperties`
  - Deleted or renamed model `GroupingId`
  - Deleted or renamed model `GroupingIdType`
  - Method `GroupQuotaLimitsOperations.list` inserted a `positional_or_keyword` parameter `location`
  - Method `GroupQuotaLimitsOperations.list` deleted or renamed its parameter `filter` of kind `positional_or_keyword`
  - Deleted or renamed method `GroupQuotaLimitsOperations.get`
  - Method `GroupQuotaLimitsRequestOperations.begin_update` inserted a `positional_or_keyword` parameter `location`
  - Method `GroupQuotaLimitsRequestOperations.begin_update` deleted or renamed its parameter `resource_name` of kind `positional_or_keyword`
  - Deleted or renamed method `GroupQuotaLimitsRequestOperations.begin_create_or_update`
  - Method `GroupQuotaSubscriptionAllocationOperations.list` inserted a `positional_or_keyword` parameter `resource_provider_name`
  - Method `GroupQuotaSubscriptionAllocationOperations.list` inserted a `positional_or_keyword` parameter `location`
  - Method `GroupQuotaSubscriptionAllocationOperations.list` deleted or renamed its parameter `filter` of kind `positional_or_keyword`
  - Deleted or renamed method `GroupQuotaSubscriptionAllocationOperations.get`
  - Method `GroupQuotaSubscriptionAllocationRequestOperations.begin_update` inserted a `positional_or_keyword` parameter `location`
  - Method `GroupQuotaSubscriptionAllocationRequestOperations.begin_update` deleted or renamed its parameter `resource_name` of kind `positional_or_keyword`
  - Method `GroupQuotaSubscriptionAllocationRequestOperations.get` inserted a `positional_or_keyword` parameter `resource_provider_name`
  - Deleted or renamed method `GroupQuotaSubscriptionAllocationRequestOperations.begin_create_or_update`
  - Deleted or renamed operation group `GroupQuotaLocationSettingsOperations`
  - Deleted or renamed operation group `GroupQuotaUsagesOperations`

## 2.0.0b1 (2024-04-22)

### Features Added

  - Added operation group GroupQuotaLimitsOperations
  - Added operation group GroupQuotaLimitsRequestOperations
  - Added operation group GroupQuotaLocationSettingsOperations
  - Added operation group GroupQuotaSubscriptionAllocationOperations
  - Added operation group GroupQuotaSubscriptionAllocationRequestOperations
  - Added operation group GroupQuotaSubscriptionRequestsOperations
  - Added operation group GroupQuotaSubscriptionsOperations
  - Added operation group GroupQuotaUsagesOperations
  - Added operation group GroupQuotasOperations
  - Model QuotaRequestDetails has a new parameter properties

### Breaking Changes

  - Model QuotaRequestDetails no longer has parameter error
  - Model QuotaRequestDetails no longer has parameter message
  - Model QuotaRequestDetails no longer has parameter provisioning_state
  - Model QuotaRequestDetails no longer has parameter request_submit_time
  - Model QuotaRequestDetails no longer has parameter value
  - Model QuotaRequestOneResourceSubmitResponse no longer has parameter current_value
  - Model QuotaRequestOneResourceSubmitResponse no longer has parameter error
  - Model QuotaRequestOneResourceSubmitResponse no longer has parameter is_quota_applicable
  - Model QuotaRequestOneResourceSubmitResponse no longer has parameter limit
  - Model QuotaRequestOneResourceSubmitResponse no longer has parameter message
  - Model QuotaRequestOneResourceSubmitResponse no longer has parameter name_properties_name
  - Model QuotaRequestOneResourceSubmitResponse no longer has parameter provisioning_state
  - Model QuotaRequestOneResourceSubmitResponse no longer has parameter quota_period
  - Model QuotaRequestOneResourceSubmitResponse no longer has parameter request_submit_time
  - Model QuotaRequestOneResourceSubmitResponse no longer has parameter resource_type
  - Model QuotaRequestOneResourceSubmitResponse no longer has parameter unit
  - Model QuotaRequestSubmitResponse202 no longer has parameter limit
  - Model QuotaRequestSubmitResponse202 no longer has parameter message
  - Model QuotaRequestSubmitResponse202 no longer has parameter name_properties_name
  - Model QuotaRequestSubmitResponse202 no longer has parameter provisioning_state
  - Model QuotaRequestSubmitResponse202 no longer has parameter quota_period
  - Model QuotaRequestSubmitResponse202 no longer has parameter resource_type
  - Model QuotaRequestSubmitResponse202 no longer has parameter unit

## 1.1.0 (2023-11-20)

### Other Changes

  - Fix for first GA

## 1.0.0 (2023-04-20)

### Breaking Changes

  - Client name is changed from `AzureQuotaExtensionAPI` to `QuotaMgmtClient`
  - First GA

## 1.1.0b3 (2022-11-09)

### Other Changes

  - Added generated samples in github repo
  - Drop support for python<3.7.0

## 1.0.0b2 (2021-11-01)

**Features**

  - Added operation group QuotaOperationOperations

**Breaking changes**

  - Parameter limit_object_type of model LimitObject is now required
  - Removed operation group OperationOperations

## 1.0.0b1 (2021-09-07)

* Initial Release
