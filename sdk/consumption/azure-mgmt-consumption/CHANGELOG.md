# Release History

## 10.1.0 (2026-05-22)

### Features Added

  - Client `ConsumptionManagementClient` added method `send_request`
  - Model `Balance` added property `system_data`
  - Model `Budget` added property `system_data`
  - Model `BudgetComparisonExpression` added property `values_property`
  - Enum `BudgetOperatorType` added member `IN_ENUM`
  - Model `ChargeSummary` added property `system_data`
  - Model `CreditSummary` added property `tags`
  - Model `CreditSummary` added property `system_data`
  - Model `EventSummary` added property `properties`
  - Model `EventSummary` added property `system_data`
  - Model `LegacyChargeSummary` added property `system_data`
  - Model `LegacyReservationRecommendation` added property `properties`
  - Model `LegacyReservationRecommendation` added property `system_data`
  - Model `LegacyUsageDetail` added property `system_data`
  - Model `LotSummary` added property `properties`
  - Model `LotSummary` added property `system_data`
  - Model `ManagementGroupAggregatedCostResult` added property `properties`
  - Model `ManagementGroupAggregatedCostResult` added property `system_data`
  - Model `Marketplace` added property `system_data`
  - Model `ModernChargeSummary` added property `system_data`
  - Model `ModernReservationRecommendation` added property `properties`
  - Model `ModernReservationRecommendation` added property `system_data`
  - Model `ModernReservationTransaction` added property `system_data`
  - Model `ModernUsageDetail` added property `system_data`
  - Model `OperationStatus` added property `properties`
  - Model `PriceSheetResult` added property `properties`
  - Model `PriceSheetResult` added property `system_data`
  - Model `ReservationDetail` added property `system_data`
  - Model `ReservationRecommendation` added property `system_data`
  - Model `ReservationRecommendationDetailsModel` added property `properties`
  - Model `ReservationRecommendationDetailsModel` added property `system_data`
  - Model `ReservationSummary` added property `system_data`
  - Model `ReservationTransaction` added property `properties`
  - Model `ReservationTransaction` added property `system_data`
  - Model `TagsResult` added property `properties`
  - Model `TagsResult` added property `system_data`
  - Model `UsageDetail` added property `system_data`
  - Added model `ArmErrorResponse`
  - Added model `ArmProxyResource`
  - Added model `ArmResource`
  - Added enum `CreatedByType`
  - Added model `EventProperties`
  - Added model `ExtensionResource`
  - Added model `LegacyReservationTransactionProperties`
  - Added model `LotProperties`
  - Added model `ManagementGroupAggregatedCostProperties`
  - Added model `PriceSheetModel`
  - Added model `PricesheetDownloadProperties`
  - Added model `ReservationRecommendationDetailsProperties`
  - Added model `SystemData`
  - Added model `TagProperties`

