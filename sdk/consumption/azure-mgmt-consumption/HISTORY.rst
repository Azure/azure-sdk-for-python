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
