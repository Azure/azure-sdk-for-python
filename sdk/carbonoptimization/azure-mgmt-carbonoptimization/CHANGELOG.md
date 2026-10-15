# Release History

## 2.0.0b1 (2026-10-15)

### Features Added

  - Client `CarbonOptimizationMgmtClient` added parameter `cloud_setting` in method `__init__`
  - Added enum `BillingAccountCategoryTypeEnum`
  - Added model `BillingAccountItemDetailsReportQueryFilter`
  - Added model `BillingAccountMonthlySummaryReportQueryFilter`
  - Added enum `BillingAccountOrderByColumnEnum`
  - Added model `BillingAccountOverallSummaryReportQueryFilter`
  - Added model `BillingAccountQueryFilter`
  - Added model `BillingAccountTopItemsMonthlySummaryReportQueryFilter`
  - Added model `BillingAccountTopItemsSummaryReportQueryFilter`
  - Operation group `CarbonServiceOperations` added method `query_carbon_emission_reports_by_billing_account`

### Breaking Changes

  - Method `CarbonServiceOperations.query_carbon_emission_reports` changed from `asynchronous` to `synchronous`
  - Method `CarbonServiceOperations.query_carbon_emission_reports` changed return type from `CarbonEmissionDataListResult` to `AsyncItemPaged[CarbonEmissionData]`
  - Method `CarbonServiceOperations.query_carbon_emission_reports` changed return type from `CarbonEmissionDataListResult` to `ItemPaged[CarbonEmissionData]`

## 1.0.0 (2025-07-21)

### Other Changes

  - First GA

## 1.0.0b1 (2025-05-08)

### Other Changes

  - Initial version
