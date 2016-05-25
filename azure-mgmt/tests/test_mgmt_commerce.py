# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.commerce
from datetime import date, timedelta
from testutils.common_recordingtestcase import record
from tests.mgmt_testcase import HttpStatusCode, AzureMgmtTestCase


class MgmtCommerceTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtCommerceTest, self).setUp()
        self.commerce_client = self.create_mgmt_client(
            azure.mgmt.commerce.UsageManagementClient
        )

    @record
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
