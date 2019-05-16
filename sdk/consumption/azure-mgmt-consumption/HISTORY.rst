.. :changelog:

Release History
===============

3.0.0 (2018-05-16)
++++++++++++++++++

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
- Removed operation BudgetsOperations.create_or_update_by_resource_group_name
- Removed operation BudgetsOperations.get_by_resource_group_name
- Removed operation BudgetsOperations.list_by_resource_group_name
- Removed operation BudgetsOperations.delete_by_resource_group_name
- Removed operation UsageDetailsOperations.list_by_billing_period
- Removed operation MarketplacesOperations.list_by_billing_period

**General Breaking changes**

This version uses a next-generation code generator that *might* introduce breaking changes.

- Model signatures now use only keyword-argument syntax. All positional arguments must be re-written as keyword-arguments.
  To keep auto-completion in most cases, models are now generated for Python 2 and Python 3. Python 3 uses the "*" syntax for keyword-only arguments.
- Enum types now use the "str" mixin (class AzureEnum(str, Enum)) to improve the behavior when unrecognized enum values are encountered.
  While this is not a breaking change, the distinctions are important, and are documented here:
  https://docs.python.org/3/library/enum.html#others
  At a glance:

  - "is" should not be used at all.
  - "format" will return the string value, where "%s" string formatting will return `NameOfEnum.stringvalue`. Format syntax should be prefered.

- New Long Running Operation:

  - Return type changes from `msrestazure.azure_operation.AzureOperationPoller` to `msrest.polling.LROPoller`. External API is the same.
  - Return type is now **always** a `msrest.polling.LROPoller`, regardless of the optional parameters used.
  - The behavior has changed when using `raw=True`. Instead of returning the initial call result as `ClientRawResponse`,
    without polling, now this returns an LROPoller. After polling, the final resource will be returned as a `ClientRawResponse`.
  - New `polling` parameter. The default behavior is `Polling=True` which will poll using ARM algorithm. When `Polling=False`,
    the response of the initial call will be returned without polling.
  - `polling` parameter accepts instances of subclasses of `msrest.polling.PollingMethod`.
  - `add_done_callback` will no longer raise if called after polling is finished, but will instead execute the callback right away.

2.0.0 (2018-02-06)
++++++++++++++++++

**Features**

- Marketplace data with and without billing period
- Price sheets data with and without billing period
- Budget CRUD operations support

**Breaking changes**

- Removing scope from usage_details, reservation summaries and details operations.

1.1.0 (2017-12-12)
++++++++++++++++++

**Features**

- Reservation summaries based on Reservation Order Id and/or ReservationId
- Reservation details based on Reservation Order Id and/or ReservationId

1.0.0 (2017-11-15)
++++++++++++++++++

**Features**

- Featuring stable api GA version 2017-11-30
- Supporting EA customers with azure consumption usage details

**Breaking changes**

- Removing support for calling usage_details.list() with 'invoice_id'. Will feature in future releases.

0.1.0 (2017-05-18)
++++++++++++++++++

* Initial Release