### Breaking Changes

  - Model `BudgetComparisonExpression` deleted or renamed its instance variable `values`
  - Deleted or renamed enum value `BudgetOperatorType.IN`
  - Model `EventSummary` deleted or renamed its instance variable `transaction_date`
  - Model `EventSummary` deleted or renamed its instance variable `description`
  - Model `EventSummary` deleted or renamed its instance variable `new_credit`
  - Model `EventSummary` deleted or renamed its instance variable `adjustments`
  - Model `EventSummary` deleted or renamed its instance variable `credit_expired`
  - Model `EventSummary` deleted or renamed its instance variable `charges`
  - Model `EventSummary` deleted or renamed its instance variable `closed_balance`
  - Model `EventSummary` deleted or renamed its instance variable `billing_account_id`
  - Model `EventSummary` deleted or renamed its instance variable `billing_account_display_name`
  - Model `EventSummary` deleted or renamed its instance variable `event_type`
  - Model `EventSummary` deleted or renamed its instance variable `invoice_number`
  - Model `EventSummary` deleted or renamed its instance variable `billing_profile_id`
  - Model `EventSummary` deleted or renamed its instance variable `billing_profile_display_name`
  - Model `EventSummary` deleted or renamed its instance variable `lot_id`
  - Model `EventSummary` deleted or renamed its instance variable `lot_source`
  - Model `EventSummary` deleted or renamed its instance variable `canceled_credit`
  - Model `EventSummary` deleted or renamed its instance variable `credit_currency`
  - Model `EventSummary` deleted or renamed its instance variable `billing_currency`
  - Model `EventSummary` deleted or renamed its instance variable `reseller`
  - Model `EventSummary` deleted or renamed its instance variable `credit_expired_in_billing_currency`
  - Model `EventSummary` deleted or renamed its instance variable `new_credit_in_billing_currency`
  - Model `EventSummary` deleted or renamed its instance variable `adjustments_in_billing_currency`
  - Model `EventSummary` deleted or renamed its instance variable `charges_in_billing_currency`
  - Model `EventSummary` deleted or renamed its instance variable `closed_balance_in_billing_currency`
  - Model `EventSummary` deleted or renamed its instance variable `is_estimated_balance`
  - Model `EventSummary` deleted or renamed its instance variable `e_tag_properties_e_tag`
  - Model `LegacyReservationRecommendation` deleted or renamed its instance variable `look_back_period`
  - Model `LegacyReservationRecommendation` deleted or renamed its instance variable `instance_flexibility_ratio`
  - Model `LegacyReservationRecommendation` deleted or renamed its instance variable `instance_flexibility_group`
  - Model `LegacyReservationRecommendation` deleted or renamed its instance variable `normalized_size`
  - Model `LegacyReservationRecommendation` deleted or renamed its instance variable `recommended_quantity_normalized`
  - Model `LegacyReservationRecommendation` deleted or renamed its instance variable `meter_id`
  - Model `LegacyReservationRecommendation` deleted or renamed its instance variable `resource_type`
  - Model `LegacyReservationRecommendation` deleted or renamed its instance variable `term`
  - Model `LegacyReservationRecommendation` deleted or renamed its instance variable `cost_with_no_reserved_instances`
  - Model `LegacyReservationRecommendation` deleted or renamed its instance variable `recommended_quantity`
  - Model `LegacyReservationRecommendation` deleted or renamed its instance variable `total_cost_with_reserved_instances`
  - Model `LegacyReservationRecommendation` deleted or renamed its instance variable `net_savings`
  - Model `LegacyReservationRecommendation` deleted or renamed its instance variable `first_usage_date`
  - Model `LegacyReservationRecommendation` deleted or renamed its instance variable `scope`
  - Model `LegacyReservationRecommendation` deleted or renamed its instance variable `sku_properties`
  - Model `LegacyReservationRecommendation` deleted or renamed its instance variable `last_usage_date`
  - Model `LegacyReservationRecommendation` deleted or renamed its instance variable `total_hours`
  - Model `LotSummary` deleted or renamed its instance variable `original_amount`
  - Model `LotSummary` deleted or renamed its instance variable `closed_balance`
  - Model `LotSummary` deleted or renamed its instance variable `source`
  - Model `LotSummary` deleted or renamed its instance variable `start_date`
  - Model `LotSummary` deleted or renamed its instance variable `expiration_date`
  - Model `LotSummary` deleted or renamed its instance variable `po_number`
  - Model `LotSummary` deleted or renamed its instance variable `purchased_date`
  - Model `LotSummary` deleted or renamed its instance variable `status`
  - Model `LotSummary` deleted or renamed its instance variable `credit_currency`
  - Model `LotSummary` deleted or renamed its instance variable `billing_currency`
  - Model `LotSummary` deleted or renamed its instance variable `original_amount_in_billing_currency`
  - Model `LotSummary` deleted or renamed its instance variable `closed_balance_in_billing_currency`
  - Model `LotSummary` deleted or renamed its instance variable `reseller`
  - Model `LotSummary` deleted or renamed its instance variable `is_estimated_balance`
  - Model `LotSummary` deleted or renamed its instance variable `e_tag_properties_e_tag`
  - Model `LotSummary` deleted or renamed its instance variable `organization_type`
  - Model `LotSummary` deleted or renamed its instance variable `used_amount`
  - Model `ManagementGroupAggregatedCostResult` deleted or renamed its instance variable `billing_period_id`
  - Model `ManagementGroupAggregatedCostResult` deleted or renamed its instance variable `usage_start`
  - Model `ManagementGroupAggregatedCostResult` deleted or renamed its instance variable `usage_end`
  - Model `ManagementGroupAggregatedCostResult` deleted or renamed its instance variable `azure_charges`
  - Model `ManagementGroupAggregatedCostResult` deleted or renamed its instance variable `marketplace_charges`
  - Model `ManagementGroupAggregatedCostResult` deleted or renamed its instance variable `charges_billed_separately`
  - Model `ManagementGroupAggregatedCostResult` deleted or renamed its instance variable `currency`
  - Model `ManagementGroupAggregatedCostResult` deleted or renamed its instance variable `children`
  - Model `ManagementGroupAggregatedCostResult` deleted or renamed its instance variable `included_subscriptions`
  - Model `ManagementGroupAggregatedCostResult` deleted or renamed its instance variable `excluded_subscriptions`
  - Model `ModernReservationRecommendation` deleted or renamed its instance variable `location_properties_location`
  - Model `ModernReservationRecommendation` deleted or renamed its instance variable `look_back_period`
  - Model `ModernReservationRecommendation` deleted or renamed its instance variable `instance_flexibility_ratio`
  - Model `ModernReservationRecommendation` deleted or renamed its instance variable `instance_flexibility_group`
  - Model `ModernReservationRecommendation` deleted or renamed its instance variable `normalized_size`
  - Model `ModernReservationRecommendation` deleted or renamed its instance variable `recommended_quantity_normalized`
  - Model `ModernReservationRecommendation` deleted or renamed its instance variable `meter_id`
  - Model `ModernReservationRecommendation` deleted or renamed its instance variable `term`
  - Model `ModernReservationRecommendation` deleted or renamed its instance variable `cost_with_no_reserved_instances`
  - Model `ModernReservationRecommendation` deleted or renamed its instance variable `recommended_quantity`
  - Model `ModernReservationRecommendation` deleted or renamed its instance variable `resource_type`
  - Model `ModernReservationRecommendation` deleted or renamed its instance variable `total_cost_with_reserved_instances`
  - Model `ModernReservationRecommendation` deleted or renamed its instance variable `net_savings`
  - Model `ModernReservationRecommendation` deleted or renamed its instance variable `first_usage_date`
  - Model `ModernReservationRecommendation` deleted or renamed its instance variable `scope`
  - Model `ModernReservationRecommendation` deleted or renamed its instance variable `sku_properties`
  - Model `ModernReservationRecommendation` deleted or renamed its instance variable `sku_name`
  - Model `ModernReservationRecommendation` deleted or renamed its instance variable `last_usage_date`
  - Model `ModernReservationRecommendation` deleted or renamed its instance variable `total_hours`
  - Model `OperationStatus` deleted or renamed its instance variable `download_url`
  - Model `OperationStatus` deleted or renamed its instance variable `valid_till`
  - Model `PriceSheetResult` deleted or renamed its instance variable `pricesheets`
  - Model `PriceSheetResult` deleted or renamed its instance variable `next_link`
  - Model `PriceSheetResult` deleted or renamed its instance variable `download`
  - Model `ReservationRecommendationDetailsModel` deleted or renamed its instance variable `currency`
  - Model `ReservationRecommendationDetailsModel` deleted or renamed its instance variable `resource`
  - Model `ReservationRecommendationDetailsModel` deleted or renamed its instance variable `resource_group`
  - Model `ReservationRecommendationDetailsModel` deleted or renamed its instance variable `savings`
  - Model `ReservationRecommendationDetailsModel` deleted or renamed its instance variable `scope`
  - Model `ReservationRecommendationDetailsModel` deleted or renamed its instance variable `usage`
  - Model `ReservationTransaction` deleted or renamed its instance variable `event_date`
  - Model `ReservationTransaction` deleted or renamed its instance variable `reservation_order_id`
  - Model `ReservationTransaction` deleted or renamed its instance variable `description`
  - Model `ReservationTransaction` deleted or renamed its instance variable `event_type`
  - Model `ReservationTransaction` deleted or renamed its instance variable `quantity`
  - Model `ReservationTransaction` deleted or renamed its instance variable `amount`
  - Model `ReservationTransaction` deleted or renamed its instance variable `currency`
  - Model `ReservationTransaction` deleted or renamed its instance variable `reservation_order_name`
  - Model `ReservationTransaction` deleted or renamed its instance variable `purchasing_enrollment`
  - Model `ReservationTransaction` deleted or renamed its instance variable `purchasing_subscription_guid`
  - Model `ReservationTransaction` deleted or renamed its instance variable `purchasing_subscription_name`
  - Model `ReservationTransaction` deleted or renamed its instance variable `arm_sku_name`
  - Model `ReservationTransaction` deleted or renamed its instance variable `term`
  - Model `ReservationTransaction` deleted or renamed its instance variable `region`
  - Model `ReservationTransaction` deleted or renamed its instance variable `account_name`
  - Model `ReservationTransaction` deleted or renamed its instance variable `account_owner_email`
  - Model `ReservationTransaction` deleted or renamed its instance variable `department_name`
  - Model `ReservationTransaction` deleted or renamed its instance variable `cost_center`
  - Model `ReservationTransaction` deleted or renamed its instance variable `current_enrollment`
  - Model `ReservationTransaction` deleted or renamed its instance variable `billing_frequency`
  - Model `ReservationTransaction` deleted or renamed its instance variable `billing_month`
  - Model `ReservationTransaction` deleted or renamed its instance variable `monetary_commitment`
  - Model `ReservationTransaction` deleted or renamed its instance variable `overage`
  - Model `TagsResult` deleted or renamed its instance variable `tags`
  - Model `TagsResult` deleted or renamed its instance variable `next_link`
  - Model `TagsResult` deleted or renamed its instance variable `previous_link`
  - Deleted or renamed model `DownloadProperties`
  - Deleted or renamed model `ErrorDetails`
  - Deleted or renamed model `ErrorResponse`
  - Deleted or renamed model `ErrorResponseAutoGenerated`
  - Deleted or renamed model `Events`
  - Deleted or renamed model `LegacyReservationTransaction`
  - Deleted or renamed model `Lots`
  - Deleted or renamed model `ProxyResource`
  - Deleted or renamed model `ReservationTransactionResource`
  - Deleted or renamed model `Resource`
  - Deleted or renamed model `ResourceAttributes`
  - Method `ChargesOperations.list` changed its parameter `start_date` from `positional_or_keyword` to `keyword_only`
  - Method `ChargesOperations.list` changed its parameter `end_date` from `positional_or_keyword` to `keyword_only`
  - Method `ChargesOperations.list` changed its parameter `apply` from `positional_or_keyword` to `keyword_only`
  - Method `EventsOperations.list_by_billing_profile` changed its parameter `start_date` from `positional_or_keyword` to `keyword_only`
  - Method `EventsOperations.list_by_billing_profile` changed its parameter `end_date` from `positional_or_keyword` to `keyword_only`
  - Method `MarketplacesOperations.list` changed its parameter `skiptoken` from `positional_or_keyword` to `keyword_only`
  - Method `PriceSheetOperations.get` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `PriceSheetOperations.get` changed its parameter `skiptoken` from `positional_or_keyword` to `keyword_only`
  - Method `PriceSheetOperations.get_by_billing_period` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `PriceSheetOperations.get_by_billing_period` changed its parameter `skiptoken` from `positional_or_keyword` to `keyword_only`
  - Method `ReservationRecommendationDetailsOperations.get` changed its parameter `scope` from `positional_or_keyword` to `keyword_only`
  - Method `ReservationRecommendationDetailsOperations.get` changed its parameter `region` from `positional_or_keyword` to `keyword_only`
  - Method `ReservationRecommendationDetailsOperations.get` changed its parameter `term` from `positional_or_keyword` to `keyword_only`
  - Method `ReservationRecommendationDetailsOperations.get` changed its parameter `look_back_period` from `positional_or_keyword` to `keyword_only`
  - Method `ReservationRecommendationDetailsOperations.get` changed its parameter `product` from `positional_or_keyword` to `keyword_only`
  - Method `ReservationTransactionsOperations.list` changed its parameter `use_markup_if_partner` from `positional_or_keyword` to `keyword_only`
  - Method `ReservationTransactionsOperations.list` changed its parameter `preview_markup_percentage` from `positional_or_keyword` to `keyword_only`
  - Method `ReservationsDetailsOperations.list` changed its parameter `start_date` from `positional_or_keyword` to `keyword_only`
  - Method `ReservationsDetailsOperations.list` changed its parameter `end_date` from `positional_or_keyword` to `keyword_only`
  - Method `ReservationsDetailsOperations.list` changed its parameter `reservation_id` from `positional_or_keyword` to `keyword_only`
  - Method `ReservationsDetailsOperations.list` changed its parameter `reservation_order_id` from `positional_or_keyword` to `keyword_only`
  - Method `ReservationsSummariesOperations.list` changed its parameter `grain` from `positional_or_keyword` to `keyword_only`
  - Method `ReservationsSummariesOperations.list` changed its parameter `start_date` from `positional_or_keyword` to `keyword_only`
  - Method `ReservationsSummariesOperations.list` changed its parameter `end_date` from `positional_or_keyword` to `keyword_only`
  - Method `ReservationsSummariesOperations.list` changed its parameter `reservation_id` from `positional_or_keyword` to `keyword_only`
  - Method `ReservationsSummariesOperations.list` changed its parameter `reservation_order_id` from `positional_or_keyword` to `keyword_only`
  - Method `ReservationsSummariesOperations.list_by_reservation_order` changed its parameter `grain` from `positional_or_keyword` to `keyword_only`
  - Method `ReservationsSummariesOperations.list_by_reservation_order_and_reservation` changed its parameter `grain` from `positional_or_keyword` to `keyword_only`
  - Method `UsageDetailsOperations.list` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `UsageDetailsOperations.list` changed its parameter `skiptoken` from `positional_or_keyword` to `keyword_only`
  - Method `UsageDetailsOperations.list` changed its parameter `metric` from `positional_or_keyword` to `keyword_only`

