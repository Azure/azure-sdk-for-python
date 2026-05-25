# Release History

## 4.1.0 (2026-05-25)

### Features Added

  - Client `CostManagementClient` added method `send_request`
  - Model `Alert` added property `system_data`
  - Model `BenefitRecommendationModel` added property `system_data`
  - Model `BenefitResource` added property `system_data`
  - Model `BenefitUtilizationSummary` added property `system_data`
  - Model `Budget` added property `system_data`
  - Model `BudgetComparisonExpression` added property `values_property`
  - Model `CostAllocationRuleDefinition` added property `system_data`
  - Model `CostDetailsOperationResults` added property `manifest`
  - Model `Export` added property `properties`
  - Model `Export` added property `system_data`
  - Model `ForecastComparisonExpression` added property `values_property`
  - Model `ForecastResult` added property `properties`
  - Model `GenerateDetailedCostReportOperationResult` added property `properties`
  - Model `GenerateDetailedCostReportOperationResult` added property `system_data`
  - Model `GenerateDetailedCostReportOperationStatuses` added property `properties`
  - Model `GenerateDetailedCostReportOperationStatuses` added property `system_data`
  - Model `IncludedQuantityUtilizationSummary` added property `properties`
  - Model `IncludedQuantityUtilizationSummary` added property `system_data`
  - Model `OperationStatus` added property `properties`
  - Model `ProxyResource` added property `system_data`
  - Model `QueryComparisonExpression` added property `values_property`
  - Model `QueryResult` added property `properties`
  - Model `ReportConfigComparisonExpression` added property `values_property`
  - Model `Resource` added property `system_data`
  - Model `SavingsPlanUtilizationSummary` added property `properties`
  - Model `SavingsPlanUtilizationSummary` added property `system_data`
  - Model `Setting` added property `system_data`
  - Model `SourceCostAllocationResource` added property `values_property`
  - Model `TagInheritanceSetting` added property `system_data`
  - Model `TargetCostAllocationResource` added property `values_property`
  - Model `View` added property `system_data`
  - Added model `ArmErrorResponse`
  - Added model `ExtensionResource`
  - Added model `ForecastProperties`
  - Added model `QueryProperties`
  - Added model `ReportConfigDefinition`
  - Added model `ReportManifest`
  - Added model `ReportURL`
  - Added model `RequestContext`
  - Model `ScheduledActionsOperations` added parameter `etag` in method `create_or_update`
  - Model `ScheduledActionsOperations` added parameter `match_condition` in method `create_or_update`
  - Model `ScheduledActionsOperations` added parameter `etag` in method `create_or_update_by_scope`
  - Model `ScheduledActionsOperations` added parameter `match_condition` in method `create_or_update_by_scope`

