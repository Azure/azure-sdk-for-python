# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.consumption
from testutils.common_recordingtestcase import record
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

class MgmtConsumptionTest(AzureMgmtTestCase):
    
    reservationOrderId = 'ca69259e-bd4f-45c3-bf28-3f353f9cce9b'
    reservationId = 'f37f4b70-52ba-4344-a8bd-28abfd21d640'

    def _validate_usage(self, usage, includeMeterDetails=False, includeAdditionalProperties=False):
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
        if includeMeterDetails:
            self.assertIsNotNone(usage.meter_details)
            self.assertIsNotNone(usage.meter_details.meter_name)
        else:
            self.assertIsNone(usage.meter_details)
        if not includeAdditionalProperties:
            self.assertIsNone(usage.additional_properties)
            
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
        
    def _validate_price_sheet(self, pricesheet, includeMeterDetails=false):
        self.assertIsNotNone(pricesheet)
        self.assertIsNotNone(pricesheet.id)
        self.assertIsNotNone(pricesheet.name)
        self.assertIsNotNone(pricesheet.type)
        self.assertIsNotNone(pricesheet.billing_period_id)
        self.assertIsNotNone(pricesheet.meter_id)
        self.assertIsNotNone(pricesheet.unit_of_measure)
        self.assertIsNotNone(pricesheet.included_quantity)
        self.assertIsNotNone(pricesheet.part_number)
        self.assertIsNotNone(pricesheet.currency_code)
        self.assertIsNotNone(pricesheet.unit_price)
        
        if includeMeterDetails:
            self.assertIsNotNone(usage.meter_details)
            self.assertIsNotNone(usage.meter_details.meter_name)
        else:
            self.assertIsNone(usage.meter_details)

    def setUp(self):
        super(MgmtConsumptionTest, self).setUp()
        self.consumption_client = self.create_mgmt_client(azure.mgmt.consumption.ConsumptionManagementClient)
    
    def test_consumption_subscription_usage(self):
        scope = 'subscriptions/{}'.format(self.settings.SUBSCRIPTION_ID)
        pages = self.consumption_client.usage_details.list(scope, top=10)
        firstPage = pages.advance_page()
        output = list(firstPage)
        self.assertEqual(10, len(output))
        self._validate_usage(output[0])

    def test_consumption_subscription_usage_filter(self):
        scope = 'subscriptions/{}'.format(self.settings.SUBSCRIPTION_ID)
        pages = self.consumption_client.usage_details.list(scope, expand='meterDetails', filter='usageEnd le 2017-11-01', top=10)
        firstPage = pages.advance_page()
        output = list(firstPage)
        self.assertEqual(10, len(output))
        self._validate_usage(output[0], includeMeterDetails=True)

    
    def test_consumption_billing_period_usage(self):
        scope = 'subscriptions/{}/providers/Microsoft.Billing/billingPeriods/201710'.format(self.settings.SUBSCRIPTION_ID)
        output = list(self.consumption_client.usage_details.list(scope, expand='properties/additionalProperties'))
        self._validate_usage(output[0], includeAdditionalProperties=True)


    def test_consumption_billing_period_usage_filter(self):
        scope = 'subscriptions/{}/providers/Microsoft.Billing/billingPeriods/201710'.format(self.settings.SUBSCRIPTION_ID)
        output = list(self.consumption_client.usage_details.list(scope, expand='properties/meterDetails,properties/additionalProperties', filter='usageEnd eq 2017-03-26T23:59:59Z'))
        self._validate_usage(output[0], includeMeterDetails=True, includeAdditionalProperties=True)

    def test_consumption_subscription_price_sheet(self):
        scope = 'subscriptions/{}'.format(self.setti.SUBSCRIPTION_ID)
        pages = self.consumption_client.pricesheet.list(scope)
        firstPage = pages.advance_page()
        output = list(firstPage)
        self.assertTrue(len(output) > 2)
        self._validate_price_sheet(output[0], includeMeterDetails=False)

    def test_consumption_subscription_price_sheet_expand(self):
        scope = 'subscriptions/{}'.format(self.setti.SUBSCRIPTION_ID)
        pages = self.consumption_client.pricesheet.list(scope, expand='properties/meterDetails')
        firstPage = pages.advance_page()
        output = list(firstPage)
        self._validate_price_sheet(output[0], includeMeterDetails=True)

    def test_consumption_billing_period_price_sheet(self):
        scope = 'subscriptions/{}/providers/Microsoft.Billing/billingPeriods/201710'.format(self.setti.SUBSCRIPTION_ID)        
        output = list(firstPage)output = list(self.consumption_client.usage_details.list(scope, expand='properties/meterDetails'))        
        self._validate_price_sheet(output[0], includeMeterDetails=True)    
    
    def test_consumption_reservations_summaries_monthly(self):
        scope = 'providers/Microsoft.Capacity/reservationorders/{}'.format(MgmtConsumptionTest.reservationOrderId)                 
        output = list(self.consumption_client.reservations_summaries.list(scope, grain="monthly"))
        self._validate_reservations_summaries(output[0])
    
    def test_consumption_reservations_summaries_monthly_withreservationid(self):
        scope = 'providers/Microsoft.Capacity/reservationorders/{}/reservations/{}'.format(MgmtConsumptionTest.reservationOrderId, MgmtConsumptionTest.reservationId)                 
        output = list(self.consumption_client.reservations_summaries.list(scope, grain="monthly"))
        self._validate_reservations_summaries(output[0])
   
    def test_consumption_reservations_summaries_daily(self):
        scope = 'providers/Microsoft.Capacity/reservationorders/{}'.format(MgmtConsumptionTest.reservationOrderId)                 
        output = list(self.consumption_client.reservations_summaries.list(scope, grain="daily", filter='properties/UsageDate ge 2017-10-01 AND properties/UsageDate le 2017-12-07'))
        self._validate_reservations_summaries(output[0])
        
    def test_consumption_reservation_summaries_daily_withreservationid(self):
        scope = 'providers/Microsoft.Capacity/reservationorders/{}/reservations/{}'.format(MgmtConsumptionTest.reservationOrderId, MgmtConsumptionTest.reservationId)                
        output = list(self.consumption_client.reservations_summaries.list(scope, grain="daily", filter='properties/UsageDate ge 2017-10-01 AND properties/UsageDate le 2017-12-07'))
        self._validate_reservations_summaries(output[0])

    def test_consumption_reservations_details(self):
        scope = 'providers/Microsoft.Capacity/reservationorders/{}'.format(MgmtConsumptionTest.reservationOrderId)                 
        output = list(self.consumption_client.reservations_details.list(scope, filter='properties/UsageDate ge 2017-10-01 AND properties/UsageDate le 2017-12-08'))
        self._validate_reservations_details(output[0])

    def test_consumption_reservations_details_withreservationid(self):
        scope = 'providers/Microsoft.Capacity/reservationorders/{}/reservations/{}'.format(MgmtConsumptionTest.reservationOrderId, MgmtConsumptionTest.reservationId)                 
        output = list(self.consumption_client.reservations_details.list(scope, filter='properties/UsageDate ge 2017-10-01 AND properties/UsageDate le 2017-12-08'))
        self._validate_reservations_details(output[0])

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