## 11.0.0b1 (2022-12-07)

### Features Added

  - Model ChargeSummary has a new parameter etag
  - Model ChargeSummary has a new parameter tags
  - Model CreditSummary has a new parameter e_tag_properties_e_tag
  - Model LegacyChargeSummary has a new parameter azure_marketplace_charges
  - Model LegacyChargeSummary has a new parameter etag
  - Model LegacyChargeSummary has a new parameter tags
  - Model ModernChargeSummary has a new parameter etag
  - Model ModernChargeSummary has a new parameter tags
  - Model ModernReservationRecommendation has a new parameter resource_type
  - Model ModernReservationRecommendation has a new parameter subscription_id

### Breaking Changes

  - Model ChargeSummary no longer has parameter e_tag
  - Model CreditSummary no longer has parameter etag
  - Model CreditSummary no longer has parameter tags
  - Model LegacyChargeSummary no longer has parameter e_tag
  - Model LegacyChargeSummary no longer has parameter marketplace_charges
  - Model ModernChargeSummary no longer has parameter e_tag

## 10.0.0 (2022-06-20)

**Features**

  - Added operation LotsOperations.list_by_customer

**Breaking changes**

  - Model BudgetFilter no longer has parameter not_property
  - Operation ReservationRecommendationDetailsOperations.get has a new parameter resource_scope
  - Operation ReservationRecommendationsOperations.list has a new parameter resource_scope
  - Operation ReservationRecommendationsOperations.list no longer has parameter scope
  - Operation ReservationsDetailsOperations.list has a new parameter resource_scope
  - Operation ReservationsDetailsOperations.list no longer has parameter scope
  - Operation ReservationsSummariesOperations.list has a new parameter resource_scope
  - Operation ReservationsSummariesOperations.list no longer has parameter scope

