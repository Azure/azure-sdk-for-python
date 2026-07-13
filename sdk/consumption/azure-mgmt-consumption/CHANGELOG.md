# Release History

## 11.0.0 (2026-07-13)

### Features Added

  - Client `ConsumptionManagementClient` added parameter `cloud_setting` in method `__init__`
  - Client `ConsumptionManagementClient` added parameter `polling_interval` in method `__init__`
  - Client `ConsumptionManagementClient` added method `send_request`
  - Model `Balance` added property `properties`
  - Model `Balance` added property `system_data`
  - Model `Budget` added property `properties`
  - Model `Budget` added property `system_data`
  - Model `BudgetComparisonExpression` added property `values_property`
  - Model `ChargeSummary` added property `etag`
  - Model `ChargeSummary` added property `system_data`
  - Model `CreditSummary` added property `properties`
  - Model `CreditSummary` added property `system_data`
  - Model `EventSummary` added property `properties`
  - Model `EventSummary` added property `system_data`
  - Model `LegacyChargeSummary` added property `etag`
  - Model `LegacyChargeSummary` added property `properties`
  - Model `LegacyChargeSummary` added property `system_data`
  - Model `LegacyReservationRecommendation` added property `properties`
  - Model `LegacyReservationRecommendation` added property `system_data`
  - Model `LegacyReservationRecommendationProperties` added property `last_usage_date`
  - Model `LegacyReservationRecommendationProperties` added property `total_hours`
  - Model `LegacySharedScopeReservationRecommendationProperties` added property `last_usage_date`
  - Model `LegacySharedScopeReservationRecommendationProperties` added property `total_hours`
  - Model `LegacySingleScopeReservationRecommendationProperties` added property `last_usage_date`
  - Model `LegacySingleScopeReservationRecommendationProperties` added property `total_hours`
  - Model `LegacyUsageDetail` added property `properties`
  - Model `LegacyUsageDetail` added property `system_data`
  - Model `LotSummary` added property `properties`
  - Model `LotSummary` added property `system_data`
  - Model `ManagementGroupAggregatedCostResult` added property `properties`
  - Model `ManagementGroupAggregatedCostResult` added property `system_data`
  - Model `Marketplace` added property `properties`
  - Model `Marketplace` added property `system_data`
  - Model `ModernChargeSummary` added property `etag`
  - Model `ModernChargeSummary` added property `properties`
  - Model `ModernChargeSummary` added property `system_data`
  - Model `ModernReservationRecommendation` added property `properties`
  - Model `ModernReservationRecommendation` added property `system_data`
  - Model `ModernReservationTransaction` added property `properties`
  - Model `ModernReservationTransaction` added property `system_data`
  - Model `ModernUsageDetail` added property `properties`
  - Model `ModernUsageDetail` added property `system_data`
  - Model `PriceSheetProperties` added property `savings_plan`
  - Model `PriceSheetResult` added property `properties`
  - Model `PriceSheetResult` added property `system_data`
  - Model `ProxyResource` added property `system_data`
  - Model `ReservationDetail` added property `properties`
  - Model `ReservationDetail` added property `system_data`
  - Model `ReservationRecommendation` added property `system_data`
  - Model `ReservationRecommendationDetailsModel` added property `properties`
  - Model `ReservationRecommendationDetailsModel` added property `system_data`
  - Model `ReservationSummary` added property `properties`
  - Model `ReservationSummary` added property `system_data`
  - Model `ReservationTransaction` added property `properties`
  - Model `ReservationTransaction` added property `system_data`
  - Model `Resource` added property `system_data`
  - Model `TagsResult` added property `properties`
  - Model `TagsResult` added property `system_data`
  - Enum `Term` added member `P1_M`
  - Model `UsageDetail` added property `system_data`
  - Added model `BalanceProperties`
  - Added model `BudgetProperties`
  - Added enum `CreatedByType`
  - Added model `CreditSummaryProperties`
  - Added model `ErrorAdditionalInfo`
  - Added model `ErrorDetail`
  - Added model `EventProperties`
  - Added model `ExtensionResource`
  - Added model `LegacyChargeSummaryProperties`
  - Added model `LegacyReservationTransactionProperties`
  - Added model `LegacyUsageDetailProperties`
  - Added model `LotProperties`
  - Added model `ManagementGroupAggregatedCostProperties`
  - Added model `MarketplaceProperties`
  - Added model `ModernChargeSummaryProperties`
  - Added model `ModernReservationRecommendationProperties`
  - Added model `ModernReservationTransactionProperties`
  - Added model `ModernSharedScopeReservationRecommendationProperties`
  - Added model `ModernSingleScopeReservationRecommendationProperties`
  - Added model `ModernUsageDetailProperties`
  - Added model `OperationStatus`
  - Added enum `OperationStatusType`
  - Added enum `OrganizationType`
  - Added model `PriceSheetModel`
  - Added model `PricesheetDownloadProperties`
  - Added model `ReservationDetailProperties`
  - Added model `ReservationRecommendationDetailsProperties`
  - Added model `ReservationSummaryProperties`
  - Added model `SavingsPlan`
  - Added model `SystemData`
  - Added model `TagProperties`
  - Model `BudgetsOperations` added parameter `content_type` in method `create_or_update`
  - Model `PriceSheetOperations` added method `begin_download_by_billing_account_period`
  - Model `ReservationRecommendationDetailsOperations` added parameter `filter` in method `get`
  - Model `ReservationTransactionsOperations` added parameter `preview_markup_percentage` in method `list`
  - Model `ReservationTransactionsOperations` added parameter `use_markup_if_partner` in method `list`

