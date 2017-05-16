# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.consumption
from testutils.common_recordingtestcase import record
from tests.mgmt_testcase import HttpStatusCode, AzureMgmtTestCase

class MgmtConsumptionTest(AzureMgmtTestCase):

    def _validate_usage(self, usage, includeMeterDetails=False, includeAdditionalProperties=False):
        self.assertIsNotNone(usage)
        self.assertIsNotNone(usage.id)
        self.assertIsNotNone(usage.name)
        self.assertIsNotNone(usage.type)
        self.assertIsNotNone(usage.billing_period_id)
        self.assertTrue(usage.usage_start <= usage.usage_end)
        self.assertIsNotNone(usage.instance_name)
        self.assertIsNotNone(usage.currency)
        self.assertTrue(usage.billable_quantity <= usage.usage_quantity)
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

    def setUp(self):
        super(MgmtConsumptionTest, self).setUp()
        self.consumption_client = self.create_mgmt_client(azure.mgmt.consumption.ConsumptionManagementClient)

    @record
    def test_consumption_subscription_usage(self):
        scope = 'subscriptions/{}'.format(self.settings.SUBSCRIPTION_ID)
        output = list(self.consumption_client.usage_details.list(scope, top=10))
        self.assertEqual(10, len(output))
        self._validate_usage(output[0])

    @record
    def test_consumption_subscription_usage_filter(self):
        scope = 'subscriptions/{}'.format(self.settings.SUBSCRIPTION_ID)
        output = list(self.consumption_client.usage_details.list(scope, expand='meterDetails', filter='usageEnd le 2017-04-01', top=10))
        self.assertEqual(10, len(output))
        self._validate_usage(output[0], includeMeterDetails=True)

    @record
    def test_consumption_invoice_usage(self):
        scope = 'subscriptions/{}/providers/Microsoft.Billing/invoices/201704-117949190364043'.format(self.settings.SUBSCRIPTION_ID)
        output = list(self.consumption_client.usage_details.list(scope, expand='meterDetails,additionalProperties', top=10))
        self.assertEqual(10, len(output))
        self._validate_usage(output[0], includeMeterDetails=True, includeAdditionalProperties=True)

    @record
    def test_consumption_invoice_usage_filter(self):
        scope = 'subscriptions/{}/providers/Microsoft.Billing/invoices/201704-117949190364043'.format(self.settings.SUBSCRIPTION_ID)
        output = list(self.consumption_client.usage_details.list(scope, filter='usageEnd le 2017-03-26 and usageEnd ge 2017-03-25', top=1))
        self.assertEqual(1, len(output))
        self._validate_usage(output[0])
  
    @record
    def test_consumption_billing_period_usage(self):
        scope = 'subscriptions/{}/providers/Microsoft.Billing/billingPeriods/201704-1'.format(self.settings.SUBSCRIPTION_ID)
        output = list(self.consumption_client.usage_details.list(scope, expand='additionalProperties', top=10))
        self.assertEqual(10, len(output))
        self._validate_usage(output[0], includeAdditionalProperties=True)

    @record
    def test_consumption_billing_period_usage_filter(self):
        scope = 'subscriptions/{}/providers/Microsoft.Billing/billingPeriods/201704-1'.format(self.settings.SUBSCRIPTION_ID)
        output = list(self.consumption_client.usage_details.list(scope, expand='meterDetails,additionalProperties', filter='usageEnd eq 2017-03-26T23:59:59Z', top=1))
        self.assertEqual(1, len(output))
        self._validate_usage(output[0], includeMeterDetails=True, includeAdditionalProperties=True)

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
