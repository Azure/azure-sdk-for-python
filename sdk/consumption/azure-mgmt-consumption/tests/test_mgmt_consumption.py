# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import datetime
import unittest

import azure.mgmt.consumption
import azure.mgmt.consumption.models
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

raise unittest.SkipTest("These were written by Consumption service team for 2.0.0 and would need adaption, and are disabled for now.")

class MgmtConsumptionTest(AzureMgmtTestCase):

    reservationOrderId = 'ca69259e-bd4f-45c3-bf28-3f353f9cce9b'
    reservationId = 'f37f4b70-52ba-4344-a8bd-28abfd21d640'
    billingPeriodName = '201710'
    startDate = '2018-02-01T00:00:00Z'
    endDate = '2018-02-28T00:00:00Z'
    models = azure.mgmt.consumption.models

    def setUp(self):
        super(MgmtConsumptionTest, self).setUp()
        self.consumption_client = self.create_mgmt_client(
            azure.mgmt.consumption.ConsumptionManagementClient
        )

    def _validate_usage(self, usage, include_meter_details=False, include_additional_properties=False):
        self.assertIsNotNone(usage)
        self.assertIsNotNone(usage.id)
        self.assertIsNotNone(usage.name)
        self.assertIsNotNone(usage.type)
        self.assertIsNotNone(usage.billing_period_id)
        self.assertTrue(usage.usage_start <= usage.usage_end)
        self.assertIsNotNone(usage.instance_name)
        self.assertIsNotNone(usage.currency)
        self.assertIsNotNone(usage.pretax_cost)
        self.assertIsNotNone(usage.is_estimated)
        self.assertIsNotNone(usage.meter_id)
        if include_meter_details:
            self.assertIsNotNone(usage.meter_details)
            self.assertIsNotNone(usage.meter_details.meter_name)
        else:
            self.assertIsNone(usage.meter_details)
        if not include_additional_properties:
            self.assertIsNone(usage.additional_properties)

    def _validate_marketplace(self, marketplace):
        self.assertIsNotNone(marketplace)
        self.assertIsNotNone(marketplace.id)
        self.assertIsNotNone(marketplace.name)
        self.assertIsNotNone(marketplace.type)
        self.assertIsNotNone(marketplace.billing_period_id)
        self.assertTrue(marketplace.usage_start <= marketplace.usage_end)
        self.assertIsNotNone(marketplace.instance_name)
        self.assertIsNotNone(marketplace.instance_id)
        self.assertIsNotNone(marketplace.currency)
        self.assertIsNotNone(marketplace.pretax_cost)
        self.assertIsNotNone(marketplace.is_estimated)
        self.assertIsNotNone(marketplace.order_number)

    def _validate_reservations_summaries(self, reservation):
        self.assertIsNotNone(reservation)
        self.assertIsNotNone(reservation.id)
        self.assertIsNotNone(reservation.name)
        self.assertIsNotNone(reservation.type)
        self.assertTrue(reservation.reservation_order_id)
        self.assertTrue(reservation.reservation_id)
        self.assertTrue(reservation.sku_name)
        self.assertIsNotNone(reservation.reserved_hours)
        self.assertIsNotNone(reservation.usage_date)
        self.assertIsNotNone(reservation.used_hours)
        self.assertIsNotNone(reservation.max_utilization_percentage)
        self.assertIsNotNone(reservation.min_utilization_percentage)
        self.assertIsNotNone(reservation.avg_utilization_percentage)

    def _validate_reservations_details(self, reservation):
        self.assertIsNotNone(reservation)
        self.assertIsNotNone(reservation.id)
        self.assertIsNotNone(reservation.name)
        self.assertIsNotNone(reservation.type)
        self.assertTrue(reservation.reservation_order_id)
        self.assertTrue(reservation.reservation_id)
        self.assertTrue(reservation.sku_name)
        self.assertIsNotNone(reservation.reserved_hours)
        self.assertIsNotNone(reservation.usage_date)
        self.assertIsNotNone(reservation.used_hours)
        self.assertIsNotNone(reservation.instance_id)
        self.assertIsNotNone(reservation.total_reserved_quantity)

    def _validate_budget(self, budget):
        self.assertIsNotNone(budget)
        self.assertIsNotNone(budget.id)
        self.assertIsNotNone(budget.name)
        self.assertIsNotNone(budget.type)
        self.assertIsNotNone(budget.time_period.start_date)
        self.assertIsNotNone(budget.time_period.end_date)
        self.assertIsNotNone(budget.time_grain)
        self.assertIsNotNone(budget.amount)

    def _validate_price_sheet(self, pricesheet, included_paging=False):
        self.assertIsNotNone(pricesheet)
        self.assertIsNotNone(pricesheet.id)
        self.assertIsNotNone(pricesheet.name)
        self.assertIsNotNone(pricesheet.type)
        self.assertIsNotNone(pricesheet.pricesheets[0].billing_period_id)
        self.assertIsNotNone(pricesheet.pricesheets[0].unit_of_measure)
        self.assertIsNotNone(pricesheet.pricesheets[0].included_quantity)
        self.assertIsNotNone(pricesheet.pricesheets[0].part_number)
        self.assertIsNotNone(pricesheet.pricesheets[0].currency_code)
        self.assertIsNotNone(pricesheet.pricesheets[0].unit_price)
        self.assertIsNotNone(pricesheet.pricesheets[0].meter_id)
        if included_paging:
            self.assertIsNotNone(pricesheet.next_link)

    def test_consumption_subscription_usage(self):
        pages = self.consumption_client.usage_details.list(top=10)
        first_page = pages.advance_page()
        output = list(first_page)
        self.assertEqual(10, len(output))
        self._validate_usage(output[0])

    def test_consumption_subscription_usage_filter(self):
        date_filter ='usageEnd le '+ str(MgmtConsumptionTest.endDate)
        pages = self.consumption_client.usage_details.list(expand='meterDetails', filter=date_filter, top=10)
        first_page = pages.advance_page()
        output = list(first_page)
        self.assertEqual(10, len(output))
        self._validate_usage(output[0], include_meter_details=True)

    def test_consumption_billing_period_usage(self):
        output = list(self.consumption_client.usage_details.list(expand='properties/additionalProperties'))
        self._validate_usage(output[0], include_additional_properties=True)

    def test_consumption_billing_period_usage_filter(self):
        output = list(self.consumption_client.usage_details.list_by_billing_period(billing_period_name=MgmtConsumptionTest.billingPeriodName, expand='properties/meterDetails,properties/additionalProperties', filter='usageEnd eq 2017-10-26T23:59:59Z'))
        self._validate_usage(output[0], include_meter_details=True, include_additional_properties=True)

    def test_consumption_reservations_summaries_monthly(self):
        output = list(self.consumption_client.reservations_summaries.list_by_reservation_order(reservation_order_id=MgmtConsumptionTest.reservationOrderId, grain="monthly"))
        self._validate_reservations_summaries(output[0])

    def test_consumption_reservations_summaries_monthly_withreservationid(self):
        output = list(self.consumption_client.reservations_summaries.list_by_reservation_order_and_reservation(reservation_order_id=MgmtConsumptionTest.reservationOrderId, reservation_id=MgmtConsumptionTest.reservationId, grain="monthly"))
        self._validate_reservations_summaries(output[0])

    def test_consumption_reservations_summaries_daily(self):
        output = list(self.consumption_client.reservations_summaries.list_by_reservation_order(reservation_order_id=MgmtConsumptionTest.reservationOrderId, grain="daily", filter='properties/UsageDate ge 2017-10-01 AND properties/UsageDate le 2017-12-07'))
        self._validate_reservations_summaries(output[0])

    def test_consumption_reservation_summaries_daily_withreservationid(self):
        output = list(self.consumption_client.reservations_summaries.list_by_reservation_order_and_reservation(reservation_order_id=MgmtConsumptionTest.reservationOrderId, reservation_id=MgmtConsumptionTest.reservationId, grain="daily", filter='properties/UsageDate ge 2017-10-01 AND properties/UsageDate le 2017-12-07'))
        self._validate_reservations_summaries(output[0])

    def test_consumption_reservations_details(self):
        output = list(self.consumption_client.reservations_details.list_by_reservation_order(reservation_order_id=MgmtConsumptionTest.reservationOrderId, filter='properties/UsageDate ge 2017-10-01 AND properties/UsageDate le 2017-12-08'))
        self._validate_reservations_details(output[0])

    def test_consumption_reservations_details_withreservationid(self):
        output = list(self.consumption_client.reservations_details.list_by_reservation_order_and_reservation(reservation_order_id=MgmtConsumptionTest.reservationOrderId, reservation_id=MgmtConsumptionTest.reservationId, filter='properties/UsageDate ge 2017-10-01 AND properties/UsageDate le 2017-12-08'))
        self._validate_reservations_details(output[0])

    def test_consumption_budget_get_by_resource_group(self):
        budget = self.consumption_client.budgets.get(resource_groups='testscaleset', budget_name='PythonSDKTestBudgetCost8')
        self._validate_budget(budget)

    def test_consumption_budget_update_By_resourceGroup(self):
        budget = self.consumption_client.budgets.get(resource_groups='testscaleset', budget_name='PythonSDKTestBudgetCost8')
        budget.amount = 90.0
        budget.time_period = self.models.BudgetTimePeriod(start_date=budget.time_period.start_date, end_date=MgmtConsumptionTest.endDate)
        output = self.consumption_client.budgets.create_or_update_by_resource_group_name(resource_group_name='testscaleset', budget_name='PythonSDKTestBudgetCost8', parameters=budget)
        self.assertEqual('PythonSDKTestBudgetCost8', output.name)
        self.assertEqual(90.0, output.amount)

    def test_consumption_budget_delete_by_budget_resource_group_name(self):
        budget = self.consumption_client.budgets.get(resource_groups='testscaleset', budget_name='PythonSDKTestBudgetCost8')
        self._validate_budget(budget)
        self.consumption_client.budgets.delete_by_resource_group_name(resource_group_name='testscaleset', budget_name=budget.name)

    def test_consumption_budget_delete_by_budgetname(self):
        budget = self.consumption_client.budgets.get(budget_name='PythonSDKTestBudgetCost')
        self._validate_budget(budget)
        self.consumption_client.budgets.delete(budget_name=budget.name)

    def test_consumption_budget_create(self):
        budget = self.models.Budget(category=self.models.CategoryType.cost, amount=60.0, time_grain=self.models.TimeGrainType.monthly, time_period=self.models.BudgetTimePeriod(start_date=MgmtConsumptionTest.startDate, end_date=MgmtConsumptionTest.endDate))
        output = self.consumption_client.budgets.create_or_update(resource_group_name='testResource1', budget_name='PythonSDKTestBudgetCost', parameters=budget)
        self.assertEqual('PythonSDKTestBudgetCost', output.name)

    def test_consumption_budget_get_by_budget_name(self):
        budget = self.consumption_client.budgets.get(budget_name='PythonSDKTestBudgetCost8')
        self._validate_budget(budget)

    def test_consumption_budget_update_and_get(self):
        budget = self.consumption_client.budgets.get(budget_name='PythonSDKTestBudgetCost1')
        budget.amount = 80.0
        budget.time_period = self.models.BudgetTimePeriod(start_date=budget.time_period.start_date, end_date=MgmtConsumptionTest.endDate)
        self.consumption_client.budgets.create_or_update(budget_name='PythonSDKTestBudgetCost1', parameters=budget)
        budget = self.consumption_client.budgets.get(budget_name='PythonSDKTestBudgetCost1')
        self._validate_budget(budget)

    def test_consumption_budget_list(self):
        budget = self.models.Budget(category=self.models.CategoryType.cost, amount=60.0, time_grain=self.models.TimeGrainType.monthly, time_period=self.models.BudgetTimePeriod(start_date=MgmtConsumptionTest.startDate, end_date=MgmtConsumptionTest.endDate))
        output = self.consumption_client.budgets.create_or_update(budget_name='PythonSDKTestBudgetCostCreateAndDelete', parameters=budget)
        self.assertEqual('PythonSDKTestBudgetCostCreateAndDelete', output.name)
        self.consumption_client.budgets.delete(budget_name=output.name)

    def test_consumption_subscription_marketplace(self):
        pages = self.consumption_client.marketplaces.list(top=1)
        first_page = pages.advance_page()
        output = list(first_page)
        self.assertEqual(1, len(output))
        self._validate_marketplace(output[0])

    def test_consumption_subscription_marketplace_filter(self):
        pages = self.consumption_client.marketplaces.list(filter='usageEnd le 2018-02-02', top=1)
        first_page = pages.advance_page()
        output = list(first_page)
        self.assertEqual(1, len(output))
        self._validate_marketplace(output[0])

    def test_consumption_billing_period_marketplace(self):
        pages = self.consumption_client.marketplaces.list_by_billing_period(billing_period_name='201804-1')
        first_page = pages.advance_page()
        output = list(first_page)
        self._validate_marketplace(output[0])

    def test_consumption_billing_period_marketplace_filter(self):
        pages = self.consumption_client.marketplaces.list_by_billing_period(billing_period_name='201804-1', filter='usageEnd ge 2018-01-26T23:59:59Z')
        first_page = pages.advance_page()
        output = list(first_page)
        self._validate_marketplace(output[0])

    def test_consumption_billing_period_price_sheet(self):
        output = self.consumption_client.price_sheet.get_by_billing_period(billing_period_name=MgmtConsumptionTest.billingPeriodName, expand='properties/meterDetails')
        self._validate_price_sheet(output)

    def test_consumption_subscription_price_sheet_expand(self):
        output = self.consumption_client.price_sheet.get(expand='properties/meterDetails')
        self._validate_price_sheet(output)

    def test_consumption_subscription_price_sheet(self):
        output = self.consumption_client.price_sheet.get(top=1)
        self._validate_price_sheet(output, included_paging=True)

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
