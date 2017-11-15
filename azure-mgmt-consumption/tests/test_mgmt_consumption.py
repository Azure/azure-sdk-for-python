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

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
