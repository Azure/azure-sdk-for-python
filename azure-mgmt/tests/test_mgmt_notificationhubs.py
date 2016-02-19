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

import azure.mgmt.notificationhubs
from testutils.common_recordingtestcase import record
from tests.mgmt_testcase import HttpStatusCode, AzureMgmtTestCase


class MgmtNotificationHubsTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtNotificationHubsTest, self).setUp()
        self.notificationhubs_client = self.create_mgmt_client(
            azure.mgmt.notificationhubs.NotificationHubsManagementClientConfiguration,
            azure.mgmt.notificationhubs.NotificationHubsManagementClient
        )

    @record
    def test_notification_hubs(self):
        self.create_resource_group()

        account_name = self.get_resource_name('pyarmnotificationhubs')

        output = self.notificationhubs_client.namespaces.check_availability(
            azure.mgmt.notificationhubs.models.CheckAvailabilityParameters(
                name=account_name
            )
        )
        self.assertTrue(output.is_availiable)


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
