# Release History

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
