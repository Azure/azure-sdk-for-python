# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest
import time
import pytest

import azure.mgmt.communication
import azure.mgmt.notificationhubs
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer
from azure.mgmt.communication.models import CommunicationServiceResource
from azure.mgmt.communication.models import KeyType
from azure.mgmt.communication.models import TaggedResource
from azure.mgmt.communication.models import RegenerateKeyParameters
from azure.mgmt.notificationhubs.models import SharedAccessAuthorizationRuleCreateOrUpdateParameters

AZURE_LOCATION = "westus"
COMMUNICATION_SERVICE_LOCATION = "global"
COMMUNICATION_SERVICE_DATA_LOCATION = "UnitedStates"
DISABLE_MGMT_TESTS = True
DISABLE_REASON = "Temporary issue causing the tests to fail"

class MgmtCommunicationTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtCommunicationTest, self).setUp()
        self.communication_client = self.create_mgmt_client(
            azure.mgmt.communication.CommunicationServiceManagementClient
        )
        self.notificationhubs_client = self.create_mgmt_client(
            azure.mgmt.notificationhubs.NotificationHubsManagementClient
        )

    @pytest.mark.skipif(DISABLE_MGMT_TESTS, reason=DISABLE_REASON)
    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_communication_link_notif_hub(self, resource_group):
        GROUP_NAME = resource_group.name
        namespace_name = self.get_resource_name("test-namespace-for-comm")
        notification_hub_name = self.get_resource_name("test-notification-hub-for-comm")
        resource_name = self.get_resource_name("test-resource-link-notif-hub")

        # Create the Notification Hubs resource that will be linked to the Communication Service resource
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
            if self.is_live == True:
                time.sleep(30)
            namespace = self.notificationhubs_client.namespaces.get(
                GROUP_NAME,
                namespace_name
            )
        notification_hubs = self.notificationhubs_client.notification_hubs.create_or_update(
            GROUP_NAME,
            namespace_name,
            notification_hub_name,
            {
                "location": AZURE_LOCATION
            }
        )

        # Create auth rule
        authorization_rule = { "properties": { "rights": [ "Listen" ] } }
        authorization_rule_name = "TestMgmtCommunicationLinkNotificationHub"
        self.notificationhubs_client.notification_hubs.create_or_update_authorization_rule(
            GROUP_NAME,
            namespace_name,
            notification_hub_name,
            authorization_rule_name,
            SharedAccessAuthorizationRuleCreateOrUpdateParameters(**authorization_rule)
        )

        # Obtain connection string
        keys = self.notificationhubs_client.notification_hubs.list_keys(
            GROUP_NAME,
            namespace_name,
            notification_hub_name,
            authorization_rule_name
        )
        notification_hub_connection_string = keys.primary_connection_string

        # Create Communication Service resource for test
        resource = CommunicationServiceResource(
            location=COMMUNICATION_SERVICE_LOCATION,
            data_location = COMMUNICATION_SERVICE_DATA_LOCATION
        )
        resource = self.communication_client.communication_service.begin_create_or_update(
            GROUP_NAME,
            resource_name,
            resource
        ).result()

        # Link Notification Hub's connection string to Communication Service
        linked_notification_hub = self.communication_client.communication_service.link_notification_hub(
            GROUP_NAME,
            resource_name,
            { 'resource_id': notification_hubs.id, 'connection_string': notification_hub_connection_string }
        )
        self.assertIsNotNone(linked_notification_hub.resource_id)
        self.assertEqual(linked_notification_hub.resource_id, notification_hubs.id)

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
