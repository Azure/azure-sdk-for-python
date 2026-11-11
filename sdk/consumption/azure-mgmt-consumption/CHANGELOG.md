# Release History

## 11.0.0 (2026-07-20)

### Features Added

  - Client `ConsumptionManagementClient` added parameter `cloud_setting` in method `__init__`
  - Client `ConsumptionManagementClient` added parameter `polling_interval` in method `__init__`
  - Client `ConsumptionManagementClient` added method `send_request`
  - Model `Balance` added property `system_data`
  - Model `Budget` added property `system_data`
  - Model `ChargeSummary` added property `etag`
  - Model `ChargeSummary` added property `system_data`
  - Model `CreditSummary` added property `system_data`
  - Model `EventSummary` added property `system_data`
  - Model `LegacyChargeSummary` added property `etag`
  - Model `LegacyChargeSummary` added property `system_data`
  - Model `LegacyReservationRecommendation` added property `system_data`
  - Model `LegacyReservationRecommendationProperties` added property `last_usage_date`
  - Model `LegacyReservationRecommendationProperties` added property `total_hours`
  - Model `LegacySharedScopeReservationRecommendationProperties` added property `last_usage_date`
  - Model `LegacySharedScopeReservationRecommendationProperties` added property `total_hours`
  - Model `LegacySingleScopeReservationRecommendationProperties` added property `last_usage_date`
  - Model `LegacySingleScopeReservationRecommendationProperties` added property `total_hours`
  - Model `LegacyUsageDetail` added property `system_data`
  - Model `LotSummary` added property `system_data`
  - Model `ManagementGroupAggregatedCostResult` added property `system_data`
  - Model `Marketplace` added property `system_data`
  - Model `ModernChargeSummary` added property `etag`
  - Model `ModernChargeSummary` added property `system_data`
  - Model `ModernReservationRecommendation` added property `system_data`
  - Model `ModernReservationTransaction` added property `system_data`
  - Model `ModernUsageDetail` added property `system_data`
  - Model `PriceSheetProperties` added property `savings_plan`
  - Model `PriceSheetResult` added property `system_data`
  - Model `ProxyResource` added property `system_data`
  - Model `ReservationDetail` added property `system_data`
  - Model `ReservationRecommendation` added property `system_data`
  - Model `ReservationRecommendationDetailsModel` added property `system_data`
  - Model `ReservationSummary` added property `system_data`
  - Model `ReservationTransaction` added property `system_data`
  - Model `Resource` added property `system_data`
  - Model `TagsResult` added property `system_data`
  - Enum `Term` added member `P1_M`
  - Model `UsageDetail` added property `system_data`
  - Added enum `CreatedByType`
  - Added model `ErrorAdditionalInfo`
  - Added model `ExtensionResource`
  - Added model `ModernSharedScopeReservationRecommendationProperties`
  - Added model `ModernSingleScopeReservationRecommendationProperties`
  - Added model `OperationStatus`
  - Added enum `OperationStatusType`
  - Added enum `OrganizationType`
  - Added model `PricesheetDownloadProperties`
  - Added model `SavingsPlan`
  - Added model `SystemData`
  - Operation group `BudgetsOperations` added parameter `content_type` in method `create_or_update`
  - Operation group `PriceSheetOperations` added method `begin_download_by_billing_account_period`
  - Operation group `ReservationRecommendationDetailsOperations` added parameter `filter` in method `get`
  - Operation group `ReservationTransactionsOperations` added parameter `preview_markup_percentage` in method `list`
  - Operation group `ReservationTransactionsOperations` added parameter `use_markup_if_partner` in method `list`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. Please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - For the method breakings, please refer to https://aka.ms/azsdk/python/migrate/operations for migration.
  - Model `Balance` moved instance variable `adjustment_details`, `adjustments`, `azure_marketplace_service_charges`, `beginning_balance`, `billing_frequency`, `charges_billed_separately`, `currency`, `ending_balance`, `new_purchases`, `new_purchases_details`, `price_hidden`, `service_overage`, `total_overage`, `total_usage` and `utilized` under property `properties` whose type is `BalanceProperties`
  - Model `Budget` moved instance variable `amount`, `category`, `current_spend`, `filter`, `forecast_spend`, `notifications`, `time_grain` and `time_period` under property `properties` whose type is `BudgetProperties`
  - Model `BudgetComparisonExpression` renamed its instance variable `values` to `values_property`
  - Renamed enum value `BudgetOperatorType.IN_ENUM` to `IN`
  - Model `CreditSummary` moved instance variable `balance_summary`, `billing_currency`, `credit_currency`, `expired_credit`, `pending_credit_adjustments`, `pending_eligible_charges` and `reseller` under property `properties` whose type is `CreditSummaryProperties`
  - Model `EventSummary` moved instance variable `adjustments`, `adjustments_in_billing_currency`, `billing_currency`, `billing_profile_display_name`, `billing_profile_id`, `canceled_credit`, `charges`, `charges_in_billing_currency`, `closed_balance`, `closed_balance_in_billing_currency`, `credit_currency`, `credit_expired`, `credit_expired_in_billing_currency`, `description`, `event_type`, `invoice_number`, `lot_id`, `lot_source`, `new_credit`, `new_credit_in_billing_currency`, `reseller` and `transaction_date` under property `properties` whose type is `EventProperties`
  - Model `LegacyChargeSummary` moved instance variable `azure_charges`, `billing_period_id`, `charges_billed_separately`, `currency`, `usage_end` and `usage_start` under property `properties` whose type is `LegacyChargeSummaryProperties`
  - Model `LegacyReservationRecommendation` moved instance variable `cost_with_no_reserved_instances`, `first_usage_date`, `instance_flexibility_group`, `instance_flexibility_ratio`, `look_back_period`, `meter_id`, `net_savings`, `normalized_size`, `recommended_quantity`, `recommended_quantity_normalized`, `resource_type`, `scope`, `sku_properties`, `term` and `total_cost_with_reserved_instances` under property `properties` whose type is `LegacyReservationRecommendationProperties`
  - Model `LegacyUsageDetail` moved instance variable `account_name`, `account_owner_id`, `additional_info`, `benefit_id`, `benefit_name`, `billing_account_id`, `billing_account_name`, `billing_currency`, `billing_period_end_date`, `billing_period_start_date`, `billing_profile_id`, `billing_profile_name`, `charge_type`, `consumed_service`, `cost`, `cost_center`, `date`, `effective_price`, `frequency`, `invoice_section`, `is_azure_credit_eligible`, `meter_details`, `meter_id`, `offer_id`, `part_number`, `pay_g_price`, `plan_name`, `pricing_model`, `product`, `product_order_id`, `product_order_name`, `publisher_name`, `publisher_type`, `quantity`, `reservation_id`, `reservation_name`, `resource_group`, `resource_id`, `resource_location`, `resource_name`, `service_info1`, `service_info2`, `subscription_id`, `subscription_name`, `term` and `unit_price` under property `properties` whose type is `LegacyUsageDetailProperties`
  - Model `LotSummary` moved instance variable `billing_currency`, `closed_balance`, `closed_balance_in_billing_currency`, `credit_currency`, `expiration_date`, `original_amount`, `original_amount_in_billing_currency`, `po_number`, `purchased_date`, `reseller`, `source`, `start_date` and `status` under property `properties` whose type is `LotProperties`
  - Model `ManagementGroupAggregatedCostResult` moved instance variable `azure_charges`, `billing_period_id`, `charges_billed_separately`, `children`, `currency`, `excluded_subscriptions`, `included_subscriptions`, `marketplace_charges`, `usage_end` and `usage_start` under property `properties` whose type is `ManagementGroupAggregatedCostProperties`
  - Model `Marketplace` moved instance variable `account_name`, `additional_info`, `billing_period_id`, `consumed_quantity`, `consumed_service`, `cost_center`, `currency`, `department_name`, `instance_id`, `instance_name`, `is_estimated`, `is_recurring_charge`, `meter_id`, `offer_name`, `order_number`, `plan_name`, `pretax_cost`, `publisher_name`, `resource_group`, `resource_rate`, `subscription_guid`, `subscription_name`, `unit_of_measure`, `usage_end` and `usage_start` under property `properties` whose type is `MarketplaceProperties`
  - Model `ModernChargeSummary` moved instance variable `azure_charges`, `billing_account_id`, `billing_period_id`, `billing_profile_id`, `charges_billed_separately`, `customer_id`, `invoice_section_id`, `is_invoiced`, `marketplace_charges`, `usage_end` and `usage_start` under property `properties` whose type is `ModernChargeSummaryProperties`
  - Model `ModernReservationRecommendation` moved instance variable `cost_with_no_reserved_instances`, `first_usage_date`, `instance_flexibility_group`, `instance_flexibility_ratio`, `look_back_period`, `meter_id`, `net_savings`, `normalized_size`, `recommended_quantity`, `recommended_quantity_normalized`, `scope`, `sku_name`, `sku_properties`, `term` and `total_cost_with_reserved_instances` under property `properties` whose type is `ModernReservationRecommendationProperties`
  - Model `ModernReservationTransaction` moved instance variable `amount`, `arm_sku_name`, `billing_frequency`, `billing_profile_id`, `billing_profile_name`, `currency`, `description`, `event_date`, `event_type`, `invoice`, `invoice_id`, `invoice_section_id`, `invoice_section_name`, `purchasing_subscription_guid`, `purchasing_subscription_name`, `quantity`, `region`, `reservation_order_id`, `reservation_order_name` and `term` under property `properties` whose type is `ModernReservationTransactionProperties`
  - Model `ModernUsageDetail` moved instance variable `additional_info`, `benefit_id`, `benefit_name`, `billing_account_id`, `billing_account_name`, `billing_currency_code`, `billing_period_end_date`, `billing_period_start_date`, `billing_profile_id`, `billing_profile_name`, `charge_type`, `consumed_service`, `cost_allocation_rule_name`, `cost_center`, `cost_in_billing_currency`, `cost_in_pricing_currency`, `cost_in_usd`, `customer_name`, `customer_tenant_id`, `date`, `effective_price`, `exchange_rate`, `exchange_rate_date`, `exchange_rate_pricing_to_billing`, `frequency`, `instance_name`, `invoice_id`, `invoice_section_id`, `invoice_section_name`, `is_azure_credit_eligible`, `market_price`, `meter_category`, `meter_id`, `meter_name`, `meter_region`, `meter_sub_category`, `partner_earned_credit_applied`, `partner_earned_credit_rate`, `partner_name`, `partner_tenant_id`, `pay_g_price`, `payg_cost_in_billing_currency`, `payg_cost_in_usd`, `previous_invoice_id`, `pricing_currency_code`, `pricing_model`, `product`, `product_identifier`, `product_order_id`, `product_order_name`, `provider`, `publisher_id`, `publisher_name`, `publisher_type`, `quantity`, `reseller_mpn_id`, `reseller_name`, `reservation_id`, `reservation_name`, `resource_group`, `resource_location`, `resource_location_normalized`, `service_family`, `service_info1`, `service_info2`, `service_period_end_date`, `service_period_start_date`, `subscription_guid`, `subscription_name`, `term`, `unit_of_measure` and `unit_price` under property `properties` whose type is `ModernUsageDetailProperties`
  - Model `PriceSheetResult` moved instance variable `download`, `next_link` and `pricesheets` under property `properties` whose type is `PriceSheetModel`
  - Model `ReservationDetail` moved instance variable `instance_flexibility_group`, `instance_flexibility_ratio`, `instance_id`, `kind`, `reservation_id`, `reservation_order_id`, `reserved_hours`, `sku_name`, `total_reserved_quantity`, `usage_date` and `used_hours` under property `properties` whose type is `ReservationDetailProperties`
  - Model `ReservationRecommendationDetailsModel` moved instance variable `currency`, `resource`, `resource_group`, `savings`, `scope` and `usage` under property `properties` whose type is `ReservationRecommendationDetailsProperties`
  - Model `ReservationSummary` moved instance variable `avg_utilization_percentage`, `kind`, `max_utilization_percentage`, `min_utilization_percentage`, `purchased_quantity`, `remaining_quantity`, `reservation_id`, `reservation_order_id`, `reserved_hours`, `sku_name`, `total_reserved_quantity`, `usage_date`, `used_hours`, `used_quantity` and `utilized_percentage` under property `properties` whose type is `ReservationSummaryProperties`
  - Model `ReservationTransaction` moved instance variable `account_name`, `account_owner_email`, `amount`, `arm_sku_name`, `billing_frequency`, `billing_month`, `cost_center`, `currency`, `current_enrollment`, `department_name`, `description`, `event_date`, `event_type`, `monetary_commitment`, `overage`, `purchasing_enrollment`, `purchasing_subscription_guid`, `purchasing_subscription_name`, `quantity`, `region`, `reservation_order_id`, `reservation_order_name` and `term` under property `properties` whose type is `LegacyReservationTransactionProperties`
  - Model `TagsResult` moved instance variable `next_link`, `previous_link` and `tags` under property `properties` whose type is `TagProperties`
  - Model `Resource` deleted or renamed its instance variable `etag`
  - Model `Resource` deleted or renamed its instance variable `tags`
  - Model `LegacyChargeSummary` deleted or renamed its instance variable `e_tag`
  - Model `LegacyChargeSummary` deleted or renamed its instance variable `marketplace_charges`
  - Model `ModernChargeSummary` deleted or renamed its instance variable `e_tag`
  - Model `ChargeSummary` deleted or renamed its instance variable `e_tag`
  - Model `ProxyResource` deleted or renamed its instance variable `e_tag`
  - Model `EventSummary` deleted or renamed its instance variable `e_tag_properties_e_tag`
  - Model `LotSummary` deleted or renamed its instance variable `e_tag_properties_e_tag`
  - Model `ModernReservationRecommendation` deleted or renamed its instance variable `location_properties_location`
  - Renamed model `ErrorDetails` to `ErrorDetail`
  - Method `ChargesOperations.list` changed its parameter `apply`/`end_date`/`start_date` from `positional_or_keyword` to `keyword_only`
  - Method `EventsOperations.list_by_billing_profile` changed its parameter `end_date`/`start_date` from `positional_or_keyword` to `keyword_only`
  - Method `MarketplacesOperations.list` changed its parameter `skiptoken` from `positional_or_keyword` to `keyword_only`
  - Method `PriceSheetOperations.get` changed its parameter `expand`/`skiptoken` from `positional_or_keyword` to `keyword_only`
  - Method `PriceSheetOperations.get_by_billing_period` changed its parameter `expand`/`skiptoken` from `positional_or_keyword` to `keyword_only`
  - Method `ReservationRecommendationDetailsOperations.get` changed its parameter `look_back_period`/`product`/`region`/`scope`/`term` from `positional_or_keyword` to `keyword_only`
  - Method `ReservationsDetailsOperations.list` changed its parameter `end_date`/`reservation_id`/`reservation_order_id`/`start_date` from `positional_or_keyword` to `keyword_only`
  - Method `ReservationsSummariesOperations.list` changed its parameter `end_date`/`grain`/`reservation_id`/`reservation_order_id`/`start_date` from `positional_or_keyword` to `keyword_only`
  - Method `ReservationsSummariesOperations.list_by_reservation_order` changed its parameter `grain` from `positional_or_keyword` to `keyword_only`
  - Method `ReservationsSummariesOperations.list_by_reservation_order_and_reservation` changed its parameter `grain` from `positional_or_keyword` to `keyword_only`
  - Method `UsageDetailsOperations.list` changed its parameter `expand`/`metric`/`skiptoken` from `positional_or_keyword` to `keyword_only`