### Breaking Changes

  - Model `BudgetComparisonExpression` deleted or renamed its instance variable `values`
  - Model `CostDetailsOperationResults` deleted or renamed its instance variable `manifest_version`
  - Model `CostDetailsOperationResults` deleted or renamed its instance variable `data_format`
  - Model `CostDetailsOperationResults` deleted or renamed its instance variable `byte_count`
  - Model `CostDetailsOperationResults` deleted or renamed its instance variable `blob_count`
  - Model `CostDetailsOperationResults` deleted or renamed its instance variable `compress_data`
  - Model `CostDetailsOperationResults` deleted or renamed its instance variable `blobs`
  - Model `CostDetailsOperationResults` deleted or renamed its instance variable `request_scope`
  - Model `CostDetailsOperationResults` deleted or renamed its instance variable `request_body`
  - Model `DismissAlertPayload` deleted or renamed its instance variable `definition`
  - Model `DismissAlertPayload` deleted or renamed its instance variable `description`
  - Model `DismissAlertPayload` deleted or renamed its instance variable `source`
  - Model `DismissAlertPayload` deleted or renamed its instance variable `details`
  - Model `DismissAlertPayload` deleted or renamed its instance variable `cost_entity_id`
  - Model `DismissAlertPayload` deleted or renamed its instance variable `status`
  - Model `DismissAlertPayload` deleted or renamed its instance variable `creation_time`
  - Model `DismissAlertPayload` deleted or renamed its instance variable `close_time`
  - Model `DismissAlertPayload` deleted or renamed its instance variable `modification_time`
  - Model `DismissAlertPayload` deleted or renamed its instance variable `status_modification_user_name`
  - Model `DismissAlertPayload` deleted or renamed its instance variable `status_modification_time`
  - Model `Export` deleted or renamed its instance variable `format`
  - Model `Export` deleted or renamed its instance variable `delivery_info`
  - Model `Export` deleted or renamed its instance variable `definition`
  - Model `Export` deleted or renamed its instance variable `run_history`
  - Model `Export` deleted or renamed its instance variable `partition_data`
  - Model `Export` deleted or renamed its instance variable `data_overwrite_behavior`
  - Model `Export` deleted or renamed its instance variable `compression_mode`
  - Model `Export` deleted or renamed its instance variable `export_description`
  - Model `Export` deleted or renamed its instance variable `next_run_time_estimate`
  - Model `Export` deleted or renamed its instance variable `system_suspension_context`
  - Model `Export` deleted or renamed its instance variable `schedule`
  - Model `ForecastComparisonExpression` deleted or renamed its instance variable `values`
  - Model `ForecastResult` deleted or renamed its instance variable `next_link`
  - Model `ForecastResult` deleted or renamed its instance variable `columns`
  - Model `ForecastResult` deleted or renamed its instance variable `rows`
  - Model `GenerateDetailedCostReportOperationResult` deleted or renamed its instance variable `expiry_time`
  - Model `GenerateDetailedCostReportOperationResult` deleted or renamed its instance variable `valid_till`
  - Model `GenerateDetailedCostReportOperationResult` deleted or renamed its instance variable `download_url`
  - Model `GenerateDetailedCostReportOperationStatuses` deleted or renamed its instance variable `expiry_time`
  - Model `GenerateDetailedCostReportOperationStatuses` deleted or renamed its instance variable `valid_till`
  - Model `GenerateDetailedCostReportOperationStatuses` deleted or renamed its instance variable `download_url`
  - Model `IncludedQuantityUtilizationSummary` deleted or renamed its instance variable `arm_sku_name`
  - Model `IncludedQuantityUtilizationSummary` deleted or renamed its instance variable `benefit_id`
  - Model `IncludedQuantityUtilizationSummary` deleted or renamed its instance variable `benefit_order_id`
  - Model `IncludedQuantityUtilizationSummary` deleted or renamed its instance variable `benefit_type`
  - Model `IncludedQuantityUtilizationSummary` deleted or renamed its instance variable `usage_date`
  - Model `IncludedQuantityUtilizationSummary` deleted or renamed its instance variable `utilization_percentage`
  - Model `OperationStatus` deleted or renamed its instance variable `report_url`
  - Model `OperationStatus` deleted or renamed its instance variable `valid_until`
  - Deleted or renamed enum value `OperationStatusType.COMPLETE`
  - Model `QueryComparisonExpression` deleted or renamed its instance variable `values`
  - Model `QueryResult` deleted or renamed its instance variable `next_link`
  - Model `QueryResult` deleted or renamed its instance variable `columns`
  - Model `QueryResult` deleted or renamed its instance variable `rows`
  - Model `ReportConfigComparisonExpression` deleted or renamed its instance variable `values`
  - Model `SavingsPlanUtilizationSummary` deleted or renamed its instance variable `arm_sku_name`
  - Model `SavingsPlanUtilizationSummary` deleted or renamed its instance variable `benefit_id`
  - Model `SavingsPlanUtilizationSummary` deleted or renamed its instance variable `benefit_order_id`
  - Model `SavingsPlanUtilizationSummary` deleted or renamed its instance variable `benefit_type`
  - Model `SavingsPlanUtilizationSummary` deleted or renamed its instance variable `usage_date`
  - Model `SavingsPlanUtilizationSummary` deleted or renamed its instance variable `avg_utilization_percentage`
  - Model `SavingsPlanUtilizationSummary` deleted or renamed its instance variable `min_utilization_percentage`
  - Model `SavingsPlanUtilizationSummary` deleted or renamed its instance variable `max_utilization_percentage`
  - Model `SourceCostAllocationResource` deleted or renamed its instance variable `values`
  - Model `TargetCostAllocationResource` deleted or renamed its instance variable `values`
  - Deleted or renamed model `CostAllocationRuleList`
  - Deleted or renamed model `EAPriceSheetProperties`
  - Deleted or renamed model `ErrorDetailAutoGenerated`
  - Deleted or renamed model `ErrorResponseAutoGenerated`
  - Deleted or renamed model `ErrorResponseAutoGenerated2`
  - Renamed enum `KpiType` to `KpiTypeType`
  - Deleted or renamed model `OperationStatusAutoGenerated`
  - Renamed enum `PivotType` to `PivotTypeType`
  - Deleted or renamed model `ScheduledActionProxyResource`
  - Method `BenefitRecommendationsOperations.list` changed its parameter `orderby` from `positional_or_keyword` to `keyword_only`
  - Method `BenefitRecommendationsOperations.list` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `BenefitUtilizationSummariesOperations.list_by_billing_account_id` changed its parameter `grain_parameter` from `positional_or_keyword` to `keyword_only`
  - Method `BenefitUtilizationSummariesOperations.list_by_billing_profile_id` changed its parameter `grain_parameter` from `positional_or_keyword` to `keyword_only`
  - Method `BenefitUtilizationSummariesOperations.list_by_savings_plan_id` changed its parameter `grain_parameter` from `positional_or_keyword` to `keyword_only`
  - Method `BenefitUtilizationSummariesOperations.list_by_savings_plan_order` changed its parameter `grain_parameter` from `positional_or_keyword` to `keyword_only`
  - Method `DimensionsOperations.by_external_cloud_provider_type` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `DimensionsOperations.by_external_cloud_provider_type` changed its parameter `skiptoken` from `positional_or_keyword` to `keyword_only`
  - Method `DimensionsOperations.list` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `DimensionsOperations.list` changed its parameter `skiptoken` from `positional_or_keyword` to `keyword_only`
  - Method `ExportsOperations.get` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `ExportsOperations.list` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `GenerateReservationDetailsReportOperations.begin_by_billing_account_id` changed its parameter `start_date` from `positional_or_keyword` to `keyword_only`
  - Method `GenerateReservationDetailsReportOperations.begin_by_billing_account_id` changed its parameter `end_date` from `positional_or_keyword` to `keyword_only`
  - Method `GenerateReservationDetailsReportOperations.begin_by_billing_profile_id` changed its parameter `start_date` from `positional_or_keyword` to `keyword_only`
  - Method `GenerateReservationDetailsReportOperations.begin_by_billing_profile_id` changed its parameter `end_date` from `positional_or_keyword` to `keyword_only`
  - Method `ScheduledActionsOperations.create_or_update` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `ScheduledActionsOperations.create_or_update_by_scope` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `PriceSheetOperations.begin_download_by_billing_account` changed return type from `AsyncLROPoller[OperationStatusAutoGenerated]` to `AsyncLROPoller[OperationStatus]`
  - Method `PriceSheetOperations.begin_download_by_billing_account` changed return type from `LROPoller[OperationStatusAutoGenerated]` to `LROPoller[OperationStatus]`

