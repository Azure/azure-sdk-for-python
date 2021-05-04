# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import time
import unittest

import azure.mgmt.notificationhubs
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer


AZURE_LOCATION = "eastus"

class MgmtNotificationHubsTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtNotificationHubsTest, self).setUp()
        self.notificationhubs_client = self.create_mgmt_client(
            azure.mgmt.notificationhubs.NotificationHubsManagementClient
        )

    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_notification_hubs(self, resource_group):
        GROUP_NAME = resource_group.name
        namespace_name = "namespacexxz"
        notification_hub_name = "notificationhubxxzx"

        self.notificationhubs_client.namespaces.create_or_update(
            GROUP_NAME,
            namespace_name,
            {
                "location": AZURE_LOCATION
            }
        )

      
        namespace = self.notificationhubs_client.namespaces.get(
            GROUP_NAME,
            namespace_name
        )
        while namespace.status == "Created":
            time.sleep(30)
            namespace = self.notificationhubs_client.namespaces.get(
                GROUP_NAME,
                namespace_name
            )
        
        self.notificationhubs_client.notification_hubs.create_or_update(
            GROUP_NAME,
            namespace_name,
            notification_hub_name,
            {
                "location": AZURE_LOCATION
            }
        )

        self.notificationhubs_client.notification_hubs.get(
            GROUP_NAME,
            namespace_name,
            notification_hub_name
        )

        self.notificationhubs_client.notification_hubs.delete(
            GROUP_NAME,
            namespace_name,
            notification_hub_name
        )

    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_namespaces(self, resource_group):
        GROUP_NAME = resource_group.name
        namespace_name = "namespacexxx"

        self.notificationhubs_client.namespaces.create_or_update(
            GROUP_NAME,
            namespace_name,
            {
                "location": AZURE_LOCATION
            }
        )

      
        namespace = self.notificationhubs_client.namespaces.get(
            GROUP_NAME,
            namespace_name
        )
        while namespace.status == "Created":
            time.sleep(30)
            namespace = self.notificationhubs_client.namespaces.get(
                GROUP_NAME,
                namespace_name
            )

        self.notificationhubs_client.namespaces.patch(
            GROUP_NAME,
            namespace_name,
            {
                "enabled": True
            }
        )

        self.notificationhubs_client.namespaces.begin_delete(
            GROUP_NAME,
            namespace_name
        ).result()


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