## 9.0.0 (2022-01-06)

**Features**

  - Added operation EventsOperations.list_by_billing_account
  - Added operation EventsOperations.list_by_billing_profile
  - Added operation LotsOperations.list_by_billing_account
  - Added operation LotsOperations.list_by_billing_profile
  - Model Balance has a new parameter etag
  - Model Budget has a new parameter forecast_spend
  - Model ChargeSummary has a new parameter e_tag
  - Model CreditBalanceSummary has a new parameter estimated_balance_in_billing_currency
  - Model CreditSummary has a new parameter billing_currency
  - Model CreditSummary has a new parameter credit_currency
  - Model CreditSummary has a new parameter e_tag
  - Model CreditSummary has a new parameter etag
  - Model CreditSummary has a new parameter reseller
  - Model EventSummary has a new parameter adjustments_in_billing_currency
  - Model EventSummary has a new parameter billing_currency
  - Model EventSummary has a new parameter billing_profile_display_name
  - Model EventSummary has a new parameter billing_profile_id
  - Model EventSummary has a new parameter canceled_credit
  - Model EventSummary has a new parameter charges_in_billing_currency
  - Model EventSummary has a new parameter closed_balance_in_billing_currency
  - Model EventSummary has a new parameter credit_currency
  - Model EventSummary has a new parameter credit_expired_in_billing_currency
  - Model EventSummary has a new parameter e_tag
  - Model EventSummary has a new parameter e_tag_properties_e_tag
  - Model EventSummary has a new parameter lot_id
  - Model EventSummary has a new parameter lot_source
  - Model EventSummary has a new parameter new_credit_in_billing_currency
  - Model EventSummary has a new parameter reseller
  - Model LegacyChargeSummary has a new parameter e_tag
  - Model LegacyReservationRecommendation has a new parameter etag
  - Model LegacyReservationRecommendation has a new parameter resource_type
  - Model LegacyReservationTransaction has a new parameter billing_month
  - Model LegacyReservationTransaction has a new parameter monetary_commitment
  - Model LegacyReservationTransaction has a new parameter overage
  - Model LegacyUsageDetail has a new parameter benefit_id
  - Model LegacyUsageDetail has a new parameter benefit_name
  - Model LegacyUsageDetail has a new parameter etag
  - Model LegacyUsageDetail has a new parameter pay_g_price
  - Model LegacyUsageDetail has a new parameter pricing_model
  - Model LotSummary has a new parameter billing_currency
  - Model LotSummary has a new parameter closed_balance_in_billing_currency
  - Model LotSummary has a new parameter credit_currency
  - Model LotSummary has a new parameter e_tag
  - Model LotSummary has a new parameter e_tag_properties_e_tag
  - Model LotSummary has a new parameter original_amount_in_billing_currency
  - Model LotSummary has a new parameter purchased_date
  - Model LotSummary has a new parameter reseller
  - Model LotSummary has a new parameter status
  - Model ManagementGroupAggregatedCostResult has a new parameter etag
  - Model Marketplace has a new parameter additional_info
  - Model Marketplace has a new parameter etag
  - Model ModernChargeSummary has a new parameter e_tag
  - Model ModernReservationRecommendation has a new parameter etag
  - Model ModernReservationRecommendation has a new parameter location_properties_location
  - Model ModernReservationRecommendation has a new parameter sku_name
  - Model ModernUsageDetail has a new parameter benefit_id
  - Model ModernUsageDetail has a new parameter benefit_name
  - Model ModernUsageDetail has a new parameter cost_allocation_rule_name
  - Model ModernUsageDetail has a new parameter effective_price
  - Model ModernUsageDetail has a new parameter etag
  - Model ModernUsageDetail has a new parameter pay_g_price
  - Model ModernUsageDetail has a new parameter pricing_model
  - Model ModernUsageDetail has a new parameter provider
  - Model Notification has a new parameter locale
  - Model Operation has a new parameter id
  - Model OperationDisplay has a new parameter description
  - Model PriceSheetResult has a new parameter download
  - Model PriceSheetResult has a new parameter etag
  - Model ReservationDetail has a new parameter etag
  - Model ReservationRecommendation has a new parameter etag
  - Model ReservationRecommendationDetailsModel has a new parameter etag
  - Model ReservationRecommendationsListResult has a new parameter previous_link
  - Model ReservationSummary has a new parameter etag
  - Model ReservationTransaction has a new parameter billing_month
  - Model ReservationTransaction has a new parameter monetary_commitment
  - Model ReservationTransaction has a new parameter overage
  - Model Resource has a new parameter etag
  - Model Tag has a new parameter value
  - Model TagsResult has a new parameter next_link
  - Model TagsResult has a new parameter previous_link
  - Model UsageDetail has a new parameter etag