## 4.0.1 (2023-07-19)

### Bugs Fixed

  - Fix deserialization error for some operation when error happens

## 4.0.0 (2023-05-22)

### Features Added

  - Added operation group BenefitRecommendationsOperations
  - Added operation group BenefitUtilizationSummariesOperations
  - Added operation group GenerateCostDetailsReportOperations
  - Added operation group GenerateDetailedCostReportOperationResultsOperations
  - Added operation group GenerateDetailedCostReportOperationStatusOperations
  - Added operation group GenerateDetailedCostReportOperations
  - Added operation group PriceSheetOperations
  - Added operation group ScheduledActionsOperations
  - Model Alert has a new parameter e_tag
  - Model AlertPropertiesDetails has a new parameter company_name
  - Model AlertPropertiesDetails has a new parameter department_name
  - Model AlertPropertiesDetails has a new parameter enrollment_end_date
  - Model AlertPropertiesDetails has a new parameter enrollment_number
  - Model AlertPropertiesDetails has a new parameter enrollment_start_date
  - Model AlertPropertiesDetails has a new parameter invoicing_threshold
  - Model CommonExportProperties has a new parameter next_run_time_estimate
  - Model CommonExportProperties has a new parameter partition_data
  - Model CommonExportProperties has a new parameter run_history
  - Model Dimension has a new parameter e_tag
  - Model Dimension has a new parameter location
  - Model Dimension has a new parameter sku
  - Model Export has a new parameter next_run_time_estimate
  - Model Export has a new parameter partition_data
  - Model Export has a new parameter run_history
  - Model ExportDeliveryDestination has a new parameter sas_token
  - Model ExportDeliveryDestination has a new parameter storage_account
  - Model ExportProperties has a new parameter next_run_time_estimate
  - Model ExportProperties has a new parameter partition_data
  - Model ExportProperties has a new parameter run_history
  - Model Operation has a new parameter action_type
  - Model Operation has a new parameter is_data_action
  - Model Operation has a new parameter origin
  - Model OperationDisplay has a new parameter description
  - Operation ExportsOperations.get has a new optional parameter expand
  - Operation ExportsOperations.list has a new optional parameter expand