### Other Changes

  - Deleted model `BudgetsListResult`/`Events`/`Lots`/`MarketplacesListResult`/`ModernReservationTransactionsListResult`/`OperationListResult`/`ReservationDetailsListResult`/`ReservationSummariesListResult`/`ReservationTransactionsListResult`/`UsageDetailsListResult` which actually were not used by SDK users
  - Deleted model `DownloadProperties`/`LegacyReservationTransaction`/`ReservationRecommendationsListResult`/`ReservationTransactionResource`/`ResourceAttributes` which actually were not used by SDK users
  - Method `BudgetsOperations.list` changed return type from `Iterable[BudgetsListResult]` to `ItemPaged[Budget]`
  - Method `EventsOperations.list_by_billing_account` changed return type from `Iterable[Events]` to `ItemPaged[EventSummary]`
  - Method `EventsOperations.list_by_billing_profile` changed return type from `Iterable[Events]` to `ItemPaged[EventSummary]`
  - Method `LotsOperations.list_by_billing_account` changed return type from `Iterable[Lots]` to `ItemPaged[LotSummary]`
  - Method `LotsOperations.list_by_billing_profile` changed return type from `Iterable[Lots]` to `ItemPaged[LotSummary]`
  - Method `LotsOperations.list_by_customer` changed return type from `Iterable[Lots]` to `ItemPaged[LotSummary]`
  - Method `MarketplacesOperations.list` changed return type from `Iterable[MarketplacesListResult]` to `ItemPaged[Marketplace]`
  - Method `Operations.list` changed return type from `Iterable[OperationListResult]` to `ItemPaged[Operation]`
  - Method `ReservationRecommendationsOperations.list` changed return type from `Iterable[ReservationRecommendationsListResult]` to `ItemPaged[ReservationRecommendation]`
  - Method `ReservationTransactionsOperations.list` changed return type from `Iterable[ReservationTransactionsListResult]` to `ItemPaged[ReservationTransaction]`
  - Method `ReservationTransactionsOperations.list_by_billing_profile` changed return type from `Iterable[ModernReservationTransactionsListResult]` to `ItemPaged[ModernReservationTransaction]`
  - Method `ReservationsDetailsOperations.list` changed return type from `Iterable[ReservationDetailsListResult]` to `ItemPaged[ReservationDetail]`
  - Method `ReservationsDetailsOperations.list_by_reservation_order` changed return type from `Iterable[ReservationDetailsListResult]` to `ItemPaged[ReservationDetail]`
  - Method `ReservationsDetailsOperations.list_by_reservation_order_and_reservation` changed return type from `Iterable[ReservationDetailsListResult]` to `ItemPaged[ReservationDetail]`
  - Method `ReservationsSummariesOperations.list` changed return type from `Iterable[ReservationSummariesListResult]` to `ItemPaged[ReservationSummary]`
  - Method `ReservationsSummariesOperations.list_by_reservation_order` changed return type from `Iterable[ReservationSummariesListResult]` to `ItemPaged[ReservationSummary]`
  - Method `ReservationsSummariesOperations.list_by_reservation_order_and_reservation` changed return type from `Iterable[ReservationSummariesListResult]` to `ItemPaged[ReservationSummary]`
  - Method `UsageDetailsOperations.list` changed return type from `Iterable[UsageDetailsListResult]` to `ItemPaged[UsageDetail]`

