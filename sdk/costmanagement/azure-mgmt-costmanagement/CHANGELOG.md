# Release History

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
