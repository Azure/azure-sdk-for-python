# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.eventgrid.models
from azure.common.credentials import ServicePrincipalCredentials

from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer


class MgmtEventGridTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtEventGridTest, self).setUp()

        self.eventgrid_client = self.create_mgmt_client(
            azure.mgmt.eventgrid.EventGridManagementClient
        )

    def process(self, result):
        pass

    @ResourceGroupPreparer()
    def test_eventgrid_topic_types(self, resource_group, location):
        # List all topic types
        for result in self.eventgrid_client.topic_types.list():
            self.process(result)

    @ResourceGroupPreparer()
    def test_eventgrid_user_topics(self, resource_group, location):
        topic_name = "kalspython1"
        eventsubscription_name = "kalspythonEventSubscription2"

        # Create a new topic and verify that it is created successfully
        topic_result_create = self.eventgrid_client.topics.create_or_update(resource_group.name, topic_name, "westus2")
        topic = topic_result_create.result()
        self.assertEqual(topic.name, topic_name)

        # Create a new event subscription to this topic
        # Use this for recording mode
        # scope = "/subscriptions/55f3dcd4-cac7-43b4-990b-a139d62a1eb2/resourceGroups/" + resource_group.name + "/providers/Microsoft.EventGrid/topics/" + topic_name        
        scope = "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/" + resource_group.name + "/providers/Microsoft.EventGrid/topics/" + topic_name

        destination = azure.mgmt.eventgrid.models.WebHookEventSubscriptionDestination(
            endpoint_url="https://requestb.in/upue0lup"
        )
        filter = azure.mgmt.eventgrid.models.EventSubscriptionFilter()

        event_subscription_info = azure.mgmt.eventgrid.models.EventSubscription(
            destination=destination,
            filter=filter
        )
        es_result_create = self.eventgrid_client.event_subscriptions.create_or_update(scope, eventsubscription_name, event_subscription_info)
        event_subscription = es_result_create.result()
        self.assertEqual(eventsubscription_name, event_subscription.name)

        # Delete the event subscription
        self.eventgrid_client.event_subscriptions.delete(scope, eventsubscription_name).wait()

        # Delete the topic
        self.eventgrid_client.topics.delete(resource_group.name, topic_name).wait()

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