### Breaking Changes

  - Model Alert no longer has parameter tags
  - Model ProxyResource no longer has parameter e_tag
  - Model ReportConfigFilter no longer has parameter tag_key
  - Model ReportConfigFilter no longer has parameter tag_value
  - Model Resource no longer has parameter tags
  - Removed operation group SettingsOperations

## 4.0.0b1 (2022-11-07)

### Features Added

  - Added operation group BenefitRecommendationsOperations
  - Added operation group BenefitUtilizationSummariesOperations
  - Added operation group GenerateCostDetailsReportOperations
  - Added operation group GenerateDetailedCostReportOperationResultsOperations
  - Added operation group GenerateDetailedCostReportOperationStatusOperations
  - Added operation group GenerateDetailedCostReportOperations
  - Added operation group PriceSheetOperations
  - Added operation group ScheduledActionsOperations
  - Model Alert has a new parameter e_tag
  - Model AlertPropertiesDetails has a new parameter company_name
  - Model AlertPropertiesDetails has a new parameter department_name
  - Model AlertPropertiesDetails has a new parameter enrollment_end_date
  - Model AlertPropertiesDetails has a new parameter enrollment_number
  - Model AlertPropertiesDetails has a new parameter enrollment_start_date
  - Model AlertPropertiesDetails has a new parameter invoicing_threshold
  - Model CommonExportProperties has a new parameter next_run_time_estimate
  - Model CommonExportProperties has a new parameter partition_data
  - Model CommonExportProperties has a new parameter run_history
  - Model Dimension has a new parameter e_tag
  - Model Dimension has a new parameter location
  - Model Dimension has a new parameter sku
  - Model Export has a new parameter next_run_time_estimate
  - Model Export has a new parameter partition_data
  - Model Export has a new parameter run_history
  - Model ExportDeliveryDestination has a new parameter sas_token
  - Model ExportDeliveryDestination has a new parameter storage_account
  - Model ExportProperties has a new parameter next_run_time_estimate
  - Model ExportProperties has a new parameter partition_data
  - Model ExportProperties has a new parameter run_history
  - Model Operation has a new parameter action_type
  - Model Operation has a new parameter is_data_action
  - Model Operation has a new parameter origin
  - Model OperationDisplay has a new parameter description

### Breaking Changes

  - Model Alert no longer has parameter tags
  - Model ProxyResource no longer has parameter e_tag
  - Model ReportConfigFilter no longer has parameter tag_key
  - Model ReportConfigFilter no longer has parameter tag_value
  - Model Resource no longer has parameter tags
  - Operation ExportsOperations.get has a new parameter expand
  - Operation ExportsOperations.list has a new parameter expand
  - Removed operation group SettingsOperations

## 3.0.0 (2021-07-27)

**Breaking changes**

  - Parameter dataset of model QueryDefinition is now required
  - Parameter dataset of model ForecastDefinition is now required

## 2.0.0 (2021-06-08)