**Breaking changes**

  - Model ChargeSummary no longer has parameter tags
  - Model EventSummary no longer has parameter tags
  - Model LegacyChargeSummary no longer has parameter tags
  - Model LotSummary no longer has parameter tags
  - Model ModernChargeSummary no longer has parameter tags
  - Operation ReservationRecommendationDetailsOperations.get has a new signature
  - Parameter scope of model LegacyReservationRecommendation is now required
  - Parameter scope of model LegacyReservationRecommendation is now required
  - Removed operation EventsOperations.list
  - Removed operation LotsOperations.list
  - Removed operation group ForecastsOperations

## 8.0.0 (2020-12-22)

**Features**

  - Model ReservationRecommendationDetailsCalculatedSavingsProperties has a new parameter reserved_unit_count
  - Model ReservationRecommendationDetailsModel has a new parameter location
  - Model ReservationRecommendationDetailsModel has a new parameter sku

## 8.0.0b1 (2020-10-31)

This is beta preview version.
For detailed changelog please refer to equivalent stable version 3.0.0(https://pypi.org/project/azure-mgmt-consumption/3.0.0/)

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
  - For a complete set of supported options, see the [parameters accept in Request documentation of azure-core](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#available-policies)

**General new features**

- Type annotations support using `typing`. SDKs are mypy ready.
- This client has now stable and official support for async. Check the `aio` namespace of your package to find the async client.
- This client now support natively tracing library like OpenCensus or OpenTelemetry. See this [tracing quickstart](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/core/azure-core-tracing-opentelemetry) for an overview.


## 3.0.0 (2018-05-16)

**Features**

  - Model MeterDetails has a new parameter service_name
  - Model MeterDetails has a new parameter service_tier
  - Model Filters has a new parameter tags
  - Model Marketplace has a new parameter is_recurring_charge
  - Model PriceSheetProperties has a new parameter offer_id
  - Added operation UsageDetailsOperations.download
  - Added operation group ForecastsOperations
  - Added operation group ChargesOperations
  - Added operation group TagsOperations
  - Added operation group BalancesOperations
  - Added operation group ReservationRecommendationsOperations
  - Added operation group AggregatedCostOperations

**Breaking changes**

  - Model UsageDetail has a new signature
  - Removed operation
    BudgetsOperations.create_or_update_by_resource_group_name
  - Removed operation BudgetsOperations.get_by_resource_group_name
  - Removed operation BudgetsOperations.list_by_resource_group_name
  - Removed operation
    BudgetsOperations.delete_by_resource_group_name
  - Removed operation UsageDetailsOperations.list_by_billing_period
  - Removed operation MarketplacesOperations.list_by_billing_period

**General Breaking changes**

This version uses a next-generation code generator that *might*
introduce breaking changes.

  - Model signatures now use only keyword-argument syntax. All
    positional arguments must be re-written as keyword-arguments. To
    keep auto-completion in most cases, models are now generated for
    Python 2 and Python 3. Python 3 uses the "*" syntax for
    keyword-only arguments.
  - Enum types now use the "str" mixin (class AzureEnum(str, Enum)) to
    improve the behavior when unrecognized enum values are encountered.
    While this is not a breaking change, the distinctions are important,
    and are documented here:
    <https://docs.python.org/3/library/enum.html#others> At a glance:
      - "is" should not be used at all.
      - "format" will return the string value, where "%s" string
        formatting will return `NameOfEnum.stringvalue`. Format syntax
        should be prefered.
  - New Long Running Operation:
      - Return type changes from
        `msrestazure.azure_operation.AzureOperationPoller` to
        `msrest.polling.LROPoller`. External API is the same.
      - Return type is now **always** a `msrest.polling.LROPoller`,
        regardless of the optional parameters used.
      - The behavior has changed when using `raw=True`. Instead of
        returning the initial call result as `ClientRawResponse`,
        without polling, now this returns an LROPoller. After polling,
        the final resource will be returned as a `ClientRawResponse`.
      - New `polling` parameter. The default behavior is
        `Polling=True` which will poll using ARM algorithm. When
        `Polling=False`, the response of the initial call will be
        returned without polling.
      - `polling` parameter accepts instances of subclasses of
        `msrest.polling.PollingMethod`.
      - `add_done_callback` will no longer raise if called after
        polling is finished, but will instead execute the callback right
        away.

## 2.0.0 (2018-02-06)

**Features**

  - Marketplace data with and without billing period
  - Price sheets data with and without billing period
  - Budget CRUD operations support

**Breaking changes**

  - Removing scope from usage_details, reservation summaries and
    details operations.

## 1.1.0 (2017-12-12)

**Features**

  - Reservation summaries based on Reservation Order Id and/or
    ReservationId
  - Reservation details based on Reservation Order Id and/or
    ReservationId

## 1.0.0 (2017-11-15)

**Features**

  - Featuring stable api GA version 2017-11-30
  - Supporting EA customers with azure consumption usage details

**Breaking changes**

  - Removing support for calling usage_details.list() with
    'invoice_id'. Will feature in future releases.

## 0.1.0 (2017-05-18)

  - Initial Release
