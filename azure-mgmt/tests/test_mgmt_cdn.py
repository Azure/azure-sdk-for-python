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

import azure.mgmt.cdn
from testutils.common_recordingtestcase import record
from tests.mgmt_testcase import HttpStatusCode, AzureMgmtTestCase


class MgmtCdnTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtCdnTest, self).setUp()
        self.cdn_client = self.create_mgmt_client(
            azure.mgmt.cdn.CdnManagementClient
        )

    @record
    def test_cdn(self):
        self.create_resource_group()

        account_name = self.get_resource_name('pyarmcdn')

        output = self.cdn_client.name_availability.check_name_availability(
            name=account_name,
            type='Microsoft.Cdn/profiles/endpoints'
        )
        self.assertTrue(output.name_available)


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