## 11.0.0b2 (2026-05-25)

### Features Added

  - Client `ConsumptionManagementClient` added parameter `cloud_setting` in method `__init__`
  - Client `ConsumptionManagementClient` added method `send_request`
  - Model `Balance` added property `system_data`
  - Model `Budget` added property `system_data`
  - Model `ChargeSummary` added property `system_data`
  - Model `CreditSummary` added property `tags`
  - Model `CreditSummary` added property `system_data`
  - Model `EventSummary` added property `system_data`
  - Model `LegacyChargeSummary` added property `system_data`
  - Model `LegacyReservationRecommendation` added property `system_data`
  - Model `LegacyReservationRecommendationProperties` added property `last_usage_date`
  - Model `LegacyReservationRecommendationProperties` added property `total_hours`
  - Model `LegacySharedScopeReservationRecommendationProperties` added property `last_usage_date`
  - Model `LegacySharedScopeReservationRecommendationProperties` added property `total_hours`
  - Model `LegacySingleScopeReservationRecommendationProperties` added property `last_usage_date`
  - Model `LegacySingleScopeReservationRecommendationProperties` added property `total_hours`
  - Model `LegacyUsageDetail` added property `system_data`
  - Model `LotSummary` added property `system_data`
  - Model `ManagementGroupAggregatedCostResult` added property `system_data`
  - Model `Marketplace` added property `system_data`
  - Model `ModernChargeSummary` added property `system_data`
  - Model `ModernReservationRecommendation` added property `system_data`
  - Model `ModernReservationRecommendationProperties` added property `last_usage_date`
  - Model `ModernReservationRecommendationProperties` added property `total_hours`
  - Model `ModernReservationTransaction` added property `system_data`
  - Model `ModernSharedScopeReservationRecommendationProperties` added property `last_usage_date`
  - Model `ModernSharedScopeReservationRecommendationProperties` added property `total_hours`
  - Model `ModernSingleScopeReservationRecommendationProperties` added property `last_usage_date`
  - Model `ModernSingleScopeReservationRecommendationProperties` added property `total_hours`
  - Model `ModernUsageDetail` added property `system_data`
  - Model `PriceSheetProperties` added property `savings_plan`
  - Model `PriceSheetResult` added property `system_data`
  - Model `ProxyResource` added property `system_data`
  - Model `ReservationDetail` added property `system_data`
  - Model `ReservationRecommendation` added property `system_data`
  - Model `ReservationRecommendationDetailsModel` added property `system_data`
  - Model `ReservationSummary` added property `system_data`
  - Model `ReservationTransaction` added property `system_data`
  - Model `Resource` added property `system_data`
  - Model `TagsResult` added property `system_data`
  - Enum `Term` added member `P1_M`
  - Model `UsageDetail` added property `system_data`
  - Added enum `CreatedByType`
  - Added model `ErrorAdditionalInfo`
  - Added model `ErrorDetail`
  - Added model `ExtensionResource`
  - Added model `OperationStatus`
  - Added enum `OperationStatusType`
  - Added enum `OrganizationType`
  - Added model `PricesheetDownloadProperties`
  - Added model `SavingsPlan`
  - Added model `SystemData`
  - Operation group `PriceSheetOperations` added method `begin_download_by_billing_account_period`
  - Operation group `ReservationRecommendationDetailsOperations` added parameter `filter` in method `get`
  - Operation group `ReservationTransactionsOperations` added parameter `use_markup_if_partner` in method `list`
  - Operation group `ReservationTransactionsOperations` added parameter `preview_markup_percentage` in method `list`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. Please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - For the method breakings, please refer to https://aka.ms/azsdk/python/migrate/operations for migration.
  - Model `BudgetComparisonExpression` renamed its instance variable `values` to `values_property`
  - Model `ChargeSummary` deleted or renamed its instance variable `tags`
  - Model `EventSummary` moved instance variable `transaction_date`, `description`, `new_credit`, `adjustments`, `credit_expired`, `charges`, `closed_balance`, `event_type`, `invoice_number`, `billing_profile_id`, `billing_profile_display_name`, `lot_id`, `lot_source`, `canceled_credit`, `credit_currency`, `billing_currency`, `reseller`, `credit_expired_in_billing_currency`, `new_credit_in_billing_currency`, `adjustments_in_billing_currency`, `charges_in_billing_currency`, `closed_balance_in_billing_currency` and `e_tag_properties_e_tag` under property `properties` whose type is `EventProperties`
  - Model `LegacyReservationRecommendation` moved instance variable `look_back_period`, `instance_flexibility_ratio`, `instance_flexibility_group`, `normalized_size`, `recommended_quantity_normalized`, `meter_id`, `resource_type`, `term`, `cost_with_no_reserved_instances`, `recommended_quantity`, `total_cost_with_reserved_instances`, `net_savings`, `first_usage_date`, `scope` and `sku_properties` under property `properties` whose type is `LegacyReservationRecommendationProperties`
  - Model `LotSummary` moved instance variable `original_amount`, `closed_balance`, `source`, `start_date`, `expiration_date`, `po_number`, `purchased_date`, `status`, `credit_currency`, `billing_currency`, `original_amount_in_billing_currency`, `closed_balance_in_billing_currency`, `reseller` and `e_tag_properties_e_tag` under property `properties` whose type is `LotProperties`
  - Model `ManagementGroupAggregatedCostResult` moved instance variable `billing_period_id`, `usage_start`, `usage_end`, `azure_charges`, `marketplace_charges`, `charges_billed_separately`, `currency`, `children`, `included_subscriptions` and `excluded_subscriptions` under property `properties` whose type is `ManagementGroupAggregatedCostProperties`
  - Model `ModernReservationRecommendation` moved instance variable `location_properties_location`, `look_back_period`, `instance_flexibility_ratio`, `instance_flexibility_group`, `normalized_size`, `recommended_quantity_normalized`, `meter_id`, `term`, `cost_with_no_reserved_instances`, `recommended_quantity`, `resource_type`, `total_cost_with_reserved_instances`, `net_savings`, `first_usage_date`, `scope`, `sku_properties` and `sku_name` under property `properties` whose type is `ModernReservationRecommendationProperties`
  - Model `PriceSheetResult` moved instance variable `pricesheets`, `next_link` and `download` under property `properties` whose type is `PriceSheetModel`
  - Model `ProxyResource` deleted or renamed its instance variable `e_tag`
  - Model `ReservationRecommendationDetailsModel` moved instance variable `currency`, `resource`, `resource_group`, `savings`, `scope` and `usage` under property `properties` whose type is `ReservationRecommendationDetailsProperties`
  - Model `ReservationTransaction` moved instance variable `event_date`, `reservation_order_id`, `description`, `event_type`, `quantity`, `amount`, `currency`, `reservation_order_name`, `purchasing_enrollment`, `purchasing_subscription_guid`, `purchasing_subscription_name`, `arm_sku_name`, `term`, `region`, `account_name`, `account_owner_email`, `department_name`, `cost_center`, `current_enrollment`, `billing_frequency`, `billing_month`, `monetary_commitment` and `overage` under property `properties` whose type is `LegacyReservationTransactionProperties`
  - Model `Resource` deleted or renamed its instance variable `etag`
  - Model `Resource` deleted or renamed its instance variable `tags`
  - Model `TagsResult` moved instance variable `tags`, `next_link` and `previous_link` under property `properties` whose type is `TagProperties`
  - Method `ChargesOperations.list` changed its parameter `start_date`/`end_date`/`apply` from `positional_or_keyword` to `keyword_only`
  - Method `EventsOperations.list_by_billing_profile` changed its parameter `start_date`/`end_date` from `positional_or_keyword` to `keyword_only`
  - Method `MarketplacesOperations.list` changed its parameter `skiptoken` from `positional_or_keyword` to `keyword_only`
  - Method `PriceSheetOperations.get` changed its parameter `expand`/`skiptoken` from `positional_or_keyword` to `keyword_only`
  - Method `PriceSheetOperations.get_by_billing_period` changed its parameter `expand`/`skiptoken` from `positional_or_keyword` to `keyword_only`
  - Method `ReservationRecommendationDetailsOperations.get` changed its parameter `scope`/`region`/`term`/`look_back_period`/`product` from `positional_or_keyword` to `keyword_only`
  - Method `ReservationsDetailsOperations.list` changed its parameter `start_date`/`end_date`/`reservation_id`/`reservation_order_id` from `positional_or_keyword` to `keyword_only`
  - Method `ReservationsSummariesOperations.list` changed its parameter `grain`/`start_date`/`end_date`/`reservation_id`/`reservation_order_id` from `positional_or_keyword` to `keyword_only`
  - Method `ReservationsSummariesOperations.list_by_reservation_order` changed its parameter `grain` from `positional_or_keyword` to `keyword_only`
  - Method `ReservationsSummariesOperations.list_by_reservation_order_and_reservation` changed its parameter `grain` from `positional_or_keyword` to `keyword_only`
  - Method `UsageDetailsOperations.list` changed its parameter `expand`/`skiptoken`/`metric` from `positional_or_keyword` to `keyword_only`

### Other Changes

  - Deleted model `DownloadProperties`/`ErrorDetails`/`Events`/`LegacyReservationTransaction`/`Lots`/`ReservationTransactionResource`/`ResourceAttributes` which actually were not used by SDK users

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