### Breaking Changes

  - Model `Balance` deleted or renamed its instance variable `adjustment_details`
  - Model `Balance` deleted or renamed its instance variable `adjustments`
  - Model `Balance` deleted or renamed its instance variable `azure_marketplace_service_charges`
  - Model `Balance` deleted or renamed its instance variable `beginning_balance`
  - Model `Balance` deleted or renamed its instance variable `billing_frequency`
  - Model `Balance` deleted or renamed its instance variable `charges_billed_separately`
  - Model `Balance` deleted or renamed its instance variable `currency`
  - Model `Balance` deleted or renamed its instance variable `ending_balance`
  - Model `Balance` deleted or renamed its instance variable `new_purchases`
  - Model `Balance` deleted or renamed its instance variable `new_purchases_details`
  - Model `Balance` deleted or renamed its instance variable `price_hidden`
  - Model `Balance` deleted or renamed its instance variable `service_overage`
  - Model `Balance` deleted or renamed its instance variable `total_overage`
  - Model `Balance` deleted or renamed its instance variable `total_usage`
  - Model `Balance` deleted or renamed its instance variable `utilized`
  - Model `Budget` deleted or renamed its instance variable `amount`
  - Model `Budget` deleted or renamed its instance variable `category`
  - Model `Budget` deleted or renamed its instance variable `current_spend`
  - Model `Budget` deleted or renamed its instance variable `filter`
  - Model `Budget` deleted or renamed its instance variable `forecast_spend`
  - Model `Budget` deleted or renamed its instance variable `notifications`
  - Model `Budget` deleted or renamed its instance variable `time_grain`
  - Model `Budget` deleted or renamed its instance variable `time_period`
  - Model `BudgetComparisonExpression` deleted or renamed its instance variable `values`
  - Deleted or renamed enum value `BudgetOperatorType.IN_ENUM`
  - Model `ChargeSummary` deleted or renamed its instance variable `e_tag`
  - Model `CreditSummary` deleted or renamed its instance variable `balance_summary`
  - Model `CreditSummary` deleted or renamed its instance variable `billing_currency`
  - Model `CreditSummary` deleted or renamed its instance variable `credit_currency`
  - Model `CreditSummary` deleted or renamed its instance variable `etag`
  - Model `CreditSummary` deleted or renamed its instance variable `expired_credit`
  - Model `CreditSummary` deleted or renamed its instance variable `pending_credit_adjustments`
  - Model `CreditSummary` deleted or renamed its instance variable `pending_eligible_charges`
  - Model `CreditSummary` deleted or renamed its instance variable `reseller`
  - Model `EventSummary` deleted or renamed its instance variable `adjustments`
  - Model `EventSummary` deleted or renamed its instance variable `adjustments_in_billing_currency`
  - Model `EventSummary` deleted or renamed its instance variable `billing_currency`
  - Model `EventSummary` deleted or renamed its instance variable `billing_profile_display_name`
  - Model `EventSummary` deleted or renamed its instance variable `billing_profile_id`
  - Model `EventSummary` deleted or renamed its instance variable `canceled_credit`
  - Model `EventSummary` deleted or renamed its instance variable `charges`
  - Model `EventSummary` deleted or renamed its instance variable `charges_in_billing_currency`
  - Model `EventSummary` deleted or renamed its instance variable `closed_balance`
  - Model `EventSummary` deleted or renamed its instance variable `closed_balance_in_billing_currency`
  - Model `EventSummary` deleted or renamed its instance variable `credit_currency`
  - Model `EventSummary` deleted or renamed its instance variable `credit_expired`
  - Model `EventSummary` deleted or renamed its instance variable `credit_expired_in_billing_currency`
  - Model `EventSummary` deleted or renamed its instance variable `description`
  - Model `EventSummary` deleted or renamed its instance variable `e_tag_properties_e_tag`
  - Model `EventSummary` deleted or renamed its instance variable `event_type`
  - Model `EventSummary` deleted or renamed its instance variable `invoice_number`
  - Model `EventSummary` deleted or renamed its instance variable `lot_id`
  - Model `EventSummary` deleted or renamed its instance variable `lot_source`
  - Model `EventSummary` deleted or renamed its instance variable `new_credit`
  - Model `EventSummary` deleted or renamed its instance variable `new_credit_in_billing_currency`
  - Model `EventSummary` deleted or renamed its instance variable `reseller`
  - Model `EventSummary` deleted or renamed its instance variable `transaction_date`
  - Model `LegacyChargeSummary` deleted or renamed its instance variable `azure_charges`
  - Model `LegacyChargeSummary` deleted or renamed its instance variable `billing_period_id`
  - Model `LegacyChargeSummary` deleted or renamed its instance variable `charges_billed_separately`
  - Model `LegacyChargeSummary` deleted or renamed its instance variable `currency`
  - Model `LegacyChargeSummary` deleted or renamed its instance variable `e_tag`
  - Model `LegacyChargeSummary` deleted or renamed its instance variable `marketplace_charges`
  - Model `LegacyChargeSummary` deleted or renamed its instance variable `usage_end`
  - Model `LegacyChargeSummary` deleted or renamed its instance variable `usage_start`
  - Model `LegacyReservationRecommendation` deleted or renamed its instance variable `cost_with_no_reserved_instances`
  - Model `LegacyReservationRecommendation` deleted or renamed its instance variable `first_usage_date`
  - Model `LegacyReservationRecommendation` deleted or renamed its instance variable `instance_flexibility_group`
  - Model `LegacyReservationRecommendation` deleted or renamed its instance variable `instance_flexibility_ratio`
  - Model `LegacyReservationRecommendation` deleted or renamed its instance variable `look_back_period`
  - Model `LegacyReservationRecommendation` deleted or renamed its instance variable `meter_id`
  - Model `LegacyReservationRecommendation` deleted or renamed its instance variable `net_savings`
  - Model `LegacyReservationRecommendation` deleted or renamed its instance variable `normalized_size`
  - Model `LegacyReservationRecommendation` deleted or renamed its instance variable `recommended_quantity`
  - Model `LegacyReservationRecommendation` deleted or renamed its instance variable `recommended_quantity_normalized`
  - Model `LegacyReservationRecommendation` deleted or renamed its instance variable `resource_type`
  - Model `LegacyReservationRecommendation` deleted or renamed its instance variable `scope`
  - Model `LegacyReservationRecommendation` deleted or renamed its instance variable `sku_properties`
  - Model `LegacyReservationRecommendation` deleted or renamed its instance variable `term`
  - Model `LegacyReservationRecommendation` deleted or renamed its instance variable `total_cost_with_reserved_instances`
  - Model `LegacyUsageDetail` deleted or renamed its instance variable `account_name`
  - Model `LegacyUsageDetail` deleted or renamed its instance variable `account_owner_id`
  - Model `LegacyUsageDetail` deleted or renamed its instance variable `additional_info`
  - Model `LegacyUsageDetail` deleted or renamed its instance variable `benefit_id`
  - Model `LegacyUsageDetail` deleted or renamed its instance variable `benefit_name`
  - Model `LegacyUsageDetail` deleted or renamed its instance variable `billing_account_id`
  - Model `LegacyUsageDetail` deleted or renamed its instance variable `billing_account_name`
  - Model `LegacyUsageDetail` deleted or renamed its instance variable `billing_currency`
  - Model `LegacyUsageDetail` deleted or renamed its instance variable `billing_period_end_date`
  - Model `LegacyUsageDetail` deleted or renamed its instance variable `billing_period_start_date`
  - Model `LegacyUsageDetail` deleted or renamed its instance variable `billing_profile_id`
  - Model `LegacyUsageDetail` deleted or renamed its instance variable `billing_profile_name`
  - Model `LegacyUsageDetail` deleted or renamed its instance variable `charge_type`
  - Model `LegacyUsageDetail` deleted or renamed its instance variable `consumed_service`
  - Model `LegacyUsageDetail` deleted or renamed its instance variable `cost`
  - Model `LegacyUsageDetail` deleted or renamed its instance variable `cost_center`
  - Model `LegacyUsageDetail` deleted or renamed its instance variable `date`
  - Model `LegacyUsageDetail` deleted or renamed its instance variable `effective_price`
  - Model `LegacyUsageDetail` deleted or renamed its instance variable `frequency`
  - Model `LegacyUsageDetail` deleted or renamed its instance variable `invoice_section`
  - Model `LegacyUsageDetail` deleted or renamed its instance variable `is_azure_credit_eligible`
  - Model `LegacyUsageDetail` deleted or renamed its instance variable `meter_details`
  - Model `LegacyUsageDetail` deleted or renamed its instance variable `meter_id`
  - Model `LegacyUsageDetail` deleted or renamed its instance variable `offer_id`
  - Model `LegacyUsageDetail` deleted or renamed its instance variable `part_number`
  - Model `LegacyUsageDetail` deleted or renamed its instance variable `pay_g_price`
  - Model `LegacyUsageDetail` deleted or renamed its instance variable `plan_name`
  - Model `LegacyUsageDetail` deleted or renamed its instance variable `pricing_model`
  - Model `LegacyUsageDetail` deleted or renamed its instance variable `product`
  - Model `LegacyUsageDetail` deleted or renamed its instance variable `product_order_id`
  - Model `LegacyUsageDetail` deleted or renamed its instance variable `product_order_name`
  - Model `LegacyUsageDetail` deleted or renamed its instance variable `publisher_name`
  - Model `LegacyUsageDetail` deleted or renamed its instance variable `publisher_type`
  - Model `LegacyUsageDetail` deleted or renamed its instance variable `quantity`
  - Model `LegacyUsageDetail` deleted or renamed its instance variable `reservation_id`
  - Model `LegacyUsageDetail` deleted or renamed its instance variable `reservation_name`
  - Model `LegacyUsageDetail` deleted or renamed its instance variable `resource_group`
  - Model `LegacyUsageDetail` deleted or renamed its instance variable `resource_id`
  - Model `LegacyUsageDetail` deleted or renamed its instance variable `resource_location`
  - Model `LegacyUsageDetail` deleted or renamed its instance variable `resource_name`
  - Model `LegacyUsageDetail` deleted or renamed its instance variable `service_info1`
  - Model `LegacyUsageDetail` deleted or renamed its instance variable `service_info2`
  - Model `LegacyUsageDetail` deleted or renamed its instance variable `subscription_id`
  - Model `LegacyUsageDetail` deleted or renamed its instance variable `subscription_name`
  - Model `LegacyUsageDetail` deleted or renamed its instance variable `term`
  - Model `LegacyUsageDetail` deleted or renamed its instance variable `unit_price`
  - Model `LotSummary` deleted or renamed its instance variable `billing_currency`
  - Model `LotSummary` deleted or renamed its instance variable `closed_balance`
  - Model `LotSummary` deleted or renamed its instance variable `closed_balance_in_billing_currency`
  - Model `LotSummary` deleted or renamed its instance variable `credit_currency`
  - Model `LotSummary` deleted or renamed its instance variable `e_tag_properties_e_tag`
  - Model `LotSummary` deleted or renamed its instance variable `expiration_date`
  - Model `LotSummary` deleted or renamed its instance variable `original_amount`
  - Model `LotSummary` deleted or renamed its instance variable `original_amount_in_billing_currency`
  - Model `LotSummary` deleted or renamed its instance variable `po_number`
  - Model `LotSummary` deleted or renamed its instance variable `purchased_date`
  - Model `LotSummary` deleted or renamed its instance variable `reseller`
  - Model `LotSummary` deleted or renamed its instance variable `source`
  - Model `LotSummary` deleted or renamed its instance variable `start_date`
  - Model `LotSummary` deleted or renamed its instance variable `status`
  - Model `ManagementGroupAggregatedCostResult` deleted or renamed its instance variable `azure_charges`
  - Model `ManagementGroupAggregatedCostResult` deleted or renamed its instance variable `billing_period_id`
  - Model `ManagementGroupAggregatedCostResult` deleted or renamed its instance variable `charges_billed_separately`
  - Model `ManagementGroupAggregatedCostResult` deleted or renamed its instance variable `children`
  - Model `ManagementGroupAggregatedCostResult` deleted or renamed its instance variable `currency`
  - Model `ManagementGroupAggregatedCostResult` deleted or renamed its instance variable `excluded_subscriptions`
  - Model `ManagementGroupAggregatedCostResult` deleted or renamed its instance variable `included_subscriptions`
  - Model `ManagementGroupAggregatedCostResult` deleted or renamed its instance variable `marketplace_charges`
  - Model `ManagementGroupAggregatedCostResult` deleted or renamed its instance variable `usage_end`
  - Model `ManagementGroupAggregatedCostResult` deleted or renamed its instance variable `usage_start`
  - Model `Marketplace` deleted or renamed its instance variable `account_name`
  - Model `Marketplace` deleted or renamed its instance variable `additional_info`
  - Model `Marketplace` deleted or renamed its instance variable `billing_period_id`
  - Model `Marketplace` deleted or renamed its instance variable `consumed_quantity`
  - Model `Marketplace` deleted or renamed its instance variable `consumed_service`
  - Model `Marketplace` deleted or renamed its instance variable `cost_center`
  - Model `Marketplace` deleted or renamed its instance variable `currency`
  - Model `Marketplace` deleted or renamed its instance variable `department_name`
  - Model `Marketplace` deleted or renamed its instance variable `instance_id`
  - Model `Marketplace` deleted or renamed its instance variable `instance_name`
  - Model `Marketplace` deleted or renamed its instance variable `is_estimated`
  - Model `Marketplace` deleted or renamed its instance variable `is_recurring_charge`
  - Model `Marketplace` deleted or renamed its instance variable `meter_id`
  - Model `Marketplace` deleted or renamed its instance variable `offer_name`
  - Model `Marketplace` deleted or renamed its instance variable `order_number`
  - Model `Marketplace` deleted or renamed its instance variable `plan_name`
  - Model `Marketplace` deleted or renamed its instance variable `pretax_cost`
  - Model `Marketplace` deleted or renamed its instance variable `publisher_name`
  - Model `Marketplace` deleted or renamed its instance variable `resource_group`
  - Model `Marketplace` deleted or renamed its instance variable `resource_rate`
  - Model `Marketplace` deleted or renamed its instance variable `subscription_guid`
  - Model `Marketplace` deleted or renamed its instance variable `subscription_name`
  - Model `Marketplace` deleted or renamed its instance variable `unit_of_measure`
  - Model `Marketplace` deleted or renamed its instance variable `usage_end`
  - Model `Marketplace` deleted or renamed its instance variable `usage_start`
  - Model `ModernChargeSummary` deleted or renamed its instance variable `azure_charges`
  - Model `ModernChargeSummary` deleted or renamed its instance variable `billing_account_id`
  - Model `ModernChargeSummary` deleted or renamed its instance variable `billing_period_id`
  - Model `ModernChargeSummary` deleted or renamed its instance variable `billing_profile_id`
  - Model `ModernChargeSummary` deleted or renamed its instance variable `charges_billed_separately`
  - Model `ModernChargeSummary` deleted or renamed its instance variable `customer_id`
  - Model `ModernChargeSummary` deleted or renamed its instance variable `e_tag`
  - Model `ModernChargeSummary` deleted or renamed its instance variable `invoice_section_id`
  - Model `ModernChargeSummary` deleted or renamed its instance variable `is_invoiced`
  - Model `ModernChargeSummary` deleted or renamed its instance variable `marketplace_charges`
  - Model `ModernChargeSummary` deleted or renamed its instance variable `usage_end`
  - Model `ModernChargeSummary` deleted or renamed its instance variable `usage_start`
  - Model `ModernReservationRecommendation` deleted or renamed its instance variable `cost_with_no_reserved_instances`
  - Model `ModernReservationRecommendation` deleted or renamed its instance variable `first_usage_date`
  - Model `ModernReservationRecommendation` deleted or renamed its instance variable `instance_flexibility_group`
  - Model `ModernReservationRecommendation` deleted or renamed its instance variable `instance_flexibility_ratio`
  - Model `ModernReservationRecommendation` deleted or renamed its instance variable `location_properties_location`
  - Model `ModernReservationRecommendation` deleted or renamed its instance variable `look_back_period`
  - Model `ModernReservationRecommendation` deleted or renamed its instance variable `meter_id`
  - Model `ModernReservationRecommendation` deleted or renamed its instance variable `net_savings`
  - Model `ModernReservationRecommendation` deleted or renamed its instance variable `normalized_size`
  - Model `ModernReservationRecommendation` deleted or renamed its instance variable `recommended_quantity`
  - Model `ModernReservationRecommendation` deleted or renamed its instance variable `recommended_quantity_normalized`
  - Model `ModernReservationRecommendation` deleted or renamed its instance variable `scope`
  - Model `ModernReservationRecommendation` deleted or renamed its instance variable `sku_name`
  - Model `ModernReservationRecommendation` deleted or renamed its instance variable `sku_properties`
  - Model `ModernReservationRecommendation` deleted or renamed its instance variable `term`
  - Model `ModernReservationRecommendation` deleted or renamed its instance variable `total_cost_with_reserved_instances`
  - Model `ModernReservationTransaction` deleted or renamed its instance variable `amount`
  - Model `ModernReservationTransaction` deleted or renamed its instance variable `arm_sku_name`
  - Model `ModernReservationTransaction` deleted or renamed its instance variable `billing_frequency`
  - Model `ModernReservationTransaction` deleted or renamed its instance variable `billing_profile_id`
  - Model `ModernReservationTransaction` deleted or renamed its instance variable `billing_profile_name`
  - Model `ModernReservationTransaction` deleted or renamed its instance variable `currency`
  - Model `ModernReservationTransaction` deleted or renamed its instance variable `description`
  - Model `ModernReservationTransaction` deleted or renamed its instance variable `event_date`
  - Model `ModernReservationTransaction` deleted or renamed its instance variable `event_type`
  - Model `ModernReservationTransaction` deleted or renamed its instance variable `invoice`
  - Model `ModernReservationTransaction` deleted or renamed its instance variable `invoice_id`
  - Model `ModernReservationTransaction` deleted or renamed its instance variable `invoice_section_id`
  - Model `ModernReservationTransaction` deleted or renamed its instance variable `invoice_section_name`
  - Model `ModernReservationTransaction` deleted or renamed its instance variable `purchasing_subscription_guid`
  - Model `ModernReservationTransaction` deleted or renamed its instance variable `purchasing_subscription_name`
  - Model `ModernReservationTransaction` deleted or renamed its instance variable `quantity`
  - Model `ModernReservationTransaction` deleted or renamed its instance variable `region`
  - Model `ModernReservationTransaction` deleted or renamed its instance variable `reservation_order_id`
  - Model `ModernReservationTransaction` deleted or renamed its instance variable `reservation_order_name`
  - Model `ModernReservationTransaction` deleted or renamed its instance variable `term`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `additional_info`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `benefit_id`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `benefit_name`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `billing_account_id`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `billing_account_name`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `billing_currency_code`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `billing_period_end_date`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `billing_period_start_date`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `billing_profile_id`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `billing_profile_name`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `charge_type`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `consumed_service`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `cost_allocation_rule_name`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `cost_center`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `cost_in_billing_currency`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `cost_in_pricing_currency`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `cost_in_usd`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `customer_name`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `customer_tenant_id`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `date`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `effective_price`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `exchange_rate`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `exchange_rate_date`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `exchange_rate_pricing_to_billing`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `frequency`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `instance_name`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `invoice_id`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `invoice_section_id`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `invoice_section_name`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `is_azure_credit_eligible`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `market_price`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `meter_category`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `meter_id`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `meter_name`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `meter_region`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `meter_sub_category`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `partner_earned_credit_applied`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `partner_earned_credit_rate`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `partner_name`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `partner_tenant_id`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `pay_g_price`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `payg_cost_in_billing_currency`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `payg_cost_in_usd`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `previous_invoice_id`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `pricing_currency_code`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `pricing_model`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `product`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `product_identifier`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `product_order_id`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `product_order_name`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `provider`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `publisher_id`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `publisher_name`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `publisher_type`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `quantity`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `reseller_mpn_id`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `reseller_name`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `reservation_id`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `reservation_name`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `resource_group`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `resource_location`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `resource_location_normalized`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `service_family`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `service_info1`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `service_info2`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `service_period_end_date`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `service_period_start_date`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `subscription_guid`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `subscription_name`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `term`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `unit_of_measure`
  - Model `ModernUsageDetail` deleted or renamed its instance variable `unit_price`
  - Model `PriceSheetResult` deleted or renamed its instance variable `download`
  - Model `PriceSheetResult` deleted or renamed its instance variable `next_link`
  - Model `PriceSheetResult` deleted or renamed its instance variable `pricesheets`
  - Model `ProxyResource` deleted or renamed its instance variable `e_tag`
  - Model `ReservationDetail` deleted or renamed its instance variable `instance_flexibility_group`
  - Model `ReservationDetail` deleted or renamed its instance variable `instance_flexibility_ratio`
  - Model `ReservationDetail` deleted or renamed its instance variable `instance_id`
  - Model `ReservationDetail` deleted or renamed its instance variable `kind`
  - Model `ReservationDetail` deleted or renamed its instance variable `reservation_id`
  - Model `ReservationDetail` deleted or renamed its instance variable `reservation_order_id`
  - Model `ReservationDetail` deleted or renamed its instance variable `reserved_hours`
  - Model `ReservationDetail` deleted or renamed its instance variable `sku_name`
  - Model `ReservationDetail` deleted or renamed its instance variable `total_reserved_quantity`
  - Model `ReservationDetail` deleted or renamed its instance variable `usage_date`
  - Model `ReservationDetail` deleted or renamed its instance variable `used_hours`
  - Model `ReservationRecommendationDetailsModel` deleted or renamed its instance variable `currency`
  - Model `ReservationRecommendationDetailsModel` deleted or renamed its instance variable `resource`
  - Model `ReservationRecommendationDetailsModel` deleted or renamed its instance variable `resource_group`
  - Model `ReservationRecommendationDetailsModel` deleted or renamed its instance variable `savings`
  - Model `ReservationRecommendationDetailsModel` deleted or renamed its instance variable `scope`
  - Model `ReservationRecommendationDetailsModel` deleted or renamed its instance variable `usage`
  - Model `ReservationSummary` deleted or renamed its instance variable `avg_utilization_percentage`
  - Model `ReservationSummary` deleted or renamed its instance variable `kind`
  - Model `ReservationSummary` deleted or renamed its instance variable `max_utilization_percentage`
  - Model `ReservationSummary` deleted or renamed its instance variable `min_utilization_percentage`
  - Model `ReservationSummary` deleted or renamed its instance variable `purchased_quantity`
  - Model `ReservationSummary` deleted or renamed its instance variable `remaining_quantity`
  - Model `ReservationSummary` deleted or renamed its instance variable `reservation_id`
  - Model `ReservationSummary` deleted or renamed its instance variable `reservation_order_id`
  - Model `ReservationSummary` deleted or renamed its instance variable `reserved_hours`
  - Model `ReservationSummary` deleted or renamed its instance variable `sku_name`
  - Model `ReservationSummary` deleted or renamed its instance variable `total_reserved_quantity`
  - Model `ReservationSummary` deleted or renamed its instance variable `usage_date`
  - Model `ReservationSummary` deleted or renamed its instance variable `used_hours`
  - Model `ReservationSummary` deleted or renamed its instance variable `used_quantity`
  - Model `ReservationSummary` deleted or renamed its instance variable `utilized_percentage`
  - Model `ReservationTransaction` deleted or renamed its instance variable `account_name`
  - Model `ReservationTransaction` deleted or renamed its instance variable `account_owner_email`
  - Model `ReservationTransaction` deleted or renamed its instance variable `amount`
  - Model `ReservationTransaction` deleted or renamed its instance variable `arm_sku_name`
  - Model `ReservationTransaction` deleted or renamed its instance variable `billing_frequency`
  - Model `ReservationTransaction` deleted or renamed its instance variable `billing_month`
  - Model `ReservationTransaction` deleted or renamed its instance variable `cost_center`
  - Model `ReservationTransaction` deleted or renamed its instance variable `currency`
  - Model `ReservationTransaction` deleted or renamed its instance variable `current_enrollment`
  - Model `ReservationTransaction` deleted or renamed its instance variable `department_name`
  - Model `ReservationTransaction` deleted or renamed its instance variable `description`
  - Model `ReservationTransaction` deleted or renamed its instance variable `event_date`
  - Model `ReservationTransaction` deleted or renamed its instance variable `event_type`
  - Model `ReservationTransaction` deleted or renamed its instance variable `monetary_commitment`
  - Model `ReservationTransaction` deleted or renamed its instance variable `overage`
  - Model `ReservationTransaction` deleted or renamed its instance variable `purchasing_enrollment`
  - Model `ReservationTransaction` deleted or renamed its instance variable `purchasing_subscription_guid`
  - Model `ReservationTransaction` deleted or renamed its instance variable `purchasing_subscription_name`
  - Model `ReservationTransaction` deleted or renamed its instance variable `quantity`
  - Model `ReservationTransaction` deleted or renamed its instance variable `region`
  - Model `ReservationTransaction` deleted or renamed its instance variable `reservation_order_id`
  - Model `ReservationTransaction` deleted or renamed its instance variable `reservation_order_name`
  - Model `ReservationTransaction` deleted or renamed its instance variable `term`
  - Model `Resource` deleted or renamed its instance variable `etag`
  - Model `Resource` deleted or renamed its instance variable `tags`
  - Model `TagsResult` deleted or renamed its instance variable `next_link`
  - Model `TagsResult` deleted or renamed its instance variable `previous_link`
  - Model `TagsResult` deleted or renamed its instance variable `tags`
  - Deleted or renamed model `BudgetsListResult`
  - Deleted or renamed model `DownloadProperties`
  - Deleted or renamed model `ErrorDetails`
  - Deleted or renamed model `Events`
  - Deleted or renamed model `LegacyReservationTransaction`
  - Deleted or renamed model `Lots`
  - Deleted or renamed model `MarketplacesListResult`
  - Deleted or renamed model `ModernReservationTransactionsListResult`
  - Deleted or renamed model `OperationListResult`
  - Deleted or renamed model `ReservationDetailsListResult`
  - Deleted or renamed model `ReservationRecommendationsListResult`
  - Deleted or renamed model `ReservationSummariesListResult`
  - Deleted or renamed model `ReservationTransactionResource`
  - Deleted or renamed model `ReservationTransactionsListResult`
  - Deleted or renamed model `ResourceAttributes`
  - Deleted or renamed model `UsageDetailsListResult`
  - Method `ChargesOperations.list` changed its parameter `apply` from `positional_or_keyword` to `keyword_only`
  - Method `ChargesOperations.list` changed its parameter `end_date` from `positional_or_keyword` to `keyword_only`
  - Method `ChargesOperations.list` changed its parameter `start_date` from `positional_or_keyword` to `keyword_only`
  - Method `EventsOperations.list_by_billing_profile` changed its parameter `end_date` from `positional_or_keyword` to `keyword_only`
  - Method `EventsOperations.list_by_billing_profile` changed its parameter `start_date` from `positional_or_keyword` to `keyword_only`
  - Method `MarketplacesOperations.list` changed its parameter `skiptoken` from `positional_or_keyword` to `keyword_only`
  - Method `PriceSheetOperations.get` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `PriceSheetOperations.get` changed its parameter `skiptoken` from `positional_or_keyword` to `keyword_only`
  - Method `PriceSheetOperations.get_by_billing_period` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `PriceSheetOperations.get_by_billing_period` changed its parameter `skiptoken` from `positional_or_keyword` to `keyword_only`
  - Method `ReservationRecommendationDetailsOperations.get` changed its parameter `look_back_period` from `positional_or_keyword` to `keyword_only`
  - Method `ReservationRecommendationDetailsOperations.get` changed its parameter `product` from `positional_or_keyword` to `keyword_only`
  - Method `ReservationRecommendationDetailsOperations.get` changed its parameter `region` from `positional_or_keyword` to `keyword_only`
  - Method `ReservationRecommendationDetailsOperations.get` changed its parameter `scope` from `positional_or_keyword` to `keyword_only`
  - Method `ReservationRecommendationDetailsOperations.get` changed its parameter `term` from `positional_or_keyword` to `keyword_only`
  - Method `ReservationsDetailsOperations.list` changed its parameter `end_date` from `positional_or_keyword` to `keyword_only`
  - Method `ReservationsDetailsOperations.list` changed its parameter `reservation_id` from `positional_or_keyword` to `keyword_only`
  - Method `ReservationsDetailsOperations.list` changed its parameter `reservation_order_id` from `positional_or_keyword` to `keyword_only`
  - Method `ReservationsDetailsOperations.list` changed its parameter `start_date` from `positional_or_keyword` to `keyword_only`
  - Method `ReservationsSummariesOperations.list` changed its parameter `end_date` from `positional_or_keyword` to `keyword_only`
  - Method `ReservationsSummariesOperations.list` changed its parameter `grain` from `positional_or_keyword` to `keyword_only`
  - Method `ReservationsSummariesOperations.list` changed its parameter `reservation_id` from `positional_or_keyword` to `keyword_only`
  - Method `ReservationsSummariesOperations.list` changed its parameter `reservation_order_id` from `positional_or_keyword` to `keyword_only`
  - Method `ReservationsSummariesOperations.list` changed its parameter `start_date` from `positional_or_keyword` to `keyword_only`
  - Method `ReservationsSummariesOperations.list_by_reservation_order` changed its parameter `grain` from `positional_or_keyword` to `keyword_only`
  - Method `ReservationsSummariesOperations.list_by_reservation_order_and_reservation` changed its parameter `grain` from `positional_or_keyword` to `keyword_only`
  - Method `UsageDetailsOperations.list` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `UsageDetailsOperations.list` changed its parameter `metric` from `positional_or_keyword` to `keyword_only`
  - Method `UsageDetailsOperations.list` changed its parameter `skiptoken` from `positional_or_keyword` to `keyword_only`
  - Method `BudgetsOperations.list` changed return type from `AsyncIterable[BudgetsListResult]` to `AsyncItemPaged[Budget]`
  - Method `EventsOperations.list_by_billing_account` changed return type from `AsyncIterable[Events]` to `AsyncItemPaged[EventSummary]`
  - Method `EventsOperations.list_by_billing_profile` changed return type from `AsyncIterable[Events]` to `AsyncItemPaged[EventSummary]`
  - Method `LotsOperations.list_by_billing_account` changed return type from `AsyncIterable[Lots]` to `AsyncItemPaged[LotSummary]`
  - Method `LotsOperations.list_by_billing_profile` changed return type from `AsyncIterable[Lots]` to `AsyncItemPaged[LotSummary]`
  - Method `LotsOperations.list_by_customer` changed return type from `AsyncIterable[Lots]` to `AsyncItemPaged[LotSummary]`
  - Method `MarketplacesOperations.list` changed return type from `AsyncIterable[MarketplacesListResult]` to `AsyncItemPaged[Marketplace]`
  - Method `Operations.list` changed return type from `AsyncIterable[OperationListResult]` to `AsyncItemPaged[Operation]`
  - Method `ReservationRecommendationsOperations.list` changed return type from `AsyncIterable[ReservationRecommendationsListResult]` to `AsyncItemPaged[ReservationRecommendation]`
  - Method `ReservationTransactionsOperations.list` changed return type from `AsyncIterable[ReservationTransactionsListResult]` to `AsyncItemPaged[ReservationTransaction]`
  - Method `ReservationTransactionsOperations.list_by_billing_profile` changed return type from `AsyncIterable[ModernReservationTransactionsListResult]` to `AsyncItemPaged[ModernReservationTransaction]`
  - Method `ReservationsDetailsOperations.list` changed return type from `AsyncIterable[ReservationDetailsListResult]` to `AsyncItemPaged[ReservationDetail]`
  - Method `ReservationsDetailsOperations.list_by_reservation_order` changed return type from `AsyncIterable[ReservationDetailsListResult]` to `AsyncItemPaged[ReservationDetail]`
  - Method `ReservationsDetailsOperations.list_by_reservation_order_and_reservation` changed return type from `AsyncIterable[ReservationDetailsListResult]` to `AsyncItemPaged[ReservationDetail]`
  - Method `ReservationsSummariesOperations.list` changed return type from `AsyncIterable[ReservationSummariesListResult]` to `AsyncItemPaged[ReservationSummary]`
  - Method `ReservationsSummariesOperations.list_by_reservation_order` changed return type from `AsyncIterable[ReservationSummariesListResult]` to `AsyncItemPaged[ReservationSummary]`
  - Method `ReservationsSummariesOperations.list_by_reservation_order_and_reservation` changed return type from `AsyncIterable[ReservationSummariesListResult]` to `AsyncItemPaged[ReservationSummary]`
  - Method `UsageDetailsOperations.list` changed return type from `AsyncIterable[UsageDetailsListResult]` to `AsyncItemPaged[UsageDetail]`
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
  - Method `BudgetsOperations.create_or_update` re-ordered its parameters from `['self', 'budget_name', 'cls', 'parameters', 'scope', 'kwargs']` to `['self', 'budget_name', 'content_type', 'parameters', 'scope', 'kwargs']`
  - Method `ReservationRecommendationDetailsOperations.get` re-ordered its parameters from `['self', 'cls', 'look_back_period', 'product', 'region', 'resource_scope', 'scope', 'term', 'kwargs']` to `['self', 'filter', 'look_back_period', 'product', 'region', 'resource_scope', 'scope', 'term', 'kwargs']`

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
