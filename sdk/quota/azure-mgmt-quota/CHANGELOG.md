# Release History

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