**Features**

  - Model QueryResult has a new parameter sku
  - Model QueryResult has a new parameter e_tag
  - Model QueryResult has a new parameter location
  - Model View has a new parameter date_range
  - Model View has a new parameter data_set
  - Model View has a new parameter include_monetary_commitment
  - Model View has a new parameter currency
  - Model ExportExecution has a new parameter tags
  - Added operation group GenerateReservationDetailsReportOperations
  - Added operation group SettingsOperations

**Breaking changes**

  - Parameter recurrence of model ExportSchedule is now required
  - Operation ExportsOperations.list has a new signature
  - Operation ExportsOperations.get has a new signature
  - Model Export no longer has parameter run_history
  - Model Export no longer has parameter next_run_time_estimate
  - Model View no longer has parameter dataset
  - Model ExportExecution no longer has parameter e_tag
  - Model ExportExecution no longer has parameter error
  - Model CommonExportProperties no longer has parameter run_history
  - Model CommonExportProperties no longer has parameter next_run_time_estimate
  - Model ExportProperties no longer has parameter run_history
  - Model ExportProperties no longer has parameter next_run_time_estimate
  - Model QueryFilter has a new signature
  - Model ReportConfigFilter has a new signature

## 1.0.0 (2021-02-04)

**Features**

  - Model ExportExecution has a new parameter e_tag

**Breaking changes**

  - Model ExportExecution no longer has parameter tags

## 1.0.0b1 (2020-12-09)

This is beta preview version.

This version uses a next-generation code generator that introduces important breaking changes, but also important new features (like unified authentication and async programming).

**General breaking changes**

- Credential system has been completly revamped:

  - `azure.common.credentials` or `msrestazure.azure_active_directory` instances are no longer supported, use the `azure-identity` classes instead: https://pypi.org/project/azure-identity/
  - `credentials` parameter has been renamed `credential`

- The `config` attribute no longer exists on a client, configuration should be passed as kwarg. Example: `MyClient(credential, subscription_id, enable_logging=True)`. For a complete set of
  supported options, see the [parameters accept in init documentation of azure-core](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#available-policies)
- You can't import a `version` module anymore, use `__version__` instead
- Operations that used to return a `msrest.polling.LROPoller` now returns a `azure.core.polling.LROPoller` and are prefixed with `begin_`.
- Exceptions tree have been simplified and most exceptions are now `azure.core.exceptions.HttpResponseError` (`CloudError` has been removed).
- Most of the operation kwarg have changed. Some of the most noticeable:

  - `raw` has been removed. Equivalent feature can be found using `cls`, a callback that will give access to internal HTTP response for advanced user
  - For a complete set of
  supported options, see the [parameters accept in Request documentation of azure-core](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#available-policies)


## 0.2.0 (2020-04-08)

**Features**

  - Added operation DimensionsOperations.list
  - Added operation QueryOperations.usage

**Breaking changes**

  - Model QueryDataset no longer has parameter sorting
  - Removed operation DimensionsOperations.list_by_subscription
  - Removed operation QueryOperations.usage_by_scope

**General Breaking Changes**

This version uses a next-generation code generator that *might*
introduce breaking changes. In summary, some modules were incorrectly
visible/importable and have been renamed. This fixed several issues
caused by usage of classes that were not supposed to be used in the
first place.

  - CostManagementClient cannot be imported from
    `azure.mgmt.costmanagement.cost_management_client` anymore (import from
    `azure.mgmt.costmanagement` works like before)
  - CostManagementClientConfiguration import has been moved from
    `azure.mgmt.costmanagement.cost_management_client` to `azure.mgmt.costmanagement`
  - A model `MyClass` from a "models" sub-module cannot be imported
    anymore using `azure.mgmt.costmanagement.models.my_class` (import from
    `azure.mgmt.costmanagement.models` works like before)
  - An operation class `MyClassOperations` from an `operations`
    sub-module cannot be imported anymore using
    `azure.mgmt.costmanagement.operations.my_class_operations` (import from
    `azure.mgmt.costmanagement.operations` works like before)

Last but not least, HTTP connection pooling is now enabled by default.
You should always use a client as a context manager, or call close(), or
use no more than one client per process.

## 0.1.0 (2019-05-04)

  - Initial Release
