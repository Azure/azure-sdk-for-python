﻿# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.commerce
from datetime import date, timedelta
from devtools_testutils import AzureMgmtTestCase

class MgmtCommerceTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtCommerceTest, self).setUp()
        self.commerce_client = self.create_mgmt_client(
            azure.mgmt.commerce.UsageManagementClient
        )

    def test_commerce(self):
        # Test not recorded for privacy concerns
        #output = self.commerce_client.usage_aggregates.list(
        #    str(date.today() - timedelta(days=1))+'T00:00:00Z',
        #    str(date.today())+'T00:00:00Z'
        #)
        #output = list(output)

        # OfferDurableID: https://azure.microsoft.com/en-us/support/legal/offer-details/
        rate = self.commerce_client.rate_card.get(
            "OfferDurableId eq 'MS-AZR-0062P' and Currency eq 'USD' and Locale eq 'en-US' and RegionInfo eq 'US'"
        )


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
