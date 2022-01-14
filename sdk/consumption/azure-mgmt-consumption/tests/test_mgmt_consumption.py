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
from devtools_testutils import AzureMgmtRecordedTestCase, ResourceGroupPreparer, recorded_by_proxy

raise unittest.SkipTest("These were written by Consumption service team for 2.0.0 and would need adaption, and are disabled for now.")

class TestMgmtConsumption(AzureMgmtRecordedTestCase):

    reservationOrderId = 'ca69259e-bd4f-45c3-bf28-3f353f9cce9b'
    reservationId = 'f37f4b70-52ba-4344-a8bd-28abfd21d640'
    billingPeriodName = '201710'
    startDate = '2018-02-01T00:00:00Z'
    endDate = '2018-02-28T00:00:00Z'
    models = azure.mgmt.consumption.models

    def setup_method(self, method):
        self.consumption_client = self.create_mgmt_client(
            azure.mgmt.consumption.ConsumptionManagementClient
        )

    def _validate_usage(self, usage, include_meter_details=False, include_additional_properties=False):
        assert usage is not None
        assert usage.id is not None
        assert usage.name is not None
        assert usage.type is not None
        assert usage.billing_period_id is not None
        assert usage.usage_start <= usage.usage_end
        assert usage.instance_name is not None
        assert usage.currency is not None
        assert usage.pretax_cost is not None
        assert usage.is_estimated is not None
        assert usage.meter_id is not None
        if include_meter_details:
            assert usage.meter_details is not None
            assert usage.meter_details.meter_name is not None
        else:
            assert usage.meter_details is None
        if not include_additional_properties:
            assert usage.additional_properties is None

    def _validate_marketplace(self, marketplace):
        assert marketplace is not None
        assert marketplace.id is not None
        assert marketplace.name is not None
        assert marketplace.type is not None
        assert marketplace.billing_period_id is not None
        assert marketplace.usage_start <= marketplace.usage_end
        assert marketplace.instance_name is not None
        assert marketplace.instance_id is not None
        assert marketplace.currency is not None
        assert marketplace.pretax_cost is not None
        assert marketplace.is_estimated is not None
        assert marketplace.order_number is not None

    def _validate_reservations_summaries(self, reservation):
        assert reservation is not None
        assert reservation.id is not None
        assert reservation.name is not None
        assert reservation.type is not None
        assert reservation.reservation_order_id
        assert reservation.reservation_id
        assert reservation.sku_name
        assert reservation.reserved_hours is not None
        assert reservation.usage_date is not None
        assert reservation.used_hours is not None
        assert reservation.max_utilization_percentage is not None
        assert reservation.min_utilization_percentage is not None
        assert reservation.avg_utilization_percentage is not None

    def _validate_reservations_details(self, reservation):
        assert reservation is not None
        assert reservation.id is not None
        assert reservation.name is not None
        assert reservation.type is not None
        assert reservation.reservation_order_id
        assert reservation.reservation_id
        assert reservation.sku_name
        assert reservation.reserved_hours is not None
        assert reservation.usage_date is not None
        assert reservation.used_hours is not None
        assert reservation.instance_id is not None
        assert reservation.total_reserved_quantity is not None

    def _validate_budget(self, budget):
        assert budget is not None
        assert budget.id is not None
        assert budget.name is not None
        assert budget.type is not None
        assert budget.time_period.start_date is not None
        assert budget.time_period.end_date is not None
        assert budget.time_grain is not None
        assert budget.amount is not None

    def _validate_price_sheet(self, pricesheet, included_paging=False):
        assert pricesheet is not None
        assert pricesheet.id is not None
        assert pricesheet.name is not None
        assert pricesheet.type is not None
        assert pricesheet.pricesheets[0].billing_period_id is not None
        assert pricesheet.pricesheets[0].unit_of_measure is not None
        assert pricesheet.pricesheets[0].included_quantity is not None
        assert pricesheet.pricesheets[0].part_number is not None
        assert pricesheet.pricesheets[0].currency_code is not None
        assert pricesheet.pricesheets[0].unit_price is not None
        assert pricesheet.pricesheets[0].meter_id is not None
        if included_paging:
            assert pricesheet.next_link is not None

    @recorded_by_proxy
    def test_consumption_subscription_usage(self):
        pages = self.consumption_client.usage_details.list(top=10)
        first_page = pages.advance_page()
        output = list(first_page)
        assert 10 == len(output)
        self._validate_usage(output[0])

    @recorded_by_proxy
    def test_consumption_subscription_usage_filter(self):
        date_filter ='usageEnd le '+ str(MgmtConsumptionTest.endDate)
        pages = self.consumption_client.usage_details.list(expand='meterDetails', filter=date_filter, top=10)
        first_page = pages.advance_page()
        output = list(first_page)
        assert 10 == len(output)
        self._validate_usage(output[0], include_meter_details=True)

    @recorded_by_proxy
    def test_consumption_billing_period_usage(self):
        output = list(self.consumption_client.usage_details.list(expand='properties/additionalProperties'))
        self._validate_usage(output[0], include_additional_properties=True)

    @recorded_by_proxy
    def test_consumption_billing_period_usage_filter(self):
        output = list(self.consumption_client.usage_details.list_by_billing_period(billing_period_name=MgmtConsumptionTest.billingPeriodName, expand='properties/meterDetails,properties/additionalProperties', filter='usageEnd eq 2017-10-26T23:59:59Z'))
        self._validate_usage(output[0], include_meter_details=True, include_additional_properties=True)

    @recorded_by_proxy
    def test_consumption_reservations_summaries_monthly(self):
        output = list(self.consumption_client.reservations_summaries.list_by_reservation_order(reservation_order_id=MgmtConsumptionTest.reservationOrderId, grain="monthly"))
        self._validate_reservations_summaries(output[0])

    @recorded_by_proxy
    def test_consumption_reservations_summaries_monthly_withreservationid(self):
        output = list(self.consumption_client.reservations_summaries.list_by_reservation_order_and_reservation(reservation_order_id=MgmtConsumptionTest.reservationOrderId, reservation_id=MgmtConsumptionTest.reservationId, grain="monthly"))
        self._validate_reservations_summaries(output[0])

    @recorded_by_proxy
    def test_consumption_reservations_summaries_daily(self):
        output = list(self.consumption_client.reservations_summaries.list_by_reservation_order(reservation_order_id=MgmtConsumptionTest.reservationOrderId, grain="daily", filter='properties/UsageDate ge 2017-10-01 AND properties/UsageDate le 2017-12-07'))
        self._validate_reservations_summaries(output[0])

    @recorded_by_proxy
    def test_consumption_reservation_summaries_daily_withreservationid(self):
        output = list(self.consumption_client.reservations_summaries.list_by_reservation_order_and_reservation(reservation_order_id=MgmtConsumptionTest.reservationOrderId, reservation_id=MgmtConsumptionTest.reservationId, grain="daily", filter='properties/UsageDate ge 2017-10-01 AND properties/UsageDate le 2017-12-07'))
        self._validate_reservations_summaries(output[0])

    @recorded_by_proxy
    def test_consumption_reservations_details(self):
        output = list(self.consumption_client.reservations_details.list_by_reservation_order(reservation_order_id=MgmtConsumptionTest.reservationOrderId, filter='properties/UsageDate ge 2017-10-01 AND properties/UsageDate le 2017-12-08'))
        self._validate_reservations_details(output[0])

    @recorded_by_proxy
    def test_consumption_reservations_details_withreservationid(self):
        output = list(self.consumption_client.reservations_details.list_by_reservation_order_and_reservation(reservation_order_id=MgmtConsumptionTest.reservationOrderId, reservation_id=MgmtConsumptionTest.reservationId, filter='properties/UsageDate ge 2017-10-01 AND properties/UsageDate le 2017-12-08'))
        self._validate_reservations_details(output[0])

    @recorded_by_proxy
    def test_consumption_budget_get_by_resource_group(self):
        budget = self.consumption_client.budgets.get(resource_groups='testscaleset', budget_name='PythonSDKTestBudgetCost8')
        self._validate_budget(budget)

    @recorded_by_proxy
    def test_consumption_budget_update_By_resourceGroup(self):
        budget = self.consumption_client.budgets.get(resource_groups='testscaleset', budget_name='PythonSDKTestBudgetCost8')
        budget.amount = 90.0
        budget.time_period = self.models.BudgetTimePeriod(start_date=budget.time_period.start_date, end_date=MgmtConsumptionTest.endDate)
        output = self.consumption_client.budgets.create_or_update_by_resource_group_name(resource_group_name='testscaleset', budget_name='PythonSDKTestBudgetCost8', parameters=budget)
        assert 'PythonSDKTestBudgetCost8' == output.name
        assert 90.0 == output.amount

    @recorded_by_proxy
    def test_consumption_budget_delete_by_budget_resource_group_name(self):
        budget = self.consumption_client.budgets.get(resource_groups='testscaleset', budget_name='PythonSDKTestBudgetCost8')
        self._validate_budget(budget)
        self.consumption_client.budgets.delete_by_resource_group_name(resource_group_name='testscaleset', budget_name=budget.name)

    @recorded_by_proxy
    def test_consumption_budget_delete_by_budgetname(self):
        budget = self.consumption_client.budgets.get(budget_name='PythonSDKTestBudgetCost')
        self._validate_budget(budget)
        self.consumption_client.budgets.delete(budget_name=budget.name)

    @recorded_by_proxy
    def test_consumption_budget_create(self):
        budget = self.models.Budget(category=self.models.CategoryType.cost, amount=60.0, time_grain=self.models.TimeGrainType.monthly, time_period=self.models.BudgetTimePeriod(start_date=MgmtConsumptionTest.startDate, end_date=MgmtConsumptionTest.endDate))
        output = self.consumption_client.budgets.create_or_update(resource_group_name='testResource1', budget_name='PythonSDKTestBudgetCost', parameters=budget)
        assert 'PythonSDKTestBudgetCost' == output.name

    @recorded_by_proxy
    def test_consumption_budget_get_by_budget_name(self):
        budget = self.consumption_client.budgets.get(budget_name='PythonSDKTestBudgetCost8')
        self._validate_budget(budget)

    @recorded_by_proxy
    def test_consumption_budget_update_and_get(self):
        budget = self.consumption_client.budgets.get(budget_name='PythonSDKTestBudgetCost1')
        budget.amount = 80.0
        budget.time_period = self.models.BudgetTimePeriod(start_date=budget.time_period.start_date, end_date=MgmtConsumptionTest.endDate)
        self.consumption_client.budgets.create_or_update(budget_name='PythonSDKTestBudgetCost1', parameters=budget)
        budget = self.consumption_client.budgets.get(budget_name='PythonSDKTestBudgetCost1')
        self._validate_budget(budget)

    @recorded_by_proxy
    def test_consumption_budget_list(self):
        budget = self.models.Budget(category=self.models.CategoryType.cost, amount=60.0, time_grain=self.models.TimeGrainType.monthly, time_period=self.models.BudgetTimePeriod(start_date=MgmtConsumptionTest.startDate, end_date=MgmtConsumptionTest.endDate))
        output = self.consumption_client.budgets.create_or_update(budget_name='PythonSDKTestBudgetCostCreateAndDelete', parameters=budget)
        assert 'PythonSDKTestBudgetCostCreateAndDelete' == output.name
        self.consumption_client.budgets.delete(budget_name=output.name)

    @recorded_by_proxy
    def test_consumption_subscription_marketplace(self):
        pages = self.consumption_client.marketplaces.list(top=1)
        first_page = pages.advance_page()
        output = list(first_page)
        assert 1 == len(output)
        self._validate_marketplace(output[0])

    @recorded_by_proxy
    def test_consumption_subscription_marketplace_filter(self):
        pages = self.consumption_client.marketplaces.list(filter='usageEnd le 2018-02-02', top=1)
        first_page = pages.advance_page()
        output = list(first_page)
        assert 1 == len(output)
        self._validate_marketplace(output[0])

    @recorded_by_proxy
    def test_consumption_billing_period_marketplace(self):
        pages = self.consumption_client.marketplaces.list_by_billing_period(billing_period_name='201804-1')
        first_page = pages.advance_page()
        output = list(first_page)
        self._validate_marketplace(output[0])

    @recorded_by_proxy
    def test_consumption_billing_period_marketplace_filter(self):
        pages = self.consumption_client.marketplaces.list_by_billing_period(billing_period_name='201804-1', filter='usageEnd ge 2018-01-26T23:59:59Z')
        first_page = pages.advance_page()
        output = list(first_page)
        self._validate_marketplace(output[0])

    @recorded_by_proxy
    def test_consumption_billing_period_price_sheet(self):
        output = self.consumption_client.price_sheet.get_by_billing_period(billing_period_name=MgmtConsumptionTest.billingPeriodName, expand='properties/meterDetails')
        self._validate_price_sheet(output)

    @recorded_by_proxy
    def test_consumption_subscription_price_sheet_expand(self):
        output = self.consumption_client.price_sheet.get(expand='properties/meterDetails')
        self._validate_price_sheet(output)

    @recorded_by_proxy
    def test_consumption_subscription_price_sheet(self):
        output = self.consumption_client.price_sheet.get(top=1)
        self._validate_price_sheet(output, included_paging=True)

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
