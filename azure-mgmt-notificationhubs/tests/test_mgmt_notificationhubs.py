# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.notificationhubs
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

class MgmtNotificationHubsTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtNotificationHubsTest, self).setUp()
        self.notificationhubs_client = self.create_mgmt_client(
            azure.mgmt.notificationhubs.NotificationHubsManagementClient
        )

    def test_notification_hubs(self):
        account_name = self.get_resource_name('pyarmnotificationhubs')

        output = self.notificationhubs_client.namespaces.check_availability({
            'name': account_name,
            'location': self.region    
        })
        self.assertTrue(output.is_availiable)


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
